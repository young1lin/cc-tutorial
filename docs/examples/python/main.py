# ============================================
# Function Calling 纯 HTTP 实现
# ============================================
# 说明：使用 httpx 实现流式和非流式的 Function Calling
# 目的：展示 Function Calling 的底层原理，不依赖 SDK
# ============================================

import json
import os
from typing import Any, Callable

import httpx
from dotenv import load_dotenv

load_dotenv()

# ============================================
# 配置
# ============================================

GLM_BASE_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
GLM_API_KEY = os.getenv("GLM_API_KEY")

# ============================================
# 输出格式化
# ============================================


def print_box_start(title: str):
    """打印框线开始"""
    width = 60
    print(f"\n┌─ {title} " + "─" * (width - len(title) - 4) + "┐")


def print_box_end():
    """打印框线结束"""
    print("└" + "─" * 59 + "┘")


def print_tool_call(func_name: str, func_args: dict, result: str, is_last: bool = False):
    """打印工具调用结果"""
    args_str = json.dumps(func_args, ensure_ascii=False)
    # 结果预览（限制长度）
    if len(result) > 100:
        result_preview = result[:97] + "..."
    else:
        result_preview = result
    print(f"│   📥 输入: {func_name}({args_str})")
    print(f"│   📤 输出: {result_preview}")
    if not is_last:
        print("│")


# ============================================
# 工具定义
# ============================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "执行数学计算表达式，返回精确结果。支持 +、-、*、/、** 等运算符。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的数学表达式，如 '9876 * 5432' 或 '(123 + 456) * 2'",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前时间（北京时间）",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


# ============================================
# 工具实现
# ============================================
def calculator(expression: str) -> str:
    """
    计算器工具 - 使用 eval 执行数学表达式
    注意：生产环境应使用更安全的表达式解析器
    """
    try:
        # 安全限制：只允许数字和基本运算符
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return f"错误：表达式包含不允许的字符"

        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"计算错误：{str(e)}"


def get_current_time() -> str:
    """获取当前时间"""
    from datetime import datetime, timezone, timedelta

    beijing_tz = timezone(timedelta(hours=8))
    now = datetime.now(beijing_tz)
    return now.strftime("%Y-%m-%d %H:%M:%S (北京时间)")


# 工具映射
TOOL_IMPLEMENTATIONS: dict[str, Callable] = {
    "calculator": calculator,
    "get_current_time": get_current_time,
}


def execute_tool(tool_name: str, arguments: dict[str, Any]) -> str:
    """执行工具并返回结果"""
    if tool_name not in TOOL_IMPLEMENTATIONS:
        return f"错误：未知工具 '{tool_name}'"

    func = TOOL_IMPLEMENTATIONS[tool_name]
    try:
        result = func(**arguments)
        return str(result)
    except Exception as e:
        return f"工具执行错误：{str(e)}"


# ============================================
# 非流式 Function Calling
# ============================================


def chat_non_streaming(
    messages: list[dict],
    model: str = "GLM-4.6",
    tools: list[dict] | None = None,
    max_iterations: int = 5,
) -> str:
    """
    非流式 Function Calling 实现
    """
    # 打印用户输入
    user_msg = next((m["content"] for m in messages if m["role"] == "user"), None)
    if user_msg:
        print_box_start("📥 用户输入")
        print(f"│ {user_msg}")
        print_box_end()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GLM_API_KEY}",
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
            response = client.post(GLM_BASE_URL, headers=headers, json=payload)

        if response.status_code != 200:
            return f"API 错误：{response.status_code} - {response.text}"

        data = response.json()
        choice = data["choices"][0]
        message = choice["message"]

        # 检查是否有工具调用
        tool_calls = message.get("tool_calls")

        if tool_calls:
            # 将 assistant 消息添加到历史
            current_messages.append(message)

            # 打印工具调用分组
            print_box_start(f"🔧 工具调用 #{iteration} ({len(tool_calls)}个)")

            # 执行每个工具调用
            for i, tool_call in enumerate(tool_calls, 1):
                tool_call_id = tool_call["id"]
                func_name = tool_call["function"]["name"]
                func_args = json.loads(tool_call["function"]["arguments"])

                # 执行工具
                tool_result = execute_tool(func_name, func_args)
                print_tool_call(func_name, func_args, tool_result, is_last=(i == len(tool_calls)))

                # 添加工具结果到消息历史
                current_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": tool_result,
                    }
                )
            print_box_end()
        else:
            # 没有工具调用，返回最终响应
            return message.get("content", "")

    return "错误：达到最大迭代次数"


# ============================================
# 流式 Function Calling
# ============================================


def chat_streaming(
    messages: list[dict],
    model: str = "GLM-4.6",
    tools: list[dict] | None = None,
    max_iterations: int = 5,
) -> str:
    """
    流式 Function Calling 实现
    """
    # 打印用户输入
    user_msg = next((m["content"] for m in messages if m["role"] == "user"), None)
    if user_msg:
        print_box_start("📥 用户输入")
        print(f"│ {user_msg}")
        print_box_end()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GLM_API_KEY}",
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
        collected_tool_calls: dict[int, dict] = {}

        with httpx.Client(timeout=60.0) as client:
            with client.stream(
                "POST", GLM_BASE_URL, headers=headers, json=payload
            ) as response:
                if response.status_code != 200:
                    return f"API 错误：{response.status_code}"

                for line in response.iter_lines():
                    if not line or line == "data: [DONE]":
                        continue

                    if line.startswith("data: "):
                        try:
                            chunk_data = json.loads(line[6:])
                            delta = chunk_data["choices"][0].get("delta", {})

                            # 收集 content
                            if "content" in delta and delta["content"]:
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
                                        collected_tool_calls[idx]["id"] = (
                                            tool_call_delta["id"]
                                        )

                                    if "function" in tool_call_delta:
                                        func_delta = tool_call_delta["function"]
                                        if "name" in func_delta:
                                            collected_tool_calls[idx]["function"][
                                                "name"
                                            ] = func_delta["name"]
                                        if "arguments" in func_delta:
                                            collected_tool_calls[idx]["function"][
                                                "arguments"
                                            ] += func_delta["arguments"]

                        except json.JSONDecodeError:
                            continue

        print()  # 换行

        # 检查是否有工具调用
        if collected_tool_calls:
            tool_calls_list = list(collected_tool_calls.values())

            # 构建 assistant 消息
            assistant_message: dict[str, Any] = {"role": "assistant"}
            if collected_content:
                assistant_message["content"] = collected_content
            assistant_message["tool_calls"] = tool_calls_list
            current_messages.append(assistant_message)

            # 打印工具调用分组
            print_box_start(f"🔧 工具调用 #{iteration} ({len(tool_calls_list)}个)")

            # 执行每个工具调用
            for i, tool_call in enumerate(tool_calls_list, 1):
                tool_call_id = tool_call["id"]
                func_name = tool_call["function"]["name"]
                func_args = json.loads(tool_call["function"]["arguments"])

                # 执行工具
                tool_result = execute_tool(func_name, func_args)
                print_tool_call(func_name, func_args, tool_result, is_last=(i == len(tool_calls_list)))

                # 添加工具结果到消息历史
                current_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": tool_result,
                    }
                )
            print_box_end()
        else:
            # 没有工具调用，返回最终响应
            return collected_content

    return "错误：达到最大迭代次数"


# ============================================
# 主函数
# ============================================


def main():
    print("=" * 60)
    print("Function Calling 纯 HTTP 实现演示")
    print("=" * 60)

    # 测试消息
    messages = [
        {
            "role": "user",
            "content": "请帮我计算：(123 + 456) * 789 / 10，然后告诉我现在几点了。",
        }
    ]

    # ============================================
    # 测试 1：非流式调用
    # ============================================
    print("\n" + "=" * 60)
    print("测试 1：非流式 Function Calling (GLM-4.6)")
    print("=" * 60)

    result = chat_non_streaming(messages, model="GLM-4.6", tools=TOOLS)
    print(f"\n🤖 最终响应:")
    print("-" * 40)
    print(result)

    # ============================================
    # 测试 2：流式调用
    # ============================================
    print("\n" + "=" * 60)
    print("测试 2：流式 Function Calling (GLM-4.6)")
    print("=" * 60)

    result = chat_streaming(messages, model="GLM-4.6", tools=TOOLS)
    # 流式输出已经显示了结果，不需要再打印


if __name__ == "__main__":
    main()
