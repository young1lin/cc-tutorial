# 插件：firecrawl

## 概述

`firecrawl` 是一个强大的 Web 数据抓取工具，提供 MCP 服务器和 Python/JS SDK 双重接入方式。支持抓取现代 JavaScript 渲染网站，将网页内容转换为干净的 Markdown 格式供 Claude 使用。

**Stars**: 70k+
**GitHub**: `firecrawl/firecrawl`
**类型**: MCP 服务器 + SDK
**官方文档**: `docs.firecrawl.dev`

**解决的核心问题**：
- 普通 `curl` 或 `fetch` 无法抓取 React/Next.js 等 JS 渲染的动态页面
- 整站爬取时无法处理反爬虫、分页、动态内容
- 竞品文档分析、API 文档提取等场景需要批量处理

**使用场景**:
- 抓取竞品文档生成对比报告
- 提取第三方 API 文档注入 Claude 上下文
- 监控网页内容变化
- 收集训练数据或研究材料

---

## 安装

### MCP 服务器方式（推荐）

```bash
# 需要先在 firecrawl.dev 获取 API Key
claude mcp add firecrawl --api-key YOUR_API_KEY
```

验证安装：

```bash
claude
> /mcp
# 应该看到 firecrawl 已连接
```

### SDK 方式

```bash
# Python
pip install firecrawl-py

# Node.js
npm install @mendable/firecrawl-js
```

---

## 核心命令

firecrawl 提供 5 个核心操作：

| 命令 | 用途 | 典型场景 |
|------|------|---------|
| `scrape` | 抓取单个页面 | 获取文档页、博客文章 |
| `crawl` | 爬取整个网站 | 抓取文档站点全部内容 |
| `search` | 搜索 + 抓取结果 | 研究特定主题并获取内容 |
| `map` | 发现网站 URL 结构 | 了解网站结构再决定抓什么 |
| `agent` | AI 自主爬取 | 复杂抓取任务，让 AI 决定路径 |

---

## 实际演示

### 通过 MCP 让 Claude 抓取网页

```bash
$ claude

> 帮我抓取 https://docs.stripe.com/api/payments 的内容，
  提取所有 API 端点和参数，整理成表格
```

Claude 会自动调用 firecrawl MCP 工具完成抓取。

### 整站爬取（SDK 示例）

```python
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key="your-api-key")

# 爬取整个文档站点
result = app.crawl_url(
    "https://docs.example.com",
    params={
        "limit": 100,           # 最多爬取 100 页
        "scrapeOptions": {
            "formats": ["markdown"],  # 输出 Markdown 格式
        }
    }
)

# 保存为 Claude 可读格式
for page in result["data"]:
    print(f"## {page['metadata']['title']}\n")
    print(page["markdown"])
```

### 竞品文档对比

```bash
$ claude

> 分别抓取以下两个文档站点，对比它们的 API 设计差异：
  1. https://docs.openai.com/api-reference
  2. https://docs.anthropic.com/reference

  重点关注：认证方式、速率限制、错误处理
```

### 搜索 + 抓取

```python
# 搜索并直接获取内容
results = app.search(
    "Claude Code MCP server tutorial 2026",
    params={
        "limit": 5,
        "scrapeOptions": {"formats": ["markdown"]}
    }
)
```

---

## MCP 配置文件

手动编辑 `~/.claude/mcp.json`：

```json
{
  "mcpServers": {
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "your-api-key"
      }
    }
  }
}
```

---

## 实战场景

### 场景 1：构建文档问答系统

```bash
# 抓取整个 Next.js 文档
> 爬取 https://nextjs.org/docs，然后回答：
  Next.js 14 的 App Router 和 Pages Router 有什么本质区别？
```

### 场景 2：监控 API 变更

```python
import hashlib
from firecrawl import FirecrawlApp

def check_api_changes(url: str):
    app = FirecrawlApp(api_key="your-key")
    result = app.scrape_url(url, formats=["markdown"])
    content = result["markdown"]

    # 计算内容哈希
    content_hash = hashlib.md5(content.encode()).hexdigest()
    return content_hash
```

### 场景 3：注入文档上下文

```bash
# 将抓取内容保存为文件，再发给 Claude
$ firecrawl scrape https://docs.example.com/api > api-docs.md
$ claude "这是 API 文档，帮我根据它写一个 TypeScript 客户端" < api-docs.md
```

---

## 常见问题

### Q1: 需要付费吗？

**A**: 提供免费额度（500 次/月），超出后按量付费。自托管版本完全免费。

### Q2: 会被反爬虫拦截吗？

**A**: firecrawl 使用无头浏览器并有反检测措施，对大多数网站有效。但不建议用于明确禁止爬取的网站。

### Q3: 抓取速度怎么样？

**A**: 单页通常 2-5 秒，整站爬取支持并发，速度取决于目标网站。

### Q4: 支持登录后的页面吗？

**A**: 支持，可以通过设置 Cookie 或使用 `agent` 模式自动登录。

---

## 技巧与最佳实践

### 使用 Markdown 格式减少 Token

```python
# 指定输出 Markdown，去掉 HTML 标签
result = app.scrape_url(url, formats=["markdown"])
# 相比原始 HTML，token 使用量减少 60-80%
```

### 结合 repomix 管理大量文档

```bash
# 先爬取，再用 repomix 打包
firecrawl crawl docs.example.com --output ./docs-cache/
repomix ./docs-cache/ --output docs-context.xml
```

### 利用 `map` 先规划再抓取

```python
# 先了解网站结构，再决定抓哪些页面
urls = app.map_url("https://docs.example.com")
# 过滤只需要的 URL
api_urls = [u for u in urls if "/api" in u]
```

---

## 相关工具

- [Fetch MCP Server](./official-mcp-servers.md#fetch) - 官方简单网页抓取（无 JS 渲染）
- [repomix](./repomix.md) - 配合使用，打包抓取结果

---

**工具版本**: 最新
**最后更新**: 2026-02-10
