# video-scripts / Hooks 与 Headless

> last_verified_commit: 3cf4d89
> source: video-scripts/layer-06-advanced.md (Hooks + Headless + ralph-loop 章节)

## 责任范围

Claude Code 的 7 个 Hook 生命周期事件、配置写法、Hook handler 收到的 JSON stdin 结构；Headless 模式参数与结构化输出；ralph-loop 的 Stop Hook 拦截机制。

不覆盖：MCP Server 配置（见 supplement-mcp.md）、Agent SDK 的 query/ClaudeSDKClient API（见 overview）、Git Worktrees 多会话并行。

## Hooks 七生命周期

| 事件 | 触发时机 | 可否拦截 | 典型用途 |
|------|---------|---------|---------|
| `SessionStart` | Claude Code 启动时 | 否 | 环境检查、加载配置 |
| `UserPromptSubmit` | 用户发送消息后 | 否 | 输入校验、日志记录、字数统计 |
| `PreToolUse` | Claude 执行工具之前 | 是（deny/allow） | 拦截危险命令（`rm -rf`）、自动审批特定工具 |
| `PostToolUse` | 工具执行完成后 | 否 | 自动格式化（`go fmt`）、运行 lint |
| `Stop` | Claude 完成回复时 | 是（block） | 自动提交、发送通知、ralph-loop 迭代控制 |
| `SubagentStop` | SubAgent 完成时 | 是（block） | 收集子任务结果、聚合日志 |
| `TaskCompleted` | 任务完成时 | 否 | 清理临时文件 |

PreToolUse 和 Stop 是两个关键的拦截点：PreToolUse 可以 deny 危险操作，Stop 可以 block 退出并注入新 prompt（ralph-loop 的核心机制）。

## Hook 配置形态

写在 `~/.claude/settings.json`（全局）或 `.claude/settings.json`（项目级）：

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
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/stop-hook.py",
            "timeout": 45
          }
        ]
      }
    ]
  }
}
```

关键字段：

| 字段 | 说明 |
|------|------|
| `type` | 固定为 `"command"` |
| `command` | Shell 命令，handler 通过 stdin 接收 JSON |
| `timeout` | 超时秒数，超时后 hook 被终止 |
| `matcher` | 工具名称匹配（`"Bash"`、`"Edit"`、`"Write"`），空字符串匹配所有 |

### Handler stdin JSON 结构

Hook handler 从 stdin 读取 JSON，关键字段：

- `cwd` — 当前工作目录
- `transcript_path` — 会话 transcript 文件路径（`.jsonl`）
- `tool_name`（PreToolUse/PostToolUse）— 被调用的工具名
- `tool_input`（PreToolUse）— 工具参数

### 拦截输出格式

PreToolUse handler 输出 JSON 拦截：

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "危险命令已被拦截"
  }
}
```

Stop handler 输出 JSON 拦截（ralph-loop 使用此模式阻止退出并注入新 prompt）：

```json
{
  "decision": "block",
  "reason": "继续执行下一个任务",
  "systemMessage": "ralph iteration 3"
}
```

`decision: block` 阻止 Claude Code 退出，`reason` 作为新用户输入注入，`systemMessage` 作为系统消息。

## Headless 模式

Headless 模式无 UI，直接在后台运行。`-p` 进入 Headless，`-c` 继续上次会话。

### 参数表

| 参数 | 说明 | 示例 |
|------|------|------|
| `-p` | 提示词（进入 Headless） | `-p "分析这段代码"` |
| `-c` | 继续上次对话 | `-c -p "接着上次"` |
| `--resume` | 恢复指定会话 | `--resume abc123` |
| `--output-format` | 输出格式 | `text` / `json` / `stream-json` |
| `--input-format` | 输入格式 | `text` / `json` |
| `--max-turns` | 最大对话轮次 | `--max-turns 5` |
| `--allowedTools` | 限制可用工具 | `--allowedTools "Read,Grep,Glob"` |
| `--system-prompt` | 自定义系统提示词 | `--system-prompt "你是代码审查专家"` |
| `--model` | 指定模型 | `--model claude-sonnet-4-20250514` |
| `--permission-mode` | 权限模式 | `--permission-mode plan` |
| `--add-dir` | 添加额外工作目录 | `--add-dir /path/to/lib` |

### --output-format 结构化输出

| 格式 | 用途 | 输出形式 |
|------|------|---------|
| `text`（默认） | 简单脚本、日志 | 纯文本，直接可读 |
| `json` | CI/CD 流水线 | 完整 JSON 对象（含 metadata） |
| `stream-json` | 实时流式处理 | 逐行 JSON，每行一个事件 |

`--output-format json` 输出结构：

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

关键字段：`session_id` 用于 `--resume` 多轮交互；`cost_usd` 和 `duration_ms` 用于成本与耗时监控。

### CI/CD 集成模式

Headless 适合简单自动化。复杂多 Agent 协作、企业集成、需要消息队列的场景应使用 Agent SDK。

三种自动化的选择路径：

- 日常开发 → CLI 交互模式
- 简单自动化 → CLI Headless（`-p` + `--output-format json`）
- 复杂自动化 → Agent SDK（`query()` / `ClaudeSDKClient`）

## 与本仓库代码的对应

| 教程概念 | 代码文件 | 做什么 |
|---------|---------|--------|
| Stop 事件 — 桌面通知 | `examples/scripts/notify-stop.py` | 跨平台（Windows/macOS/Linux）桌面通知；解析 transcript 取项目名、模型、耗时、最后输入；Windows 用 WinRT Toast XML，macOS 用 osascript，Linux 用 notify-send |
| Stop 事件 — ralph-loop 控制 | `examples/scripts/stop-hook.py` | 读取 `.claude/ralph-loop.local.md` 状态文件；检查迭代次数和 `<promise>` 完成标记；输出 `decision: block` 阻止退出并注入下一轮 prompt |
| UserPromptSubmit — 字数统计 | `~/.claude/hooks/analyze_prompt.py`（全局配置） | 每次 Prompt 提交后统计字数并输出 |
| PreToolUse — 危险命令拦截 | Agent SDK 示例（TypeScript） | 匹配 `Bash` 工具，deny 含 `rm -rf` 或 `DROP TABLE` 的命令 |

## ralph-loop 机制

ralph-loop 是一个第三方插件，通过 Stop Hook 实现"无人值守循环"。

核心流程：

1. 安装：`claude plugin install ralph-loop`
2. 创建状态文件 `.claude/ralph-loop.local.md`，写入 YAML frontmatter（`iteration`、`max_iterations`、`completion_promise`）和 prompt 文本
3. 每轮结束时，`stop-hook.py` 从 stdin 读取 `transcript_path`，解析 transcript 提取 Claude 最后输出
4. 检查 `<promise>` 标签：匹配则删除状态文件、允许退出；不匹配则 `decision: block` 并注入下一轮 prompt
5. 迭代计数递增，达到 `max_iterations` 上限后退出

状态文件结构：

```yaml
---
iteration: 1
max_iterations: 10
completion_promise: "所有测试通过"
---
你的任务指令写在这里
```

## 坑点

- **Windows 下 ralph-loop 乱码**：原版 Stop Hook 使用 `.sh` 脚本，Windows 下必出乱码。必须替换为 Python 版 `stop-hook.py`。
- **内存泄露**：Claude Code 存在已知内存泄露（v2.1.39 未修复，GitHub issue #21665 / #19720 / #23252），长时间运行 ralph-loop 可导致 4GB+ 内存占用。`max_iterations` 不建议超过 20-30，不要完全无人值守。
- **Stop Hook handler 必须安全退出**：返回非零退出码可能影响会话。`notify-stop.py` 的 `main()` 始终 `return 0`，异常只写 stderr。
- **transcript 文件过大时性能问题**：`notify-stop.py` 只读最后 512KB（`tail_size = 512 * 1024`），避免加载大文件。
- **Hook 注入风险**：`notify-stop.py` 的 `_oneline()` 函数将换行符折叠，防止 Windows PowerShell here-string 注入和 AppleScript 注入。
- **Worktree 限制**：Git Worktrees 不能跨 worktree 同时修改同一文件，适合功能边界清晰的并行任务。

## 检索锚点

`PreToolUse` / `PostToolUse` / `Stop` / `SubagentStop` / `UserPromptSubmit` / `SessionStart` / `ralph-loop` / `--output-format` / `stream-json` / `notify-stop.py` / `stop-hook.py` / `permissionDecision` / `decision` / `completion_promise` / `--resume` / `WinToast`

## 相关文档

- `video-scripts/layer-06-advanced.md` — Hooks、Headless、ralph-loop、Git Worktrees、Agent SDK 完整教程
- `research/13-claude-code-skills-lessons.md` — Anthropic 内部 skills 分类与编写建议
- `research/15-claude-code-dynamic-workflows.md` — 动态多 Agent 工作流
- `research/16-claude-code-agent-teams.md` — Agent Teams 与 inter-agent messaging
