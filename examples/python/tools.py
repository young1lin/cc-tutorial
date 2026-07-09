# ============================================
# 共享工具
# ============================================
# 说明：工具定义和实现，供各 Agent 使用
# ============================================

import json
import os
from datetime import datetime, timezone, timedelta
from typing import Any, Callable

import httpx

# ============================================
# Web Search - 智谱 MCP (Coding Plan)
# ============================================

MCP_URL = "https://open.bigmodel.cn/api/mcp/web_search_prime/mcp"
_mcp_session_id: str | None = None


def _mcp_initialize(client: httpx.Client, api_key: str) -> str:
    """初始化 MCP 会话，返回 session ID"""
    global _mcp_session_id

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json, text/event-stream",
    }

    payload = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "python-agent", "version": "1.0.0"},
        },
        "id": 1,
    }

    resp = client.post(MCP_URL, headers=headers, json=payload, timeout=30)
    _mcp_session_id = resp.headers.get("mcp-session-id")
    return _mcp_session_id


def _parse_sse_response(text: str) -> dict:
    """解析 SSE 格式响应"""
    for line in text.strip().split("\n"):
        if line.startswith("data:"):
            data_str = line[5:].strip()
            if data_str:
                return json.loads(data_str)
    return {}


def web_search(query: str, n: int = 5) -> list[dict]:
    """
    网络搜索 - 智谱 MCP webSearchPrime (Coding Plan)

    Args:
        query: 搜索关键词
        n: 结果数量（MCP 返回固定数量，此参数保留兼容）

    Returns:
        搜索结果列表 [{"title", "url", "snippet", "media"}, ...]
    """
    api_key = os.getenv("GLM_API_KEY")
    if not api_key:
        return [{"error": "未设置 GLM_API_KEY"}]

    global _mcp_session_id

    try:
        with httpx.Client(timeout=30.0) as client:
            # 如果没有 session，先初始化
            if not _mcp_session_id:
                _mcp_initialize(client, api_key)

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json, text/event-stream",
                "mcp-session-id": _mcp_session_id,
            }

            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "webSearchPrime",
                    "arguments": {"search_query": query},
                },
                "id": 2,
            }

            resp = client.post(MCP_URL, headers=headers, json=payload)

            if resp.status_code != 200:
                return [{"error": f"搜索失败: {resp.status_code}"}]

            # 解析 SSE 响应
            result = _parse_sse_response(resp.text)

            if result.get("result", {}).get("isError"):
                error_text = result["result"]["content"][0]["text"]
                return [{"error": error_text}]

            # 解析搜索结果（双重 JSON 编码）
            content = result.get("result", {}).get("content", [])
            if content and content[0].get("type") == "text":
                # 第一次解析：SSE data 里的 text 字段是 JSON 字符串
                text = content[0]["text"]
                parsed = json.loads(text)
                # 第二次解析：parsed 仍然是 JSON 字符串，需要再解析
                if isinstance(parsed, str):
                    search_results = json.loads(parsed)
                else:
                    search_results = parsed
                return [
                    {
                        "title": item.get("title"),
                        "url": item.get("link"),
                        "snippet": (item.get("content") or "")[:300],
                        "media": item.get("media"),
                        "publish_date": item.get("publish_date"),
                    }
                    for item in search_results
                ]

            return []
    except Exception as e:
        return [{"error": str(e)}]


# ============================================
# 工具实现
# ============================================

# 城市名映射
LOCATION_MAP = {
    "杭州": "杭州",
    "Hangzhou": "杭州",
    "hangzhou": "杭州",
    "北京": "北京",
    "Beijing": "北京",
    "上海": "上海",
    "Shanghai": "上海",
}


def get_weather(location: str, date: str | None = None) -> str:
    """获取天气信息 - 通过 Web Search"""
    normalized_location = LOCATION_MAP.get(location, location)
    query = f"{normalized_location} {date} 天气" if date else f"{normalized_location} 天气"
    results = web_search(query, n=3)
    return json.dumps({"location": normalized_location, "date": date or "今天", "results": results}, ensure_ascii=False)


def get_attractions(location: str, category: str = "all") -> str:
    """获取景点信息 - 通过 Web Search"""
    normalized_location = LOCATION_MAP.get(location, location)
    query = f"{normalized_location} {category} 景点推荐"
    results = web_search(query, n=5)
    return json.dumps({"location": normalized_location, "category": category, "results": results}, ensure_ascii=False)


def get_restaurants(location: str, cuisine: str | None = None) -> str:
    """获取餐厅推荐 - 通过 Web Search"""
    normalized_location = LOCATION_MAP.get(location, location)
    query = f"{normalized_location} {cuisine or ''} 美食餐厅推荐"
    results = web_search(query, n=5)
    return json.dumps({"location": normalized_location, "cuisine": cuisine, "results": results}, ensure_ascii=False)


def get_current_time() -> str:
    """获取当前时间（北京时间）"""
    beijing_tz = timezone(timedelta(hours=8))
    now = datetime.now(beijing_tz)
    return now.strftime("%Y-%m-%d %H:%M:%S (北京时间)")


def calculator(expression: str) -> str:
    """计算器"""
    try:
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return "错误：表达式包含不允许的字符"
        return str(eval(expression))
    except Exception as e:
        return f"计算错误：{str(e)}"


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
                    "category": {"type": "string", "enum": ["outdoor", "indoor", "cultural", "all"]},
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
                "properties": {"expression": {"type": "string", "description": "数学表达式"}},
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "搜索互联网获取实时信息",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "搜索关键词"}},
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
    "web_search": lambda query: json.dumps({"query": query, "results": web_search(query)}, ensure_ascii=False),
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
