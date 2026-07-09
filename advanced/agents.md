# Agents

## Sub-agent 的本质

`T1` Claude Code 官方把 subagent 定义为 specialized AI assistant。每个 subagent 都有：

- 独立上下文窗口
- 自己的 system prompt
- 可单独限制的工具权限
- 独立权限和配置

Claude 会根据用户任务描述、subagent 的 `description` 字段和当前上下文自动决定是否委派任务。[Anthropic subagents docs](https://code.claude.com/docs/en/sub-agents)

**[Tutorial perspective]** Sub-agent 的本质不是“再开一个聊天窗口”。它是上下文隔离器 + 专用执行器。主线程负责目标和协调。Sub-agent 负责把脏活、重活、窄任务吞下去，再只返回结果。

这东西值钱的地方有三个：

- 防止主上下文被搜索结果、工具调用和中间废话污染
- 给不同任务装不同权限和不同 prompt
- 把复杂流程拆成稳定的专业工种

## 怎么创建自己的 subagent

`T1` 官方推荐直接用 `/agents` 创建和管理 subagents，也支持手工写 Markdown 文件。[Anthropic subagents docs](https://code.claude.com/docs/en/sub-agents)

项目级目录：

```text
.claude/agents/
```

用户级目录：

```text
~/.claude/agents/
```

优先级上，项目级高于用户级。[Anthropic subagents docs](https://code.claude.com/docs/en/sub-agents)

## 最小文件格式

`T1` 官方说明 subagent 是 Markdown + YAML frontmatter。至少需要：

- `name`
- `description`

常用可选字段包括：

- `tools`
- `disallowedTools`
- `model`
- `skills`
- `memory`
- `hooks`
- `background`

来源：[Anthropic subagents docs](https://code.claude.com/docs/en/sub-agents)

最小示例：

```md
---
name: code-reviewer
description: Review code quality after modifications. Use proactively after code changes.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a focused code review specialist.
```

## 为什么 description 很关键

`T1` 官方写得很明白：Claude uses each subagent’s description to decide when to delegate tasks。[Anthropic subagents docs](https://code.claude.com/docs/en/sub-agents)

所以 `description` 不是简介。它是路由规则。

烂写法：

```text
A helpful assistant
```

这种 description 几乎等于没写。

好写法：

```text
Analyze repository business logic, map controllers to services and repositories, and update business markdown files. Use proactively when code changes affect domain behavior.
```

这才像能触发自动委派的描述。

## tools 怎么配

`T1` 默认情况下，subagent 继承主会话的全部工具。要收紧权限，就用 `tools` 做 allowlist，或用 `disallowedTools` 做 denylist。[Anthropic subagents docs](https://code.claude.com/docs/en/sub-agents)

经验规则：

- 只读分析 agent：`Read, Grep, Glob, Bash`
- 文档同步 agent：再加 `Edit, Write`
- 高风险 agent：尽量别继承所有工具

权限不是装饰。权限是保险丝。

## skills 怎么和 subagent 组合

`T1` 官方支持 `skills` 字段，可以在 subagent 启动时预加载 skill 内容。[Anthropic subagents docs](https://code.claude.com/docs/en/sub-agents)

这就是你前面那套 `business-logic` 结构真正发力的地方。

例如：

```md
---
name: business-logic-researcher
description: Analyze and sync domain-specific business logic markdown from code changes. Use proactively for business-flow questions and business-logic sync tasks.
tools: Read, Grep, Glob, Bash, Edit, Write
skills:
  - business-logic
model: sonnet
memory: project
---
```

这样 subagent 一启动，就不是从零开始猜这个项目的业务结构，而是先带着 `business-logic` skill 的路由和知识结构进去。

## subagent 适合做什么

官方和工程经验都指向同一个方向：focused subagents。[Anthropic subagents docs](https://code.claude.com/docs/en/sub-agents)

适合：

- 代码审查
- 调试定位
- 业务逻辑同步
- 文档提炼
- 只读探索
- 测试执行与失败分析

不适合：

- 把所有事情塞进一个万能 agent
- 让一个 subagent 既做规划又做实现又做发布
- 给所有 subagent 都开满权限

## 一个项目级示例

这个仓库已经加了一个项目级示例：

- [business-logic-researcher.md](../.claude/agents/business-logic-researcher.md)

它演示了三件事：

- subagent 放到 `.claude/agents/`
- 通过 `skills: business-logic` 预加载 skill
- 让 agent 专注做业务逻辑同步，而不是包打天下

## LangChain 还是 LangGraph

`T1` LangGraph 官方把自己定义成低层 orchestration framework，强调 durable execution、human-in-the-loop、memory 和 stateful workflow。[LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)

`T1` LangGraph 官方同时写明：如果你只是想更快开始，用 LangChain agents；LangChain 的 agent abstractions built on top of LangGraph。[LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)

工程判断很简单：

- FAQ 型、轻工具调用客服：先用 LangChain 高层 agent
- 多阶段、多状态、要审批、要持久化、要人工接管：直接上 LangGraph

## 从源码看 LangChain 的 agent 入口

我直接看了 `langchain` 源码，不靠转述。

在 `langchain_v1/langchain/agents/factory.py` 里，`create_agent(...)` 的签名直接暴露了这些能力：

- `checkpointer`
- `store`
- `interrupt_before`
- `interrupt_after`
- `cache`
- `system_prompt`
- `middleware`

这说明一件事。LangChain 的高层 agent 不是只有“模型 + 工具”两件事。它已经把状态持久化、中断点、缓存和中间件暴露出来了。只是很多教程还停留在 hello world。

## 从源码看 LangChain 的 RAG 形状

我也直接看了 `langchain_classic/chains/retrieval.py` 和 `combine_documents/stuff.py`。

源码很直接：

- `create_retrieval_chain(...)` 会把检索结果放进 `context`
- `create_stuff_documents_chain(...)` 要求 prompt 必须包含 `context`
- 源码示例里，`context` 经常被直接插进 system prompt

这就是前面 `token.md` 里那条判断的源码依据。问题不在“你用了 LangChain”。问题在“你把动态 context 塞到了 prompt 的哪个位置”。

## 怎么用 LangChain 或 LangGraph + LangChain 做智能客服

### 方案 1：LangChain 快速起一个客服 agent

适合：

- FAQ
- 工单查询
- 知识库问答
- 简单退款说明或流程答疑

做法：

1. 用 LangChain 绑定模型和工具
2. 接上检索或数据库查询工具
3. 用单 agent 处理问答
4. 用 LangSmith 做 tracing 和评估

短平快。上线也快。坏处也明显：流程一复杂，就开始缠。

一个现实判断：

- 如果客服只做 FAQ、订单查询、知识库问答，LangChain `create_agent` 足够快
- 如果客服开始碰退款、审批、人工确认、敏感动作，中断和状态马上会变成刚需

### 方案 2：LangGraph + LangChain 做真正能落地的客服

`T1` LangChain 官方的 handoffs 文档明确说，customer support 很适合 handoffs pattern：通过工具更新状态变量，让系统在不同状态或 agent 之间切换。[LangChain handoffs docs](https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs)

`T1` LangGraph 官方有完整 customer support bot 教程，展示了多状态、工具调用、checkpointer、interrupts 和敏感操作前人工确认的模式。[LangGraph customer support tutorial](https://langchain-ai.github.io/langgraph/tutorials/customer-support/customer-support/)

我也直接拉了 `langgraph` 仓库本地源码（git submodule，刚 clone 的仓库需先 `git submodule update --init`，否则是空目录）。官方示例文件在：

```text
advanced/vendor/langgraph/examples/customer-support/customer-support.ipynb
```

这不是纸上谈兵。初始化 submodule 之后，仓库里就有完整样例。

推荐架构：

1. 一个主协调 agent
2. 若干 specialist agents
3. 显式 state
4. checkpointer
5. human-in-the-loop interrupt
6. LangSmith tracing

典型 specialist：

- `faq-agent`
- `refund-agent`
- `order-status-agent`
- `account-agent`
- `escalation-agent`

典型 state：

- `active_agent`
- `customer_id`
- `ticket_type`
- `order_id`
- `refund_eligibility`
- `approval_required`

典型流程：

1. 主 agent 判断意图
2. handoff 到退款/订单/账户 specialist
3. specialist 补齐缺失字段
4. 命中高风险动作时中断，请人工确认
5. 执行工具调用
6. 记录轨迹和评估结果

## 一个冷判断

**[Author's analysis]** 很多所谓“智能客服 agent”其实只是一个套了知识库的问答机器人。只要它不处理状态、不处理审批、不处理失败恢复、不处理人工接管，它就不算成熟客服系统。那只是个会说话的搜索框。

真要进生产，LangGraph 那种状态机味道会越来越重。不是因为它高级。是因为真实客服流程本来就脏。
