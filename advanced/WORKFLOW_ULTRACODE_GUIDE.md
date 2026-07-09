# Workflow 与 ultracode：动态多 agent 编排

## 先说结论

Workflow 让 Claude 为当前任务现场写一个多 agent harness：一段 JS 脚本，编排一群独立上下文的 subagent。它解决的是单上下文干不动的活——大规模、长时、对抗验证。代价是 token 消耗显著。小任务上它是杀鸡用炮。

`T1` 官方定位与前提（[A harness for every task](https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code)，Thariq Shihipar & Sid Bidasaria, Anthropic, 2026-06）：dynamic workflows 通常用更多 token，最适合复杂、高价值任务。

## 单上下文的三种死法

`T1` 官方点名的三种失败模式（同上）：

- **Agentic laziness**：复杂多部分任务做到一半宣布完成。50 项安全 review 只做 35 项。
- **Self-preferential bias**：Claude 偏好自己的产出，让它验证自己等于让被告当法官。
- **Goal drift**：跨回合、尤其压缩后，原始目标的约束一点点漏掉。

Workflow 的解法是同一个：独立 context window、目标聚焦的 subagent。

## 触发条件：显式 opt-in

`T1` 触发方式（同上）：直接要求 Claude 做一个 workflow，或用触发词 `ultracode`。它不是默认行为——多数任务不该为它买单。

## 机制

Workflow 执行一个 JS 文件：`agent()` 生成 subagent，`parallel()` 并发（屏障语义），`pipeline()` 流水线（无屏障），`phase()` 分组进度。`schema` 参数强制 subagent 返回校验过的结构化 JSON。可设 token budget，中断后可从断点续跑。脚本内 `Date.now()`/`Math.random()` 不可用——恢复机制依赖确定性。

## 六种常见模式

`T1` 官方模式表（同上）：

| 模式 | 做法 |
|------|------|
| Classify-and-act | 分类器 agent 决定任务类型，再路由 |
| Fan-out-and-synthesize | 拆小步各派一个 agent，合成时设屏障 |
| Adversarial verification | 每个生成 agent 配一个独立对抗验证 agent |
| Generate-and-filter | 批量生成 → 按 rubric 过滤去重 |
| Tournament | agent 竞争同一任务，judge 两两比较出赢家 |
| Loop until done | 工作量未知时循环派 agent 直到无新发现 |

## 典型用例

`T1` 官方用例（同上），挑四个最有含金量的：

- **迁移与重构**：Bun 从 Zig 迁 Rust 用的就是 workflow——拆步骤、每个修复在 worktree 里跑 subagent、配对抗 review、最后合并。
- **深度研究**：官方 `/deep-research` skill 本身就是 dynamic workflow：fan-out 搜索、抓源、对抗验证、合成带引用报告。
- **根因排查**：从不相交的证据（日志、文件、数据）各生成假设，每个假设面对 verifier/refuter 面板。
- **大规模分诊**：分类、去重、行动。配 quarantine 模式：读不可信内容的 agent 禁高权限动作。

## 与 Agent Teams、Subagents 的分工

**[Tutorial perspective]** 三句话切清楚：控制流要确定性（循环、屏障、流水线）用 Workflow；agent 之间要来回沟通、人要中途介入用 Agent Teams；只是想要一个干净上下文干一件事用 Subagent。详见 [Agent 协作系统总览](CLAUDE_CODE_AGENT_GUIDE.md)的决策树。

## 何时不用

`T1` 官方原话（同上）：对常规编码任务先问「它真的需要更多算力吗？」大多数传统编码任务不需要 5 个 reviewer 面板。

## 最小实测

`实测 @ Claude Code v2.1.202`（2026-07-07，Windows 10）。下面这个最小 workflow（2 个 Sonnet agent 并发扫描本仓库两篇文档的证据标注）真实跑通：

```js
export const meta = {
  name: 'demo-evidence-scan',
  description: 'Scan two advanced/ docs and count evidence-tier markers',
  phases: [{ title: 'Scan' }, { title: 'Merge' }],
}
phase('Scan')
const files = ['advanced/token.md', 'advanced/skill.md']
const results = await parallel(files.map(f => () =>
  agent(`统计文件 ${f} 中 T1、T2、T4 标注各出现多少次，返回结构化结果`, {
    label: `scan:${f}`,
    phase: 'Scan',
    model: 'sonnet',
    schema: {
      type: 'object',
      properties: {
        file: { type: 'string' },
        t1: { type: 'number' },
        t2: { type: 'number' },
        t4: { type: 'number' }
      },
      required: ['file', 't1', 't2', 't4'],
      additionalProperties: false
    }
  })
))
phase('Merge')
return { results: results.filter(Boolean) }
```

运行结果：

- runId：`wf_3328e074-0a4`（后台执行，Task ID `wzqk7choz`）
- 脚本持久化路径：`C:\Users\Administrator\.claude\projects\D--goProject-cc-tutorial\<session-id>\workflows\scripts\demo-evidence-scan-wf_3328e074-0a4.js`
- 返回值：

```json
{"results":[{"file":"D:\\goProject\\cc-tutorial\\advanced\\token.md","t1":10,"t2":2,"t4":1},{"file":"D:\\goProject\\cc-tutorial\\advanced\\skill.md","t1":3,"t2":0,"t4":0}]}
```

journal 位置：`<session>\subagents\workflows\wf_3328e074-0a4\journal.jsonl`——每个完成的 agent 一行 `{"type":"result",...}` 记录完整返回值。用量：2 agents（0 error / 0 skipped），71,008 subagent tokens，13 次工具调用，25.3 秒。

**[Author's analysis]** 注意脚本本身没有任何魔法：真正的价值在 `schema` 强制结构化返回和 `parallel` 的屏障语义——这两样把「一群 agent」从放羊变成流水线。
