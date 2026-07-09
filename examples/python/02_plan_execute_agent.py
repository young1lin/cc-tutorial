# ============================================
# 02 - Plan-and-Execute Agent - 规划执行模式
# ============================================
# 说明：先规划任务步骤，再逐步执行
# 特点：
#   - 分离规划和执行阶段
#   - 展示思考过程（灰色流式输出）
#   - 适合复杂多步骤任务
# 使用：
#   uv run python 02_plan_execute_agent.py 1
#   uv run python 02_plan_execute_agent.py 1 -m ds   # DeepSeek
# ============================================

import json
import re
import sys
import argparse

from config import get_client, DEFAULT_PROVIDER, print_section, print_box_start, print_box_end, GRAY, RESET
from tools import TOOL_DEFINITIONS, execute_tool

# ============================================
# Plan-and-Execute Agent
# ============================================

PLAN_PROMPT = """你是一个任务规划助手。根据用户需求，制定详细的执行计划。

可用工具：
- get_weather(location, date?): 获取天气信息
- get_attractions(location, category?): 获取景点推荐
- get_restaurants(location, cuisine?): 获取餐厅推荐
- get_current_time(): 获取当前时间
- calculator(expression): 执行数学计算
- web_search(query): 搜索互联网

重要规则：
1. 首先用 <thinking>...</thinking> 标签包裹你的思考过程
2. 思考时要分析：用户的核心需求是什么？需要调用哪些工具？调用顺序是什么？
3. 思考完成后，输出任务分析和执行步骤

格式示例：
<thinking>
用户想要...，核心需求是...。我需要先获取天气，再获取景点，最后获取餐厅...
</thinking>

## 任务分析
...

## 执行步骤
1. [步骤描述]
2. ...
"""

EXECUTE_PROMPT = """你是一个任务执行助手。根据用户需求和计划，调用工具获取信息并给出最终答案。

重要规则：
1. 首先用 <thinking>...</thinking> 标签包裹你的思考过程
2. 思考时要分析：需要调用哪些工具？参数是什么？如何组织最终答案？
3. 思考完成后，调用相应的工具
4. 最后给出完整的结果

格式示例：
<thinking>
用户想要...，我需要先调用 get_weather 获取天气，然后调用 get_attractions 获取景点...
</thinking>
[然后调用工具]
"""


class PlanExecuteAgent:
    """Plan-and-Execute Agent - 带思考过程展示"""

    def __init__(self, provider: str = DEFAULT_PROVIDER):
        self.client, self.model = get_client(provider)
        self.provider = provider

    def _stream_with_thinking(self, response) -> str:
        """流式输出，thinking 部分用灰色"""
        collected = ""
        in_thinking = False
        buffer = ""
        first_chunk = True

        TAG_START = "<thinking>"
        TAG_END = "</thinking>"
        MAX_TAG_LEN = len(TAG_START)

        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                collected += content

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

                    # buffer 不以 '<' 开头，说明不可能匹配标签，直接输出
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

    def plan_task(self, user_input: str) -> str:
        """规划阶段 - 流式输出带思考"""
        print_section("📋 规划阶段")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": PLAN_PROMPT},
                {"role": "user", "content": user_input},
            ],
            temperature=0,
            stream=True,
        )

        return self._stream_with_thinking(response)

    def execute_plan(self, user_input: str) -> str:
        """执行阶段 - 带思考过程流式展示"""
        print_section("🔧 执行阶段")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": EXECUTE_PROMPT},
                {"role": "user", "content": user_input},
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

        # 执行工具调用
        if collected_tool_calls:
            tool_calls_list = list(collected_tool_calls.values())
            messages = [
                {"role": "system", "content": EXECUTE_PROMPT},
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": collected_content, "tool_calls": tool_calls_list},
            ]

            print_box_start(f"🔧 工具调用 ({len(tool_calls_list)}个)")
            for tc in tool_calls_list:
                func_name = tc["function"]["name"]
                func_args = json.loads(tc["function"]["arguments"])
                result = execute_tool(func_name, func_args)
                print(f"│ {func_name}({json.dumps(func_args, ensure_ascii=False)})")
                print(f"│ → {result[:100]}...")
                messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result})
            print_box_end()

            print_section("🤖 最终结果")
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                temperature=0,
                stream=True,
            )
            for chunk in final_response:
                if chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="", flush=True)
            print()

        return collected_content

    def run(self, user_input: str):
        """运行 Plan-and-Execute 流程"""
        print_box_start("📥 用户输入")
        print(f"│ {user_input}")
        print_box_end()

        self.plan_task(user_input)
        self.execute_plan(user_input)

        print("\n" + "-" * 60)
        print("✅ 完成")
        print("-" * 60)


# ============================================
# 演示场景
# ============================================

DEMOS = {
    "1": {"name": "杭州旅游博客", "user": "写一篇关于杭州旅游的博客文章，包括天气建议、必去景点、美食推荐三个部分。"},
    "2": {"name": "北京一日游", "user": "规划北京一日游，包括上午、下午、晚上的行程安排。"},
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
    print("02 - Plan-and-Execute Agent - 规划执行模式")
    print("=" * 60)
    print()
    print("用法: uv run python 02_plan_execute_agent.py <demo_id> [-m <model>]")
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
    print("  uv run python 02_plan_execute_agent.py 1           # 默认 GLM-4.7")
    print("  uv run python 02_plan_execute_agent.py 1 -m ds     # DeepSeek")
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

    agent = PlanExecuteAgent(provider=provider)
    agent.run(demo["user"])


if __name__ == "__main__":
    main()
