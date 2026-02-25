#!/usr/bin/env python3
"""
实时语音识别悬浮字幕 - 入口

功能:
  - 支持麦克风输入、系统声音回环、回声消除（AEC）三种音频源
  - SenseVoice-Small 引擎：中英双语，内置标点，VAD 触发推理
  - DPI 自适应字幕窗口定位
"""

import os
import sys
import logging

# ── 镜像 & 模型缓存路径（必须在导入 funasr / modelscope 之前设置）──────────────
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

# SentencePiece（SenseVoice BPE 分词器）的 C++ 底层在 Windows 上无法正确处理
# 含非 ASCII 字符的路径（例如中文用户名）。若用户主目录含非 ASCII 字符，则自动
# 回退到 SystemDrive 根目录下的纯 ASCII 安全路径，避免 OSError "No such file"。
if "MODELSCOPE_CACHE" not in os.environ:
    _home = os.path.expanduser("~")
    try:
        _home.encode("ascii")
        os.environ["MODELSCOPE_CACHE"] = os.path.join(_home, ".cache", "modelscope")
    except UnicodeEncodeError:
        _sys_drive = os.environ.get("SystemDrive", "C:")
        os.environ["MODELSCOPE_CACHE"] = _sys_drive + "\\modelscope_models"

# ── 日志配置 ──────────────────────────────────────────────────────────────────
_log_fmt = "%(asctime)s [%(levelname)s] %(threadName)s - %(message)s"
logging.basicConfig(
    level=logging.DEBUG,
    format=_log_fmt,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("subtitle.log", encoding="utf-8", mode="w"),
    ],
)
log = logging.getLogger("subtitle")
log.info("MODELSCOPE_CACHE = %s", os.environ.get("MODELSCOPE_CACHE"))

# 抑制第三方库的 DEBUG 噪音
for _lib in (
    "funasr", "modelscope", "sounddevice", "urllib3",
    "httpx", "httpcore", "huggingface_hub", "filelock",
    "torch", "torchaudio", "torio",
):
    logging.getLogger(_lib).setLevel(logging.WARNING)

# ── 导入本地模块（日志配置完成后）────────────────────────────────────────────
import tkinter as tk

from engine import SenseVoiceEngine
from subtitle import RealtimeSubtitle
from gui import ControlPanel, build_subtitle_window


def main():
    engine   = SenseVoiceEngine()
    subtitle = RealtimeSubtitle(engine)

    root  = tk.Tk()
    panel = ControlPanel(root, subtitle)
    win   = build_subtitle_window(root, subtitle, panel.font_size_var, panel.alpha_var)
    panel.set_subtitle_win(win)

    root.mainloop()

    subtitle.stop_stream()
    log.info("程序已退出")


if __name__ == "__main__":
    main()
