# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A comprehensive Claude Code tutorial project for video script production. Contains 10 modules (39+ chapters) of tutorial content, video scripts, example code, and research materials. The companion real-world case study project is at `C:\PythonProject\mybatis-boost`.

## Architecture

- `docs/tutorial/module-{01..11}-*/chapter-*.md` - Tutorial chapters (primary content)
- `docs/video-scripts/` - Video scripts per module; use `episode-outline-template.md` as the template
- `docs/examples/` - Example code: HTTP API examples, official skills docs, recommended plugins
- `docs/research/` - Completed research materials (Anthropic official, Boris Cherny, Andrew Ng, Addy Osmani)
- `.claude/commands/` - Custom slash commands (`/commit-push`, `/setup`)

## Vector Knowledge Base

Located at `vector-kb-mcp/`. Uses `paraphrase-multilingual-MiniLM-L12-v2` (384-dim). ~850 MB memory footprint.

```bash
# CLI usage
cd vector-kb-mcp
uv run python -m src.cli add "text" "source"
uv run python -m src.cli search "query"

# MCP server
uv run python -m src.cli mcp
```

In Python, always use the context manager to ensure resource cleanup:
```python
with VectorStore() as store:
    store.add_text("content", source="source")
    results = store.search("query")
```

Do NOT create VectorStore instances in a loop. GPU memory auto-cleans but system memory retains ~350 MB model cache.

## Content Authoring Rules

### Tutorial Chapters
Each chapter must include: learning objectives, prerequisites, core concepts, hands-on examples, common pitfalls, further reading, and a video script section.

### Video Scripts
Follow `docs/video-scripts/episode-outline-template.md`:
1. Intro (30-60s) - what and why
2. Concept explanation (2-3min) - with diagrams/animations
3. Live demo (5-8min) - screen recording with code
4. Summary (1-2min) - key takeaways
5. Exercises (optional)

### When writing content
- Use Markdown format with code examples and real-world scenarios
- When citing experts, attribute the source (author, document) and link to research materials in `docs/research/`
- Place example code in `docs/examples/` with comments and usage instructions

## Key Research Files

- `docs/research/00-research-summary.md` - Full research summary (start here)
- `docs/research/01-claude-code-best-practices-anthropic-official.md` - Boris Cherny best practices
- `docs/research/02-plan-mode-guide-official.md` - Plan Mode official guide
- `docs/research/03-andrew-ng-course-outline.md` - Andrew Ng course outline
- `docs/research/04-addy-osmani-2026-workflow.md` - Addy Osmani 2026 workflow
- `docs/research/05-boris-cherny-workflow-x-thread.md` - Boris Cherny X thread

## Custom Commands

- `/commit-push` - Stage, commit (conventional commits format), and push. Auto-excludes debug files, binaries, logs, temp files.
- `/setup` - Install claude-token-monitor statusline plugin from GitHub releases.
