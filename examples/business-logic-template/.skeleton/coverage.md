# Documentation Coverage

> last_updated: <YYYY-MM-DD HH:MM>
> last_sync_commit: <hash>

One row per domain. The first three columns are the human record — what shape
the domain is in and what last changed in it. The last three are machine-filled
by `.scripts/init_plan.py verify`.

## Domain Coverage

| Domain | Docs | last_verified_commit | Status | Files | Sub-docs | Coverage |
|--------|------|---------------------|--------|-------|----------|----------|
| _example-domain | 2 | <hash> | Stable | 18 | 1 / 1 | - |

`Status` is a sentence, not a flag: say what the last sync changed and why, so a
reader can tell whether the domain moved recently.

```
Updated (fee tiers split into pricing.md; discount rule engine rewritten)
Stable
CORRECTED: <what the docs previously claimed, and what is true at HEAD>
```

**Corrections are first-class.** When a sync discovers the docs asserted
something false, say so explicitly in `Status` rather than silently rewriting —
a knowledge base that records its own corrections is one people keep trusting.

## Notes

- `Docs` -- total markdown files in the domain directory (including records).
- `Files` -- source files in the domain's ledger (`.state/init-plan.json`).
- `Sub-docs` -- analysis docs written / required (`ceil(files / 40)`, 0 below 25
  files). Changelog and archive docs do not count.
- `Coverage` -- share of ledger files actually named in the domain's docs; the
  depth gate requires 70%.
- `-` means not yet verified against the current code.
- Refresh the machine columns with `.scripts/init_plan.py verify`; run
  `/business-logic check` to update the human ones.
