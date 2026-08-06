# video-scripts 领域概述

> **生成基准**: commit `3cf4d89`
> **源文件数**: 13（9 层 + README + 2 补充 + 1 官方插件）

---

## 快速索引

| 文件 | 一句话说明 |
|------|-----------|
| `video-scripts/README.md` | 9 层目录索引表 |
| `video-scripts/layer-01-theory.md` | LLM 理论地基：Token、上下文窗口、局限性、Function Calling、Prompt Engineering、参数调优、注意力机制、Agent 模式、多模态、模型选择 |
| `video-scripts/layer-02-setup.md` | 安装与环境配置：npm install、Windows 踩坑（执行策略/UTF-8/PATH）、IDE 联动、`/init`、代理中转、模型切换 |
| `video-scripts/layer-03-basics.md` | 基本操作：快捷键、Extended Thinking（think/think harder/ultrathink）、Resume/Rewind、Auto Compact、`@` 引用、图片粘贴、输入队列 |
| `video-scripts/layer-04-workflow.md` | 工作方法论：Vibe Coding vs Spec Coding、Plan Mode、CLAUDE.md 三级体系、Git 提交策略、Feedback Loop、代码分层/Clean Architecture、组件化、Few-shot 提示（珠玉在前） |
| `video-scripts/layer-05-config.md` | 配置体系：配置目录结构、settings.json、.gitignore、Rules 三级、Memory 系统（MEMORY.md vs CLAUDE.md）、自定义 Commands、Context Engineering |
| `video-scripts/layer-06-advanced.md` | 高级功能：MCP、SubAgent、`/plugin`（LSP/Playwright）、推荐插件表、Skills、Hooks（7 生命周期事件）、Headless 模式、Git Worktrees、ralph-loop、Agent SDK |
| `video-scripts/layer-07-caveats.md` | 注意事项：AI 能力边界表、4 类典型翻车场景、Playwright 自动化闭环、Burnout（Siddhant Khare/HN/Peter Steinberger）、数据安全、内存泄露 BUG、扩展学习资源 |
| `video-scripts/layer-08-practice.md` | 实战案例：claude-token-monitor 布局改造（三层架构 + `--debug` 数据分析 + 小步提交）、从零开发参考项目建议 |
| `video-scripts/layer-09-supplement.md` | 补充：Claude Code Web、Session Teleport、中国区订阅方案、模型对比表（Opus 4.6/StepFun/GLM-5/Kimi K2.5/MiniMax）、HTTPS 安全 |
| `video-scripts/supplement-mcp.md` | MCP 深度拆解（从 layer-01 第 4.6 节拆出）：Function Calling 碎片化问题、USB 类比、Tools/Resources/Prompts、JSON-RPC 2.0、stdio/HTTP/SSE、FastMCP Python 实现 |
| `video-scripts/supplement-attention-mechanism.md` | 注意力机制深度拆解（从 layer-01 第七章拆出）：Self-Attention O(n²)、Multi-Head 分工表、Full/SWA/Mixed/Linear/Bidirectional 变体、Flash/Ring Attention/GQA/MQA 工程优化 |
| `video-scripts/official-plugin.md` | 官方插件安装命令（`/plugin marketplace add`） |

---

## 领域概述

本领域覆盖 Claude Code 视频教程的完整 9 层脚本内容，从 LLM 理论基础（Token、上下文窗口、Agent 模式）到安装配置、基本操作、工作方法论、配置体系、高级功能、注意事项、实战案例、补充资源，构成一条从认知地基到生产实战的渐进式学习路径。所有内容围绕一个核心命题展开：**在有限的上下文窗口中，如何最大化 Claude Code 的输出质量**。两条补充文档（MCP 协议、注意力机制）从 layer-01 中拆出，提供独立深度的技术专题。

---

## 子领域

| 层级 | 文件 | 主题 | 关键词 |
|------|------|------|--------|
| 第一层 | `layer-01-theory.md` | 理论基础（认知地基） | Token, Context Window, Function Calling, Prompt Engineering, CoT, Few-Shot, ReAct, Plan-and-Execute, Self-Reflection, Multi-Agent, 注意力机制, Temperature, Top-P, 多模态 |
| 第二层 | `layer-02-setup.md` | 安装与环境 | `npm install`, Windows 执行策略, UTF-8 乱码, PATH, `/init`, `ANTHROPIC_BASE_URL`, `dangerously-skip-permissions`, Claude Code Router, Antigravity, `/model`, `/cost` |
| 第三层 | `layer-03-basics.md` | 基本操作 | Ctrl+V, Alt+V, `think`, `think harder`, `ultrathink`, Resume, Rewind, `/compact`, `/clear`, `@` 引用, Extended Thinking |
| 第四层 | `layer-04-workflow.md` | 工作方法论 | Vibe Coding, Spec Coding, Plan Mode, CLAUDE.md, Feedback Loop, Clean Architecture, 组件化, Few-shot 提示, 珠玉在前, Git 提交 |
| 第五层 | `layer-05-config.md` | 配置体系 | `settings.json`, Rules, Memory, `MEMORY.md`, Commands, Context Engineering, `.claude/commands/` |
| 第六层 | `layer-06-advanced.md` | 高级功能 | MCP, SubAgent, `/plugin`, LSP, Playwright, Skills, Hooks, Headless, Git Worktrees, ralph-loop, Agent SDK |
| 第七层 | `layer-07-caveats.md` | 注意事项 | AI 能力边界, 幻觉, Burnout, AI Fatigue, 数据安全, 内存泄露, Playwright 自动化 |
| 第八层 | `layer-08-practice.md` | 实战案例 | claude-token-monitor, `--debug`, stdin JSON, 三层架构, 4x4 Grid, Feedback Loop, 参考项目 |
| 第九层 | `layer-09-supplement.md` | 补充资源 | Claude Code Web, Session Teleport, 中国区订阅, GLM Coding, 模型对比, HTTPS |
| 补充 A | `supplement-mcp.md` | MCP 深度拆解 | MCP, JSON-RPC 2.0, Tools, Resources, Prompts, stdio, HTTP+SSE, FastMCP |
| 补充 B | `supplement-attention-mechanism.md` | 注意力机制深度拆解 | Self-Attention, Multi-Head, Flash Attention, Ring Attention, GQA, MQA, SWA |

---

## 内容地图

```
video-scripts
├── 理论基础 (layer-01)
│   ├── LLM 基础: Token / Context Window / 概率预测
│   ├── LLM 局限性: 数学 / 幻觉 / 逻辑 / 知识截止 / 计数偏差
│   ├── 实战场景: 代码审查 / 文本处理 / 数据提取
│   ├── Function Calling: 基本流程 / HTTP 请求解剖 / 多工具编排 / 并行调用 / 传统演进 / API 协议兼容
│   ├── Prompt Engineering: Few-Shot / CoT / Structured Output / Role Playing / Negative Prompting / In-Context Learning / Self-Consistency / PAL
│   ├── 参数调优: Temperature / Top-P / Max Tokens / Penalties
│   ├── 注意力机制 → supplement-attention-mechanism.md
│   ├── Agent 模式: ReAct / Plan-and-Execute / Self-Reflection / Multi-Agent / Lilian Weng 三组件
│   ├── 多模态: 原生 vs 非原生
│   └── 模型选择: Opus 4.6 / GLM / StepFun / DeepSeek
│
├── 安装与环境 (layer-02)
│   ├── 安装: npm / Windows 踩坑（执行策略/UTF-8/PATH）
│   ├── IDE 联动: VSCode / IDEA / Cursor / `/config` / `/ide`
│   ├── 启动设置: 环境变量 / API Key / `dangerously-skip-permissions`
│   ├── /init: 项目扫描 → CLAUDE.md 生成
│   └── 中转与模型: Claude Code Router / Antigravity / `/model` / `/cost`
│
├── 基本操作 (layer-03)
│   ├── 快捷键: Ctrl+V / Alt+V / Ctrl+C / Ctrl+O / Ctrl+T / Ctrl+B / Ctrl+A / Shift+?
│   ├── Extended Thinking: think / think harder / ultrathink（Token 预算）
│   ├── 会话管理: Resume / Rewind / Auto Compact
│   ├── 输入方式: @文件引用 / 图片粘贴(Alt+V) / 输入队列
│   └── 英文提示词建议
│
├── 工作方法论 (layer-04)
│   ├── Vibe Coding vs Spec Coding（产出质量公式）
│   ├── Plan Mode (Shift+Tabx2)
│   ├── CLAUDE.md 三级: user / project / local
│   ├── Git 工作流: 提交作为存档点
│   ├── Feedback Loop（Boris Cherny）
│   ├── 代码架构: 分层 / Clean Architecture / 组件化
│   ├── Few-shot 提示（珠玉在前）
│   └── 平台差异: Windows vs Unix / 语言推荐
│
├── 配置体系 (layer-05)
│   ├── 目录结构: ~/.claude/ / .claude/ / .local.*
│   ├── settings.json 字段
│   ├── .gitignore 规则
│   ├── Rules 三级体系
│   ├── Memory: MEMORY.md vs CLAUDE.md
│   ├── 自定义 Commands: .claude/commands/
│   └── Context Engineering: 所有信息源汇总表
│
├── 高级功能 (layer-06)
│   ├── MCP 概述 → supplement-mcp.md
│   ├── SubAgent: Task 工具 / java-unit-test-generator 示例
│   ├── /plugin: LSP / Playwright / 推荐插件表
│   ├── MCP 配置: CLI / .mcp.json
│   ├── Skills: .claude/skills/
│   ├── Hooks: 7 生命周期事件 / 配置示例
│   ├── Headless 模式: 参数全表 / --output-format / CI/CD 示例
│   ├── Git Worktrees
│   ├── ralph-loop 自动化
│   └── Agent SDK: CLI vs SDK / API 参考 / Python/TypeScript / JSON Schema / 自定义 Tools
│
├── 注意事项 (layer-07)
│   ├── AI 能力边界表（5 级）
│   ├── 4 类典型翻车场景
│   ├── Playwright 自动化闭环
│   ├── Burnout / AI Fatigue（Siddhant Khare / HN / Peter Steinberger）
│   ├── 数据安全（训练数据风险）
│   ├── 内存泄露 BUG
│   └── 扩展学习: Lilian Weng / HuggingFace / DeepLearning.AI / ChatDev / Stanford Generative Agents / Cyber-Zen-Master
│
├── 实战案例 (layer-08)
│   ├── claude-token-monitor 布局改造
│   │   ├── 三层架构: Content Collection → Layout → Render
│   │   ├── --debug 获取 stdin 实际数据
│   │   └── 小步提交 + 验证
│   └── 从零开发: 参考项目建议
│
├── 补充资源 (layer-09)
│   ├── Claude Code Web
│   ├── Session Teleport
│   ├── 中国区订阅方案（U 卡 / Google Play / iOS / VPS）
│   ├── 模型对比表
│   └── HTTPS 安全要求
│
├── supplement-mcp.md
│   ├── Function Calling 碎片化 → MCP USB 类比
│   ├── 三能力: Tools / Resources / Prompts
│   ├── 协议: JSON-RPC 2.0 / stdio / HTTP+SSE
│   └── FastMCP Python 实现
│
├── supplement-attention-mechanism.md
│   ├── Self-Attention O(n²)
│   ├── Multi-Head 分工表
│   ├── 注意力变体: Full / SWA / Mixed / Linear / Bidirectional
│   └── 工程优化: Flash Attention / Ring Attention / GQA / MQA
│
└── official-plugin.md
    └── /plugin marketplace add anthropics/skills
```

---

## 关键文件

| 文件 | 行数 | 角色 |
|------|------|------|
| `layer-01-theory.md` | ~1684 | 核心理论地基，覆盖 12+ 重大主题（Token → Agent → 多模态），引用 9 个 HTTP 示例文件、97 个可执行 API 请求 |
| `layer-06-advanced.md` | ~1046 | 高级功能全集，覆盖 MCP/SubAgent/Plugins/Skills/Hooks/Headless/Worktrees/Agent SDK |
| `layer-04-workflow.md` | ~569 | 工作方法论核心，定义 Vibe Coding vs Spec Coding 范式、Plan Mode 使用、CLAUDE.md 体系、Feedback Loop |
| `layer-07-caveats.md` | ~327 | AI 能力边界认知，Burnout/AI Fatigue 深度讨论（含 Siddhant Khare/HN 来源） |
| `layer-08-practice.md` | ~300 | 唯一实战案例，演示 `--debug` 数据驱动的工作流 |
| `layer-09-supplement.md` | ~281 | 中国区开发者订阅方案和模型对比 |
| `layer-02-setup.md` | ~233 | 安装配置实操，Windows 三大坑点 |
| `layer-05-config.md` | ~185 | 配置体系全景，Context Engineering 概念引入 |
| `supplement-mcp.md` | ~163 | MCP 协议独立深度拆解 |
| `layer-03-basics.md` | ~176 | 快捷键和 Extended Thinking Token 预算 |
| `supplement-attention-mechanism.md` | ~107 | 注意力机制独立深度拆解 |
| `official-plugin.md` | ~6 | 官方插件安装命令 |
| `README.md` | ~20 | 9 层索引表 |

---

## 检索锚点

- `Plan Mode` — `layer-03-basics.md`, `layer-04-workflow.md` — Shift+Tabx2 触发的只读规划模式，对应 Plan-and-Execute Agent 模式
- `CLAUDE.md` — `layer-01-theory.md`, `layer-02-setup.md`, `layer-04-workflow.md`, `layer-05-config.md`, `layer-06-advanced.md` — 三级配置体系（user/project/local），项目的长期记忆载体
- `Function Calling` — `layer-01-theory.md`, `supplement-mcp.md` — LLM 调用外部工具的核心机制，含完整 HTTP 请求解剖
- `MCP` — `layer-01-theory.md`, `layer-05-config.md`, `layer-06-advanced.md`, `supplement-mcp.md` — Model Context Protocol，统一工具调用标准，Tools/Resources/Prompts 三能力
- `SubAgent` — `layer-01-theory.md`, `layer-06-advanced.md` — 独立上下文窗口的子任务执行器，解决主 Agent 上下文溢出
- `Extended Thinking` — `layer-01-theory.md`, `layer-03-basics.md` — think/think harder/ultrathink 三级 Token 预算的深度思考机制
- `Context Engineering` — `layer-01-theory.md`, `layer-05-config.md` — 在有限上下文窗口中最大化输出质量的系统性策略
- `Agent SDK` — `layer-06-advanced.md` — Claude Code 的 CLI 架构与 SDK API，支持 Python/TypeScript 自定义 Agent
- `Feedback Loop` — `layer-04-workflow.md`, `layer-07-caveats.md`, `layer-08-practice.md` — Boris Cherny 强调的核心工作流：给 Claude 提供验证方法
- `ralph-loop` — `layer-06-advanced.md` — Claude Code 的连续自动化工作模式
- `Hooks` — `layer-06-advanced.md` — 7 个生命周期事件（PreToolUse/PostToolUse/Notification/Stop 等），支持命令拦截和自定义处理
- `Headless` — `layer-06-advanced.md` — 无头模式全参数参考，`--output-format json/stream-json/text`，CI/CD 集成
- `Burnout` — `layer-07-caveats.md` — AI Fatigue 深度讨论，Siddhant Khare 文章 + HN 社区 + Peter Steinberger 采访

---

## 潜在坑点

- `layer-01-theory.md` 体量巨大（~1684 行），覆盖 12+ 独立主题，跨 Token 基础到 Multi-Agent 全链路，检索时需精确定位到章节标题
- `layer-06-advanced.md` 同样超千行（~1046 行），MCP/SubAgent/Hooks/Headless/SDK 五大独立主题合并在一个文件中
- `supplement-mcp.md` 和 `supplement-attention-mechanism.md` 是从 `layer-01-theory.md` 拆出的，内容有交叉引用，修改时需同步检查
- `layer-09-supplement.md` 中的订阅方案和模型对比信息时效性强（2026 年初数据），可能已过时
- `layer-02-setup.md` 中的 Windows 版本号（Terminal 1.23.12371.0、PowerShell 7.4.13）为特定时间点的推荐版本
- 官方协议差异（OpenAI vs Anthropic）分散在 `layer-01-theory.md` 第 4.5 节和 `layer-02-setup.md` 中转部分，跨文件检索需注意

---

## 深度文档(Sub-docs)

- [agent-patterns](agent-patterns.md) -- layer-01 的 Agent 设计模式深度(ReAct / Plan-Execute / Self-Reflection / Multi-Agent + Lilian Weng 三组件),交叉到 `examples/python/01-03` 与 `research/07`、`research/11`。
- [hooks-and-headless](hooks-and-headless.md) -- layer-06 的 Hooks 七生命周期 + Headless 参数表 + ralph-loop 机制,交叉到 `examples/scripts/notify-stop.py`、`stop-hook.py`。
- [subagent-and-sdk](subagent-and-sdk.md) -- layer-06 的 SubAgent 三独立性 + Agent SDK(query / ClaudeSDKClient / @tool / 结构化输出),交叉到 `research/11`。

---

## 相关文档

- `research/00-research-summary.md` — 全部研究材料汇总索引
- `research/01-claude-code-best-practices-anthropic-official.md` — Boris Cherny 最佳实践（T1），被 layer-04 Feedback Loop 引用
- `research/03-andrew-ng-course-outline.md` — Andrew Ng 课程大纲，被 layer-07 扩展学习引用
- `research/04-addy-osmani-2026-workflow.md` — Addy Osmani 2026 工作流，引入 Context Engineering 概念
- `research/11-claude-code-subagents.md` — Claude Code SubAgent 专题，对应 layer-06 和 layer-01 第 8.8 节
- `research/13-claude-code-skills-lessons.md` — Anthropic 内部 Skills 9 大类别，对应 layer-06 Skills 节
- `research/16-claude-code-agent-teams.md` — Agent Teams 专题，对应 layer-01 Multi-Agent 和 layer-06 Agent SDK
- `examples/http/` — 9 个 HTTP 示例文件（01-09），被 layer-01 各章节引用
- `examples/python/` — 4 个 Agent 模式 Python 实现，被 layer-01 Agent 章节引用
- `CLAUDE.md` — 项目级配置，定义 Evidence-Based Content Policy 和写作规范
