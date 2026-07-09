"""End-to-end consumer flow with a stubbed SDK: digest wiring + cursor commit."""

import asyncio
import json
import os
import shutil
import subprocess as sp
import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TMP = REPO / "tests" / "tmp" / "flowproj"
shutil.rmtree(TMP, ignore_errors=True)
TMP.mkdir(parents=True)
sp.run(["git", "init", "-q", str(TMP)], check=True)
DATA = TMP / ".claude" / "business-logic"
(DATA / "state").mkdir(parents=True)
(DATA / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
os.chdir(str(TMP))


def load():
    src = (REPO / "scripts" / "auto_sync.py").read_text(encoding="utf-8")
    src = src.replace(
        "from claude_agent_sdk import ClaudeAgentOptions, query",
        "class ClaudeAgentOptions(dict):\n"
        "    def __init__(self, **kw): super().__init__(**kw); self.__dict__.update(kw)\n"
        "query = None",
    )
    mod = types.ModuleType("auto_sync_t")
    mod.__dict__["__file__"] = str(REPO / "scripts" / "auto_sync.py")
    exec(compile(src, str(REPO / "scripts" / "auto_sync.py"), "exec"), mod.__dict__)
    return mod


m = load()
m.BATCH_WINDOW = 0
seen_prompts = []


class ResultMessage:
    is_error = False
    result = "ok"
    stop_reason = "end_turn"
    duration_ms = 1
    num_turns = 1
    errors = None


def make_query(update_changelog):
    async def fake_query(prompt, options):
        seen_prompts.append(prompt)
        if update_changelog:
            (DATA / "CHANGELOG.md").write_text(
                "## 2026-07-07\n- **Commits**: aaaaaaa..bbbbbbb (1 commits)\n",
                encoding="utf-8")
        yield ResultMessage()
    return fake_query


# Stub the digest so the test controls conversation content deterministically.
def fake_build_digest(project_root, cursors, max_bytes=80000, transcript_dir=None):
    return "## Session s1\nUSER: hit a pitfall in cancel-order", {"s1.jsonl": 3}


m.digest_transcripts.build_digest = fake_build_digest

# 1. Success path: digest lands in prompt, cursors advance, digest file removed.
m.query = make_query(update_changelog=True)
m.queue_push("pre-push")
assert m.run_consumer() is True
assert "CONVERSATION DIGEST" in seen_prompts[-1]
assert "digest-pending.txt" in seen_prompts[-1]
assert m.digest_transcripts.load_cursors(m.STATE_DIR) == {"s1.jsonl": 3}
assert not (m.STATE_DIR / "digest-pending.txt").exists()
print("1. success: digest in prompt, cursors saved, digest cleaned: OK")

# 2. Failure path (CHANGELOG untouched): cursors must NOT advance further.
m.digest_transcripts.build_digest = lambda *a, **k: ("## Session s2\nUSER: more", {"s1.jsonl": 9})
m.query = make_query(update_changelog=False)
m.queue_push("pre-push")
assert m.run_consumer() is False
assert m.digest_transcripts.load_cursors(m.STATE_DIR) == {"s1.jsonl": 3}
assert (m.STATE_DIR / "digest-pending.txt").exists()
print("2. failure: cursors frozen, digest kept for retry: OK")

# 3. Prompt hygiene: sync scope + data-dir tool scoping.
assert "/business-logic sync" in seen_prompts[0]
assert ".claude/business-logic/" in seen_prompts[0]
print("3. prompt targets the data dir: OK")

# 4. Regression: fingerprint must detect an entry appended under a long header.
#    The original [:200] fingerprint missed this (header alone > 200 chars) and
#    froze cursors forever on every successful sync.
LONG_HEADER = (
    "# Changelog\n\n"
    "> Maintained automatically by the auto-sync hooks. One entry per sync run.\n"
    "> Edit history is pruned to the most recent max_changelog_entries (default 20).\n\n"
    "<!-- Entry format: prepend newest-first. -->\n\n"
)
(DATA / "CHANGELOG.md").write_text(LONG_HEADER, encoding="utf-8")
fp_before = m._get_changelog_fingerprint()
m.digest_transcripts.build_digest = lambda *a, **k: ("## Session s3\nUSER: x", {"s1.jsonl": 12})


async def append_query(prompt, options):
    seen_prompts.append(prompt)
    # Realistic agent behavior: keep the header, append the new entry below it.
    (DATA / "CHANGELOG.md").write_text(
        LONG_HEADER + "## 2026-07-08\n- **Commits**: ccccccc..ddddddd (1 commits)\n",
        encoding="utf-8")
    yield ResultMessage()


m.query = append_query
m.queue_push("pre-push")
assert m.run_consumer() is True, "appended entry under long header must be detected as success"
assert m._get_changelog_fingerprint() != fp_before, "fingerprint must change on append"
print("4. regression: appended entry under long header detected: OK")

print("ALL SYNC FLOW TESTS PASSED")
