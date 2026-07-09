"""Functional tests for auto_sync.py's single-instance lock (PID + heartbeat)."""

import os
import shutil
import subprocess as sp
import sys
import threading
import time
import types
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TMP = REPO / "tests" / "tmp" / "lockproj"
SRC_PATH = REPO / "scripts" / "auto_sync.py"


def make_project():
    if not (TMP / ".git").exists():
        TMP.mkdir(parents=True, exist_ok=True)
        sp.run(["git", "init", "-q", str(TMP)], check=True)
    (TMP / ".claude" / "business-logic" / "state").mkdir(parents=True, exist_ok=True)


def load():
    src = SRC_PATH.read_text(encoding="utf-8")
    src = src.replace(
        "from claude_agent_sdk import ClaudeAgentOptions, query",
        "ClaudeAgentOptions = query = None",
    )
    mod = types.ModuleType("auto_sync_t")
    mod.__dict__["__file__"] = str(SRC_PATH)
    exec(compile(src, str(SRC_PATH), "exec"), mod.__dict__)
    return mod


make_project()
os.chdir(str(TMP))

if len(sys.argv) > 1 and sys.argv[1] == "race":
    m = load()
    got = m.try_become_consumer()
    print("WIN" if got else "LOSE", flush=True)
    if got:
        time.sleep(5)  # hold the lock while the other racers check it
        m.release_consumer()
    sys.exit(0)


m = load()
PID = m.PID_FILE
PID.unlink(missing_ok=True)

assert m.try_become_consumer() is True
assert PID.read_text().strip() == str(os.getpid())
print("1. fresh acquire -> WIN, pid file owned: OK")

assert m.try_become_consumer() is False
print("2. live owner + fresh heartbeat -> defer: OK")

old = time.time() - 700
os.utime(PID, (old, old))
assert m.try_become_consumer() is True
print("3. alive owner, heartbeat stale 700s -> takeover: OK")

PID.unlink()
child = sp.Popen([sys.executable, "-c", "pass"])
dead_pid = child.pid
child.wait()
PID.write_text(str(dead_pid))
assert m.try_become_consumer() is True
print("4. dead owner -> takeover: OK")

m.HEARTBEAT_INTERVAL = 1
ev = threading.Event()
m.start_heartbeat(ev)
mt0 = PID.stat().st_mtime
time.sleep(2.5)
mt1 = PID.stat().st_mtime
assert mt1 > mt0, "heartbeat did not touch the PID file"
print("5. heartbeat refreshes PID mtime: OK")

PID.write_text("99999999")
time.sleep(1.5)
mt2 = PID.stat().st_mtime
time.sleep(1.5)
mt3 = PID.stat().st_mtime
assert mt3 == mt2, "heartbeat kept touching after supersession"
ev.set()
print("6. heartbeat stops after supersession: OK")
PID.unlink(missing_ok=True)

procs = [sp.Popen([sys.executable, __file__, "race"], stdout=sp.PIPE, text=True) for _ in range(8)]
outs = [p.communicate()[0].strip() for p in procs]
wins = sum(1 for o in outs if o == "WIN")
print("race outcomes:", outs)
assert wins == 1, "expected exactly 1 winner, got {}".format(wins)
print("7. 8-process concurrent race -> exactly 1 consumer: OK")

print("ALL LOCK TESTS PASSED")
