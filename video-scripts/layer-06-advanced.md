# 第六层：高级功能

## MCP

从上面的例子我们可以看到，如果要让 AI 大模型了解最新的信息，必须使用 Function Calling 调用工具，并且把工具返回的信息给带上。但是并不是所有的 Agent 工具都会用 Function Calling，像比较早期的 Cline 就是用的 XML 格式返回，XML 工具调用，在那个时候提出了 MCP。当然 MCP 不只是工具调用，还有 `prompts` 和 `resources` 等概念，当然这些很多工具都没有用到。

如果要详细从零了解 MCP 除了看官网，还可以看我这个，我这里不止有时序图、概念讲解，还有完整的最小化 Python 代码实现。`https://github.com/young1lin/minimal-mcp`

# SubAgent

有自己的 Prompt，有自己可以用的 Tool，也有自己的独立的上下文窗口。关于如何创建合适的 subAgent，在 Claude Code 中，可以输入 `/agents` 命令，回车，然后按照提示来创建 Agent，本质上就是一个 Markdown 文件。这个 Markdown 文件包含了元信息，名称、描述（会在上下文中占用）、model（继承父级，或者指定模型）、color（颜色）等等。其中描述（description）是最关键的字段，它会被写入主 Agent 的 System Prompt 中，Claude 根据这段描述来判断什么时候应该调用这个 SubAgent。所以描述里要包含清晰的触发条件和使用示例（用 `<example>` 标签），让主 Agent 知道"遇到什么场景就该把任务交给我"。SubAgent 的独立上下文窗口意味着它不会污染主对话的上下文，干完活返回结果，主 Agent 继续工作。

```markdown
name: java-unit-test-generator
description: Use this agent when you need to create comprehensive JUnit5 unit tests for Java code. Examples: <example>Context: User has just written a UserService class with methods for creating, updating, and validating users. user: 'I just finished implementing UserService with createUser, updateUser, and validateUser methods. Can you help me create unit tests?' assistant: 'I'll use the java-unit-test-generator agent to create comprehensive JUnit5 tests for your UserService class.'</example> <example>Context: User is working on a Spring Boot application and has implemented a REST controller. user: 'Here's my OrderController class. I need to write tests for all the endpoints including error handling.' assistant: 'I'll use the java-unit-test-generator agent to create MockMvc-based tests for your OrderController.'</example>
model: inherit
color: green
You are Java Code Tester, an expert in creating comprehensive JUnit5 unit tests with Mockito. You specialize in writing high-quality, maintainable test code that follows industry best practices and achieves meaningful code coverage.

## Foundational Principles

Every test you write must satisfy three quality pillars (Roy Osherove, "The Art of Unit Testing"):

- **Trustworthy**: Tests catch real bugs and never produce false positives or false negatives. Developers must trust that a red test means a real problem.
- **Maintainable**: Tests survive refactoring without modification. If behavior hasn't changed but tests break, the tests are testing implementation details, not behavior.
- **Readable**: Another developer can understand the test's purpose, setup, and expected outcome at a glance. A test is living documentation of system behavior.

Every test must also follow the **F.I.R.S.T.** principles (Robert C. Martin, "Clean Code" Chapter 9):

- **Fast**: Unit tests run in milliseconds. If a test needs seconds, reconsider the design.
- **Independent**: Tests must not depend on each other or on execution order. Each test sets up its own state.
- **Repeatable**: Tests produce the same result in any environment — local machine, CI server, or colleague's laptop.
- **Self-validating**: Tests have a boolean outcome (pass/fail). No manual inspection of logs or output.
- **Timely**: Tests are written close to the production code they verify.
```

## /plugin（LSP 和 Playwright）

**Playwright 插件**：自动化网页测试，截图验证前端实现。

**LSP 插件**：语言服务器协议，让 Claude Code 精准读取代码。例如一个 3000 行的 Java 文件，你只改其中一个方法，LSP 让 Claude 只读 400 行相关代码，而不是整个文件。就像 IDE 里 Ctrl + 点击跳转一样精准。

### 推荐插件

详细的插件推荐和安装指南见 [examples/recommended-plugins/](../examples/recommended-plugins/)。

| 插件 | 用途 | 安装方式 |
|------|------|----------|
| **firecrawl** | 抓取 JS 渲染网站 | `claude mcp add firecrawl --api-key YOUR_KEY` |
| **claude-mem** | 跨会话长期记忆 | `/plugin install claude-mem` |
| **ccusage** | Token 用量统计 | `npm install -g ccusage` |
| **repomix** | 代码库打包为 AI 格式 | `npm install -g repomix` |
| **claude-squad** | 多代理并行管理 | `npm install -g claude-squad` |

官方 MCP 服务器（文件/网络/Git/记忆/推理）：`npx @modelcontextprotocol/server-filesystem` 等。

### 配置 MCP

**方式一：命令行（全局安装）**

```bash
# HTTP 类型 MCP（Figma 官方）
claude mcp add --transport http figma https://mcp.figma.com/mcp

# Stdio 类型 MCP（本地进程）
claude mcp add firecrawl --env FIRECRAWL_API_KEY=... -- npx firecrawl-mcp
```

**方式二：`.mcp.json`（项目级，团队共享）**

在项目根目录创建 `.mcp.json`：

```json
{
  "mcpServers": {
    "figma": {
      "type": "http",
      "url": "https://mcp.figma.com/mcp"
    },
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"]
    }
  }
}
```

`.mcp.json` 可以提交到 git，方便团队统一配置。含 API Key 的敏感配置用 `~/.claude/settings.json` 或环境变量传入，不写入 `.mcp.json`。

**Figma MCP 认证**（安装后）：

```
> /mcp
```

在列表中找到 `figma`，点击 Authenticate，浏览器授权后完成。

详细的 Figma MCP 用法见：[examples/recommended-plugins/figma-mcp.md](../examples/recommended-plugins/figma-mcp.md)

## Skills

Skills 的前身 Claude Code 自定义 Command，现在两者同时存在。.claude/commands/ 目录下，放自定义命令， .claude/skills/ 目录下放不同的 Skill，例如 .claude/skills/java-pro/SKILL.md 这里就会写这个技能的元信息，元信息里面只有需要用到的时候，才会调用相应的内容。可以在 .claude/skills/java-pro/examples/ 目录下放示例代码，能让 Claude Code 有个参考样例，能按照你想要的方式写代码。例如强制使用构造器依赖注入，而不是注解。如果有循环依赖的情况下，需要拆分代码。

## Hooks

Hooks 是用户自定义的 Shell 命令或 LLM Prompt，在 Claude Code 生命周期的特定节点自动执行。你可以理解为"事件监听器"。

**核心 Hook 事件：**

| 事件 | 触发时机 | 典型用途 |
|------|---------|---------|
| `SessionStart` | Claude Code 启动时 | 环境检查、加载配置 |
| `UserPromptSubmit` | 用户发送消息后 | 输入校验、日志记录（本项目就在用这个 Hook，每次对话都会统计字数和分析） |
| `PreToolUse` | Claude 执行工具之前 | 拦截危险操作（如阻止 `rm -rf`）、自动审批特定工具 |
| `PostToolUse` | 工具执行完成后 | 自动格式化代码、运行 lint |
| `Stop` | Claude 完成回复时 | 自动提交、发送通知 |
| `SubagentStop` | SubAgent 完成时 | 收集子任务结果 |
| `TaskCompleted` | 任务完成时 | 清理临时文件 |

**配置方式：** 在 `.claude/settings.json` 或 `~/.claude/settings.json` 中配置。Hook handler 接收 JSON 格式的上下文数据，可以根据工具名称、参数等条件来匹配触发。

**实际例子：** 比如你想在每次 Claude 编辑文件后自动运行 `go fmt`，就可以配置一个 PostToolUse Hook，匹配 `Edit` 和 `Write` 工具，执行格式化命令。

**配置示例：**

Hooks 写在 `~/.claude/settings.json`（全局）或 `.claude/settings.json`（项目），结构如下：

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/analyze_prompt.py record",
            "timeout": 30
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/notify-stop.py",
            "timeout": 45
          }
        ]
      }
    ]
  }
}
```

本教程已在全局 settings.json 中配置了两个 Hook：
- **UserPromptSubmit**：每次提交 Prompt 后统计字数（对话框上方的统计输出就是它）
- **Stop**：Claude 完成回复后发送桌面通知（Windows/macOS/Linux 跨平台）

完整实现见：
- `examples/recommended-plugins/notify-stop.py` — 跨平台桌面通知
- `examples/recommended-plugins/stop-hook.py` — ralph-loop 迭代控制

## Headless 用法

Headless 用法就是不显示任何界面，直接在后台运行。-c 表示 continue，--agent 表示使用指定的 Agent。

```bash
claude -p "你好你是谁？"

claude -c -p "我上一句说的什么？"

claude -p --agent code-analyzer "分析这段代码 print('test')"
```

你可以看到，这个很容易就和 Code Review 结合到一起，配合 Git 的 Hook 能自动检测本次变更的代码，进行代码审核。

### --output-format 结构化输出

Headless 模式下，`--output-format` 参数控制输出格式，是自动化集成的关键：

| 格式 | 用途 | 输出形式 |
|------|------|---------|
| `text`（默认） | 简单脚本、日志记录 | 纯文本，直接可读 |
| `json` | CI/CD 流水线、自动化处理 | 完整 JSON 对象（含 metadata） |
| `stream-json` | 实时流式处理、进度展示 | 逐行 JSON，每行一个事件 |

**JSON 输出结构**（`--output-format json`）：

```json
{
  "type": "result",
  "result": "Claude 的文本回复内容",
  "session_id": "abc123-...",
  "usage": {
    "input_tokens": 1520,
    "output_tokens": 830
  },
  "cost_usd": 0.042,
  "duration_ms": 12500
}
```

关键字段说明：
- **result**：Claude 的文本回复
- **session_id**：可用于 `--resume` 恢复对话，实现多轮 Headless 交互
- **usage**：input/output tokens 统计
- **cost_usd**：本次调用费用（美元）
- **duration_ms**：本次调用耗时（毫秒）

### 关键 Headless 参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--max-turns` | 最大对话轮次 | `--max-turns 5` |
| `-p` | 提示词（进入 Headless 模式） | `-p "分析这段代码"` |
| `-c` | 继续上次对话 | `-c -p "接着上次的问题"` |
| `--resume` | 恢复指定会话 | `--resume abc123` |
| `--allowedTools` | 限制可用工具 | `--allowedTools "Read,Grep,Glob"` |
| `--system-prompt` | 自定义系统提示词 | `--system-prompt "你是代码审查专家"` |
| `--model` | 指定模型 | `--model claude-sonnet-4-20250514` |
| `--permission-mode` | 权限模式 | `--permission-mode plan` |
| `--add-dir` | 添加额外工作目录 | `--add-dir /path/to/lib` |

### CI/CD 集成示例

**GitHub Actions Code Review：**

```yaml
- name: AI Code Review
  run: |
    gh pr diff ${{ github.event.pull_request.number }} | \
    claude -p "Review this diff for bugs, security issues, and style problems. \
    Be concise, only flag real issues." \
    --output-format json \
    --allowedTools "Read,Grep,Glob" \
    --max-turns 3 > review.json
```

**Shell 脚本多步自动化（Session Continuation）：**

```bash
#!/bin/bash
# 第一步：分析项目结构
RESULT=$(claude -p "分析 src/ 目录结构，列出核心模块" --output-format json)
SESSION_ID=$(echo "$RESULT" | jq -r '.session_id')

# 第二步：基于分析结果继续（复用同一会话）
claude -p "针对你刚才分析的结构，找出潜在的循环依赖" \
  --resume "$SESSION_ID" \
  --output-format json > analysis.json
```

**`stream-json` 实时流式处理：**

```bash
# 实时打印 Claude 的思考过程
claude -p "重构这个模块" --output-format stream-json | \
  while IFS= read -r line; do
    TYPE=$(echo "$line" | jq -r '.type')
    if [ "$TYPE" = "assistant" ]; then
      echo "$line" | jq -r '.message.content[0].text // empty'
    fi
  done
```

## Git Worktrees —— 多会话并行开发

Claude Code 团队内部称 Git Worktrees 为**"最大生产力解锁"（single biggest productivity unlock）**。原理很简单：用 `git worktree` 命令创建多个工作目录，每个目录是同一个仓库的不同分支，然后在每个目录里开一个独立的 Claude Code 会话。

```bash
# 在主目录外创建两个 worktree
git worktree add ../project-feature-auth feature/auth
git worktree add ../project-fix-perf fix/performance

# 现在你有三个独立目录：
# ./project/              ← 主分支（main）
# ../project-feature-auth/ ← auth 功能分支
# ../project-fix-perf/     ← 性能修复分支

# 每个目录开一个 Claude Code，互不干扰
```

每个 Claude 会话在自己的 worktree 里工作，有独立的 git 分支、独立的文件系统、独立的上下文。不会出现一个会话改了文件影响另一个会话的情况。

**局限性：** Git Worktrees 不能跨 worktree 同时修改同一个文件。如果两个分支都需要改 `src/config.ts`，合并时必然有冲突。所以它适合**功能边界清晰**的并行任务——一个做认证模块、一个做性能优化、一个写测试——而不是两个人改同一个模块。

此功能在实际项目中价值有限，因为很难完全避免文件重叠。但如果项目模块化做得好，这确实是个强大的并行策略。

**替代方案：** 如果你不想折腾 worktrees，最简单的并行方式是开多个终端 tab，每个 tab 一个 Claude Code 会话，做不同的任务。用 `/clear` 保持每个会话上下文干净就行。

## 我能休息，Claude Code 不能休息

ralph-loop 插件，让 Claude Code 在你不在的时候持续工作。它的核心思路是：给 Claude Code 一个任务列表，插件会自动循环驱动 Claude Code 执行任务，遇到需要确认的地方自动同意，直到所有任务完成或达到设定的轮次上限。

**⚠️ Windows 用户注意事项：**

原版 ralph-loop 的 Stop Hook 使用 shell 脚本（`.sh` 文件），在 Windows 下执行会出现乱码问题。需要替换为 Python 版本的 hook 脚本。

解决方案：使用 Python 版本的 `stop-hook.py`（示例文件见 `examples/recommended-plugins/stop-hook.py`），在 `.claude/settings.json` 中配置：

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/stop-hook.py"
          }
        ]
      }
    ]
  }
}
```

**⚠️ 内存泄露风险警告（重要）：**

Claude Code 本身存在内存泄露问题（截至 v2.1.39 版本仍未修复）。GitHub 上有多个相关 issue 报告：

- [#21665](https://github.com/anthropics/claude-code/issues/21665): ~2GB/minute RAM growth even when idle
- [#19720](https://github.com/anthropics/claude-code/issues/19720): 100%+ CPU and memory leak
- [#23252](https://github.com/anthropics/claude-code/issues/23252): ~12GB RAM consumption

长时间无人值守运行 ralph-loop 可能导致：

- Claude Code 进程内存占用持续增长（可达 4GB+）
- 电脑内存耗尽，系统变慢甚至死机
- 任务执行到一半被迫中断

**安全使用建议：**

1. **设置合理的轮次上限**：不要设置无限循环，建议 max_iterations 不超过 20-30
2. **监控内存使用**：如果可能，用脚本定期检查 Claude Code 进程内存，超过阈值自动重启
3. **分段执行**：不要指望"下班前启动，第二天早上来看结果"。建议每 1-2 小时检查一次
4. **重要数据勤提交**：每完成一个任务就 `git commit`，即使崩溃也能恢复
5. **Windows 用户额外注意**：确保使用 Python 版 hook，避免 shell 脚本乱码导致意外行为

用法：

1. 安装插件：`claude plugin install ralph-loop`
2. 编写任务文件（Markdown 格式的待办列表）
3. 启动循环：让 Claude Code 按照任务文件逐项执行
4. 设置合理的轮次上限，避免无限循环消耗 Token

适用场景：批量重构、大规模测试编写、多文件迁移等重复性高但需要 AI 判断的任务。**但不建议完全无人值守运行**，定期检查是必要的。

## 自动化工具

**Vibe Kanban** 是一个网页看板工具，支持与 Claude Code、CodeX、Copilot-CLI 集成。可以在网页端创建和管理任务，Claude Code 通过 API 获取任务并执行。

> **延伸阅读**：[Vibe Kanban 官网](https://vibekanban.com/)

## Claude Code SDK / Agent SDK

### CLI vs SDK：架构关系

```
┌─────────────────────────────────────────────────────────────────┐
│                        你的应用层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Web 前端    │  │  CLI 工具    │  │  CI/CD Pipeline      │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
└─────────┼─────────────────┼─────────────────────┼──────────────┘
          │                 │                     │
          ▼                 ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Agent SDK (可选)                            │
│  Python: claude-code-sdk    TypeScript: @anthropic-ai/claude-code-sdk │
│  • 类型安全的 API                                             │
│  • 流式消息处理                                               │
│  • 自定义工具 / Hook 拦截                                     │
│  • Session 管理 + **消息队列**                                │
└─────────────────────────┬───────────────────────────────────────┘
                          │ 启动子进程 + stdio 通信
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Claude Code CLI                               │
│  @anthropic-ai/claude-code                                     │
│  • 工具调用循环 (Read → LLM → Edit → LLM → ...)               │
│  • MCP 协议处理                                                │
│  • 文件系统访问                                                │
│  • Shell 命令执行                                              │
│  • 权限管理                                                    │
└─────────────────────────────────────────────────────────────────┘
```

**核心原理：Agent SDK 不是独立运行时，而是 CLI 的"编程遥控器"**

1. SDK 启动一个 CLI 子进程
2. 通过 stdio (JSON-RPC) 与 CLI 通信
3. CLI 负责工具调用循环、文件操作、MCP 管理
4. SDK 提供 Python/TypeScript 的类型安全封装

### CLI vs SDK 详细对比

| 维度 | Claude Code CLI | Agent SDK |
|------|----------------|-----------|
| **本质** | 独立的可执行程序 | CLI 的编程封装 |
| **安装** | `npm i -g @anthropic-ai/claude-code` | `pip install claude-code-sdk` |
| **依赖关系** | 独立运行 | **依赖 CLI**（必须先装 CLI） |
| **运行环境** | 终端进程 | 你的 Python/TS 进程 |
| **工具能力** | 内置 15+ 工具 + MCP | 继承 CLI 全部能力 |
| **输出格式** | `--output-format json` | 原生对象、类型推断 |
| **流式输出** | `stream-json` | 原生 async iterator |
| **Session 管理** | `--resume` / `--continue` | `resume` 参数 + `ClaudeSDKClient` |
| **权限控制** | 交互式确认 / `--dangerously-skip` | `permissionMode` + `hooks` |
| **结构化输出** | ❌ 不支持 | ✅ `outputFormat` (JSON Schema) |
| **自定义工具** | MCP Server（独立进程） | MCP Server **或** 代码内定义 |
| **Hook 拦截** | `settings.json` 配置 | 代码中定义回调 |
| **并发控制** | 多开终端 / Git Worktrees | `asyncio.gather` / `Promise.all` |
| **错误处理** | 退出码 + stderr | 异常 + `result.subtype` |
| **消息队列** | ❌ 无 | ✅ `ClaudeSDKClient` 支持 |
| **适合场景** | 日常开发、手动操作 | **自动化、企业集成** |

### 什么时候用 SDK？

```
              需要编程控制？
                    │
         ┌─────────┴─────────┐
         │ 否                │ 是
         ▼                   ▼
       用 CLI          需要复杂控制？
                         │
                  ┌──────┴──────┐
                  │ 否          │ 是
                  ▼             ▼
            CLI Headless    Agent SDK
            (-p + json)     (完整控制)
```

**用 CLI 的场景**：日常开发、手动操作
**用 CLI Headless 的场景**：简单自动化、CI/CD 脚本
**用 Agent SDK 的场景**：复杂自动化、多 Agent 协作、企业集成、需要消息队列

### Agent SDK 的核心价值

**相比 CLI Headless**：
- **类型安全** - Python 类型提示 / TypeScript 类型推断
- **流式消息** - `async for` / `for await` 实时处理
- **代码内定义工具** - 无需启动独立 MCP Server
- **Hook 拦截器** - 程序化权限控制
- **结构化输出** - JSON Schema 强类型
- **消息队列** - 持续输入，自动入队，下次调用自动带上

### 为什么要用 Agent SDK？

1. **CI/CD 集成** - PR 自动代码审查、批量重构
2. **企业内部平台** - 定制化 AI 编码助手，集成 SSO/权限
3. **多 Agent 协作** - 规划 Agent → 编码 Agent → 测试 Agent
4. **结构化输出** - 需要返回 JSON 给下游系统处理
5. **自定义工具** - 接入公司内部 API、数据库、监控系统

**什么时候不需要 SDK？**

- 日常开发用 CLI 就够了
- 简单的自动化用 Headless 模式 (`-p` + `--output-format json`)
- 只是需要调用 Claude API，不需要文件操作/工具调用 → 直接用 Anthropic API

### 前提条件

**重要**：Agent SDK **必须先安装 Claude Code CLI**，因为 SDK 本质上是 CLI 的编程封装。

```bash
# macOS/Linux
curl -fsSL https://claude.ai/install.sh | bash

# macOS (Homebrew)
brew install --cask claude-code

# Windows (PowerShell)
winget install Anthropic.ClaudeCode

# npm (全平台)
npm install -g @anthropic-ai/claude-code
```

### 安装 SDK

**Python**：

```bash
pip install claude-code-sdk

# 或使用 uv（推荐）
uv init && uv add claude-code-sdk
```

**TypeScript**：

```bash
npm install @anthropic-ai/claude-code-sdk
```

### API 密钥配置

**方式一：CLI 已登录（推荐）**

如果你已经在终端运行过 `claude` 并登录，SDK 会自动复用认证，无需额外配置。

**方式二：环境变量**

```bash
# macOS / Linux
export ANTHROPIC_API_KEY="sk-ant-..."

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="sk-ant-..."

# 或创建 .env 文件
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

**方式三：第三方提供商（企业用户）**

```bash
# Amazon Bedrock
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...

# Google Vertex AI
export CLAUDE_CODE_USE_VERTEX=1
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Microsoft Foundry (Azure)
export CLAUDE_CODE_USE_FOUNDRY=1
export AZURE_API_KEY=...
```

### URL / 代理配置（国内用户）

**方法一：环境变量代理**

```bash
# HTTP 代理
export HTTPS_PROXY="http://127.0.0.1:7890"

# SOCKS5 代理
export HTTPS_PROXY="socks5://127.0.0.1:1080"
```

**方法二：自定义 API Base URL（中转服务）**

如果你使用第三方中转（如 OpenRouter、自建代理），需要在 CLI 配置中设置：

```bash
# 设置中转地址（实际配置方式请参考你的中转服务文档）
# SDK 会继承 CLI 的配置
```

**方法三：直接在代码中指定（部分 SDK 版本支持）**

```python
# Python - 通过环境变量
import os
os.environ["ANTHROPIC_BASE_URL"] = "https://your-proxy.com/v1"
```

### 完整参数参考

```typescript
query({
  prompt: string | Message[],  // 输入指令或消息数组
  options: {
    // === 模型配置 ===
    model?: string,              // "opus" | "sonnet" | "haiku" 或完整模型名
    fallbackModel?: string,      // 主模型失败时的备用

    // === 工具配置 ===
    allowedTools?: string[],     // 工具白名单，["*"] 表示全部
    disallowedTools?: string[],  // 工具黑名单

    // === 权限控制 ===
    permissionMode?: "default" | "acceptEdits" | "bypassPermissions" | "plan",
    allowDangerouslySkipPermissions?: boolean,  // 配合 bypassPermissions 使用

    // === 行为控制 ===
    maxTurns?: number,           // 最大轮数，防止无限循环
    maxBudgetUsd?: number,       // 预算上限（美元）
    maxThinkingTokens?: number,  // 思考 token 上限

    // === 输出配置 ===
    systemPrompt?: string | { type: "preset", preset: "claude_code", append?: string },
    outputFormat?: { type: "json_schema", schema: object },

    // === 会话管理 ===
    resume?: string,             // 恢复的 session ID
    forkSession?: boolean,       // true = 创建新分支，false = 追加到原会话
    continue?: boolean,          // 继续最近一次对话

    // === MCP 集成 ===
    mcpServers?: Record<string, McpServerConfig>,

    // === 高级选项 ===
    cwd?: string,                // 工作目录
    additionalDirectories?: string[],  // 额外可访问目录
    hooks?: Record<HookEvent, HookCallback[]>,  // 事件钩子
    settingSources?: ("project" | "user" | "policy")[],  // 加载哪些 CLAUDE.md
  }
})
```

**参数详解**：

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `model` | `opus` 最强、`sonnet` 平衡、`haiku` 快速 | 学习阶段用 `sonnet` |
| `allowedTools` | `["Read", "Glob"]` 只读，`["*"]` 全部 | 按需限制 |
| `permissionMode` | `bypassPermissions` 跳过确认 | 开发环境跳过，生产环境用 Hook 控制 |
| `maxTurns` | 简单 10，一般 50，复杂 250 | 宁大勿小 |
| `maxBudgetUsd` | 防止意外高额消费 | 测试时设置 1-5 美元上限 |
| `settingSources` | 加载 CLAUDE.md 等配置 | `["project"]` 加载项目级配置 |

### Python 完整示例

```python
import asyncio
from claude_code_sdk import query, ClaudeCodeOptions

async def main():
    session_id = None

    async for message in query(
        prompt="分析当前项目的架构并给出优化建议",
        options=ClaudeCodeOptions(
            model="sonnet",
            max_turns=50,
            allowed_tools=["Read", "Glob", "Grep"],
            system_prompt="你是一个资深架构师，用中文回答",
        ),
    ):
        # 1. 系统消息 - 获取 session_id
        if message.type == "system" and message.subtype == "init":
            session_id = message.session_id
            print(f"会话 ID: {session_id}")

        # 2. 助手消息 - Claude 的思考和工具调用
        if message.type == "assistant":
            for block in message.message.get("content", []):
                if block.get("type") == "text":
                    print(f"Claude: {block['text']}")
                if block.get("type") == "tool_use":
                    print(f"使用工具: {block['name']}")

        # 3. 结果消息 - 任务完成
        if message.type == "result":
            if message.subtype == "success":
                print(f"\n花费: ${message.total_cost_usd:.4f}")
            else:
                print(f"错误: {message.error}")

    # 恢复会话继续对话
    if session_id:
        async for message in query(
            prompt="刚才的分析中，哪个建议优先级最高？",
            options=ClaudeCodeOptions(resume=session_id),
        ):
            if message.type == "assistant":
                for block in message.message.get("content", []):
                    if block.get("type") == "text":
                        print(block["text"])

asyncio.run(main())
```

### TypeScript 完整示例

```typescript
import { query } from "@anthropic-ai/claude-code-sdk";

async function main() {
  let sessionId: string | undefined;

  for await (const message of query({
    prompt: "Review the code in src/ and suggest improvements",
    options: {
      model: "sonnet",
      maxTurns: 50,
      allowedTools: ["Read", "Glob", "Grep"],
      systemPrompt: "You are a senior code reviewer",
    },
  })) {
    // 1. 系统消息
    if (message.type === "system" && message.subtype === "init") {
      sessionId = message.session_id;
      console.log(`Session ID: ${sessionId}`);
    }

    // 2. 助手消息
    if (message.type === "assistant") {
      for (const block of message.message.content) {
        if (block.type === "text") {
          console.log(`Claude: ${block.text}`);
        }
        if (block.type === "tool_use") {
          console.log(`Using tool: ${block.name}`);
        }
      }
    }

    // 3. 结果消息
    if (message.type === "result") {
      if (message.subtype === "success") {
        console.log(`\nCost: $${message.total_cost_usd.toFixed(4)}`);
      }
    }
  }
}

main().catch(console.error);
```

### 消息类型详解

```typescript
// SDK 返回的消息类型
type SDKMessage =
  | SDKSystemMessage      // 会话初始化
  | SDKAssistantMessage   // Claude 的回复
  | SDKUserMessage        // 用户消息（回放）
  | SDKResultMessage      // 任务结果
  | SDKPartialAssistantMessage  // 流式输出（可选开启）
```

**各类型结构**：

```typescript
// System - 会话启动
{
  type: "system",
  subtype: "init",
  session_id: "abc123...",
  tools: ["Read", "Write", "Bash", ...],
  model: "claude-sonnet-4-5",
  permission_mode: "default"
}

// Assistant - Claude 回复
{
  type: "assistant",
  message: {
    content: [
      { type: "text", text: "我来分析..." },
      { type: "tool_use", name: "Read", input: { file_path: "..." } }
    ]
  }
}

// Result - 任务结束
{
  type: "result",
  subtype: "success" | "error_max_turns" | "error_during_execution",
  total_cost_usd: 0.0234,
  num_turns: 5,
  structured_output: { ... }  // 仅当使用 outputFormat 时
}
```

### 结构化输出 (JSON Schema)

当需要 Agent 返回可被程序直接处理的 JSON 时：

```typescript
import { z } from "zod";
import { zodToJsonSchema } from "zod-to-json-schema";

// 用 Zod 定义 Schema（类型安全）
const CodeReviewSchema = z.object({
  issues: z.array(z.object({
    severity: z.enum(["low", "medium", "high"]),
    file: z.string(),
    line: z.number().optional(),
    description: z.string(),
    suggestion: z.string().optional(),
  })),
  score: z.number().min(0).max(100),
  summary: z.string(),
});

for await (const message of query({
  prompt: "审查 src/ 目录的代码质量问题",
  options: {
    model: "opus",
    allowedTools: ["Read", "Glob", "Grep"],
    outputFormat: {
      type: "json_schema",
      schema: zodToJsonSchema(CodeReviewSchema),
    },
  },
})) {
  if (message.type === "result" && message.structured_output) {
    const result = CodeReviewSchema.parse(message.structured_output);
    console.log(`评分: ${result.score}/100`);
    console.log(`问题数: ${result.issues.length}`);
  }
}
```

**Python 版本（Pydantic）**：

```python
from pydantic import BaseModel
from typing import Optional

class Issue(BaseModel):
    severity: str  # 'low' | 'medium' | 'high'
    file: str
    line: Optional[int] = None
    description: str

class CodeReviewResult(BaseModel):
    issues: list[Issue]
    score: int
    summary: str

# 在 query 中使用
options=ClaudeCodeOptions(
    output_format={
        "type": "json_schema",
        "schema": CodeReviewResult.model_json_schema()
    }
)

# 解析结果
if message.type == "result" and message.structured_output:
    result = CodeReviewResult.model_validate(message.structured_output)
```

### 自定义工具（MCP Server）

SDK 支持在代码中直接定义工具，无需外部 MCP Server：

**TypeScript**：

```typescript
import { query, tool, createSdkMcpServer } from "@anthropic-ai/claude-code-sdk";
import { z } from "zod";

const myTools = createSdkMcpServer({
  name: "my-tools",
  version: "1.0.0",
  tools: [
    tool(
      "get_weather",
      "获取指定坐标的天气",
      { latitude: z.number(), longitude: z.number() },
      async (args) => {
        const res = await fetch(
          `https://api.open-meteo.com/v1/forecast?latitude=${args.latitude}&longitude=${args.longitude}&current=temperature_2m`
        );
        const data = await res.json();
        return { content: [{ type: "text", text: `温度: ${data.current.temperature_2m}°C` }] };
      }
    ),
  ],
});

for await (const message of query({
  prompt: "北京（39.9, 116.4）现在多少度？",
  options: {
    mcpServers: { "my-tools": myTools },
    allowedTools: ["mcp__my-tools__get_weather"],
  },
})) {
  // ...
}
```

**Python**：

```python
from claude_code_sdk import tool, create_sdk_mcp_server, query, ClaudeCodeOptions

@tool("get_weather", "获取天气", {"latitude": float, "longitude": float})
async def get_weather(args: dict):
    import aiohttp
    async with aiohttp.ClientSession() as session:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={args['latitude']}&longitude={args['longitude']}&current=temperature_2m"
        async with session.get(url) as resp:
            data = await resp.json()
            return {"content": [{"type": "text", "text": f"温度: {data['current']['temperature_2m']}°C"}]}

my_tools = create_sdk_mcp_server(name="my-tools", version="1.0.0", tools=[get_weather])

async for message in query(
    prompt="北京（39.9, 116.4）现在多少度？",
    options=ClaudeCodeOptions(
        mcp_servers={"my-tools": my_tools},
        allowed_tools=["mcp__my-tools__get_weather"],
    ),
):
    pass
```

### Hook 拦截（高级权限控制）

```typescript
import { query, HookCallback } from "@anthropic-ai/claude-code-sdk";

// 拦截危险命令
const validateBash: HookCallback = async (input) => {
  const command = input.tool_input?.command ?? "";
  if (command.includes("rm -rf") || command.includes("DROP TABLE")) {
    return {
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: "危险命令已被拦截",
      },
    };
  }
  return {};
};

for await (const message of query({
  prompt: "清理项目临时文件",
  options: {
    permissionMode: "bypassPermissions",
    allowDangerouslySkipPermissions: true,
    hooks: {
      PreToolUse: [{ matcher: "Bash", hooks: [validateBash] }],
    },
  },
})) {
  // ...
}
```

### 高强度使用模式

**1. ClaudeSDKClient（连续对话）**

`query()` 是一次性调用，每次都是独立的。当你需要**持续交互**时，用 `ClaudeSDKClient`：

```python
from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions

async def interactive_session():
    async with ClaudeSDKClient() as client:
        # 第一轮
        await client.query("分析这个项目的结构")
        async for msg in client.receive_response():
            if hasattr(msg, "content"):
                print(msg.content)

        # 第二轮 - 自动保持上下文
        await client.query("重点看安全方面")
        async for msg in client.receive_response():
            if hasattr(msg, "content"):
                print(msg.content)

        # 第三轮
        await client.query("生成修复建议")
        # ...
```

**query() vs ClaudeSDKClient 对比**：

| 特性 | `query()` | `ClaudeSDKClient` |
|------|-----------|-------------------|
| 调用方式 | 一次性 | 持续连接 |
| 上下文 | 需要手动 `resume` | 自动保持 |
| 适用场景 | 单次任务 | 多轮交互 |

**2. 并发任务（多 Agent 协作）**

```python
import asyncio
from claude_code_sdk import query, ClaudeCodeOptions

async def analyze_module(module_path: str):
    results = []
    async for msg in query(
        prompt=f"分析 {module_path} 的代码质量",
        options=ClaudeCodeOptions(
            allowed_tools=["Read", "Glob", "Grep"],
            max_turns=20,
        ),
    ):
        if msg.type == "result":
            return msg.result
    return None

async def main():
    # 并发分析多个模块
    modules = ["src/auth", "src/api", "src/db", "src/utils"]
    results = await asyncio.gather(*[analyze_module(m) for m in modules])

    for module, result in zip(modules, results):
        print(f"{module}: {result[:100]}...")

asyncio.run(main())
```

**3. 预算控制 + 超时**

```typescript
import { query } from "@anthropic-ai/claude-code-sdk";

const controller = new AbortController();
const timeout = setTimeout(() => controller.abort(), 60000); // 60 秒超时

try {
  for await (const message of query({
    prompt: "大规模重构项目",
    options: {
      maxBudgetUsd: 5.0,  // 最多花费 5 美元
      maxTurns: 100,
      abortController: controller,
    },
  })) {
    if (message.type === "result") {
      console.log(`花费: $${message.total_cost_usd}`);
    }
  }
} finally {
  clearTimeout(timeout);
}
```

### 常见陷阱

| 陷阱 | 问题 | 解决 |
|------|------|------|
| 忘记检查 result.subtype | 任务失败但程序继续 | 始终检查 `subtype === "success"` |
| maxTurns 过低 | 复杂任务被截断 | 简单 10，一般 50，复杂 250 |
| 阻塞消息流 | 同步操作卡住迭代器 | 用 `await` 异步操作 |
| Schema 过于复杂 | Agent 难以生成正确输出 | 扁平化，最多 2-3 层嵌套 |
| 未设置预算上限 | 意外高额消费 | 测试时设置 `maxBudgetUsd` |
| CLI 未安装 | SDK 报错找不到命令 | 先 `npm i -g @anthropic-ai/claude-code` |

### 选型建议

- **日常开发** → 直接用 Claude Code CLI
- **简单自动化** → CLI Headless 模式 (`-p` + `--output-format json`)
- **企业集成 / CI/CD** → Agent SDK
- **需要自定义工具** → Agent SDK + MCP Server
- **只调用 Claude API，不需要文件操作** → 直接用 Anthropic API（更轻量）
