# Chapter 13: 自定义 Commands

**模块**: Module 3 - 高级功能
**预计阅读时间**: 12 分钟
**难度**: ⭐⭐⭐

---

## 学习目标

本章结束后，你将能够：

- [ ] 理解自定义 Commands 的概念
- [ ] 掌握 Commands 的创建和配置
- [ ] 学会编写参数化 Commands
- [ ] 了解 Commands 与其他功能的区别

---

## 前置知识

- [ ] 已完成 Chapter 12 - Hooks 配置
- [ ] 熟悉 Claude Code 的基本命令
- [ ] 了解 JSON/YAML 配置

---

## 什么是自定义 Commands？

### Commands 概述

**Claude Code Commands** 是用户定义的斜杠命令，
用于快速执行常见任务和工作流。

```
┌─────────────────────────────────────────────────────────┐
│              内置 vs 自定义 Commands                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  内置 Commands                                          │
│  ─────────────────────────────────────────────          │
│  /help           - 显示帮助信息                         │
│  /clear          - 清空对话上下文                       │
│  /init           - 初始化项目配置                       │
│  /mode           - 切换模式（plan/auto）                │
│  /permissions    - 管理权限                             │
│  /commit         - 提交变更                             │
│                                                         │
│  自定义 Commands                                        │
│  ─────────────────────────────────────────────          │
│  /review         - 执行代码审查                         │
│  /test           - 运行测试套件                         │
│  /deploy         - 部署到生产环境                       │
│  /docs           - 生成文档                             │
│  /refactor       - 重构选中代码                         │
│  /fix            - 修复 bug                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Commands vs Skills vs Hooks

| 特性 | Commands | Skills | Hooks |
|------|----------|--------|-------|
| **触发方式** | 用户主动调用 | 用户主动调用 | 自动触发 |
| **参数支持** | 是 | 否 | 否（环境变量） |
| **返回值** | 是 | 是 | 否（仅状态） |
| **交互性** | 高 | 中 | 低 |
| **适用场景** | 快捷操作 | 重用提示词 | 自动化流程 |

### Commands 的价值

```
┌─────────────────────────────────────────────────────────┐
│              自定义 Commands 的好处                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ⚡ 快速执行                                            │
│     → 一条命令完成复杂任务                               │
│     → 无需重复输入提示词                                 │
│                                                         │
│  🔄 标准化工作流                                         │
│     → 团队统一操作方式                                   │
│     → 减少人为错误                                       │
│                                                         │
│  📊 可追踪                                              │
│     → 命令执行记录                                       │
│     → 审计日志                                           │
│                                                         │
│  🎯 专业化                                              │
│     → 针对项目定制                                       │
│     → 集成项目工具链                                     │
│                                                         │
│  🤝 可共享                                              │
│     → 团队共享命令                                       │
│     → 知识沉淀                                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Commands 基础

### Commands 配置文件

**.claude/commands.json** (项目级) 或 **~/.claude/commands.json** (全局):

```json
{
  "commands": [
    {
      "name": "review",
      "description": "Perform comprehensive code review",
      "prompt": "Please review the following code for security, performance, and best practices...",
      "parameters": [
        {
          "name": "files",
          "description": "Files to review",
          "required": false,
          "type": "array"
        }
      ]
    },
    {
      "name": "test",
      "description": "Run tests and generate coverage report",
      "prompt": "Run all tests and provide a summary of results...",
      "parameters": []
    }
  ]
}
```

### Command 结构

```typescript
interface CommandConfig {
  // 命令名称（调用时使用 /name）
  name: string;

  // 命令描述（显示在帮助中）
  description: string;

  // 提示词模板
  prompt: string;

  // 参数定义
  parameters?: Array<{
    name: string;
    description: string;
    required: boolean;
    type: 'string' | 'number' | 'boolean' | 'array';
    default?: any;
    enum?: any[];
  }>;

  // 快捷别名
  aliases?: string[];

  // 权限要求
  permissions?: string[];

  // 执行前确认
  confirmation?: string;

  // 仅在特定模式下可用
  mode?: 'plan' | 'auto' | 'both';

  // 子命令
  subcommands?: CommandConfig[];
}
```

---

## 创建 Commands

### 实战示例 1: 代码审查命令

**.claude/commands.json**:

```json
{
  "commands": [
    {
      "name": "review",
      "description": "Perform comprehensive code review",
      "aliases": ["rv", "code-review"],
      "confirmation": "This will review all changes. Continue?",
      "prompt": "Please perform a comprehensive code review using the code-review skill.\n\nFocus on:\n1. Security vulnerabilities\n2. Performance issues\n3. Code quality and maintainability\n4. Test coverage\n5. Documentation\n\n{% if files %}Files to review:\n{{files}}\n{% else %}Reviewing all uncommitted changes.{% endif %}",
      "parameters": [
        {
          "name": "files",
          "description": "Specific files to review (comma-separated)",
          "required": false,
          "type": "array"
        },
        {
          "name": "strict",
          "description": "Enable strict review mode",
          "required": false,
          "type": "boolean",
          "default": false
        }
      ],
      "subcommands": [
        {
          "name": "security",
          "description": "Focus on security issues only",
          "prompt": "Please perform a security-focused code review.\n\nCheck for:\n1. SQL injection\n2. XSS vulnerabilities\n3. Authentication/authorization issues\n4. Sensitive data exposure\n5. Dependency vulnerabilities\n\n{% if files %}Files:\n{{files}}{% endif %}"
        },
        {
          "name": "performance",
          "description": "Focus on performance issues only",
          "prompt": "Please perform a performance-focused code review.\n\nCheck for:\n1. Inefficient algorithms\n2. Memory leaks\n3. Unnecessary re-renders\n4. Database query optimization\n5. Caching opportunities\n\n{% if files %}Files:\n{{files}}{% endif %}"
        }
      ]
    }
  ]
}
```

**使用示例**:

```
> /review

[审查所有变更]

> /review src/api/user.ts src/models/User.ts

[审查指定文件]

> /review security src/auth/

[执行安全审查子命令]

> /review performance --strict

[执行严格的性能审查]
```

### 实战示例 2: 测试命令

**.claude/commands.json**:

```json
{
  "commands": [
    {
      "name": "test",
      "description": "Run tests and provide analysis",
      "aliases": ["t", "tests"],
      "prompt": "Please run the test suite and provide a comprehensive analysis.\n\nSteps:\n1. Run the tests using npm test\n2. Analyze the results\n3. Identify failing tests\n4. Suggest fixes for failures\n5. Report coverage\n\n{% if suite %}Test suite: {{suite}}{% endif %}\n{% if coverage %}Include coverage report{% endif %}",
      "parameters": [
        {
          "name": "suite",
          "description": "Specific test suite to run",
          "required": false,
          "type": "string",
          "enum": ["unit", "integration", "e2e", "all"],
          "default": "all"
        },
        {
          "name": "coverage",
          "description": "Include coverage report",
          "required": false,
          "type": "boolean",
          "default": false
        },
        {
          "name": "watch",
          "description": "Run tests in watch mode",
          "required": false,
          "type": "boolean",
          "default": false
        }
      ],
      "subcommands": [
        {
          "name": "unit",
          "description": "Run unit tests only",
          "prompt": "Run unit tests only:\n\nnpm run test:unit\n\nAnalyze results and suggest fixes for any failures."
        },
        {
          "name": "coverage",
          "description": "Generate coverage report",
          "prompt": "Generate test coverage report:\n\nnpm run test:coverage\n\nProvide:\n1. Overall coverage percentage\n2. Per-file coverage\n3. Uncovered lines\n4. Suggestions for improving coverage"
        },
        {
          "name": "failing",
          "description": "Run only failing tests",
          "prompt": "Run only the tests that failed last time:\n\nnpm run test -- --onlyFailures\n\nAnalyze the failures and suggest fixes."
        }
      ]
    }
  ]
}
```

### 实战示例 3: 部署命令

**.claude/commands.json**:

```json
{
  "commands": [
    {
      "name": "deploy",
      "description": "Deploy application to environment",
      "aliases": ["dep"],
      "confirmation": "Deploy to {{env}}. Are you sure?",
      "prompt": "Please deploy the application to {{env}} environment.\n\nDeployment checklist:\n1. ✅ All tests passing\n2. ✅ Build successful\n3. ✅ Environment variables configured\n4. ✅ Migration scripts ready\n5. ✅ Rollback plan prepared\n\nSteps:\n1. Run tests\n2. Build application\n3. Run database migrations\n4. Deploy to {{env}}\n5. Run smoke tests\n6. Verify deployment\n\n{% if branch %}Branch: {{branch}}{% endif %}\n{% if tag %}Tag: {{tag}}{% endif %}",
      "parameters": [
        {
          "name": "env",
          "description": "Target environment",
          "required": true,
          "type": "string",
          "enum": ["dev", "staging", "production"]
        },
        {
          "name": "branch",
          "description": "Branch to deploy",
          "required": false,
          "type": "string"
        },
        {
          "name": "tag",
          "description": "Git tag to deploy",
          "required": false,
          "type": "string"
        }
      ],
      "subcommands": [
        {
          "name": "rollback",
          "description": "Rollback last deployment",
          "confirmation": "Rollback {{env}}. Are you sure?",
          "prompt": "Rollback the last deployment on {{env}} environment.\n\nSteps:\n1. Identify current version\n2. Identify previous version\n3. Rollback to previous version\n4. Verify rollback\n5. Report status"
        },
        {
          "name": "status",
          "description": "Check deployment status",
          "prompt": "Check the current deployment status for {{env}} environment.\n\nReport:\n1. Current deployed version\n2. Deployment time\n3. Health check status\n4. Recent error logs"
        }
      ]
    }
  ]
}
```

---

## 高级 Commands

### 1. 带有脚本执行的 Commands

```json
{
  "commands": [
    {
      "name": "format",
      "description": "Format code using project formatter",
      "prompt": "Format all code files using the project's configured formatter.\n\n1. Run the format command\n2. Check for any formatting issues\n3. Report results",
      "script": {
        "command": "npm run format",
        "onSuccess": "Code formatted successfully!",
        "onFailure": "Formatting failed. Please check the errors above."
      }
    }
  ]
}
```

### 2. 多步骤 Commands

```json
{
  "commands": [
    {
      "name": "pr",
      "description": "Create pull request with all checks",
      "prompt": "Create a pull request with the following workflow:\n\n1. Run linter and fix issues\n2. Run type check\n3. Run all tests\n4. Build project\n5. Create feature branch if needed\n6. Commit changes with conventional commit message\n7. Push to remote\n8. Create PR with template\n9. Run checks\n\nBranch: {{branch}}\nTitle: {{title}}",
      "parameters": [
        {
          "name": "branch",
          "description": "Feature branch name",
          "required": false,
          "type": "string",
          "default": "feature/auto-pr"
        },
        {
          "name": "title",
          "description": "PR title",
          "required": false,
          "type": "string",
          "default": "Automated PR"
        }
      ]
    }
  ]
}
```

### 3. 交互式 Commands

```json
{
  "commands": [
    {
      "name": "refactor",
      "description": "Interactive refactoring tool",
      "prompt": "Let's refactor the selected code. I'll guide you through the process.\n\n1. First, show me the code you want to refactor\n2. I'll analyze it and suggest improvements\n3. We'll discuss the changes\n4. I'll implement the refactoring\n5. We'll verify tests still pass\n\nWhat code would you like to refactor?",
      "interactive": true,
      "steps": [
        {
          "prompt": "Here's the code I want to refactor:\n\n{{code}}\n\nPlease analyze it.",
          "response": "Analyzing..."
        },
        {
          "prompt": "What improvements would you suggest?",
          "response": "Suggestions:\n1. ...\n2. ...\n3. ..."
        },
        {
          "prompt": "Please implement these changes.",
          "response": "Implementing..."
        },
        {
          "prompt": "Verify tests pass.",
          "response": "Running tests..."
        }
      ]
    }
  ]
}
```

---

## Commands 组织

### 按功能分类

```
.claude/
├── commands/
│   ├── review.json          # 审查相关命令
│   ├── testing.json         # 测试相关命令
│   ├── deployment.json      # 部署相关命令
│   ├── documentation.json   # 文档相关命令
│   └── development.json     # 开发相关命令
```

**.claude/commands/review.json**:

```json
{
  "commands": [
    {
      "name": "review",
      "description": "Perform code review",
      "prompt": "..."
    },
    {
      "name": "audit",
      "description": "Security audit",
      "prompt": "..."
    },
    {
      "name": "scan",
      "description": "Dependency scan",
      "prompt": "..."
    }
  ]
}
```

### 命令命名最佳实践

```
✅ 好的命令名：
- /review        - 清晰，动词
- /test:unit     - 层级化
- /deploy:prod   - 明确目标
- /fmt           - 简短但清晰

❌ 不好的命令名：
- /doSomething   - 太模糊
- /command1      - 无意义
- /a             - 太短
- /very-long-command-name-that-types-forever  - 太长
```

---

## Commands 与其他功能集成

### 1. Commands 调用 Skills

```json
{
  "commands": [
    {
      "name": "review",
      "description": "Code review using skill",
      "prompt": "Use the code-review skill to review:\n\n{% if files %}{{files}}{% else %}All changes{% endif %}"
    }
  ]
}
```

### 2. Commands 触发 Hooks

```json
{
  "commands": [
    {
      "name": "deploy",
      "description": "Deploy with pre-flight checks",
      "prompt": "Deploy to production",
      "beforeHooks": [
        "check-tests",
        "check-build",
        "check-security"
      ],
      "afterHooks": [
        "notify-team",
        "update-status"
      ]
    }
  ]
}
```

### 3. Commands 使用 MCP 工具

```json
{
  "commands": [
    {
      "name": "db-backup",
      "description": "Backup database using MCP",
      "prompt": "Use the database MCP tool to create a backup.\n\nDatabase: {{database}}\nDestination: {{destination}}",
      "parameters": [
        {
          "name": "database",
          "description": "Database name",
          "required": true,
          "type": "string"
        },
        {
          "name": "destination",
          "description": "Backup destination",
          "required": false,
          "type": "string",
          "default": "./backups"
        }
      ]
    }
  ]
}
```

---

## Commands 最佳实践

### 1. 清晰的描述

```json
{
  "commands": [
    {
      "name": "test",
      "description": "Run tests",  // ✅ 清晰
      // vs
      "description": "Execute the testing suite to verify code correctness",  // ❌ 太长
      "prompt": "..."
    }
  ]
}
```

### 2. 合理的参数

```json
{
  "commands": [
    {
      "name": "deploy",
      "prompt": "...",
      "parameters": [
        {
          "name": "env",
          "required": true,        // ✅ 关键参数
          "type": "string",
          "enum": ["dev", "prod"]
        },
        {
          "name": "verbose",
          "required": false,       // ✅ 可选参数
          "type": "boolean",
          "default": false
        }
      ]
    }
  ]
}
```

### 3. 提供确认

```json
{
  "commands": [
    {
      "name": "deploy",
      "description": "Deploy to production",
      "confirmation": "This will deploy to PRODUCTION. Continue?",  // ✅ 危险操作确认
      "prompt": "..."
    }
  ]
}
```

### 4. 使用子命令

```json
{
  "commands": [
    {
      "name": "test",
      "subcommands": [
        { "name": "unit", "description": "Run unit tests" },
        { "name": "integration", "description": "Run integration tests" },
        { "name": "e2e", "description": "Run end-to-end tests" }
      ]
    }
  ]
}
```

---

## 常见问题

### Q1: Commands 和 Scripts 有什么区别？

**A**: **抽象层次不同**

```bash
# Scripts（直接执行）
/deploy.sh production

# Commands（通过 Claude）
/deploy env=production

# Commands 可以：
# - 理解意图
# - 处理错误
# - 提供反馈
# - 做智能决策
```

### Q2: 如何调试 Command？

**A**: 添加详细日志

```json
{
  "commands": [
    {
      "name": "test",
      "description": "Run tests",
      "prompt": "Running tests with DEBUG enabled...\n\n{% if debug %}Debug mode is ON{% endif %}\n\n[执行测试...]",
      "parameters": [
        {
          "name": "debug",
          "description": "Enable debug output",
          "type": "boolean",
          "default": false
        }
      ]
    }
  ]
}
```

### Q3: Commands 可以嵌套调用吗？

**A**: 可以，但要注意循环

```json
{
  "commands": [
    {
      "name": "ci",
      "description": "Run full CI pipeline",
      "prompt": "Execute the following commands in order:\n\n1. /test\n2. /lint\n3. /build\n4. /security-check\n\nReport overall status."
    }
  ]
}
```

---

## 总结

### 关键要点

1. **Commands 是快捷操作**
   - 斜杠命令调用
   - 参数化支持
   - 可嵌套子命令

2. **Commands 结构**
   - 名称、描述、提示词
   - 参数定义
   - 子命令组织

3. **Commands 类型**
   - 简单命令：单一操作
   - 复杂命令：多步骤工作流
   - 交互式命令：对话式操作

4. **最佳实践**
   - 清晰命名
   - 合理参数
   - 危险操作确认
   - 使用子命令

### Module 3 总结

恭喜！你已完成 **Module 3 - 高级功能**！

### 你已经掌握了：

**Chapter 9**: Plugin 系统
- Plugin 架构和创建
- 自定义工具和命令
- 生命周期管理

**Chapter 10**: MCP 深度解析
- MCP 协议和服务器
- Provider 模式（mybatis-boost 案例）
- 资源、工具、提示词

**Chapter 11**: Skills 系统
- Skills 概念和结构
- 可重用提示词模板
- Skills 管理

**Chapter 12**: Hooks 配置
- Pre/Post/Error Hooks
- 自动化工作流
- 钩子链和条件执行

**Chapter 13**: 自定义 Commands
- 命令创建和配置
- 参数化命令
- 子命令组织

### 准备好进入下一模块了吗？

**Module 4 - mybatis-boost 实战案例** 将教你：
- 项目架构概览
- CST vs 正则表达式
- Provider 模式深入解析
- 性能优化策略
- 测试与质量保证

继续你的学习之旅吧！

---

## 进一步阅读

### 官方文档
- Claude Code Commands Reference
- Configuration Guide

### 相关章节
- [Chapter 11 - Skills 系统](chapter-11-skills.md)
- [Module 4 - mybatis-boost 实战](../module-04-real-world-mybatis-boost/)

### mybatis-boost 项目
- `C:\PythonProject\mybatis-boost\CLAUDE.md`
- `C:\PythonProject\mybatis-boost\package.json`

---

## 练习

完成以下练习：

1. **基本练习**
   - [ ] 创建一个简单的命令
   - [ ] 添加参数支持
   - [ ] 测试命令执行

2. **进阶练习**
   - [ ] 创建带子命令的命令
   - [ ] 实现交互式命令
   - [ ] 集成 Skills 和 Hooks

3. **实战练习**
   - [ ] 为你的项目创建命令集
   - [ ] 实现完整的部署命令
   - [ ] 团队共享和文档化

---

**上一章**: [Chapter 12 - Hooks 配置](chapter-12-hooks.md)
**下一模块**: [Module 4 - mybatis-boost 实战案例](../module-04-real-world-mybatis-boost/)
