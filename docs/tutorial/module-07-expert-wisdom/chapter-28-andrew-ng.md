# Chapter 28: Andrew Ng 课程精华

## 学习目标

完成本章后，你将能够：

- 理解 Andrew Ng 与 Anthropic 官方合作的 Claude Code 课程
- 掌握课程中的核心最佳实践
- 学习三个实际项目案例
- 应用课程中学到的技巧
- 理解高级工作流程

## 前置知识

- [Chapter 26: Boris Power 官方建议](chapter-26-boris-power.md)
- [Chapter 27: Addy Osmani 的 2026 工作流](chapter-27-addy-osmani.md)
- Python 和 Git 基础

---

## 28.1 课程概述

### 28.1.1 课程信息

```
┌─────────────────────────────────────────────────────────────┐
│         Claude Code: A Highly Agentic Coding Assistant        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  提供商：DeepLearning.AI (Andrew Ng)                        │
│  合作方：Anthropic (官方合作)                               │
│                                                             │
│  讲师：Elie Schoppik                                        │
│  - Anthropic 技术教育主管                                   │
│  - 负责 Claude Code 的教育内容                               │
│                                                             │
│  课程信息：                                                 │
│  - 级别：中级                                               │
│  - 时长：1 小时 50 分钟                                     │
│  - 格式：10 个视频课程                                      │
│                                                             │
│  状态：                                                     │
│  - 发布日期：2025 年 8 月 5 日                             │
│  - Beta 期间免费                                            │
│                                                             │
│  为什么重要：                                               │
│  - 这是 Claude Code 的权威课程                              │
│  - Anthropic 官方合作                                       │
│  - 涵盖最新的功能和最佳实践                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 28.1.2 课程亮点

```typescript
/**
 * 课程的独特价值
 */

const courseHighlights = {
  // 1. 官方权威性
  official: `
    这是 Claude Code 的权威课程：
    - DeepLearning.AI 与 Anthropic 官方合作
    - 由 Anthropic 技术教育主管讲授
    - 反映了 Anthropic 内部和外部开发者的集体学习
  `,

  // 2. 实践导向
  practical: `
    强调在实践中学习：
    - 三个完整的项目示例
    - 真实的开发场景
    - 可立即应用的技巧
  `,

  // 3. 全面覆盖
  comprehensive: `
    涵盖从基础到高级：
    - 基础设置和使用
    - 高级功能和工作流
    - 团队协作模式
    - 与其他工具的集成
  `,

  // 4. 最新内容
  upToDate: `
    2025 年 8 月发布，包含：
    - 最新的功能
    - 最新的最佳实践
    - MCP 服务器集成
    - 增强的 GitHub 工作流
  `
};
```

---

## 28.2 课程结构

### 28.2.1 10 个课程概览

```typescript
/**
 * 课程大纲
 */

const courseOutline = [
  // Lesson 1
  {
    title: "什么是 Claude Code？",
    duration: "8 分钟",
    type: "视频",
    topics: [
      "Claude Code 简介",
      "其能力",
      "与其他 AI 编码助手的区别"
    ]
  },

  // Lesson 2
  {
    title: "课程笔记",
    duration: "1 分钟",
    type: "阅读",
    topics: [
      "快速参考材料",
      "课程要点"
    ]
  },

  // Lesson 3
  {
    title: "设置与代码库理解",
    duration: "14 分钟",
    type: "视频",
    topics: [
      "如何设置 Claude Code",
      "探索和理解新代码库",
      "RAG 聊天机器人示例"
    ]
  },

  // Lesson 4
  {
    title: "添加功能",
    duration: "17 分钟",
    type: "视频",
    topics: [
      "使用 Claude Code 添加新功能的最佳实践",
      "先规划",
      "使用思考模式"
    ]
  },

  // Lesson 5
  {
    title: "测试、错误调试和代码重构",
    duration: "12 分钟",
    type: "视频",
    topics: [
      "使用 Claude Code 编写测试",
      "调试错误",
      "重构现有代码"
    ]
  },

  // Lesson 6
  {
    title: "同时添加多个功能",
    duration: "11 分钟",
    type: "视频",
    topics: [
      "高级工作流",
      "使用 git worktrees",
      "并行运行多个 Claude 会话"
    ]
  },

  // Lesson 7
  {
    title: "探索 GitHub 集成和 Hooks",
    duration: "10 分钟",
    type: "视频",
    topics: [
      "Claude Code 的 GitHub 集成",
      "修复 issue",
      "创建 PR",
      "使用 hooks"
    ]
  },

  // Lesson 8
  {
    title: "重构 Jupyter 笔记本和创建仪表板",
    duration: "12 分钟",
    type: "视频",
    topics: [
      "实际示例",
      "将 Jupyter 笔记本转换为仪表板"
    ]
  },

  // Lesson 9
  {
    title: "基于 Figma 模型创建 Web 应用",
    duration: "9 分钟",
    type: "视频",
    topics: [
      "使用 Figma 和 Playwright MCP 服务器",
      "从设计模型创建 Web 应用"
    ]
  },

  // Lesson 10
  {
    title: "Prompts 和课程总结",
    duration: "1 分钟",
    type: "阅读",
    topics: [
      "关键 Prompts 集合",
      "课程总结快速参考"
    ]
  }
];
```

---

## 28.3 核心学习目标

### 28.3.1 详细学习目标

```typescript
/**
 * 课程承诺的学习成果
 */

const learningObjectives = {
  // 1. 理解 Claude Code 架构
  architecture: `
    理解 Claude Code 的底层架构：
    - 它用于导航代码库的工具
    - 它如何在会话之间存储记忆
    - 高度自主的助手能力
  `,

  // 2. 探索代码库
  explore: `
    探索和理解代码库：
    - RAG 聊天机器人的代码库
    - 前端和后端之间的信息流
  `,

  // 3. CLAUDE.md 文件
  claudeMd: `
    在项目目录中启动 CLAUDE.md 文件：
    - 包含代码库的信息和指南
    - Claude Code 可以跨会话记住
  `,

  // 4. 上下文管理
  context: `
    将上下文输入 Claude Code：
    - 提及相关文件
    - 清晰定义功能和功能
    - 连接到 MCP 服务器
  `,

  // 5. 添加功能
  features: `
    为 RAG 聊天机器人的前端和后端添加功能：
    - 先规划以提高性能
    - 对更难的任务使用思考模式
    - 使用 Claude Code 的子代理进行头脑风暴
  `,

  // 6. 编写测试
  testing: `
    编写测试以评估 RAG 聊天机器人功能：
    - 重构聊天机器人的部分
  `,

  // 7. Git Worktrees
  worktrees: `
    使用 git worktrees：
    - 同时运行多个 Claude 会话
    - 每个专注于为聊天机器人添加独立功能
  `,

  // 8. GitHub 集成
  github: `
    修复 GitHub issue：
    - 创建、审查和合并 GitHub PR
    - 使用 Claude Code 的 GitHub 集成
  `,

  // 9. Hooks
  hooks: `
    通过 Claude Code hooks：
    - 在使用工具之前和之后执行代码
  `,

  // 10. Jupyter 重构
  jupyter: `
    重构电子商务数据分析的 Jupyter notebook：
    - 将其转换为仪表板
  `,

  // 11. Figma to Web
  figma: `
    将 Claude 连接到 Figma MCP 服务器：
    - 导入设计模型到 Claude Code
    - 开发显示联邦储备经济数据的 Web 界面
  `,

  // 12. Playwright MCP
  playwright: `
    使用 Playwright MCP 服务器：
    - 自动打开 Web 浏览器
    - 截图
    - 指导 Claude Code 改进应用的 UI 设计
  `
};
```

---

## 28.4 三个项目案例

### 28.4.1 项目 1: RAG 聊天机器人

```typescript
/**
 * RAG Chatbot 项目
 */

const ragChatbotProject = {
  description: "使用检索增强生成 (RAG) 的聊天机器人",

  phases: {
    // Phase 1: 探索代码库
    exploration: `
      Lesson 3: 设置与代码库理解

      目标：
      - 理解 RAG 聊天机器人的架构
      - 探索前端和后端代码
      - 理解信息如何在两者之间流动

      技巧：
      - 使用 Claude Code 导航代码库
      - 询问关于代码结构的问题
      - 理解数据流
    `,

    // Phase 2: 添加功能
    features: `
      Lesson 4: 添加功能

      前端功能：
      - 添加用户输入框
      - 显示聊天历史
      - 添加加载状态

      后端功能：
      - 实现检索逻辑
      - 添加 API 端点
      - 优化响应生成

      最佳实践：
      - 先规划！
      - 使用思考模式处理复杂任务
      - 使用子代理进行头脑风暴
    `,

    // Phase 3: 测试和重构
    testing: `
      Lesson 5: 测试、错误调试和代码重构

      测试：
      - 单元测试
      - 集成测试
      - 端到端测试

      调试：
      - 使用 Claude Code 识别错误
      - 修复 bug
      - 验证修复

      重构：
      - 改进代码结构
      - 优化性能
      - 提高可维护性
    `
  }
};
```

### 28.4.2 项目 2: 电子商务仪表板

```typescript
/**
 * E-commerce Dashboard 项目
 */

const ecommerceProject = {
  description: "将 Jupyter 笔记本转换为仪表板",

  phases: {
    // Phase 1: 分析现有代码
    analysis: `
      Lesson 8: 重构 Jupyter 笔记本

      现状：
      - 电子商务数据分析的 Jupyter notebook
      - 包含数据可视化
      - 包含统计分析

      挑战：
      - Notebook 不适合生产环境
      - 需要转换为交互式仪表板
      - 需要保持分析逻辑
    `,

    // Phase 2: 重构
    refactoring: `
      使用 Claude Code：
      - 提取分析逻辑
      - 创建可重用的组件
      - 实现交互式可视化

      技巧：
      - 保持分析完整性
      - 改进代码结构
      - 添加用户交互
    `,

    // Phase 3: 部署
    deployment: `
      创建仪表板：
      - 选择前端框架
      - 实现数据管道
      - 部署到生产环境
    `
  }
};
```

### 28.4.3 项目 3: Figma to Web 应用

```typescript
/**
 * Figma to Web App 项目
 */

const figmaProject = {
  description: "从设计模型创建 Web 应用",

  phases: {
    // Phase 1: 导入设计
    importDesign: `
      Lesson 9: 基于 Figma 模型创建 Web 应用

      使用 Figma MCP：
      - 连接到 Figma MCP 服务器
      - 导入设计模型
      - 理解设计规范

      数据来源：
      - 联邦储备经济数据
      - 需要可视化显示
    `,

    // Phase 2: 实现 UI
    implementUI: `
      使用 Playwright MCP：
      - 自动打开浏览器
      - 截取当前 UI
      - 与设计模型对比

      迭代改进：
      - 根据 Playwright 截图调整
      - 逐个匹配设计元素
      - 确保响应式设计
    `,

    // Phase 3: 集成数据
    integrateData: `
      连接数据源：
      - 实现数据获取逻辑
      - 创建可视化组件
      - 实现实时更新
    `
  }
};
```

---

## 28.5 核心最佳实践

### 28.5.1 提供清晰的上下文

```typescript
/**
 * 课程强调的上下文管理技巧
 */

const contextTips = {
  // 1. 提及相关文件
  mentionFiles: `
    明确告诉 Claude Code 相关文件：
    - "请查看 src/services/auth.ts"
    - "这个功能在 components/UserProfile.tsx 中"
    - "参考 utils/validation.ts 中的验证逻辑"
  `,

  // 2. 提供截图或图像
  provideImages: `
    视觉上下文很重要：
    - 粘贴设计模型
    - 错误截图
    - UI 参考图像
    - 数据可视化图表
  `,

  // 3. 控制上下文
  controlContext: `
    使用命令管理上下文：
    - Escape: 中断操作
    - /clear: 清空上下文
    - /compact: 压缩上下文
  `
};
```

### 28.5.2 先规划

```typescript
/**
 * "规划优先"原则
 */

const planFirstPrinciple = `
课程强调的核心原则：

先规划！再编码。

规划的好处：
1. 提高 Claude Code 的性能
2. 减少返工
3. 确保覆盖所有需求
4. 使任务更可管理

规划技巧：
- 使用 /plan 命令
- 创建 spec.md
- 分解为小任务
- 定义验收标准
`;
```

### 28.5.3 使用思考模式

```typescript
/**
 * 思考模式的使用
 */

const thinkingModes = {
  // 基础思考
  think: `
    "think" - 基础思考
    用于：标准复杂度的任务
  `,

  // 深度思考
  thinkHard: `
    "think hard" - 深度思考
    用于：较复杂的任务
  `,

  // 更深度思考
  thinkHarder: `
    "think harder" - 更深度思考
    用于：非常复杂的任务
  `,

  // 超级思考
  ultrathink: `
    "ultrathink" - 超级思考
    用于：最复杂的任务，需要最大计算预算
  `
};
```

### 28.5.4 使用子代理

```typescript
/**
 * 子代理的强大功能
 */

const subagentTips = {
  what: `
    子代理是什么：
    - Claude Code 可以启动额外的代理
    - 用于验证细节或调查问题
    - 保留主会话的上下文
  `,

  when: `
    何时使用子代理：
    - 复杂问题的早期
    - 需要验证多个选项时
    - 需要深入调查时
  `,

  how: `
    如何使用：
    "使用子代理验证这个方法是否最优"
    "使用子代理调查这个 bug 的根本原因"
    "使用子代理探索不同的实现方式"
  `
};
```

---

## 28.6 Git Worktrees 实战

### 28.6.1 并行工作流

```typescript
/**
 * Lesson 6: 同时添加多个功能
 */

const parallelWorkflow = {
  concept: `
    课程的高级工作流：
    - 使用 git worktrees
    - 运行多个 Claude 会话
    - 同时专注于不同功能
  `,

  setup: `
    设置步骤：
    1. 创建 worktrees
       git worktree add ../project-feature-a feature-a
       git worktree add ../project-feature-b feature-b

    2. 在每个 worktree 中启动 Claude
       cd ../project-feature-a && claude
       cd ../project-feature-b && claude

    3. 分配独立任务
       Terminal 1: "实现用户认证"
       Terminal 2: "实现数据导出"
  `,

  benefits: `
    优势：
    - 并行开发
    - 互不干扰
    - 全速工作
    - 独立提交
  `,

  merge: `
    合并：
    1. 审查每个功能的更改
    2. 运行测试
    3. 合并到主分支
    4. 清理 worktrees
  `
};
```

---

## 28.7 GitHub 集成

### 28.7.1 GitHub 工作流

```typescript
/**
 * Lesson 7: GitHub 集成和 Hooks
 */

const githubWorkflow = {
  // 修复 Issue
  fixIssues: `
    修复 GitHub Issue：
    1. Claude Code 读取 issue 详情
    2. 理解问题描述
    3. 搜索相关代码
    4. 实现修复
    5. 运行测试
    6. 创建 commit
    7. 推送并创建 PR
  `,

  // 创建 PR
  createPRs: `
    创建 Pull Request：
    - 自动生成 PR 描述
    - 包含更改摘要
    - 引用相关 issue
    - 遵循 PR 模板
  `,

  // 审查 PR
  reviewPRs: `
    审查 Pull Request：
    - 分析代码更改
    - 检查测试覆盖
    - 验证功能
    - 提供反馈
  `,

  // 合并 PR
  mergePRs: `
    合并 Pull Request：
    - 确保 CI 通过
    - 解决冲突
    - 合并到主分支
    - 删除分支
  `
};
```

### 28.7.2 Hooks

```typescript
/**
 * 使用 Hooks 自动化工作流
 */

const hooksExample = {
  // beforeEdit
  beforeEdit: `
    beforeEdit:
      - 在编辑文件之前运行
      - 示例：运行 linter
      - 示例：备份文件
  `,

  // afterEdit
  afterEdit: `
    afterEdit:
      - 在编辑文件之后运行
      - 示例：运行测试
      - 示例：格式化代码
  `,

  // beforeCommit
  beforeCommit: `
    beforeCommit:
      - 在 commit 之前运行
      - 示例：检查 commit 消息格式
      - 示例：运行完整测试套件
  `
};

// .claude/hooks.json
{
  "beforeEdit": [
    {
      "name": "run-linter",
      "command": "npm run lint",
      "include": ["**/*.ts", "**/*.tsx"]
    }
  ],
  "afterEdit": [
    {
      "name": "format-code",
      "command": "npm run format"
    }
  ]
}
```

---

## 28.8 关键 Prompts 集合

### 28.8.1 课程中的关键 Prompts

```typescript
/**
 * Lesson 10: 关键 Prompts
 */

const keyPrompts = {
  // 探索代码库
  explore: `
    "请探索这个代码库的结构。
     主要组件是什么？
     数据如何在前端和后端之间流动？
     请总结架构。"
  `,

  // 添加功能
  addFeature: `
    "请先规划一下如何添加这个功能。
     列出需要的步骤。
     不要立即编写代码。"
  `,

  // 编写测试
  writeTests: `
    "请为这个功能编写全面的测试。
     包括：
     - 单元测试
     - 集成测试
     - 边界情况测试"
  `,

  // 调试错误
  debug: `
    "这个测试失败了。请分析错误日志，
     找出根本原因，
     并修复它。"
  `,

  // 重构
  refactor: `
    "请重构这段代码以提高可读性和性能。
     保持功能不变。
     添加注释解释更改。"
  `,

  // GitHub Issue
  githubIssue: `
    "请分析这个 GitHub issue 并实现修复。
     步骤：
     1. 理解问题
     2. 找到相关代码
     3. 实现修复
     4. 编写测试
     5. 创建 PR"
  `
};
```

---

## 28.9 课程总结

### 28.9.1 核心要点

```typescript
/**
 * 课程的关键要点
 */

const courseKeyTakeaways = [
  // 1
  {
    title: "理解架构",
    description: "理解 Claude Code 的底层架构和工具"
  },

  // 2
  {
    title: "探索代码库",
    description: "有效地探索和理解新的代码库"
  },

  // 3
  {
    title: "CLAUDE.md",
    description: "创建和使用 CLAUDE.md 文件进行上下文管理"
  },

  // 4
  {
    title: "提供上下文",
    description: "通过提及相关文件和图像来获取上下文"
  },

  // 5
  {
    title: "先规划",
    description: "在编码之前规划以提高性能"
  },

  // 6
  {
    title: "使用思考模式",
    description: "对困难任务使用思考模式"
  },

  // 7
  {
    title: "编写测试",
    description: "编写测试来评估功能"
  },

  // 8
  {
    title: "Git Worktrees",
    description: "使用 git worktrees 同时添加多个功能"
  },

  // 9
  {
    title: "GitHub 集成",
    description: "使用 GitHub 集成修复 issue 和创建 PR"
  },

  // 10
  {
    title: "Hooks",
    description: "使用 hooks 在工具使用前后执行代码"
  },

  // 11
  {
    title: "MCP 服务器",
    description: "连接到 MCP 服务器（Figma、Playwright）"
  },

  // 12
  {
    title: "最佳实践",
    description: "应用一套最佳实践来加速和改进编码工作流"
  }
];
