# Chapter 16: Provider 模式支持多种 AI 工具

**模块**: Module 4 - mybatis-boost 实战案例
**预计阅读时间**: 18 分钟
**难度**: ⭐⭐⭐⭐

---

## 学习目标

本章结束后，你将能够：

- [ ] 理解 Provider 模式的设计理念
- [ ] 掌握 MCP Manager 的实现细节
- [ ] 学习如何支持多种 AI 工具 (Cursor/Copilot)
- [ ] 了解中间抽象层的设计原则

---

## 前置知识

- [ ] 已完成 Chapter 10 - MCP 深度解析
- [ ] 已完成 Chapter 15 - CST vs Regex
- [ ] 了解 Cursor IDE 和 VS Code Copilot

---

## 问题背景

### 多 AI 工具的挑战

mybatis-boost 需要支持两种主流的 AI 集成方式：

```
┌─────────────────────────────────────────────────────────┐
│              AI 工具生态                                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Cursor IDE                                             │
│  ────────────                                           │
│  • 使用 MCP 扩展 API                                    │
│  • 专有协议和接口                                        │
│  • 特定的工具调用格式                                    │
│                                                         │
│  VS Code + Copilot                                     │
│  ────────────────────                                   │
│  • 使用 Language Model Tools API                       │
│  • 微软的 AI 集成标准                                    │
│  • 不同的工具调用格式                                    │
│                                                         │
│  问题：                                                 │
│  ────────                                               │
│  • 两种 API 完全不同                                    │
│  • 需要维护两套代码                                     │
│  • 功能重复，难以维护                                   │
│  • 扩展新的 AI 工具困难                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Provider 模式的解决方案

```
┌─────────────────────────────────────────────────────────┐
│              Provider 模式架构                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  mybatis-boost 核心服务                                  │
│  ────────────────────────                               │
│  • GeneratorService                                    │
│  • TemplateEngine                                       │
│  • CodeGeneration                                       │
│           ↑                                             │
│           │                                             │
│  ┌─────────────────────────────────────────────────┐    │
│  │           MCP Manager (统一接口)                 │    │
│  │  ┌───────────────────────────────────────────┐  │    │
│  │  │         IMCPProvider (接口)                 │  │    │
│  │  │  + initialize()                             │  │    │
│  │  │  + callTool()                               │  │    │
│  │  │  + listTools()                              │  │    │
│  │  │  + disconnect()                             │  │    │
│  │  └───────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────┘    │
│           ↑         ↑                                   │
│    ┌──────┴─────┐  │                                   │
│    │            │  │                                   │
│ ┌──┴───┐    ┌───┴────────┐                            │
│ │Cursor│    │  Copilot   │                            │
│ │Provider│   │  Provider   │                            │
│ └──────┘    └────────────┘                            │
│    │              │                                    │
│    ↓              ↓                                    │
│  Cursor IDE    VS Code + Copilot                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Provider 模式详解

### 接口定义

**src/mcp/core/IMCPProvider.ts**:

```typescript
/**
 * MCP Provider 接口
 * 定义所有 MCP Provider 必须实现的方法
 */
export interface IMCPProvider {
  /**
   * Provider 名称
   */
  readonly name: string;

  /**
   * Provider 版本
   */
  readonly version: string;

  /**
   * 初始化 Provider
   */
  initialize(context: ProviderContext): Promise<void>;

  /**
   * 调用 MCP 工具
   * @param toolName 工具名称
   * @param params 工具参数
   * @returns 工具执行结果
   */
  callTool(toolName: string, params: any): Promise<ToolResult>;

  /**
   * 获取可用工具列表
   */
  listTools(): Promise<Tool[]>;

  /**
   * 检查 Provider 是否可用
   */
  isAvailable(): boolean;

  /**
   * 断开连接
   */
  disconnect(): Promise<void>;
}

/**
 * Provider 上下文
 */
export interface ProviderContext {
  /**
   * 扩展上下文
   */
  extensionContext: vscode.ExtensionContext;

  /**
   * 配置
   */
  config: ProviderConfig;

  /**
   * 日志记录器
   */
  logger: Logger;
}

/**
 * Provider 配置
 */
export interface ProviderConfig {
  /**
   * 是否启用
   */
  enabled: boolean;

  /**
   * 连接超时（毫秒）
   */
  timeout?: number;

  /**
   * 重试次数
   */
  retries?: number;

  /**
   * 自定义配置
   */
  custom?: Record<string, any>;
}

/**
 * 工具定义
 */
export interface Tool {
  /**
   * 工具名称
   */
  name: string;

  /**
   * 工具描述
   */
  description: string;

  /**
   * 输入架构（JSON Schema）
   */
  inputSchema: {
    type: 'object';
    properties: Record<string, any>;
    required?: string[];
  };
}

/**
 * 工具执行结果
 */
export interface ToolResult {
  /**
   * 是否成功
   */
  success: boolean;

  /**
   * 结果数据
   */
  data?: any;

  /**
   * 错误信息
   */
  error?: string;
}
```

---

## Cursor MCP Provider 实现

**src/mcp/providers/CursorMCPProvider.ts**:

```typescript
import * as vscode from 'vscode';
import { IMCPProvider, ProviderContext, Tool, ToolResult } from '../core/IMCPProvider';

/**
 * Cursor IDE MCP Provider
 * 实现 Cursor 特定的 MCP 集成
 */
export class CursorMCPProvider implements IMCPProvider {
  readonly name = 'cursor';
  readonly version = '1.0.0';

  private context?: ProviderContext;
  private client?: CursorMCPClient;
  private isConnected = false;

  /**
   * 初始化 Cursor MCP Provider
   */
  async initialize(context: ProviderContext): Promise<void> {
    this.context = context;

    // 检查 Cursor 环境变量
    if (!this.isCursorEnvironment()) {
      throw new Error('Cursor IDE environment not detected');
    }

    context.logger.info('Initializing Cursor MCP Provider');

    // 创建 Cursor MCP 客户端
    this.client = new CursorMCPClient({
      endpoint: 'mcp://cursor-extension',
      timeout: context.config.timeout || 30000
    });

    try {
      await this.client.connect();
      this.isConnected = true;
      context.logger.info('Cursor MCP Provider connected successfully');
    } catch (error) {
      context.logger.error('Failed to connect to Cursor MCP', error);
      throw error;
    }
  }

  /**
   * 检查是否在 Cursor 环境中
   */
  private isCursorEnvironment(): boolean {
    // Cursor 特定的环境变量
    return (
      process.env.VSCODE_IPC_HOOK_CLI?.includes('cursor') ||
      process.env.CURSOR_VERSION !== undefined ||
      vscode.env.appName.includes('Cursor')
    );
  }

  /**
   * 调用 MCP 工具（Cursor 格式）
   */
  async callTool(toolName: string, params: any): Promise<ToolResult> {
    if (!this.isConnected || !this.client) {
      throw new Error('Cursor MCP Provider not connected');
    }

    this.context?.logger.debug(`Calling tool: ${toolName}`, params);

    try {
      // Cursor 特定的工具调用格式
      const response = await this.client.invoke({
        jsonrpc: '2.0',
        id: Date.now(),
        method: 'tools/call',
        params: {
          name: toolName,
          arguments: params  // Cursor 使用 "arguments"
        }
      });

      if (response.error) {
        return {
          success: false,
          error: response.error.message
        };
      }

      return {
        success: true,
        data: response.result
      };
    } catch (error) {
      this.context?.logger.error(`Tool call failed: ${toolName}`, error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * 获取可用工具列表
   */
  async listTools(): Promise<Tool[]> {
    if (!this.isConnected || !this.client) {
      throw new Error('Cursor MCP Provider not connected');
    }

    const response = await this.client.invoke({
      jsonrpc: '2.0',
      id: Date.now(),
      method: 'tools/list',
      params: {}
    });

    if (response.error) {
      throw new Error(`Failed to list tools: ${response.error.message}`);
    }

    return response.result.tools;
  }

  /**
   * 检查 Provider 是否可用
   */
  isAvailable(): boolean {
    return this.isConnected && this.client !== undefined;
  }

  /**
   * 断开连接
   */
  async disconnect(): Promise<void> {
    if (this.client) {
      await this.client.disconnect();
      this.isConnected = false;
      this.context?.logger.info('Cursor MCP Provider disconnected');
    }
  }
}

/**
 * Cursor MCP 客户端（简化版）
 */
class CursorMCPClient {
  private endpoint: string;
  private timeout: number;

  constructor(config: { endpoint: string; timeout: number }) {
    this.endpoint = config.endpoint;
    this.timeout = config.timeout;
  }

  async connect(): Promise<void> {
    // 实现 Cursor MCP 连接逻辑
    // 实际使用 Cursor 的 IPC 机制
  }

  async invoke(request: any): Promise<any> {
    // 实现 JSON-RPC 调用
    // 使用 Cursor 的通信协议
    return {};
  }

  async disconnect(): Promise<void> {
    // 断开连接
  }
}
```

---

## Copilot MCP Provider 实现

**src/mcp/providers/CopilotMCPProvider.ts**:

```typescript
import * as vscode from 'vscode';
import { IMCPProvider, ProviderContext, Tool, ToolResult } from '../core/IMCPProvider';

/**
 * VS Code Copilot MCP Provider
 * 实现 Copilot 特定的 MCP 集成
 */
export class CopilotMCPProvider implements IMCPProvider {
  readonly name = 'copilot';
  readonly version = '1.0.0';

  private context?: ProviderContext;
  private client?: CopilotLMClient;
  private isConnected = false;

  /**
   * 初始化 Copilot MCP Provider
   */
  async initialize(context: ProviderContext): Promise<void> {
    this.context = context;

    // 检查 Copilot 可用性
    if (!await this.isCopilotAvailable()) {
      throw new Error('VS Code Copilot not available');
    }

    context.logger.info('Initializing Copilot MCP Provider');

    // 创建 Copilot LM 客户端
    this.client = new CopilotLMClient({
      timeout: context.config.timeout || 30000
    });

    try {
      await this.client.connect();
      this.isConnected = true;
      context.logger.info('Copilot MCP Provider connected successfully');
    } catch (error) {
      context.logger.error('Failed to connect to Copilot MCP', error);
      throw error;
    }
  }

  /**
   * 检查 Copilot 是否可用
   */
  private async isCopilotAvailable(): Promise<boolean> {
    // 检查 Copilot 扩展是否安装
    const copilotExtension = vscode.extensions.getExtension('GitHub.copilot');
    if (!copilotExtension) {
      return false;
    }

    // 检查 Copilot 是否激活
    if (!copilotExtension.isActive) {
      try {
        await copilotExtension.activate();
      } catch (error) {
        return false;
      }
    }

    // 检查 Language Model Tools API
    return 'languageModelTools' in vscode;
  }

  /**
   * 调用 MCP 工具（Copilot 格式）
   */
  async callTool(toolName: string, params: any): Promise<ToolResult> {
    if (!this.isConnected || !this.client) {
      throw new Error('Copilot MCP Provider not connected');
    }

    this.context?.logger.debug(`Calling tool: ${toolName}`, params);

    try {
      // Copilot 特定的工具调用格式
      // 使用 VS Code Language Model Tools API
      const response = await this.client.invokeTool({
        name: toolName,
        parameters: params,  // Copilot 使用 "parameters"
        toolCallId: this.generateToolCallId()
      });

      if (response.error) {
        return {
          success: false,
          error: response.error.message
        };
      }

      return {
        success: true,
        data: response.result
      };
    } catch (error) {
      this.context?.logger.error(`Tool call failed: ${toolName}`, error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * 获取可用工具列表
   */
  async listTools(): Promise<Tool[]> {
    if (!this.isConnected || !this.client) {
      throw new Error('Copilot MCP Provider not connected');
    }

    const response = await this.client.listTools();

    return response.tools.map(tool => ({
      name: tool.name,
      description: tool.description,
      inputSchema: tool.inputSchema
    }));
  }

  /**
   * 检查 Provider 是否可用
   */
  isAvailable(): boolean {
    return this.isConnected && this.client !== undefined;
  }

  /**
   * 断开连接
   */
  async disconnect(): Promise<void> {
    if (this.client) {
      await this.client.disconnect();
      this.isConnected = false;
      this.context?.logger.info('Copilot MCP Provider disconnected');
    }
  }

  /**
   * 生成工具调用 ID
   */
  private generateToolCallId(): string {
    return `tool_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

/**
 * Copilot LM 客户端（简化版）
 */
class CopilotLMClient {
  private timeout: number;

  constructor(config: { timeout: number }) {
    this.timeout = config.timeout;
  }

  async connect(): Promise<void> {
    // 实现 Copilot LM 连接逻辑
    // 使用 vscode.languageModelTools API
  }

  async invokeTool(request: any): Promise<any> {
    // 实现 Language Model Tools 调用
    return {};
  }

  async listTools(): Promise<any> {
    // 列出可用工具
    return { tools: [] };
  }

  async disconnect(): Promise<void> {
    // 断开连接
  }
}
```

---

## MCP Manager 统一管理

**src/mcp/MCPManager.ts**:

```typescript
import * as vscode from 'vscode';
import { IMCPProvider, ProviderConfig, ToolResult } from './core/IMCPProvider';
import { CursorMCPProvider } from './providers/CursorMCPProvider';
import { CopilotMCPProvider } from './providers/CopilotMCPProvider';

/**
 * MCP Manager - 统一管理多个 MCP Provider
 * 使用 Provider 模式抽象不同的 AI 工具
 */
export class MCPManager {
  // Provider 注册表
  private providers = new Map<string, IMCPProvider>();

  // 当前活跃的 Provider
  private activeProvider: string | null = null;

  // 输出通道用于日志
  private outputChannel: vscode.OutputChannel;

  constructor() {
    this.outputChannel = vscode.window.createOutputChannel('MyBatis Boost MCP');

    // 注册默认 Providers
    this.registerProvider('cursor', new CursorMCPProvider());
    this.registerProvider('copilot', new CopilotMCPProvider());

    // 自动检测并激活
    this.autoDetectAndActivate();
  }

  /**
   * 注册一个 MCP Provider
   */
  registerProvider(name: string, provider: IMCPProvider): void {
    this.providers.set(name, provider);
    this.log(`Registered MCP Provider: ${name}`);
  }

  /**
   * 注销一个 MCP Provider
   */
  unregisterProvider(name: string): void {
    const provider = this.providers.get(name);
    if (provider) {
      provider.disconnect().catch(error => {
        this.log(`Error disconnecting ${name}: ${error.message}`);
      });
      this.providers.delete(name);
      this.log(`Unregistered MCP Provider: ${name}`);
    }
  }

  /**
   * 激活指定的 Provider
   */
  async activateProvider(name: string, config?: ProviderConfig): Promise<void> {
    const provider = this.providers.get(name);

    if (!provider) {
      throw new Error(`Provider not found: ${name}`);
    }

    // 检查 Provider 是否可用
    if (!provider.isAvailable()) {
      try {
        // 初始化 Provider
        await provider.initialize({
          extensionContext: vscode.extensions.getExtension('young1lin.mybatis-boot')!.exports,
          config: config || this.getDefaultConfig(),
          logger: this.createLogger(name)
        });
      } catch (error) {
        this.log(`Failed to activate ${name}: ${error.message}`);
        throw new Error(`Provider activation failed: ${error.message}`);
      }
    }

    // 断开当前 Provider（如果有）
    if (this.activeProvider && this.activeProvider !== name) {
      await this.deactivateProvider();
    }

    this.activeProvider = name;
    this.log(`Activated MCP Provider: ${name}`);

    // 显示通知
    vscode.window.showInformationMessage(`MCP Provider activated: ${name}`);
  }

  /**
   * 断开当前 Provider
   */
  async deactivateProvider(): Promise<void> {
    if (!this.activeProvider) {
      return;
    }

    const provider = this.providers.get(this.activeProvider);
    if (provider) {
      await provider.disconnect();
      this.log(`Deactivated MCP Provider: ${this.activeProvider}`);
    }

    this.activeProvider = null;
  }

  /**
   * 调用工具（通过当前活跃的 Provider）
   */
  async callTool(toolName: string, params: any): Promise<ToolResult> {
    if (!this.activeProvider) {
      throw new Error('No active MCP Provider');
    }

    const provider = this.providers.get(this.activeProvider);
    if (!provider) {
      throw new Error(`Active provider not found: ${this.activeProvider}`);
    }

    this.log(`Calling tool: ${toolName} via ${this.activeProvider}`);

    try {
      return await provider.callTool(toolName, params);
    } catch (error) {
      this.log(`Tool call failed: ${error.message}`);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * 获取当前可用工具
   */
  async listTools(): Promise<any[]> {
    if (!this.activeProvider) {
      return [];
    }

    const provider = this.providers.get(this.activeProvider);
    if (!provider) {
      return [];
    }

    try {
      return await provider.listTools();
    } catch (error) {
      this.log(`Failed to list tools: ${error.message}`);
      return [];
    }
  }

  /**
   * 获取当前活跃的 Provider 名称
   */
  getActiveProvider(): string | null {
    return this.activeProvider;
  }

  /**
   * 获取所有已注册的 Provider 名称
   */
  getRegisteredProviders(): string[] {
    return Array.from(this.providers.keys());
  }

  /**
   * 自动检测并激活合适的 Provider
   */
  private async autoDetectAndActivate(): Promise<void> {
    this.log('Auto-detecting MCP Provider...');

    // 优先级 1: Cursor IDE
    if (process.env.VSCODE_IPC_HOOK_CLI?.includes('cursor')) {
      try {
        await this.activateProvider('cursor');
        return;
      } catch (error) {
        this.log(`Cursor activation failed: ${error.message}`);
      }
    }

    // 优先级 2: VS Code Copilot
    if (vscode.extensions.getExtension('GitHub.copilot')) {
      try {
        await this.activateProvider('copilot');
        return;
      } catch (error) {
        this.log(`Copilot activation failed: ${error.message}`);
      }
    }

    // 没有 Provider 可用
    this.log('No MCP Provider available');
  }

  /**
   * 获取默认配置
   */
  private getDefaultConfig(): ProviderConfig {
    return {
      enabled: true,
      timeout: 30000,
      retries: 3
    };
  }

  /**
   * 创建 Provider 专用的日志记录器
   */
  private createLogger(providerName: string) {
    return {
      info: (message: string, ...args: any[]) => {
        this.log(`[${providerName}] ${message}`, ...args);
      },
      debug: (message: string, ...args: any[]) => {
        this.log(`[${providerName}] ${message}`, ...args);
      },
      error: (message: string, ...args: any[]) => {
        this.log(`[${providerName}] ERROR: ${message}`, ...args);
      },
      warn: (message: string, ...args: any[]) => {
        this.log(`[${providerName}] WARN: ${message}`, ...args);
      }
    };
  }

  /**
   * 记录日志
   */
  private log(message: string, ...args: any[]): void {
    const timestamp = new Date().toISOString();
    this.outputChannel.appendLine(`[${timestamp}] ${message}`);

    if (args.length > 0) {
      this.outputChannel.appendLine(JSON.stringify(args, null, 2));
    }
  }

  /**
   * 显示输出通道
   */
  showOutput(): void {
    this.outputChannel.show();
  }

  /**
   * 清理资源
   */
  dispose(): void {
    this.deactivateProvider().catch(() => {});
    this.outputChannel.dispose();
  }
}
```

---

## MCP 工具实现

### 工具列表

mybatis-boost 提供的 MCP 工具：

| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `parseSqlAndGenerate` | 解析 SQL 并生成代码 | `ddl`, `templateType` |
| `exportGeneratedFiles` | 导出生成的文件 | `files`, `outputPath` |
| `queryGenerationHistory` | 查询生成历史 | `limit` |
| `parseAndExport` | 解析并导出 | `ddl`, `outputPath` |

### 工具实现示例

**src/mcp/tools/ParseSqlAndGenerateTool.ts**:

```typescript
import { Tool } from '../core/IMCPProvider';
import { GeneratorService } from '../../generator/GeneratorService';

/**
 * 解析 SQL 并生成代码工具
 */
export class ParseSqlAndGenerateTool implements Tool {
  name = 'parseSqlAndGenerate';
  description = 'Parse SQL DDL and generate MyBatis mapper, model, and service code';

  inputSchema = {
    type: 'object' as const,
    properties: {
      ddl: {
        type: 'string',
        description: 'SQL DDL statement (CREATE TABLE)'
      },
      templateType: {
        type: 'string',
        description: 'Template type to use',
        enum: ['basic', 'advanced', 'mybatis-plus'],
        default: 'basic'
      },
      config: {
        type: 'object',
        description: 'Optional generator configuration',
        properties: {
          packageName: { type: 'string' },
          mapperPackage: { type: 'string' },
          modelPackage: { type: 'string' },
          useLombok: { type: 'boolean' }
        }
      }
    },
    required: ['ddl']
  };

  private generatorService: GeneratorService;

  constructor(generatorService: GeneratorService) {
    this.generatorService = generatorService;
  }

  /**
   * 执行工具
   */
  async execute(params: {
    ddl: string;
    templateType?: string;
    config?: any;
  }): Promise<{
    success: boolean;
    generated?: {
      mapper: string;
      model: string;
      service?: string;
    };
    error?: string;
  }> {
    try {
      // 解析 DDL
      const schema = await this.generatorService.parseDDL(params.ddl);

      // 生成代码
      const generated = await this.generatorService.generate({
        schema,
        templateType: params.templateType || 'basic',
        config: params.config
      });

      return {
        success: true,
        generated
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
}
```

---

## 使用 Provider 模式的优势

### 1. 解耦

```
┌─────────────────────────────────────────────────────────┐
│              解耦的优势                                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  解耦前：                                               │
│  ─────────                                             │
│  GeneratorService → 直接调用 Cursor API                 │
│                        → 直接调用 Copilot API            │
│                                                         │
│  问题：                                                 │
│  • 核心服务依赖具体实现                                 │
│  • 难以添加新的 AI 工具                                 │
│  • 代码重复                                             │
│                                                         │
│  解耦后：                                               │
│  ─────────                                             │
│  GeneratorService → MCPManager → IMCPProvider           │
│                                              ↑          │
│                                  ┌──────┴──────┐       │
│                                  │ Cursor     │       │
│                                  │ Copilot    │       │
│                                  │ (New AI)   │       │
│                                  └────────────┘       │
│                                                         │
│  优势：                                                 │
│  • 核心服务只依赖接口                                   │
│  • 易于添加新的 Provider                                │
│  • 无代码重复                                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2. 可测试

```typescript
/**
 * 使用 Mock Provider 进行测试
 */
class MockMCPProvider implements IMCPProvider {
  readonly name = 'mock';
  readonly version = '1.0.0';

  async callTool(toolName: string, params: any): Promise<ToolResult> {
    // 返回预定义的测试数据
    return {
      success: true,
      data: { /* 测试数据 */ }
    };
  }

  // ... 其他方法
}

/**
 * 测试 GeneratorService
 */
describe('GeneratorService', () => {
  it('should generate code using MCP tool', async () => {
    // 使用 Mock Provider
    const mockProvider = new MockMCPProvider();
    const mcpManager = new MCPManager();
    mcpManager.registerProvider('mock', mockProvider);
    await mcpManager.activateProvider('mock');

    // 测试 GeneratorService
    const generator = new GeneratorService(mcpManager);
    const result = await generator.generate({
      ddl: 'CREATE TABLE users (id INT PRIMARY KEY);'
    });

    expect(result.success).toBe(true);
  });
});
```

### 3. 灵活性

```typescript
/**
 * 运行时切换 Provider
 */
async function switchProvider(manager: MCPManager, providerName: string) {
  // 当前活跃的 Provider
  const current = manager.getActiveProvider();
  console.log(`Switching from ${current} to ${providerName}`);

  // 切换 Provider
  await manager.activateProvider(providerName);

  // 现在所有工具调用都通过新的 Provider
  const result = await manager.callTool('parseSqlAndGenerate', {
    ddl: 'CREATE TABLE test (id INT);'
  });
}
```

---

## 总结

### 关键要点

1. **Provider 模式的价值**
   - 解耦核心服务和具体实现
   - 支持多种 AI 工具
   - 易于扩展和维护

2. **IMCPProvider 接口**
   - 统一的方法签名
   - 清晰的职责定义
   - 标准化的错误处理

3. **MCP Manager 的作用**
   - Provider 注册表
   - 自动检测和激活
   - 统一的工具调用接口

4. **实际应用**
   - Cursor MCP Provider
   - Copilot MCP Provider
   - MCP 工具实现

### 下一步

在下一章中，我们将学习 **性能优化策略**：
- LRU 缓存的实现
- 文件监听器
- 优先级策略
- 性能监控和调优

---

## 进一步阅读

### 源代码
- `C:\PythonProject\mybatis-boost\src\mcp\MCPManager.ts`
- `C:\PythonProject\mybatis-boost\src\mcp\core\IMCPProvider.ts`
- `C:\PythonProject\mybatis-boost\docs\MCP_SERVER.md`

### 相关章节
- [Chapter 10 - MCP 深度解析](../module-03-advanced-features/chapter-10-mcp.md)
- [Chapter 17 - 性能优化](chapter-17-performance.md)

---

## 练习

完成以下练习：

1. **理解练习**
   - [ ] 分析 Provider 模式的设计
   - [ ] 理解 IMCPProvider 接口
   - [ ] 比较 Cursor 和 Copilot 的差异

2. **代码练习**
   - [ ] 阅读 MCPManager 源代码
   - [ ] 实现一个简单的 Mock Provider
   - [ ] 添加一个新的 MCP 工具

3. **实战练习**
   - [ ] 在 Cursor IDE 中测试 mybatis-boost
   - [ ] 在 VS Code + Copilot 中测试
   - [ ] 对比两种 AI 工具的使用体验

---

**上一章**: [Chapter 15 - CST vs Regex](chapter-15-cst-vs-regex.md)
**下一章**: [Chapter 17 - 性能优化](chapter-17-performance.md)
