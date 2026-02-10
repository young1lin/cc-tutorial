# Chapter 25: "AI 辅助工程" vs "AI 自动化工程"

## 学习目标

完成本章后，你将能够：

- 理解"AI 辅助工程"与"AI 自动化工程"的区别
- 知道如何正确地使用 Claude Code
- 避免过度依赖 AI
- 建立健康的人机协作模式
- 保持工程师的核心价值

## 前置知识

- [Chapter 23: LLM 真实工作原理](chapter-23-how-llms-work.md)
- [Chapter 24: AI 失败案例](chapter-24-ai-failures.md)
- 所有前面的章节内容

---

## 25.1 两种模式的对比

### 25.1.1 核心区别

```
┌─────────────────────────────────────────────────────────────┐
│       AI 辅助工程 vs AI 自动化工程                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  AI 辅助工程 (AI-Assisted Engineering)              │   │
│  │  ─────────────────────────────────────────          │   │
│  │                                                       │   │
│  │  核心理念：AI 是工具，工程师是导演                   │   │
│  │                                                       │   │
│  │  特征：                                               │   │
│  │  ├─ 工程师做决策                                     │   │
│  │  ├─ AI 提供建议和选项                               │   │
│  │  ├─ 工程师审查 AI 的输出                             │   │
│  │  ├─ 工程师对最终结果负责                             │   │
│  │  └─ AI 放大工程师的能力                              │   │
│  │                                                       │   │
│  │  比例：工程师 70% + AI 30%                           │   │
│  │                                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  AI 自动化工程 (AI-Automated Engineering)            │   │
│  │  ────────────────────────────────────────           │   │
│  │                                                       │   │
│  │  核心理念：AI 做所有事（危险！）                      │   │
│  │                                                       │   │
│  │  特征：                                               │   │
│  │  ├─ AI 做决策                                        │   │
│  │  ├─ AI 生成代码                                      │   │
│  │  ├─ 工程师不审查                                     │   │
│  │  ├─ 没有人对结果负责                                 │   │
│  │  └─ 工程师能力退化                                   │   │
│  │                                                       │   │
│  │  比例：工程师 10% + AI 90%                           │   │
│  │                                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 25.1.2 具体场景对比

```typescript
/**
 * 场景 1: 实现一个新功能
 */

/**
 * ❌ AI 自动化工程 (不推荐)
 */
async function implementFeatureAutomated() {
  // 工程师：让 AI 做所有事
  user: "帮我实现用户评论功能"

  // AI：生成所有代码
  ai: `好的，这是完整的实现：
      [生成 500 行代码]

      包括：
      - 前端组件
      - 后端 API
      - 数据库模型
      - 测试用例`

  // 工程师：不理解代码，直接提交
  engineer: [直接提交到生产环境]

  // 结果：
  // - 可能的 bug
  // - 可能的安全问题
  // - 可能的性能问题
  // - 没人真正理解代码
}

/**
 * ✅ AI 辅助工程 (推荐)
 */
async function implementFeatureAssisted() {
  // 工程师：设计解决方案
  engineer: `
    # 功能设计
    用户评论功能需要：
    - 评论 CRUD 操作
    - 评论权限控制
    - 评论审核流程
    - 防止垃圾评论

    # 架构决策
    - 使用 REST API
    - PostgreSQL 存储
    - Redis 缓存热门评论
  `;

  // AI：根据设计生成代码
  ai: "理解了。让我先生成 API 接口定义，您确认后继续..."

  // 工程师：审查并迭代
  engineer: "接口设计不错，但需要添加评论举报功能。"
  ai: "好的，添加举报接口..."

  // 工程师：理解每部分代码
  engineer: "解释一下缓存失效逻辑..."
  ai: [详细解释]

  // 工程师：编写测试
  engineer: "我来编写测试用例，确保边界情况覆盖。"

  // 工程师：代码审查
  engineer: [仔细审查 AI 生成的代码]
  engineer: "这里有个性能问题，让我修复..."

  // 结果：
  // - 代码质量高
  // - 工程师完全理解
  // - 测试覆盖完整
  // - 有负责人
}

/**
 * 场景 2: Debug 问题
 */

/**
 * ❌ AI 自动化工程
 */
async function debugAutomated() {
  // 工程师：直接把错误信息给 AI
  engineer: "报错了，帮我修复"

  // AI：给出解决方案
  ai: "把 this.timeout = 10000 改为 this.timeout = 20000"

  // 工程师：不理解原因，直接应用
  engineer: [复制粘贴]

  // 问题：
  // - 没有理解根本原因
  // - 可能是错误的解决方案
  // - 同类问题会再次发生
}

/**
 * ✅ AI 辅助工程
 */
async function debugAssisted() {
  // 工程师：先自己分析
  engineer: `
    # 问题分析
    错误：Request timeout after 10s
    发生在：用户数据导入功能

    # 可能原因
    1. 数据量太大
    2. 网络问题
    3. 服务器性能

    # 我已经检查
    - 服务器 CPU 正常
    - 网络连接稳定
    - 数据量约 1000 条
  `;

  // AI：帮助分析
  ai: `
    基于你的分析，可能的原因：
    1. 同步处理 1000 条请求
    2. 没有使用批处理

    建议方案：
    - 使用批处理，每次 100 条
    - 添加进度反馈
    - 实现重试机制
  `;

  // 工程师：理解后实施
  engineer: [理解方案，自己实施]

  // 工程师：验证解决方案
  engineer: [测试验证，确认问题解决]
}
```

---

## 25.2 健康的人机协作模式

### 25.2.1 工程师的核心职责

```typescript
/**
 * AI 无法替代的工程师职责
 */

/**
 * 1. 问题理解和分解
 */
interface EngineerResponsibility {
  understandProblem: {
    // AI 不擅长
    aiCannot: [
      "理解模糊的需求",
      "识别隐含的约束",
      "权衡业务优先级",
      "考虑长期影响"
    ];

    // 工程师必须做
    engineerMust: [
      "与利益相关者沟通",
      "明确需求边界",
      "识别技术债务",
      "规划架构演进"
    ];
  };
}

/**
 * 2. 架构决策
 */
const ARCHITECTURE_DECISIONS = {
  // 这些决策不能让 AI 做
  requireHumanJudgment: [
    {
      decision: "选择技术栈",
      factors: [
        "团队技能",
        "现有架构",
        "维护成本",
        "社区支持",
        "长期发展"
      ],
      whyHuman: "需要考虑上下文和未来"
    },
    {
      decision: "设计 API 接口",
      factors: [
        "用户体验",
        "向后兼容",
        "版本策略",
        "安全性"
      ],
      whyHuman: "需要理解业务和使用场景"
    },
    {
      decision: "制定代码规范",
      factors: [
        "团队风格",
        "项目特性",
        "工具集成"
      ],
      whyHuman: "需要考虑团队协作"
    }
  ]
};

/**
 * 3. 代码质量责任
 */
class CodeQualityResponsibility {
  /**
   * 工程师必须做：
   */

  // ✅ 审查每一行代码
  reviewCode(aiGeneratedCode: string): void {
    // 理解每一行在做什么
    // 检查是否有潜在问题
    // 确保符合项目规范
  }

  // ✅ 编写测试
  writeTests(): void {
    // AI 可以生成测试框架
    // 但工程师必须：
    // - 定义测试场景
    // - 考虑边界情况
    // - 验证测试质量
  }

  // ✅ 性能优化
  optimizePerformance(): void {
    // AI 可能写出"能跑"的代码
    // 但工程师必须：
    // - 识别性能瓶颈
    // - 考虑优化策略
    // - 测量优化效果
  }

  // ✅ 安全审查
  securityReview(): void {
    // AI 不知道所有安全漏洞
    // 工程师必须：
    // - 检查输入验证
    // - 验证权限控制
    // - 审查数据处理
  }
}
```

### 25.2.2 AI 的正确角色

```typescript
/**
 * AI 的正确角色：助手和倍增器
 */

/**
 * 角色 1: 知识检索器
 */
const aiAsKnowledgeRetriever = {
  // ✅ AI 擅长
  goodAt: [
    "查找 API 文档",
    "回忆语法细节",
    "提供代码示例",
    "解释概念"
  ],

  // 使用方式
  howToUse: `
    engineer: "React 的 useEffect 依赖数组如何工作？"
    ai: [详细解释 + 示例代码]
    engineer: [理解后应用]
  `
};

/**
 * 角色 2: 代码生成器
 */
const aiAsCodeGenerator = {
  // ✅ AI 擅长
  goodAt: [
    "生成样板代码",
    "实现标准算法",
    "转换数据格式",
    "编写重复逻辑"
  ],

  // 使用方式
  howToUse: `
    engineer: "生成一个 TypeScript 的 User 接口和验证函数"
    ai: [生成代码]
    engineer: [审查并调整]
  `
};

/**
 * 角色 3: 代码审查助手
 */
const aiAsCodeReviewAssistant = {
  // ✅ AI 擅长
  goodAt: [
    "发现常见 bug",
    "识别代码异味",
    "建议改进",
    "检查规范"
  ],

  // 使用方式
  howToUse: `
    engineer: "审查这段代码的潜在问题"
    ai: [列出问题 + 建议改进]
    engineer: [评估建议，选择性应用]
  `
};

/**
 * 角色 4: 测试生成助手
 */
const aiAsTestGenerator = {
  // ✅ AI 擅长
  goodAt: [
    "生成测试框架",
    "提供测试用例",
    "创建 mock 数据"
  ],

  // 使用方式
  howToUse: `
    engineer: "为这个函数生成测试用例"
    ai: [生成测试]
    engineer: [补充边界情况 + 审查测试质量]
  `
};

/**
 * 角色 5: 文档编写助手
 */
const aiAsDocumentationWriter = {
  // ✅ AI 擅长
  goodAt: [
    "生成 JSDoc",
    "编写 README",
    "创建 API 文档"
  ],

  // 使用方式
  howToUse: `
    engineer: "为这些函数生成文档"
    ai: [生成文档]
    engineer: [审查准确性 + 补充细节]
  `
};
```

---

## 25.3 实际工作流程对比

### 25.3.1 AI 辅助的工作流程

```typescript
/**
 * ✅ 健康的 AI 辅助工作流
 */

/**
 * Step 1: 工程师理解问题
 */
async function aiAssistedWorkflow(task: string) {
  // 工程师：先自己思考
  const myUnderstanding = {
    what: task,
    constraints: [
      "现有架构",
      "团队能力",
      "时间限制"
    ],
    approach: "我的初步想法..."
  };

  /**
   * Step 2: 使用 Plan Mode
   */
  // Shift+Tab (两次)
  // 让 Claude 先规划，而不是直接写代码

  const plan = await claudeCode.plan({
    task: task,
    context: {
      existingArchitecture: myUnderstanding.constraints,
      myApproach: myUnderstanding.approach
    }
  });

  /**
   * Step 3: 工程师审查计划
   */
  const reviewedPlan = engineerReview(plan);
  // - 这个方案合理吗？
  // - 有没有遗漏的地方？
  // - 需要调整什么？

  /**
   * Step 4: 迭代实施
   */
  const implementation = await claudeCode.implement(reviewedPlan);

  // 工程师：逐步审查
  for (const part of implementation.parts) {
    // 理解每部分代码
    const myUnderstanding = understandCode(part.code);

    // 如果不理解，问 AI
    if (!myUnderstanding) {
      const explanation = await claudeCode.explain(part.code);
      // 学习代码的原理
    }

    // 检查代码质量
    const issues = reviewCodeQuality(part.code);

    // 如果有问题，让 AI 修复
    if (issues.length > 0) {
      const fixed = await claudeCode.fix(part.code, issues);
      // 再次审查
    }
  }

  /**
   * Step 5: 工程师编写测试
   */
  const tests = engineerWriteTests(implementation);

  // 可以让 AI 帮忙生成测试框架
  const testFramework = await claudeCode.generateTestFramework(
    implementation
  );

  // 但工程师必须：
  // - 定义测试场景
  // - 考虑边界情况
  // - 验证测试质量

  /**
   * Step 6: 运行测试
   */
  const testResults = runTests(tests);

  if (testResults.failures.length > 0) {
    // 工程师分析失败原因
    // 可能需要 AI 帮助调试
    const fix = await claudeCode.helpDebug(testResults.failures);
    // 工程师理解后应用
  }

  /**
   * Step 7: 代码审查
   */
  const review = {
    selfReview: engineerReview(implementation),
    aiReview: await claudeCode.review(implementation),
    peerReview: await peerReview(implementation)
  };

  // 工程师：综合所有反馈
  const finalCode = applyReviewFeedback(implementation, review);

  /**
   * Step 8: 提交
   */
  // 工程师：对代码负责，理解每一条
  commit(finalCode, {
    message: engineerWriteCommitMessage(finalCode),
    reviewed: true,
    tested: true,
    understood: true
  });
}
```

### 25.3.2 AI 自动化的问题工作流程

```typescript
/**
 * ❌ 不健康的 AI 自动化工作流
 */

async function aiAutomatedWorkflow(task: string) {
  // 工程师：直接让 AI 做
  user: "帮我完成这个任务"

  // AI：生成所有代码
  ai: [生成大量代码]

  // 工程师：不理解，直接提交
  engineer: [直接提交]

  // 结果：
  // - 可能有 bug
  // - 可能有安全问题
  // - 可能有性能问题
  // - 无人真正理解代码
  // - 无法维护

  // 后果：
  // - 生产环境出问题
  // - 无人能修复
  // - 技术债务累积
  // - 工程师能力退化
}
```

---

## 25.4 保持工程师的核心价值

### 25.4.1 AI 无法替代的技能

```typescript
/**
 * 工程师的不可替代技能
 */

const IRREPLACEABLE_SKILLS = {
  /**
   * 1. 系统思维
   */
  systemsThinking: {
    description: "理解整个系统如何协同工作",
    examples: [
      "架构设计",
      "技术选型",
      "权衡决策",
      "长期规划"
    ],
    whyAIcant: "AI 只能看到局部，无法理解全局"
  },

  /**
   * 2. 问题定义
   */
  problemDefinition: {
    description: "将模糊的需求转化为清晰的技术方案",
    examples: [
      "与产品经理沟通",
      "识别真实需求",
      "定义成功标准",
      "设置边界条件"
    ],
    whyAIcant: "AI 需要明确的输入，无法处理模糊性"
  },

  /**
   * 3. 创造性解决问题
   */
  creativeProblemSolving: {
    description: "在约束条件下找到创新的解决方案",
    examples: [
      "绕过技术限制",
      "优化性能瓶颈",
      "降低成本",
      "提高用户体验"
    ],
    whyAIcant: "AI 依赖训练数据，难以创新"
  },

  /**
   * 4. 责任感
   */
  accountability: {
    description: "对代码质量和系统稳定性负责",
    examples: [
      "代码审查",
      "生产环境监控",
      "事故响应",
      "持续改进"
    ],
    whyAIcant: "AI 无法承担责任"
  },

  /**
   * 5. 沟通协作
   */
  communication: {
    description: "与团队成员和利益相关者有效沟通",
    examples: [
      "技术文档",
      "团队讨论",
      "知识分享",
      "需求澄清"
    ],
    whyAIcant: "AI 无法理解人类情感和复杂关系"
  },

  /**
   * 6. 学习成长
   */
  learning: {
    description: "持续学习新技术和改进技能",
    examples: [
      "学习新框架",
      "研究新技术",
      "参加社区",
      "分享经验"
    ],
    whyAIcant: "AI 无法主动学习和成长"
  }
};
```

### 25.4.2 如何保持竞争力

```typescript
/**
 * 在 AI 时代保持工程师竞争力
 */

/**
 * 策略 1: 深入理解基础
 */
const deepenFoundations = {
  principles: [
    "数据结构与算法",
    "系统设计",
    "网络协议",
    "操作系统",
    "编程语言原理"
  ],

  why: `
    AI 可以帮你写代码，但：
    - 你需要知道什么是好代码
    - 你需要理解性能影响
    - 你需要诊断问题
    - 你需要做出架构决策
  `
};

/**
 * 策略 2: 成为领域专家
 */
const becomeDomainExpert = {
  focus: [
    "选择一个领域深耕",
    "理解业务逻辑",
    "掌握最佳实践",
    "积累经验教训"
  ],

  why: `
    AI 的知识是通用的，但：
    - 深度领域知识需要经验
    - 业务理解需要上下文
    - 最佳实践需要实践
    - 经验无法替代
  `
};

/**
 * 策略 3: 提升软技能
 */
const improveSoftSkills = {
  skills: [
    "沟通能力",
    "团队协作",
    "问题解决",
    "领导力",
    "教学能力"
  ],

  why: `
    AI 越强大，人类技能越重要：
    - 技术决策需要沟通
    - 复杂问题需要协作
    - 团队需要领导者
    - 知识需要传承
  `
};

/**
 * 策略 4: 学习使用 AI
 */
const learnToUseAI = {
  skills: [
    "Prompt Engineering",
    "理解 AI 的能力边界",
    "验证 AI 的输出",
    "将 AI 集成到工作流"
  ],

  why: `
    使用 AI 的工程师会取代不使用的：
    - AI 提高效率
    - AI 减少重复工作
    - AI 让你专注于高价值任务
    - 但你需要知道如何正确使用
  `
};

/**
 * 策略 5: 保持好奇心
 */
const stayCurious = {
  actions: [
    "阅读技术博客",
    "参与开源项目",
    "参加技术会议",
    "尝试新技术"
  ],

  why: `
    AI 训练数据有截止日期：
    - 新技术需要你主动学习
    - 新趋势需要你关注
    - 创新来自于好奇心
    - AI 无法替代探索者
  `
};
```

---

## 25.5 实践建议

### 25.5.1 日常工作清单

```typescript
/**
 * 使用 Claude Code 的日常工作清单
 */

const DAILY_CHECKLIST = {
  /**
   ✅ 必须做
   */
  mustDo: [
    "审查 AI 生成的每一行代码",
    "理解代码的工作原理",
    "编写和运行测试",
    "考虑边界情况",
    "检查安全漏洞",
    "考虑性能影响",
    "对最终结果负责"
  ],

  /**
   ⚠️ 谨慎做
   */
  beCareful: [
    "使用 AI 生成样板代码后仔细审查",
    "让 AI 帮助调试，但要理解根本原因",
    "参考 AI 的建议，但自己做决策",
    "让 AI 生成测试框架，但定义测试场景"
  ],

  /**
   ❌ 不要做
   */
  neverDo: [
    "不理解代码就提交",
    "让 AI 做架构决策",
    "完全信任 AI 的输出",
    "跳过代码审查",
    "忽略边界情况",
    "放弃责任"
  ]
};
```

### 25.5.2 Claude Code 使用建议

```typescript
/**
 * Claude Code 使用最佳实践
 */

const CLAUDE_CODE_BEST_PRACTICES = {
  /**
   * 1. 使用 Plan Mode
   */
  planMode: `
    对于任何非平凡的任务：
    - 按 Shift+Tab 两次激活
    - 让 Claude 先规划
    - 审查规划后再实施

    为什么：
    - 避免 AI 直接生成可能错误的代码
    - 让你参与设计过程
    - 确保方案符合项目需求
  `,

  /**
   * 2. 提供充分上下文
   */
  context: `
    好的 Prompt：
    - 说明项目背景
    - 描述约束条件
    - 提供相关代码
    - 说明期望结果

    坏的 Prompt：
    - "修复这个 bug"（太模糊）
    - "重写这个函数"（没有上下文）
  `,

  /**
   * 3. 渐进式交互
   */
  progressive: `
    而非一次让 AI 做所有事：
    - 步骤 1: 先让 AI 解释代码
    - 步骤 2: 让 AI 建议改进
    - 步骤 3: 让 AI 生成新版本
    - 步骤 4: 审查并调整
  `,

  /**
   * 4. 验证输出
   */
  verify: `
    总是验证 AI 的输出：
    - 代码能运行吗？
    - 符合规范吗？
    - 有安全问题吗？
    - 性能如何？
  `,

  /**
   * 5. 学习模式
   */
  learning: `
    把 AI 当作学习工具：
    - "解释这段代码"
    - "为什么要这样做？"
    - "有什么替代方案？"
    - "这个概念是什么？"
  `
};
```

---

## 25.6 总结：正确的 AI 哲学

### 25.6.1 核心原则

```typescript
/**
 * AI 辅助工程的核心原则
 */

const CORE_PRINCIPLES = {
  /**
   * 原则 1: 人机协作，而非人机替代
   */
  humanAIcollaboration: `
    AI 是工具，不是替代。
    工程师是导演，AI 是助手。
  `,

  /**
   * 原则 2: AI 放大能力，而非外包思考
   */
  amplifyNotOutsource: `
    AI 让你更快、更高效。
    但你仍然需要思考、决策、负责。
  `,

  /**
   * 原则 3: 信任但验证
   */
  trustButVerify: `
    AI 的建议有价值，但必须验证。
    理解 AI 给出的每一个建议。
  `,

  /**
   * 原则 4: 保持核心技能
   */
  maintainCoreSkills: `
    不要让 AI 让你的技能退化。
    继续学习、实践、成长。
  `,

  /**
   * 原则 5: 责任在人
   */
  humanAccountability: `
    无论 AI 生成什么，
    你是工程师，你负责。
  `
};
```

### 25.6.2 最终思考

```typescript
/**
 * 给 Claude Code 用户的最终建议
 */

/**
 * Claude Code 是什么？
 */
const claudeCodeIdentity = {
  is: "一个强大的 AI 辅助工具",
  isNot: "你的替代",

  can: [
    "提高你的效率",
    "减少重复工作",
    "提供知识支持",
    "生成样板代码",
    "帮助调试问题"
  ],

  cannot: [
    "替代你的思考",
    "做架构决策",
    "理解业务上下文",
    "对结果负责",
    "保持技能更新"
  ]
};

/**
 * 成功的 Claude Code 用户
 */
const successfulUser = {
  mindset: `
    - 我用 AI 增强自己
    - 我理解所有 AI 生成的代码
    - 我对最终结果负责
    - 我持续学习新技术
    - 我保持核心技能
  `,

  workflow: `
    - 使用 Plan Mode
    - 提供充分上下文
    - 审查 AI 输出
    - 编写测试
    - 保持好奇心
  `,

  outcome: `
    - 更高的效率
    - 更好的代码质量
    - 更快的成长
    - 更强的竞争力
  `
};

/**
 * 失败的 Claude Code 用户
 */
const unsuccessfulUser = {
  mindset: `
    - AI 替代我工作
    - 我不理解代码也能用
    - AI 比我更懂
    - 我不需要学习
  `,

  workflow: `
    - 让 AI 做所有事
    - 不审查输出
    - 不写测试
    - 不理解代码
  `,

  outcome: `
    - 代码质量下降
    - 技术债务累积
    - 技能退化
    - 被淘汰风险
  `
};

/**
 * 最终建议
 */
const finalAdvice = `
┌──────────────────────────────────────────────────────────┐
│                                                            │
│  Claude Code 是一个强大的工具。                            │
│  正确使用它，它会成为你的超级助手。                        │
│  错误使用它，它会成为你的能力陷阱。                        │
│                                                            │
│  记住：                                                   │
│  ─────────────                                            │
│  AI 辅助工程 = 你 + AI                                    │
│  AI 自动化工程 = AI (你在哪里？)                          │
│                                                            │
│  你是工程师，你是导演，你是负责人。                        │
│  Claude Code 是你的助手，让你的工作更出色。                │
│                                                            │
│  保持好奇，持续学习，善用工具。                            │
│  这样，无论 AI 如何发展，你都不可替代。                    │
│                                                            │
└──────────────────────────────────────────────────────────┘
`;
```

---

## 25.7 练习

### 练习 1：识别工作模式

以下哪些是 AI 辅助工程，哪些是 AI 自动化工程？

A. 工程师设计 API，AI 生成代码，工程师审查后提交
B. 工程师让 AI 实现整个功能，直接提交
C. 工程师让 AI 解释代码，然后自己修复 bug
D. AI 生成测试，工程师补充边界情况

### 练习 2：改进 Prompt

改进以下 Prompt，使其更符合 AI 辅助工程：

```
"帮我实现用户认证功能"
```

### 练习 3：自我评估

评估你自己使用 Claude Code 的方式：
- 你属于 AI 辅助还是 AI 自动化？
- 有哪些地方需要改进？

---

## 25.8 进一步阅读

- [AI-Assisted Engineering: A Guide](https://docs.anthropic.com/claude/docs/ai-assisted-engineering)
- [The Future of Software Engineering](https://blog.pragmaticengineer.com/the-future-of-software-engineering/)
- [Module 7: 专家建议与最佳实践](../module-07-expert-wisdom/) - 下一模块

---

## 视频脚本

### Episode 25: AI 辅助 vs AI 自动化 (16 分钟)

#### [0:00-1:00] 引入
**视觉元素**：
- 标题："AI 辅助工程 vs AI 自动化工程"
- 对比图

**内容**：
> 这是 Module 6 的最后一章，也是最重要的一章。
>
> 我们讨论了 LLM 的工作原理，看了 AI 失败的案例。现在我们要问：**我们应该如何正确地使用 AI？**
>
> 答案是：**AI 辅助工程，而非 AI 自动化工程**。

#### [1:00-4:00] 核心区别
**视觉元素**：
- 两种模式并列对比
- 比例图：工程师 vs AI

**内容**：
> **AI 辅助工程**：
> - 工程师做决策
> - AI 提供建议
> - 工程师审查输出
> - 工程师负责
>
> **AI 自动化工程**：
> - AI 做决策
> - AI 生成代码
> - 工程师不审查
> - 无人负责
>
> [动画：显示比例差异]
>
> AI 辅助：工程师 70% + AI 30%
> AI 自动化：工程师 10% + AI 90%

#### [4:00-8:00] 实际场景对比
**视觉元素**：
- 代码对比
- 流程图

**内容**：
> [演示实现功能的两种方式]
>
> **AI 自动化**：
> - 工程师："帮我实现用户评论功能"
> - AI：生成 500 行代码
> - 工程师：不理解，直接提交
> - 结果：可能有 bug，没人理解
>
> **AI 辅助**：
> - 工程师：设计功能架构
> - AI：根据设计生成代码
> - 工程师：审查、理解、调整
> - 工程师：编写测试
> - 结果：代码质量高，完全理解

#### [8:00-11:00] 健康的人机协作
**视觉元素**：
- AI 的角色列表
- 工程师的不可替代技能

**内容**：
> **AI 的正确角色**：
> - 知识检索器
> - 代码生成器
> - 审查助手
> - 测试助手
>
> **工程师的不可替代技能**：
> - 系统思维
> - 问题定义
> - 创造性解决问题
> - 责任感
> - 沟通协作
> - 学习成长

#### [11:00-14:00] 使用 Claude Code 的最佳实践
**视觉元素**：
- 使用清单
- 示例对比

**内容**：
> **✅ 必须做**：
> - 审查 AI 生成的每一行代码
> - 理解代码的工作原理
> - 编写和运行测试
> - 对最终结果负责
>
> **❌ 不要做**：
> - 不理解代码就提交
> - 让 AI 做架构决策
> - 完全信任 AI 的输出
>
> **最佳实践**：
> 1. 使用 Plan Mode (Shift+Tab)
> 2. 提供充分上下文
> 3. 渐进式交互
> 4. 验证输出
> 5. 保持学习模式

#### [14:00-16:00] 总结与 Module 6 总结
**视觉元素**：
- 核心原则列表
- Module 6 总结

**内容**：
> **核心原则**：
> 1. 人机协作，而非人机替代
> 2. AI 放大能力，而非外包思考
> 3. 信任但验证
> 4. 保持核心技能
> 5. 责任在人
>
> **Module 6 总结**：
> 我们学习了：
> - LLM 的本质（预测下一个 Token）
> - AI 失败的案例（HTTP 连接限制）
> - AI 辅助 vs AI 自动化
>
> **关键要点**：
> Claude Code 是一个强大的工具，但你仍然是工程师，你是导演，你是负责人。
>
> 下一模块，我们将学习专家建议和最佳实践，看看行业领袖如何使用 AI。
