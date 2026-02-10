# Chapter 32: 设置工具集

## 学习目标

完成本章后，你将能够：

- 配置 Claude Code 的核心设置
- 理解和管理工具权限
- 配置和使用 MCP 服务器
- 创建自定义 Slash Commands
- 设置 Hooks 工作流
- 优化整体开发环境

## 前置知识

- [Module 1: Claude Code 基础](../module-01-fundamentals/)
- [Chapter 31: 创建 CLAUDE.md 模板](chapter-31-claude-md-template.md)

---

## 32.1 核心设置

### 32.1.1 配置文件

```typescript
/**
 * Claude Code 配置文件位置
 */

const configLocations = {
  // Windows
  windows: `
    用户配置：
    C:\\Users\\<用户名>\\AppData\\Roaming\\claude\\config.json

    项目配置（可选）：
    <项目根目录>\\.claude\\config.json
  `,

  // macOS / Linux
  unix: `
    用户配置：
    ~/.config/claude/config.json

    项目配置（可选）：
    <项目根目录>/.claude/config.json
  `
};

/**
 * 配置文件结构
 */

interface ClaudeCodeConfig {
  // 模型选择
  model?: string;

  // API 配置
  apiKey?: string;
  baseURL?: string;

  // 默认 Thinking Mode
  thinkingMode?: "think" | "think-hard" | "think-harder" | "ultrathink";

  // 权限配置
  permissions?: {
    // 工具权限
    edit?: "always" | "ask" | "never";
    bash?: "always" | "ask" | "never";
    write?: "always" | "ask" | "never";

    // Bash 命令权限
    allowedCommands?: string[];
    blockedCommands?: string[];
  };

  // 其他设置
  maxTokens?: number;
  temperature?: number;
  timeout?: number;
}

/**
 * 示例配置文件
 */

const exampleConfig: ClaudeCodeConfig = {
  model: "claude-opus-4-5",
  thinkingMode: "think-hard",
  permissions: {
    edit: "always",
    bash: "always",
    write: "always",
    allowedCommands: [
      "git",
      "npm",
      "pnpm",
      "yarn",
      "node",
      "python",
      "pytest",
      "jest"
    ],
    blockedCommands: [
      "rm -rf /",
      "dd",
      "mkfs"
    ]
  },
  maxTokens: 200000,
  temperature: 0.1
};
```

### 32.1.2 基本配置

```bash
# 创建配置目录
mkdir -p ~/.config/claude

# 创建配置文件
cat > ~/.config/claude/config.json << 'EOF'
{
  "model": "claude-opus-4-5",
  "thinkingMode": "think-hard",
  "permissions": {
    "edit": "always",
    "bash": "always",
    "write": "always"
  }
}
EOF

# 验证配置
claude-code --version
```

---

## 32.2 权限管理

### 32.2.1 理解权限系统

```typescript
/**
 * Claude Code 权限系统
 */

interface PermissionConfig {
  // 工具级别权限
  tools: {
    [toolName: string]: "always" | "ask" | "never";
  };

  // 命令级别权限（Bash）
  commands: {
    allowed: string[];    // 总是允许的命令
    blocked: string[];    // 总是阻止的命令
    patterns: {
      allow: RegExp[];    // 允许模式
      block: RegExp[];    // 阻止模式
    };
  };

  // 上下文权限
  context: {
    allowedPaths: string[];    // 允许访问的路径
    blockedPaths: string[];    // 阻止访问的路径
  };
}

/**
 * 推荐的权限配置策略
 */

const permissionStrategies = {
  // 开发环境：宽松配置
  development: {
    philosophy: "效率优先，适当保护",
    config: {
      edit: "always",
      bash: "always",
      write: "always",
      blockedCommands: ["rm -rf", "dd", "mkfs", ":(){ :|:& };:"]
    }
  },

  // 生产环境：严格配置
  production: {
    philosophy: "安全优先，谨慎操作",
    config: {
      edit: "ask",
      bash: "ask",
      write: "ask",
      allowedCommands: ["git", "cat", "ls", "grep"]
    }
  },

  // 容器/沙盒环境：安全配置
  container: {
    philosophy: "容器隔离，可以宽松",
    config: {
      edit: "always",
      bash: "always",
      write: "always",
      // 容器内允许所有命令
      blockedCommands: []
    }
  }
};
```

### 32.2.2 设置权限

```typescript
/**
 * 权限配置的 4 种方式
 */

const permissionSetupMethods = {
  // 方法 1：交互式提示
  interactive: `
    首次使用工具时，Claude 会询问权限。

    示例：
    > Claude: "我想运行 npm install"
    > 系统: "允许 Bash 执行 'npm install'？"
    > 选项: [Always allow] [Allow once] [Deny]

    推荐：
    - 开发命令：Always allow
    - 危险命令：Allow once
    - 不需要：Deny
  `,

  // 方法 2：/permissions 命令
  cliCommand: `
    使用 /permissions 命令管理运行时权限。

    命令：
    /permissions              # 查看当前权限
    /permissions allow git    # 允许 git 命令
    /permissions block rm     # 阻止 rm 命令
  `,

  // 方法 3：配置文件
  configFile: `
    在 ~/.config/claude/config.json 中配置。

    {
      "permissions": {
        "edit": "always",
        "bash": "always",
        "write": "always",
        "allowedCommands": ["git", "npm", "pnpm"],
        "blockedCommands": ["rm -rf"]
      }
    }
  `,

  // 方法 4：CLI 标志
  cliFlags: `
    启动时通过命令行标志设置。

    claude-code \\
      --allow-edit \\
      --allow-bash \\
      --block-command "rm -rf"
  `
};

/**
 * 推荐的权限配置
 */

const recommendedPermissions = {
  // 总是允许（安全）
  alwaysAllow: [
    "edit",          // 编辑文件（版本控制保护）
    "write",         // 写入文件（版本控制保护）
    "git:*",         // 所有 Git 命令（可撤销）
    "npm:*",         // npm 命令（开发环境）
    "pnpm:*",        // pnpm 命令（开发环境）
    "yarn:*",        // yarn 命令（开发环境）
    "node",          // Node.js
    "python",        // Python
    "pytest",        // pytest
    "jest",          // Jest
    "cat",           // 查看文件
    "ls",            // 列出文件
    "grep",          // 搜索文件
    "find"           // 查找文件
  ],

  // 总是阻止（危险）
  alwaysBlock: [
    "rm -rf /",      // 删除根目录
    "rm -rf .*",     // 删除所有隐藏文件
    "dd",            // 磁盘操作
    "mkfs",          // 文件系统创建
    "chmod 000",     // 移除所有权限
    "kill -9",       // 强制终止关键进程
    ":(){ :|:& };:", // Fork 炸弹
    "sudo rm",       // sudo 删除
    "format",        // Windows 格式化
    "del /q /s *"    // Windows 删除所有
  ],

  // 询问确认（需谨慎）
  askConfirm: [
    "docker",        // Docker 命令
    "kubectl",       // Kubernetes 命令
    "aws",           // AWS CLI
    "gcloud",        // GCP CLI
    "apt",           // 包管理器
    "yum",           // 包管理器
    "brew",          // 包管理器
    "systemctl"      // 系统服务
  ]
};
```

---

## 32.3 MCP 服务器配置

### 32.3.1 MCP 基础

```typescript
/**
 * MCP (Model Context Protocol)
 * 让 Claude 连接到外部工具和服务
 */

interface MCPServer {
  name: string;
  description: string;
  command: string;
  args?: string[];
  env?: Record<string, string>;
  disabled?: boolean;
}

/**
 * MCP 配置文件位置
 */

const mcpConfigPath = {
  windows: `C:\\Users\\<用户名>\\AppData\\Roaming\\claude\\mcp.json`,
  unix: `~/.config/claude/mcp.json`
};

/**
 * MCP 配置文件示例
 */

const mcpConfigExample = {
  mcpServers: {
    // GitHub 服务器
    github: {
      command: "npx",
      args: ["-y", "@modelcontextprotocol/server-github"],
      env: {
        GITHUB_TOKEN: process.env.GITHUB_TOKEN
      }
    },

    // Google Drive 服务器
    "google-drive": {
      command: "npx",
      args: ["-y", "@modelcontextprotocol/server-google-drive"],
      env: {
        GOOGLE_TOKEN: process.env.GOOGLE_TOKEN
      }
    },

    // Postgres 服务器
    postgres: {
      command: "npx",
      args: ["-y", "@modelcontextprotocol/server-postgres"],
      env: {
        POSTGRES_CONNECTION_STRING: process.env.POSTGRES_URL
      }
    },

    // 文件系统服务器
    filesystem: {
      command: "npx",
      args: [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/allowed/path",
        "/another/allowed/path"
      ]
    },

    // Puppeteer 服务器
    puppeteer: {
      command: "npx",
      args: ["-y", "@modelcontextprotocol/server-puppeteer"]
    }
  }
};
```

### 32.3.2 常用 MCP 服务器

```typescript
/**
 * 推荐的 MCP 服务器
 */

const recommendedMCPServers = [
  {
    name: "GitHub",
    package: "@modelcontextprotocol/server-github",
    description: "访问 GitHub 仓库、Issues、PR",
    setup: `
      1. 获取 GitHub Token: https://github.com/settings/tokens
      2. 设置环境变量: export GITHUB_TOKEN=your_token
      3. 添加到 mcp.json
    `,
    useCases: [
      "查看仓库信息",
      "读取文件内容",
      "创建 Issues",
      "查看 PR 状态"
    ]
  },

  {
    name: "Google Drive",
    package: "@modelcontextprotocol/server-google-drive",
    description: "访问 Google Drive 文件",
    setup: `
      1. OAuth 认证
      2. 授权访问 Drive
      3. 配置 mcp.json
    `,
    useCases: [
      "读取文档",
      "创建文件",
      "搜索文件"
    ]
  },

  {
    name: "Postgres",
    package: "@modelcontextprotocol/server-postgres",
    description: "查询 PostgreSQL 数据库",
    setup: `
      1. 准备数据库连接字符串
      2. 设置 POSTGRES_CONNECTION_STRING
      3. 配置 mcp.json
    `,
    useCases: [
      "查询数据",
      "分析表结构",
      "生成报告"
    ]
  },

  {
    name: "Puppeteer",
    package: "@modelcontextprotocol/server-puppeteer",
    description: "自动化浏览器操作",
    setup: `
      1. 安装: npx -y @modelcontextprotocol/server-puppeteer
      2. 配置 mcp.json
      3. 启动 Claude Code
    `,
    useCases: [
      "截图",
      "PDF 生成",
      "网页测试",
      "数据抓取"
    ]
  },

  {
    name: "Filesystem",
    package: "@modelcontextprotocol/server-filesystem",
    description: "访问指定路径的文件系统",
    setup: `
      1. 选择允许访问的路径
      2. 配置 mcp.json with paths
      3. 注意：只允许配置的路径
    `,
    useCases: [
      "读取日志文件",
      "访问系统目录",
      "批量文件操作"
    ]
  },

  {
    name: "Brave Search",
    package: "@modelcontextprotocol/server-brave-search",
    description: "使用 Brave 进行网络搜索",
    setup: `
      1. 获取 Brave API Key
      2. 设置 BRAVE_API_KEY
      3. 配置 mcp.json
    `,
    useCases: [
      "网络搜索",
      "获取最新信息",
      "研究话题"
    ]
  }
];
```

### 32.3.3 调试 MCP

```bash
# 使用 --mcp-debug 标志启动
claude-code --mcp-debug

# 查看加载的 MCP 服务器
# 在 Claude Code 中询问：列出所有可用的 MCP 工具

# 测试 MCP 连接
# 在 Claude Code 中询问：测试 [服务器名称] 连接

# 查看 MCP 日志
# 日志会显示 MCP 服务器的启动状态和错误信息
```

```typescript
/**
 * MCP 调试技巧
 */

const mcpDebugging = {
  checkList: [
    "1. MCP 服务器是否在 mcp.json 中配置？",
    "2. 环境变量是否正确设置？",
    "3. 命令是否可以手动运行？",
    "4. 包是否已安装（npx -y）？",
    "5. 是否使用了 --mcp-debug？"
  ],

  commonErrors: [
    {
      error: "Command not found",
      solution: "确保包可以通过 npx 运行"
    },
    {
      error: "Environment variable not set",
      solution: "检查并设置所需的环境变量"
    },
    {
      error: "Permission denied",
      solution: "检查文件系统权限和路径"
    },
    {
      error: "Connection timeout",
      solution: "检查网络连接和 API 可用性"
    }
  ]
};
```

---

## 32.4 自定义 Slash Commands

### 32.4.1 创建 Slash Commands

```typescript
/**
 * Slash Commands: 可重用的提示词模板
 */

interface SlashCommand {
  name: string;
  description: string;
  template: string;
  arguments?: string[];
}

/**
 * Slash Commands 存储位置
 */

const slashCommandsLocation = {
  // 用户全局命令
  global: `~/.claude/commands/`,

  // 项目特定命令
  project: `<project-root>/.claude/commands/`
};

/**
 * 示例 Slash Commands
 */

const exampleSlashCommands: SlashCommand[] = [
  {
    name: "review",
    description: "审查代码并提供改进建议",
    template: `
请审查以下代码，提供：

1. **功能正确性**：代码是否正确实现了预期功能？
2. **代码质量**：命名、结构、可读性如何？
3. **潜在问题**：是否有 bug、安全漏洞或性能问题？
4. **改进建议**：具体的改进建议

代码：
\`\`\`
$CODE
\`\`\`
    `
  },

  {
    name: "test",
    description: "为代码生成单元测试",
    template: `
为以下代码生成完整的单元测试：

要求：
1. 使用项目测试框架（Jest/Vitest/Pytest）
2. 覆盖正常情况和边界情况
3. 包含必要的 setup 和 teardown
4. 添加清晰的测试描述

代码：
\`\`\`
$CODE
\`\`\`
    `
  },

  {
    name: "explain",
    description: "解释代码的工作原理",
    template: `
请详细解释以下代码：

1. **概述**：代码的整体目的
2. **逐步分析**：每一部分的作用
3. **关键概念**：使用的重要概念或模式
4. **潜在问题**：可能的问题或改进点

代码：
\`\`\`
$CODE
\`\`\`
    `
  },

  {
    name: "refactor",
    description: "重构代码以提高质量",
    template: `
重构以下代码以提升：

1. **可读性**：更清晰的命名和结构
2. **可维护性**：更容易修改和扩展
3. **性能**：优化性能（如果有明显改进空间）

保持功能不变，提供重构后的代码和变更说明。

代码：
\`\`\`
$CODE
\`\`\`
    `
  },

  {
    name: "document",
    description: "为代码生成文档",
    template: `
为以下代码生成完整的文档：

1. **函数/类描述**：清晰的用途说明
2. **参数说明**：每个参数的类型和用途
3. **返回值说明**：返回值的类型和含义
4. **使用示例**：1-2 个使用示例
5. **注意事项**：重要的使用注意事项

代码：
\`\`\`
$CODE
\`\`\`
    `
  },

  {
    name: "debug",
    description: "帮助调试代码问题",
    template: `
帮我调试以下代码：

问题描述：
$PROBLEM

代码：
\`\`\`
$CODE
\`\`\`

错误信息：
\`\`\`
$ERROR
\`\`\`

请分析可能的原因并提供解决方案。
    `,
    arguments: ["PROBLEM", "CODE", "ERROR"]
  }
];
```

### 32.4.2 创建项目特定命令

```bash
# 创建项目命令目录
mkdir -p .claude/commands

# 创建命令文件
cat > .claude/commands/api.md << 'EOF'
# API 端点生成

为以下需求创建 API 端点：

需求描述：
$REQUIREMENT

要求：
1. 遵循项目架构（controller -> service -> repository）
2. 包含输入验证
3. 包含错误处理
4. 添加适当的 TypeScript 类型
5. 包含 JSDoc 注释
EOF

# 使用方式：/api "创建用户注册端点"
```

```typescript
/**
 * 项目特定 Slash Commands 示例
 */

const projectSpecificCommands = {
  // React 项目命令
  react: [
    {
      name: "component",
      description: "创建 React 组件",
      template: `
创建一个 React 组件：

组件名称：$NAME
功能描述：$DESCRIPTION

要求：
1. 使用 TypeScript
2. 遵循项目组件结构
3. 包含 PropTypes 或 TypeScript 接口
4. 添加基本样式
      `
    },
    {
      name: "hook",
      description: "创建自定义 Hook",
      template: `
创建一个自定义 React Hook：

Hook 名称：$NAME
功能描述：$DESCRIPTION

要求：
1. 使用 TypeScript
2. 遵循 Hook 规则
3. 包含错误处理
4. 添加使用示例
      `
    }
  ],

  // API 项目命令
  api: [
    {
      name: "endpoint",
      description: "创建 API 端点",
      template: `
创建 API 端点：

路径：$PATH
方法：$METHOD
功能：$DESCRIPTION

要求：
1. 遵循分层架构
2. 包含验证
3. 包含错误处理
4. 添加 OpenAPI 文档
      `
    },
    {
      name: "middleware",
      description: "创建中间件",
      template: `
创建 Express 中间件：

功能：$FUNCTION

要求：
1. 遵循 Express 中间件模式
2. 包含错误处理
3. 可配置选项
      `
    }
  ],

  // 测试命令
  testing: [
    {
      name: "unit-test",
      description: "创建单元测试",
      template: `
为以下代码创建单元测试：

\`\`\`
$CODE
\`\`\`

要求：
1. 使用项目测试框架
2. 覆盖所有分支
3. 包含边界情况
4. 使用清晰的测试描述
      `
    }
  ]
};
```

---

## 32.5 Hooks 配置

### 32.5.1 Hooks 基础

```typescript
/**
 * Hooks: 在工具执行前后自动运行的命令
 */

interface HookConfig {
  // 工具前钩子
  beforeTool?: {
    [toolName: string]: string | string[];
  };

  // 工具后钩子
  afterTool?: {
    [toolName: string]: string | string[];
  };

  // 用户提示提交前钩子
  beforeUserPrompt?: string[];

  // 响应完成后钩子
  afterResponse?: string[];
}

/**
 * Hooks 配置示例
 */

const hookConfigExample: HookConfig = {
  // 编辑前运行 lint
  beforeTool: {
    edit: ["eslint --fix", "prettier --write"]
  },

  // 编辑后格式化
  afterTool: {
    edit: "prettier --write $FILE"
  },

  // Bash 命令后检查 git 状态
  afterTool: {
    bash: "git status --short"
  }
};
```

### 32.5.2 实用 Hook 配置

```typescript
/**
 * 推荐的 Hooks 配置
 */

const recommendedHooks = {
  // 代码质量
  codeQuality: {
    beforeEdit: ["npm run lint"],
    afterEdit: ["npx prettier --write $FILE"],
    afterWrite: ["git add $FILE"]
  },

  // 测试
  testing: {
    beforeCommit: ["npm test"],
    afterWrite: ["npm test -- --related $FILE"]
  },

  // 通知
  notifications: {
    afterResponse: ["notify-send 'Claude Code' 'Response complete'"]
  },

  // 日志
  logging: {
    beforeUserPrompt: ["echo $(date) >> ~/.claude/prompt.log"],
    afterResponse: ["echo '---' >> ~/.claude/prompt.log"]
  }
};

/**
 * Hooks 配置文件
 */

const hooksConfig = {
  // 在配置文件中配置
  config: `
{
  "hooks": {
    "beforeTool": {
      "edit": ["npm run lint-check"]
    },
    "afterTool": {
      "edit": ["npx prettier --write $FILE"],
      "bash": ["git status --short"]
    },
    "beforeUserPrompt": [
      "echo \"Timestamp: $(date +%s)\""
    ]
  }
}
  `
};
```

### 32.5.3 Hook 变量

```typescript
/**
 * Hooks 中可用的变量
 */

const hookVariables = {
  // 文件相关
  "$FILE": "当前操作的文件路径",
  "$DIR": "当前操作的目录路径",
  "$FILES": "所有操作的文件路径（数组）",

  // 命令相关
  "$COMMAND": "执行的命令",
  "$EXIT_CODE": "命令退出码",

  // Claude 相关
  "$CLAUDE_RESPONSE": "Claude 的响应",
  "$USER_PROMPT": "用户提示词",

  // 时间相关
  "$TIMESTAMP": "当前时间戳",
  "$DATE": "当前日期",
  "$TIME": "当前时间",

  // Git 相关（如果在 git 仓库中）
  "$GIT_BRANCH": "当前 Git 分支",
  "$GIT_COMMIT": "当前 Git commit",
  "$GIT_ROOT": "Git 仓库根目录"
};
```

---

## 32.6 环境变量

### 32.6.1 必需的环境变量

```bash
# Claude Code API 密钥
export ANTHROPIC_API_KEY="your-api-key"

# API Base URL（如果使用代理）
export ANTHROPIC_BASE_URL="https://api.anthropic.com"

# 模型选择（可选）
export CLAUDE_MODEL="claude-opus-4-5"
```

### 32.6.2 MCP 服务器环境变量

```bash
# GitHub MCP
export GITHUB_TOKEN="your-github-token"

# Google Drive MCP
export GOOGLE_TOKEN="your-google-token"
export GOOGLE_CREDENTIALS="path/to/credentials.json"

# Postgres MCP
export POSTGRES_CONNECTION_STRING="postgresql://user:pass@host:5432/db"

# Brave Search MCP
export BRAVE_API_KEY="your-brave-api-key"

# Puppeteer MCP
export PUPPETEER_EXECUTABLE_PATH="/path/to/chrome"

# Filesystem MCP
export ALLOWED_PATHS="/path1,/path2"
```

### 32.6.3 环境变量管理

```bash
# 创建 .env 文件（不要提交到 git）
cat > .env << 'EOF'
# Claude Code
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-opus-4-5

# MCP 服务器
GITHUB_TOKEN=ghp_...
POSTGRES_CONNECTION_STRING=postgresql://...
EOF

# 添加到 .gitignore
echo ".env" >> .gitignore

# 加载环境变量（使用 direnv）
cat > .envrc << 'EOF'
source .env
EOF

# 或在 shell 配置中加载
# ~/.bashrc 或 ~/.zshrc
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi
```

---

## 32.7 完整设置示例

### 32.7.1 React/Next.js 项目完整配置

```bash
#!/bin/bash
# setup-claude.sh - React 项目 Claude Code 设置

echo "🚀 设置 Claude Code for React/Next.js 项目"

# 1. 创建 CLAUDE.md
cat > CLAUDE.md << 'EOF'
# 项目名称

## 技术栈
- Next.js 14 (App Router)
- TypeScript 5.3+
- Tailwind CSS
- Zustand (状态管理)

## 项目结构
src/
├── app/              # Next.js App Router
├── components/       # React 组件
├── lib/              # 工具函数
└── types/            # TypeScript 类型

## 常用命令
pnpm dev              # 开发服务器
pnpm build            # 生产构建
pnpm lint             # ESLint
pnpm test             # Vitest

## 编码规范
- 使用 TypeScript 严格模式
- 组件使用 PascalCase
- 文件名使用 kebab-case
- 使用 Prettier 格式化

## 重要提醒
- 所有组件必须 TypeScript
- Server Components 优先
- 客户端组件添加 'use client'
EOF

# 2. 创建配置目录
mkdir -p .claude/commands

# 3. 创建 Slash Commands
cat > .claude/commands/component.md << 'EOF'
# 创建 React 组件

创建一个 React 组件：

名称：$NAME
描述：$DESCRIPTION

要求：
- TypeScript
- Server Component（默认）
- 如需客户端交互，添加 'use client'
- Tailwind CSS 样式
EOF

cat > .claude/commands/hook.md << 'EOF'
# 创建自定义 Hook

创建一个自定义 React Hook：

名称：$NAME
描述：$DESCRIPTION

要求：
- TypeScript
- 遵循 Hook 规则
- 错误处理
- 使用示例
EOF

# 4. 创建 .env 示例
cat > .env.example << 'EOF'
# Claude Code
ANTHROPIC_API_KEY=your-api-key-here

# MCP 服务器（可选）
GITHUB_TOKEN=your-github-token
EOF

# 5. 更新 .gitignore
echo ".env" >> .gitignore
echo ".claude/.env" >> .gitignore

# 6. 创建 Hooks 配置
mkdir -p .claude
cat > .claude/hooks.json << 'EOF'
{
  "hooks": {
    "afterTool": {
      "edit": ["npx prettier --write $FILE"]
    }
  }
}
EOF

echo "✅ Claude Code 设置完成！"
echo ""
echo "下一步："
echo "1. 复制 .env.example 到 .env 并添加你的 API key"
echo "2. 根据项目需求调整 CLAUDE.md"
echo "3. 运行 claude-code 开始使用"
```

### 32.7.2 Node.js API 项目完整配置

```bash
#!/bin/bash
# setup-claude.sh - Node.js API 项目 Claude Code 设置

echo "🚀 设置 Claude Code for Node.js API 项目"

# 1. 创建 CLAUDE.md
cat > CLAUDE.md << 'EOF'
# API 项目

## 技术栈
- Node.js 20+
- TypeScript 5.3+
- Express 4.x
- Prisma ORM
- PostgreSQL

## 项目结构
src/
├── controllers/      # 请求处理
├── services/         # 业务逻辑
├── repositories/     # 数据访问
├── models/           # 数据模型
├── middlewares/      # Express 中间件
├── routes/           # 路由定义
├── utils/            # 工具函数
└── index.ts          # 入口文件

## 常用命令
pnpm dev              # 开发模式（nodemon）
pnpm build            # 构建
pnpm start            # 生产模式
pnpm test             # Jest 测试
pnpm lint             # ESLint

## 架构模式
分层架构：Routes → Controllers → Services → Repositories → Models

## 编码规范
- 异步使用 async/await
- 错误使用统一错误类
- 所有路由验证输入
- 所有端点验证认证

## 重要提醒
- 所有 API 调用通过 services 层
- 不在 controller 中直接调用 Prisma
- 使用统一错误处理中间件
- 敏感数据使用环境变量
EOF

# 2. 创建 Slash Commands
mkdir -p .claude/commands

cat > .claude/commands/endpoint.md << 'EOF'
# 创建 API 端点

创建 API 端点：

路径：$PATH
方法：$METHOD
描述：$DESCRIPTION

要求：
1. 在 routes/ 创建路由
2. 在 controllers/ 创建控制器
3. 在 services/ 创建服务
4. 在 repositories/ 创建仓库（如需要）
5. 包含输入验证
6. 包含错误处理
7. 添加 JSDoc 注释
EOF

cat > .claude/commands/model.md << 'EOF'
# 创建 Prisma Model

创建 Prisma 模型：

模型名称：$NAME
字段：$FIELDS

要求：
1. 在 prisma/schema.prisma 中添加模型
2. 生成迁移：pnpm prisma migrate dev
3. 生成客户端：pnpm prisma generate
EOF

# 3. 创建权限配置
mkdir -p .claude
cat > .claude/permissions.json << 'EOF'
{
  "permissions": {
    "edit": "always",
    "bash": "always",
    "write": "always",
    "allowedCommands": [
      "pnpm",
      "node",
      "npx",
      "git",
      "cat",
      "ls",
      "grep"
    ],
    "blockedCommands": [
      "rm -rf",
      "dd",
      "mkfs"
    ]
  }
}
EOF

# 4. 创建 MCP 配置
cat > ~/.config/claude/mcp.json << 'EOF'
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "$DATABASE_URL"
      }
    }
  }
}
EOF

echo "✅ Claude Code API 项目设置完成！"
```

---

## 32.8 练习

### 练习 1：基础设置

为你的项目完成基础设置：
1. 创建 CLAUDE.md
2. 配置基本权限
3. 创建 2-3 个 Slash Commands

### 练习 2：MCP 服务器

设置一个 MCP 服务器：
1. 选择一个适合的 MCP 服务器
2. 配置认证
3. 测试连接
4. 使用 MCP 工具

### 练习 3：Hooks 配置

创建有用的 Hooks：
1. 配置编辑后自动格式化
2. 配置 Bash 命令后显示 Git 状态
3. 测试 Hooks 工作

### 练习 4：完整工作流

建立完整的开发工作流：
1. 配置所有工具
2. 创建 Slash Commands
3. 设置 Hooks
4. 测试完整流程

---

## 32.9 进一步阅读

- [Chapter 31: 创建 CLAUDE.md 模板](chapter-31-claude-md-template.md) - 上一章
- [Chapter 33: 衡量成功](chapter-33-measuring-success.md) - 下一章
- [Module 3: 高级功能](../module-03-advanced-features/) - MCP、Skills、Hooks 详细说明

---

## 视频脚本

### Episode 32: 设置工具集 (20 分钟)

#### [0:00-1:00] 引入

**视觉元素**：
- 标题："Claude Code 工具集设置"
- 配置文件概览

**内容**：
> 前面我们创建了 CLAUDE.md，现在我们来设置完整的工具集。
>
> 这包括：权限管理、MCP 服务器、Slash Commands、Hooks 配置等。
>
> 好的设置可以大大提升你的 AI 辅助开发效率。

#### [1:00-4:00] 核心设置

**视觉元素**：
- 配置文件位置
- 配置文件结构示例

**内容**：
> **配置文件位置**：
>
> - Windows: `C:\Users\<用户>\AppData\Roaming\claude\config.json`
> - macOS/Linux: `~/.config/claude/config.json`
>
> **基本配置**：
> - 模型选择
> - Thinking Mode
> - 权限设置
>
> [展示配置文件示例]

#### [4:00-8:00] 权限管理

**视觉元素**：
- 权限配置的 4 种方式
- 推荐的权限配置

**内容**：
> **权限配置的 4 种方式**：
>
> 1. **交互式提示** - 首次使用时询问
> 2. **/permissions 命令** - 运行时管理
> 3. **配置文件** - 永久配置
> 4. **CLI 标志** - 会话级别
>
> **推荐配置**：
> - ✅ edit: always（版本控制保护）
> - ✅ git: always（可撤销）
> - ✅ npm/pnpm: always（开发环境）
> - ❌ rm -rf: blocked（危险命令）

#### [8:00-12:00] MCP 服务器

**视觉元素**：
- MCP 配置示例
- 常用 MCP 服务器列表

**内容**：
> **MCP (Model Context Protocol)** 让 Claude 连接外部工具。
>
> **常用 MCP 服务器**：
> - **GitHub** - 访问仓库、Issues、PR
> - **Postgres** - 查询数据库
> - **Puppeteer** - 浏览器自动化
> - **Brave Search** - 网络搜索
>
> [演示配置一个 MCP 服务器]
>
> **调试技巧**：
> - 使用 `--mcp-debug` 标志
> - 检查环境变量
> - 测试连接

#### [12:00-16:00] Slash Commands 和 Hooks

**视觉元素**：
- Slash Command 示例
- Hooks 配置示例

**内容**：
> **Slash Commands**：可重用的提示词模板
>
> 示例命令：
> - `/review` - 审查代码
> - `/test` - 生成测试
> - `/explain` - 解释代码
>
> [创建项目特定命令]
>
> **Hooks**：工具执行前后自动运行
>
> 有用的 Hooks：
> - 编辑后自动格式化
> - Bash 命令后显示 Git 状态
> - 提交前运行测试

#### [16:00-20:00] 完整设置演示

**视觉元素**：
- 完整设置脚本
- 项目配置示例

**内容**：
> [演示为 React 项目创建完整设置]
>
> 1. 创建 CLAUDE.md
> 2. 配置权限
> 3. 创建 Slash Commands
> 4. 设置 Hooks
> 5. 配置 MCP（可选）
>
> **总结**：
>
> 1. ✅ 从基础配置开始
> 2. ✅ 根据项目定制
> 3. ✅ 持续优化
> 4. ✅ 团队共享配置
>
> 下一章，我们将学习如何衡量 AI 辅助开发的成功。
