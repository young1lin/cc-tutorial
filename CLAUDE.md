# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A comprehensive Claude Code tutorial project for video script production. Contains 9 layers of video scripts, example code, and research materials. The companion real-world case study project is at `C:\PythonProject\mybatis-boost`.

## Architecture

- `video-scripts/` - Video scripts (9 layers: theory → setup → basics → workflow → config → advanced → caveats → practice → supplement)
- `examples/` - Example code: HTTP API examples, official skills docs, recommended plugins
- `research/` - Completed research materials (Anthropic official, Boris Cherny, Andrew Ng, Addy Osmani)
- `.claude/commands/` - Custom slash commands (`/commit-push`)

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
Each episode follows a standard format:
1. Intro (30-60s) - what and why
2. Concept explanation (2-3min) - with diagrams/animations
3. Live demo (5-8min) - screen recording with code
4. Summary (1-2min) - key takeaways
5. Exercises (optional)

### When writing content
- Use Markdown format with code examples and real-world scenarios
- Follow the Evidence-Based Content Policy below for all factual claims and citations
- When citing experts, use the standard citation format defined in the policy
- Place example code in `examples/` with comments and usage instructions
- Mark all author interpretations with the `**[Author's analysis]**` or `**[Tutorial perspective]**` prefix

### Evidence-Based Content Policy

This policy ensures learners are never misled. Every factual claim must be traceable to a verifiable source, and opinions must be clearly distinguished from facts.

#### Evidence Tiers

| Tier | Name | Definition | Example |
|------|------|-----------|---------|
| **T1** | Official Doctrine | Primary source from the tool/platform vendor (official docs, changelogs, blog posts by the engineering team) | Anthropic docs stating Claude Code supports Plan Mode |
| **T2** | Expert Practitioner | Published content from a recognized practitioner with demonstrated expertise (blog posts, conference talks, courses, books) | Boris Cherny's best practices guide, Andrew Ng's course, Addy Osmani's workflow article |
| **T3** | Community Consensus | Widely repeated claim across multiple independent sources, but no single authoritative origin | "Most developers prefer dark mode IDEs" (cite 2+ sources) |
| **T4** | Author Interpretation | The tutorial author's own analysis, opinion, pedagogical framing, or prediction | "We believe starting with CLAUDE.md is the most effective onboarding approach" |

#### Citation Rules

**T1 citations** -- inline format:
```markdown
According to [Anthropic's official documentation](URL) (Author/Team, YYYY-MM), ...
```

**T2 citations** -- inline format:
```markdown
Boris Cherny recommends ... ([Best Practices Guide](research/01-claude-code-best-practices-anthropic-official.md), 2025-01)
```

**T3 citations** -- must reference at least two independent sources:
```markdown
Multiple sources report that ... ([Source A](URL), [Source B](URL))
```

**T4 markers** -- must be explicitly prefixed:
```markdown
**[Author's analysis]** Based on our testing across 5 projects, we found that ...
**[Tutorial perspective]** We recommend starting with Module 01 because ...
```

#### Superlative and Absolute Claims

Statements containing superlatives or absolutes ("best", "only", "always", "never", "fastest", "most powerful") **require T1 or T2 evidence**. If no such evidence exists, the claim must be:
1. Downgraded to T4 with an explicit marker, AND
2. Rewritten with hedging language ("in our experience", "based on available benchmarks", "among the tools we evaluated")

**Bad:** "Claude Code is the best AI coding tool available."
**Good:** "**[Tutorial perspective]** In our testing, Claude Code provided the most effective workflow for the use cases covered in this tutorial."

#### Predictive Claims

All predictions about future trends, adoption, or capabilities are **always T4**. They must:
1. Be marked with `**[Author's analysis]**`
2. Include a reasoning chain explaining the basis for the prediction

#### Conflicting Expert Opinions

When experts disagree, **present both positions with citations**. Do not silently adopt one side. Use a structure like:

```markdown
There are differing views on this approach:
- Boris Cherny argues for X ([source](URL))
- Addy Osmani suggests Y ([source](URL))

**[Tutorial perspective]** For the purposes of this tutorial, we follow X because ...
```

#### When Evidence Is Required vs. Optional

**Evidence REQUIRED (T1-T3 citation mandatory):**
- Performance or benchmark claims
- Feature existence or capability claims
- Direct quotes or paraphrases of specific people
- Historical events or timelines
- Statistics or numerical data
- Comparative claims ("X is faster/better/more popular than Y")

**T4 marker sufficient (no external citation needed):**
- Workflow recommendations and pedagogical choices
- Analogies and teaching metaphors
- Tutorial structure decisions
- Subjective experience reports (clearly marked)

#### Adding New Research Materials

When adding a new research source:
1. Save to `research/NN-descriptive-name.md` (increment NN from the last file)
2. Include YAML front matter at the top of the file:
   ```yaml
   ---
   title: "Source Title"
   author: "Author Name"
   date: "YYYY-MM-DD"
   url: "https://original-source-url"
   tier: T1 | T2 | T3
   topics: [topic1, topic2]
   ---
   ```
3. Update `research/00-research-summary.md` with a summary entry
4. Add the file to the Key Research Files list below

## Key Research Files

Each research file should include YAML front matter with `title`, `author`, `date`, `url`, `tier`, and `topics` fields (see policy above).

- `research/00-research-summary.md` - Full research summary (start here)
- `research/01-claude-code-best-practices-anthropic-official.md` - Boris Cherny best practices
- `research/02-plan-mode-guide-official.md` - Plan Mode official guide
- `research/03-andrew-ng-course-outline.md` - Andrew Ng course outline
- `research/04-addy-osmani-2026-workflow.md` - Addy Osmani 2026 workflow
- `research/05-boris-cherny-workflow-x-thread.md` - Boris Cherny X thread

## Custom Commands

- `/commit-push` - Stage, commit (conventional commits format), and push. Auto-excludes debug files, binaries, logs, temp files.
