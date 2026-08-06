# Business Logic Index

> Navigation for this project's knowledge units. Maintained by `/business-logic init` and `sync`.
> Replace the example below with your real domains.

**Every entry carries an annotation, not just a title.** A bare link tells a
reader nothing about whether to open it; the annotation is what turns this file
into the place people actually start. List domains AND their sub-docs -- an
index that stops at the domain level hides exactly the content people search for.

Annotation conventions:

- Say what is inside **and when to read it**: `-- 90-day window, ROI units gotcha (read this first when the numbers disagree)`.
- Mark liveness when it is not obvious: `**ACTIVE** at HEAD`, `**REMOVED** (commit <hash>)`, `**DEPRECATED** -- replaced by <doc>`.
- Mark the domain's entry point: `**start here**`.

## Domains

### <Business area>

- [_example-domain](_example-domain/overview.md) -- **start here** for the domain map, quick index and sub-domain table.
  - [example-subdomain](_example-domain/example-subdomain.md) -- fee calculation, discount rules, `fee_config` tiers; **ACTIVE** at HEAD.

Entries you will add as the domain grows (shown here unlinked on purpose -- a
link to a doc that does not exist yet is exactly what the depth rules forbid):

- `settlement.md` -- settlement batches, `settlement_record` state machine.
- `changelog-archive.md` -- dated sync history; a record, not a knowledge doc.

## Cross-domain map

```
<domain-a> ──► <domain-b> ──► <domain-c>
     └────────► <shared-infra>
```
