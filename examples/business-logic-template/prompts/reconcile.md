# Reconcile pass prompt

> Run via `/business-logic reconcile`. This is ONE serial pass -- do NOT fan
> out parallel agents. Reconciliation needs a global view to spot
> cross-document duplicates and contradictions, and concurrent edits to the
> same doc conflict. Global view, single writer.

## Inputs

1. `<data>/state/reconcile-candidates.md` -- the deterministic scan output
   (duplicate groups, oversized docs, stale anchors). **Read it first.**
2. The unit docs under `<data>/` that it points at.

`<data>` is the project's `.claude/business-logic/` directory.

## Goal

Reverse accumulated decay from many digest merges WITHOUT losing information:

- **Duplicates**: where the same rule / pitfall / flow appears in >= 2 places,
  keep the best wording and replace the others with a short cross-reference
  (e.g. "See `order/overview.md` > Potential Pitfalls"), or delete if trivial.
- **Contradictions**: where two docs (or two parts of one doc) state mutually
  incompatible facts, resolve against the current CODE -- code wins. Note the
  decision in the doc, then update both sides. If you cannot tell which is
  current, flag it for human review instead of guessing.
- **Bloat**: trim repetition and stale detail inside a single doc while keeping
  it focused. Do NOT remove any of the required structure (the two top anchors
  and the nine sections for `overview.md`).
- **Oversized docs**: if a candidate exceeds `BL_MAX_DOC_BYTES`, split it into
  linked sub-docs (each with the required anchors and sections), and update
  `index.md` to link them.

## Hard rules

- Preserve every overview's `> last_verified_commit:` anchor and the
  newest-first CHANGELOG hash ordering (the sync engine reads the first hash).
- Never delete the only copy of unique information -- consolidate, do not drop.
- Never copy credentials, tokens, or pasted raw configs. If you find one in a
  doc, STOP and report it; do not propagate it by editing around it.
- After editing, append ONE entry to `CHANGELOG.md` marked `[reconcile]`, and
  bump the `last_verified_commit:` of every doc you touched to the current HEAD.
- Touch only files under `<data>/`. Do not modify engine scripts or source code.

## Output

A short summary: how many duplicates consolidated, contradictions resolved
(with each decision), docs split, and anything you flagged for human review.
Then delete `<data>/state/reconcile-candidates.md` -- it has been consumed.
