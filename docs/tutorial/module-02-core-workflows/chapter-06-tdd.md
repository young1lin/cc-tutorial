# Chapter 6: 测试驱动开发 (TDD)

**模块**: Module 2 - 核心工作流
**预计阅读时间**: 12 分钟
**难度**: ⭐⭐

---

## 学习目标

本章结束后，你将能够：

- [ ] 理解为什么 TDD 与 Claude Code 配合得特别好
- [ ] 掌握 Claude Code 的 TDD 工作流
- [ ] 学会如何让 Claude 先写测试、再写实现
- [ ] 应用 AAA 测试模式

---

## 前置知识

- [ ] 已完成 Chapter 5 - 探索/计划/编码/提交
- [ ] 了解基本的测试概念
- [ ] 熟悉 Plan Mode

---

## 为什么 TDD 与 Claude Code 配合得特别好？

### TDD 的核心理念

**测试驱动开发 (TDD)** 是一种开发方法：

```
┌─────────────────────────────────────────────┐
│              TDD 循环                         │
├─────────────────────────────────────────────┤
│                                             │
│  1. 🔴 Red: 写一个失败的测试                 │
│     → 描述期望的行为                         │
│                                             │
│  2. 🟢 Green: 写最少的代码让测试通过         │
│     → 不需要完美，只需要通过测试             │
│                                             │
│  3. 🔵 Refactor: 重构代码                   │
│     → 改进代码质量，保持测试通过             │
│                                             │
└─────────────────────────────────────────────┘
```

### Claude Code + TDD = 完美组合

> **"Claude 在有明确目标（测试用例）时表现最佳。"**
> —— Anthropic 官方最佳实践

**为什么**：

1. **明确的目标**: 测试提供了清晰的期望
2. **自动验证**: Claude 可以运行测试并迭代
3. **快速反馈**: 测试失败立即反馈
4. **防止过度设计**: 只实现测试要求的功能

### Anthropic 团队最喜欢的 TDD 工作流

这是 Anthropic 内部用于可验证变更的首选工作流：

```
1. 要求 Claude 编写测试（基于期望的输入/输出）
   → 明确说明正在进行 TDD
   → 避免创建 mock 实现

2. 告诉 Claude 运行测试并确认失败
   → 明确不要编写实现代码

3. 要求 Claude 提交测试

4. 要求 Claude 编写通过测试的代码
   → 指示不要修改测试
   → 让 Claude 持续迭代直到所有测试通过

5. 要求 Claude 提交代码
```

---

## Claude Code TDD 工作流详解

### 完整示例：添加用户年龄验证功能

#### 第 1 步：编写测试

```
> 我要进行 TDD 开发。

请为用户模型添加年龄验证功能：
- 年龄必须是 18-120 之间的整数
- 如果年龄无效，抛出 ValidationError

先编写测试，不要创建任何实现代码。

使用 AAA 模式（Arrange-Act-Assert）。
```

**Claude 的响应**:

```typescript
// src/models/__tests__/User.test.ts

import { User } from '../User';
import { ValidationError } from '../errors';

describe('User.age validation', () => {
  describe('valid ages', () => {
    it('should accept age 18', () => {
      // Arrange
      const user = new User();
      const validAge = 18;

      // Act
      user.setAge(validAge);

      // Assert
      expect(user.age).toBe(validAge);
    });

    it('should accept age 120', () => {
      // Arrange
      const user = new User();
      const validAge = 120;

      // Act
      user.setAge(validAge);

      // Assert
      expect(user.age).toBe(validAge);
    });

    it('should accept age between 18 and 120', () => {
      // Arrange
      const user = new User();
      const validAge = 50;

      // Act
      user.setAge(validAge);

      // Assert
      expect(user.age).toBe(validAge);
    });
  });

  describe('invalid ages', () => {
    it('should throw ValidationError for age < 18', () => {
      // Arrange
      const user = new User();
      const invalidAge = 17;

      // Act & Assert
      expect(() => user.setAge(invalidAge)).toThrow(ValidationError);
    });

    it('should throw ValidationError for age > 120', () => {
      // Arrange
      const user = new User();
      const invalidAge = 121;

      // Act & Assert
      expect(() => user.setAge(invalidAge)).toThrow(ValidationError);
    });

    it('should throw ValidationError for non-integer age', () => {
      // Arrange
      const user = new User();
      const invalidAge = 25.5;

      // Act & Assert
      expect(() => user.setAge(invalidAge)).toThrow(ValidationError);
    });
  });
});
```

#### 第 2 步：运行测试并确认失败

```
> 请运行测试，确认它们失败。
不要编写任何实现代码。
```

**Claude 的响应**:

```
运行测试...

npm test -- User.test.ts

 FAIL  src/models/__tests__/User.test.ts
  User.age validation
    valid ages
      ✕ should accept age 18
      ✕ should accept age 120
      ✕ should accept age between 18 and 120
    invalid ages
      ✕ should throw ValidationError for age < 18
      ✕ should throw ValidationError for age > 120
      ✕ should throw ValidationError for non-integer age

测试失败，因为 setAge 方法还不存在。
这符合 TDD 的 Red 阶段 ✓
```

#### 第 3 步：提交测试

```
> 测试确认失败。请提交这个测试文件。
```

**Claude 的响应**:

```
创建提交...

```
test: add user age validation tests (TDD - Red phase)

- Add comprehensive test suite for age validation
- Test valid ages: 18, 120, and between range
- Test invalid ages: below 18, above 120, non-integer
- Tests currently failing (expected)
```

✓ 提交成功
```

#### 第 4 步：编写实现代码

```
> 现在请编写实现代码让测试通过。
不要修改测试，只实现功能。
持续迭代直到所有测试通过。
```

**Claude 的响应**:

```typescript
// src/models/User.ts

import { ValidationError } from './errors';

export class User {
  private _age: number | null = null;

  get age(): number | null {
    return this._age;
  }

  setAge(value: number): void {
    // Validate integer
    if (!Number.isInteger(value)) {
      throw new ValidationError('Age must be an integer');
    }

    // Validate range
    if (value < 18 || value > 120) {
      throw new ValidationError('Age must be between 18 and 120');
    }

    this._age = value;
  }
}
```

```
让我运行测试...

npm test -- User.test.ts

 PASS  src/models/__tests__/User.test.ts
  User.age validation
    valid ages
      ✓ should accept age 18
      ✓ should accept age 120
      ✓ should accept age between 18 and 120
    invalid ages
      ✕ should throw ValidationError for age < 18
      ✕ should throw ValidationError for age > 120
      ✕ should throw ValidationError for non-integer age

还有 3 个测试失败。让我检查错误信息...

问题是错误消息不匹配。让我调整错误消息...
```

**Claude 迭代...**

```typescript
// src/models/errors.ts

export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}
```

```
再次运行测试...

npm test -- User.test.ts

 PASS  src/models/__tests__/User.test.ts
  User.age validation
    valid ages
      ✓ should accept age 18
      ✓ should accept age 120
      ✓ should accept age between 18 and 120
    invalid ages
      ✓ should throw ValidationError for age < 18
      ✓ should throw ValidationError for age > 120
      ✓ should throw ValidationError for non-integer age

所有测试通过！✓
```

#### 第 5 步：提交实现代码

```
> 所有测试通过！请提交实现代码。
```

**Claude 的响应**:

```
创建提交...

```
feat: implement user age validation (TDD - Green phase)

- Add setAge method with validation
- Validate age is integer between 18 and 120
- Throw ValidationError for invalid ages
- All tests passing

Closes [previous commit]
```

✓ 提交成功
```

---

## AAA 测试模式

### 什么是 AAA 模式？

**AAA** = **Arrange**（准备）→ **Act**（执行）→ **Assert**（断言）

这是编写清晰、可读测试的标准模式。

### AAA 模式结构

```typescript
describe('功能描述', () => {
  it('应该做什么', () => {
    // ========== Arrange ==========
    // 准备测试数据和条件

    // ========== Act ==========
    // 执行要测试的操作

    // ========== Assert ==========
    // 验证结果是否符合预期
  });
});
```

### AAA 示例对比

#### 不好的测试（没有 AAA 结构）

```typescript
it('works', () => {
  const user = new User();
  user.setAge(25);
  expect(user.age).toBe(25);
  // 看不出哪是 Arrage、Act、Assert
});
```

#### 好的测试（清晰的 AAA 结构）

```typescript
it('should set age when value is valid', () => {
  // Arrange
  const user = new User();
  const validAge = 25;

  // Act
  user.setAge(validAge);

  // Assert
  expect(user.age).toBe(validAge);
});
```

### AAA 最佳实践

1. **Arrange**: 准备所有必要的测试数据
2. **Act**: 只有一个操作或方法调用
3. **Assert**: 验证预期的结果

```typescript
// ❌ 不好的示例：多个 Act
it('should update user', () => {
  const user = new User();
  user.setName('Alice');  // Act 1
  user.setAge(25);        // Act 2
  expect(user.name).toBe('Alice');
  expect(user.age).toBe(25);
});

// ✅ 好的示例：单个 Act
it('should set user name', () => {
  const user = new User();
  const name = 'Alice';

  user.setName(name);  // 唯一的 Act

  expect(user.name).toBe(name);
});
```

---

## TDD 与 Claude Code 的高级技巧

### 技巧 1: 使用表格驱动测试

```
> 请为年龄验证编写表格驱动测试。

测试用例：
- 17 → 失败
- 18 → 成功
- 120 → 成功
- 121 → 失败
- 25.5 → 失败
```

**Claude 的响应**:

```typescript
describe('User.age validation (table-driven)', () => {
  const testCases = [
    { age: 17, shouldPass: false, description: 'below minimum' },
    { age: 18, shouldPass: true, description: 'minimum age' },
    { age: 120, shouldPass: true, description: 'maximum age' },
    { age: 121, shouldPass: false, description: 'above maximum' },
    { age: 25.5, shouldPass: false, description: 'non-integer' },
  ];

  testCases.forEach(({ age, shouldPass, description }) => {
    it(`should ${shouldPass ? 'accept' : 'reject'} age ${age} (${description})`, () => {
      // Arrange
      const user = new User();

      // Act & Assert
      if (shouldPass) {
        expect(() => user.setAge(age)).not.toThrow();
        expect(user.age).toBe(age);
      } else {
        expect(() => user.setAge(age)).toThrow(ValidationError);
      }
    });
  });
});
```

### 技巧 2: 使用子代理验证实现

```
> 请编写测试，然后使用子代理验证：
1. 测试是否覆盖所有边界情况
2. 测试是否有重复逻辑
3. 是否可以改进
```

**Claude 的响应**:

```
测试已创建。让我使用子代理验证...

[子代理分析]

子代理反馈：
✓ 测试覆盖了所有边界情况
✓ 没有重复逻辑
→ 建议：可以添加测试用例处理 null 输入

是否要添加这个测试用例？
```

### 技巧 3: 集成测试的 TDD

```
> 请使用 TDD 为用户注册 API 编写集成测试。

测试流程：
1. POST /api/users/register
2. 验证用户被创建
3. 验证返回正确的响应
4. 验证密码被哈希
```

**Claude 的响应**:

```typescript
describe('POST /api/users/register', () => {
  it('should register a new user successfully', async () => {
    // Arrange
    const userData = {
      email: 'test@example.com',
      password: 'SecurePass123',
      username: 'testuser',
    };

    // Act
    const response = await request(app)
      .post('/api/users/register')
      .send(userData);

    // Assert
    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty('userId');
    expect(response.body.email).toBe(userData.email);
    expect(response.body).not.toHaveProperty('password');

    // 验证用户被创建且密码被哈希
    const user = await User.findOne({ email: userData.email });
    expect(user).toBeTruthy();
    expect(user.passwordHash).not.toBe(userData.password);
  });
});
```

---

## 常见 TDD 错误和如何避免

### 错误 1: 先写实现再写测试

```
❌ "实现这个功能，然后写测试"

结果: 这不是 TDD，测试只是事后补充

✅ "先写测试描述期望的行为，然后实现"
```

### 错误 2: 测试不够具体

```
❌ "写一些用户验证的测试"

结果: Claude 不知道具体要验证什么

✅ "写测试验证：年龄必须是 18-120 的整数"
```

### 错误 3: 一次写太多测试

```
❌ "写完所有功能的测试"

结果: 测试和实现都变得复杂

✅ "先写一个功能的测试，实现后继续下一个"
```

### 错误 4: 在实现阶段修改测试

```
❌ "测试失败了，让我修改测试让它通过"

结果: 失去了 TDD 的价值

✅ "测试失败了，修改实现代码让它通过"
```

---

## TDD 工作流对比

### 传统工作流 vs TDD 工作流

```
┌─────────────────────────────────────────────────────────┐
│              传统工作流（不推荐）                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 编写实现代码                                        │
│  2. 编写测试（如果有时间）                               │
│  3. 发现测试失败                                        │
│  4. 修改代码或测试（随意）                               │
│                                                         │
│  问题：                                                 │
│  - 测试是事后思考                                       │
│  - 容易过度设计                                         │
│  - 测试可能覆盖不足                                     │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              TDD 工作流（推荐）                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 编写失败的测试（Red）                               │
│  2. 编写最少代码让测试通过（Green）                      │
│  3. 重构改进代码（Refactor）                            │
│                                                         │
│  优势：                                                 │
│  - 测试驱动设计                                         │
│  - 防止过度设计                                         │
│  - 100% 测试覆盖（至少对于新代码）                      │
│  - 更容易重构                                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 总结

### 关键要点

1. **TDD 与 Claude Code 完美配合**
   - 测试提供明确目标
   - Claude 可以迭代直到测试通过

2. **Anthropic 的 TDD 工作流**
   - 写测试 → 确认失败 → 提交测试
   - 写实现 → 迭代到通过 → 提交实现

3. **使用 AAA 模式**
   - Arrange（准备）
   - Act（执行）
   - Assert（断言）

4. **迭代是关键**
   - 不要期望一次完美
   - 让 Claude 持续运行测试并修复

### 下一步

在下一章中，我们将学习**多实例工作流**：
- 如何同时运行多个 Claude Code 实例
- "一个编写，一个审查"模式
- 使用 git worktrees 并行开发

---

## 进一步阅读

### 官方文档
- `docs/research/01-claude-code-best-practices-anthropic-official.md` - TDD 工作流部分

### 相关章节
- [Chapter 5 - 探索/计划/编码/提交](chapter-05-explore-plan-code-commit.md)
- [Chapter 7 - 多实例工作流](chapter-07-multi-instance.md) - 下一章

### 测试资源
- `docs/research/00-research-summary.md` - AAA 模式部分

---

## 练习

完成以下练习：

1. **基本练习**
   - [ ] 为一个简单函数编写 TDD 测试
   - [ ] 让 Claude 先写测试，再写实现
   - [ ] 验证 AAA 模式的使用

2. **进阶练习**
   - [ ] 使用表格驱动测试
   - [ ] 编写集成测试的 TDD
   - [ ] 使用子代理验证测试质量

3. **实战练习**
   - [ ] 选择一个真实功能
   - [ ] 完整执行 TDD 循环
   - [ ] 对比传统开发方式的差异

---

**上一章**: [Chapter 5 - 探索/计划/编码/提交](chapter-05-explore-plan-code-commit.md)
**下一章**: [Chapter 7 - 多实例工作流](chapter-07-multi-instance.md)
