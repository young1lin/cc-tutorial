# ============================================
# 01 - ReAct Agent - 纯文本 ReAct 模式
# ============================================
# 说明：基于 LangChain hwchase17/react 提示词的纯文本 ReAct 实现
# 特点：
#   - 不使用 Function Calling，纯文本解析
#   - 每次只执行一个 Action
#   - 严格的 Thought → Action → Observation 循环
# 使用：
#   uv run python 01_react_agent.py 1
#   uv run python 01_react_agent.py 1 -m ds      # DeepSeek
#   uv run python 01_react_agent.py 1 -m glm     # GLM-4-flash
# ============================================

import json
import os
import re
import sys
import argparse
from typing import Any

from dotenv import load_dotenv

from config import get_client, DEFAULT_PROVIDER, print_section, print_box_start, print_box_end, CYAN, GREEN, YELLOW, GRAY, RESET
from tools import TOOL_DEFINITIONS, TOOL_IMPLEMENTATIONS, execute_tool

load_dotenv()

# ============================================
# 模型别名映射
# ============================================

MODEL_ALIASES = {
    "glm": "glm-4.7",
    "glm4.7": "glm-4.7",
    "glm-4.7": "glm-4.7",
    "ds": "deepseek",
    "deepseek": "deepseek",
    "step": "stepfun",
    "stepfun": "stepfun",
}


# ============================================
# ReAct 提示词
# ============================================

REACT_PROMPT = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action (MUST be valid JSON like {{"key": "value"}})
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

IMPORTANT RULES:
1. You can only execute ONE Action at a time
2. After writing Action and Action Input, STOP and wait for Observation
3. NEVER write Observation yourself - the system will provide it
4. Action Input MUST be valid JSON format: {{"key": "value"}}

Begin!

Question: {input}
Thought:{agent_scratchpad}"""


def format_tools_for_prompt() -> tuple[str, str]:
    """格式化工具描述和工具名列表"""
    tool_descriptions = []
    tool_names = []
    for info in TOOL_DEFINITIONS:
        func = info["function"]
        params = ", ".join(f"{k}" for k in func["parameters"].get("properties", {}).keys())
        tool_descriptions.append(f"{func['name']}({params}): {func['description']}")
        tool_names.append(func["name"])
    return "\n".join(tool_descriptions), ", ".join(tool_names)


# ============================================
# ReAct Agent
# ============================================

class ReActAgent:
    """ReAct Agent - 文本解析模式"""

    def __init__(self, provider: str = DEFAULT_PROVIDER):
        self.client, self.model = get_client(provider)
        self.provider = provider
        self.max_iterations = 10
        self.scratchpad = ""

    def _parse_action(self, text: str) -> tuple[str | None, dict | None]:
        """解析 Action 和 Action Input（只取第一个）"""
        action_match = re.search(r"Action:\s*(\w+)", text)
        action_input_match = re.search(r"Action Input:\s*(.+?)(?=\n(?:Thought|Action|Final Answer|Observation)|$)", text, re.DOTALL)

        if not action_match:
            return None, None

        action = action_match.group(1)
        action_input = {}

        if action_input_match:
            raw_input = action_input_match.group(1).strip()
            action_input = self._parse_action_input(raw_input)

        return action, action_input

    def _parse_action_input(self, raw_input: str) -> dict[str, Any]:
        """解析 Action Input，支持 JSON 和 key="value" 两种格式"""
        raw_input = raw_input.strip()

        if raw_input.startswith("{"):
            try:
                cleaned = raw_input.replace("\n", "").replace("\r", "")
                return json.loads(cleaned)
            except json.JSONDecodeError:
                pass

        result = {}
        pattern = r'(\w+)\s*=\s*["\']([^"\']*)["\']'
        matches = re.findall(pattern, raw_input)
        for key, value in matches:
            result[key] = value

        if not result:
            pattern = r'(\w+)\s*=\s*(\S+)'
            matches = re.findall(pattern, raw_input)
            for key, value in matches:
                value = value.rstrip(",;")
                result[key] = value

        return result

    def _parse_final_answer(self, text: str) -> str | None:
        """解析 Final Answer"""
        match = re.search(r"Final Answer:\s*", text)
        if match:
            return text[match.end():].strip()
        return None

    def _extract_thought(self, text: str) -> str:
        """提取最后一个 Thought"""
        matches = list(re.finditer(r"Thought:\s*(.+?)(?=\n\s*(?:Action|Final Answer|Thought:)|$)", text, re.DOTALL))
        if matches:
            return matches[-1].group(1).strip()
        return ""

    def run(self, question: str, stream: bool = False) -> str:
        """执行 ReAct 循环"""
        print_box_start("📥 用户输入")
        print(f"│ {question}")
        print_box_end()

        tools_desc, tool_names = format_tools_for_prompt()

        for iteration in range(1, self.max_iterations + 1):
            print(f"\n{CYAN}🔄 第 {iteration} 轮{RESET}")

            prompt = REACT_PROMPT.format(
                tools=tools_desc,
                tool_names=tool_names,
                input=question,
                agent_scratchpad=self.scratchpad
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                stream=stream,
                stop=["\nObservation:"],
            )

            if stream:
                output = self._handle_streaming(response)
            else:
                output = response.choices[0].message.content

            action, action_input = self._parse_action(output)

            if not action:
                final_answer = self._parse_final_answer(output)
                if final_answer and iteration > 1:
                    print(f"\n{GREEN}✅ Final Answer:{RESET}")
                    print(final_answer)
                    return final_answer
                elif final_answer and iteration == 1:
                    self.scratchpad += f"\n(你必须先使用工具获取信息，不能直接给出答案。)\n"
                    print(f"{YELLOW}⚠️ 第一轮必须先调用工具，请继续...{RESET}")
                    continue
                else:
                    self.scratchpad += f"\n(请继续，使用正确的格式：Thought -> Action -> Action Input)\n"
                    print(f"{YELLOW}⚠️ 未找到有效的 Action，提示模型继续...{RESET}")
                    continue

            if not stream:
                thought = self._extract_thought(output)
                if thought:
                    print(f"{CYAN}💭 Thought:{RESET} {thought}")
                print(f"{CYAN}🎯 Action:{RESET} {action}")
                print(f"{CYAN}📥 Action Input:{RESET} {json.dumps(action_input, ensure_ascii=False)}")

            observation = execute_tool(action, action_input)
            print(f"{GRAY}👁️ Observation:{RESET} {observation[:200]}{'...' if len(observation) > 200 else ''}")

            thought = self._extract_thought(output)
            self.scratchpad += f"\nThought: {thought}\n"
            self.scratchpad += f"Action: {action}\n"
            self.scratchpad += f"Action Input: {json.dumps(action_input, ensure_ascii=False)}\n"
            self.scratchpad += f"Observation: {observation}\n"

        return "错误：达到最大迭代次数"

    def _handle_streaming(self, response) -> str:
        collected = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                collected += content
        print()
        return collected


# ============================================
# 演示场景
# ============================================

DEMOS = {
    "1": {"name": "旅游规划", "question": "帮我规划明天（2026-02-15）的杭州一日游，需要考虑天气情况。", "stream": True},
    "2": {"name": "数学计算", "question": "计算 (123 + 456) * (789 - 654) 的结果", "stream": True},
    "3": {"name": "多步骤查询", "question": "告诉我现在几点了，然后帮我算一下 9876 * 5432 等于多少", "stream": True},
}


def print_help():
    print("=" * 60)
    print("01 - ReAct Agent - 纯文本 ReAct 模式")
    print("=" * 60)
    print()
    print("用法: uv run python 01_react_agent.py <demo_id> [--model <model>]")
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
    print("  uv run python 01_react_agent.py 1           # 默认 GLM-4.7")
    print("  uv run python 01_react_agent.py 1 -m ds     # DeepSeek")
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

    agent = ReActAgent(provider=provider)
    agent.run(demo["question"], stream=demo.get("stream", True))

    print("\n" + "-" * 60)
    print("✅ 完成")
    print("-" * 60)


if __name__ == "__main__":
    main()
