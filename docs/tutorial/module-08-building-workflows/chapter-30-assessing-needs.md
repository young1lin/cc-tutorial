# Chapter 30: 评估你的需求

## 学习目标

完成本章后，你将能够：

- 评估你当前的开发工作流和痛点
- 识别 Claude Code 可以提供最大价值的领域
- 确定你的 AI 辅助开发成熟度级别
- 制定个性化的 AI 采用计划
- 避免常见的采用陷阱

## 前置知识

- [Module 1: Claude Code 基础](../module-01-fundamentals/)
- [Module 2: 核心工作流](../module-02-core-workflows/)
- [Module 7: 专家建议与最佳实践](../module-07-expert-wisdom/)

---

## 30.1 为什么评估很重要

```typescript
/**
 * 评估需求：成功采用 AI 的第一步
 */

const assessmentImportance = {
  problem: `
    问题：
    许多开发者直接跳进 AI 辅助开发，
    没有评估他们的实际需求和准备工作。

    结果：
    - 期望不切实际
    - 采用策略不当
    - 效果不佳
    - 最终放弃
  `,

  solution: `
    解决方案：
    在深入采用之前，花时间评估：

    1. 你当前的工作流是什么样的？
    2. 你的主要痛点是什么？
    3. 你准备程度如何？
    4. 你的目标是什么？

    这让你能够：
    - 设定现实的期望
    - 选择正确的采用策略
    - 最大化投资回报率
    - 持续改进
  `
};
```

---

## 30.2 当前工作流分析

### 30.2.1 映射你的开发流程

```typescript
/**
 * Step 1: 绘制你当前的工作流
 */

interface WorkflowStage {
  name: string;
  activities: string[];
  tools: string[];
  painPoints: string[];
  aiPotential: number; // 1-5
}

const myCurrentWorkflow: WorkflowStage[] = [
  {
    name: "需求分析",
    activities: ["阅读需求文档", "与 PM 讨论", "理解用户故事"],
    tools: ["Jira", "Confluence", "Figma"],
    painPoints: ["需求不清晰", "反复确认", "缺少上下文"],
    aiPotential: 4 // AI 可以帮助理解和澄清需求
  },

  {
    name: "架构设计",
    activities: ["设计系统架构", "选择技术栈", "定义接口"],
    tools: ["白板", "绘图工具", "文档"],
    painPoints: ["设计耗时", "容易遗漏边界情况", "文档更新滞后"],
    aiPotential: 3 // AI 可以辅助但不应主导设计
  },

  {
    name: "编码实现",
    activities: ["编写功能代码", "实现 API", "构建 UI"],
    tools: ["VS Code", "浏览器 DevTools"],
    painPoints: ["样板代码多", "API 文档查找", "语法细节"],
    aiPotential: 5 // AI 在这里价值最高
  },

  {
    name: "测试",
    activities: ["编写单元测试", "集成测试", "手动测试"],
    tools: ["Jest", "Cypress", "浏览器"],
    painPoints: ["测试编写耗时", "覆盖率不足", "测试维护"],
    aiPotential: 5 // AI 非常擅长生成测试
  },

  {
    name: "代码审查",
    activities: ["Review PR", "提供反馈", "讨论改进"],
    tools: ["GitHub", "GitLab"],
    painPoints: ["反馈不及时", "细节遗漏", "沟通成本"],
    aiPotential: 4 // AI 可以快速发现常见问题
  },

  {
    name: "调试",
    activities: ["定位 bug", "分析日志", "修复问题"],
    tools: ["Chrome DevTools", "日志工具"],
    painPoints: ["定位困难", "试错成本高", "类似问题重复"],
    aiPotential: 4 // AI 可以帮助分析和建议
  },

  {
    name: "文档编写",
    activities: ["写 API 文档", "更新 README", "编写注释"],
    tools: ["Markdown", "文档生成器"],
    painPoints: ["文档滞后", "格式不一致", "维护困难"],
    aiPotential: 5 // AI 擅长生成文档
  }
];

/**
 * 练习：绘制你自己的工作流
 *
 * 1. 列出你典型开发周期中的所有阶段
 * 2. 为每个阶段识别：
 *    - 你执行的活动
 *    - 你使用的工具
 *    - 你的主要痛点
 *    - AI 的潜在价值（1-5）
 *
 * 2. 找出 AI 潜在价值最高的 3 个阶段
 * 这些应该成为你的 AI 采用重点。
 */
```

### 30.2.2 识别你的痛点

```typescript
/**
 * Step 2: 深入分析痛点
 */

interface PainPointAnalysis {
  category: string;
  severity: "low" | "medium" | "high" | "critical";
  frequency: "rare" | "occasional" | "frequent" | "constant";
  impact: string;
  aiCanHelp: boolean;
  howAIHelps: string;
}

const commonPainPoints: PainPointAnalysis[] = [
  {
    category: "上下文切换",
    severity: "high",
    frequency: "constant",
    impact: "打断思路，降低效率",
    aiCanHelp: true,
    howAIHelps: "CLAUDE.md 提供项目上下文，减少文档查找"
  },

  {
    category: "样板代码",
    severity: "medium",
    frequency: "frequent",
    impact: "浪费时间，容易出错",
    aiCanHelp: true,
    howAIHelps: "快速生成样板代码，专注业务逻辑"
  },

  {
    category: "API 文档查找",
    severity: "low",
    frequency: "frequent",
    impact: "打断编码流程",
    aiCanHelp: true,
    howAIHelps: "AI 直接提供 API 用法，无需切换浏览器"
  },

  {
    category: "测试覆盖不足",
    severity: "high",
    frequency: "constant",
    impact: "bug 逃逸，质量风险",
    aiCanHelp: true,
    howAIHelps: "快速生成测试用例，提高覆盖率"
  },

  {
    category: "代码审查滞后",
    severity: "medium",
    frequency: "frequent",
    impact: "延长开发周期",
    aiCanHelp: true,
    howAIHelps: "AI 实时代码审查，快速反馈"
  },

  {
    category: "知识孤岛",
    severity: "high",
    frequency: "constant",
    impact: "重复工作，协作困难",
    aiCanHelp: true,
    howAIHelps: "共享 CLAUDE.md，统一团队知识"
  },

  {
    category: "技术债务",
    severity: "high",
    frequency: "occasional",
    impact: "长期维护困难",
    aiCanHelp: false, // AI 不应直接处理技术债务
    howAIHelps: "但 AI 可以帮助识别和规划重构"
  }
];

/**
 * 痛点优先级矩阵
 *
 * 高影响 + 高频率 = 优先处理
 * 高影响 + 低频率 = 计划处理
 * 低影响 + 高频率 = 优化处理
 * 低影响 + 低频率 = 忽略
 */

const prioritizePainPoints = (points: PainPointAnalysis[]) => {
  const severityScore = { low: 1, medium: 2, high: 3, critical: 4 };
  const frequencyScore = { rare: 1, occasional: 2, frequent: 3, constant: 4 };

  return points
    .map(p => ({
      ...p,
      priority: severityScore[p.severity] * frequencyScore[p.frequency]
    }))
    .sort((a, b) => b.priority - a.priority);
};
```

---

## 30.3 AI 辅助开发成熟度模型

```typescript
/**
 * AI 辅助开发成熟度模型
 *
 * 这个模型帮助你评估你当前的 AI 使用水平，
 * 并规划向下一个级别的路径。
 */

enum AIDevelopmentMaturityLevel {
  // Level 0: 无意识
  Unaware = 0,

  // Level 1: 意识到
  Aware = 1,

  // Level 2: 实验
  Experimenting = 2,

  // Level 3: 采用
  Adopting = 3,

  // Level 4: 优化
  Optimizing = 4,

  // Level 5: 创新
  Innovating = 5
}

const maturityLevels = {
  [AIDevelopmentMaturityLevel.Unaware]: {
    name: "无意识",
    description: "不了解或不关心 AI 辅助开发",
    characteristics: [
      "没有使用过 AI 编码工具",
      "对 AI 能力不了解",
      "满足于当前工作流"
    ],
    nextSteps: [
      "了解 Claude Code 的能力",
      "阅读成功案例",
      "尝试基础功能"
    ]
  },

  [AIDevelopmentMaturityLevel.Aware]: {
    name: "意识到",
    description: "了解 AI 工具但还没有使用",
    characteristics: [
      "听说过 AI 编码助手",
      "阅读过相关文章",
      "对效果持怀疑态度"
    ],
    nextSteps: [
      "安装 Claude Code",
      "完成第一个任务",
      "体验基本功能"
    ]
  },

  [AIDevelopmentMaturityLevel.Experimenting]: {
    name: "实验",
    description: "偶尔使用 AI 工具进行特定任务",
    characteristics: [
      "使用 AI 生成样板代码",
      "偶尔询问编程问题",
      "没有系统化的使用方式"
    ],
    nextSteps: [
      "识别高价值使用场景",
      "创建 CLAUDE.md",
      "建立使用习惯"
    ]
  },

  [AIDevelopmentMaturityLevel.Adopting]: {
    name: "采用",
    description: "在日常开发中定期使用 AI",
    characteristics: [
      "有配置好的 CLAUDE.md",
      "使用 Plan Mode 处理复杂任务",
      "团队中有 AI 最佳实践分享"
    ],
    nextSteps: [
      "优化工作流",
      "建立团队标准",
      "收集使用数据"
    ]
  },

  [AIDevelopmentMaturityLevel.Optimizing]: {
    name: "优化",
    description: "系统化地优化 AI 辅助开发流程",
    characteristics: [
      "有明确的 AI 使用 SOP",
      "衡量 AI 的 ROI",
      "持续改进提示词",
      "团队培训项目"
    ],
    nextSteps: [
      "分享最佳实践",
      "探索高级功能",
      "创新使用方式"
    ]
  },

  [AIDevelopmentMaturityLevel.Innovating]: {
    name: "创新",
    description: "创建新的 AI 辅助开发模式和工具",
    characteristics: [
      "开发自定义 MCP 服务器",
      "创建团队 Skills",
      "在社区分享经验",
      "影响他人采用"
    ],
    nextSteps: [
      "保持学习",
      "贡献社区",
      "持续创新"
    ]
  }
};

/**
 * 成熟度评估问卷
 *
 * 回答这些问题来确定你的成熟度级别：
 */

const assessmentQuestions = [
  {
    question: "你有配置好的 CLAUDE.md 文件吗？",
    levels: { 0: "没有", 1: "有基础版本", 2: "有优化版本" }
  },
  {
    question: "你多久使用一次 Claude Code？",
    levels: { 0: "从不", 1: "偶尔", 2: "每天", 3: "每个任务" }
  },
  {
    question: "你使用 Plan Mode 吗？",
    levels: { 0: "不知道", 1: "知道但不常用", 2: "复杂任务必用" }
  },
  {
    question: "你的团队有 AI 使用规范吗？",
    levels: { 0: "没有", 1: "有非正式讨论", 2: "有正式文档" }
  },
  {
    question: "你衡量 AI 的效果吗？",
    levels: { 0: "不衡量", 1: "主观感受", 2: "有数据跟踪" }
  },
  {
    question: "你开发了自定义工具吗（Skills/MCP）？",
    levels: { 0: "没有", 1: "计划中", 2: "有自定义工具" }
  }
];
```

---

## 30.4 角色特定考虑

### 30.4.1 不同角色的评估重点

```typescript
/**
 * 不同开发角色的评估重点
 */

interface RoleAssessment {
  role: string;
  primaryGoals: string[];
  aiValueAreas: string[];
  commonConcerns: string[];
  recommendedStartingPoints: string[];
}

const roleAssessments: RoleAssessment[] = [
  {
    role: "前端开发者",
    primaryGoals: [
      "快速实现 UI",
      "处理响应式设计",
      "管理状态",
      "优化用户体验"
    ],
    aiValueAreas: [
      "生成组件代码",
      "转换设计到代码",
      "编写样式",
      "生成测试用例"
    ],
    commonConcerns: [
      "代码一致性",
      "性能优化",
      "浏览器兼容性",
      "框架更新"
    ],
    recommendedStartingPoints: [
      "让 AI 生成组件模板",
      "使用 AI 解释复杂 CSS",
      "AI 辅助编写单元测试",
      "创建前端特定的 CLAUDE.md"
    ]
  },

  {
    role: "后端开发者",
    primaryGoals: [
      "设计 API",
      "处理数据逻辑",
      "确保安全性",
      "优化性能"
    ],
    aiValueAreas: [
      "生成 API 端点",
      "编写数据库查询",
      "实现认证逻辑",
      "生成 API 文档"
    ],
    commonConcerns: [
      "数据一致性",
      "安全性漏洞",
      "性能瓶颈",
      "扩展性"
    ],
    recommendedStartingPoints: [
      "让 AI 生成 CRUD 操作",
      "AI 辅助编写集成测试",
      "使用 AI 检查安全问题",
      "创建后端特定的 CLAUDE.md"
    ]
  },

  {
    role: "全栈开发者",
    primaryGoals: [
      "端到端功能交付",
      "技术栈协调",
      "快速原型",
      "产品迭代"
    ],
    aiValueAreas: [
      "生成全栈功能",
      "连接前后端",
      "快速原型",
      "全栈测试"
    ],
    commonConcerns: [
      "上下文切换",
      "技术栈广度",
      "架构决策",
      "时间管理"
    ],
    recommendedStartingPoints: [
      "使用 AI 进行完整功能开发",
      "CLAUDE.md 包含全栈架构",
      "AI 辅助技术选型",
      "并行处理前后端任务"
    ]
  },

  {
    role: "移动开发者",
    primaryGoals: [
      "构建原生体验",
      "处理平台差异",
      "优化性能",
      "应用商店发布"
    ],
    aiValueAreas: [
      "生成平台特定代码",
      "处理权限",
      "实现常见功能",
      "平台适配"
    ],
    commonConcerns: [
      "平台规范",
      "性能要求",
      "更新审核",
      "设备差异"
    ],
    recommendedStartingPoints: [
      "AI 生成平台代码模板",
      "处理平台特定 API",
      "AI 辅助性能优化",
      "创建移动端 CLAUDE.md"
    ]
  },

  {
    role: "数据工程师/ML 工程师",
    primaryGoals: [
      "数据处理管道",
      "模型训练",
      "特征工程",
      "模型部署"
    ],
    aiValueAreas: [
      "生成数据处理代码",
      "编写训练脚本",
      "数据可视化",
      "模型监控"
    ],
    commonConcerns: [
      "数据质量",
      "模型准确性",
      "计算资源",
      "实验可重复性"
    ],
    recommendedStartingPoints: [
      "AI 辅助数据探索",
      "生成实验模板",
      "AI 编写数据处理管道",
      "创建数据科学 CLAUDE.md"
    ]
  },

  {
    role: "DevOps/SRE",
    primaryGoals: [
      "CI/CD 管道",
      "基础设施管理",
      "监控告警",
      "可靠性"
    ],
    aiValueAreas: [
      "生成配置文件",
      "编写脚本",
      "故障排查",
      "文档生成"
    ],
    commonConcerns: [
      "安全性",
      "稳定性",
      "合规性",
      "可追溯性"
    ],
    recommendedStartingPoints: [
      "AI 生成 Docker/K8s 配置",
      "AI 辅助编写 Terraform",
      "AI 分析日志",
      "创建 DevOps CLAUDE.md"
    ]
  },

  {
    role: "技术负责人/架构师",
    primaryGoals: [
      "技术决策",
      "团队效率",
      "代码质量",
      "长期可维护性"
    ],
    aiValueAreas: [
      "架构方案比较",
      "技术调研",
      "代码审查",
      "最佳实践推广"
    ],
    commonConcerns: [
      "团队一致性",
      "技术债务",
      "知识传递",
      "过度依赖"
    ],
    recommendedStartingPoints: [
      "使用 AI 进行技术调研",
      "AI 辅助架构评审",
      "创建团队 CLAUDE.md",
      "制定 AI 使用规范"
    ]
  }
];
```

### 30.4.2 团队规模考虑

```typescript
/**
 * 不同团队规模的采用策略
 */

const teamSizeStrategies = {
  solo: {
    size: "1 人（独立开发者）",
    advantages: [
      "快速决策",
      "灵活采用",
      "无协调成本"
    ],
    challenges: [
      "知识孤岛",
      "无人审查",
      "容易过度依赖"
    ],
    strategy: `
      独立开发者策略：

      1. 充分利用 AI - 你没有团队成员可以咨询
      2. 保持审查习惯 - 特别容易跳过审查
      3. 定期手工编码 - 保持技能敏锐
      4. 加入社区 - 获取外部反馈
      5. 文档一切 - AI 帮助你记忆决策
    `
  },

  smallTeam: {
    size: "2-5 人（小团队）",
    advantages: [
      "快速协调",
      "灵活适应",
      "容易统一标准"
    ],
    challenges: [
      "工作流不一致",
      "知识分散",
      "培训成本"
    ],
    strategy: `
      小团队策略：

      1. 建立 CLAUDE.md 标准 - 共享项目知识
      2. 定期分享会 - 交流最佳实践
      3. 配对编程 - AI + 人类
      4. 统一工具链 - 相同的配置
      5. 互相审查 - 不要盲目信任 AI
    `
  },

  mediumTeam: {
    size: "6-20 人（中型团队）",
    advantages: [
      "有专业知识",
      "可以分工",
      "有流程基础"
    ],
    challenges: [
      "一致性维护",
      "文化差异",
      "培训规模化"
    ],
    strategy: `
      中型团队策略：

      1. 指定 AI 倡导者 - 推动采用
      2. 创建模板 - CLAUDE.md、配置文件
      3. 培训项目 - 系统化学习
      4. 最佳实践文档 - 收集和分享
      5. 渐进采用 - 从小项目开始
    `
  },

  largeTeam: {
    size: "20+ 人（大团队）",
    advantages: [
      "资源充足",
      "专业分工",
      "有成熟流程"
    ],
    challenges: [
      "审批流程",
      "安全合规",
      "文化变革阻力"
    ],
    strategy: `
      大团队策略：

      1. 自上而下支持 - 管理层背书
      2. 试点项目 - 证明价值
      3. 官方指南 - 标准化使用
      4. 安全审查 - 权限管理
      5. 持续培训 - 新人入职
      6. 效果衡量 - ROI 分析
    `
  }
};
```

---

## 30.5 技术栈考虑

```typescript
/**
 * 不同技术栈的 AI 采用考虑
 */

interface TechStackConsideration {
  stack: string;
  aiStrength: string;
  aiWeakness: string;
  claudeMdTips: string[];
}

const techStackConsiderations: TechStackConsideration[] = [
  {
    stack: "React / Next.js",
    aiStrength: "组件生成、Hook 使用、状态管理",
    aiWeakness: "最新特性、性能优化细节",
    claudeMdTips: [
      "指定 React 版本",
      "说明使用的状态管理库",
      "描述组件模式（函数组件、类组件）",
      "列出关键依赖（UI 库、路由等）"
    ]
  },

  {
    stack: "Vue / Nuxt",
    aiStrength: "模板生成、组合式 API、响应式系统",
    aiWeakness: "Vue 2 vs 3 差异、特定插件",
    claudeMdTips: [
      "明确 Vue 版本（2 或 3）",
      "说明使用的 UI 框架",
      "描述状态管理模式",
      "列出常用 composition API"
    ]
  },

  {
    stack: "Angular",
    aiStrength: "服务生成、依赖注入、RxJS",
    aiWeakness: "Angular 特有概念、最佳实践",
    claudeMdTips: [
      "指定 Angular 版本",
      "描述状态管理（NgRx 等）",
      "说明使用的模块模式",
      "列出自定义指令和管道"
    ]
  },

  {
    stack: "Node.js / Express",
    aiStrength: "路由生成、中间件、REST API",
    aiWeakness: "性能优化、安全最佳实践",
    claudeMdTips: [
      "说明 Node 版本",
      "描述框架选择（Express、Fastify 等）",
      "列出数据库 ORM",
      "说明认证方式"
    ]
  },

  {
    stack: "Python / Django / FastAPI",
    aiStrength: "模型生成、视图、序列化器",
    aiWeakness: "Python 特有模式、异步处理",
    claudeMdTips: [
      "指定 Python 版本",
      "说明框架（Django/Flask/FastAPI）",
      "描述 ORM 使用",
      "列出关键依赖"
    ]
  },

  {
    stack: "Java / Spring Boot",
    aiStrength: "实体生成、Repository、Service",
    aiWeakness: "Spring 复杂配置、Java 生态",
    claudeMdTips: [
      "指定 Java 和 Spring 版本",
      "描述架构模式",
      "列出数据库和 JPA 提供",
      "说明安全配置"
    ]
  },

  {
    stack: "Go",
    aiStrength: "并发模式、接口设计、错误处理",
    aiWeakness: "Go 特有惯用法、性能细节",
    claudeMdTips: [
      "说明项目结构（标准 vs 自定义）",
      "描述使用的框架",
      "列出关键包",
      "说明并发模式"
    ]
  },

  {
    stack: "Rust",
    aiStrength: "结构体定义、trait 实现",
    aiWeakness: "借用检查、生命周期、unsafe",
    claudeMdTips: [
      "说明 Rust 版本",
      "描述使用的异步运行时",
      "列出关键 crates",
      "强调安全和性能考虑"
    ]
  }
];
```

---

## 30.6 制定采用计划

### 30.6.1 SMART 目标设定

```typescript
/**
 * 制定你的 AI 采用计划
 */

interface AdoptionPlan {
  timeline: string;
  goals: SMARTGoal[];
  milestones: Milestone[];
  successMetrics: SuccessMetric[];
}

interface SMARTGoal {
  specific: string;    // 具体的
  measurable: string;  // 可衡量的
  achievable: string;  // 可实现的
  relevant: string;    // 相关的
  timeBound: string;   // 有时限的
}

const exampleAdoptionPlans: AdoptionPlan[] = [
  {
    timeline: "30 天快速启动计划",
    goals: [
      {
        specific: "每天至少使用 Claude Code 完成 1 个任务",
        measurable: "记录每日使用情况",
        achievable: "从简单任务开始",
        relevant: "建立使用习惯",
        timeBound: "持续 30 天"
      },
      {
        specific: "为当前项目创建完善的 CLAUDE.md",
        measurable: "CLAUDE.md 包含所有必需部分",
        achievable: "迭代式完善",
        relevant: "提供充分上下文",
        timeBound: "第 1 周完成"
      },
      {
        specific: "使用 Plan Mode 完成至少 3 个复杂任务",
        measurable: "记录 Plan Mode 使用效果",
        achievable: "选择适当复杂度的任务",
        relevant: "掌握核心工作流",
        timeBound: "30 天内"
      }
    ],
    milestones: [
      { week: 1, milestone: "安装配置，创建 CLAUDE.md" },
      { week: 2, milestone: "完成 5 个 AI 辅助任务" },
      { week: 3, milestone: "使用 Plan Mode 处理复杂任务" },
      { week: 4, milestone: "评估效果，调整计划" }
    ],
    successMetrics: [
      { metric: "任务完成时间", target: "减少 20%" },
      { metric: "CLAUDE.md 质量", target: "包含所有必需部分" },
      { metric: "使用频率", target: "每天至少 1 次" },
      { metric: "满意度", target: "主观评分 7+/10" }
    ]
  },

  {
    timeline: "90 天深度采用计划",
    goals: [
      {
        specific: "在 50% 的开发任务中使用 Claude Code",
        measurable: "跟踪任务类型和使用率",
        achievable: "逐步增加使用场景",
        relevant: "最大化 AI 价值",
        timeBound: "90 天内"
      },
      {
        specific: "建立团队的 AI 使用规范",
        measurable: "完成规范文档",
        achievable: "基于最佳实践",
        relevant: "团队一致性",
        timeBound: "第 60 天完成"
      },
      {
        specific: "开发至少 1 个自定义 Skill 或 MCP",
        measurable: "成功部署和使用",
        achievable: "从简单工具开始",
        relevant: "深度定制工作流",
        timeBound: "90 天内"
      }
    ],
    milestones: [
      { week: 2, milestone: "基础使用熟练" },
      { week: 4, milestone: "CLAUDE.md 优化完成" },
      { week: 8, milestone: "团队规范完成" },
      { week: 10, milestone: "自定义工具开发" },
      { week: 12, milestone: "效果评估和总结" }
    ],
    successMetrics: [
      { metric: "开发效率", target: "提升 30%" },
      { metric: "代码质量", target: "保持或提升" },
      { metric: "团队采用率", target: "80% 成员使用" },
      { metric: "自定义工具", target: "至少 1 个" }
    ]
  }
];

/**
 * 练习：制定你自己的采用计划
 *
 * 1. 选择合适的时间线（30/60/90 天）
 * 2. 设定 SMART 目标
 * 3. 定义里程碑
 * 4. 确定成功指标
 * 5. 定期审查和调整
 */
```

### 30.6.2 渐进式采用路径

```typescript
/**
 * 渐进式采用：从小到大
 */

const progressiveAdoption = {
  phase1: {
    name: "第 1 阶段：实验（1-2 周）",
    focus: "低风险任务",
    tasks: [
      "生成样板代码",
      "编写简单测试",
      "解释代码",
      "格式化代码",
      "编写文档注释"
    ],
    do: [
      "选择非关键任务",
      "充分审查输出",
      "记录效果",
      "建立使用习惯"
    ],
    dont: [
      "不要在生产代码中使用",
      "不要不经审查就提交",
      "不要期望完美"
    ]
  },

  phase2: {
    name: "第 2 阶段：集成（2-4 周）",
    focus: "日常开发任务",
    tasks: [
      "实现新功能",
      "重构代码",
      "调试问题",
      "代码审查",
      "编写复杂测试"
    ],
    do: [
      "使用 Plan Mode",
      "创建 CLAUDE.md",
      "建立工作流程",
      "分享经验"
    ],
    dont: [
      "不要让 AI 做架构决策",
      "不要跳过测试",
      "不要失去理解"
    ]
  },

  phase3: {
    name: "第 3 阶段：优化（4-8 周）",
    focus: "工作流优化",
    tasks: [
      "开发自定义 Skills",
      "配置 MCP 服务器",
      "优化提示词",
      "建立团队标准",
      "衡量效果"
    ],
    do: [
      "系统化优化",
      "数据驱动决策",
      "团队培训",
      "最佳实践分享"
    ],
    dont: [
      "不要过度优化",
      "不要忽视反馈",
      "不要停止学习"
    ]
  },

  phase4: {
    name: "第 4 阶段：创新（持续）",
    focus: "创造新方式",
    tasks: [
      "开发新工具",
      "探索新用法",
      "社区贡献",
      "影响他人"
    ],
    do: [
      "保持实验精神",
      "分享创新",
      "持续学习",
      "反馈改进"
    ],
    dont: [
      "不要固步自封",
      "不要忽视安全",
      "不要停止反思"
    ]
  }
};
```

---

## 30.7 常见陷阱和如何避免

```typescript
/**
 * 常见的 AI 采用陷阱
 */

const commonPitfalls = [
  {
    pitfall: "期望不切实际",
    description: "期望 AI 立即解决所有问题",
    consequences: [
      "失望和放弃",
      "错误的工具选择",
      "资源浪费"
    ],
    prevention: [
      "设定现实的期望",
      "从简单开始",
      "逐步提高目标",
      "关注渐进改进"
    ]
  },

  {
    pitfall: "盲目信任输出",
    description: "不经审查就使用 AI 生成的代码",
    consequences: [
      "代码质量下降",
      "安全漏洞",
      "技能退化"
    ],
    prevention: [
      "总是审查代码",
      "理解生成的逻辑",
      "运行测试",
      "保持学习模式"
    ]
  },

  {
    pitfall: "忽视上下文",
    description: "不给 AI 充分的项目上下文",
    consequences: [
      "输出质量差",
      "反复修改",
      "效率低下"
    ],
    prevention: [
      "创建 CLAUDE.md",
      "提及相关文件",
      "提供背景信息",
      "使用图像说明"
    ]
  },

  {
    pitfall: "过度依赖",
    description: "让 AI 做所有决策",
    consequences: [
      "失去工程判断",
      "架构问题",
      "长期维护困难"
    ],
    prevention: [
      "保留决策权",
      "AI 辅助而非替代",
      "保持技能练习",
      "定期手工编码"
    ]
  },

  {
    pitfall: "忽视团队一致性",
    description: "个人使用但没有团队标准",
    consequences: [
      "代码风格不一致",
      "知识孤岛",
      "协作困难"
    ],
    prevention: [
      "共享 CLAUDE.md",
      "建立团队规范",
      "定期分享会",
      "互相学习"
    ]
  },

  {
    pitfall: "不衡量效果",
    description: "不知道 AI 是否真的有帮助",
    consequences: [
      "无法证明价值",
      "无法优化",
      "可能放弃有用工具"
    ],
    prevention: [
      "定义成功指标",
      "跟踪使用数据",
      "定期评估",
      "数据驱动优化"
    ]
  },

  {
    pitfall: "停止学习",
    description: "依赖 AI 后不再深入学习技术",
    consequences: [
      "技能退化",
      "无法解决复杂问题",
      "职业发展受限"
    ],
    prevention: [
      "把 AI 当学习工具",
      "理解 AI 的输出",
      "学习底层原理",
      "保持好奇心"
    ]
  }
];
```

---

## 30.8 自我评估清单

```typescript
/**
 * 使用这个清单评估你的准备程度
 */

const selfAssessmentChecklist = {
  category1: {
    name: "技术准备",
    items: [
      { checked: false, item: "我已安装 Claude Code" },
      { checked: false, item: "我了解基本的快捷键和命令" },
      { checked: false, item: "我的开发环境配置正确" },
      { checked: false, item: "我有 Git 版本控制设置" }
    ]
  },

  category2: {
    name: "项目准备",
    items: [
      { checked: false, item: "我有 CLAUDE.md 文件" },
      { checked: false, item: "我的项目有测试" },
      { checked: false, item: "我理解项目架构" },
      { checked: false, item: "我的代码库有适当文档" }
    ]
  },

  category3: {
    name: "心理准备",
    items: [
      { checked: false, item: "我有现实的期望" },
      { checked: false, item: "我愿意审查 AI 的输出" },
      { checked: false, item: "我理解 AI 的局限性" },
      { checked: false, item: "我对学习持开放态度" }
    ]
  },

  category4: {
    name: "团队准备（如适用）",
    items: [
      { checked: false, item: "团队了解 AI 工具" },
      { checked: false, item: "我们有使用指南或规范" },
      { checked: false, item: "我们有分享机制" },
      { checked: false, item: "管理层支持使用" }
    ]
  },

  interpret(score: number) {
    if (score >= 15) return "准备充分，可以全面采用";
    if (score >= 10) return "基本准备，可以渐进采用";
    if (score >= 5) return "部分准备，建议从实验开始";
    return "准备不足，建议先完成基础准备";
  }
};

/**
 * 练习：完成自我评估
 *
 * 1. 检查每个项目
 * 2. 计算总分
 * 3. 根据分数确定你的采用策略
 * 4. 识别需要改进的领域
 */
```

---

## 30.9 练习

### 练习 1：工作流映射

绘制你当前的开发工作流，识别：
- 每个阶段的活动
- 使用的工具
- 主要痛点
- AI 的潜在价值（1-5）

找出 AI 潜在价值最高的 3 个阶段。

### 练习 2：成熟度评估

使用成熟度模型评估你当前的水平：
1. 回答评估问题
2. 确定你的成熟度级别
3. 阅读下一级别的建议
4. 制定提升计划

### 练习 3：制定采用计划

使用 SMART 目标框架制定你的 30 天或 90 天采用计划：
1. 设定具体目标
2. 定义可衡量的指标
3. 确保目标可实现
4. 确认与工作相关
5. 设定时间框架

### 练习 4：识别陷阱

评估你当前情况，识别：
1. 你最容易陷入哪个陷阱？
2. 如何预防？
3. 需要建立什么习惯？

---

## 30.10 进一步阅读

- [Chapter 31: 创建 CLAUDE.md 模板](chapter-31-claude-md-template.md) - 下一章
- [Module 7: 专家建议与最佳实践](../module-07-expert-wisdom/) - 专家建议
- [Claude Code 官方文档](https://docs.anthropic.com/claude-code/) - 官方指南

---

## 视频脚本

### Episode 30: 评估你的需求 (16 分钟)

#### [0:00-1:00] 引入

**视觉元素**：
- 标题："AI 辅助开发的第一步：了解自己"
- 评估流程图

**内容**：
> 在深入采用 AI 辅助开发之前，最重要的是：**了解你自己**。
>
> 你当前的工作流是什么样的？你的主要痛点是什么？你准备得怎么样？
>
> 这个评估将决定你的 AI 采用策略是成功还是失败。

#### [1:00-4:00] 工作流分析

**视觉元素**：
- 工作流阶段列表
- 痛点分析表格

**内容**：
> **第一步：映射你的工作流**
>
> 一个典型的开发周期包括：
> - 需求分析
> - 架构设计
> - 编码实现
> - 测试
> - 代码审查
> - 调试
> - 文档编写
>
> 对每个阶段，问自己：
> 1. 我主要做什么活动？
> 2. 我使用什么工具？
> 3. 我的痛点是什么？
> 4. AI 的潜在价值有多大（1-5）？
>
> 找出 AI 价值最高的 3 个阶段 - 这些是你的采用重点。

#### [4:00-7:00] 成熟度模型

**视觉元素**：
- 6 级成熟度模型图表
- 每个级别的特征

**内容**：
> **AI 辅助开发成熟度模型**：
>
> - **Level 0 - 无意识**：不了解或不关心
> - **Level 1 - 意识到**：了解但还没使用
> - **Level 2 - 实验**：偶尔使用特定任务
> - **Level 3 - 采用**：定期使用，有 CLAUDE.md
> - **Level 4 - 优化**：系统化优化，有 SOP
> - **Level 5 - 创新**：创建新工具和模式
>
> [展示评估问题]
>
> 确定你的级别，然后看下一级别的建议。

#### [7:00-10:00] 角色和团队考虑

**视觉元素**：
- 不同角色的评估重点
- 团队规模策略

**内容**：
> **不同角色，不同策略**：
>
> - **前端开发者**：组件生成、样式编写、测试
> - **后端开发者**：API 生成、数据库查询、安全检查
> - **全栈开发者**：端到端功能、快速原型
> - **技术负责人**：架构评审、技术调研、团队标准
>
> **团队规模考虑**：
> - **独立开发者**：充分利用 AI，保持审查习惯
> - **小团队**：建立 CLAUDE.md 标准，定期分享
> - **大团队**：试点项目，官方指南，安全审查

#### [10:00-13:00] 制定采用计划

**视觉元素**：
- SMART 目标模板
- 渐进式采用路径（4 个阶段）

**内容**：
> **制定你的采用计划**：
>
> **SMART 目标**：
> - **S**pecific - 具体的
> - **M**easurable - 可衡量的
> - **A**chievable - 可实现的
> - **R**elevant - 相关的
> - **T**ime-bound - 有时限的
>
> **渐进式采用路径**：
> 1. **第 1 阶段（1-2 周）**：实验 - 低风险任务
> 2. **第 2 阶段（2-4 周）**：集成 - 日常任务
> 3. **第 3 阶段（4-8 周）**：优化 - 工作流优化
> 4. **第 4 阶段（持续）**：创新 - 创造新方式
>
> [展示 30 天和 90 天计划示例]

#### [13:00-16:00] 陷阱与总结

**视觉元素**：
- 常见陷阱列表
- 自我评估清单

**内容**：
> **常见陷阱**：
>
> 1. ❌ 期望不切实际 → ✅ 设定现实目标
> 2. ❌ 盲目信任输出 → ✅ 总是审查代码
> 3. ❌ 忽视上下文 → ✅ 创建 CLAUDE.md
> 4. ❌ 过度依赖 → ✅ AI 辅助而非替代
> 5. ❌ 不衡量效果 → ✅ 跟踪使用数据
>
> **自我评估清单**：
> - 技术准备（4 项）
> - 项目准备（4 项）
> - 心理准备（4 项）
> - 团队准备（4 项）
>
> **总结**：
> 了解你的需求是成功采用 AI 的第一步。花时间评估，制定计划，然后渐进式采用。
>
> 下一章，我们将学习如何创建一个优秀的 CLAUDE.md 模板。
