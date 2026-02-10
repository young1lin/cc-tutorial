# Chapter 29: 其他专家经验

## 学习目标

完成本章后，你将能够：

- 了解更多行业专家的 AI 辅助编程经验
- 学习来自不同背景的开发者的最佳实践
- 理解不同视角和方法的共同点
- 综合应用多样化的专家建议
- 建立自己的 AI 辅助开发哲学

## 前置知识

- [Chapter 26: Boris Power 官方建议](chapter-26-boris-power.md)
- [Chapter 27: Addy Osmani 的 2026 工作流](chapter-27-addy-osmani.md)
- [Chapter 28: Andrew Ng 课程精华](chapter-28-andrew-ng.md)

---

## 29.1 专家观点汇总

### 29.1.1 共同主题

```
┌─────────────────────────────────────────────────────────────┐
│                  专家们的共同见解                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  经过与多位专家的对话和研究，我们发现了一些共同主题：   │
│                                                             │
│  ✅ 人在循环中                                               │
│    "AI 是助手，不是替代"                                   │
│    - Boris Power                                           │
│    - Addy Osmani                                           │
│    - Simon Willison                                        │
│                                                             │
│  ✅ 规划优先                                               │
│    "先规划，再编码"                                         │
│    - Boris Power                                           │
│    - Addy Osmani                                           │
│    - Andrew Ng 课程                                        │
│                                                             │
│  ✅ 上下文为王                                             │
│    "提供充分的上下文"                                      │
│    - Boris Power                                           │
│    - Addy Osmani                                           │
│    - Elie Schoppik                                        │
│                                                             │
│  ✅ 测试是安全网                                           │
│    "有良好测试的项目，AI 表现最好"                          │
│    - Addy Osmani                                           │
│    - Simon Willison                                        │
│    - Elie Schoppik                                        │
│                                                             │
│  ✅ 频繁提交                                               │
│    "把提交当作游戏保存点"                                  │
│    - Addy Osmani                                           │
│    - 多位专家                                              │
│                                                             │
│  ✅ 审查一切                                               │
│    "永远不要盲目信任 AI"                                   │
│    - Simon Willison                                        │
│    - Addy Osmani                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 29.2 Simon Willison

### 29.2.1 谁是 Simon Willison

```typescript
/**
 * Simon Willison
 * Django 联合创建者
 * 独立开发者、作家、演讲者
 * AI 工具的早期采用者和重度用户
 */

const simonWillison = {
  background: `
    背景：
    - Django 联合创建者
    - Datasette 创始人
    - 独立软件开发者
    - 技术作家和演讲者

    AI 经验：
    - 从 2023 年开始大量使用 AI 工具
    - 编写了大量关于 AI 编程的文章
    - 在实际项目中深度应用 AI
  `,

  philosophy: `
    核心理念：
    "LLM pair programmer is over-confident and prone to mistakes"

    关键洞察：
    - AI 会自信地生成错误代码
    - 必须审查 AI 的所有输出
    - 测试是验证 AI 工作的关键
  `
};
```

### 29.2.2 Simon 的关键建议

```typescript
/**
 * Simon Willison 的核心建议
 */

const simonKeyAdvice = {
  // 1. AI 是过度自信的初级开发者
  overConfidentJunior: `
    "Think of an LLM pair programmer as
     an over-confident junior developer"

    - 它会自信地写出 bug
    - 它不会告诉你有问题
    - 你必须审查所有内容
  `,

  // 2. 测试是关键
  testingIsKey: `
    那些从 AI 编码代理中获得最多收益的人，
    往往是那些有强大测试实践的人。

    有良好测试套件的项目：
    - AI 可以快速"飞过"项目
    - 测试套件是安全网

    没有测试的项目：
    - AI 可能盲目假设一切正常
    - 错误可能很晚才发现
  `,

  // 3. AI 放大现有技能
  amplifiesSkills: `
    LLMs "奖励现有最佳实践"：
    - 编写清晰的规格
    - 有良好的测试
    - 进行代码审查

    当涉及 AI 时，这些变得更加重要。
  `,

  // 4. 保持原始技能
  keepRawSkills: `
    有意地定期在没有 AI 的情况下编码，
    以保持原始技能敏锐。

    不要让 AI 成为你技能的拐杖。
  `
};
```

---

## 29.3 其他行业专家

### 29.3.1 Jesse Vincent

```typescript
/**
 * Jesse Vincent
 * 经验丰富的软件工程师和技术领导者
 */

const jesseVincent = {
  contributions: `
    贡献：
    - 推广 CLAUDE.md 的使用
    - Git workflows 和并行工作流的早期采用者
    - 大量使用 AI 工具的实际经验
  `,

  claudeMdInsight: `
    关于 CLAUDE.md 的洞察：

    "CLAUDE.md 文件非常有效，
     它可以让模型'保持在轨道上'，
     减少 AI 偏离脚本或引入不想要的模式的倾向。"
  `,

  worktreeInsight: `
    关于 Git Worktrees：

    "使用 git worktrees 是一个高级工作流，
     让我可以在同一个仓库上并行运行多个 AI 编码会话
     而不会互相干扰。"

    这就像让每个 AI 任务在自己的沙盒分支中。
  `
};
```

### 29.3.2 Ben Congdon

```typescript
/**
 * Ben Congdon
 * 软件工程师，AI 工具深度用户
 */

const benCongdon = {
  observation: `
    观察：
    "我很震惊很少有人使用 Copilot 的自定义指令，
     考虑到它们多么有效。"

    他可以通过提供一些示例和偏好
    来引导 AI 输出符合团队习语的代码。
  `,

  customInstructions: `
    自定义指令的价值：

    - 提供代码风格示例
    - 指定命名约定
    - 定义架构偏好
    - 说明要避免的模式

    投资回报率巨大：
    输出需要较少的调整
    更顺畅地与代码库集成
  `;
};
```

### 29.3.3 Les Orchard

```typescript
/**
 * Les Orchard
 * 软件工程师，技术作家
 */

const lesOrchard = {
  metaphor: `
    比喻：
    "这就像'15 分钟的瀑布模型'"

    解释：
    传统瀑布模型的问题：
    - 规格阶段：几个月
    - 设计阶段：几个月
    - 实现阶段：几个月

    AI 辅助的"快速瀑布"：
    - 规格阶段：15 分钟
    - 设计阶段：5 分钟
    - 实现阶段：AI 加速完成

    关键：
    前期的结构化规划让后续编码更顺畅。
  `;
};
```

### 29.3.4 社区集体智慧

```typescript
/**
 * 来自 Claude Code 用户社区的集体学习
 */

const communityWisdom = {
  // 来自社区的提示
  tips: [
    {
      author: "多位用户",
      tip: "使用子代理验证细节或调查问题",
      context: "尤其在对话或任务早期"
    },

    {
      author: "多位用户",
      tip: "并行运行多个 AI 会话",
      context: "用于不同的独立任务"
    },

    {
      author: "多位用户",
      tip: "将提交视为游戏保存点",
      context: "如果 LLM 会话出错，可以回滚"
    },

    {
      author: "多位用户",
      tip: "使用 git bisect 查找 bug",
      context: "LLM 非常擅长遍历提交历史"
    }
  ],

  // 模式识别
  patterns: `
    社区中出现的模式：

    1. 探索 → 计划 → 编码 → 提交
       最常见的成功模式

    2. TDD + AI
       先写测试，AI 实现代码

    3. 多 Claude 审查
       一个编写，另一个审查

    4. Git Worktrees
       并行开发独立功能

    5. CLAUDE.md 优先
       在一切之前设置项目记忆
  `
};
```

---

## 29.4 不同视角的比较

### 29.4.1 工程师 vs 产品经理视角

```typescript
/**
 * 不同角色的视角
 */

const perspectiveComparison = {
  // 工程师视角
  engineer: `
    关注点：
    - 代码质量
    - 架构设计
    - 技术实现
    - 测试覆盖

    AI 使用：
    - 生成样板代码
    - 调试问题
    - 重构代码
    - 编写测试

    担心：
    - 技能退化
    - 代码质量下降
    - 过度依赖
  `,

  // 产品经理视角
  productManager: `
    关注点：
    - 功能交付速度
    - 用户需求满足
    - 产品迭代

    AI 使用：
    - 快速原型
    - 需求分析
    - 用户故事生成
    - 文档编写

    担心：
    - 功能完整性
    - 用户体验
    - 时间表
  `,

  // CTO / 技术负责人视角
  cto: `
    关注点：
    - 团队效率
    - 架构一致性
    - 技术债务
    - 团队成长

    AI 使用：
    - 代码审查
    - 架构决策
    - 知识分享
    - 制定标准

    担心：
    - 团队能力
    - 代码一致性
    - 长期可维护性
  `
};
```

### 29.4.2 不同公司规模的实践

```typescript
/**
 * 不同规模公司的 AI 采用策略
 */

const companySizeComparison = {
  // 初创公司
  startup: `
    特点：
    - 有限资源
    - 需要快速迭代
    - 小型团队

    AI 策略：
    - 高度采用 AI
    - AI 作为"力量倍增器"
    - 快速原型开发
    - AI 补偿人力不足

    挑战：
    - 代码质量把控
    - 长期维护性
    - 知识积累
  `,

  // 中型公司
  midSize: `
    特点：
    - 一定规模
    - 有一定流程
    - 混合经验水平

    AI 策略：
    - 渐进采用
    - 建立最佳实践
    - 团队培训
    - AI 辅助而非替代

    挑战：
    - 标准化
    - 团队一致性
    - 文化适应
  `,

  // 大型企业
  enterprise: `
    特点：
    - 大型代码库
    - 严格流程
    - 合规要求

    AI 策略：
    - 审慎采用
    - 安全优先
    - 严格的审查流程
    - AI 辅助特定任务

    挑战：
    - 安全和合规
    - 文化变革
    - 集成复杂性
  `
};
```

---

## 29.5 综合最佳实践

### 29.5.1 所有专家的共识

```typescript
/**
 * 专家们的核心共识
 */

const expertConsensus = {
  // 1. 人在循环
  humanInLoop: `
    共识：AI 是辅助，不是替代

    所有人都同意：
    - 工程师必须审查 AI 输出
    - 工程师对代码负责
    - 工程师做最终决策
    - AI 加速，但不替代思考
  `,

  // 2. 测试至关重要
  testingCritical: `
    共识：测试是 AI 辅助开发的基础

    所有人都同意：
    - 有测试的项目，AI 表现最好
    - TDD + AI 是强大组合
    - 测试是安全网
    - 测试提供快速反馈
  `,

  // 3. 上下文管理
  contextManagement: `
    共识：提供充分的上下文

    所有人都同意：
    - CLAUDE.md 是必须的
    - 提及相关文件很重要
    - 图像和截图有帮助
    - 上下文质量决定输出质量
  `,

  // 4. 版本控制是安全网
  versionControlSafety: `
    共识：频繁提交是最佳实践

    所有人都同意：
    - 把提交当作保存点
    - 小提交比大提交好
    - git worktrees 很有用
    - 可撤销的实验很重要
  `,

  // 5. 持续学习
  continuousLearning: `
    共识：保持学习和成长

    所有人都同意：
    - 不要依赖 AI 而退化
    - 定期手工编码保持技能
    - 理解 AI 生成的代码
    - 从 AI 的错误中学习
  `
};
```

### 29.5.2 构建自己的哲学

```typescript
/**
 * 基于专家建议构建自己的 AI 辅助开发哲学
 */

/**
 * Step 1: 核心信念
 */
const coreBeliefs = `
我的核心信念：

1. AI 是强大的助手，不是替代
   - AI 放大我的能力
   - 我仍然是工程师和决策者
   - 我对最终结果负责

2. 规划优先于编码
   - 先理解问题
   - 制定清晰的规格
   - 分解为小任务
   - 然后才开始编码

3. 测试是非 negotiable
   - 有测试才使用 AI
   - AI 编写测试也要审查
   - 测试覆盖不能牺牲

4. 上下文决定质量
   - CLAUDE.md 是基础
   - 提供充分的背景
   - 使用图像和示例
   - 明确需求和约束
`;

/**
 * Step 2: 实践规则
 */
const practicalRules = `
我的实践规则：

编码前：
- [ ] 问题理解了吗？
- [ ] 规格写了吗？
- [ ] 计划制定了吗？
- [ ] 测试策略有了吗？

编码中：
- [ ] 小步迭代
- [ ] 每步都测试
- [ ] 频繁提交
- [ ] 审查 AI 输出

编码后：
- [ ] 所有测试通过？
- [ ] 代码审查了吗？
- [ ] 理解所有更改吗？
- [ ] 文档更新了吗？
`;

/**
 * Step 3: 工具配置
 */
const toolConfiguration = `
我的工具配置：

CLAUDE.md:
- 项目概述
- 架构说明
- 编码规范
- 常用命令
- 重要提醒

权限:
- Edit: 总是允许
- Bash(git): 总是允许
- Bash(npm): 总是允许
- 其他: 根据需要

Hooks:
- beforeEdit: 运行 lint
- afterEdit: 格式化
- beforeCommit: 运行测试
`;
```

---

## 29.6 行业趋势

### 29.6.1 2025-2026 年趋势

```typescript
/**
 * AI 辅助开发的演进趋势
 */

const trends2025to2026 = {
  // 趋势 1: 从实验到标准
  fromExperimentToStandard: `
    2024:
    - 少数先锋者实验
    - 许多怀疑者
    - 没有最佳实践

    2025:
    - 广泛采用
    - 最佳实践涌现
    - 官方课程发布

    2026:
    - 行业标准
    - 教育体系整合
    - 成熟的工作流
  `,

  // 趋势 2: 从个人到团队
  fromIndividualToTeam: `
    演进：
    个人工具 → 团队工具 → 企业工具

    关键：
    - 共享 CLAUDE.md
    - 统一工作流
    - 团队培训
    - 代码审查标准
  `,

  // 趋势 3: 从编码到全生命周期
  fromCodingToFullLifecycle: `
    覆盖范围：
    - 需求分析
    - 架构设计
    - 编码实现
    - 测试验证
    - 部署运维
    - 文档编写
    - 代码审查
  `,

  // 趋势 4: 从单一模型到多模型
  fromSingleToMultiple: `
    使用策略：
    - 不同任务用不同模型
    - 并行尝试多个模型
    - 比较和选择最佳输出
    - A/B 测试模型效果
  `
};
```

---

## 29.7 练习

### 练习 1：综合专家建议

基于所有专家的建议，创建你个人的 AI 辅助开发宣言。

### 练习 2：评估你的当前实践

评估你自己使用 Claude Code 的方式：
- 你遵循哪些专家建议？
- 你可以改进什么？
- 你想采用哪些新实践？

### 练习 3：与团队分享

准备一个简短的演示，与你的团队分享：
- Claude Code 的最佳实践
- 如何设置团队标准
- 如何避免常见陷阱

---

## 29.8 进一步阅读

- [Chapter 26: Boris Power 官方建议](chapter-26-boris-power.md)
- [Chapter 27: Addy Osmani 的 2026 工作流](chapter-27-addy-osmani.md)
- [Chapter 28: Andrew Ng 课程精华](chapter-28-andrew-ng.md)
- [Module 8: 构建自己的工作流](../module-08-building-workflows/) - 下一模块

---

## 视频脚本

### Episode 29: 其他专家经验 (14 分钟)

#### [0:00-1:00] 引入
**视觉元素**：
- 标题："集体智慧：来自多位专家的见解"
- 专家头像画廊

**内容**：
> 我们已经学习了 Boris Power、Addy Osmani 和 Andrew Ng 课程的官方建议。今天我们看看其他行业专家的经验和智慧。
>
> 虽然背景不同，但他们的核心见解惊人地一致。

#### [1:00-4:00] 共同主题
**视觉元素**：
- 共同主题列表（逐个出现）
- 专家引言叠加

**内容**：
> 在与多位专家对话后，我们发现了一些核心共同主题：
>
> **1. 人在循环** - Boris、Addy、Simon 都强调
> **2. 规划优先** - 所有专家一致同意
> **3. 上下文为王** - 普遍认可
> **4. 测试是安全网** - 反复强调
> **5. 频繁提交** - 最佳实践
> **6. 审查一切** - 永远不要盲目信任
>
> [展示专家原话]

#### [4:00-8:00] Simon Willison
**视觉元素**：
- Simon Willison 照片
- 他的核心观点

**内容**：
> Simon Willison，Django 联合创建者，提供了一个关键比喻：
>
> "Think of an LLM pair programmer as an over-confident junior developer"
>
> [解释含义]
>
> Simon 的洞察：那些从 AI 编码代理中获得最多收益的人，往往是那些有强大测试实践的人。

#### [8:00-11:00] 其他专家亮点
**视觉元素**：
- Jesse Vincent、Ben Congdon、Les Orchard 等专家
- 每人的关键贡献

**内容**：
> [快速展示其他专家的见解]
>
> Jesse Vincent: CLAUDE.md 让模型"保持在轨道上"
>
> Ben Congdon: 自定义指令的投资回报率巨大
>
> Les Orchard: "15 分钟的瀑布模型"比喻
>
> 社区集体智慧：子代理、Git Worktrees、提交作为保存点

#### [11:00-14:00] 总结与 Module 7 总结
**视觉元素**：
- 综合最佳实践
- Module 7 总结
- Module 8 预告

**内容**：
> **综合最佳实践**：
> - 人是导演，AI 是助手
> - 规划优先于编码
> - 上下文决定质量
> - 测试是安全网
> - 版本控制是安全网
> - 持续学习成长
>
> **Module 7 总结**：
> 我们学习了四位重要专家的建议：
> - Boris Power：官方最佳实践
> - Addy Osmani：2026 AI 工作流
> - Andrew Ng 课程：权威教程
> - 其他专家：集体智慧
>
> 下一模块，我们将学习如何构建你自己的工作流。
