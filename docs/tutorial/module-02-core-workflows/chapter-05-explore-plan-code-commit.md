# Chapter 5: "探索 → 计划 → 编码 → 提交" 循环

**模块**: Module 2 - 核心工作流
**预计阅读时间**: 15 分钟
**难度**: ⭐⭐

---

## 学习目标

本章结束后，你将能够：

- [ ] 掌握 Claude Code 的黄金工作流
- [ ] 学会有效地提供上下文
- [ ] 理解如何编写高质量的提示词
- [ ] 掌握 Git 集成和提交最佳实践

---

## 前置知识

- [ ] 已完成 Module 1 - 入门基础
- [ ] 熟悉 Plan Mode 的使用
- [ ] 了解基本的 Git 操作

---

## 黄金工作流概述

### 什么是黄金工作流？

**[Tutorial perspective]** **"探索 → 计划 → 编码 → 提交"** 是 Boris Cherny 推荐的工作流程（[Best Practices Guide](../../research/01-claude-code-best-practices-anthropic-official.md), 2025-01），也是本教程认为最适合初学者建立良好习惯的工作模式。

```
┌─────────────────────────────────────────────────────────────┐
│              黄金工作流：四个阶段                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1️⃣ 探索 (Explore)                                         │
│     → 让 Claude 读取相关文件、图片、URL                      │
│     → 明确告诉它暂不编写代码                                 │
│     → 使用子代理验证细节                                     │
│                                                             │
│  2️⃣ 计划 (Plan)                                            │
│     → 使用 "think" 触发扩展思考                              │
│     → Claude 制定详细计划                                    │
│     → 可以创建文档或 GitHub issue                            │
│                                                             │
│  3️⃣ 编码 (Code)                                            │
│     → Claude 实现解决方案                                   │
│     → 明确验证合理性                                        │
│                                                             │
│  4️⃣ 提交 (Commit)                                          │
│     → Claude 提交结果并创建 PR                               │
│     → 更新 README 或 CHANGELOG                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 为什么这个工作流有效？

> **"步骤 1-2 至关重要——没有它们，Claude 倾向于直接编码。"**
> —— Anthropic 官方最佳实践

**关键原因**：

1. **避免盲目行动**: 先探索再行动，减少错误
2. **保持上下文**: 探索阶段收集的信息支持后续步骤
3. **明确目标**: 计划阶段确保方向正确
4. **可追溯性**: 每个阶段都有明确的输出

---

## 阶段 1: 探索 (Explore)

### 目标

让 Claude 理解代码库和相关上下文，但**不编写任何代码**。

### 如何做

#### 方法 1: 读取特定文件

```
> 请阅读以下文件，但不要编写任何代码：
- src/api/user.ts
- src/components/UserCard.tsx
- src/utils/auth.ts

阅读后，总结当前的认证流程。
```

**关键点**: 明确说"不要编写任何代码"

#### 方法 2: 探索性搜索

```
> 我想了解这个项目的错误处理机制。
请搜索并阅读相关文件，但暂时不要做任何修改。

搜索关键词：error, catch, throw, handleError
```

#### 方法 3: 使用子代理验证

```
> 我想添加一个新功能。首先，请使用子代理：
1. 探索现有代码库中的类似功能
2. 分析它们是如何实现的
3. 总结我可以复用的模式

不要开始编码，只需要探索和报告。
```

### 探索阶段的输出

探索阶段应该产生：

```
## 探索结果

### 相关文件
- src/api/user.ts: 用户 API 端点
- src/components/UserCard.tsx: 用户卡片组件
- src/utils/auth.ts: 认证工具函数

### 当前实现
[总结当前实现]

### 可复用模式
[列出可复用的代码模式]

### 潜在风险
[指出可能的坑]
```

---

## 阶段 2: 计划 (Plan)

### 目标

基于探索结果，制定详细的实现计划。

### 使用 "think" 触发扩展思考

Claude 支持不同级别的思考：

| 关键词 | 思考级别 | 使用场景 |
|--------|----------|----------|
| `think` | 基础思考 | 一般任务 |
| `think hard` | 深度思考 | 复杂任务 |
| `think harder` | 更深度思考 | 非常复杂的任务 |
| `ultrathink` | 最深度思考 | 最复杂的任务 |

```
> [在 Plan Mode 中]

请使用 "think hard" 模式，为添加用户个人资料功能制定详细计划。

需要包括：
1. 前端组件
2. API 端点
3. 数据库变更
4. 测试策略
```

### 计划阶段的输出

```
## 实现计划：用户个人资料功能

### 概述
[总体目标和策略]

### 详细步骤

#### 第 1 步：数据库层
- 文件: migrations/002_add_profile_table.sql
- 内容: 创建 user_profiles 表
- 理由: 分离用户信息和个人资料

#### 第 2 步：后端 API
- 文件: src/api/profile.ts
- 端点:
  - GET /api/user/profile
  - PUT /api/user/profile
- 理由: RESTful 设计

#### 第 3 步：前端组件
- 文件: src/pages/Profile.tsx
- 功能: 展示和编辑个人资料
- 理由: 集中管理

### 风险和缓解
- 风险: 头像上传可能很慢
- 缓解: 使用异步上传和进度条

### 测试计划
- 单元测试: API 端点
- 集成测试: 完整流程
- E2E 测试: 关键用户路径
```

### 可选：创建文档或 Issue

```
> 计划看起来不错。请将这个计划创建为一个 GitHub issue。

[Claude 创建 issue]

✓ Issue #123 已创建
https://github.com/your-repo/issues/123
```

---

## 阶段 3: 编码 (Code)

### 目标

根据批准的计划，实现解决方案。

### 退出 Plan Mode

```
> [按 Shift+Tab 退出 Plan Mode]

✓ 已退出 Plan Mode
现在可以执行修改操作了
```

### 让 Claude 实现

```
> 请按照计划开始实现。

从第 1 步开始，每完成一步后停下来确认。
```

### 编码阶段的最佳实践

#### 1. 分步执行

```
❌ 一次性实现所有功能
✅ 一步步实现，每步验证

> 完成第 1 步了吗？请暂停。

✓ 第 1 步完成：数据库迁移已创建

> 让我检查一下... 看起来不错，继续第 2 步。
```

#### 2. 明确验证

```
> 实现这个功能时，请：
1. 遵循项目现有的代码风格
2. 添加适当的错误处理
3. 确保 TypeScript 类型正确
4. 在实现后验证合理性
```

#### 3. 运行测试

```
> 完成第 2 步后，请运行相关测试。

[Claude 运行测试]

✓ 所有测试通过

> 很好，继续第 3 步。
```

---

## 阶段 4: 提交 (Commit)

### 目标

将完成的代码提交到版本控制系统，并创建 PR（如果需要）。

### Claude 的 Git 能力

Claude Code 可以：

- ✅ 分析变更并生成提交信息
- ✅ 创建符合规范的 commit message
- ✅ 创建分支
- ✅ 推送到远程
- ✅ 创建 Pull Request
- ✅ 处理 merge conflicts

### 提交流程

#### 1. 查看变更

```
> 请显示当前的 git 变更

[Claude 运行 git diff]

Modified files:
- src/api/profile.ts
- src/pages/Profile.tsx
- migrations/002_add_profile_table.sql
```

#### 2. 创建提交

```
> 请提交这些变更

[Claude 分析变更]

基于变更内容，我建议以下提交信息：

```
feat: add user profile feature

- Add profile database table
- Implement profile API endpoints
- Create profile page component
- Add avatar upload functionality

Closes #123
```

是否使用这个提交信息？

> 是的，使用这个信息

[Claude 创建提交]

✓ 提交创建成功
commit abc123def...
```

#### 3. 创建 PR（可选）

```
> 请为这个提交创建 Pull Request

[Claude 使用 gh CLI 创建 PR]

✓ PR #124 已创建
https://github.com/your-repo/pull/124
```

### 提交信息最佳实践

Claude 生成的提交信息遵循常见约定：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**常见类型**:
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档变更
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 添加测试
- `chore`: 构建/工具变更

---

## 完整示例

### 场景：添加用户搜索功能

#### 阶段 1: 探索

```
> 我想添加用户搜索功能。
首先，请探索现有的代码库，了解：
1. 当前的用户数据结构
2. 是否有类似的搜索功能可以参考
3. 推荐使用的搜索库

不要编写任何代码，只需要探索和报告。
```

**Claude 的响应**:

```
我来探索一下代码库...

[读取 src/models/User.ts]
[读取 src/api/user.ts]
[搜索现有搜索实现]

## 探索结果

### 用户数据结构
User 模型包含：
- id, username, email, displayName, bio
- 索引: username, email

### 类似功能
发现 src/components/PostSearch.tsx
- 使用 fuse.js 进行模糊搜索
- 可以参考其实现

### 推荐方案
对于用户搜索，建议：
1. 使用 fuse.js（项目已依赖）
2. 搜索字段: username, displayName
3. 支持拼音搜索（可选）

### 风险
- 用户量大时前端搜索可能慢
- 建议: 考虑分页或虚拟滚动
```

#### 阶段 2: 计划

```
> [激活 Plan Mode]
请使用 "think hard" 模式制定详细计划。
```

**Claude 的响应**:

```
## 实现计划：用户搜索功能

### 第 1 步：创建搜索 Hook
- 文件: src/hooks/useUserSearch.ts
- 功能: 封装搜索逻辑
- 使用 fuse.js 进行模糊匹配

### 第 2 步：创建搜索组件
- 文件: src/components/UserSearch.tsx
- 功能: 搜索输入框和结果列表
- 参考: PostSearch.tsx 的设计

### 第 3 步：集成到导航
- 文件: src/components/Navbar.tsx
- 功能: 添加搜索按钮和模态框

### 第 4 步：添加路由
- 文件: src/App.tsx
- 路由: /search/users?q=

### 第 5 步：测试
- 单元测试: useUserSearch Hook
- 集成测试: 搜索流程

批准此计划吗？
```

#### 阶段 3: 编码

```
> [退出 Plan Mode]
计划看起来不错，请开始实现。

从第 1 步开始。
```

**Claude 逐步实现**...

```
✓ 第 1 步完成: src/hooks/useUserSearch.ts

✓ 第 2 步完成: src/components/UserSearch.tsx

✓ 第 3 步完成: 已集成到 Navbar

✓ 第 4 步完成: 路由已添加

✓ 第 5 步完成: 测试已添加，全部通过
```

#### 阶段 4: 提交

```
> 请提交这些变更并创建 PR
```

**Claude 的响应**:

```
分析变更...

建议的提交信息：

```
feat: add user search feature

- Implement useUserSearch hook with fuse.js
- Create UserSearch component with autocomplete
- Integrate search into navigation bar
- Add search route with query parameter
- Add unit and integration tests

Refs #456
```

创建提交...

✓ 提交成功

创建 PR...

✓ PR #457 已创建
https://github.com/your-repo/pull/457
```

---

## 工作流变体

### 快速任务变体

对于简单任务，可以简化流程：

```
1. 探索: 快速读取相关文件
2. 计划: 跳过（或快速计划）
3. 编码: 直接实现
4. 提交: 提交变更
```

### TDD 变体

在下一章详细讲解，基本流程：

```
1. 探索: 理解需求
2. 计划: 规划测试
3. 编码: 先写测试，再写实现
4. 提交: 分别提交测试和代码
```

### 多实例变体

在后面章节详细讲解，基本流程：

```
实例 1: 探索 + 计划
实例 2: 实现（基于实例 1 的计划）
实例 3: 审查和验证
```

---

## 常见错误和如何避免

### 错误 1: 跳过探索阶段

```
❌ "直接添加用户搜索功能"

结果: Claude 可能不知道项目已使用 fuse.js，
     实现了不一致的方案

✅ "先探索现有的搜索实现，然后添加用户搜索"
```

### 错误 2: 探索后立即编码

```
❌ 探索完就让 Claude 开始编码

结果: 缺少计划，可能方向错误

✅ 探索 → 计划 → 审查计划 → 编码
```

### 错误 3: 一次性实现所有步骤

```
❌ "按照计划实现所有功能"

结果: 如果早期有错，后面都白费

✅ "一步步实现，每步确认"
```

### 错误 4: 不使用 Plan Mode

```
❌ 对于复杂任务直接编码

结果: 返工率高

✅ 复杂任务使用 Plan Mode
```

---

## 总结

### 黄金工作流回顾

```
┌─────────────────────────────────────────────┐
│  探索 → 计划 → 编码 → 提交                  │
│  Explore → Plan → Code → Commit             │
├─────────────────────────────────────────────┤
│                                             │
│  1️⃣ 探索: 读取文件，理解上下文              │
│  2️⃣ 计划: 使用 "think" 制定详细计划         │
│  3️⃣ 编码: 分步实现，每步验证                │
│  4️⃣ 提交: 提交变更，创建 PR                 │
│                                             │
└─────────────────────────────────────────────┘
```

### 关键要点

1. **不要跳过探索**: 了解现有代码再动手
2. **使用 "think" 触发**: 复杂任务用扩展思考
3. **分步执行**: 一步步来，每步验证
4. **善用 Git**: 让 Claude 帮你提交和创建 PR

### 下一步

在下一章中，我们将学习**测试驱动开发（TDD）**，这是 Anthropic 团队最喜欢的可验证变更工作流。

---

## 进一步阅读

### 官方文档
- `docs/research/01-claude-code-best-practices-anthropic-official.md` - 官方最佳实践

### 相关章节
- [Chapter 4 - Plan Mode 革命](../module-01-fundamentals/chapter-04-plan-mode.md)
- [Chapter 6 - 测试驱动开发](chapter-06-tdd.md) - 下一章

---

## 练习

完成以下练习：

1. **基本练习**
   - [ ] 对你的项目执行探索阶段
   - [ ] 为一个简单功能制定计划
   - [ ] 按计划实现并提交

2. **进阶练习**
   - [ ] 使用 "think hard" 模式规划复杂功能
   - [ ] 分步实现，每步验证
   - [ ] 让 Claude 创建有意义的提交信息

3. **实战练习**
   - [ ] 选择一个真实需求
   - [ ] 完整执行"探索 → 计划 → 编码 → 提交"
   - [ ] 对比使用/不使用此工作流的差异

---

**上一章**: [Chapter 4 - Plan Mode 革命](../module-01-fundamentals/chapter-04-plan-mode.md)
**下一章**: [Chapter 6 - 测试驱动开发](chapter-06-tdd.md)

```java

byte[] data = "Hello, World!".getBytes();

ByteBuffer buffer = ByteBuffer.allocate(1024);

io.netty.buffer.ByteBuf byteBuf = io.netty.buffer.Unpooled.buffer(1024);


GzipInputStream gzipInputStream = new GzipInputStream(new ByteArrayInputStream(data));
Inflater inflater = new Inflater();
inflater.setInput(data);
inflter.inflate(buffer);
int x = 1;
inflater.end(x);

byte[] buffer = new byte[1024];
int len = gzipInputStream.read(buffer);
while (len != -1) {
    System.out.println(new String(buffer, 0, len));
    len = gzipInputStream.read(buffer);
}
gzipInputStream.close();
```

