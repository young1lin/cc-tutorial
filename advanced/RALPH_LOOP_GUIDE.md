# Ralph Loop 插件详解

> 用 Stop hook 把 Claude 关在同一个会话里，同一道题反复做，直到它交出完成信号。

本地：Anthropic 官方插件 `ralph-loop` v1.0.0，市场 `claude-plugins-official`，作者署名 Anthropic（[plugin.json](.claude-plugin/plugin.json), T1）。实现 Geoffrey Huntley 的 **Ralph Wiggum 技术**（[ghuntley.com/ralph](https://ghuntley.com/ralph/), T1/T2，以《辛普森一家》角色命名）。

---

## 一、它是什么

README 原话（T1）：

> Ralph is a Bash loop — a simple `while true` that repeatedly feeds an AI agent a prompt file, allowing it to iteratively improve its work until completion.

核心：让 agent 在循环里反复吃**同一个 prompt**，直到任务完成。原版是外部 `bash while-true`；这个插件把它搬进**当前会话**，靠 Stop hook 实现——不用外部脚本，不用开第二个进程。

---

## 二、核心机制

启动一次：

```bash
/ralph-loop "Build a REST API for todos. CRUD + validation + tests. Output <promise>COMPLETE</promise> when done." \
  --completion-promise "COMPLETE" --max-iterations 50
```

之后会话自动循环（T1）：

```
1. Claude 工作一轮
2. 想退出（触发 Stop 事件）
3. Stop hook 拦截退出
4. Stop hook 把同一个 prompt 喂回去
5. Claude 看到自己上一轮改过的文件 + git history → 继续迭代
6. 直到完成信号 或 max-iterations
```

loop 跑在当前会话内。Stop hook（[hooks/stop-hook.sh](hooks/stop-hook.sh)）通过阻止正常会话退出，造出**自引用反馈循环**（T1）：

- prompt 每轮不变
- Claude 上一轮的修改留在文件和 git history 里
- 每一轮看到改过的文件，自主改进
- 靠读自己过去的产出迭代，而不是靠记忆对话

---

## 三、stop-hook 源码级拆解

这是整个插件的灵魂。stop-hook.sh 在每次 Claude 想退出时跑一遍，逻辑（T1）：

1. **没活动 loop？放行。** 检查 `.claude/ralph-loop.local.md` 状态文件不存在 → `exit 0`，正常退出。
2. **session 隔离。** 状态文件是 project-scoped，但 Stop hook 在该项目的**每个**会话都触发。源码比對状态里的 `session_id` 和 hook 输入的 `session_id`，不一致就放行——别的会话不能被这个 loop 误伤。
3. **数值校验。** `iteration` / `max_iterations` 不是合法数字 → 判定状态文件损坏，删文件、报错、停止。防手动编辑或写入中断导致的脏数据。
4. **到 max-iterations？放行。** `iteration >= max_iterations` → 删状态、打日志 `🛑 Max iterations reached`、退出。
5. **读 transcript 最后一条 assistant 文本。** transcript 是 JSONL，每行一个 content block。源码 `grep '"role":"assistant"' | tail -n 100` 取最后 100 条，jq 拼出最后一个 text block。限 100 行是为了长会话下 jq slurp 输入有界。
6. **检查完成信号。** 用 perl `-0777`（multiline）从最后输出里抽 `<promise>...</promise>` 标签内容，**精确字符串匹配** completion_promise。命中 → 删状态、`✅ Detected`、放行。
7. **都没命中 → 继续循环。** `iteration + 1`，更新状态文件，返回：

   ```json
   {
     "decision": "block",
     "reason": "<原 prompt>",
     "systemMessage": "🔄 Ralph iteration N | To stop: output <promise>COMPLETE</promise> (ONLY when statement is TRUE - do not lie to exit!)"
   }
   ```

   `decision: "block"` 阻止退出，`reason` 是下一轮要喂回的 prompt。

四个关键设计（T1）：

### 1. prompt 永不变，世界在变

prompt 是常量，但 Claude 每轮看到的世界变了——它自己上一轮改的文件、提交的 commit。这是「self-referential」的精髓：不靠对话记忆，靠**文件系统当跨轮记忆**。

### 2. completion promise 防「撒谎逃脱」

Claude 会想偷懒说「我做完了」溜走。所以完成信号必须是显式 `<promise>COMPLETE</promise>` 标签，且命令文件专门强调（T1 原文）：

> CRITICAL RULE: If a completion promise is set, you may ONLY output it when the statement is completely and unequivocally TRUE. Do not output false promises to escape the loop, even if you think you're stuck or should exit for other reasons.

这是反 rationalization——和 superpowers 的 Iron Law 同一个调调：用硬约束堵住 agent 的偷懒路径。

### 3. max-iterations 是真安全网

completion_promise 是精确字符串匹配，**处理不了多条件**（比如「SUCCESS」vs「BLOCKED」无法区分，README 明说）。所以 `--max-iterations` 是主防线，防不可能的任务死循环。README 建议**永远设一个合理的上限**，并在 prompt 里写「卡住 N 轮后怎么办」（记下阻塞点、列已尝试方案、给替代思路）。

### 4. 健壮兜底

状态文件损坏、transcript 缺失、jq 解析失败、没有 assistant 消息——每一种异常分支都是「删状态文件 + 停止循环 + 报错」。不会卡死，不会无限循环，每次失败都留可读日志。

---

## 四、用法

### `/ralph-loop`

```bash
/ralph-loop "<prompt>" --max-iterations <n> --completion-promise "<text>"
```

- `--max-iterations <n>`：N 轮后停（默认无限）
- `--completion-promise <text>`：完成信号词

### `/cancel-ralph`

取消活动 loop。

### Prompt 写法（README best practices，T1）

ralph-loop 成败**几乎全看 prompt 质量**。README 自己说「Operator Skill Matters — Success depends on writing good prompts, not just having a good model」。

| 原则 | 坏 | 好 |
|------|----|----|
| 明确完成标准 | "Build a todo API and make it good" | 列出：CRUD 全通、校验到位、测试覆盖 >80%、README 齐、输出 `<promise>COMPLETE</promise>` |
| 增量目标 | "Create a complete e-commerce platform" | Phase 1 认证 / Phase 2 商品目录 / Phase 3 购物车，全完成才输出 promise |
| 自我纠错 | "Write code for feature X" | TDD 循环写进 prompt：写失败测试 → 实现 → 跑 → 修 → refactor → 全绿才 promise |
| 逃生舱 | 不设上限 | 永远设 `--max-iterations`，并在 prompt 里写卡住后的兜底 |

---

## 五、loop 光谱定位

Claude Code 现在有**两套 loop 机制**，定位完全不同：

| | `/loop`（内置） | ralph-loop（插件） |
|---|---|---|
| 驱动 | **时间**（cron 式，按间隔触发） | **条件**（直到完成信号 / max 迭代） |
| 会话 | 每次触发是新一轮 | **同一会话**内紧密循环 |
| prompt | 可变 | **永不变** |
| 终止 | 手动 / 定时 | completion promise |
| 适合 | 周期性巡检（「每 5 分钟看 CI」） | 单任务死磕到底（「把测试搞绿」） |

和 superpowers 的 subagent-driven-development 也形成对照——都是「让 agent 长时间自主工作」，哲学相反：

- **superpowers SDD**：靠**流程纪律**——多 subagent、两阶段审查、TDD、plan，结构化管线
- **ralph-loop**：靠**暴力迭代**——单会话、同一 prompt、文件当记忆，极简 `while true`

**[Tutorial perspective]** ralph-loop 是「hooks = 强制执行」这条原理的最纯粹案例。你无法用 prompt 让 Claude 自主循环——它会自己停下、说做完了。但 Stop hook 能**物理上**阻止它退出。这是 hooks 价值的终极证明：CLAUDE.md 是请求，hook 是执行。

---

## 六、何时用 / 何时不用

T1（README）+ 判断：

**用**：
- 定义清楚 + 有明确成功标准的任务
- 需要迭代精炼（典型：让测试从红到绿）
- greenfield 项目，能走开（「walk away, come back to completed work」）
- 有自动验证（测试、linter）的任务

**不用**：
- 需要人判断 / 设计决策
- 一次性操作
- 成功标准模糊
- 生产 debugging（用 superpowers 的 systematic-debugging 针对性排查）

**[Author's analysis]** 适合 ralph-loop 的活，本质是「目标明确、路径未知、能用测试自动判完成」。最典型就是「把这批测试搞到全绿」。要设计审美、要产品判断的活交给它，它会迭代出一个能跑但丑陋的东西——因为它的停止条件是「测试过」，不是「做得好」。

---

## 七、Windows 兼容性（对你直接相关，T1）

stop hook 是 bash 脚本。Windows 上 `bash` 命令可能解析到 **WSL bash**（常配错）而不是 Git Bash，hook 会挂，报错如：

- `wsl: Unknown key 'automount.crossDistro'`
- `execvpe(/bin/bash) failed: No such file or directory`

README 给的 workaround——改缓存里插件的 hooks.json，显式指向 Git Bash（T1）：

```json
"command": "\"C:/Program Files/Git/bin/bash.exe\" ${CLAUDE_PLUGIN_ROOT}/hooks/stop-hook.sh"
```

位置：`~/.claude/plugins/cache/claude-plugins-official/ralph-wiggum/<hash>/hooks/hooks.json`

注意用 `Git/bin/bash.exe`（带 PATH 的 wrapper），**不是** `Git/usr/bin/bash.exe`（裸 MinGW，PATH 里缺工具，jq/perl 会找不到）。你是 Windows 11，要用必先修这条。

---

## 八、现实结果

**README 作者声称（T1，未独立验证）**：
- Y Combinator hackathon 一夜生成 6 个仓库
- 一个 $50k 合同用 $297 API 成本完成
- 3 个月用这个方法造了一整个编程语言「cursed」

**社区（T3）**：
- Claude Opus 4.5 自主跑 4 小时 49 分钟（[developersdigest](https://www.developersdigest.tech/blog/claude-code-autonomous-hours)）
- 「walk away, come back to completed work」（[paddo.dev](https://paddo.dev/blog/ralph-wiggum-autonomous-loops/)、[atcyrus](https://www.atcyrus.com/stories/ralph-wiggum-technique-claude-code-autonomous-loops)）

**[Tutorial perspective]** 这些数字是营销口径，不是独立基准。但方向可信：ralph-loop 真正的价值不在「省 API 钱」，而在**把人从循环里解放**——你把定义清楚、可自动验证的任务扔进去，去睡觉，醒来收结果。代价是 prompt 写不好就白烧 token，且产出质量天花板由「测试覆盖到什么程度」决定，不是「做得好不好」。

---

## 九、给本教程的判断

**[Tutorial perspective]** ralph-loop 在 Claude Code 高级用法里占一个独特位置：它是**最激进的自主性**——人完全离场，agent 自己迭代到完成。这和本教程的几条主线都对得上：

- 和 [research/14 loops](../research/14-claude-code-loops-getting-started.md) 互补：内置 `/loop` 是时间驱动，ralph 是条件驱动
- 和 [SUPERPOWERS_GUIDE](SUPERPOWERS_GUIDE.md) 对照：superpowers 用纪律让 agent 自主，ralph 用暴力让 agent 自主
- 是 hooks 价值的终极实证：见 [EXTENSIONS_OVERVIEW](EXTENSIONS_OVERVIEW.md)（待写）的 hooks 一节

**风险提示**：自主循环 = token 烧得快 + 产出不可预测。务必设 `--max-iterations`，务必写清楚完成标准和卡住兜底。把它当「能走开的重型机械」——好用，但得先检查安全装置。

---

## 参考（T1，本地插件源文件，路径相对插件根 `ralph-loop/`）

- `README.md` — 定位、原理、prompt 写法、何时用、Windows 注意
- `.claude-plugin/plugin.json` — 版本、作者元数据
- `commands/ralph-loop.md` — 启动命令、completion promise 诚实规则
- `commands/cancel-ralph.md` — 取消命令
- `hooks/hooks.json` — Stop hook 注册
- `hooks/stop-hook.sh` — 核心循环逻辑（拦截、状态机、promise 检测）
- `scripts/setup-ralph-loop.sh` — 状态文件初始化
- 原始技术：[ghuntley.com/ralph](https://ghuntley.com/ralph/)（T1/T2）
