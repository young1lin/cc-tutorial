# Claude Code 扩展机制全景

> 八个扩展点，决定 Claude 知道什么、连什么、自动做什么。选错扩展点 = 烧 context 或堵不住漏洞。

来源：官方 [Extend Claude Code (features-overview)](https://code.claude.com/docs/en/features-overview)（T1）、[Common workflows](https://docs.claude.com/en/docs/claude-code/common-workflows)（T1）。

---

## 一、扩展层全景

Claude Code = 会推理的模型 + 内置工具（文件操作、搜索、执行、web）。内置工具覆盖大部分编码任务。**扩展层是你加上去定制的东西**——让 Claude 知道项目约定、连外部服务、自动化流程（T1）。

八个扩展点（T1）：

| 扩展 | 作用 | 加载时机 | context 成本 |
|------|------|----------|--------------|
| **CLAUDE.md** | 每会话加载的持久上下文 | 会话启动 | 高——全量，每个请求 |
| **Skills** | 可复用知识 + 可调用工作流 | 启动时描述，用时全文 | 低——描述每次，全文仅用时 |
| **Code intelligence** | LSP 符号导航 + 实时类型错误 | 编辑后 + 按需 | 低——替代全文读，净降 |
| **MCP** | 连外部服务/工具 | 启动时工具名，用时 schema | 低——用时才展开 |
| **Subagents** | 隔离 context 跑自己的循环 | 派出时 | 隔离——不占主 context |
| **Agent teams** | 多个独立会话协调 | 派出时 | 高——每个 teammate 独立实例 |
| **Hooks** | 生命周期事件触发脚本/HTTP/prompt/subagent | 事件触发 | 零——除非返回输出 |
| **Artifacts** | 会话输出发布成私有交互网页 | 手动 | N/A |
| **Plugins** | 打包上述一切分发 | 安装时 | 取决于内含物 |

记住这张表的「加载时机」和「context 成本」列——它是所有架构决策的依据。

---

## 二、核心辨析（官方，T1）

### Skill vs Subagent

| | Skill | Subagent |
|---|---|---|
| 是什么 | 可复用内容，加载进任意 context | 隔离 worker，自带 context |
| 关键收益 | 跨 context 共享内容 | context 隔离，只回摘要 |
| context 影响 | 加进主窗口 | 独立窗口，自带 input/output token |
| 适合 | 参考资料、可调用工作流 | 读很多文件的活、并行、专门 worker |

**[Author's analysis]** 一句话区分：Skill 是「知识」，Subagent 是「工人」。知识进主 context，工人在外面干活只汇报。

### CLAUDE.md vs Skill

| | CLAUDE.md | Skill |
|---|---|---|
| 加载 | 每会话自动 | 按需 |
| 能触发工作流 | 否 | 是（`/<name>`）|
| 适合 | 「永远要做 X」 | 参考资料、可调用工作流 |

**官方铁律（T1）**：Keep CLAUDE.md under 200 lines. 超了就移参考资料到 skills，或拆成 `.claude/rules/`。

### CLAUDE.md vs Rules vs Skills（三层都存指令）

| | CLAUDE.md | `.claude/rules/` | Skill |
|---|---|---|---|
| 加载 | 每会话 | 每会话，**或打开匹配文件时** | 按需 |
| 范围 | 全项目 | 可限定文件路径 | 任务级 |

`.claude/rules/` 带 `paths` frontmatter，只在 Claude 碰匹配文件时加载——**省 context**。语言专属或目录专属的约定放这里，别堆进 CLAUDE.md。

### Subagent vs Agent team

| | Subagent | Agent team |
|---|---|---|
| context | 自有窗口，结果回调用者 | 自有窗口，完全独立 |
| 通信 | 只回主 agent | teammate 之间直接互发消息 |
| 协调 | 主 agent 管一切 | 共享任务列表，自协调 |
| token | 低（摘要回主 context） | 高（每个 teammate 独立实例） |

**转折点（T1）**：并行 subagent 撞 context 上限，或 subagent 之间需要互相通信 → 上 agent team。详见 [AGENT_TEAMS_COMPLETE_GUIDE](AGENT_TEAMS_COMPLETE_GUIDE.md)。

### MCP vs Skill

| | MCP | Skill |
|---|---|---|
| 是什么 | 连外部服务的协议 | 知识、工作流、参考 |
| 提供 | 工具和数据访问 | 怎么用好那些工具 |

**黄金组合（T1）**：MCP 给连接（连接和鉴权由 server 管），Skill 教用法。例：MCP 连数据库，Skill 文档化 schema 和查询模式，加 `/post-to-slack` 工作流定义消息格式。

**[Author's analysis]** 想搞懂 MCP 协议本身——host/client/server 三角色、JSON-RPC 2.0 over stdio、`initialize` → `tools/list` → `tools/call` 握手、从零写 server 和 client——可看本教程作者的配套项目 [minimal-mcp](https://github.com/young1lin/minimal-mcp)：手把手 README（从 LLM 本质、ReAct 一路写到多轮工具循环和真实 server 集成），Python 实现，另有 Java / Go / Streamable HTTP 版本。Claude Code 只是 MCP 的一个 host，协议吃透了，任何 host 上的配置都是细节。

### Hook vs Skill（最重要的一条）

| | Hook | Skill |
|---|---|---|
| 跑什么 | shell 命令/HTTP/LLM prompt/subagent | Claude 读取并遵循的指令 |
| 触发 | 生命周期事件（PostToolUse、SessionStart 等） | 你打 `/<name>` 或 Claude 匹配 description |
| 确定性 | **事件必触发，保证** | Claude 解读指令，结果可变 |
| context 成本 | 零（除非返回输出） | 描述每次，全文用时 |

**官方核心洞察（T1 原文）**：

> Put guardrails in hooks. An instruction like "never edit `.env`" in CLAUDE.md or a skill is a request, not a guarantee. A `PreToolUse` hook that blocks the edit is enforcement. **If a rule must hold every time, make it a hook rather than a prompt instruction.**

CLAUDE.md / Skill 里写「别碰 .env」是**请求**——Claude 大概率听话，不保证。`PreToolUse` hook 拦截是**执行**。强制规则 → hook。[Loop 与调度全指南](LOOPS_SCHEDULING_GUIDE.md)里的 Ralph Loop 就是这条原理的极致：用 Stop hook 强制 Claude 自主循环。事件清单、matcher 语法、输入输出协议见 [Hooks 完全参考](HOOKS_GUIDE.md)。

---

## 三、上下文成本决定架构

官方警告（T1 原文）：

> Every feature you add consumes some of Claude's context. Too much can fill up your context window, but it can also add noise that makes Claude less effective; skills may not trigger correctly, or Claude may lose track of your conventions.

context 成本排序（T1）：CLAUDE.md（全量每次）> Skills（描述每次 + 全文用时）> MCP（工具名 + 用时 schema）> Hooks（零）> Subagents（隔离）。

**架构含义**：

- **always-on 要克制**。CLAUDE.md 是最贵的，<200 行，超了拆 rules/skills。
- **能 on-demand 就别 always-on**。参考资料进 Skill，不进 CLAUDE.md。
- **副任务隔离**。读很多文件的活走 Subagent，别污染主 context。
- **强制零成本**。规则用 Hook，不占 context 还保证执行。

**省成本技巧（T1）**：Skill 设 `disable-model-invocation: true`，对 Claude 完全不可见，直到你手动调——context 成本归零。只手动触发的 skill 都该这么设。

---

## 四、渐进式构建（别一上来全配，T1）

每个扩展点都有「 recognizable trigger」。按触发增量加，不要预先配置：

| 触发 | 加什么 |
|------|--------|
| Claude 同一个 convention 错两次 | 写进 CLAUDE.md |
| 反复敲同一个 prompt 起任务 | 存成 user-invocable skill |
| 反复贴同一个 playbook（第三次） | 做成 skill |
| 反复从浏览器拷数据给 Claude | 接 MCP |
| Claude 读一堆文件找符号定义 | 装 code intelligence |
| 副任务输出淹没对话 | 走 subagent |
| 想某事每次自动发生 | 写 hook |
| 第二个仓库要同样配置 | 打包成 plugin（[怎么打](PLUGINS_GUIDE.md)） |

**[Author's analysis]** 同样的触发也告诉你何时**更新**现有的：同一个错误反复出现 = CLAUDE.md 该编辑，不是聊天里再纠正一次；一个工作流反复手调 = 该再修一次 skill。

---

## 五、组合模式（T1）

真实配置都是组合，每个扩展干自己最擅长的：

| 模式 | 怎么协作 | 例子 |
|------|----------|------|
| **Skill + MCP** | MCP 给连接，Skill 教用法 | MCP 连数据库，Skill 文档化 schema 和查询模式 |
| **Skill + Subagent** | Skill 派 subagent 并行干活 | `/audit` 派 security / performance / style 三个 subagent |
| **CLAUDE.md + Skills** | CLAUDE.md 持 always-on 规则，Skill 装按需参考 | CLAUDE.md 说「遵循 API 约定」，Skill 装完整 API style guide |
| **Hook + MCP** | Hook 通过 MCP 触发外部动作 | 编辑后 hook 改关键文件时发 Slack |

典型一天：CLAUDE.md 装项目约定，Skill 装部署工作流，MCP 连数据库，Hook 编辑后跑 lint。各司其职。

---

## 六、给教程的判断

**[Tutorial perspective]** 选扩展点的三条原则，记住就够了：

1. **强制规则用 Hook，不用 CLAUDE.md**。请求 vs 执行。
2. **能 on-demand 就别 always-on**。context 是稀缺资源。
3. **副任务隔离走 Subagent**。主 context 留给推理。

和本仓库其他文档的关系：[advanced/README.md](README.md) 的 business-logic skill 是 **Skill** 的深度用法；[SUPERPOWERS_GUIDE](SUPERPOWERS_GUIDE.md) 的 superpowers 是 **Plugin**（打包与分发见 [PLUGINS_GUIDE](PLUGINS_GUIDE.md)）；[LOOPS_SCHEDULING_GUIDE](LOOPS_SCHEDULING_GUIDE.md) 的 Ralph Loop 是 **Hook** 的极致。这篇全景是它们的地图——先看地图，再钻细节。

---

## 参考（T1，官方文档）

- [Extend Claude Code (features-overview)](https://code.claude.com/docs/en/features-overview) — 八扩展全景、辨析、context 成本、渐进构建、组合模式
- [Common workflows](https://docs.claude.com/en/docs/claude-code/common-workflows) — Plan mode、subagent、worktree、headless、slash command 工作流
- [How Anthropic Teams Use Claude Code (官方内部 PDF, T2)](https://www-cdn.anthropic.com/58284b19e702b49db9302d5b6f135ad8871e7658.pdf) — 敏感数据走 MCP 而非 CLI
