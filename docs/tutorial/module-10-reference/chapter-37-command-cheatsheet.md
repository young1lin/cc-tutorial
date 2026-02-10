# Chapter 37: 命令速查表

## 概述

本章提供 Claude Code 的完整命令参考，包括所有快捷键、斜杠命令和配置选项。

---

## 37.1 核心快捷键

### 基础快捷键

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| `Shift+Tab` `Shift+Tab` | 激活 Plan Mode | 进入规划模式，让 Claude 先规划再编码 |
| `Escape` | 中断操作 | 停止当前的 AI 响应或工具执行 |
| `Alt+V` | 粘贴图片 | 从剪贴板粘贴图片到对话中 |
| `Ctrl+C` | 复制选中内容 | 复制终端中的选中内容 |
| `Ctrl+V` | 粘贴内容 | 粘贴剪贴板内容到输入中 |

### 导航快捷键

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| `↑` `↓` | 浏览历史 | 在对话历史中上下移动 |
| `Ctrl+L` | 清屏 | 清除终端屏幕内容 |
| `Home` | 跳到行首 | 移动光标到输入行开头 |
| `End` | 跳到行尾 | 移动光标到输入行结尾 |

### macOS 替代快捷键

| Windows/Linux | macOS | 功能 |
|---------------|-------|------|
| `Ctrl+C` | `Cmd+C` | 复制 |
| `Ctrl+V` | `Cmd+V` | 粘贴 |
| `Ctrl+L` | `Cmd+K` | 清屏 |
| `Alt+V` | `Option+V` | 粘贴图片 |

---

## 37.2 斜杠命令

### 基础命令

```
/help
```
显示帮助信息，列出所有可用命令。

```
/clear
```
清空当前对话上下文，重新开始会话。

```
/exit
```
退出 Claude Code。

```
/version
```
显示 Claude Code 版本信息。

```
/config
```
显示当前配置信息。

### 权限管理

```
/permissions
```
查看和管理当前权限设置。

```
/permissions allow <command>
```
允许特定命令执行。

```
/permissions block <command>
```
阻止特定命令执行。

```
/permissions reset
```
重置权限到默认状态。

### 工作流命令

```
/plan
```
进入 Plan Mode，等同于按 `Shift+Tab` 两次。

```
/commit
```
创建 Git 提交，Claude 会生成提交消息。

```
/review
```
审查当前工作区的更改。

```
/test
```
运行项目测试。

```
/build
```
构建项目。

### 上下文命令

```
/read <file>
```
读取并显示文件内容。

```
/search <pattern>
```
在代码库中搜索模式。

```
/find <name>
```
查找文件或符号。

### 信息命令

```
/status
```
显示项目状态信息。

```
/log
```
显示操作日志。

```
/stats
```
显示使用统计信息。

---

## 37.3 Thinking Modes

### 可用模式

```
/think
```
使用标准思考模式。适用于大多数任务。

```
/think hard
```
使用深度思考模式。适用于复杂问题。

```
/think harder
```
使用更深度思考模式。适用于非常复杂的问题。

```
/ultrathink
```
使用最强思考模式。适用于最复杂的问题。

### 模式选择指南

| 任务类型 | 推荐模式 | Token 使用 |
|----------|----------|------------|
| 简单代码补全 | `think` 或不使用 | 低 |
| 代码解释 | `think` | 低-中 |
| 重构代码 | `think hard` | 中 |
| 复杂问题解决 | `think harder` | 中-高 |
| 架构设计 | `ultrathink` | 高 |

---

## 37.4 配置选项

### config.json 结构

```json
{
  "model": "claude-opus-4-5",
  "thinkingMode": "think-hard",
  "temperature": 0.1,
  "maxTokens": 200000,
  "permissions": {
    "edit": "always",
    "bash": "always",
    "write": "always"
  }
}
```

### 模型选择

| 模型 | 用途 | 特点 |
|------|------|------|
| `claude-haiku` | 快速任务 | 速度最快，成本最低 |
| `claude-sonnet` | 通用任务 | 平衡速度和质量 |
| `claude-opus-4-5` | 复杂任务 | 最高质量，成本较高 |

### Temperature 设置

```
0.0 - 0.2  代码生成（确定性强）
0.3 - 0.7  一般对话
0.8 - 1.0  创意写作（随机性强）
```

### 权限级别

| 级别 | 行为 |
|------|------|
| `always` | 总是允许，不询问 |
| `ask` | 每次询问确认 |
| `never` | 总是阻止 |

---

## 37.5 MCP 服务器配置

### mcp.json 示例

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "${DATABASE_URL}"
      }
    }
  }
}
```

### 常用 MCP 服务器

| 服务器 | 包名 | 用途 |
|--------|-------|------|
| GitHub | `@modelcontextprotocol/server-github` | 访问 GitHub 仓库 |
| Postgres | `@modelcontextprotocol/server-postgres` | 查询 PostgreSQL |
| Puppeteer | `@modelcontextprotocol/server-puppeteer` | 浏览器自动化 |
| Filesystem | `@modelcontextprotocol/server-filesystem` | 文件系统访问 |
| Brave Search | `@modelcontextprotocol/server-brave-search` | 网络搜索 |

---

## 37.6 环境变量

### 必需变量

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```
Claude API 密钥。

### 可选变量

```bash
export ANTHROPIC_BASE_URL="https://api.anthropic.com"
```
API 基础 URL（用于代理）。

```bash
export CLAUDE_MODEL="claude-opus-4-5"
```
默认模型。

```bash
export CLAUDE_THINKING_MODE="think-hard"
```
默认思考模式。

### MCP 服务器变量

```bash
export GITHUB_TOKEN="ghp_..."
```
GitHub MCP 令牌。

```bash
export POSTGRES_CONNECTION_STRING="postgresql://..."
```
Postgres MCP 连接字符串。

```bash
export BRAVE_API_KEY="..."
```
Brave Search API 密钥。

---

## 37.7 CLI 参数

### 基础参数

```bash
claude-code [options]
```

| 参数 | 简写 | 说明 |
|------|------|------|
| `--help` | `-h` | 显示帮助 |
| `--version` | `-v` | 显示版本 |
| `--model <model>` | `-m` | 指定模型 |
| `--thinking-mode <mode>` | `-t` | 指定思考模式 |
| `--non-interactive` | `-n` | 非交互模式 |
| `--debug` | `-d` | 调试模式 |
| `--mcp-debug` | | MCP 调试模式 |

### 使用示例

```bash
# 使用特定模型
claude-code --model claude-haiku

# 使用深度思考
claude-code --thinking-mode think-hard

# 调试 MCP
claude-code --mcp-debug

# 非交互执行
echo "解释这段代码" | claude-code --non-interactive
```

---

## 37.8 常用提示词模板

### 代码审查

```
请审查以下代码：

[粘贴代码]

检查：
1. 功能正确性
2. 代码质量
3. 潜在 bug
4. 安全问题
5. 性能考虑
```

### 代码解释

```
请解释以下代码的工作原理：

[粘贴代码]

包括：
1. 整体功能
2. 关键部分
3. 设计模式
4. 潜在问题
```

### 重构代码

```
请重构以下代码以提高质量：

[粘贴代码]

改进：
1. 可读性
2. 可维护性
3. 性能
4. 最佳实践

保持功能不变。
```

### 生成测试

```
为以下代码生成单元测试：

[粘贴代码]

要求：
1. 使用 [测试框架]
2. 覆盖所有分支
3. 包含边界情况
4. 清晰的测试描述
```

### 调试帮助

```
帮我调试以下问题：

代码：
[粘贴代码]

错误：
[粘贴错误信息]

请分析原因并提供解决方案。
```

---

## 37.9 Plan Mode 提示词

### 进入 Plan Mode

```
[Shift+Tab] [Shift+Tab]
```

### 计划格式

```markdown
## 分析
[理解问题和需求]

## 方法
[建议的解决方案]

## 步骤
1. [第一步]
2. [第二步]
3. [第三步]

## 文件
- [需要修改/创建的文件]

## 风险
[潜在问题和注意事项]
```

---

## 37.10 快速参考卡片

### 每日使用

```
Plan Mode:    Shift+Tab 两次
粘贴图片:     Alt+V
中断操作:     Escape
清空上下文:   /clear
查看帮助:     /help
```

### 权限管理

```
查看权限:     /permissions
允许命令:     /permissions allow <cmd>
阻止命令:     /permissions block <cmd>
```

### Git 工作流

```
审查更改:     /review
创建提交:     /commit
查看状态:     /status
```

### 调试

```
调试模式:     --debug
MCP 调试:     --mcp-debug
查看日志:     /log
```

---

## 37.11 键盘快捷键速查

### Windows/Linux

| 功能 | 快捷键 |
|------|--------|
| Plan Mode | `Shift+Tab` `Shift+Tab` |
| 粘贴图片 | `Alt+V` |
| 中断 | `Escape` |
| 清屏 | `Ctrl+L` |
| 复制 | `Ctrl+C` |
| 粘贴 | `Ctrl+V` |
| 上一个命令 | `↑` |
| 下一个命令 | `↓` |
| 行首 | `Home` |
| 行尾 | `End` |

### macOS

| 功能 | 快捷键 |
|------|--------|
| Plan Mode | `Shift+Tab` `Shift+Tab` |
| 粘贴图片 | `Option+V` |
| 中断 | `Escape` |
| 清屏 | `Cmd+K` |
| 复制 | `Cmd+C` |
| 粘贴 | `Cmd+V` |
| 上一个命令 | `↑` |
| 下一个命令 | `↓` |
| 行首 | `Cmd+←` |
| 行尾 | `Cmd+→` |

---

## 37.12 常用命令组合

### 开发工作流

```bash
# 1. 启动 Claude Code
claude-code

# 2. 进入 Plan Mode
[Shift+Tab][Shift+Tab]

# 3. 描述任务
> 实现用户登录功能

# 4. 审查计划后继续
> 继续

# 5. 运行测试
/test

# 6. 提交更改
/commit
```

### 调试工作流

```bash
# 1. 显示错误
> 我的代码有错误

# 2. 粘贴错误信息
[粘贴错误]

# 3. 获取解决方案
[查看 AI 回答]

# 4. 应用修复
[编辑代码]

# 5. 验证修复
/test
```

### 代码审查工作流

```bash
# 1. 查看更改
/review

# 2. 深入审查特定文件
> 请详细审查 src/auth.ts

# 3. 应用建议
[根据建议修改代码]

# 4. 最终审查
> 再次审查更改

# 5. 提交
/commit
```

---

## 37.13 模型选择指南

### 场景推荐

```
快速补全 / 简单问答
→ claude-haiku

代码生成 / 代码解释 / 重构
→ claude-sonnet

复杂问题 / 架构设计 / 深度分析
→ claude-opus-4-5

不确定时
→ claude-sonnet（默认，平衡选择）
```

### 成本对比

| 模型 | 相对成本 | 速度 | 质量 |
|------|----------|------|------|
| Haiku | 1x | 最快 | 良好 |
| Sonnet | 5x | 快 | 优秀 |
| Opus | 15x | 中等 | 最佳 |

---

## 37.14 故障排除快速命令

```bash
# 检查配置
/config

# 查看权限
/permissions

# 清空并重新开始
/clear

# 调试模式
claude-code --debug

# MCP 调试
claude-code --mcp-debug

# 查看日志
/log

# 重置权限
/permissions reset
```

---

## 37.15 提示词最佳实践

### 好的提示词

```
✅ 具体明确
"为 User 类创建一个 TypeScript 接口，包含 id、name、email 字段"

✅ 提供上下文
"在现有的 Express.js API 中添加一个新的 /users 端点"

✅ 指定格式
"以 JSON 格式返回以下数据"

✅ 包含约束
"创建一个不超过 50 行的函数"
```

### 不好的提示词

```
❌ 太模糊
"帮我写代码"

❌ 缺少上下文
"修复这个错误" [没有提供错误信息]

❌ 目标不明确
"优化这段代码" [没有说明优化什么]

❌ 过于宽泛
"做一个网站"
```

---

## 37.16 进一步阅读

- [Chapter 38: 故障排除指南](chapter-38-troubleshooting.md) - 下一章
- [Chapter 39: 社区资源](chapter-39-community-resources.md) - 社区链接
- [Claude Code 官方文档](https://docs.anthropic.com/claude-code/) - 完整文档

---

## 视频脚本

### Episode 37: 命令速查表 (15 分钟)

#### [0:00-1:00] 引入

**视觉元素**：
- 标题："Claude Code 命令速查表"
- 命令分类概览

**内容**：
> 这是你的 Claude Code 快速参考指南。
>
> 我们将涵盖所有核心命令、快捷键和配置选项。
>
> 把这一章当作你的备忘单，随时可以回来查阅。

#### [1:00-4:00] 核心快捷键

**视觉元素**：
- 快捷键表格
- 动画演示

**内容**：
> **最重要的快捷键**：
>
> | 功能 | 快捷键 |
> |------|--------|
> | Plan Mode | `Shift+Tab` `Shift+Tab` |
> | 粘贴图片 | `Alt+V` |
> | 中断操作 | `Escape` |
> | 清空上下文 | `/clear` |
>
> [演示每个快捷键]
>
> macOS 用户：使用 `Option+V` 代替 `Alt+V`，`Cmd+K` 代替 `Ctrl+L`。

#### [4:00-7:00] 斜杠命令

**视觉元素**：
- 命令列表
- 使用示例

**内容**：
> **基础斜杠命令**：
>
> ```
> /help      - 显示帮助
> /clear     - 清空对话
> /plan      - 进入 Plan Mode
> /commit    - 创建 Git 提交
> /review    - 审查更改
> /test      - 运行测试
> ```
>
> **权限管理**：
> ```
> /permissions              - 查看权限
> /permissions allow <cmd>  - 允许命令
> /permissions block <cmd>  - 阻止命令
> ```

#### [7:00-10:00] Thinking Modes 和模型

**视觉元素**：
- 模式对比表
- 模型选择指南

**内容**：
> **Thinking Modes**：
>
> ```
> /think        - 标准思考
> /think hard   - 深度思考
> /think harder - 更深度思考
> /ultrathink   - 最强思考
> ```
>
> **模型选择**：
>
> - **Haiku**：快速任务，最低成本
> - **Sonnet**：通用任务，平衡选择
> - **Opus**：复杂任务，最高质量
>
> 使用场景：
> - 简单补全 → Haiku
> - 代码生成 → Sonnet
> - 架构设计 → Opus

#### [10:00-13:00] 配置和环境

**视觉元素**：
- 配置文件示例
- 环境变量列表

**内容**：
> **配置文件** (`~/.config/claude/config.json`)：
>
> ```json
> {
>   "model": "claude-sonnet",
>   "thinkingMode": "think-hard",
>   "permissions": {
>     "edit": "always",
>     "bash": "always"
>   }
> }
> ```
>
> **必需环境变量**：
> ```bash
> export ANTHROPIC_API_KEY="sk-ant-..."
> ```
>
> **可选环境变量**：
> ```bash
> export CLAUDE_MODEL="claude-sonnet"
> export CLAUDE_THINKING_MODE="think-hard"
> ```

#### [13:00-15:00] 提示词和总结

**视觉元素**：
- 好坏提示词对比
- 快速参考卡片

**内容**：
> **好的提示词**：
> - ✅ 具体明确
> - ✅ 提供上下文
> - ✅ 指定格式
> - ✅ 包含约束
>
> **快速参考卡片**：
>
> ```
> Plan Mode:    Shift+Tab 两次
> 粘贴图片:     Alt+V
> 中断操作:     Escape
> 清空上下文:   /clear
> 查看帮助:     /help
> ```
>
> **总结**：
> 这些命令和快捷键是你使用 Claude Code 的基础。
> 熟练掌握它们将大大提高你的效率。
>
> 下一章，我们将学习故障排除。
