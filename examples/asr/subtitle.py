#!/usr/bin/env python3
"""
识别核心：VAD 循环 + 后台推理线程（双线程解耦）

架构：
  inference 线程 (_vad_loop)   ── 仅做帧级 VAD，提交推理请求到 _infer_q
  infer     线程 (_infer_worker) ── 后台调用 engine.transcribe()，不阻塞 VAD

好处：
  - VAD 循环不再因 ML 推理（200-500ms）阻塞，音频帧不积压
  - preview 请求可合并（队列中存在更新的 preview 时跳过旧的）
  - 字幕显示前剥离 SenseVoice 标签，日志保留原始文本供调试

# TODO 状态
# [x] 动态 preview 窗口：预览只用 buf 末尾 PREVIEW_WINDOW_SEC 秒（已实现）
# [x] 滑动窗口流式：0.3s 间隔 + 后台线程 + 4s 动态窗口，近似逐字更新（已实现）
# [x] 噪声门控：RMS < NOISE_GATE_RMS 时跳过最终推理，减少幻觉（已实现）
# [ ] 情感/语言标签可选显示：将 _TAG_RE 结果单独呈现为小字提示（暂跳过）
"""

import queue
import re
import threading
import time
import logging
from collections import deque

import numpy as np
import torch
from silero_vad import load_silero_vad, VADIterator

from config import (
    SAMPLE_RATE,
    VAD_CHUNK,
    SILENCE_MS,
    MAX_SEG_SEC,
    MAX_DISPLAY_LINES,
    PREVIEW_INTERVAL_SEC,
    PREVIEW_WINDOW_SEC,
    NOISE_GATE_RMS,
)
from capture import AudioCapture

log = logging.getLogger("subtitle")

# 字幕显示前剥离 SenseVoice 标签（<|zh|> <|HAPPY|> <|Speech|> <|withitn|> 等）
# 日志仍打印原始文本，方便调试情感/语言标签
_TAG_RE  = re.compile(r"<\|[^|>]*\|>")
# 语言标签：仅匹配小写 2-3 字母（zh、en、ja、ko 等）
_LANG_RE = re.compile(r"<\|([a-z]{2,3})\|>")


class RealtimeSubtitle:
    """
    识别核心：SenseVoice + Silero VAD 触发断句，双线程架构。
    音频流通过 start_stream / stop_stream 管理。
    """

    def __init__(self, engine):
        self.engine = engine

        log.info("正在加载 Silero VAD（断句检测）...")
        self._vad_model = load_silero_vad()
        log.info("Silero VAD 加载完成，准备就绪")

        # 音频输入队列
        self.audio_q = queue.Queue(maxsize=300)

        # 语音状态（受 buf_lock 保护，GUI 线程只读 speaking）
        self.buf_lock         = threading.Lock()
        self.speaking         = False
        self.last_speech_time = 0.0

        # 显示状态（受 disp_lock 保护）
        self.disp_lock = threading.Lock()
        self.finals    = deque(maxlen=MAX_DISPLAY_LINES)
        self.pending   = ""

        # 设备错误回调（由控制面板注册）
        self.on_device_error = None

        # 流控
        self._capture   = None
        self._stop_flag = threading.Event()
        self._stop_flag.set()   # 初始为停止状态
        self.vad        = None
        self._gen       = 0     # 会话代次，用于使过期推理请求失效

        # 推理请求队列：items = (req_type, audio, gen)
        # req_type: "preview" | "final"
        self._infer_q = queue.Queue()

        # 两个常驻后台线程
        threading.Thread(target=self._vad_loop,     daemon=True, name="inference").start()
        threading.Thread(target=self._infer_worker, daemon=True, name="infer").start()

    # ── VAD 实例 ───────────────────────────────────────────────────────────────

    def _new_vad(self) -> VADIterator:
        return VADIterator(
            self._vad_model,
            threshold=0.5,
            sampling_rate=SAMPLE_RATE,
            min_silence_duration_ms=SILENCE_MS,
            speech_pad_ms=80,
        )

    # ── 后台推理线程 ───────────────────────────────────────────────────────────

    def _infer_worker(self):
        """
        后台推理线程：消费 _infer_q。

        - preview：若队列中存在更新的 preview（同一 gen），跳过旧的，仅处理最新
        - final  ：始终处理，不跳过
        - 字幕写入前剥离 SenseVoice 标签，日志保留原始文本
        """
        while True:
            try:
                req_type, audio, gen = self._infer_q.get(timeout=0.5)
            except queue.Empty:
                continue

            # 过期请求（流已重启）
            if gen != self._gen:
                continue

            # preview：排空队列中同代次更新的 preview，使用最新音频
            if req_type == "preview":
                latest_audio = audio
                while True:
                    try:
                        nxt_type, nxt_audio, nxt_gen = self._infer_q.get_nowait()
                        if nxt_type == "preview" and nxt_gen == gen:
                            latest_audio = nxt_audio        # 覆盖为更新的
                        else:
                            self._infer_q.put((nxt_type, nxt_audio, nxt_gen))  # 放回
                            break
                    except queue.Empty:
                        break
                audio = latest_audio

            # 二次检查（draining 期间流可能已停止）
            if gen != self._gen:
                continue

            raw   = self.engine.transcribe(audio)           # 含 SenseVoice 标签
            clean = _TAG_RE.sub("", raw).strip()            # 字幕显示用

            with self.disp_lock:
                if req_type == "final":
                    if clean:
                        self.finals.append(clean)
                        log.info("[字幕] %s", raw)
                    self.pending = ""
                else:  # preview
                    if clean:
                        self.pending = clean
                    log.debug("[预览] %s", raw)

    # ── VAD 循环（轻量，不阻塞于推理）────────────────────────────────────────

    def _vad_loop(self):
        """
        轻量 VAD 循环：逐帧运行 Silero VAD，将推理请求提交到 _infer_q。
        不直接调用 engine.transcribe()，彻底消除推理阻塞。
        """
        leftover          = np.array([], dtype=np.float32)
        buf: list         = []       # 当前语音段缓冲
        seg_start         = 0.0
        last_preview_time = 0.0

        while True:
            # ── 停止状态：清理并等待 ──────────────────────────────────────────
            if self._stop_flag.is_set():
                with self.buf_lock:
                    buf = []
                    self.speaking = False
                leftover = np.array([], dtype=np.float32)
                time.sleep(0.05)
                continue

            # ── 取音频 ────────────────────────────────────────────────────────
            try:
                chunk = self.audio_q.get(timeout=0.5)
            except queue.Empty:
                continue

            # ── 按 VAD_CHUNK 对齐，逐帧处理 ───────────────────────────────────
            data     = np.concatenate([leftover, chunk]) if len(leftover) else chunk.copy()
            n        = len(data) // VAD_CHUNK
            leftover = data[n * VAD_CHUNK:].copy()

            for i in range(n):
                if self._stop_flag.is_set():
                    break

                frame      = data[i * VAD_CHUNK:(i + 1) * VAD_CHUNK]
                frame_t    = torch.from_numpy(frame)
                vad_result = self.vad(frame_t, return_seconds=False) if self.vad else None

                sentence_end = False
                force_cut    = False

                with self.buf_lock:
                    if vad_result:
                        if "start" in vad_result:
                            self.speaking     = True
                            seg_start         = time.time()
                            last_preview_time = seg_start
                            self.last_speech_time = seg_start
                            buf = []
                        elif "end" in vad_result and self.speaking:
                            sentence_end  = True
                            self.speaking = False

                    if self.speaking:
                        self.last_speech_time = time.time()
                        buf.append(frame.copy())

                        if time.time() - seg_start > MAX_SEG_SEC:
                            force_cut = True
                            seg_start = time.time()   # 重置计时，继续说话
                            if self.vad:
                                self.vad.reset_states()

                # ── 句尾 / 强制切断 → 提交最终推理 ───────────────────────────
                if (sentence_end or force_cut) and buf:
                    audio = np.concatenate(buf)
                    rms   = float(np.sqrt(np.mean(audio ** 2)))
                    if rms >= NOISE_GATE_RMS:
                        self._infer_q.put(("final", audio, self._gen))
                    else:
                        log.debug("[噪声门控] 跳过推理 rms=%.4f", rms)
                    buf = []

                # ── 说话中 → 提交预览推理（动态窗口：仅取末尾 PREVIEW_WINDOW_SEC 秒）
                elif self.speaking and buf:
                    now = time.time()
                    if now - last_preview_time >= PREVIEW_INTERVAL_SEC:
                        audio     = np.concatenate(buf)
                        max_samp  = int(PREVIEW_WINDOW_SEC * SAMPLE_RATE)
                        if len(audio) > max_samp:
                            audio = audio[-max_samp:]   # 滑动窗口：只看最近 N 秒
                        self._infer_q.put(("preview", audio, self._gen))
                        last_preview_time = now

    # ── 流控 ───────────────────────────────────────────────────────────────────

    def start_stream(self, device_index: int, mode: str = "input",
                     device_info: dict = None,
                     loopback_idx: int = None, loopback_info: dict = None):
        """
        启动指定设备的音频流并重建 VAD。
        mode: 'input' | 'loopback' | 'mic_aec'
        """
        self._gen += 1   # 使所有待处理的旧推理请求失效

        self.vad = self._new_vad()
        self.last_speech_time = time.time()

        # 清空残留音频
        while not self.audio_q.empty():
            try:
                self.audio_q.get_nowait()
            except queue.Empty:
                break

        # 清空残留推理请求
        while not self._infer_q.empty():
            try:
                self._infer_q.get_nowait()
            except queue.Empty:
                break

        with self.buf_lock:
            self.speaking = False

        self._capture = AudioCapture(
            audio_q=self.audio_q,
            on_error=self.on_device_error,
        )
        if mode == "loopback":
            self._capture.start_loopback(device_index, device_info or {})
        elif mode == "mic_aec":
            if loopback_idx is None:
                raise ValueError("mic_aec 模式需要提供 loopback_idx")
            self._capture.start_mic_aec(device_index, loopback_idx, loopback_info or {})
        elif mode == "mic_mix":
            if loopback_idx is None:
                raise ValueError("mic_mix 模式需要提供 loopback_idx")
            self._capture.start_mix(device_index, loopback_idx, loopback_info or {})
        else:
            self._capture.start_input(device_index)

        self._stop_flag.clear()   # 最后清除 stop_flag，让两个循环开始工作

    def stop_stream(self):
        """停止音频流，清空推理队列"""
        self._stop_flag.set()
        self._gen += 1   # 使所有待处理推理请求失效

        while not self._infer_q.empty():
            try:
                self._infer_q.get_nowait()
            except queue.Empty:
                break

        if self._capture is not None:
            self._capture.stop()
            self._capture = None

        with self.disp_lock:
            self.pending = ""

    # ── 显示 ───────────────────────────────────────────────────────────────────

    def get_display(self) -> tuple[list[str], str]:
        with self.disp_lock:
            return list(self.finals), self.pending

    def clear_display(self):
        with self.disp_lock:
            self.finals.clear()
            self.pending = ""
