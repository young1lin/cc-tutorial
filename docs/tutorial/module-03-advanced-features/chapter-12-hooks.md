# Chapter 12: Hooks 配置

**模块**: Module 3 - 高级功能
**预计阅读时间**: 14 分钟
**难度**: ⭐⭐⭐

---

## 学习目标

本章结束后，你将能够：

- [ ] 理解 Hooks 系统的概念和作用
- [ ] 掌握 Hooks 的配置和使用
- [ ] 学会编写自定义 Hooks
- [ ] 了解 Hooks 在工作流中的应用

---

## 前置知识

- [ ] 已完成 Chapter 11 - Skills 系统
- [ ] 了解基本的命令行操作
- [ ] 熟悉脚本编写基础

---

## 什么是 Hooks 系统？

### Hooks 概述

**Claude Code Hooks** 是在特定事件发生时自动执行的脚本，
允许你在工作流中插入自定义逻辑。

```
┌─────────────────────────────────────────────────────────┐
│              Hooks 工作流程                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  用户请求                                                │
│     ↓                                                   │
│  ┌─────────────────┐                                   │
│  │  Pre-Hooks      │ ← 在处理前执行                    │
│  │  - validate     │                                   │
│  │  - prepare      │                                   │
│  └────────┬────────┘                                   │
│           ↓                                             │
│  ┌─────────────────┐                                   │
│  │  Claude 处理    │                                   │
│  │  - 分析         │                                   │
│  │  - 执行         │                                   │
│  └────────┬────────┘                                   │
│           ↓                                             │
│  ┌─────────────────┐                                   │
│  │  Post-Hooks     │ ← 在处理后执行                    │
│  │  - notify       │                                   │
│  │  - cleanup      │                                   │
│  └────────┬────────┘                                   │
│           ↓                                             │
│  返回结果                                                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Hooks 的价值

```
┌─────────────────────────────────────────────────────────┐
│              Hooks 的典型用途                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🔍 验证和检查                                          │
│     → 确保请求符合项目规范                               │
│     → 检查敏感信息                                       │
│     → 验证代码风格                                       │
│                                                         │
│  📊 通知和报告                                          │
│     → 发送 Slack/Teams 通知                             │
│     → 更新项目管理系统                                   │
│     → 记录审计日志                                       │
│                                                         │
│  🔄 自动化工作流                                        │
│     → 自动运行测试                                       │
│     → 自动格式化代码                                     │
│     → 自动提交变更                                       │
│                                                         │
│  🛡️ 安全和保护                                          │
│     → 阻止危险操作                                       │
│     → 检查权限                                           │
│     → 审计日志                                           │
│                                                         │
│  🔧 自定义集成                                          │
│     → 集成 CI/CD                                         │
│     → 连接外部服务                                       │
│     → 自定义行为                                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Hooks 基础

### Hooks 类型

```
┌─────────────────────────────────────────────────────────┐
│              Hooks 事件类型                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Pre-Hooks（执行前）                                    │
│  ────────────────────────────                           │
│  • beforeCommand    - 任何命令执行前                    │
│  • beforeEdit       - 编辑文件前                         │
│  • beforeRead       - 读取文件前                         │
│  • beforeRun        - 运行命令前                         │
│  • beforeCommit     - Git 提交前                         │
│                                                         │
│  Post-Hooks（执行后）                                   │
│  ────────────────────────────                           │
│  • afterCommand     - 任何命令执行后                    │
│  • afterEdit        - 编辑文件后                         │
│  • afterRead        - 读取文件后                         │
│  • afterRun         - 运行命令后                         │
│  • afterCommit      - Git 提交后                         │
│                                                         │
│  Error-Hooks（错误时）                                  │
│  ────────────────────────────                           │
│  • onError          - 命令执行出错时                    │
│  • onEditError      - 编辑文件失败时                     │
│  • onRunError       - 运行命令失败时                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Hooks 配置文件

**~/.claude/hooks.json** (全局) 或 **项目/.claude/hooks.json** (项目级):

```json
{
  "hooks": {
    "beforeEdit": [
      {
        "name": "check-sensitive-data",
        "command": "node scripts/check-sensitive.js",
        "runSilently": false
      },
      {
        "name": "validate-code-style",
        "command": "npm run lint-check",
        "runSilently": true
      }
    ],
    "afterEdit": [
      {
        "name": "format-code",
        "command": "npm run format",
        "runSilently": true
      }
    ],
    "beforeCommit": [
      {
        "name": "run-tests",
        "command": "npm test",
        "runSilently": false
      },
      {
        "name": "check-documentation",
        "command": "node scripts/check-docs.js",
        "runSilently": false
      }
    ],
    "afterCommit": [
      {
        "name": "notify-team",
        "command": "node scripts/notify-commit.js",
        "runSilently": true
      }
    ],
    "onError": [
      {
        "name": "log-error",
        "command": "node scripts/log-error.js",
        "runSilently": true
      }
    ]
  }
}
```

### Hook 配置属性

```typescript
interface HookConfig {
  // Hook 名称（用于识别）
  name: string;

  // 要执行的命令
  command: string;

  // 是否静默运行（不显示输出）
  runSilently?: boolean;

  // 是否阻塞（失败时阻止操作继续）
  blockOnError?: boolean;

  // 超时时间（毫秒）
  timeout?: number;

  // 环境变量
  env?: Record<string, string>;

  // 仅在特定条件下运行
  condition?: {
    // 仅对特定文件模式
    files?: string[];

    // 仅对特定命令
    commands?: string[];

    // 仅在特定分支
    branches?: string[];
  };
}
```

---

## 创建 Hooks

### 实战示例：敏感信息检查器

让我们创建一个完整的 Hook 系统，防止敏感信息泄露。

#### 步骤 1: 创建 Hook 脚本

**scripts/check-sensitive.js**:

```javascript
#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// 敏感信息模式
const SENSITIVE_PATTERNS = [
  {
    name: 'API Key',
    pattern: /(?:api[_-]?key|apikey)['":\s]*[=]['":\s]*([a-zA-Z0-9-_]{20,})/gi,
    severity: 'critical'
  },
  {
    name: 'AWS Secret',
    pattern: /aws[_-]?secret[_-]?access[_-]?key['":\s]*[=]['":\s]*([a-zA-Z0-9/+=]{40})/gi,
    severity: 'critical'
  },
  {
    name: 'Password',
    pattern: /password['":\s]*[=]['":\s]*['"]([^'"]{8,})['"]/gi,
    severity: 'high'
  },
  {
    name: 'Private Key',
    pattern: /-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----/g,
    severity: 'critical'
  },
  {
    name: 'Token',
    pattern: /(?:token|bearer|auth)['":\s]*[=]['":\s]*['"]([a-zA-Z0-9-_]{20,})['"]/gi,
    severity: 'medium'
  }
];

// 忽略的目录
const IGNORED_DIRS = [
  'node_modules',
  '.git',
  'dist',
  'build',
  'coverage',
  '.next',
  '.nuxt'
];

// 忽略的文件模式
const IGNORED_PATTERNS = [
  /\.lock$/,
  /\.env\.\w+$/,  // .env.local, .env.development 等（但允许 .env）
  /package-lock\.json$/,
  /yarn\.lock$/
];

function findFiles(dir, fileList = []) {
  const files = fs.readdirSync(dir);

  for (const file of files) {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);

    if (stat.isDirectory()) {
      // 跳过忽略的目录
      if (!IGNORED_DIRS.includes(file)) {
        findFiles(filePath, fileList);
      }
    } else {
      // 检查是否应该忽略此文件
      const shouldIgnore = IGNORED_PATTERNS.some(pattern =>
        pattern.test(file)
      );

      if (!shouldIgnore) {
        fileList.push(filePath);
      }
    }
  }

  return fileList;
}

function checkFile(filePath) {
  const issues = [];

  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n');

    for (const pattern of SENSITIVE_PATTERNS) {
      let match;
      const regex = new RegExp(pattern.pattern);

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        regex.lastIndex = 0;

        while ((match = regex.exec(line)) !== null) {
          issues.push({
            line: i + 1,
            type: pattern.name,
            severity: pattern.severity,
            text: line.trim(),
            match: match[1] || match[0]
          });
        }
      }
    }
  } catch (error) {
    // 无法读取文件（可能是二进制文件）
  }

  return issues;
}

function main() {
  // 获取变更的文件列表（从 git 或参数）
  const args = process.argv.slice(2);
  const targetPath = args[0] || '.';

  console.log(`\x1b[36m%s\x1b[0m`, '🔍 Scanning for sensitive information...');

  let filesToCheck = [];

  if (args.length > 0) {
    // 检查指定的文件
    filesToCheck = args;
  } else {
    // 检查所有文件
    filesToCheck = findFiles(targetPath);
  }

  console.log(`\x1b[90m%s\x1b[0m`, `Checking ${filesToCheck.length} files...`);

  const allIssues = [];

  for (const file of filesToCheck) {
    const issues = checkFile(file);

    if (issues.length > 0) {
      allIssues.push({
        file,
        issues
      });
    }
  }

  if (allIssues.length === 0) {
    console.log(`\x1b[32m%s\x1b[0m`, '✓ No sensitive information found');
    process.exit(0);
  }

  // 报告问题
  console.log(`\x1b[31m%s\x1b[0m`, '\n❌ Sensitive information detected!\n');

  for (const { file, issues } of allIssues) {
    console.log(`\x1b[33m%s\x1b[0m`, `📄 ${file}`);

    for (const issue of issues) {
      const severityColor = {
        critical: '\x1b[31m', // red
        high: '\x1b[31m',     // red
        medium: '\x1b[33m',   // yellow
        low: '\x1b[36m'       // cyan
      }[issue.severity];

      const resetColor = '\x1b[0m';

      console.log(`  ${severityColor}[${issue.severity.toUpperCase()}]${resetColor} Line ${issue.line}: ${issue.type}`);
      console.log(`  ${issue.text.substring(0, 100)}`);

      // 不显示实际的敏感值，只显示位置
      if (issue.match && issue.match.length < 50) {
        const masked = issue.match.substring(0, 3) + '***' + issue.match.substring(issue.match.length - 3);
        console.log(`  Found: ${masked}`);
      }
      console.log('');
    }
  }

  // 统计
  const totalIssues = allIssues.reduce((sum, { issues }) => sum + issues.length, 0);
  const criticalIssues = allIssues.reduce((sum, { issues }) =>
    sum + issues.filter(i => i.severity === 'critical').length, 0);

  console.log(`\x1b[31m%s\x1b[0m`, `Total: ${totalIssues} issues found`);
  console.log(`\x1b[31m%s\x1b[0m`, `Critical: ${criticalIssues} issues\n`);

  // 如果有严重问题，退出并阻止操作
  if (criticalIssues > 0) {
    console.log(`\x1b[31m%s\x1b[0m`, '🚫 Operation blocked: Remove sensitive data before continuing\n');
    process.exit(1);
  }

  process.exit(1);
}

main();
```

#### 步骤 2: 使脚本可执行

```bash
chmod +x scripts/check-sensitive.js
```

#### 步骤 3: 配置 Hooks

**.claude/hooks.json**:

```json
{
  "hooks": {
    "beforeEdit": [
      {
        "name": "check-sensitive-data",
        "command": "node scripts/check-sensitive.js",
        "blockOnError": true
      }
    ],
    "beforeCommit": [
      {
        "name": "check-sensitive-data",
        "command": "node scripts/check-sensitive.js $(git diff --cached --name-only)",
        "blockOnError": true
      }
    ]
  }
}
```

#### 步骤 4: 测试 Hook

```bash
# 尝试编辑包含敏感信息的文件
echo "const apiKey = 'sk-1234567890abcdef1234567890abcdef';" > test.js

# Claude 会尝试编辑，但 Hook 会阻止
```

---

## 更多 Hook 示例

### Hook 2: 自动格式化

**scripts/auto-format.js**:

```javascript
#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');

// 获取 Claude 即将编辑的文件（从环境变量）
const filePath = process.env.CLAUDE_FILE_TO_EDIT;

if (!filePath) {
  console.log('No file to format');
  process.exit(0);
}

// 检查文件类型
const ext = filePath.split('.').pop();

let formatCommand = null;

switch (ext) {
  case 'js':
  case 'jsx':
  case 'ts':
  case 'tsx':
    formatCommand = `npx prettier --write "${filePath}"`;
    break;

  case 'json':
    formatCommand = `npx prettier --write "${filePath}"`;
    break;

  case 'md':
    formatCommand = `npx prettier --write "${filePath}"`;
    break;

  case 'css':
  case 'scss':
  case 'less':
    formatCommand = `npx prettier --write "${filePath}"`;
    break;

  case 'py':
    formatCommand = `black "${filePath}"`;
    break;

  default:
    console.log(`No formatter configured for .${ext} files`);
    process.exit(0);
}

try {
  console.log(`Formatting ${filePath}...`);
  execSync(formatCommand, { stdio: 'inherit' });
  console.log('✓ Formatted');
} catch (error) {
  console.error('✗ Format failed:', error.message);
  process.exit(1);
}
```

### Hook 3: Slack 通知

**scripts/notify-slack.js**:

```javascript
#!/usr/bin/env node

const https = require('https');

// 从环境变量获取 Slack Webhook URL
const webhookUrl = process.env.SLACK_WEBHOOK_URL;

if (!webhookUrl) {
  console.log('SLACK_WEBHOOK_URL not configured');
  process.exit(0);
}

// 获取操作信息
const operation = process.env.CLAUDE_OPERATION || 'unknown';
const files = process.env.CLAUDE_FILES_EDITED || 'unknown';
const user = process.env.USER || process.env.USERNAME || 'unknown';

// 构建消息
const message = {
  text: `Claude Code Activity`,
  blocks: [
    {
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: `*Claude Code ${operation}*`
      }
    },
    {
      type: 'section',
      fields: [
        {
          type: 'mrkdwn',
          text: `*User:*\n${user}`
        },
        {
          type: 'mrkdwn',
          text: `*Files:*\n${files.split(',').length}`
        }
      ]
    },
    {
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: `*Files edited:*\n\`${files}\``
      }
    }
  ]
};

// 发送通知
const url = new URL(webhookUrl);

const req = https.request(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  }
}, (res) => {
  if (res.statusCode === 200) {
    console.log('✓ Slack notification sent');
  } else {
    console.error('✗ Slack notification failed');
  }
});

req.on('error', (error) => {
  console.error('✗ Slack notification error:', error.message);
});

req.write(JSON.stringify(message));
req.end();
```

**配置环境变量**:

```bash
# ~/.zshrc or ~/.bashrc
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### Hook 4: 测试运行器

**scripts/run-tests.js**:

```javascript
#!/usr/bin/env node

const { execSync } = require('child_process');
const path = require('path');

// 获取受影响的文件
const files = process.argv.slice(2);

// 如果没有指定文件，获取所有变更的文件
let filesToTest = files;

if (filesToTest.length === 0) {
  try {
    const gitFiles = execSync('git diff --name-only HEAD', { encoding: 'utf-8' });
    filesToTest = gitFiles.trim().split('\n').filter(Boolean);
  } catch (error) {
    console.log('No files to test');
    process.exit(0);
  }
}

// 确定需要运行的测试
const testMap = {
  'src/': 'npm test -- --testPathPattern=src',
  'tests/': 'npm test -- --testPathPattern=tests',
  'lib/': 'npm test -- --testPathPattern=lib',
  'e2e/': 'npm run test:e2e'
};

let testsToRun = new Set();

for (const file of filesToTest) {
  for (const [dir, test] of Object.entries(testMap)) {
    if (file.startsWith(dir)) {
      testsToRun.add(test);
    }
  }
}

if (testsToRun.size === 0) {
  console.log('No tests to run for changed files');
  process.exit(0);
}

console.log(`\x1b[36m%s\x1b[0m`, `🧪 Running ${testsToRun.size} test suites...`);

// 运行测试
let failed = false;

for (const test of testsToRun) {
  console.log(`\n\x1b[90m%s\x1b[0m`, `Running: ${test}`);

  try {
    execSync(test, { stdio: 'inherit' });
    console.log(`\x1b[32m%s\x1b[0m`, `✓ Passed: ${test}`);
  } catch (error) {
    console.log(`\x1b[31m%s\x1b[0m`, `✗ Failed: ${test}`);
    failed = true;
  }
}

if (failed) {
  console.log(`\n\x1b[31m%s\x1b[0m`, '❌ Some tests failed');
  process.exit(1);
}

console.log(`\n\x1b[32m%s\x1b[0m`, '✓ All tests passed');
```

---

## Hooks 高级功能

### 1. 条件执行

```json
{
  "hooks": {
    "beforeEdit": [
      {
        "name": "ts-check-only-for-ts-files",
        "command": "npm run type-check",
        "condition": {
          "files": ["**/*.ts", "**/*.tsx"],
          "commands": ["edit", "create"]
        }
      }
    ]
  }
}
```

### 2. 环境变量传递

```json
{
  "hooks": {
    "beforeCommit": [
      {
        "name": "custom-commit-check",
        "command": "node scripts/check.js",
        "env": {
          "PROJECT_ROOT": ".",
          "CUSTOM_VAR": "value"
        }
      }
    ]
  }
}
```

### 3. 钩子链（多个 Hooks）

```json
{
  "hooks": {
    "beforeCommit": [
      {
        "name": "step-1-lint",
        "command": "npm run lint",
        "blockOnError": true
      },
      {
        "name": "step-2-type-check",
        "command": "npm run type-check",
        "blockOnError": true
      },
      {
        "name": "step-3-tests",
        "command": "npm test",
        "blockOnError": true
      },
      {
        "name": "step-4-build",
        "command": "npm run build",
        "blockOnError": false
      }
    ]
  }
}
```

---

## Hooks 最佳实践

### 1. 快速执行

```javascript
// ❌ 不好：慢速 Hook
const allFiles = glob.sync('**/*');
for (const file of allFiles) {
  // 处理所有文件
}

// ✅ 好：只处理变更的文件
const changedFiles = execSync('git diff --name-only').trim().split('\n');
for (const file of changedFiles) {
  // 只处理变更的文件
}
```

### 2. 明确的错误消息

```javascript
// ❌ 不好：模糊的错误
if (error) {
  console.log('Error');
  process.exit(1);
}

// ✅ 好：清晰的错误
if (error) {
  console.error('❌ Linting failed');
  console.error('File:', filePath);
  console.error('Issue:', error.message);
  console.error('\nRun "npm run lint --fix" to auto-fix');
  process.exit(1);
}
```

### 3. 幂等性

```javascript
// Hook 应该可以安全地多次运行
function formatFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const formatted = prettier.format(content, { filepath: filePath });

  // 只在需要时写入
  if (content !== formatted) {
    fs.writeFileSync(filePath, formatted);
    return true;
  }

  return false;
}
```

### 4. 超时处理

```javascript
// 设置超时
const TIMEOUT = 30000; // 30 秒

const timeout = setTimeout(() => {
  console.error('❌ Hook timed out');
  process.exit(1);
}, TIMEOUT);

try {
  // 执行操作
  doSomething();
  clearTimeout(timeout);
} catch (error) {
  clearTimeout(timeout);
  throw error;
}
```

---

## 常见问题

### Q1: Hook 失败了怎么办？

**A**: 取决于 `blockOnError` 设置

```json
{
  "command": "npm test",
  "blockOnError": true  // 失败时阻止操作继续
}

// 或

{
  "command": "npm run notify",
  "blockOnError": false  // 失败时继续操作
}
```

### Q2: 如何调试 Hook？

**A**: 添加日志输出

```javascript
// 启用调试模式
const DEBUG = process.env.HOOK_DEBUG === '1';

function debug(message) {
  if (DEBUG) {
    console.log(`[DEBUG] ${message}`);
  }
}

// 使用
debug('Starting hook...');
debug(`Files: ${files.length}`);
```

运行时：
```bash
HOOK_DEBUG=1 claude
```

### Q3: Hooks 可以调用其他 Hooks 吗？

**A**: 不直接，但可以共享脚本

```javascript
// scripts/shared-hooks.js
module.exports = {
  checkSensitive: (files) => { /* ... */ },
  formatCode: (files) => { /* ... */ },
  runTests: (files) => { /* ... */ }
};

// scripts/hook1.js
const { checkSensitive } = require('./shared-hooks');
checkSensitive(files);

// scripts/hook2.js
const { formatCode } = require('./shared-hooks');
formatCode(files);
```

---

## 总结

### 关键要点

1. **Hooks 是自动执行的脚本**
   - 在特定事件时触发
   - 可以验证、修改、通知
   - 自动化工作流程

2. **Hooks 类型**
   - Pre-Hooks: 操作前执行
   - Post-Hooks: 操作后执行
   - Error-Hooks: 错误时执行

3. **Hooks 最佳实践**
   - 快速执行
   - 清晰的错误消息
   - 幂等性
   - 适当的超时

4. **常见用例**
   - 敏感信息检查
   - 自动格式化
   - 通知系统
   - 测试运行

### 下一步

在下一章中，我们将学习 **自定义 Commands**：
- Commands 的概念和创建
- 参数化 Commands
- Commands 组织和管理
- 实际应用案例

---

## 进一步阅读

### 官方文档
- Claude Code Hooks Reference
- Configuration Guide

### 相关章节
- [Chapter 11 - Skills 系统](chapter-11-skills.md)
- [Chapter 13 - 自定义 Commands](chapter-13-commands.md)

---

## 练习

完成以下练习：

1. **基本练习**
   - [ ] 创建一个简单的 Hook
   - [ ] 配置 beforeEdit Hook
   - [ ] 测试 Hook 的执行

2. **进阶练习**
   - [ ] 创建条件 Hook
   - [ ] 实现 Hook 链
   - [ ] 添加错误处理

3. **实战练习**
   - [ ] 为你的项目设置完整的 Hooks
   - [ ] 实现敏感信息检查
   - [ ] 集成通知系统

---

**上一章**: [Chapter 11 - Skills 系统](chapter-11-skills.md)
**下一章**: [Chapter 13 - 自定义 Commands](chapter-13-commands.md)
