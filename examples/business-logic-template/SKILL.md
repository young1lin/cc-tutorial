---
name: business-logic
description: |
  Use when asked to understand business logic, locate a feature, explain how
  something works, trace a call chain, find the code behind a concept, or bring
  the knowledge base up to date with recent code changes.
  Triggers: "business logic", "domain overview", "how does <feature> work",
  "where is <feature> implemented", "code flow", "call graph", "call chain",
  "which service handles", "error codes", "API entry points", "sync docs",
  "docs out of date", "stale docs".
---

# Business Logic Handbook

A living, domain-organized knowledge base for this project. **When exploring the
project, consult these docs first rather than blindly scanning the codebase.**

Everything lives in one project-level folder that can be copied between repos:

```
<project>/.claude/skills/business-logic/
├── SKILL.md          this file
├── index.md          navigation -- start here
├── coverage.md       doc coverage matrix
├── CHANGELOG.md      human-facing sync log
├── <domain>/         one directory per business domain: overview.md (the map)
│                     plus one doc per sub-domain (where the depth lives)
├── .scripts/         engine (auto-sync worker, init planner + depth gate, hooks)
├── .sync/            sync workflow reference
├── .skeleton/        templates expanded on install
├── .state/           cursors, job queue, completion records, locks (git-ignored)
└── .tmp/             scratch space (git-ignored)
```

## Naming rule: the dot namespace is reserved

**Directories starting with `.` belong to the skill. Everything else is user
content.** A business domain called `sync`, `state`, `scripts`, or `rules` is
perfectly legitimate and must not collide with skill internals — the dot prefix
is what keeps those two namespaces apart.

**`init` and `sync` must never create a directory whose name starts with `.`,**
and must never write domain docs into `.scripts/`, `.sync/`, `.skeleton/`,
`.state/`, or `.tmp/`. Domain directories are always plain names.

The secret `.env` is the one exception that lives *outside* this folder, at
`<project>/<cli>/.env` (`.claude/.env`, `.agents/.env`, ...), so that copying
the skill directory never carries credentials with it.

## Running the scripts

Every script under `.scripts/` is PEP 723 self-contained (inline `# /// script`
metadata, stdlib-only on the CLI-runner path). **Always prefer uv**; it needs no
pre-created environment and no install step:

```
uv run --script .claude/skills/business-logic/.scripts/<script>.py [args]
```

If `uv` is not on PATH, `python <same path> [args]` behaves identically. Every
example below uses the uv form; substitute `python` only as a fallback.

## Commands

| Command | Description |
|---------|-------------|
| `install` | Set up this project: expand the skeleton, install git hooks, register the explore-first memory rule (CLAUDE.md / AGENTS.md). |
| `init` | Full initialization: plan the domains, then generate each domain's overview + sub-domain docs. |
| `init <domain>` | Deep single-domain initialization (for a new domain or after a large refactor). |
| `sync` | Sync the commit range recorded in the queue (hooks) or since the last synced head. |
| `capture` | Distill THIS conversation into the affected domain docs, now, without waiting for a push. |
| `status` | Current state: last synced commit, doc coverage. |
| `check` | Verify docs against code, flag stale content. |
| `search <keyword>` | Full-text search across all docs. |
| `map [target]` | Call-relation graph (target = domain / class / method). |
| `explain <concept>` | Deep explanation of a concept, linked to code and flows. |
| `api [domain]` | List API entry points for a domain. |
| `diff` | Show code changes since the last sync (read-only). |
| `errors [domain]` | List error codes for a domain. |

### Examples

```
/business-logic init                     # first-time full initialization
/business-logic init payments            # deep single-domain init
/business-logic sync                     # sync the pending commit range
/business-logic sync --staged            # sync staged (uncommitted) changes
/business-logic sync --dry-run           # preview proposals, write nothing
/business-logic status                   # coverage state
/business-logic explain liquidation      # deep explanation of a concept
/business-logic map OrderService         # call graph centered on a class
/business-logic search "stop loss"       # full-text search
/business-logic check                    # consistency check against code
/business-logic api order                # API endpoints of the order domain
/business-logic errors order             # error codes of the order domain
```

---

## Command: install

Run from the project root.

1. Copy `.skeleton/*` into the skill directory root (`index.md`, `coverage.md`,
   `CHANGELOG.md`, `_example-domain/`). Never overwrite existing files.
2. Create `.state/` and `.tmp/` (empty).
3. Install the git hooks — prefer uv, fall back to python:
   ```
   uv run --script .claude/skills/business-logic/.scripts/install_hooks.py
   python .claude/skills/business-logic/.scripts/install_hooks.py   # fallback
   ```
   This installs `post-merge` + `pre-push`, removes any legacy `post-commit`,
   appends an "explore via this skill first" block to `CLAUDE.md` (Claude Code)
   or `AGENTS.md` (opencode / codex) -- reusing an existing file if present,
   otherwise creating one at the project root -- and runs the `.env` guard.
 4. Configure `.env` (the credentials file) **interactively** with `AskUserQuestion`.
    Write the result to `<cli>/.env` (`.claude/.env` or `.agents/.env`). Transcript
    source (what you code with) and sync LLM (what runs the sync) are TWO
    INDEPENDENT choices -- ask them together, then branch.

    **Ask #1 — two parallel questions:**

    *Q1 "Which CLI do you code with?"* (→ `TRANSCRIPT_SOURCE`):
    Claude Code / Codex / opencode / Mixed-use (all)

    *Q2 "What runs the sync?"* (→ runner + provider):
    - Reuse a CLI subscription (no API key) — claude / codex / opencode
    - Zhipu Coding Plan (GLM API)
    - DeepSeek (API)
    - Tongyi Qianwen / DashScope (API)
    - OpenRouter (API)
    - Anthropic native (API)
    - Custom (you supply base_url + model)

    **Branch on Q2:**

    *A. Subscription* — pick which CLI's subscription (if Q1 = Mixed, ask which:
    claude / codex / opencode). Then **ask "Need an HTTP proxy?"** (subscriptions
    reach overseas; if yes, collect the proxy URL → `HTTPS_PROXY`/`HTTP_PROXY`).
    No API key, no extra packages.

    *B. Domestic API* (Zhipu / DeepSeek / Qianwen) — `SYNC_RUNNER=api`,
    `SYNC_BACKEND=openai`. No proxy question.

    *C. Overseas API* (OpenRouter / Anthropic) — `SYNC_RUNNER=api`,
    `SYNC_BACKEND=openai` (or `anthropic`). Leave the proxy lines as commented
    placeholders in the preset (the user uncomments if needed).

    *D. Custom* — collect base_url + model. No proxy question.

    **Ask #2 — model + reasoning effort (EVERY path; the user can override the
    default, since models update over time):** offer the preset's default + a
    custom option to type their own. Examples: Zhipu→`glm-5.2` (`REASONING_EFFORT=low`),
    DeepSeek→`deepseek-v4-flash` (`REASONING_EFFORT=high`),
    opencode→`zhipuai-coding-plan/glm-5.2` (`OPENCODE_VARIANT=low`), codex→
    `gpt-5.6-luna` (`CODEX_REASONING=low`).

    **Ask #3 — API key** (only paths B/C/D): let the user type it via the custom
    answer. If they decline, leave the `your-...-key` placeholder and tell them
    which line to fill.

    **Dependencies hint (end of install):** tell the user exactly what to install
    for their chosen path -- NOT everything:
    - Subscription / opencode-native → nothing (`pip install` not needed).
    - API path → `pip install "pydantic-ai-slim[openai]"` (or `[anthropic]`).
    - Legacy `claude-sdk` → `pip install claude-agent-sdk`.

    Pick the closest preset from `examples/`, copy to `<cli>/.env`, then overwrite
    the model / key / proxy lines with the user's answers.

---

## Command: init

Full initialization. **A domain is a DIRECTORY OF DOCS, never a single file.**

A domain directory holding only `overview.md` is a failed init. One file cannot
carry a 500-file domain, so it degenerates into a symbol inventory: broad, flat,
and useless to search -- the user greps a real term (a class, a table, an error
code, a config key) and gets nothing back. `overview.md` is a MAP. The knowledge
lives in the sub-domain docs beside it.

```
<domain>/
├── overview.md          the map: quick index, sub-domain table, cross-domain links
├── <sub-domain>.md      one per sub-domain -- where the actual depth lives
├── <sub-domain>.md
└── ...
```

### Step 1 -- plan (script, no agents, no LLM)

```
uv run --script .claude/skills/business-logic/.scripts/init_plan.py suggest              # candidate domains, ranked by size + churn
uv run --script .claude/skills/business-logic/.scripts/init_plan.py plan --spec-file <spec>   # lock the list -> .state/init-plan.json
uv run --script .claude/skills/business-logic/.scripts/init_plan.py progress             # domains done / remaining
```

`plan` records, per domain, its **file ledger** (every source file the domain
owns), its churn, and `min_subdocs`. That file is the progress ledger and makes
init resumable: an interrupted run picks up the pending domains instead of
starting over.

Show the user the plan table before dispatching anything: domains, files each,
sub-docs required.

### Step 2 -- cut each domain into sub-domains

Cut along the code's own seams, never arbitrarily:

| Seam | Example |
|------|---------|
| subpackage / module with its own entry points | `service/order/pricing/` |
| a distinct flow | order placement vs. order cancellation |
| a distinct integration | a payment gateway, an MQ consumer |
| a distinct data cluster | one table family and everything that writes it |
| a distinct policy / rule engine | risk checks, approval rules |

**Minimum `ceil(source_files / 40)` sub-domain docs per domain, and at least 2
once a domain passes 25 source files.** Under 25 files, `overview.md` alone is
fine -- do not manufacture ceremony for a small domain. A domain that would need
more than ~12 sub-docs is really two domains: split it.

### Step 3 -- deep pass, 2-3 agents at a time

**One agent per DOMAIN** (not per sub-domain): one context holds the whole
domain, so cross-cutting flows stay coherent and the sub-domain cuts do not
overlap. **Run only 2-3 agents at a time** -- a wide fan-out dilutes each
agent's context, which is what produces flat inventory docs. Hand each agent the
file ledger from the plan, not just a package name.

After every wave:

```
uv run --script .claude/skills/business-logic/.scripts/init_plan.py verify     # depth gate; marks each domain done / failed
uv run --script .claude/skills/business-logic/.scripts/init_plan.py progress   # the numbers to report to the user
```

Report to the user after each wave: `N/M domains done, K remaining, S sub-docs
written, file coverage X%`. Re-dispatch failed domains with the verifier's
reasons pasted into the prompt.

### Every agent must

1. **Read every file in its ledger.** The files, not the package listing.
2. Trace the full call chain from each entry point inward and record it as an
   indented tree (symbol, file, role per hop) — then additionally call out the
   **decision points**: where it branches, retries, locks, or fails silently.
3. Trace the data flow: input -> processing -> DB/cache -> return value.
4. Identify shared state (multiple methods touching the same table or cache key).
5. Emit a Mermaid flow diagram per sub-domain, plus the domain's call graph.
6. Name real, searchable things: class, method, table, column, error code, config
   key, event, endpoint path. **A doc the user cannot grep is worthless.**

### Required structure: `<domain>/overview.md`

`overview.md` stays a COMPLETE domain doc -- it keeps every section below -- and
gains a `Sub-domains` table that routes to the depth. Do not gut an existing
overview when adding sub-docs: the overview answers "what is this domain", the
sub-docs answer "how does this part work".

```markdown
# <Domain> Overview

> last_verified_commit: <hash>
> source_packages:
> - <package path>            a path, a package, or `package (ClassPrefix*)`

## Quick Index
- Core entry:
- Core service:
- Core tables:
- Core events:
- Most-changed spots:
- High-risk spots:

## Business Overview   one sentence, then 2-3 lines of context

## Sub-domains         REQUIRED once the domain passes 25 source files
| Doc | Scope | Owns |
|-----|-------|------|
| [pricing](pricing.md) | `service/order/pricing/` (18 files) | fee calculation, discount rules |

## API Entry Points    the full list; rows link to the sub-doc detailing them
## Core Flow           Mermaid: the domain's main path, linking into sub-docs
## Business Rules      domain-wide rules; per-flow detail lives in the sub-docs
## Code Location       Class.method (never line numbers -- they rot)
## Database            tables and key fields involved
## Potential Pitfalls  concurrency, boundary conditions, common mistakes
## Related Docs        links to other domain docs
```

### Sub-doc types

Long-running knowledge bases converge on a small vocabulary. Name sub-docs after
what they are, so a reader can guess the filename:

| Type | Filename | Holds |
|------|----------|-------|
| flow | `open-flow.md`, `close-position.md` | one traced end-to-end flow |
| api | `query-api.md`, `position-query-api.md` | an endpoint family + params |
| schema | `database-schema.md` | tables, fields, relations |
| job | `stats-job.md` | scheduled work and its state |
| integration | `okmax/overview.md`, `notify-system.md` | a third-party or cross-system link |
| record | `changelog-archive.md`, `sync-log.md` | dated history (see below) |

A sub-domain that outgrows one file becomes a directory with its own
`overview.md` (`trading/binary-option/overview.md`) -- the same rule, one level
down.

**Record docs do not count as decomposition.** Fourteen changelog files do not
make a domain documented; the depth gate excludes them from the sub-doc count.

### Required structure: `<domain>/<sub-domain>.md` (the depth)

```markdown
# <Domain> / <Sub-domain>

> last_verified_commit: <hash>
> source_files: <N> files under <path>

## Responsibility   one sentence, then what this sub-domain does NOT cover
## Entry Points     API paths / public methods / consumed events -> handler
## Core Flow        Mermaid sequenceDiagram / flowchart of THIS sub-domain
## Call Chain       indented tree, one line per hop: `Class.method()` -- file --
                    what it does. Indentation shows nesting and branching at a
                    glance. Then call out the hops that branch, retry, lock or
                    fail, and why.
## Business Rules   validation conditions, config keys, error codes, thresholds
## Key Symbols      the searchable index -- one row per significant class/method
| Symbol | File | Role |
## Database         tables, key fields, cache keys touched here
## Pitfalls         concurrency, boundary conditions, common mistakes
## Related          sibling sub-domains + other domains
```

### Depth rules -- a doc that breaks any of these is superficial

These are what `.scripts/init_plan.py verify` measures, so they are checkable
rather than aspirational:

1. **Every file in the ledger is accounted for** -- named in a `Key Symbols` row,
   in a call chain, or explicitly listed as trivial in the domain's overview.
   The gate requires 70% of the domain's source files to appear by name.
2. **Two of three depth signals per doc**: a traced flow (Mermaid or an
   `A -> B -> C` chain), a table, and at least 8 distinct concrete identifiers.
   Prose with no literals is not searchable, and one fake diagram is not depth.
3. **Never line numbers** (`Foo.java:123`). They rot on the next edit; use symbols.
4. **No `(planned)` / `TODO` / `TBD` links or sections.** An unwritten doc is not
   a link, it is a missing doc: write it now or drop the reference.
5. **Every sub-doc is reachable** from `overview.md`, `index.md`, or the
   navigation. An unlinked doc is invisible.
6. **Concrete literals over prose**: real table names, real error codes, real
   config keys, real endpoint paths. That is what makes `search` work.

Write the docs in whatever language the team reads -- the gate measures
structure and literals, never English section names.

### Do not hand-write what a graph derives

This skill holds what a parser CANNOT extract: requirement background, design
trade-offs, historical pitfalls, "when the numbers disagree, read this one
first". Structure — who calls whom, what imports what, where a symbol lives —
is derivable from the code, and a derived index is always fresher than prose.

**This skill has no dependency on any indexer and never will** (the whole point
is that the directory copies into any repo with no third-party setup). But the
division of labour holds whether or not one is installed:

| Content | Where it belongs |
|---------|------------------|
| whole-repo lookups: "who calls X", import edges, every symbol's location | a derived index (tree-sitter / LSP / MCP code-graph tool), or read from source on demand |
| **the domain's main chain, curated** — entry point inward, the hops that carry the business | **these docs** (`Call Chain`) |
| WHY a hop exists, what breaks there, which branch is the trap | **these docs** |
| business rules spanning several classes, tables and config keys | **these docs** — a graph shows unrelated nodes; only prose makes it one thing |
| searchable literals: table names, error codes, config keys, endpoints | **these docs** (`Key Symbols`) |

The distinction is **curation, not brevity**. A graph can emit every edge it
finds; it cannot tell you which six hops out of two hundred are the business
flow, which one silently falls back to a default, or which one must not be
reordered. Write the chain out as a tree so a reader follows it at a glance —
just do not pad it with trivial getters, DTO mapping and framework plumbing that
an index resolves better.

**If the project has a code-graph / index tool available** (an MCP indexer, an
LSP, a `codegraph`-style local graph), query it FIRST for structural questions
and spend the analysis budget on the why. If it does not, read the source as
usual — nothing here requires it.

### After init

1. Update `index.md` navigation: every domain AND its sub-docs.
2. Install the git hooks (see `install` above).
3. Initialize `CHANGELOG.md`.
4. Fill in `coverage.md`: one row per domain, including its sub-doc count.
5. Delete `_example-domain/` once real domains exist.
6. Run `verify` one final time and report the numbers to the user.

---

## Command: sync

Sync the commits in scope into the docs. See [.sync/SYNC-WORKFLOW.md](.sync/SYNC-WORKFLOW.md)
for the file-to-domain mapping table and the full proposal format.

**The sync scope is an EXPLICIT commit range `base..head`.** The automated
worker receives it in its prompt; the engine captures it per trigger source
(post-merge: `ORIG_HEAD..HEAD`; pre-push: `@{u}..HEAD`; manual:
last-completed-head..HEAD). NEVER use `HEAD~N` -- history has merge commits,
so `HEAD~N` does not match the range.

The single source of truth for "what has been synced" is
`.state/complete.jsonl` (the last record's head), NOT CHANGELOG.md --
CHANGELOG.md is a human-facing log. On first run after an upgrade from an
older engine, the CHANGELOG hash is used once as the base; afterwards
complete.jsonl takes over.

### Procedure

1. Resolve the range `base..head`; run `git log --oneline base..head` and
   `git diff base..head --stat`.
2. **Detect new domains** (see below).
3. Map changed files to domains via the mapping table in `.sync/SYNC-WORKFLOW.md`.
4. For each changed file, analyze in depth:
   - read the diff plus surrounding context (~50 lines each side);
   - trace the call chain both ways (callers and callees);
   - check whether related config/constants/enums changed.
5. Compare against the existing docs and generate diff-style proposals.
6. Apply the changes — **in automated mode (git hooks) write directly; in
   interactive mode confirm first**, unless `--dry-run`.
7. Update the call-relation graphs of affected domains.
8. Prepend an entry to `CHANGELOG.md` (newest first; keep the most recent
   `max_changelog_entries`).
9. Update the `last_verified_commit` anchor of every touched doc.

### New-domain / new-sub-domain detection

**Trigger if any of these hold:**

1. ≥3 new files under the same `service/` subpackage that has no doc yet.
2. A new controller class with no corresponding domain doc.
3. A new data-access mapping file whose table appears in no database section.
4. New files make up >50% of the diff.

**Sub-domain first.** Most triggers land inside an EXISTING domain: the answer is
a new `<domain>/<sub-domain>.md` plus a row in that domain's `## Sub-domains`
table — not a new top-level domain, and never a paragraph appended to
`overview.md`. Create a new domain only when the code belongs to no existing
domain's scan paths.

**On trigger, run the deep analysis immediately — do not ask:**

1. Trace the full chain from the new controller inward (controller → service →
   data access → DB).
2. Grep for callers and callees of the new services.
3. Identify shared state (other classes touching the same table or cache key).
4. Generate `overview.md` following the required structure above.
5. If new tables are involved, generate the database section alongside.
6. Add the new domain to `index.md` navigation.
7. Add a row to `coverage.md`.
8. Mark the CHANGELOG entry `[NEW DOMAIN]`.

Remember the naming rule: a new domain directory never starts with `.`.

### Parameters

- `--staged` — sync staged (uncommitted) changes via `git diff --staged`.
- `--dry-run` — print proposals only; write nothing.

### Engine-side bookkeeping (invisible to the model)

The engine (`auto_sync.py`) keeps sync state itself; the model never does:

- `SYNC_RUNNER` (in `.env`) picks WHO runs the sync: `auto` (default — prefer an
  installed CLI: `claude` / `codex` / `opencode`, each run headless and reusing
  your existing subscription or configured provider, so it costs no extra API
  tokens), or `api` (direct API call). CLI runners are preferred because
  subscriptions are bound to the CLI and can't be invoked via raw API.
- `SYNC_BACKEND` (only when `SYNC_RUNNER=api`, or auto finds no CLI) picks the
  LLM provider: `openai` (ChatCompletion — glm/deepseek/qwen and any compatible
  relay), `anthropic` (Messages), or `claude-sdk` (legacy). The first two use
  PydanticAI with six in-process tools (read/write/edit/glob/grep/bash); writes
  are sandboxed to the skill data dir. Proxy: `HTTPS_PROXY`/`HTTP_PROXY`/`NO_PROXY`.
- `.state/queue.jsonl` — pending job records (explicit `base..head` per trigger),
  hash-deduped at commit granularity so the same commit is never synced twice.
- `.state/complete.jsonl` — append-only completion records; the last record's
  `head` is the source of truth for the next sync's base. Written ONLY on
  success, so a failed sync retries from the same base.
- `auto_sync.py state` — JSON: last_head / head / lock_busy / pending.
- `auto_sync.py record --base B --head H --from manual-inline` — for an
  interactive manual sync: the model edits the docs itself, then records the
  completion so bookkeeping always lives in one place.

After every sync run the engine also enforces a per-doc size budget
(`MAX_DOC_BYTES`, default 50KB): oversized domain docs are split into focused
sub-docs by dedicated worker calls, regardless of whether the sync itself
succeeded.

### CHANGELOG format

```markdown
## YYYY-MM-DD HH:MM
- **Commits**: <start_hash>..<end_hash> (N commits)
- **Domains**: domain1, domain2
- **Updated docs**:
  - path/to/file.md: what changed and why
```

### Per-domain changelog rotation

A domain that changes constantly outgrows the shared `CHANGELOG.md`. When its
history starts crowding out the knowledge, move it into the domain:

- `<domain>/changelog-recent.md` -- the current window.
- `<domain>/changelog-archive.md` -- older entries, rotated by date range
  (`changelog-2026-06-30-to-07-03.md` when one archive gets large).

Keep the top-level `CHANGELOG.md` as the cross-domain log. Record docs are
history, **not** documentation: they never count toward a domain's sub-doc
requirement, and the depth gate excludes them by filename.

---

## Command: capture

Escape hatch for a valuable conversation that will not end in a push. In the
CURRENT session: read `index.md` and the affected domain docs, extract
requirement background, design intent, and pitfalls from this conversation,
merge them into those docs, and prepend a CHANGELOG entry marked `[capture]`.

**Never copy credentials, tokens, or pasted raw configs into the docs.** They
are committed and reviewed like code.

---

## Command: status

Report both halves: sync state and doc depth.

```
uv run --script .claude/skills/business-logic/.scripts/auto_sync.py state       # sync cursor
uv run --script .claude/skills/business-logic/.scripts/init_plan.py progress    # depth + coverage
```

```markdown
## Sync Status
- last_head: b79b30a (source of truth: .state/complete.jsonl)
- unsynced_commits: 3

## Doc Status
- domains: 8 total | 6 done | 2 remaining
- sub-docs: 31 written / 34 required
- file coverage: 78% of source files named in docs
- thin domains: payments (2/5 sub-docs, 41% coverage)
```

`init_plan.py progress` reads `.state/init-plan.json`; if no plan exists yet,
say so and point at `init`.

---

## Command: check

Verify the docs against the code in depth.

```markdown
## Stale Report

### Missing Classes
- file: payments/overview.md
  issue: referenced `FooService` no longer exists
  suggestion: remove, or replace with `PaymentService`

### Outdated Enums
- file: order/overview.md
  issue: `OrderType.XXX` description disagrees with the code
  suggestion: update to the current definition

### Up-to-date
- inventory/overview.md
```

---

## Command: search <keyword>

Full-text search across `**/*.md` in this skill directory (skipping the dot
directories). Return matching file paths, section headings, and a context
snippet. Rank by relevance: title match > heading match > body match.

---

## Command: map [target]

Emit a Mermaid call-relation graph:

- no target — cross-domain relation overview;
- a domain name — internal call graph of that domain;
- a class name — graph centered on that class;
- a method name — the full call chain of that method.

Output `graph TD` or `sequenceDiagram`.

---

## Command: explain <concept>

1. Search the docs to find the relevant domain.
2. Read that domain's docs.
3. If the docs are not detailed enough, read the source to fill the gap.
4. Answer with: overview + flow + code location + related domains.
5. **Backfill whatever you learned from source into the domain doc.**

---

## Command: api [domain]

```markdown
## APIs: order
| Method | Path | Controller | Service | Note |
|--------|------|------------|---------|------|
| POST | /v1/order/create | OrderCtl | OrderService.create | create an order |
```

---

## Command: diff

1. Read `.state/complete.jsonl` for the last synced head (fallback: the
   `hash..` in CHANGELOG.md on the first run after an upgrade).
2. `git diff <head>..HEAD --stat`.
3. Map changed files to domains.
4. Print the list of docs that need updating. **Change nothing.**

---

## Command: errors [domain]

```markdown
## Errors: order
| Code | Meaning | Trigger |
|------|---------|---------|
| INSUFFICIENT_BALANCE | available balance too low | placing an order without enough margin |
```

---

## Fallback Strategy

When the docs are incomplete or disagree with the code:

1. **Docs conflict with code → code wins.** Say explicitly that the docs may be
   stale.
2. **Cannot locate a domain →** read `index.md`, then the controller entry point.
3. **Crosses several domains →** read the most core domain first, then the
   supporting infrastructure.
4. **Docs missing → read the source**, following package paths inward from the
   controller layer.
5. **`check` reports stale →** run `search` to confirm the blast radius, then
   decide whether a `sync` is warranted.
6. **Explored code and found new logic → backfill it into the domain doc.** The
   knowledge base only stays useful if every exploration feeds back into it.
