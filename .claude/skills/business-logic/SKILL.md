---
name: business-logic
description: Route Codex to the right business-domain knowledge files on demand and keep those files synced with code, requirements, logic, and recent commits. Use when Codex needs to load only the relevant business area such as `order`, `order cancel-order`, `team`, or `team leave-team`, explain how that business works, or sync recent code changes into the corresponding markdown files without re-exploring the whole repository.
---

# business-logic

Persist repository business knowledge as a project-local index. `SKILL.md` only defines metadata, parameter routing, loading rules, and sync rules. It must not hold domain-specific business content.

## Routing Contract

Route by parameter. Do not load all business documents at once.

Invocation forms:

```bash
business-logic <domain>
business-logic <domain> <action>
business-logic sync
business-logic last <n>
```

Execution order:

1. Read `change-log.md` first to detect stale domains and recent sync scope.
2. If the argument is `<domain>`, load only `<domain>/overview.md`.
3. If the argument is `<domain> <action>`, load `<domain>/overview.md` first, then `<domain>/<action>.md`.
4. If the action file does not exist, fall back to `<domain>/overview.md` and create the missing action file from code evidence.
5. Read `shared/cross-cutting.md` only when multiple domains or shared rules are involved.
6. Return to code only when the domain files are missing or stale. Do not scan every business directory first.

Examples:

- `business-logic order` -> `order/overview.md`
- `business-logic order cancel-order` -> `order/overview.md` + `order/cancel-order.md`
- `business-logic team leave-team` -> `team/overview.md` + `team/leave-team.md`

## Directory Contract

```text
.claude/skills/business-logic/
├── SKILL.md
├── change-log.md
├── shared/
│   └── cross-cutting.md
├── order/
│   ├── overview.md
│   ├── create-order.md
│   └── cancel-order.md
└── team/
    ├── overview.md
    ├── join-team.md
    └── leave-team.md
```

Rules:

- Use one directory per business domain.
- Require an `overview.md` file in every domain directory.
- Split concrete actions into separate files such as `leave-team.md`, `join-team.md`, and `cancel-order.md`.
- Put shared rules in `shared/cross-cutting.md` instead of duplicating them across domains.
- When the user asks about one action, load only that action file and the local `overview.md`.
- Make every domain file useful for code changes, not just for concept summaries.
- Keep metadata and routing in English.
- Write domain content in the user's working language for that repository or task.

## Operating Modes

### init

Initialize the business index.

1. Split exploration by entrypoints, application layer, domain layer, infrastructure layer, tests, and docs.
2. Parallelize with sub-agents when possible. Give each agent one layer or one business domain.
3. Identify domain directories before generating `overview.md` and action files.
4. Write key code locations, line numbers, call chains, rules, requirement context, and state changes into every domain file.
5. Add Mermaid sequence diagrams when they improve flow comprehension.
6. Write results back to the affected domain directory and `shared/`.

### sync

Sync recent changes incrementally.

1. Read `change-log.md` and the already-known files for the affected domain.
2. Inspect `git status`, `git diff`, the latest commit, or the user-specified range.
3. Identify affected domains and action files first.
4. Update only the affected domain directory instead of rebuilding the full index.
5. Refresh code paths, line numbers, fields, call chains, rules, requirements, sequence diagrams, and risks.
6. Append time, changed files, evidence, and update results to `change-log.md`.

### last N

Sync the last `N` commits instead of only the latest one.

1. Read `change-log.md` and the existing files for the affected domains.
2. Use `git log` and `git diff` to lock the changed file set for the last `N` commits.
3. Interpret `last 3` as `HEAD~2..HEAD`, which includes the current `HEAD` plus the prior two commits.
4. Merge the business impact across that range and update only the affected domain files and shared files.
5. Record the exact commit range in `change-log.md`, for example `HEAD~2..HEAD`.

## Output Contract

Every domain `overview.md` should contain:

- `业务摘要`
- `需求背景`
- `业务目标`
- `关键代码`
- `入口接口`
- `应用编排`
- `领域规则`
- `数据与集成`
- `核心时序`
- `风险与未知项`

Every action file should contain:

- `动作摘要`
- `需求背景`
- `动作目标`
- `关键代码`
- `触发入口`
- `前置检查`
- `调用链`
- `请求与字段`
- `状态变化`
- `时序图`
- `风险与未知项`

Use file paths and line numbers whenever possible in `关键代码`.

Prefer Mermaid for `时序图`.

## Constraints

- Do not present unsupported claims as facts.
- Mark inferences as `**[Author's analysis]**`.
- If code paths conflict, record the conflict before giving the current best interpretation.
- If a knowledge file is stale, update it before continuing the business explanation.
