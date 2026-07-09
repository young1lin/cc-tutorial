"""
Build a compact text digest of new Claude Code conversation content.

Zero-LLM pre-pass used by auto_sync.py: reads the project's transcripts from
~/.claude/projects/<munged-path>/*.jsonl, keeps user text and assistant text
(where requirement background and pitfalls live), drops tool calls/results
(the bulk of the bytes), and tracks per-file line cursors so each sync only
ever processes new content.
"""

import json
from pathlib import Path

# Sessions whose first user message starts with one of these are our own
# automated sync runs; digesting them would feed the agent its own output.
SYNC_MARKERS = ("/business-logic sync",)

# User-message payloads that are command wrappers or system noise.
SKIP_PREFIXES = (
    "<local-command-", "<command-name>", "<local-command-stdout",
    "[Request interrupted by user]", "[System]",
    "This session is being continued",
)

MAX_DIGEST_BYTES = 80_000
MAX_MESSAGE_CHARS = 2_000

CURSOR_FILE = "cursors.json"


def transcript_dir_for(project_root):
    """Map a project path to its Claude Code transcript directory."""
    name = str(project_root).replace(":", "-").replace("\\", "-").replace("/", "-")
    return Path.home() / ".claude" / "projects" / name


def load_cursors(state_dir):
    """Read cursors.json from state_dir; empty dict if absent or corrupt."""
    path = Path(state_dir) / CURSOR_FILE
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_cursors(state_dir, cursors):
    """Write cursors.json to state_dir."""
    path = Path(state_dir) / CURSOR_FILE
    path.write_text(json.dumps(cursors, ensure_ascii=False, indent=0), encoding="utf-8")


def _text_of(content):
    """Extract plain text from a message content (string or block list)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(p for p in parts if p)
    return ""


def _is_own_sync_session(lines):
    """True if the session's first user message is an automated sync prompt."""
    for raw in lines[:20]:
        try:
            data = json.loads(raw)
        except ValueError:
            continue
        if data.get("type") == "user":
            text = _text_of(data.get("message", {}).get("content", ""))
            return text.lstrip().startswith(SYNC_MARKERS)
    return False


def _digest_lines(lines):
    """Yield 'USER:'/'ASSISTANT:' entries from raw jsonl lines."""
    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except ValueError:
            continue
        kind = data.get("type", "")
        if kind not in ("user", "assistant"):
            continue
        text = _text_of(data.get("message", {}).get("content", "")).strip()
        if not text or text.startswith(SKIP_PREFIXES):
            continue
        if len(text) > MAX_MESSAGE_CHARS:
            text = text[:MAX_MESSAGE_CHARS] + " [...]"
        yield "{}: {}".format("USER" if kind == "user" else "ASSISTANT", text)


def build_digest(project_root, cursors, max_bytes=MAX_DIGEST_BYTES, transcript_dir=None):
    """Return (digest_text, new_cursors) for content beyond the cursors."""
    tdir = Path(transcript_dir) if transcript_dir else transcript_dir_for(project_root)
    new_cursors = dict(cursors)
    if not tdir.exists():
        return "", new_cursors

    chunks = []
    for f in sorted(tdir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime):
        if "subagents" in str(f):
            continue
        try:
            lines = f.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        start = int(cursors.get(f.name, 0))
        new_cursors[f.name] = len(lines)
        if len(lines) <= start:
            continue
        if _is_own_sync_session(lines):
            continue
        entries = list(_digest_lines(lines[start:]))
        if entries:
            chunks.append("## Session {}\n{}".format(f.stem, "\n".join(entries)))

    digest = "\n\n".join(chunks)
    encoded = digest.encode("utf-8")
    if len(encoded) > max_bytes:
        tail = encoded[-max_bytes:].decode("utf-8", errors="ignore")
        digest = "[digest truncated to the most recent {} bytes]\n{}".format(max_bytes, tail)
    return digest, new_cursors
