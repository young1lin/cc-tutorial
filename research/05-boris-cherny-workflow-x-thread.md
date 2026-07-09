---
title: Boris Cherny's Claude Code Workflow - Original X Thread
url: https://x.com/bcherny/status/2007179833990885678
author: Boris Cherny (Creator of Claude Code at Anthropic)
date: 2026-01
tier: T2
topics: [boris-cherny, workflow, parallel-instances, claude-code, x-thread]
---

# Boris Cherny's Claude Code Workflow - Original X Thread

**Source**: https://x.com/bcherny/status/2007179833990885678
**Author**: Boris Cherny (Creator of Claude Code at Anthropic)
**Date**: January 2026
**Translator**: cc-tutorial project

---

## Introduction / 介绍

**English:**
I'm Boris and I created Claude Code. Lots of people have asked how I use Claude Code, so I wanted to show off my setup a bit.

My setup might be surprisingly vanilla! Claude Code works great out of the box, so I personally don't customize it much. There is no one correct way to use Claude Code: we intentionally build it in a way that you can use it, customize it, and hack it however you like. Each person on the Claude Code team uses it very differently.

**中文：**
我是 Boris，我创建了 Claude Code。很多人问我如何使用 Claude Code，所以我想展示一下我的设置。

我的设置可能简单得出乎意料！Claude Code 开箱即用效果很好，所以我个人并没有做太多定制。使用 Claude Code 没有唯一正确的方式：我们特意以这种方式构建它，让你可以按照自己的喜好使用、定制和黑客它。Claude Code 团队的每个人都用得很不一样。

---

## 1. Parallel Claude Instances / 并行 Claude 实例

**English:**
I run 5 Claudes in parallel in my terminal. I number my tabs 1-5, and use system notifications to know when a Claude needs input.

**中文：**
我在终端中并行运行 5 个 Claude。我把标签页编号为 1-5，并使用系统通知来知道什么时候 Claude 需要输入。

**Documentation**: https://code.claude.com/docs/en/terminal-config#iterm-2-system-notifications

---

## 2. Web + Local + Mobile / Web + 本地 + 移动端

**English:**
I also run 5-10 Claudes on http://claude.ai/code, in parallel with my local Claudes. As I code in my terminal, I will often hand off local sessions to web (using &), or manually kick off sessions in Chrome, and sometimes I will --teleport back and forth. I also start a few sessions from my phone (from the Claude iOS app) every morning and throughout the day, and check in on them later.

**中文：**
我还会在 http://claude.ai/code 上运行 5-10 个 Claude，与我的本地 Claude 并行。当我在终端编码时，我经常把本地会话交接给 web（使用 &），或者在 Chrome 中手动启动会话，有时我会来回 --teleport（传送）。我每天早上和一整天都会从手机（Claude iOS 应用）启动几个会话，稍后再查看它们。

---

## 3. Use Opus 4.5 with Thinking / 使用 Opus 4.5 + Thinking

**English:**
I use Opus 4.5 with thinking for everything. It's the best coding model I've ever used, and even though it's bigger & slower than Sonnet, since you have to steer it less and it's better at tool use, it is almost always faster than using a smaller model in the end.

**中文：**
我用 Opus 4.5 with thinking 处理所有事情。这是我用过的最好的编码模型，虽然它比 Sonnet 更大、更慢，但由于你需要引导它的次数更少，而且它更擅长使用工具，最终几乎总是比使用更小的模型更快。

**Key Insight**: The bottleneck isn't token generation speed — it's human time spent correcting mistakes. A smarter model upfront eliminates the "correction tax" later.

---

## 4. Shared CLAUDE.md / 共享的 CLAUDE.md

**English:**
Our team shares a single http://CLAUDE.md for the Claude Code repo. We check it into git, and the whole team contributes multiple times a week. Anytime we see Claude do something incorrectly we add it to the http://CLAUDE.md, so Claude knows not to do it next time.

Other teams maintain their own http://CLAUDE.md's. It is each team's job to keep theirs up to date.

**中文：**
我们的团队为 Claude Code 仓库共享一个 http://CLAUDE.md。我们把它提交到 git，整个团队每周贡献多次。每当我们看到 Claude 做错了什么，我们就把它添加到 http://CLAUDE.md 中，这样 Claude 就知道下次不要这样做了。

其他团队维护他们自己的 http://CLAUDE.md。保持他们的最新状态是每个团队的工作。

**Key Practice**: "Every mistake becomes a rule." The longer the team works together, the smarter the agent becomes.

---

## 5. Code Review Integration / 代码审查集成

**English:**
During code review, I will often tag @.claude on my coworkers' PRs to add something to the http://CLAUDE.md as part of the PR. We use the Claude Code Github action (/install-github-action) for this. It's our version of @danshipper's Compounding Engineering.

**中文：**
在代码审查期间，我经常在同事的 PR 上标记 @.claude，作为 PR 的一部分向 http://CLAUDE.md 添加内容。我们为此使用 Claude Code Github action（/install-github-action）。这是我们的 @danshipper 的"复合工程"版本。

**Reference**: Dan Shipper's Compounding Engineering - the practice of having AI learn from each code review to compound knowledge over time.

---

## 6. Plan Mode First / 优先使用 Plan Mode

**English:**
Most sessions start in Plan mode (shift+tab twice). If my goal is to write a Pull Request, I will use Plan mode, and go back and forth with Claude until I like its plan. From there, I switch into auto-accept edits mode and Claude can usually 1-shot it. A good plan is really important!

**中文：**
大多数会话以 Plan mode（按两次 shift+tab）开始。如果我的目标是写一个 Pull Request，我会使用 Plan mode，并与 Claude 来回沟通，直到我喜欢它的计划。从那里，我切换到自动接受编辑模式，Claude 通常可以一次性完成。一个好的计划真的很重要！

**Key Practice**: Always plan before coding. A good plan = better execution with less iteration.

---

## 7. Slash Commands for Common Workflows / 常用工作流的 Slash 命令

**English:**
I use slash commands for every "inner loop" workflow that I end up doing many times a day. This saves me from repeated prompting, and makes it so Claude can use these workflows, too. Commands are checked into git and live in .claude/commands/.

For example, Claude and I use a /commit-push-pr slash command dozens of times every day. The command uses inline bash to pre-compute git status and a few other pieces of info to make the command run quickly and avoid back-and-forth with the model.

**中文：**
我对我每天最终要做的很多次的每一个"内循环"工作流都使用 slash 命令。这让我免于重复提示，也使 Claude 可以使用这些工作流。命令被提交到 git 并存放在 .claude/commands/ 中。

例如，Claude 和我每天使用 /commit-push-pr slash 命令几十次。该命令使用内联 bash 来预计算 git 状态和一些其他信息，使命令快速运行并避免与模型来回交互。

**Documentation**: https://code.claude.com/docs/en/slash-commands#bash-command-execution

---

## 8. Subagents for Specialized Tasks / 专门任务的 Subagents

**English:**
I use a few subagents regularly: code-simplifier simplifies the code after Claude is done working, verify-app has detailed instructions for testing Claude Code end to end, and so on. Similar to slash commands, I think of subagents as automating the most common workflows that I do for most PRs.

**中文：**
我经常使用几个 subagents：code-simplifier 在 Claude 完成工作后简化代码，verify-app 有详细的端到端测试 Claude Code 的指令，等等。与 slash 命令类似，我认为 subagents 是自动化我对大多数 PR 所做的最常见工作流。

---

## 9. PostToolUse Hook for Formatting / PostToolUse Hook 用于格式化

**English:**
We use a PostToolUse hook to format Claude's code. Claude usually generates well-formatted code out of the box, and the hook handles the last 10% to avoid formatting errors in CI later.

**中文：**
我们使用 PostToolUse hook 来格式化 Claude 的代码。Claude 通常开箱即用地生成格式良好的代码，hook 处理最后的 10%，以避免稍后在 CI 中出现格式错误。

**Key Practice**: Automate the "last mile" tasks with hooks.

---

## 10. Pre-allow Safe Commands / 预先允许安全命令

**English:**
I don't use --dangerously-skip-permissions. Instead, I use /permissions to pre-allow common bash commands that I know are safe in my environment, to avoid unnecessary permission prompts. Most of these are checked into .claude/settings.json and shared with the team.

**中文：**
我不使用 --dangerously-skip-permissions。相反，我使用 /permissions 来预先允许我知道在我的环境中安全的常见 bash 命令，以避免不必要的权限提示。其中大部分被提交到 .claude/settings.json 并与团队共享。

**Key Practice**: Be selective about permissions, not reckless.

---

## 11. MCP for External Tools / MCP 用于外部工具

**English:**
Claude Code uses all my tools for me. It often searches and posts to Slack (via the MCP server), runs BigQuery queries to answer analytics questions (using bq CLI), grabs error logs from Sentry, etc. The Slack MCP configuration is checked into our .mcp.json and shared with the team.

**中文：**
Claude Code 为我使用我所有的工具。它经常搜索并发布到 Slack（通过 MCP 服务器），运行 BigQuery 查询来回答分析问题（使用 bq CLI），从 Sentry 获取错误日志等等。Slack MCP 配置被提交到我们的 .mcp.json 并与团队共享。

**Key Practice**: If you have a tool or API, Claude can use it via MCP.

---

## 12. Long-running Task Strategies / 长时间运行任务的策略

**English:**
For very long-running tasks, I will either (a) prompt Claude to verify its work with a background agent when it's done, or (b) use an agent Stop hook to do that more deterministically, or (c) use the ralph-wiggum plugin (originally dreamt up by @GeoffreyHuntley). I will also use either --permission-mode=dontAsk or --dangerously-skip-permissions in a sandbox to avoid permission prompts for the session, so Claude can cook without being blocked on me.

**中文：**
对于非常长时间运行的任务，我要么（a）提示 Claude 在完成后使用后台 agent 验证其工作，要么（b）使用 agent Stop hook 更确定地执行此操作，要么（c）使用 ralph-wiggum 插件（最初由 @GeoffreyHuntley 构思）。我还将在沙盒中使用 --permission-mode=dontAsk 或 --dangerously-skip-permissions 来避免会话的权限提示，这样 Claude 可以不受阻碍地运行。

**References**:
- Plugin: https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-wiggum
- Hooks: https://code.claude.com/docs/en/hooks-guide

---

## 13. Verification Loops (Most Important!) / 验证循环（最重要！）

**English:**
A final tip: probably the most important thing to get great results out of Claude Code -- give Claude a way to verify its work. If Claude has that feedback loop, it will 2-3x the quality of the final result.

Claude tests every single change I land to http://claude.ai/code using the Claude Chrome extension. It opens a browser, tests the UI, and iterates until the code works and the UX feels good.

Verification looks different for each domain. It might be as simple as running a bash command, or running a test suite, or testing the app in a browser or phone simulator. Make sure to invest in making this rock-solid.

**中文：**
最后一个提示：可能是从 Claude Code 获得出色结果的最重要的事情 —— 给 Claude 一种验证其工作的方法。如果 Claude 有那个反馈循环，它将使最终结果的质量提高 2-3 倍。

Claude 使用 Claude Chrome 扩展测试我落地到 http://claude.ai/code 的每一个更改。它打开浏览器，测试 UI，并迭代直到代码工作并且 UX 感觉良好。

验证在每个领域看起来都不同。它可能就像运行 bash 命令一样简单，或者运行测试套件，或在浏览器或手机模拟器中测试应用程序。确保投资使其坚如磐石。

**Documentation**: https://code.claude.com/docs/en/chrome

**Key Insight**: This is the single most important practice. Without verification, Claude is just guessing. With verification, Claude is self-correcting.

---

## Summary / 总结

### Core Principles / 核心原则

| Principle | English | 中文 |
|-----------|---------|------|
| **1. Parallel Processing** | Run multiple Claudes simultaneously | 同时运行多个 Claude |
| **2. Best Model** | Use Opus 4.5 with thinking | 使用 Opus 4.5 + thinking |
| **3. Shared Memory** | Team CLAUDE.md in git | 团队 CLAUDE.md 提交到 git |
| **4. Plan First** | Always start with Plan mode | 始终以 Plan mode 开始 |
| **5. Automate Repetition** | Slash commands for common workflows | 常用工作流使用 slash 命令 |
| **6. Verify Everything** | Give Claude feedback loops | 给 Claude 反馈循环 |

### The "Vanilla" Philosophy / "原生"哲学

**English:**
Boris emphasizes that his setup is "surprisingly vanilla." Claude Code works great out of the box. The key is not heavy customization — it's understanding the core workflows: Plan mode, shared CLAUDE.md, and verification loops.

**中文：**
Boris 强调他的设置"简单得出乎意料"。Claude Code 开箱即用效果很好。关键不是大量定制 —— 而是理解核心工作流：Plan mode、共享的 CLAUDE.md 和验证循环。

---

**Version**: 1.0.0
**Created**: 2026-01-11
**Project**: cc-tutorial
