# 补充：从 Function Calling 到 MCP —— 协议标准化详解

> 本文从 `layer-01-theory.md` 第 4.6 节拆分而来，供深入了解 MCP 协议原理使用。
>
> 动手实践首选：[minimal-mcp](https://github.com/young1lin/minimal-mcp) — 从零理解 MCP 协议的完整实现。
>
> Claude Code 中 MCP 的实际配置和使用见**第六层（高级功能）**。

---

## 问题：Function Calling 的碎片化

上面我们看到了两种协议（OpenAI 格式 vs Anthropic 格式），加上历史上的 Text ReAct、XML、JSON 格式。每个 AI 工具（Cursor、Cline、Claude Code、Copilot）都有自己的工具调用方式。

这带来了一个严重问题：**工具开发者要为每个 AI 平台写一遍适配**。

```
同一个"查天气"工具，需要适配：
  ├── OpenAI Function Calling 格式
  ├── Anthropic Function Calling 格式
  ├── Cline 的 XML 工具格式
  ├── Cursor 的工具调用格式
  └── ... 每出一个新 AI 工具，再适配一遍
```

## 解决方案：MCP（Model Context Protocol）

MCP 就是为了解决这个问题而诞生的——**一个统一的协议标准，让工具只写一次，到处运行**。

```
没有 MCP 的世界：
  天气工具 ─→ 适配 OpenAI
  天气工具 ─→ 适配 Anthropic
  天气工具 ─→ 适配 Cursor
  天气工具 ─→ 适配 Cline
  ... N 个平台 × M 个工具 = N×M 个适配

有 MCP 的世界：
  天气工具 ─→ 实现 MCP 协议（写一次）
       ↓
  MCP Client（Claude Code / Cursor / Cline / ...）自动对接
  ... N 个平台 + M 个工具 = N+M 个实现
```

> **核心类比**：MCP 之于 AI 工具，就像 USB 之于外设。没有 USB 标准之前，每个设备都需要专用接口；有了 USB，一个口通吃所有设备。

## MCP 的三大能力

MCP 不仅仅是 Function Calling 的标准化。它提供了**三种能力**：

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Server                            │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Tools       │  │  Resources   │  │   Prompts    │  │
│  │   工具        │  │  资源        │  │   提示词模板  │  │
│  │               │  │              │  │               │  │
│  │  执行操作     │  │  读取数据    │  │  预设模板     │  │
│  │  • 查天气     │  │  • 配置文件  │  │  • 代码审查   │  │
│  │  • 执行SQL    │  │  • 数据库表  │  │  • Bug修复    │  │
│  │  • 调API      │  │  • 日志文件  │  │  • 测试生成   │  │
│  │  • 写文件     │  │  • API响应   │  │  • 文档撰写   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

| 能力 | 定义 | 等价于 | 例子 |
|------|------|--------|------|
| **Tools** | 可执行的操作 | Function Calling 中的 function | 查天气、执行 SQL、调用 API |
| **Resources** | 只读数据源 | 给模型额外的上下文信息 | 数据库 Schema、配置文件、日志 |
| **Prompts** | 预定义的提示词模板 | System Prompt 的模块化 | 代码审查模板、Bug 修复流程 |

**为什么 Resources 很重要？** 因为它解决了一个 Function Calling 解决不了的问题——**被动地向模型提供信息，而不需要模型主动调用**。

```
Function Calling: 模型必须主动说"我要查数据库 Schema"
Resources:        MCP Server 自动把 Schema 提供给模型，模型直接就知道
```

## MCP 协议架构

```
┌──────────────┐         JSON-RPC 2.0          ┌──────────────┐
│              │  ←─── stdio / HTTP / SSE ───→  │              │
│  MCP Client  │                                │  MCP Server  │
│  (Claude Code)│  Request:  {method, params}   │  (你写的)     │
│              │  Response: {result}            │              │
│              │  Error:    {error}             │              │
└──────────────┘                                └──────────────┘
```

**传输方式**：
- **stdio**：本地进程通信，Claude Code 默认使用
- **HTTP/SSE**：远程服务器，适合团队共享的 MCP 服务

**消息格式**（JSON-RPC 2.0）：

```json
// 请求
{ "jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": { "name": "get_weather", "arguments": { "location": "hangzhou" } } }

// 成功响应
{ "jsonrpc": "2.0", "id": 1, "result": { "content": [{ "type": "text", "text": "Sunny, 29°C" }] } }

// 错误响应
{ "jsonrpc": "2.0", "id": 1, "error": { "code": -32602, "message": "Invalid location" } }
```

## MCP 与 Claude Code 的关系

Claude Code 本身就是一个 MCP Client。它的内置工具（Read、Write、Edit、Bash、Glob、Grep...）其实就是内置的 "Tool"。当你配置外部 MCP Server 时，就是在给 Claude Code 增加更多的工具。

```
Claude Code 的工具来源：
  ├── 内置工具（Read, Write, Edit, Bash, Glob, Grep, WebFetch...）
  ├── 你配置的 MCP Server（数据库、API、文件系统...）
  └── Skills（模块化的 Prompt + Tool 组合）
```

**常见 MCP Server**：

| 名称 | 功能 | 来源 |
|------|------|------|
| filesystem | 文件系统读写 | Anthropic 官方 |
| memory | 跨会话记忆 | Anthropic 官方 |
| Git | Git 操作 | Anthropic 官方 |
| firecrawl | JS 渲染网页抓取 | 社区 |
| claude-mem | 跨会话记忆增强 | 社区 |
| repomix | 代码打包 | 社区 |

## 动手实现一个 MCP Server

用 Python FastMCP 写一个最简单的 MCP Server：

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo-server")

@mcp.tool()
def get_weather(location: str) -> str:
    """获取指定城市的天气信息
    Args:
        location: 城市名称（如 hangzhou, beijing）
    """
    # 实际项目中这里调用天气 API
    return f"{location}: Sunny, 29°C"

@mcp.resource("config://app")
def get_config() -> str:
    """提供应用配置信息"""
    return "{ \"version\": \"1.0\", \"debug\": false }"

@mcp.prompt()
def code_review(code: str) -> str:
    """代码审查提示词模板"""
    return f"请审查以下代码，重点关注安全性和性能：\n\n{code}"
```

> **注意区别**：`@mcp.tool()` 定义的是 Tools（可执行操作），`@mcp.resource()` 定义的是 Resources（只读数据），`@mcp.prompt()` 定义的是 Prompts（提示词模板）。

完整的从零实现，看这个项目：[minimal-mcp](https://github.com/young1lin/minimal-mcp)
