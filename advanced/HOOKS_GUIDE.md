# Hooks 完全参考

## 先说结论

Hook 是执行，不是请求。CLAUDE.md 里写「别碰 .env」，Claude 大概率听话，不保证；`PreToolUse` hook 拦截，是物理上做不到。这条原理在[扩展机制全景](EXTENSIONS_OVERVIEW.md)立过论，本文只做一件事：把 hooks 的事件、配置位置、matcher、输入输出协议、安全边界一次讲清。全文对照官方 [Hooks reference](https://code.claude.com/docs/en/hooks)（`T1`，2026-07-07 校对 @ Claude Code v2.1.202）。

## 事件全景

官方事件约 30 个，按生命周期分组（`T1`）：

| 分组 | 事件 |
|------|------|
| 会话 | `SessionStart`、`SessionEnd`、`Setup`、`InstructionsLoaded`、`ConfigChange`、`CwdChanged` |
| Prompt 与消息 | `UserPromptSubmit`、`UserPromptExpansion`、`Notification`、`MessageDisplay` |
| 工具调用 | `PreToolUse`、`PermissionRequest`、`PermissionDenied`、`PostToolUse`、`PostToolUseFailure`、`PostToolBatch`、`FileChanged` |
| 停止与压缩 | `Stop`、`StopFailure`、`PreCompact`、`PostCompact` |
| Subagent 与 Teams | `SubagentStart`、`SubagentStop`、`TeammateIdle`、`TaskCreated`、`TaskCompleted` |
| Worktree | `WorktreeCreate`、`WorktreeRemove` |
| MCP 交互 | `Elicitation`、`ElicitationResult` |

最常用的五个：`PreToolUse`（拦）、`PostToolUse`（验）、`UserPromptSubmit`（预处理）、`SessionStart`（注入上下文）、`Stop`（拦截退出——Ralph Loop 的核心，见 [Loop 与调度全指南](LOOPS_SCHEDULING_GUIDE.md)）。

## 配置在哪里

六个位置，全部命中的 hook **并行执行**，相同 handler 自动去重（`T1`）：

| 位置 | 作用域 | 入库共享 |
|------|--------|----------|
| `~/.claude/settings.json` | 本机所有项目 | 否 |
| `.claude/settings.json` | 单项目 | 是 |
| `.claude/settings.local.json` | 单项目 | 否 |
| managed 设置 | 组织 | 管理员控制 |
| 插件 `hooks/hooks.json` | 插件启用时 | 随插件 |
| skill / agent frontmatter 的 `hooks` 字段 | 组件存活期间 | 随文件 |

frontmatter hooks 只在 skill/agent 激活期间生效，结束即清理；写在 subagent 里的 `Stop` 自动转成 `SubagentStop`——因为 subagent 完成时触发的是后者。总闸：settings 里 `"disableAllHooks": true`；企业面可用 `allowManagedHooksOnly` 只放行管理员审过的 managed hook。

## matcher 与 if

`matcher` 决定 hook 对什么触发，按字符内容三分（`T1`）：

- `"*"`、空串或省略：全部命中。
- 只含 `[a-zA-Z0-9_\- ,|]`：精确匹配，或 `|` / `,` 分隔的列表，如 `Edit|Write`。
- 含任何其他字符：按**未锚定**的 JS 正则求值。坑在这里：`Edit.*` 会同时命中 `NotebookEdit`——要全串匹配就写 `^Edit$`。

matcher 匹配的对象随事件变：工具类事件匹配工具名；`SessionStart` 匹配来源（`startup`/`resume`/`clear`/`compact`）；`SubagentStart/Stop` 匹配 agent 类型；`PreCompact` 匹配 `manual`/`auto`。`UserPromptSubmit`、`Stop`、`TeammateIdle`、`TaskCreated`、`TaskCompleted`、`WorktreeCreate/Remove` 不支持 matcher。MCP 工具名格式是 `mcp__<server>__<tool>`，匹配整个 server 写 `mcp__memory__.*`。

工具类事件（`PreToolUse`、`PostToolUse`、`PostToolUseFailure`、`PermissionRequest`、`PermissionDenied`）还可以再加一层 `if`，用 permissions 规则语法收窄：

```json
{
  "matcher": "Bash",
  "hooks": [
    {
      "type": "command",
      "if": "Bash(rm *)",
      "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.sh"
    }
  ]
}
```

`if` 的 Bash 匹配不天真（`T1`）：`FOO=bar git push` 剥掉前缀赋值照样命中 `Bash(git *)`；`npm test && git push` 逐段检查；`echo $(rm -rf /)` 连命令替换里的 `rm` 都查得出来。

## 五种 handler

| 类型 | 干什么 | 关键字段 |
|------|--------|----------|
| `command` | 跑本地命令/脚本 | `command`、`timeout`、`async`、`asyncRewake`、`shell`、`statusMessage` |
| `prompt` | 单次 LLM 判定 | `prompt`、`model` |
| `agent` | 派一个带工具的 agent 验证 | `prompt`、`timeout` |
| `http` | 把事件 POST 到外部端点 | `url`、`headers`、`allowedEnvVars` |
| `mcp_tool` | 调用已连接 MCP server 的某个工具 | `server`、`tool`、`input`；server 必须已连接，不触发 OAuth |

command 型加 `async: true` 后台执行不阻塞主流程；`asyncRewake: true`（隐含 async）在脚本以退出码 2 结束时把输出作为 system reminder 唤醒 Claude。

## 输入协议：stdin 上的 JSON

hook 不靠环境变量拿参数。stdin 进来一段 JSON：公共字段 `hook_event_name`、`session_id`、`transcript_path`、`cwd`、`permission_mode`，工具类事件再加 `tool_name`、`tool_input`：

```bash
#!/bin/bash
# Read the file path from the PreToolUse/PostToolUse payload.
FILE=$(jq -r '.tool_input.file_path')
```

可用环境变量只有少数几个：`$CLAUDE_PROJECT_DIR`、`$CLAUDE_PLUGIN_ROOT`、`$CLAUDE_ENV_FILE`、`$CLAUDE_EFFORT` 等。不存在 `$FILE_PATH` 这类逐字段变量——想拿字段，解析 stdin。

## 输出协议：退出码 + JSON

三档退出码（`T1`）：

| 退出码 | 语义 |
|--------|------|
| `0` | 放行；stdout 若是 JSON 则按决策字段解析 |
| `2` | 阻断；stderr 喂回 Claude 作为反馈 |
| 其他 | 非阻断错误，动作照常执行 |

**`exit 1` 不会阻断。** Unix 直觉在这里失灵——官方原文明确：要强制拦截，用 `exit 2`。

退出码 0 时 stdout 的 JSON 决策，通用字段：`continue`（`false` 直接停掉 Claude）、`stopReason`、`suppressOutput`、`systemMessage`、`hookSpecificOutput.additionalContext`（注入 Claude 上下文）。事件专属决策，挑要紧的（`T1`）：

- `PreToolUse`：`permissionDecision: allow|deny|ask|defer`，还能用 `updatedInput` **改写工具入参**再放行。
- `PostToolUse`：`updatedToolOutput` 替换工具输出，`additionalContext` 附加评语。
- `UserPromptSubmit` / `Stop` / `SubagentStop` / `PreCompact` 等：`{"decision": "block", "reason": "..."}`——只有 `block` 一个合法值，省略即放行。Ralph Loop 的自我循环就是 `Stop` hook 返回 `block` + 原 prompt（[源码级拆解](LOOPS_SCHEDULING_GUIDE.md)）。
- `SessionStart`：`additionalContext` 注入上下文、`initialUserMessage` 预填首条消息、`sessionTitle` 命名会话、`watchPaths` 声明监听路径。

## 活例子

`实测`（本教程作者环境，2026-07-07，Claude Code v2.1.202）：

- 用户级 `~/.claude/settings.json` 挂了两组 command hook：`UserPromptSubmit` 跑 `analyze_prompt.py record`——每条 prompt 提交后统计字符数、词数并回显横幅，hook 的成功输出直接注入会话上下文；`Stop` 挂两个脚本（更新模型使用记录 + 桌面通知）。每轮对话都能看到它触发——事件必触发，这就是 hook 与 prompt 指令的本质差别。桌面通知脚本的脱敏版收录在 [examples/scripts/notify-stop.py](../examples/scripts/notify-stop.py)：零依赖，从 stdin 读 hook JSON，Windows toast / macOS osascript / Linux notify-send 三平台。
- superpowers 插件用 SessionStart hook 把 `using-superpowers` skill 全文注入每个新会话——[SUPERPOWERS_GUIDE](SUPERPOWERS_GUIDE.md) 那句「skills 是弹药，hook 是保险栓」落地在这里。
- `Stop` hook 的极致用法（拦截退出、强制自主循环、防撒谎逃脱）见 [LOOPS_SCHEDULING_GUIDE](LOOPS_SCHEDULING_GUIDE.md) 的 Ralph Loop 章节。

## 安全边界

hook 以你的身份跑：无沙箱、继承全部环境变量、能读写你能读写的一切（`T1` 执行模型如此，官方无独立警告页）。四条纪律：

1. stdin 里是工具的**全部入参**——可能含密钥、文件内容。hook 脚本别乱写日志。
2. `.claude/settings.json` 入库共享——review PR 时把 hooks diff 当代码审。它就是代码。
3. 装插件先看它的 `hooks/hooks.json`——hook 随插件启用自动生效，以你的权限执行。
4. `http` hook 会把事件全量 POST 出去——HTTPS、自己控制的端点、密钥走 `allowedEnvVars`，别硬编码进 headers。

## 何时不用

**[Tutorial perspective]** 能用 permissions 的 `deny` 规则解决的，别写 hook——声明式规则比脚本便宜，而且不会挂。hook 是代码：会出 bug、会超时、会拖慢每一次工具调用。它只该出现在「规则必须每次成立」且 permissions 语法表达不了的地方：内容级校验、外部系统联动、注入上下文、拦截退出。
