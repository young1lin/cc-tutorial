# Chapter 27: Addy Osmani 的 2026 AI 工作流

## 学习目标

完成本章后，你将能够：

- 理解 Google Chrome 工程师的 AI 编程工作流
- 掌握"AI 辅助工程"的核心原则
- 学习从规划到编码到测试的完整流程
- 应用多模型使用的策略
- 建立健康的 AI 辅助开发习惯

## 前置知识

- [Chapter 5: 探索/计划/编码/提交循环](../module-02-core-workflows/chapter-5-gold-workflow.md)
- [Chapter 25: AI 辅助 vs AI 自动化](../module-06-llm-limitations/chapter-25-assisted-vs-automated.md)
- Git 和版本控制基础

---

## 27.1 Addy Osmani 简介

### 27.1.1 谁是 Addy Osmani

```
┌─────────────────────────────────────────────────────────────┐
│                    Addy Osmani                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  身份：                                                     │
│  - Google Chrome 团队资深工程师                             │
│  - 知名技术作家和演讲者                                      │
│  - Web 性能和开发者工具专家                                 │
│  - 多本 O'Reilly 书籍作者                                   │
│                                                             │
│  专长：                                                     │
│  - Web 性能优化                                             │
│  - 开发者工具                                               │
│  - 工程最佳实践                                             │
│  - AI 辅助编程                                             │
│                                                             │
│  为什么重要：                                               │
│  - 在 Google 内部大量使用 AI 工具                           │
│  - 一年多的实战经验总结                                     │
│  - 代表了资深工程师的成熟观点                               │
│  - 强调"AI 辅助"而非"AI 自动化"                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 27.1.2 核心理念：AI 辅助工程

```typescript
/**
 * Addy Osmani 的核心理念
 */

const CORE_PHILOSOPHY = {
  // 不是什么
  not: `
    ❌ AI 自动化工程
    - AI 做所有事
    - 工程师不参与
    - 无人负责
  `,

  // 是什么
  is: `
    ✅ AI 辅助工程
    - AI 是强大的配对程序员
    - 工程师是导演
    - 人机协作
  `,

  // 关键区别
  keyDifference: `
    "AI coding assistants are game-changers,
     but getting great results requires skill and structure."

    "Think of an LLM pair programmer as
     'over-confident and prone to mistakes'."
    - Simon Willison
  `
};

/**
 * Addy 的观察
 */
const addyObservation = `
在 Anthropic，工程师们大量采用 Claude Code：
今天 Claude Code 约 90% 的代码是由 Claude Code 自己编写的。

但这不是说工程师不重要。
相反，工程师的角色从"编码者"转变为"导演"。

关键：清晰的指导、上下文、监督。
`;
```

---

## 27.2 工作流第一阶段：明确规划

### 27.2.1 规格优先

```typescript
/**
 * Addy: 不要直接向 LLM 投掷愿望
 */

/**
 * ❌ 常见错误：直接开始编码
 */
const commonMistake = `
用户：帮我实现用户认证功能
AI：[开始生成大量代码]
结果：可能不符合需求，代码混乱
`;

/**
 * ✅ 正确方式：先制定规格
 */
const correctApproach = `
Step 1: 头脑风暴规格
  - 描述想法
  - 让 AI 迭代提问
  - 完善需求和边界情况

Step 2: 编写 spec.md
  - 需求
  - 架构决策
  - 数据模型
  - 测试策略

Step 3: 生成项目计划
  - 将实现分解为任务
  - 小型、可管理的任务
  - 逻辑顺序
`;

/**
 * spec.md 示例
 */
// spec.md
```markdown
# 用户认证功能规格

## 需求

### 功能需求
- 用户可以注册新账户
- 用户可以使用 email/password 登录
- 支持"记住我"功能
- 支持密码重置

### 非功能需求
- 响应时间 < 200ms
- 支持每秒 1000 次登录请求
- 安全存储密码（bcrypt）
- JWT Token 认证

## 架构决策

### 技术选择
- 后端: Node.js + Express
- 数据库: PostgreSQL
- 认证: JWT
- 密码哈希: bcrypt (salt rounds: 10)

### API 设计
\`\`\`
POST   /api/auth/register    注册
POST   /api/auth/login       登录
POST   /api/auth/logout      登出
POST   /api/auth/refresh     刷新 token
POST   /api/auth/forgot     忘记密码
POST   /api/auth/reset       重置密码
\`\`\`

## 数据模型

### User 表
\`\`\`sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
\`\`\`

### Session 表
\`\`\`sql
CREATE TABLE sessions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  token VARCHAR(500) NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
\`\`\`

## 测试策略

### 单元测试
- 密码验证逻辑
- Token 生成和验证
- 输入验证

### 集成测试
- 注册流程
- 登录流程
- Token 刷新

### 边界情况
- 重复 email 注册
- 错误密码
- 过期 token
- 无效 email 格式
- SQL 注入测试

## 安全考虑

### 密码策略
- 最少 8 个字符
- 必须包含大小写字母和数字
- bcrypt 哈希（10 轮）

### Token 安全
- 短期 access token (15 分钟)
- 长期 refresh token (7 天)
- HTTPOnly cookies
- CSRF 保护

### 已知威胁
- 暴力破解 → 速率限制
- 会话劫持 → HTTPOnly + Secure
- SQL 注入 → 参数化查询
```;

/**
 * Les Orchard 的比喻
 */
const waterfallMetaphor = `
这就像"15 分钟的瀑布模型"：

传统瀑布模型（问题）：
- 规格阶段：几个月
- 设计阶段：几个月
- 实现阶段：几个月

AI 辅助的"快速瀑布"：
- 规格阶段：15 分钟
- 设计阶段：5 分钟
- 实现阶段：AI 加速完成

关键：前期的结构化规划让后续编码更顺畅。
`;
```

### 27.2.2 迭代完善计划

```typescript
/**
 * 与 AI 共同完善计划
 */

/**
 * Step 1: 让 AI 提问
 */
user: `
  我想实现一个用户评论功能

  请问我问题，帮助我们完善需求
`;

ai: `
  我有以下问题：

  1. 评论是否需要审核？
  2. 支持嵌套评论吗？
  3. 评论有字数限制吗？
  4. 支持编辑和删除吗？
  5. 需要评论通知吗？
  6. 如何处理垃圾评论？
  7. 支持匿名评论吗？
`;

/**
 * Step 2: 回答问题，迭代完善
 */
user: `
  回答：
  1. 是的，需要审核后才能显示
  2. 暂不支持嵌套
  3. 最多 1000 字
  4. 支持编辑（5分钟内）和删除（作者和管理员）
  5. 需要邮件通知被回复的评论
  6. 使用 Akismet 检测垃圾评论
  7. 不支持匿名，必须登录
`;

/**
 * Step 3: 生成最终规格
 */
ai: [基于回答生成详细的 spec.md]

/**
 * Step 4: 生成项目计划
 */
user: "基于上面的规格，生成实现计划"

ai: `
  # 实现计划

  ## Phase 1: 数据层 (1-2 天)
  - [ ] 设计数据库 schema
  - [ ] 创建 migration
  - [ ] 实现 Model 层

  ## Phase 2: API 层 (2-3 天)
  - [ ] 实现评论 CRUD 端点
  - [ ] 实现审核工作流
  - [ ] 实现通知系统
  - [ ] 集成 Akismet

  ## Phase 3: 前端 (3-4 天)
  - [ ] 评论列表组件
  - [ ] 评论表单组件
  - [ ] 审核界面
  - [ ] 通知设置

  ## Phase 4: 测试 (1-2 天)
  - [ ] 单元测试
  - [ ] 集成测试
  - [ ] E2E 测试

  ## Phase 5: 部署 (1 天)
  - [ ] CI/CD 配置
  - [ ] 监控设置
  - [ ] 文档更新
`;
```

---

## 27.3 工作流第二阶段：小型迭代

### 27.3.1 分解工作

```typescript
/**
 * Addy: 范围管理就是一切
 */

/**
 * ❌ 错误：一次性生成大量代码
 */
const badApproach = `
user: "实现完整的电商系统"

AI 问题：
- 上下文超出范围
- 容易混乱
- 难以理解生成的代码
- 可能不一致和重复

结果："就像 10 个开发者在没有沟通的情况下工作"
`;

/**
 * ✅ 正确：分解为小任务
 */
const goodApproach = `
user: "让我们实现计划中的 Step 1：设计数据库 schema"

完成后：
user: "现在实现 Step 2：创建 User Model"

再然后：
user: "现在实现 Step 3：实现注册端点"
`;

/**
 * 每个小任务的特点
 */
const taskCharacteristics = {
  size: `
    小到：
    - AI 可以在上下文中处理
    - 你可以理解生成的代码
    - 容易测试和验证
  `,

  focused: `
    专注：
    - 一个函数
    - 一个 bug 修复
    - 一个功能
  `,

  independent: `
    独立：
    - 可以单独测试
    - 减少依赖
    - 容易回滚
  `
};

/**
 * 结构化的 Prompt 计划文件
 */
// prompt-plan.md
```markdown
# 用户认证 - Prompt 计划

## Task 1: 数据库 Schema
实现 User 和 Session 表的 schema。

## Task 2: User Model
创建 User 类，包含注册、登录方法。

## Task 3: 注册端点
实现 POST /api/auth/register

## Task 4: 登录端点
实现 POST /api/auth/login

## Task 5: JWT 工具
实现 Token 生成和验证。

## Task 6: 中间件
实现认证中间件。

## Task 7: 密码重置流程
实现忘记密码和重置密码。

## Task 8: 测试
为所有功能编写测试。
```
```

### 27.3.2 TDD 方法

```typescript
/**
 * Addy: AI 在有明确目标时表现最好
 */

/**
 * TDD 循环与 AI
 */
const tddWithAI = {
  // Step 1: 编写/生成测试
  step1: `
    user: "为登录功能编写测试"
    ai: [生成测试用例]
  `,

  // Step 2: 确认测试失败
  step2: `
    user: "运行测试，确认它们失败"
    ai: [运行测试，显示失败]
  `,

  // Step 3: 编写实现代码
  step3: `
    user: "编写代码让测试通过"
    ai: [实现代码，运行测试，迭代]
  `,

  // Step 4: 测试通过后提交
  step4: `
    user: "测试通过了，提交代码"
    ai: [创建 commit]
  `
};

/**
 * Addy 的观察
 */
const addyObservation = `
那些从 AI 编码代理中获得最多收益的人，
往往是那些有强大测试实践的人。

有良好测试套件的项目：
- AI 可以快速"飞过"项目
- 测试套件是安全网
- AI 有信心（因为测试通过）

没有测试的项目：
- AI 可能盲目假设一切正常
- 错误可能很晚才发现
`;

/**
 * 测试作为反馈循环
 */
const testingFeedbackLoop = `
编写代码 → 运行测试 → 发现失败 → 修复 → 再次测试

AI 擅长：
- 快速迭代
- 根据测试反馈调整
- 持续改进直到成功

关键：测试必须存在！
`;
```

---

## 27.4 工作流第三阶段：提供上下文

### 27.4.1 上下文打包

```typescript
/**
 * Addy: LLM 只和你提供的上下文一样好
 */

/**
 * 需要提供的上下文
 */
const contextNeeded = {
  // 1. 相关代码
  code: `
    展示需要修改的代码
    展示需要参考的代码
    展示相关模块
  `,

  // 2. 技术约束
  constraints: `
    性能要求
    兼容性要求
    安全要求
  `,

  // 3. 已知陷阱
  pitfalls: `
    要避免的方法
    已知的 bug
    性能瓶颈
  `,

  // 4. 首选方法
  preferences: `
    代码风格
    设计模式
    库的选择
  `
};

/**
 * "Brain Dump" 技巧
 */
const brainDump = `
在编码前，做一次"brain dump"：

包含：
- 高层目标
- 不变量
- 好的解决方案示例
- 要避免的方法

示例：
\`\`\`
我要实现一个高效的用户查找功能。

目标：
- 支持模糊搜索
- 响应时间 < 100ms
- 支持 100万+ 用户

不变量：
- 始终返回有效用户
- 不暴露已删除用户

好方案示例：
- 使用 PostgreSQL 全文搜索
- 使用 trigram 索引

要避免：
- LIKE 查询（太慢）
- 正则表达式（太慢）
- 前端过滤（数据量大时不行）
\`\`\`
`;

/**
 * 上下文工具
 */
const contextTools = {
  // Claude Projects
  claudeProjects: `
    可以导入整个 GitHub 仓库
    自动包含相关文件
  `,

  // Cursor / Copilot
  ideAssistants: `
    自动包含打开的文件
    感知项目结构
  `,

  // Context7 (MCP)
  context7: `
    智能上下文管理
    自动选择相关文件
  `,

  // 手动复制
  manualCopy: `
    对于小段代码
    对于特定文档
    对于 API 文档
  `
};

/**
 * 自动化工具
 */
const automationTools = {
  // gitingest
  gitingest: `
    将代码库"转储"为文本
    AI 可以快速读取
  `,

  // repo2txt
  repo2txt: `
    类似 gitingest
    生成文本包
  `
};
```

### 27.4.2 Claude Skills 的潜力

```typescript
/**
 * Addy: Claude Skills 将脆弱的提示转变为耐用和可重用的
 */

/**
 * 什么是 Claude Skills
 */
const claudeSkills = {
  concept: `
    将指令、脚本和领域专业知识
    打包成模块化能力

    当请求匹配 Skill 时
    工具自动应用它
  `,

  benefits: `
    ✅ 更可靠的结果
    ✅ 上下文感知
    ✅ 可重用
    ✅ 团队知识编码
    ✅ 一致的过程
  `
};
```

---

## 27.5 工作流第四阶段：选择合适的模型

### 27.5.1 多模型策略

```typescript
/**
 * Addy: 不是所有编码 LLM 都相等
 */

/**
 * 模型的"个性"
 */
const modelPersonalities = {
  claude: `
    特点：
    - 详细、深思熟虑的回答
    - 优秀的代码审查能力
    - 善于解释推理过程

    适合：
    - 代码审查
    - 架构设计
    - 复杂问题解决
  `,

  gemini: `
    特点：
    - 自然、流畅的交互
    - 往往第一次尝试就理解请求
    - 快速响应

    适合：
    - 日常编码
    - 快速原型
    - 对话式开发
  `,

  gpt: `
    特点：
    - 创造性解决方案
    - 广泛的知识
    - 多语言支持

    适合：
    - 探索新技术
    - 创造性任务
    - 跨语言代码
  `
};

/**
 * "模型抢椅子"策略
 */
const modelMusicalChairs = `
如果一个模型卡住或给出平庸的输出，
尝试另一个模型。

示例：

Step 1: Claude 尝试
claude: [输出]

Step 2: 如果不满意，尝试 Gemini
gemini: [不同的输出]

Step 3: 如果仍不满意，尝试 GPT
gpt: [又一个不同的输出]

关键：不同的模型有不同的"盲点"。
`;
```

---

## 27.6 工作流第五阶段：人在循环

### 27.6.1 永远不要盲目信任

```typescript
/**
 * Addy: 我的绝对规则之一
 */

/**
 * Simon Willison 的比喻
 */
const simonWillisonQuote = `
"Think of an LLM pair programmer as
 'over-confident and prone to mistakes'"

它用完全的自信编写代码
- 包括 bug 或废话
- 除非你发现，否则不会告诉你有什么问题
`;

/**
 * 像审查初级开发者一样审查
 */
const reviewLikeJunior = `
对待每段 AI 生成的代码，
就像它来自初级开发者：

1. 通读代码
2. 运行它
3. 根据需要测试
4. 检查边缘情况
5. 审查安全性
6. 验证性能

你必须测试它写的代码！
`;

/**
 * Addy 的实践
 */
const addyPractice = `
我将测试编织到工作流本身：

规划阶段：
- 生成测试列表
- 为每个步骤生成测试计划

实现阶段：
- 指示 AI 在实现任务后运行测试
- 让它调试任何失败

这创造了紧密的反馈循环：
编写代码 → 运行测试 → 修复

AI 擅长这个 - 只要有测试存在。
`;

/**
 * AI 编码成功的条件
 */
const aiCodingSuccess = `
从 AI 编码代理中获得最多收益的人，
往往是那些有强大测试实践的人。

有良好测试套件：
- AI 可以快速"飞过"项目
- 测试套件是安全网
- AI 有信心（因为测试通过）

没有测试：
- AI 可能盲目假设一切正常
- "是的，一切正常！"但实际上破坏了几件事

投资测试 - 它放大了 AI 的有用性。
`;
```

### 27.6.2 AI 辅助代码审查

```typescript
/**
 * Addy: AI 编写的代码需要额外审查
 */

/**
 * 双 AI 审查
 */
const doubleAIReview = `
Claude: [编写代码]
Gemini: "你能审查这个函数的任何错误或改进吗？"

这可以捕获微妙的问题。

关键：不要因为代码是 AI 写的就跳过审查。
AI 编写的代码需要**额外审查**。
`;

/**
 * Chrome DevTools MCP
 */
const chromeDevToolsMCP = `
给代理"眼睛"：
- 检查 DOM
- 获取性能跟踪
- 控制台日志
- 网络跟踪

消除手动上下文切换的摩擦，
允许直接通过 LLM 进行自动化 UI 测试。

Bug 可以基于实际运行时数据以高精度诊断和修复。
`;
```

---

## 27.7 工作流第六阶段：版本控制作为安全网

### 27.7.1 频繁提交

```typescript
/**
 * Addy: 频繁提交是你的保存点
 */

/**
 * 超细粒度的版本控制
 */
const ultraGranularVC = `
每个小任务或每次成功的编辑后，
创建一个清晰的 git commit。

好处：
- 如果 AI 下一步建议引入 bug，
你有最近的检查点可以回滚
- 不会丢失数小时的工作
`;

/**
 * 游戏保存点
 */
const savePoints = `
将提交比作"游戏中的保存点"：

如果 LLM 会话出错，
总是可以回滚到最后一个稳定的提交。

这让用 AI 大胆重构实验的压力小得多。
`;

/**
 * 提交历史作为日志
 */
const commitHistoryAsLog = `
git 历史成为有价值的日志：
- 简要发生了什么变化
- 什么代码是新的

LLM 非常擅长：
- 解析 diffs
- 使用 git bisect 查找 bug
- 遍历提交历史

但这只有在你有整洁的提交历史时才有效。
`;

/**
 * 小提交的好处
 */
const smallCommitBenefits = `
如果 AI 一次性做 5 个更改并破坏了什么，
将它们放在单独的提交中
使得更容易确定哪个提交导致了问题。

一切在一个名为"AI 更改"的巨大提交中？
祝你好运！

自律：完成任务 → 运行测试 → 提交
`;
```

### 27.7.2 Git Worktrees

```typescript
/**
 * Addy: 使用分支或 worktrees 隔离 AI 实验
 */

/**
 * Git Worktrees
 */
const gitWorktrees = `
为新功能启动新的 git worktree。

这让你可以：
- 在同一仓库上并行运行多个 AI 会话
- 不会互相干扰
- 稍后可以合并更改

就像每个 AI 任务在自己的沙盒分支中。

成功 = 合并
失败 = 扔掉 worktree，主分支无损失
`;
```

---

## 27.8 工作流第七阶段：定制 AI 行为

### 27.8.1 规则文件

```typescript
/**
 * Addy: 通过提供风格指南、示例和"规则文件"来引导 AI
 */

/**
 * CLAUDE.md 示例
 */
// CLAUDE.md
```markdown
# 项目规则

## 代码风格

### TypeScript
- 使用 4 空格缩进
- 使用 ES 模块（import/export）
- 优先解构导入
- 避免使用 any

### React
- 使用函数组件（非类组件）
- Props 必须有接口定义
- 使用 React hooks
- 在 React 中避免箭头函数
- 使用描述性的变量名
- 代码应该通过 ESLint

## 禁止
- 不要使用 moment.js（使用 dayjs）
- 不要使用 lodash（使用原生方法）
- 不要在组件中直接调用 API
```;

/**
 * Jesse Vincent 的观察
 */
const jesseObservation = `
它非常有效，可以让模型"保持在轨道上"，
减少 AI 偏离脚本或引入我们不想要的模式的倾向。
`;
```

### 27.8.2 内联示例

```typescript
/**
 * Addy: 用内联示例引导 AI
 */

/**
 * 提供示例
 */
const provideExamples = `
如果我希望 AI 以特定的方式编写函数，
首先向它展示代码库中类似的函数：

"这是我们实现 X 的方式，对 Y 使用类似的方法。"

LLM 擅长模仿 - 向它展示一两个示例，
它会以那种方式继续。
`;

/**
 * 有用的规则
 */
const usefulRules = [
  // 规则 1
  {
    rule: "无幻觉规则",
    prompt: "如果不确定或缺少代码库上下文，请要求澄清而不是编造答案。"
  },

  // 规则 2
  {
    rule: "解释推理",
    prompt: "修复 bug 时，总是在注释中简要解释你的推理。"
  }
];
