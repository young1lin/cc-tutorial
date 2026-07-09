# Loop 与调度全指南

## 先说结论

loop 不是一种功能，是一条光谱：从「你每发一条 prompt」到「云端 routine 无人值守」。选错档位的代价是真金白银的 token。本文按光谱从轻到重过一遍，最后给选型表。

`T1` 官方定义（[Getting started with loops](https://claude.com/blog/getting-started-with-loops)，Delba de Oliveira & Michael Segner, Anthropic, 2026-06-30）：loops 是 agent 重复工作循环直到满足停止条件。不是所有任务都需要复杂 loop——从最简方案开始。

## loop 光谱总览

`T1` 四种类型（同上）：

| 类型 | 触发 | 停止 | 适合 |
|------|------|------|------|
| Turn-based | 用户 prompt | Claude 判定完成或需更多上下文 | 常规流程外的短任务 |
| Goal-based（`/goal`） | 实时手动 prompt | 目标达成或回合上限 | 有可验证退出条件的任务 |
| Time-based（`/loop`、`/schedule`） | 指定时间间隔 | 手动取消或工作完成 | 周期性工作、外部系统交互 |
| Proactive | 事件或排期 | 任务达目标退出 | 定义良好的周期性工作流 |

## Turn-based：每条 prompt 都是循环

你发的每条 prompt 都启动一个手动 loop：取上下文 → 行动 → 自检 → 必要时重来 → 回复。`T1` 官方建议（同上）：把手动验证步骤编码进 SKILL.md，让 Claude 端到端自检、带量化断言，减少来回回合。

## /goal：给循环一个可验证的终点

`T1` 机制（同上）：`/goal` 定义 done 条件 + 回合上限；每次 Claude 想停，evaluator 检查条件，不满足就扔回去继续。确定性条件（测试通过数、分数阈值）最有效。

```
/goal get the homepage Lighthouse score to 90 or above, stop after 5 tries.
```

`实测 @ Claude Code v2.1.202`（2026-07-07，Windows 10）：`claude --help 2>&1 | Select-String -Pattern 'goal'` 无匹配输出；本会话可用技能清单含 `loop`、`schedule`，不含 `goal`。两处均未见 `/goal` 入口——按上文 `T1` 描述记录机制，本环境 v2.1.202 未验证。

## /loop：本机定时重跑

`T1`（同上）：`/loop` 按间隔重跑一个 prompt，跑在本机、关机就停。

```
/loop 5m check my PR, address review comments, and fix failing CI
```

省略间隔则模型自节奏。本环境 v2.1.202 技能清单可见 `/loop` 入口。

## Cron 工具面

会话内还有一层更细的原生定时原语：`CronCreate` / `CronList` / `CronDelete`。

`实测 @ Claude Code v2.1.202`（2026-07-07，Windows 10）：

- CronCreate 入参与返回：入参 `{cron: "3 9 * * *", prompt: "输出一行文本：cron demo", recurring: true}`；返回原文「Scheduled recurring job cad084ed (Every day at 9:03 AM). Session-only (not written to disk, dies when Claude exits). Auto-expires after 7 days. Use CronDelete to cancel sooner.」`CronCreate` 没有独立的任务名参数，任务以返回的 job ID（如 `cad084ed`）标识，不是按名字调度——这点和「建一个叫 demo-noop 的任务」的直觉命名不同。
- CronList 输出：「cad084ed — Every day at 9:03 AM (recurring) [session-only]: 输出一行文本：cron demo」
- CronDelete 后列表：`CronDelete(id: "cad084ed")` 返回原文「Cancelled job cad084ed.」；随后复跑 `CronList` 输出「No scheduled jobs.」——列表确认已清空。

机制事实（同一次实测中读到的工具描述，可作补充参考）：标准 5 字段 cron 表达式按用户本地时区解释，无需换算；`recurring: false` 为一次性任务，触发后自动删除；任务只在 REPL 空闲时触发，不打断进行中的查询；调度器自带抖动，recurring 任务最多晚 10% 周期（上限 15 分钟），建议避开 :00/:30 整点；任务只存活于当前会话，不写盘，会话退出即消失，recurring 任务 7 天自动过期。

## /schedule：loop 上云

`T1`（同上）：`/loop` 跑本机，`/schedule` 把 loop 搬到云上成为 routine，关机也跑。本环境 v2.1.202 技能清单可见 `/schedule` 入口。

## Ralph Loop：不让会话停的 hook 内循环

### 它是什么

本地插件：Anthropic 官方市场 `claude-plugins-official` 里的 `ralph-loop` v1.0.0，plugin.json 作者署名 Anthropic（`T1`）——但技术本身原创者是 **Geoffrey Huntley**（[ghuntley.com/ralph](https://ghuntley.com/ralph/)，`T2`，以《辛普森一家》角色命名）；Anthropic 只是把 Huntley 的外部 bash 循环打包进当前会话。别把「官方市场里的插件」误读成「Anthropic 发明的技术」。

README 原话（`T1`）：

> Ralph is a Bash loop — a simple `while true` that repeatedly feeds an AI agent a prompt file, allowing it to iteratively improve its work until completion.

核心：让 agent 在循环里反复吃同一个 prompt，直到任务完成。原版是外部 `bash while-true`；这个插件把它搬进当前会话，靠 Stop hook 实现——不用外部脚本，不用开第二个进程。

### 核心机制

启动一次：

```bash
/ralph-loop "Build a REST API for todos. CRUD + validation + tests. Output <promise>COMPLETE</promise> when done." \
  --completion-promise "COMPLETE" --max-iterations 50
```

之后会话自动循环（`T1`）：Claude 工作一轮 → 想退出（触发 Stop 事件） → Stop hook（插件源文件 `hooks/stop-hook.sh`）拦截退出 → 把同一个 prompt 喂回去 → Claude 看到自己上一轮改过的文件 + git history → 继续迭代 → 直到完成信号或 max-iterations。

这是自引用反馈循环（`T1`）：prompt 每轮不变；Claude 上一轮的修改留在文件和 git history 里；每一轮看到改过的文件，自主改进；靠读自己过去的产出迭代，而不是靠记忆对话。

### stop-hook 源码级拆解

`hooks/stop-hook.sh` 是整个插件的灵魂，每次 Claude 想退出时跑一遍，逻辑（`T1`）：

1. 没活动 loop？检查 `.claude/ralph-loop.local.md` 状态文件不存在则 `exit 0`，正常退出。
2. session 隔离：状态里的 `session_id` 与 hook 输入的 `session_id` 不一致就放行，别的会话不受这个 loop 误伤。
3. 数值校验：`iteration` / `max_iterations` 不是合法数字判定状态文件损坏，删文件、报错、停止。
4. 到 `max-iterations`：删状态、打日志 `🛑 Max iterations reached`、退出。
5. 读 transcript 最后一条 assistant 文本：`grep '"role":"assistant"' | tail -n 100`，jq 拼出最后一个 text block（限 100 行是为长会话下 jq slurp 输入设界）。
6. 检查完成信号：用 perl `-0777`（multiline）从最后输出抽 `<promise>...</promise>` 标签内容，精确字符串匹配 completion_promise，命中则删状态、`✅ Detected`、放行。
7. 都没命中则 `iteration + 1`，更新状态文件，返回：

   ```json
   {
     "decision": "block",
     "reason": "<原 prompt>",
     "systemMessage": "🔄 Ralph iteration N | To stop: output <promise>COMPLETE</promise> (ONLY when statement is TRUE - do not lie to exit!)"
   }
   ```

   `decision: "block"` 阻止退出，`reason` 是下一轮要喂回的 prompt。

两个关键设计（`T1`）：prompt 永不变，世界（文件系统、git history）在变——这是「文件系统当跨轮记忆」的精髓；completion promise 必须显式精确匹配，防「撒谎逃脱」，命令文件原文强调：

> CRITICAL RULE: If a completion promise is set, you may ONLY output it when the statement is completely and unequivocally TRUE. Do not output false promises to escape the loop, even if you think you're stuck or should exit for other reasons.

`max-iterations` 是真正的安全网——completion_promise 是精确字符串匹配，处理不了多条件（README 明说无法区分「SUCCESS」vs「BLOCKED」），所以务必设合理上限，并在 prompt 里写清楚卡住后的兜底。状态文件损坏、transcript 缺失、jq 解析失败、没有 assistant 消息——每一种异常分支都是「删状态文件 + 停止循环 + 报错」，不会卡死，每次失败都留可读日志。

用法：`/ralph-loop "<prompt>" --max-iterations <n> --completion-promise "<text>"`（插件源文件 `commands/ralph-loop.md`）启动一次循环；`/cancel-ralph`（插件源文件 `commands/cancel-ralph.md`）取消活动 loop。成败几乎全看 prompt 质量——README 原话「Operator Skill Matters — Success depends on writing good prompts, not just having a good model」：明确列出完成标准而不是模糊描述、把大任务拆成必须全部完成才输出 promise 的增量 Phase、把 TDD 式自我纠错循环写进 prompt、永远设逃生舱（`--max-iterations` 加卡住后的兜底动作）。

### Windows 兼容性

stop hook 是 bash 脚本。Windows 上 `bash` 命令可能解析到 WSL bash（常配错）而不是 Git Bash，hook 会挂，报错如 `wsl: Unknown key 'automount.crossDistro'`、`execvpe(/bin/bash) failed: No such file or directory`。README 给的 workaround（`T1`）：改缓存里插件的 `hooks/hooks.json`，显式指向 Git Bash：

```json
"command": "\"C:/Program Files/Git/bin/bash.exe\" ${CLAUDE_PLUGIN_ROOT}/hooks/stop-hook.sh"
```

位置：`~/.claude/plugins/cache/claude-plugins-official/ralph-wiggum/<hash>/hooks/hooks.json`。注意用 `Git/bin/bash.exe`（带 PATH 的 wrapper），**不是** `Git/usr/bin/bash.exe`（裸 MinGW，PATH 里缺工具，jq/perl 会找不到）。

### 何时用 / 何时不用

`T1`（README）+ 判断：

**用**：定义清楚 + 有明确成功标准的任务；需要迭代精炼（典型：让测试从红到绿）；greenfield 项目，能走开（「walk away, come back to completed work」）；有自动验证（测试、linter）的任务。

**不用**：需要人判断 / 设计决策；一次性操作；成功标准模糊；生产 debugging（用 superpowers 的 systematic-debugging 针对性排查）。

**[Author's analysis]** 适合 ralph-loop 的活，本质是「目标明确、路径未知、能用测试自动判完成」。最典型就是「把这批测试搞到全绿」。要设计审美、要产品判断的活交给它，它会迭代出一个能跑但丑陋的东西——因为它的停止条件是「测试过」，不是「做得好」。

### 现实结果

README 作者声称（`T1`，未独立验证）：Y Combinator hackathon 一夜生成 6 个仓库；一个 $50k 合同用 $297 API 成本完成；3 个月用这个方法造了一整个编程语言「cursed」。

社区（`T3`，两个独立来源）：「walk away, come back to completed work」（[paddo.dev](https://paddo.dev/blog/ralph-wiggum-autonomous-loops/)、[atcyrus](https://www.atcyrus.com/stories/ralph-wiggum-technique-claude-code-autonomous-loops)）。另有单一来源报道 Claude Opus 4.5 自主跑 4 小时 49 分钟（[developersdigest](https://www.developersdigest.tech/blog/claude-code-autonomous-hours)）——只有一家，够不上 T3，当轶闻看。

**[Tutorial perspective]** 这些数字是营销口径，不是独立基准。但方向可信：ralph-loop 真正的价值不在「省 API 钱」，而在把人从循环里解放——把定义清楚、可自动验证的任务扔进去，去睡觉，醒来收结果。代价是 prompt 写不好就白烧 token，且产出质量天花板由「测试覆盖到什么程度」决定，不是「做得好不好」。

### 给本教程的判断

**[Tutorial perspective]** ralph-loop 在 Claude Code 高级用法里占一个独特位置：它是最激进的自主性——人完全离场，agent 自己迭代到完成。和 [SUPERPOWERS_GUIDE](SUPERPOWERS_GUIDE.md) 的 subagent-driven-development 哲学相反：superpowers 靠流程纪律（多 subagent、两阶段审查、TDD、plan）让 agent 自主；ralph 靠暴力迭代（单会话、同一 prompt、文件当记忆）让 agent 自主。它也是 hooks 价值的终极实证——CLAUDE.md 是请求，hook 是执行：你无法用 prompt 让 Claude 自主循环，它会自己停下说做完了，但 Stop hook 能物理上阻止它退出。

**风险提示**：自主循环 = token 烧得快 + 产出不可预测。务必设 `--max-iterations`，务必写清楚完成标准和卡住兜底。把它当「能走开的重型机械」——好用，但得先检查安全装置。

参考（`T1`，本地插件源文件，路径相对插件根 `ralph-loop/`）：`README.md`、`.claude-plugin/plugin.json`、`commands/ralph-loop.md`、`commands/cancel-ralph.md`、`hooks/hooks.json`、`hooks/stop-hook.sh`、`scripts/setup-ralph-loop.sh`；原始技术：[ghuntley.com/ralph](https://ghuntley.com/ralph/)（`T1`/`T2`）。

光谱定位：原生 `/loop` 是「外部定时重跑」，Ralph 是「用 Stop hook 拦住会话不让它结束」。前者每轮全新上下文，后者同一会话滚雪球。

## 选型表

**[Tutorial perspective]**

| 场景 | 用什么 |
|------|--------|
| 一次性任务 | 别上 loop，一条 prompt 打完 |
| 有可验证 done 条件 | `/goal`（本环境 v2.1.202 未见此入口，见上文实测） |
| 周期性、本机、可关机停 | `/loop` 或 Cron 工具 |
| 周期性、跨机器、长期 | `/schedule` |
| 「永不松手」压榨单会话 | Ralph Loop |

## token 边界

`T1` 官方用量管理四条（同上）：选对 primitive 和模型；定义清晰的 success/stop 条件；大规模跑前先试点；确定性工作用脚本而不是推理。
