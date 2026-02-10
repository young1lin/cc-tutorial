# Chapter 10: MCP (Model Context Protocol) 深度解析

**模块**: Module 3 - 高级功能
**预计阅读时间**: 18 分钟
**难度**: ⭐⭐⭐⭐

---

## 学习目标

本章结束后，你将能够：

- [ ] 理解 MCP 的核心概念和设计哲学
- [ ] 掌握 MCP 服务器的创建和配置
- [ ] 学会实现 MCP 工具和资源
- [ ] 了解 mybatis-boost 中的 MCP Provider 模式

---

## 前置知识

- [ ] 已完成 Chapter 9 - Plugin 系统
- [ ] 了解 JSON-RPC 协议基础
- [ ] 熟悉 Node.js 和 TypeScript

---

## 什么是 MCP？

### MCP 概述

**MCP (Model Context Protocol)** 是 Anthropic 开发的开放协议，
用于 AI 应用与外部数据源和工具之间的连接。

```
┌─────────────────────────────────────────────────────────┐
│              MCP 架构概览                                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐         ┌─────────────┐              │
│  │   Claude    │         │   MCP       │              │
│  │    Code     │ ◄────► │   Client    │              │
│  └─────────────┘         └─────────────┘              │
│                                  │                      │
│                         ┌────────┴────────┐            │
│                         │  JSON-RPC over  │            │
│                         │  stdio/HTTP/SSE │            │
│                         └────────┬────────┘            │
│                                  │                      │
│                    ┌─────────────┼─────────────┐       │
│                    │             │             │       │
│            ┌───────┴───┐  ┌─────┴─────┐  ┌───┴────┐   │
│            │   MCP     │  │   MCP     │  │  MCP   │   │
│            │  Server 1 │  │  Server 2 │  │Server 3│   │
│            │(Database) │  │  (Files)  │  │(API)   │   │
│            └───────────┘  └───────────┘  └────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### MCP 的核心能力

```
┌─────────────────────────────────────────────────────────┐
│              MCP 三大核心能力                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 资源 (Resources)                                    │
│     → 读取数据：文件、数据库记录、API 响应               │
│     → 支持订阅：实时更新                                 │
│     → 示例：日志文件、数据库查询、监控数据               │
│                                                         │
│  2. 工具 (Tools)                                        │
│     → 执行操作：运行命令、修改数据、调用 API             │
│     → 带参数的函数                                      │
│     → 示例：执行 SQL、调用 API、运行脚本                │
│                                                         │
│  3. 提示词 (Prompts)                                    │
│     → 预定义的模板                                      │
│     → 可重用的 AI 交互模式                              │
│     → 示例：代码审查模板、文档生成模板                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 为什么使用 MCP？

**传统方式的问题**：

```
❌ 每个工具都需要独立集成
❌ 不同工具接口不一致
❌ 难以维护和扩展
❌ 安全性和权限管理复杂
```

**MCP 的解决方案**：

```
✅ 标准化协议
✅ 统一的工具接口
✅ 模块化和可扩展
✅ 内置权限管理
✅ 跨平台支持
```

---

## MCP 架构详解

### 通信协议

MCP 使用 **JSON-RPC 2.0** 协议进行通信，支持多种传输方式：

```
┌─────────────────────────────────────────────────────────┐
│              MCP 传输层                                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  stdio (标准输入/输出)                                   │
│  ────────────────────                                   │
│  • 最常用，适合本地进程                                  │
│  • 父子进程通信                                          │
│  • 示例：claude-code ↔ mcp-server                       │
│                                                         │
│  HTTP/SSE                                               │
│  ────────────                                           │
│  • 适合远程服务                                          │
│  • Server-Sent Events 实时推送                          │
│  • 示例：claude-code ↔ cloud-mcp-service               │
│                                                         │
│  WebSocket (未来支持)                                    │
│  ────────────────────                                   │
│  • 双向实时通信                                          │
│  • 更低延迟                                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### JSON-RPC 消息格式

**请求消息**：

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "read_file",
    "arguments": {
      "path": "/path/to/file.txt"
    }
  }
}
```

**响应消息**：

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "File content here..."
      }
    ]
  }
}
```

**错误消息**：

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32601,
    "message": "Method not found",
    "data": {
      "details": "The requested tool does not exist"
    }
  }
}
```

---

## 创建 MCP 服务器

### 基础 MCP 服务器

让我们创建一个简单的文件监控 MCP 服务器。

#### 步骤 1: 初始化项目

```bash
mkdir mcp-file-monitor
cd mcp-file-monitor
npm init -y
npm install @modelcontextprotocol/sdk
npm install --save-dev typescript @types/node
```

#### 步骤 2: 配置 TypeScript

**tsconfig.json**:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true
  },
  "include": ["src/**/*"]
}
```

#### 步骤 3: 实现 MCP 服务器

**src/index.ts**:

```typescript
#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { promises as fs } from 'fs';
import path from 'path';

// 创建 MCP 服务器
const server = new Server(
  {
    name: 'file-monitor-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
      resources: {},
    },
  }
);

// 注册工具列表处理器
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'read_file',
        description: 'Read the contents of a file',
        inputSchema: {
          type: 'object',
          properties: {
            path: {
              type: 'string',
              description: 'Path to the file to read',
            },
          },
          required: ['path'],
        },
      },
      {
        name: 'write_file',
        description: 'Write content to a file',
        inputSchema: {
          type: 'object',
          properties: {
            path: {
              type: 'string',
              description: 'Path to the file to write',
            },
            content: {
              type: 'string',
              description: 'Content to write',
            },
          },
          required: ['path', 'content'],
        },
      },
      {
        name: 'list_files',
        description: 'List files in a directory',
        inputSchema: {
          type: 'object',
          properties: {
            directory: {
              type: 'string',
              description: 'Path to the directory',
            },
            pattern: {
              type: 'string',
              description: 'Optional glob pattern',
            },
          },
          required: ['directory'],
        },
      },
      {
        name: 'watch_file',
        description: 'Watch a file for changes',
        inputSchema: {
          type: 'object',
          properties: {
            path: {
              type: 'string',
              description: 'Path to the file to watch',
            },
          },
          required: ['path'],
        },
      },
    ],
  };
});

// 注册资源列表处理器
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources: [
      {
        uri: 'file:///system-info',
        name: 'System Information',
        description: 'Current system information',
        mimeType: 'text/plain',
      },
      {
        uri: 'file:///recent-changes',
        name: 'Recent File Changes',
        description: 'Recently changed files',
        mimeType: 'application/json',
      },
    ],
  };
});

// 注册资源读取处理器
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;

  if (uri === 'file:///system-info') {
    return {
      contents: [
        {
          uri,
          mimeType: 'text/plain',
          text: JSON.stringify({
            platform: process.platform,
            arch: process.arch,
            nodeVersion: process.version,
            cwd: process.cwd(),
          }, null, 2),
        },
      ],
    };
  }

  if (uri === 'file:///recent-changes') {
    return {
      contents: [
        {
          uri,
          mimeType: 'application/json',
          text: JSON.stringify(recentChanges, null, 2),
        },
      ],
    };
  }

  throw new Error(`Resource not found: ${uri}`);
});

// 存储文件变更记录
const recentChanges: Array<{
  path: string;
  timestamp: number;
  type: 'modified' | 'created' | 'deleted';
}> = [];

// 注册工具调用处理器
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'read_file': {
        const filePath = args?.path as string;
        if (!filePath) {
          throw new Error('Path is required');
        }

        const content = await fs.readFile(filePath, 'utf-8');
        return {
          content: [
            {
              type: 'text',
              text: content,
            },
          ],
        };
      }

      case 'write_file': {
        const filePath = args?.path as string;
        const content = args?.content as string;

        if (!filePath || content === undefined) {
          throw new Error('Path and content are required');
        }

        await fs.mkdir(path.dirname(filePath), { recursive: true });
        await fs.writeFile(filePath, content, 'utf-8');

        // 记录变更
        recentChanges.unshift({
          path: filePath,
          timestamp: Date.now(),
          type: 'modified',
        });

        // 只保留最近 100 条记录
        if (recentChanges.length > 100) {
          recentChanges.pop();
        }

        return {
          content: [
            {
              type: 'text',
              text: `Successfully wrote to ${filePath}`,
            },
          ],
        };
      }

      case 'list_files': {
        const directory = args?.directory as string;
        const pattern = args?.pattern as string | undefined;

        if (!directory) {
          throw new Error('Directory is required');
        }

        const files = await fs.readdir(directory, { withFileTypes: true });
        const result = files
          .filter((file) => {
            if (pattern) {
              // 简单的 glob 匹配
              const regex = new RegExp(pattern.replace('*', '.*'));
              return regex.test(file.name);
            }
            return true;
          })
          .map((file) => ({
            name: file.name,
            type: file.isDirectory() ? 'directory' : 'file',
          }));

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'watch_file': {
        const filePath = args?.path as string;
        if (!filePath) {
          throw new Error('Path is required');
        }

        // 使用 chokidar 或 fs.watch
        const watcher = require('fs').watch(filePath, (eventType) => {
          recentChanges.unshift({
            path: filePath,
            timestamp: Date.now(),
            type: eventType === 'change' ? 'modified' : 'created',
          });
        });

        return {
          content: [
            {
              type: 'text',
              text: `Now watching ${filePath}`,
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

// 启动服务器
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('File Monitor MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});
```

#### 步骤 4: 配置和运行

**package.json**:

```json
{
  "name": "mcp-file-monitor",
  "version": "1.0.0",
  "type": "module",
  "bin": {
    "mcp-file-monitor": "./dist/index.js"
  },
  "scripts": {
    "build": "tsc",
    "watch": "tsc --watch",
    "start": "node dist/index.js"
  }
}
```

**编译并运行**：

```bash
npm run build
npm start
```

#### 步骤 5: 在 Claude Code 中配置

**~/.claude/config.json** (或项目的 .mcp.json):

```json
{
  "mcpServers": {
    "file-monitor": {
      "command": "node",
      "args": ["/path/to/mcp-file-monitor/dist/index.js"]
    }
  }
}
```

---

## MCP 在 mybatis-boost 中的应用

### Provider 模式

在 **mybatis-boost** 项目中，使用了 Provider 模式来支持多种 AI 工具的 MCP。

**项目背景**：

```
mybatis-boost 需要同时支持：
- Cursor MCP (Microsoft 的 AI 编辑器)
- VS Code Copilot MCP

问题是：两者的 MCP 接口略有不同。

解决方案：创建一个中间抽象层（Provider）
```

### MCPManager 实现

让我们看看 mybatis-boost 中的 MCPManager：

**src/mcp/MCPManager.ts** (简化示例):

```typescript
/**
 * MCP Provider 抽象接口
 */
export interface IMCPProvider {
  /**
   * 初始化 MCP 连接
   */
  initialize(): Promise<void>;

  /**
   * 调用 MCP 工具
   */
  callTool(toolName: string, params: any): Promise<any>;

  /**
   * 获取可用工具列表
   */
  listTools(): Promise<Tool[]>;

  /**
   * 断开连接
   */
  disconnect(): Promise<void>;
}

/**
 * Cursor MCP Provider
 */
export class CursorMCPProvider implements IMCPProvider {
  private client: MCPClient;

  async initialize(): Promise<void> {
    // 初始化 Cursor 特定的 MCP 客户端
    this.client = new MCPClient({
      endpoint: 'cursor-mcp',
      transport: 'stdio'
    });
    await this.client.connect();
  }

  async callTool(toolName: string, params: any): Promise<any> {
    // Cursor 特定的工具调用格式
    return await this.client.invoke({
      method: 'tools/call',
      params: {
        name: toolName,
        arguments: params
      }
    });
  }

  async listTools(): Promise<Tool[]> {
    const response = await this.client.invoke({
      method: 'tools/list'
    });
    return response.tools;
  }

  async disconnect(): Promise<void> {
    await this.client.disconnect();
  }
}

/**
 * VS Code Copilot MCP Provider
 */
export class VSCodeCopilotMCPProvider implements IMCPProvider {
  private client: MCPClient;

  async initialize(): Promise<void> {
    // VS Code Copilot 特定的初始化
    this.client = new MCPClient({
      endpoint: 'copilot-mcp',
      transport: 'stdio',
      headers: {
        'X-Copilot-Integration': 'vscode'
      }
    });
    await this.client.connect();
  }

  async callTool(toolName: string, params: any): Promise<any> {
    // VS Code Copilot 特定的工具调用格式
    return await this.client.invoke({
      method: 'tools/call',
      params: {
        toolName,
        parameters: params  // 注意：不同的参数名称
      }
    });
  }

  async listTools(): Promise<Tool[]> {
    const response = await this.client.invoke({
      method: 'tools/list'
    });
    return response.tools;
  }

  async disconnect(): Promise<void> {
    await this.client.disconnect();
  }
}

/**
 * MCP Manager - 统一管理多个 Provider
 */
export class MCPManager {
  private providers: Map<string, IMCPProvider> = new Map();
  private activeProvider: string | null = null;

  /**
   * 注册一个 MCP Provider
   */
  registerProvider(name: string, provider: IMCPProvider): void {
    this.providers.set(name, provider);
  }

  /**
   * 激活指定的 Provider
   */
  async activateProvider(name: string): Promise<void> {
    const provider = this.providers.get(name);
    if (!provider) {
      throw new Error(`Provider not found: ${name}`);
    }

    // 断开当前 provider
    if (this.activeProvider) {
      await this.deactivateProvider();
    }

    // 初始化并激活新 provider
    await provider.initialize();
    this.activeProvider = name;
  }

  /**
   * 断开当前 Provider
   */
  async deactivateProvider(): Promise<void> {
    if (this.activeProvider) {
      const provider = this.providers.get(this.activeProvider);
      if (provider) {
        await provider.disconnect();
      }
      this.activeProvider = null;
    }
  }

  /**
   * 调用工具（通过当前活跃的 Provider）
   */
  async callTool(toolName: string, params: any): Promise<any> {
    if (!this.activeProvider) {
      throw new Error('No active provider');
    }

    const provider = this.providers.get(this.activeProvider);
    if (!provider) {
      throw new Error(`Active provider not found: ${this.activeProvider}`);
    }

    return await provider.callTool(toolName, params);
  }

  /**
   * 获取当前可用工具
   */
  async listTools(): Promise<Tool[]> {
    if (!this.activeProvider) {
      return [];
    }

    const provider = this.providers.get(this.activeProvider);
    if (!provider) {
      return [];
    }

    return await provider.listTools();
  }

  /**
   * 获取当前活跃的 Provider 名称
   */
  getActiveProvider(): string | null {
    return this.activeProvider;
  }
}

/**
 * 使用示例
 */
export async function createMCPManager(): Promise<MCPManager> {
  const manager = new MCPManager();

  // 注册多个 Provider
  manager.registerProvider('cursor', new CursorMCPProvider());
  manager.registerProvider('copilot', new VSCodeCopilotMCPProvider());

  // 检测环境并激活相应的 Provider
  const isCursor = process.env.VSCODE_IPC_HOOK_CLI?.includes('cursor');
  const providerName = isCursor ? 'cursor' : 'copilot';

  await manager.activateProvider(providerName);

  console.log(`MCP Manager initialized with provider: ${providerName}`);

  return manager;
}
```

### 为什么使用 Provider 模式？

```
┌─────────────────────────────────────────────────────────┐
│         Provider 模式的优势                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 解耦                                              │
│     → 核心服务不依赖特定的 MCP 实现                     │
│     → 易于添加新的 Provider                             │
│                                                         │
│  2. 可测试                                            │
│     → 可以 Mock Provider 进行单元测试                   │
│     → 不需要真实的 MCP 连接                             │
│                                                         │
│  3. 灵活性                                            │
│     → 运行时切换 Provider                               │
│     → 支持多个 MCP 同时存在                            │
│                                                         │
│  4. 可维护                                            │
│     → 每个 Provider 独立维护                            │
│     → 接口变化不影响其他 Provider                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## MCP 高级功能

### 1. 资源订阅

```typescript
// 支持实时更新的资源
server.setRequestHandler(SubscribeRequestSchema, async (request) => {
  const { uri } = request.params;

  // 订阅资源
  subscriptions.add(uri);

  // 设置监听器
  const watcher = fs.watch(uri, () => {
    // 资源变化时通知客户端
    server.notification({
      method: 'notifications/resources/updated',
      params: {
        uri,
      },
    });
  });

  return {};
});
```

### 2. 流式响应

```typescript
// 支持流式返回大量数据
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name } = request.params;

  if (name === 'stream_large_file') {
    const stream = fs.createReadStream(largeFilePath);

    return {
      content: [
        {
          type: 'resource',
          uri: 'stream:///file',
          mimeType: 'text/plain',
        },
      ],
    };
  }
});
```

### 3. 权限管理

```typescript
// 定义权限级别
interface Permission {
  level: 'read' | 'write' | 'admin';
  resources: string[];
}

// 权限检查中间件
function checkPermission(permission: Permission) {
  return async (req, next) => {
    const userPermissions = getUserPermissions(req.user);

    if (!hasPermission(userPermissions, permission)) {
      throw new Error('Permission denied');
    }

    return next(req);
  };
}

// 应用权限检查
server.setRequestHandler(
  CallToolRequestSchema,
  checkPermission({ level: 'write', resources: ['fs'] }),
  handleToolCall
);
```

---

## MCP 最佳实践

### 1. 错误处理

```typescript
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    const result = await handleToolCall(request);
    return {
      content: [{ type: 'text', text: JSON.stringify(result) }],
    };
  } catch (error) {
    // 返回结构化的错误信息
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            error: error.name,
            message: error.message,
            stack: error.stack,
          }),
        },
      ],
      isError: true,
    };
  }
});
```

### 2. 性能优化

```typescript
// 使用 LRU 缓存
import { LRUCache } from 'lru-cache';

const cache = new LRUCache<string, any>({
  max: 500,
  ttl: 1000 * 60 * 5, // 5 分钟
});

server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;

  // 检查缓存
  if (cache.has(uri)) {
    return cache.get(uri);
  }

  // 获取资源
  const result = await fetchResource(uri);

  // 缓存结果
  cache.set(uri, result);

  return result;
});
```

### 3. 日志和监控

```typescript
import winston from 'winston';

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'mcp-server.log' }),
  ],
});

// 包装所有请求处理器
function withLogging(handler) {
  return async (request) => {
    const startTime = Date.now();

    logger.info({
      type: 'request',
      method: request.method,
      params: request.params,
    });

    try {
      const result = await handler(request);

      logger.info({
        type: 'response',
        method: request.method,
        duration: Date.now() - startTime,
      });

      return result;
    } catch (error) {
      logger.error({
        type: 'error',
        method: request.method,
        error: error.message,
        duration: Date.now() - startTime,
      });

      throw error;
    }
  };
}
```

---

## 常见问题

### Q1: MCP 和 Plugin 有什么区别？

**A**: **关注点不同**

- **MCP**: 专注于连接外部服务和数据源
- **Plugin**: 专注于扩展 Claude Code 的核心功能

使用 MCP 如果：
- 需要连接外部 API
- 需要访问数据库
- 需要实时数据流

使用 Plugin 如果：
- 需要自定义工具
- 需要修改 Claude Code 行为
- 需要复杂的交互逻辑

### Q2: MCP 服务器可以部署为独立服务吗？

**A**: 可以！

使用 HTTP/SSE 传输：

```typescript
import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js';

const express = require('express');
const app = express();

app.get('/sse', async (req, res) => {
  const transport = new SSEServerTransport('/messages', res);
  await server.connect(transport);
});

app.listen(3000, () => {
  console.log('MCP Server running on http://localhost:3000');
});
```

### Q3: 如何调试 MCP 服务器？

**A**: 使用调试模式

```bash
# 启用详细日志
MCP_DEBUG=1 node dist/index.js

# 在 VS Code 中调试
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Debug MCP Server",
      "program": "${workspaceFolder}/dist/index.js",
      "env": {
        "MCP_DEBUG": "1"
      }
    }
  ]
}
```

---

## 总结

### 关键要点

1. **MCP 核心概念**
   - 开放协议，用于 AI 与外部系统连接
   - 三大能力：资源、工具、提示词
   - JSON-RPC 2.0 协议

2. **MCP 架构**
   - Client-Server 模式
   - 多种传输方式（stdio、HTTP/SSE）
   - 标准化的消息格式

3. **Provider 模式**
   - 解耦不同的 MCP 实现
   - mybatis-boost 的实际应用
   - 支持运行时切换

4. **最佳实践**
   - 完善的错误处理
   - 性能优化（缓存）
   - 日志和监控

### 下一步

在下一章中，我们将学习 **Skills 系统**：
- Skills 的概念和用途
- 创建可重用的 Skills
- Skills 管理和组织
- 实际应用案例

---

## 进一步阅读

### 官方文档
- [MCP Protocol Specification](https://modelcontextprotocol.io/specs/)
- [MCP SDK Documentation](https://github.com/modelcontextprotocol/typescript-sdk)

### mybatis-boost 项目
- `C:\PythonProject\mybatis-boost\src\mcp\MCPManager.ts`
- `C:\PythonProject\mybatis-boost\CLAUDE.md`

### 相关章节
- [Chapter 9 - Plugin 系统](chapter-09-plugins.md)
- [Chapter 11 - Skills 系统](chapter-11-skills.md)

---

## 练习

完成以下练习：

1. **基本练习**
   - [ ] 创建一个简单的 MCP 服务器
   - [ ] 实现一个自定义工具
   - [ ] 在 Claude Code 中配置并测试

2. **进阶练习**
   - [ ] 实现资源订阅功能
   - [ ] 添加权限管理
   - [ ] 实现流式响应

3. **实战练习**
   - [ ] 为你的项目创建 MCP 服务器
   - [ ] 实现 Provider 模式支持多个 MCP
   - [ ] 添加监控和日志

---

**上一章**: [Chapter 9 - Plugin 系统](chapter-09-plugins.md)
**下一章**: [Chapter 11 - Skills 系统](chapter-11-skills.md)
