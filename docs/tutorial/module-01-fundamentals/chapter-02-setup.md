# Chapter 2: 安装与配置

**模块**: Module 1 - 入门基础
**预计阅读时间**: 15 分钟
**难度**: ⭐

---

## 学习目标

本章结束后，你将能够：

- [ ] 安装 Claude Code CLI
- [ ] 配置 VS Code 扩展（可选）
- [ ] 创建和配置 CLAUDE.md 文件
- [ ] 理解权限系统
- [ ] 运行你的第一个 Claude Code 会话

---

## 前置知识

- 基本的命令行操作（cd、ls、mkdir 等）
- Node.js 环境（可选，用于某些 MCP 服务器）
- Git 基础知识（推荐）

---

## 系统要求

### 最低要求

| 组件 | 要求 |
|------|------|
| **操作系统** | Windows 10+、macOS 10.15+、Linux |
| **内存** | 4 GB RAM |
| **磁盘空间** | 500 MB |
| **网络** | 稳定的互联网连接 |

### 推荐配置

| 组件 | 要求 |
|------|------|
| **操作系统** | Windows 11、macOS 13+、主流 Linux 发行版 |
| **内存** | 8 GB RAM 或更多 |
| **磁盘空间** | 2 GB 或更多 |
| **终端** | 现代终端（Windows Terminal、iTerm2 等） |

---

## 安装 Claude Code CLI

### 方法 1: 使用 npm（推荐）

Claude Code 可以通过 npm 全局安装：

```bash
# 安装 Claude Code CLI
npm install -g @anthropic-ai/claude-code

# 验证安装
claude --version
```

**注意**: 如果遇到权限问题，可能需要使用 `sudo`（Linux/macOS）：

```bash
sudo npm install -g @anthropic-ai/claude-code
```

### 方法 2: 使用 Homebrew（macOS）

```bash
# 添加 tap
brew tap anthropic/claude-code

# 安装
brew install claude-code

# 验证
claude --version
```

### 方法 3: 从源码安装

```bash
# 克隆仓库
git clone https://github.com/anthropics/claude-code.git
cd claude-code

# 安装依赖
npm install

# 链接到全局
npm link
```

### 验证安装

```bash
# 检查版本
claude --version

# 查看帮助
claude --help

# 查看 CLI 选项
claude --help-commands
```

**预期输出**:
```
Claude Code v1.x.x
Anthropic's AI coding assistant
```

---

## 配置 Anthropic API 密钥

### 获取 API 密钥

1. 访问 [Anthropic Console](https://console.anthropic.com/)
2. 注册或登录账户
3. 导航到 API Keys 部分
4. 创建新的 API 密钥

### 设置环境变量

**Linux/macOS**:

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export ANTHROPIC_API_KEY="your-api-key-here"

# 重新加载配置
source ~/.bashrc  # 或 source ~/.zshrc
```

**Windows (PowerShell)**:

```powershell
# 添加到系统环境变量
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'your-api-key-here', 'User')

# 或为当前会话设置
$env:ANTHROPIC_API_KEY="your-api-key-here"
```

**Windows (CMD)**:

```cmd
setx ANTHROPIC_API_KEY "your-api-key-here"
```

### 验证配置

```bash
# 检查环境变量
echo $ANTHROPIC_API_KEY  # Linux/macOS
echo %ANTHROPIC_API_KEY% # Windows CMD
```

---

## VS Code 扩展（可选）

虽然 Claude Code 主要是 CLI 工具，但也提供了 VS Code 扩展以便更好地集成。

### 安装扩展

1. 打开 VS Code
2. 按 `Ctrl+Shift+X` 打开扩展面板
3. 搜索 "Claude Code"
4. 点击 "Install"

### 配置扩展

在 VS Code 设置中搜索 "Claude Code" 进行配置：

```json
{
  "claudeCode.apiKey": "your-api-key-here",
  "claudeCode.model": "claude-opus-4-5",
  "claudeCode.autoApproveEdits": false
}
```

---

## 首次运行与初始化

### 启动 Claude Code

```bash
# 在你的项目目录中
cd /path/to/your/project

# 启动 Claude Code
claude
```

### 首次启动向导

首次运行时，Claude Code 会引导你完成初始设置：

```
Welcome to Claude Code! 🚀

Let's get you set up...

1. API Key Configuration
   ✓ API key found in environment

2. Checking connectivity...
   ✓ Connected to Anthropic API

3. Creating initial configuration...
   ✓ Created .claude/settings.json

4. Would you like to create a CLAUDE.md file? (Y/n)
```

### 使用 /init 命令

如果跳过了初始向导，可以随时使用 `/init` 命令：

```
> /init
```

Claude Code 会分析你的项目并生成：
- `.claude/settings.json` - 项目配置
- `CLAUDE.md` - 项目上下文文件

---

## 配置文件详解

### .claude/settings.json

项目级别的配置文件：

```json
{
  "permissions": {
    "defaultMode": "ask",
    "allow": [
      "Read",
      "Bash(ls,cd,cat,echo)"
    ],
    "deny": [
      "Bash(rm,rf,mkdir)"
    ]
  },
  "model": "claude-opus-4-5",
  "maxTokens": 200000,
  "temperature": 0.7
}
```

**配置选项说明**:

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `defaultMode` | 权限默认模式 | `ask` |
| `allow` | 允许的工具列表 | `[]` |
| `deny` | 拒绝的工具列表 | `[]` |
| `model` | 使用的模型 | `claude-opus-4-5` |
| `maxTokens` | 最大 token 数 | `200000` |
| `temperature` | 创造性程度 | `0.7` |

### 全局配置

全局配置文件位于 `~/.claude.json`（或 `%USERPROFILE%\.claude.json` on Windows）：

```json
{
  "apiKey": "sk-ant-xxxxx",
  "defaultModel": "claude-opus-4-5",
  "permissions": {
    "defaultMode": "bypassPermissions"
  },
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-filesystem", "/allowed/path"]
    }
  }
}
```

---

## CLAUDE.md 文件

### 什么是 CLAUDE.md？

`CLAUDE.md` 是一个特殊的文件，Claude Code 会自动将其内容读取到上下文中。这是存放项目特定信息和指导原则的最佳位置。

### CLAUDE.md 示例

```markdown
# 项目名称

## 项目概述
这是一个使用 React 和 Node.js 的全栈应用。

## 技术栈
- 前端: React 18, TypeScript, Tailwind CSS
- 后端: Node.js, Express, PostgreSQL
- 测试: Jest, Playwright

## 常用命令
```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 运行测试
npm test

# 构建
npm run build
```

## 代码风格
- 使用 TypeScript 严格模式
- 函数组件优于类组件
- 使用 4 空格缩进
- 遵循 ESLint 规则

## 重要文件
- `src/api/` - API 端点
- `src/components/` - React 组件
- `src/utils/` - 工具函数

## 开发注意事项
- 所有 API 调用需要错误处理
- 组件需要 PropTypes 或 TypeScript 类型
- 不要使用 `any` 类型
```

### CLAUDE.md 最佳实践

**DO（应该做的）**:
✅ 保持简洁明了
✅ 包含常用命令
✅ 说明代码风格
✅ 列出重要文件和目录
✅ 提及项目特有行为

**DON'T（不应该做的）**:
❌ 写成完整文档
❌ 包含过时信息
❌ 过于冗长
❌ 重复通用信息

### CLAUDE.md 位置

可以在多个位置放置 `CLAUDE.md`：

```
project/
├── CLAUDE.md              # 项目级别（推荐）
├── .claude/
│   └── CLAUDE.md          # 私有配置（不提交到 Git）
└── src/
    └── CLAUDE.md          # 子模块特定
```

**优先级**: 子目录 > 项目根目录 > 全局配置

---

## 权限系统

### 理解权限模式

Claude Code 有三种权限模式：

| 模式 | 说明 | 使用场景 |
|------|------|----------|
| **ask** | 每次操作前询问 | 首次使用、敏感项目 |
| **auto** | 自动允许安全操作 | 信任的项目、快速开发 |
| **bypassPermissions** | 跳过所有权限检查 | 自动化脚本、容器环境 |

### 配置权限

**在配置文件中**:

```json
{
  "permissions": {
    "defaultMode": "ask",
    "allow": [
      "Read",
      "Edit",
      "Bash(ls,cat,echo,cd)"
    ],
    "deny": [
      "Bash(rm,rf,sudo)"
    ]
  }
}
```

**运行时设置**:

```bash
# 完全跳过权限检查（谨慎使用！）
claude --dangerously-skip-permissions

# 允许特定工具
claude --allowed-tools Read,Edit,Bash
```

### 使用 /permissions 命令

在 Claude Code 运行时管理权限：

```
> /permissions

Current permissions:
- defaultMode: ask
- allowed: Read, Bash(ls,cat)

> /permissions allow Edit

> /permissions deny Bash(rm)

> /permissions defaultMode auto
```

---

## 第一个会话

### 启动并测试

```bash
# 在你的项目目录
cd /path/to/your/project

# 启动 Claude Code
claude
```

### 第一次对话

```
Welcome to Claude Code! 🤖

Type 'help' for available commands.
Type 'exit' or Ctrl+D to exit.

> 你好，请介绍一下你自己

我是 Claude，Anthropic 开发的 AI 助手。我可以通过 Claude Code CLI 帮助你进行各种编程任务。

我可以：
- 阅读和分析你的代码
- 编写和修改代码
- 运行测试和调试
- 与 Git 和 GitHub 集成
- 连接到 MCP 服务器

有什么我可以帮助你的吗？
```

### 测试基本功能

```
> 请帮我列出当前目录的文件
```

Claude Code 会：
1. 请求执行 `ls` 命令的权限
2. 显示目录内容
3. 等待你的下一个指令

---

## 故障排除

### 常见问题

#### 问题 1: API 密钥错误

```
Error: Invalid API key
```

**解决方案**:
```bash
# 检查环境变量
echo $ANTHROPIC_API_KEY

# 重新设置
export ANTHROPIC_API_KEY="your-correct-key"
```

#### 问题 2: 权限被拒绝

```
Error: Permission denied for tool 'Edit'
```

**解决方案**:
```bash
# 允许工具
> /permissions allow Edit

# 或使用自动模式
> /permissions defaultMode auto
```

#### 问题 3: 模型不可用

```
Error: Model 'claude-opus-4-5' not available
```

**解决方案**:
- 检查你的 API 计划是否支持该模型
- 切换到可用模型（如 `claude-sonnet-4-5`）

#### 问题 4: 网络连接问题

```
Error: Failed to connect to Anthropic API
```

**解决方案**:
- 检查网络连接
- 如果使用代理，配置 `HTTP_PROXY` 和 `HTTPS_PROXY`
- 检查防火墙设置

### 调试模式

```bash
# 启用详细输出
claude --verbose

# 启用调试输出
claude --debug

# 查看 MCP 配置问题
claude --mcp-debug
```

---

## 总结

### 关键要点

1. **安装简单**: 通过 npm 或 Homebrew 一行命令安装
2. **配置灵活**: 支持项目级和全局配置
3. **CLAUDE.md 重要**: 是项目上下文的核心文件
4. **权限安全**: 默认询问模式确保安全
5. **易于开始**: 首次运行有向导引导

### 下一步

现在你已经安装并配置了 Claude Code，在下一章中我们将学习：
- 核心快捷键
- 基本命令
- 如何有效使用 Claude Code

---

## 进一步阅读

### 官方文档
- [Claude Code 官方文档](https://claude.ai/code)
- [API 密钥管理](https://console.anthropic.com/)

### 相关章节
- [Chapter 1 - Claude Code 简介](chapter-01-introduction.md)
- [Chapter 3 - 核心快捷键](chapter-03-shortcuts.md)

---

## 练习

完成以下练习以巩固学习：

1. **安装 Claude Code**
   - [ ] 使用 npm 或 Homebrew 安装
   - [ ] 验证安装成功

2. **配置环境**
   - [ ] 设置 API 密钥
   - [ ] 创建项目目录
   - [ ] 初始化 Claude Code

3. **创建 CLAUDE.md**
   - [ ] 为你的项目创建 CLAUDE.md
   - [ ] 包含项目概述、技术栈、常用命令

4. **测试运行**
   - [ ] 启动 Claude Code
   - [ ] 尝试基本对话
   - [ ] 测试文件读取功能

---

**上一章**: [Chapter 1 - Claude Code 简介](chapter-01-introduction.md)
**下一章**: [Chapter 3 - 核心快捷键](chapter-03-shortcuts.md)
