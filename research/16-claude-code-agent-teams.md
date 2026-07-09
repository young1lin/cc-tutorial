---
title: "Orchestrate teams of Claude Code sessions (Agent Teams)"
author: "Anthropic (Claude Code Docs)"
date: "2026-07-04"
url: "https://code.claude.com/docs/en/agent-teams"
tier: T1
topics: [agent-teams, claude-code, multi-agent, teammates, parallel-work, experimental]
---

# Claude Code Agent Teams（Anthropic 官方文档编译）

## 来源与定位

[Orchestrate teams of Claude Code sessions](https://code.claude.com/docs/en/agent-teams)（Anthropic 官方 Claude Code Docs，T1）。Agent Teams 是**实验性功能**，默认禁用。官方文档持续更新，本文截至官方文档引用的 v2.1.199 行为。

核心：协调多个 Claude Code 实例协作。一个会话作 **team lead**，协调工作、分配任务、综合结果。**Teammates 各自独立 context window，彼此直接通信**——这是它与 subagents 的关键区别。你也可以绕过 lead，直接和某个 teammate 对话。

> ⚠️ 纠正一个常见误传：第三方文章常说"subagents 之间不能通信、只能向 lead 汇报"。这描述的是 **subagents**，不是 **agent teams teammates**。官方明确：teammates 之间直接互发消息。

## 一、何时用、何时不用

**最强用例：**
- **研究与审查**：多个 teammate 同时调查问题的不同侧面，互相分享、质疑发现。
- **新模块/功能**：各 teammate 各占一块，互不踩脚。
- **竞争假设调试**：teammates 并行测试不同理论，更快收敛。
- **跨层协调**：前端、后端、测试各由一个 teammate 负责。

**不该用：** Agent Teams 引入协调开销，token 消耗远高于单会话。teammates 能独立运作时才划算。顺序任务、同文件编辑、依赖密集的工作——单会话或 subagents 更有效。

### 与 subagents 对比

|  | Subagents | Agent teams |
|---|---|---|
| **Context** | 独立 window，结果返回调用者 | 独立 window，完全独立 |
| **通信** | 只向主 agent 汇报 | teammates 之间直接互发消息 |
| **协调** | 主 agent 管理一切 | 共享任务列表，自协调 |
| **适合** | 只关心结果的聚焦任务 | 需要讨论与协作的复杂工作 |
| **Token 成本** | 较低（结果摘要回主 context） | 较高（每个 teammate 是独立 Claude 实例） |

## 二、启用

默认禁用。设置 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`（shell 或 settings.json）：

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

## 三、启动与控制

启用后用自然语言描述任务和想要的 teammates，Claude 生成并协调。两种生成方式：你主动要 teammates，或 Claude 判断任务适合并行后**提议**（你确认才执行——不会未经同意生成）。

### 显示模式

- **In-process**（**默认**）：所有 teammates 跑在主终端。用上下方向键在 agent panel 选 teammate，回车查看，直接打字发消息。任何终端可用，零配置。
  - 注意：**v2.1.179 起默认改为 `in-process`**；此前默认是 `auto`。升级后的会话若以前开 split panes，现在会留在单终端，除非显式设置。
- **Split panes**：每个 teammate 独立窗格，可同时看所有人输出，点窗格直接交互。**需要 tmux 或 iTerm2**。

模式取值：`in-process`、`auto`（在 tmux 会话内或 iTerm2+it2 时启用 split panes，否则回退）、`tmux`、`iterm2`（v2.1.186 起，显式 iTerm2 原生分屏，需 `it2` CLI）。

配置：`teammateMode` 写进 `~/.claude/settings.json`，或单次会话用 `claude --teammate-mode auto`。

Split panes 依赖：tmux（系统包管理器装）或 iTerm2（装 `it2` CLI + 启用 iTerm2 → Settings → General → Magic → Enable Python API）。**不支持** VS Code 集成终端、Windows Terminal、Ghostty。

### ⚠️ 导航键（官方，非 Shift+方向键）

agent panel 内：
- **上/下方向键**：选择 teammate
- **Enter**：打开该 teammate 的 transcript，直接发消息
- **Escape**：中断该 teammate 当前回合
- **`x`**（选中 teammate 时）：停止它
- **Ctrl+T**：切换任务列表

> 注意：`Shift+↑/↓` 是 **Agent View**（另一功能）里用来重排会话顺序的，**不是**切换 teammate 的键。此处易混。

### 指定 teammates 与模型

Claude 按任务决定数量，或你显式指定：

```
Spawn 4 teammates to refactor these modules in parallel. Use Sonnet for each teammate.
```

**teammates 默认不继承 lead 的 `/model`**。改默认模型：在 `/config` 里设 **Default teammate model**（选 "Default (leader's model)" 则跟随 lead）。teammates **继承 lead 的 effort level**（split-pane 模式自 v2.1.186 起）。

### 要求计划审批

高风险任务可要求 teammate 先规划，lead 审批后才实施（teammate 处于只读 plan mode）：

```
Spawn an architect teammate to refactor the authentication module.
Require plan approval before they make any changes.
```

teammate 完成规划→发审批请求→lead 批准或附反馈拒绝（拒绝则留 plan mode 修改重提）。lead 自主决策；用 prompt 给标准影响其判断（如"只批准含测试覆盖的计划"）。

### 直接与 teammate 对话

每个 teammate 是完整的独立 Claude Code 会话。可给它追加指令、追问、重定向。
- In-process：方向键选中→Enter 查看→打字发送。`x` 停止。Ctrl+T 切任务列表。
- Split-pane：点窗格直接交互。

查看 in-process teammate 时，纯文本和 skills 发给该 teammate，但**内置命令仍跑在 lead 会话**。teammate 的模型和 fast mode 在生成时固定，`/model`、`/fast` 只改 lead 的设置。`/effort` 仍作用于当前查看的 teammate（因为 teammates 跟随 lead 的 effort）。

### 任务分配与领取

共享任务列表协调。任务三态：pending / in progress / completed，且可有依赖（有未完成依赖的 pending 任务不能被领取）。
- **Lead 分配**：告诉 lead 哪个任务给哪个 teammate。
- **自主领取**：teammate 完成一个任务后，自己领取下一个未分配、未阻塞的任务。

**任务领取用文件锁**防止多个 teammate 同时抢同一任务的竞态。

### 关闭 teammate

按名字引用：`Ask the researcher teammate to shut down`。lead 发关闭请求，teammate 可批准（优雅退出）或附理由拒绝。**会话结束时共享目录自动清理**，无需单独 cleanup 步骤。

### 用 Hooks 强制质量门

- `TeammateIdle`：teammate 即将空闲时跑。exit 2 = 发反馈并让它继续。
- `TaskCreated`：任务被创建时跑。exit 2 = 阻止创建并发反馈。
- `TaskCompleted`：任务被标记完成时跑。exit 2 = 阻止完成并发反馈。

## 四、工作原理

### 架构

| 组件 | 角色 |
|---|---|
| **Team lead** | 主 Claude Code 会话，生成 teammates、协调工作 |
| **Teammates** | 独立 Claude Code 实例，各干分配的任务 |
| **Task list** | 共享任务列表，teammates 领取与完成 |
| **Mailbox** | agent 间通信系统 |

任务依赖自动管理：一个 teammate 完成被依赖的任务，阻塞的任务自动解锁。

**本地存储**（团队名 = `session-` + 会话 ID 前 8 位）：
- **Team config**：`~/.claude/teams/{team-name}/config.json` —— 会话结束时删除。
- **Task list**：`~/.claude/tasks/{team-name}/` —— **持久化**，从不上传，恢复会话时保留任务（受 `cleanupPeriodDays` 管）。

team config 存运行时状态（会话 ID、tmux pane ID），**别手改或预写**——下次状态更新会覆盖。**没有项目级等价物**：项目里的 `.claude/teams/teams.json` 不被识别为配置，Claude 当普通文件对待。

### 用 subagent 定义当 teammate

生成 teammate 时可引用任何 scope（project/user/plugin/CLI）的 subagent 类型，把一个角色（如 security-reviewer）定义一次，既作委托 subagent 又作 teammate 复用：

```
Spawn a teammate using the security-reviewer agent type to audit the auth module.
```

该 teammate 遵守定义的 `tools` allowlist 和 `model`；定义体**追加**进系统 prompt（非替换）。即便 `tools` 限制了别的工具，`SendMessage` 和任务管理工具对 teammate **始终可用**。

### 权限

teammates 以 lead 的权限设置启动（lead 跑 `--dangerously-skip-permissions` 则所有 teammates 也是）。生成后可改单个 teammate 的模式，但**生成时不能逐个设**。

关键安全约束：
- 一个 agent 经 `SendMessage` 发消息给另一个时，接收方被告知消息来自**另一个 Claude 会话**，不是来自你。
- **teammate 不能替你批准权限提示或提供同意**；被拒的动作不能转发给另一个 teammate 绕过检查。
- auto 模式下，分类器把"从别的 agent 转来的批准声明"当**不可信输入**，不当作你的确认。
- teammate 的权限提示**冒泡到 lead 会话**，在那里自己批准。

### 上下文与通信

每个 teammate 独立 context window，生成时加载与普通会话相同的项目上下文（CLAUDE.md、MCP servers、skills）+ lead 的生成 prompt。**lead 的对话历史不带过来。**

teammates 共享信息的方式：
- **自动消息送达**：teammates 发消息时自动送达接收方，lead 无需轮询。
- **空闲通知**：teammate 完成停止时自动通知 lead（v2.1.198 起，回合因 API 错误结束的会带错误文本，不再伪装正常完成）。
- **共享任务列表**：所有 agent 能看任务状态、领可用工作。
- **按名发消息**：给某个具体 teammate 按名发消息。**要触达所有人，给每个接收方各发一条**（没有原生广播原语）。

lead 给每个 teammate 起名，任何 teammate 可按名互发。要后续 prompt 能引用，在生成指令里告诉 lead 每个叫什么。

### Token 用量

远高于单会话。每个 teammate 独立 context window，用量随活跃 teammate 数**线性增长**。研究/审查/新功能通常值得；常规任务单会话更省。

> 注：官方只说"显著更多""线性增长"，**未给具体倍数**。任何"3 队友 ≈ 3.5x"这类精确数字都是推测，须标 T4。

## 五、用例

### 并行代码审查

单个审查者一次只偏向一类问题。把审查标准拆成独立域，安全/性能/测试覆盖率同时被深入审查：

```
Spawn three teammates to review PR #142:
- One focused on security implications
- One checking performance impact
- One validating test coverage
Have them each review and report findings.
```

### 竞争假设调试

根因不明时，单个 agent 倾向找一个貌似合理的解释就停。让 teammates 显式对抗——每个不只调查自己的理论，还要质疑别人的：

```
Users report the app exits after one message instead of staying connected.
Spawn 5 agent teammates to investigate different hypotheses. Have them talk to
each other to try to disprove each other's theories, like a scientific
debate. Update the findings doc with whatever consensus emerges.
```

辩论结构是关键机制：顺序调查受锚定效应影响；多个独立调查者主动互相证伪，活下来的理论更可能是真因。

## 六、最佳实践

1. **给够上下文**：teammates 自动加载项目上下文，但不继承 lead 对话历史。任务细节写进生成 prompt。
2. **合适的团队规模**：无硬上限，但 token 线性增长、协调开销增加、边际递减。**多数工作流 3-5 个 teammates 起步**。**每个 teammate 5-6 个任务**保持产出。15 个独立任务→3 teammates 起步。3 个聚焦的常胜过 5 个分散的。
3. **任务粒度合适**：太小（协调开销 > 收益）/ 太大（太久不 check-in，浪费风险高）/ 合适（自包含、有清晰交付物：一个函数、一个测试文件、一份审查）。
4. **等 teammates 完成**：lead 有时自己动手而不等。发现就提示：`Wait for your teammates to complete their tasks before proceeding`。
5. **从研究与审查起步**：新手先用边界清晰、不需写代码的任务（审 PR、调研库、查 bug），体会并行探索的价值，避开并行实现的协调难题。
6. **避免文件冲突**：两个 teammate 改同一文件会互相覆盖。拆工作让每个 teammate 拥有不同文件集。
7. **监控与引导**：定期查进度、重定向无效方向、综合发现。放任团队跑太久增加浪费风险。

## 七、故障排除

- **teammates 不出现**：in-process 下 teammates 在 prompt 下方 agent panel，方向键选+Enter 看；任务太简单 Claude 可能判断不需要团队；显式要 split panes 则确认 tmux 在 PATH；iTerm2 确认 `it2` CLI + Python API。
- **权限提示太多**：teammate 权限请求冒泡到 lead 造成摩擦。生成前在权限设置里预批常见操作。
- **teammate 遇错停止**：选中+Enter 看输出，给指令或生成替代 teammate（v2.1.198 起，lead 或别的 teammate 发消息能唤醒等待重试 API 的 in-process teammate，立即重试）。
- **lead 提前收工**：告诉它继续 / 等 teammates 完成。
- **孤儿 tmux session**：`tmux ls` → `tmux kill-session -t <name>`。

## 八、局限

- **in-process teammate 不能会话恢复**：`/resume`、`/rewind` 不恢复 in-process teammates。恢复后 lead 可能给已不存在的 teammates 发消息——让它生成新的。
- **任务状态滞后**：teammates 有时忘标完成，阻塞依赖任务。手动更新或让 lead 提醒。
- **关闭较慢**：teammates 完成当前请求/工具调用才关。
- **一会话一团队**：会话有且仅有一个团队，作用于该会话。不能建额外命名团队或跨会话共享。
- **无嵌套团队**：teammates 不能生成自己的 teammates。只有 lead 管团队。
- **in-process teammate 不能跑后台 subagent**：in-process teammate 自己的 subagents 跑前台；要后台的（`run_in_background` 或 frontmatter `background: true`）会报错，因为 teammate 的后台工作活不过 lead 进程。
- **lead 固定**：主会话终身是 lead，不能提升 teammate 或转交。
- **权限生成时定**：所有 teammates 以 lead 权限模式启动；生成后可改单个，生成时不能逐个设。
- **split panes 需 tmux 或 iTerm2**：in-process 任何终端可用；split-pane 不支持 VS Code 集成终端、Windows Terminal、Ghostty。

## 九、关联：Agent View（`claude agents`）

[Agent View](https://code.claude.com/docs/en/agent-view) 是同一"Agents and parallel work"家族里的**另一功能**（research preview，需 v2.1.139+）。一句话区分：

- **Agent Teams**：lead + teammates **协作**（共享任务列表、互发消息、自协调）。
- **Agent View**：从一个屏幕**派发并管理多个独立后台会话**——`claude agents` 打开，每条 prompt 起一个独立后台会话，各行其是，互不通信。适合多个互不相干的独立任务。

Agent View 要点：`claude agents` 打开；方向键选行、Space 预览、Enter/→ 挂进、← 空 prompt 后台化、Ctrl+T 置顶、Ctrl+X 停止（再按删除）；`claude --bg "prompt"` 从 shell 直接起后台会话；后台会话编辑前自动移进 `.claude/worktrees/` 隔离 worktree（v2.1.198 起会自动 commit/push 独立分支并开 draft PR，绝不碰 main/master、不 force-push、不 merge）。后台会话由 per-user supervisor 进程托管，关终端不停。

**[Tutorial perspective]** 三种并行方式的取舍：subagents（同会话内轻量委托，只回结果）／agent teams（协作型，互发消息自协调）／agent view（独立后台会话，互不通信）／git worktrees（你手动跑多个会话，无自动协调）。

## 原文出处
- [Orchestrate teams of Claude Code sessions](https://code.claude.com/docs/en/agent-teams)（Anthropic 官方 Claude Code Docs，截至 v2.1.199，访问于 2026-07-04）
- [Manage multiple agents with agent view](https://code.claude.com/docs/en/agent-view)（Anthropic 官方 Claude Code Docs，research preview）
