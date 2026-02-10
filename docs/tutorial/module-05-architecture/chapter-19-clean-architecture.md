# Chapter 19: 整洁架构原则

## 学习目标

完成本章后，你将能够：

- 理解 Robert C. Martin (Uncle Bob) 的整洁架构核心原则
- 识别依赖规则和层次结构
- 将整洁架构应用于实际项目
- 理解如何让 Claude Code 遵循架构约束

## 前置知识

- [Chapter 14: mybatis-boost 项目概览](../module-04-real-world-mybatis-boost/chapter-14-project-overview.md)
- 基本的项目结构和模块化概念
- 依赖注入的基础理解

---

## 19.1 什么是整洁架构

**整洁架构** (Clean Architecture) 是 Robert C. Martin (Uncle Bob) 提出的一种软件架构模式，其核心思想是：**将系统划分为 concentric layers (同心圆层)，依赖方向始终由外向内**。

### 核心依赖规则

```
        ┌─────────────────────────────┐
        │      Frameworks & Drivers    │  ← 最外层
        │    (Frameworks, DB, Web, etc) │
        └─────────────▲────────────────┘
                      │
        ┌─────────────┴────────────────┐
        │      Interface Adapters       │  ← 外层
        │   (Controllers, Presenters)   │
        └─────────────▲────────────────┘
                      │
        ┌─────────────┴────────────────┐
        │      Use Cases (App Business) │  ← 中间层
        │      (Application Specific)   │
        └─────────────▲────────────────┘
                      │
        ┌─────────────┴────────────────┐
        │      Entities (Enterprise)    │  ← 最内层
        │      (Core Business Rules)    │
        └─────────────────────────────┘

    ↑ 依赖方向：外层依赖内层
    ↑ 数据流向：内层 → 外层
```

### 关键原则

| 原则 | 说明 | 应用示例 |
|------|------|----------|
| **依赖规则** | 源代码依赖只能指向内部 | Entities 不依赖任何框架 |
| **隔离原则** | 每层独立于其他层 | 可替换 UI 框架不影响业务逻辑 |
| **边界原则** | 层与层之间通过接口通信 | Use Cases 定义接口 |
| **数据原则** | 数据格式由内层定义 | Entities 定义数据结构 |

---

## 19.2 整洁架构的层次结构

### 19.2.1 Entities (实体层) - 最内层

**职责**：封装企业级业务规则

```typescript
/**
 * Entity: 最内层的业务实体
 * - 不依赖任何框架、数据库、UI
 * - 只包含纯业务逻辑
 */

export interface User {
  id: string;
  name: string;
  email: string;
  createdAt: Date;
}

/**
 * 业务规则：企业级的通用规则
 * - 跨应用使用
 * - 最少变化
 */
export class UserEntity {
  /**
   * 验证邮箱格式的业务规则
   * 这是企业规则，不依赖具体实现
   */
  static isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  /**
   * 业务规则：用户名长度限制
   */
  static isValidName(name: string): boolean {
    return name.length >= 2 && name.length <= 50;
  }

  /**
   * 业务规则：检查密码强度
   */
  static isPasswordStrong(password: string): boolean {
    // 至少 8 位，包含大小写字母和数字
    const strongRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
    return strongRegex.test(password);
  }
}
```

### 19.2.2 Use Cases (用例层) - 应用业务规则

**职责**：封装应用特定的业务规则

```typescript
/**
 * Use Case: 应用层的业务逻辑
 * - 依赖 Entity（内层）
 * - 被外层依赖
 * - 不依赖框架、数据库、UI
 */

import { User, UserEntity } from './entities/User';

/**
 * Input Boundary: 用例的输入接口
 * 由外层实现，定义外层如何调用内层
 */
export interface RegisterUserInputBoundary {
  register(request: RegisterUserRequest): Promise<RegisterUserResponse>;
}

/**
 * Request/Response Models: 数据结构由内层定义
 */
export interface RegisterUserRequest {
  name: string;
  email: string;
  password: string;
}

export interface RegisterUserResponse {
  success: boolean;
  user?: User;
  error?: string;
}

/**
 * Output Boundary: 用例的输出接口
 * 由外层实现，定义内层如何向外层传递数据
 */
export interface RegisterUserOutputBoundary {
  present(response: RegisterUserResponse): void;
}

/**
 * Use Case Implementation: 具体的应用业务逻辑
 */
export class RegisterUserUseCase implements RegisterUserInputBoundary {
  private readonly userGateway: UserGateway;
  private readonly outputBoundary: RegisterUserOutputBoundary;

  constructor(
    userGateway: UserGateway,
    outputBoundary: RegisterUserOutputBoundary
  ) {
    this.userGateway = userGateway;
    this.outputBoundary = outputBoundary;
  }

  async register(request: RegisterUserRequest): Promise<RegisterUserResponse> {
    // 1. 输入验证（应用业务规则）
    if (!UserEntity.isValidName(request.name)) {
      return { success: false, error: 'Invalid name' };
    }

    if (!UserEntity.isValidEmail(request.email)) {
      return { success: false, error: 'Invalid email' };
    }

    if (!UserEntity.isPasswordStrong(request.password)) {
      return { success: false, error: 'Weak password' };
    }

    // 2. 检查用户是否存在（应用业务规则）
    const existingUser = await this.userGateway.findByEmail(request.email);
    if (existingUser) {
      return { success: false, error: 'User already exists' };
    }

    // 3. 创建新用户（应用业务规则）
    const hashedPassword = await this.hashPassword(request.password);
    const newUser: User = {
      id: this.generateId(),
      name: request.name,
      email: request.email,
      createdAt: new Date()
    };

    // 4. 保存用户
    await this.userGateway.save(newUser, hashedPassword);

    // 5. 返回结果
    const response: RegisterUserResponse = {
      success: true,
      user: newUser
    };

    // 6. 通知输出边界
    this.outputBoundary.present(response);

    return response;
  }

  // 私有辅助方法
  private async hashPassword(password: string): Promise<string> {
    // 实际实现会在 Infrastructure 层
    return 'hashed_' + password;
  }

  private generateId(): string {
    return Math.random().toString(36).substring(7);
  }
}

/**
 * Gateway Interface: 数据访问接口由内层定义
 * 由外层实现具体的存储方式
 */
export interface UserGateway {
  findByEmail(email: string): Promise<User | null>;
  save(user: User, hashedPassword: string): Promise<void>;
}
```

### 19.2.3 Interface Adapters (接口适配器层)

**职责**：将数据从外层格式转换为内层格式

```typescript
/**
 * Interface Adapter: 控制器
 * - 接收外部请求（HTTP、CLI 等）
 * - 调用 Use Case
 */

import { Request, Response } from 'express'; // 外层框架
import {
  RegisterUserInputBoundary,
  RegisterUserRequest
} from '../use-cases/RegisterUserUseCase';

/**
 * Controller: 将 HTTP 请求转换为 Use Case 请求
 */
export class RegisterUserController {
  private readonly useCase: RegisterUserInputBoundary;

  constructor(useCase: RegisterUserInputBoundary) {
    this.useCase = useCase;
  }

  /**
   * 处理 HTTP POST /register 请求
   */
  async handle(request: Request, response: Response): Promise<void> {
    try {
      // 1. 从 HTTP 请求提取数据
      const httpRequest = {
        name: request.body.name,
        email: request.body.email,
        password: request.body.password
      };

      // 2. 转换为 Use Case 请求格式
      const useCaseRequest: RegisterUserRequest = {
        name: httpRequest.name,
        email: httpRequest.email,
        password: httpRequest.password
      };

      // 3. 调用 Use Case
      const useCaseResponse = await this.useCase.register(useCaseRequest);

      // 4. 转换为 HTTP 响应格式
      if (useCaseResponse.success) {
        response.status(201).json({
          user: useCaseResponse.user
        });
      } else {
        response.status(400).json({
          error: useCaseResponse.error
        });
      }
    } catch (error) {
      response.status(500).json({
        error: 'Internal server error'
      });
    }
  }
}

/**
 * Presenter: 将 Use Case 响应转换为可显示格式
 */
export class RegisterUserPresenter implements RegisterUserOutputBoundary {
  private viewModel: any;

  present(response: RegisterUserResponse): void {
    // 转换为视图模型格式
    this.viewModel = {
      success: response.success,
      message: response.success
        ? `Welcome, ${response.user?.name}!`
        : response.error,
      user: response.user
    };
  }

  getViewModel(): any {
    return this.viewModel;
  }
}
```

### 19.2.4 Frameworks & Drivers (框架和驱动层) - 最外层

**职责**：外部工具和框架

```typescript
/**
 * Framework & Driver: 数据库实现
 * - 实现 Gateway 接口
 * - 使用具体的技术栈
 */

import { User, UserGateway } from '../use-cases/RegisterUserUseCase';
import { Database } from 'some-database-framework'; // 外层框架

/**
 * Database Gateway Implementation: 具体的数据库实现
 */
export class DatabaseUserGateway implements UserGateway {
  private readonly db: Database;

  constructor(db: Database) {
    this.db = db;
  }

  async findByEmail(email: string): Promise<User | null> {
    const row = await this.db.query(
      'SELECT * FROM users WHERE email = ?',
      [email]
    );

    if (!row) return null;

    return {
      id: row.id,
      name: row.name,
      email: row.email,
      createdAt: new Date(row.created_at)
    };
  }

  async save(user: User, hashedPassword: string): Promise<void> {
    await this.db.query(
      'INSERT INTO users (id, name, email, password, created_at) VALUES (?, ?, ?, ?, ?)',
      [user.id, user.name, user.email, hashedPassword, user.createdAt]
    );
  }
}

/**
 * Framework: Express 应用设置
 */
import express from 'express';
import { RegisterUserController } from '../adapters/RegisterUserController';
import { RegisterUserPresenter } from '../adapters/RegisterUserPresenter';

export function createApp(
  useCase: RegisterUserInputBoundary
): express.Application {
  const app = express();

  app.use(express.json());

  const presenter = new RegisterUserPresenter();
  const controller = new RegisterUserController(useCase);

  // 依赖注入：将 presenter 注入到 use case
  useCase.setOutputBoundary(presenter);

  app.post('/register', (req, res) => controller.handle(req, res));

  return app;
}
```

---

## 19.3 整洁架构的优势

### 19.3.1 可测试性

```typescript
/**
 * 测试 Use Case 时，不需要数据库、HTTP 等
 * 只需要 mock Gateway 接口
 */

import { assert } from 'chai';
import { RegisterUserUseCase, UserGateway } from './RegisterUserUseCase';

class MockUserGateway implements UserGateway {
  private users: Map<string, any> = new Map();

  async findByEmail(email: string): Promise<any> {
    return this.users.get(email) || null;
  }

  async save(user: any, hashedPassword: string): Promise<void> {
    this.users.set(user.email, { user, hashedPassword });
  }
}

suite('RegisterUserUseCase', () => {
  test('should register a new user', async () => {
    // Arrange
    const mockGateway = new MockUserGateway();
    const mockPresenter = {
      present: (response: any) => {}
    };
    const useCase = new RegisterUserUseCase(mockGateway, mockPresenter);

    const request = {
      name: 'John Doe',
      email: 'john@example.com',
      password: 'StrongPass123'
    };

    // Act
    const response = await useCase.register(request);

    // Assert
    assert.isTrue(response.success);
    assert.isDefined(response.user);
    assert.equal(response.user?.email, 'john@example.com');
  });
});
```

### 19.3.2 框架独立性

```typescript
/**
 * 同一个 Use Case 可以用于：
 * - REST API
 * - GraphQL API
 * - CLI 工具
 * - 消息队列消费者
 */

// REST API
const restController = new RegisterUserController(registerUserUseCase);
app.post('/register', (req, res) => restController.handle(req, res));

// GraphQL
const graphqlResolver = {
  Mutation: {
    register: (_, args) => registerUserUseCase.register(args.input)
  }
};

// CLI
const cliCommand = async (args: string[]) => {
  const request = {
    name: args[0],
    email: args[1],
    password: args[2]
  };
  const response = await registerUserUseCase.register(request);
  console.log(response.success ? 'Success!' : response.error);
};

// Message Queue
const messageHandler = async (message: any) => {
  await registerUserUseCase.register(message.payload);
};
```

### 19.3.3 数据库独立性

```typescript
/**
 * 同一个 Use Case 可以配合：
 * - PostgreSQL
 * - MongoDB
 * - Redis
 * - 文件系统
 */

// PostgreSQL
const postgresGateway = new DatabaseUserGateway(postgresDB);

// MongoDB
const mongoGateway = new MongoUserGateway(mongoClient);

// Redis
const redisGateway = new RedisUserGateway(redisClient);

// 文件系统
const fileGateway = new FileUserGateway('/data/users.json');

// 都可以使用同一个 Use Case
const useCase = new RegisterUserUseCase(gateway, presenter);
```

---

## 19.4 实际项目中的应用

### 19.4.1 mybatis-boost 的架构分析

```typescript
/**
 * mybatis-boost 项目中的整洁架构应用
 */

// ========== Entity Layer ==========
/**
 * Entity: 核心业务实体
 * 不依赖 VS Code API、不依赖文件系统
 */
export interface MappingResult {
  source: string;        // 源文件路径
  target: string;        // 目标文件路径
  line: number;          // 目标行号
  column?: number;       // 目标列号
  type: MappingType;     // 映射类型
}

export enum MappingType {
  JAVA_TO_XML = 'java-to-xml',
  XML_TO_JAVA = 'xml-to-java'
}

/**
 * 业务规则：验证映射结果的有效性
 */
export class MappingValidator {
  static isValid(result: MappingResult): boolean {
    // 企业级业务规则：映射必须包含有效路径
    return result.source.length > 0 && result.target.length > 0;
  }
}

// ========== Use Case Layer ==========
/**
 * Gateway Interface: 由内层定义，外层实现
 */
export interface IFileGateway {
  readFile(path: string): Promise<string>;
  fileExists(path: string): Promise<boolean>;
  findFiles(pattern: string): Promise<string[]>;
}

/**
 * Parser Gateway Interface: 解析器抽象
 */
export interface IParserGateway {
  parseJavaFile(content: string): JavaParseResult;
  parseXmlFile(content: string): XmlParseResult;
}

/**
 * Use Case: 查找映射关系
 */
export class FindMappingUseCase {
  constructor(
    private fileGateway: IFileGateway,
    private parserGateway: IParserGateway
  ) {}

  async execute(javaFile: string): Promise<MappingResult[]> {
    // 1. 读取文件
    const content = await this.fileGateway.readFile(javaFile);

    // 2. 解析
    const parseResult = this.parserGateway.parseJavaFile(content);

    // 3. 应用业务规则
    const mapperName = parseResult.className + 'Mapper';
    const xmlPattern = `**/${mapperName}.xml`;

    // 4. 查找匹配文件
    const candidates = await this.fileGateway.findFiles(xmlPattern);

    // 5. 构建结果
    return candidates.map(target => ({
      source: javaFile,
      target: target,
      line: 1,
      type: MappingType.JAVA_TO_XML
    })).filter(MappingValidator.isValid);
  }
}

// ========== Interface Adapter Layer ==========
/**
 * Controller: VS Code Extension API 适配器
 */
import * as vscode from 'vscode'; // 外层框架

export class DefinitionProvider implements vscode.DefinitionProvider {
  constructor(private useCase: FindMappingUseCase) {}

  async provideDefinition(
    document: vscode.TextDocument,
    position: vscode.Position,
    token: vscode.CancellationToken
  ): Promise<vscode.Definition> {
    // 1. 从 VS Code 请求中提取数据
    const javaFile = document.uri.fsPath;

    // 2. 调用 Use Case
    const mappings = await this.useCase.execute(javaFile);

    // 3. 转换为 VS Code 定义格式
    return mappings.map(m => {
      const uri = vscode.Uri.file(m.target);
      return new vscode.Location(uri, new vscode.Position(m.line - 1, 0));
    });
  }
}

// ========== Framework & Driver Layer ==========
/**
 * Gateway Implementation: VS Code 文件系统
 */
export class VSCodeFileGateway implements IFileGateway {
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
}

/**
 * Gateway Implementation: 具体的解析器实现
 */
export class MyBatisParserGateway implements IParserGateway {
  parseJavaFile(content: string): JavaParseResult {
    // 具体的解析逻辑
    return parseJava(content);
  }

  parseXmlFile(content: string): XmlParseResult {
    // 具体的解析逻辑
    return parseMyBatisXml(content);
  }
}

// ========== 依赖注入 (Dependency Injection) ==========
/**
 * 组装所有层次
 */
export function createDefinitionProvider(): vscode.DefinitionProvider {
  // 创建外层实现
  const fileGateway = new VSCodeFileGateway();
  const parserGateway = new MyBatisParserGateway();

  // 创建 Use Case（注入外层实现）
  const useCase = new FindMappingUseCase(fileGateway, parserGateway);

  // 创建 Adapter（注入 Use Case）
  return new DefinitionProvider(useCase);
}
```

### 19.4.2 架构层次图

```
mybatis-boost Architecture:

┌───────────────────────────────────────────────────────────┐
│  Frameworks & Drivers (最外层)                             │
│  ┌─────────────────┐  ┌─────────────────────────────────┐ │
│  │ VS Code API     │  │ MyBatis XML Parser              │ │
│  │ Extension API   │  │ Concrete Implementation         │ │
│  └────────▲────────┘  └────────▲────────────────────────┘ │
└───────────│──────────────────────│─────────────────────────┘
            │                      │
┌───────────│──────────────────────│─────────────────────────┐
│  Interface Adapters (外层)                               │
│  ┌─────────┴──────────────────────────────────────────┐   │
│  │ DefinitionProvider (Go to Definition)             │   │
│  │ CodeActionProvider (Refactorings)                 │   │
│  │ CompletionItemProvider (Auto-completion)          │   │
│  └─────────▲──────────────────────────────────────────┘   │
└────────────│──────────────────────────────────────────────┘
             │
┌────────────│──────────────────────────────────────────────┐
│  Use Cases (中间层)                                       │
│  ┌─────────┴──────────────────────────────────────────┐   │
│  │ FindMappingUseCase (Core Navigation Logic)        │   │
│  │ FormatSQLUseCase (SQL Formatting)                  │   │
│  │ GenerateCodeUseCase (Code Generation)              │   │
│  └─────────▲──────────────────────────────────────────┘   │
└────────────│──────────────────────────────────────────────┘
             │
┌────────────│──────────────────────────────────────────────┐
│  Entities (最内层)                                        │
│  ┌─────────┴──────────────────────────────────────────┐   │
│  │ MappingResult, MappingType                         │   │
│  │ MappingValidator (Business Rules)                  │   │
│  │ NavigationMode (Core Abstractions)                 │   │
│  └────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────┘
```

---

## 19.5 使用 Claude Code 遵循整洁架构

### 19.5.1 配置 CLAUDE.md

```markdown
# CLAUDE.md

## 项目架构

本项目遵循**整洁架构** (Clean Architecture) 原则。

### 依赖规则

1. **Entities** (`src/core/entities/`) - 最内层
   - 只包含纯业务逻辑
   - 不依赖任何框架、数据库、外部 API

2. **Use Cases** (`src/core/use-cases/`) - 中间层
   - 应用特定的业务逻辑
   - 只依赖 Entities 层
   - 定义 Gateway 接口

3. **Interface Adapters** (`src/adapters/`) - 外层
   - Controllers, Presenters
   - 实现 Gateway 接口
   - 依赖 Use Cases 层

4. **Frameworks & Drivers** (`src/frameworks/`) - 最外层
   - Express, PostgreSQL, Redis 等
   - 实现 Gateway 接口的具体实现

### 编码规范

- **禁止**内层依赖外层！
- **禁止**在 Entity 中导入任何框架代码
- **禁止**在 Use Case 中直接调用数据库

### 示例

✅ 正确：
```typescript
// src/core/use-cases/RegisterUser.ts
import { User } from '../entities/User'; // OK: 依赖内层
import { UserGateway } from './UserGateway'; // OK: 定义接口

export class RegisterUserUseCase {
  constructor(private gateway: UserGateway) {}
}
```

❌ 错误：
```typescript
// src/core/use-cases/RegisterUser.ts
import { Request } from 'express'; // ❌ 错误: 依赖外层框架
import { Database } from 'some-db'; // ❌ 错误: 依赖外层
```
```

### 19.5.2 使用 Plan Mode 构建新功能

```bash
# 激活 Plan Mode
Shift+Tab (两次)

# 任务描述：
创建用户评论功能

# Claude 会：
1. 分析现有架构
2. 设计各层组件
3. 确保依赖方向正确
4. 列出需要创建的文件
```

### 19.5.3 让 Claude 检查架构违规

```bash
# 使用 AskUserQuestion 工具
# 任务：检查项目是否有架构违规

# Claude 会：
1. 检查 import 语句
2. 识别错误的依赖方向
3. 报告潜在的架构问题
4. 建议重构方案
```

---

## 19.6 常见陷阱

### 陷阱 1：在 Entity 中引入框架依赖

```typescript
// ❌ 错误：Entity 依赖了外部库
// src/entities/User.ts
import { Request } from 'express'; // ❌ 错误！

export class User {
  static fromRequest(req: Request): User {
    return {
      id: req.body.id,
      name: req.body.name
    };
  }
}

// ✅ 正确：Entity 纯粹，只包含业务规则
// src/entities/User.ts
export interface User {
  id: string;
  name: string;
}

export class UserEntity {
  static isValidName(name: string): boolean {
    return name.length >= 2 && name.length <= 50;
  }
}

// 在 Adapter 层处理框架相关逻辑
// src/adapters/UserController.ts
export class UserController {
  static fromRequest(req: Request): User {
    return {
      id: req.body.id,
      name: req.body.name
    };
  }
}
```

### 陷阱 2：在 Use Case 中直接访问数据库

```typescript
// ❌ 错误：Use Case 直接使用数据库
// src/use-cases/RegisterUser.ts
import { Database } from 'postgres'; // ❌ 错误！

export class RegisterUserUseCase {
  private db = new Database();

  async execute(data: any) {
    await this.db.query('INSERT INTO users...'); // ❌ 错误！
  }
}

// ✅ 正确：通过 Gateway 接口访问数据
// src/use-cases/RegisterUser.ts
export interface UserGateway {
  save(user: User): Promise<void>;
}

export class RegisterUserUseCase {
  constructor(private gateway: UserGateway) {}

  async execute(data: any) {
    await this.gateway.save(user); // ✅ 正确！
  }
}

// 在 Framework 层实现 Gateway
// src/frameworks/DatabaseUserGateway.ts
export class DatabaseUserGateway implements UserGateway {
  private db = new Database();

  async save(user: User): Promise<void> {
    await this.db.query('INSERT INTO users...', user);
  }
}
```

### 陷阱 3：数据流向错误

```typescript
// ❌ 错误：内层定义了外层的数据结构
// src/entities/User.ts
export interface User {
  id: string;
  // ❌ 错误：Entity 不应该知道 HTTP 响应格式
  httpResponse?: {
    status: number;
    headers: Record<string, string>;
  };
}

// ✅ 正确：每层定义自己的数据结构
// src/entities/User.ts - 内层数据结构
export interface User {
  id: string;
  name: string;
}

// src/adapters/UserController.ts - 外层数据结构
import { Response } from 'express';

export interface UserResponseDTO {
  user: User;
  status: number;
}

export class UserController {
  toResponse(user: User): UserResponseDTO {
    return {
      user: user,
      status: 200
    };
  }
}
```

---

## 19.7 练习

### 练习 1：识别架构层次

给定以下代码，指出每个组件属于哪个层次：

```typescript
// A
export interface Product {
  id: string;
  name: string;
  price: number;
}

export class ProductEntity {
  static isValidPrice(price: number): boolean {
    return price > 0;
  }
}

// B
export interface ProductGateway {
  findById(id: string): Promise<Product | null>;
  save(product: Product): Promise<void>;
}

export class AddToCartUseCase {
  constructor(private gateway: ProductGateway) {}

  async execute(productId: string): Promise<void> {
    const product = await this.gateway.findById(productId);
    if (!product || !ProductEntity.isValidPrice(product.price)) {
      throw new Error('Invalid product');
    }
    // Add to cart logic...
  }
}

// C
import { Request, Response } from 'express';

export class CartController {
  constructor(private useCase: AddToCartUseCase) {}

  async handle(req: Request, res: Response): Promise<void> {
    await this.useCase.execute(req.params.productId);
    res.json({ success: true });
  }
}

// D
import { Database } from 'postgres';

export class PostgresProductGateway implements ProductGateway {
  private db = new Database();

  async findById(id: string): Promise<Product | null> {
    const row = await this.db.query('SELECT * FROM products WHERE id = $1', [id]);
    return row ? { id: row.id, name: row.name, price: row.price } : null;
  }

  async save(product: Product): Promise<void> {
    await this.db.query('INSERT INTO products VALUES ($1, $2, $3)', [product.id, product.name, product.price]);
  }
}
```

**答案**：
- A → Entities 层（最内层）
- B → Use Cases 层（中间层）
- C → Interface Adapters 层（外层）
- D → Frameworks & Drivers 层（最外层）

### 练习 2：重构违反架构的代码

重构以下代码，使其符合整洁架构原则：

```typescript
// ❌ 需要重构的代码
// src/services/OrderService.ts
import { Database } from 'postgres';
import { Request } from 'express';
import { sendEmail } from './email-service';

export class OrderService {
  private db = new Database();

  async createOrder(req: Request): Promise<void> {
    const { productId, userId } = req.body;

    // 验证产品
    const product = await this.db.query('SELECT * FROM products WHERE id = $1', [productId]);
    if (!product || product.price <= 0) {
      throw new Error('Invalid product');
    }

    // 创建订单
    await this.db.query('INSERT INTO orders (product_id, user_id) VALUES ($1, $2)', [productId, userId]);

    // 发送邮件
    await sendEmail(userId, 'Order created');
  }
}
```

**提示**：
1. 创建 Entity 层：`Order`、`OrderEntity`
2. 创建 Use Case 层：`CreateOrderUseCase`
3. 定义 Gateway 接口：`OrderGateway`
4. 创建 Adapter 层：`OrderController`
5. 实现 Framework 层：`DatabaseOrderGateway`

---

## 19.8 进一步阅读

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) - 原始文章
- [The Clean Code Blog](https://blog.cleancoder.com/) - Uncle Bob 的博客
- [Chapter 20: 洋葱架构与六边形架构](chapter-20-onion-hexagonal.md) - 下一章

---

## 视频脚本

### Episode 19: 整洁架构原则 (15 分钟)

#### [0:00-1:00] 引入
**视觉元素**：
- 标题："整洁架构：依赖方向决定一切"
- 整洁架构同心圆图

**内容**：
> 什么是好的软件架构？不是使用最新的框架，不是最复杂的模式。好的架构让你的代码易于测试、易于修改、易于理解。今天我们学习 Uncle Bob 的整洁架构，一个改变了整个行业的架构模式。

#### [1:00-3:00] 概念讲解
**视觉元素**：
- 同心圆图解动画（每层依次出现）
- 依赖方向箭头动画

**内容**：
> 整洁架构的核心是"依赖规则"：源代码依赖只能由外向内。最内层是实体（Entities），包含核心业务规则。外层是用例（Use Cases），包含应用特定规则。再外层是接口适配器（Interface Adapters），最外层是框架和驱动器。
>
> 关键点：内层不知道外层的存在！Entity 不依赖任何框架，Use Case 不依赖数据库。

#### [3:00-8:00] 实战演示
**视觉元素**：
- VS Code 屏幕录制
- 代码高亮显示各层代码
- 架构图与代码对照

**内容**：
> 让我们用 Claude Code 从零开始构建一个用户注册功能。首先激活 Plan Mode (Shift+Tab)，让 Claude 帮我们设计架构。
>
> [演示：使用 Claude Code 创建四层代码]
>
> 看到没有？Entity 层只包含业务规则，不知道数据库的存在。Use Case 层定义了 Gateway 接口。Adapter 层处理 HTTP 请求。Framework 层实现具体的数据库操作。每一层都可以独立测试！

#### [8:00-12:00] mybatis-boost 案例分析
**视觉元素**：
- mybatis-boost 架构图
- MappingResult entity 代码
- DefinitionProvider adapter 代码

**内容**：
> 让我们看看真实项目 mybatis-boost 是如何应用整洁架构的。
>
> [演示：查看 mybatis-boost 代码结构]
>
> MappingResult 和 MappingValidator 在最内层，是纯业务逻辑。FindMappingUseCase 定义了 IFileGateway 接口。DefinitionProvider 在 Adapter 层，连接 VS Code API 和 Use Case。VSCodeFileGateway 和 MyBatisParserGateway 在最外层，实现了具体技术。
>
> 这种架构让 mybatis-boost 可以轻松支持新的文件系统、新的解析器，而不影响核心导航逻辑。

#### [12:00-14:00] 常见陷阱
**视觉元素**：
- 错误代码示例（红色 X）
- 正确代码示例（绿色 ✓）

**内容**：
> 三个最常见的错误：
> 1. 在 Entity 中导入框架代码
> 2. 在 Use Case 中直接访问数据库
> 3. 让内层知道外层的数据结构
>
> [演示：展示错误和正确代码对比]

#### [14:00-15:00] 总结
**视觉元素**：
- 关键要点列表
- Next Chapter 预告

**内容**：
> 整洁架构的核心要点：
> - 依赖方向由外向内
> - 内层不依赖外层
> - 通过接口解耦各层
>
> 下一章，我们将学习洋葱架构和六边形架构，看看它们与整洁架构的关系。
