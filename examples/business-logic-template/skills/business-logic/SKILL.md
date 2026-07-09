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
| `doctor` | Run the deterministic anti-corruption gate on demand (size cap, secret scan, dead `source_packages`, structure, links, conflict markers, CHANGELOG rotation, UTF-8/BOM). Interactive sessions prompt per hard finding via `AskUserQuestion`; headless `claude -p` reports only. |
| `reconcile` | Manual decay cleanup: runs the deterministic scanner (`scripts/reconcile_scan.py`) then ONE serial LLM reconcile pass (`prompts/reconcile.md`) to dedup sections, resolve contradictions against code, and split oversized docs. Run periodically (e.g. before a release) to prevent knowledge-base rot. |

## Install procedure (`/business-logic install [--global]`)

Run from the target project root. `<plugin>` below is this skill's base
directory's parent parent (the plugin root).

1. Create the data dir: copy `<plugin>/data-skeleton/*` to
   `<project>/.claude/business-logic/` (do not overwrite existing files).
2. Create `<project>/.claude/business-logic/state/` (empty).
3. Engine placement:
   - **project mode (default):** copy `<plugin>/scripts/auto_sync.py`,
     `anticorruption.py`, `reconcile_scan.py`, `digest_transcripts.py`,
     `ensure_env_ignored.py`, `install_hooks.py`, `.env.example`,
     `requirements.txt` to `<project>/.claude/business-logic/scripts/`.
   - **`--global` mode:** copy the same eight files to
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

## Anti-corruption gate

Every per-push sync first runs a deterministic, zero-LLM gate
(`scripts/anticorruption.py`):

- **Hard** findings (a secret scanned in a committed doc, or a merge-conflict
  marker) abort the sync round and write a masked `state/audit.md`. Secrets are
  masked (`sk-***...***312`) before they ever touch disk; the raw value is
  never logged.
- **Soft** findings (oversize, broken links, dead `source_packages`, missing
  sections, BOM/encoding) are written to `state/audit.md`; the sync proceeds.
- Oversized docs are split in place during the same sync round. After repeated
  `BL_MAX_DOC_BYTES`-split attempts that fail to converge, the gate stops
  auto-splitting and nags in `state/audit.md`.

`/business-logic doctor` is the human face of the gate; it runs the checks on
demand and (in an interactive session) walks hard findings via `AskUserQuestion`.
Thresholds live in `.env` and all have defaults.

## Reconcile procedure (`/business-logic reconcile`)

Manual escape hatch to reverse accumulated decay (duplicate sections,
contradictions, bloat) from many digest merges. Run it periodically -- before a
release, or monthly -- to keep the knowledge base from rotting. It is ONE serial
pass; do not fan out parallel agents (reconciliation needs a global view, and
concurrent edits to the same doc conflict).

1. Run the deterministic scanner from the project root:
   - project mode: `python .claude/business-logic/scripts/reconcile_scan.py`
   - global mode: `python ~/.claude/business-logic/bin/reconcile_scan.py`

   It writes `state/reconcile-candidates.md` (duplicate groups, oversized docs,
   stale anchors).
2. Follow `prompts/reconcile.md` as one serial pass: read the candidates report,
   consolidate duplicates (keep the best wording, cross-reference the rest),
   resolve contradictions against the current code (code wins), split oversized
   docs into linked sub-docs, and append a `[reconcile]` CHANGELOG entry.
3. Delete `state/reconcile-candidates.md` once consumed.

Thresholds: stale-anchor cutoff via `BL_RECONCILE_STALE_COMMITS` (default 50);
oversized via `BL_MAX_DOC_BYTES`.

## Fallback strategy

1. Doc conflicts with code → code wins; note "docs may be stale".
2. Cannot locate a unit → read `index.md`, then the controller entry.
3. Docs missing → read source, then **backfill the unit doc**.
4. `check` reports stale → `search` to confirm blast radius, then `sync`.
