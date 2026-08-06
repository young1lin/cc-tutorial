# /// script
# requires-python = ">=3.10"
# CLI-runner mode (claude/codex/opencode) needs NO third-party packages -- it
# just spawns the CLI as a subprocess. The api fallback lazy-imports
# pydantic-ai (install pydantic-ai-slim[openai] or [anthropic] yourself); the
# legacy claude-sdk path needs claude-agent-sdk. Keeping this empty means
# `uv run --script` sets up a minimal stdlib-only environment by default.
# dependencies = []
# ///
"""
Git hook worker: auto-sync business-logic docs after git pull / push, or on a
manual trigger.

Usage:
    uv run --script auto_sync.py post-merge            # triggered after git pull
    uv run --script auto_sync.py pre-push               # triggered before git push
    uv run --script auto_sync.py manual [--base B] [--head H] [--prompt "..."]
    uv run --script auto_sync.py record --base B --head H --from manual-inline [--prompt "..."]
    uv run --script auto_sync.py state                  # print JSON: last_head / lock_busy / pending

Architecture: file-based job queue + single consumer.
Every trigger captures the EXACT commit range it introduced (post-merge:
ORIG_HEAD..HEAD; pre-push: @{u}..HEAD; manual: <last-completed-head>..HEAD) and
appends a job record to `.state/queue.jsonl`. Enqueue deduplicates at commit-hash
granularity against jobs already pending or in-flight, so the same commit is
never processed twice. Only one consumer runs at a time, enforced by an atomic
O_EXCL PID lock plus a heartbeat that keeps long syncs from looking dead. The
consumer batches all pending jobs into one range, builds a zero-LLM conversation
digest, then runs ONE claude-agent-sdk call (permission granted via the SDK
permission callback) that syncs that explicit range AND merges the digest into
the domain docs. On success it appends a completion record to
`.state/complete.jsonl` and validates the CHANGELOG was actually updated.

Single source of truth for "what has been synced" is `.state/complete.jsonl`
(the last record's head), NOT CHANGELOG.md -- CHANGELOG.md is a human-facing log
the model writes, and deriving sync state from it was brittle (stale/reformatted
hashes caused pathological over-syncs). For upgrades from older installs, the
first sync falls back to the CHANGELOG hash once, then complete.jsonl takes over.

The skill is always project-level: everything lives under
<project>/<cli>/skills/<name>/. Skill-owned directories are dot-prefixed
(.scripts, .state, .sync, .tmp) so they can never collide with a user's
business-domain directory of the same name. The engine location is derived from
__file__, so the same script serves any skill name and survives a git root that
sits above the <cli> dir.
"""

import argparse
import asyncio
import ctypes
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

try:
    from claude_agent_sdk import (
        ClaudeAgentOptions,
        ClaudeSDKClient,
        PermissionResultAllow,
    )
    HAVE_CLAUDE_SDK = True
except ImportError:
    # Optional: only the legacy SYNC_BACKEND=claude-sdk path needs it. PydanticAI
    # (openai/anthropic) works without claude-agent-sdk installed.
    HAVE_CLAUDE_SDK = False

# Make the sibling modules importable. Both ensure_env_ignored and
# digest_transcripts are stdlib-only (subprocess/pathlib/json/sqlite3), so
# top-level imports are safe. llm_backend pulls in pydantic-ai and is imported
# lazily only on the api path -- see _run_worker / _run_worker_pydantic.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ensure_env_ignored  # noqa: E402
import digest_transcripts  # noqa: E402

# ---------------------------------------------------------------------------
# Force UTF-8 EVERYWHERE. The engine must run on zh-CN Windows where the
# default codepage is GBK; git output and doc content are UTF-8, so any
# reliance on the platform default corrupts data (it crashed real syncs).
#   * PYTHONUTF8 / PYTHONIOENCODING propagate UTF-8 to child processes.
#   * stdout/stderr are reconfigured so state/record JSON prints as UTF-8.
#   * Every file read/write and subprocess call here passes encoding="utf-8",
#     and git() forces core.quotepath=false + i18n.logOutputEncoding=utf-8.
# ---------------------------------------------------------------------------
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ.setdefault("LANG", "C.UTF-8")
os.environ.setdefault("LC_ALL", "C.UTF-8")
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def find_git_root(start):
    """Walk up from `start` until a directory containing `.git` is found."""
    start = Path(start).resolve()
    for candidate in [start, *start.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None


# Engine location is derived from __file__, so the same script serves any skill
# (business-logic, bl, ...). The skill directory IS the data directory: docs,
# engine and state all live together under the project, so the whole thing is
# one copyable folder.
#
# WORK_ROOT is found by walking UP from the script to the nearest .git -- this
# does NOT assume a fixed <cli>/skills/<name> layout, so the skill works
# anywhere inside a repo (standard .claude/skills/ or .agents/skills/, a custom
# with a git root sitting above <cli>). DATA_REL is computed from the actual
# positions, never hardcoded.
SCRIPT_DIR = Path(__file__).resolve().parent       # <skill>/.scripts
SKILL_DIR = SCRIPT_DIR.parent                      # the skill folder (== data dir)
SKILL_NAME = SKILL_DIR.name                        # "business-logic" | "bl"
GIT_ROOT = find_git_root(SKILL_DIR)
# CLI_DIR = the config dir that owns this skill (.claude / .agents / .opencode).
# Standard layout <root>/<cli>/skills/<skill> puts the shared .env at <cli>/.env,
# so the secret travels with whichever CLI the user picked -- never hardcoded.
CLI_DIR = SKILL_DIR.parent.parent

if GIT_ROOT is None:
    print("[auto_sync] Not inside a git repository; nothing to sync.", file=sys.stderr)
    sys.exit(0)

WORK_ROOT = GIT_ROOT
DATA_DIR = SKILL_DIR
STATE_DIR = SKILL_DIR / ".state"   # cursors, queue, PID lock (git-ignored)
TMP_DIR = SKILL_DIR / ".tmp"       # logs + digest (git-ignored; safe to delete)

if not DATA_DIR.exists():
    # Project not initialized for business-logic; stay silent and inert.
    sys.exit(0)

DATA_REL = SKILL_DIR.relative_to(WORK_ROOT).as_posix()

# cwd = the dir containing <cli>/, so git commands and skill discovery both work.
os.chdir(str(WORK_ROOT))
STATE_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = TMP_DIR / "auto_sync.log"
QUEUE_FILE = STATE_DIR / "queue.jsonl"           # pending job records (one JSON object per line)
PROCESSING_FILE = STATE_DIR / "queue.processing" # in-flight batch (crash-safe drain target)
COMPLETE_FILE = STATE_DIR / "complete.jsonl"     # append-only completed batches; last head = source of truth
PID_FILE = STATE_DIR / "auto_sync.pid"

# Max heartbeat staleness in seconds; beyond this a consumer is considered dead
# or hung. The live consumer refreshes the PID file mtime every
# HEARTBEAT_INTERVAL seconds, so even a multi-hour sync stays fresh.
LOCK_TIMEOUT = 600

# How often the consumer touches the PID file to prove it is still alive.
HEARTBEAT_INTERVAL = 30

# Batch window: after becoming consumer, wait this long for more hooks to queue.
BATCH_WINDOW = 3

# Per-doc size budget. After a sync, any domain doc larger than this is split
# into focused sub-docs by a dedicated SDK call (see run_split). Each resulting
# doc is aimed at SPLIT_TARGET_BYTES so it keeps room to grow.
MAX_DOC_BYTES = 50_000
SPLIT_TARGET_BYTES = 40_000

# Oversized docs are split concurrently -- one worker per file (bounded) -- so
# wall-clock is the slowest single file, not the sum.
SPLIT_CONCURRENCY = 4

# Skill control files are never treated as splittable domain docs.
CONTROL_DOCS = {"SKILL.md", "coverage.md", "CHANGELOG.md", "index.md"}

# When listing commits into the sync prompt, cap the visible list.
MAX_COMMIT_LINES = 40

# Backoff intervals (seconds) for rate-limit retries.
RATE_LIMIT_BACKOFF = [1, 5, 10, 30]

# Error-text keywords that indicate rate limiting / transient server errors.
RATE_LIMIT_PATTERNS = [
    "rate_limit", "rate limit", "ratelimit", "too many requests",
    "429", "503", "502", "throttle", "quota exceeded",
    "resource exhausted", "concurrency limit", "overloaded",
    "server error", "internal error", "service unavailable",
]

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def git(args):
    """Run a git command in WORK_ROOT and return the CompletedProcess.

    Force UTF-8 decoding: git emits UTF-8 (commit subjects may be non-ASCII),
    but subprocess defaults to the locale codepage (GBK on zh-CN Windows), which
    would raise UnicodeDecodeError and leave stdout=None.
    """
    return subprocess.run(
        # Force UTF-8: literal (not octal-escaped) non-ASCII paths, UTF-8 log output.
        ["git", "-c", "core.quotepath=false", "-c", "i18n.logOutputEncoding=utf-8", *args],
        capture_output=True, text=True,
        encoding="utf-8", errors="replace", cwd=str(WORK_ROOT),
    )


def git_out(args):
    """Run a git command and return stripped stdout, or '' on failure."""
    r = git(args)
    return r.stdout.strip() if r.returncode == 0 else ""


def rev_parse(ref):
    """Resolve a ref to a full commit sha, or '' if it does not resolve."""
    if not ref:
        return ""
    r = git(["rev-parse", "--verify", "--quiet", "{}^{{commit}}".format(ref)])
    return r.stdout.strip() if r.returncode == 0 else ""


def rev_list(base, head):
    """Return the commit hashes in base..head (newest first).

    If base is empty (e.g. head is the root commit), returns head's ancestry;
    in normal operation base is always resolved so the range stays bounded.
    """
    if not head:
        return []
    rng = "{}..{}".format(base, head) if base else head
    r = git(["rev-list", rng])
    if r.returncode != 0:
        log.warning("rev-list %s failed: %s", rng, r.stderr.strip()[:200])
        return []
    return [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]


def _fallback_base(head):
    """The parent of head, used when no better base is known ('' at root)."""
    return rev_parse(head + "~1") if head else ""


# ---------------------------------------------------------------------------
# Job records + queue: append (JSONL) + hash-dedup + batch drain
# Uses an O_EXCL lock file for safe concurrent writes on Windows.
# ---------------------------------------------------------------------------

QUEUE_LOCK = STATE_DIR / "queue.lock"


def _acquire_queue_lock(retries=20, base_delay=0.02):
    """Acquire an exclusive lock via O_CREAT|O_EXCL (atomic on NTFS)."""
    for attempt in range(retries):
        try:
            return os.open(str(QUEUE_LOCK), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            # Jittered backoff: 20-80ms per attempt, ~1s max total.
            delay = base_delay + (os.getpid() % 50) * 0.001 + attempt * 0.01
            time.sleep(delay)
    return None


def _release_queue_lock(fd):
    """Release the queue lock."""
    if fd is None:
        return
    try:
        os.close(fd)
    except OSError:
        pass
    try:
        QUEUE_LOCK.unlink(missing_ok=True)
    except OSError:
        pass


def _read_jobs(path):
    """Read a JSONL job file into a list of dicts (skips blank/corrupt lines)."""
    jobs = []
    if not path.exists():
        return jobs
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            jobs.append(json.loads(line))
        except Exception as e:
            log.warning("Skipping corrupt job line in %s: %s", path.name, e)
    return jobs


def _write_jobs(path, jobs):
    """Overwrite a JSONL job file with the given jobs."""
    path.write_text(
        "".join(json.dumps(j, ensure_ascii=False) + "\n" for j in jobs),
        encoding="utf-8",
    )


def _append_job(path, job):
    """Append one job record as a JSONL line."""
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(job, ensure_ascii=False) + "\n")


def _tracked_commits():
    """Commit hashes already pending (queue) or in-flight (.processing)."""
    seen = set()
    for f in (QUEUE_FILE, PROCESSING_FILE):
        for j in _read_jobs(f):
            seen.update(j.get("commits", []))
    return seen


def _dedup_and_append(job):
    """Dedup this job's commits against pending+in-flight, then append it.

    A trigger whose commits are ALL already queued/in-flight is dropped -- this
    is how a duplicate pull/push firing twice is coalesced. A job carrying a
    manual prompt is always kept even if its commits are duplicates, because the
    prompt is new intent the model should still act on.
    """
    already = _tracked_commits()
    new_commits = [c for c in job.get("commits", []) if c not in already]
    if not new_commits and not job.get("prompt"):
        log.info("All %d commit(s) already queued/in-flight; skipping enqueue.",
                 len(job.get("commits", [])))
        return
    if new_commits:
        job["commits"] = new_commits
    _append_job(QUEUE_FILE, job)
    log.info("Queued %s: %d commit(s) [%s..%s]%s",
             job.get("from"), len(job.get("commits", [])),
             (job.get("base") or "")[:9], (job.get("head") or "")[:9],
             " +prompt" if job.get("prompt") else "")


def queue_push(job):
    """Append a job to the queue (concurrency-safe, hash-deduped)."""
    fd = _acquire_queue_lock()
    if fd is None:
        log.error("Failed to acquire queue lock for push; writing directly.")
        try:
            _dedup_and_append(job)
        except Exception as e:
            log.error("Fallback queue push also failed: %s", e)
        return
    try:
        _dedup_and_append(job)
    finally:
        _release_queue_lock(fd)


def queue_drain():
    """Drain all pending jobs via an atomic rename (crash-safe).

    Holds QUEUE_LOCK across recovery + rename so a producer cannot interleave a
    write between our rename and a new push. Strategy: rename queue.jsonl to
    queue.processing, then parse it. If the consumer crashes mid-processing, the
    .processing file is merged back on the next consumer start.
    """
    fd = _acquire_queue_lock()
    if fd is None:
        log.error("Failed to acquire queue lock for drain; aborting drain.")
        return []
    try:
        # Recovery: fold a leftover .processing file (from a crash) back in.
        if PROCESSING_FILE.exists():
            log.warning("Found stale .processing file, merging back into queue.")
            leftover = _read_jobs(PROCESSING_FILE)
            existing = _read_jobs(QUEUE_FILE)
            _write_jobs(QUEUE_FILE, leftover + existing)
            PROCESSING_FILE.unlink(missing_ok=True)

        if not QUEUE_FILE.exists():
            return []
        QUEUE_FILE.rename(PROCESSING_FILE)      # atomic -- no partial state possible
        jobs = _read_jobs(PROCESSING_FILE)
        PROCESSING_FILE.unlink(missing_ok=True)
        log.info("Drained %d job(s) from queue.", len(jobs))
        return jobs
    except Exception as e:
        log.error("Failed to drain queue: %s", e)
        if PROCESSING_FILE.exists():
            log.error("Preserving .processing file for manual recovery.")
        return []
    finally:
        _release_queue_lock(fd)


def merge_jobs(jobs):
    """Merge pending jobs into one batch: union of commits, span base..head.

    Jobs are stored oldest-first, so base = oldest job's base and head = newest
    job's head. Commit order is preserved and deduped. Manual prompts are joined.
    """
    prompts = [j["prompt"] for j in jobs if j.get("prompt")]
    seen, commits = set(), []
    for j in jobs:
        for c in j.get("commits", []):
            if c not in seen:
                seen.add(c)
                commits.append(c)
    return {
        "from": [j.get("from") for j in jobs],
        "base": jobs[0].get("base", "") if jobs else "",
        "head": jobs[-1].get("head", "") if jobs else "",
        "commits": commits,
        "prompt": "\n\n".join(prompts),
    }


def last_complete_head():
    """The head of the most recent completed batch -- the sync source of truth."""
    head = ""
    for rec in _read_jobs(COMPLETE_FILE):
        if rec.get("head"):
            head = rec["head"]
    return head


def changelog_fallback_head():
    """Legacy fallback: the last synced hash recorded in CHANGELOG.md.

    Used once when complete.jsonl is empty (upgrading from an older engine).
    CHANGELOG uses newest-first entries; the leftmost `hash..` is the most
    recent sync.
    """
    changelog = DATA_DIR / "CHANGELOG.md"
    if not changelog.exists():
        return ""
    try:
        content = changelog.read_text(encoding="utf-8")
        match = re.search(r"\b([0-9a-f]{7,12})\.\.", content)
        return match.group(1) if match else ""
    except Exception as e:
        log.warning("Failed to read CHANGELOG.md: %s", e)
        return ""


def record_complete(batch, result="ok", from_override=None):
    """Append a completion record to complete.jsonl (concurrency-safe).

    Recorded ONLY on success, so a failed sync retries from the same base.
    """
    rec = {
        "from": from_override or batch.get("from"),
        "base": batch.get("base", ""),
        "head": batch.get("head", ""),
        "commits": batch.get("commits", []),
        "prompt": batch.get("prompt", ""),
        "result": result,
        "is_done": True,
        "synced_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    fd = _acquire_queue_lock()
    try:
        _append_job(COMPLETE_FILE, rec)
    finally:
        _release_queue_lock(fd)
    log.info("Recorded completion (%s): %d commit(s) up to %s",
             result, len(rec["commits"]), (rec["head"] or "")[:9])


# ---------------------------------------------------------------------------
# Commit-range capture (per trigger source)
# ---------------------------------------------------------------------------

def capture_job(trigger, args):
    """Build a job record with the exact commit range this trigger introduced.

    - post-merge: ORIG_HEAD..HEAD (what git merge/pull just brought in)
    - pre-push:   @{u}..HEAD (commits not yet on the upstream being pushed to)
    - manual:     <--base | last-completed-head | HEAD~1>..<--head | HEAD>
    """
    head = rev_parse(args.head or "HEAD")
    if trigger == "post-merge":
        base = rev_parse("ORIG_HEAD") or _fallback_base(head)
    elif trigger == "pre-push":
        base = rev_parse("@{u}") or last_complete_head() or _fallback_base(head)
    else:  # manual (and any other explicit trigger)
        base = (rev_parse(args.base) if args.base else "") or last_complete_head() or _fallback_base(head)
    commits = rev_list(base, head)
    return {
        "from": trigger,
        "base": base,
        "head": head,
        "commits": commits,
        "prompt": args.prompt or "",
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "is_done": False,
    }


# ---------------------------------------------------------------------------
# PID-based consumer lock
# ---------------------------------------------------------------------------

def is_pid_alive(pid):
    """Check whether a process is still running (Windows and POSIX)."""
    if sys.platform == "win32":
        try:
            kernel32 = ctypes.windll.kernel32
            SYNCHRONIZE = 0x100000
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = kernel32.OpenProcess(
                SYNCHRONIZE | PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
            if not handle:
                return False
            try:
                # OpenProcess also succeeds for exited processes whose handles
                # are still held elsewhere; only STILL_ACTIVE means running.
                exit_code = ctypes.c_ulong()
                if kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                    return exit_code.value == 259  # STILL_ACTIVE
                return True  # cannot query; err toward "alive" (defer, no double run)
            finally:
                kernel32.CloseHandle(handle)
        except Exception:
            return False
    try:
        os.kill(pid, 0)  # signal 0 = existence probe, does not kill
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # process exists but belongs to another user
    except OSError:
        return False


def consumer_is_active():
    """True if a live consumer currently holds the PID lock."""
    if not PID_FILE.exists():
        return False
    try:
        pid = int(PID_FILE.read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        return False
    return is_pid_alive(pid)


def _create_pid_file():
    """Atomically create the PID file via O_CREAT|O_EXCL. True if we own it."""
    try:
        fd = os.open(str(PID_FILE), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    try:
        os.write(fd, str(os.getpid()).encode("ascii"))
    finally:
        os.close(fd)
    return True


def try_become_consumer():
    """Try to become the consumer. Returns True if we got the role.

    The PID file is created with O_CREAT|O_EXCL (atomic on NTFS and POSIX), so
    two processes can never both believe they created it. If the file already
    exists, its owner is honored while alive and its heartbeat is fresh;
    otherwise the stale file is removed and creation is retried. Losing the race
    is safe: the trigger is already queued and will be drained by the winner.
    """
    for _ in range(2):
        if _create_pid_file():
            log.info("Became consumer (PID %d)", os.getpid())
            return True

        try:
            pid = int(PID_FILE.read_text(encoding="utf-8").strip())
            age = time.time() - PID_FILE.stat().st_mtime
        except (ValueError, OSError) as e:
            log.warning("Corrupt or vanished PID file (%s), removing and retrying", e)
            try:
                PID_FILE.unlink()
            except OSError:
                pass
            continue

        if is_pid_alive(pid):
            if age < LOCK_TIMEOUT:
                log.info("Consumer PID %d is alive (heartbeat age=%.0fs), deferring", pid, age)
                return False
            log.warning("Consumer PID %d heartbeat is stale (age=%.0fs), taking over", pid, age)
        else:
            log.warning("Dead consumer PID %d, taking over", pid)

        try:
            PID_FILE.unlink()
        except OSError:
            pass
        # Loop back to the atomic create; a concurrent taker may win it instead.

    log.info("Lost consumer race to another process, deferring")
    return False


def release_consumer():
    """Release the consumer role."""
    try:
        if PID_FILE.exists():
            if PID_FILE.read_text(encoding="utf-8").strip() == str(os.getpid()):
                PID_FILE.unlink()
                log.info("Released consumer role")
    except OSError as e:
        log.warning("Failed to release consumer PID: %s", e)


def start_heartbeat(stop_event):
    """Refresh the PID file mtime periodically while the consumer runs.

    Without this, a sync longer than LOCK_TIMEOUT would look stale and get taken
    over by the next trigger while still running. The thread stops when
    stop_event is set or when the PID file no longer belongs to this process.
    """
    def beat():
        while not stop_event.wait(HEARTBEAT_INTERVAL):
            try:
                if PID_FILE.read_text(encoding="utf-8").strip() != str(os.getpid()):
                    return  # superseded; stop claiming liveness
                os.utime(str(PID_FILE), None)
            except OSError:
                return
    thread = threading.Thread(target=beat, daemon=True, name="pid-heartbeat")
    thread.start()
    return thread


# ---------------------------------------------------------------------------
# Rate-limit detection + env loading
# ---------------------------------------------------------------------------

def is_rate_limit_error(error_text):
    """Return True if an error message indicates rate limiting / transient error."""
    lower = error_text.lower()
    return any(pat in lower for pat in RATE_LIMIT_PATTERNS)


def load_env():
    """Load env vars from the CLI config dir's .env (e.g. .claude/.env, .agents/.env).

    The .env sits outside the skill directory on purpose: it is per-machine
    environment config (provider URL, token), not skill content, so copying
    the skill folder between projects never drags credentials along.
    """
    candidates = [
        CLI_DIR / ".env",
    ]
    extra_env = {}
    env_file = next((p for p in candidates if p.exists()), None)
    if env_file is None:
        log.warning(".env not found in: %s", " | ".join(str(p) for p in candidates))
        return extra_env
    loaded = 0
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)
        extra_env[key] = value
        loaded += 1
    log.info("Loaded %d env vars from %s", loaded, env_file)
    return extra_env


def _auto_allow_tool(tool_name, tool_input, context):
    """Programmatically grant every tool the automated worker requests.

    permission_mode alone is unreliable here: bypassPermissions is downgraded (an
    enterprise/managed policy), and neither it nor `allowed_tools` satisfied the
    Edit/Write "write grant" -- the worker got "you haven't granted it yet" and
    fell back to slow, repo-polluting shell writes. The SDK's can_use_tool
    callback is the authoritative headless approver, so we allow here.
    """
    return PermissionResultAllow()


def _sdk_options(env_vars):
    """Shared ClaudeAgentOptions for sync + split worker calls.

    Permission is granted programmatically via can_use_tool (see _auto_allow_tool)
    because bypassPermissions is not honored in this environment. Tools are
    listed with paths scoped to the skill data dir; cwd is the project root.
    """
    env_vars["BUSINESS_LOGIC_SYNC"] = "1"  # lets tooling identify our own sessions
    env_vars["PYTHONUTF8"] = "1"           # force UTF-8 in the worker + any child it spawns
    env_vars["PYTHONIOENCODING"] = "utf-8"
    return ClaudeAgentOptions(
        permission_mode="acceptEdits",
        cwd=str(WORK_ROOT),
        env=env_vars,
        allowed_tools=[
            "Read", "Glob", "Grep", "Bash",
            "Edit({rel}/**)".format(rel=DATA_REL),
            "Write({rel}/**)".format(rel=DATA_REL),
        ],
        can_use_tool=_auto_allow_tool,
    )


async def _run_worker(prompt, label, max_retries=3):
    """Run one worker turn via the best available runner, with retry.

    Runner selection (SYNC_RUNNER in .env, default auto):
      - claude / codex / opencode : spawn that CLI headless -- it has its own
        agent loop + tools and runs on the user's already-paid subscription
        (Claude Code / Codex plans) or configured provider (opencode). This is
        the preferred path: subscriptions are bound to the CLI and cannot be
        invoked via raw API.
      - api : PydanticAI direct API call (the "Pi-style" fallback, for when no
        CLI is available); provider picked by SYNC_BACKEND.
    Returns True on a clean finish, False on error / exhausted retries.
    """
    env_vars = load_env()
    runner = _detect_runner(env_vars)
    if runner in ("claude", "codex", "opencode"):
        return await _run_worker_cli(prompt, label, runner, env_vars, max_retries)
    # runner == "api": prefer PydanticAI, then legacy claude-agent-sdk.
    # Lazy import: pydantic-ai is only needed on the api path; the CLI-runner
    # branch above must work with zero third-party packages installed.
    try:
        import llm_backend
    except ImportError:
        llm_backend = None
    if llm_backend is not None and llm_backend.make_backend(env_vars):
        return await _run_worker_pydantic(prompt, label, env_vars, max_retries)
    if HAVE_CLAUDE_SDK:
        return await _run_worker_claude_sdk(prompt, label, env_vars, max_retries)
    log.error("No sync runner available: no CLI (claude/codex/opencode) found and "
              "no API backend (SYNC_BACKEND) configured. Set SYNC_RUNNER or provide "
              "an API key in .env.")
    return False


def _detect_runner(env):
    """Pick the runner: explicit SYNC_RUNNER, else auto-detect an installed CLI,
    else 'api'."""
    configured = (env.get("SYNC_RUNNER") or "auto").strip().lower()
    if configured != "auto":
        return configured
    for cli in ("claude", "codex", "opencode"):
        if shutil.which(cli):
            return cli
    return "api"


def _cli_command(runner, env=None):
    """Build the headless command for a CLI runner. The prompt is fed via stdin
    so very long sync prompts (diff + digest) never hit the argv length limit."""
    env = env or {}
    if runner == "claude":
        return ["claude", "-p", "--dangerously-skip-permissions",
                "--allowedTools", "Read", "Edit", "Write", "Bash", "Glob", "Grep"]
    if runner == "codex":
        # codex exec runs headless; bypass approvals so it isn't blocked. The
        # model can be pinned (e.g. gpt-5.3 with low reasoning effort) instead
        # of accepting codex's default, which is often slower for batch work.
        cmd = ["codex", "exec", "--dangerously-bypass-approvals-and-sandbox"]
        model = env.get("CODEX_MODEL")
        if model:
            cmd += ["-m", model]
        reasoning = env.get("CODEX_REASONING")
        if reasoning:
            cmd += ["-c", "model_reasoning_effort={}".format(reasoning)]
        return cmd
    if runner == "opencode":
        # --auto: auto-approve tool permissions (sync is unattended).
        # --format json: structured events on stdout (parsed for errors).
        # -m: optional model override (provider/model, e.g. zhipuai-coding-plan/glm-5.2);
        #     without it opencode uses whatever it's configured for.
        # --variant: optional reasoning effort (low/minimal/high/max).
        cmd = ["opencode", "run", "--auto", "--format", "json"]
        model = env.get("OPENCODE_MODEL")
        if model:
            cmd += ["-m", model]
        variant = env.get("OPENCODE_VARIANT")
        if variant:
            cmd += ["--variant", variant]
        return cmd
    raise ValueError("unknown CLI runner: {!r}".format(runner))


def _spawn_cli(cmd, prompt, timeout):
    """Run one CLI headless turn synchronously (called via run_in_executor)."""
    # On Windows, npm-global CLIs ship as .ps1; subprocess (no shell) can only
    # launch .exe/.cmd/.bat. Resolve the .cmd shim when the lookup hit a .ps1.
    resolved = shutil.which(cmd[0])
    if resolved:
        if resolved.lower().endswith(".ps1"):
            alt = resolved[:-4] + ".cmd"
            if Path(alt).exists():
                cmd = [alt] + cmd[1:]
        else:
            cmd = [resolved] + cmd[1:]
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(cmd, input=prompt, cwd=str(WORK_ROOT), capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          timeout=timeout, env=env)
    if proc.stdout:
        log.info("cli stdout: %s", (proc.stdout or "")[:300])
    if proc.stderr:
        log.info("cli stderr: %s", (proc.stderr or "")[:300])
    return proc.returncode


async def _run_worker_cli(prompt, label, runner, env_vars, max_retries):
    """Spawn a CLI headless to execute the prompt (reuses the user's subscription)."""
    cmd = _cli_command(runner, env_vars)
    timeout = int(env_vars.get("API_TIMEOUT_MS") or 1800000) / 1000
    for attempt in range(1, max_retries + 1):
        log.info("Starting %s (cli:%s) attempt %d/%d", label, runner, attempt, max_retries)
        log.info("cmd: %s", " ".join(cmd))
        try:
            loop = asyncio.get_event_loop()
            rc = await loop.run_in_executor(None, _spawn_cli, cmd, prompt, timeout)
            if rc == 0:
                log.info("%s (cli:%s) completed rc=0", label, runner)
                return True
            log.error("%s (cli:%s) failed rc=%d", label, runner, rc)
        except subprocess.TimeoutExpired:
            log.error("%s (cli:%s) timed out after %ds", label, runner, int(timeout))
        except Exception as e:
            log.error("%s (cli:%s) error: %s", label, runner, e)
        backoff = RATE_LIMIT_BACKOFF[min(attempt - 1, len(RATE_LIMIT_BACKOFF) - 1)]
        log.warning("retrying %s (cli:%s) in %ds", label, runner, backoff)
        await asyncio.sleep(backoff)
    log.error("All %d %s (cli:%s) attempts exhausted", max_retries, label, runner)
    return False


async def _run_worker_pydantic(prompt, label, env_vars, max_retries):
    """PydanticAI path (openai / anthropic). Proxy via httpx env vars."""
    import llm_backend  # lazy: pydantic-ai only needed on the api path
    allow_bash = os.environ.get("ALLOW_SYNC_BASH") == "1" or env_vars.get("ALLOW_SYNC_BASH") == "1"
    for attempt in range(1, max_retries + 1):
        log.info("Starting %s (pydantic-ai) attempt %d/%d", label, attempt, max_retries)
        log.info("Prompt: %s", prompt[:200])
        text, ok = await llm_backend.run_worker(
            prompt, None, env_vars, WORK_ROOT, DATA_DIR,
            allow_bash=allow_bash, log=log.info)
        if ok:
            return True
        backoff = RATE_LIMIT_BACKOFF[min(attempt - 1, len(RATE_LIMIT_BACKOFF) - 1)]
        log.warning("%s failed (attempt %d/%d), retrying in %ds",
                    label, attempt, max_retries, backoff)
        await asyncio.sleep(backoff)
    log.error("All %d %s attempts exhausted", max_retries, label)
    return False


async def _run_worker_claude_sdk(prompt, label, env_vars, max_retries):
    """Legacy path: claude-agent-sdk (bidirectional ClaudeSDKClient)."""
    options = _sdk_options(env_vars)

    def on_stderr(line):
        if line.strip():
            log.info("SDK stderr (%s): %s", label, line.strip()[:300])
    options.stderr = on_stderr

    for attempt in range(1, max_retries + 1):
        log.info("Starting %s attempt %d/%d", label, attempt, max_retries)
        log.info("Prompt: %s", prompt[:200])
        try:
            async with ClaudeSDKClient(options=options) as client:
                await client.query(prompt)
                async for message in client.receive_response():
                    mtype = type(message).__name__
                    if mtype == "AssistantMessage":
                        for block in getattr(message, "content", None) or []:
                            if getattr(block, "text", "") and block.text.strip():
                                log.info("Assistant (%s): %s", label, block.text.strip()[:200])
                    elif mtype == "ResultMessage":
                        errors = getattr(message, "errors", None)
                        is_err = getattr(message, "is_error", False)
                        log.info("%s completed - is_error=%s, duration_ms=%s, turns=%s",
                                 label, is_err,
                                 getattr(message, "duration_ms", "?"),
                                 getattr(message, "num_turns", "?"))
                        if errors:
                            error_str = str(errors)
                            log.error("%s errors: %s", label, errors)
                            if is_rate_limit_error(error_str) and attempt < max_retries:
                                backoff = RATE_LIMIT_BACKOFF[min(attempt - 1, len(RATE_LIMIT_BACKOFF) - 1)]
                                log.warning("Rate limit in %s, retrying in %ds (attempt %d/%d)",
                                            label, backoff, attempt + 1, max_retries)
                                await asyncio.sleep(backoff)
                                break  # reconnect on the next attempt
                            return False
                        if is_err:
                            log.error("%s returned is_error=True", label)
                            return False
                        return True
        except Exception as e:
            error_str = str(e)
            log.error("%s failed (attempt %d/%d): %s", label, attempt, max_retries, e, exc_info=True)
            if is_rate_limit_error(error_str) and attempt < max_retries:
                backoff = RATE_LIMIT_BACKOFF[min(attempt - 1, len(RATE_LIMIT_BACKOFF) - 1)]
                await asyncio.sleep(backoff)
                continue
            return False

    log.error("All %d %s attempts exhausted", max_retries, label)
    return False


# ---------------------------------------------------------------------------
# SDK sync
# ---------------------------------------------------------------------------

def _get_changelog_fingerprint():
    """Return a fingerprint of CHANGELOG.md for change detection.

    Hashes the whole file. A prefix-only fingerprint would miss appended
    entries when the header alone exceeds the prefix length, falsely flagging
    successful syncs as failures and freezing cursors forever.
    """
    changelog = DATA_DIR / "CHANGELOG.md"
    if not changelog.exists():
        return ""
    try:
        return hashlib.sha256(changelog.read_bytes()).hexdigest()
    except Exception:
        return ""


async def run_sync(batch, digest_path, max_retries=3):
    """Sync an explicit commit range via claude-agent-sdk, with rate-limit retry."""
    base, head = batch.get("base", ""), batch.get("head", "")
    commits = batch.get("commits", [])
    n = len(commits)
    rng = "{}..{}".format(base, head) if base else head

    # Record the CHANGELOG fingerprint before sync for post-sync validation.
    changelog_before = _get_changelog_fingerprint()

    if base:
        log_out = git_out(["log", "--format=%h %s", rng])
    else:
        log_out = git_out(["log", "--format=%h %s", "-n", str(MAX_COMMIT_LINES), head])
    commit_lines = "\n".join(log_out.splitlines()[:MAX_COMMIT_LINES]) or "(no commits in range)"

    guidance_note = ""
    if batch.get("prompt"):
        guidance_note = (
            "\nUSER GUIDANCE for this sync (high-priority human context -- use it "
            "to focus, disambiguate, and prioritize):\n{p}\n".format(p=batch["prompt"])
        )

    digest_note = ""
    if digest_path is not None:
        digest_note = (
            "\nCONVERSATION DIGEST:\n"
            "Read {digest} -- new Claude Code conversation excerpts for this "
            "repository since the last sync (tool noise already stripped). "
            "Extract requirement background, design intent, and pitfalls; merge "
            "them into the affected domain docs. Skip excerpts unrelated to this "
            "repository's business. NEVER copy credentials, tokens, or pasted "
            "raw configs from the digest into the docs.\n"
        ).format(digest=str(digest_path).replace("\\", "/"))

    prompt = (
        "SYNC SCOPE -- exactly the {n} commit(s) in range `{rng}`:\n{lines}\n\n"
        "Inspect them with `git diff {rng}` and `git log {rng}`. NEVER use "
        "HEAD~N (history has merge commits); always use the explicit range above.\n\n"
        "CRITICAL INSTRUCTIONS - FOLLOW THESE RULES:\n"
        "1. You are running in an automated pipeline. There is NO human to approve anything.\n"
        "2. Edit and Write ARE enabled and pre-approved (granted via the SDK permission "
        "callback). Use them directly, as the ONLY way to change files under `{rel}/`. "
        "Do NOT ask permission.\n"
        "3. If an Edit is ever rejected, Read the target file first and retry Edit. Do NOT "
        "fall back to shell/Python file-writing -- it is slow and error-prone.\n"
        "4. NEVER create scratch or temp files, and NEVER write anything in the repo root. "
        "If you truly need scratch, use an ABSOLUTE path under `{rel}/.tmp/` and delete it when done.\n"
        "5. Map changed files to domains via `{rel}/.sync/SYNC-WORKFLOW.md`.\n"
        "6. After updating docs, you MUST update `{rel}/CHANGELOG.md` with the new sync entry.\n"
        "7. You ARE the automated sync worker. Do NOT run auto_sync.py and do NOT "
        "re-invoke any sync command -- perform the sync yourself by editing files directly.\n"
        "8. Start applying changes NOW. Do not explain what you plan to do -- just do it.\n"
        "{guidance_note}{digest_note}"
    ).format(name=SKILL_NAME, n=n, rng=rng, lines=commit_lines, rel=DATA_REL,
             guidance_note=guidance_note, digest_note=digest_note)

    ok = await _run_worker(prompt, "sync [{}]".format(rng), max_retries)
    if not ok:
        return False

    # Validate: CHANGELOG must have been updated.
    changelog_after = _get_changelog_fingerprint()
    if changelog_after == changelog_before:
        log.warning("CHANGELOG.md was NOT modified during sync -- "
                    "agent may have failed to write files")
        return False
    log.info("CHANGELOG.md verified as updated after sync")
    return True


# ---------------------------------------------------------------------------
# Post-sync size budget: split oversized docs
# ---------------------------------------------------------------------------

def find_oversized_docs():
    """Return [(path, size)] for domain docs over MAX_DOC_BYTES, largest first.

    Skips the skill's own dot-directories (.scripts/.sync/.state/.tmp) and the
    control files (SKILL.md, coverage.md, CHANGELOG.md, index.md) -- only real
    domain docs are candidates for splitting.
    """
    oversized = []
    for md in DATA_DIR.rglob("*.md"):
        rel_parts = md.relative_to(DATA_DIR).parts
        if any(part.startswith(".") for part in rel_parts):
            continue
        if md.name in CONTROL_DOCS:
            continue
        try:
            size = md.stat().st_size
        except OSError:
            continue
        if size > MAX_DOC_BYTES:
            oversized.append((md, size))
    oversized.sort(key=lambda t: t[1], reverse=True)
    return oversized


async def _split_one(path, size, sem, max_retries):
    """Split ONE oversized doc in its own worker (bounded by `sem`).

    Scoped to the file's OWN domain directory + the new sibling docs it creates.
    It must NOT touch shared files (SKILL.md / coverage.md / index.md), so
    concurrent per-file workers can never race on a shared write.
    """
    rel = path.relative_to(WORK_ROOT).as_posix()
    domain_dir = path.parent.relative_to(WORK_ROOT).as_posix()
    max_kb = MAX_DOC_BYTES // 1000
    target_kb = SPLIT_TARGET_BYTES // 1000
    prompt = (
        "Split ONE oversized business-logic doc into smaller focused docs.\n"
        "TARGET FILE: `{rel}` (~{kb} KB, over the {max_kb}KB budget).\n\n"
        "CRITICAL INSTRUCTIONS - FOLLOW THESE RULES:\n"
        "1. Automated pipeline, NO human. Edit and Write are pre-approved (SDK "
        "permission callback) -- use them directly. Do NOT ask permission, do NOT "
        "use shell/Python to write files, and NEVER create temp files or write in "
        "the repo root. Do NOT run auto_sync.py.\n"
        "2. Split `{rel}` on SECTION BOUNDARIES (never mid-section, mid-code-fence, "
        "or mid-table) into SUB-DOMAIN docs: group the moved sections by the "
        "sub-domain they describe (a module, a flow, an integration, a table "
        "family) and write each group to a NEW plain-named doc in the SAME "
        "directory `{dir}/` (e.g. `{dir}/<sub-domain>.md`). Each new doc keeps the "
        "sub-domain shape where the content supports it: Responsibility, Entry "
        "Points, Core Flow, Call Chain, Business Rules, Key Symbols, Database, "
        "Pitfalls, Related.\n"
        "3. Keep `{rel}` itself as a lean MAP: quick index, cross-domain "
        "interfaces, navigation. It MUST carry a `## Sub-domains` table with one "
        "row per new doc (`| Doc | Scope | Owns |`) -- that table is how readers "
        "and the next sync find the moved content.\n"
        "4. MOVE content, never drop or summarize it. The union of `{rel}` + the new "
        "docs must contain everything the original had.\n"
        "5. Each resulting file MUST end up under {max_kb}KB (aim <= {target_kb}KB).\n"
        "6. Touch ONLY `{rel}` and the NEW sibling docs you create in `{dir}/`. Do NOT "
        "edit SKILL.md, coverage.md, index.md, or any file outside `{dir}/` -- the "
        "top-level navigation is reconciled separately on the next sync.\n"
        "7. Do NOT create '.'-prefixed directories. Start NOW -- just do it.\n"
    ).format(rel=rel, kb=size // 1000, max_kb=max_kb, target_kb=target_kb, dir=domain_dir)
    async with sem:
        return await _run_worker(prompt, "split {}".format(path.name), max_retries)


async def run_split(oversized_files, max_retries=3):
    """Split each oversized doc in its OWN worker, concurrently.

    Per-file (not one worker for all files) so wall-clock is the slowest single
    file, not the sum, and each worker keeps a small, focused context. Workers are
    scoped to their own domain directory and never touch shared files, so
    concurrent writes cannot race. Bounded to SPLIT_CONCURRENCY concurrent workers.
    Top-level nav/coverage are intentionally left to the next sync (kept out of the
    parallel workers to avoid a shared-write race).
    """
    sem = asyncio.Semaphore(SPLIT_CONCURRENCY)
    results = await asyncio.gather(
        *[_split_one(p, size, sem, max_retries) for p, size in oversized_files],
        return_exceptions=True,
    )
    ok = True
    for (p, _size), r in zip(oversized_files, results):
        if isinstance(r, BaseException):
            log.error("Split worker for %s raised: %s", p.name, r)
            ok = False
        elif r is not True:
            log.error("Split worker for %s did not succeed", p.name)
            ok = False
    if ok:
        log.info("All %d file(s) split; top-level nav/coverage will reconcile on next sync.",
                 len(oversized_files))
    return ok


def enforce_size_budget():
    """Split any doc over the size budget. Runs regardless of sync outcome --
    doc size is a standing invariant. Lives in the single consumer, so git pull,
    git push, and manual sync all get the same enforcement."""
    oversized = find_oversized_docs()
    budget_kb = MAX_DOC_BYTES // 1000
    if not oversized:
        log.info("All docs within %dKB budget; no split needed.", budget_kb)
        return
    log.info("%d doc(s) over %dKB budget: %s", len(oversized), budget_kb,
             ", ".join("{}={}KB".format(p.name, s // 1000) for p, s in oversized))
    try:
        if asyncio.run(run_split(oversized)):
            still = find_oversized_docs()
            if still:
                log.warning("After split, %d doc(s) still over budget: %s", len(still),
                            ", ".join("{}={}KB".format(p.name, s // 1000) for p, s in still))
            else:
                log.info("All docs within %dKB budget after split.", budget_kb)
        else:
            log.error("Doc-split step failed; oversized docs remain.")
    except Exception as e:
        log.error("Doc-split step raised: %s", e, exc_info=True)


# ---------------------------------------------------------------------------
# Consumer main loop
# ---------------------------------------------------------------------------

def run_consumer():
    """Run as the consumer: guard, batch-drain, digest, sync once, split."""
    # Security guard: refuse to run if a .env secret is exposed.
    guard_rc = ensure_env_ignored.main(DATA_DIR)
    if guard_rc != 0:
        log.error(".env safety check failed (rc=%d); aborting sync to protect secrets", guard_rc)
        return False

    # Wait for more triggers to accumulate (e.g. during a rebase).
    log.info("Consumer waiting %ds for batch window...", BATCH_WINDOW)
    time.sleep(BATCH_WINDOW)

    jobs = queue_drain()
    if not jobs:
        log.info("Queue empty after drain; enforcing size budget only.")
        enforce_size_budget()
        return True

    batch = merge_jobs(jobs)
    log.info("Processing batch: %d job(s), %d commit(s) [%s..%s], from=%s%s",
             len(jobs), len(batch["commits"]),
             (batch["base"] or "")[:9], (batch["head"] or "")[:9],
             batch["from"], " +prompt" if batch.get("prompt") else "")

    # Zero-LLM pre-pass: digest new conversation content since the cursors.
    cursors = digest_transcripts.load_cursors(STATE_DIR)
    source = os.environ.get("TRANSCRIPT_SOURCE") or "auto"
    digest_text, new_cursors = digest_transcripts.build_digest(WORK_ROOT, cursors, source=source)
    digest_path = None
    if digest_text:
        digest_path = TMP_DIR / "digest-pending.txt"
        digest_path.write_text(digest_text, encoding="utf-8")
        log.info("Conversation digest: %d bytes, %d session(s)",
                 len(digest_text), digest_text.count("## Session "))
    else:
        log.info("No new conversation content since last sync")

    success = asyncio.run(run_sync(batch, digest_path))
    if not success:
        log.error("Auto-sync FAILED for batch of %d job(s)", len(jobs))
    else:
        # Advance cursors + record completion only on success so failures retry.
        digest_transcripts.save_cursors(STATE_DIR, new_cursors)
        record_complete(batch)
        if digest_path is not None:
            digest_path.unlink(missing_ok=True)
        log.info("Auto-sync completed successfully for %d commit(s)", len(batch["commits"]))

    enforce_size_budget()
    return success


# ---------------------------------------------------------------------------
# Subcommands: state / record
# ---------------------------------------------------------------------------

def cmd_state():
    """Print JSON: last synced head, whether a consumer is active, pending count.

    Used by the interactive `manual` path to check the lock and pick a base.
    """
    st = {
        "last_head": last_complete_head(),
        "head": rev_parse("HEAD"),
        "lock_busy": consumer_is_active(),
        "pending": len(_read_jobs(QUEUE_FILE)),
    }
    print(json.dumps(st, ensure_ascii=False))


def cmd_record(args):
    """Append a completion record (for an interactive manual sync).

    The model edits the docs itself, then calls this so the sync state stays
    consistent -- bookkeeping always lives in one place (this script).
    """
    head = rev_parse(args.head or "HEAD")
    base = (rev_parse(args.base) if args.base else "") or last_complete_head() or _fallback_base(head)
    commits = rev_list(base, head)
    batch = {
        "from": args.from_ or "manual-inline",
        "base": base,
        "head": head,
        "commits": commits,
        "prompt": args.prompt or "",
    }
    record_complete(batch)
    print("recorded {} commit(s) {}..{}".format(len(commits), (base or "")[:9], (head or "")[:9]))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args(argv):
    p = argparse.ArgumentParser(prog="auto_sync.py")
    p.add_argument("command", nargs="?", default="post-merge",
                   help="post-merge | pre-push | manual | record | state")
    p.add_argument("--base", help="explicit base commit (exclusive lower bound of the range)")
    p.add_argument("--head", help="explicit head commit (default HEAD)")
    p.add_argument("--from", dest="from_", help="provenance label for a `record` completion")
    p.add_argument("--prompt", help="extra human guidance passed through to the sync worker")
    return p.parse_args(argv)


def main():
    args = parse_args(sys.argv[1:])
    cmd = args.command

    # Read-only / bookkeeping subcommands never take the consumer lock.
    if cmd == "state":
        cmd_state()
        return
    if cmd == "record":
        cmd_record(args)
        return

    log.info("=" * 60)
    log.info("Triggered by %s (PID %d)", cmd, os.getpid())

    # Step 1: capture the exact commit range and enqueue it (hash-deduped).
    job = capture_job(cmd, args)
    queue_push(job)

    # Step 2: try to become the consumer.
    if not try_become_consumer():
        log.info("Deferred to existing consumer")
        sys.exit(0)

    heartbeat_stop = threading.Event()
    start_heartbeat(heartbeat_stop)
    try:
        success = run_consumer()
        log.info("Auto-sync finished: success=%s", success)
        sys.exit(0 if success else 1)
    finally:
        heartbeat_stop.set()
        release_consumer()


if __name__ == "__main__":
    main()
