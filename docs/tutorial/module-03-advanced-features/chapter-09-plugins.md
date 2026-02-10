# Chapter 9: Plugin 系统

**模块**: Module 3 - 高级功能
**预计阅读时间**: 15 分钟
**难度**: ⭐⭐⭐

---

## 学习目标

本章结束后，你将能够：

- [ ] 理解 Claude Code Plugin 系统的架构
- [ ] 掌握 Plugin 的创建和配置
- [ ] 学会编写自定义 Plugin
- [ ] 了解 Plugin 与 MCP 的区别

---

## 前置知识

- [ ] 已完成 Module 2 - 核心工作流
- [ ] 了解 TypeScript/JavaScript 基础
- [ ] 熟悉 npm 包管理

---

## 什么是 Plugin 系统？

### Plugin 系统概述

**Claude Code Plugin** 是扩展 Claude Code 功能的模块化插件系统。

```
┌─────────────────────────────────────────────────────────┐
│              Claude Code Plugin 架构                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐      ┌─────────────┐                 │
│  │   Claude    │ ←──→ │   Plugin    │                 │
│  │    Code     │      │   System    │                 │
│  └─────────────┘      └─────────────┘                 │
│         ↑                      ↑                        │
│         │                      │                        │
│    ┌────┴────┐          ┌─────┴──────┐                │
│    │  Core   │          │  Plugins   │                │
│    │  Tools  │          │            │                │
│    └─────────┘          └────────────┘                │
│                              │                         │
│                    ┌─────────┼─────────┐              │
│                    │         │         │              │
│               ┌────┴───┐ ┌───┴───┐ ┌──┴────┐         │
│               │Plugin 1│ │Plugin 2│ │Plugin 3│        │
│               │(Linter)│ │(Test) │ │(Build)│         │
│               └────────┘ └───────┘ └───────┘         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Plugin vs MCP vs Skills

| 特性 | Plugin | MCP | Skills |
|------|--------|-----|--------|
| **用途** | 扩展核心功能 | 连接外部服务 | 可重用能力 |
| **实现方式** | npm 包 | MCP 服务器 | Prompt 模板 |
| **配置位置** | `package.json` | `.mcp.json` | `.skills/` |
| **复杂度** | 高 | 中 | 低 |
| **示例** | 自定义工具、命令 | 数据库、API | 代码生成、审查 |

### Plugin 的典型用途

```
┌─────────────────────────────────────────────────────────┐
│              Plugin 常见使用场景                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🔧 自定义工具                                           │
│     - 特定语言的格式化器                                 │
│     - 自定义代码分析器                                   │
│     - 项目特定工具                                       │
│                                                         │
│  📦 集成外部系统                                         │
│     - CI/CD 平台                                        │
│     - 项目管理系统                                       │
│     - 监控和日志                                         │
│                                                         │
│  🎨 工作流增强                                           │
│     - 自定义 Git 工作流                                  │
│     - 自动化测试策略                                     │
│     - 代码生成器                                         │
│                                                         │
│  🔐 企业集成                                             │
│     - 内部工具集成                                       │
│     - 权限管理                                           │
│     - 审计日志                                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Plugin 基础

### Plugin 结构

一个典型的 Claude Code Plugin 结构：

```
my-claude-plugin/
├── package.json           # npm 包配置
├── tsconfig.json          # TypeScript 配置
├── src/
│   ├── index.ts           # Plugin 入口
│   ├── tools/             # 自定义工具
│   │   ├── myTool.ts
│   │   └── anotherTool.ts
│   ├── commands/          # 自定义命令
│   │   └── myCommand.ts
│   └── utils/             # 工具函数
└── README.md
```

### 最小 Plugin 示例

**package.json**:

```json
{
  "name": "@my-org/my-claude-plugin",
  "version": "1.0.0",
  "description": "My Claude Code Plugin",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "claude": {
    "plugin": true
  },
  "scripts": {
    "build": "tsc",
    "dev": "tsc --watch"
  },
  "peerDependencies": {
    "@anthropic-ai/claude-code": "^1.0.0"
  },
  "devDependencies": {
    "@anthropic-ai/claude-code": "^1.0.0",
    "typescript": "^5.0.0"
  }
}
```

**src/index.ts**:

```typescript
import { Plugin } from '@anthropic-ai/claude-code';

export const myPlugin: Plugin = {
  name: 'my-plugin',
  version: '1.0.0',

  // 初始化插件
  async initialize(context) {
    console.log('My plugin initialized!');
  },

  // 注册自定义工具
  tools: [
    {
      name: 'my_custom_tool',
      description: 'A custom tool that does something useful',
      inputSchema: {
        type: 'object',
        properties: {
          message: {
            type: 'string',
            description: 'The message to process'
          }
        },
        required: ['message']
      },
      async handler(params, context) {
        return {
          success: true,
          result: `Processed: ${params.message}`
        };
      }
    }
  ],

  // 注册自定义命令
  commands: [
    {
      name: 'mycommand',
      description: 'A custom command',
      async handler(context) {
        return 'Hello from my command!';
      }
    }
  ]
};

export default myPlugin;
```

---

## 创建自定义 Plugin

### 实战示例：项目文档生成器

让我们创建一个实用的 Plugin：自动生成项目文档。

#### 步骤 1: 初始化项目

```bash
mkdir claude-doc-generator
cd claude-doc-generator
npm init -y
npm install --save-dev typescript @types/node
```

#### 步骤 2: 配置 TypeScript

**tsconfig.json**:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "declaration": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

#### 步骤 3: 实现 Plugin 功能

**src/tools/docGenerator.ts**:

```typescript
import { promises as fs } from 'fs';
import path from 'path';

interface DocGeneratorInput {
  projectPath: string;
  outputPath: string;
  includePatterns: string[];
}

export const docGeneratorTool = {
  name: 'generate_docs',
  description: 'Generate documentation from project source code',

  inputSchema: {
    type: 'object',
    properties: {
      projectPath: {
        type: 'string',
        description: 'Path to the project directory'
      },
      outputPath: {
        type: 'string',
        description: 'Path where documentation will be generated'
      },
      includePatterns: {
        type: 'array',
        items: { type: 'string' },
        description: 'Glob patterns for files to include'
      }
    },
    required: ['projectPath', 'outputPath']
  },

  async handler(params: DocGeneratorInput, context: any) {
    const { projectPath, outputPath, includePatterns = ['**/*.ts'] } = params;

    try {
      // 1. 扫描项目文件
      const files = await scanFiles(projectPath, includePatterns);

      // 2. 解析文件内容
      const documentation = await parseFiles(files);

      // 3. 生成文档
      const markdown = generateMarkdown(documentation);

      // 4. 写入文件
      await fs.writeFile(outputPath, markdown, 'utf-8');

      return {
        success: true,
        result: `Documentation generated at ${outputPath}`,
        filesProcessed: files.length
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
};

async function scanFiles(projectPath: string, patterns: string[]): Promise<string[]> {
  // 实现文件扫描逻辑
  const glob = require('glob');
  const files: string[] = [];

  for (const pattern of patterns) {
    const matched = glob.sync(pattern, { cwd: projectPath });
    files.push(...matched);
  }

  return files;
}

async function parseFiles(files: string[]): Promise<any[]> {
  // 实现文件解析逻辑
  const docs = [];

  for (const file of files) {
    const content = await fs.readFile(file, 'utf-8');
    // 解析注释、类、函数等
    docs.push({
      file,
      content,
      exports: extractExports(content)
    });
  }

  return docs;
}

function generateMarkdown(documentation: any[]): string {
  let markdown = '# Project Documentation\n\n';

  for (const doc of documentation) {
    markdown += `## ${doc.file}\n\n`;
    markdown += '```typescript\n';
    markdown += doc.content;
    markdown += '\n```\n\n';
  }

  return markdown;
}

function extractExports(content: string): string[] {
  // 提取导出内容
  const exports: string[] = [];
  const exportRegex = /export\s+(?:const|function|class|interface)\s+(\w+)/g;
  let match;

  while ((match = exportRegex.exec(content)) !== null) {
    exports.push(match[1]);
  }

  return exports;
}
```

**src/commands/docCommand.ts**:

```typescript
export const docCommand = {
  name: 'docs',
  description: 'Generate project documentation',

  async handler(context: any) {
    const { projectPath } = context;

    // 使用 docGeneratorTool
    const result = await context.tools.generate_docs({
      projectPath,
      outputPath: './DOCUMENTATION.md',
      includePatterns: ['src/**/*.ts']
    });

    return result.success
      ? `✓ Documentation generated successfully`
      : `✗ Failed: ${result.error}`;
  }
};
```

**src/index.ts**:

```typescript
import { Plugin } from '@anthropic-ai/claude-code';
import { docGeneratorTool } from './tools/docGenerator';
import { docCommand } from './commands/docCommand';

export const docGeneratorPlugin: Plugin = {
  name: 'doc-generator',
  version: '1.0.0',

  description: 'Automatically generate project documentation from source code',

  async initialize(context) {
    console.log('Doc Generator Plugin initialized');
  },

  tools: [docGeneratorTool],
  commands: [docCommand]
};

export default docGeneratorPlugin;
```

#### 步骤 4: 构建和发布

```bash
npm run build
npm publish
```

#### 步骤 5: 在项目中使用

**项目的 package.json**:

```json
{
  "devDependencies": {
    "@my-org/doc-generator": "^1.0.0"
  },
  "claude": {
    "plugins": [
      "@my-org/doc-generator"
    ]
  }
}
```

**在 Claude Code 中使用**:

```
> 使用 doc-generator 插件生成项目文档

[Claude 调用插件工具]

✓ Documentation generated successfully

文档已生成到 ./DOCUMENTATION.md
```

---

## Plugin 高级功能

### 1. 生命周期钩子

```typescript
export const myPlugin: Plugin = {
  name: 'my-plugin',

  // 插件初始化时调用
  async initialize(context) {
    // 设置配置
    // 注册监听器
  },

  // 会话开始时调用
  async sessionStart(context) {
    // 初始化会话状态
  },

  // 会话结束时调用
  async sessionEnd(context) {
    // 清理资源
  },

  // 工具执行前调用
  async beforeTool(toolName, params, context) {
    // 验证参数
    // 记录日志
  },

  // 工具执行后调用
  async afterTool(toolName, result, context) {
    // 处理结果
    // 更新状态
  }
};
```

### 2. 配置管理

```typescript
interface PluginConfig {
  apiKey?: string;
  endpoint?: string;
  options?: Record<string, any>;
}

export const myPlugin: Plugin = {
  name: 'my-plugin',

  async initialize(context) {
    // 读取配置
    const config = context.getConfig('my-plugin') as PluginConfig;

    // 验证配置
    if (!config.apiKey) {
      throw new Error('API key is required');
    }

    // 存储配置供后续使用
    this.config = config;
  }
};
```

**配置文件 (claude.config.json)**:

```json
{
  "plugins": {
    "my-plugin": {
      "apiKey": "your-api-key",
      "endpoint": "https://api.example.com",
      "options": {
        "timeout": 30000,
        "retries": 3
      }
    }
  }
}
```

### 3. 事件系统

```typescript
export const myPlugin: Plugin = {
  name: 'my-plugin',

  async initialize(context) {
    // 监听事件
    context.on('file:changed', async (file) => {
      // 文件变化时执行操作
    });

    context.on('command:executed', async (command) => {
      // 命令执行后执行操作
    });

    context.on('error', async (error) => {
      // 错误处理
    });
  }
};
```

### 4. 与 MCP 集成

```typescript
export const myPlugin: Plugin = {
  name: 'my-plugin',

  async initialize(context) {
    // 注册 MCP 服务器
    context.registerMCPServer({
      name: 'my-mcp-server',
      command: 'node',
      args: ['./dist/mcp-server.js']
    });
  }
};
```

---

## Plugin 最佳实践

### 1. 命名规范

```
✅ 好的命名：
- @scope/claude-plugin-name
- claude-plugin-format
- @company/claude-ci-integration

❌ 不好的命名：
- my-plugin
- cool-tool
- random-name
```

### 2. 错误处理

```typescript
async handler(params, context) {
  try {
    // 执行操作
    const result = await doSomething(params);

    return {
      success: true,
      result
    };
  } catch (error) {
    // 记录错误
    context.logger.error('Operation failed', error);

    // 返回友好的错误信息
    return {
      success: false,
      error: error.message,
      recoverable: true
    };
  }
}
```

### 3. 性能优化

```typescript
// 使用缓存
const cache = new Map();

async handler(params, context) {
  const cacheKey = JSON.stringify(params);

  if (cache.has(cacheKey)) {
    return cache.get(cacheKey);
  }

  const result = await expensiveOperation(params);
  cache.set(cacheKey, result);

  return result;
}

// 使用流处理
async function processLargeFile(filePath: string) {
  const stream = fs.createReadStream(filePath);

  for await (const chunk of stream) {
    // 分块处理
    await processChunk(chunk);
  }
}
```

### 4. 类型安全

```typescript
import { z } from 'zod';

const inputSchema = z.object({
  message: z.string().min(1).max(1000),
  count: z.number().int().min(1).max(100).optional()
});

async handler(params, context) {
  // 验证输入
  const validated = inputSchema.parse(params);

  // 类型推断正常工作
  const { message, count = 1 } = validated;
}
```

---

## 常见问题

### Q1: Plugin 和 Skill 有什么区别？

**A**: **复杂度和用途不同**

- **Plugin**: 完整的 npm 包，可以包含复杂逻辑、外部依赖、自定义工具
- **Skill**: Prompt 模板，用于简单的可重用能力

选择 Plugin 如果：
- 需要自定义工具
- 需要外部依赖
- 需要复杂的状态管理

选择 Skill 如果：
- 只是重用提示词
- 不需要额外代码
- 简单的代码生成

### Q2: 如何调试 Plugin？

**A**: 使用调试模式

```bash
# 启用调试日志
CLAUDE_DEBUG=1 claude

# 在 VS Code 中调试
# 创建 .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Debug Plugin",
      "program": "${workspaceFolder}/node_modules/.bin/claude",
      "cwd": "${workspaceFolder}",
      "env": {
        "CLAUDE_DEBUG": "1"
      }
    }
  ]
}
```

### Q3: Plugin 可以访问文件系统吗？

**A**: 可以，但需要权限

```typescript
async handler(params, context) {
  // 明确声明需要的权限
  const permission = await context.requestPermission({
    type: 'fs:read',
    path: params.filePath
  });

  if (!permission.granted) {
    return {
      success: false,
      error: 'Permission denied'
    };
  }

  // 执行文件操作
  const content = await fs.readFile(params.filePath, 'utf-8');
}
```

---

## 总结

### 关键要点

1. **Plugin 系统架构**
   - 模块化的扩展系统
   - 与 MCP、Skills 协同工作
   - 支持 npm 包分发

2. **Plugin 核心功能**
   - 自定义工具（Tools）
   - 自定义命令（Commands）
   - 生命周期钩子
   - 配置管理

3. **Plugin 最佳实践**
   - 遵循命名规范
   - 完善错误处理
   - 性能优化
   - 类型安全

### 下一步

在下一章中，我们将深入学习 **MCP (Model Context Protocol)**：
- MCP 的核心概念
- 如何创建 MCP 服务器
- MCP 工具的实现
- 与 Claude Code 的集成

---

## 进一步阅读

### 官方文档
- Claude Code Plugin API Reference
- MCP Protocol Specification

### 相关章节
- [Chapter 10 - MCP 深度解析](chapter-10-mcp.md) - 下一章
- [Chapter 11 - Skills 系统](chapter-11-skills.md)

---

## 练习

完成以下练习：

1. **基本练习**
   - [ ] 创建一个简单的 Plugin
   - [ ] 实现一个自定义工具
   - [ ] 在项目中测试 Plugin

2. **进阶练习**
   - [ ] 实现生命周期钩子
   - [ ] 添加配置管理
   - [ ] 实现错误处理

3. **实战练习**
   - [ ] 创建一个实用的 Plugin（如代码格式化器）
   - [ ] 发布到 npm
   - [ ] 在实际项目中使用

---

**上一章**: [Chapter 8 - 验证与安全](../module-02-core-workflows/chapter-08-verification.md)
**下一章**: [Chapter 10 - MCP 深度解析](chapter-10-mcp.md)
