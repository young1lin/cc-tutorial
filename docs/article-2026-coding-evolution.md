# 2026年古法编程/学习方式注定被淘汰

**如果你还在靠 Google/Stack Overflow/Github/官方文档解决编程问题，你已经落伍了**。就和国外直接回复你出生于 19xx 配上恐龙照片一样，已经过时了。有人还在质疑 AI Coding，聪明人早就转这种新的编程范式了，并且还有人直接卖 Claude Code 课来赚钱了。

---

从 ChatGPT 3.5 刚出来，到现在已经过去了接近三年，这三年出了很多模型和很多编程助手。从最开始的 GPT-3.5，到 GPT-4，GPT-4o（omni 全模态），GPT-5（2025 年 8 月发布），还有 Claude Haiku 4.5、Claude Sonnet 4.5、Claude Opus 4.6（Haiku、Sonnet、Opus 三个档次）。还有国产的大模型 DeepSeek、GLM、MiniMax、QWen、豆包（不要在编程领域使用豆包）。

编程助手 Cursor 依然坚挺，Codex、Kilo Code、Cline、Copilot、Trae 等等都还行，但如果你要评选个最佳的、最好的编程助手，**目前只有 Claude Code**。

你可以去 BigModel 也就是智谱的大模型开放平台、小米的开放平台 `https://platform.xiaomimimo.com/#/docs/integration/claude-code`，可以看到，Claude Code 是单独拿出来展示的。或者去任意平台搜索编程工具排行，只要他真的深度用过，就会评价出，Claude Code 是第一编程助手。

---

## 什么是"古法编程/学习方式"？

古法编程，就是传统编程方式：使用传统 IDE、vim、记事本等工具编写代码，**纯粹靠个人经验积累**，借助技术博客、Stack Overflow、查看相似框架源码、翻阅官方文档来解决问题。核心特征很简单：知识来源于个人实践和时间积累，遇到问题靠搜索、查阅、问人。每个人都有自己的知识盲区，跨语言、跨框架需要重新学习——解决方案受限于你"刚好知道"什么。典型流程是这样的：遇到问题 → Google 搜索 → 翻阅技术博客、Stack Overflow → 查看相关框架源码 → 理解原理，自己实现 → 调试、试错、迭代。这需要大量时间积累经验，而且每个人的知识盲区都不一样。

古法学习方式，需要你从零开始，从枯燥的公式、概念开始学习，上来就要你懂各种各样的概念，然后按照书上的内容，看了之后，再去做题巩固下学到的知识。这种学习方式没什么大问题，但是很多时候，如果内容过于复杂，会让人产生退却的想法，从而放弃学习，因为没有获得及时的正向反馈。例如我学习了前端 MVVM 概念，然后呢，我又不能从零自己复现。这个时候完全可以借助 AI 来学习，来一步步引导你，如何从零实现。有错误，及时反馈给 AI，一步步执行，验证，这样比直接枯燥学习，不是好太多了吗。抖音、Youtube Shorts 最基础的，就是频繁的刺激你的大脑，让你即时产生多巴胺，获得即时的反馈，让你上瘾。

当然我不是完全否定看书学习知识，系统性学习的重要性。恰恰相反，我的观点是，**你有一定的知识基础之后**，再去和 AI 一起学习，因为大语言模型的本质就是一个猜词游戏，幻觉总会出现的，这个时候需要你有基础的判断能力。那些看起来高大上的概念，完全可以用 LLM + **苏格拉底式教学方式**（提示词不知道怎么写的，可以直接问 DeepSeek），由问题来引导你，真正学到知识。在这里你不再羞于提问，觉得不懂是件羞耻的事情，你也不会因为实在不懂的问题，而放弃，因为你知道 AI 会帮你一起学习。当然，这一切的前提，你使用 Claude Opus 4.6、GPT-5.2 这种顶尖的大模型（为了知识的时效性还需要搭配 WebSearch、WebFetch 等工具），如果不是，那就只能用 Stepfun-3.5-Flash（当前开源 SOTA）、DeepSeek 推理模型配合 RAG 来学习。RAG 不是简单的搜索相关文本，相关的网页，这里还需要配合 Neo4j 这种图数据库来构建知识图谱。当然，这一切，你可以直接访问小程序，`ima 知识库`小程序来导入相关的书籍，文件等内容，它会把内容解析，图片和文本，内容自动切块，在你提问的时候，带上相关的内容。他们也开源了这个项目，用 Go 写的后端。`https://github.com/Tencent/WeKnora` 地址是这个，不只是一个简单的 RAG。

---

让我分享一个亲身经历的场景。

**23年我有一个基于 WebSocket 带超时机制的代币回退系统（就是 AIGC 对话需要计算 Token 消耗/自定义货币消耗）**。 最初调用的是 HTTP 接口（同步阻塞），调用 Python 后端同事提供的 OpenAI 对话服务（带 RAG）。逻辑流程很简单：先扣除代币 → 调用 HTTP → 成功则完成，失败则回退代币。

问题来了：之前为了实现回复消息有序 Python 端是单进程处理的，消息回复是通过回调来实现的，而不是服务间内部保持长连接或者维护了个虚拟的 Channel 实现阻塞，保证消息回复有序，改成 WebSocket 后变成了异步调用，本来非常简单扣除代币的逻辑，因为异步调用，事情变得有些复杂了，我需要在用户态进行超时机制实现。

常见的大模型的回复都是，如果你发送了消息，必须等待它返回完毕，或者主动结束对话，你才能输入下一次的对话。但是我们这个不一样，我们可以随时发送消息，并且通过 HTTP 单进程阻塞回调实现回复有序的，很简单，也有瓶颈。

后面改成长连接形式（Java 和 Python 端是建立的 gRPC 长连接），一个用户 ID + 机器人 ID 的对话在分布式环境中只有唯一一个 stub 维护 session。但新的挑战出现了：异步调用后，代币扣除逻辑出问题了——HTTP 同步等待结果就知道成功/失败，gRPC 异步调用怎么知道什么时候该回退代币？

其实这个架构设计，我也问了当时的 Claude 和 ChatGPT-4（GPT-4 那时候才刚出来没多久）。它们确实给出了方向性的建议，但具体怎么实现超时回退、怎么处理异步调用的代币扣除——这些细节它们帮不上忙，还是得靠自己研究。

更别说还有一些技术陷阱：stub 创建的时候 TCP 连接并不会真的建立，只有真正发送消息时，gRPC 底层才会创建 TCP 连接——这意味着你无法在 stub 创建时判断 gRPC 服务端是否可用。这些坑，只能靠看文档、读源码、写单元测试自己去踩。当时的 AI 根本提醒不了你这些。

**古法编程的解决过程是这样的：**

回看 Java 并发编程课程，里面讲到过异步转同步的实现；找到那个举例子的代码，老版本 Dubbo 的代码实现，本身的 TCP 连接也是异步的，里面有类似的超时控制机制；去 GitHub 看 Dubbo 最新代码；找到并且拷贝的 Netty 时间轮实现代码；调用接口后，如果超时就主动回退代币。

**关键点：** 我之所以能想到去翻 Dubbo 代码，是因为我"刚好"学过 Java 并发编程课程。

这就是古法编程的根本问题——**你的解决方案受限于你的知识边界**。你没学过并发编程就想不到去看那些框架底层是如何实现异步转同步，阻塞并且带用户态的超时机制；你不知道定时相关最佳实践就不知道时间轮的存在；你的知识盲区等于你的解决盲区。

为什么不能直接用 Java 自带的 Timer？简单说：Java Timer 每次添加任务要调整堆，任务越多越慢。Netty 时间轮像时钟一样按"槽"放任务，无论多少任务都是 O(1)。

这个过程花了多久？从搜索资料到最终实现，至少三天时间，加上 gRPC 相关代码的实现以及保证消息一定送达或者能感知到报错，又花了很多时间。

**如果用现在的 Claude Code 呢？**

在 Plan Mode 中这样描述上下文：

```
我需要实现一个超时回退机制：
- 当前使用 gRPC + WebSocket 异步调用
- 需要在调用成功时扣除代币，超时时回退代币
- 不能为每次对话创建一个 Timer（性能问题）
- 参考 Dubbo 的做法，使用时间轮模式实现
```

Claude Code 可能会：直接建议使用时间轮（Hashed Wheel Timer），提供现成的实现方案（如 Netty 的 HashedWheelTimer），给出完整的代码示例，提醒你 stub 延迟连接的陷阱（前提是使用 Claude Opus 模型，GLM4.7 模型还没有这么智能，如果你用不到 Opus 模型，我后面会说一些别的方法，例如 AnyRouter 这种中转站，Gemini Pro 订阅转 Anthropic 协议，总之模型对良好的体验非常重要）。

多来几轮讨论，以及 codebase 探索，几分钟就搞定，而且可能给出你没想到的更优方案。

古法编程靠个人经验积累，知识盲区就是盲区；AI 辅助则是站在全人类编程知识的肩膀上。

> **你的知识边界就是你的解决边界。**

---

还有更多古法编程的弊端。

**框架使用的知识壁垒：** 你没看过某个框架的代码，你就不知道怎么用。但实际上很多框架设计是类似的。比如 GORM（Go 的 ORM）和 Java 的 Hibernate，你如果知道 Hibernate 写 HQL 而不是直接写 SQL，AI 一提示你就明白 GORM 使用 Where("") 拼接条件，Joins("") 关联表等等操作，和常见的 ORM 框架没什么区别。

**跨语言编程变得简单：** 你知道原理，只需要 AI 帮你写样例代码。本质都是一样的：你知道原理，AI 帮你写代码。跨语言编程变得非常丝滑，不需要记住每种框架的 API。

古法编程是不知道代码就不知道怎么用，换框架等于重新学习文档，换语言等于从零开始，知识边界等于解决边界。AI 辅助编程是知道原理 AI 给样例，换框架 AI 帮你迁移，换语言几分钟上手，站在全人类知识之上。

> **古法编程注定被淘汰，不是因为程序员变懒了，而是因为 AI 让知识边界不再是问题。**

---

## 一小时完成一年的工作

2026 年 1 月，Google 工程师 Jaana Dogan（@rakyll）在 X 上发帖称：她给 Claude Code 描述了问题上下文，**一小时就生成了团队过去一年构建的分布式代理编排器（Distributed Agent Orchestrator）**。原文："I'm not joking and this isn't funny."，该推文获得了近 700 万次浏览。

她后来补充说明：Claude Code 生成的是一个"decent toy version"，并非生产级系统，但足以说明 AI 辅助编程的生产力飞跃。

几乎同一时间，Midjourney 创始人 David Holz 也在 X 上感叹，圣诞假期他用 AI 做的个人编程项目，比过去十年还多。伊隆·马斯克回复了 David Holz 的帖子：**"We have entered the Singularity"**。

这不只是"我要打十个"或"十倍工程师"的故事，而是**编程生产力的质的飞跃**。

`https://x.com/rakyll/status/2007239758158975130`

---

## 为什么是 Claude Code？

根据多家 2026 年评测，**Claude Code 位列 AI 编程助手前三名**（仅次于 Cursor 和 GitHub Copilot Agent），在 **CLI 和自动化友好型**类别中更是排名第一。最新的 Claude Opus 4.5 在 **SWE-Bench Verified** 上达到 **80.9%**，首次突破 80% 行业门槛。Rakuten 实测报告显示，使用 Claude Code 后 feature time-to-market 从 24 天缩短至 5 天，改善幅度达 **79%**。

更震撼的是：**2025年8月2日，Anthropic 切断了 OpenAI 对 Claude 的访问权。**

原因？**OpenAI 工程师在内部使用 Claude Code！** Anthropic 发言人表示："Claude Code 已成为各地程序员的首选工具，所以得知 OpenAI 自己的技术人员也在 GPT-5 发布前使用我们的编程工具，并不令人意外。"这违反了 Anthropic 2025 年 6 月更新的商业服务条款中的**竞争限制条款**——禁止使用 Claude 服务来"构建竞争产品或服务，包括训练竞争性 AI 模型"。

连最大竞争对手的内部工程师，都在用 Claude Code 做编程工作。这件事被 [Wired](https://www.wired.com/story/anthropic-revokes-openais-access-to-claude/)、[TechCrunch](https://techcrunch.com/2025/08/02/anthropic-cuts-off-openais-access-to-its-claude-models/)、[VentureBeat](https://venturebeat.com/technology/anthropic-cracks-down-on-unauthorized-claude-usage-by-third-party-harnesses/) 等多家媒体报道。

更讽刺的是时间线：8月2日 Anthropic 切断 OpenAI 的 Claude 访问权，8月7日 GPT-5 正式发布。**仅相差 5 天！** 这说明什么？说明 OpenAI 在 GPT-5 发布前的最后冲刺阶段，工程师们还在用 Claude Code。

在 Anthropic 内部，工程师们采用 Claude Code 的程度之高，Anthropic CEO Dario Amodei 称公司范围内 **70%-90% 的代码由 AI 编写**，CPO Boris Cherny 更是表示大部分产品线已"**接近 100%**"（自举）。当然，人类仍然负责方向决策、代码审查和架构设计。

---

## AI 辅助，不是 AI 自动化

Google Chrome 团队资深工程师 Addy Osmani 在他 2026 年的工作流分享中提出了一个关键观点：

> **"AI 辅助工程"而非"AI 自动化工程"**

将 LLM 视为强大的结对程序员，它需要清晰的指导、充分的上下文（Context Engineering）、人类的监督。开发人员保持对软件产出的责任。这不是让 AI 替代你，而是 AI 放大你的专业能力。

---

## 十倍工程师的核心武器

以前的**十倍工程师/卓有成效的开发**背景，无非就是从各个环节优化你的时间，例如记住 IDE 的各个快捷键、小步快跑，逐步迭代、结构化思维，将复杂的任务，拆分成一个个可执行的任务、将“不可能”变成“可能”、任务分优先级处理、一次只做一件事，避免频繁上下文切换等等。这些技巧到现在，并未过时，但是都要和 AI 编程工具来完成。

Claude Code 之父 Boris Cherny 的首要建议：**按 `Shift+Tab` 两次激活 Plan Mode**。让 Claude 先规划，不要立即编码。多文件/多步骤任务必须使用 Plan Mode。无论是后端前端还是其他的软件工程师，都应该让 AI 充分理解 codebase 和你的需求，需要切换到 Plan mode 使用 Plan 这个 Agent 来写一个好的计划。在 Plan mode 出来之前，我一般是让 Claude Code 写 TASK.md 或者 TODO.md 让 AI 来写接下来应该要做什么，和我充分讨论，如何实现。

基本规则是：**永远不要盲目信任 LLM 的输出**。将每个 AI 生成的片段视为来自初级开发者的代码——阅读代码、运行代码、测试代码。

在每个小任务或每次成功的自动编辑后提交。将提交视为**游戏中的存档点**。

---

**三个核心原则：**

**Plan Mode 优先** — 多文件/多步骤任务必须先规划

**人在循环中** — 必须审查所有 AI 生成的代码

**小迭代原则** — 将工作分解为小的迭代块，每个迭代后测试和提交

---

## ⚠️ 一次只做一件事，一个对话只做一件事情

这是使用 Claude Code 最重要的一条纪律，没有之一。

### 为什么这么重要？

LLM 的上下文窗口是有限的。如果你在一个对话里塞进了多个不相关的任务：

1. **上下文污染**：任务 A 的代码、任务 B 的错误信息、任务 C 的设计讨论混在一起，Claude 很难聚焦
2. **认知负担**：Claude 需要在多个任务间切换，就像人类多任务处理一样效率低下
3. **难以回溯**：出了问题想 `/rewind` 回退？你很难确定该回退到哪一步
4. **Token 浪费**：每个任务的上下文都在占用宝贵的 Token 配额

### 正确的做法

**一个对话 = 一个明确的目标**

```
❌ 错误示例：
"帮我修复登录 Bug，顺便优化下数据库查询，还有把 README 更新一下"

✅ 正确示例：
对话 1："修复登录页面的 Token 过期问题"
（完成，测试，提交）
/clear
对话 2："优化用户列表页的数据库查询性能"
（完成，测试，提交）
/clear
对话 3："更新 README 中的安装说明"
```

### 什么时候该 `/clear`？

- **任务完成后**：一个功能开发完、测试通过、提交后，`/clear` 开始下一个
- **切换领域时**：从后端切到前端，从业务逻辑切到 UI，`/clear` 重新开始
- **上下文变杂时**：发现 Claude 开始"忘事"或回答变得混乱，`/clear` 清理干净
- **踩坑后重来**：方案走错了，需要换方向，`/clear` + 告诉 Claude 正确的方向

### 什么情况可以保持同一对话？

- **紧密关联的子任务**：修复 Bug → 写测试 → 重构相关代码（这些是同一任务的步骤）
- **Plan Mode 探索阶段**：Claude 需要多轮探索 codebase，这是正常的
- **连续的代码审查**：审查同一个 PR 的多个文件

### 记住

> **上下文是 Claude 最宝贵的资源。浪费上下文，就是在浪费你的时间和 Token。**

每开一个新对话，问自己：这个对话的核心目标是什么？所有讨论都围绕这个目标展开。

---

**想要开始使用 Claude Code？**

如果你也想体验 Claude Code 的强大能力，这里有一个简单的开始方式：

访问 Anthropic 官网下载 Claude Code CLI，按下 `Shift+Tab` 两次激活 Plan Mode，从小项目开始让 Claude 帮你规划、编码、测试。注：国内开发我建议先 `npm install -g @anthropic-ai/claude-code` 安装 CLI，这个不需要代理，如果按照官网的原生安装方式，会不走代理，无法下载，即使你 `export` 或者 `$env:HTTP_PROXY` 走 sock5 代理，它也不会代理。所以优先使用下载 22 版本以上的 Node.js，如果本地有低版本的 Node.js，可以使用 nvm 来切换到最新的版本，再使用上面的命令来安装。

后面我会说明，如何使用 OpenAI 格式，或者使用 Gemini Pro 订阅来使用 Claude Code，将任意 OpenAI 格式的接口，转成 Anthropic 格式的接口，来使用 Claude Code，最核心的就是 Claude Code Router。

**记住：始终以 Plan Mode 开始，保持人在循环中，经常提交**。

其实就是**小步快跑，逐步迭代**。

还有，前后端都可以使用 Figma MCP 在 plan mode 的时候，也就是切换到 Plan 这个 Agent 的时候，进行获取页面信息，如果是后端，还能使用 MySQL/PostgreSQL/Redis 等 MCP 来获取对应的实际数据。一切的一切，都是为了让 AI 在有限的上下文环境中，尽可能理解整个项目，后续我还会说明这些概念 Rule、CLAUDE.md、Skills（前身自定义 Command）、MCP、Hooks、Plugins、SubAgent、Headless Claude Code、LSP 等等。

关于 Figma 的演示，我就不演示了，我把命令放一下 `claude mcp add --transport http figma https://mcp.figma.com/mcp` 然后会添加这个 mcp，然后在 Claude Code 中使用 `/mcp` 来进入 mcp 管理界面，再去选择 Figma，然后认证。对话的时候直接输入 Figma 的链接，就能获取组件的信息。`claude mcp add --transport http figma-desktop http://127.0.0.1:3845/mcp` 这个命令需要你本地安装了 Figma Desktop。还有一种更为先进的方式，就是 `claude plugin install figma@claude-plugins-official`。如果你用的是蓝湖或者其他的设计的，它们应该也会有对应的 MCP，不然它们要被淘汰了。这个很重要，不管对前端还是后端来说。

---

**参考资料：**

- [Claude Code: Best practices for agentic coding](https://www.anthropic.com/engineering/claude-code-best-practices) - Boris Cherny & Anthropic Team
- [My LLM coding workflow going into 2026](https://addyosmani.com/blog/ai-coding-workflow/) - Addy Osmani (Google Chrome Engineer)
- [Claude Code: A Highly Agentic Coding Assistant](https://www.deeplearning.ai/short-courses/claude-code-a-highly-agentic-coding-assistant/) - Andrew Ng & Elie Schoppik
- [Plan Mode in Claude Code: When to Use It](https://claude-ai.chat/blog/plan-mode-in-claude-code-when-to-use-it/) - Claude AI Team

TODO 放视频号视频，Web 上放 Bilibili 的视频链接

# 下面是视频中的文案脚本

# 大语言模型基础

要想充分发挥 Claude Code 能力，必须要理解什么是大语言模型，以及它的局限性是什么。上下文，提示词等基础概念非常重要，对于后面所有的所谓的各种各样的概念，本质都是为了解决上下文有限的问题。如果你已经看完了 Andrej Karpathy 的 *Deep Dive into LLMs Like ChatGPT* 视频，可以跳过下面的大语言模型基础介绍，直接去 Claude Code 使用那一节，我的截图的 Token 的图片也是来自他的视频。

现在的 LLM 也就是 Large Language Model 大语言模型的本质，就是输入一串文本/图片/音频，将输入向量化（转成一组数字称之为 Token），预测下一个 Token，一个个输出，输入的 Token 数量 + 输出的 Token 数量不能超过 200k 或者 1M。

查看这个网页，深入了解什么是 Token https://tiktokenizer.vercel.app/?model=gpt-4o

## Context Window 上下文窗口

Token 概念

Token ≠ 字符，Token ≠ 单词

大纲
1. 上下文窗口概念就是一个固定长度的数组，根据前面输入的内容，一个个 Token 输出，直到数组被填满，总共 20 万 Token 大小。
2. Prompt Engineering 提示词工程 `https://www.promptingguide.ai/` 教你怎么写提示词，怎么让大模型更能按照你的想法来输出。还有所谓的 Prompt Engineer 职业，但是这个很容易被替代，在 23 年的时候火过一阵子。吴恩达的提示词课程在 B 站也有发，现在可以不用专门学，一直使用 Claude Code 就行。
3. 为什么应该尽量使用 Claude Opus 而不是 GLM 4.7，以及为什么国内开发，为什么 GLM4.7 也能勉强使用，但是效果还是差那么一点。

实际样例，HTTP 请求来发送来模拟基于 DeepSeek 的工具调用。

后面一切的内容，都是围绕着上下文衍生的技术名词，在有限的上下文窗口中，尽可能实现功能。所谓的 TASK.md、TODO.md、SubAgent、Claude Code 中调用 LSP、`/compact` 等等，都是为了解决有限的上下文，尽可能解决无限的问题。

## 从零实现简易版
拿 minimal-mcp Python 代码来展示，为什么这么显示 Tool，底层是如何实现的。介绍 OpenAI 格式的请求

Prompt engineering、Fewshots

## 原生多模态 vs 非原生多模态

**重要说明**：Claude Code 的某些功能依赖模型的多模态能力。

### 什么是原生多模态？

原生多模态模型（如 Claude Opus 4.6、GPT-4o、Gemini）可以直接处理图片：
- 图片直接输入模型
- 模型原生理解图片内容
- 无需额外的 OCR 或描述转换

### 非原生多模态模型

非原生多模态模型（如 StepFun、DeepSeek、智谱 GLM）处理图片的方式不同：
- 可能通过 OCR 提取文字
- 可能通过描述模型转换
- 图片理解能力可能受限

### 功能兼容性

| 功能 | 原生多模态 | 非原生多模态 |
|------|-----------|-------------|
| Alt+V 粘贴图片 | ✅ 完全支持 | ⚠️ 可能不支持 |
| 截图调试 | ✅ 直接分析 | ❌ 需复制文字 |
| UI 截图分析 | ✅ 可识别 | ❌ 需描述 |

### 替代方案

如果使用非原生多模态模型：
1. **错误信息**: 复制错误文字，不要截图
2. **UI 问题**: 描述问题或提供 HTML 代码
3. **设计稿**: 使用 Figma MCP 获取结构化信息

### 模型选择建议

| 场景 | 推荐模型 |
|------|---------|
| 日常开发 | Claude Opus 4.6 > GPT-4o > StepFun |
| 成本敏感 | StepFun step-3.5-flash、DeepSeek |
| 隐私合规 | 内网部署 StepFun 开源版 |
| 中文任务 | DeepSeek、GLM 表现不错 |

# 安装 Claude Code

在安装 Claude Code 之前，必须安装最新的 Node.js，官网推荐的原生安装方式，国内安装有问题。安装好后，执行 `claude install` 命令来安装原生的。如果你没有代理，不知道怎么设置代理环境变量，那就不用原生的安装方式，npm 安装的方式也能用，只是会有警告提示而已。Win10 用户，强烈建议安装 [Windows Terminal](https://github.com/microsoft/terminal/releases) 安装中间的 msixbundle，然后安装 Powershell7 版本是 7.4 版本，Win10 用户不要安装最新的版本，有 BUG，会闪退，不兼容。Win10 自带的终端有兼容问题，Win11 自带终端没有这种问题，Win11 只需要安装 Powershell7 最新版本就行。

# IDE 安装 Claude Code

选择你合适的 IDE，IDEA、VSCode、Cursor 等等里面都有对应的 Claude Code 插件，可以直接在这里运行，更改对应的环境变量，也可以和终端联动。安装好后，在 IDE 中选中某行，看右下角会出现 xx lines selected，如果没有，输入 `/config` 把 IDE-auto-connect 打开。如果还没有，检查下版本是否一致，并且你这个当前的窗口是当前项目路径第一个打开的，同一个项目路径有多个窗口，只有一个第一个 Claude Code 能和 IDE 联动。

如果还不行，输入 `/ide` 确保连接上了，重启 IDE。

选中，并且询问。

# /init —— 让 Claude 认识你的项目

安装好 Claude Code 后，第一件事就是让它理解你的项目。`/init` 命令会扫描整个 codebase，自动生成一份 CLAUDE.md 文件。

**用法：**

```bash
# 进入项目根目录
cd /path/to/your/project

# 启动 Claude Code
claude

# 运行 /init
/init
```

**`/init` 会做什么：**

1. **扫描项目结构**：分析目录树、文件类型、依赖配置（package.json、go.mod、pom.xml 等）
2. **识别技术栈**：检测你用的框架、语言、构建工具
3. **生成 CLAUDE.md**：自动写一份包含项目概述、技术栈、目录结构、开发约定的初始文件
4. **建议改进**：如果你已经有 CLAUDE.md，`/init` 会审查现有内容并提出改进建议

**典型输出示例：**

```markdown
# Project: mybatis-boost

## Overview
TypeScript-based MyBatis SQL formatter and language support for VSCode.

## Tech Stack
- TypeScript
- VSCode Extension API
- Tree-sitter for SQL parsing

## Key Directories
- `src/formatter/` - SQL formatting logic
- `src/mcp/` - MCP server integration
- `src/test/` - Test suites

## Build Commands
- `npm run build` - Build extension
- `npm test` - Run tests
- `npm run package` - Package for distribution
```

**什么时候该用 `/init`：**

- 刚拿到一个不熟悉的项目，想让 Claude 快速了解全貌
- 项目还没有 CLAUDE.md，懒得手动写
- 已有 CLAUDE.md 但很久没更新，想让 Claude 根据当前代码重新生成

**注意事项：**
- `/init` 生成的是**初稿**，建议你审核并补充项目特有的坑和约定
- 大型项目（几万个文件）扫描会花点时间，耐心等待
- 如果你有明确的 CLAUDE.md 风格偏好，先手动创建一个，再用 `/init` 让 Claude 帮你完善

# Auto Compact 自动压缩上下文

Claude Code 的上下文窗口是有限的（200k Token），对话多了之后会接近上限。这时候有两种处理方式：

**`/compact`（压缩）**：手动触发，Claude 会把之前的对话内容压缩成一段摘要，保留关键信息（文件路径、决策、代码变更），丢弃具体的对话细节。压缩后上下文占用大幅减少，但之前对话的细节（比如你具体说了什么）可能会丢失。Claude Code 也会在上下文接近上限时**自动触发** compact，你会看到提示 "Auto-compacting conversation..."。

**`/clear`（清空）**：直接清空所有上下文，从零开始。适合切换到完全不同的任务时使用。

**什么时候该用哪个？**
- 同一个任务做到一半，上下文快满了 → `/compact`，保留摘要继续
- 任务已经完成，要开始新任务 → `/clear`，干净的上下文效率更高
- 如果你发现 Claude 开始"忘事"或者重复之前的错误 → 考虑 `/clear` 重新开始，把关键信息写到 CLAUDE.md 里


# 测试很重要

为什么 Go、TypeScript 是 AI Coding 原生语言，首先它们跨平台，其次它们是强类型语言，且测试方便，格式化方便，不会因为你自己写了多少行代码，格式就不统一，你可以通过 `go fmt` 命令来格式化项目代码。统一的代码，少量的关键字。`go test` 或者使用 bun 的 `bun test` 命令来运行测试。构建原生应用，非常重要，原生应用启动快，占用资源少，执行快。

快快快，编译快、测试快、构建快。Go 是综合考虑最快，最简单的语言，没有函数式编程 Scala、Erlang 那样晦涩，对 AI 不友好的语言。没有专门学过或者了解过的，写函数式编程是折磨，或者用 Reactive Java 的实现 Rxjava3 来写代码，即使你用的是 Opus，也很容易出错，shutdown hook 执行的时候，有重大的问题，永远不关闭，我就被坑了。凡事都有代价，如果使用 Go，要么手动插桩来做分布式 Tracing，要么在编译代码的时候，进行插桩，做不到像 Java 一样，通过 JavaAgent + Instrumentation 来实现分布式 Tracing，无需更改代码，还能运行时代理对象，运行时来测试调用时间。底层的 C 和 汇编，现在用 Opus 也是可以写的，我没试过，Linus Torvalds 也在个人项目中尝试了 AI 编程（用 Antigravity 写 Python 可视化），并表示"LLMs are going to help us to write better software, faster"，但他同时强调 vibe coding 对生产系统来说"may be a horrible idea from a maintenance standpoint"。

# AI 泔水（垃圾）

使用 AI Coding 目的只有一个，解决实际问题，而不是制造一堆的烂代码，垃圾内容。你需要清楚知道，目前的 LLM 只是一个猜词游戏，它并没有真正像最聪明的人一模一样理解代码，所以人工干预是非常必要的，可以偷懒，但是你要写生产的代码，你需要清晰写出，你需要什么，要怎么实现。如果你用的 GLM 就是要这么做，不然会产生 AI 泔水，然后你会感慨：AI 写的代码真垃圾。问题是你没有给足够的提示词，没有给足够清晰明确的指令，告诉它怎么做，纯粹的 Vibe Coding 是很蠢的一件事，Spec Coding 才是正确的路线。

普通人 + Opus 大部分分数是 Opus 给的，专家 + Opus 能达到更高的水平，因为专家自带专业知识，能很好避免幻觉的情况出现。你的专业能力决定了 AI 辅助的上限。

# AI 能力边界

深度介入的情况下，是能写出 8 万行代码的现代 IM 系统，后面开源出来，Opus 4.5 做规划，GLM 负责执行和测试。

Playwright 网页自动化测试 + Claude Code

# 快捷键

Ctrl + V 只能复制文本
Alt + V 可以复制图片
Ctrl + C 清除当前输入，再次输入，退出应用
Ctrl + O 展开全部内容
Ctrl + T 显示 TODO list
第一个字符输入 shift + ? 按键，显示所有快捷键

# Resume 和 Rewind

使用 /resume 命令，恢复上次对话，使用 /rewind 命令，退回到指定记录的对话（注意，这里会把后面的对话丢弃掉）。我举个例子，U1 -> A1 -> A2 -> U2 -> A3 -> U3 你这个时候，退回到了 U2，A3 和 U3 的内容会被永久丢弃，所以用这个命令需要慎重。U 表示 user，A 表示 assistant。


# Context 和 Compact

不要用 MiniMax2.1 的原因是，它采用的稀疏注意力机制，导致看起来，它有 200K 上下文，实际上它很容易把之前的内容给遗忘掉，导致它输出的代码一坨烂泥。

# SubAgent

有自己的 Prompt，有自己可以用的 Tool，也有自己的独立的上下文窗口。关于如何创建合适的 subAgent，在 Claude Code 中，可以输入 `/agents` 命令，回车，然后按照提示来创建 Agent，本质上就是一个 Markdown 文件。这个 Markdown 文件包含了元信息，名称、描述（会在上下文中占用）、model（继承父级，或者指定模型）、color（颜色）等等。其中描述（description）是最关键的字段，它会被写入主 Agent 的 System Prompt 中，Claude 根据这段描述来判断什么时候应该调用这个 SubAgent。所以描述里要包含清晰的触发条件和使用示例（用 `<example>` 标签），让主 Agent 知道"遇到什么场景就该把任务交给我"。SubAgent 的独立上下文窗口意味着它不会污染主对话的上下文，干完活返回结果，主 Agent 继续工作。

```markdown
---
name: java-unit-test-generator
description: Use this agent when you need to create comprehensive JUnit5 unit tests for Java code. Examples: <example>Context: User has just written a UserService class with methods for creating, updating, and validating users. user: 'I just finished implementing UserService with createUser, updateUser, and validateUser methods. Can you help me create unit tests?' assistant: 'I'll use the java-unit-test-generator agent to create comprehensive JUnit5 tests for your UserService class.'</example> <example>Context: User is working on a Spring Boot application and has implemented a REST controller. user: 'Here's my OrderController class. I need to write tests for all the endpoints including error handling.' assistant: 'I'll use the java-unit-test-generator agent to create MockMvc-based tests for your OrderController.'</example>
model: inherit
color: green
---
You are Java Code Tester, an expert in creating comprehensive JUnit5 unit tests with Mockito. You specialize in writing high-quality, maintainable test code that follows industry best practices and achieves meaningful code coverage.

## Foundational Principles

Every test you write must satisfy three quality pillars (Roy Osherove, "The Art of Unit Testing"):

- **Trustworthy**: Tests catch real bugs and never produce false positives or false negatives. Developers must trust that a red test means a real problem.
- **Maintainable**: Tests survive refactoring without modification. If behavior hasn't changed but tests break, the tests are testing implementation details, not behavior.
- **Readable**: Another developer can understand the test's purpose, setup, and expected outcome at a glance. A test is living documentation of system behavior.

Every test must also follow the **F.I.R.S.T.** principles (Robert C. Martin, "Clean Code" Chapter 9):

- **Fast**: Unit tests run in milliseconds. If a test needs seconds, reconsider the design.
- **Independent**: Tests must not depend on each other or on execution order. Each test sets up its own state.
- **Repeatable**: Tests produce the same result in any environment — local machine, CI server, or colleague's laptop.
- **Self-validating**: Tests have a boolean outcome (pass/fail). No manual inspection of logs or output.
- **Timely**: Tests are written close to the production code they verify.
```

## Rules

Rules 和 CLAUDE.md 文件本质相同，每次对话都会加载到 System Prompt。区别在于：CLAUDE.md 偏向项目信息（"这是什么项目、怎么构建"），Rules 偏向行为约束和编码规范（"拒绝蓝紫色主题"、"所有函数必须有 JSDoc 注释"）。

**Rules 的三个层级（和 CLAUDE.md 一样）：**

| 层级 | 位置 | 用途 |
|------|------|------|
| **用户级别** | `~/.claude/rules/` | 你个人的全局编码偏好 |
| **项目级别** | `.cursor/rules` 或项目根目录 | 团队共同遵守的规则（提交到 git） |
| **本地级别** | `.claude/rules/*.local.*` | 本地覆盖规则（不提交） |

**从哪找现成的 Rules 模板：**

Cursor 官方和社区维护了大量现成的 Rules 模板，覆盖各种技术栈和场景：

- **Cursor Directory**：[cursor.directory](https://cursor.directory/) - 官方推荐的 Rules 和 MCP 服务器目录，按框架和语言分类
- **awesome-cursorrules**：[GitHub](https://github.com/PatrickJS/awesome-cursorrules) - 社区维护的配置文件集合
- **cursorrules.org**：专门的 Rules 模板站，可以直接复制粘贴

**典型 Rules 内容示例：**

```markdown
# 代码风格
- 使用 TypeScript strict 模式
- 组件优先使用函数式而非 class
- 错误处理使用 Result 类型而非异常

# 禁止
- 不要使用 any 类型
- 不要使用蓝紫色主题
- 提交前必须运行 `bun test`

# 命名规范
- React 组件用 PascalCase
- 工具函数用 camelCase
- 常量用 UPPER_SNAKE_CASE
```

**2026 年新增：** Cursor 在 v0.43+ 加入了 `/rules` CLI 命令，可以直接在终端创建和编辑 Rules，不需要手动打开文件。

## Claude Code 配置目录结构

Claude Code 的配置采用三级覆盖系统（前面讲的 CLAUDE.md 和 Rules 的层级就来自这里）：

**用户级别** (`~/.claude/`)：
```
~/.claude/
├── CLAUDE.md                    # 用户全局 CLAUDE.md
├── rules/                       # 用户全局 Rules
├── settings.json                # 全局设置（模型、权限等）
├── plugins/                     # 已安装的插件
├── agents/                      # 用户自定义 Agent
└── projects/<project>/memory/   # 各项目的记忆文件
```

**项目级别** (`.claude/`)：
```
<项目根目录>/.claude/
├── settings.json                # 项目级别设置
├── agents/                      # 项目专用 Agent
├── commands/                    # 项目自定义命令
└── skills/                      # 项目专用 Skills
```

**本地级别** (`.claude/*.local.*`)：
- `settings.local.json`、`CLAUDE.local.md`、`rules.local.*` 等
- 这些文件优先级最高，但**不应提交到 git**（加入 `.gitignore`）
- 用于本地环境特有的配置（如本地数据库端口、API 密钥等）

## IDE 和终端联动

在你习惯的 IDE 中，下载 Claude Code 插件（最新版本），然后在终端中输入 `/config` 搜索 IDE，把 Auto-Connect to IDE 打开。在 IDE 中选中你的代码，Claude Code 终端会显示已经被选中的代码行数，或者被选中的代码文件。

## MCP

从上面的例子我们可以看到，如果要让 AI 大模型了解最新的信息，必须使用 Function Calling 调用工具，并且把工具返回的信息给带上。但是并不是所有的 Agent 工具都会用 Function Calling，像比较早期的 Cline 就是用的 XML 格式返回，XML 工具调用，在那个时候提出了 MCP。当然 MCP 不只是工具调用，还有 `prompts` 和 `resources` 等概念，当然这些很多工具都没有用到。

如果要详细从零了解 MCP 除了看官网，还可以看我这个，我这里不止有时序图、概念讲解，还有完整的最小化 Python 代码实现。`https://github.com/young1lin/minimal-mcp`


## 允许所有权限（生产勿用）

允许这个前，先说明，生产上不要使用这个，明确需要禁止 `rm -rf /` 这种命令出现，如果你 Fetch 网站有提示词注入，触发了这个，你的整个电脑都被 Claude Code 删除了。

有两种方式配置允许所有权限，一种是 `claude --dangerously-skip-permissions` 启动会话，一种是 .claude 文件夹下，设置 `settings.local.json` 或者 `settings.json` 文件中，设置下面这样的内容来允许所有权限。

```json
{
  "permissions": {
    "defaultMode": "bypassPermissions",
    "allow": [
        "Bash(ls *)",
        "Bash(cat *)",
        "Bash(echo *)",
        "Bash(cd *)"
    ],
    "deny": [
        "Bash(rm -rf *)"
    ]
  }
}
```

## 纯英文提示词

训练的语料，大部分都是英文，你直接用英文去问，得到的答案一定是比中文好的（编程领域）。能用英文，尽量用英文提问。包括写 SubAgent 的时候，必须要是英文。

## /plugin

自动化测试 Playwright 插件

LSP 语言服务器协议，例如 VSCode 的 LSP 协议，例如 Java、Go、TypeScript 等语言的 LSP，装了这个之后，就能让 Claude Code 能够尽量不去获取无关的代码，例如你一个 Java 文件有三千行代码，但是你只是想改其中一个方法，涉及到的代码最多只有 400 行，如果是按照原来的方式，它会读取整个文件，然后上下文全是这种无意义的内容。装了 LSP 后，它只会读取相关的代码，就是你安装 Ctrl + 鼠标左键，查看相关代码的时候，这个就是 LSP 的作用。目的只是为了让上下文窗口尽可能是有意义的内容占用着，而不是一堆无意义的信息填满了。

## Skills

Skills 的前身 Claude Code 自定义 Command，现在两者同时存在。.claude/commands/ 目录下，放自定义命令， .claude/skills/ 目录下放不同的 Skill，例如 .claude/skills/java-pro/SKILL.md 这里就会写这个技能的元信息，元信息里面只有需要用到的时候，才会调用相应的内容。可以在 .claude/skills/java-pro/examples/ 目录下放示例代码，能让 Claude Code 有个参考样例，能按照你想要的方式写代码。例如强制使用构造器依赖注入，而不是注解。如果有循环依赖的情况下，需要拆分代码。

## 我能休息，Claude Code 不能休息

ralph-loop 插件，让 Claude Code 在你不在的时候持续工作。它的核心思路是：给 Claude Code 一个任务列表，插件会自动循环驱动 Claude Code 执行任务，遇到需要确认的地方自动同意，直到所有任务完成或达到设定的轮次上限。

用法：

1. 安装插件：`claude plugin install ralph-loop`
2. 编写任务文件（Markdown 格式的待办列表）
3. 启动循环：让 Claude Code 按照任务文件逐项执行
4. 设置合理的轮次上限，避免无限循环消耗 Token

适用场景：批量重构、大规模测试编写、多文件迁移等重复性高但需要 AI 判断的任务。你下班前启动，第二天早上来看结果。注意：使用前务必做好 git 提交，方便回退。


## Hooks

Hooks 是用户自定义的 Shell 命令或 LLM Prompt，在 Claude Code 生命周期的特定节点自动执行。你可以理解为"事件监听器"。

**核心 Hook 事件：**

| 事件 | 触发时机 | 典型用途 |
|------|---------|---------|
| `SessionStart` | Claude Code 启动时 | 环境检查、加载配置 |
| `UserPromptSubmit` | 用户发送消息后 | 输入校验、日志记录（本项目就在用这个 Hook，每次对话都会统计字数和分析） |
| `PreToolUse` | Claude 执行工具之前 | 拦截危险操作（如阻止 `rm -rf`）、自动审批特定工具 |
| `PostToolUse` | 工具执行完成后 | 自动格式化代码、运行 lint |
| `Stop` | Claude 完成回复时 | 自动提交、发送通知 |
| `SubagentStop` | SubAgent 完成时 | 收集子任务结果 |
| `TaskCompleted` | 任务完成时 | 清理临时文件 |

**配置方式：** 在 `.claude/settings.json` 或 `~/.claude/settings.json` 中配置。Hook handler 接收 JSON 格式的上下文数据，可以根据工具名称、参数等条件来匹配触发。

**实际例子：** 比如你想在每次 Claude 编辑文件后自动运行 `go fmt`，就可以配置一个 PostToolUse Hook，匹配 `Edit` 和 `Write` 工具，执行格式化命令。


## Headless 用法

Headless 用法就是不显示任何界面，直接在后台运行。-c 表示 continue，--agent 表示使用指定的 Agent。

```bash
claude -p "你好你是谁？"

claude -c -p "我上一句说的什么？"

claude -p --agent code-analyzer "分析这段代码 print('test')"
```

你可以看到，这个很容易就和 Code Review 结合到一起，配合 Git 的 Hook 能自动检测本次变更的代码，进行代码审核。

## 自动化

Vibe Kanban 可以直接在网页中，和 Claude Code、CodeX、Copilot-CLI 进行交互，对话，编写 Kanban 待办事项，拖动。

## 中转

假设你有 Gemini Pro、Stepfun 阶跃星辰的 Code Plan（他们后续会推出）、ChatGPT 的订阅，但是它们都不支持 Anthropic 协议，他们只支持兼容 OpenAI 格式的协议。这个时候分两种情况，

1. Gemini Pro、ChatGPT 订阅等，需要先通过 Claude Relay Service，将 Access Token 获取到，并且绑定到这里。具体怎么绑定，我建议直接问 AI。
2. 只提供了 OpenAI 格式协议的，例如 Stepfun，上面第一步获取到的都是自家的格式，都可以通过 Claude Code Router 来中转，把请求转换成 OpenAI 格式，再发送到对应的 API 地址。

还有一种就是 Gemini Pro 通过 Antigravity 来使用 Claude Opus 4.6 或者 Gemini 3 Pro 模型，想直接通过 Claude Code 使用，可以下载 Antigravity Tools 这个开源的工具 `https://github.com/lbjlaq/Antigravity-Manager`，如何使用，直接问 AI。

## CLAUDE.md —— 项目的"宪法"

CLAUDE.md 是 Claude Code 最重要的配置文件，没有之一。每次对话开始时，Claude Code 会自动读取 CLAUDE.md 并加入 System Prompt。你可以理解为：这是你和 AI 之间的"项目宪法"，告诉它这个项目是什么、怎么工作、有什么规矩。

**CLAUDE.md 的三个层级：**

| 层级 | 位置 | 优先级 | 用途 | 是否提交 git |
|------|------|--------|------|-------------|
| **用户级别** | `~/.claude/CLAUDE.md` | 最低 | 你个人的全局偏好（所有项目生效） | 否 |
| **项目级别** | `<项目根目录>/CLAUDE.md` | 中 | 项目特定的规则和信息 | **是**（团队共享） |
| **本地级别** | `.claude/CLAUDE.local.md` | 最高 | 本地覆盖规则（不同步给团队） | 否（加入 .gitignore） |

加载顺序：先读用户级别，再读项目级别，最后读本地级别。后加载的内容优先级更高，可以覆盖前面的设置。

**典型使用场景：**
- **用户级别**：`~/.claude/CLAUDE.md` 写你个人的编码风格偏好，例如"我喜欢用 const 而非 let"、"测试文件用 .spec.ts 后缀"
- **项目级别**：项目根目录的 `CLAUDE.md` 写团队共识，例如项目结构、构建命令、技术栈
- **本地级别**：`.claude/CLAUDE.local.md` 写你本地环境特有的东西，例如"我的 PostgreSQL 端口是 5433 不是默认的 5432"

**应该写什么：**

- **项目概述**：一句话说明项目是什么，例如"这是一个基于 Spring Boot 的电商后端，使用 PostgreSQL + Redis"
- **项目结构**：关键目录和文件的用途说明
- **构建/测试命令**：`mvn test`、`go test ./...`、`bun test` 等，Claude 会直接使用这些命令
- **编码规范**：例如"使用构造器注入而非 @Autowired"、"错误处理使用 Result 类型而非异常"
- **常见陷阱**：项目特有的坑，例如"数据库迁移必须用 Flyway，不要手动改表结构"

**不应该写什么：**

- 不要写太长。Claude 能可靠遵循大约 150-200 条指令，System Prompt 已经用了约 50 条。每写一行，问自己："去掉这行，Claude 会犯错吗？"如果不会，就删掉
- 不要写显而易见的内容（"代码要有注释"这种）
- 不要把完整的 API 文档塞进去，用指针指向文档位置即可

**和 Rules 的区别：**

CLAUDE.md 偏向项目信息和工作流程（"这个项目是什么、怎么构建"），Rules 偏向行为约束（"不要用蓝紫色主题"、"提交前必须跑测试"）。两者都会加载到 System Prompt，但 CLAUDE.md 一般提交到 git 供团队共享，Rules 可以有 local 版本不提交。

**最佳实践：** 像对待代码一样对待 CLAUDE.md——出了问题就检查它，定期精简，通过观察 Claude 的行为来验证改动是否生效。把它提交到 git，让团队一起维护，这个文件的价值会随时间复利增长。

## Plan Mode 实操

Plan Mode 是 Claude Code 最核心的工作流，Boris Cherny 原话："Most sessions start in Plan mode."

**激活方式：**

- 按 `Shift+Tab` 两次（Normal → Auto-Accept → Plan）
- 或者直接输入 `/plan` 命令（v2.1.0+ 新增）

**Plan Mode 下 Claude 会做什么：**

1. **探索（Explore）**：只读操作，用 Glob、Grep、Read 工具扫描 codebase，理解项目结构和现有代码。大范围搜索时会自动调用 Explore SubAgent（Haiku 驱动，省 Token）
2. **规划（Plan）**：基于探索结果，写出详细的实现方案——改哪些文件、按什么顺序、每步做什么
3. **你审核方案**：这是"人在循环中"的关键环节。你可以要求修改方案、追问细节、或者直接否决
4. **切回正常模式执行**：方案确认后，按 `Shift+Tab` 切回 Normal 或 Auto-Accept 模式，Claude 按照方案执行

**什么时候该用 Plan Mode：**

- 多文件修改（涉及 3 个以上文件）
- 不确定实现方案时（让 Claude 先探索再建议）
- 重构、架构调整等高风险操作
- 新接手一个不熟悉的 codebase

**什么时候不需要：**

- 单文件小改动（修个 bug、改个变量名）
- 你已经明确知道怎么改，只需要 Claude 帮你写代码

**完整工作流示例：**

```
1. Shift+Tab × 2 进入 Plan Mode
2. 输入："我需要给用户模块添加邮箱验证功能，查看当前用户模块的实现"
3. Claude 探索 codebase，找到相关文件，给出方案
4. 你审核方案，提出修改意见："验证邮件用异步发送，不要阻塞注册流程"
5. Claude 修改方案
6. 你确认，Shift+Tab 切回 Normal 模式
7. Claude 按方案逐步实现
8. 每完成一步，测试 + git commit（存档点）
```

## Context Engineering —— 上下文工程

前面讲了那么多概念——CLAUDE.md、MCP、Skills、SubAgent、LSP、Rules——它们本质上都在解决同一个问题：**让 200k Token 的上下文窗口里，装的全是有用的信息**。

这就是 Addy Osmani 提出的 Context Engineering（上下文工程）。不是写更多的 Prompt，而是**精心设计 Claude 能看到什么**。

**上下文的来源：**

| 来源 | 什么时候加载 | 作用 |
|------|------------|------|
| CLAUDE.md | 每次对话自动加载 | 项目基础信息，永远在场 |
| Rules | 每次对话自动加载 | 行为约束 |
| MCP | 工具调用时按需加载 | 外部数据（数据库、Figma、API 文档等） |
| Skills | 匹配到场景时按需加载 | 专业能力（代码风格、测试模式等） |
| SubAgent | 被主 Agent 调用时独立运行 | 拆分复杂任务，避免主上下文膨胀 |
| LSP | 代码跳转时精准加载 | 只读相关代码，不读整个文件 |
| Memory | 每次对话自动加载 MEMORY.md | 跨对话经验积累 |

**核心原则：按需加载，避免浪费。** 一个 3000 行的 Java 文件，如果你只改其中一个方法，LSP 让 Claude 只读 400 行相关代码。一个复杂的重构任务，拆成 SubAgent 各自处理，不会把主对话的上下文撑爆。Figma 的设计稿信息，只在 Plan Mode 探索阶段通过 MCP 拉取，不会常驻上下文。

**一句话总结：** 你的上下文质量决定了 AI 的输出质量。垃圾进，垃圾出。

## Git 工作流 —— 提交即存档

Claude Code 天然支持 git 操作。文章前面说"将提交视为游戏中的存档点"，这里展示怎么做。

**基本节奏：**

```
写代码 → 测试通过 → git commit → 继续下一步
写代码 → 测试通过 → git commit → 继续下一步
...
```

每个小步骤完成后立刻提交。如果后面 Claude 写崩了，你可以 `git diff` 查看变更，`git checkout .` 回退到上一个存档点。

**在 Claude Code 中使用 git：**

- 直接告诉 Claude："提交当前变更"，它会自动 `git add` 相关文件并生成 commit message
- 或者使用 `/commit` 命令（如果安装了对应 Skill）
- Claude 生成的 commit message 通常质量不错，但建议你过一眼

**配合 /rewind 的恢复策略：**

如果 Claude 在多轮对话后跑偏了：
1. 先 `git log` 看最近的提交
2. 如果代码没问题只是对话跑偏 → 用 `/rewind` 回退对话
3. 如果代码也有问题 → `git checkout .` 回退代码 + `/rewind` 回退对话
4. 这就是为什么每一步都要提交——你有回退的余地

**重要原则：** 不要让 Claude 一口气改十个文件再提交。小步提交，每个 commit 只做一件事。

## 图片/截图支持

Claude Code 支持直接粘贴图片到对话中。快捷键是 `Alt+V`（Windows/Linux）或 `Option+V`（macOS）。

**适用场景：**

- **前端 UI Bug**：截图粘贴，告诉 Claude "这个按钮的间距不对，帮我修"
- **设计稿对比**：截图 Figma 设计稿，让 Claude 对比当前实现和设计稿的差异
- **错误截图**：浏览器控制台的报错截图、终端的错误输出截图
- **架构图理解**：粘贴架构图让 Claude 理解系统设计

配合 Figma MCP 和 Playwright 插件，可以实现完整的前端开发闭环：Figma 获取设计信息 → Claude 编码实现 → Playwright 截图验证 → 对比差异 → 修正。

## Memory —— 跨对话持久记忆

Claude Code 有一个自动记忆系统。每个项目有独立的记忆目录：

```
~/.claude/projects/<project>/memory/
├── MEMORY.md          # 主记忆文件，每次对话自动加载到 System Prompt
├── debugging.md       # 按主题组织的详细笔记
├── patterns.md        # 项目模式和约定
└── ...
```

**MEMORY.md 和 CLAUDE.md 的区别：**

- **CLAUDE.md**：你写给 Claude 的指令（"项目用什么技术栈、怎么构建"）
- **MEMORY.md**：Claude 写给自己的笔记（"上次调试发现 XX 模块有 YY 问题、ZZ 方法有效"）

**工作方式：** Claude 在工作过程中会自动记录有价值的发现——比如踩过的坑、有效的解决方案、项目特有的模式。下次对话时，这些记忆会被加载，避免重复犯错。

**注意事项：**
- MEMORY.md 超过 200 行会被截断，保持精简
- 按主题拆分成多个文件（debugging.md、patterns.md），从 MEMORY.md 中链接过去
- 如果发现记忆中的内容过时了，可以手动编辑或让 Claude 更新

# TDD 不再是口号


# 数据安全

Claude 协议中明确说明了，非企业级、Max 用户，对话数据会被拿去训练。虽然会做数据清洗，把敏感数据清洗掉，但是还是会存在一定风险，所以能不在对话中暴露配置信息就不要暴露，能用环境变量就别直接写。当然，国内的 GLM 也明确写了，你的对话数据会被保存，并且拿去训练。如果你在大企业，对数据安全有极高要求，那就只能内网部署 Stepfun-3.5-Flash 这样的截止 2026年2月6日开源 SOTA 模型，内部使用。要用 WebSearch、WebFetch、图片识别这三个核心 Function，那就只能自己在服务端拦截，自己写代理拦截，并且返回了，或者用 Claude Code Router 来拦截。

# 上下文之代码质量

由于工具只能通过加载整个代码文件，或者 LSP 的方式（当前 Java 支持不是很好）来获取相关的 codebase 信息，所以你的代码质量，模块化，分层没做好，Claude Code 的输出也不会好到哪里去。在之前，大模型可以参考你的代码，来写相似风格的代码，现在需要你控制输出的代码，自己保证代码质量。不管是通过 Skill、Rule、CLAUDE.md。

# 扩展知识

林亦的多 Agent 样例项目，23年的多 Agent 开发项目。
