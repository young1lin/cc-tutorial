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
import logging
import os
import re
import sys
import argparse
from typing import Any

from dotenv import load_dotenv

# ============================================
# 调试日志配置
# ============================================
logging.basicConfig(
    filename='react_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s\n%(message)s\n' + '='*60
)

from config import (
    get_client,
    DEFAULT_PROVIDER,
    print_section,
    print_box_start,
    print_box_end,
    CYAN,
    GREEN,
    YELLOW,
    GRAY,
    RESET,
)
from tools import TOOL_DEFINITIONS, TOOL_IMPLEMENTATIONS, execute_tool
from datetime import datetime

load_dotenv()

# ============================================
# 模型别名映射
# ============================================

MODEL_ALIASES = {
    "glm": "glm-4-flash",
    "glm4": "glm-4-flash",
    "glm-4-flash": "glm-4-flash",
    "glm4.7": "glm-4.7",
    "glm-4.7": "glm-4.7",
    "glm5": "glm-5",
    "glm-5": "glm-5",
    "ds": "deepseek",
    "deepseek": "deepseek",
    "step": "stepfun",
    "stepfun": "stepfun",
}


# ============================================
# ReAct 提示词
# ============================================

# System Prompt - 完整的 ReAct 指令（工具 + 格式）
REACT_SYSTEM_PROMPT = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action as JSON
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!"""


def format_tools_for_prompt() -> tuple[str, str]:
    """格式化工具描述和工具名列表"""
    tool_descriptions = []
    tool_names = []
    for info in TOOL_DEFINITIONS:
        func = info["function"]
        params = ", ".join(
            f"{k}" for k in func["parameters"].get("properties", {}).keys()
        )
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
        self.logger = logging.getLogger(__name__)

    def _parse_action(self, text: str) -> tuple[str | None, dict | None]:
        """解析 Action 和 Action Input - 参考 LangChain 实现

        LangChain 使用简单的正则，用 \\n 作为分隔符，不依赖预测模式
        """
        # 先检查 Final Answer
        if "Final Answer:" in text:
            return None, None  # 让 _parse_final_answer 处理

        # LangChain 风格的正则：简单直接，用 \n 分隔
        match = re.search(r"Action\s*:\s*(\w+)\s*\n\s*Action Input\s*:\s*(.+)", text, re.DOTALL)

        if not match:
            return None, None

        action = match.group(1).strip()
        action_input_str = match.group(2).strip()

        # 解析 action_input
        action_input = self._parse_action_input(action_input_str)

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
            pattern = r"(\w+)\s*=\s*(\S+)"
            matches = re.findall(pattern, raw_input)
            for key, value in matches:
                value = value.rstrip(",;")
                result[key] = value

        return result

    def _parse_final_answer(self, text: str) -> str | None:
        """解析 Final Answer"""
        match = re.search(r"Final Answer:\s*", text)
        if match:
            return text[match.end() :].strip()
        return None

    def _extract_thought(self, text: str) -> str:
        """提取最后一个 Thought"""
        matches = list(
            re.finditer(
                r"Thought:\s*(.+?)(?=\n\s*(?:Action|Final Answer|Thought:)|$)",
                text,
                re.DOTALL,
            )
        )
        if matches:
            return matches[-1].group(1).strip()
        return ""

    def run(self, question: str, stream: bool = False) -> str:
        """执行 ReAct 循环"""
        tools_desc, tool_names = format_tools_for_prompt()

        # 构建固定的 system prompt
        system_prompt = REACT_SYSTEM_PROMPT.format(
            tools=tools_desc,
            tool_names=tool_names,
        )

        # 打印 system prompt
        print_box_start("🤖 System Prompt")
        for line in system_prompt.split('\n'):
            print(f"│ {line}")
        print_box_end()

        # 打印用户问题
        print_box_start("👤 User")
        print(f"│ {question}")
        print_box_end()

        # 初始化 messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Question: {question}"},
        ]

        for iteration in range(1, self.max_iterations + 1):
            print(f"\n{CYAN}🔄 第 {iteration} 轮{RESET}")

            # 调试日志
            self.logger.debug(f"=== 第 {iteration} 轮 ===")
            self.logger.debug(f"MESSAGES:\n{json.dumps(messages, ensure_ascii=False, indent=2)}")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0,
                stream=stream,
                stop=["\nObservation:", "\nObservation"],
            )

            if stream:
                output = self._handle_streaming(response)
            else:
                output = response.choices[0].message.content

            # 调试日志：记录原始输出
            self.logger.debug(f"RAW OUTPUT (repr): {repr(output)}")

            # 清理输出末尾可能的部分 stop sequence 残留
            # 匹配：\nObservation:、\nObservation、\nObserv、\nObser、\nObse、\nObs、\nOb 等
            output_cleaned = re.sub(r'\n?Ob(?:s(?:e(?:r(?:v(?:a(?:t(?:i(?:o(?:n?)?)?)?)?)?)?)?)?)?(?::)?$', '', output).strip()
            if output_cleaned != output:
                self.logger.debug(f"CLEANED OUTPUT (removed partial stop): {repr(output_cleaned)}")

            action, action_input = self._parse_action(output_cleaned)

            # 调试日志：记录解析结果
            self.logger.debug(f"PARSED: action={action}, action_input={action_input}")

            if not action:
                final_answer = self._parse_final_answer(output_cleaned)
                if final_answer and iteration > 1:
                    print(f"\n{GREEN}✅ Final Answer:{RESET}")
                    print(final_answer)
                    return final_answer
                elif final_answer and iteration == 1:
                    messages.append({"role": "assistant", "content": output_cleaned})
                    messages.append({"role": "user", "content": "(你必须先使用工具获取信息，不能直接给出答案。)"})
                    print(f"{YELLOW}⚠️ 第一轮必须先调用工具，请继续...{RESET}")
                    continue
                else:
                    messages.append({"role": "assistant", "content": output_cleaned})
                    messages.append({"role": "user", "content": "(请继续，使用正确的格式：Thought -> Action -> Action Input)"})
                    print(f"{YELLOW}⚠️ 未找到有效的 Action，提示模型继续...{RESET}")
                    continue

            # 显示本轮思考
            if not stream:
                thought = self._extract_thought(output_cleaned)
                if thought:
                    print(f"{CYAN}💭 Thought:{RESET} {thought}")
                print(f"{CYAN}🎯 Action:{RESET} {action}")
                print(
                    f"{CYAN}📥 Action Input:{RESET} {json.dumps(action_input, ensure_ascii=False)}"
                )

            # 执行工具
            observation = execute_tool(action, action_input)
            print(
                f"{GRAY}👁️ Observation:{RESET} {observation[:200]}{'...' if len(observation) > 200 else ''}"
            )

            # 追加到 messages
            messages.append({"role": "assistant", "content": output_cleaned})
            messages.append({"role": "user", "content": f"Observation: {observation}"})

        return "错误：达到最大迭代次数"

    # stop sequence 及其所有可能截断形式的正则
    # 匹配: \nO, \nOb, \nObs, \nObse, \nObser, \nObserv, ... \nObservation, \nObservation:
    STOP_PATTERN = r'\nOb(?:s(?:e(?:r(?:v(?:a(?:t(?:i(?:o(?:n?)?)?)?)?)?)?)?)?)?(?::\s*)?$'
    # 用于检测缓冲区末尾是否可能是 stop sequence 的开头
    STOP_PREFIX_RE = re.compile(r'\nOb[servaion]*$')

    def _handle_streaming(self, response) -> str:
        """流式输出 + 过滤 stop sequence"""
        collected = ""
        buffer = ""  # 缓冲区：保留最后可能构成 stop sequence 的字符

        for chunk in response:
            if not chunk.choices[0].delta.content:
                continue

            content = chunk.choices[0].delta.content
            collected += content
            buffer += content

            # 当缓冲区足够长时，尝试输出安全部分
            while len(buffer) > 15:  # "\nObservation:" 长度是 14
                # 检查缓冲区末尾是否可能是 stop sequence 的开头
                if self.STOP_PREFIX_RE.search(buffer):
                    # 末尾可能是 stop sequence，保留缓冲区，跳出
                    break
                else:
                    # 末尾安全，输出除最后 14 个字符外的内容
                    safe_len = len(buffer) - 14
                    print(buffer[:safe_len], end="", flush=True)
                    buffer = buffer[safe_len:]

        # 流结束，处理缓冲区剩余内容
        # 清理可能的 stop sequence
        cleaned_buffer = re.sub(self.STOP_PATTERN, '', buffer)
        if cleaned_buffer:
            print(cleaned_buffer, end="", flush=True)
        print()  # 换行

        # 记录原始数据到日志
        self.logger.debug(f"STREAMING RAW (repr): {repr(collected)}")

        # 返回清理后的完整结果
        return re.sub(self.STOP_PATTERN, '', collected).strip()


# ============================================
# 演示场景
# ============================================

DEMOS = {
    "1": {
        "name": "旅游规划",
        "question": "帮我规划明天的杭州一日游，需要考虑天气情况。",
        "stream": True,
    },
    "2": {
        "name": "数学计算",
        "question": "计算 (123 + 456) * (789 - 654) 的结果",
        "stream": True,
    },
    "3": {
        "name": "多步骤查询",
        "question": "告诉我现在几点了，然后帮我算一下 9876 * 5432 等于多少",
        "stream": True,
    },
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
