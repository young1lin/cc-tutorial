---
name: business-logic
description: Route Codex to the right repository knowledge files on demand and keep those files synced with code, requirements, logic, architecture, and recent commits. Use when Codex needs to load only the relevant knowledge unit such as `order`, `order cancel-order`, `team`, `advanced`, `research`, `examples`, or a cross-cutting topic, explain how that unit works, or sync recent code changes into the corresponding markdown files without re-exploring the whole repository.
---

# business-logic

Persist repository knowledge as a project-local index. `SKILL.md` only defines metadata, parameter routing, loading rules, and sync rules. It must not hold unit-specific content.

## Routing Contract

Route by parameter. Do not load all business documents at once.

Invocation forms:

```bash
business-logic <unit>
business-logic <unit> <topic>
business-logic sync
business-logic last <n>
```

Execution order:

1. Read `change-log.md` first to detect stale units and recent sync scope.
2. If the argument is `<unit>`, load only `<unit>/overview.md`.
3. If the argument is `<unit> <topic>`, load `<unit>/overview.md` first, then `<unit>/<topic>.md`.
4. If the topic file does not exist, fall back to `<unit>/overview.md` and create the missing topic file from code evidence.
5. Read `shared/cross-cutting.md` only when multiple units or shared rules are involved.
6. Return to code only when the unit files are missing or stale. Do not scan every unit directory first.

Examples:

- `business-logic order` -> `order/overview.md`
- `business-logic order cancel-order` -> `order/overview.md` + `order/cancel-order.md`
- `business-logic team leave-team` -> `team/overview.md` + `team/leave-team.md`
- `business-logic advanced` -> `advanced/overview.md`
- `business-logic research prompt-caching` -> `research/overview.md` + `research/prompt-caching.md`

## Directory Contract

```text
.claude/skills/business-logic/
├── SKILL.md
├── change-log.md
├── shared/
│   └── cross-cutting.md
├── <unit-a>/
│   ├── overview.md
│   └── <topic>.md
└── <unit-b>/
    ├── overview.md
    └── <topic>.md
```

Rules:

- Use one directory per reusable knowledge unit.
- A unit can be a runtime business flow, a content section, an engineering subsystem, or a cross-cutting concern.
- Require an `overview.md` file in every unit directory.
- Split concrete topics into separate files such as `leave-team.md`, `cancel-order.md`, `prompt-caching.md`, or `subagents.md`.
- Put shared rules in `shared/cross-cutting.md` instead of duplicating them across units.
- When the user asks about one topic, load only that topic file and the local `overview.md`.
- Make every unit file useful for code changes and reasoning, not just for concept summaries.
- Keep metadata and routing in English.
- Write unit content in the user's working language for that repository or task.

## Operating Modes

### init

Initialize the repository knowledge index.

1. Start with a shallow repository scan. Inspect the top-level tree, entrypoints, route or controller directories, service or use-case directories, data or infrastructure directories, tests, docs, examples, and any existing project-specific folders. Do not begin with a full deep scan.
2. Infer candidate knowledge units from repository evidence after that shallow scan. Use modules, folders, handlers, services, docs, scripts, tests, and naming patterns to identify stable units worth loading on demand.
3. Do not classify the repository first. Extract units directly from what exists. A unit may be a business flow, a content area, an engineering subsystem, or a shared concern.
4. Decide how many explore agents to launch only after the shallow scan. Small repositories may need only 2 to 3 agents. Larger repositories can split by unit or by structural layer.
5. Give each agent a hard boundary. One agent should own one candidate unit or one layer. Do not let multiple agents rescan the same area without a reason.
6. Consolidate the findings into unit directories only after code or document evidence confirms those units. Do not pre-create folders from assumptions.
7. Write key code locations, line numbers, call chains, rules, requirement context, design intent, and state changes into every unit file.
8. Add Mermaid sequence diagrams when they improve flow comprehension.
9. Write results back to the affected unit directory and `shared/`.

### sync

Sync recent changes incrementally.

1. Read `change-log.md` and the already-known files for the affected unit.
2. Inspect `git status`, `git diff`, the latest commit, or the user-specified range.
3. Identify affected units and topic files first.
4. Update only the affected unit directory instead of rebuilding the full index.
5. Refresh code paths, line numbers, fields, call chains, rules, requirements, sequence diagrams, risks, and design notes.
6. Append time, changed files, evidence, and update results to `change-log.md`.

### last N

Sync the last `N` commits instead of only the latest one.

1. Read `change-log.md` and the existing files for the affected units.
2. Use `git log` and `git diff` to lock the changed file set for the last `N` commits.
3. Interpret `last 3` as `HEAD~2..HEAD`, which includes the current `HEAD` plus the prior two commits.
4. Merge the repository impact across that range and update only the affected unit files and shared files.
5. Record the exact commit range in `change-log.md`, for example `HEAD~2..HEAD`.

## Output Contract

Every unit `overview.md` should contain:

- `单元摘要`
- `需求背景`
- `单元目标`
- `关键代码`
- `入口与边界`
- `核心编排`
- `规则与约束`
- `数据与集成`
- `核心时序`
- `风险与未知项`

Every topic file should contain:

- `主题摘要`
- `需求背景`
- `主题目标`
- `关键代码`
- `触发入口或阅读入口`
- `前置条件`
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
