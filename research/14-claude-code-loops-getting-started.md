---
title: "Getting started with loops"
author: "Delba de Oliveira, Michael Segner (Anthropic)"
date: "2026-06-30"
url: "https://claude.com/blog/getting-started-with-loops"
tier: T1
topics: [loops, claude-code, loop, schedule, goal, agentic-loop, automation]
---

# Claude Code Loops 入门（Anthropic 官方）

## 来源与定位

[Getting started with loops](https://claude.com/blog/getting-started-with-loops)（Delba de Oliveira, Michael Segner, Anthropic, 2026-06-30）。T1 官方文档。

核心定义：**loops 是 agent 重复工作循环直到满足停止条件**。按「如何触发、如何停止、用什么 primitive、适合什么任务」分类。不是所有任务都需要复杂 loop——从最简方案开始，按需用这些模式。

## 一、四种 Loop 类型

### 1. Turn-based loop（回合制）
- **触发**：用户 prompt
- **停止**：Claude 判定任务完成或需要更多上下文
- **适合**：不属于常规流程/排期的短任务
- **管理用法**：写明确的 prompt；用 skills 强化验证，减少回合数

你发的每条 prompt 都启动一个手动 loop，由你导演每一步。这就是 agentic loop：取上下文 → 行动 → 自检 → 必要时重来 → 回复。

强化验证的方法：把手动步骤编码进 SKILL.md，让 Claude 端到端自检，包含量化断言。文中给的 `verify-frontend-change` 范例：起 dev server、点控件、看 console、跑 Chrome DevTools MCP 性能 trace，任何一步失败就修了从头跑。

### 2. Goal-based loop（`/goal`）
- **触发**：实时手动 prompt
- **停止**：目标达成 OR 达到回合上限
- **适合**：有可验证退出条件的任务
- **管理用法**：设定具体完成条件 + 显式回合上限（"stop after 5 tries"）

单回合不够时，用 `/goal` 定义 done。每次 Claude 想停，evaluator model 检查条件，不满足就扔回去继续。确定性条件最有效（测试通过数、分数阈值）。

```
/goal get the homepage Lighthouse score to 90 or above, stop after 5 tries.
```

### 3. Time-based loop（`/loop` 与 `/schedule`）
- **触发**：指定时间间隔
- **停止**：你取消，或工作完成（PR 合并、队列清空）
- **适合**：周期性工作，或与外部系统交互
- **管理用法**：拉长间隔，或改成基于事件响应而非定时

`/loop` 按间隔重跑一个 prompt：

```
/loop 5m check my PR, address review comments, and fix failing CI
```

`/loop` 跑在你本机，关机就停。`/schedule` 把 loop 搬到云上。

### 4. Proactive loop（主动式）
- **触发**：事件或排期，无需人实时参与
- **停止**：每个任务达目标即退出；routine 本身跑到你关掉
- **适合**：定义良好的周期性工作流——bug 报告、issue 分诊、迁移、依赖升级
- **管理用法**：routine 路由到更小更快的模型，判断类调用最强模型

把上述 primitive 与 auto mode、dynamic workflows 组合成给长时运行工作的 loop。文中的反馈处理范例：`/schedule` 每小时查新报告 → `/goal` 定义 done + skills 文档化验证 → dynamic workflows 编排分诊/修复/review 的 agent → auto mode 让 routine 不停下来问权限。

## 二、维护代码质量

loop 输出质量取决于周围的系统：
- **保持代码库干净**：Claude 跟随已有 pattern 和约定。
- **给 Claude 自验证手段**：用 skills 编码"好"的标准。
- **让文档触手可及**：框架/库文档要是最新的最佳实践。
- **用第二个 agent 做 code review**：fresh context 的 reviewer 偏见更少。可用内置 `/code-review` 或 Code Review for GitHub。

单个结果不达标时，别只修单点——编码进系统，惠及未来所有迭代。

## 三、管理 token 用量

loop 要有清晰边界：
- **选对 primitive 和模型**：小任务不需要多 agent/loop；有些任务能用更便宜更快的模型。
- **定义清晰的 success/stop 条件**：让 Claude 更快收敛（但别太快）。
- **大规模跑前先试点**：dynamic workflows 可生成数百 agent。先在小切片上估量用量。
- **确定性工作用脚本**：跑脚本比推理便宜。
- **别过度频繁跑 routine**：间隔匹配被观察事物变化的频率。
- **复盘用量**：`/usage` 按 skills/subagents/MCP 拆分用量；`/goal`（无参数）显示回合数和 token；`/workflows` 显示每个 agent 的 token 用量，可随时停。

## 四、速查表

| Loop | 你交出去的是 | 用在 | 工具 |
|------|------------|------|------|
| Turn-based | 检查这一步 | 你在探索或决策 | 自定义验证 skills |
| Goal-based | 停止条件 | 你知道 done 长什么样 | `/goal` |
| Time-based | 触发 | 工作发生在项目外、按排期 | `/loop`、`/schedule` |
| Proactive | prompt | 工作是周期性、定义良好的 | 以上全部 + dynamic workflows |

## 五、起步

看你已经在做的工作，挑一个你是瓶颈的任务，问自己能交出去哪一块：验证检查能写下来吗？目标够清晰吗？工作是否按排期到来？

然后跑 loop，观察它卡在哪、在哪越界，别怕迭代。

## 原文出处
- [Getting started with loops](https://claude.com/blog/getting-started-with-loops)（Delba de Oliveira, Michael Segner, Anthropic, 2026-06-30）
