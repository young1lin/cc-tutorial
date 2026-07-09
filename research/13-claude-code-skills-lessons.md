---
title: "Lessons from building Claude Code: How we use skills"
author: "Thariq Shihipar (Anthropic)"
date: "2026-06-03"
url: "https://claude.com/blog/lessons-from-building-claude-code-how-we-use-skills"
tier: T1
topics: [skills, claude-code, agents, context-engineering, progressive-disclosure, plugins]
---

# Claude Code Skills 实战经验（Anthropic 官方）

## 来源与定位

[Lessons from building Claude Code: How we use skills](https://claude.com/blog/lessons-from-building-claude-code-how-we-use-skills)（Thariq Shihipar, Anthropic, 2026-06-03）。作者为 Claude Code 团队成员。该文是 Anthropic 内部构建、扩展数百个 skills 后的总结，属 T1 官方文档。

核心问题：什么样的 skill 有用，怎么写才不打架。

## 一、Skill 的九大类型

Anthropic 把内部 skills 归为九类。最好的 skill 干净地落在某一类；试图做多件事的 skill 会跨类，混淆 agent。

| 类型 | 作用 | 示例 |
|------|------|------|
| 1. 库与 API 参考 | 解释如何正确使用库/CLI/SDK，含参考代码片段与陷阱 | `billing-lib`、`internal-platform-cli`、`sandbox-proxy` |
| 2. 产品验证 | 描述如何测试/验证代码工作，常配 playwright/tmux | `signup-flow-driver`、`checkout-verifier`、`tmux-cli-driver` |
| 3. 数据获取与分析 | 连接数据与监控栈，含凭据、dashboard id、查询模式 | `funnel-query`、`cohort-compare`、`grafana`、`datadog` |
| 4. 业务流程与团队自动化 | 把重复工作流压成一条命令 | `standup-post`、`create-<ticket>-ticket`、`weekly-recap` |
| 5. 代码脚手架与模板 | 生成框架样板代码 | `new-<framework>-workflow`、`new-migration`、`create-app` |
| 6. 代码质量与审查 | 强制代码质量、辅助 review，可放 hook/GitHub Action | `adversarial-review`、`code-style`、`testing-practices` |
| 7. CI/CD 与部署 | 拉取、推送、部署代码 | `babysit-pr`、`deploy-<service>`、`cherry-pick-prod` |
| 8. Runbook | 接收症状（Slack/告警/错误签名），多工具排查，产出结构化报告 | `<service>-debugging`、`oncall-runner`、`log-correlator` |
| 9. 基础设施运维 | 例行维护与运维操作，含破坏性操作的护栏 | `<resource>-orphans`、`dependency-management`、`cost-investigation` |

**[Tutorial perspective]** 第二类「产品验证」对输出质量的提升最可量化。Anthropic 称值得让一个工程师花一周把验证类 skill 做到极致。

## 二、写 Skill 的实战技巧

### 1. 不要陈述显而易见的东西
Claude 已经会写代码、能读你的代码库。复述默认行为只增加 context 不增加价值。聚焦能推翻 Claude 默认思维的信息。`frontend-design` skill 是范例——专门纠正 Inter 字体、紫色渐变这类"AI 味"默认审美。

### 2. 建一个 Gotchas 段
信号密度最高的内容。从 Claude 常踩的坑积累而来，随时间更新。例：

> "The `subscriptions` table is append-only. The row you want is the one with the highest version, not the most recent `created_at`."
> "This field is called `@request_id` in the API gateway and `trace_id` in the billing service. They're the same value."

### 3. 用文件系统做渐进式披露
Skill 是一个文件夹，不是一个 md 文件。把整个文件系统当成 context engineering：SKILL.md 指向其它文件，Claude 在合适时机读取。把详细函数签名拆进 `references/api.md`；最终产物是 md 的话，模板放进 `assets/`。

### 4. 不要把 Claude 钉死
给信息，给灵活性。指令太具体反而限制 skill 的复用性。

### 5. 想清楚 setup
有些 skill 需要用户提供上下文。模式：把 setup 信息存进 `config.json`，未配置就让 agent 问用户。要结构化多选问题，指示 Claude 用 `AskUserQuestion` 工具。

### 6. description 写给模型看，不是写给人看
会话启动时 Claude 扫描所有 skill 的 description 决定是否触发。description 不是摘要，是「何时触发」。把触发词写进去，比如 `babysit`。

### 7. 帮 Claude 记住
用 append-only log、JSON 或 SQLite 存历史。例：`standup-post` 维护 `standups.log`，下次跑时能说出"自昨天以来变了什么"。可用环境变量 `${CLAUDE_PLUGIN_DATA}` 拿到稳定存储目录（见 https://code.claude.com/docs/en/plugins-reference#persistent-data-directory）。

### 8. 存脚本、生成代码
给 Claude 脚本和库，让它把 turn 花在组合决策上，而不是重写样板。`data-science` skill 提供取数 helper，Claude 现场拼脚本做更复杂分析。

### 9. 用按需 hook
Skill 可携带只在调用时激活、只持续该会话的 hook。
- `/careful`：PreToolUse 拦 `rm -rf`、`DROP TABLE`、force-push、`kubectl delete`。只在碰 prod 时用——常开会让人疯。
- `/freeze`：拦截指定目录外的 Edit/Write。调试时防止"顺手修了不相关的代码"。

## 三、分发与规模

两种分发方式：
- 提交进仓库（`.claude/skills`）——适合小团队、少仓库。代价：每个 skill 都往 context 里加一点。
- 做成 plugin，发布到内部 marketplace——随规模扩大更合适，团队自选安装，带 setup 流程。

Anthropic 没有中央团队决定哪些 skill 进 marketplace：先放 sandbox 文件夹在 Slack 推广，有 traction 后再 PR 进 marketplace。

## 四、组合与度量

- **组合**：skill 间依赖目前无原生支持，可直接按名字引用另一个 skill，模型在已安装时会调用。
- **度量**：用 PreToolUse hook 记录 skill 使用情况，找出热门或 undertriggering 的 skill。

## 五、起步建议

最好的 skill 起步都是几行 + 一个 gotcha，随 Claude 撞上新边界再迭代。

**[Tutorial perspective]** 对本教程而言，这条规律很关键：不要一上来就写大而全的 skill。把"自定义 skill 替代 Graph RAG / Explore Agent / Code2Graph 这类插件"这件事，拆成一个个小 skill 去验证。

## 原文出处
- [Lessons from building Claude Code: How we use skills](https://claude.com/blog/lessons-from-building-claude-code-how-we-use-skills)（Thariq Shihipar, Anthropic, 2026-06-03）
