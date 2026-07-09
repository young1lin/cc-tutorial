# business-logic (Claude Code plugin)

A per-project living business-knowledge base. Unit docs live in your repo
under `.claude/business-logic/`; git hooks keep them synced from **two
sources in one LLM round per push cycle**: the commit diff, and a zero-LLM
digest of your Claude Code conversations (requirement background, design
intent, pitfalls).

This engine repo contains no project data and no secrets.

## How syncing works

- `pre-push` (git hook): queues a trigger; a single consumer (atomic
  `O_EXCL` PID lock + 30s heartbeat) batches triggers, builds a Python-only
  transcript digest (per-session line cursors, tool noise stripped, capped
  at 80KB), then runs ONE `claude-agent-sdk` call that syncs all commits
  since the CHANGELOG hash *and* merges the digest into the unit docs.
- `post-merge` (git hook): same consumer, covering commits arriving via
  `git pull` (your teammates' context reaches you through the docs they
  pushed).
- There is **no `post-commit` hook and no Claude Code Stop hook**: ten
  commits and fifteen turn-ends between pushes cost zero LLM rounds.
- `/business-logic capture`: manual escape hatch — distill the current
  conversation into the docs without waiting for a push.
- Doc updates from a `pre-push` sync land after that push finishes (the
  hook is async); they ride the next push.

## Install

Prerequisite once per machine: `pip install claude-agent-sdk`.

### As a plugin (recommended)

```
/plugin marketplace add young1lin/claude-token-monitor
/plugin install business-logic@claude-token-monitor
```

Then, in each project that wants it, run `/business-logic install`
(project mode: engine vendored into `.claude/business-logic/scripts/`) or
`/business-logic install --global` (one shared engine in
`~/.claude/business-logic/bin/`; re-run after plugin updates). The command
creates the data dir from the skeleton, installs the `post-merge` +
`pre-push` git hooks, runs the `.env` guard, and installs the
explore-via-skill rule.

### Standalone (no marketplace)

Clone this repo and run the same steps by hand: copy `data-skeleton/*` to
`<project>/.claude/business-logic/`, copy `scripts/*` to
`.claude/business-logic/scripts/`, then from the project root:
`python .claude/business-logic/scripts/install_hooks.py`.

## Configure

```
cd <project>/.claude/business-logic/scripts   # project mode engine dir
cp .env.example .env                          # fill BASE_URL + AUTH_TOKEN + models
# Global mode instead: cd ~/.claude/business-logic && cp bin/.env.example .env
```

`.env` resolution order: project `scripts/.env`, then
`~/.claude/business-logic/.env` (global fallback — set it once for all
projects if you use one provider).

## Security

- The `.env` guard (`ensure_env_ignored.py`) runs at install and before
  every sync: a git-tracked `.env` aborts everything; missing ignore
  patterns (`.claude/business-logic/.env`, `state/`, …) are appended to the
  repo `.gitignore`; a ground-truth `git check-ignore` catches conflicting
  `!` rules.
- The conversation digest can contain anything you typed. The sync prompt
  forbids copying credentials, tokens, or pasted raw configs into docs —
  and docs are committed, so review them like code.
- Transcripts are read from `~/.claude/projects/`; content older than your
  `cleanupPeriodDays` is gone. If you rarely push, conversation context may
  expire before a sync (commit-diff sync is unaffected).

## Migrating from the old copy-paste template

1. Move your docs: `.claude/skills/business-logic/<units>` →
   `.claude/business-logic/`.
2. Delete the old skill folder and its `.gitignore` entries.
3. Run `/business-logic install`. The installer removes the legacy
   `post-commit` hook automatically.

## Tests

```
python tests/test_digest.py
python tests/test_lock.py
python tests/test_sync_flow.py
python tests/test_install.py
```

Each prints `ALL ... TESTS PASSED`.
