"""
Git hook worker: auto-sync business-logic docs after git pull / push.

Usage:
    python auto_sync.py post-merge     # triggered after git pull
    python auto_sync.py pre-push       # triggered before git push

Architecture: file-based queue + single consumer.
Every hook trigger appends to a queue file. Only one consumer process runs
at a time, enforced by an atomic O_EXCL PID lock plus a heartbeat that keeps
long syncs from being mistaken for dead consumers. The consumer batches all
pending triggers, builds a zero-LLM conversation digest, then runs ONE
claude-agent-sdk call (permission_mode="bypassPermissions") that syncs all
commits since the CHANGELOG hash AND merges the digest into the unit docs.

The project is resolved from the current working directory (git runs hooks
from the repo top level). The skill name is fixed ("business-logic"); the
engine may live anywhere (vendored under the data dir, or
~/.claude/business-logic/bin). State lives in <project>/.claude/business-logic/state/.
"""

import asyncio
import json
import logging
import os
import hashlib
import re
import subprocess
import sys
import threading
import time
import ctypes
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions, query

# Make the sibling ensure_env_ignored module importable.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ensure_env_ignored  # noqa: E402
import digest_transcripts  # noqa: E402


def find_git_root(start):
    """Walk up from `start` until a directory containing `.git` is found."""
    start = Path(start).resolve()
    for candidate in [start, *start.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None


# Root resolution: the project is the git repository containing the CURRENT
# WORKING DIRECTORY. Git runs hooks from the repo top level, so cwd is correct
# in hooks; run manual invocations from inside the target repo. The engine may
# live anywhere (vendored in the repo, or ~/.claude/business-logic/bin).
PROJECT_ROOT = find_git_root(Path.cwd())

# The slash-command name of the skill (fixed; owned by the plugin).
SKILL_NAME = "business-logic"

# Per-project data directory: docs and state live in the repo, never in the plugin.
DATA_REL = ".claude/business-logic"

# Global-mode engine directory (stable across plugin updates); also the
# fallback location for .env.
GLOBAL_ENGINE_DIR = Path.home() / ".claude" / "business-logic"

if PROJECT_ROOT is None:
    print("[auto_sync] Not inside a git repository; nothing to sync.", file=sys.stderr)
    sys.exit(0)

DATA_DIR = PROJECT_ROOT / ".claude" / "business-logic"
STATE_DIR = DATA_DIR / "state"

if not DATA_DIR.exists():
    # Project not initialized for business-logic; stay silent and inert.
    sys.exit(0)

# Change to the project root so git commands and skill discovery both work.
os.chdir(str(PROJECT_ROOT))
STATE_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = STATE_DIR / "auto_sync.log"
QUEUE_FILE = STATE_DIR / "auto_sync_queue.json"
PID_FILE = STATE_DIR / "auto_sync.pid"

# Max heartbeat staleness in seconds; beyond this a consumer is considered dead
# or hung. The live consumer refreshes the PID file mtime every
# HEARTBEAT_INTERVAL seconds, so even a multi-hour sync stays fresh.
LOCK_TIMEOUT = 600

# How often the consumer touches the PID file to prove it is still alive.
HEARTBEAT_INTERVAL = 30

# Batch window: after becoming consumer, wait this long for more hooks to queue.
BATCH_WINDOW = 3

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
# Queue: file-based append + batch drain
# Uses an O_EXCL lock file for safe concurrent writes on Windows.
# Drain uses an atomic rename to prevent data loss on crash.
# ---------------------------------------------------------------------------

QUEUE_LOCK = STATE_DIR / "auto_sync_queue.lock"


def _acquire_queue_lock(retries=20, base_delay=0.02):
    """Acquire an exclusive lock via O_CREAT|O_EXCL (atomic on NTFS)."""
    for attempt in range(retries):
        try:
            fd = os.open(str(QUEUE_LOCK), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            return fd
        except FileExistsError:
            # Jittered backoff: 20-80ms per attempt, ~1s max total.
            delay = base_delay + (os.getpid() % 50) * 0.001 + attempt * 0.01
            time.sleep(delay)
    return None


def _release_queue_lock(fd):
    """Release the queue lock."""
    try:
        os.close(fd)
    except OSError:
        pass
    try:
        QUEUE_LOCK.unlink(missing_ok=True)
    except OSError:
        pass


def queue_push(hook_type):
    """Append a trigger event to the queue file (concurrency-safe)."""
    entry = {"hook": hook_type, "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
    fd = _acquire_queue_lock()
    if fd is None:
        log.error("Failed to acquire queue lock for push, retrying with direct write")
        # Fallback: write directly (better than losing the trigger).
        try:
            data = json.loads(QUEUE_FILE.read_text(encoding="utf-8")) if QUEUE_FILE.exists() else []
            data.append(entry)
            QUEUE_FILE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            log.info("Queued %s via fallback (depth=%d)", hook_type, len(data))
        except Exception as e:
            log.error("Fallback queue push also failed: %s", e)
        return

    try:
        data = json.loads(QUEUE_FILE.read_text(encoding="utf-8")) if QUEUE_FILE.exists() else []
        data.append(entry)
        QUEUE_FILE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        log.info("Queued %s (depth=%d)", hook_type, len(data))
    except Exception as e:
        log.error("Failed to write queue: %s", e)
    finally:
        _release_queue_lock(fd)


def queue_drain():
    """Drain all pending items via an atomic rename (crash-safe).

    Holds QUEUE_LOCK across recovery + rename so a producer cannot interleave a
    read-modify-write between our rename and a new push (which would duplicate
    an already-drained item). Strategy: rename the queue file to a .processing
    file, then parse it. If the consumer crashes mid-processing, the
    .processing file is left behind and merged back on the next consumer start.
    """
    processing = QUEUE_FILE.with_suffix(".processing")

    fd = _acquire_queue_lock()
    if fd is None:
        log.error("Failed to acquire queue lock for drain; aborting drain")
        return []
    try:
        # Recovery: merge a leftover .processing file from a previous crash.
        if processing.exists():
            log.warning("Found stale .processing file, merging back into queue")
            _merge_into_queue_locked(processing)

        if not QUEUE_FILE.exists():
            return []
        # Atomic rename -- no partial state possible.
        QUEUE_FILE.rename(processing)
        data = json.loads(processing.read_text(encoding="utf-8"))
        processing.unlink()
        log.info("Drained %d items from queue", len(data))
        return data
    except FileNotFoundError:
        return []
    except Exception as e:
        log.error("Failed to drain queue: %s", e)
        # If rename succeeded but parse failed, do not lose data.
        if processing.exists():
            log.error("Preserving .processing file for manual recovery")
        return []
    finally:
        _release_queue_lock(fd)


def _merge_into_queue_locked(processing):
    """Merge a .processing file back into the queue.

    Caller MUST already hold QUEUE_LOCK. queue_drain acquires it once for the
    whole drain, so this helper does not re-acquire -- re-acquiring an O_EXCL
    lock we already own would deadlock.
    """
    try:
        existing = json.loads(QUEUE_FILE.read_text(encoding="utf-8")) if QUEUE_FILE.exists() else []
        leftover = json.loads(processing.read_text(encoding="utf-8"))
        merged = existing + leftover
        QUEUE_FILE.write_text(json.dumps(merged, ensure_ascii=False), encoding="utf-8")
        processing.unlink()
        log.info("Recovered %d items from .processing into queue", len(leftover))
    except Exception as e:
        log.error("Failed to merge .processing: %s", e)


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
    exists, its owner is honored while the process is alive and its heartbeat
    is fresh; otherwise the stale file is removed and creation is retried.
    Losing any race here is safe: the trigger is already queued and will be
    drained by whichever consumer won.
    """
    for _ in range(2):
        if _create_pid_file():
            log.info("Became consumer (PID %d)", os.getpid())
            return True

        try:
            pid = int(PID_FILE.read_text().strip())
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
            if PID_FILE.read_text().strip() == str(os.getpid()):
                PID_FILE.unlink()
                log.info("Released consumer role")
    except OSError as e:
        log.warning("Failed to release consumer PID: %s", e)


def start_heartbeat(stop_event):
    """Refresh the PID file mtime periodically while the consumer runs.

    Without this, a sync longer than LOCK_TIMEOUT would look stale and get
    taken over by the next trigger while still running. The thread stops when
    stop_event is set or when the PID file no longer belongs to this process.
    """
    def beat():
        while not stop_event.wait(HEARTBEAT_INTERVAL):
            try:
                if PID_FILE.read_text().strip() != str(os.getpid()):
                    return  # superseded; stop claiming liveness
                os.utime(str(PID_FILE), None)
            except OSError:
                return
    thread = threading.Thread(target=beat, daemon=True, name="pid-heartbeat")
    thread.start()
    return thread


# ---------------------------------------------------------------------------
# Rate-limit detection
# ---------------------------------------------------------------------------

def is_rate_limit_error(error_text):
    """Return True if an error message indicates rate limiting / transient error."""
    lower = error_text.lower()
    return any(pat in lower for pat in RATE_LIMIT_PATTERNS)


# ---------------------------------------------------------------------------
# Env loading
# ---------------------------------------------------------------------------

def load_env():
    """Load env vars from the project .env, falling back to the global one."""
    candidates = [
        DATA_DIR / "scripts" / ".env",
        GLOBAL_ENGINE_DIR / ".env",
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


# ---------------------------------------------------------------------------
# Commit counting
# ---------------------------------------------------------------------------

def get_last_sync_hash():
    """Extract the last synced commit hash from CHANGELOG.md."""
    changelog = DATA_DIR / "CHANGELOG.md"
    if not changelog.exists():
        return ""
    try:
        content = changelog.read_text(encoding="utf-8")
        # CHANGELOG uses newest-first: the latest sync entry sits directly under
        # the header (see data-skeleton/CHANGELOG.md), so the leftmost hash is
        # the most recent sync. re.search returns that first match.
        match = re.search(r"\b([0-9a-f]{7,12})\.\.", content)
        return match.group(1) if match else ""
    except Exception as e:
        log.warning("Failed to read CHANGELOG.md: %s", e)
        return ""


def get_commits_to_sync():
    """Calculate how many commits to sync: from the last CHANGELOG hash to HEAD."""
    last_hash = get_last_sync_hash()
    if not last_hash:
        # No previous sync; default to 5.
        log.info("No previous sync hash found, defaulting to 5 commits")
        return 5
    try:
        result = subprocess.run(
            ["git", "rev-list", "{}..HEAD".format(last_hash), "--count"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        count = max(1, int(result.stdout.strip() or "1"))
        log.info("Commits since last sync (%s): %d", last_hash, count)
        return count
    except Exception as e:
        log.warning("Failed to count commits: %s", e)
        return 1


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


async def run_sync(commit_count, digest_path, max_retries=3):
    """Run /<skill> sync using claude-agent-sdk, with rate-limit retry."""
    env_vars = load_env()

    # Record the CHANGELOG fingerprint before sync for post-sync validation.
    changelog_before = _get_changelog_fingerprint()
    log.info("CHANGELOG fingerprint before sync: %s", changelog_before[:80])

    digest_note = ""
    if digest_path is not None:
        digest_note = (
            "\nCONVERSATION DIGEST:\n"
            "Read {digest} -- new Claude Code conversation excerpts for this "
            "repository since the last sync (tool noise already stripped). "
            "Extract requirement background, design intent, and pitfalls; merge "
            "them into the affected unit docs. Skip excerpts unrelated to this "
            "repository's business. NEVER copy credentials, tokens, or pasted "
            "raw configs from the digest into the docs.\n"
        ).format(digest=str(digest_path).replace("\\", "/"))

    prompt = (
        "/{name} sync {count}\n\n"
        "CRITICAL INSTRUCTIONS - FOLLOW THESE RULES:\n"
        "1. You are running in an automated pipeline. There is NO human to approve anything.\n"
        "2. You MUST use the Edit and Write tools directly to update files under "
        "`{rel}/`. Do NOT ask for permission.\n"
        "3. Do NOT say 'I need permission' or 'please approve' or 'waiting for approval'. "
        "Just call the Edit/Write tools immediately.\n"
        "4. The `permission_mode` is `bypassPermissions` -- all file writes are pre-approved.\n"
        "5. After updating docs, you MUST update {rel}/CHANGELOG.md with the new sync entry.\n"
        "6. Start applying changes NOW. Do not explain what you plan to do -- just do it.\n"
        "{digest_note}"
    ).format(name=SKILL_NAME, count=commit_count, rel=DATA_REL, digest_note=digest_note)

    env_vars["BUSINESS_LOGIC_SYNC"] = "1"  # lets tooling identify our own sessions
    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        cwd=str(PROJECT_ROOT),
        env=env_vars,
        allowed_tools=[
            "Read", "Glob", "Grep", "Bash",
            "Edit({rel}/**)".format(rel=DATA_REL),
            "Write({rel}/**)".format(rel=DATA_REL),
        ],
    )

    def on_stderr(line):
        if line.strip():
            log.info("SDK stderr: %s", line.strip()[:300])

    options.stderr = on_stderr

    for attempt in range(1, max_retries + 1):
        log.info("Starting SDK sync attempt %d/%d: %d commits", attempt, max_retries, commit_count)
        log.info("Prompt: %s", prompt[:200])

        try:
            async for message in query(prompt=prompt, options=options):
                msg_type = type(message).__name__
                log.info("SDK message: %s", msg_type)
                if msg_type == "ResultMessage":
                    log.info("Sync completed - is_error=%s, result=%s, stop_reason=%s, duration_ms=%s, turns=%s",
                             getattr(message, "is_error", "?"),
                             getattr(message, "result", "?")[:300],
                             getattr(message, "stop_reason", "?"),
                             getattr(message, "duration_ms", "?"),
                             getattr(message, "num_turns", "?"))
                    errors = getattr(message, "errors", None)
                    if errors:
                        error_str = str(errors)
                        log.error("Sync errors: %s", errors)
                        if is_rate_limit_error(error_str) and attempt < max_retries:
                            backoff = RATE_LIMIT_BACKOFF[min(attempt - 1, len(RATE_LIMIT_BACKOFF) - 1)]
                            log.warning("Rate limit detected, retrying in %ds (attempt %d/%d)",
                                        backoff, attempt + 1, max_retries)
                            await asyncio.sleep(backoff)
                            break
                        return False

                    # Validate: CHANGELOG must have been updated.
                    changelog_after = _get_changelog_fingerprint()
                    if changelog_after == changelog_before:
                        log.warning("CHANGELOG.md was NOT modified during sync -- "
                                    "agent may have failed to write files")
                        return False
                    log.info("CHANGELOG.md verified as updated after sync")
                    return True
                elif msg_type == "AssistantMessage":
                    if hasattr(message, "content"):
                        for block in message.content:
                            if hasattr(block, "text") and block.text.strip():
                                log.info("Assistant: %s", block.text.strip()[:200])
        except Exception as e:
            error_str = str(e)
            log.error("SDK sync failed (attempt %d/%d): %s", attempt, max_retries, e, exc_info=True)
            if is_rate_limit_error(error_str) and attempt < max_retries:
                backoff = RATE_LIMIT_BACKOFF[min(attempt - 1, len(RATE_LIMIT_BACKOFF) - 1)]
                log.warning("Rate limit exception, retrying in %ds (attempt %d/%d)",
                            backoff, attempt + 1, max_retries)
                await asyncio.sleep(backoff)
                continue
            return False

    log.error("All %d retry attempts exhausted", max_retries)
    return False


# ---------------------------------------------------------------------------
# Consumer main loop
# ---------------------------------------------------------------------------

def run_consumer():
    """Run as the consumer: guard, batch-drain, digest, then sync once."""
    # Security guard: refuse to run if a .env secret is exposed. This catches the
    # case where the user created .env after install without re-running install.
    guard_rc = ensure_env_ignored.main(DATA_DIR)
    if guard_rc != 0:
        log.error(".env safety check failed (rc=%d); aborting sync to protect secrets", guard_rc)
        return False

    # Wait for more hooks to accumulate (e.g. during a rebase).
    log.info("Consumer waiting %ds for batch window...", BATCH_WINDOW)
    time.sleep(BATCH_WINDOW)

    # Drain all pending items.
    items = queue_drain()
    if not items:
        log.info("Queue empty after drain, nothing to do")
        return True

    hook_summary = ", ".join("{}({})".format(item["hook"], item["ts"]) for item in items)
    log.info("Processing batch of %d triggers: %s", len(items), hook_summary)

    # Zero-LLM pre-pass: digest new conversation content since the cursors.
    cursors = digest_transcripts.load_cursors(STATE_DIR)
    digest_text, new_cursors = digest_transcripts.build_digest(PROJECT_ROOT, cursors)
    digest_path = None
    if digest_text:
        digest_path = STATE_DIR / "digest-pending.txt"
        digest_path.write_text(digest_text, encoding="utf-8")
        log.info("Conversation digest: %d bytes, %d session(s)",
                 len(digest_text), digest_text.count("## Session "))
    else:
        log.info("No new conversation content since last sync")

    # Calculate commits to sync from CHANGELOG (auto-dedup).
    commit_count = get_commits_to_sync()

    # Run the sync: one SDK round covering both the diff and the digest.
    success = asyncio.run(run_sync(commit_count, digest_path))
    if not success:
        log.error("Auto-sync FAILED for batch of %d items", len(items))
    else:
        # Advance conversation cursors only on success so failed content retries.
        digest_transcripts.save_cursors(STATE_DIR, new_cursors)
        if digest_path is not None:
            digest_path.unlink(missing_ok=True)
        log.info("Auto-sync completed successfully for %d commits", commit_count)

    return success


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    hook_type = sys.argv[1] if len(sys.argv) > 1 else "post-merge"
    log.info("=" * 60)
    log.info("Triggered by %s (PID %d)", hook_type, os.getpid())

    # Step 1: always enqueue the trigger.
    queue_push(hook_type)

    # Step 2: try to become the consumer.
    if not try_become_consumer():
        # Another consumer is running; our trigger stays queued and will be
        # drained by the next consumer run.
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
