# ============================================
# 00 - Basic Function Calling - 纯 HTTP 实现
# ============================================
# 说明：使用 httpx 直接调用 API，展示 Function Calling 底层原理
# 特点：
#   - 不依赖 SDK，纯 HTTP 请求
#   - 流式和非流式两种模式
#   - 自动处理多轮工具调用循环
# 使用：
#   uv run python 00_basic_function_calling.py 1
#   uv run python 00_basic_function_calling.py 1 -m ds   # DeepSeek
# ============================================

import argparse
import json
import os

import httpx
from dotenv import load_dotenv

from config import print_section, print_box_start, print_box_end, GRAY, RESET
from tools import TOOL_DEFINITIONS, execute_tool

load_dotenv()

# ============================================
# 模型配置
# ============================================

MODEL_CONFIGS = {
    "glm": {
        "base_url": "https://open.bigmodel.cn/api/coding/paas/v4/chat/completions",
        "api_key": os.getenv("GLM_API_KEY"),
        "model": "GLM-4-flash",
    },
    "glm-4.7": {
        "base_url": "https://open.bigmodel.cn/api/coding/paas/v4/chat/completions",
        "api_key": os.getenv("GLM_API_KEY"),
        "model": "GLM-4.7",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/chat/completions",
        "api_key": os.getenv("DEEPSEEK_API_KEY"),
        "model": "deepseek-chat",
    },
}

MODEL_ALIASES = {
    "glm": "glm",
    "glm4.7": "glm-4.7",
    "ds": "deepseek",
    "deepseek": "deepseek",
}

DEFAULT_MODEL = "glm-4.7"


# ============================================
# 工具调用输出
# ============================================


def print_tool_call(func_name: str, func_args: dict, result: str, is_last: bool = False):
    """打印工具调用结果"""
    args_str = json.dumps(func_args, ensure_ascii=False)
    if len(result) > 100:
        result_preview = result[:97] + "..."
    else:
        result_preview = result
    print(f"│   📥 输入: {func_name}({args_str})")
    print(f"│   📤 输出: {result_preview}")
    if not is_last:
        print("│")


# ============================================
# 非流式 Function Calling
# ============================================


def chat_non_streaming(
    messages: list[dict],
    model_config: dict,
    tools: list[dict] | None = None,
    max_iterations: int = 5,
) -> str:
    """非流式 Function Calling 实现"""
    user_msg = next((m["content"] for m in messages if m["role"] == "user"), None)
    if user_msg:
        print_box_start("📥 用户输入")
        print(f"│ {user_msg}")
        print_box_end()

    base_url = model_config["base_url"]
    api_key = model_config["api_key"]
    model = model_config["model"]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    current_messages = messages.copy()
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"🔄 调用 {model}...")

        payload = {
            "model": model,
            "messages": current_messages,
            "stream": False,
            "temperature": 0,
        }

        if tools:
            payload["tools"] = tools

        with httpx.Client(timeout=60.0) as client:
            response = client.post(base_url, headers=headers, json=payload)

        if response.status_code != 200:
            return f"API 错误：{response.status_code} - {response.text}"

        data = response.json()
        choice = data["choices"][0]
        message = choice["message"]

        # 打印推理内容（灰色）
        if "reasoning_content" in message and message["reasoning_content"]:
            print(f"{GRAY}{message['reasoning_content']}{RESET}\n")

        # 打印回复内容
        if "content" in message and message["content"]:
            print(message["content"])

        # 检查是否有工具调用
        tool_calls = message.get("tool_calls")

        if tool_calls:
            current_messages.append(message)

            print_box_start(f"🔧 工具调用 #{iteration} ({len(tool_calls)}个)")

            for i, tool_call in enumerate(tool_calls, 1):
                tool_call_id = tool_call["id"]
                func_name = tool_call["function"]["name"]
                func_args = json.loads(tool_call["function"]["arguments"])

                tool_result = execute_tool(func_name, func_args)
                print_tool_call(func_name, func_args, tool_result, is_last=(i == len(tool_calls)))

                current_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": tool_result,
                })
            print_box_end()
        else:
            return message.get("content", "")

    return "错误：达到最大迭代次数"


# ============================================
# 流式 Function Calling
# ============================================


def chat_streaming(
    messages: list[dict],
    model_config: dict,
    tools: list[dict] | None = None,
    max_iterations: int = 5,
) -> str:
    """流式 Function Calling 实现"""
    user_msg = next((m["content"] for m in messages if m["role"] == "user"), None)
    if user_msg:
        print_box_start("📥 用户输入")
        print(f"│ {user_msg}")
        print_box_end()

    base_url = model_config["base_url"]
    api_key = model_config["api_key"]
    model = model_config["model"]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    current_messages = messages.copy()
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"🔄 调用 {model}...")

        payload = {
            "model": model,
            "messages": current_messages,
            "stream": True,
            "temperature": 0,
        }

        if tools:
            payload["tools"] = tools

        # 收集流式响应
        collected_content = ""
        collected_reasoning = ""
        collected_tool_calls: dict[int, dict] = {}
        in_reasoning = False

        with httpx.Client(timeout=60.0) as client:
            with client.stream("POST", base_url, headers=headers, json=payload) as response:
                if response.status_code != 200:
                    return f"API 错误：{response.status_code}"

                for line in response.iter_lines():
                    if not line or line == "data: [DONE]":
                        continue

                    if line.startswith("data: "):
                        try:
                            chunk_data = json.loads(line[6:])
                            delta = chunk_data["choices"][0].get("delta", {})

                            # 收集 reasoning_content（灰色）
                            if "reasoning_content" in delta and delta["reasoning_content"]:
                                reasoning_chunk = delta["reasoning_content"]
                                collected_reasoning += reasoning_chunk
                                if not in_reasoning:
                                    print(GRAY, end="", flush=True)
                                    in_reasoning = True
                                print(reasoning_chunk, end="", flush=True)

                            # 收集 content
                            if "content" in delta and delta["content"]:
                                if in_reasoning:
                                    print(RESET)
                                    in_reasoning = False
                                content_chunk = delta["content"]
                                collected_content += content_chunk
                                print(content_chunk, end="", flush=True)

                            # 收集 tool_calls
                            if "tool_calls" in delta:
                                for tool_call_delta in delta["tool_calls"]:
                                    idx = tool_call_delta.get("index", 0)

                                    if idx not in collected_tool_calls:
                                        collected_tool_calls[idx] = {
                                            "id": "",
                                            "type": "function",
                                            "function": {"name": "", "arguments": ""},
                                        }

                                    if "id" in tool_call_delta:
                                        collected_tool_calls[idx]["id"] = tool_call_delta["id"]

                                    if "function" in tool_call_delta:
                                        func_delta = tool_call_delta["function"]
                                        if "name" in func_delta:
                                            collected_tool_calls[idx]["function"]["name"] = func_delta["name"]
                                        if "arguments" in func_delta:
                                            collected_tool_calls[idx]["function"]["arguments"] += func_delta["arguments"]

                        except json.JSONDecodeError:
                            continue

        # 确保颜色重置
        if in_reasoning:
            print(RESET, end="", flush=True)
        print()

        # 检查是否有工具调用
        if collected_tool_calls:
            tool_calls_list = list(collected_tool_calls.values())

            assistant_message: dict = {"role": "assistant"}
            if collected_content:
                assistant_message["content"] = collected_content
            assistant_message["tool_calls"] = tool_calls_list
            current_messages.append(assistant_message)

            print_box_start(f"🔧 工具调用 #{iteration} ({len(tool_calls_list)}个)")

            for i, tool_call in enumerate(tool_calls_list, 1):
                tool_call_id = tool_call["id"]
                func_name = tool_call["function"]["name"]
                func_args = json.loads(tool_call["function"]["arguments"])

                tool_result = execute_tool(func_name, func_args)
                print_tool_call(func_name, func_args, tool_result, is_last=(i == len(tool_calls_list)))

                current_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": tool_result,
                })
            print_box_end()
        else:
            return collected_content

    return "错误：达到最大迭代次数"


# ============================================
# 演示场景
# ============================================

DEMOS = {
    "1": {"name": "非流式模式", "question": "请帮我计算：(123 + 456) * 789 / 10，然后告诉我现在几点了。", "stream": False},
    "2": {"name": "流式模式", "question": "请帮我计算：(123 + 456) * 789 / 10，然后告诉我现在几点了。", "stream": True},
}


def print_help():
    print("=" * 60)
    print("00 - Basic Function Calling - 纯 HTTP 实现")
    print("=" * 60)
    print()
    print("用法: uv run python 00_basic_function_calling.py <demo_id> [-m <model>]")
    print()
    print("可用的场景:")
    for demo_id, demo in DEMOS.items():
        print(f"  {demo_id}. {demo['name']}")
    print()
    print("支持的模型 (-m):")
    print("  - glm / glm4.7: GLM-4.7 (默认)")
    print("  - ds / deepseek: DeepSeek Chat")
    print()
    print("示例:")
    print("  uv run python 00_basic_function_calling.py 1           # 非流式")
    print("  uv run python 00_basic_function_calling.py 2           # 流式")
    print("  uv run python 00_basic_function_calling.py 2 -m ds     # DeepSeek")
    print()


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("demo_id", nargs="?", default=None)
    parser.add_argument("-m", "--model", default="glm-4.7")
    parser.add_argument("-h", "--help", action="store_true")

    args = parser.parse_args()

    if args.help or args.demo_id is None:
        print_help()
        return

    if args.demo_id not in DEMOS:
        print(f"❌ 未知的场景 ID: {args.demo_id}")
        print_help()
        return

    model_key = args.model.lower()
    model_name = MODEL_ALIASES.get(model_key, DEFAULT_MODEL)
    model_config = MODEL_CONFIGS.get(model_name, MODEL_CONFIGS[DEFAULT_MODEL])

    demo = DEMOS[args.demo_id]
    print_section(f"📌 {demo['name']} [{model_name}]")

    messages = [{"role": "user", "content": demo["question"]}]

    if demo["stream"]:
        chat_streaming(messages, model_config=model_config, tools=TOOL_DEFINITIONS)
    else:
        result = chat_non_streaming(messages, model_config=model_config, tools=TOOL_DEFINITIONS)
        print(f"\n🤖 最终响应:")
        print("-" * 40)
        print(result)

    print("\n" + "-" * 60)
    print("✅ 完成")
    print("-" * 60)


if __name__ == "__main__":
    main()
