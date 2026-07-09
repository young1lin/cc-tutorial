# Claude Code 插件推荐

Claude Code 的插件生态由三种形式组成，本目录收录了按 Star 数排名的热门工具。

---

## 插件类型说明

| 类型 | 安装方式 | 特点 |
|------|---------|------|
| **npm 插件** | `/plugin install <名称>` | 通过 Claude Code 插件系统管理，深度集成生命周期 Hook |
| **MCP 服务器** | `claude mcp add <名称> <命令>` | 通过 Model Context Protocol 扩展 Claude 能力，支持工具调用 |
| **独立 CLI 工具** | `npm install -g <名称>` | 独立运行，与 Claude Code 配合使用 |

---

## 热门工具排名（按 Star 数）

| 工具 | Stars | 类型 | 解决的核心问题 | 文档 |
|------|-------|------|--------------|------|
| [firecrawl](https://github.com/firecrawl/firecrawl) | 70k+ | MCP 服务器 | 抓取 JS 渲染网站、提取文档 | [详情](./firecrawl.md) |
| [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | 78k+ | MCP 服务器 | 官方参考实现（文件/网络/Git/记忆） | [详情](./official-mcp-servers.md) |
| [claude-mem](https://github.com/thedotmack/claude-mem) | ~20k | npm 插件 | 跨会话长期记忆，解决 Claude 失忆问题 | [详情](./claude-mem.md) |
| [ccusage](https://github.com/ryoppippi/ccusage) | 10k+ | 独立 CLI | Token 用量统计与成本监控 | [详情](./ccusage.md) |
| [claude-squad](https://github.com/smtg-ai/claude-squad) | 5.6k | 独立 CLI | 多代理并行管理 | [详情](./claude-squad.md) |
| [repomix](https://github.com/yamadashy/repomix) | 热门 | 独立 CLI | 将整个代码库打包为 AI 优化格式 | [详情](./repomix.md) |
| Figma MCP | 官方 | MCP 服务器 | 从 Figma 设计稿直接生成代码 | [详情](./figma-mcp.md) |
| code-review 插件 | 官方 | npm 插件 | 5 个并行代理从不同角度审查 PR | [详情](./code-review-plugin.md) |

---

## 按使用场景分类

### 记忆持久化
- **[claude-mem](./claude-mem.md)** - SQLite + 向量搜索，自动捕获和检索对话历史
- **[Memory MCP Server](./official-mcp-servers.md#memory)** - 官方 Key-Value 持久记忆

### 设计集成
- **[figma-mcp](./figma-mcp.md)** - Figma 官方 MCP，直接读取设计组件生成代码

### 代码质量
- **[code-review 插件](./code-review-plugin.md)** - 5 代理并行 PR 审查，置信度过滤
- **[Sequential Thinking MCP](./official-mcp-servers.md#sequential-thinking)** - 结构化推理辅助复杂分析

### 数据抓取
- **[firecrawl](./firecrawl.md)** - 抓取现代 JS 渲染网站，支持整站爬取
- **[Fetch MCP Server](./official-mcp-servers.md#fetch)** - 网页内容转 Markdown

### 成本监控
- **[ccusage](./ccusage.md)** - 实时追踪 Token 用量、成本估算、缓存命中率

### 多代理协作
- **[claude-squad](./claude-squad.md)** - tmux + git worktrees 管理多个并行 AI 代理

### 上下文管理
- **[repomix](./repomix.md)** - 将整个仓库打包为单文件，方便投喂给 Claude

---

## 安装方式速查

```bash
# npm 插件（在 Claude Code 会话中）
/plugin install claude-mem
/plugin install pr-review-toolkit

# MCP 服务器
claude mcp add firecrawl --api-key YOUR_KEY
claude mcp add --transport http figma https://mcp.figma.com/mcp
claude mcp add filesystem npx @modelcontextprotocol/server-filesystem /path/to/dir
claude mcp add fetch npx @modelcontextprotocol/server-fetch
claude mcp add git uvx mcp-server-git --repository /path/to/repo
claude mcp add memory npx @modelcontextprotocol/server-memory
claude mcp add think npx @modelcontextprotocol/server-sequential-thinking

# 独立 CLI 工具
npm install -g ccusage
npm install -g claude-squad
npm install -g repomix
```

---

## 社区资源

- [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) - 精选插件、工具、Skill 列表
- [awesome-claude-code-toolkit](https://github.com/hesreallyhim/awesome-claude-code-toolkit) - 深度工具集
- [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) - 官方 MCP 服务器仓库

---

**最后更新**: 2026-02-10
