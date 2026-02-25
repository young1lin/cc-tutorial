#!/usr/bin/env python3
"""全局常量配置"""

# SenseVoice 模型（中英双语，内置标点，70ms/10s）
SENSEVOICE_MODEL = "iic/SenseVoiceSmall"

# 音频参数
SAMPLE_RATE       = 16000
VAD_CHUNK         = 512       # 16kHz 下 Silero VAD 每帧需要 512 采样 (~32ms)
SILENCE_MS        = 700       # 静音超过此时长触发句尾
MAX_SEG_SEC       = 25        # 超长强制切断
MAX_DISPLAY_LINES = 2         # 字幕保留最近几行（2 白 + 1 灰 = 3 行，正好填满窗口）

# 说话中预览间隔（后台推理线程不阻塞 VAD，可设较短间隔）
PREVIEW_INTERVAL_SEC = 0.5    # 说话中每隔 0.5s 提交一次预览推理请求

# 动态 preview 窗口：预览推理只用 buf 末尾 N 秒，避免长句预览过慢
# 最终推理（sentence_end）仍使用完整 buf
PREVIEW_WINDOW_SEC   = 4.0    # 预览最多取最近 4s 音频（恢复原值，实时感更好）

# 噪声门控：整段 buf 的 RMS 低于此值时跳过最终推理（静音/呼吸声漏出 VAD）
NOISE_GATE_RMS       = 0.002  # 约 -54 dBFS，低于正常说话声

# 回环音频参数
LOOPBACK_SAMPLE_RATE = 48000  # Windows 输出设备原生采样率
LOOPBACK_BLOCKSIZE   = 1536   # = 512 × 3，48kHz→16kHz resample 后恰好 512 samples

# 静音动画参数
SILENCE_ANIM_THRESHOLD = 10   # 静音超过此秒数触发闪烁动画
IDLE_CLEAR_SEC         = 120  # 静音超过此秒数自动清空字幕

# 字幕悬浮窗（宽度在运行时按屏幕 84% 计算，高度由字体大小决定）
SUB_BG        = "#FF00FF"  # 色键颜色，运行后变透明（洋红极少出现在自然场景）
SUB_ALPHA     = 0.95      # 默认文字不透明度（高，保证清晰）
SUB_FONT_SIZE = 28        # 默认字体大小
C_FINAL       = "#ffffff"
C_PEND        = "#ffffff" # 流式字幕颜色（白色，作为主要展示内容）

# 控制面板
CTRL_W = 560
CTRL_H = 420              # 加高，放下字体 / 透明度滑条

# 设备列表自动刷新间隔（停止状态下，毫秒）
DEVICE_REFRESH_MS = 3000

# AEC 参数
AEC_FILTER_BLOCKS = 8
AEC_MU            = 0.01
