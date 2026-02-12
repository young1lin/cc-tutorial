---
title: Claude Code 最佳实践研究总结
url: N/A (Research Summary)
author: Research Compilation
date: 2026-01-10
tier: T4
why_important: |
  这是对 Claude Code 最佳实践、教程和专家建议的全面研究总结。
  汇集了官方文档、知名专家（Boris Cherny、Andrew Ng、Addy Osmani、Ethan Mollick、Zvi Mowshowitz）的建议，
  以及关于架构模式（DDD、六边形架构、洋葱架构）的实践指南。
topics: [summary, research, best-practices, claude-code, compilation]
---

# Claude Code 最佳实践研究总结

## 研究概述

本研究收集了关于 Claude Code 的最佳实践、官方教程和专家建议，重点关注以下方面：

1. **Claude Code 之父/创造者的官方建议**
2. **知名博主的教程（Andrew Ng、Ethan Mollick、Zvi Mowshowitz、Addy Osmani）**
3. **最佳实践主题**（代码分层、依赖注入、AAA 单元测试模式等）

所有重要文档已保存至：`C:\PythonProject\cc-tutorial\docs\research\`

---

## 一、Claude Code 之父 Boris Power 的官方建议

### 1.1 关于 Plan Mode 的完整建议

**来源：** 官方最佳实践文档 + Reddit 分享

**核心建议：**

1. **始终以 Plan Mode 开始**
   - 使用 `Shift+Tab` 两次激活 Plan Mode
   - 让 Claude 先规划，不要立即编写代码
   - 一旦计划确定且可靠，切换到自动接受编辑模式

2. **Plan Mode 的适用场景：**
   - ✅ 多文件或多步骤实现
   - ✅ 理解大型代码库
   - ✅ 端到端重构规划
   - ✅ 测试生成和 QA 规划
   - ✅ 依赖和影响分析
   - ✅ 复杂任务分解

3. **不使用 Plan Mode 的场景：**
   - ❌ 需要低延迟的快速修复
   - ❌ 简单单文件编辑
   - ❌ 快速转换或样板代码
   - ❌ 短反馈循环的实验

### 1.2 验证机制是最高 ROI 投资

**Boris 的首要建议：**
> "投入精力把验证机制做扎实。这是回报率最高的投资"

**实践方法：**
- 设置自动验证机制，让 Claude 能够自我验证工作
- 集成各种工具（如 MCP - Model Context Protocol）增强功能
- 建立 CI/CD 管道，让测试自动运行
- 使用代码审查机器人（AI 或其他）

### 1.3 团队实践

**Boris 团队的做法：**
- 使用一个共享的 `CLAUDE.md` 文件
- 将文件提交到 Git，团队共享
- 定期调优 `CLAUDE.md` 内容
- 使用 prompt improver 优化指令

**CLAUDE.md 应包含：**
- 常用的 bash 命令
- 核心文件和实用函数
- 代码风格指南
- 测试说明
- 仓库礼仪（分支命名、合并 vs rebase）
- 开发环境设置
- 项目特有的意外行为或警告

### 1.4 关于多个 Opus 窗口的澄清

**重要发现：可以同时运行多个 Opus 窗口！**

**误解：** 很多用户认为不能同时开多个 Opus 窗口
**真相：** 技术上完全可行，限制主要是配额和定价

**专家实践：**
- **Zvi Mowshowitz：** 使用 5-10 个并行 Claude Code 窗口
- **Boris 团队：** 使用 git worktrees 实现多会话并行工作

**使用 git worktrees 的最佳实践：**
```bash
# 创建 worktree
git worktree add ../project-feature-a feature-a

# 在每个 worktree 中启动 Claude
cd ../project-feature-a && claude

# 清理
git worktree remove ../project-feature-a
```

**优势：**
- 每个 Claude 实例专注于独立任务
- 避免等待和合并冲突
- 可以同时处理不相关的功能

---

## 二、官方 Anthropic 最佳实践（Boris Cherny 执笔）

### 2.1 核心工作流程

#### 工作流 1：探索 → 计划 → 编码 → 提交

1. **要求 Claude 读取相关文件、图片或 URL**
   - 提供通用指针或具体文件名
   - 明确告诉它暂不编写代码
   - **使用子代理验证细节**（对复杂问题很重要）

2. **要求 Claude 制定计划**
   - 使用 "think" 触发扩展思考模式
   - 思考等级：think < think hard < think harder < ultrathink
   - 如果结果合理，让 Claude 创建文档或 GitHub issue

3. **要求 Claude 实现解决方案**
   - 在实现时明确验证解决方案的合理性

4. **要求 Claude 提交结果并创建 PR**

**关键：** 步骤 1-2 至关重要——没有它们，Claude 倾向于直接编码。

#### 工作流 2：TDD（测试驱动开发）

Anthropic 团队最喜欢的用于可验证更改的工作流：

1. **要求 Claude 编写测试**（基于预期的输入/输出对）
   - 明确说明正在进行 TDD
   - 避免创建模拟实现

2. **告诉 Claude 运行测试并确认失败**
   - 明确告诉它此时不要编写实现代码

3. **要求 Claude 提交测试**

4. **要求 Claude 编写通过测试的代码**
   - 指示它不要修改测试
   - 让 Claude 持续迭代直到所有测试通过

5. **要求 Claude 提交代码**

**关键：** Claude 在有明确目标（测试用例）时表现最佳。

### 2.2 多 Claude 实例工作流

#### 模式 1：一个 Claude 编写，另一个验证

1. 使用 Claude 编写代码
2. 运行 `/clear` 或启动第二个 Claude
3. 让第二个 Claude 审查第一个的工作
4. 启动第三个 Claude（或再次 `/clear`）读取代码和审查反馈
5. 让这个 Claude 根据反馈编辑代码

**优势：** 分离上下文通常产生更好的结果。

#### 模式 2：使用 Git Worktrees

适用于多个独立任务：

1. 创建 3-4 个 git checkout（或 worktrees）
2. 在单独的终端标签页中打开每个文件夹
3. 在每个文件夹中启动 Claude 处理不同任务
4. 循环检查进度并批准/拒绝权限请求

### 2.3 优化工作流的建议

1. **具体化指令**
   - 给出清晰的方向可以减少后续纠正的需要
   - 示例对比：
     - ❌ 差："add tests for foo.py"
     - ✅ 好："write a new test case for foo.py, covering the edge case where the user is logged out. avoid mocks"

2. **给 Claude 提供图片**
   - 粘贴截图（macOS: cmd+ctrl+shift+4）
   - 拖放图片
   - 提供图片文件路径

3. **提及你想要 Claude 查看或处理的文件**
   - 使用 tab 补全快速引用文件或文件夹

4. **给 Claude 提供 URL**
   - 粘贴特定 URL 供 Claude 获取和读取
   - 使用 `/permissions` 将域名添加到允许列表

5. **早期且经常纠偏**
   - 要求 Claude 在编码前制定计划
   - 按 Escape 中断 Claude
   - 双击 Escape 跳回历史记录
   - 要求 Claude 撤销更改

6. **使用 `/clear` 保持上下文聚焦**
   - 在任务之间频繁使用

7. **为复杂工作流使用清单和草稿本**
   - 让 Claude 使用 Markdown 文件作为清单和工作草稿本
   - 示例：修复大量 lint 错误时，先生成清单然后逐个处理

### 2.4 使用 Headless 模式自动化基础设施

**用途：**
- CI、pre-commit hooks、构建脚本、自动化

**使用方法：**
```bash
claude -p "prompt" --output-format stream-json
```

**应用场景：**
1. **问题分类：** 触发 GitHub 事件时自动检查新问题
2. **作为 linter：** 提供超出传统 lint 工具的主观代码审查

---

## 三、Andrew Ng 的 Claude Code 权威课程

### 3.1 课程信息

- **标题：** Claude Code: A Highly Agentic Coding Assistant
- **平台：** DeepLearning.AI 与 Anthropic 合作
- **讲师：** Elie Schoppik（Anthropic 技术教育主管）
- **时长：** 1 小时 50 分钟，10 节视频课
- **状态：** Beta 期间免费

### 3.2 课程内容

**你将学到：**
1. 理解 Claude Code 的底层架构
2. 探索和理解 RAG 聊天机器人代码库
3. 创建 CLAUDE.md 文件
4. 通过提及相关文件和提供截图来获取上下文
5. 为 RAG 聊天机器人的前端和后端添加功能
6. 编写测试、重构代码
7. 使用 git worktrees 同时运行多个 Claude 会话
8. 修复 GitHub issues、创建和合并 PR
9. 重构 Jupyter notebook 并创建仪表板
10. 连接 Figma MCP 服务器从设计创建 Web 应用
11. 使用 Playwright MCP 服务器进行浏览器截图

**三个实战项目：**
1. **RAG 聊天机器人：** 探索代码库、添加功能
2. **电商仪表板：** 重构 Jupyter notebook
3. **Figma 到 Web 应用：** 设计到代码工作流

### 3.3 关键要点

- **规划优先：** 在编码前让 Claude Code 制定计划
- **使用思考模式：** 对困难任务使用 "thinking mode"
- **子代理：** 使用 Claude Code 的子代理进行头脑风暴
- **CLAUDE.md：** 在项目目录中创建以存储跨会话信息
- **上下文控制：** 使用 escape、clear 和 compact 命令
- **并行工作：** 使用 git worktrees 同时添加多个独立功能
- **GitHub 集成：** 使用 Claude Code 的 GitHub 集成修复问题、创建 PR
- **MCP 服务器：** 连接到 Figma 和 Playwright 等 MCP 服务器

---

## 四、Addy Osmani 的 2026 AI 编码工作流

### 4.1 核心理念

**"AI 辅助工程"而非"AI 自动化工程"**

- 将 LLM 视为强大的结对程序员
- 需要清晰的指导、上下文和监督
- 开发人员保持对软件产出的责任

### 4.2 十大最佳实践

#### 1. 从清晰计划开始（规格说明先于代码）

**不要只是向 LLM 投掷愿望——首先要定义问题并规划解决方案。**

- 与 AI 头脑风暴详细的规格说明
- 迭代地让 AI 提出问题直到明确需求和边缘情况
- 编制综合的 `spec.md`（需求、架构决策、数据模型、测试策略）
- 让 AI 生成项目计划：分解为逻辑的、可管理的任务
- **"15 分钟内的瀑布"**：快速结构化规划阶段使后续编码更顺畅

#### 2. 将工作分解为小的迭代块

**范围管理是一切——给 LLM 可管理的任务，而不是整个代码库。**

- 避免要求大型、单一的输出
- 分解为迭代步骤或 ticket
- LLM 在给予集中提示时表现最佳：实现一个函数、修复一个错误、添加一个功能
- 生成结构化的"提示计划"文件
- **通过小迭代避免灾难性错误**

#### 3. 提供广泛的上下文和指导

**LLM 只与你提供的上下文一样好——向它们展示相关代码、文档和约束。**

- 提供所有必要信息：代码、技术约束、已知陷阱、首选方法
- 使用"大脑倾倒"：高层目标、不变量、好解决方案的示例、避免的方法
- 粘贴相关代码库部分或 API 文档
- 使用工具如 `gitingest` 或 `repo2txt` 自动化上下文打包
- **不要让 AI 在部分信息上操作**
- 使用注释和规则在提示中指导 AI

#### 4. 选择正确的模型（并在需要时使用多个）

**并非所有编码 LLM 都平等——有意图地选择你的工具，不要害怕在流中切换模型。**

- 为每个任务选择最适合的模型或服务
- 尝试两个或更多 LLM 并行以交叉检查
- **如果一个模型卡住或给出平庸输出，尝试另一个**
- 使用最新的 "pro" 层模型
- 选择"氛围"与你契合的 AI 结对程序员

#### 5. 在整个 SDLC 中利用 AI 编码

**使用编码特定的 AI 帮助来增强你的工作流。**

**命令行工具：**
- Claude Code、OpenAI Codex CLI、Google Gemini CLI

**异步编码代理：**
- Google Jules、GitHub Copilot Agent
- 克隆仓库到云 VM，在后台工作，打开 PR

**关键：** 这些工具不是万无一失的，必须理解其限制
- 提供计划或待办事项列表
- 加载 spec.md 或 plan.md
- **我们不处于让 AI 代理无人值守地编码整个功能的阶段**
- 以监督方式使用这些工具

#### 6. 保持人在循环中——验证、测试和审查所有内容

**AI 会愉快地生成看起来合理的代码，但你要对质量负责——始终审查和测试。**

**基本规则：** 永远不要盲目信任 LLM 的输出
- 将每个 AI 生成的片段视为来自初级开发者的代码
- 阅读代码、运行代码、测试代码
- **你必须测试它编写的内容**

**将测试编织到工作流中：**
- 规划阶段包括生成测试列表
- 指示 Claude Code 在实现任务后运行测试套件
- **投资测试**：它放大 AI 的有用性

**进行代码审查（手动和 AI 辅助）：**
- 定期暂停并审查生成的代码
- 启动第二个 AI 会话（或不同模型）批评或审查第一个的代码
- **AI 编写的代码需要额外审查**

**Chrome DevTools MCP：**
- 消除手动上下文切换的摩擦
- 允许基于实际运行时数据高精度地诊断和修复错误

**责任：**
- **无论使用多少 AI，我仍然是负责任的工程师**
- 只在理解代码后合并或发布代码
- AI 是助手，不是自主可靠的编码者

#### 7. 经常提交并使用版本控制作为安全网

**频繁的提交是你的存档点——它们让你能够撤销 AI 的误操作并理解更改。**

**实践：**
- 采用超细粒度的版本控制习惯
- 在每个小任务或每次成功的自动编辑后提交
- 将提交视为**游戏中的存档点**
- 如果 LLM 会话出错，可以回滚到最后一个稳定提交

**版本控制还有助于：**
- 扫描最近的提交以向 AI 简要介绍更改
- 将 git diff 或提交日志粘贴到提示中
- LLM 非常擅长解析 diff 和使用 git bisect

**使用分支或 worktrees 隔离 AI 实验：**
- 为新功能或子项目启动新的 git worktree
- 让多个 AI 编码会话在同一仓库上并行运行
- 在同一存储库上让 AI 实现功能 A，同时实现功能 B
- **经常提交、使用分支组织工作、拥抱 git**

#### 8. 使用规则和示例自定义 AI 的行为

**通过提供风格指南、示例，甚至"规则文件"来引导你的 AI 助手——一点前期调整会产生更好的输出。**

**CLAUDE.md 文件：**
- 包含过程规则和偏好
- "以我们项目的风格编写代码，遵循我们的 lint 规则，不使用某些函数，首选函数式风格而非 OOP"
- 在会话开始时将此文件提供给 Claude

**自定义指令或系统提示：**
- 配置 AI 的全局行为
- 编写关于编码风格的短段落
- "使用 4 空格缩进，在 React 中避免箭头函数，首选描述性变量名"

**提供内联示例：**
- 展示类似的函数："这是我们实现 X 的方式，对 Y 使用类似的方法"
- 编写注释并要求 AI 继续该风格
- **用要遵循的模式引导模型**

**创造性规则集：**
- "Big Daddy" 规则
- 添加"no hallucination/no deception"条款
- "如果你不确定某事或缺少代码库上下文，请要求澄清而不是编造答案"
- "修复错误时总是在注释中简要解释你的推理"

**总结：** 不要将 AI 视为黑盒——调整它
- 配置系统指令
- 共享项目文档
- 编写明确的规则
- **投资回报率巨大**

#### 9. 拥抱测试和自动化作为倍增器

**使用你的 CI/CD、linters 和代码审查机器人——AI 在自动捕获错误的环境中效果最好。**

**强大的持续集成设置：**
- 每次提交或 PR 运行自动测试
- 执行代码风格检查（ESLint、Prettier 等）
- 理想情况下为任何新分支提供暂存部署

**工作流：**
- AI 打开 PR，CI 运行测试并报告失败
- 将失败日志反馈给 AI："集成测试失败，让我们调试"
- 将错误修复变成具有快速反馈的协作循环

**自动代码质量检查：**
- 在提示中包含 linter 输出
- 如果 AI 写的代码不通过 linter，复制错误到聊天中
- **就像有一个严格的老师监督 AI**

**AI 编码代理：**
- 一些代理会拒绝说代码任务"完成"，直到所有测试通过
- 代码审查机器人（AI 或其他）作为额外的过滤器

**良性循环：**
- AI 编写代码
- 自动工具捕获问题
- AI 修复问题
- 你监督高层方向

**目标：** AI 友好的工作流是有强大自动化的工作流

#### 10. 持续学习和适应（AI 放大你的技能）

**将每个 AI 编码会话视为学习机会——你知道的越多，AI 能帮助你的就越多，创造良性循环。**

**关键洞察：**
- 如果你有扎实的软件工程基础，AI 会**放大**你的生产力
- 如果你缺乏基础，AI 可能只是放大混乱
- LLM "奖励现有的最佳实践"

**AI 对资深工程师的影响：**
- 在更高的抽象级别操作（设计、接口、架构）
- AI 处理样板代码
- 但你需要先拥有那些高层技能

**对技能退化的担忧：**
- 如果做得对，情况恰恰相反
- 通过审查 AI 代码，接触到了新的习语和解决方案
- 通过调试 AI 错误，加深了对语言和问题领域的理解
- 要求 AI 解释其代码或修复背后的基本原理

**AI 作为研究助手：**
- 枚举选项
- 比较权衡
- **就像有一个百科全书式的导师随时待命**

**结论：**
- AI 工具放大你的专业知识
- 不害怕它们"夺走我的工作"
- 兴奋它们将我从苦差事中解放出来
- 有意地定期在没有 AI 的情况下编码，保持原始技能敏锐

### 4.3 总结

**"AI 放大软件工程"而非"AI 自动化软件工程"**

**最佳结果来自于将经典软件工程纪律应用于 AI 协作：**
- 编码前设计
- 编写测试
- 使用版本控制
- 维护标准

**底线：** AI 编码助手是令人难以置信的倍增器，但人类工程师仍然是节目的导演。

---

## 五、其他知名专家的建议

### 5.1 Ethan Mollick（Wharton 教授，One Useful Thing）

**关键观点：**
- Claude Code 是新一代自主编码工具的一部分
- 通过自我纠正和压缩自主完成长任务
- 需要命令行舒适度和 Node.js 等工具的熟悉度
- Opus 4.5 集成增强了能力

### 5.2 Zvi Mowshowitz（知名分析师，Don't Worry About the Vase）

**实践：**
- 使用 5-10 个并行 Claude Code 窗口
- 5-10 个在 claude.ai/code 上
- 所有并行，始终使用 Opus 4.5 与 Thinking
- 评论："现在我们有了 Claude Code 和 Opus 4.5。我不写代码。然而现在每当网站上的某些东西让我烦恼时，我就会导致代码存在。"

**相关文章：**
- "AI #150: While Claude Codes"（1 天前）
- "2025 Year in Review"（1 周前）
- "Claude Opus 4.5 Is The Best Model Available"

---

## 六、架构最佳实践

### 6.1 依赖注入和依赖倒置

**相关资源：**
- [Claude Code Toolkit - Code Architect](https://github.com/redpop/claude-code-toolkit/blob/main/docs/agents/architecture/code-architect.md)
  - 提及**依赖倒置**、**关注点分离**和**可测试性改进**
  - 提供清洁架构转换计划和层分离

**原则：**
- 依赖应该指向内部，而不是外部
- 高层模块不应该依赖低层模块
- 抽象不应该依赖细节

### 6.2 清洁架构/洋葱架构/六边形架构

**找到的资源：**

1. **Using Claude Code for Clean Architecture** (Peter Bouda)
   - Claude Code 尊重架构模式并遵循既定约定
   - 产生干净的、可测试的代码
   - 减少上下文切换

2. **Backend Coding Rules for AI Coding Agents: DDD and Hexagonal Architecture**
   - AI 编码代理的综合规则
   - 涵盖领域驱动设计（DDD）和六边形架构原则

3. **通用架构资源：**
   - [A Detailed Guide to Hexagonal Architecture with Examples](https://devcookies.medium.com/a-detailed-guide-to-hexagonal-architecture-with-examples-042523acb1db)
   - [DDD and Hexagonal Architecture Guide](https://vaadin.com/blog/ddd-part-3-domain-driven-design-and-the-hexagonal-architecture)
   - [Explicit Architecture - DDD, Hexagonal, Onion, Clean, CQRS](https://herbertograca.com/2017/11/16/explicit-architecture-01-ddd-hexagonal-onion-clean-cqrs-how-i-put-it-all-together/)

**核心概念：**
- **由内而外的分层原则：** 从领域核心开始，向外添加适配器
- **关注点分离：** 业务逻辑与基础设施关注点分离
- **依赖方向：** 依赖指向内部（领域核心）
- **可测试性：** 架构使代码更容易测试

### 6.3 AAA 单元测试模式

**相关资源：**
- [Testing Patterns and Utilities - Claude Code Showcase](https://github.com/ChrisWiles/claude-code-showcase/blob/main/.claude/skills/testing-patterns/SKILL.md)
  - 专门的 Claude Code 技能，包括 AAA 模式使用
  - 涵盖单元测试、测试工厂、TDD red-green-refactor 循环

- [Python Testing Patterns Guide | Claude Code Skill](https://mcpmarket.com/tools/skills/python-testing-patterns-1767566172392)
  - 使用 Claude Code 实现 AAA 模式
  - 涵盖 pytest、fixtures、mocking、async 测试、健壮的 TDD

**AAA 模式：**
1. **Arrange（准备）：** 设置测试环境
2. **Act（执行）：** 执行要测试的代码
3. **Assert（断言）：** 验证预期结果

**示例：**
```python
def test_user_login():
    # Arrange - 准备测试数据和环境
    user = User(username="test", password="password123")
    db.add(user)
    db.commit()

    # Act - 执行要测试的操作
    result = authenticate("test", "password123")

    # Assert - 验证结果
    assert result.is_authenticated == True
    assert result.user_id == user.id
```

---

## 七、已保存的文档清单

所有文档已保存至：`C:\PythonProject\cc-tutorial\docs\research\`

### 高优先级文档（已保存）

1. ✅ **01-claude-code-best-practices-anthropic-official.md**
   - Anthropic 官方最佳实践
   - 作者：Boris Cherny & Anthropic Team
   - 最全面的 Claude Code 使用指南

2. ✅ **02-plan-mode-guide-official.md**
   - Plan Mode 社区整理指南（T3，非 Anthropic 官方）
   - 来源：claude-ai.chat（第三方域名）
   - 日期：2025-11-30
   - 何时使用以及何时不使用 Plan Mode

3. ✅ **03-andrew-ng-course-outline.md**
   - Andrew Ng 与 Anthropic 合作课程大纲
   - 讲师：Elie Schoppik
   - 日期：2025-08-05
   - 10 节课的完整内容概述

4. ✅ **04-addy-osmani-2026-workflow.md**
   - Addy Osmani 的 2026 AI 编码工作流
   - 作者：Addy Osmani（Google Chrome Engineer）
   - 日期：2026-01-04
   - 十大最佳实践的详细指南

5. ✅ **05-boris-cherny-workflow-x-thread.md**
   - Boris Cherny 在 X（Twitter）发布的 Claude Code 工作流分享（T2）
   - 作者：Boris Cherny（Claude Code 创建者，Anthropic）
   - 日期：2026-01
   - 来源：https://x.com/bcherny/status/2007179833990885678
   - 内容：并行实例、CLAUDE.md 配置、自动化工作流、Hooks 等个人工作流展示

6. ✅ **00-research-summary.md**（本文档）
   - 研究总结和综合

### 待获取文档（中优先级）

6. **Zvi Mowshowitz - Claude Codes**
   - 来源：https://thezvi.substack.com/p/ai-150-while-claude-codes
   - 需要获取完整内容

7. **Ethan Mollick - Claude Code and What Comes Next**
   - 来源：https://www.oneusefulthing.org/p/claude-code-and-what-comes-next
   - 访问被拒绝，需要尝试其他方式

8. **Clean Architecture with Claude Code**
   - 来源：https://www.peterbouda.eu/using-claude-code-for-clean-architecture.html
   - 需要获取完整内容

---

## 八、关键发现和建议总结

### 8.1 关于 Plan Mode

**官方建议（Boris Power）：**
- ✅ **始终以 Plan Mode 开始**（Shift+Tab 两次）
- ✅ 让 Claude 先规划，不要立即编码
- ✅ 计划确定后切换到自动接受模式

**适用场景：**
- 多文件/多步骤实现
- 大型代码库理解
- 端到端重构
- 测试规划
- 复杂任务分解

**不适用场景：**
- 快速修复
- 简单单文件编辑
- 样板代码生成
- 实验性迭代

### 8.2 关于多个 Opus 窗口

**重要澄清：**
- ✅ **技术上完全可以**同时运行多个 Opus 窗口
- ✅ 专家们经常这样做（Zvi 使用 5-10 个并行窗口）
- ⚠️ 限制主要是**配额和定价**，而非技术限制

**最佳实践：**
- 使用 git worktrees 实现多会话并行
- 每个 worktree 专注于独立任务
- 保持一致的命名约定
- 为每个 worktree 使用单独的终端标签

### 8.3 关于验证机制

**Boris 的首要建议：**
> "投入精力把验证机制做扎实。这是回报率最高的投资"

**实践方法：**
- 自动验证机制
- CI/CD 集成
- 测试驱动开发（TDD）
- 代码审查机器人
- AI-on-AI 审查

### 8.4 关于 CLAUDE.md

**团队最佳实践：**
- 使用一个共享的 CLAUDE.md 文件
- 提交到 Git 以便团队共享
- 定期调优内容
- 使用 prompt improver 优化

**应包含内容：**
- 常用 bash 命令
- 核心文件和函数
- 代码风格指南
- 测试说明
- 仓库礼仪
- 环境设置
- 项目特有行为

### 8.5 关于人在循环中

**所有专家一致同意：**
- 🚫 **不要**盲目信任 LLM 输出
- ✅ **必须**审查和测试所有内容
- ✅ 人类工程师保持责任
- ✅ "AI 辅助工程"而非"AI 自动化工程"

**Addy Osmani：**
> "AI 编码助手是令人难以置信的倍增器，但人类工程师仍然是节目的导演。"

### 8.6 关于工作流

**通用最佳模式：**

1. **规划 → 编码 → 调试 → 提交**（重复小块）
2. **TDD：** 编写测试 → 运行（失败）→ 编写代码 → 运行（通过）→ 提交
3. **多 Claude：** 一个编写，另一个验证

**Addy Osmani 的 2026 工作流：**
1. 从清晰计划开始（规格说明先于代码）
2. 将工作分解为小的迭代块
3. 提供广泛的上下文和指导
4. 选择正确的模型（并在需要时使用多个）
5. 在整个 SDLC 中利用 AI 编码
6. 保持人在循环中——验证、测试和审查所有内容
7. 经常提交并使用版本控制作为安全网
8. 使用规则和示例自定义 AI 的行为
9. 拥抱测试和自动化作为倍增器
10. 持续学习和适应

### 8.7 关于架构模式

**核心原则：**
- **依赖倒置：** 依赖指向内部
- **关注点分离：** 业务逻辑与基础设施分离
- **由内而外分层：** 从领域核心开始
- **可测试性：** 使代码易于测试

**Claude Code 可以帮助：**
- 尊重架构模式
- 遵循既定约定
- 产生干净、可测试的代码

---

## 九、Sources（来源）

### 官方文档
- [Claude Code: Best practices for agentic coding](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Plan Mode in Claude Code: When to Use It (and When Not To)](https://claude-ai.chat/blog/plan-mode-in-claude-code-when-to-use-it/)（社区来源 T3，非 Anthropic 官方；官方文档见 https://docs.anthropic.com/en/docs/claude-code/overview）
- [Claude Code Documentation](https://claude.ai/code)

### 课程和教程
- [Claude Code: A Highly Agentic Coding Assistant](https://www.deeplearning.ai/short-courses/claude-code-a-highly-agentic-coding-assistant/) (Andrew Ng & Elie Schoppik)

### 专家文章
- [My LLM coding workflow going into 2026](https://addyosmani.com/blog/ai-coding-workflow/) (Addy Osmani)
- [Claude Code and What Comes Next](https://www.oneusefulthing.org/p/claude-code-and-what-comes-next) (Ethan Mollick)
- [AI #150: While Claude Codes](https://thezvi.substack.com/p/ai-150-while-claude-codes) (Zvi Mowshowitz)
- [Claude Code creator Boris shares his setup](https://www.reddit.com/r/ClaudeAI/comments/1q2c0ne/claude_code_creator_boris_shares_his_setup_with/)

### 架构资源
- [Claude Code Toolkit - Code Architect](https://github.com/redpop/claude-code-toolkit/blob/main/docs/agents/architecture/code-architect.md)
- [Using Claude Code for Clean Architecture](https://www.peterbouda.eu/using-claude-code-for-clean-architecture.html)
- [Backend Coding Rules for AI Coding Agents: DDD and Hexagonal Architecture](https://medium.com/@bardia.khosravi/backend-coding-rules-for-ai-coding-agents-ddd-and-hexagonal-architecture-ecafe91c753f)

### 测试模式
- [Testing Patterns and Utilities - Claude Code Showcase](https://github.com/ChrisWiles/claude-code-showcase/blob/main/.claude/skills/testing-patterns/SKILL.md)
- [Python Testing Patterns Guide | Claude Code Skill](https://mcpmarket.com/tools/skills/python-testing-patterns-1767566172392)
- [The AAA Pattern in Unit Test Automation](https://semaphore.io/blog/aaa-pattern-test-automation)

---

## 十、结论

本研究收集并整理了 Claude Code 的最佳实践，来自：

1. ✅ **官方来源**：Anthropic 团队、Boris Power（Claude Code 之父）
2. ✅ **权威课程**：Andrew Ng 的 DeepLearning.AI
3. ✅ **知名专家**：Addy Osmani（Google）、Ethan Mollick（Wharton）、Zvi Mowshowitz
4. ✅ **架构实践**：DDD、六边形架构、洋葱架构、清洁架构
5. ✅ **测试模式**：AAA 模式、TDD

**关键发现：**
- Plan Mode 应该始终是开始（Shift+Tab 两次）
- 可以同时运行多个 Opus 窗口（使用 git worktrees）
- 验证机制是最高 ROI 投资
- 保持在循环中，审查所有内容
- AI 是"助手"，不是"替代品"

所有重要文档已保存为本地 MD 文件，包含完整的元信息（作者、日期、来源、重要性）。

---

**研究完成日期：** 2026-01-10
**研究执行者：** Claude (Anthropic)
**保存位置：** `C:\PythonProject\cc-tutorial\docs\research\`
