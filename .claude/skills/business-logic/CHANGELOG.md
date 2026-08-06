# Changelog

> Maintained automatically by the auto-sync hooks. One entry per sync run.
> Edit history is pruned to the most recent `max_changelog_entries` (default 20).

<!-- Entry format (prepend NEWEST-FIRST: insert each new entry directly under
     this header so the most recent sync is at the top -- get_last_sync_hash
     in auto_sync.py relies on the first hash in the file being the latest):

## YYYY-MM-DD HH:MM
- **Commits**: <start_hash>..<end_hash> (N commits)
- **Domains**: domain1, domain2
- **Updated docs**:
  - path/to/file.md: what changed and why
-->

## 2026-08-07 00:00
- **Commits**: 3cf4d89 (working-tree; sub-doc pass 2 + fixes)
- **Domains**: video-scripts, examples, research
- **Updated docs**:
  - [SUB-DOC] video-scripts/subagent-and-sdk.md: SubAgent 三独立性 + Agent SDK(query / ClaudeSDKClient / @tool / 结构化输出,12 锚点)
  - [SUB-DOC] examples/asr-subtitle-architecture.md: asr/subtitle.py 双线程架构(4 线程 + 3 锁 + 3 队列,gen 代次机制,10 锚点)
  - video-scripts/overview.md、examples/overview.md: 深度文档节各 +1
  - index.md、coverage.md: sub-doc 计数 → video-scripts 3/3、examples 3/3
- **Fixes**: `research/00` 第 29/600 行 `docs\research\` → `research\`;`agent-patterns` 行号引用 → `iteration == 1` 符号。

## 2026-08-06 23:55
- **Commits**: 3cf4d89 (working-tree; sub-doc pass)
- **Domains**: video-scripts, examples
- **Updated docs**:
  - [SUB-DOC] video-scripts/agent-patterns.md: layer-01 Agent 模式深度(ReAct/Plan-Execute/Self-Reflection/Multi-Agent + Lilian Weng 三组件,14 锚点)
  - [SUB-DOC] video-scripts/hooks-and-headless.md: Hooks 七生命周期 + Headless 参数表 + ralph-loop 机制(16 锚点)
  - [SUB-DOC] examples/mcp-websearch-client.md: tools.py MCP `webSearchPrime` 客户端(5 跳 call chain,11 Key Symbols)
  - [SUB-DOC] examples/ralph-loop-stop-hook.md: stop-hook.py Ralph Loop 状态机(2 态 4 迁移 + promise 终止)
  - video-scripts/overview.md、examples/overview.md: 各加"深度文档(Sub-docs)"节
  - index.md、coverage.md: sub-doc 计数更新(video-scripts 2/2, examples 2/2)
- **Correction**: ralph-loop sub-doc 发现 examples overview 误称的 `STOP_PATTERN` 实际不存在(代码用字符串 `'"role":"assistant"'` 粗匹配),已在 coverage.md 记录。

## 2026-08-06 23:48
- **Commits**: 3cf4d89 (working-tree init; not a commit-range sync)
- **Domains**: video-scripts, examples, research, tooling
- **Updated docs**:
  - [INIT] video-scripts/overview.md: 13 文件(9 层 + README + 2 补充 + 官方插件)映射进内容树与子领域表
  - [INIT] examples/overview.md: 7 子项目、~22 源文件,含 Mermaid 关系图与 15 检索锚点
  - [INIT] research/overview.md: 17 份资料按 7 主题簇分组,T1–T4 分级,标出 6 个坑点
  - [INIT] tooling/overview.md: /commit-push、evidence-based、voice-and-tone、business-logic-researcher
  - index.md / coverage.md: 4 领域导航接入;_example-domain/ 已删
- **Note**: init 由 4 个并行 Haiku agent 驱动;init_plan.py suggest 对纯文档仓库返回 0,verify 门禁基于源码扩展名不适用,故未走脚本 verify。
