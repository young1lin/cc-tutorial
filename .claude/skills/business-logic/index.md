# Business Logic 索引

> 本项目知识单元的导航。由 `/business-logic init` 和 `sync` 维护。
> cc-tutorial 是**文档/教程仓库**,非业务代码库。下列为内容领域;每个 `overview.md` 是进入该领域的地图。

**每个条目都带说明,不只是标题。** 光秃秃的链接无法判断是否该点开。领域及其 sub-docs 都要列出。

## 领域

### video-scripts

- [video-scripts](video-scripts/overview.md) -- **从此开始**;Claude Code 9 层视频教程脚本(theory→setup→basics→workflow→config→advanced→caveats→practice→supplement)+ MCP / 注意力机制两份补充。问"教程讲了什么"时先读。
  - [agent-patterns](video-scripts/agent-patterns.md) -- layer-01 的 Agent 设计模式深度(ReAct / Plan-Execute / Self-Reflection / Multi-Agent + Lilian Weng 三组件)。
  - [hooks-and-headless](video-scripts/hooks-and-headless.md) -- layer-06 的 Hooks 七生命周期 + Headless 参数 + ralph-loop 机制。
  - [subagent-and-sdk](video-scripts/subagent-and-sdk.md) -- SubAgent 三独立性 + Agent SDK(query / ClaudeSDKClient / @tool / 结构化输出)。

### examples

- [examples](examples/overview.md) -- **从此开始**;可运行示例:HTTP API(97 请求)、Python Agent 模式、ASR 字幕、官方 Skills 文档、推荐插件、Hook 脚本。问"示例代码 / API 调用形态"时读。
  - [mcp-websearch-client](examples/mcp-websearch-client.md) -- `python/tools.py` 的 MCP `webSearchPrime` 客户端深度(session / JSON-RPC / SSE 双重解码)。
  - [ralph-loop-stop-hook](examples/ralph-loop-stop-hook.md) -- `scripts/stop-hook.py` 的 Ralph Loop 状态机(2 态 4 迁移 / promise 终止)。
  - [asr-subtitle-architecture](examples/asr-subtitle-architecture.md) -- `asr/subtitle.py` 双线程架构(VAD / 推理解耦 + preview 合并 + gen 代次)。

### research

- [research](research/overview.md) -- **从此开始**;17 份研究材料(00-summary + 01–16),全部事实声明的证据基础,按 7 个主题簇分组,带 T1–T4 分级。验证声明或追溯概念来源时读。

### tooling

- [tooling](tooling/overview.md) -- **从此开始**;本项目自带的 Claude Code 配置:`/commit-push`、`evidence-based` 与 `voice-and-tone` 规则、`business-logic-researcher` agent。问"本仓库工具如何运转"时读。

## 跨领域关系图

```
research (证据基础)
   │
   ▼
video-scripts (9 层教程) ◄──────► examples (可运行代码)
   │                                 │
   └────────► tooling (规则约束全部内容) ◄┘
```

- `video-scripts` ↔ `examples`:每层概念都有对应的 HTTP/Python 示例(layer-01 Function Calling ↔ `examples/http/04`、`examples/python/00`)。
- `video-scripts` ↔ `research`:脚本里每个事实声明都可追溯到 `research/`(Boris Cherny、Addy Osmani、Anthropic 官方)。
- `tooling` → 全部:`evidence-based` / `voice-and-tone` 规则约束每个领域的内容。
