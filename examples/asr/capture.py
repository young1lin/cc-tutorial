#!/usr/bin/env python3
"""音频采集后端：麦克风 / WASAPI 回环 / AEC 双流"""

import queue
import threading
import logging
from math import gcd

import numpy as np
import sounddevice as sd

from config import (
    SAMPLE_RATE,
    VAD_CHUNK,
    LOOPBACK_SAMPLE_RATE,
    LOOPBACK_BLOCKSIZE,
    AEC_FILTER_BLOCKS,
    AEC_MU,
)

log = logging.getLogger("subtitle")


# ─── 设备枚举 ──────────────────────────────────────────────────────────────────

def list_input_devices() -> list[tuple[int, str]]:
    """用 sounddevice 列出输入设备（麦克风、WoMic 等）"""
    devs = sd.query_devices()
    return [(i, d["name"]) for i, d in enumerate(devs) if d["max_input_channels"] > 0]


def list_loopback_devices() -> list[tuple[int, str, dict]]:
    """用 PyAudioWPatch 列出 WASAPI 回环设备（扬声器输出）"""
    try:
        import pyaudiowpatch as pyaudio
        result = []
        with pyaudio.PyAudio() as p:
            for dev in p.get_loopback_device_info_generator():
                result.append((int(dev["index"]), dev["name"], dict(dev)))
        return result
    except Exception as e:
        log.warning("回环设备枚举失败（PyAudioWPatch 未安装或无 WASAPI 设备）: %s", e)
        return []


# ─── 工具函数 ──────────────────────────────────────────────────────────────────

def _pad_or_trim(arr: np.ndarray, length: int) -> np.ndarray:
    """将数组调整为指定长度（截断或末尾补零）"""
    if len(arr) >= length:
        return arr[:length].astype(np.float32)
    return np.pad(arr.astype(np.float32), (0, length - len(arr)))


# ─── 频域回声消除（AEC）────────────────────────────────────────────────────────

class FreqDomainAEC:
    """
    基于 Overlap-Save 的频域自适应回声消除 (Frequency-Domain NLMS)。

    算法原理：
      每个 block (B 采样) 进来时，将历史 L=B*K 个参考采样拼接成 FFT 窗口，
      在频域估计回声并减去，然后用误差信号更新频域滤波器系数。
      约束滤波器因果性（时域前 L 系数清零），避免估计发散。

    参数：
      block_size   : 每次处理的采样数，应等于 VAD_CHUNK (512)
      filter_blocks: 滤波器覆盖的历史块数，建议 8→覆盖 256ms @ 16kHz
      mu           : 步长，越大收敛越快但越不稳定，建议 0.005~0.02
    """

    def __init__(self, block_size: int = VAD_CHUNK,
                 filter_blocks: int = AEC_FILTER_BLOCKS,
                 mu: float = AEC_MU):
        self.B        = block_size
        self.K        = filter_blocks
        self.L        = block_size * filter_blocks   # 滤波器有效长度（样本数）
        self.mu       = mu
        self._fft_n   = self.B + self.L              # FFT 窗口大小
        n_bins        = self._fft_n // 2 + 1
        self.H        = np.zeros(n_bins, dtype=complex)          # 频域滤波器
        self._ref_hist = np.zeros(self.L, dtype=np.float32)     # 参考信号历史

    def process(self, ref: np.ndarray, mic: np.ndarray) -> np.ndarray:
        """
        ref : 参考信号块（扬声器回环，已重采样到 16kHz，长度应 == block_size）
        mic : 麦克风信号块（含回声，长度应 == block_size）
        返回 : 去回声后的干净信号（float32，与 mic 等长）
        """
        B = self.B
        ref = _pad_or_trim(ref, B)
        mic = _pad_or_trim(mic, B)

        # ── 频域回声估计 ──────────────────────────────────────────────────────
        x        = np.concatenate([self._ref_hist, ref])
        X        = np.fft.rfft(x, n=self._fft_n)
        echo_td  = np.fft.irfft(self.H * X, n=self._fft_n)
        echo_est = echo_td[-B:].astype(np.float32)

        # ── 误差信号（去回声后的人声）─────────────────────────────────────────
        e = mic - echo_est

        # ── 频域 NLMS 权重更新 ────────────────────────────────────────────────
        e_padded = np.concatenate([np.zeros(self.L), e])
        E        = np.fft.rfft(e_padded, n=self._fft_n)
        power    = np.abs(X) ** 2 + 1e-8
        self.H  += (self.mu / power) * np.conj(X) * E

        # 约束因果性：时域前 L 个系数清零（防止非因果发散）
        h_td = np.fft.irfft(self.H, n=self._fft_n)
        h_td[:self.L] = 0.0
        self.H = np.fft.rfft(h_td, n=self._fft_n)

        # ── 更新参考历史 ──────────────────────────────────────────────────────
        self._ref_hist = np.concatenate([self._ref_hist[B:], ref])

        return e.astype(np.float32)


# ─── 音频采集后端 ──────────────────────────────────────────────────────────────

class AudioCapture:
    """
    统一音频采集后端，支持三种模式：
      - input:    sounddevice.InputStream，16000Hz mono（麦克风、WoMic）
      - loopback: PyAudioWPatch WASAPI 回环，自动重采样到 16000Hz mono
      - mic_aec:  麦克风 + 扬声器回环双流，实时回声消除后送入 audio_q
    """

    def __init__(self, audio_q: queue.Queue, on_error=None):
        self._audio_q  = audio_q
        self._on_error = on_error
        self._stream   = None   # sd.InputStream 或 PyAudio stream
        self._pa       = None   # PyAudio 实例（回环模式专用）

    # ── 麦克风输入模式 ─────────────────────────────────────────────────────────

    def start_input(self, device_idx: int):
        """启动 sounddevice 麦克风输入流（16000Hz mono）"""
        log.info("启动麦克风流: device=%s", device_idx)
        self._stream = sd.InputStream(
            device=device_idx,
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=VAD_CHUNK,
            callback=self._input_cb,
        )
        self._stream.start()
        log.info("麦克风流已启动")

    def _input_cb(self, indata, frames, time_info, status):
        if status:
            log.warning("麦克风流状态异常: %s", status)
            if self._on_error:
                self._on_error(str(status))
            return
        try:
            self._audio_q.put_nowait(indata[:, 0].copy())
        except queue.Full:
            pass

    # ── 扬声器回环模式 ─────────────────────────────────────────────────────────

    def start_loopback(self, device_idx: int, device_info: dict):
        """
        启动 PyAudioWPatch WASAPI 回环流。
        自动将设备原生格式（通常 stereo 48kHz）重采样为 mono 16kHz。
        """
        from scipy.signal import resample_poly
        import pyaudiowpatch as pyaudio

        self._pa = pyaudio.PyAudio()

        ch   = int(device_info.get("maxInputChannels", 2))
        rate = int(device_info.get("defaultSampleRate", LOOPBACK_SAMPLE_RATE))
        ch   = max(1, ch)
        log.info("启动回环流: device=%s name=%s rate=%s ch=%s",
                 device_idx, device_info.get("name", "?"), rate, ch)

        g    = gcd(SAMPLE_RATE, rate)
        up   = SAMPLE_RATE // g
        down = rate // g

        if rate == LOOPBACK_SAMPLE_RATE:
            blocksize = LOOPBACK_BLOCKSIZE
        else:
            blocksize = VAD_CHUNK * down // up * 2 + 64

        def _loopback_cb(in_data, frame_count, time_info, status):
            if status:
                log.warning("回环流状态异常（xrun/设备拔出）: %s", status)
                if self._on_error:
                    self._on_error(f"loopback status: {status}")
            audio = np.frombuffer(in_data, dtype=np.float32).reshape(-1, ch)
            mono  = audio.mean(axis=1)
            mono  = resample_poly(mono, up, down).astype(np.float32)
            try:
                self._audio_q.put_nowait(mono)
            except queue.Full:
                pass
            return (None, pyaudio.paContinue)

        self._stream = self._pa.open(
            format=pyaudio.paFloat32,
            channels=ch,
            rate=rate,
            input=True,
            input_device_index=device_idx,
            frames_per_buffer=blocksize,
            stream_callback=_loopback_cb,
        )
        self._stream.start_stream()
        log.info("回环流已启动: blocksize=%s resample=%s→%s", blocksize, rate, SAMPLE_RATE)

    # ── 麦克风 + 回环双流（AEC 模式）──────────────────────────────────────────

    def start_mic_aec(self, mic_idx: int, loopback_idx: int, loopback_info: dict):
        """
        同时捕获麦克风和扬声器回环，实时做回声消除后送入 audio_q。
        mic_idx      : sounddevice 麦克风设备索引
        loopback_idx : PyAudioWPatch 回环设备索引
        loopback_info: list_loopback_devices() 返回的设备信息字典
        """
        from scipy.signal import resample_poly
        import pyaudiowpatch as pyaudio

        log.info("启动 AEC 模式: mic=%s loopback=%s name=%s",
                 mic_idx, loopback_idx, loopback_info.get("name", "?"))
        self._mic_q    = queue.Queue(maxsize=200)
        self._ref_q    = queue.Queue(maxsize=200)
        self._aec_obj  = FreqDomainAEC(block_size=VAD_CHUNK)
        self._aec_stop = threading.Event()

        def _mic_cb(indata, frames, time_info, status):
            if status:
                log.warning("AEC 麦克风流状态异常: %s", status)
                if self._on_error:
                    self._on_error(str(status))
                return
            try:
                self._mic_q.put_nowait(indata[:, 0].copy())
            except queue.Full:
                pass

        self._stream = sd.InputStream(
            device=mic_idx,
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=VAD_CHUNK,
            callback=_mic_cb,
        )

        ch   = int(loopback_info.get("maxInputChannels", 2))
        rate = int(loopback_info.get("defaultSampleRate", LOOPBACK_SAMPLE_RATE))
        ch   = max(1, ch)
        g    = gcd(SAMPLE_RATE, rate)
        up, down = SAMPLE_RATE // g, rate // g
        bs   = LOOPBACK_BLOCKSIZE if rate == LOOPBACK_SAMPLE_RATE else VAD_CHUNK * down // up * 2 + 64

        def _ref_cb(in_data, frame_count, time_info, status):
            if status:
                log.warning("AEC 参考回环流状态异常: %s", status)
            audio = np.frombuffer(in_data, dtype=np.float32).reshape(-1, ch)
            mono  = resample_poly(audio.mean(axis=1), up, down).astype(np.float32)
            try:
                self._ref_q.put_nowait(mono)
            except queue.Full:
                log.debug("AEC 参考队列满，丢弃一帧（ref_q 积压）")
            return (None, pyaudio.paContinue)

        self._pa = pyaudio.PyAudio()
        self._ref_stream = self._pa.open(
            format=pyaudio.paFloat32,
            channels=ch,
            rate=rate,
            input=True,
            input_device_index=loopback_idx,
            frames_per_buffer=bs,
            stream_callback=_ref_cb,
        )

        threading.Thread(target=self._aec_worker, daemon=True, name="aec").start()

        self._stream.start()
        self._ref_stream.start_stream()
        log.info("AEC 双流已启动: mic_blocksize=%s ref_blocksize=%s resample=%s/%s",
                 VAD_CHUNK, bs, up, down)

    def _aec_worker(self):
        """
        对齐麦克风块与参考块，逐块调用 FreqDomainAEC，
        将清洁人声送入 audio_q。
        """
        log.debug("AEC 工作线程启动")
        ref_buf = np.array([], dtype=np.float32)
        mic_buf = np.array([], dtype=np.float32)
        ref_zero_count = 0

        while not self._aec_stop.is_set():
            try:
                while True:
                    ref_buf = np.concatenate([ref_buf, self._ref_q.get_nowait()])
            except queue.Empty:
                pass

            try:
                mic_chunk = self._mic_q.get(timeout=0.1)
            except queue.Empty:
                continue

            mic_buf = np.concatenate([mic_buf, mic_chunk])

            while len(mic_buf) >= VAD_CHUNK:
                if len(ref_buf) < VAD_CHUNK:
                    ref_buf = np.zeros(VAD_CHUNK, dtype=np.float32)
                    ref_zero_count += 1
                    if ref_zero_count == 10:
                        log.warning("AEC 参考信号持续缺失（已用零填充 %d 块），"
                                    "请检查回环设备是否正常工作", ref_zero_count)
                else:
                    if ref_zero_count > 0:
                        log.debug("AEC 参考信号恢复，之前缺失 %d 块", ref_zero_count)
                    ref_zero_count = 0

                mic_blk = mic_buf[:VAD_CHUNK]
                ref_blk = ref_buf[:VAD_CHUNK]
                mic_buf = mic_buf[VAD_CHUNK:]
                ref_buf = ref_buf[VAD_CHUNK:]

                clean = self._aec_obj.process(ref_blk, mic_blk)
                try:
                    self._audio_q.put_nowait(clean)
                except queue.Full:
                    log.debug("audio_q 满，丢弃一帧（SenseVoice 处理滞后）")

    # ── 麦克风 + 回环双流（混音模式，不消除回声）─────────────────────────────

    def start_mix(self, mic_idx: int, loopback_idx: int, loopback_info: dict):
        """
        同时捕获麦克风和扬声器回环，直接混合后送入 audio_q（无回声消除）。
        适用：同时识别自己说的话和屏幕/视频声音。
        """
        from scipy.signal import resample_poly
        import pyaudiowpatch as pyaudio

        log.info("启动混音模式: mic=%s loopback=%s name=%s",
                 mic_idx, loopback_idx, loopback_info.get("name", "?"))
        self._mic_q    = queue.Queue(maxsize=200)
        self._ref_q    = queue.Queue(maxsize=200)
        self._mix_stop = threading.Event()

        def _mic_cb(indata, frames, time_info, status):
            if status:
                log.warning("混音麦克风流状态异常: %s", status)
                if self._on_error:
                    self._on_error(str(status))
                return
            try:
                self._mic_q.put_nowait(indata[:, 0].copy())
            except queue.Full:
                pass

        self._stream = sd.InputStream(
            device=mic_idx,
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=VAD_CHUNK,
            callback=_mic_cb,
        )

        ch   = int(loopback_info.get("maxInputChannels", 2))
        rate = int(loopback_info.get("defaultSampleRate", LOOPBACK_SAMPLE_RATE))
        ch   = max(1, ch)
        g    = gcd(SAMPLE_RATE, rate)
        up, down = SAMPLE_RATE // g, rate // g
        bs   = LOOPBACK_BLOCKSIZE if rate == LOOPBACK_SAMPLE_RATE else VAD_CHUNK * down // up * 2 + 64

        def _ref_cb(in_data, frame_count, time_info, status):
            if status:
                log.warning("混音回环流状态异常: %s", status)
            audio = np.frombuffer(in_data, dtype=np.float32).reshape(-1, ch)
            mono  = resample_poly(audio.mean(axis=1), up, down).astype(np.float32)
            try:
                self._ref_q.put_nowait(mono)
            except queue.Full:
                log.debug("混音参考队列满，丢弃一帧")
            return (None, pyaudio.paContinue)

        self._pa = pyaudio.PyAudio()
        self._ref_stream = self._pa.open(
            format=pyaudio.paFloat32,
            channels=ch,
            rate=rate,
            input=True,
            input_device_index=loopback_idx,
            frames_per_buffer=bs,
            stream_callback=_ref_cb,
        )

        threading.Thread(target=self._mix_worker, daemon=True, name="mix").start()

        self._stream.start()
        self._ref_stream.start_stream()
        log.info("混音双流已启动: mic_blocksize=%s ref_blocksize=%s resample=%s/%s",
                 VAD_CHUNK, bs, up, down)

    def _mix_worker(self):
        """对齐麦克风块与回环块，叠加后限幅，送入 audio_q。"""
        log.debug("混音工作线程启动")
        ref_buf = np.array([], dtype=np.float32)
        mic_buf = np.array([], dtype=np.float32)

        while not self._mix_stop.is_set():
            try:
                while True:
                    ref_buf = np.concatenate([ref_buf, self._ref_q.get_nowait()])
            except queue.Empty:
                pass

            try:
                mic_chunk = self._mic_q.get(timeout=0.1)
            except queue.Empty:
                continue

            mic_buf = np.concatenate([mic_buf, mic_chunk])

            while len(mic_buf) >= VAD_CHUNK:
                mic_blk = mic_buf[:VAD_CHUNK]
                mic_buf  = mic_buf[VAD_CHUNK:]

                if len(ref_buf) >= VAD_CHUNK:
                    ref_blk = ref_buf[:VAD_CHUNK]
                    ref_buf  = ref_buf[VAD_CHUNK:]
                else:
                    ref_blk = np.zeros(VAD_CHUNK, dtype=np.float32)

                # 直接叠加（各自保持原始音量），限幅防止溢出
                mixed = np.clip(mic_blk + ref_blk, -1.0, 1.0)
                try:
                    self._audio_q.put_nowait(mixed)
                except queue.Full:
                    log.debug("audio_q 满，丢弃一帧（识别滞后）")

    # ── 停止 ───────────────────────────────────────────────────────────────────

    def stop(self):
        """统一停止，兼容单流和双流（AEC / 混音）两种情况"""
        if hasattr(self, "_aec_stop"):
            self._aec_stop.set()

        if hasattr(self, "_mix_stop"):
            self._mix_stop.set()

        if self._stream is not None:
            try:
                if hasattr(self._stream, "stop_stream"):
                    self._stream.stop_stream()
                    self._stream.close()
                else:
                    self._stream.stop()
                    self._stream.close()
            except Exception:
                pass
            self._stream = None

        if hasattr(self, "_ref_stream") and self._ref_stream is not None:
            try:
                self._ref_stream.stop_stream()
                self._ref_stream.close()
            except Exception:
                pass
            self._ref_stream = None

        if self._pa is not None:
            try:
                self._pa.terminate()
            except Exception:
                pass
            self._pa = None
