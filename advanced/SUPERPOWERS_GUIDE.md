# Superpowers 插件详解

> 一套给编码 agent 的「软件开发方法论」，核心不在教 agent 新本事，而在用强制流程堵死它的偷懒路径。

本地版本：`v6.1.1`，作者 [Jesse Vincent](https://blog.fsck.com) / Prime Radiant，MIT，来自 Anthropic 官方插件市场 `claude-plugins-official`（插件源文件 `.claude-plugin/plugin.json` 与插件 `README.md`，T1，路径相对插件根，见文末参考）。仓库 `obra/superpowers`，首发 2025-10-09（[发布文](https://blog.fsck.com/2025/10/09/superpowers/)）。本篇讲怎么用现成插件；想自己打包、自建市场，见 [Plugins 打包与分发](PLUGINS_GUIDE.md)。

---

## 一、它到底是什么

README 一句话定位（T1，原文）：

> Superpowers is a complete software development methodology for your coding agents, built on top of a set of composable skills and some initial instructions that make sure your agent uses them.

后半句是重点。市面上多的是「100 个 prompt 模板」之类的仓库，agent 用不用全看心情。Superpowers 的差别在 `make sure your agent uses them`——它靠一个 `session-start` hook，在每次会话启动时把 `using-superpowers` 这条 bootstrap 指令注入 agent 上下文，强制 agent 在任何动作前先检查「有没有 skill 适用」。skills 是弹药，hook 是保险栓。

14 个 skill（T1，按 README 分类）：

| 类别 | Skill | 作用 |
|------|-------|------|
| 入口 | `using-superpowers` | 强制 skill 检查（会话启动注入） |
| 协作 | `brainstorming` | 写代码前先把需求逼成设计 |
| 协作 | `writing-plans` / `executing-plans` | 把设计拆成 2-5 分钟的任务粒度 |
| 协作 | `subagent-driven-development` | 每个任务派 subagent + 两阶段审查 |
| 协作 | `dispatching-parallel-agents` | 并行 subagent |
| 协作 | `requesting-code-review` / `receiving-code-review` | 代码审查的请求与接收 |
| 协作 | `using-git-worktrees` / `finishing-a-development-branch` | 工作树隔离与收尾 |
| 测试 | `test-driven-development` | 强制 RED-GREEN-REFACTOR |
| 调试 | `systematic-debugging` | 找根因前不准改代码 |
| 调试 | `verification-before-completion` | 声称完成前必须跑验证 |
| 元 | `writing-skills` | 怎么写新 skill |

---

## 二、设计哲学：对抗 rationalization

**[Author's analysis]** 整个插件的「为什么这么写」，归结到一个判断：**LLM agent 的头号失败模式不是能力不足，是 rationalization（自我合理化跳过流程）。** 它会说「这个太简单，不用 brainstorm」「先改了再看」「should work now」「我记得这个 skill」——然后绕开流程，产出半成品。

Superpowers 的作者显然吃过足够多的亏。每个核心 skill 都长着同一副骨架：

1. **一条不可协商的 Iron Law / HARD-GATE**——全大写、措辞绝对。
2. **一张「Red Flags / Rationalizations」表**——把 agent 可能冒出来的偷懒念头逐条列出，逐条击破。
3. **强制顺序流程**（checklist / phases），且明确「违反字面就是违反精神」。
4. **证据门槛**——不准猜、不准假设、必须 run command 看输出。

这套骨架是反 rationalization 的工程化实现。`using-superpowers` 的红旗表最能说明问题（T1，原文摘录）：

| Agent 的念头 | 现实 |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "The skill is overkill" | Simple things become complex. Use it. |
| "I remember this skill" | Skills evolve. Read current version. |
| "I'll just do this one thing first" | Check BEFORE doing anything. |

这张表的每一行，都是某次 agent 真实绕过流程后补上的。

---

## 三、brainstorming：HARD-GATE 与九步

`brainstorming` 是整个方法论的入口（T1，插件源文件 `skills/brainstorming/SKILL.md`）。它的核心是一条硬门：

> <HARD-GATE>
> Do NOT invoke any implementation skill, write any code, scaffold any project, or take any implementation action until you have presented a design and the user has approved it. This applies to EVERY project regardless of perceived simplicity.
> </HARD-GATE>

设计获批前，禁止任何实现动作。而且它专门点名一个反模式——「This Is Too Simple To Need A Design」：

> Every project goes through this process. A todo list, a single-function utility, a config change — all of them. "Simple" projects are where unexamined assumptions cause the most wasted work.

**[Author's analysis]** 这条针对的就是 agent 最常见的 rationalization：「就改一行，不用走流程」。作者的反驳很准——简单项目不是不该设计，而是设计可以短（几句话），但必须摆出来、必须获批。因为最浪费的返工，恰恰来自「太简单所以没问」的隐性假设。

九步 checklist（T1，强制逐项建 task）：

1. 探查项目上下文（文件、文档、最近 commit）
2. **适时**提供 visual companion（见下节，不提前 offer）
3. 一次问一个澄清问题
4. 给 2-3 个方案 + trade-off + 推荐
5. 分节呈现设计，每节获批准
6. 写设计文档到 `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` 并 commit
7. 设计自审（占位符 / 自相矛盾 / 范围 / 歧义）
8. 用户审 spec 文件
9. 转交 `writing-plans` 写实现计划

终态也是硬约束：

> The terminal state is invoking writing-plans. Do NOT invoke frontend-design, mcp-builder, or any other implementation skill.

brainstorming 之后唯一允许调的下一个 skill 是 `writing-plans`。不准跳过计划直接撸代码，也不准拐去别的实现 skill。这条把「设计→计划→实现」的管线焊死。

几个贯穿全文的小原则（T1）：

- **一次一个问题**——不准一堆问题砸过去
- **优先多选题**——比开放题好答
- **YAGNI ruthlessly**——设计里所有不必要的功能砍掉
- **必给 2-3 方案**——不准只给一条路

---

## 四、Visual Companion：为什么是 tool，不是 mode

这是 Superpowers 里最「炫」、也最克制的一个功能。用户特别问到它，值得单独拆。

### 它解决什么

**[Author's analysis]** 有些设计决策用文字描述，等于让用户在脑子里做渲染。「左边 sidebar 还是顶部 nav」「这两个配色哪个对」「这个状态机长什么样」——这类问题，看一眼图比读三段话快十倍，且不会因为描述歧义各想各的。Visual companion 给 agent 一个浏览器 tab，让它把 mockup / 布局对比 / 架构图直接画出来，用户点选，选择回传给 agent。

### 为什么是 tool 不是 mode

SKILL.md 原文（T1）：

> A browser-based companion for showing mockups, diagrams, and visual options during brainstorming. Available as a tool — not a mode. Accepting the companion means it's available for questions that benefit from visual treatment; it does NOT mean every question goes through the browser.

**[Author's analysis]** mode 会劫持整个会话——一旦开了，所有问题都强制走浏览器。但大部分设计问题本质是概念问题（「这里的 personality 指什么」「这几个功能哪些在范围内」），文字比图清楚。只有少数问题是真正的视觉问题。所以设计成 tool：按需取用，不是全局开关。

### 为什么 just-in-time，不提前 offer

SKILL.md 原文（T1）：

> Do NOT offer it upfront. Wait until a question would genuinely be clearer shown than told — a real mockup / layout / diagram question, not merely a UI *topic*.

而且 offer 必须**独占一条消息**：

> This offer MUST be its own message. Only the offer — no clarifying question, summary, or other content. Wait for the user's response.

**[Author's analysis]** 提前 offer 是个伪选择——用户还没遇到视觉问题，就被要求决定「要不要开浏览器」，决定没有信息支撑。等到真出现「看比说清楚」的瞬间再 offer，这个 yes/no 才有意义。独占消息这条更狠：offer 是一个会改变交互模式、有 token 成本的决策，必须从上下文里隔离出来，不能夹带在别的问题或总结里被用户顺手略过。这是反 rationalization 的延续——逼 agent 把「现在要不要切媒介」当成一个独立决策点，而不是顺手为之。

### 为什么 per-question decision

即使用户接受了 companion，也不准「开了就一直用」：

> Even after the user accepts, decide FOR EACH QUESTION whether to use the browser or the terminal. The test: would the user understand this better by seeing it than reading it?

判断标准给得很死（T1）：

- **浏览器**：内容本身就是视觉的——mockup、wireframe、布局对比、架构图、并排设计
- **终端**：内容是文字或表格——需求/范围问题、概念 A/B/C、trade-off 列表、技术决策

还专门防一类误判：

> A question about a UI topic is not automatically a visual question. "What does personality mean in this context?" is a conceptual question — use the terminal. "Which wizard layout works better?" is a visual question — use the browser.

**[Author's analysis]** 这是 agent 最容易偷懒的地方——一旦开了浏览器，惰性会驱使它把什么都往里塞（反正开着）。强制 per-question 判断 = 强制 agent 每个问题重新证明「这真的值得开图」。三道闸（just-in-time offer、offer 独占消息、per-question 决策）一起，把一个「很酷所以容易被滥用」的功能锁在「只在真正省事时才用」的窄通道里。SKILL.md 自己也明说它 `token-intensive`——克制是为了控成本。

### 技术架构：为什么这么搭

插件源文件 `skills/brainstorming/visual-companion.md`（T1）描述的机制：

1. **file-watch server**：一个本地服务器监视某个目录，把**最新写入的 HTML 文件**推给浏览器。agent 产出内容的方式就是写文件——它最熟的工具，不用学新 API。
2. **HTML fragment，不是完整文档**：agent 写的内容若不以 `<!DOCTYPE` / `<html>` 开头，server 自动套上 frame template（header、CSS 主题、连接状态、交互脚本）。agent 只管内容，基础设施由 server 提供。关注点分离，降低 agent 出错率。
3. **events 闭环**：用户在浏览器点选项，交互记成 JSONL 写到 `state_dir/events`，agent 下一轮读这个文件拿到结构化反馈。终端文字是主反馈，events 是补充。
4. **session key 鉴权**：URL 带 `?key=…`，server 拒绝无 key 的请求。防同一台机器的其他浏览器 tab、或局域网其他机器偷看屏幕 / 注入事件。首次加载后 cookie 记住 key。
5. **跨平台存活**：不同 harness（Claude Code / Codex / Copilot CLI / Pi）对后台进程的回收策略不同，start-server.sh 自动检测并切换 foreground/background 模式。

### 它是迭代出来的，不是一次写成的

`docs/superpowers/plans/` 目录留了完整演进线（T1，文件存在即证据）：

- `2026-01-17-visual-brainstorming.md` — 立项
- `2026-02-19-visual-brainstorming-refactor.md` — 重构
- `2026-03-11-zero-dep-brainstorm-server.md` — **零依赖重写**（server.cjs 不靠 npm install，用 Node 内置，降安装门槛）
- `2026-06-09-visual-companion-issues.md` — 问题修复
- `2026-06-10-visual-companion-auth-hardening.md` — **安全加固**（session key 就是这轮补的）
- `2026-06-11-visual-companion-final-hardening-fixup.md` — 收尾加固

**[Author's analysis]** 这条线本身就是「为什么这么写」的答案：session key 鉴权不是一开始就有的，是出了信任问题才补；零依赖不是洁癖，是装不上的人太多才重写。每一个设计决定背后都对应过一个真实痛点。

---

## 五、systematic-debugging：找根因前不准改

T1，插件源文件 `skills/systematic-debugging/SKILL.md`。铁律：

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

四阶段，必须顺序完成（T1）：

1. **Root Cause Investigation** — 读完错误、稳定复现、查最近改动、在多组件系统的每个边界打日志定位是哪层断了、回溯数据流找坏值的源头
2. **Pattern Analysis** — 找同仓库里能跑的相似代码，逐行读完参考实现，列出工作版与坏版的所有差异
3. **Hypothesis and Testing** — 写下「我认为 X 是根因因为 Y」，做最小改动单变量验证
4. **Implementation** — 先写失败测试，再单点修复，验证

最狠的一条在阶段 4：

> If ≥ 3: STOP and question the architecture ... This is NOT a failed hypothesis - this is a wrong architecture.

**[Author's analysis]** 连续 3 次修复失败，不准再试第 4 次——这说明不是假设错了，是架构错了。这条直接对抗 agent 的「再试一次」惯性。SKILL.md 给的数据（T1，作者声称）：systematic 路径 15-30 分钟修好、首次修复率 95%；乱猜路径 2-3 小时、首次 40%。这是作者用真实 debug session 量的对比。

---

## 六、verification-before-completion：证据先于断言

T1，插件源文件 `skills/verification-before-completion/SKILL.md`。铁律：

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

Gate Function 五步（T1）：识别证明命令 → 跑完整命令 → 读全输出和退出码 → 核对输出是否支持论断 → 只有支持才下论断。

它把「声称完成」和「验证完成」分开，并且明确点名红旗词：

> Using "should", "probably", "seems to" ... Expressing satisfaction before verification ("Great!", "Perfect!", "Done!", etc.)

最重的一句（T1，来自作者积累的失败记忆）：

> From 24 failure memories:
> - your human partner said "I don't believe you" - trust broken

**[Author's analysis]** 这个 skill 的存在本身就是一个教训的固化：agent 说「修好了」但没验证，用户信了，后来炸了，信任崩塌。所以它要求——「should work」「I'm confident」「agent said success」全都不算证据，必须 run command、读输出、再下结论。confidence ≠ evidence 是它的核心等式。

---

## 七、subagent-driven-development:进度账本是主梁

T1,插件源文件 `skills/subagent-driven-development/SKILL.md`。它把一份计划的执行拆成:controller 编排 + 每个 task 派一个 implementer 子代理 + 一个 task-reviewer 子代理(模板 `implementer-prompt.md` / `task-reviewer-prompt.md`,审 spec 合规 + 代码质量),整分支收尾再过一遍 `requesting-code-review` 的 `code-reviewer.md`。

但它真正的主梁是 **Durable Progress**(T1,原文):

> Conversation memory does not survive compaction ... controllers that lost their place have re-dispatched entire completed task sequences — **the single most expensive failure observed.**

机制(账本文件 `.superpowers/sdd/progress.md`):
- 开工先读账本(`cat "$(git rev-parse --show-toplevel)/.superpowers/sdd/progress.md"`);标 complete 的任务=已完成,不准重派,从第一个未完成续上
- 每过一个 review,追一行 `Task N: complete (commits <base7>..<head7>, review clean)`
- 账本是恢复地图:compaction 之后,信账本 + `git log`,别信自己的记忆
- `git clean -fdx` 会毁掉它(git-ignored scratch),毁了就从 `git log` 重建

外加一条 **Continuous execution**(T1):任务间不准停下来问"要不要继续"——唯一能停的理由是无法解决的 BLOCKED、真歧义、全部完成。

**[Author's analysis]** 这一节就是"带进度的 TODO.md"的工程化终点:进度不活在对话里,活在一个 git-SHA 键控、优先于记忆的文件里。区别只在——手动维护 vs 强制且带恢复协议。

---

## 八、receiving-code-review:不表演性同意

T1,`skills/receiving-code-review/SKILL.md`。这是之前只在总览表里一句带过、却最反直觉的 skill:**收到 review,第一反应不是照做。**

六步响应模式(T1,原文):

> READ → UNDERSTAND(用自己的话复述)→ VERIFY(对着代码现实核)→ EVALUATE(对**这个**代码库技术上成立吗)→ RESPOND(技术承认或有理反驳)→ IMPLEMENT(一次一条,逐条测)

**Forbidden Responses**(T1,原文):

> **NEVER:** "You're absolutely right!" / "Great point!" / "Let me implement that now" (before verification)

表演性同意被明令禁止。取而代之:复述技术需求、问澄清、有错用技术理由顶回去、或直接动手(actions > words)。**When To Push Back**:意见破坏现有功能、reviewer 缺上下文、违反 YAGNI、对本技术栈不正确、有兼容性理由、或和人类搭档的架构决策冲突——都该顶,用技术推理而非防御。

**[Author's analysis]** 这条直击 agent 头号谄媚失败:一见 review 就"您说得对"然后照单全改,把对的代码改坏。它把"同意"降级成一个需要证据的技术判断——和本仓库 evidence-based 同源。

---

## 九、dispatching-parallel-agents:先证明"独立"

T1,`skills/dispatching-parallel-agents/SKILL.md`。核心不是"能并行就并行",是**先证明任务之间真独立**。

**Use when**(T1):3+ 测试文件因不同根因失败、多子系统各自坏、每个问题不需要别人上下文就能懂、**investigations 之间无共享状态**。
**Don't use when**(T1):失败相关(修一个可能修好其它)、需要整体系统状态、代理之间会互相干扰。

四步法(T1):① Identify Independent Domains(按"坏了什么"分组,确认互不影响)② Create Focused Agent Tasks ③ Dispatch in Parallel ④ **Review and Integrate**(并行结果收回统一审、合并)。

**[Author's analysis]** 危险从来不是并行,是**假独立**:两个代理改同一块状态,并行就是数据竞争。所以重量全压在前置判断和第 4 步收口上。原来那句"并行 subagent"把最重要的前提和收尾都吞了。

---

## 十、test-driven-development:先看它失败

T1,`skills/test-driven-development/SKILL.md`。铁律:

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

执行最硬:先写了实现再补测试?**删掉,重来**(T1:"Write code before the test? Delete it. Start over.")——不准留作"参考"、不准"改改用",delete means delete。

RED-GREEN-REFACTOR 不是走一圈就算,中间有一道**亲眼验证门**:

> **Verify RED - Watch It Fail. MANDATORY. Never skip.**

跑测试,确认它**失败**(不是报错)、失败信息符合预期、失败原因是功能缺失而非 typo。测试直接过了?说明你在测已有行为,测试写错了。GREEN 之后同样要亲眼看它转绿。外加 Common Rationalizations 表、Red Flags—STOP and Start Over、独立的 `testing-anti-patterns.md`。

**[Author's analysis]** 原来的"强制 RED-GREEN-REFACTOR"漏了这个 skill 的灵魂——**"watch it fail"**。没亲眼见它红过的测试证明不了任何东西,绿可能是假绿。这一步是 TDD 与"补几个测试"的分水岭。

---

## 十一、writing-plans:计划里不准有占位

T1,`skills/writing-plans/SKILL.md`。它把"计划"定义成**另一个 session、没上下文的工程师照着就能做**的东西,所以两条硬规矩。

**No Placeholders**(T1,原文列为 "plan failures",永不准写):`TBD`/`TODO`/`implement later`、"add appropriate error handling"、"write tests for the above"(不给实际测试代码)、"Similar to Task N"(必须重复代码,读者可能乱序读)、只说做什么不给代码块。

**Self-Review**(T1):写完用新眼睛对着 spec 自审——① spec 覆盖(每条需求都指得到一个 task 吗)② 占位符扫描 ③ 类型一致性(Task 3 叫 `clearLayers()`、Task 7 叫 `clearFullLayers()` 就是 bug)。原文强调:**这是你自己跑的 checklist,不是派子代理**。另有 `plan-document-reviewer-prompt.md` 供需要时派审。粒度即文档说的 2-5 分钟 / 确切文件路径 / 每步给完整代码与预期输出。

**[Author's analysis]** 占位符=把思考推迟到执行时;而执行时是另一个没上下文的 agent,推迟=丢失。这条把"计划"和"愿望清单"划开。

---

## 十二、requesting-code-review:机制是派一个 reviewer 子代理

T1,`skills/requesting-code-review/SKILL.md`。之前文档只说"请求审查",没点出机制:**它派一个 `general-purpose` 子代理,套 `code-reviewer.md` 模板来审**。

流程:① 取 SHA(`BASE_SHA=$(git rev-parse HEAD~1)` / `HEAD_SHA=$(git rev-parse HEAD)`)② 用 `{DESCRIPTION}/{PLAN_OR_REQUIREMENTS}/{BASE_SHA}/{HEAD_SHA}` 填模板派子代理 ③ 按等级处置:**Critical 立即修、Important 推进前修、Minor 记下、reviewer 错了带理由顶回去**。

**[Author's analysis]** 关键是"审查=一个独立上下文的子代理读你的 diff",不是你自己回头看一眼——独立上下文才看得见被 tunnel-vision 挡住的东西。sdd 每个 task 的第二阶段审查复用的正是同一个 `code-reviewer.md`。

---

## 十三、executing-plans:先离开 main

T1,`skills/executing-plans/SKILL.md`。三步:Load and Review Plan → Execute Tasks → Complete Development(交给 finishing)。

一条硬门(T1):**`Never start implementation on main/master branch`**——执行计划前必须在隔离分支/工作树,呼应 `using-git-worktrees`。两个决策规则:**When to Stop and Ask for Help**(遇无法解决的 BLOCKED / 真歧义就停,不硬撑)、**When to Revisit Earlier Steps**(发现计划本身有问题,回头改计划,不将错就错)。

**[Author's analysis]** 它和 `subagent-driven-development` 是执行同一份计划的两种模式:executing-plans 带人工检查点、适合你想盯着;sdd 连续无人值守、靠 progress 账本。选哪个,看你要不要留在回路里。

---

## 十四、finishing-a-development-branch:先验证合并结果,再删

T1,`skills/finishing-a-development-branch/SKILL.md`。六步:Verify Tests → Detect Environment → Determine Base Branch → Present Options → Execute Choice → Cleanup Workspace。选项摆给用户:merge / 开 PR / 保留分支 / 丢弃,不替他决定。

真正的安全在执行顺序(T1,原文注释):

> Merge first — verify success before removing anything → **Verify tests on merged result** → Only after merge succeeds: cleanup worktree, then delete branch

**先合并、在合并后的结果上重跑测试、只有过了才清理工作树和删分支**;外加自动探测环境与 base 分支、用主仓库根做 CWD 防误删。

**[Author's analysis]** 顺序就是一切。先删分支再合并,合并一炸,work 就没了。文档原来列了"选项+清理",漏的正是这个"验证 gate 清理"的顺序——而顺序才是这个 skill 防的那类事故。

---

## 十五、工作流串联

README 给的标准管线（T1）：

```
brainstorming          → 把想法逼成设计 spec
       ↓
using-git-worktrees    → 开隔离工作树，跑通干净测试基线
       ↓
writing-plans          → 拆成 2-5 分钟粒度任务，每个任务带确切文件路径与验证步骤
       ↓
subagent-driven-dev    → 每任务派一个新 subagent，两阶段审查（spec 合规 → 代码质量）
   或 executing-plans     （或带人工检查点的批量执行）
       ↓
test-driven-development→ 强制 RED-GREEN-REFACTOR，先写测试看它失败，再写实现看它过
       ↓
requesting-code-review → 按计划逐条审，critical 问题阻断推进
       ↓
finishing-a-dev-branch → 验证测试、给选项（merge/PR/保留/丢弃）、清理工作树
```

README 原话总结：

> The agent checks for relevant skills before any task. Mandatory workflows, not suggestions.

「mandatory, not suggestions」——这是整个插件的态度。

---

## 十六、给本教程的判断

**[Tutorial perspective]** Superpowers 值得认真用，但要认清它的成本和适用边界。

**它的真实价值**不在「让 agent 更聪明」，而在「用不可协商的流程约束，把资深工程师的工作纪律编码进 agent，堵住它自我合理化跳步骤的倾向」。HARD-GATE、Iron Law、anti-rationalization 表、强制 checklist——每一项都是某次真实失败换来的。这一点从 `systematic-debugging/CREATION-LOG.md`、verification 的「24 failure memories」、visual companion 的 auth-hardening 演进线都能印证（T1）。

**代价**：

- 流程重。一行 typo 也要走 brainstorm → plan → TDD，对小任务是 overkill。
- token 贵。visual companion 明确 `token-intensive`，subagent-driven-development 每个 task 起新 subagent 也是独立 context。
- 语气强硬。`EXTREMELY-IMPORTANT` / `ALL CAPS` / `This is not negotiable` 的措辞，对人类读者有压迫感，但对 agent 有效——这是写给机器的纪律，不是写给人的散文。

**适用场景**：中大型工程任务、多人协作、容易返工的需求模糊地带——Superpowers 的流程收益覆盖它的成本。改一行配置、写个一次性脚本、快速验证想法——直接做，别让流程拖死自己。

**[Author's analysis]** 它的设计哲学和本教程强调的 evidence-based 规则同源：都把「证明」置于「断言」之上。`verification-before-completion` 的「evidence before claims」几乎就是本仓库 `evidence-based.md` 的「If it is a fact, prove it」的工程版。区别只在——一个约束 agent 怎么下技术结论，一个约束教程怎么下事实结论。

---

## 参考（T1，均为本地插件源文件，路径相对插件根 `superpowers/6.1.1/`）

- `README.md` — 定位、作者、工作流总览、哲学
- `.claude-plugin/plugin.json` — 版本、作者元数据
- `skills/using-superpowers/SKILL.md` — skill 检查强制规则、红旗表
- `skills/brainstorming/SKILL.md` — HARD-GATE、九步 checklist、visual companion 触发规则
- `skills/brainstorming/visual-companion.md` — visual companion 完整技术指南
- `skills/systematic-debugging/SKILL.md` — 四阶段、Iron Law、rationalization 表
- `skills/verification-before-completion/SKILL.md` — Gate Function、证据门槛
- `docs/superpowers/plans/2026-0*-visual-companion-*.md` — visual companion 迭代史
- `skills/subagent-driven-development/SKILL.md` — Durable Progress 账本、continuous execution;`implementer-prompt.md` / `task-reviewer-prompt.md` / `scripts/sdd-workspace`
- `skills/receiving-code-review/SKILL.md` — 六步响应、Forbidden Responses、When To Push Back
- `skills/dispatching-parallel-agents/SKILL.md` — 独立性判据、四步法
- `skills/test-driven-development/SKILL.md` — Iron Law、Verify RED/GREEN;`testing-anti-patterns.md`
- `skills/writing-plans/SKILL.md` — No Placeholders、Self-Review;`plan-document-reviewer-prompt.md`
- `skills/requesting-code-review/SKILL.md` 与 `code-reviewer.md` — reviewer 子代理模板
- `skills/executing-plans/SKILL.md` — 分支安全门、stop/revisit 规则
- `skills/finishing-a-development-branch/SKILL.md` — 验证-gate-清理顺序
