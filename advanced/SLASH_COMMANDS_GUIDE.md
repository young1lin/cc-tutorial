# Claude Code 斜杠命令全景（交互命令全集）

> 按用途分组的**全量**交互命令地图,覆盖官方 commands 参考里的 99 个命令（[Commands reference](https://code.claude.com/docs/en/commands)，T1，本篇校对于 Claude Code v2.1.202，2026-07）。一个不落,但已有专篇的领域(循环调度、权限沙箱、记忆、插件、hooks)只给一行入口 + 指针,细节不重讲。
>
> **两层结构**:§一–§十二 是**全量速查表**(一行一个,当索引);[§十三 高频命令详解](#十三高频命令详解约-34-个)把约 34 个日常高频、有门道的命令展开(用途 + 何时用 + 坑)。长尾平台/账户类只在速查表里,一行足够。

命令规则(T1):

- 只有消息**开头**的 `/` 才被识别为命令,后面的文字是参数。
- 打 `/` 看全部,`/` 加字母过滤。
- v2.1.199 起,skill 类命令可链式:`/skill-a /skill-b do XYZ`,最多 6 个,尾部文字作为参数传给每个。
- **不是每个命令对每个人都出现**——原文:"Availability depends on your platform, plan, and environment."(平台、套餐、环境不同,可见命令不同)

---

## 一、会话与上下文

| 命令 | 作用(T1) |
|------|----------|
| `/clear`(`/reset` `/new`) | 清空上下文开新对话,旧对话仍可 `/resume` |
| `/compact [instructions]` | 摘要压缩当前对话腾出上下文,可给聚焦指令 |
| `/context [all]` | 把上下文占用画成彩色网格,提示什么在吃窗口 |
| `/rewind`(`/checkpoint` `/undo`) | 把代码和/或对话回退到检查点,或从某条消息起做摘要 |
| `/branch [name]` | 在当前点分叉对话,试另一条路又不丢原对话 |
| `/fork <directive>` | 派一个继承完整对话的后台子代理去做某事,结果回流(v2.1.161+) |
| `/btw <question>` | 问个不进对话历史的旁支问题 |
| `/resume [session]`(`/continue`) | 按 ID/名字恢复会话或开选择器;后台会话标 `bg` |
| `/rename [name]` | 重命名会话并显示在 prompt 栏 |
| `/recap` | 生成当前会话的一行摘要 |
| `/export [file]` | 导出当前对话为纯文本 |
| `/copy [N]` | 复制第 N 新的回复(默认最后一条) |
| `/diff` | 交互式 diff 查看器:未提交改动 + 每轮 diff |
| `/exit`(`/quit`) | 退出 CLI;附着后台会话时是分离、会话继续 |

**[Author's analysis]** 这组价值全在「省上下文」。`/compact` 和 `/rewind` 是长会话两把刀:一把切摘要腾空间,一把回退到没被污染的检查点。`/branch`(你自己跳进副本)vs `/fork`(派后台替身、你继续)别搞混。

---

## 二、工作目录

| 命令 | 作用(T1) |
|------|----------|
| `/add-dir <path>` | 给当前会话加一个可访问的工作目录(注意:`.claude/` 配置不会从新目录发现) |
| `/cd <path>` | 把会话整体移到新目录,保留 prompt 缓存(新目录的 `CLAUDE.md` 追加为消息)(v2.1.169+) |

---

## 三、TUI 与外观

| 命令 | 作用(T1) |
|------|----------|
| `/tui [default\|fullscreen]` | 切换终端 UI 渲染器并带对话重启;`fullscreen` 启用无闪烁 alt-screen;无参打印当前渲染器 |
| `/config [key=value ...]`(`/settings`) | 打开设置界面;v2.1.181+ 可 `/config thinking=false`,v2.1.182+ `/config theme=dark`;`-p` 也可用 |
| `/theme` | 换配色(含 `auto`、色盲友好、ANSI、自定义) |
| `/focus` | 精简视图:只显你上条 prompt、一行工具摘要、最终回复(仅 fullscreen) |
| `/statusline` | 配置状态栏,可描述需求或从 shell prompt 自动生成 |
| `/status` | Status 标签:版本/模型/账户/连接(响应中也能开) |
| `/scroll-speed` | 调滚轮速度(仅 fullscreen) |
| `/color [color]` | 设 prompt 栏颜色 |
| `/keybindings` | 打开键位配置文件 |
| `/terminal-setup` | 配置 Shift+Enter 等终端键位(仅需要的终端:VS Code/Cursor/Zed 等) |
| `/ide` | 管理 IDE 集成、看状态 |

**[Author's analysis]** 你说的"`/tui` 设置"其实是这一族。`/tui fullscreen` + `/focus` 把终端变成干净屏幕;`/config model=sonnet` 一行改设置比进菜单快。

---

## 四、模型与推理

| 命令 | 作用(T1) |
|------|----------|
| `/model [model]` | 换模型并存为新会话默认;支持的模型可左右方向键调 effort |
| `/effort [level\|auto]` | 调推理力度:`low`…`max`、`ultracode`(`max`/`ultracode` 仅本会话) |
| `/advisor [model\|off]` | 开关顾问工具:关键节点咨询第二个模型(v2.1.98+) |
| `/fast [on\|off]` | 切换 fast mode |

---

## 五、记忆与项目初始化

| 命令 | 作用(T1) |
|------|----------|
| `/memory` | 编辑 `CLAUDE.md` 记忆文件、开关 **auto-memory**、查看 auto-memory 条目 |
| `/init` | 生成起步 `CLAUDE.md`;`CLAUDE_CODE_NEW_INIT=1` 走交互流程 |
| `/insights` | 分析会话,产出项目区域、交互模式、摩擦点报告 |

记忆的**机制层**(memory tool vs claude-mem、auto-memory 原理)见 [`MEMORY_VS_CLAUDE_MEM.md`](MEMORY_VS_CLAUDE_MEM.md)。

**[Author's analysis]** `/memory` 是命令入口,`MEMORY_VS_CLAUDE_MEM` 是原理——别混。

---

## 六、技能、子代理与并行

| 命令 | 作用(T1) |
|------|----------|
| `/skills` | 列出可用 skill;可过滤、按 token 排序、切换可见性(v2.1.121+) |
| `/agents` | v2.1.198+ 打印提示让你让 Claude 建/管子代理或直接编辑 `.claude/agents/`;更早是交互界面 |
| `/background [prompt]`(`/bg`) | 把当前会话转后台代理、释放终端;`claude agents` 监控 |
| `/tasks`(`/bashes`) | 看/管当前会话后台运行的一切 |
| `/stop` | 停掉当前后台会话(附着时才可用,保留 transcript 和 worktree) |
| `/batch <instruction>` | 跨库大改拆成 5–30 个独立单元,各在自己 worktree 里实现、跑测试、开 PR |
| `/goal [condition]` | 设目标,Claude 跨轮次持续做到条件满足 |
| `/loop [interval] [prompt]`(`/proactive`) | 按间隔或自定步调重复跑一个 prompt |
| `/schedule`(`/routines`) | 建/管云端定时 routine |
| `/workflows` | 打开 workflow 进度视图:看/暂停/恢复/保存 |
| `/reload-skills` | 重扫 skill/命令目录,免重启生效(v2.1.152+) |
| `/reload-plugins [--force]` | 重载插件应用改动 |
| `/plugin [subcommand]` | 管插件(`list`/`install`/`enable`/`disable`) |

`/goal` `/loop` `/schedule` 完整玩法(含 cron、`.claude/loop.md`)见 [`LOOPS_SCHEDULING_GUIDE.md`](LOOPS_SCHEDULING_GUIDE.md);`/batch`、动态编排见 [`WORKFLOW_ULTRACODE_GUIDE.md`](WORKFLOW_ULTRACODE_GUIDE.md);插件打包见 [`PLUGINS_GUIDE.md`](PLUGINS_GUIDE.md)。

---

## 七、审查、验证、计划与 bundled skills

| 命令 | 作用(T1) |
|------|----------|
| `/plan [description]` | 直接进 plan mode,可带任务 |
| `/code-review [level] [--fix] [--comment]` | 审当前 diff(正确性 + 复用/简化/效率);`ultra` 走云端深审 |
| `/simplify [target]` | 只做清理(复用/简化/效率/抽象层级),不查 bug,四 agent 并行 |
| `/review [PR]` | 对 GitHub PR 快速单趟只读审(v2.1.202 起) |
| `/security-review` | 审当前分支未提交改动的安全漏洞 |
| `/verify` | 真把 app 跑起来看改动是否生效 |
| `/run` | 启动并驱动你的 app 看改动效果(不只测试) |
| `/run-skill-generator` | 教 `/run` `/verify` 如何从干净环境构建/启动/驱动你的 app |
| `/fewer-permission-prompts` | 扫 transcript,给 `.claude/settings.json` 加只读允许清单减少权限弹窗 |
| `/claude-api [migrate\|managed-agents-onboard]` | 载入对应语言的 Claude API 参考;`migrate` 升级 API 代码到新模型 |
| `/dataviz [request]` | 图表/仪表盘设计指导(选型/配色/无障碍校验)(v2.1.198+) |
| `/deep-research <question>` | 扇出网络搜索、交叉核对、合成带引用的报告 |
| `/design-sync [hint]` | 把 repo 的 React 设计系统转换并上传到 Claude Design |
| `/design-login` | 为 `/design-sync` 授权设计系统访问 |
| `/ultraplan <prompt>` | 在 ultraplan 会话起草计划、浏览器审、远程执行或回传终端 |
| `/ultrareview [PR]` | 云端多 agent 深审(首选写法 `/code-review ultra`) |

审查方法论(请求/接收、两阶段)见 [`SUPERPOWERS_GUIDE.md`](SUPERPOWERS_GUIDE.md)。

---

## 八、协作、云端与远程

| 命令 | 作用(T1) |
|------|----------|
| `/team-onboarding` | 从**过去 30 天**的会话/命令/MCP 使用生成团队上手 markdown;Pro/Max/Team/Enterprise 还给可直接打开的分享链接 |
| `/powerup` | 带动画 demo 的交互小课,发现功能 |
| `/feedback [report]`(`/bug` `/share`) | 提交反馈/报 bug/分享对话 |
| `/install-github-app` | 装 Claude GitHub App,可选配 Actions |
| `/install-slack-app` | 装 Claude Slack app(走 OAuth) |
| `/autofix-pr [prompt]` | 起一个 web 会话盯当前分支 PR,CI 挂或有评论就推修复 |
| `/remote-control`(`/rc`) | 让本会话可从 claude.ai 远程控制 |
| `/teleport`(`/tp`) | 把 web 会话拉进本终端(取分支 + 对话) |
| `/web-setup` | 用本地 `gh` 凭据把 GitHub 连到 Claude Code on the web |
| `/remote-env` | 选云端 agent 的默认环境 |

**[Author's analysis]** `/team-onboarding` 是这波最"团队"的一个:把你踩熟的路径沉淀成新人一键复现的起点。它读 30 天历史,老项目上产出更有料。

---

## 九、权限、诊断与维护

| 命令 | 作用(T1) |
|------|----------|
| `/permissions`(`/allowed-tools`) | 管 allow/ask/deny 规则 |
| `/sandbox` | 切沙箱模式(仅支持平台) |
| `/hooks` | 看工具事件的 hook 配置 |
| `/mcp` | 管 MCP 连接与 OAuth |
| `/doctor` | 诊断安装与设置,`f` 让 Claude 修 |
| `/debug [desc]` | 开调试日志、读日志排查 |
| `/heapdump` | 写 JS 堆快照排查高内存 |
| `/release-notes` | 交互版本选择器看 changelog |
| `/help` | 显示帮助和可用命令 |

权限模式与沙箱见 [`PERMISSIONS_SANDBOX.md`](PERMISSIONS_SANDBOX.md);hooks 见 [`HOOKS_GUIDE.md`](HOOKS_GUIDE.md)。

---

## 十、账户、套餐与计费

| 命令 | 作用(T1) |
|------|----------|
| `/login` | 登入 Anthropic 账户 |
| `/logout` | 登出 Anthropic 账户 |
| `/usage`(`/cost` `/stats`) | 会话成本、套餐用量、活动统计;付费套餐含按 skill/subagent/plugin/MCP 拆分 |
| `/usage-credits` | 配置用量额度以在触顶后继续(原 `/extra-usage`) |
| `/upgrade` | 打开升级页换更高档 |
| `/passes` | 分享一周免费 Claude Code 给朋友(账户合格才可见) |
| `/privacy-settings` | 查看/改隐私设置(Pro/Max) |
| `/desktop`(`/app`) | 在 Claude Code 桌面 app 继续会话(mac/win + 订阅) |
| `/mobile`(`/ios` `/android`) | 显示下载移动 app 的二维码 |

---

## 十一、平台特定与杂项

| 命令 | 作用(T1) |
|------|----------|
| `/chrome` | 配置 Claude in Chrome 设置 |
| `/voice [hold\|tap\|off]` | 切换语音听写(需 claude.ai 账户) |
| `/radio` | 打开 Claude FM lo-fi 电台 |
| `/stickers` | 订 Claude Code 贴纸 |
| `/setup-bedrock` | 配置 Amazon Bedrock 认证(`CLAUDE_CODE_USE_BEDROCK=1` 时可见) |
| `/setup-vertex` | 配置 Google Vertex 认证(`CLAUDE_CODE_USE_VERTEX=1` 时可见) |

---

## 十二、已移除（别再教用户用）

| 命令 | 状态(T1) |
|------|----------|
| `/pr-comments` | v2.1.91 移除,改为直接让 Claude 看 PR 评论 |
| `/vim` | v2.1.92 移除,改用 `/config` → Editor mode |

---

## 十三、高频命令详解（约 34 个）

> §一–§十二 是全量速查(一行一个)。这一节把日常高频、且有真实门道的命令讲透:用途(T1)+ 何时用 / 坑(`[Author's analysis]`)。长尾平台/账户类不在此列。

### 上下文治理（长会话的命脉）

**`/compact [instructions]`** — 摘要压缩对话腾出上下文窗口(T1)。**[Author's analysis]** 上下文快满时的第一反应。可带指令聚焦("保留 auth 相关决策");但压缩是**有损**的,关键约束该落到 `CLAUDE.md` 或文件,别指望它记住。

**`/rewind`（`/checkpoint` `/undo`）** — 把**代码和/或对话**回退到某个检查点,或从选定消息起做摘要(T1)。**[Author's analysis]** 和 compact 是两把不同的刀:compact 往前压,rewind 往后退。改崩了、跑偏了,退回上一个干净点,比让模型"再试一次"省事。它能同时回退代码——有未保存工作时别乱退。

**`/context [all]`** — 把上下文占用画成彩色网格,标出什么在吃窗口、给优化建议(T1)。**[Author's analysis]** 会话变慢/变贵时先跑它,看是哪个大文件或工具输出在占坑,再决定 compact 还是清理。

**`/clear`（`/reset` `/new`）** — 清空上下文开新对话,旧的仍可 `/resume`(T1)。**[Author's analysis]** 换任务就 clear,别让上个任务的上下文污染下一个;想省空间又要接着聊,用 compact 而非 clear。

**`/branch [name]` vs `/fork <directive>`** — branch 在当前点分叉对话、你自己跳进副本(原对话保留,可 `/resume` 回去);fork(v2.1.161+)派一个继承完整对话的**后台子代理**去做某事、你继续,结果回流(T1)。**[Author's analysis]** 一句话:branch 是你换条路走,fork 是你派个分身、自己不动。探索性试错用 branch,甩独立子任务用 fork。

### 模型与推理

**`/model [model]`** — 换模型并存为新会话默认;有 prior output 时切换会让下次回复**不带缓存地重读全历史**,故要确认(T1)。**[Author's analysis]** 长会话中途换模型有缓存代价,不是免费的;按 `s` 只切当前会话不改默认。

**`/effort [level|auto]`** — 调推理力度 `low`…`max`、`ultracode`(`max`/`ultracode` 仅本会话);`ultracode` = `xhigh` 推理 + 自动 workflow 编排(T1)。**[Author's analysis]** 简单活压 low 省 token,硬骨头拉 high/max。

**`/advisor [model|off]`** — 开关顾问工具:关键节点咨询第二个模型(v2.1.98+)(T1)。**[Author's analysis]** 花额外 token 换高风险决策点的第二意见,不适合日常。

### 记忆与初始化

**`/memory`** — 编辑 `CLAUDE.md` 记忆文件、开关 auto-memory、看 auto-memory 条目(T1)。**[Author's analysis]** 只是命令入口;记忆机制原理见 [`MEMORY_VS_CLAUDE_MEM.md`](MEMORY_VS_CLAUDE_MEM.md)。

**`/init`** — 生成起步 `CLAUDE.md`;`CLAUDE_CODE_NEW_INIT=1` 走带 skills/hooks/个人记忆的交互流程(T1)。**[Author's analysis]** 进新仓库第一件事;生成后务必人工过一遍,别全信自动摘要。

### 终端形态

**`/tui [default|fullscreen]`** — 切终端 UI 渲染器并带对话重启;`fullscreen` 启用无闪烁 alt-screen(T1)。**[Author's analysis]** 终端刷屏/闪烁严重就上 fullscreen,配合 `/focus` 收噪音。

**`/config [key=value ...]`（`/settings`）** — 打开设置界面;v2.1.181+ 可 `/config thinking=false`,v2.1.182+ `/config theme=dark`;`-p` 非交互也可用(T1)。**[Author's analysis]** 能一行改设置后,脚本化/CI 里也能设,比进菜单快;`/config --help` 列全部可设键。

**`/focus`** — 精简视图:只显你上条 prompt、一行工具摘要、最终回复(仅 fullscreen)(T1)。**[Author's analysis]** 长工具链刷屏时用它把噪音收起来。

### 技能、子代理与并行

**`/skills`** — 列可用 skill,可过滤、按 token 排序、切可见性(v2.1.121+)(T1)。**[Author's analysis]** 不确定某能力是不是 skill、吃多少 token,先看这里。

**`/agents`** — v2.1.198+ 变成提示你让 Claude 建/管子代理或直接编辑 `.claude/agents/`;更早是交互界面(T1)。**[Author's analysis]** 语义变了:现在建子代理靠对话或直接编目录,不再是弹窗。

**`/background [prompt]`（`/bg`）** — 把当前会话转后台代理、释放终端,`claude agents` 监控(T1)。**[Author's analysis]** 长跑任务甩后台,腾出终端干别的。

**`/batch <instruction>`** — 跨库大改拆成 5–30 个独立单元,各在自己 worktree 里实现、跑测试、开 PR;需 git 仓库(T1)。**[Author's analysis]** 迁移/大规模重构利器,前提是任务真能切成独立单元。

**`/goal` · `/loop` · `/schedule`** — goal 设条件让 Claude 跨轮次做到达成;loop 按间隔或自定步调重复跑;schedule 建云端定时 routine(T1)。完整玩法见 [`LOOPS_SCHEDULING_GUIDE.md`](LOOPS_SCHEDULING_GUIDE.md)。**[Author's analysis]** goal=一个会话内盯到达成;loop=重复触发;schedule=离线定时。别混。

### 审查、验证与计划

**`/plan [description]`** — 直接进 plan mode,可带任务(T1)。**[Author's analysis]** 大改动前先 plan,把方案摆出来再动手。

**`/code-review · /simplify · /review`** — code-review 审当前 diff(正确性 + 复用/简化/效率,`ultra` 云端深审);simplify 只清理不查 bug、四 agent 并行;review 对 PR 快速单趟只读审(v2.1.202 起)(T1)。**[Author's analysis]** 分工:找 bug 用 code-review;只想收拾干净用 simplify;审别人 PR 用 review。方法论见 [`SUPERPOWERS_GUIDE.md`](SUPERPOWERS_GUIDE.md)。

**`/verify` 与 `/run`** — verify 把 app 真跑起来看改动是否生效(不只测试通过);run 启动并驱动你的 app(T1)。**[Author's analysis]** "测试绿 ≠ 真能用";改了有运行时表现的东西,verify 一下再报完成。

### 协作

**`/team-onboarding`** — 从过去 30 天会话/命令/MCP 使用生成团队上手 markdown;付费套餐还给可直接打开的分享链接(T1)。**[Author's analysis]** 老项目上产出更有料——历史越厚,沉淀越准。

### 权限与诊断

**`/permissions`（`/allowed-tools`）** — 管 allow/ask/deny 规则、工作目录、看最近 auto 模式拒绝(T1)。细节见 [`PERMISSIONS_SANDBOX.md`](PERMISSIONS_SANDBOX.md)。**[Author's analysis]** 权限弹窗烦,来这里批量放行只读命令(或用 `/fewer-permission-prompts` 自动生成)。

**`/mcp`** — 管 MCP 连接与 OAuth,可 `reconnect`/`enable`/`disable`(T1)。**[Author's analysis]** server 掉线先 `reconnect` 单个,别整个重启。

**`/doctor`** — 诊断安装与设置,按 `f` 让 Claude 修(T1)。**[Author's analysis]** 装完或出怪问题先跑它,再翻文档。

### 计费

**`/usage`（`/cost` `/stats`）** — 会话成本、套餐用量、活动统计;付费套餐含按 skill/subagent/plugin/MCP 拆分(T1)。**[Author's analysis]** 觉得烧太快,来这看是哪个 subagent/MCP 在吞额度。

### 会话恢复与查看

**`/resume [session]`（`/continue`）** — 按 ID/名字恢复或开选择器,后台会话标 `bg`(T1)。**`/diff`** — 交互式 diff 查看器:未提交改动 + 每轮 diff,v2.1.198+ 外部 git 变化会自动刷新(T1)。**[Author's analysis]** resume 找回昨天的会话;diff 看这轮到底改了啥,比翻聊天记录快。

---

## 2026 年值得注意的新命令

**[Author's analysis]** 挑几个近期加入、改变操作习惯的:

- `/tui` `/focus`(fullscreen 渲染族)——终端体验整体升级
- `/team-onboarding`(2026-04,Week 15 引入)——团队知识一键沉淀
- `/config key=value`(v2.1.181+)——设置可脚本化,`-p` 也能用
- `/agents` 语义改版(v2.1.198,从交互界面改为提示直接编辑 `.claude/agents/`)
- `/rewind` 检查点 · `/fork` 后台分叉 · `/cd` 迁移会话——长任务的容错与灵活
- `/batch` · `/ultraplan` · `/ultrareview`——跨库并行与云端重活

命令可用性随平台、套餐、版本变化;引入时点来自官方 changelog,描述来自官方 commands 参考。

---

## 参考

- [Claude Code — Commands reference](https://code.claude.com/docs/en/commands)（T1,99 个命令全量逐条说明,本篇一切命令描述的来源）
- [Claude Code — Changelog](https://code.claude.com/docs/en/changelog)（T1,命令引入/移除时点）
- 本仓库相关专篇:[LOOPS_SCHEDULING_GUIDE](LOOPS_SCHEDULING_GUIDE.md) · [PERMISSIONS_SANDBOX](PERMISSIONS_SANDBOX.md) · [MEMORY_VS_CLAUDE_MEM](MEMORY_VS_CLAUDE_MEM.md) · [HOOKS_GUIDE](HOOKS_GUIDE.md) · [PLUGINS_GUIDE](PLUGINS_GUIDE.md) · [SUPERPOWERS_GUIDE](SUPERPOWERS_GUIDE.md) · [WORKFLOW_ULTRACODE_GUIDE](WORKFLOW_ULTRACODE_GUIDE.md)
