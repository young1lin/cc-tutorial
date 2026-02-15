# Skill: mcp-builder

## 概述

`mcp-builder` 是用于创建高质量 MCP（Model Context Protocol）服务器的指导 Skill。它帮助开发者设计和实现 MCP 服务器，使 LLM（大型语言模型）能够通过良好设计的工具与外部服务进行交互。

**支持的实现语言**:
- **Python**: 使用 FastMCP 框架
- **TypeScript/Node.js**: 使用 MCP SDK

---

## 触发方式

### 斜杠命令

```bash
/mcp-builder
```

### 自然语言触发

```
"构建一个 MCP 服务器"
"创建一个 MCP 工具集成 [服务名]"
"帮我写一个 MCP server 连接数据库"
"实现 MCP 协议的 [功能] 服务"
```

---

## 工作原理

```
1. 分析集成需求
   ├─ 目标服务类型（数据库、API、文件系统等）
   ├─ 需要哪些工具（Tools）
   ├─ 需要哪些资源（Resources）
   └─ 需要哪些提示（Prompts）

2. 选择实现框架
   ├─ Python → FastMCP
   └─ TypeScript → @modelcontextprotocol/sdk

3. 设计 MCP 接口
   ├─ 定义工具名称和描述
   ├─ 设计输入参数（JSON Schema）
   └─ 设计输出格式

4. 生成服务器代码
   ├─ 服务器初始化
   ├─ 工具实现
   └─ 错误处理

5. 配置和部署说明
   ├─ 安装依赖
   ├─ 配置 Claude Desktop
   └─ 调试指南
```

---

## 实际演示

### 示例 1: SQLite 数据库 MCP（Python/FastMCP）

**用户请求**:
```
创建一个 SQLite 数据库的 MCP 服务器，需要支持：
1. 执行 SELECT 查询
2. 执行 INSERT/UPDATE/DELETE 操作
3. 查看表结构
4. 列出所有表
```

**生成的代码**（Python/FastMCP）:

```python
# mcp_sqlite/server.py
"""SQLite MCP Server - 使用 FastMCP 实现"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from fastmcp import FastMCP

# 初始化 MCP 服务器
mcp = FastMCP(
    name="sqlite-server",
    description="SQLite 数据库操作工具集"
)

# 数据库路径（从环境变量或默认值）
import os
DB_PATH = os.getenv("SQLITE_DB_PATH", "./database.db")


@contextmanager
def get_connection():
    """获取数据库连接（上下文管理器）"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 返回字典格式
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@mcp.tool()
def list_tables() -> list[str]:
    """列出数据库中所有表名"""
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        return [row["name"] for row in cursor.fetchall()]


@mcp.tool()
def describe_table(table_name: str) -> list[dict]:
    """
    获取指定表的结构信息

    Args:
        table_name: 要查询的表名

    Returns:
        包含列名、类型、是否可空等信息的列表
    """
    with get_connection() as conn:
        cursor = conn.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        if not columns:
            raise ValueError(f"表 '{table_name}' 不存在")
        return [
            {
                "column_id": col["cid"],
                "name": col["name"],
                "type": col["type"],
                "not_null": bool(col["notnull"]),
                "default": col["dflt_value"],
                "is_primary_key": bool(col["pk"])
            }
            for col in columns
        ]


@mcp.tool()
def execute_query(sql: str, params: list = None) -> dict:
    """
    执行 SELECT 查询语句

    Args:
        sql: SELECT 查询语句
        params: 查询参数（防止 SQL 注入）

    Returns:
        包含列名和数据行的字典
    """
    # 安全检查：只允许 SELECT 语句
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith("SELECT"):
        raise ValueError("execute_query 只支持 SELECT 语句，写操作请使用 execute_write")

    with get_connection() as conn:
        cursor = conn.execute(sql, params or [])
        rows = cursor.fetchall()
        return {
            "columns": [desc[0] for desc in cursor.description],
            "rows": [list(row) for row in rows],
            "row_count": len(rows)
        }


@mcp.tool()
def execute_write(sql: str, params: list = None) -> dict:
    """
    执行数据写操作（INSERT/UPDATE/DELETE）

    Args:
        sql: 写操作 SQL 语句
        params: 语句参数

    Returns:
        操作结果信息
    """
    # 安全检查：不允许 DROP/TRUNCATE
    sql_upper = sql.strip().upper()
    forbidden = ["DROP TABLE", "TRUNCATE", "DROP DATABASE"]
    for keyword in forbidden:
        if keyword in sql_upper:
            raise ValueError(f"不允许执行 {keyword} 操作")

    with get_connection() as conn:
        cursor = conn.execute(sql, params or [])
        return {
            "affected_rows": cursor.rowcount,
            "last_insert_id": cursor.lastrowid,
            "message": f"操作成功，影响 {cursor.rowcount} 行"
        }


if __name__ == "__main__":
    mcp.run()
```

**依赖文件**:

```toml
# pyproject.toml
[project]
name = "mcp-sqlite"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "fastmcp>=0.1.0",
]

[project.scripts]
mcp-sqlite = "mcp_sqlite.server:mcp.run"
```

**Claude Desktop 配置**:

```json
// ~/.claude/claude_desktop_config.json
{
  "mcpServers": {
    "sqlite": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_sqlite.server"],
      "env": {
        "SQLITE_DB_PATH": "/path/to/your/database.db"
      }
    }
  }
}
```

---

### 示例 2: REST API 集成 MCP（TypeScript）

**用户请求**:
```
创建一个 GitHub API 的 MCP 服务器，支持：
- 搜索仓库
- 获取仓库详情
- 列出 Issues
- 创建 Issue
```

**生成的代码**（TypeScript/Node.js）:

```typescript
// src/index.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const API_BASE = "https://api.github.com";

// GitHub API 请求辅助函数
async function githubRequest(path: string, options: RequestInit = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Authorization": `token ${GITHUB_TOKEN}`,
      "Accept": "application/vnd.github.v3+json",
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(`GitHub API Error: ${error.message}`);
  }

  return response.json();
}

// 创建 MCP 服务器
const server = new Server(
  {
    name: "github-mcp",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// 定义可用工具列表
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "search_repositories",
      description: "搜索 GitHub 仓库",
      inputSchema: {
        type: "object",
        properties: {
          query: {
            type: "string",
            description: "搜索关键词",
          },
          language: {
            type: "string",
            description: "编程语言过滤（可选）",
          },
          limit: {
            type: "number",
            description: "返回结果数量，默认 10",
            default: 10,
          },
        },
        required: ["query"],
      },
    },
    {
      name: "get_repository",
      description: "获取仓库详细信息",
      inputSchema: {
        type: "object",
        properties: {
          owner: { type: "string", description: "仓库所有者" },
          repo: { type: "string", description: "仓库名称" },
        },
        required: ["owner", "repo"],
      },
    },
    {
      name: "list_issues",
      description: "列出仓库的 Issues",
      inputSchema: {
        type: "object",
        properties: {
          owner: { type: "string" },
          repo: { type: "string" },
          state: {
            type: "string",
            enum: ["open", "closed", "all"],
            default: "open",
          },
          limit: { type: "number", default: 20 },
        },
        required: ["owner", "repo"],
      },
    },
    {
      name: "create_issue",
      description: "创建新的 Issue",
      inputSchema: {
        type: "object",
        properties: {
          owner: { type: "string" },
          repo: { type: "string" },
          title: { type: "string", description: "Issue 标题" },
          body: { type: "string", description: "Issue 正文（Markdown）" },
          labels: {
            type: "array",
            items: { type: "string" },
            description: "标签列表",
          },
        },
        required: ["owner", "repo", "title"],
      },
    },
  ],
}));

// 处理工具调用
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case "search_repositories": {
      const { query, language, limit = 10 } = args as {
        query: string;
        language?: string;
        limit?: number;
      };

      let q = query;
      if (language) q += ` language:${language}`;

      const result = await githubRequest(
        `/search/repositories?q=${encodeURIComponent(q)}&per_page=${limit}`
      );

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              result.items.map((repo: any) => ({
                name: repo.full_name,
                description: repo.description,
                stars: repo.stargazers_count,
                language: repo.language,
                url: repo.html_url,
              })),
              null,
              2
            ),
          },
        ],
      };
    }

    case "get_repository": {
      const { owner, repo } = args as { owner: string; repo: string };
      const result = await githubRequest(`/repos/${owner}/${repo}`);

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                name: result.full_name,
                description: result.description,
                stars: result.stargazers_count,
                forks: result.forks_count,
                open_issues: result.open_issues_count,
                language: result.language,
                topics: result.topics,
                license: result.license?.name,
                created_at: result.created_at,
                updated_at: result.updated_at,
              },
              null,
              2
            ),
          },
        ],
      };
    }

    case "list_issues": {
      const { owner, repo, state = "open", limit = 20 } = args as {
        owner: string;
        repo: string;
        state?: string;
        limit?: number;
      };

      const issues = await githubRequest(
        `/repos/${owner}/${repo}/issues?state=${state}&per_page=${limit}`
      );

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              issues.map((issue: any) => ({
                number: issue.number,
                title: issue.title,
                state: issue.state,
                labels: issue.labels.map((l: any) => l.name),
                created_at: issue.created_at,
                url: issue.html_url,
              })),
              null,
              2
            ),
          },
        ],
      };
    }

    case "create_issue": {
      const { owner, repo, title, body, labels } = args as {
        owner: string;
        repo: string;
        title: string;
        body?: string;
        labels?: string[];
      };

      const issue = await githubRequest(`/repos/${owner}/${repo}/issues`, {
        method: "POST",
        body: JSON.stringify({ title, body, labels }),
      });

      return {
        content: [
          {
            type: "text",
            text: `Issue 创建成功！\n编号: #${issue.number}\n标题: ${issue.title}\n链接: ${issue.html_url}`,
          },
        ],
      };
    }

    default:
      throw new Error(`未知工具: ${name}`);
  }
});

// 启动服务器
const transport = new StdioServerTransport();
await server.connect(transport);
console.error("GitHub MCP Server 已启动");
```

**package.json**:

```json
{
  "name": "github-mcp",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "tsx src/index.ts"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0",
    "tsx": "^4.0.0"
  }
}
```

**Claude Desktop 配置**:

```json
{
  "mcpServers": {
    "github": {
      "command": "node",
      "args": ["/path/to/github-mcp/dist/index.js"],
      "env": {
        "GITHUB_TOKEN": "your_github_token_here"
      }
    }
  }
}
```

---

## MCP 核心概念

### Tools（工具）

工具是 MCP 服务器暴露给 LLM 调用的功能：

```python
@mcp.tool()
def my_tool(param1: str, param2: int = 10) -> dict:
    """
    工具描述（这会成为 LLM 的提示）

    Args:
        param1: 参数1的描述
        param2: 参数2的描述（默认值10）
    """
    # 实现逻辑
    return {"result": "..."}
```

**工具设计原则**:

```
✅ 好的工具设计：
- 单一职责（一个工具做一件事）
- 清晰的参数名和描述
- 有意义的返回值
- 适当的错误处理

❌ 不好的工具设计：
- 一个工具做太多事情
- 参数命名不清晰
- 缺少错误处理
- 返回值结构混乱
```

### Resources（资源）

资源是 MCP 服务器暴露的数据（只读）：

```python
@mcp.resource("config://settings")
def get_settings() -> str:
    """暴露配置信息作为资源"""
    return json.dumps({"version": "1.0", "mode": "production"})

@mcp.resource("file://logs/{date}")
def get_logs(date: str) -> str:
    """暴露日志文件内容"""
    with open(f"logs/{date}.log") as f:
        return f.read()
```

### Prompts（提示模板）

预定义的提示词模板：

```python
@mcp.prompt()
def analyze_code(code: str, language: str) -> str:
    """代码分析提示模板"""
    return f"""
请分析以下 {language} 代码：

```{language}
{code}
```

分析维度：
1. 代码质量
2. 潜在 Bug
3. 性能问题
4. 改进建议
"""
```

---

## FastMCP vs MCP SDK

| 特性 | FastMCP (Python) | MCP SDK (TypeScript) |
|------|-----------------|---------------------|
| 语言 | Python | TypeScript/JavaScript |
| 复杂度 | 低（装饰器语法） | 中（更详细的配置） |
| 类型支持 | Python 类型注解 | TypeScript 强类型 |
| 适合场景 | 快速原型、数据处理 | 生产级、Node.js 生态 |
| 社区 | 活跃 | 官方支持 |

**选择建议**:

```
选择 FastMCP (Python) 如果：
✅ 主要处理数据（数据库、文件、API）
✅ 需要快速原型
✅ 团队熟悉 Python
✅ 需要 Python 生态（pandas, numpy 等）

选择 MCP SDK (TypeScript) 如果：
✅ 集成 Node.js 生态
✅ 团队熟悉 TypeScript
✅ 需要与前端代码共享类型
✅ 生产级部署
```

---

## 调试技巧

### 使用 MCP Inspector

```bash
# 安装 MCP Inspector
npm install -g @modelcontextprotocol/inspector

# 调试 Python MCP
mcp-inspector uv run python -m mcp_sqlite.server

# 调试 TypeScript MCP
mcp-inspector node dist/index.js
```

### 日志记录

```python
# Python: 使用 stderr（不干扰 MCP 协议）
import sys

def log(message: str):
    print(f"[MCP] {message}", file=sys.stderr)

@mcp.tool()
def my_tool(query: str) -> dict:
    log(f"执行工具: my_tool, 参数: {query}")
    result = process(query)
    log(f"工具执行完成, 结果: {result}")
    return result
```

```typescript
// TypeScript: 同样使用 stderr
console.error("[MCP] 工具被调用:", name, args);
```

---

## 安全最佳实践

### 1. 输入验证

```python
@mcp.tool()
def execute_query(sql: str) -> dict:
    # 参数验证
    if not sql or not sql.strip():
        raise ValueError("SQL 语句不能为空")

    # 注入防护
    if any(keyword in sql.upper() for keyword in ["DROP", "TRUNCATE", "ALTER"]):
        raise ValueError("不允许执行危险操作")

    # 参数化查询（永远不要字符串拼接 SQL）
    with get_connection() as conn:
        cursor = conn.execute(sql)  # 安全的查询
```

### 2. 认证和权限

```python
import os

def check_auth():
    """检查 API 密钥"""
    api_key = os.getenv("MCP_API_KEY")
    if not api_key:
        raise PermissionError("未配置 API 密钥")
    return api_key

@mcp.tool()
def sensitive_operation(data: str) -> dict:
    check_auth()  # 每个敏感操作都要检查权限
    # 执行操作...
```

### 3. 速率限制

```python
from functools import wraps
from collections import defaultdict
from time import time

call_counts = defaultdict(list)

def rate_limit(max_calls: int = 10, window: int = 60):
    """速率限制装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = func.__name__
            now = time()
            # 清理过期记录
            call_counts[key] = [t for t in call_counts[key] if now - t < window]
            if len(call_counts[key]) >= max_calls:
                raise RuntimeError(f"调用频率超限: {max_calls} 次/{window}秒")
            call_counts[key].append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

@mcp.tool()
@rate_limit(max_calls=5, window=60)  # 每分钟最多5次
def external_api_call(query: str) -> dict:
    # 调用外部 API...
```

---

## 常见问题

### Q1: MCP 服务器和普通 API 有什么区别？

**A**: MCP 专门为 LLM 设计：
- 标准化的工具描述格式（LLM 可以理解）
- 通过 stdio 通信（无需 HTTP）
- 工具描述使用自然语言
- 输出格式对 LLM 友好

### Q2: 如何处理大量数据返回？

**A**: 分页或截断：

```python
@mcp.tool()
def query_large_dataset(query: str, page: int = 1, page_size: int = 50) -> dict:
    """支持分页的大数据集查询"""
    results = execute_query(query)
    total = len(results)
    start = (page - 1) * page_size
    end = start + page_size

    return {
        "data": results[start:end],
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    }
```

### Q3: 如何更新已配置的 MCP 服务器？

**A**: 修改代码后重启 Claude Desktop 即可。

---

## 相关资源

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- [MCP SDK GitHub](https://github.com/modelcontextprotocol/typescript-sdk)
- [Layer 06 - 高级特性 (MCP)](../../../video-scripts/layer-06-advanced.md)
- [项目向量知识库 MCP 示例](../../../vector-kb-mcp/)

---

**Skill 版本**: 内置
**最后更新**: 2026-02-10
