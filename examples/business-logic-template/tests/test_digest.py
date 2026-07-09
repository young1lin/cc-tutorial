"""Tests for digest_transcripts: cursors, filtering, self-sync skip, cap."""

import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import digest_transcripts as dt  # noqa: E402

TMP = REPO / "tests" / "tmp" / "digest"
shutil.rmtree(TMP, ignore_errors=True)
TDIR = TMP / "transcripts"
STATE = TMP / "state"
TDIR.mkdir(parents=True)
STATE.mkdir(parents=True)


def jline(obj):
    return json.dumps(obj, ensure_ascii=False)


# Session A: normal conversation with tool noise.
(TDIR / "session-a.jsonl").write_text("\n".join([
    jline({"type": "user", "message": {"content": "how does order cancel work?"}}),
    jline({"type": "assistant", "message": {"content": [
        {"type": "text", "text": "Pitfall: the cancel path double-writes the status column."},
        {"type": "tool_use", "name": "Read", "input": {"file_path": "x"}},
    ]}}),
    jline({"type": "tool_result", "content": "HUGE TOOL OUTPUT " * 100}),
    jline({"type": "user", "message": {"content": "<command-name>/clear</command-name>"}}),
]) + "\n", encoding="utf-8")

# Session B: our own automated sync run -- must be skipped entirely.
(TDIR / "session-b.jsonl").write_text("\n".join([
    jline({"type": "user", "message": {"content": "/business-logic sync 3\n\nCRITICAL INSTRUCTIONS"}}),
    jline({"type": "assistant", "message": {"content": [{"type": "text", "text": "syncing"}]}}),
]) + "\n", encoding="utf-8")

# 1. Fresh digest picks up session A text, drops tool noise, skips session B.
digest, cur = dt.build_digest(TMP, {}, transcript_dir=TDIR)
assert "order cancel" in digest, digest
assert "double-writes the status column" in digest
assert "HUGE TOOL OUTPUT" not in digest
assert "<command-name>" not in digest
assert "syncing" not in digest, "self-sync session must be skipped"
assert cur["session-a.jsonl"] == 4 and cur["session-b.jsonl"] == 2
print("1. fresh digest content + self-sync skip: OK")

# 2. Cursor round-trip through state files.
dt.save_cursors(STATE, cur)
assert dt.load_cursors(STATE) == cur
print("2. cursor save/load round-trip: OK")

# 3. No new content -> empty digest, cursors unchanged.
digest2, cur2 = dt.build_digest(TMP, cur, transcript_dir=TDIR)
assert digest2 == "" and cur2 == cur
print("3. no new lines -> empty digest: OK")

# 4. Appended lines -> only the increment is digested.
with open(TDIR / "session-a.jsonl", "a", encoding="utf-8") as fh:
    fh.write(jline({"type": "user", "message": {"content": "new question about refunds"}}) + "\n")
digest3, cur3 = dt.build_digest(TMP, cur, transcript_dir=TDIR)
assert "refunds" in digest3 and "order cancel" not in digest3
assert cur3["session-a.jsonl"] == 5
print("4. incremental digest: OK")

# 5. Cap keeps the newest bytes and notes truncation.
digest4, _ = dt.build_digest(TMP, {}, max_bytes=100, transcript_dir=TDIR)
assert len(digest4.encode("utf-8")) < 400 and "truncated" in digest4
print("5. byte cap with truncation notice: OK")

# 6. Missing transcript dir -> empty result, no crash.
digest5, cur5 = dt.build_digest(TMP, {}, transcript_dir=TMP / "nope")
assert digest5 == "" and cur5 == {}
print("6. missing transcript dir: OK")

# 7. transcript path munging matches Claude Code's ~/.claude/projects naming.
assert dt.transcript_dir_for(Path(r"D:\goProject\cc-tutorial")).name == "D--goProject-cc-tutorial"
assert dt.transcript_dir_for(Path("/home/u/foo")).name == "-home-u-foo"
print("7. transcript path munging: OK")

print("ALL DIGEST TESTS PASSED")
