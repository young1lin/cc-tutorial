# Chapter 26: Boris Power 官方建议

## 学习目标

完成本章后，你将能够：

- 理解 Claude Code 创建者的官方最佳实践
- 掌握 CLAUDE.md 文件的正确使用方法
- 学会自定义 Claude Code 工作流
- 应用 Anthropic 团队验证过的工作模式
- 优化 Claude Code 的配置和权限

## 前置知识

- [Chapter 4: Plan Mode 革命](../module-01-fundamentals/chapter-04-plan-mode.md)
- [Chapter 5: 探索/计划/编码/提交循环](../module-02-core-workflows/chapter-5-gold-workflow.md)
- 基本的命令行操作

---

## 26.1 Boris Power 简介

### 26.1.1 谁是 Boris Power

```
┌─────────────────────────────────────────────────────────────┐
│                    Boris Cherny (Boris Power)                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  身份：                                                     │
│  - Claude Code 的创建者和首席架构师                         │
│  - Anthropic 工程团队负责人                                 │
│  - TypeScript 核心贡献者                                    │
│  - 多个开源项目的作者                                       │
│                                                             │
│  背景：                                                     │
│  - 在 Meta (Facebook) 工作，参与 React 开发                 │
│  - 在 Google 工作，参与 TypeScript 开发                     │
│  - 丰富的编程语言设计和工具开发经验                         │
│                                                             │
│  为什么重要：                                               │
│  - Claude Code 是基于他的实践经验设计                      │
│  - 这些建议来自 Anthropic 内部的大量使用                   │
│  - 经过真实项目的验证                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 26.1.2 官方最佳实践的价值

```typescript
/**
 * 为什么官方建议重要
 */

const OFFICIAL_RECOMMENDATIONS_VALUE = {
  // 1. 来自设计者
  fromCreator: `
    Boris Power 设计了 Claude Code
    他最了解工具的能力和限制
  `,

  // 2. 经过验证
  validated: `
    Anthropic 内部团队每日使用
    在各种代码库、语言、环境中验证
    覆盖从小型脚本到大型系统的场景
  `,

  // 3. 持续更新
  continuouslyUpdated: `
    随着工具演进而更新
    基于用户反馈改进
    反映最新的最佳实践
  `,

  // 4. 权威性
  authoritative: `
    这是"官方"建议
    不是社区猜测或个人经验
    来自源头的可靠信息
  `
};
```

---

## 26.2 定制你的设置

### 26.2.1 创建 CLAUDE.md 文件

```markdown
/**
 * CLAUDE.md 是最重要的配置文件
 *
 * Claude 会在每次会话开始时自动读取
 * 它是提供项目特定"长期记忆"的最佳方式
 */

# 项目名称 CLAUDE.md

## 常用命令

### 构建和测试
- `npm run build` - 构建项目
- `npm run test` - 运行测试
- `npm run lint` - 代码检查

### 开发
- `npm run dev` - 启动开发服务器
- `npm run typecheck` - TypeScript 类型检查

## 代码风格

### 导入
- 使用 ES 模块语法 (import/export)
- 优先解构导入: `import { foo } from 'bar'`
- 避免使用 CommonJS (require)

### 命名
- 组件: PascalCase (UserProfile.tsx)
- 工具函数: camelCase (formatDate.ts)
- 常量: UPPER_SNAKE_CASE (API_BASE_URL)
- 类型/接口: PascalCase (UserData)

### 格式
- 使用 2 空格缩进
- 单引号字符串
- 行尾分号

## 架构

### 目录结构
```
src/
├── components/     # React 组件
├── hooks/          # 自定义 Hooks
├── services/       # API 服务
├── utils/          # 工具函数
├── types/          # TypeScript 类型
└── __tests__/      # 测试文件
```

### 关键文件
- `src/services/api.ts` - API 客户端
- `src/utils/auth.ts` - 认证工具
- `src/types/index.ts` - 全局类型定义

## 工作流

### Git 工作流
- 使用 feature 分支
- 提交前运行 lint 和 typecheck
- PR 需要至少一个审查

### 测试
- 新功能必须包含测试
- 使用 Jest 和 React Testing Library
- 测试覆盖率 > 80%

## 重要提醒

### 安全
- ⚠️ 永远不要在代码中硬编码 API 密钥
- ⚠️ 使用环境变量存储敏感信息
- ⚠️ 审查所有来自用户输入的数据

### 性能
- ⚠️ 避免在渲染循环中创建新函数
- ⚠️ 使用 React.memo 优化重渲染
- ⚠️ 大列表使用虚拟化

### 已知问题
- ⚠️ Date 对象在某些时区有问题 - 使用 dayjs
- ⚠️ 第三方库 X 在生产环境需要特殊配置
```

### 26.2.2 CLAUDE.md 的放置位置

```typescript
/**
 * CLAUDE.md 可以放在多个位置
 */

/**
 * 位置 1: 仓库根目录（最常见）
 */
// 位置: /project/CLAUDE.md
// 用途: 整个项目的通用信息
// 建议: 提交到 git，团队共享

/**
 * 位置 2: 当前工作目录
 */
// 位置: /project/frontend/CLAUDE.md
// 用途: 特定于 frontend 的信息
// 优先级: 高于根目录的 CLAUDE.md

/**
 * 位置 3: 父目录
 */
// 位置: /project/CLAUDE.md (从 /project/frontend 运行时)
// 用途: Monorepo 的共享配置
// 注意: 所有子目录都会继承

/**
 * 位置 4: 用户主目录
 */
// 位置: ~/.claude/CLAUDE.md
// 用途: 全局配置，所有会话
// 建议: 个人偏好，不提交

/**
 * 位置优先级（从高到低）:
 * 1. 当前目录的 CLAUDE.md
 * 2. 父目录的 CLAUDE.md
 * 3. ~/.claude/CLAUDE.md
 */

/**
 * 最佳实践：Monorepo 配置
 */
/my-monorepo/
├── CLAUDE.md              # 共享配置（构建、测试等）
├── .claude/
│   └── settings.json      # 项目特定设置
├── packages/
│   ├── frontend/
│   │   ├── CLAUDE.md      # 前端特定配置
│   │   └── package.json
│   └── backend/
│       ├── CLAUDE.md      # 后端特定配置
│       └── package.json
```

### 26.2.3 优化 CLAUDE.md 内容

```typescript
/**
 * Boris 的建议：迭代优化 CLAUDE.md
 */

/**
 * 常见错误：添加大量内容后不优化
 */

// ❌ 错误的 CLAUDE.md
const badCLAUDEmd = `
# 项目文档

[包含 500 行详细的文档]
[每个细节都有说明]
[Claude 很难记住重点]
`;

// ✅ 好的 CLAUDE.md
const goodCLAUDEmd = `
# 项目概述
[简短的 3-5 句话]

## 常用命令
[最常用的 5-10 个命令]

## 重要提醒
[用 ⚠️ 标记关键信息]

## 代码风格
[最核心的 3-5 条规则]
`;

/**
 * 优化技巧
 */
const OPTIMIZATION_TIPS = {
  // 1. 使用强调标记
  emphasis: `
    使用 "IMPORTANT"、"YOU MUST" 等标记
    提高关键信息的权重

    例如：
    - IMPORTANT: Always run typecheck before committing
    - YOU MUST: Use environment variables for secrets
  `,

  // 2. 保持简洁
  concise: `
    Claude 的上下文有限
    只包含最关键的信息
    详细文档可以链接到其他文件
  `,

  // 3. 结构清晰
  structured: `
    使用一致的格式
    ## 标题层次清晰
    - 列表项明确
  `,

  // 4. 迭代改进
  iterate: `
    观察 Claude 的行为
    如果某条规则经常被违反
    可能需要改写或添加强调
  `
};

/**
 * 使用 # 键快速添加
 */
// 在 Claude Code 中按 # 键
// 输入要添加的内容
// Claude 会自动合并到 CLAUDE.md

// 示例会话：
// You: # 记住：这个项目使用 PostgreSQL，不是 MySQL
// Claude: 已添加到 CLAUDE.md
```

### 26.2.4 配置权限和工具

```typescript
/**
 * 工具权限管理
 */

/**
 * 四种配置方式
 */

// 方式 1: 会话中 "Always allow"
// 当 Claude 请求权限时选择 "Always allow"
// 只在当前会话有效

// 方式 2: 使用 /permissions 命令
// /permissions
// Claude: [显示权限配置界面]

// 方式 3: 手动编辑配置文件
// .claude/settings.json (项目级别)
{
  "allowedTools": [
    "Edit",                    // 允许编辑文件
    "Bash(git commit:*)",     // 允许 git commit
    "Bash(git push:*)"        // 允许 git push
  ]
}

// ~/.claude.json (全局级别)
{
  "allowedTools": [
    "Edit",                    // 个人偏好：总是允许编辑
    "Read"                     // 个人偏好：总是允许读取
  ]
}

// 方式 4: CLI 参数
// claude --allowedTools Edit,Bash(git\\ commit\\:*) --your-prompt

/**
 * 常用工具权限配置
 */
const COMMON_PERMISSIONS = {
  // 安全：总是允许
  alwaysSafe: [
    "Read",                    // 读取文件（安全）
    "Bash(git status)",        // git status（只读）
    "Bash(git log)",           // git log（只读）
    "Bash(git diff)"           // git diff（只读）
  ],

  // 中等：需要审查但通常允许
  moderate: [
    "Edit",                    // 编辑文件（可撤销）
    "Bash(git commit:*)",      // git commit（可撤销）
    "Bash(npm run test:*)",    // 运行测试（安全）
    "Bash(npm run lint:*)"     // 运行 lint（安全）
  ],

  // 危险：需要谨慎
  dangerous: [
    "Bash(rm)",               // 删除文件（危险！）
    "Bash(git push)",         // 推送到远程（需审查）
    "Bash(npm publish)"       // 发布包（需审查）
  ]
};

/**
 * Boris 的建议
 */
const borisRecommendations = `
权限配置原则：

1. 默认安全
   - Claude Code 默认需要权限确认
   - 这是有意的设计选择

2. 逐步放宽
   - 从严格权限开始
   - 根据信任程度逐步放宽

3. 团队共享
   - .claude/settings.json 提交到 git
   - 团队成员共享权限配置

4. 个人偏好
   - ~/.claude.json 用于个人配置
   - 不提交到 git
`;
```

---

## 26.3 给 Claude 更多工具

### 26.3.1 使用 Bash 工具

```typescript
/**
 * 让 Claude 知道你的自定义工具
 */

/**
 * 方法 1: 告诉 Claude 工具名称和用法
 */

// 示例：自定义脚本
// 你有一个脚本: scripts/deploy.sh

// ❌ 效果不好
user: "部署应用"
claude: "我不知道如何部署..."

// ✅ 效果好
user: `
  我有一个部署脚本 scripts/deploy.sh
  用法: ./scripts/deploy.sh [环境]
  例如: ./scripts/deploy.sh staging

  请使用这个脚本部署到 staging 环境
`
claude: [调用脚本并输出结果]

/**
 * 方法 2: 让 Claude 运行 --help
 */
user: "运行 ./scripts/deploy.sh --help 看看用法"
claude: [读取帮助输出并理解]

/**
 * 方法 3: 在 CLAUDE.md 中记录
 */
// CLAUDE.md
## 常用脚本

### 部署
- `./scripts/deploy.sh [env]` - 部署到指定环境
- `./scripts/rollback.sh [env]` - 回滚部署

### 数据库
- `./scripts/db/migrate.sh` - 运行数据库迁移
- `./scripts/db/seed.sh` - 填充测试数据
```

### 26.3.2 使用 MCP (Model Context Protocol)

```typescript
/**
 * MCP 配置方式
 */

/**
 * 配置位置 1: 项目配置 (.mcp.json)
 */
// .mcp.json (提交到 git，团队共享)
{
  "mcpServers": {
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-puppeteer"]
    },
    "sentry": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-sentry"]
    }
  }
}

/**
 * 配置位置 2: 全局配置
 */
// ~/.claude/json (个人配置)
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-filesystem", "/allowed/path"]
    }
  }
}

/**
 * 调试 MCP
 */
// 使用 --mcp-debug 标志启动
// claude --mcp-debug

// 这会显示详细的 MCP 连接信息
// 帮助诊断配置问题

/**
 * 常用 MCP 服务器
 */
const COMMON_MCP_SERVERS = {
  // Puppeteer - 浏览器自动化
  puppeteer: {
    install: "npx -y @anthropic/mcp-server-puppeteer",
    use: "截图、PDF 生成、UI 测试"
  },

  // Filesystem - 文件系统访问
  filesystem: {
    install: "npx -y @anthropic/mcp-server-filesystem /path",
    use: "读取、写入、搜索文件"
  },

  // Sentry - 错误追踪
  sentry: {
    install: "npx -y @anthropic/mcp-server-sentry",
    use: "查看错误、性能数据"
  },

  // Postgres - 数据库
  postgres: {
    install: "npx -y @anthropic/mcp-server-postgres",
    use: "查询数据库、执行 SQL"
  }
};
```

### 26.3.3 自定义 Slash 命令

```typescript
/**
 * 创建可重用的命令模板
 */

/**
 * 位置: .claude/commands/*.md
 */

// .claude/commands/fix-github-issue.md
/**
 * 自动修复 GitHub Issue
 *
 * 用法: /project:fix-github-issue [issue-number]
 */

请分析并修复 GitHub Issue: $ARGUMENTS

遵循以下步骤：

1. 使用 \`gh issue view $ARGUMENTS\` 获取 Issue 详情
2. 理解 Issue 中描述的问题
3. 搜索代码库中的相关文件
4. 实现必要的修复
5. 编写并运行测试验证修复
6. 确保代码通过 lint 和 typecheck
7. 创建描述性的提交信息
8. 推送并创建 PR

记住使用 GitHub CLI (\`gh\`) 处理所有 GitHub 相关任务。

---

// .claude/commands/refactor-component.md
/**
 * 重构 React 组件
 *
 * 用法: /project:refactor-component [component-name]
 */

请重构组件: $ARGUMENTS

重构要求：
1. 使用 TypeScript 和现代 Hooks
2. 提取可重用的逻辑到自定义 Hooks
3. 改进类型定义
4. 添加 PropTypes/TypeScript 验证
5. 优化性能（useMemo, useCallback）
6. 改进代码可读性
7. 添加 JSDoc 注释

重构后：
- 运行测试确保功能不变
- 运行 lint 确保代码规范
- 创建 PR 并描述改进点

---

// .claude/commands/debug-performance.md
/**
 * 性能调试
 *
 * 用法: /project:debug-performance [file-or-component]
 */

请分析性能问题: $ARGUMENTS

调试步骤：
1. 使用 React DevProfiler 分析组件
2. 识别不必要的重渲染
3. 检查是否有大型对象作为 props
4. 查找循环中的内联函数
5. 检查 useEffect 依赖
6. 提供优化建议并实施

/**
 * 个人命令（全局）
 */
// ~/.claude/commands/review-code.md

请审查以下代码的：

1. **安全性**
   - SQL 注入风险
   - XSS 漏洞
   - 敏感信息泄露

2. **性能**
   - 不必要的重渲染
   - 内存泄漏
   - 低效算法

3. **可维护性**
   - 代码重复
   - 命名清晰度
   - 复杂度

4. **最佳实践**
   - TypeScript 使用
   - 错误处理
   - 测试覆盖

提供具体的改进建议和代码示例。
```

---

## 26.4 经典工作流

### 26.4.1 Explore → Plan → Code → Commit

```typescript
/**
 * Boris 推荐的黄金工作流
 */

/**
 * Step 1: Explore (探索)
 */
// ❌ 不要直接让 Claude 编码
user: "实现用户认证功能"
claude: [可能产生不合适的代码]

// ✅ 先让 Claude 探索
user: `
  请阅读以下文件，但不要写代码：
  - src/services/auth.ts
  - src/types/user.ts
  - docs/authentication.md

  理解现有的认证架构
`
claude: [读取文件，总结架构]

// 在这个阶段，Boris 建议使用子代理
user: `
  使用子代理验证：
  - 当前的认证流程
  - 已有的用户模型
  - 安全措施
`

/**
 * Step 2: Plan (计划)
 */
// 使用 "think" 触发扩展思考
user: `
  请 think 一下如何添加"记住我"功能

  考虑：
  - 安全性（token 存储）
  - 用户体验
  - 与现有代码的集成

  先不要写代码，只需要制定计划
`

// 思考级别
const THINK_LEVELS = {
  "think": "基础思考",
  "think hard": "深入思考",
  "think harder": "非常深入的思考",
  "ultrathink": "最大思考预算"
};

// 可以将计划保存到文件
user: "将计划写入 docs/remember-me-plan.md"

/**
 * Step 3: Code (编码)
 */
// 计划确认后，开始实现
user: `
  基于上面的计划，实现"记住我"功能

  在实现过程中：
  - 验证每一步的合理性
  - 确保类型安全
  - 添加必要的错误处理
`

/**
 * Step 4: Commit (提交)
 */
user: `
  创建一个描述性的提交信息
  推送并创建 PR
  PR 描述中包含：
  - 实现的功能
  - 技术决策
  - 测试策略
`

/**
 * Boris 的关键建议
 */
const borisKeyAdvice = `
步骤 #1-#2 是关键！

没有探索和计划，Claude 会直接跳到编码。
对于需要深入思考的问题，这会导致次优的解决方案。

先研究，再计划，最后编码。
`;
```

### 26.4.2 TDD 工作流

```typescript
/**
 * Anthropic 最喜欢的测试驱动开发流程
 */

/**
 * Step 1: 编写测试
 */
user: `
  为以下功能编写测试：

  功能：用户登录
  输入：email, password
  输出：{ success: boolean, token?: string, error?: string }

  测试用例：
  - 成功登录
  - 错误密码
  - 不存在的用户
  - 无效的 email 格式
  - 空密码

  IMPORTANT: 这是 TDD，不要编写实现代码！
  测试应该描述期望的行为，即使功能还不存在。
`;

// Claude 会生成测试
// test/auth.test.ts
describe('User Login', () => {
  test('should return token on successful login', async () => {
    // ...
  });

  test('should reject wrong password', async () => {
    // ...
  });

  // ...
});

/**
 * Step 2: 运行测试（确认失败）
 */
user: "运行测试，确认它们失败"
claude: [运行测试，显示失败]

// TDD 的第一步：红灯（测试失败）

/**
 * Step 3: 提交测试
 */
user: "提交测试代码"
claude: [git commit]

/**
 * Step 4: 编写实现代码
 */
user: `
  编写代码让测试通过

  IMPORTANT:
  - 不要修改测试
  - 持续运行测试
  - 直到所有测试通过
  - 迭代改进代码
`;

// TDD 的第二步：绿灯（测试通过）

/**
 * Step 5: 验证实现没有过度拟合
 */
user: `
  使用子代理验证实现
  确保代码没有"作弊"或过度拟合测试
`;

/**
 * Step 6: 提交实现
 */
user: "提交实现代码"
claude: [git commit]

/**
 * Boris 的观察
 */
const borisObservation = `
Claude 在有明确目标时表现最好：
- 视觉模型
- 测试用例
- 其他输出

通过提供预期输出（测试），Claude 可以：
- 做出改变
- 评估结果
- 迭代改进直到成功
`;
```

### 26.4.3 Safe YOLO 模式

```typescript
/**
 * 自动化批量任务
 */

/**
 * 使用场景
 */
const YOLO_USE_CASES = [
  "修复 lint 错误",
  "生成样板代码",
  "批量重命名",
  "格式化代码"
];

/**
 * 使用方式
 */
// 注意：这是危险的模式！
// claude --dangerously-skip-permissions -p "your prompt"

// Boris 的安全建议：
const SAFETY_RECOMMENDATIONS = `
⚠️ 警告：--dangerously-skip-permissions 跳过所有权限检查

风险：
- 数据丢失
- 系统损坏
- 数据泄露（通过提示注入攻击）

安全使用方式：
1. 在没有网络访问的容器中运行
2. 使用 Docker Dev Containers
3. 只用于可逆的操作

示例：Docker 容器
docker run -it --rm \\
  -v $(pwd):/workspace \\
  -w /workspace \\
  node:18 \\
  npx -y @anthropic/claude-code \\
  --dangerously-skip-permissions \\
  -p "fix all lint errors"
`;

/**
 * 参考 Docker 配置
 */
// .devcontainer/devcontainer.json
{
  "name": "Claude Code Safe Container",
  "image": "node:18",
  "features": {
    "ghcr.io/devcontainers/features/node:1": {}
  },
  "mounts": [
    "source=${localWorkspaceFolder},target=/workspace,type=bind"
  ],
  "remoteUser": "node",
  "postCreateCommand": "npm install"
}
```

---

## 26.5 工作流优化技巧

### 26.5.1 具体的指令

```typescript
/**
 * Boris: 更具体的指令 = 更好的结果
 */

/**
 * 对比示例
 */
const INSTRUCTION_EXAMPLES = {
  // ❌ 差的指令
  bad: [
    "为 foo.py 添加测试",
    "为什么 ExecutionFactory 的 API 这么奇怪？",
    "添加一个日历组件"
  ],

  // ✅ 好的指令
  good: [
    // 具体：描述要测试的场景
    "为 foo.py 编写新的测试用例，" +
    "覆盖用户未登录时的边界情况。" +
    "避免使用 mocks。",

    // 具体：告诉 Claude 去哪里找答案
    "查看 ExecutionFactory 的 git 历史，" +
    "总结它的 API 是如何演变的。",

    // 具体：提供详细的实现指导
    "查看主页上现有组件的实现方式，" +
    "理解代码和接口是如何分离的模式。" +
    "HotDogWidget.php 是一个很好的起点。" +
    "然后遵循这个模式实现新的日历组件，" +
    "让用户可以选择月份并前后翻页选择年份。" +
    "从头构建，除了代码库中已经使用的库外不使用其他库。"
  ]
};

/**
 * 提高具体性的技巧
 */
const SPECIFICITY_TIPS = [
  "1. 指定文件或目录",
  "2. 描述期望的输出",
  "3. 提供上下文或约束",
  "4. 引用类似的实现",
  "5. 说明要避免什么"
];
```

### 26.5.2 使用图像

```typescript
/**
 * Claude 擅长处理图像
 */

/**
 * 图像输入方式
 */
const IMAGE_INPUT_METHODS = {
  // 1. 粘贴截图
  // macOS: Cmd+Ctrl+Shift+4 (截图到剪贴板)
  // 然后按 Ctrl+V 粘贴（不是 Cmd+V！）

  // 2. 拖放
  // 直接拖放图像到提示输入区

  // 3. 文件路径
  // 提供图像文件路径
  user: "请看 /path/to/screenshot.png 并分析问题"
};

/**
 * 使用场景
 */
const IMAGE_USE_CASES = {
  // 设计模型
  design: `
    user: [粘贴 UI 设计图]
    claude: 根据这个设计实现组件
  `,

  // 错误截图
  error: `
    user: [粘贴错误截图]
    claude: 分析这个错误并修复
  `,

  // 数据可视化
  data: `
    user: [粘贴图表]
    claude: 解释这个数据趋势
  `
};

/**
 * 视觉效果的提示词
 */
const AESTHETIC_PROMPTS = [
  "使结果在视觉上具有吸引力",
  "确保设计美观专业",
  "优化用户体验和视觉效果"
];
```

### 26.5.3 提及文件

```typescript
/**
 * 使用 Tab 补全引用文件
 */

/**
 * 为什么重要
 */
const FILE_REFERENCES = `
Claude 需要知道：
- 哪些文件与任务相关
- 在哪里找到这些文件
- 哪些文件需要修改

使用 Tab 补全：
1. 输入文件名的一部分
2. 按 Tab 键
3. 选择正确的文件
4. Claude 会自动添加完整路径
`;

/**
 * 示例
 */
user: "请查看 src/comp[按 Tab] → src/components/"
claude: "你是指 src/components/UserProfile.tsx 吗？"

user: "修改 src/servi[按 Tab] → src/services/"
claude: "你是指 src/services/api.ts 吗？"
```

### 26.5.4 及早纠正

```typescript
/**
 * Boris: 及早且经常纠正方向
 */

/**
 * 四个纠正工具
 */
const CORRECTION_TOOLS = {
  // 1. 先让 Claude 做计划
  planFirst: `
    user: "先制定计划，不要写代码"
    claude: [输出计划]
    user: "计划看起来不错，开始实现"
  `,

  // 2. 按 Escape 中断
  escape: `
    Claude 运行时：
    - 按 Escape: 中断当前操作
    - 保留上下文
    - 可以重定向或扩展指令
  `,

  // 3. 双击 Escape 返回历史
  doubleEscape: `
    - 双击 Escape: 返回到之前的提示
    - 编辑提示
    - 尝试不同的方向
  `,

  // 4. 撤销更改
  undo: `
    user: "撤销这些更改，用不同的方法"
    claude: [撤销并重新实现]
  `
};

/**
 * Boris 的观察
 */
const borisObservation = `
虽然 Claude 偶尔会在第一次尝试时完美解决问题，
但使用这些纠正工具通常能更快地产生更好的解决方案。

不要害怕纠正 Claude。
迭代是成功的关键。
`;
```

### 26.5.5 使用 /clear

```typescript
/**
 * 保持上下文聚焦
 */

/**
 * 何时使用 /clear
 */
const WHEN_TO_USE_CLEAR = [
  "任务完成，开始新任务",
  "上下文窗口满了",
  "对话偏离主题",
  "想要重置对话"
];

/**
 * 示例
 */
// 会话 1
user: "实现用户认证"
claude: [实现认证]
user: "修复登录 bug"
claude: [修复 bug]
user: "添加 OAuth"
claude: [添加 OAuth]
// 上下文变得混乱...

user: "/clear"
// 上下文重置

// 会话 2
user: "实现购物车"
claude: [全新开始，无旧上下文干扰]

/**
 * Boris 的建议
 */
const borisAdvice = `
在长会话中，Claude 的上下文窗口会充满：
- 不相关的对话
- 文件内容
- 命令输出

这会降低性能并分散 Claude 的注意力。

在不同任务之间频繁使用 /clear。
`;
```

### 26.5.6 检查清单和草稿板

```typescript
/**
 * 复杂工作流的组织工具
 */

/**
 * 适用场景
 */
const CHECKLIST_USE_CASES = [
  "代码迁移",
  "修复大量 lint 错误",
  "运行复杂的构建脚本",
  "多步骤的代码审查"
];

/**
 * 示例：修复 lint 错误
 */

// Step 1: 创建检查清单
user: `
  运行 npm run lint
  将所有错误写入 Markdown 检查清单
  格式：
  - [ ] file.ts:line:error message
`

// Step 2: 逐个修复
user: `
  使用上面的检查清单，逐个修复错误：
  1. 修复一个错误
  2. 验证修复
  3. 勾选检查清单
  4. 移动到下一个
`

/**
 * 示例：代码迁移
 */
user: `
  创建一个迁移计划文档：

  # 从 React 迁移到 Vue

  ## 组件迁移清单
  - [ ] Button.tsx
  - [ ] Input.tsx
  - [ ] Modal.tsx
  ...

  ## 进度跟踪
  - 已完成: 0/15
  - 进行中: -
  - 待处理: 15

  使用这个文档作为工作草稿板
`;
```

---

## 26.6 多 Claude 工作流

### 26.6.1 代码和审查分离

```typescript
/**
 * 让一个 Claude 编写，另一个审查
 */

/**
 * 工作流程
 */
const WORKFLOW = {
  // Step 1: Claude A 编写代码
  terminal1: `
    cd /project
    claude

    user: "实现用户认证功能"
    claude: [编写代码]
  `,

  // Step 2: Claude B 审查代码
  terminal2: `
    cd /project
    claude

    user: "审查 src/services/auth.ts 中的新代码"
    claude: [进行代码审查]
  `,

  // Step 3: Claude C 根据反馈编辑
  terminal1: `
    user: "/clear"
    user: "根据以下反馈改进代码：[粘贴审查反馈]"
    claude: [改进代码]
  `
};

/**
 * 为什么有效
 */
const WHY_IT_WORKS = `
分离的上下文是有益的：
- 每个 Claude 专注于自己的任务
- 避免单个 Claude 陷入循环
- 类似与多个工程师协作
- 产生更全面的审查
`;
```

### 26.6.2 Git Worktrees

```typescript
/**
 * Boris 推荐的并行工作方式
 */

/**
 * 什么是 Git Worktrees
 */
const GIT_WORKTREES = `
Git worktrees 允许你：
- 同一仓库的多个分支检出到不同目录
- 每个目录有独立的工作文件
- 共享相同的 Git 历史和 reflog
- 独立切换分支而互不影响
`;

/**
 * 设置步骤
 */
// Step 1: 创建 worktrees
bash: `
  # 主仓库
  cd /my-project

  # 创建 feature-a worktree
  git worktree add ../my-project-feature-a feature-a

  # 创建 feature-b worktree
  git worktree add ../my-project-feature-b feature-b
`

// Step 2: 在每个 worktree 中启动 Claude
terminal1: `
  cd ../my-project-feature-a
  claude
  user: "重构认证系统"
`

terminal2: `
  cd ../my-project-feature-b
  claude
  user: "构建数据可视化组件"
`

/**
 * 提示
 */
const WORKTREE_TIPS = [
  "使用一致的命名约定",
  "每个 worktree 使用单独的终端标签",
  "使用 iTerm2 设置通知（当 Claude 需要关注时）",
  "为不同的 worktree 使用单独的 IDE 窗口",
  "完成后清理: git worktree remove ../my-project-feature-a"
];

/**
 * 为什么使用 worktrees
 */
const WHY_WORKTREES = `
优势：
1. 并行工作
   - 多个 Claude 同时工作
   - 不需要等待

2. 独立任务
   - 任务不会重叠
   - 没有合并冲突

3. 全速工作
   - 每个 Claude 以全速工作
   - 不受其他 Claude 影响

4. 更好的组织
   - 每个功能独立目录
   - 清晰的上下文分离
`;
```

---

## 26.7 关键要点总结

### 26.7.1 Boris Power 的核心理念

```typescript
/**
 * Claude Code 的设计哲学
 */

const CORE_PHILOSOPHY = {
  // 1. 低层次和无偏见
  lowLevel: `
    Claude Code 是低层次工具
    不强制特定工作流
    提供接近原始模型的访问
    灵活、可定制、可脚本化
  `,

  // 2. 安全优先
  safetyFirst: `
    默认需要权限确认
    这是有意的设计
    安全比便利更重要
  `,

  // 3. 上下文为王
  contextIsKing: `
    CLAUDE.md 提供长期记忆
 上下文理解是成功的关键
  具体的指令产生更好的结果
  `,

  // 4. 人机协作
  humanAIcollaboration: `
    Claude 是助手，不是替代
    工程师是导演
    迭代和纠正是成功的关键
  `
};
```

### 26.7.2 最重要的建议

```typescript
/**
 * Boris 最想强调的几点
 */

const TOP_RECOMMENDATIONS = {
  // 1. 使用 CLAUDE.md
  claudeMd: `
    CLAUDE.md 是最重要的配置
    花时间优化它
    迭代改进
    添加到版本控制
  `,

  // 2. 探索和计划
  exploreAndPlan: `
    不要直接跳到编码
    先探索代码库
    制定计划
    然后实现
  `,

  // 3. 具体的指令
  beSpecific: `
    越具体越好
    提供文件名
  描述期望输出
  给出上下文
  `,

  // 4. 使用图像
  useImages: `
    Claude 擅长处理图像
    粘贴截图
  提供设计模型
  视觉参考很有帮助
  `,

  // 5. 及早纠正
  courseCorrect: `
    不要等待完美
  及早纠正
    经常纠正
    迭代改进
  `
};
```

---

## 26.8 练习

### 练习 1：创建 CLAUDE.md

为一个假设的项目创建 CLAUDE.md 文件：

```
项目：Todo 应用
技术栈：React + TypeScript + Vite
团队规范：使用 ESLint、Prettier
```

### 练习 2：改进 Prompt

改进以下 Prompt 使其更具体：

```
"添加测试"
```

### 练习 3：设计工作流

设计一个完整的工作流来完成以下任务：

```
任务：重构认证系统
要求：
- 改进安全性
- 添加单元测试
- 更新文档
```

使用 Explore → Plan → Code → Commit 工作流。

---

## 26.9 进一步阅读

- [Claude Code Best Practices (官方)](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Chapter 27: Addy Osmani 的 2026 工作流](chapter-27-addy-osmani.md) - 下一章

---

## 视频脚本

### Episode 26: Boris Power 官方建议 (20 分钟)

#### [0:00-1:30] 引入
**视觉元素**：
- Boris Cherny 照片
- "Claude Code 之父" 标题

**内容**：
> 今天我们学习最权威的建议：来自 Claude Code 创建者 Boris Cherny (Boris Power) 的官方最佳实践。
>
> 这些建议不是猜测，不是个人经验，而是经过 Anthropic 内部团队大量验证的权威指南。

#### [1:30-5:00] CLAUDE.md 的力量
**视觉元素**：
- CLAUDE.md 示例
- 位置示意图

**内容**：
> CLAUDE.md 是最重要的配置文件。
>
> [展示 CLAUDE.md 结构]
>
> 它应该包含：
> - 常用命令
> - 代码风格
> - 架构说明
> - 重要提醒
>
> [演示创建和优化 CLAUDE.md]

#### [5:00-8:00] 探索 → 计划 → 编码 → 提交
**视觉元素**：
- 工作流程图
- 每步的详细说明

**内容**：
> Boris 推荐的经典工作流。
>
> [演示完整工作流]
>
> 关键：步骤 #1-#2 是最重要的！不要直接跳到编码。

#### [8:00-11:00] TDD 工作流
**视觉元素**：
- TDD 循环图
- 红灯 → 绿灯动画

**内容**：
> Anthropic 团队最喜欢的 TDD 流程。
>
> [演示 TDD 工作流]
>
> Claude 在有明确目标（测试）时表现最好。

#### [11:00-14:00] 工作流优化
**视觉元素**：
- 技巧列表
- 对比示例

**内容**：
> 提高效果的关键技巧：
> - 具体的指令
> - 使用图像
> - 提及文件
> - 及早纠正
> - 使用 /clear
>
> [逐个演示]

#### [14:00-17:00] 多 Claude 工作流
**视觉元素**：
- Git Worktrees 示意图
- 并行工作演示

**内容**：
> 进阶技巧：运行多个 Claude 实例。
>
> [演示 Git Worktrees]
>
> 让一个 Claude 编写，另一个审查。或者在不同 worktrees 中并行工作。

#### [17:00-20:00] 总结
**视觉元素**：
- 关键要点列表
- Next Chapter 预告

**内容**：
> **关键要点**：
> 1. 花时间优化 CLAUDE.md
> 2. 先探索和计划，再编码
> 3. 提供具体的指令
> 4. 使用图像和视觉参考
> 5. 及早且经常纠正
> 6. 使用 Git Worktrees 并行工作
>
> 下一章，我们将学习 Google 工程师领袖 Addy Osmani 的 2026 AI 工作流。
