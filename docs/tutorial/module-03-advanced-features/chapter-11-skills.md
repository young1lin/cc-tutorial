# Chapter 11: Skills 系统

**模块**: Module 3 - 高级功能
**预计阅读时间**: 12 分钟
**难度**: ⭐⭐

---

## 学习目标

本章结束后，你将能够：

- [ ] 理解 Skills 系统的概念和价值
- [ ] 掌握 Skills 的创建和组织
- [ ] 学会编写可重用的 Skills
- [ ] 了解 Skills 与 Plugin、MCP 的区别

---

## 前置知识

- [ ] 已完成 Module 2 - 核心工作流
- [ ] 熟悉 Claude Code 的基本使用
- [ ] 了解 Prompt Engineering 基础

---

## 什么是 Skills 系统？

### Skills 概述

**Claude Code Skills** 是可重用的提示词模板，用于封装常见任务的 AI 交互模式。

```
┌─────────────────────────────────────────────────────────┐
│              Skills vs Plugin vs MCP                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Skills                                                 │
│  ─────────────────────────────────────────────────      │
│  • 本质：Prompt 模板                                    │
│  • 复杂度：低                                           │
│  • 适用：可重用的代码模式、审查流程                     │
│  • 示例：代码审查、文档生成、测试编写                   │
│                                                         │
│  Plugin                                                 │
│  ─────────────────────────────────────────────────      │
│  • 本质：npm 包 + 自定义工具                            │
│  • 复杂度：高                                           │
│  • 适用：扩展核心功能、集成外部系统                     │
│  • 示例：自定义 linter、CI 集成                         │
│                                                         │
│  MCP                                                    │
│  ─────────────────────────────────────────────────      │
│  • 本质：协议 + 服务器                                  │
│  • 复杂度：中-高                                        │
│  • 适用：连接外部服务、实时数据                         │
│  • 示例：数据库连接、API 集成                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Skills 的价值

```
┌─────────────────────────────────────────────────────────┐
│              使用 Skills 的好处                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 一致性                                              │
│     → 确保相同任务的处理方式一致                         │
│     → 减少人工编写的提示词变体                           │
│                                                         │
│  2. 效率                                                │
│     → 无需重复编写相同的提示词                           │
│     → 快速调用常见任务                                   │
│                                                         │
│  3. 可维护                                              │
│     → 集中管理提示词                                     │
│     → 容易更新和改进                                     │
│                                                         │
│  4. 可共享                                              │
│     → 团队可以共享 Skills                               │
│     → 社区可以贡献 Skills                               │
│                                                         │
│  5. 版本控制                                            │
│     → 技能随项目一起版本控制                             │
│     → 可以追踪变更历史                                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Skills 基础

### Skills 目录结构

```
project/
├── .skills/                  # Skills 目录
│   ├── code-review/          # 代码审查技能
│   │   ├── skill.md          # 技能定义
│   │   └── examples/         # 示例
│   │       └── good-review.md
│   ├── test-generator/       # 测试生成技能
│   │   └── skill.md
│   └── doc-writer/           # 文档编写技能
│       └── skill.md
├── src/
└── CLAUDE.md
```

### Skill 文件格式

**.skills/my-skill/skill.md**:

```markdown
---
name: "my-skill"
description: "A brief description of what this skill does"
version: "1.0.0"
author: "Your Name"
tags: ["testing", "quality", "review"]
---

# Skill Name

## Overview

[What this skill does and when to use it]

## When to Use

- [ ] Scenario 1
- [ ] Scenario 2
- [ ] Scenario 3

## Instructions

[Step-by-step instructions for Claude]

## Examples

### Example 1: [Title]

[Input]:
```
[user input or code]
```

[Expected Output]:
```
[what Claude should produce]
```

## Notes

[Additional context, tips, or caveats]
```

---

## 创建 Skills

### 实战示例：代码审查 Skill

让我们创建一个实用的代码审查 Skill。

#### 步骤 1: 创建 Skill 目录

```bash
mkdir -p .skills/code-review/examples
```

#### 步骤 2: 编写 Skill 定义

**.skills/code-review/skill.md**:

```markdown
---
name: "code-review"
description: "Comprehensive code review following best practices"
version: "1.0.0"
author: "Dev Team"
tags: ["review", "quality", "best-practices"]
---

# Code Review Skill

## Overview

This skill performs a comprehensive code review, checking for:
- Code correctness and logic errors
- Security vulnerabilities
- Performance issues
- Code style and consistency
- Test coverage
- Documentation

## When to Use

Use this skill when:
- [ ] Reviewing pull requests
- [ ] Auditing code before commit
- [ ] Onboarding new team members
- [ ] Learning codebase patterns

## Instructions

### Phase 1: Understanding (1-2 minutes)

1. **Read the context**
   - Read CLAUDE.md to understand project conventions
   - Read related files to understand the codebase
   - Identify the purpose of the changes

2. **Identify the scope**
   - What files were changed?
   - What is the intended functionality?
   - Are there breaking changes?

### Phase 2: Analysis (3-5 minutes)

For each changed file:

1. **Correctness Check**
   - Does the code do what it's supposed to do?
   - Are there obvious bugs?
   - Are edge cases handled?
   - Is error handling appropriate?

2. **Security Check**
   - Are user inputs validated?
   - Are there injection vulnerabilities?
   - Is sensitive data protected?
   - Are dependencies secure?

3. **Performance Check**
   - Are there obvious performance issues?
   - Is there unnecessary computation?
   - Are resources properly managed?
   - Are there better algorithms/approaches?

4. **Style Check**
   - Does it follow project style guidelines?
   - Are names meaningful?
   - Is code properly formatted?
   - Are comments appropriate?

5. **Test Check**
   - Are tests included?
   - Do tests cover edge cases?
   - Are tests meaningful?
   - Are there missing test cases?

6. **Documentation Check**
   - Is complex code explained?
   - Are APIs documented?
   - Are changes reflected in docs?

### Phase 3: Feedback (2-3 minutes)

Organize feedback into categories:

#### 🔴 Critical Issues (Must Fix)

Security vulnerabilities, crashes, data loss, breaking changes

#### 🟡 Major Issues (Should Fix)

Performance problems, poor error handling, missing tests

#### 🟢 Minor Issues (Nice to Have)

Style inconsistencies, unclear naming, missing comments

#### ✅ Positive Feedback

Good practices, clever solutions, clean code

### Phase 4: Report

Generate a structured report:

```markdown
## Code Review: [PR/Commit Title]

**Files Changed**: N
**Lines Added**: N
**Lines Removed**: N

### Summary
[2-3 sentence overview]

### 🔴 Critical Issues
[List critical issues with file:line references]

### 🟡 Major Issues
[List major issues with file:line references]

### 🟢 Minor Issues
[List minor issues with file:line references]

### ✅ What's Good
[Highlight good practices]

### Recommendations
[Specific actionable suggestions]
```

## Examples

### Example 1: Simple Bug Fix

**Input**: A PR fixing a null pointer exception

**Expected Review**:
```markdown
## Code Review: Fix NPE in UserService

### Summary
Fixes a critical null pointer exception when user ID is not found.
The fix is appropriate and includes error handling.

### ✅ What's Good
- Proper null check added
- Error message is descriptive
- Test case included

### 🟡 Recommendations
Consider returning a Result type instead of throwing exception
for better error handling composition.
```

### Example 2: New Feature

**Input**: A PR adding user authentication

**Expected Review**:
```markdown
## Code Review: Add User Authentication

### Summary
Implements JWT-based authentication with login and refresh endpoints.
Overall implementation is solid but has some security concerns.

### 🔴 Critical Issues
1. **JWT Secret Hardcoded** (src/auth/jwt.ts:15)
   - Secret is committed to code
   - Use environment variables

2. **Missing Rate Limiting** (src/api/auth.ts:45)
   - Login endpoint has no rate limiting
   - Vulnerable to brute force attacks

### 🟡 Major Issues
1. **Token Expiration Too Long** (src/auth/jwt.ts:30)
   - 30 days is too long for access tokens
   - Consider 15-30 minutes

2. **No Account Lockout**
   - Failed attempts don't lock accounts
   - Should implement after N failed attempts

### 🟢 Minor Issues
1. Inconsistent error messages
2. Missing JSDoc comments
3. Test coverage could be improved

### ✅ What's Good
- Clean separation of concerns
- Uses established libraries
- Includes basic tests
- Refresh token implementation

### Recommendations
1. Move secrets to environment variables
2. Implement rate limiting
3. Add account lockout mechanism
4. Shorten token expiration
5. Add integration tests
```

## Notes

- **Be constructive**: Focus on improvement, not criticism
- **Explain why**: Don't just say what's wrong, explain the impact
- **Provide alternatives**: Suggest better approaches when possible
- **Acknowledge good work**: Positive reinforcement is important
- **Prioritize**: Critical issues first, then major, then minor
- **Be specific**: Include file paths and line numbers
```

#### 步骤 3: 创建示例

**.skills/code-review/examples/good-review.md**:

```markdown
---
title: "Example of Good Code Review"
context: "Reviewing a PR that adds file upload functionality"
---

# Example: File Upload Feature Review

## Context

The PR adds a file upload feature with the following changes:
- New endpoint: POST /api/files/upload
- File validation (size, type)
- Cloud storage integration
- Progress tracking

## Review Output

### Summary

Implements file upload with proper validation and cloud storage.
Overall good implementation with minor security concerns.

### 🔴 Critical Issues

**1. Missing Virus Scanning** (src/api/files/upload.ts:42)
```typescript
// File is directly uploaded without scanning
await cloudStorage.upload(file);
```
**Impact**: Malicious files could be uploaded and distributed
**Recommendation**: Integrate virus scanning before upload

**2. No File Type Verification** (src/middleware/upload.ts:28)
```typescript
// Only checks MIME type from request
const isValidType = ALLOWED_TYPES.includes(file.mimetype);
```
**Impact**: MIME type can be spoofed
**Recommendation**: Verify file by magic number/content

### 🟡 Major Issues

**1. No Rate Limiting** (src/api/files/upload.ts:15)
- Upload endpoint has no rate limit
- Vulnerable to DoS attacks

**2. Missing File Size Check in Middleware**
- Size is checked after upload completes
- Wastes bandwidth for oversized files

### 🟢 Minor Issues

1. Inconsistent error responses
2. Missing logging for upload failures
3. No upload progress for large files

### ✅ What's Good

1. ✓ Proper file size limit (10MB)
2. ✓ Whitelist approach for allowed types
3. ✓ Cloud storage with CDN
4. ✓ Includes unit tests
5. ✓ Clean error handling
6. ✓ Uses streaming for uploads

### Recommendations

1. **High Priority**: Add virus scanning
2. **High Priority**: Verify file by content, not MIME type
3. **Medium Priority**: Add rate limiting
4. **Medium Priority**: Move size check to middleware
5. **Low Priority**: Add upload progress tracking
6. **Low Priority**: Standardize error responses

### Approval Status

**🟡 Approve with Changes**

Address critical issues before merging.
Major issues should be addressed soon after.
```

#### 步骤 4: 使用 Skill

```
> 使用 code-review skill 审查这个 PR：
> files: src/api/user.ts, src/models/User.ts
> changes: Added user profile functionality

[Claude 使用 skill 进行审查]

## Code Review: Add User Profile Functionality

**Files Changed**: 2
**Lines Added**: 156
**Lines Removed**: 23

### Summary
Implements user profile with avatar upload and bio editing.
Good implementation with security concerns around file uploads.

### 🔴 Critical Issues
[详细审查...]

### Recommendations
[具体建议...]
```

---

## 更多 Skill 示例

### Skill 2: 测试生成器

**.skills/test-generator/skill.md**:

```markdown
---
name: "test-generator"
description: "Generate comprehensive tests following AAA pattern"
version: "1.0.0"
tags: ["testing", "tdd", "quality"]
---

# Test Generator Skill

## Overview

Generate comprehensive tests for code following the AAA (Arrange-Act-Assert) pattern.

## When to Use

- [ ] Writing tests for new code
- [ ] Increasing test coverage
- [ ] Finding missing test cases

## Instructions

### Phase 1: Analysis

1. **Understand the code**
   - Read the implementation
   - Identify public methods/functions
   - Understand dependencies and side effects

2. **Identify test cases**
   - Happy path: normal inputs
   - Edge cases: boundary values
   - Error cases: invalid inputs
   - Integration points: dependencies

### Phase 2: Generate Tests

For each function/method:

1. **Name tests clearly**
   ```
   ✓ should [expected behavior] when [condition]
   ✗ test1, testFunction, doTest
   ```

2. **Use AAA pattern**
   ```typescript
   it('should return user when valid ID provided', () => {
     // Arrange
     const userId = '123';
     const expectedUser = mockUser();

     // Act
     const result = await userService.getUser(userId);

     // Assert
     expect(result).toEqual(expectedUser);
   });
   ```

3. **Cover all scenarios**
   - Valid inputs
   - Invalid inputs
   - Boundary values
   - Error conditions

### Phase 3: Test Organization

```typescript
describe('UserService', () => {
  describe('getUser', () => {
    describe('valid inputs', () => {
      it('should return user when ID exists');
      it('should return user with all fields');
    });

    describe('invalid inputs', () => {
      it('should throw when ID is null');
      it('should throw when ID is empty string');
      it('should throw when user not found');
    });

    describe('edge cases', () => {
      it('should handle special characters in ID');
      it('should handle very long IDs');
    });
  });
});
```

## Examples

### Example: String Validator

**Input Code**:
```typescript
function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}
```

**Generated Tests**:
```typescript
describe('validateEmail', () => {
  describe('valid emails', () => {
    it('should accept simple email', () => {
      // Arrange
      const email = 'user@example.com';

      // Act
      const result = validateEmail(email);

      // Assert
      expect(result).toBe(true);
    });

    it('should accept email with dots', () => {
      const email = 'first.last@example.com';
      expect(validateEmail(email)).toBe(true);
    });

    it('should accept email with numbers', () => {
      const email = 'user123@example.com';
      expect(validateEmail(email)).toBe(true);
    });
  });

  describe('invalid emails', () => {
    it('should reject email without @', () => {
      const email = 'userexample.com';
      expect(validateEmail(email)).toBe(false);
    });

    it('should reject email without domain', () => {
      const email = 'user@';
      expect(validateEmail(email)).toBe(false);
    });

    it('should reject email with spaces', () => {
      const email = 'user @example.com';
      expect(validateEmail(email)).toBe(false);
    });
  });

  describe('edge cases', () => {
    it('should handle empty string', () => {
      expect(validateEmail('')).toBe(false);
    });

    it('should handle null', () => {
      expect(validateEmail(null as any)).toBe(false);
    });

    it('should handle multiple @ signs', () => {
      expect(validateEmail('user@name@example.com')).toBe(false);
    });
  });
});
```

## Notes

- **Mock external dependencies**: Use mocking for databases, APIs, etc.
- **Test behavior, not implementation**: Focus on what, not how
- **Keep tests independent**: Each test should work in isolation
- **Use descriptive names**: Test names should document expected behavior
- **Keep it simple**: Tests should be easy to read and understand
```

### Skill 3: 文档生成器

**.skills/doc-writer/skill.md**:

```markdown
---
name: "doc-writer"
description: "Generate comprehensive documentation for code"
version: "1.0.0"
tags: ["documentation", "communication"]
---

# Documentation Writer Skill

## Overview

Generate clear, comprehensive documentation for code, APIs, and features.

## When to Use

- [ ] Writing API documentation
- [ ] Creating README files
- [ ] Documenting new features
- [ ] Generating JSDoc comments

## Instructions

### Phase 1: Understand the Code

1. **Read the implementation**
2. **Identify the purpose**
3. **Find usage examples**
4. **Understand the audience**

### Phase 2: Structure Documentation

#### For Functions/Methods:

```typescript
/**
 * Brief description of what it does.
 *
 * @param paramName - Description of parameter
 * @param paramTwo - Description of second parameter
 * @returns Description of return value
 * @throws {ErrorType} When and why error is thrown
 *
 * @example
 * ```typescript
 * const result = functionName(arg1, arg2);
 * console.log(result); // Expected output
 * ```
 *
 * @remarks
 * Additional context, implementation details, or caveats.
 *
 * @see {@link RelatedFunction} for related functionality
 */
```

#### For APIs:

```markdown
## Endpoint Name

Brief description of what this endpoint does.

### Request

**Method**: `POST`
**Path**: `/api/users`
**Authentication**: Required (Bearer token)

**Headers**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**Body**:
```json
{
  "name": "string",
  "email": "string"
}
```

**Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | User's full name |
| email | string | Yes | User's email address |

### Response

**Success (200)**:
```json
{
  "id": "string",
  "name": "string",
  "email": "string",
  "createdAt": "ISO date"
}
```

**Error (400)**:
```json
{
  "error": "Invalid input",
  "details": ["email is required"]
}
```

### Examples

```bash
curl -X POST https://api.example.com/users \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com"}'
```

### Error Codes

| Code | Description |
|------|-------------|
| 400 | Invalid input |
| 401 | Unauthorized |
| 409 | Email already exists |
```

## Examples

### Example: User Service Documentation

**Input**: UserService class

**Output**:
```markdown
# UserService

Manages user-related operations including creation, retrieval, and updates.

## Class: UserService

### Constructor

```typescript
constructor(database: Database, emailService: EmailService)
```

Creates a new UserService instance.

**Parameters**:
- `database` - Database connection for user storage
- `emailService` - Service for sending emails

### Methods

#### createUser

```typescript
async createUser(data: CreateUserData): Promise<User>
```

Creates a new user account.

**Parameters**:
- `data` - User creation data
  - `email` (string, required) - User's email address
  - `password` (string, required) - User's password (will be hashed)
  - `name` (string, optional) - User's display name

**Returns**: Promise resolving to created User object

**Throws**:
- `ValidationError` - If input validation fails
- `DuplicateError` - If email already exists

**Example**:
```typescript
const user = await userService.createUser({
  email: 'user@example.com',
  password: 'securepassword',
  name: 'John Doe'
});
```

**Remarks**:
- Passwords are automatically hashed using bcrypt
- Email verification is sent automatically
- User is created in inactive state

## Usage Example

```typescript
import { UserService } from './services/UserService';

const userService = new UserService(database, emailService);

// Create a user
const user = await userService.createUser({
  email: 'user@example.com',
  password: 'password123',
  name: 'Jane Doe'
});

console.log(`Created user: ${user.id}`);
```

## Related

- [User Model](./models/User.md)
- [Authentication Guide](./guides/authentication.md)
```

## Notes

- **Know your audience**: Adjust detail level accordingly
- **Be consistent**: Use same format/style throughout
- **Keep it current**: Update docs with code changes
- **Show examples**: Examples are worth thousand words
- **Use diagrams**: Visuals help explain complex concepts
```

---

## Skills 管理

### 组织 Skills

```
.skills/
├── review/                    # 审查相关
│   ├── code-review/
│   ├── security-review/
│   └── performance-review/
├── generation/                # 生成相关
│   ├── test-generator/
│   ├── doc-writer/
│   └── code-generator/
├── analysis/                  # 分析相关
│   ├── bug-finder/
│   ├── dependency-analyzer/
│   └── complexity-checker/
└── workflow/                  # 工作流相关
    ├── pr-template/
    ├── release-checklist/
    └── migration-guide/
```

### Skills 配置

**CLAUDE.md** 中添加 Skills 引用：

```markdown
# Project Skills

This project uses the following Claude Code Skills:

## Code Quality
- `code-review` - Comprehensive code review
- `test-generator` - Generate tests with AAA pattern

## Documentation
- `doc-writer` - Generate documentation

## Usage

To use a skill, reference it by name:
```
> 使用 code-review skill 审查 PR #123
```

For custom workflows, combine multiple skills:
```
> 使用 doc-writer 生成 API 文档，
> 然后使用 test-generator 生成测试
```
```

---

## Skills 最佳实践

### 1. 保持专注

```
✅ 好的 Skill：
- 专注于单一任务
- 清晰的边界
- 易于理解和维护

❌ 不好的 Skill：
- 试图做太多事情
- 职责不清晰
- 难以使用
```

### 2. 提供示例

```
每个 Skill 应该包含：
1. 输入示例
2. 预期输出示例
3. 多个场景示例

示例越具体，效果越好。
```

### 3. 版本控制

```markdown
---
name: "my-skill"
version: "2.0.0"  # 语义化版本
---

## Changelog

### 2.0.0 (2026-01-10)
- Breaking: Changed instruction format
- Added: New phase for security checks

### 1.1.0 (2026-01-05)
- Added: Examples section
- Fixed: Typo in instructions

### 1.0.0 (2025-12-20)
- Initial release
```

### 4. 团队协作

```
团队协作技巧：

1. **共享 Skills 库**
   - 将 Skills 放在共享仓库
   - 团队成员可以贡献和改进

2. **定期审查**
   - 像审查代码一样审查 Skills
   - 收集反馈并改进

3. **文档化**
   - 维护 Skills 索引
   - 记录使用场景
```

---

## 常见问题

### Q1: 什么时候用 Skill，什么时候用 Plugin？

**A**: **复杂度判断**

```
使用 Skill 如果：
✅ 只是重用提示词模式
✅ 不需要额外代码执行
✅ 主要是指导 Claude 的行为

使用 Plugin 如果：
✅ 需要自定义工具
✅ 需要外部依赖
✅ 需要复杂的状态管理
✅ 需要执行实际操作（不只是生成内容）
```

### Q2: Skill 可以调用其他 Skill 吗？

**A**: 可以！

```markdown
## Instructions

1. First, use the `code-review` skill to analyze the code
2. Then, use the `bug-finder` skill to identify potential bugs
3. Finally, use the `test-generator` skill to create tests
```

### Q3: 如何共享 Skills？

**A**: 三种方式

```bash
# 1. Git 子模块
git submodule add https://github.com/org/skills.git .skills

# 2. npm 包
npm install @org/skills
# 在 .skills/ 中创建符号链接

# 3. 直接复制
cp -r /path/to/shared-skills/* .skills/
```

---

## 总结

### 关键要点

1. **Skills 是 Prompt 模板**
   - 可重用的 AI 交互模式
   - 比 Plugin 简单，但功能强大
   - 适合标准化常见任务

2. **Skills 的结构**
   - 元数据（name, description, version）
   - 指令（分步骤）
   - 示例（输入/输出）

3. **常见 Skills 类型**
   - 代码审查
   - 测试生成
   - 文档编写
   - 代码分析

4. **最佳实践**
   - 保持专注
   - 提供示例
   - 版本控制
   - 团队协作

### 下一步

在下一章中，我们将学习 **Hooks 配置**：
- Hooks 的概念和类型
- 配置 Pre/Post Hooks
- Hooks 使用场景
- 实际应用案例

---

## 进一步阅读

### 官方文档
- Claude Code Skills Guide

### 相关章节
- [Chapter 9 - Plugin 系统](chapter-09-plugins.md)
- [Chapter 10 - MCP 深度解析](chapter-10-mcp.md)
- [Chapter 12 - Hooks 配置](chapter-12-hooks.md)

---

## 练习

完成以下练习：

1. **基本练习**
   - [ ] 创建一个简单的 Skill
   - [ ] 为 Skill 添加示例
   - [ ] 在对话中使用 Skill

2. **进阶练习**
   - [ ] 创建 Skill 系列（相关技能）
   - [ ] 实现 Skill 之间的调用
   - [ ] 为 Skill 添加版本控制

3. **实战练习**
   - [ ] 为你的团队创建常用 Skills
   - [ ] 建立共享 Skills 库
   - [ ] 收集反馈并改进

---

**上一章**: [Chapter 10 - MCP 深度解析](chapter-10-mcp.md)
**下一章**: [Chapter 12 - Hooks 配置](chapter-12-hooks.md)
