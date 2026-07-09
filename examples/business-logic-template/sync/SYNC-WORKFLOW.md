# Sync Workflow

This document describes the workflow for syncing git code changes into the
business-logic documentation. It is the reference the auto-sync agent follows
when `/<skill> sync` runs.

## Usage

```bash
/<skill> sync              # sync the latest commit
/<skill> sync 3            # sync the last 3 commits
/<skill> sync --staged     # sync staged (uncommitted) changes
/<skill> sync --dry-run    # preview without modifying files
```

> Replace `<skill>` with the actual skill (folder) name, e.g. `business-logic`.

---

## File-to-Domain Mapping

Define your own mapping here. For each file pattern in your codebase, record the
business domain it belongs to and the doc file that covers it. Example shape:

| File Pattern | Business Domain | Target Doc |
|--------------|-----------------|-----------|
| `YourService*.java` | Your Domain | `your-domain/*.md` |
| `*Mapper.xml` | Database Schema | `*/database-schema.md` |
| `*Ctl.java` / `*Controller.java` | API Endpoints | `*/api.md` or `*/overview.md` |

Keep this table in sync with how you organize docs on disk.

---

## Workflow

### Step 1: Gather Git Changes

```bash
git log --oneline -5           # recent commits
git diff HEAD~1 HEAD --stat    # file summary
git diff HEAD~1 HEAD           # detailed changes
```

For `sync N`, use `HEAD~N` instead of `HEAD~1`. For `--staged`, use `git diff --staged`.

### Step 2: Load Current Documentation

Read the relevant docs from the project data dir (`.claude/business-logic/`):
- `index.md` for the table of contents / navigation.
- The domain docs that correspond to the changed files.

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
- Keep the main `SKILL.md` navigation in sync when domains are added or removed.
- Remove stale docs when the corresponding code is deleted.
- In automated mode, write files directly; in interactive mode, confirm first.
