# Headless CLI：claude -p 与 CI 集成

## 先说结论

**[Tutorial perspective]** `-p` 把 Claude Code 从交互终端变成一个可管道、可脚本化的 Unix 工具：stdin 进，text/json 出。这是把它塞进 CI、cron、pre-commit 的钥匙。

## claude -p：无头单次执行

`T1` flags 权威口径见官方 [CLI reference](https://code.claude.com/docs/en/cli-reference)。

`实测 @ Claude Code v2.1.202`（2026-07-07，Windows 10）：

```bash
claude -p "用一句话说明这个仓库是做什么的" --model sonnet
```

输出：

```text
这是一个用于制作 Claude Code 教程视频脚本的项目仓库，包含 9 层视频脚本（理论→环境搭建→基础→工作流→配置→进阶→注意事项→实战→补充）、示例代码与研究资料，并配套一个真实案例项目 mybatis-boost。
```

一句话进，一句话出，没有交互框、没有权限确认弹窗。这就是无头模式的全部意义：可以被另一个程序当作黑盒调用。

三种输出格式：`--output-format text`（默认）、`json`、`stream-json`。JSON 模式实测：

```bash
claude -p "用一句话说明这个仓库是做什么的" --model sonnet --output-format json
```

顶层字段（本次实测抓到的完整字段名）：

`type`、`subtype`、`is_error`、`api_error_status`、`duration_ms`、`duration_api_ms`、`ttft_ms`、`ttft_stream_ms`、`time_to_request_ms`、`num_turns`、`result`、`stop_reason`、`session_id`、`total_cost_usd`、`usage`、`modelUsage`、`permission_denials`、`terminal_reason`、`fast_mode_state`、`uuid`。

对脚本化调用真正有用的是这几个：`result`（正文答案）、`session_id`（喂给 `--resume` 用）、`total_cost_usd`（记账）、`is_error`（判断成败，别只看退出码）、`usage`（token 明细，含 `cache_read_input_tokens`/`cache_creation_input_tokens`，见 [token.md](token.md)）。

## 会话续接

`-c/--continue` 续最近一次会话，`--resume <session-id>` 按 ID 恢复指定会话。

`实测 @ Claude Code v2.1.202`（2026-07-07，Windows 10）：

```bash
claude -p --continue "把刚才那句话压缩到一半长度" --model sonnet
```

输出：

```text
Claude Code 教程项目：视频脚本、示例代码与研究资料。
```

上一条 `--output-format json` 调用的 `result` 是「这是一个 Claude Code 教程项目，包含 9 层视频脚本、示例代码和研究资料，用于制作 Claude Code 的教学视频内容。」（85 token）。这条 `--continue` 输出把它压到约一半长度，且内容明显是对上一句的压缩改写，不是重新回答原问题——证明 `--continue` 确实续上了上一次会话的上下文，不是重新起了一轮空会话。

`-c` 找的是「当前目录最近一次会话」，不是「最近一次 `-p` 调用」。如果同一目录下并行跑多个无头调用，`-c` 续到哪一个是不确定的；需要精确定位就必须用 `--resume <session-id>`，`session_id` 从上一条的 JSON 输出里拿。

## 权限与模型控制

脚本场景三件套（`T1` [CLI reference](https://code.claude.com/docs/en/cli-reference)）：

- `--model sonnet`：脚本化调用没必要烧大模型。
- `--allowedTools`：白名单放行工具，避免无头模式卡在权限询问。
- `--permission-mode`：`实测 @ Claude Code v2.1.202` 的 `--help` 输出给出的可选值是 `acceptEdits`、`auto`、`bypassPermissions`、`manual`、`dontAsk`、`plan`。`T1` 官方 [Permission modes](https://code.claude.com/docs/en/permission-modes) 的准确口径：配置值本体至今仍是 `default`（hooks、SDK、settings 用的都是它），`manual` 是 v2.1.200 起新增的别名，Manual 是 CLI/IDE 的 UI 标签——是加别名，不是重命名。`--help` 的 choices 只展示 `manual`，但 `default` 依然被接受：`实测 @ Claude Code v2.1.202`，`claude --permission-mode default -p` 正常执行，不报参数错误。

无头场景最常配的两个值：`bypassPermissions`（完全跳过权限确认，等价于 `--dangerously-skip-permissions`，只在无网络沙箱里用）、`plan`（只出计划不落地，适合先跑一遍看 Claude 打算做什么）。

**[Author's analysis]** 无头模式的权限默认从紧是对的：没有人在场确认，放权就要显式声明。宁可脚本失败，不要静默越权。

## CI 集成

`T1` 官方提供 GitHub Actions 集成（[Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions)）：装 `anthropics/claude-code-action@v1`，PR/issue 评论里 `@claude` 触发，或者用 `prompt` 字段直接派发定时任务（如按 cron 生成日报）；CLI 参数统一通过 `claude_args` 透传，例如 `claude_args: "--model claude-sonnet-5 --max-turns 10"`。

本地脚本示例——pre-commit 里让 Claude 检查暂存区 diff：

```bash
git diff --cached | claude -p "检查这个 diff 有没有明显的 bug 或泄密，只输出问题清单，没有就输出 OK" --model sonnet
```

## 边界

Agent SDK 是另一条路：程序内嵌 agent、自定义工具、多轮控制。那是独立主题，本文不展开。
