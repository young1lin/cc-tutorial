# Explore the project via the business-logic skill first

> Project rule. Installed by `/business-logic install` into `.claude/rules/`.
> The skill name is fixed as `business-logic`.

## Rule

When asked to understand business logic, locate a feature, explain how something
works, or find the code for a given concept, **prefer the `/business-logic` skill
over launching an Explore Agent or blindly grepping/globbing the codebase.**

The skill maintains a living, domain-organized knowledge base under
`.claude/business-logic/`: one `overview.md` per business domain, plus
flow docs, call-relation graphs, DB schemas, and pitfall notes. It is kept in
sync with the code automatically by the auto-sync git hooks, so it is usually
faster and more accurate than re-deriving the design from source.

## How to use it

```
/business-logic search <keyword>    # locate relevant business logic fast
/business-logic explain <concept>   # deep explanation of a concept
/business-logic map <class|method>  # call-relation graph
/business-logic status              # doc coverage state
/business-logic check               # flag stale docs vs code
```

Start with `search` or `explain`. Reach for `map` when you need callers/callees.

## When to fall back to code

- `/business-logic status` shows the topic's domain has no doc yet, or
- `/business-logic check` reports the relevant doc as stale, or
- the doc conflicts with the code (code wins; note "docs may be stale").

In those cases: read the source code directly, then **backfill what you learned
into the relevant domain doc** (`overview.md` etc.) so the knowledge base stays
current for the next exploration.
