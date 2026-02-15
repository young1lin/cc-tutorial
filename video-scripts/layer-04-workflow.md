# 第四层：核心工作流

# Vibe Coding vs Spec Coding

用 AI Coding 目的只有一个：**解决实际问题，而不是制造一堆烂代码。**

你需要清楚知道：目前的 LLM 本质上就是个猜词游戏，它并没有真正理解代码。所以人工干预是必须的。可以偷懒，但要写生产代码，你就得清楚地说出你要什么、怎么实现。

**Vibe Coding** —— 凭感觉写 prompt，不给足够清晰的指令 —— 结果就是 AI 泔水。然后你感慨"AI 写的代码真垃圾"。**问题是：你没给够提示词。**

**[Tutorial perspective]** 普通人 + Opus，大部分分数是 Opus 给的；专家 + Opus 能达到更高水平——因为专家自带专业知识，能识别幻觉。你的专业能力决定了 AI 辅助的上限。

## 想法 × 模型 × 提示词 —— 缺一不可的三要素

很多人有个误区：我有好想法，用 AI 就能实现。**错。**

AI 辅助编程的产出质量是一个乘法公式：

```
产出质量 = 想法 × 模型能力 × 提示词精确度
```

注意是**乘法**，不是加法。任何一项为零，整体就是零。

### 模型选择的重要性

用弱模型写代码，就像让一个刚毕业的实习生去架构分布式系统——他能写，但写出来的东西你可能不敢用。

**弱模型的典型问题：**

| 问题 | 表现 | 后果 |
|------|------|------|
| **幻觉** | 编造不存在的 API、过时的方法 | 代码跑不起来，debug 花半天 |
| **上下文理解差** | 忘记前面的约定，前后矛盾 | 代码风格不一致，逻辑混乱 |
| **边缘情况处理差** | 只考虑 happy path | 生产环境各种奇葩 bug |
| **推理能力弱** | 复杂逻辑搞不定 | 简单问题复杂化，或者直接写错 |

**为什么推荐 Opus 4.6？** 不是因为贵，而是因为在编程场景下，它的错误率显著更低。根据 [LM Council Benchmarks](https://lmcouncil.ai/benchmarks)，Opus 4.6 在 coding benchmark 排名第一，SWE-Bench 得分 34.9%（远超 Sonnet 4.5 的 12.9%）。你省下的模型费用，会花在 debug 时间上——而且 debug 时间比 API 费用贵得多。

### 提示词精确度 —— 你说得多清楚，AI 就做多好

LLM 不是你肚子里的蛔虫。它不知道：
- 你的目标平台是什么
- 你的性能要求是什么
- 你之前踩过什么坑
- 你的业务约束是什么

**Vibe Coding（反面教材）：**

```
"帮我写一个日志文件读取器"
```

Claude 会给你一个能跑的代码。但可能：
- 没有处理文件编码问题（UTF-8、GBK、GB2312）
- 没有处理大文件的流式读取（直接 `readAll` 内存爆掉）
- 没有处理文件被其他进程占用的情况
- 没有处理 Windows/Linux 路径差异

**Spec Coding（正确姿势）：**

```
帮我写一个日志文件读取器，要求：

1. 跨平台兼容（Windows + Linux + macOS）
2. 支持流式读取，避免大文件 OOM（日志文件可能 10GB+）
3. 自动检测文件编码（UTF-8、GBK、GB2312 常见编码）
4. 处理文件被占用的情况：
   - Windows 下文件可能被其他进程锁定，需要重试机制
   - 重试 3 次，每次间隔 500ms
5. 支持从文件末尾倒序读取（类似 tail -f）
6. 错误处理：文件不存在、权限不足、磁盘空间不足都要有明确提示
```

你看，这代码写出来能用吗？能用。能直接上生产吗？基本可以。

### 平台差异 —— 跨平台开发的隐形巨坑

这是 Spec Coding 最关键的应用场景之一。你在 macOS 上开发爽得很，一切正常；一部署到 Windows 服务器，各种奇葩问题。

**Windows vs Unix 的经典差异：**

| 差异点 | Windows | Unix/Linux/macOS | 你的代码怎么挂 |
|--------|---------|------------------|----------------|
| **文件锁** | 独占锁，一个进程打开文件，其他进程无法访问 | 共享锁，多个进程可同时读取 | 日志文件被监控程序占用，你的程序读不了 |
| **路径分隔符** | `\` | `/` | 硬编码 `/` 的路径全挂 |
| **换行符** | CRLF (`\r\n`) | LF (`\n`) | 解析配置文件时莫名其妙多出 `\r` |
| **文件名大小写** | 不敏感（`File.txt` = `file.txt`） | 敏感 | 部署到 Linux 找不到文件 |
| **文件权限** | 简单的只读/读写 | rwx 三元组 + ACL | 脚本没有执行权限 |
| **最大路径长度** | 260 字符（除非启用长路径） | 通常 4096 字符 | 嵌套目录太深直接报错 |
| **进程管理** | 没有 fork，CreateProcess 很重 | fork + exec | 多进程架构移植困难 |

**通用问题：**

如果你在 macOS/Linux 上开发，部署到 Windows 服务器，很容易遇到这类问题——你的代码在开发环境跑得好好的，一上线就崩溃。这种问题，如果你不明确告诉 Claude "要支持 Windows 文件锁场景"，它大概率不会处理——因为它的训练数据里，大多数代码示例是 Linux/macOS 环境的。

**正确的提示方式：**

```
这个工具需要跨平台运行（Windows Server + Linux），特别注意：

1. Windows 文件锁：
   - 日志文件可能被其他进程（监控 agent、备份程序）占用
   - 使用 FileShare.ReadWrite 模式打开文件
   - 添加重试机制，避免直接抛异常

2. 路径处理：
   - 使用 Path.Combine 而不是字符串拼接
   - 使用 Path.DirectorySeparatorChar 或直接用 /（.NET 会自动处理）

3. 编码问题：
   - 不要假设 UTF-8，用 EncodingDetector 或尝试多种编码
```

### 边界情况 —— AI 不知道你的业务约束

LLM 只能根据通用知识写代码。你的业务约束、性能要求、安全策略，它一概不知。

**需要明确告诉 AI 的边界情况：**

```
✅ 性能约束：
   "这个接口响应时间不能超过 200ms"
   "数据库查询结果集可能 100 万条，不能全部加载到内存"

✅ 安全约束：
   "用户输入要做 XSS 过滤"
   "SQL 语句必须用参数化查询，禁止拼接"
   "敏感日志要脱敏处理"

✅ 业务约束：
   "金额计算用 BigDecimal，不能用 float/double"
   "订单号生成要保证分布式唯一性"
   "这个操作要记录审计日志"

✅ 兼容性约束：
   "要兼容 Java 8，不能用 Java 17 的新特性"
   "要兼容 MySQL 5.7，不能用 8.0 的新函数"
   "这个 API 要同时支持 JSON 和 XML 响应"
```

### 一句话总结

> **Vibe Coding 是"帮我写个登录功能"；Spec Coding 是"帮我写个登录功能，密码要 bcrypt 加密，登录失败 5 次锁定账号 30 分钟，要记录审计日志，要支持手机号/邮箱两种登录方式，要兼容旧系统的 session 机制"。**

前者你得到的是"能跑"的代码；后者你得到的是"能上线"的代码。

你的专业能力不是体现在"你能写出这些代码"，而是体现在"你知道这些约束条件存在，并能准确传达给 AI"。

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

- 不要写太长。根据 [Claude 官方文档](https://platform.claude.com/docs/en/build-with-claude/context-windows)，上下文窗口接近限制时性能会下降。每写一行，问自己："去掉这行，Claude 会犯错吗？"如果不会，就删掉
- 不要写显而易见的内容（"代码要有注释"这种）
- 不要把完整的 API 文档塞进去，用指针指向文档位置即可

**和 Rules 的区别：**

CLAUDE.md 偏向项目信息和工作流程（"这个项目是什么、怎么构建"），Rules 偏向行为约束（"不要用蓝紫色主题"、"提交前必须跑测试"）。两者都会加载到 System Prompt，但 CLAUDE.md 一般提交到 git 供团队共享，Rules 可以有 local 版本不提交。

**最佳实践：** 像对待代码一样对待 CLAUDE.md——出了问题就检查它，定期精简，通过观察 Claude 的行为来验证改动是否生效。把它提交到 git，让团队一起维护，这个文件的价值会随时间复利增长。

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

## Feedback Loop —— 给 Claude 验证自己工作的方式

这是 Claude Code 之父 Boris Cherny 反复强调的**最重要的一条建议**，甚至比 Plan Mode 还重要。根据 [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices)（Boris Cherny, Anthropic Team）：

> "Correct Claude as soon as you notice it going off track. The best results come from tight feedback loops."

核心思想很简单：**永远给 Claude 一种验证自己工作的方法。** 如果 Claude 能看到自己代码的运行结果——报错信息、测试通过与否、浏览器截图——它的代码质量会提升 2-3 倍。

为什么？因为 LLM 是概率预测，第一次写的代码不一定对。但如果它能看到错误信息，它就能根据实际的报错来修正，而不是凭"猜测"来修。这和人类程序员是一样的——看到报错信息 debug 比盲猜效率高几十倍。

**正确的做法：**

```
✅ "写完后运行测试，把结果贴给我看"
✅ "在浏览器里打开这个页面，截图给我"（配合 Playwright）
✅ "运行 npm run build，看有没有编译错误"
✅ "执行这个 SQL，看返回结果是否正确"

❌ 让 Claude 写完代码就完事，不验证运行结果
❌ 自己手动跑测试但不把结果贴回对话里
```

**验证 prompt 金句（来自 ykdojo 的 45 tips）：**

> "Double check everything, every single claim in what you produced, and at the end make a table of what you were able to verify."

让 Claude 自查它产出的每一条内容，最后列一个验证表。这个 prompt 在生成文档、写技术方案的时候特别有效——Claude 会自己发现并修正问题。

**Feedback Loop 的本质：** 不是你不信任 Claude，而是你给它信息让它做得更好。就像你给初级开发者做 Code Review 一样——你指出问题，他修正，下次就不会犯同样的错。只不过 Claude 的"下次"是在同一个对话里。

# 测试与语言选择

为什么 Go、TypeScript 是 AI Coding 原生语言？跨平台、强类型、测试方便、格式化统一。`go fmt` 一把梭，代码风格不可能乱。

**快快快——编译快、测试快、构建快。** Go 是综合考虑最快、最简单的语言。没有函数式编程那种晦涩玩意儿，对 AI 友好。

没有专门学过的人写函数式编程（Scala、Erlang）是折磨。用 RxJava 写响应式代码，即使你用 Opus 也容易翻车——shutdown hook 执行的时候，永远不关闭，我就被坑过。凡事都有代价：Go 做不到像 Java 那样通过 JavaAgent 运行时插桩做分布式 Tracing，要么手动插桩，要么编译时搞。

> Linus Torvalds 表示 "LLMs are going to help us to write better software, faster"，但 vibe coding "fine for prototypes" 对生产系统 "may be a horrible idea from a maintenance standpoint"（来源：[Slashdot 采访](https://slashdot.org/story/25/12/28/024236/linus-torvalds-weighs-in-on-ai-coding-tools)）。

# 上下文之代码质量

由于工具只能通过加载整个代码文件，或者 LSP 的方式（当前 Java 支持不是很好）来获取相关的 codebase 信息，所以你的代码质量，模块化，分层没做好，Claude Code 的输出也不会好到哪里去。在之前，大模型可以参考你的代码，来写相似风格的代码，现在需要你控制输出的代码，自己保证代码质量。不管是通过 Skill、Rule、CLAUDE.md。

## 代码分层与整洁架构：不是装逼，是生存

你肯定听过 Clean Architecture、洋葱架构、DDD、组件化这些词。有些人觉得这是过度设计，是"企业级 Java 病"。**错。**

在 AI Coding 时代，代码分层不是可选项，是**必选项**。原因很简单：

**Claude Code 按文件读写代码。**

如果你的代码是"大泥球"（Big Ball of Mud）——所有逻辑塞在一个 2000 行的文件里——Claude 每次改任何东西都要读这 2000 行。上下文被垃圾填满，真正有用的信息被挤掉。输出质量必然下降。

反过来，如果你的代码遵循整洁架构（洋葱架构）：

```
                    ┌─────────────────────────────────────┐
                    │           Infrastructure            │
                    │   (DB, HTTP, Message Queue, etc.)   │
                    │  ┌─────────────────────────────┐    │
                    │  │        Use Cases            │    │
                    │  │    (Application Services)   │    │
                    │  │  ┌─────────────────────┐    │    │
                    │  │  │    Domain Entities  │    │    │
                    │  │  │   (Business Logic)  │    │    │
                    │  │  │                     │    │    │
                    │  │  └─────────────────────┘    │    │
                    │  │         ▲                   │    │
                    │  └──────────│───────────────────┘    │
                    │             │ 依赖方向：外 → 内        │
                    └─────────────│─────────────────────────┘
                                  ▼
                           Domain 核心，零外部依赖
```

**核心原则：依赖方向永远指向圆心。**

- 外层（Infrastructure）依赖内层（Use Cases）
- 内层（Use Cases）依赖核心（Domain）
- **Domain 不依赖任何东西**——纯业务逻辑，零框架，零外部依赖

对应的目录结构：

```
internal/
├── domain/       # 纯业务逻辑，零依赖
├── service/      # 用例编排，调用 domain
├── repository/   # 数据访问，实现 domain 接口
└── handler/      # HTTP 处理，调用 service
```

Claude 改 HTTP 层只需要读 `handler/`，改业务逻辑只需要读 `domain/`。上下文利用率高，输出质量自然好。

## 分层对 AI Coding 的三大好处

### 1. 上下文聚焦

好的分层 = 每个文件职责单一。Claude 改一个功能，只需要加载相关的 2-3 个文件，而不是整个项目。

**例子：** 你要给"创建订单"加一个校验规则。
- 好的分层：只加载 `domain/order.go`，改一行，完事
- 大泥球：加载 2000 行的 `order_service.go`，上下文爆炸，Claude 可能改错地方

### 2. Few-shot 天然素材

前面说了"珠玉在前"——给 Claude 看参考样例，输出更精准。

分层架构天然提供这些样例。你要加一个新的 `PaymentService`？告诉 Claude："参考 `OrderService` 的写法"。它看一眼，立马知道：
- 怎么注入 Repository
- 错误处理怎么写
- 日志怎么打

如果没有分层，每个 Service 写法都不一样，Claude 没法学习你的"风格"，只能靠猜。

### 3. 改动范围可控

分层架构的核心是**依赖方向**：外层依赖内层，内层不知道外层的存在。

这意味着你改内层（比如 `domain/`），不会影响外层。改外层（比如 `handler/`），更不会影响内层。

Claude 改代码时，这个特性让它不会"越界"。你让它在 `service/` 层加逻辑，它不会把 SQL 写到 `handler/` 里——因为 `service/` 根本不知道 `handler/` 的存在。

## 组件化：分层的横向切分

分层是纵向切分（按职责），组件化是横向切分（按业务领域）。

```
internal/
├── domain/
│   ├── order/       # 订单领域
│   ├── payment/     # 支付领域
│   └── user/        # 用户领域
├── service/
│   ├── order/
│   ├── payment/
│   └── user/
└── handler/
    ├── order/
    ├── payment/
    └── user/
```

这样做的好处是：**改一个业务领域，只需要动那个领域的文件夹**。

你要重构支付逻辑？`internal/domain/payment/` 和 `internal/service/payment/` 就够了。订单、用户相关的代码一行都不用碰。Claude 的上下文更聚焦，改错其他模块的概率为零。

**组件化的核心原则：高内聚，低耦合。**

- 高内聚：同一个业务领域的代码放一起
- 低耦合：不同领域之间通过接口通信，不直接依赖实现

这和整洁架构（洋葱架构）的理念完全一致：**依赖指向圆心，核心业务不依赖任何外部东西**。

## 不分层、不组件化会怎样？

**[Tutorial perspective]** 我见过太多"先跑起来再说"的项目。一开始一个文件 200 行，挺清晰。三个月后变成 2000 行，全是 if-else。六个月后没人敢动，包括原作者。

AI Coding 加速了这个过程。你让 Claude 加功能，它不会主动重构。它会在那 2000 行里再加 200 行。一年后，你的项目变成一个 5000 行的怪物，Claude 也没法救你。

**解决方案：** 从第一天就分层、组件化。哪怕只有三个文件夹：`domain/`、`service/`、`handler/`。后续实战章节会用 `claude-token-monitor` 项目的演进过程演示这一点——从单文件到分层架构，每一步的考量是什么。

## 语言差异：Go vs Java

Go 的标准项目布局天然鼓励分层：
```
cmd/        # 入口
internal/   # 私有代码，按层组织
pkg/        # 公开库
```

Java 的 Spring Boot 反而容易变成"贫血模型"——所有逻辑塞在 Service 里，Entity 只有一堆 getter/setter。这不是分层，是把数据和行为拆散了。

**[Tutorial perspective]** 如果你是 Java 背景，警惕"贫血 DDD"。Entity 不应该只是数据容器，它应该有自己的行为。`Order.cancel()` 比 `orderService.cancel(order)` 更符合领域模型的本质。


**实战预告：** 第八层实战章节会用 `claude-token-monitor` 项目演示：
- 从单文件脚本到分层架构的演进过程
- 整洁架构（洋葱架构）的实际应用
- 组件化拆分的时机和方法
- 每次重构的触发条件是什么
- 如何在保持功能不变的前提下逐步演进
- 演进前后 Claude Code 输出质量的对比

# 珠玉在前（Few-shot Prompting） —— 有参考样例，输出更精准

LLM 的学习机制有一个核心特性：**上下文学习（In-Context Learning）**。模型不只靠训练数据输出代码，它会实时参考你在对话里给出的所有信息——包括你贴进去的代码片段。这意味着，**你给的参考样例质量越高，它写出来的代码就越贴近你的要求**。

这不是玄学，是 Transformer 架构的工作原理。给它看一个例子，比写三段文字描述"我要什么风格"有效得多。

Gemini 刚出来的时候，拿着自己 **CoT@32**（32次运行取最好）和 GPT-4 **5-shot**（单次运行）的对比，PPT 上表格赢了其他模型。这种"best-of-32 vs single-run"的不对等比较引发社区争议（详见 [Hacker News](https://news.ycombinator.com/item?id=38545663)，本地报告截图见 [Gemini Report Table 2](../research/evidence/gemini-1-report-page8-benchmark-table.png)）。

## 为什么叫"珠玉在前"？

这个成语的本意是：前人已有精彩之作，后来者有所参照。用在 Claude Code 最佳实践上，意思是：**开始写代码之前，先把参考样例放在上下文里**。

没有参考，Claude 靠训练数据里的"平均风格"输出；有参考，Claude 对齐你的具体代码库、你的命名习惯、你的架构模式，写出来的代码直接可用，不需要大改。

## 三种参考来源

### 1. 项目内已有的实现

这是最直接、最有效的方法。

```
❌ "帮我实现一个 OrderService，支持创建订单和查询订单"

✅ "帮我实现一个 OrderService，参考 UserService（src/services/user.service.ts）的写法：
   - 同样使用 Repository 注入
   - 同样的错误处理模式
   - 同样的 DTO 结构"
```

或者更直接，用 `@` 引用文件：

```
参考 @src/services/user.service.ts 的模式，实现一个功能类似的 OrderService
```

Claude 会读取 UserService 的代码，学习你的命名约定、注入方式、异常处理风格，然后写出风格一致的 OrderService。这比任何文字描述都精确。

### 2. 从 GitHub 上找标杆实现

你要做一个功能，但项目里还没有类似的代码。这时可以去 GitHub 找一个质量好的参考实现，贴给 Claude，告诉它"按这个思路来"。

例如要实现一个带超时的重试机制：

```
参考这个实现（来自 resilience4j 官方示例）：
[贴入代码]

按照相同的思路，为我们的 gRPC 客户端实现带指数退避的重试逻辑
```

官方示例、知名开源项目的实现，都是绝佳的"珠玉"。Claude 会理解这些样例的设计意图，而不只是复制粘贴。

### 3. 文档里的示例代码

框架文档里的官方示例，也是有效的参考来源。比如你要实现一个 Spring Security 的自定义过滤器：

```
这是 Spring Security 官方文档里的过滤器示例：
[贴入文档代码]

按照这个结构，为我们的 JWT 验证实现一个自定义过滤器，
注意我们用的是 Spring Boot 3.x，JWT 库是 jjwt 0.12
```

把版本信息同时提供，配合参考代码，能大幅减少 Claude 使用旧 API 的概率。

## 具体技巧

**技巧一：在 CLAUDE.md 里写明样板代码的位置**

```markdown
## 代码样板参考位置
- API 控制器样板：`src/controllers/user.controller.ts`
- Service 层样板：`src/services/user.service.ts`
- 数据库 Repository 样板：`src/repositories/user.repository.ts`
- 测试文件样板：`src/services/__tests__/user.service.test.ts`

实现新功能时，请参考以上对应层级的现有实现风格。
```

这样每次对话开始，Claude 就已经知道该参考哪些文件，不用你每次手动指定。

**技巧二：先让 Claude 读懂现有代码，再让它写新代码**

```
第一步（Plan Mode）：
"读一下 src/services/ 目录下的现有 Service 实现，
理解我们项目的代码风格和架构模式"

第二步：
"好，现在按照这个风格实现 OrderService"
```

两步走比一步到位效果更好，因为 Claude 在第一步里把代码模式内化到了上下文。

**技巧三：把"反例"也提供出来**

```
我不想要这样的写法（下面这个太复杂了）：
[贴入你不想要的代码风格]

我想要这样简洁的写法：
[贴入你期望的风格]

按照第二种写法实现 X 功能
```

正例 + 反例同时给出，Claude 对"边界"的理解会非常清晰，不会往错误方向偏。

## 为什么参考样例比文字描述更有效？

Andrej Karpathy 在 2025 年的技术分享中表达过类似观点。根据他的 [2025 Year in Review](https://karpathy.bearblog.dev/year-in-review-2025/) 和 YC AI Startup School 演讲：

> "Prompts are the new source code"
> "English is the new programming language"

核心观点是：Few-shot 示例（你提供的参考代码）是 prompt 中信息密度最高的部分。你花一百字描述"我要函数式风格、不要可变状态、使用 Option 而不是 null"，还不如直接贴一段你喜欢的代码。代码是最精确的规格说明。

## 注意事项

- **参考代码要代表你的最佳实践**，不要把你想淘汰的旧代码当样例——Claude 会照着学
- **样例不需要太长**，关键是展示你要的模式，通常 50-150 行足够
- **注意样例的时效性**：如果参考代码用的是旧版本 API，要在 prompt 里说明"我们已经升级到 X 版本，请用新 API"

> **一句话总结：让 Claude 看到最好的，它才会写出最好的。你的代码库就是它最好的教材。**
