# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Build a compact text digest of new conversation content.

Zero-LLM pre-pass used by auto_sync.py: reads this project's transcripts from
whichever coding CLI produced them, keeps user text and assistant text (where
requirement background and pitfalls live), drops tool calls/results (the bulk of
the bytes), and tracks per-session cursors so each sync only ever processes new
content.

Transcript sources are pluggable. Three ship out of the box:
  - claude-code : ~/.claude/projects/<munged>/*.jsonl
  - codex       : ~/.codex/sessions/YYYY/MM/*.jsonl
  - opencode    : ~/.local/share/opencode/opencode.db (SQLite)

Selection: pass `source=` explicitly, or leave it to auto-detect (the first
source that has records for this project wins; configurable via the
TRANSCRIPT_SOURCE env var). Sources can also be merged (source="all") so teams
that use more than one CLI still capture every conversation.

All sources emit the same digest shape -- one block per session:
    ## Session <id>
    USER: ...
    ASSISTANT: ...
"""

import json
import sqlite3
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


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _same_path(a, b):
    """True if two path strings refer to the same directory (cross-CLI robust).

    Each CLI stores the project path differently (claude munges it into a dir
    name; codex/opencode store a literal cwd that may use / or \\). Normalize
    both to a resolved posix form, lower-cased, before comparing.
    """
    def norm(p):
        try:
            return Path(p).resolve().as_posix().lower()
        except Exception:
            return str(p).replace("\\", "/").lower()
    return norm(a) == norm(b)


def _clean_text(text):
    """Trim, skip command/system noise, cap length. Return '' if it should drop."""
    text = text.strip()
    if not text or text.startswith(SKIP_PREFIXES):
        return ""
    if len(text) > MAX_MESSAGE_CHARS:
        text = text[:MAX_MESSAGE_CHARS] + " [...]"
    return text


# ---------------------------------------------------------------------------
# Source registry
# ---------------------------------------------------------------------------

SOURCES = {}


def register_source(name, source):
    SOURCES[name] = source


def get_source(project_root, configured=None):
    """Return the active source: configured name, auto-detected, or claude-code."""
    if configured and configured != "auto":
        if configured == "all":
            return MultiSource()
        src = SOURCES.get(configured)
        if src is not None:
            return src
    # Auto-detect: first source with records for THIS project wins.
    for name in ("claude-code", "opencode", "codex"):
        src = SOURCES.get(name)
        if src is None:
            continue
        try:
            if src.has_project(project_root):
                return src
        except Exception:
            continue
    return SOURCES["claude-code"]  # safe default: inert if no records


class MultiSource:
    """Merge every available source into one digest (for multi-CLI teams)."""

    name = "all"

    def has_project(self, project_root):
        return any(s.has_project(project_root) for s in SOURCES.values())

    def collect(self, project_root, since_map):
        out = []
        new = dict(since_map)
        for name, src in SOURCES.items():
            try:
                entries, updated = src.collect(project_root, since_map.get(name, {}))
            except Exception:
                continue
            out.extend(entries)
            new[name] = updated
        return out, new


# ---------------------------------------------------------------------------
# Claude Code  --  ~/.claude/projects/<munged>/*.jsonl
# ---------------------------------------------------------------------------

class ClaudeCodeSource:
    name = "claude-code"

    def dir_for(self, project_root):
        """Map a project path to its Claude Code transcript directory."""
        name = str(project_root).replace(":", "-").replace("\\", "-").replace("/", "-")
        return Path.home() / ".claude" / "projects" / name

    def has_project(self, project_root):
        return self.dir_for(project_root).exists()

    def _text_of(self, content):
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

    def _is_own_sync(self, lines):
        """True if the session's first user message is an automated sync prompt."""
        for raw in lines[:20]:
            try:
                data = json.loads(raw)
            except ValueError:
                continue
            if data.get("type") == "user":
                text = self._text_of(data.get("message", {}).get("content", ""))
                return text.lstrip().startswith(SYNC_MARKERS)
        return False

    def collect(self, project_root, since_map, override_dir=None):
        """Return (entries, new_since_map) for content beyond the cursors."""
        tdir = Path(override_dir) if override_dir else self.dir_for(project_root)
        new_map = dict(since_map)
        if not tdir.exists():
            return [], new_map

        chunks = []
        for f in sorted(tdir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime):
            if "subagents" in str(f):
                continue
            try:
                lines = f.read_text(encoding="utf-8", errors="ignore").splitlines()
            except OSError:
                continue
            start = int(since_map.get(f.name, 0))
            new_map[f.name] = len(lines)
            if len(lines) <= start:
                continue
            if self._is_own_sync(lines):
                continue
            entries = []
            for raw in lines[start:]:
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
                text = _clean_text(self._text_of(data.get("message", {}).get("content", "")))
                if text:
                    entries.append("{}: {}".format(
                        "USER" if kind == "user" else "ASSISTANT", text))
            if entries:
                chunks.append("## Session {}\n{}".format(f.stem, "\n".join(entries)))
        return chunks, new_map


register_source("claude-code", ClaudeCodeSource())

# Back-compat alias used by older callers / tests.
def transcript_dir_for(project_root):
    return SOURCES["claude-code"].dir_for(project_root)


# ---------------------------------------------------------------------------
# Codex CLI  --  ~/.codex/sessions/YYYY/MM/*.jsonl
#   line: {"timestamp", "type": "session_meta"|"response_item", "payload": {...}}
# ---------------------------------------------------------------------------

class CodexSource:
    name = "codex"
    SESSIONS_DIR = Path.home() / ".codex" / "sessions"

    def has_project(self, project_root):
        return self.SESSIONS_DIR.exists() and bool(self._matching_files(project_root))

    def _matching_files(self, project_root):
        """Session jsonl files whose session_meta.payload.cwd matches."""
        if not self.SESSIONS_DIR.exists():
            return []
        out = []
        for f in self.SESSIONS_DIR.rglob("*.jsonl"):
            cwd = self._read_cwd(f)
            if cwd and _same_path(cwd, project_root):
                out.append(f)
        out.sort(key=lambda p: p.stat().st_mtime)
        return out

    def _read_cwd(self, f):
        """Read the session_meta line's cwd (it is the first line of the file)."""
        try:
            with open(f, "r", encoding="utf-8", errors="ignore") as fh:
                first = fh.readline()
            data = json.loads(first)
            if data.get("type") == "session_meta":
                return data.get("payload", {}).get("cwd", "")
        except Exception:
            pass
        return ""

    def _is_own_sync(self, lines):
        """Skip a session that is one of our automated sync runs."""
        for raw in lines[:40]:
            try:
                data = json.loads(raw)
            except ValueError:
                continue
            if data.get("type") != "response_item":
                continue
            payload = data.get("payload", {})
            if payload.get("type") != "message" or payload.get("role") != "user":
                continue
            for block in payload.get("content", []):
                if isinstance(block, dict):
                    text = (block.get("text") or "").lstrip()
                    if text.startswith(SYNC_MARKERS):
                        return True
        return False

    def collect(self, project_root, since_map):
        new_map = dict(since_map)
        chunks = []
        for f in self._matching_files(project_root):
            try:
                lines = f.read_text(encoding="utf-8", errors="ignore").splitlines()
            except OSError:
                continue
            start = int(since_map.get(f.name, 0))
            new_map[f.name] = len(lines)
            if len(lines) <= start:
                continue
            if self._is_own_sync(lines):
                continue
            entries = []
            for raw in lines[start:]:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    data = json.loads(raw)
                except ValueError:
                    continue
                if data.get("type") != "response_item":
                    continue
                payload = data.get("payload", {})
                if payload.get("type") != "message":
                    continue
                role = payload.get("role", "")
                if role not in ("user", "assistant"):
                    continue  # drop developer/system messages
                text_parts = []
                for block in payload.get("content", []):
                    if isinstance(block, dict) and block.get("text"):
                        text_parts.append(block["text"])
                text = _clean_text("\n".join(text_parts))
                if text:
                    entries.append("{}: {}".format(
                        "USER" if role == "user" else "ASSISTANT", text))
            if entries:
                chunks.append("## Session {}\n{}".format(f.stem, "\n".join(entries)))
        return chunks, new_map


register_source("codex", CodexSource())


# ---------------------------------------------------------------------------
# opencode  --  ~/.local/share/opencode/opencode.db (SQLite)
#   session(directory) -> message(role, time_created) -> part(type==text, text)
# ---------------------------------------------------------------------------

class OpencodeSource:
    name = "opencode"

    def _db_candidates(self):
        home = Path.home()
        return [
            home / ".local" / "share" / "opencode" / "opencode.db",
            home / "AppData" / "Local" / "opencode" / "opencode.db",
        ]

    def _db(self):
        for p in self._db_candidates():
            if p.exists():
                return p
        return None

    def has_project(self, project_root):
        db = self._db()
        if db is None:
            return False
        try:
            c = sqlite3.connect("file:{}?mode=ro".format(db.as_posix()), uri=True, timeout=2)
            try:
                row = c.execute(
                    "SELECT 1 FROM session WHERE directory = ? LIMIT 1",
                    (Path(project_root).resolve().as_posix(),),
                ).fetchone()
                if row:
                    return True
                # Fallback: case-insensitive / slash-variant match.
                norm = Path(project_root).resolve().as_posix().lower()
                for (d,) in c.execute("SELECT DISTINCT directory FROM session"):
                    if d and d.replace("\\", "/").lower() == norm:
                        return True
                return False
            finally:
                c.close()
        except Exception:
            return False

    def _is_own_sync_title(self, title):
        return bool(title) and "business-logic sync" in title.lower()

    def collect(self, project_root, since_map):
        db = self._db()
        new_map = dict(since_map)
        if db is None:
            return [], new_map

        norm = Path(project_root).resolve().as_posix().lower()
        c = sqlite3.connect("file:{}?mode=ro".format(db.as_posix()), uri=True, timeout=2)
        try:
            sessions = c.execute(
                "SELECT id, title FROM session WHERE directory = ?", (norm,)
            ).fetchall()
            if not sessions:
                # slash/case-variant match
                rows = c.execute("SELECT id, title, directory FROM session").fetchall()
                sessions = [(r[0], r[1]) for r in rows
                            if r[2] and r[2].replace("\\", "/").lower() == norm]
            chunks = []
            for sid, title in sessions:
                if self._is_own_sync_title(title):
                    continue
                since = int(since_map.get(sid, 0))
                msgs = c.execute(
                    "SELECT id, time_created FROM message "
                    "WHERE session_id = ? AND time_created > ? ORDER BY time_created",
                    (sid, since),
                ).fetchall()
                if not msgs:
                    continue
                entries = []
                max_ts = since
                for mid, ts in msgs:
                    if ts and ts > max_ts:
                        max_ts = ts
                    role = None
                    try:
                        mdata = json.loads(
                            c.execute("SELECT data FROM message WHERE id = ?", (mid,)).fetchone()[0])
                        role = mdata.get("role")
                    except Exception:
                        continue
                    if role not in ("user", "assistant"):
                        continue
                    parts = c.execute(
                        "SELECT data FROM part WHERE message_id = ? ORDER BY time_created",
                        (mid,),
                    ).fetchall()
                    text_parts = []
                    for (pdata,) in parts:
                        try:
                            pobj = json.loads(pdata)
                        except Exception:
                            continue
                        if pobj.get("type") == "text" and pobj.get("text"):
                            text_parts.append(pobj["text"])
                    text = _clean_text("\n".join(text_parts))
                    if text:
                        entries.append("{}: {}".format(
                            "USER" if role == "user" else "ASSISTANT", text))
                new_map[sid] = max_ts
                if entries:
                    chunks.append("## Session {}\n{}".format(sid, "\n".join(entries)))
            return chunks, new_map
        finally:
            c.close()


register_source("opencode", OpencodeSource())


# ---------------------------------------------------------------------------
# Cursor persistence (multi-source aware; migrates the old flat format)
# ---------------------------------------------------------------------------

def load_cursors(state_dir):
    """Read cursors.json; migrate the legacy flat {file: count} layout."""
    path = Path(state_dir) / CURSOR_FILE
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    # Legacy layout: {filename: <int>}. Re-key under the claude-code source.
    if raw and all(isinstance(v, int) for v in raw.values()):
        return {"claude-code": raw}
    return raw


def save_cursors(state_dir, cursors):
    """Write cursors.json."""
    path = Path(state_dir) / CURSOR_FILE
    path.write_text(json.dumps(cursors, ensure_ascii=False, indent=0), encoding="utf-8")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def build_digest(project_root, cursors, max_bytes=MAX_DIGEST_BYTES,
                 transcript_dir=None, source=None):
    """Return (digest_text, new_cursors) for content beyond the cursors.

    `source`: a source name ("claude-code" | "codex" | "opencode" | "auto" |
    "all"), a TranscriptSource instance, or None (= auto-detect).
    `transcript_dir`: claude-code override (used by tests); ignored otherwise.
    """
    if isinstance(source, str) or source is None:
        src = get_source(project_root, source)
    else:
        src = source

    new_cursors = dict(cursors)
    if isinstance(src, MultiSource):
        # Merges every source; `updated` is {source_name: {...}}, merge at top level.
        chunks, updated = src.collect(project_root, cursors)
        new_cursors.update(updated)
    elif isinstance(src, ClaudeCodeSource):
        chunks, updated = src.collect(project_root, cursors.get("claude-code", {}),
                                      override_dir=transcript_dir)
        new_cursors["claude-code"] = updated
    else:
        chunks, updated = src.collect(project_root, cursors.get(src.name, {}))
        new_cursors[src.name] = updated

    digest = "\n\n".join(chunks)
    encoded = digest.encode("utf-8")
    if len(encoded) > max_bytes:
        tail = encoded[-max_bytes:].decode("utf-8", errors="ignore")
        digest = "[digest truncated to the most recent {} bytes]\n{}".format(max_bytes, tail)
    return digest, new_cursors
