# ============================================
# 03 - Self-Reflection Agent - 自我反思模式
# ============================================
# 说明：先给出答案，然后自我检查和修正
# 特点：
#   - 生成初始答案
#   - 自我评估和反思（带思考过程展示）
#   - 必要时修正答案
# 使用：
#   uv run python 03_self_reflection_agent.py 1
#   uv run python 03_self_reflection_agent.py 1 -m ds   # DeepSeek
# ============================================

import json
import re
import sys
import argparse

from config import get_client, DEFAULT_PROVIDER, print_section, print_box_start, print_box_end, GRAY, RESET
from tools import TOOL_DEFINITIONS, execute_tool

# ============================================
# Self-Reflection Agent
# ============================================

SOLVE_PROMPT = """你是一个数学助手。使用 calculator 工具进行计算。

重要规则：
1. 首先用 <thinking>...</thinking> 标签包裹你的思考过程
2. 思考时要分析：如何拆解这个计算？需要调用几次 calculator？
3. 思考完成后，调用工具进行计算
4. 使用中文回复
"""

REFLECT_PROMPT = """你是一个数学助手。请检查以下答案是否正确：

问题: {question}
答案: {answer}

重要规则：
1. 首先用 <thinking>...</thinking> 标签包裹你的反思过程
2. 思考时要分析：计算过程是否正确？结果是否合理？
3. 如果有错误，请指出并给出正确答案

请分析：
1. 计算过程是否正确？
2. 结果是否合理？
3. 如果有错误，请指出并给出正确答案。

输出格式：
## 检查结果
正确 / 有误

## 分析
...

## 最终答案
..."""


class SelfReflectionAgent:
    """Self-Reflection Agent - 带思考过程展示"""

    def __init__(self, provider: str = DEFAULT_PROVIDER):
        self.client, self.model = get_client(provider)
        self.provider = provider

    def _stream_with_thinking(self, response) -> str:
        """流式输出，thinking 部分用灰色"""
        collected = ""
        in_thinking = False
        buffer = ""
        first_chunk = True  # 标记是否是第一个 chunk

        TAG_START = "<thinking>"
        TAG_END = "</thinking>"
        MAX_TAG_LEN = len(TAG_START)

        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                collected += content

                # 第一个 chunk 到达时，显示思考提示
                if first_chunk:
                    first_chunk = False
                    # 如果不是以 <thinking> 开头，显示默认思考提示
                    if not content.lstrip().startswith("<"):
                        print(f"{GRAY}💭 思考中...{RESET} ", end="", flush=True)

                for char in content:
                    buffer += char

                    # 检测 <thinking> 开始
                    if not in_thinking and buffer.endswith(TAG_START):
                        in_thinking = True
                        print(f"\n{GRAY}💭 思考过程:{RESET} ", end="", flush=True)
                        buffer = ""
                        continue

                    # 检测 </thinking> 结束
                    if in_thinking and buffer.endswith(TAG_END):
                        in_thinking = False
                        print(RESET)
                        buffer = ""
                        continue

                    # 智能输出：如果 buffer 不可能是标签的一部分，直接输出
                    if buffer and not buffer.startswith("<"):
                        char_to_output = buffer[0]
                        buffer = buffer[1:]
                        if in_thinking:
                            print(f"{GRAY}{char_to_output}{RESET}", end="", flush=True)
                        else:
                            print(char_to_output, end="", flush=True)
                        continue

                    # buffer 以 '<' 开头，等待更多字符确认是否是标签
                    if len(buffer) > MAX_TAG_LEN:
                        char_to_output = buffer[0]
                        buffer = buffer[1:]
                        if in_thinking:
                            print(f"{GRAY}{char_to_output}{RESET}", end="", flush=True)
                        else:
                            print(char_to_output, end="", flush=True)

        # 输出剩余缓冲区
        if buffer:
            for tag in [TAG_START, TAG_END, "<thinking", "</thinking", "<think", "</think"]:
                buffer = buffer.replace(tag, "")
            if buffer:
                if in_thinking:
                    print(f"{GRAY}{buffer}{RESET}", end="", flush=True)
                else:
                    print(buffer, end="", flush=True)

        print()
        return collected

    def solve(self, question: str) -> str:
        """解决问题 - 带思考过程流式展示"""
        print_section("🔧 解决阶段")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SOLVE_PROMPT},
                {"role": "user", "content": question},
            ],
            tools=TOOL_DEFINITIONS,
            temperature=0,
            stream=True,
        )

        collected_content = ""
        collected_tool_calls: dict[int, dict] = {}
        in_thinking = False
        buffer = ""
        first_chunk = True

        TAG_START = "<thinking>"
        TAG_END = "</thinking>"
        MAX_TAG_LEN = len(TAG_START)

        for chunk in response:
            delta = chunk.choices[0].delta

            if delta.content:
                content = delta.content
                collected_content += content

                if first_chunk:
                    first_chunk = False
                    if not content.lstrip().startswith("<"):
                        print(f"{GRAY}💭 思考中...{RESET} ", end="", flush=True)

                for char in content:
                    buffer += char

                    if not in_thinking and buffer.endswith(TAG_START):
                        in_thinking = True
                        print(f"\n{GRAY}💭 思考过程:{RESET} ", end="", flush=True)
                        buffer = ""
                        continue

                    if in_thinking and buffer.endswith(TAG_END):
                        in_thinking = False
                        print(RESET)
                        buffer = ""
                        continue

                    if buffer and not buffer.startswith("<"):
                        char_to_output = buffer[0]
                        buffer = buffer[1:]
                        if in_thinking:
                            print(f"{GRAY}{char_to_output}{RESET}", end="", flush=True)
                        else:
                            print(char_to_output, end="", flush=True)
                        continue

                    if len(buffer) > MAX_TAG_LEN:
                        char_to_output = buffer[0]
                        buffer = buffer[1:]
                        if in_thinking:
                            print(f"{GRAY}{char_to_output}{RESET}", end="", flush=True)
                        else:
                            print(char_to_output, end="", flush=True)

            if delta.tool_calls:
                for tc_delta in delta.tool_calls:
                    idx = tc_delta.index
                    if idx not in collected_tool_calls:
                        collected_tool_calls[idx] = {"id": "", "type": "function", "function": {"name": "", "arguments": ""}}
                    if tc_delta.id:
                        collected_tool_calls[idx]["id"] = tc_delta.id
                    if tc_delta.function:
                        if tc_delta.function.name:
                            collected_tool_calls[idx]["function"]["name"] = tc_delta.function.name
                        if tc_delta.function.arguments:
                            collected_tool_calls[idx]["function"]["arguments"] += tc_delta.function.arguments

        # 输出剩余缓冲区
        if buffer:
            for tag in [TAG_START, TAG_END, "<thinking", "</thinking"]:
                buffer = buffer.replace(tag, "")
            if buffer:
                if in_thinking:
                    print(f"{GRAY}{buffer}{RESET}", end="", flush=True)
                else:
                    print(buffer, end="", flush=True)
        print()

        # 执行工具
        if collected_tool_calls:
            tool_calls_list = list(collected_tool_calls.values())
            messages = [
                {"role": "system", "content": SOLVE_PROMPT},
                {"role": "user", "content": question},
                {"role": "assistant", "content": collected_content, "tool_calls": tool_calls_list},
            ]

            print_box_start(f"🔧 工具调用")
            for tc in tool_calls_list:
                func_name = tc["function"]["name"]
                func_args = json.loads(tc["function"]["arguments"])
                result = execute_tool(func_name, func_args)
                print(f"│ {func_name}({json.dumps(func_args, ensure_ascii=False)})")
                print(f"│ → {result}")
                messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result})
            print_box_end()

            # 继续获取最终答案
            print(f"\n{GRAY}💭 继续思考...{RESET}")
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                temperature=0,
                stream=True,
            )
            for chunk in final_response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    collected_content += content
            print()

        return collected_content

    def reflect(self, question: str, answer: str) -> str:
        """反思阶段 - 带思考过程流式展示"""
        print_section("🤔 反思阶段")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": REFLECT_PROMPT.format(question=question, answer=answer)},
            ],
            temperature=0,
            stream=True,
        )

        return self._stream_with_thinking(response)

    def run(self, question: str):
        """运行 Self-Reflection 流程"""
        print_box_start("📥 用户输入")
        print(f"│ {question}")
        print_box_end()

        # 解决阶段
        answer = self.solve(question)

        # 反思阶段
        self.reflect(question, answer)

        print("\n" + "-" * 60)
        print("✅ 完成")
        print("-" * 60)


# ============================================
# 演示场景
# ============================================

DEMOS = {
    "1": {"name": "数学计算", "user": "计算：(123 + 456) × (789 - 654) ÷ 10"},
    "2": {"name": "复杂运算", "user": "计算：9876 * 5432，然后除以 8"},
}

# 模型别名映射
MODEL_ALIASES = {
    "glm": "glm-4.7",
    "glm4.7": "glm-4.7",
    "glm-4.7": "glm-4.7",
    "ds": "deepseek",
    "deepseek": "deepseek",
    "step": "stepfun",
    "stepfun": "stepfun",
}


def print_help():
    print("=" * 60)
    print("03 - Self-Reflection Agent - 自我反思模式")
    print("=" * 60)
    print()
    print("用法: uv run python 03_self_reflection_agent.py <demo_id> [-m <model>]")
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
    print("  uv run python 03_self_reflection_agent.py 1           # 默认 GLM-4.7")
    print("  uv run python 03_self_reflection_agent.py 1 -m ds     # DeepSeek")
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
    provider = MODEL_ALIASES.get(model_key, "glm-4.7")

    demo = DEMOS[args.demo_id]
    print_section(f"📌 {demo['name']} [{provider}]")

    agent = SelfReflectionAgent(provider=provider)
    agent.run(demo["user"])


if __name__ == "__main__":
    main()
