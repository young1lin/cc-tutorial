# 第七层：注意事项

# AI 能力边界

AI 辅助编程不是万能的，清楚它的能力边界，才能用好它。

## 能做到什么？

**[Tutorial perspective]** 在深度介入的情况下，可以构建大型系统（例如 8 万行代码的 IM 系统，使用 Opus 4.6 做规划，GLM 负责执行和测试）。但注意关键词：**深度介入**——不是丢一句话就跑，而是全程做架构决策、拆分任务、审查代码、处理 AI 搞不定的边界情况。

**实际能力范围：**

| 能力级别 | 具体表现 | 条件 |
|---------|---------|------|
| **很强** | 单文件功能实现、CRUD、单元测试编写、代码重构、文档生成 | Sonnet 就够 |
| **强** | 多文件协作、API 设计、前端组件开发、Bug 定位与修复 | Opus + Plan Mode |
| **可以但需要人盯着** | 跨模块架构重构、数据库迁移、CI/CD 配置 | Opus + 拆分子任务 + 频繁提交 |
| **勉强** | 复杂并发问题、性能调优、分布式系统设计 | 需要你自己有专业知识引导 |
| **做不到** | 需求分析、产品决策、真正的创新性架构设计 | 这些是人的工作 |

## 典型翻车场景

1. **长对话漂移**：对话超过 50 轮后，Claude 开始"忘记"早期的约定，重复引入已经被否决的方案。解法：频繁 `/clear`，把关键决策写进 CLAUDE.md
2. **自信地写出错误代码**：LLM 不知道自己不知道什么。它不会说"我不确定"，而是自信地给你一段看起来合理但有隐藏 Bug 的代码。解法：永远跑测试，不要目视审查就合并
3. **过度工程化**：让 Claude 写一个简单功能，它可能给你搞出设计模式全家桶。解法：在 CLAUDE.md 或 prompt 里明确要求"保持简单，不要过度设计"
4. **框架版本混淆**：Claude 的训练数据有截止日期，可能混淆框架的新旧 API。解法：在 CLAUDE.md 里写明框架版本，用 WebSearch/WebFetch 补充最新文档

## Playwright 网页自动化测试 + Claude Code

前端开发的杀手级组合。流程是这样的：

```
1. Figma MCP 获取设计稿信息
2. Claude 根据设计稿编写前端代码
3. Playwright 插件自动打开浏览器、截图
4. 截图自动传回 Claude 对话
5. Claude 对比设计稿和实际截图，发现差异
6. Claude 修正代码
7. 重复 3-6 直到满意
```

这形成了一个**完整的前端开发闭环**——设计 → 编码 → 验证 → 修正，全程不需要你手动打开浏览器。配合 `webapp-testing` Skill，还能自动化表单提交、按钮点击、页面导航等交互测试。

对于后端开发者，类似的闭环是：Claude 写代码 → 运行 `go test` / `bun test` → 测试结果自动回到对话 → Claude 修复失败的测试 → 再次运行。这就是前面讲的 **Feedback Loop**。

## 不要高估也不要低估

> **高估 AI 的人，最终被 AI 坑；低估 AI 的人，被用 AI 的人淘汰。**

正确的姿势是：把 AI 当一个**知识渊博但缺乏判断力的初级开发者**。它什么都知道一点，但不知道什么时候该用什么，也不知道你的业务上下文。你给它越清晰的指令和越准确的上下文，它表现越好。

## 效率越高，越容易 Burnout

> "I shipped more code last quarter than any quarter in my career. I also felt more drained than any quarter in my career."
> —— Siddhant Khare（OpenFGA 核心维护者），[AI Fatigue Is Real](https://siddhantkhare.com/writing/ai-fatigue-is-real)（2026-02-08）

这是一个被集体回避的悖论：**AI 让单个任务变快了，但你并没有变轻松，反而更累了。**

### 为什么更累？

**1. 任务量膨胀填满时间**

以前一个功能写 3 小时，现在 45 分钟搞定。但你不会提前下班——你会接着做下一个任务。结果是以前一天做 1 个功能，现在一天做 4 个。产出量暴增，消耗也暴增。效率提高的红利被更多任务吃掉了，基准线被整体抬升。Siddhant Khare 的原话是："AI reduces the cost of production but increases the cost of coordination, review, and decision-making. And those costs fall entirely on the human."

**2. 角色从创造者变成审查者**

> "I became a reviewer. A judge. A quality inspector on an assembly line that never stops. Creating is energizing. Reviewing is draining."
> —— Siddhant Khare

以前你是写代码的人，进入心流状态一写就是几小时。现在你变成了"AI 产出评审者"——Claude 写完一大段代码，你需要逐行确认它没有引入 Bug、没有偏离架构设计、没有幻觉出不存在的 API。Khare 描述自己的状态："By Wednesday, I couldn't make simple decisions anymore. My brain was full. Not from writing code—from judging code." 这种持续做无数细小判断的工作模式，比自己写代码更消耗心智。

**3. 上下文切换代价**

HN 用户 parpfish 在[讨论帖](https://news.ycombinator.com/item?id=46934404)中精确描述了这种疲劳："For me the fatigue is a little different— it's the constant switching between doing a little bit of work/coding/reviewing and then stopping to wait for the llm to generate something." 另一位用户 amelius 补充道："As a programmer I want to minimize my context switches, because they require a lot of energy. LLMs force me to context switch all the time."

以前一天专注一个问题，深度思考。现在 Claude 让你一天能摸 6 个问题，但**人脑在问题间的切换代价极其昂贵**。每次切换都要重建上下文、回忆约定、确认状态。频繁切换让你一天下来感觉什么都碰了，但什么都没想透。

**4. AI 输出的不确定性打破确定感**

> "You are collaborating with a probabilistic system, and your brain is wired for deterministic ones. That mismatch is a constant, low-grade source of stress."
> —— Siddhant Khare

工程师习惯了编译器的确定性逻辑：代码对就过，代码错就报错。但 AI 的输出没有这种确定性——它可能"看起来对但其实错了"。你需要对每一段输出保持警惕，这种持续的认知紧张状态会不断消耗你。

**5. 心流状态被彻底打碎**

HN 用户 ericmcer 一针见血："I love the flow state, and I'm pretty sure it's fundamentally incompatible with prompting." 写代码时你能进入心流——键盘响个不停，思路连贯，几小时不知不觉过去。但用 AI 编程的节奏是"写 prompt → 等 → 审查 → 发现问题 → 再写 prompt"，这种碎片化的节奏让心流状态根本无法建立。

### "每提一个请求，就点一根烟"

有开发者说：每次给 Claude Code 提一个不知道要跑多久的请求，就点上一根烟放松一下；也有人会切去玩那种随时拿起来、随时放下都不影响的小游戏（HN 用户 mikkupikku 提到用 [Endless Sky](https://endless-sky.github.io/) 来填充等待时间）。

这不是玩笑，这是一种**真实的应对机制**。当你的工作节奏变成"写 prompt → 等 AI 跑 → 审查输出 → 发现问题 → 再写 prompt"的循环时，你需要在每个间隙给自己充电，否则很快就会被掏空。

### FOMO 跑步机

**FOMO**（Fear Of Missing Out）——错失恐惧症在 AI 工具领域被无限放大。Claude Code 发 sub-agents、skills、Agent SDK；OpenAI 上线 Codex CLI；Google 推出 Gemini CLI……每次迁移耗掉一个周末，换来大概 5% 的提升。Siddhant Khare 称之为"FOMO 跑步机"（FOMO treadmill）。

### 怎么避免 Burnout？

Peter Steinberger（Clawdbot 开发者）曾创建了一个聚会，最初叫"Claude Code Anonymous"，后来改名"Agents Anonymous"——他和朋友们都出现了凌晨 4 点互发消息、停不下来的症状。他说："I used to have an addiction, now I have one again, but this time it's the positive kind."（[采访原文](https://blog.wenhaofree.com/en/posts/articles/2026-01-30-peter-steinberger-clawdbot-interview/)）但不是所有人都能把瘾控制在正面范围内。

Viacheslav Vasipenok 在 [The Hidden Dangers of AI Coding Agents](https://quasa.io/media/the-hidden-dangers-of-ai-coding-agents-how-addiction-to-claude-code-and-beyond-could-claim-many-victims)（2026-02-08）中警告："a mental health crisis in the making, where the thrill of AI-assisted creation overrides work-life balance, leading to exhaustion and regret."

**可持续使用建议（来自 Siddhant Khare 原文 + HN 社区讨论）：**

1. **设时间盒**：给 Claude Code 的任务设 30 分钟上限，超时就 Esc 停掉，重新拆分
2. **接受 70% 可用**：不要追求 AI 输出完美，差不多能用就先提交，后面再迭代
3. **前置思考，后置执行**：先用 Plan Mode 想清楚再让 Claude 写，别一上来就"帮我实现这个"
4. **不追每一个 changelog**：工具更新很快，但你不需要每个都跟。挑对你有用的，其他的无视
5. **物理隔断**：Claude 跑的时候站起来走走、倒杯水。别盯着终端等输出——这和盯着进度条一样浪费精力
6. **记录 AI 在哪帮了忙、在哪添了乱**：Khare 建议 "log where AI helps versus creates friction"，这样你能理性评估而不是凭感觉

> AI 时代最重要的技能不是 prompt 工程，而是知道**什么时候该停下来**。—— Siddhant Khare 原文："the real skill of the AI age isn't prompt engineering—it's knowing when to stop."

**参考来源：**
- Siddhant Khare，[AI Fatigue Is Real](https://siddhantkhare.com/writing/ai-fatigue-is-real)（2026-02-08）
- [Hacker News 讨论帖](https://news.ycombinator.com/item?id=46934404)（2026-02-11，parpfish / ericmcer / amelius / mikkupikku 等用户评论）
- Peter Steinberger 采访，[Burnout, Restart, Viral: Clawdbot Creator Interview](https://blog.wenhaofree.com/en/posts/articles/2026-01-30-peter-steinberger-clawdbot-interview/)（2026-01-30）
- Viacheslav Vasipenok，[The Hidden Dangers of AI Coding Agents](https://quasa.io/media/the-hidden-dangers-of-ai-coding-agents-how-addiction-to-claude-code-and-beyond-could-claim-many-victims)（2026-02-08）

# 数据安全

Claude 协议中明确说明了，非企业级、Max 用户，对话数据会被拿去训练。虽然会做数据清洗，把敏感数据清洗掉，但是还是会存在一定风险，所以能不在对话中暴露配置信息就不要暴露，能用环境变量就别直接写。当然，国内的 GLM 也明确写了，你的对话数据会被保存，并且拿去训练。如果你在大企业，对数据安全有极高要求，那就只能内网部署 Stepfun-3.5-Flash 这样的截止 2026年2月6日开源 SOTA 模型，内部使用。要用 WebSearch、WebFetch、图片识别这三个核心 Function，那就只能自己在服务端拦截，自己写代理拦截，并且返回了，或者用 Claude Code Router 来拦截。

# BUG

Claude Code 有严重的 BUG，不要开太久，或者对话太长，偶尔会有内存泄露的问题，一个终端占用 4GB 内存。需要注意下，直接退出。

# 扩展知识

## 必学 Agent 资源

在深入学习 Claude Code 和 AI 编程之前，强烈推荐先学习以下两个资源，它们是理解 Agent 的基石。

### 1. LLM Powered Autonomous Agents —— Lilian Weng

**链接**: `https://lilianweng.github.io/posts/2023-06-23-agent`

这是 Agent 领域**最经典的入门文章**，由 OpenAI 应用 AI 研究负责人 Lilian Weng 于 2023 年 6 月撰写。几乎所有 Agent 相关的论文、项目、框架都会引用这篇文章。

**核心内容**：

**Agent 的三大组件**：

1. **规划（Planning）**
   - **任务分解**：将复杂任务拆分成可执行的子任务
   - **反思（Self-Reflection）**：检查自己的行为，从错误中学习

2. **记忆（Memory）**
   - **感觉记忆（Sensory Memory）**：原始输入的短暂保留
   - **短期记忆（Working Memory）**：上下文窗口，有限容量
   - **长期记忆（Long-term Memory）**：向量数据库、知识图谱等持久存储

3. **工具使用（Tool Use）**
   - 调用外部 API、搜索引擎、代码执行器等
   - 这正是 MCP、Function Calling 的理论基础

**为什么必学**：

- 这篇文章奠定了现代 Agent 的理论框架
- 理解了这篇文章，你就能理解 Claude Code、AutoGPT、MetaGPT 等所有 Agent 工具的设计原理
- Claude Code 的 Plan Mode、Memory 系统、MCP 工具调用，都可以在这篇文章中找到理论依据

### 2. Hugging Face Agents Course

**链接**: `https://huggingface.co/learn/agents-course/en/unit0/introduction`

这是 Hugging Face 官方推出的**免费 Agent 课程**，从初学者到专家的完整学习路径。

**课程结构**：

| 章节 | 主题 | 内容 |
|------|------|------|
| 0 | 入门 | 工具和平台配置 |
| 1 | Agent 基础 | Tools、Thoughts、Actions、Observations 概念；LLM、消息格式、Chat Templates |
| 2 | 框架 | smolagents、LangGraph、LlamaIndex 等主流框架实战 |
| 3 | 实战案例 | 真实世界的 Agent 应用 |
| 4 | 最终项目 | 构建 Agent 并在排行榜上竞争 |

**Bonus 单元**：
- Fine-tuning an LLM for Function-calling
- Agent Observability and Evaluation
- Agents in Games with Pokemon（用 Agent 打宝可梦）

**课程特色**：
- 完全免费，可选认证（完成作业可获得证书）
- 实践导向：每个概念都有配套的 Hands-on 练习
- 社区驱动：Discord 学习群组、排行榜竞争
- 多语言支持：有中文翻译版本

**学习时间**：每章约 3-4 小时，共约 4 周

**为什么推荐**：
- 这是最系统、最权威的 Agent 入门课程
- 学完后你不仅会用 Agent 框架，还能理解其底层原理
- 认证证书在求职时有参考价值


### 3. DeepLearning.AI Short Courses —— 吴恩达 Agent 系列课程

**链接**: `https://www.deeplearning.ai/short-courses/`

吴恩达的 DeepLearning.AI 平台提供了大量**免费**的 Short Courses，每个课程 1-2 小时，由行业专家讲授。以下是 Agent 相关的核心课程：

**多 Agent 系统**：

| 课程 | 合作方 | 核心内容 |
|------|--------|----------|
| [AI Agentic Design Patterns with AutoGen](https://www.deeplearning.ai/short-courses/ai-agentic-design-patterns-with-autogen/) | Microsoft | AutoGen 框架、多 Agent 协作模式、对话驱动开发 |
| [Multi AI Agent Systems with crewAI](https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/) | crewAI | crewAI 框架、角色定义、任务分配、Agent 编排 |
| [Multi-Agents with Gemma and LangChain](https://www.deeplearning.ai/short-courses/multi-agents-with-gemma-and-langchain/) | Google | Gemma + LangChain、多 Agent 协作实战 |

**Agent 框架实战**：

| 课程 | 合作方 | 核心内容 |
|------|--------|----------|
| [Functions, Tools and Agents with LangChain](https://www.deeplearning.ai/short-courses/functions-tools-agents-langchain/) | LangChain | Function Calling、工具定义、Agent 构建 |
| [Building Agentic RAG with LlamaIndex](https://www.deeplearning.ai/short-courses/building-agentic-rag-with-llamaindex/) | LlamaIndex | Agentic RAG、动态检索、智能查询路由 |
| [LLM Agents](https://www.deeplearning.ai/short-courses/llm-agents/) | Harrison Chase | Agent 核心概念、ReAct 模式、工具使用 |

**专业领域 Agent**：

| 课程 | 合作方 | 核心内容 |
|------|--------|----------|
| [Building Your Own Database Agent](https://www.deeplearning.ai/short-courses/build-your-database-agent/) | - | 数据库查询 Agent、SQL 生成 |
| [Building with Voice AI](https://www.deeplearning.ai/short-courses/building-with-voice-ai/) | Deepgram | 语音识别、语音 Agent、实时对话 |
| [AI Agents in Production](https://www.deeplearning.ai/short-courses/ai-agents-in-production/) | Arize AI | Agent 监控、评估、生产部署 |
| [Building AI Applications with Haystack](https://www.deeplearning.ai/short-courses/building-ai-applications-with-haystack/) | deepset | Haystack 框架、RAG Pipeline、Agent 集成 |

**编码 Agent（Claude Code 相关）**：

| 课程 | 合作方 | 核心内容 |
|------|--------|----------|
| [Claude Code: A Highly Agentic Coding Assistant](https://www.deeplearning.ai/short-courses/claude-code-a-highly-agentic-coding-assistant/) | Anthropic | Claude Code 最佳实践、Plan Mode、MCP |
| [Code Generation with CodeLlama](https://www.deeplearning.ai/short-courses/code-generation-with-codellama/) | Meta | 代码生成模型、编程助手构建 |

**学习建议**：
- 所有课程免费，只需注册即可学习
- 每个课程 1-2 小时，适合碎片化学习
- 配有代码实践（Colab Notebook）
- 建议按"LangChain → AutoGen/crewAI → 专业领域"顺序学习


**学习路径建议**：

```
1. 先读 Lilian Weng 的文章（1-2 天）
   → 理解 Agent 的理论框架和三大组件

2. 再学 Hugging Face 课程（4 周）
   → 掌握主流 Agent 框架的实战技能

3. 选学 DeepLearning.AI Short Courses（按需）
   → 深入特定框架或领域

4. 最后回到 Claude Code
   → 你会发现 Claude Code 的 Plan Mode、Memory、MCP 都是这些理论的应用
```


## 2023 年经典多 Agent 项目

### 1. ChatDev —— 多 Agent 协作软件开发

**GitHub**: `https://github.com/OpenBMB/ChatDev`

清华大学 OpenBMB 团队出品。多个 Agent 扮演软件公司不同角色（CEO、CTO、程序员、测试员、设计师等），协作完成软件开发。整个流程模拟真实公司：

```
需求分析 → 技术设计 → 编码实现 → 代码审查 → 测试 → 环境配置
```

**核心创新**：
- 角色扮演机制：每个 Agent 有明确的职责和专业领域
- 对话驱动：Agent 之间通过自然语言对话协作
- 迭代优化：支持多轮修改和完善

**论文**: *Communicative Agents for Software Development* (2023)


### 2. Stanford Generative Agents —— 斯坦福 AI 小镇

**GitHub**: `https://github.com/joonspk-research/generative_agents`

斯坦福大学研究项目。25 个 AI 角色在虚拟小镇 "Smallville" 里生活、社交、工作。每个 Agent 有独立的记忆系统和个性。

**核心特性**：
- **记忆流（Memory Stream）**：记录所有经历，按重要性排序
- **反思机制（Reflection）**：定期总结经验，形成高层认知
- **规划系统（Planning）**：根据记忆和反思制定行动计划
- **社交传播**：信息在小镇里自然传播，Agent 之间会分享消息

**经典场景**：一个 Agent 在派对上听说要办情人节活动，消息在小镇里传播开，其他 Agent 也会来参加。

**论文**: *Generative Agents: Interactive Simulacra of Human Behavior* (2023)


**这两个项目的影响**：直接启发了后来的 AutoGen、MetaGPT、CrewAI 等多 Agent 框架。

### 3. Cyber-Zen-Master（赛博禅师）—— 思维链多步推理工作流

**GitHub**: `https://github.com/LYiHub/Cyber-Zen-Master`

林亦（young1lin）出品的哲理问答多步推理项目。基于 DeepSeek 实现，核心是**思维链（Chain of Thought）多步推理**的工作流设计。

**核心特性**：

- **三阶段推理流程**：通过 stage1 → stage2 → stage3 的渐进式推理，逐步深化对问题的理解
- **Lisp 风格提示词**：采用李继刚老师「汉语新解」系列的 Lisp 格式提示词，结构化思维表达
- **可扩展架构**：每个阶段独立的 prompt 设计，方便针对不同场景定制
- **完整输出记录**：中间推理过程和最终结果都保存在 `output` 文件夹

**典型工作流**：

```
输入问题 → stage1 初步分析 → stage2 深度思考 → stage3 自我表达 → 输出答案
```

**技术亮点**：

- 展示了如何设计多步骤推理的 Agent 工作流
- Lisp 格式提示词的结构化优势（嵌套、条件、函数式思维）
- 国产大模型（DeepSeek）在复杂推理任务上的实践

**适用场景**：创意写作、哲学思辨、复杂问题的多角度分析。
