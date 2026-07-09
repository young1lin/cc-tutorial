---
name: business-logic
description: |
  Per-project business-logic knowledge base. Routes to the current project's
  `.claude/business-logic/` docs on demand and keeps them synced from git
  changes and conversation digests via git hooks (one LLM round per push).
  Triggers: "business logic", "domain overview", "how does <feature> work",
  "code flow", "call graph", "sync docs".
  Use `/business-logic` to browse, `/business-logic install` to set up a
  project, `/business-logic init` to build docs, `/business-logic sync` to
  update from recent commits, `/business-logic capture` to distill the
  current conversation.
---

# Business Logic Handbook (engine)

All knowledge data lives in the **current project**, never in this plugin:

```
<project-root>/.claude/business-logic/
├── index.md            navigation (start here)
├── CHANGELOG.md        sync log (last synced commit hash lives here)
├── coverage.md         doc coverage matrix
├── <unit>/overview.md  one directory per knowledge unit
├── scripts/            vendored engine scripts (project mode) + .env
└── state/              cursors, queue, locks, logs (git-ignored)
```

When asked about business logic in a project, read that project's
`.claude/business-logic/index.md` first, then only the relevant unit docs.
If the directory does not exist, say so and offer `/business-logic install`.

## Commands

| Command | Description |
|---------|-------------|
| `install [--global]` | Set up the current project (see Install procedure below). |
| `init` / `init <unit>` | Scan the codebase with parallel agents and generate unit docs into the data dir. |
| `sync [N]` | Sync the last N commits (default: all commits since the CHANGELOG hash). |
| `capture` | Distill THIS conversation's requirement background / design intent / pitfalls into the affected unit docs, right now, in-session. |
| `status` / `check` / `search <kw>` / `map [target]` / `explain <c>` / `api [unit]` / `diff` / `errors [unit]` | Same semantics as before, operating on the data dir. |

## Install procedure (`/business-logic install [--global]`)

Run from the target project root. `<plugin>` below is this skill's base
directory's parent parent (the plugin root).

1. Create the data dir: copy `<plugin>/data-skeleton/*` to
   `<project>/.claude/business-logic/` (do not overwrite existing files).
2. Create `<project>/.claude/business-logic/state/` (empty).
3. Engine placement:
   - **project mode (default):** copy `<plugin>/scripts/auto_sync.py`,
     `digest_transcripts.py`, `ensure_env_ignored.py`, `install_hooks.py`,
     `.env.example`, `requirements.txt` to
     `<project>/.claude/business-logic/scripts/`.
   - **`--global` mode:** copy the same six files to
     `~/.claude/business-logic/bin/` instead (one shared engine for all
     projects; re-run `install --global` after plugin updates to refresh it).
4. Copy `<plugin>/rules/explore-with-business-logic.md` to
   `<project>/.claude/rules/` (skip if present).
5. From the project root, run the hook installer with the engine you placed:
   - project mode: `python .claude/business-logic/scripts/install_hooks.py`
   - global mode: `python ~/.claude/business-logic/bin/install_hooks.py`
   (It installs `post-merge` + `pre-push`, removes any legacy `post-commit`,
   and runs the `.env` guard.)
6. Tell the user to create the `.env` where the engine loads it from:
   - project mode: copy `.env.example` to
     `<project>/.claude/business-logic/scripts/.env`.
   - global mode: copy `.env.example` to `~/.claude/business-logic/.env`
     (the engine's fallback location -- the engine dir root, NOT `bin/`).
   Fill `ANTHROPIC_BASE_URL` + `ANTHROPIC_AUTH_TOKEN`.
7. If the project wants team distribution, suggest adding to the repo's
   `.claude/settings.json`:
   `"enabledPlugins": {"business-logic@<marketplace-name>": true}`.

## Capture procedure (`/business-logic capture`)

Escape hatch for valuable conversations that will not end in a push.
In the CURRENT session: read `index.md` and the affected unit docs, extract
requirement background, design intent, and pitfalls from this conversation,
merge them into those docs, and append a CHANGELOG entry marked `[capture]`.
Never copy credentials, tokens, or pasted raw configs into docs.

## Required doc structure (per unit)

Every `overview.md` contains, in order: Quick Index / Business Overview /
API Entry Points / Core Flow (Mermaid) / Business Rules / Code Location /
Database / Potential Pitfalls / Related Docs — plus the anchors
`> last_verified_commit: <hash>` and `> source_packages:` at the top.

## Fallback strategy

1. Doc conflicts with code → code wins; note "docs may be stale".
2. Cannot locate a unit → read `index.md`, then the controller entry.
3. Docs missing → read source, then **backfill the unit doc**.
4. `check` reports stale → `search` to confirm blast radius, then `sync`.
