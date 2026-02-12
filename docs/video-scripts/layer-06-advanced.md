# 第六层：高级功能

## MCP

从上面的例子我们可以看到，如果要让 AI 大模型了解最新的信息，必须使用 Function Calling 调用工具，并且把工具返回的信息给带上。但是并不是所有的 Agent 工具都会用 Function Calling，像比较早期的 Cline 就是用的 XML 格式返回，XML 工具调用，在那个时候提出了 MCP。当然 MCP 不只是工具调用，还有 `prompts` 和 `resources` 等概念，当然这些很多工具都没有用到。

如果要详细从零了解 MCP 除了看官网，还可以看我这个，我这里不止有时序图、概念讲解，还有完整的最小化 Python 代码实现。`https://github.com/young1lin/minimal-mcp`

# SubAgent

有自己的 Prompt，有自己可以用的 Tool，也有自己的独立的上下文窗口。关于如何创建合适的 subAgent，在 Claude Code 中，可以输入 `/agents` 命令，回车，然后按照提示来创建 Agent，本质上就是一个 Markdown 文件。这个 Markdown 文件包含了元信息，名称、描述（会在上下文中占用）、model（继承父级，或者指定模型）、color（颜色）等等。其中描述（description）是最关键的字段，它会被写入主 Agent 的 System Prompt 中，Claude 根据这段描述来判断什么时候应该调用这个 SubAgent。所以描述里要包含清晰的触发条件和使用示例（用 `<example>` 标签），让主 Agent 知道"遇到什么场景就该把任务交给我"。SubAgent 的独立上下文窗口意味着它不会污染主对话的上下文，干完活返回结果，主 Agent 继续工作。

```markdown
---
name: java-unit-test-generator
description: Use this agent when you need to create comprehensive JUnit5 unit tests for Java code. Examples: <example>Context: User has just written a UserService class with methods for creating, updating, and validating users. user: 'I just finished implementing UserService with createUser, updateUser, and validateUser methods. Can you help me create unit tests?' assistant: 'I'll use the java-unit-test-generator agent to create comprehensive JUnit5 tests for your UserService class.'</example> <example>Context: User is working on a Spring Boot application and has implemented a REST controller. user: 'Here's my OrderController class. I need to write tests for all the endpoints including error handling.' assistant: 'I'll use the java-unit-test-generator agent to create MockMvc-based tests for your OrderController.'</example>
model: inherit
color: green
---
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

详细的插件推荐和安装指南见 [docs/examples/recommended-plugins/](docs/examples/recommended-plugins/)。

| 插件 | 用途 | 安装方式 |
|------|------|----------|
| **firecrawl** | 抓取 JS 渲染网站 | `claude mcp add firecrawl --api-key YOUR_KEY` |
| **claude-mem** | 跨会话长期记忆 | `/plugin install claude-mem` |
| **ccusage** | Token 用量统计 | `npm install -g ccusage` |
| **repomix** | 代码库打包为 AI 格式 | `npm install -g repomix` |
| **claude-squad** | 多代理并行管理 | `npm install -g claude-squad` |

官方 MCP 服务器（文件/网络/Git/记忆/推理）：`npx @modelcontextprotocol/server-filesystem` 等。

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

**局限性（实话）：** Git Worktrees 不能跨 worktree 同时修改同一个文件。如果两个分支都需要改 `src/config.ts`，合并时必然有冲突。所以它适合**功能边界清晰**的并行任务——一个做认证模块、一个做性能优化、一个写测试——而不是两个人改同一个模块。对我来说有点鸡肋，因为实际项目中很难完全避免文件重叠，但如果你的项目模块化做得好，这确实是个强大的并行策略。

**替代方案：** 如果你不想折腾 worktrees，最简单的并行方式是开多个终端 tab，每个 tab 一个 Claude Code 会话，做不同的任务。用 `/clear` 保持每个会话上下文干净就行。

## 我能休息，Claude Code 不能休息

ralph-loop 插件，让 Claude Code 在你不在的时候持续工作。它的核心思路是：给 Claude Code 一个任务列表，插件会自动循环驱动 Claude Code 执行任务，遇到需要确认的地方自动同意，直到所有任务完成或达到设定的轮次上限。

**⚠️ Windows 用户注意事项：**

原版 ralph-loop 的 Stop Hook 使用 shell 脚本（`.sh` 文件），在 Windows 下执行会出现乱码问题。需要替换为 Python 版本的 hook 脚本。

解决方案：使用 Python 版本的 `stop-hook.py`（示例文件见 `docs/examples/recommended-plugins/stop-hook.py`），在 `.claude/settings.json` 中配置：

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

Claude Code 本身存在内存泄露问题（截至 v2.1.39 版本仍未修复）。长时间无人值守运行 ralph-loop 可能导致：

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

## 自动化

Vibe Kanban 可以直接在网页中，和 Claude Code、CodeX、Copilot-CLI 进行交互，对话，编写 Kanban 待办事项，拖动。

## Claude Code SDK / Agent SDK

Claude Code CLI 是面向开发者的交互工具；Agent SDK 是面向**构建 Agent 平台**的编程库。两者定位不同，互为补充。

| 维度 | Claude Code CLI | Agent SDK |
|------|----------------|-----------|
| 使用方式 | 终端交互 / Headless | Python / TypeScript 代码调用 |
| 适用场景 | 日常开发、代码审查 | 自定义 Agent、企业集成 |
| 安装 | `npm i -g @anthropic-ai/claude-code` | `pip install claude-code-sdk` / `npm i @anthropic-ai/claude-code-sdk` |
| 输出控制 | `--output-format` | 原生对象、回调、流式 |
| 工具管理 | 内置 + MCP | 自定义 Tool 注册 + MCP 集成 |

### Agent SDK 核心组件

- **Agent**：主体，定义行为和目标
- **Tool**：工具定义，Agent 可调用的能力
- **Session**：状态管理，维护对话上下文
- **MCP 集成**：可直接复用已有的 MCP Server
- **SubAgent 调用**：Agent 之间可以互相委托任务
- **流式输出**：实时获取 Agent 的思考和输出过程
- **成本追踪**：内置 Token 用量和费用统计

### Python 示例

```python
import anyio
from claude_code_sdk import query, ClaudeCodeOptions, Message

async def main():
    messages: list[Message] = []
    # 流式获取结果
    async for message in query(
        prompt="分析当前项目的架构并给出优化建议",
        options=ClaudeCodeOptions(
            max_turns=10,
            system_prompt="你是一个资深架构师",
        ),
    ):
        if message.type == "text":
            print(message.content)
        messages.append(message)

anyio.run(main)
```

### TypeScript 示例

```typescript
import { query, type Message } from "@anthropic-ai/claude-code-sdk";

async function main() {
  const messages: Message[] = [];

  for await (const message of query({
    prompt: "Review the code in src/ and suggest improvements",
    options: {
      maxTurns: 10,
      systemPrompt: "You are a senior code reviewer",
    },
  })) {
    if (message.type === "text") {
      console.log(message.content);
    }
    messages.push(message);
  }
}

main();
```

### 适用场景

- **企业内部 Agent 平台**：用 SDK 构建定制化的 AI 编码助手，集成到内部工具链
- **批量代码审查系统**：结合 CI/CD，对多个 PR 并行执行代码审查
- **自动化测试流水线**：Agent 自动编写测试、运行测试、修复失败的测试
- **自定义 IDE 插件后端**：作为 VSCode / JetBrains 插件的后端引擎
- **多 Agent 协作**：一个 Agent 负责规划，一个负责编码，一个负责测试

**选型建议**：日常开发直接用 Claude Code CLI（包括 Headless 模式）就够了。只有当你需要在自己的程序中嵌入 Claude Code 的能力、或者构建面向团队的 Agent 平台时，才需要 Agent SDK。
