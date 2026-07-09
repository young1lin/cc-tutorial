# Worktree 与并行开发

## 先说结论

Worktree 管文件系统隔离。Agent Teams 管协作，Subagents 管上下文隔离，Worktree 管的是「两个任务同时改文件不互相踩」。三者可叠加。

**[Tutorial perspective]** 选型判断：改的是同一批文件 → 排队做，别并行；改的是不同模块 → Worktree 并行；还需要 agent 之间沟通 → Teams + Worktree 叠加。

## 原生入口：会话内 Worktree

`实测 @ Claude Code v2.1.202`（2026-07-07，Windows 10）

对话里直接说「创建一个 worktree 来处理 X」即可触发 EnterWorktree 工具。实测记录：

- 创建位置：`D:\goProject\cc-tutorial\.claude\worktrees\demo-parallel-test`。`EnterWorktree(name: "demo-parallel-test")` 返回原文：「Created worktree at D:\goProject\cc-tutorial\.claude\worktrees\demo-parallel-test on branch worktree-demo-parallel-test. The session is now working in the worktree. Use ExitWorktree to leave mid-session, or exit the session to be prompted.」
- 分支命名：`worktree-demo-parallel-test`——固定前缀 `worktree-` 拼接 `name` 参数。
- 退出保留改动：`ExitWorktree(action: "keep")` 返回原文：「Exited worktree. Your work is preserved at D:\goProject\cc-tutorial\.claude\worktrees\demo-parallel-test on branch worktree-demo-parallel-test. Session is now back in D:\goProject\cc-tutorial.」目录和分支都留下。
- 退出丢弃改动：`ExitWorktree(action: "remove")` 返回原文：「Exited and removed worktree at D:\goProject\cc-tutorial\.claude\worktrees\demo-discard-test. Session is now back in D:\goProject\cc-tutorial.」之后 `git branch -D worktree-demo-discard-test` 报 `error: branch 'worktree-demo-discard-test' not found`——证实 `remove` 把目录和分支一并删干净，不留残枝。

工具 schema 里几条容易踩坑的机制，同一批实测中一并记录：

- `name`（新建）与 `path`（进入已存在的树）互斥，两者都不传则随机命名。
- 新树建在 `.claude/worktrees/` 下，新开一个分支；基准由 `worktree.baseRef` 控制：`fresh`（默认，基于 `origin/<默认分支>`）或 `head`（基于当前本地 HEAD）。实测里本地 HEAD 是 `2ff6eba`（实测当时的临时提交，后来被整理进正式提交，已不在任何分支上，仅作当时状态记录，无法按哈希复现），新树却基于 `origin/main` 的 `bc1ef00`——默认走的是 `fresh`，不是本地 HEAD，这个默认值容易让人以为新树会带上本地未推送的提交，实际不会。
- `ExitWorktree` 只认本会话用 `EnterWorktree` 建的树，对手动 `git worktree add` 建的树是 no-op。
- `remove` 遇到未提交文件或未合并提交会拒绝执行，除非显式传 `discard_changes: true`。

## 子代理与 Workflow 的 worktree 隔离

Agent 工具带 `isolation: "worktree"` 参数：子代理在独立 worktree 里干活，主工作区不动。未变更的 worktree 自动清理。

`实测 @ Claude Code v2.1.202`（2026-07-07，Windows 10）：让一个 Sonnet 子代理在 `isolation: "worktree"` 下创建文件——

- 子代理报告的写入路径：`D:\goProject\cc-tutorial\.claude\worktrees\agent-a9362c44c25d90dd2\scratch-test.txt`——文件写进了子代理自己的隔离树，不是主树根目录。
- 主工作区验证：实测用 `test -f scratch-test.txt` 检查（等价于 `Test-Path` 判定），结果为不存在，即 `Test-Path` 语义下的 `False`——主工作区确认没被子代理写入。
- worktree 留存情况：**有改动的隔离树被保留**，`git worktree list` 里能看到分支 `worktree-agent-a9362c44c25d90dd2`（基于 `bc1ef00`）；文档里「未变更自动清理」这条只对没有任何改动的树成立，一旦子代理写了文件，树就不会自动消失，需要手动清理。事后用 `git worktree remove --force .claude/worktrees/agent-a9362c44c25d90dd2` + `git branch -D worktree-agent-a9362c44c25d90dd2` 清理成功。
- 本次调用用量：35,168 subagent tokens，耗时 11.7 秒（含子代理实际执行任务的时间，不是单纯建树开销，两者无法从这一次调用中拆分）。

Workflow 中同理：`agent(prompt, {isolation: 'worktree'})`。**[Author's analysis]** 建树本身应该比子代理跑一次完整任务快得多，但本次实测没有单独测量纯建树耗时，不把「数百毫秒」这种具体数字当作已验证结论——只在并行改文件会冲突时开这个开销，改的是互不重叠的文件就没必要为每个 agent 多建一棵树。

## 多会话并行开发

`T1` 官方 common-workflows 文档给出的并行模式（[Claude Code docs](https://code.claude.com/docs/en/common-workflows)，Anthropic）：

- 场景定义原文：「Work on a feature in one terminal while Claude fixes a bug in another, without the edits colliding. Each worktree is a separate checkout on its own branch.」
- 命令入口是 CLI flag，不是会话内工具：`claude --worktree feature-auth`。
- 开第二个并行会话的方法：换一个名字，在第二个终端跑同一条命令。
- 清理、`.worktreeinclude`、非 git VCS 支持，原文指向专页 `/en/worktrees`。
- 想在一个屏幕监控多个并行会话而不是开多个终端，原文指向 `background agents`（`/en/agent-view`）。

本环境 v2.1.202 未验证 `claude --worktree` 这个 CLI flag——上面「原生入口」一节的实测走的是会话内 `EnterWorktree` 工具，是另一条路径，两者都能落到「一个 worktree 一个分支」的同一套机制上。

多终端各开一个 Claude 会话、各占一个 worktree、各做一个 feature。会话之间无共享状态，靠 git 汇合。

## 合并与清理

worktree 里的改动就是普通 git 提交：worktree 内 commit → 回主工作区 merge 或 rebase。

```bash
git worktree list          # 盘点
git worktree remove <path> # 清理已完成的树
```

冲突边界：两个 worktree 改同一文件，合并时照样冲突。Worktree 隔离的是工作目录，不是修改意图。

## 何时不用

**[Tutorial perspective]** 单任务、无并发文件修改时，worktree 是纯开销：多一份目录、多一次合并。默认单树干活，确认要并行再开树。
