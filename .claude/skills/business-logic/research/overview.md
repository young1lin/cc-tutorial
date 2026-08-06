# research 研究材料 Overview

> last_verified_commit: 3cf4d89
> source_paths: research/

## 快速索引

- **索引文件:** research/00-research-summary.md
- **T1 官方源头:** research/01, research/06, research/08, research/09, research/10, research/11, research/12, research/13, research/14, research/15, research/16
- **T2 专家实践:** research/03, research/04, research/05, research/07
- **T3 社区共识:** research/02
- **高频主题:** best-practices, plan-mode, workflow, subagents, skills, loops, dynamic-workflows, agent-teams, prompt-caching, RAG, LSP

## 领域概述

research/ 是整个教程的证据基础。16 份资料覆盖 Anthropic 官方文档、知名专家博文、经典 prompt 模板和基础设施协议研究，所有 factual claim 必须追溯到此处。证据分级体系(T1-T4)的定义和引用规则也源于这里。

## 资料清单

| 文件 | 作者 | Tier | 主题 | 关键论点 |
|------|------|------|------|----------|
| research/00-research-summary.md | Research Compilation | T4 | 综合索引 | 全局研究汇总；Plan Mode/多实例/验证机制/CLAUDE.md/人在循环的共识提炼 |
| research/01-claude-code-best-practices-anthropic-official.md | Boris Cherny & Anthropic Engineering Team | T1 | 最佳实践 | Claude Code 创建者主笔的权威指南；CLAUDE.md/TDD/多实例/headless 模式的官方推荐 |
| research/02-plan-mode-guide-official.md | claude-ai.chat (社区源) | T3 | Plan Mode | Plan Mode 使用时机与反模式；社区整理，非 Anthropic 官方域名 |
| research/03-andrew-ng-course-outline.md | Elie Schoppik, Andrew Ng (DeepLearning.AI) | T2 | 课程大纲 | Anthropic 官方合作课程；10 节课覆盖 RAG/Figma/Jupyter 三实战项目 |
| research/04-addy-osmani-2026-workflow.md | Addy Osmani (Google Chrome Engineer) | T2 | 工作流 | "AI 辅助工程"而非"AI 自动化工程"；十大实践：spec 先行/小块迭代/人在循环 |
| research/05-boris-cherny-workflow-x-thread.md | Boris Cherny (Claude Code Creator) | T2 | 个人工作流 | 并行 5 个 Claude 实例；标签编号+系统通知；极简配置哲学 |
| research/06-anthropic-internal-ai-transforming-work.md | Saffron Huang, Bryan Seethor 等 (Anthropic) | T1 | 内部调研 | 132 名工程师调研；生产力自报 +20% 到 +50%；PR 数增 67% |
| research/07-hwchase17-react-prompt.md | Harrison Chase (LangChain 创始人) | T2 | Prompt 模板 | 经典 ReAct 提示词模板；Thought/Action/Observation 循环定义 |
| research/08-lsp-language-server-protocol.md | Research Compilation | T1 | 开发工具协议 | LSP 定义、历史、JSON-RPC 机制；与 Tree-sitter 对比；IDE 集成 |
| research/09-prompt-caching-and-kv-cache.md | Research Compilation | T1 | Prompt 缓存 | Anthropic 三字段缓存计数器；cache hierarchy tools->system->messages 结构性命中 |
| research/10-langchain-rag-cache-shape.md | Research Compilation | T1 | RAG + 缓存 | LangChain RAG 把检索内容放 system prompt 会破坏下游缓存复用 |
| research/11-claude-code-subagents.md | Anthropic | T1 | Subagents | description 字段是路由逻辑不是装饰；`.claude/agents/` Markdown+YAML 格式 |
| research/12-langgraph-customer-support-agents.md | LangChain | T1 | 多 Agent 编排 | LangGraph 状态化工作流 vs LangChain 高层抽象；handoffs 模式适合客服 |
| research/13-claude-code-skills-lessons.md | Thariq Shihipar (Anthropic) | T1 | Skills | 九大 skill 分类；写 skill 九大技巧(gotchas/渐进披露/按需 hook) |
| research/14-claude-code-loops-getting-started.md | Delba de Oliveira, Michael Segner (Anthropic) | T1 | Loops | 四种 loop：turn-based / /goal / /loop+schedule / proactive；停止条件与 token 管理 |
| research/15-claude-code-dynamic-workflows.md | Thariq Shihipar, Sid Bidasaria (Anthropic) | T1 | 动态工作流 | 三种失败模式(agentic laziness/self-preferential bias/goal drift)；workflow 对抗策略 |
| research/16-claude-code-agent-teams.md | Anthropic (Claude Code Docs) | T1 | Agent Teams | 实验性功能；lead+teammates 直接通信 vs subagents 单向汇报；token 成本高 |

## 内容地图

### best-practices 工作流
- research/01 — 官方最佳实践(核心参考)
- research/04 — Addy Osmani 十大实践(工作流视角)
- research/05 — Boris Cherny 个人工作流(创建者视角)
- research/06 — 内部调研数据(效果证据)
- research/00 — 综合提炼

### plan-mode
- research/01 — 官方建议(何时用/何时不用)
- research/02 — 社区整理的完整指南(T3)

### 课程与教学
- research/03 — DeepLearning.AI 合作课程大纲

### subagent / agent 架构
- research/11 — Subagents 官方文档
- research/12 — LangGraph 多 agent 编排模式
- research/16 — Agent Teams(实验性，teammates 直接通信)

### skills
- research/13 — Anthropic 内部九大分类与写作技巧

### loops / 动态编排
- research/14 — 四种 loop 类型与 token 管理
- research/15 — 动态工作流：三种失败模式与六大编排模式

### prompt 工程与缓存
- research/07 — ReAct prompt 模板(经典)
- research/09 — Prompt caching 与 KV cache 机制
- research/10 — LangChain RAG prompt 结构与缓存失效

### 基础设施与工具
- research/08 — LSP 协议深度研究

## 关键文件

| 文件 | 角色 |
|------|------|
| research/00-research-summary.md | 全局索引，所有 factual claim 的入口 |
| research/01-claude-code-best-practices-anthropic-official.md | 权威程度最高的单份资料，教程核心引用源 |
| research/06-anthropic-internal-ai-transforming-work.md | 唯一提供量化生产力数据的内部研究 |
| research/13-claude-code-skills-lessons.md | skill 系统设计与写作的权威参考 |
| research/15-claude-code-dynamic-workflows.md | agent 失败模式分类的唯一来源 |

## 检索锚点

- `research/00-research-summary.md` — 索引文件，所有 claim 的入口
- `Boris Cherny` — Claude Code 创建者，research/01 和 research/05 的作者
- `Andrew Ng` — DeepLearning.AI 课程合作方，research/03
- `Addy Osmani` — Google Chrome Engineer，research/04 作者
- `prompt caching` — 缓存机制关键词，research/09
- `ReAct` — 经典 agent prompt 模式，research/07
- `KV cache` — 底层缓存实现，research/09
- `LSP` — Language Server Protocol，research/08
- `ultracode` — 动态工作流触发词，research/15
- `Thariq Shihipar` — Anthropic，research/13 和 research/15 作者
- `handoffs` — LangChain 多 agent 交接模式，research/12
- `agentic laziness` — agent 失败模式之一，research/15
- `cache_read_input_tokens` — Anthropic 缓存计数器字段，research/09

## 潜在坑点 / 注意

1. **research/02 tier 争议:** 来源是 claude-ai.chat(第三方域名)，非 Anthropic 官方。已标为 T3，引用时需注明"社区来源"。
2. **research/08 和 research/09/10 作者标注为 Research Compilation:** 非原始作者，是对 Microsoft/Anthropic/LangChain 官方文档的二次整理。内容本身是 T1，但整理者的解读部分为 T4。
3. **专家观点冲突需双引:** research/05(Boris Cherny 极简配置)与 research/04(Addy Osmani 强调 spec/CLAUDE.md/Rules)存在张力。Boris 说"vanilla setup"，Addy 说"invest in rules"。这不是矛盾——Boris 是创建者视角(默认行为已够好)，Addy 是非 Anthropic 工程师视角(需要显式指导)。引用时需呈现双方。
4. **过期链接风险:** research/03 课程链接可能随 DeepLearning.AI 平台调整而失效。research/07 LangChain Hub URL 可能变更。使用前应验证。
5. **research/00 路径错误:** 00-research-summary.md 第 29 行引用 `C:\PythonProject\cc-tutorial\docs\research\`，实际路径是 `research/`。这是文件内的遗留错误。
6. **Agent Teams 实验性:** research/16 描述的 Agent Teams 是实验性功能，API 可能变化，引用时需标注"实验性"。

## 相关文档

- `.claude/rules/evidence-based.md` — 证据分级体系(T1-T4)的完整规则
- `CLAUDE.md` — 项目级内容创作规则，引用 evidence-based policy
- `video-scripts/` — 9 层视频脚本，research 资料的消费端
- `examples/` — 示例代码，部分与 research 内容对应
