# ============================================
# 模型配置
# ============================================
# 说明：统一的模型配置和客户端创建
# ============================================

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ============================================
# 模型配置
# ============================================

MODEL_CONFIGS = {
    "deepseek": {
        "api_key": os.getenv("DEEPSEEK_API_KEY"),
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
    },
    "glm": {
        "api_key": os.getenv("GLM_API_KEY"),
        "base_url": "https://open.bigmodel.cn/api/coding/paas/v4",
        "model": "GLM-4-flash",
    },
    "glm-4.7": {
        "api_key": os.getenv("GLM_API_KEY"),
        "base_url": "https://open.bigmodel.cn/api/coding/paas/v4",
        "model": "GLM-4.7",
    },
    "stepfun": {
        "api_key": os.getenv("STEPFUN_API_KEY"),
        "base_url": "https://api.stepfun.com/v1",
        "model": "step-1-8k",
    },
}

# 默认模型
DEFAULT_PROVIDER = "glm-4.7"


def get_client(provider: str = DEFAULT_PROVIDER) -> tuple[OpenAI, str]:
    """获取指定提供商的客户端和模型名"""
    config = MODEL_CONFIGS.get(provider, MODEL_CONFIGS[DEFAULT_PROVIDER])
    client = OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"],
    )
    return client, config["model"]


# ============================================
# 颜色定义
# ============================================

GRAY = "\033[90m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


# ============================================
# 输出格式化
# ============================================

def print_section(title: str):
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print("=" * 60)


def print_box_start(title: str):
    width = 60
    print(f"\n┌─ {title} " + "─" * (width - len(title) - 4) + "┐")


def print_box_end():
    print("└" + "─" * 59 + "┘")
