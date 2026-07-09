# Claude Code Advanced

添加官方的插件市场，并且安装 examples 内容，这里有 skill-creator 以及所有高级内容处理

```
/plugin marketplace add anthropics/claude-code
```

> 本目录部分文档（[langchain-rag.md](langchain-rag.md)、[agents.md](agents.md)）直接引用 `advanced/vendor/` 下的第三方源码。那是三个 git submodule（langchain、langgraph、WeKnora），刚 clone 的仓库里是空目录，源码链接会 404。先执行：
>
> ```
> git submodule update --init
> ```

**[Tutorial perspective]** 这一套用法的目标不是“让 Claude 更聪明”，而是砍掉重复探索。每次都开 Explore Agent 扫全仓库，像让人每天重新背一次地图。浪费上下文。也浪费时间。

## 导航

- [Skill 高级用法](skill.md)
- [Command 高级用法](command.md)
- [Agents 与 Sub-agents](agents.md)
- [Token 与缓存](token.md)
- [LangChain 与 RAG](langchain-rag.md)
- [Worktree 与并行开发](WORKTREE_PARALLEL_GUIDE.md)
- [Workflow 与 ultracode](WORKFLOW_ULTRACODE_GUIDE.md)
- [Loop 与调度全指南](LOOPS_SCHEDULING_GUIDE.md)
- [Headless CLI 与 CI 集成](HEADLESS_CLI_GUIDE.md)
- [权限与沙箱](PERMISSIONS_SANDBOX.md)
- [Hooks 完全参考](HOOKS_GUIDE.md)
- [Agent 协作系统总览](CLAUDE_CODE_AGENT_GUIDE.md)
- [Agent Teams 完全指南](AGENT_TEAMS_COMPLETE_GUIDE.md)
- [Superpowers 插件详解](SUPERPOWERS_GUIDE.md)
- [Plugins 打包与分发](PLUGINS_GUIDE.md)
- [扩展机制全景](EXTENSIONS_OVERVIEW.md)
- [记忆机制：原生 vs claude-mem](MEMORY_VS_CLAUDE_MEM.md)
- [订阅计划价格对照](PLANS_PRICING.md)

## 核心思路

把业务理解沉淀到项目内的 Skill。Skill 不只是一段提示词。它还可以绑定一套路由协议、一套固定目录、一套更新流程、一套命令入口。

推荐结构：

```text
.claude/
└── skills/
    └── business-logic/
        ├── SKILL.md
        ├── change-log.md
        ├── shared/
        │   └── cross-cutting.md
        └── team/
            ├── overview.md
            ├── join-team.md
            └── leave-team.md
```

这套结构解决三个问题：

1. `SKILL.md` 只做元信息和调度，不污染具体业务内容。
2. 业务逻辑按目录拆开，命中哪个业务就只加载哪个业务。
3. 最近代码变更可以增量同步，不必每次全量扫描。
4. 新会话先拿业务骨架，再决定是否回到代码深挖。

这不是把 Markdown 当笔记本。是把 Markdown 当业务索引层。加载 `order cancel-order` 时，Claude 应该能立刻看到：

- 关键代码在哪些文件哪几行
- 请求字段是什么
- 前置校验是什么
- 调用了哪些 service、repository、事件
- 需求为什么这样设计
- 改这个逻辑可能炸哪里

## `business-logic` Skill 的定位

这个 Skill 不是 RAG 替身。它更像项目内建的业务索引层。

**[Tutorial perspective]** RAG 解决“召回文档”的问题。这个 Skill 解决“把项目业务理解写成结构化工程资产”的问题。两者能共存，但后者更适合团队内部的持续维护。

Skill 应该维护这些内容：

- 业务目录：例如 `team/`、`order/`、`billing/`。
- 业务总览：放在各自目录的 `overview.md`。
- 业务动作：例如 `leave-team.md`、`join-team.md`。
- 交叉逻辑：多个业务共用的权限、事件、审计、状态机，集中放共享目录。
- 变更记录：最近一次同步覆盖了哪些文件，推断更新了哪些业务规则。
- 待确认项：代码里看得见流程，看不见产品规则的地方必须显式标注。
- 关键代码引用：尽量记录文件路径和行号。
- 时序图：复杂流程直接给 Mermaid。
- 需求背景：写清业务为何存在，不要只记实现细节。

## 命令设计

### `business-logic init`

用途：首次建立业务索引。

执行原则：

1. 自动拆出多个 Agent。
2. 每个 Agent 只负责一块内容，不准互相踩上下文。
3. 汇总时输出统一格式，落到对应业务目录。

推荐的 Agent 分工：

- Agent A：扫描入口层。控制器、路由、HTTP handler、RPC service。
- Agent B：扫描应用层。use case、service、command handler、orchestrator。
- Agent C：扫描领域层。实体、聚合、领域服务、规则判断。
- Agent D：扫描基础设施层。repository、DAO、事件发布、外部 API。
- Agent E：扫描测试与文档。测试命名、fixture、注释、ADR、接口文档。

输出结果至少包括：

- `<domain>/overview.md`
- `<domain>/*.md`
- `shared/cross-cutting.md`
- `change-log.md` 的初始条目

### `business-logic sync`

用途：同步最近一次代码改动，不重建全量索引。

执行原则：

1. 只看最近变更。优先 `git diff`、`git status`、最近提交。
2. 先判断受影响的业务域，再更新对应业务目录。
3. 更新 `change-log.md`，记录这次同步基于哪些文件和哪些判断。

适用场景：

- 刚合并一个功能分支。
- 刚重构 service 或 repository。
- 新增一个业务接口，但不想重新扫描整个仓库。

### `business-logic last 3`

用途：同步最近三次提交，而不是只盯着最后一次。

这个命令适合两种情况：

- 一个功能拆成多次 commit，最后一次提交本身看不出全貌。
- 你刚拉下来别人一串提交，想快速知道这几次改动一共碰了哪些业务规则。

执行原则：

1. 先列出最近 `N` 次提交。
2. `last 3` 默认用 `git diff HEAD~2..HEAD`，也就是当前 `HEAD` 加上前两个提交。
3. 合并分析这段提交范围内的文件变化。
4. 按业务域回写，而不是按 commit 逐条碎片化记录。
5. 在 `change-log.md` 里保留提交范围，避免后续追溯断链。

### `business-logic order`

用途：只加载订单业务总览。

### `business-logic order cancel-order`

用途：只加载订单取消这个动作相关的业务文档。

这才是整套结构的关键。不是先把整个 skill 吞进去，再让模型自己找。是先用参数把范围缩到一个业务域，甚至一个动作，再加载对应文档。

## Skill 与 Command

`Command` 更轻。通常就是一段强提示词，加上一套固定执行步骤。它适合把一次性工作流钉死，例如 `/commit-push`。像 `business-logic` 这种需要长期维护领域知识的入口，不应该再复制一层 command 定义。

`Skill` 更重。它不只是提示词。它还能挂载目录、路由规则、脚本、参考资料、共享知识和增量同步机制。它适合长期复用的领域能力。

**[Tutorial perspective]** 可以把 `Command` 看成前锋，把 `Skill` 看成仓库内建的长期记忆层。前者帮你起手。后者帮你别失忆。对 `business-logic` 这种场景，直接让 skill 自己承担入口协议更干净。

## 业务分层写法

以“团队业务”为例，不要只写接口清单。那种东西像尸检报告。没有结构，没有因果。

`team/overview.md` 应该写清楚：

- 业务摘要
- 需求背景
- 业务目标：为什么存在加入团队、离开团队、踢出团队、邀请成员。
- 关键代码：核心入口、service、repository，尽量带路径和行号。
- 入口接口：哪个 controller 或 route 接收请求。
- 应用编排：哪个 service 负责事务边界和权限校验。
- 领域规则：成员上限、角色限制、重复加入、团队状态限制。
- 持久化与集成：数据落库在哪里，是否触发消息、审计、通知。
- 核心时序：复杂流程用 Mermaid 画出来。
- 风险点：并发、幂等、权限绕过、缓存一致性。

`team/leave-team.md` 应该写清楚：

- 动作摘要
- 需求背景
- 退出团队要做什么前置检查。
- 入口接口和请求字段是什么。
- 关键代码路径和关键行号是什么。
- 会调用哪些 service、repository、外部通知。
- 是否涉及最后一个管理员、团队所有者、审计日志。
- 时序图是什么。
- 失败条件和状态变化是什么。

## 推荐工作流

1. 在项目根目录创建 `.claude/skills/business-logic/`
2. 按业务域建立目录，例如 `team/`、`order/`
3. 先运行 `business-logic init`
4. 初始化完成后，人工快速检查一次业务域命名是否准确
5. 小改动后运行 `business-logic sync`
6. 多个 commit 合并理解时运行 `business-logic last 3`
7. 开新会话时，先让 Claude 读取 `SKILL.md`，再按参数加载命中的业务目录和动作文件

## 这套方案的边界

**[Author's analysis]** 它不会自动保证正确。错的总结，积累十次，只会变成更稳的错。所以 `sync` 必须绑定到代码变更，不能只靠会话记忆。

它也不适合替代这些东西：

- 架构决策记录
- 正式产品需求文档
- 面向外部的 API 文档
- 数据字典

它最适合做的，是让 Claude 在进入任务前先拿到“业务骨架”。

## 安全告警

`T1` OpenClaw 官方文档明确要求把第三方 skills 当成不受信任代码处理，并建议在不受信任输入和高风险工具场景下优先使用沙箱。[Skills docs](https://docs.openclaw.ai/skills) [Security docs](https://docs.openclaw.ai/gateway/security)

`T1` OpenClaw 官方的 ClawHub 文档说明该市场是默认开放上传的，只依赖 GitHub 账号年龄、举报和隐藏机制做一部分治理。这不是强审计，也不是强签名。[ClawHub docs](https://docs.openclaw.ai/tools/clawhub)

`T3` 公开安全报告已经把 OpenClaw 技能市场描述为现实攻击面，而不是理论风险。公开研究和报道提到恶意 skills、凭据窃取和恶意载荷投递。[Snyk report summary](https://snyk.io/articles/clawdhub-malicious-campaign-ai-agent-skills/) [TechRadar report](https://www.techradar.com/pro/security/openclaw-ai-agents-targeted-by-infostealer-malware-for-the-first-time)

**[Author's analysis]** 结论很简单。不要把公共 Skill Marketplace 当 npm 镜像站那样随手装。装错一个 skill，最坏结果不是“回答变差”，而是凭据泄露、命令执行、机器被接管。AI agent 一旦带文件、网络、终端权限，恶意 skill 就不再是普通插件。它更像一段披着说明文档外衣的入侵脚本。

## 相关文件

- [business-logic skill](../.claude/skills/business-logic/SKILL.md)
- [advanced skill guide](skill.md)
- [advanced command guide](command.md)
