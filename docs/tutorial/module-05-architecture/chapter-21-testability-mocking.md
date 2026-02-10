# Chapter 21: 可测试性与 Mocking

## 学习目标

完成本章后，你将能够：

- 理解什么是可测试代码和不可测试代码
- 掌握 Mock、Stub、Spy 等测试替身技术
- 使用依赖注入提高代码可测试性
- 使用 Claude Code 编写可测试的代码
- 在测试中正确使用 Mocking

## 前置知识

- [Chapter 19: 整洁架构原则](chapter-19-clean-architecture.md)
- [Chapter 20: 洋葱架构与六边形架构](chapter-20-onion-hexagonal.md)
- 基本的单元测试概念

---

## 21.1 什么是可测试性

### 21.1.1 可测试代码 vs 不可测试代码

```typescript
/**
 * ❌ 不可测试的代码
 */

/**
 * 问题 1: 硬编码依赖
 */
export class UserService {
  // ❌ 直接创建依赖，无法替换
  private db = new PostgreSQLDatabase(); // ❌ 无法 mock
  private emailer = new SendGridEmailer(); // ❌ 无法 mock

  async registerUser(data: any): Promise<void> {
    // 验证
    if (this.isValidEmail(data.email)) {
      // 保存到数据库
      await this.db.query('INSERT INTO users...'); // ❌ 直接调用

      // 发送邮件
      await this.emailer.send(data.email); // ❌ 直接调用
    }
  }

  private isValidEmail(email: string): boolean {
    // 业务逻辑混在技术细节中
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }
}

/**
 * 问题 2: 全局状态
 */
export class OrderService {
  // ❌ 依赖全局变量，测试间会互相影响
  async createOrder(order: any): Promise<void> {
    global.currentUser; // ❌ 无法控制
    global.databaseConnection; // ❌ 无法替换
  }
}

/**
 * 问题 3: 静态方法调用
 */
export class PaymentService {
  async processPayment(amount: number): Promise<void> {
    // ❌ 静态方法无法 mock
    const result = await ExternalPaymentAPI.charge(amount); // ❌ 无法测试
  }
}
```

```typescript
/**
 * ✅ 可测试的代码
 */

/**
 * 解决方案 1: 依赖注入
 */
export interface IDatabase {
  query(sql: string, params?: any[]): Promise<any>;
}

export interface IEmailer {
  send(to: string, subject: string, body: string): Promise<void>;
}

/**
 * ✅ 可测试的 UserService
 */
export class UserService {
  // ✅ 通过构造函数注入依赖
  constructor(
    private db: IDatabase,
    private emailer: IEmailer
  ) {}

  async registerUser(data: RegisterUserData): Promise<void> {
    // ✅ 业务逻辑独立
    if (!this.isValidEmail(data.email)) {
      throw new Error('Invalid email');
    }

    // ✅ 通过接口调用，可以 mock
    await this.db.query(
      'INSERT INTO users (email, name) VALUES ($1, $2)',
      [data.email, data.name]
    );

    await this.emailer.send(
      data.email,
      'Welcome!',
      'Thank you for registering.'
    );
  }

  private isValidEmail(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }
}

export interface RegisterUserData {
  email: string;
  name: string;
}

/**
 * 解决方案 2: 避免全局状态
 */
export interface ICurrentUserProvider {
  getCurrentUser(): User | null;
}

export class OrderService {
  // ✅ 注入依赖，而非使用全局状态
  constructor(
    private currentUserProvider: ICurrentUserProvider,
    private db: IDatabase
  ) {}

  async createOrder(order: any): Promise<void> {
    // ✅ 通过 provider 获取当前用户
    const user = this.currentUserProvider.getCurrentUser();

    if (!user) {
      throw new Error('User not authenticated');
    }

    await this.db.query(
      'INSERT INTO orders (user_id, data) VALUES ($1, $2)',
      [user.id, order]
    );
  }
}

export interface User {
  id: string;
  email: string;
}

/**
 * 解决方案 3: 包装外部 API
 */
export interface IPaymentGateway {
  charge(amount: number): Promise<PaymentResult>;
}

export interface PaymentResult {
  success: boolean;
  transactionId?: string;
  error?: string;
}

/**
 * ✅ 包装外部 API，使用接口抽象
 */
export class ExternalPaymentAdapter implements IPaymentGateway {
  async charge(amount: number): Promise<PaymentResult> {
    // 调用实际的 ExternalPaymentAPI
    const result = await ExternalPaymentAPI.charge(amount);
    return {
      success: result.status === 'success',
      transactionId: result.transactionId
    };
  }
}

export class PaymentService {
  constructor(private gateway: IPaymentGateway) {}

  async processPayment(amount: number): Promise<void> {
    // ✅ 通过接口调用，可以 mock
    const result = await this.gateway.charge(amount);

    if (!result.success) {
      throw new Error(result.error || 'Payment failed');
    }
  }
}
```

### 21.1.2 可测试性特征

| 特征 | 不可测试代码 | 可测试代码 |
|------|-------------|-----------|
| **依赖创建** | 内部创建 (`new`) | 注入依赖 |
| **全局状态** | 使用全局变量 | 通过参数/注入 |
| **静态调用** | 直接调用静态方法 | 通过接口 |
| **职责单一** | 多个职责混合 | 职责分离 |
| **副作用隔离** | I/O 混在逻辑中 | I/O 通过接口 |

---

## 21.2 测试替身 (Test Doubles)

### 21.2.1 五种测试替身

Gerard Meszaros 定义了五种测试替身：

```
┌─────────────────────────────────────────────────────────────┐
│                    Test Doubles 分类                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Dummy (哑元)        - 传递但不使用                        │
│  2. Stub (桩)          - 返回预设值                          │
│  3. Spy (间谍)         - 记录调用信息                        │
│  4. Mock (模拟)        - 预期行为验证                        │
│  5. Fake (伪造)        - 简化实现                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 21.2.2 Dummy (哑元)

```typescript
/**
 * Dummy: 只是为了满足参数要求，实际不会被使用
 */

/**
 * 示例：测试 OrderService
 */
export class OrderService {
  constructor(
    private db: IDatabase,
    private logger: ILogger  // 只在错误时使用
  ) {}

  async createOrder(order: any): Promise<void> {
    // logger 只在错误时使用，正常情况下不调用
    await this.db.query('INSERT INTO orders...');
  }
}

export interface ILogger {
  log(message: string): void;
}

/**
 * 测试：使用 Dummy Logger
 */
import { assert } from 'chai';

suite('OrderService', () => {
  test('should create order', async () => {
    // Arrange
    const dummyLogger: ILogger = {
      log: () => {} // 空实现，不会被调用
    };

    const mockDb: IDatabase = {
      query: async (sql, params) => {
        return { rows: [{ id: '123' }] };
      }
    };

    const service = new OrderService(mockDb, dummyLogger);

    // Act
    await service.createOrder({ product: 'Widget' });

    // Assert
    // 测试通过，logger 没有被使用
  });
});
```

### 21.2.3 Stub (桩)

```typescript
/**
 * Stub: 提供预设的返回值，不验证调用
 */

/**
 * 示例：使用 Stub 测试 UserService
 */
export class UserService {
  constructor(private userRepo: IUserRepository) {}

  async getUserEmail(userId: string): Promise<string> {
    const user = await this.userRepo.findById(userId);

    if (!user) {
      throw new Error('User not found');
    }

    return user.email;
  }
}

export interface IUserRepository {
  findById(id: string): Promise<User | null>;
}

export interface User {
  id: string;
  email: string;
}

/**
 * 测试：使用 Stub
 */
suite('UserService', () => {
  test('should return user email', async () => {
    // Arrange
    const stubRepo: IUserRepository = {
      // ✅ Stub: 返回预设值
      findById: async (id: string) => {
        return {
          id: id,
          email: 'user@example.com'
        };
      }
    };

    const service = new UserService(stubRepo);

    // Act
    const email = await service.getUserEmail('123');

    // Assert
    assert.equal(email, 'user@example.com');
  });

  test('should throw when user not found', async () => {
    // Arrange
    const stubRepo: IUserRepository = {
      // ✅ Stub: 返回 null
      findById: async (id: string) => null
    };

    const service = new UserService(stubRepo);

    // Act & Assert
    assertthrows(
      () => service.getUserEmail('999'),
      'User not found'
    );
  });
});
```

### 21.2.4 Spy (间谍)

```typescript
/**
 * Spy: 记录调用信息，用于验证交互
 */

/**
 * 示例：使用 Spy 验证邮件发送
 */
export class NotificationService {
  constructor(
    private userRepo: IUserRepository,
    private emailer: IEmailer
  ) {}

  async sendWelcomeEmail(userId: string): Promise<void> {
    const user = await this.userRepo.findById(userId);

    if (!user) {
      throw new Error('User not found');
    }

    await this.emailer.send(
      user.email,
      'Welcome!',
      `Hello ${user.name}, welcome to our service!`
    );
  }
}

export interface IEmailer {
  send(to: string, subject: string, body: string): Promise<void>;
}

export interface User {
  id: string;
  email: string;
  name: string;
}

/**
 * 测试：使用 Spy
 */
suite('NotificationService', () => {
  test('should send welcome email with correct parameters', async () => {
    // Arrange
    const stubRepo: IUserRepository = {
      findById: async (id: string) => ({
        id: id,
        email: 'user@example.com',
        name: 'John Doe'
      })
    };

    // ✅ Spy: 记录调用信息
    const emailSpy: IEmailer & { calls: any[] } = {
      calls: [],
      send: async (to: string, subject: string, body: string) => {
        emailSpy.calls.push({ to, subject, body });
      }
    };

    const service = new NotificationService(stubRepo, emailSpy);

    // Act
    await service.sendWelcomeEmail('123');

    // Assert - 验证调用
    assert.equal(emailSpy.calls.length, 1);
    assert.equal(emailSpy.calls[0].to, 'user@example.com');
    assert.equal(emailSpy.calls[0].subject, 'Welcome!');
    assert.include(emailSpy.calls[0].body, 'John Doe');
  });
});
```

### 21.2.5 Mock (模拟)

```typescript
/**
 * Mock: 预设期望的调用行为和次数
 */

/**
 * 示例：使用 Mock 验证期望
 */
export class OrderService {
  constructor(
    private paymentGateway: IPaymentGateway,
    private orderRepo: IOrderRepository
  ) {}

  async createOrder(order: OrderData): Promise<string> {
    // 1. 处理支付
    const paymentResult = await this.paymentGateway.charge(order.total);

    if (!paymentResult.success) {
      throw new Error('Payment failed');
    }

    // 2. 创建订单
    const orderId = await this.orderRepo.save({
      ...order,
      paymentId: paymentResult.transactionId
    });

    return orderId;
  }
}

export interface IPaymentGateway {
  charge(amount: number): Promise<PaymentResult>;
}

export interface IOrderRepository {
  save(order: any): Promise<string>;
}

export interface OrderData {
  items: any[];
  total: number;
}

export interface PaymentResult {
  success: boolean;
  transactionId?: string;
}

/**
 * 测试：使用 Mock
 */
suite('OrderService', () => {
  test('should charge payment and save order', async () => {
    // Arrange
    const mockPaymentGateway: IPaymentGateway & {
      chargeCalled: boolean;
      chargeCalledWith: number;
    } = {
      chargeCalled: false,
      chargeCalledWith: 0,
      charge: async (amount: number) => {
        mockPaymentGateway.chargeCalled = true;
        mockPaymentGateway.chargeCalledWith = amount;
        return {
          success: true,
          transactionId: 'txn-123'
        };
      }
    };

    const mockOrderRepo: IOrderRepository = {
      save: async (order: any) => 'order-456'
    };

    const service = new OrderService(mockPaymentGateway, mockOrderRepo);

    // Act
    const orderId = await service.createOrder({
      items: [{ product: 'Widget', quantity: 2 }],
      total: 99.99
    });

    // Assert - 验证 Mock 期望
    assert.isTrue(mockPaymentGateway.chargeCalled);
    assert.equal(mockPaymentGateway.chargeCalledWith, 99.99);
    assert.equal(orderId, 'order-456');
  });
});
```

### 21.2.6 Fake (伪造)

```typescript
/**
 * Fake: 简化但可用的实现
 */

/**
 * 示例：使用 Fake Repository
 */
export class UserService {
  constructor(private userRepo: IUserRepository) {}

  async registerUser(email: string, password: string): Promise<string> {
    // 检查邮箱是否已存在
    const existing = await this.userRepo.findByEmail(email);

    if (existing) {
      throw new Error('Email already registered');
    }

    // 创建新用户
    const userId = await this.userRepo.save({
      email,
      passwordHash: this.hashPassword(password)
    });

    return userId;
  }

  private hashPassword(password: string): string {
    return 'hashed_' + password;
  }
}

export interface IUserRepository {
  findByEmail(email: string): Promise<User | null>;
  save(user: any): Promise<string>;
}

export interface User {
  id: string;
  email: string;
  passwordHash: string;
}

/**
 * ✅ Fake: 内存实现，可用于测试
 */
export class InMemoryUserRepository implements IUserRepository {
  private users: Map<string, User> = new Map();
  private nextId = 1;

  async findByEmail(email: string): Promise<User | null> {
    for (const user of this.users.values()) {
      if (user.email === email) {
        return user;
      }
    }
    return null;
  }

  async save(user: any): Promise<string> {
    const id = String(this.nextId++);
    const newUser: User = {
      id,
      email: user.email,
      passwordHash: user.passwordHash
    };
    this.users.set(id, newUser);
    return id;
  }

  // 额外辅助方法
  count(): number {
    return this.users.size;
  }

  clear(): void {
    this.users.clear();
    this.nextId = 1;
  }
}

/**
 * 测试：使用 Fake Repository
 */
suite('UserService', () => {
  let service: UserService;
  let fakeRepo: InMemoryUserRepository;

  setup(() => {
    fakeRepo = new InMemoryUserRepository();
    service = new UserService(fakeRepo);
  });

  teardown(() => {
    fakeRepo.clear();
  });

  test('should register new user', async () => {
    // Act
    const userId = await service.registerUser(
      'user@example.com',
      'password123'
    );

    // Assert
    assert.equal(userId, '1');
    assert.equal(fakeRepo.count(), 1);
  });

  test('should reject duplicate email', async () => {
    // Arrange
    await service.registerUser('user@example.com', 'password123');

    // Act & Assert
    assertthrows(
      () => service.registerUser('user@example.com', 'password456'),
      'Email already registered'
    );

    assert.equal(fakeRepo.count(), 1); // 只创建了一个用户
  });
});
```

---

## 21.3 使用测试框架的 Mocking

### 21.3.1 Sinon.js - 强大的测试库

```typescript
/**
 * 使用 Sinon.js 进行 Mocking
 */

import * as sinon from 'sinon';
import { assert } from 'chai';

export class EmailService {
  constructor(
    private emailer: IEmailer,
    private userRepo: IUserRepository
  ) {}

  async sendWelcomeEmail(userId: string): Promise<void> {
    const user = await this.userRepo.findById(userId);

    if (!user) {
      throw new Error('User not found');
    }

    await this.emailer.send(user.email, 'Welcome', 'Welcome!');
  }
}

export interface IEmailer {
  send(to: string, subject: string, body: string): Promise<void>;
}

export interface IUserRepository {
  findById(id: string): Promise<User | null>;
}

export interface User {
  id: string;
  email: string;
}

/**
 * 测试：使用 Sinon
 */
suite('EmailService with Sinon', () => {
  test('should send welcome email', async () => {
    // Arrange
    const user = { id: '123', email: 'user@example.com' };

    // ✅ Sinon Stub
    const userRepoStub = sinon.stub();
    userRepoStub.withArgs('123').resolves(user);
    userRepoStub.withArgs('999').resolves(null);

    const userRepo: IUserRepository = {
      findById: userRepoStub
    };

    // ✅ Sinon Spy
    const emailerSpy = sinon.spy();

    const emailer: IEmailer = {
      send: emailerSpy
    };

    const service = new EmailService(emailer, userRepo);

    // Act
    await service.sendWelcomeEmail('123');

    // Assert - Sinon 断言
    assert.isTrue(emailerSpy.calledOnce);
    assert.isTrue(
      emailerSpy.calledWith(
        'user@example.com',
        'Welcome',
        'Welcome!'
      )
    );
  });

  test('should throw when user not found', async () => {
    // Arrange
    const userRepoStub = sinon.stub();
    userRepoStub.resolves(null);

    const userRepo: IUserRepository = {
      findById: userRepoStub
    };

    const emailer: IEmailer = {
      send: async () => {}
    };

    const service = new EmailService(emailer, userRepo);

    // Act & Assert
    await assert.isRejected(
      service.sendWelcomeEmail('999'),
      'User not found'
    );

    // 验证邮件没有被发送
    // (需要创建 emailerSpy 来验证)
  });
});
```

### 21.3.2 使用 Mocking 框架的注意事项

```typescript
/**
 * ✅ 好的 Mocking 实践
 */

/**
 * 1. 行为验证 vs 状态验证
 */

// ✅ 状态验证 - 检查最终状态
test('should create order', async () => {
  const fakeRepo = new InMemoryOrderRepository();
  const service = new OrderService(fakeRepo);

  await service.createOrder({ total: 100 });

  const orders = await fakeRepo.findAll();
  assert.equal(orders.length, 1);
  assert.equal(orders[0].total, 100);
});

// ✅ 行为验证 - 检查调用行为
test('should send email after registration', async () => {
  const emailer = sinon.spy();
  const service = new UserService(fakeRepo, emailer);

  await service.registerUser('user@example.com', 'pass');

  assert.isTrue(emailer.calledOnce);
});

/**
 * 2. 避免过度 Mocking
 */

// ❌ 过度 Mocking - 测试变得脆弱
test('fragile test with over-mocking', async () => {
  // 太多 Mock，测试变得脆弱
  const mock1 = sinon.mock(obj1);
  const mock2 = sinon.mock(obj2);
  const mock3 = sinon.mock(obj3);
  const mock4 = sinon.mock(obj4);

  // ... 测试逻辑

  // 太多验证，任何一个变化都会导致测试失败
  mock1.verify();
  mock2.verify();
  mock3.verify();
  mock4.verify();
});

// ✅ 适当 Mocking - 测试关注点
test('focused test with minimal mocking', async () => {
  // 只 Mock 真正需要隔离的依赖
  const fakeRepo = new InMemoryRepository(); // 使用 Fake

  const service = new OrderService(fakeRepo);

  // 关注业务逻辑，而非实现细节
  await service.createOrder({ total: 100 });

  // 验证最终结果
  assert.equal(await fakeRepo.count(), 1);
});

/**
 * 3. Mock 的层次
 */

// ✅ Mock 外部依赖
const mockDb = sinon.stub().resolves({ id: '123' });
const mockEmailer = sinon.spy();

// ✅ Fake 数据访问层
const fakeRepo = new InMemoryRepository();

// ❌ 不要 Mock 被测试的系统
// const mockService = sinon.mock(service); // ❌ 不要这样！
```

---

## 21.4 mybatis-boost 中的测试实践

```typescript
/**
 * mybatis-boost 的测试策略
 */

/**
 * 1. 使用 Fake 测试 FileMapper
 */

export class FileMapper {
  constructor(
    private fileSystem: IFileSystem,
    private parser: IParser,
    private cache: ICache
  ) {}

  async findXmlForJava(javaFile: string): Promise<MappingResult[]> {
    // 检查缓存
    const cached = await this.cache.get(javaFile);
    if (cached) {
      return cached;
    }

    // 读取文件
    const content = await this.fileSystem.readFile(javaFile);

    // 解析
    const parseResult = this.parser.parseJava(content);

    // 查找匹配的 XML 文件
    const xmlFiles = await this.fileSystem.findFiles(
      `**/${parseResult.mapperName}.xml`
    );

    const results = xmlFiles.map(xmlFile => ({
      source: javaFile,
      target: xmlFile,
      line: 1
    }));

    // 缓存结果
    await this.cache.set(javaFile, results);

    return results;
  }
}

export interface IFileSystem {
  readFile(path: string): Promise<string>;
  findFiles(pattern: string): Promise<string[]>;
}

export interface IParser {
  parseJava(content: string): ParseResult;
}

export interface ICache {
  get(key: string): Promise<MappingResult[] | null>;
  set(key: string, value: MappingResult[]): Promise<void>;
}

export interface MappingResult {
  source: string;
  target: string;
  line: number;
}

export interface ParseResult {
  mapperName: string;
}

/**
 * ✅ 测试 FileMapper
 */
import { assert } from 'mocha';

suite('FileMapper', () => {
  let mapper: FileMapper;
  let mockFileSystem: IFileSystem;
  let mockParser: IParser;
  let mockCache: ICache;

  setup(() => {
    mockFileSystem = {
      readFile: async () => '',
      findFiles: async () => []
    };

    mockParser = {
      parseJava: () => ({ mapperName: 'UserMapper' })
    };

    mockCache = {
      get: async () => null,
      set: async () => {}
    };

    mapper = new FileMapper(mockFileSystem, mockParser, mockCache);
  });

  test('should return cached result', async () => {
    // Arrange
    const cachedResults: MappingResult[] = [
      { source: '/test.java', target: '/test.xml', line: 1 }
    ];

    mockCache.get = async (key: string) => {
      if (key === '/test.java') {
        return cachedResults;
      }
      return null;
    };

    // Act
    const results = await mapper.findXmlForJava('/test.java');

    // Assert
    assert.equal(results.length, 1);
    assert.equal(results[0].target, '/test.xml');
  });

  test('should find XML file for Java mapper', async () => {
    // Arrange
    mockFileSystem.readFile = async () => 'public class UserMapper {}';
    mockParser.parseJava = () => ({ mapperName: 'UserMapper' });
    mockFileSystem.findFiles = async () => ['/src/UserMapper.xml'];
    mockCache.get = async () => null;

    // Act
    const results = await mapper.findXmlForJava('/src/UserMapper.java');

    // Assert
    assert.equal(results.length, 1);
    assert.equal(results[0].source, '/src/UserMapper.java');
    assert.equal(results[0].target, '/src/UserMapper.xml');
  });

  test('should cache results', async () => {
    // Arrange
    const cached: any[] = [];

    mockFileSystem.readFile = async () => 'public class UserMapper {}';
    mockParser.parseJava = () => ({ mapperName: 'UserMapper' });
    mockFileSystem.findFiles = async () => ['/src/UserMapper.xml'];
    mockCache.get = async () => null;
    mockCache.set = async (key: string, value: MappingResult[]) => {
      cached.push({ key, value });
    };

    // Act
    await mapper.findXmlForJava('/src/UserMapper.java');

    // Assert
    assert.equal(cached.length, 1);
    assert.equal(cached[0].key, '/src/UserMapper.java');
    assert.equal(cached[0].value.length, 1);
  });
});
```

---

## 21.5 使用 Claude Code 编写可测试代码

### 21.5.1 让 Claude Code 帮助识别不可测试代码

```bash
# 激活 Plan Mode
Shift+Tab (两次)

# 任务描述：
检查这个文件的可测试性问题

# Claude 会：
1. 识别硬编码依赖
2. 找出全局状态使用
3. 发现静态方法调用
4. 建议重构方案
```

### 21.5.2 让 Claude Code 生成测试

```bash
# 任务：
为 UserService 编写单元测试

# Claude 会：
1. 分析 UserService 的依赖
2. 创建适当的 Mock 对象
3. 编写测试用例
4. 覆盖主要场景
```

### 21.5.3 配置 CLAUDE.md

```markdown
# CLAUDE.md

## 测试规范

### 可测试性原则

1. **所有依赖必须可注入**
   - 使用构造函数注入
   - 定义接口而非具体类

2. **避免全局状态**
   - 不使用全局变量
   - 通过参数传递依赖

3. **避免静态方法**
   - 包装外部 API
   - 使用接口抽象

### 测试替身选择

- **Fake**: 用于 Repository、Cache 等数据访问
- **Stub**: 用于返回固定值
- **Spy**: 用于验证调用行为
- **Mock**: 用于复杂交互验证

### 测试示例

\`\`\`typescript
// ✅ 好的测试实践
suite('UserService', () => {
  test('should register new user', async () => {
    const fakeRepo = new InMemoryUserRepository();
    const service = new UserService(fakeRepo);

    const userId = await service.registerUser('user@example.com', 'pass');

    assert.equal(userId, '1');
  });
});
\`\`\`
```

---

## 21.6 常见陷阱

### 陷阱 1：Mock 被测试的系统

```typescript
// ❌ 错误：Mock 被测试的系统
test('bad test - mocking the system under test', () => {
  const mockService = sinon.mock(userService);

  mockService.expects('registerUser')
    .once()
    .withArgs('user@example.com', 'pass')
    .returns(Promise.resolve('123'));

  // 这没有测试真正的实现！
  mockService.verify();
});

// ✅ 正确：测试真正的实现
test('good test - testing real implementation', () => {
  const fakeRepo = new InMemoryUserRepository();
  const service = new UserService(fakeRepo);

  const userId = await service.registerUser('user@example.com', 'pass');

  assert.equal(userId, '1');
  assert.equal(await fakeRepo.count(), 1);
});
```

### 陷阱 2：过度验证实现细节

```typescript
// ❌ 过度验证实现细节
test('fragile test - verifying implementation details', () => {
  const emailer = sinon.spy();
  const repo = sinon.stub();
  const validator = sinon.spy();
  const logger = sinon.spy();

  // ...

  assert.isTrue(emailer.calledOnce);
  assert.isTrue(repo.calledOnce);
  assert.isTrue(validator.calledTwice);
  assert.isTrue(logger.calledWithExactly('INFO', 'User registered'));
  // 太多验证！任何内部实现变化都会导致测试失败
});

// ✅ 关注行为，而非实现
test('robust test - verifying behavior', () => {
  const fakeRepo = new InMemoryUserRepository();
  const service = new UserService(fakeRepo);

  await service.registerUser('user@example.com', 'pass');

  // 只验证最终结果
  assert.equal(await fakeRepo.count(), 1);
  const user = await fakeRepo.findByEmail('user@example.com');
  assert.isDefined(user);
});
```

### 陷阱 3：Mock 链

```typescript
// ❌ Mock 链 - 脆弱且难以维护
test('mock chain - fragile', () => {
  const mockObj1 = mock(obj1);
  const mockObj2 = mock(obj2);
  const mockObj3 = mock(obj3);

  when(mockObj1.method()).thenReturn(mockObj2);
  when(mockObj2.method()).thenReturn(mockObj3);
  when(mockObj3.method()).thenReturn('value');

  // 脆弱！任何链的变化都会破坏测试
});

// ✅ 直接 Mock 最终结果
test('direct mock - robust', () => {
  const fakeRepo = new InMemoryRepository();
  // 使用 Fake，避免 Mock 链
});
```

---

## 21.7 练习

### 练习 1：识别不可测试代码

指出以下代码中的可测试性问题：

```typescript
export class OrderProcessor {
  private db = new PostgresDatabase('localhost', 5432);
  private emailer = new SendGridEmailer('api-key');

  async processOrder(orderData: any): Promise<void> {
    if (this.isValidOrder(orderData)) {
      const orderId = await this.db.query(
        'INSERT INTO orders...'
      );

      await this.emailer.send(
        orderData.customerEmail,
        'Order Confirmation',
        `Your order ${orderId} has been received.`
      );
    }
  }

  private isValidOrder(data: any): boolean {
    return data.items?.length > 0 && data.total > 0;
  }
}
```

**答案**：
1. `db` 是硬编码依赖，无法 mock
2. `emailer` 是硬编码依赖，无法 mock
3. 数据库连接字符串硬编码
4. API key 硬编码

### 练习 2：重构为可测试代码

重构上面的代码，使其可测试。

### 练习 3：编写测试

为重构后的代码编写单元测试。

---

## 21.8 进一步阅读

- [Test Doubles by Gerard Meszaros](https://martinfowler.com/bliki/TestDouble.html)
- [Sinon.js Documentation](https://sinonjs.org/)
- [Chapter 22: AAA 模式与测试最佳实践](chapter-22-aaa-pattern.md) - 下一章

---

## 视频脚本

### Episode 21: 可测试性与 Mocking (16 分钟)

#### [0:00-1:00] 引入
**视觉元素**：
- 标题："可测试代码：好的架构的自然结果"
- 代码对比：不可测试 vs 可测试

**内容**：
> 什么是可测试代码？不是"能写测试"的代码，而是"容易写测试"的代码。好的架构自然产生可测试的代码。今天我们学习如何识别和编写可测试的代码。

#### [1:00-3:00] 识别不可测试代码
**视觉元素**：
- 不可测试代码示例（红色高亮）
- 问题列表

**内容**：
> 三个常见的不可测试代码特征：
> 1. 硬编码依赖 - `new Database()`
> 2. 全局状态 - `global.currentUser`
> 3. 静态方法 - `ExternalAPI.call()`
>
> 这些都让我们无法隔离代码进行测试。

#### [3:00-7:00] 测试替身
**视觉元素**：
- Test Doubles 分类图
- 每种 Double 的示例代码

**内容**：
> Gerard Meszaros 定义了五种测试替身：
>
> - **Dummy**: 哑元，满足参数但不使用
> - **Stub**: 桩，返回预设值
> - **Spy**: 间谍，记录调用信息
> - **Mock**: 模拟，验证期望行为
> - **Fake**: 伪造，简化实现
>
> [演示：使用不同的 Test Doubles]
>
> 记住：Fake 是最强大的，因为它提供了真实的实现！

#### [7:00-11:00] 使用 Sinon.js
**视觉元素**：
- Sinon.js 代码演示
- 测试运行结果

**内容**：
> Sinon.js 是 JavaScript 测试的瑞士军刀。
>
> [演示：使用 Sinon Stub 和 Spy]
>
> 看到没有？我们可以精确验证方法被调用的次数、参数、返回值。但记住：不要过度 Mock！测试应该关注行为，而非实现细节。

#### [11:00-14:00] mybatis-boost 测试实战
**视觉元素**：
- mybatis-boost 测试文件
- Fake Repository 实现

**内容**：
> [演示：查看 mybatis-boost 的测试]
>
> mybatis-boost 使用 Fake Repository 测试 FileMapper。这比 Mock 更好，因为它提供了真实的内存实现，让测试更接近真实场景。
>
> 注意看：FileMapper 的所有依赖都是接口，这让测试变得简单。

#### [14:00-16:00] 总结
**视觉元素**：
- 关键要点列表
- Next Chapter 预告

**内容**：
> 可测试性关键要点：
> - 所有依赖必须可注入
> - 使用接口抽象
> - 优先使用 Fake 而非 Mock
> - 测试行为，而非实现细节
>
> 下一章，我们将学习 AAA 模式，看看如何组织清晰、易读的测试。
