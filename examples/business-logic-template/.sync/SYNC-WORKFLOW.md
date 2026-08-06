# Sync Workflow

This document describes the workflow for syncing git code changes into the
business-logic documentation. It is the reference the auto-sync agent follows
when `/business-logic sync` runs.

## Usage

```bash
/business-logic sync              # sync the pending commit range
/business-logic sync --staged     # sync staged (uncommitted) changes
/business-logic sync --dry-run    # preview without modifying files
```

The sync scope is an EXPLICIT commit range `base..head`: the automated worker
receives it in its prompt; for a manual inline sync, `base` = the last
completed head from `.state/complete.jsonl` and `head` = HEAD. Run:

```bash
git log  --oneline base..head    # commits in scope
git diff base..head --stat       # file summary
git diff base..head              # detailed changes
```

NEVER use `HEAD~N` -- history has merge commits, so `HEAD~N` does not match the
range. Always use the explicit `base..head`.

The single source of truth for "what has been synced" is `.state/complete.jsonl`
(the last record's head), NOT CHANGELOG.md -- CHANGELOG.md is a human-facing log.
The engine deduplicates at commit-hash granularity, so a commit is never synced
twice even if a trigger fires repeatedly (e.g. several pushes in a row).

For machine-readable sync state (last_head / lock_busy / pending):

```bash
uv run --script .claude/skills/business-logic/.scripts/auto_sync.py state
```

---

## File-to-Doc Mapping

Define your own mapping here. For each file pattern in your codebase, record the
business domain it belongs to and **the sub-domain doc that covers it** -- not
just the domain. Routing everything to `overview.md` is what turns a knowledge
base back into a flat inventory.

| File Pattern | Business Domain | Target Doc |
|--------------|-----------------|-----------|
| `service/yourdomain/pricing/*.java` | Your Domain | `your-domain/pricing.md` |
| `service/yourdomain/settlement/*.java` | Your Domain | `your-domain/settlement.md` |
| `*Mapper.xml` | Your Domain | the sub-doc owning that table (`## Database`) |
| `*Ctl.java` / `*Controller.java` | Your Domain | the sub-doc owning that endpoint |

Keep this table in sync with how you organize docs on disk.

**A changed file that maps to no sub-doc is a signal, not a rounding error:**
either it belongs to an existing sub-domain (add it there), or it is a NEW
sub-domain -- create `<domain>/<sub-domain>.md` from the sub-domain structure and
add a row to that domain's `## Sub-domains` table. Only the domain's map content
(quick index, cross-domain interfaces, navigation) belongs in `overview.md`.

---

## Workflow

### Step 1: Gather Git Changes

The sync scope is the explicit `base..head` range from the sync prompt (see
Usage above). For `--staged`, use `git diff --staged` instead.

### Step 2: Load Current Documentation

Read the relevant docs from the skill directory
(`.claude/skills/business-logic/`):
- `index.md` for the table of contents / navigation.
- The affected domain's `overview.md` -- specifically its `## Sub-domains` table,
  which tells you which sub-doc owns each changed file.
- **The sub-domain docs that own the changed files.** Update those; touch
  `overview.md` only when the map itself changed (a new sub-domain, a new entry
  point, a changed cross-domain interface).

Skip the dot-prefixed directories (`.scripts/`, `.state/`, `.tmp/`, …) — they
are skill internals, never documentation.

### Step 3: Analyze Code Changes

For each changed file, extract:
- **New methods** -> document new business flows.
- **Modified methods** -> update existing flow descriptions.
- **New constants/enums** -> add to the relevant reference sections.
- **New tables/fields** -> update database-schema docs.
- **New API endpoints** -> add to API reference tables.
- **Business-rule changes** -> update the rules sections.

### Step 4: Generate Proposals

Create diff-style proposals:

```markdown
### Proposed Update: your-domain/your-flow.md

**Section:** Complete Flow

**Change:**
```diff
- Step 4: one remote call per item (N calls)
+ Step 4: batch API (1 call)
```

**Reason:** Refactored to use the batch API.
```

### Step 5: Apply (or confirm, in interactive mode)

In automated mode (git hooks), apply changes directly with the Edit/Write tools
and append an entry to `CHANGELOG.md`. In interactive mode, present proposals and
wait for confirmation first.

---

## Output Format

```markdown
## Git Changes Analysis

### Commits
- abc123: feat: your feature summary

### Files Changed
| File | Lines | Domain |
|------|-------|--------|
| YourService.java | +45/-12 | Your Domain |

### Documentation Updates Required

#### 1. your-domain/your-flow.md
- Section: Complete Flow
- Action: add batch-processing step
- Reason: code now uses the batch API
```

---

## Important Notes

- Preserve the existing documentation style and anchors (`last_verified_commit`).
- Keep `index.md` navigation and `coverage.md` in sync when domains **or
  sub-domains** are added or removed -- `index.md` lists both levels.
- When a domain's docs grow past the point where one sub-doc covers several
  unrelated concerns, split it: a new sub-doc plus a row in `## Sub-domains`.
  `uv run --script .claude/skills/business-logic/.scripts/init_plan.py verify
  --domain <name>` reports when a domain has fallen below its required sub-doc
  count or file coverage.
- Never create a domain directory whose name starts with `.` — that namespace
  belongs to the skill.
- Remove stale docs when the corresponding code is deleted.
- In automated mode, write files directly; in interactive mode, confirm first.
- Never edit `.state/` files — the queue and `complete.jsonl` are the engine's
  bookkeeping. Interactive manual syncs end with
  `uv run --script .scripts/auto_sync.py record --base <base> --head <head>`, never with
  hand-edited state.
