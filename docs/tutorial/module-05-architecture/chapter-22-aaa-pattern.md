# Chapter 22: AAA 模式与测试最佳实践

## 学习目标

完成本章后，你将能够：

- 理解 AAA (Arrange-Act-Assert) 模式
- 编写清晰、易读的单元测试
- 应用测试命名最佳实践
- 使用 Claude Code 辅助编写测试
- 避免常见的测试反模式

## 前置知识

- [Chapter 21: 可测试性与 Mocking](chapter-21-testability-mocking.md)
- 基本的单元测试框架知识 (Mocha, Jest, 等)

---

## 22.1 AAA 模式概述

### 22.1.1 什么是 AAA 模式

**AAA 模式** (Arrange-Act-Assert) 是一种组织单元测试的模式，将测试分为三个清晰的阶段：

```
┌─────────────────────────────────────────────────────────────┐
│                    AAA 测试结构                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Arrange (准备) - 设置测试场景                       │   │
│  │  - 创建对象                                          │   │
│  │  - 设置 Mock/Stubs                                   │   │
│  │  - 准备数据                                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ↓                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Act (执行) - 执行被测试的行为                       │   │
│  │  - 调用被测试的方法                                  │   │
│  │  - 触发事件                                          │   │
│  │  - 执行操作                                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ↓                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Assert (断言) - 验证结果                           │   │
│  │  - 检查返回值                                        │   │
│  │  - 验证状态变化                                      │   │
│  │  - 确认副作用                                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 22.1.2 AAA 模式示例

```typescript
/**
 * AAA 模式示例：用户注册测试
 */

import { assert } from 'chai';
import { UserService } from './UserService';
import { InMemoryUserRepository } from './InMemoryUserRepository';

suite('UserService - AAA Pattern', () => {
  test('should register new user successfully', async () => {
    // ==================== Arrange ====================
    // 准备测试环境和数据
    const fakeRepo = new InMemoryUserRepository();
    const userService = new UserService(fakeRepo);
    const userData = {
      email: 'user@example.com',
      password: 'SecurePass123',
      name: 'John Doe'
    };

    // ==================== Act ====================
    // 执行被测试的行为
    const userId = await userService.registerUser(
      userData.email,
      userData.password,
      userData.name
    );

    // ==================== Assert ====================
    // 验证结果
    assert.isDefined(userId);
    assert.equal(await fakeRepo.count(), 1);

    const savedUser = await fakeRepo.findByEmail(userData.email);
    assert.isDefined(savedUser);
    assert.equal(savedUser!.email, userData.email);
    assert.equal(savedUser!.name, userData.name);
  });

  test('should reject duplicate email', async () => {
    // ==================== Arrange ====================
    const fakeRepo = new InMemoryUserRepository();
    const userService = new UserService(fakeRepo);
    const email = 'user@example.com';

    // 预先注册一个用户
    await userService.registerUser(email, 'pass123', 'User 1');

    // ==================== Act ====================
    // 尝试使用相同邮箱注册
    const promise = userService.registerUser(email, 'pass456', 'User 2');

    // ==================== Assert ====================
    // 应该抛出错误
    await assert.isRejected(promise, 'Email already registered');

    // 验证只有一个用户
    assert.equal(await fakeRepo.count(), 1);
  });

  test('should validate email format', async () => {
    // ==================== Arrange ====================
    const fakeRepo = new InMemoryUserRepository();
    const userService = new UserService(fakeRepo);

    // ==================== Act & Assert ====================
    // 对于简单的验证，可以合并 Act 和 Assert
    await assert.isRejected(
      userService.registerUser('invalid-email', 'pass123', 'User'),
      'Invalid email format'
    );
  });
});
```

---

## 22.2 测试命名最佳实践

### 22.2.1 命名模式

好的测试名称应该：
1. **描述性** - 清楚说明测试的内容
2. **以用户/业务为中心** - 关注行为，而非实现
3. **一致的格式** - 使用统一的命名约定

```typescript
/**
 * ✅ 好的测试命名
 */

// 模式 1: Should_ExpectedBehavior_When_StateUnderTest
suite('UserService', () => {
  test('should_return_user_when_found_by_id', async () => {
    // ...
  });

  test('should_throw_error_when_user_not_found', async () => {
    // ...
  });

  test('should_create_user_when_valid_data_provided', async () => {
    // ...
  });
});

// 模式 2: MethodUnderTest_ExpectedBehavior_StateUnderTest
suite('OrderService', () => {
  test('createOrder_returnsOrderId_whenPaymentSuccessful', async () => {
    // ...
  });

  test('createOrder_throwsError_whenPaymentFails', async () => {
    // ...
  });
});

// 模式 3: Given_StateUnderTest_Expect_ExpectedBehavior
suite('PaymentGateway', () => {
  test('given_valid_payment_expect_success', async () => {
    // ...
  });

  test('given_insufficient_funds_expect_declined', async () => {
    // ...
  });
});

/**
 * ❌ 差的测试命名
 */

suite('UserService', () => {
  test('test1', async () => {
    // ❌ 没有描述性
  });

  test('should_work', async () => {
    // ❌ 太模糊
  });

  test('databaseReturnsTrueThenUserIsNotNull', async () => {
    // ❌ 关注实现细节，而非行为
  });

  test('checkUserRegistration', async () => {
    // ❌ "check" 不清楚期望什么
  });
});
```

### 22.2.2 命名示例对比

```typescript
/**
 * 场景：测试用户登录功能
 */

// ❌ 差的命名
test('login', async () => {});
test('testLogin', async () => {});
test('loginTest', async () => {});
test('checkLoginWorks', async () => {});

// ✅ 好的命名
test('should_authenticate_user_when_credentials_correct', async () => {});
test('should_return_token_when_login_successful', async () => {});
test('should_throw_error_when_credentials_invalid', async () => {});
test('should_lock_account_after_multiple_failed_attempts', async () => {});
```

---

## 22.3 测试组织结构

### 22.3.1 测试文件组织

```typescript
/**
 * 推荐的测试文件结构
 */

/**
 * 测试文件命名：*.test.ts
 *
 * 文件结构：
 * src/
 *   services/
 *     UserService.ts
 *     UserService.test.ts  ← 测试文件与源文件同名
 *     OrderService.ts
 *     OrderService.test.ts
 *
 * 或：
 * tests/
 *   unit/
 *     services/
 *       UserService.test.ts
 *       OrderService.test.ts
 *   integration/
 *     api/
 *       userApi.test.ts
 */

/**
 * 测试文件内容组织
 */

// ========================================
// 1. Imports
// ========================================
import { assert } from 'chai';
import { UserService } from '../src/services/UserService';
import { InMemoryUserRepository } from '../src/repositories/InMemoryUserRepository';
import { MockEmailService } from '../src/mocks/MockEmailService';

// ========================================
// 2. Test Suite Definition
// ========================================
suite('UserService', () => {

  // ========================================
  // 3. Setup/Teardown
  // ========================================
  let userService: UserService;
  let fakeRepo: InMemoryUserRepository;
  let mockEmailer: MockEmailService;

  setup(() => {
    // 每个测试前执行
    fakeRepo = new InMemoryUserRepository();
    mockEmailer = new MockEmailService();
    userService = new UserService(fakeRepo, mockEmailer);
  });

  teardown(() => {
    // 每个测试后执行
    fakeRepo.clear();
    mockEmailer.reset();
  });

  suiteSetup(() => {
    // 整个 suite 前执行一次
  });

  suiteTeardown(() => {
    // 整个 suite 后执行一次
  });

  // ========================================
  // 4. Test Groups (Nested Suites)
  // ========================================

  suite('registerUser', () => {

    suite('when email is valid', () => {

      test('should create user successfully', async () => {
        // Arrange
        const email = 'user@example.com';
        const password = 'SecurePass123';

        // Act
        const userId = await userService.registerUser(email, password);

        // Assert
        assert.isDefined(userId);
        assert.equal(await fakeRepo.count(), 1);
      });

      test('should send welcome email', async () => {
        // Arrange
        const email = 'user@example.com';

        // Act
        await userService.registerUser(email, 'pass');

        // Assert
        assert.isTrue(mockEmailer.wasCalled);
        assert.equal(mockEmailer.lastRecipient, email);
      });
    });

    suite('when email is invalid', () => {

      test('should throw validation error', async () => {
        // Arrange
        const invalidEmail = 'not-an-email';

        // Act & Assert
        await assert.isRejected(
          userService.registerUser(invalidEmail, 'pass'),
          'Invalid email format'
        );
      });

      test('should not create user', async () => {
        // Arrange
        const invalidEmail = 'not-an-email';

        // Act
        try {
          await userService.registerUser(invalidEmail, 'pass');
        } catch (e) {
          // Expected error
        }

        // Assert
        assert.equal(await fakeRepo.count(), 0);
      });
    });

    suite('when email already exists', () => {

      test('should throw duplicate error', async () => {
        // Arrange
        const email = 'user@example.com';
        await userService.registerUser(email, 'pass1');

        // Act & Assert
        await assert.isRejected(
          userService.registerUser(email, 'pass2'),
          'Email already registered'
        );
      });
    });
  });

  suite('authenticateUser', () => {
    // 测试用户认证
  });

  suite('updateProfile', () => {
    // 测试更新配置文件
  });
});
```

### 22.3.2 测试数据管理

```typescript
/**
 * 测试数据组织
 */

/**
 * 方式 1: 测试构建器 (Test Builder)
 */
class UserTestDataBuilder {
  private email = 'test@example.com';
  private password = 'TestPass123';
  private name = 'Test User';
  private age = 25;

  withEmail(email: string): UserTestDataBuilder {
    this.email = email;
    return this;
  }

  withPassword(password: string): UserTestDataBuilder {
    this.password = password;
    return this;
  }

  withName(name: string): UserTestDataBuilder {
    this.name = name;
    return this;
  }

  withAge(age: number): UserTestDataBuilder {
    this.age = age;
    return this;
  }

  build(): RegisterUserData {
    return {
      email: this.email,
      password: this.password,
      name: this.name,
      age: this.age
    };
  }
}

// 使用 Builder
test('should register user with custom data', async () => {
  // Arrange
  const userData = new UserTestDataBuilder()
    .withEmail('custom@example.com')
    .withName('Custom User')
    .withAge(30)
    .build();

  // Act
  const userId = await userService.registerUser(userData);

  // Assert
  const user = await fakeRepo.findById(userId);
  assert.equal(user!.email, 'custom@example.com');
});

/**
 * 方式 2: 测试数据常量
 */
const TEST_DATA = {
  VALID_USER: {
    email: 'valid@example.com',
    password: 'ValidPass123',
    name: 'Valid User'
  },
  INVALID_EMAIL: 'not-an-email',
  WEAK_PASSWORD: '123',
  DUPLICATE_EMAIL: 'duplicate@example.com'
};

/**
 * 方式 3: 测试 Fixture
 */
class UserTestFixture {
  readonly userService: UserService;
  readonly fakeRepo: InMemoryUserRepository;
  readonly mockEmailer: MockEmailService;

  constructor() {
    this.fakeRepo = new InMemoryUserRepository();
    this.mockEmailer = new MockEmailService();
    this.userService = new UserService(this.fakeRepo, this.mockEmailer);
  }

  async createRegisteredUser(
    email?: string,
    password?: string
  ): Promise<string> {
    return await this.userService.registerUser(
      email || TEST_DATA.VALID_USER.email,
      password || TEST_DATA.VALID_USER.password
    );
  }
}

// 使用 Fixture
suite('UserService with Fixture', () => {
  let fixture: UserTestFixture;

  setup(() => {
    fixture = new UserTestFixture();
  });

  test('should authenticate registered user', async () => {
    // Arrange
    const userId = await fixture.createRegisteredUser();

    // Act
    const result = await fixture.userService.authenticateUser(
      TEST_DATA.VALID_USER.email,
      TEST_DATA.VALID_USER.password
    );

    // Assert
    assert.isTrue(result.success);
    assert.equal(result.userId, userId);
  });
});
```

---

## 22.4 测试覆盖的场景

### 22.4.1 测试金字塔

```
                    ┌──────────────┐
                    │    E2E       │  ← 少量端到端测试
                    │    Tests     │     (UI/集成)
                    │   (10%)      │
                    └──────▲───────┘
                           │
              ┌────────────┴────────────┐
              │     Integration         │  ← 中量集成测试
              │       Tests            │    (API/DB)
              │       (20%)            │
              └────────────▲────────────┘
                           │
       ┌───────────────────┴───────────────────┐
       │          Unit Tests                  │  ← 大量单元测试
       │          (70%)                       │    (业务逻辑)
       └──────────────────────────────────────┘
```

### 22.4.2 单元测试应该覆盖的场景

```typescript
/**
 * 单元测试覆盖清单
 */

suite('OrderService - Complete Coverage', () => {

  // ========================================
  // 1. 快乐路径 (Happy Path)
  // ========================================
  suite('happy path', () => {
    test('should_create_order_when_payment_successful', async () => {
      // 最常见的成功场景
    });

    test('should_return_order_id_when_created', async () => {
      // 验证返回值正确
    });
  });

  // ========================================
  // 2. 边界条件 (Boundary Conditions)
  // ========================================
  suite('boundary conditions', () => {
    test('should_handle_empty_order_items', async () => {
      // 空集合
    });

    test('should_handle_single_item', async () => {
      // 单个元素
    });

    test('should_handle_maximum_items', async () => {
      // 最大限制
    });

    test('should_handle_zero_total', async () => {
      // 零值
    });

    test('should_handle_very_large_total', async () => {
      // 大数值
    });
  });

  // ========================================
  // 3. 错误情况 (Error Cases)
  // ========================================
  suite('error cases', () => {
    test('should_throw_when_payment_fails', async () => {
      // 外部依赖失败
    });

    test('should_throw_when_inventory_insufficient', async () => {
      // 业务规则违反
    });

    test('should_throw_when_data_invalid', async () => {
      // 输入验证失败
    });

    test('should_throw_when_user_unauthorized', async () => {
      // 权限问题
    });
  });

  // ========================================
  // 4. 边缘情况 (Edge Cases)
  // ========================================
  suite('edge cases', () => {
    test('should_handle_null_values', async () => {
      // null 处理
    });

    test('should_handle_undefined_values', async () => {
      // undefined 处理
    });

    test('should_handle_special_characters', async () => {
      // 特殊字符
    });

    test('should_handle_unicode_characters', async () => {
      // Unicode
    });
  });

  // ========================================
  // 5. 并发和性能 (Concurrency & Performance)
  // ========================================
  suite('concurrency', () => {
    test('should_handle_concurrent_requests', async () => {
      // 并发场景
    });

    test('should_prevent_duplicate_orders', async () => {
      // 幂等性
    });
  });

  // ========================================
  // 6. 状态变化 (State Changes)
  // ========================================
  suite('state changes', () => {
    test('should_update_inventory_after_order', async () => {
      // 副作用验证
    });

    test('should_track_order_status_changes', async () => {
      // 状态转换
    });
  });
});
```

---

## 22.5 使用 Claude Code 编写测试

### 22.5.1 让 Claude Code 生成 AAA 测试

```bash
# 激活 Plan Mode
Shift+Tab (两次)

# 任务描述：
为 PaymentService 的 processPayment 方法编写完整的单元测试

# Claude 会：
1. 分析 PaymentService 的依赖
2. 识别所有需要测试的场景
3. 使用 AAA 模式组织测试
4. 创建适当的 Mock 对象
5. 生成测试代码
```

### 22.5.2 让 Claude Code 检查测试覆盖率

```bash
# 任务：
检查 UserService.test.ts 的测试覆盖率

# Claude 会：
1. 分析 UserService 的所有方法
2. 识别未测试的代码路径
3. 建议需要添加的测试用例
```

### 22.5.3 让 Claude Code 重构测试

```bash
# 任务：
重构这个测试，使其更清晰

# Claude 会：
1. 识别测试中的问题
2. 提取重复的 setup 代码
3. 改进测试命名
4. 应用 AAA 模式
```

---

## 22.6 常见反模式

### 22.1.1 反模式 1：测试中的条件逻辑

```typescript
// ❌ 反模式：测试中有条件逻辑
test('bad test with conditional logic', async () => {
  const result = await service.process(data);

  if (result.type === 'success') {
    assert.equal(result.code, 200);
  } else if (result.type === 'error') {
    assert.equal(result.code, 400);
  }
  // 问题：一个测试验证多个场景
});

// ✅ 正确：每个场景一个测试
test('should_return_200_when_success', async () => {
  const result = await service.process(successData);
  assert.equal(result.code, 200);
});

test('should_return_400_when_error', async () => {
  const result = await service.process(errorData);
  assert.equal(result.code, 400);
});
```

### 22.6.2 反模式 2：测试中的循环

```typescript
// ❌ 反模式：测试中有循环
test('bad test with loop', async () => {
  const inputs = [1, 2, 3, 4, 5];

  for (const input of inputs) {
    const result = service.calculate(input);
    assert.isTrue(result > 0);
  }
  // 问题：不知道哪个输入失败了
});

// ✅ 正确：使用参数化测试或单独测试
test('should_return_positive_for_input_1', () => {
  assert.isTrue(service.calculate(1) > 0);
});

test('should_return_positive_for_input_2', () => {
  assert.isTrue(service.calculate(2) > 0);
});

// 或使用参数化测试（如果框架支持）
const inputs = [1, 2, 3, 4, 5];
inputs.forEach(input => {
  test(`should_return_positive_for_input_${input}`, () => {
    assert.isTrue(service.calculate(input) > 0);
  });
});
```

### 22.6.3 反模式 3：共享可变状态

```typescript
// ❌ 反模式：共享可变状态
let sharedCounter = 0;

test('test 1', () => {
  sharedCounter++;
  assert.equal(sharedCounter, 1);
});

test('test 2', () => {
  sharedCounter++;
  assert.equal(sharedCounter, 2); // 如果 test 1 失败，这个也会失败
});

// ✅ 正确：每个测试独立
suite('independent tests', () => {
  test('test 1', () => {
    const counter = 0;
    counter++;
    assert.equal(counter, 1);
  });

  test('test 2', () => {
    const counter = 0;
    counter++;
    assert.equal(counter, 1); // 独立于 test 1
  });
});
```

### 22.6.4 反模式 4：测试实现细节

```typescript
// ❌ 反模式：测试实现细节
test('bad test - testing implementation', async () => {
  const spy = sinon.spy(service, 'internalMethod');
  await service.publicMethod();

  assert.isTrue(spy.calledOnce); // 测试私有方法调用
});

// ✅ 正确：测试公共行为
test('good test - testing behavior', async () => {
  const result = await service.publicMethod();

  assert.equal(result.status, 'success'); // 测试可见结果
});
```

---

## 22.7 mybatis-boost 中的 AAA 测试示例

```typescript
/**
 * mybatis-boost 的测试实践
 */

import { assert } from 'chai';
import { FileMapper } from '../src/FileMapper';
import { MockFileSystem } from '../mocks/MockFileSystem';
import { MockParser } from '../mocks/MockParser';
import { MockCache } from '../mocks/MockCache';

suite('FileMapper - AAA Pattern', () => {

  let fileMapper: FileMapper;
  let mockFileSystem: MockFileSystem;
  let mockParser: MockParser;
  let mockCache: MockCache;

  setup(() => {
    mockFileSystem = new MockFileSystem();
    mockParser = new MockParser();
    mockCache = new MockCache();
    fileMapper = new FileMapper(mockFileSystem, mockParser, mockCache);
  });

  suite('findXmlForJava', () => {

    suite('when cache hit', () => {
      test('should_return_cached_result', async () => {
        // ==================== Arrange ====================
        const javaFile = '/src/UserMapper.java';
        const cachedResults = [
          { source: javaFile, target: '/src/UserMapper.xml', line: 1 }
        ];

        mockCache.set(javaFile, cachedResults);

        // ==================== Act ====================
        const results = await fileMapper.findXmlForJava(javaFile);

        // ==================== Assert ====================
        assert.equal(results.length, 1);
        assert.equal(results[0].target, '/src/UserMapper.xml');

        // 验证没有读取文件或调用解析器
        assert.isFalse(mockFileSystem.readFileCalled);
        assert.isFalse(mockParser.parseJavaCalled);
      });
    });

    suite('when cache miss', () => {
      test('should_parse_and_find_xml', async () => {
        // ==================== Arrange ====================
        const javaFile = '/src/UserMapper.java';
        const xmlFile = '/src/UserMapper.xml';

        mockFileSystem.addFile(javaFile, 'public class UserMapper {}');
        mockParser.setParseResult('UserMapper');
        mockFileSystem.addMatch(xmlFile);

        mockCache.set(javaFile, null); // 缓存未命中

        // ==================== Act ====================
        const results = await fileMapper.findXmlForJava(javaFile);

        // ==================== Assert ====================
        assert.equal(results.length, 1);
        assert.equal(results[0].source, javaFile);
        assert.equal(results[0].target, xmlFile);
        assert.equal(results[0].line, 1);

        // 验证文件被读取
        assert.isTrue(mockFileSystem.readFileCalled);

        // 验证解析器被调用
        assert.isTrue(mockParser.parseJavaCalled);

        // 验证结果被缓存
        const cached = await mockCache.get(javaFile);
        assert.isDefined(cached);
        assert.equal(cached!.length, 1);
      });

      test('should_return_empty_when_no_xml_found', async () => {
        // ==================== Arrange ====================
        const javaFile = '/src/OrphanMapper.java';

        mockFileSystem.addFile(javaFile, 'public class OrphanMapper {}');
        mockParser.setParseResult('OrphanMapper');
        mockFileSystem.addMatch(''); // 没有匹配的 XML

        // ==================== Act ====================
        const results = await fileMapper.findXmlForJava(javaFile);

        // ==================== Assert ====================
        assert.equal(results.length, 0);
      });
    });

    suite('when parsing fails', () => {
      test('should_handle_parse_error_gracefully', async () => {
        // ==================== Arrange ====================
        const javaFile = '/src/InvalidMapper.java';

        mockFileSystem.addFile(javaFile, 'invalid java code');
        mockParser.setParseError('Parse error: invalid syntax');

        // ==================== Act ====================
        const results = await fileMapper.findXmlForJava(javaFile);

        // ==================== Assert ====================
        // 根据实际需求，可能返回空数组或抛出错误
        assert.equal(results.length, 0);
      });
    });
  });

  suite('performance', () => {
    test('should_complete_within_time_limit', async () => {
      // ==================== Arrange ====================
      const javaFile = '/src/UserMapper.java';

      mockFileSystem.addFile(javaFile, 'public class UserMapper {}');
      mockParser.setParseResult('UserMapper');
      mockFileSystem.addMatch('/src/UserMapper.xml');

      const startTime = Date.now();

      // ==================== Act ====================
      await fileMapper.findXmlForJava(javaFile);

      // ==================== Assert ====================
      const duration = Date.now() - startTime;
      assert.isBelow(duration, 100); // 应该在 100ms 内完成
    });
  });
});
```

---

## 22.8 练习

### 练习 1：重构测试为 AAA 模式

将以下测试重构为 AAA 模式：

```typescript
test('user login', async () => {
  const service = new LoginService();
  await service.register('user@example.com', 'pass123');
  const result = await service.login('user@example.com', 'pass123');
  assert.equal(result.token, 'expected-token');
  assert.equal(result.user.email, 'user@example.com');
});
```

### 练习 2：改进测试命名

改进以下测试的命名：

```typescript
test('test1', () => {});
test('check', () => {});
test('works', () => {});
test('database', () => {});
```

### 练习 3：编写完整的测试套件

为以下 `OrderService` 编写完整的测试套件：

```typescript
export class OrderService {
  constructor(
    private inventory: IInventory,
    private payment: IPaymentGateway
  ) {}

  async createOrder(order: OrderData): Promise<OrderResult> {
    if (!order.items || order.items.length === 0) {
      throw new Error('Order must have at least one item');
    }

    for (const item of order.items) {
      const available = await this.inventory.checkStock(
        item.productId,
        item.quantity
      );

      if (!available) {
        throw new Error(`Insufficient stock for ${item.productId}`);
      }
    }

    const total = order.items.reduce((sum, item) => sum + item.price * item.quantity, 0);

    const paymentResult = await this.payment.charge(total);

    if (!paymentResult.success) {
      throw new Error('Payment failed');
    }

    for (const item of order.items) {
      await this.inventory.reduceStock(item.productId, item.quantity);
    }

    return {
      orderId: this.generateOrderId(),
      total: total,
      status: 'confirmed'
    };
  }

  private generateOrderId(): string {
    return 'ORD-' + Math.random().toString(36).substring(7);
  }
}
```

**提示**：覆盖以下场景：
- 快乐路径
- 空订单
- 库存不足
- 支付失败
- 多个商品

---

## 22.9 进一步阅读

- [AAA Pattern by William C. Wake](https://billwakeling.wordpress.com/2011/08/17/aaa-test-pattern/)
- [Unit Testing Best Practices by Martin Fowler](https://martinfowler.com/bliki/UnitTest.html)
- [Chapter 23: LLM 真实工作原理](../module-06-llm-limitations/chapter-23-how-llms-work.md) - 下一章

---

## 视频脚本

### Episode 22: AAA 模式与测试最佳实践 (14 分钟)

#### [0:00-1:00] 引入
**视觉元素**：
- 标题："AAA：让测试清晰易读"
- 代码对比：混乱的测试 vs AAA 测试

**内容**：
> 什么是好的测试？不是覆盖率高的测试，而是**清晰、易读、易维护**的测试。AAA 模式——Arrange、Act、Assert——是编写清晰测试的金标准。今天我们学习如何应用 AAA 模式和测试最佳实践。

#### [1:00-3:00] AAA 模式
**视觉元素**：
- AAA 三阶段图解
- 每阶段的代码示例

**内容**：
> AAA 模式将测试分为三个阶段：
> - **Arrange (准备)**: 设置测试环境、创建对象、准备数据
> - **Act (执行)**: 调用被测试的方法
> - **Assert (断言)**: 验证结果
>
> [演示：AAA 模式代码]
>
> 看到这三个清晰的区块了吗？任何人都能立即理解测试在做什么！

#### [3:00-6:00] 测试命名
**视觉元素**：
- 好的命名 vs 差的命名对比
- 命名模式列表

**内容**：
> 好的测试名称应该像一个故事：
> - ✅ "should_authenticate_user_when_credentials_valid"
> - ❌ "test1" 或 "checkLogin"
>
> 推荐的命名模式：
> - "should_ExpectedBehavior_When_StateUnderTest"
> - "MethodUnderTest_ExpectedBehavior_StateUnderTest"
>
> [演示：重构测试命名]

#### [6:00-10:00] 测试组织
**视觉元素**：
- 测试文件结构
- Nested Suites 示例

**内容**：
> 好的测试组织让测试套件易于维护：
>
> [演示：测试文件组织]
>
> 使用嵌套 suite 组织相关测试：
> - 顶层 suite: 类名
> - 二层 suite: 方法名
> - 三层 suite: 场景描述
>
> 这样每个测试的完整路径就是一个清晰的故事描述！

#### [10:00-12:00] 覆盖场景
**视觉元素**：
- 测试金字塔
- 测试清单

**内容**：
> 完整的测试应该覆盖：
> - 快乐路径（成功场景）
> - 边界条件（空值、最大值）
> - 错误情况（失败场景）
> - 边缘情况（特殊字符）
> - 并发场景
>
> 记住：70% 单元测试，20% 集成测试，10% E2E 测试。

#### [12:00-14:00] 总结
**视觉元素**：
- AAA 模式总结
- Module 5 总结
- Module 6 预告

**内容**：
> AAA 模式和测试最佳实践：
> - 三个阶段：Arrange、Act、Assert
> - 描述性命名
> - 清晰的组织结构
> - 覆盖关键场景
>
> **Module 5 总结**：
> 我们学习了四种架构模式：
> - 整洁架构：依赖规则
> - 洋葱架构：Domain 层次
> - 六边形架构：Ports 和 Adapters
> - 可测试性：测试替身和 AAA 模式
>
> 下一章，我们将进入 Module 6，理解 LLM 的真实工作原理和局限性。
