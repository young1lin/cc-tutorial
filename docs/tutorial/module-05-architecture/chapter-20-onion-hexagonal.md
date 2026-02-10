# Chapter 20: 洋葱架构与六边形架构

## 学习目标

完成本章后，你将能够：

- 理解洋葱架构 (Onion Architecture) 的核心概念
- 理解六边形架构 (Hexagonal Architecture/Ports and Adapters)
- 比较整洁架构、洋葱架构和六边形架构的异同
- 在实际项目中应用这些架构模式
- 选择适合你项目的架构模式

## 前置知识

- [Chapter 19: 整洁架构原则](chapter-19-clean-architecture.md)
- 依赖注入和依赖倒置原则
- 接口和抽象的概念

---

## 20.1 洋葱架构 (Onion Architecture)

### 20.1.1 概念概述

**洋葱架构** 由 Jeffrey Palermo 在 2008 年提出，其核心思想是：**将应用程序组织为 concentric layers (同心层)，依赖方向始终由外向内**。

```
                    ┌─────────────────────────┐
                    │   UI / Tests / CI/CD    │  ← 最外层
                    │   (External Concerns)    │
                    └───────────▲─────────────┘
                                │
        ┌───────────────────────┴─────────────────────────┐
        │              Application Services                │  ← 应用服务层
        │          (Orchestration, Coordination)          │
        └───────────────────────▲─────────────────────────┘
                                │
        ┌───────────────────────┴─────────────────────────┐
        │             Domain Services + Models             │  ← 领域服务层
        │          (Business Logic, Entities)              │
        └───────────────────────▲─────────────────────────┘
                                │
        ┌───────────────────────┴─────────────────────────┐
        │                 Core Domain                      │  ← 核心领域层
        │           (Enterprise Business Rules)            │
        └─────────────────────────────────────────────────┘

                    依赖方向：外层 → 内层
                    数据流向：内层 → 外层
```

### 20.1.2 与整洁架构的关系

洋葱架构和整洁架构**本质上是相同的架构思想**，只是术语不同：

| 洋葱架构 | 整洁架构 | 职责 |
|----------|----------|------|
| Core Domain | Entities | 企业级业务规则 |
| Domain Services + Models | Use Cases | 应用业务规则 |
| Application Services | Interface Adapters | 适配外部世界 |
| UI / Tests / CI/CD | Frameworks & Drivers | 外部工具 |

**核心区别**：
- 整洁架构更强调"Entities"和"Use Cases"的分离
- 洋葱架构更强调"Domain"的层次划分

### 20.1.3 洋葱架构的实现

```typescript
/**
 * 洋葱架构示例：用户认证系统
 */

// ============================================================
// CORE DOMAIN (核心领域层) - 最内层
// ============================================================

/**
 * Domain Entity: 用户实体
 * 不依赖任何外部框架或库
 */
export interface User {
  id: UserId;
  email: Email;
  passwordHash: PasswordHash;
  profile: UserProfile;
}

/**
 * Value Objects: 值对象
 * 确保数据的有效性
 */
export class UserId {
  constructor(private readonly value: string) {
    if (value.length === 0) {
      throw new Error('User ID cannot be empty');
    }
  }

  getValue(): string {
    return this.value;
  }

  equals(other: UserId): boolean {
    return this.value === other.getValue();
  }
}

export class Email {
  private static readonly EMAIL_REGEX =
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  constructor(private readonly value: string) {
    if (!Email.EMAIL_REGEX.test(value)) {
      throw new Error('Invalid email format');
    }
  }

  getValue(): string {
    return this.value;
  }
}

export class PasswordHash {
  constructor(private readonly value: string) {
    if (value.length < 32) {
      throw new Error('Invalid password hash');
    }
  }

  getValue(): string {
    return this.value;
  }
}

export interface UserProfile {
  firstName: string;
  lastName: string;
  dateOfBirth: Date;
}

/**
 * Domain Service: 领域服务
 * 包含核心业务规则
 */
export class UserDomainService {
  /**
   * 业务规则：用户必须年满 18 岁
   */
  static isAdult(profile: UserProfile): boolean {
    const today = new Date();
    const age = today.getFullYear() - profile.dateOfBirth.getFullYear();
    const monthDiff = today.getMonth() - profile.dateOfBirth.getMonth();

    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < profile.dateOfBirth.getDate())) {
      return age - 1 >= 18;
    }

    return age >= 18;
  }

  /**
   * 业务规则：密码必须包含大小写字母和数字
   */
  static isPasswordStrong(password: string): boolean {
    const strongRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
    return strongRegex.test(password);
  }
}

/**
 * Domain Events: 领域事件
 */
export interface DomainEvent {
  occurredAt: Date;
}

export class UserRegisteredEvent implements DomainEvent {
  readonly occurredAt = new Date();

  constructor(
    public readonly userId: UserId,
    public readonly email: Email
  ) {}
}

export class UserLoggedInEvent implements DomainEvent {
  readonly occurredAt = new Date();

  constructor(
    public readonly userId: UserId,
    public readonly loginTime: Date
  ) {}
}

// ============================================================
// DOMAIN SERVICES + MODELS (领域服务层)
// ============================================================

/**
 * Repository Interface: 仓储接口
 * 由内层定义，外层实现
 */
export interface IUserRepository {
  save(user: User): Promise<void>;
  findById(id: UserId): Promise<User | null>;
  findByEmail(email: Email): Promise<User | null>;
  existsByEmail(email: Email): Promise<boolean>;
}

/**
 * Domain Service: 用户注册领域服务
 */
export class UserRegistrationService {
  constructor(
    private userRepository: IUserRepository
  ) {}

  async register(
    email: Email,
    password: string,
    profile: UserProfile
  ): Promise<User> {
    // 领域规则 1: 检查用户是否已存在
    if (await this.userRepository.existsByEmail(email)) {
      throw new Error('User already exists');
    }

    // 领域规则 2: 验证密码强度
    if (!UserDomainService.isPasswordStrong(password)) {
      throw new Error('Password is not strong enough');
    }

    // 领域规则 3: 验证年龄
    if (!UserDomainService.isAdult(profile)) {
      throw new Error('User must be at least 18 years old');
    }

    // 创建新用户
    const user: User = {
      id: new UserId(this.generateId()),
      email: email,
      passwordHash: new PasswordHash(this.hashPassword(password)),
      profile: profile
    };

    // 保存用户
    await this.userRepository.save(user);

    return user;
  }

  private generateId(): string {
    return Math.random().toString(36).substring(7);
  }

  private hashPassword(password: string): string {
    // 实际实现会在 Infrastructure 层
    return 'hashed_' + password;
  }
}

// ============================================================
// APPLICATION SERVICES (应用服务层)
// ============================================================

/**
 * Application Service: 应用服务
 * 编排用例流程
 */
export class UserApplicationService {
  constructor(
    private registrationService: UserRegistrationService,
    private eventPublisher: EventPublisher
  ) {}

  async handleRegisterUserCommand(
    command: RegisterUserCommand
  ): Promise<RegisterUserResult> {
    try {
      // 1. 创建值对象
      const email = new Email(command.email);
      const profile: UserProfile = {
        firstName: command.firstName,
        lastName: command.lastName,
        dateOfBirth: command.dateOfBirth
      };

      // 2. 调用领域服务
      const user = await this.registrationService.register(
        email,
        command.password,
        profile
      );

      // 3. 发布领域事件
      await this.eventPublisher.publish(
        new UserRegisteredEvent(user.id, user.email)
      );

      // 4. 返回结果
      return {
        success: true,
        userId: user.id.getValue()
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
}

/**
 * Commands: 命令对象
 */
export interface RegisterUserCommand {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  dateOfBirth: Date;
}

/**
 * Results: 结果对象
 */
export interface RegisterUserResult {
  success: boolean;
  userId?: string;
  error?: string;
}

/**
 * Event Publisher Interface: 事件发布器接口
 */
export interface EventPublisher {
  publish(event: DomainEvent): Promise<void>;
}

// ============================================================
// UI / TESTS / INFRASTRUCTURE (最外层)
// ============================================================

/**
 * Framework: Express Controller
 */
import { Request, Response } from 'express';

export class UserController {
  constructor(
    private applicationService: UserApplicationService
  ) {}

  async register(req: Request, res: Response): Promise<void> {
    const command: RegisterUserCommand = {
      email: req.body.email,
      password: req.body.password,
      firstName: req.body.firstName,
      lastName: req.body.lastName,
      dateOfBirth: new Date(req.body.dateOfBirth)
    };

    const result = await this.applicationService.handleRegisterUserCommand(command);

    if (result.success) {
      res.status(201).json({ userId: result.userId });
    } else {
      res.status(400).json({ error: result.error });
    }
  }
}

/**
 * Infrastructure: PostgreSQL Repository Implementation
 */
export class PostgresUserRepository implements IUserRepository {
  constructor(private db: any) {}

  async save(user: User): Promise<void> {
    await this.db.query(
      'INSERT INTO users (id, email, password_hash, first_name, last_name, date_of_birth) VALUES ($1, $2, $3, $4, $5, $6)',
      [
        user.id.getValue(),
        user.email.getValue(),
        user.passwordHash.getValue(),
        user.profile.firstName,
        user.profile.lastName,
        user.profile.dateOfBirth
      ]
    );
  }

  async findById(id: UserId): Promise<User | null> {
    const row = await this.db.query('SELECT * FROM users WHERE id = $1', [id.getValue()]);
    if (!row) return null;

    return this.mapRowToUser(row);
  }

  async findByEmail(email: Email): Promise<User | null> {
    const row = await this.db.query('SELECT * FROM users WHERE email = $1', [email.getValue()]);
    if (!row) return null;

    return this.mapRowToUser(row);
  }

  async existsByEmail(email: Email): Promise<boolean> {
    const result = await this.db.query('SELECT COUNT(*) FROM users WHERE email = $1', [email.getValue()]);
    return result.count > 0;
  }

  private mapRowToUser(row: any): User {
    return {
      id: new UserId(row.id),
      email: new Email(row.email),
      passwordHash: new PasswordHash(row.password_hash),
      profile: {
        firstName: row.first_name,
        lastName: row.last_name,
        dateOfBirth: new Date(row.date_of_birth)
      }
    };
  }
}

/**
 * Infrastructure: In-Memory Event Publisher
 */
export class InMemoryEventPublisher implements EventPublisher {
  private events: DomainEvent[] = [];

  async publish(event: DomainEvent): Promise<void> {
    this.events.push(event);
    console.log('Event published:', event);
  }

  getEvents(): DomainEvent[] {
    return [...this.events];
  }
}

// ============================================================
// DEPENDENCY INJECTION (依赖注入)
// ============================================================

/**
 * Application Composition Root
 * 应用程序组合根
 */
export function composeApplication() {
  // Infrastructure (最外层)
  const db = createPostgresConnection();
  const userRepository = new PostgresUserRepository(db);
  const eventPublisher = new InMemoryEventPublisher();

  // Domain Services (中间层)
  const registrationService = new UserRegistrationService(userRepository);

  // Application Services (外层)
  const applicationService = new UserApplicationService(
    registrationService,
    eventPublisher
  );

  // UI / Controllers (最外层)
  const userController = new UserController(applicationService);

  return {
    userController,
    userRepository,
    eventPublisher
  };
}

function createPostgresConnection(): any {
  // 实际的数据库连接创建逻辑
  return {};
}
```

---

## 20.2 六边形架构 (Hexagonal Architecture)

### 20.2.1 概念概述

**六边形架构** (也称为 **Ports and Adapters** 架构) 由 Alistair Cockburn 在 2005 年提出，其核心思想是：**应用程序通过 "Ports" (端口) 与外部世界交互，通过 "Adapters" (适配器) 连接不同的外部技术**。

```
                 ┌─────────────────────────────┐
                 │      APPLICATION CORE        │
                 │    (Business Logic Only)     │
                 └───────────▲─────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────┴────┐         ┌────┴────┐         ┌────┴────┐
    │  Port   │         │  Port   │         │  Port   │
    │(Driving)│         │(Driving)│         │(Driven) │
    └────▲────┘         └────▲────┘         └────▲────┘
         │                   │                   │
    ┌────┴────┐         ┌────┴────┘         ┌────┴────┐
    │Adapter  │         │Adapter  │         │Adapter  │
    │(HTTP)   │         │(CLI)    │         │(DB)     │
    └─────────┘         └─────────┘         └─────────┘

    Driving Ports: 由外部驱动的端口 (Primary)
    Driven Ports: 驱动外部的端口 (Secondary)
```

### 20.2.2 Ports 和 Adapters

#### Ports (端口)

**Port** 是应用程序与外部世界交互的**接口**，定义在**应用程序内部**。

```typescript
/**
 * Port: 定义在应用程序内部的接口
 */

// ============================================================
// DRIVING PORTS (Primary Ports)
// 由外部驱动的端口 - 输入端口
// ============================================================

/**
 * Driving Port: 用户注册用例
 * 外部（HTTP、CLI、消息队列）通过此端口与应用程序交互
 */
export interface IUserRegistrationPort {
  register(request: RegisterUserRequest): Promise<RegisterUserResponse>;
}

export interface RegisterUserRequest {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  dateOfBirth: Date;
}

export interface RegisterUserResponse {
  success: boolean;
  userId?: string;
  error?: string;
}

/**
 * Driving Port: 用户登录用例
 */
export interface IUserAuthenticationPort {
  authenticate(email: string, password: string): Promise<AuthenticationResult>;
}

export interface AuthenticationResult {
  success: boolean;
  token?: string;
  error?: string;
}

// ============================================================
// DRIVEN PORTS (Secondary Ports)
// 驱动外部的端口 - 输出端口
// ============================================================

/**
 * Driven Port: 用户数据存储
 * 应用程序通过此端口访问外部存储
 */
export interface IUserRepositoryPort {
  save(user: User): Promise<void>;
  findById(id: string): Promise<User | null>;
  findByEmail(email: string): Promise<User | null>;
}

/**
 * Driven Port: 邮件发送
 * 应用程序通过此端口发送邮件
 */
export interface IEmailSenderPort {
  sendWelcomeEmail(to: string, userName: string): Promise<void>;
}

/**
 * Driven Port: 事件发布
 * 应用程序通过此端口发布领域事件
 */
export interface IEventPublisherPort {
  publish(event: DomainEvent): Promise<void>;
}
```

#### Adapters (适配器)

**Adapter** 是实现 Port 接口的具体技术，位于**应用程序外部**。

```typescript
/**
 * Adapter: 实现接口的具体技术
 */

// ============================================================
// DRIVING ADAPTERS (Primary Adapters)
// 驱动应用程序的适配器 - 输入适配器
// ============================================================

/**
 * Driving Adapter: HTTP REST Controller
 * 将 HTTP 请求转换为应用程序可理解的格式
 */
import { Request, Response } from 'express';

export class UserHttpAdapter {
  constructor(private port: IUserRegistrationPort) {}

  async register(req: Request, res: Response): Promise<void> {
    try {
      // 将 HTTP 请求转换为 Port 请求格式
      const portRequest: RegisterUserRequest = {
        email: req.body.email,
        password: req.body.password,
        firstName: req.body.firstName,
        lastName: req.body.lastName,
        dateOfBirth: new Date(req.body.dateOfBirth)
      };

      // 调用 Port
      const response = await this.port.register(portRequest);

      // 将 Port 响应转换为 HTTP 响应格式
      if (response.success) {
        res.status(201).json({ userId: response.userId });
      } else {
        res.status(400).json({ error: response.error });
      }
    } catch (error) {
      res.status(500).json({ error: 'Internal server error' });
    }
  }
}

/**
 * Driving Adapter: CLI Command
 * 将命令行参数转换为应用程序可理解的格式
 */
export class UserCliAdapter {
  constructor(private port: IUserRegistrationPort) {}

  async register(args: string[]): Promise<void> {
    // 将 CLI 参数转换为 Port 请求格式
    const portRequest: RegisterUserRequest = {
      email: args[0],
      password: args[1],
      firstName: args[2],
      lastName: args[3],
      dateOfBirth: new Date(args[4])
    };

    // 调用 Port
    const response = await this.port.register(portRequest);

    // 将 Port 响应转换为 CLI 输出格式
    if (response.success) {
      console.log(`✓ User registered successfully. ID: ${response.userId}`);
    } else {
      console.error(`✗ Registration failed: ${response.error}`);
      process.exit(1);
    }
  }
}

/**
 * Driving Adapter: Message Queue Consumer
 * 将消息队列消息转换为应用程序可理解的格式
 */
export class UserMessageQueueAdapter {
  constructor(private port: IUserRegistrationPort) {}

  async handleMessage(message: any): Promise<void> {
    // 将消息队列消息转换为 Port 请求格式
    const portRequest: RegisterUserRequest = {
      email: message.payload.email,
      password: message.payload.password,
      firstName: message.payload.firstName,
      lastName: message.payload.lastName,
      dateOfBirth: new Date(message.payload.dateOfBirth)
    };

    // 调用 Port
    const response = await this.port.register(portRequest);

    // 将 Port 响应转换为消息队列确认格式
    if (response.success) {
      await message.ack();
    } else {
      await message.nack();
    }
  }
}

// ============================================================
// DRIVEN ADAPTERS (Secondary Adapters)
// 被应用程序驱动的适配器 - 输出适配器
// ============================================================

/**
 * Driven Adapter: PostgreSQL Repository
 * 实现用户数据存储 Port
 */
export class PostgresUserRepositoryAdapter implements IUserRepositoryPort {
  constructor(private db: any) {}

  async save(user: User): Promise<void> {
    await this.db.query(
      'INSERT INTO users (id, email, password_hash, first_name, last_name, date_of_birth) VALUES ($1, $2, $3, $4, $5, $6)',
      [
        user.id,
        user.email,
        user.passwordHash,
        user.firstName,
        user.lastName,
        user.dateOfBirth
      ]
    );
  }

  async findById(id: string): Promise<User | null> {
    const row = await this.db.query('SELECT * FROM users WHERE id = $1', [id]);
    if (!row) return null;

    return {
      id: row.id,
      email: row.email,
      passwordHash: row.password_hash,
      firstName: row.first_name,
      lastName: row.last_name,
      dateOfBirth: new Date(row.date_of_birth)
    };
  }

  async findByEmail(email: string): Promise<User | null> {
    const row = await this.db.query('SELECT * FROM users WHERE email = $1', [email]);
    if (!row) return null;

    return {
      id: row.id,
      email: row.email,
      passwordHash: row.password_hash,
      firstName: row.first_name,
      lastName: row.last_name,
      dateOfBirth: new Date(row.date_of_birth)
    };
  }
}

/**
 * Driven Adapter: MongoDB Repository
 * 另一个用户数据存储实现
 */
export class MongoUserRepositoryAdapter implements IUserRepositoryPort {
  constructor(private client: any) {}

  async save(user: User): Promise<void> {
    await this.client.db().collection('users').insertOne(user);
  }

  async findById(id: string): Promise<User | null> {
    return await this.client.db().collection('users').findOne({ id });
  }

  async findByEmail(email: string): Promise<User | null> {
    return await this.client.db().collection('users').findOne({ email });
  }
}

/**
 * Driven Adapter: Email Service
 * 实现邮件发送 Port
 */
export class SendGridEmailAdapter implements IEmailSenderPort {
  constructor(private apiKey: string) {}

  async sendWelcomeEmail(to: string, userName: string): Promise<void> {
    // 调用 SendGrid API
    console.log(`Sending welcome email to ${to} via SendGrid`);
  }
}

/**
 * Driven Adapter: Event Publisher
 * 实现事件发布 Port
 */
export class KafkaEventPublisherAdapter implements IEventPublisherPort {
  constructor(private producer: any) {}

  async publish(event: DomainEvent): Promise<void> {
    // 发布到 Kafka
    await this.producer.send({
      topic: 'domain-events',
      messages: [{ value: JSON.stringify(event) }]
    });
  }
}
```

### 20.2.3 应用程序核心 (Application Core)

```typescript
/**
 * Application Core: 不依赖任何外部技术
 * 只包含业务逻辑和 Port 定义
 */

// ============================================================
// DOMAIN MODEL
// ============================================================

export interface User {
  id: string;
  email: string;
  passwordHash: string;
  firstName: string;
  lastName: string;
  dateOfBirth: Date;
}

export interface DomainEvent {
  type: string;
  occurredAt: Date;
  data: any;
}

// ============================================================
// APPLICATION SERVICES
// ============================================================

/**
 * Application Service: 用户注册服务
 * 实现 Driving Port，使用 Driven Ports
 */
export class UserRegistrationService implements IUserRegistrationPort {
  constructor(
    private userRepository: IUserRepositoryPort,
    private emailSender: IEmailSenderPort,
    private eventPublisher: IEventPublisherPort
  ) {}

  async register(request: RegisterUserRequest): Promise<RegisterUserResponse> {
    // 1. 业务规则验证
    if (!this.isValidEmail(request.email)) {
      return { success: false, error: 'Invalid email' };
    }

    if (!this.isPasswordStrong(request.password)) {
      return { success: false, error: 'Weak password' };
    }

    if (!this.isAdult(request.dateOfBirth)) {
      return { success: false, error: 'Must be 18 or older' };
    }

    // 2. 检查用户是否已存在
    const existingUser = await this.userRepository.findByEmail(request.email);
    if (existingUser) {
      return { success: false, error: 'User already exists' };
    }

    // 3. 创建用户
    const user: User = {
      id: this.generateId(),
      email: request.email,
      passwordHash: this.hashPassword(request.password),
      firstName: request.firstName,
      lastName: request.lastName,
      dateOfBirth: request.dateOfBirth
    };

    // 4. 保存用户
    await this.userRepository.save(user);

    // 5. 发送欢迎邮件
    await this.emailSender.sendWelcomeEmail(user.email, user.firstName);

    // 6. 发布领域事件
    await this.eventPublisher.publish({
      type: 'UserRegistered',
      occurredAt: new Date(),
      data: { userId: user.id, email: user.email }
    });

    return {
      success: true,
      userId: user.id
    };
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  private isPasswordStrong(password: string): boolean {
    const strongRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
    return strongRegex.test(password);
  }

  private isAdult(dateOfBirth: Date): boolean {
    const today = new Date();
    const age = today.getFullYear() - dateOfBirth.getFullYear();
    return age >= 18;
  }

  private generateId(): string {
    return Math.random().toString(36).substring(7);
  }

  private hashPassword(password: string): string {
    return 'hashed_' + password;
  }
}
```

### 20.2.4 六边形架构的优势

```typescript
/**
 * 六边形架构的优势演示
 */

// 1. 可以轻松替换外部技术
// 不需要修改 Application Core

// 从 PostgreSQL 切换到 MongoDB
const postgresAdapter = new PostgresUserRepositoryAdapter(postgresDb);
const mongoAdapter = new MongoUserRepositoryAdapter(mongoClient);

// 使用相同的 Application Service
const serviceWithPostgres = new UserRegistrationService(
  postgresAdapter,
  emailSender,
  eventPublisher
);

const serviceWithMongo = new UserRegistrationService(
  mongoAdapter,
  emailSender,
  eventPublisher
);

// 2. 可以同时支持多种输入方式
const httpAdapter = new UserHttpAdapter(userRegistrationService);
const cliAdapter = new UserCliAdapter(userRegistrationService);
const mqAdapter = new UserMessageQueueAdapter(userRegistrationService);

// 3. 可以轻松测试
class MockUserRepositoryAdapter implements IUserRepositoryPort {
  private users: Map<string, User> = new Map();

  async save(user: User): Promise<void> {
    this.users.set(user.id, user);
  }

  async findByEmail(email: string): Promise<User | null> {
    for (const user of this.users.values()) {
      if (user.email === email) return user;
    }
    return null;
  }

  async findById(id: string): Promise<User | null> {
    return this.users.get(id) || null;
  }
}
```

---

## 20.3 架构模式对比

### 20.3.1 整洁架构 vs 洋葱架构 vs 六边形架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      整洁架构 (Clean)                            │
├─────────────────────────────────────────────────────────────────┤
│  • 强调 Entities 和 Use Cases 的分离                             │
│  • 依赖规则：源代码依赖由外向内                                   │
│  • 同心圆模型                                                    │
│  • 适合：复杂业务逻辑的应用                                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      洋葱架构 (Onion)                            │
├─────────────────────────────────────────────────────────────────┤
│  • 强调 Domain 的层次划分                                        │
│  • 依赖规则：外层依赖内层                                         │
│  • 同心圆模型（与 Clean 类似）                                   │
│  • 适合：DDD (Domain-Driven Design) 项目                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┤
│                  六边形架构 (Hexagonal)                          │
├─────────────────────────────────────────────────────────────────┤
│  • 强调 Ports 和 Adapters 的概念                                 │
│  • 依赖规则：通过 Port 接口解耦                                  │
│  • 六边形模型                                                    │
│  • 适合：需要多种输入/输出的应用                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 20.3.2 核心共同点

| 特性 | 整洁架构 | 洋葱架构 | 六边形架构 |
|------|----------|----------|------------|
| **依赖倒置** | ✅ | ✅ | ✅ |
| **核心业务逻辑独立** | ✅ | ✅ | ✅ |
| **可测试性** | ✅ | ✅ | ✅ |
| **框架独立性** | ✅ | ✅ | ✅ |
| **关注点分离** | ✅ | ✅ | ✅ |

### 20.3.3 如何选择

```
选择决策树：

开始
  │
  ├─ 你的项目使用 DDD (Domain-Driven Design) 吗？
  │   ├─ 是 → 洋葱架构
  │   └─ 否 ↓
  │
  ├─ 你需要支持多种输入/输出方式吗？
  │   ├─ 是 → 六边形架构
  │   └─ 否 ↓
  │
  └─ 默认选择：整洁架构
      （最通用，适合大多数项目）
```

---

## 20.4 实际项目应用：mybatis-boost

```typescript
/**
 * mybatis-boost 中的六边形架构应用
 */

// ============================================================
// APPLICATION CORE
// ============================================================

/**
 * Port: 导航服务接口
 */
export interface INavigationServicePort {
  findNavigation(sourceFile: string, position: Position): Promise<NavigationResult>;
}

export interface Position {
  line: number;
  character: number;
}

export interface NavigationResult {
  targetUri: string;
  targetRange: Range;
}

/**
 * Port: 文件访问接口
 */
export interface IFileAccessPort {
  readFile(path: string): Promise<string>;
  fileExists(path: string): Promise<boolean>;
  findFiles(pattern: string): Promise<string[]>;
  watchFile(pattern: string, callback: FileChangeCallback): Disposable;
}

export interface FileChangeCallback {
  (uri: string, changeType: FileChangeType): void;
}

export enum FileChangeType {
  Created = 1,
  Changed = 2,
  Deleted = 3
}

export interface Disposable {
  dispose(): void;
}

/**
 * Application Service: 导航服务
 */
export class NavigationService implements INavigationServicePort {
  constructor(
    private fileAccess: IFileAccessPort,
    private javaParser: IJavaParserPort,
    private xmlParser: IXmlParserPort,
    private cache: ICachePort
  ) {}

  async findNavigation(sourceFile: string, position: Position): Promise<NavigationResult> {
    // 1. 检查缓存
    const cacheKey = `${sourceFile}:${position.line}:${position.character}`;
    const cached = await this.cache.get(cacheKey);
    if (cached) {
      return cached;
    }

    // 2. 读取源文件
    const content = await this.fileAccess.readFile(sourceFile);

    // 3. 解析
    let parseResult;
    if (sourceFile.endsWith('.java')) {
      parseResult = await this.javaParser.parse(content, position);
    } else if (sourceFile.endsWith('.xml')) {
      parseResult = await this.xmlParser.parse(content, position);
    }

    // 4. 查找目标文件
    const targetUri = await this.findTarget(parseResult);

    // 5. 构建结果
    const result: NavigationResult = {
      targetUri: targetUri,
      targetRange: parseResult.targetRange
    };

    // 6. 缓存结果
    await this.cache.set(cacheKey, result);

    return result;
  }

  private async findTarget(parseResult: any): Promise<string> {
    // 查找目标文件的业务逻辑
    // ...
    return '';
  }
}

/**
 * Port: 解析器接口
 */
export interface IJavaParserPort {
  parse(content: string, position: Position): Promise<ParseResult>;
}

export interface IXmlParserPort {
  parse(content: string, position: Position): Promise<ParseResult>;
}

export interface ParseResult {
  targetRange: Range;
  identifier: string;
  type: string;
}

export interface Range {
  start: Position;
  end: Position;
}

/**
 * Port: 缓存接口
 */
export interface ICachePort {
  get(key: string): Promise<NavigationResult | undefined>;
  set(key: string, value: NavigationResult): Promise<void>;
  invalidate(pattern: string): Promise<void>;
}

// ============================================================
// ADAPTERS
// ============================================================

/**
 * Driving Adapter: VS Code Definition Provider
 * 将 VS Code API 调用转换为导航服务调用
 */
import * as vscode from 'vscode';

export class VSCodeDefinitionAdapter implements vscode.DefinitionProvider {
  constructor(private navigationService: INavigationServicePort) {}

  async provideDefinition(
    document: vscode.TextDocument,
    position: vscode.Position,
    token: vscode.CancellationToken
  ): Promise<vscode.Definition> {
    // 将 VS Code 请求转换为 Port 请求
    const portRequest: Position = {
      line: position.line,
      character: position.character
    };

    // 调用 Port
    const result = await this.navigationService.findNavigation(
      document.uri.fsPath,
      portRequest
    );

    // 将 Port 响应转换为 VS Code 定义
    const uri = vscode.Uri.file(result.targetUri);
    const range = new vscode.Range(
      result.targetRange.start.line,
      result.targetRange.start.character,
      result.targetRange.end.line,
      result.targetRange.end.character
    );

    return new vscode.Location(uri, range);
  }
}

/**
 * Driven Adapter: VS Code File System
 * 实现 VS Code 文件系统访问
 */
export class VSCodeFileAccessAdapter implements IFileAccessPort {
  async readFile(path: string): Promise<string> {
    const uri = vscode.Uri.file(path);
    const content = await vscode.workspace.fs.readFile(uri);
    return Buffer.from(content).toString('utf8');
  }

  async fileExists(path: string): Promise<boolean> {
    try {
      await vscode.workspace.fs.stat(vscode.Uri.file(path));
      return true;
    } catch {
      return false;
    }
  }

  async findFiles(pattern: string): Promise<string[]> {
    const files = await vscode.workspace.findFiles(pattern);
    return files.map(f => f.fsPath);
  }

  watchFile(pattern: string, callback: FileChangeCallback): Disposable {
    const watcher = vscode.workspace.createFileSystemWatcher(pattern);

    watcher.onDidChange(uri => callback(uri.fsPath, FileChangeType.Changed));
    watcher.onDidCreate(uri => callback(uri.fsPath, FileChangeType.Created));
    watcher.onDidDelete(uri => callback(uri.fsPath, FileChangeType.Deleted));

    return {
      dispose: () => watcher.dispose()
    };
  }
}

/**
 * Driven Adapter: MyBatis Java Parser
 * 实现 Java 解析器
 */
export class MyBatisJavaParserAdapter implements IJavaParserPort {
  async parse(content: string, position: Position): Promise<ParseResult> {
    // 具体的 MyBatis Java 解析逻辑
    // ...
    return {
      targetRange: {
        start: { line: 0, character: 0 },
        end: { line: 0, character: 0 }
      },
      identifier: '',
      type: ''
    };
  }
}

/**
 * Driven Adapter: MyBatis XML Parser
 * 实现 XML 解析器
 */
export class MyBatisXmlParserAdapter implements IXmlParserPort {
  async parse(content: string, position: Position): Promise<ParseResult> {
    // 具体的 MyBatis XML 解析逻辑
    // ...
    return {
      targetRange: {
        start: { line: 0, character: 0 },
        end: { line: 0, character: 0 }
      },
      identifier: '',
      type: ''
    };
  }
}

/**
 * Driven Adapter: LRU Cache
 * 实现 LRU 缓存
 */
import { LRUCache } from 'lru-cache';

export class LRUCacheAdapter implements ICachePort {
  private cache = new LRUCache<string, NavigationResult>({
    max: 5000,
    ttl: 1000 * 60 * 30  // 30 minutes
  });

  async get(key: string): Promise<NavigationResult | undefined> {
    return this.cache.get(key);
  }

  async set(key: string, value: NavigationResult): Promise<void> {
    this.cache.set(key, value);
  }

  async invalidate(pattern: string): Promise<void> {
    // 删除匹配模式的所有缓存
    for (const key of this.cache.keys()) {
      if (key.startsWith(pattern)) {
        this.cache.delete(key);
      }
    }
  }
}

// ============================================================
// COMPOSITION ROOT
// ============================================================

/**
 * 组装应用程序
 */
export function composeApplication(): vscode.DefinitionProvider {
  // Driven Adapters
  const fileAccess = new VSCodeFileAccessAdapter();
  const javaParser = new MyBatisJavaParserAdapter();
  const xmlParser = new MyBatisXmlParserAdapter();
  const cache = new LRUCacheAdapter();

  // Application Service
  const navigationService = new NavigationService(
    fileAccess,
    javaParser,
    xmlParser,
    cache
  );

  // Driving Adapter
  return new VSCodeDefinitionAdapter(navigationService);
}
```

---

## 20.5 使用 Claude Code 应用这些架构

### 20.5.1 配置 CLAUDE.md

```markdown
# CLAUDE.md

## 项目架构

本项目使用**六边形架构** (Hexagonal Architecture)。

### 核心原则

1. **应用程序核心** (`src/core/`) - 不依赖任何外部技术
   - 定义 Port 接口
   - 实现业务逻辑

2. **Adapters** (`src/adapters/`) - 连接外部技术
   - **Driving Adapters**: HTTP, CLI, Message Queue
   - **Driven Adapters**: Database, Email, Cache

### 依赖规则

- ✅ 应用程序核心 → 依赖 Port 接口（自身定义）
- ✅ Adapters → 实现 Port 接口
- ❌ 应用程序核心 → 不依赖任何 Adapter

### 文件组织

```
src/
├── core/                          # 应用程序核心
│   ├── ports/                     # Port 接口定义
│   │   ├── driving/               # 输入端口
│   │   └── driven/                # 输出端口
│   ├── domain/                    # 领域模型
│   └── services/                  # 应用服务
└── adapters/                      # 适配器
    ├── driving/                   # 输入适配器
    │   ├── http/
    │   ├── cli/
    │   └── message-queue/
    └── driven/                    # 输出适配器
        ├── database/
        ├── email/
        └── cache/
```

### 编码规范

- 在 `core/` 中**禁止**导入任何外部框架代码
- 所有外部依赖必须通过 Port 接口访问
- Adapter 只负责格式转换，不包含业务逻辑
```

### 20.5.2 使用 Plan Mode 设计新功能

```bash
# 激活 Plan Mode
Shift+Tab (两次)

# 任务描述：
创建用户评论功能，需要支持：
- HTTP REST API
- CLI 命令
- PostgreSQL 存储

# Claude 会：
1. 识别需要创建的 Ports
2. 设计 Application Service
3. 规划所需的 Adapters
4. 确保依赖方向正确
```

---

## 20.6 常见陷阱

### 陷阱 1：Port 包含技术细节

```typescript
// ❌ 错误：Port 包含了 HTTP 相关的技术细节
// src/ports/driving/IUserRegistrationPort.ts
import { Request } from 'express'; // ❌ 错误！

export interface IUserRegistrationPort {
  register(req: Request): Promise<Response>; // ❌ 错误！
}

// ✅ 正确：Port 只包含业务相关的定义
// src/ports/driving/IUserRegistrationPort.ts
export interface IUserRegistrationPort {
  register(request: RegisterUserRequest): Promise<RegisterUserResponse>;
}

export interface RegisterUserRequest {
  email: string;
  password: string;
}

export interface RegisterUserResponse {
  success: boolean;
  userId?: string;
}
```

### 陷阱 2：Adapter 包含业务逻辑

```typescript
// ❌ 错误：Adapter 包含了业务逻辑
// src/adapters/driving/http/UserHttpAdapter.ts
export class UserHttpAdapter {
  async register(req: Request, res: Response): Promise<void> {
    // ❌ 错误：业务验证应该在 Application Core
    if (!this.isValidEmail(req.body.email)) {
      return res.status(400).json({ error: 'Invalid email' });
    }

    // ...
  }

  private isValidEmail(email: string): boolean { // ❌ 错误！
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }
}

// ✅ 正确：Adapter 只负责格式转换
// src/adapters/driving/http/UserHttpAdapter.ts
export class UserHttpAdapter {
  constructor(private port: IUserRegistrationPort) {}

  async register(req: Request, res: Response): Promise<void> {
    // ✅ 正确：只做格式转换
    const portRequest: RegisterUserRequest = {
      email: req.body.email,
      password: req.body.password
    };

    const response = await this.port.register(portRequest);

    // ✅ 正确：只做格式转换
    if (response.success) {
      res.status(201).json({ userId: response.userId });
    } else {
      res.status(400).json({ error: response.error });
    }
  }
}
```

### 陷阱 3：直接在 Adapter 中使用多个实现

```typescript
// ❌ 错误：Adapter 直接依赖多个具体实现
// src/core/services/UserService.ts
import { PostgresRepository } from '../adapters/driven/database/PostgresRepository'; // ❌ 错误！
import { SendGridEmailer } from '../adapters/driven/email/SendGridEmailer'; // ❌ 错误！

export class UserService {
  private userRepository = new PostgresRepository(); // ❌ 错误！
  private emailer = new SendGridEmailer(); // ❌ 错误！
}

// ✅ 正确：依赖 Port 接口，通过构造函数注入
// src/core/services/UserService.ts
import { IUserRepositoryPort } from '../ports/driven/IUserRepositoryPort';
import { IEmailSenderPort } from '../ports/driven/IEmailSenderPort';

export class UserService {
  constructor(
    private userRepository: IUserRepositoryPort, // ✅ 正确！
    private emailer: IEmailSenderPort // ✅ 正确！
  ) {}
}
```

---

## 20.7 练习

### 练习 1：识别 Ports 和 Adapters

给定以下代码，识别哪些是 Ports，哪些是 Adapters：

```typescript
// A
export interface IOrderRepositoryPort {
  save(order: Order): Promise<void>;
  findById(id: string): Promise<Order>;
}

// B
export class OrderHttpController {
  constructor(private orderService: IOrderServicePort) {}

  async createOrder(req: Request, res: Response): Promise<void> {
    const request = { /* ... */ };
    const result = await this.orderService.createOrder(request);
    res.json(result);
  }
}

// C
export class OrderService implements IOrderServicePort {
  constructor(private repository: IOrderRepositoryPort) {}

  async createOrder(request: CreateOrderRequest): Promise<CreateOrderResponse> {
    // 业务逻辑
  }
}

// D
export class MongoOrderRepository implements IOrderRepositoryPort {
  async save(order: Order): Promise<void> {
    await this.collection.insertOne(order);
  }
}
```

**答案**：
- A → Driven Port（输出端口）
- B → Driving Adapter（输入适配器）
- C → Application Service（实现 Driving Port）
- D → Driven Adapter（输出适配器）

### 练习 2：设计六边形架构

为一个"博客文章评论"功能设计六边形架构，需要支持：
- HTTP REST API
- Admin CLI
- MongoDB 存储
- Email 通知

**提示**：
1. 定义所需的 Ports
2. 设计 Application Service
3. 规划所需的 Adapters

---

## 20.8 进一步阅读

- [Hexagonal Architecture by Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
- [Onion Architecture by Jeffrey Palermo](https://jeffreypalermo.com/2008/07/the-onion-architecture-part-1/)
- [Chapter 21: 可测试性与 Mocking](chapter-21-testability-mocking.md) - 下一章

---

## 视频脚本

### Episode 20: 洋葱架构与六边形架构 (18 分钟)

#### [0:00-1:00] 引入
**视觉元素**：
- 标题："三种架构，同一核心"
- 架构对比图

**内容**：
> 上章我们学习了整洁架构。今天我们看看另外两个重要的架构模式：洋葱架构和六边形架构。它们看起来不同，但核心思想是一致的：让业务逻辑独立于外部技术。

#### [1:00-3:00] 洋葱架构
**视觉元素**：
- 洋葱架构分层图
- 与整洁架构对照

**内容**：
> 洋葱架构由 Jeffrey Palermo 提出，和整洁架构几乎一样，只是术语不同。核心是 Domain，外层是 Domain Services，再外层是 Application Services，最外层是 Infrastructure。
>
> 洋葱架构特别适合 DDD (Domain-Driven Design) 项目，因为它强调 Domain 的层次划分。

#### [3:00-8:00] 六边形架构
**视觉元素**：
- 六边形架构图
- Ports 和 Adapters 动画

**内容**：
> 六边形架构由 Alistair Cockburn 提出，也叫 Ports and Adapters 架构。
>
> 核心概念是：
> - **Port**: 应用程序定义的接口
> - **Adapter**: 实现 Port 的具体技术
>
> [演示：创建六边形架构的用户注册系统]
>
> 注意看，Application Core 不知道 HTTP 的存在，不知道 PostgreSQL 的存在。它只知道 IEmailSenderPort 和 IUserRepositoryPort 接口。
>
> 这意味着我们可以轻松替换：
> - PostgreSQL → MongoDB
> - SendGrid → AWS SES
> - HTTP API → CLI → Message Queue
>
> 都不需要修改 Application Core！

#### [8:00-12:00] 架构对比
**视觉元素**：
- 三种架构并列对比表
- 选择决策树

**内容**：
> [演示：对比三种架构的差异]
>
> 三种架构的核心共同点：
> - 依赖倒置
> - 业务逻辑独立
> - 可测试
> - 框架独立
>
> 如何选择？
> - DDD 项目 → 洋葱架构
> - 多输入/输出 → 六边形架构
> - 默认选择 → 整洁架构

#### [12:00-16:00] mybatis-boost 实战
**视觉元素**：
- mybatis-boost 六边形架构图
- 代码展示

**内容**：
> [演示：查看 mybatis-boost 的架构]
>
> mybatis-boost 使用六边形架构：
> - **NavigationService**: Application Core
> - **INavigationServicePort**: Driving Port
> - **IFileAccessPort**: Driven Port
> - **VSCodeDefinitionAdapter**: Driving Adapter
> - **VSCodeFileAccessAdapter**: Driven Adapter
>
> 这种架构让 mybatis-boost 可以支持不同的文件系统、不同的解析器，而不影响核心导航逻辑。

#### [16:00-18:00] 总结
**视觉元素**：
- 关键要点列表
- Next Chapter 预告

**内容**：
> 三种架构，同一核心：
> - 整洁架构：强调 Entities 和 Use Cases
> - 洋葱架构：强调 Domain 层次
> - 六边形架构：强调 Ports 和 Adapters
>
> 选择适合你的架构，但记住：**让业务逻辑独立于外部技术**是所有架构的核心目标。
>
> 下一章，我们将学习可测试性和 Mocking，看看这些架构如何让测试变得简单。
