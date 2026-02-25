#!/usr/bin/env python3
"""GUI 组件：字幕悬浮窗 + 控制面板"""

import time
import logging
import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk

from config import (
    SUB_BG, SUB_ALPHA, SUB_FONT_SIZE, C_FINAL, C_PEND,
    CTRL_W, CTRL_H, DEVICE_REFRESH_MS,
    SILENCE_ANIM_THRESHOLD, IDLE_CLEAR_SEC,
)
from capture import list_input_devices, list_loopback_devices

log = logging.getLogger("subtitle")


# ─── 字体工具 ──────────────────────────────────────────────────────────────────

def _get_cjk_font(size: int, weight: str = "normal") -> tuple:
    """自动选择可用的中文字体，带回退链"""
    candidates = ["Microsoft YaHei UI", "Microsoft YaHei", "SimHei", "DengXian", "SimSun"]
    try:
        available = set(tkFont.families())
        for f in candidates:
            if f in available:
                return (f, size, weight) if weight != "normal" else (f, size)
    except Exception:
        pass
    return ("TkDefaultFont", size, weight) if weight != "normal" else ("TkDefaultFont", size)


# ─── 字幕悬浮窗 ────────────────────────────────────────────────────────────────

def build_subtitle_window(root: tk.Tk, subtitle,
                          font_size_var: tk.IntVar,
                          alpha_var: tk.DoubleVar) -> tk.Toplevel:
    CHROMA   = "#FF00FF"  # 色键：此色像素变透明且穿透鼠标
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    sub_w    = int(screen_w * 0.84)

    def _h(): return max(60, int(font_size_var.get() * 2.4))
    def _x(): return max(0, (screen_w - sub_w) // 2)
    def _y(): return max(0, screen_h - _h() - 80)

    win = tk.Toplevel(root)
    win.withdraw()
    win.title("字幕")
    win.geometry(f"{sub_w}x{_h()}+{_x()}+{_y()}")
    win.configure(bg=CHROMA)

    # Windows 下 overrideredirect + alpha 需严格按此顺序
    win.overrideredirect(True)
    win.update_idletasks()
    win.deiconify()
    win.attributes("-topmost", True)
    win.attributes("-transparentcolor", CHROMA)   # 色键透明：洋红像素穿透鼠标
    win.attributes("-alpha", alpha_var.get())      # 控制文字不透明度

    # Canvas 替代 Text widget，支持多层绘制（描边 + 主文字）
    canvas = tk.Canvas(win, bg=CHROMA, highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    def _redraw(text: str):
        canvas.delete("all")
        if not text:
            return
        font = _get_cjk_font(font_size_var.get(), "bold")
        cw = canvas.winfo_width() or sub_w
        ch = canvas.winfo_height() or _h()
        canvas.create_text(cw // 2, ch // 2, text=text,
                           fill="#ffffff", font=font, anchor="center")

    # 字体大小变化 → 重算窗口高度
    def _on_font(*_):
        win.geometry(f"{sub_w}x{_h()}+{_x()}+{_y()}")

    font_size_var.trace_add("write", _on_font)

    # 透明度变化 → 立即生效（只影响文字像素）
    alpha_var.trace_add("write",
                        lambda *_: win.attributes("-alpha", alpha_var.get()))

    # 拖动（点 canvas 文字区域拖动）
    def on_press(e):
        win._dx = e.x_root - win.winfo_x()
        win._dy = e.y_root - win.winfo_y()

    def on_drag(e):
        win.geometry(f"+{e.x_root - win._dx}+{e.y_root - win._dy}")

    canvas.bind("<Button-1>",  on_press)
    canvas.bind("<B1-Motion>", on_drag)

    # 100ms 轮询：只显示流式文字，不显示历史字幕
    def refresh():
        _, pending = subtitle.get_display()
        _redraw(pending)
        win.after(100, refresh)

    win.after(100, refresh)
    return win


# ─── 控制面板 ──────────────────────────────────────────────────────────────────

class ControlPanel:
    """
    音频源切换（麦克风 / 系统声音回环 / AEC）+ 设备选择 + 开始/停止控制。
    停止状态下每 3 秒自动刷新设备列表；长时间静音时状态点闪烁提示。
    """

    _DOT = {
        "ready":   "#888888",
        "running": "#44cc44",
        "error":   "#ff4444",
        "warn":    "#ff8800",
    }

    def __init__(self, root: tk.Tk, subtitle):
        self.root      = root
        self.subtitle  = subtitle
        self.running   = False
        self._devices  = []   # 主设备列表 [(index, name, info_or_None), ...]
        self._ref_devs = []   # mic_aec 回环参考设备列表
        self._mode     = tk.StringVar(value="input")
        self._anim_state = False
        self._sub_win  = None
        self.font_size_var = tk.IntVar(value=SUB_FONT_SIZE)
        self.alpha_var     = tk.DoubleVar(value=SUB_ALPHA)

        subtitle.on_device_error = self._on_device_error

        root.title("实时字幕 · 控制面板")
        root.geometry(f"{CTRL_W}x{CTRL_H}")
        root.resizable(False, False)

        self._build()
        self._refresh_devices()
        self._schedule_auto_refresh()
        self._schedule_anim_tick()

    # ── UI 构建 ────────────────────────────────────────────────────────────────

    def _build(self):
        PAD = dict(padx=14, pady=4)

        # ── 音频源切换 Combobox ──────────────────────────────────────────────
        f0 = tk.Frame(self.root)
        f0.pack(fill=tk.X, **PAD)

        tk.Label(f0, text="音频源:", width=8, anchor="w",
                 font=_get_cjk_font(10)).pack(side=tk.LEFT)

        self._mode_labels = [
            "🎤 麦克风输入",
            "🔊 系统声音（回环）",
            "🎤🔊 回声消除",
            "🎤🔊 混音识别",
        ]
        self._mode_values = ["input", "loopback", "mic_aec", "mic_mix"]

        self.mode_cb = ttk.Combobox(
            f0, values=self._mode_labels, state="readonly", width=22,
            font=_get_cjk_font(10),
        )
        self.mode_cb.current(0)
        self.mode_cb.bind("<<ComboboxSelected>>", lambda _: self._on_mode_change())
        self.mode_cb.pack(side=tk.LEFT, padx=(4, 0))

        # ── 主设备选择 ───────────────────────────────────────────────────────
        f1 = tk.Frame(self.root)
        f1.pack(fill=tk.X, **PAD)

        self.dev_label = tk.Label(f1, text="输入设备:", width=8, anchor="w",
                                  font=_get_cjk_font(10))
        self.dev_label.pack(side=tk.LEFT)

        self.dev_var = tk.StringVar()
        self.dev_cb  = ttk.Combobox(f1, textvariable=self.dev_var,
                                    state="readonly", width=36)
        self.dev_cb.pack(side=tk.LEFT, padx=(4, 8))

        self.btn_refresh = tk.Button(f1, text="⟳ 刷新", width=7,
                                     command=self._refresh_devices)
        self.btn_refresh.pack(side=tk.LEFT)

        # ── 参考声源（mic_aec 专用，默认隐藏）──────────────────────────────
        self._ref_row = tk.Frame(self.root)

        tk.Label(self._ref_row, text="参考声源:", width=8, anchor="w",
                 font=_get_cjk_font(10)).pack(side=tk.LEFT)

        self.ref_var = tk.StringVar()
        self.ref_cb  = ttk.Combobox(self._ref_row, textvariable=self.ref_var,
                                    state="readonly", width=36)
        self.ref_cb.pack(side=tk.LEFT, padx=(4, 8))

        # ── 状态 ─────────────────────────────────────────────────────────────
        f2 = tk.Frame(self.root)
        f2.pack(fill=tk.X, **PAD)

        tk.Label(f2, text="状态:", width=8, anchor="w",
                 font=_get_cjk_font(10)).pack(side=tk.LEFT)
        self.dot_lbl = tk.Label(f2, text="●", fg=self._DOT["ready"],
                                font=("Arial", 13))
        self.dot_lbl.pack(side=tk.LEFT)
        self.status_lbl = tk.Label(f2, text="就绪，请选择设备后开始", anchor="w",
                                   font=_get_cjk_font(10))
        self.status_lbl.pack(side=tk.LEFT, padx=5)

        # ── 操作按钮 ─────────────────────────────────────────────────────────
        f3 = tk.Frame(self.root)
        f3.pack(fill=tk.X, **PAD)

        self.btn_start = tk.Button(
            f3, text="▶  开始识别", width=14,
            bg="#2a6e2a", fg="white", font=_get_cjk_font(11, "bold"),
            command=self._on_start,
        )
        self.btn_start.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_stop = tk.Button(
            f3, text="■  停止", width=9,
            font=_get_cjk_font(11), state=tk.DISABLED,
            command=self._on_stop,
        )
        self.btn_stop.pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(f3, text="清空字幕", width=8,
                  font=_get_cjk_font(10),
                  command=self.subtitle.clear_display).pack(side=tk.LEFT, padx=(0, 8))

        self.btn_show_sub = tk.Button(
            f3, text="显示字幕", width=8,
            font=_get_cjk_font(10),
            command=self._on_show_subtitle,
        )
        self.btn_show_sub.pack(side=tk.LEFT)

        # ── 提示行 ───────────────────────────────────────────────────────────
        self.hint_lbl = tk.Label(self.root, text="", fg="#777777",
                                 font=_get_cjk_font(9), anchor="w")
        self.hint_lbl.pack(fill=tk.X, padx=14, pady=(0, 4))

        # ── 字体大小 ─────────────────────────────────────────────────────────
        f_font = tk.Frame(self.root)
        f_font.pack(fill=tk.X, padx=14, pady=(0, 2))
        tk.Label(f_font, text="字体大小:", width=8, anchor="w",
                 font=_get_cjk_font(10)).pack(side=tk.LEFT)
        tk.Scale(f_font, from_=14, to=56, orient=tk.HORIZONTAL,
                 variable=self.font_size_var, length=230, resolution=1,
                 showvalue=True, font=_get_cjk_font(9)).pack(side=tk.LEFT)

        # ── 字幕透明度 ────────────────────────────────────────────────────────
        f_alpha = tk.Frame(self.root)
        f_alpha.pack(fill=tk.X, padx=14, pady=(0, 6))
        tk.Label(f_alpha, text="文字透明:", width=8, anchor="w",
                 font=_get_cjk_font(10)).pack(side=tk.LEFT)
        tk.Scale(f_alpha, from_=0.10, to=0.95, orient=tk.HORIZONTAL,
                 variable=self.alpha_var, length=230, resolution=0.05,
                 showvalue=True, font=_get_cjk_font(9)).pack(side=tk.LEFT)

    # ── 音频源模式切换 ─────────────────────────────────────────────────────────

    def _on_mode_change(self):
        i = self.mode_cb.current()
        mode = self._mode_values[i] if 0 <= i < len(self._mode_values) else "input"
        self._mode.set(mode)
        if mode in ("mic_aec", "mic_mix"):
            self._ref_row.pack(fill=tk.X, padx=14, pady=4,
                               after=self.dev_cb.master)
        else:
            self._ref_row.pack_forget()
        self._refresh_devices()

    # ── 设备刷新 ───────────────────────────────────────────────────────────────

    def _refresh_devices(self):
        mode = self._mode.get()
        try:
            if mode == "loopback":
                raw = list_loopback_devices()
                self._devices = [(idx, name, info) for idx, name, info in raw]
                names = [f"[{idx}]  {name}" for idx, name, _ in self._devices]
                self.dev_label.config(text="输出设备:")
            else:
                raw = list_input_devices()
                self._devices = [(idx, name, None) for idx, name in raw]
                names = [f"[{idx}]  {name}" for idx, name, _ in self._devices]
                self.dev_label.config(text="麦克风:" if mode in ("mic_aec", "mic_mix") else "输入设备:")
        except Exception as e:
            self._set_hint(f"设备列表获取失败: {e}")
            return

        prev = self.dev_var.get()
        self.dev_cb["values"] = names
        if prev in names:
            self.dev_var.set(prev)
        elif names:
            self.dev_cb.current(0)

        if mode in ("mic_aec", "mic_mix"):
            try:
                ref_raw = list_loopback_devices()
                self._ref_devs = [(idx, name, info) for idx, name, info in ref_raw]
                ref_names = [f"[{idx}]  {name}" for idx, name, _ in self._ref_devs]
            except Exception:
                self._ref_devs, ref_names = [], []
            prev_ref = self.ref_var.get()
            self.ref_cb["values"] = ref_names
            if prev_ref in ref_names:
                self.ref_var.set(prev_ref)
            elif ref_names:
                self.ref_cb.current(0)

        count = len(self._devices)
        kind  = "回环设备" if mode == "loopback" else "输入设备"
        self._set_hint(f"找到 {count} 个{kind}  （停止状态下每 3 秒自动刷新）")

    def _schedule_auto_refresh(self):
        if not self.running:
            self._refresh_devices()
        self.root.after(DEVICE_REFRESH_MS, self._schedule_auto_refresh)

    # ── 静音动画定时器（1Hz）──────────────────────────────────────────────────

    def _schedule_anim_tick(self):
        if self.running:
            self._update_silence_anim()
        self.root.after(1000, self._schedule_anim_tick)

    def _update_silence_anim(self):
        now     = time.time()
        elapsed = now - self.subtitle.last_speech_time

        if elapsed > IDLE_CLEAR_SEC:
            self.subtitle.clear_display()

        if elapsed > SILENCE_ANIM_THRESHOLD and not self.subtitle.speaking:
            self._anim_state = not self._anim_state
            dot = "●" if self._anim_state else "○"
            self.dot_lbl.config(text=dot, fg=self._DOT["running"])
        else:
            self.dot_lbl.config(text="●", fg=self._DOT["running"])

    # ── 获取当前选中设备 ───────────────────────────────────────────────────────

    def _selected_device(self):
        i = self.dev_cb.current()
        if not (0 <= i < len(self._devices)):
            return None, None, None, None, None
        idx, name, info = self._devices[i]
        j = self.ref_cb.current()
        if 0 <= j < len(self._ref_devs):
            ref_idx, _, ref_info = self._ref_devs[j]
        else:
            ref_idx, ref_info = None, None
        return idx, name, info, ref_idx, ref_info

    # ── 状态显示 ───────────────────────────────────────────────────────────────

    def _set_status(self, kind: str, text: str):
        self.dot_lbl.config(text="●", fg=self._DOT[kind])
        self.status_lbl.config(text=text)

    def _set_hint(self, text: str):
        self.hint_lbl.config(text=text)

    # ── 按钮回调 ───────────────────────────────────────────────────────────────

    def _on_start(self):
        dev_idx, dev_name, dev_info, ref_idx, ref_info = self._selected_device()
        if dev_idx is None:
            self._set_status("error", "请先选择一个设备")
            return

        mode = self._mode.get()
        if mode in ("mic_aec", "mic_mix") and ref_idx is None:
            self._set_status("error", "此模式需要选择参考声源（扬声器/回环设备）")
            return

        try:
            self.subtitle.start_stream(
                dev_idx, mode=mode, device_info=dev_info,
                loopback_idx=ref_idx, loopback_info=ref_info,
            )
        except Exception as e:
            self._set_status("error", f"启动失败: {e}")
            return

        self.running = True
        self._anim_state = False
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        for w in (self.mode_cb, self.dev_cb, self.ref_cb, self.btn_refresh):
            w.config(state=tk.DISABLED)
        short_name = dev_name[:28] + ("…" if len(dev_name) > 28 else "")
        label_map  = {"input": "麦克风", "loopback": "回环",
                      "mic_aec": "回声消除", "mic_mix": "混音识别"}
        self._set_status("running", f"录音中 [{label_map[mode]}]  ·  {short_name}")
        self._set_hint("识别中，说话即可显示字幕")

    def _unlock_controls(self):
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.mode_cb.config(state="readonly")
        self.dev_cb.config(state="readonly")
        self.ref_cb.config(state="readonly")
        self.btn_refresh.config(state=tk.NORMAL)

    def _on_stop(self):
        self.subtitle.stop_stream()
        self.running = False
        self._unlock_controls()
        self._set_status("ready", "已停止")
        self._set_hint("")

    def set_subtitle_win(self, win: tk.Toplevel):
        self._sub_win = win

    def _on_show_subtitle(self):
        if self._sub_win is not None:
            self._sub_win.deiconify()
            self._sub_win.lift()

    # ── 设备断开（音频线程回调 → 调度到 GUI 线程）────────────────────────────

    def _on_device_error(self, err_msg: str):
        self.root.after(0, self._handle_device_error, err_msg)

    def _handle_device_error(self, err_msg: str):
        if not self.running:
            return
        self.subtitle.stop_stream()
        self.running = False
        self._unlock_controls()
        self._set_status("warn", "设备已断开")
        self._set_hint(f"错误: {err_msg[:60]}  ·  重新连接后点「刷新」再开始")
