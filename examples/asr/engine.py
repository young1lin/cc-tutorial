#!/usr/bin/env python3
"""SenseVoice-Small 语音识别引擎（中英双语，内置标点）"""

import logging

import numpy as np
import torch
from funasr import AutoModel

from config import SENSEVOICE_MODEL

log = logging.getLogger("subtitle")


class SenseVoiceEngine:
    """
    SenseVoice-Small 推理引擎。
    VAD 触发式：每次对整段音频推理一次，返回带标点的完整文本。
    支持中文、英文及中英混用，自动语言检测。
    """

    def __init__(self):
        log.info("正在加载 SenseVoice 模型，请稍候...")
        try:
            self._device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = AutoModel(
                model=SENSEVOICE_MODEL,
                device=self._device,
                disable_update=True,
                disable_log=True,
            )
            log.info("SenseVoice 模型加载完成 (device=%s)", self._device)
        except Exception as e:
            log.exception("SenseVoice 模型加载失败: %s", e)
            raise

    def transcribe(self, audio: np.ndarray) -> str:
        """
        对整段音频推理一次，返回带标点的文本。

        Args:
            audio: 16kHz mono float32 音频数组

        Returns:
            识别的文本（可能为空字符串）
        """
        try:
            result = self.model.generate(
                input=audio,
                cache={},
                language="auto",   # 自动识别语言（中/英/日/韩等）
                use_itn=True,      # 数字/英文规范化
                batch_size_s=300,
            )
            if result and result[0].get("text"):
                return result[0]["text"].strip()
        except Exception as e:
            log.warning("SenseVoice 推理异常: %s", e)
        return ""

    def reset(self):
        """SenseVoice 无状态，每次 generate 独立，此方法仅保留接口兼容"""
        pass
