---
title: Claude Code Subagents
author: Anthropic
date: 2026-03-07
url: https://code.claude.com/docs/en/sub-agents
tier: T1
topics: [subagents, claude-code, agents, context-management]
---

# Claude Code Subagents

## Key Findings

`T1` Subagents are specialized AI assistants with their own context window, custom system prompt, tool access, and independent permissions.

`T1` Claude uses the `description` field to decide when to delegate tasks.

`T1` Project-level subagents live in `.claude/agents/`; user-level subagents live in `~/.claude/agents/`.

`T1` Markdown + YAML frontmatter is the native format. Required fields are `name` and `description`. Common optional fields include `tools`, `disallowedTools`, `model`, `skills`, `memory`, `hooks`, and `background`.

`T1` Subagents can preload skills with the `skills` field.

## Practical Implication

**[Author's analysis]** The `description` field is routing logic, not decoration. Weak descriptions produce weak delegation. Focused subagents with narrow prompts and narrow permissions are more predictable and safer than “do-everything” agents.
