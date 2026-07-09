---
title: "A harness for every task: dynamic workflows in Claude Code"
author: "Thariq Shihipar, Sid Bidasaria (Anthropic)"
date: "2026-06-02"
url: "https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code"
tier: T1
topics: [workflows, dynamic-workflows, multi-agent, claude-code, orchestration, subagents]
---

# Claude Code Dynamic Workflows（Anthropic 官方）

## 来源与定位

[A harness for every task: dynamic workflows in Claude Code](https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code)（Thariq Shihipar, Sid Bidasaria, Anthropic, 2026-06-02）。T1 官方文档。

核心：Claude 现在能**为当前任务现场编写自己的多 agent harness**。默认 harness 为编码设计，但很多任务长得像编码任务。研究、安全分析、agent teams、code review 这几类任务，此前需要在 Claude Code 之上手搭定制 harness 才能达到峰值表现——workflow 让这类问题更原生地解决。

**重要前提**：dynamic workflows 通常用更多 token，最适合复杂、高价值任务。

## 一、为什么需要

默认 harness 在**同一个 context window 里既规划又执行**。编码任务上很有效，但在长时运行、大规模并行、高度结构化、对抗性任务上会崩。原因——Claude 在单一 context 里干复杂任务越久，越容易撞三种失败模式：

- **Agentic laziness（agent 懒惰）**：复杂多部分任务做到一半就宣布完成。例：50 项安全 review 只做了 35 项。
- **Self-preferential bias（自我偏好偏见）**：Claude 倾向偏好自己的结果/发现，尤其在被要求按 rubric 验证或评判时。
- **Goal drift（目标漂移）**：跨多回合、尤其压缩后，对原始目标的保真度逐渐流失。每次摘要都有损，"边缘 case 要求"或"别做 X"这类约束会丢。

Workflow 通过编排**独立 context window、目标聚焦隔离的 Claude subagent** 来对抗这三点。

## 二、工作原理

Dynamic workflow 执行一个 javascript 文件，内含若干用于生成和协调 subagent 的特殊函数，外加标准 JS（JSON、Math、Array）做数据处理。

关键能力：
- workflow 能决定每个 agent 用哪个模型；
- subagent 是否在独立 worktree 运行——Claude 自行选择智能层级与隔离程度；
- 被打断（用户操作、退出终端）后，恢复会话能从断点续跑。

## 三、Dynamic vs Static

此前可用 Claude Agent SDK 或 `claude -p` 编排多个 Claude Code 实例做**静态 workflow**。但静态 workflow 要覆盖所有边缘 case，通常更通用。配合 Claude Opus 4.8，Claude 现在能写出为你的 case 量身定制的 harness。

触发方式：直接让 Claude 做一个 workflow，或用触发词 **`ultracode`** 确保 Claude Code 创建 workflow。

## 四、常见模式

| 模式 | 做法 |
|------|------|
| **Classify-and-act** | 分类器 agent 决定任务类型，再路由到不同 agent/行为；或末端分类决定输出 |
| **Fan-out-and-synthesize** | 任务拆成许多小步，每步一个 agent，再合成。synthesize 是 barrier——等所有 fan-out agent 完成，合并结构化输出 |
| **Adversarial verification** | 每个生成 agent 配一个独立 agent 按 rubric 对抗验证 |
| **Generate-and-filter** | 生成一批想法，按 rubric/验证过滤，去重，只留经过测试的高质量想法 |
| **Tournament** | agent 们竞争同一任务而非分工，judge agent 两两比较直到产生赢家 |
| **Loop until done** | 工作量未知时，循环生成 agent 直到停止条件（无新发现、日志无新错误），而非固定轮数 |

## 五、典型用例

- **迁移与重构**：Bun 从 Zig 重写为 Rust 就用了 workflow。关键——把任务拆成一系列步骤（调用点、失败测试、模块），每个修复在 worktree 里起 subagent，再配一个 agent 对抗 review，最后合并。提示 agent 别用资源密集命令以最大化并行。
- **深度研究**：官方 `/deep-research` skill 用 dynamic workflow：fan-out 搜索、抓源、对抗验证 claim、合成带引用的报告。也可用于从 Slack 编状态报告、深挖代码库研究某 feature。
- **深度验证**：报告里每条事实 claim 单独起 subagent 核查；还可配 verification agent 检查 source agent 的来源质量。
- **排序**：1000+ 行一次排序质量下降且塞不进 context。改用 tournament、成对比较 pipeline（比较判断比绝对打分可靠）、或并行分桶排名再合并。
- **记忆与规则遵守**：CLAUDE.md 里总被漏的规则，建 workflow 让每个 verifier agent 负责一条；加 skeptic persona 审规则本身，避免误报。反向也可——挖近期会话/review 评论里反复出现的纠正，聚成候选规则，对抗验证后蒸馏回 CLAUDE.md。
- **根因排查**：调试最好提出多个独立假设分别验证。workflow 让 agent 从不相交的证据（日志、文件、数据各自一个）生成假设，每个假设再面对 verifier/refuter 面板。不止代码——销售、数据工程、复盘都能用。
- **大规模分诊**：每个 support 队列/bug backlog 都无法全靠人处理。triage workflow 分类、去重、采取行动。有用模式 **quarantine**：读不可信公开内容的 agent 禁止执行高权限动作，改由负责行动的 agent 做。配 `/loop` 让 Claude 持续做。
- **探索与品味**：设计、命名这类品味导向任务，让 Claude 探索一批方案，review agent 拿 rubric 判，达标即完成；也可 tournament 排序。
- **Evals**：worktree 里起 agent 产出，再起比较 agent 按 rubric 打分。例：按特定标准评估并精炼一个新 skill。
- **模型/智能路由**：分类器 agent 先调研任务复杂度，再路由到 Sonnet 或 Opus。

## 六、什么时候不要用

Workflow 是新的。很多场景效果突出，但**不是每个任务都需要**，可能显著多用 token。

对常规编码任务问自己：**它真的需要更多算力吗？** 大多数传统编码任务不需要 5 个 reviewer 面板。

## 七、技巧

- **详细 prompting**：把上述具体技术写进 prompt 效果最好。workflow 不只用于大任务——可 prompt "quick workflow" 做一次快速对抗 review。
- **配 `/goal` 与 `/loop`**：可重复的 workflow（triage、research、verification）配 `/loop` 定期跑，配 `/goal` 设硬性完成要求。
- **token 预算**：可设显式预算，prompt "use 10k tokens" 即设上限。
- **保存与分享**：在 workflow 菜单按 `s` 保存，提交进 `~/.claude/workflows`，或通过 skill 分发（把 JS workflow 文件放进 skill 文件夹，在 SKILL.md 引用；建议提示 Claude 把 skill 里的 workflow 当模板而非逐字脚本）。

## 原文出处
- [A harness for every task: dynamic workflows in Claude Code](https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code)（Thariq Shihipar, Sid Bidasaria, Anthropic, 2026-06-02）
