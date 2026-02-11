# 官方 MCP 参考服务器

## 概述

Anthropic 官方维护的 5 个 MCP 参考服务器，来自 `modelcontextprotocol/servers` 仓库（78k+ Stars）。这些服务器覆盖了最常见的扩展需求，是 MCP 生态的基础。

**GitHub**: `modelcontextprotocol/servers`
**Stars**: 78k+
**类型**: 官方参考实现

---

## 快速安装汇总

```bash
# 文件系统访问
claude mcp add filesystem npx @modelcontextprotocol/server-filesystem /path/to/dir

# 网页抓取
claude mcp add fetch npx @modelcontextprotocol/server-fetch

# Git 操作
claude mcp add git uvx mcp-server-git --repository /path/to/repo

# 持久记忆
claude mcp add memory npx @modelcontextprotocol/server-memory

# 结构化推理
claude mcp add think npx @modelcontextprotocol/server-sequential-thinking
```

---

## Filesystem MCP Server {#filesystem}

### 概述

提供安全的文件系统访问，支持读写文件、目录操作，可精确控制允许访问的路径范围。

**核心价值**: 让 Claude 访问项目目录以外的文件，同时通过白名单机制确保安全。

### 安装

```bash
# 允许访问特定目录
claude mcp add filesystem npx @modelcontextprotocol/server-filesystem \
  /Users/yourname/Documents \
  /Users/yourname/Projects
```

### 完整 mcp.json 配置

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/yourname/Documents",
        "/Users/yourname/Projects"
      ]
    }
  }
}
```

### 支持的工具

| 工具 | 功能 |
|------|------|
| `read_file` | 读取文件内容 |
| `write_file` | 写入文件 |
| `list_directory` | 列出目录内容 |
| `create_directory` | 创建目录 |
| `move_file` | 移动/重命名文件 |
| `search_files` | 搜索文件内容 |
| `get_file_info` | 获取文件元数据 |

### 使用示例

```bash
$ claude

> 读取 ~/Documents/notes/ 目录下所有 Markdown 文件，
  整理成一个知识库索引
```

---

## Fetch MCP Server {#fetch}

### 概述

将网页内容转换为干净的 Markdown 格式，支持 robots.txt 遵守，适合简单的网页内容提取。

**与 firecrawl 的区别**: Fetch 适合简单静态页面，firecrawl 适合 JS 渲染的复杂页面。

### 安装

```bash
claude mcp add fetch npx @modelcontextprotocol/server-fetch
```

### 完整 mcp.json 配置

```json
{
  "mcpServers": {
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"],
      "env": {
        "IGNORE_ROBOTS_TXT": "false"  // 默认遵守 robots.txt
      }
    }
  }
}
```

### 支持的工具

| 工具 | 功能 |
|------|------|
| `fetch` | 获取 URL 内容，转换为 Markdown |

### 使用示例

```bash
$ claude

> 获取 https://docs.python.org/3/library/asyncio.html 的内容，
  总结异步编程的核心概念

> 对比以下两个 npm 包的文档，推荐哪个更适合我们的项目：
  1. https://npmjs.com/package/zod
  2. https://npmjs.com/package/yup
```

---

## Git MCP Server {#git}

### 概述

提供 Git 仓库操作工具，让 Claude 直接读取提交历史、分支信息、文件变更等。

**核心价值**: 结合 Git 历史上下文进行代码审查和重构决策。

### 安装

```bash
# 需要 Python uvx
claude mcp add git uvx mcp-server-git --repository /path/to/repo

# 或多个仓库
claude mcp add git uvx mcp-server-git \
  --repository /path/to/repo1 \
  --repository /path/to/repo2
```

### 完整 mcp.json 配置

```json
{
  "mcpServers": {
    "git": {
      "command": "uvx",
      "args": [
        "mcp-server-git",
        "--repository",
        "/path/to/your/repo"
      ]
    }
  }
}
```

### 支持的工具

| 工具 | 功能 |
|------|------|
| `git_log` | 查看提交历史 |
| `git_diff` | 查看变更内容 |
| `git_status` | 查看工作区状态 |
| `git_show` | 查看特定提交 |
| `git_branch` | 列出/切换分支 |
| `git_blame` | 查看代码行作者 |

### 使用示例

```bash
$ claude

> 查看过去 30 天的提交历史，找出哪些文件修改最频繁，
  这些文件可能是最脆弱的部分

> 分析 src/auth/ 目录的 git blame，
  了解这部分代码的演化历史，再帮我规划重构方案

> 比较 main 和 feature/new-api 分支的差异，
  评估这个 PR 的影响范围
```

---

## Memory MCP Server {#memory}

### 概述

基于知识图谱的持久化记忆系统，让 Claude 跨会话记住实体、关系和事实。

**与 claude-mem 的区别**:
- `Memory MCP`: 结构化知识图谱，适合记录实体和关系
- `claude-mem`: 基于向量搜索，适合记录对话上下文和偏好

### 安装

```bash
claude mcp add memory npx @modelcontextprotocol/server-memory
```

### 完整 mcp.json 配置

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "/Users/yourname/.claude-memory/knowledge.json"
      }
    }
  }
}
```

### 支持的工具

| 工具 | 功能 |
|------|------|
| `create_entities` | 创建实体（人、地点、概念） |
| `create_relations` | 创建实体间关系 |
| `add_observations` | 为实体添加观察/属性 |
| `search_nodes` | 语义搜索知识图谱 |
| `read_graph` | 读取完整图谱 |
| `delete_entities` | 删除实体 |

### 使用示例

```bash
$ claude

> 记住：我们的技术栈是 Next.js 14 + NestJS + PostgreSQL + Redis。
  团队成员：张三（前端）、李四（后端）、王五（DevOps）

> 我们决定将认证系统从 Passport.js 迁移到 Lucia Auth，
  记录这个决定和原因：因为 Passport.js 与 NestJS 的集成太复杂

# 下次会话时
> 根据你记住的项目信息，帮我评估是否应该引入 tRPC
```

---

## Sequential Thinking MCP Server {#sequential-thinking}

### 概述

通过结构化的分步推理框架，帮助 Claude 处理需要深度思考的复杂问题。

**核心价值**: 对于多步骤决策、系统设计、复杂调试，引导 Claude 分步推理而不是直接跳到结论。

### 安装

```bash
claude mcp add think npx @modelcontextprotocol/server-sequential-thinking
```

### 完整 mcp.json 配置

```json
{
  "mcpServers": {
    "sequentialThinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

### 工作原理

```
复杂问题
    │
    ▼
思维步骤 1: 问题拆解
    │         └── 可以回溯修改
    ▼
思维步骤 2: 信息收集
    │         └── 可以分支推理
    ▼
思维步骤 3: 方案评估
    │
    ▼
思维步骤 N: 最终结论
```

每个思维步骤都可以：修订之前的想法、探索新方向、标记假设性结论

### 使用示例

```bash
$ claude

> 我需要为一个日处理 100 万次交易的支付系统设计数据库架构，
  请使用结构化推理，考虑：一致性、性能、可扩展性、故障恢复

> 我有一个生产环境的内存泄漏问题，
  已知：每小时内存增加约 50MB，在处理 WebSocket 连接时更明显。
  请分步骤分析可能的原因并给出排查方案
```

---

## 完整 mcp.json 示例（所有 5 个服务器）

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/yourname/Documents",
        "/Users/yourname/Projects"
      ]
    },
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    },
    "git": {
      "command": "uvx",
      "args": [
        "mcp-server-git",
        "--repository",
        "/Users/yourname/Projects/myapp"
      ]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "sequentialThinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

配置文件位置：`~/.claude/mcp.json`（全局）或 `.mcp.json`（项目级）

---

## 服务器对比速查

| 服务器 | 最适合场景 | Token 消耗 | 依赖 |
|--------|-----------|-----------|------|
| Filesystem | 跨目录文件操作 | 按文件大小 | Node.js |
| Fetch | 静态网页内容提取 | 按页面大小 | Node.js |
| Git | 代码历史分析 | 低 | Python/uvx |
| Memory | 长期知识图谱 | 极低 | Node.js |
| Sequential Thinking | 复杂推理任务 | 中等（多步骤） | Node.js |

---

## 相关工具

- [firecrawl](./firecrawl.md) - Fetch 的升级版，支持 JS 渲染
- [claude-mem](./claude-mem.md) - Memory 的升级版，支持向量搜索
- [figma-mcp](./figma-mcp.md) - 第三方 MCP 服务器示例

---

**最后更新**: 2026-02-10
