# Documentation Coverage

> last_updated: 2026-08-07
> last_sync_commit: 3cf4d89

One row per domain. The first three columns are the human record — what shape
the domain is in and what last changed in it. The last three are machine-filled
by `.scripts/init_plan.py verify`.

## Domain Coverage

| Domain | Docs | last_verified_commit | Status | Files | Sub-docs | Coverage |
|--------|------|---------------------|--------|-------|----------|----------|
| video-scripts | 4 | 3cf4d89 | init + 3 sub-docs(agent-patterns, hooks-and-headless, subagent-and-sdk) | 13 | 3 / 3 | ~100% |
| examples | 4 | 3cf4d89 | init + 3 sub-docs(mcp-websearch-client, ralph-loop-stop-hook, asr-subtitle-architecture) | ~22 | 3 / 3 | ~95% |
| research | 1 | 3cf4d89 | Initial init (Haiku) — 17 份资料按 7 主题簇分组 | 17 | 0 / 0 | 100% |
| tooling | 1 | 3cf4d89 | Initial init (Haiku) — commit-push / 两条规则 / researcher agent | 4 | 0 / 0 | 100% |

`Status` 是一句话,不是标志:说最近一次 sync 改了什么、为什么。

**Corrections are first-class.** 当 sync 发现文档断言有误,在 `Status` 里明说,而不是默默改写。已记录:`ralph-loop-stop-hook.md` 纠正 examples overview 误称的 `STOP_PATTERN`(实际不存在,用字符串粗匹配);`research/00` 第 29/600 行 `docs\research\` 路径已修正为 `research\`。

## Notes

- **本仓库是文档仓库**(绝大多数为 `.md`)。`init_plan.py verify` 基于源码扩展名(`.py/.java/...`),对本仓库不适用——`Files` / `Coverage` 为人工估算,非脚本产出。
- `Sub-docs`:video-scripts 3/3、examples 3/3 已拆(两轮 Haiku 共产出 6 个 sub-doc);research / tooling 体量小,overview 足够。layer-06 的主要主题(SubAgent / Hooks / Headless / SDK)均已覆盖;剩 plugins / LSP 等边缘主题可视情况再拆。
- `Docs` 含 overview + sub-docs;`Files` 为该领域被 overview 命名的源文件数(估算)。
- 刷新机器列对文档仓库无意义;`/business-logic check` 仍可用于人工核对。
