# ============================================
# Agent 模式实现 - OpenAI SDK + Function Calling + Web Search
# ============================================
# 说明：使用 OpenAI SDK 实现 ReAct、Plan-and-Execute 等 Agent 模式
# 对应：docs/examples/http/07-agent-patterns.http 的 Python 实现
# 特性：
#   - OpenAI SDK（兼容 StepFun API）
#   - StepFun Search API（实时网络搜索）
#   - Function Calling（工具调用循环）
# 使用：
#   uv run python agent.py 0   # 查看帮助
#   uv run python agent.py 1   # ReAct 旅游规划
#   uv run python agent.py 2   # Plan-and-Execute
#   uv run python agent.py 3   # Self-Reflection
#   uv run python agent.py 4   # Web Search
#   uv run python agent.py 5   # 流式输出
# ============================================

import asyncio
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from typing import Any, Callable

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 线程池执行器（用于并行工具调用）
_executor = ThreadPoolExecutor(max_workers=10)

# ============================================
# 输出格式化
# ============================================


def print_section(title: str):
    """打印分隔线标题"""
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print("=" * 60)


def print_box_start(title: str):
    """打印框线开始"""
    width = 60
    print(f"\n┌─ {title} " + "─" * (width - len(title) - 4) + "┐")


def print_box_end():
    """打印框线结束"""
    print("└" + "─" * 59 + "┘")


def print_tool_result(func_name: str, func_args: dict, result: str, is_last: bool = False):
    """打印工具调用结果"""
    args_str = json.dumps(func_args, ensure_ascii=False)
    # 结果预览（限制长度）
    if len(result) > 150:
        result_preview = result[:147] + "..."
    else:
        result_preview = result
    print(f"│   📥 输入: {func_name}({args_str})")
    print(f"│   📤 输出: {result_preview}")
    if not is_last:
        print("│")

# ============================================
# 配置
# ============================================

# 智谱 AI GLM Coding Plan（OpenAI 兼容）
# 注意：Coding Plan 使用专属端点，模型名小写
GLM_CLIENT = OpenAI(
    api_key=os.getenv("GLM_API_KEY"),
    base_url="https://open.bigmodel.cn/api/coding/paas/v4",
)

# ============================================
# 工具实现
# ============================================


def get_weather(location: str, date: str | None = None) -> str:
    """
    获取天气信息 - 通过 Web Search

    Args:
        location: 城市名称
        date: 日期（可选）

    Returns:
        天气信息
    """
    query = f"{location} 天气"
    if date:
        query = f"{location} {date} 天气"

    # 使用 StepFun Search API 获取实时天气
    results = _web_search_internal(query, n=3)

    if not results:
        return f"未能获取 {location} 的天气信息"

    # 返回搜索结果摘要
    return json.dumps(
        {
            "location": location,
            "date": date or "今天",
            "source": "web_search",
            "results": results[:2],
        },
        ensure_ascii=False,
    )


def get_attractions(location: str, category: str = "all") -> str:
    """
    获取景点信息 - 通过 Web Search

    Args:
        location: 城市名称
        category: 景点类别

    Returns:
        景点推荐
    """
    category_map = {
        "outdoor": "户外景点 公园",
        "indoor": "室内景点 博物馆",
        "cultural": "文化景点 古迹",
        "all": "热门景点 推荐",
    }

    query = f"{location} {category_map.get(category, '景点')} 推荐"
    results = _web_search_internal(query, n=5)

    return json.dumps(
        {"location": location, "category": category, "source": "web_search", "results": results},
        ensure_ascii=False,
    )


def get_restaurants(location: str, cuisine: str | None = None) -> str:
    """
    获取餐厅推荐 - 通过 Web Search

    Args:
        location: 城市名称
        cuisine: 菜系类型

    Returns:
        餐厅推荐
    """
    query = f"{location} 美食餐厅推荐"
    if cuisine:
        query = f"{location} {cuisine} 菜餐厅推荐"

    results = _web_search_internal(query, n=5)

    return json.dumps(
        {"location": location, "cuisine": cuisine, "source": "web_search", "results": results},
        ensure_ascii=False,
    )


def get_current_time() -> str:
    """获取当前时间（北京时间）"""
    beijing_tz = timezone(timedelta(hours=8))
    now = datetime.now(beijing_tz)
    return now.strftime("%Y-%m-%d %H:%M:%S (北京时间)")


def calculator(expression: str) -> str:
    """
    计算器 - 精确数学计算

    Args:
        expression: 数学表达式

    Returns:
        计算结果
    """
    try:
        # 安全限制
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return "错误：表达式包含不允许的字符"
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"计算错误：{str(e)}"


def web_search(query: str, n: int = 5, category: str = "") -> str:
    """
    网络搜索 - StepFun Search API

    Args:
        query: 搜索关键词
        n: 结果数量
        category: 场景类别

    Returns:
        搜索结果
    """
    results = _web_search_internal(query, n, category)
    return json.dumps({"query": query, "results": results}, ensure_ascii=False)


def _web_search_internal(query: str, n: int = 5, category: str = "") -> list[dict]:
    """内部搜索函数"""
    import httpx

    api_key = os.getenv("STEPFUN_API_KEY")
    if not api_key:
        return [{"error": "未设置 STEPFUN_API_KEY"}]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {"query": query, "n": n}
    if category:
        payload["category"] = category

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                "https://api.stepfun.com/v1/search",
                headers=headers,
                json=payload,
            )

        if response.status_code != 200:
            return [{"error": f"搜索失败: {response.status_code}"}]

        data = response.json()
        return [
            {
                "title": item.get("title"),
                "url": item.get("url"),
                "snippet": item.get("snippet", "")[:300],
            }
            for item in data.get("results", [])
        ]
    except Exception as e:
        return [{"error": str(e)}]


# ============================================
# 工具注册
# ============================================

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "城市名称"},
                    "date": {"type": "string", "description": "日期，格式 YYYY-MM-DD"},
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_attractions",
            "description": "获取指定城市的景点列表",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "城市名称"},
                    "category": {
                        "type": "string",
                        "enum": ["outdoor", "indoor", "cultural", "all"],
                        "description": "景点类别",
                    },
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_restaurants",
            "description": "获取指定城市的餐厅推荐",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "城市名称"},
                    "cuisine": {"type": "string", "description": "菜系类型"},
                },
                "required": ["location"],
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
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "执行数学计算，返回精确结果",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式"}
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "搜索互联网获取实时信息（新闻、技术文档等）",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"},
                    "n": {"type": "integer", "description": "结果数量，默认5"},
                    "category": {
                        "type": "string",
                        "enum": ["", "programming", "research", "gov", "business"],
                        "description": "搜索场景",
                    },
                },
                "required": ["query"],
            },
        },
    },
]

TOOL_IMPLEMENTATIONS: dict[str, Callable] = {
    "get_weather": get_weather,
    "get_attractions": get_attractions,
    "get_restaurants": get_restaurants,
    "get_current_time": get_current_time,
    "calculator": calculator,
    "web_search": web_search,
}


def execute_tool(tool_name: str, arguments: dict[str, Any]) -> str:
    """执行工具"""
    if tool_name not in TOOL_IMPLEMENTATIONS:
        return f"错误：未知工具 '{tool_name}'"

    func = TOOL_IMPLEMENTATIONS[tool_name]
    try:
        return str(func(**arguments))
    except Exception as e:
        return f"工具执行错误：{str(e)}"


async def execute_tool_async(tool_name: str, arguments: dict[str, Any]) -> str:
    """异步执行工具（在线程池中运行同步函数）"""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_executor, execute_tool, tool_name, arguments)
    return result


class ParallelToolExecutor:
    """并行工具执行器 - 清晰的分组输出"""

    def __init__(self, tool_calls: list[dict], round_num: int):
        self.tool_calls = tool_calls
        self.n = len(tool_calls)
        self.results: list[str | None] = [None] * self.n
        self.round_num = round_num
        self.start_time = 0.0

    async def _execute_one(self, index: int, tc: dict) -> tuple[int, str, dict]:
        """执行单个工具，返回 (index, result, args)"""
        name = tc["function"]["name"]
        args = json.loads(tc["function"]["arguments"])

        try:
            result = await execute_tool_async(name, args)
        except Exception as e:
            result = f"执行错误: {str(e)}"

        return index, result, args

    async def execute_all(self) -> list[str]:
        """并行执行所有工具"""
        self.start_time = time.time()

        # 并行执行所有工具
        tasks = [
            self._execute_one(i, tc)
            for i, tc in enumerate(self.tool_calls)
        ]
        completed = await asyncio.gather(*tasks)

        # 收集结果（保持顺序）
        results_with_args = []
        for idx, result, args in completed:
            self.results[idx] = result
            results_with_args.append((idx, result, args))

        # 按顺序排序
        results_with_args.sort(key=lambda x: x[0])

        elapsed = time.time() - self.start_time

        # 打印结果
        print_box_start(f"🔧 工具调用 - 第{self.round_num}轮 ({self.n}个工具, {elapsed:.1f}s)")
        for i, (_, result, args) in enumerate(results_with_args):
            tc = self.tool_calls[i]
            func_name = tc["function"]["name"]
            is_last = (i == len(results_with_args) - 1)
            print_tool_result(func_name, args, result, is_last)
        print_box_end()

        return self.results


# ============================================
# Agent 实现
# ============================================


class Agent:
    """基于 OpenAI SDK 的 Agent（智谱 AI GLM-4.7 Coding Plan）"""

    def __init__(self, model: str = "GLM-4.7", system_prompt: str = ""):
        self.model = model
        self.system_prompt = system_prompt
        self.messages: list[dict] = []
        self.max_iterations = 10
        self._iteration = 0  # 当前迭代计数

    def chat(self, user_input: str, stream: bool = False) -> str:
        """
        执行 Agent 对话

        流程（ReAct 模式）：
        1. 添加用户消息
        2. 调用 API
        3. 如果有 tool_calls，执行工具，添加结果，回到步骤 2
        4. 返回最终响应
        """
        if user_input:
            self.messages.append({"role": "user", "content": user_input})
            # 显示用户输入
            print_box_start("📥 用户输入")
            print(f"│ {user_input}")
            print_box_end()

        while self._iteration < self.max_iterations:
            self._iteration += 1

            # 调用 API
            print(f"🔄 调用 {self.model}...")
            response = GLM_CLIENT.chat.completions.create(
                model=self.model,
                messages=self._build_messages(),
                tools=TOOL_DEFINITIONS,
                stream=stream,
                temperature=0,
            )

            if stream:
                return self._handle_streaming(response)

            # 非流式处理
            message = response.choices[0].message

            # 检查工具调用
            if message.tool_calls:
                # 转换工具调用格式
                tool_calls_list = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ]

                # 使用并行执行器
                executor = ParallelToolExecutor(tool_calls_list, self._iteration)
                results = asyncio.run(executor.execute_all())

                # 添加 assistant 消息
                self.messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": tool_calls_list,
                })

                # 添加每个工具的结果
                for tc, result in zip(tool_calls_list, results):
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": result,
                    })
            else:
                # 无工具调用，返回最终响应
                self.messages.append({"role": "assistant", "content": message.content})
                print_box_start("🤖 最终响应")
                print_box_end()
                print(message.content or "")
                return message.content or ""

        return "错误：达到最大迭代次数"

    def _build_messages(self) -> list[dict]:
        """构建消息列表"""
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.extend(self.messages)
        return messages

    def _handle_streaming(self, response) -> str:
        """处理流式响应"""
        collected_content = ""
        collected_tool_calls: dict[int, dict] = {}

        # 流式输出模型思考
        for chunk in response:
            delta = chunk.choices[0].delta

            # 收集 content
            if delta.content:
                collected_content += delta.content
                print(delta.content, end="", flush=True)

            # 收集 tool_calls
            if delta.tool_calls:
                for tc_delta in delta.tool_calls:
                    idx = tc_delta.index

                    if idx not in collected_tool_calls:
                        collected_tool_calls[idx] = {
                            "id": "",
                            "type": "function",
                            "function": {"name": "", "arguments": ""},
                        }

                    if tc_delta.id:
                        collected_tool_calls[idx]["id"] = tc_delta.id
                    if tc_delta.function:
                        if tc_delta.function.name:
                            collected_tool_calls[idx]["function"]["name"] = tc_delta.function.name
                        if tc_delta.function.arguments:
                            collected_tool_calls[idx]["function"]["arguments"] += tc_delta.function.arguments

        print()  # 流式输出结束后换行

        # 如果有工具调用，并行执行并继续
        if collected_tool_calls:
            tool_calls_list = list(collected_tool_calls.values())

            # 使用并行执行器
            executor = ParallelToolExecutor(tool_calls_list, self._iteration)
            results = asyncio.run(executor.execute_all())

            # 添加 assistant 消息（包含所有工具调用）
            self.messages.append({
                "role": "assistant",
                "content": collected_content,
                "tool_calls": tool_calls_list,
            })

            # 添加每个工具的结果
            for tc, result in zip(tool_calls_list, results):
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                })

            # 递归继续
            return self.chat("", stream=True)

        # 最终响应
        print_box_start("🤖 最终响应")
        print_box_end()

        return collected_content

    def reset(self):
        """重置对话"""
        self.messages = []
        self._iteration = 0


# ============================================
# 演示场景
# ============================================

DEMOS = {
    "1": {
        "name": "ReAct 旅游规划",
        "desc": "规划杭州一日游，考虑天气情况",
        "system": """你是一个旅游规划助手。请使用 ReAct 模式：
1. Thought: 先思考需要什么信息
2. Action: 调用合适的工具获取信息
3. Observation: 分析工具返回的结果
4. 重复以上步骤，直到能给出完整的旅游建议

请明确说明你的思考过程。使用中文回复。""",
        "user": "帮我规划明天（2026-02-15）的杭州一日游，需要考虑天气情况。",
    },
    "2": {
        "name": "Plan-and-Execute 内容创作",
        "desc": "写一篇杭州旅游博客文章",
        "system": """你是一个内容创作助手。请使用 Plan-and-Execute 模式：

第一阶段 - 规划（Plan）：
1. 分析任务需求
2. 制定完整的执行计划
3. 列出需要调用的工具和顺序

第二阶段 - 执行（Execute）：
1. 按计划逐步调用工具
2. 收集所有信息
3. 整合成最终结果

请先输出你的计划，再开始执行。使用中文回复。""",
        "user": "写一篇关于杭州旅游的博客文章，包括天气建议、必去景点、美食推荐三个部分。",
    },
    "3": {
        "name": "Self-Reflection 数学验证",
        "desc": "计算复杂数学问题并验证",
        "system": """你是一个数学助手。请使用自我反思模式：
1. 先使用 calculator 工具解决问题
2. 分析结果是否合理
3. 如果需要，再次验证
4. 给出最终答案

使用中文回复。""",
        "user": "计算：(123 + 456) × (789 - 654) ÷ 10",
    },
    "4": {
        "name": "Web Search 实时信息",
        "desc": "搜索最新的 AI 技术进展",
        "system": "你是一个助手。需要实时信息时请使用 web_search 工具。使用中文回复。",
        "user": "搜索一下 2026 年最新的 AI 大模型技术进展，给我一个简要总结。",
    },
    "5": {
        "name": "流式输出演示",
        "desc": "计算并想象场景（流式）",
        "system": "你是一个助手。需要计算时使用 calculator 工具。使用中文回复。",
        "user": "计算 9876 * 5432，并告诉我这个结果代表什么（你可以想象一个场景）。",
    },
}


def run_demo(demo_id: str):
    """运行指定的 demo（流式输出）"""
    if demo_id not in DEMOS:
        print(f"❌ 未知的 demo ID: {demo_id}")
        return

    demo = DEMOS[demo_id]

    print_section(f"📌 {demo['name']} - {demo['desc']}")

    agent = Agent(
        model="GLM-4.7",
        system_prompt=demo["system"],
    )

    result = agent.chat(demo["user"], stream=True)

    print("\n" + "-" * 60)
    print("✅ 完成")
    print("-" * 60)


def print_help():
    """打印帮助信息"""
    print("=" * 60)
    print("Agent 模式演示 - OpenAI SDK + Function Calling + Web Search")
    print("=" * 60)
    print()
    print("用法: uv run python agent.py <demo_id>")
    print()
    print("可用的 demo:")
    for demo_id, demo in DEMOS.items():
        print(f"  {demo_id}. {demo['name']:<25} - {demo['desc']}")
    print()
    print("示例:")
    print("  uv run python agent.py 1    # ReAct 旅游规划")
    print("  uv run python agent.py 5    # 流式输出演示")
    print()


# ============================================
# 主函数
# ============================================


def main():
    if len(sys.argv) < 2:
        print_help()
        return

    demo_id = sys.argv[1]

    if demo_id in ("0", "-h", "--help", "help"):
        print_help()
        return

    run_demo(demo_id)


if __name__ == "__main__":
    main()
