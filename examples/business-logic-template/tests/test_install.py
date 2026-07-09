"""Installer test: hooks written, legacy removed, guard patterns appended."""

import os
import shutil
import subprocess as sp
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TMP = REPO / "tests" / "tmp" / "installproj"
shutil.rmtree(TMP, ignore_errors=True)
TMP.mkdir(parents=True)
sp.run(["git", "init", "-q", str(TMP)], check=True)

DATA = TMP / ".claude" / "business-logic"
SCRIPTS = DATA / "scripts"
SCRIPTS.mkdir(parents=True)
for name in ("auto_sync.py", "digest_transcripts.py", "ensure_env_ignored.py", "install_hooks.py"):
    shutil.copy(REPO / "scripts" / name, SCRIPTS / name)

# A legacy post-commit hook from an older engine version.
hooks_dir = TMP / ".git" / "hooks"
(hooks_dir / "post-commit").write_text('#!/bin/bash\nnohup python auto_sync.py post-commit &\n', encoding="utf-8")

r = sp.run([sys.executable, str(SCRIPTS / "install_hooks.py")],
           cwd=str(TMP), capture_output=True, text=True)
assert r.returncode == 0, r.stdout + r.stderr

assert (hooks_dir / "post-merge").exists()
assert (hooks_dir / "pre-push").exists()
assert not (hooks_dir / "post-commit").exists(), "legacy post-commit must be removed"
assert "auto_sync.py" in (hooks_dir / "pre-push").read_text(encoding="utf-8")
print("1. hooks: post-merge + pre-push installed, post-commit removed: OK")

gi = (TMP / ".gitignore").read_text(encoding="utf-8")
assert ".claude/business-logic/state/" in gi
assert ".claude/business-logic/.env" in gi
print("2. guard appended data-dir ignore patterns: OK")

r2 = sp.run([sys.executable, str(SCRIPTS / "install_hooks.py"), "--uninstall"],
            cwd=str(TMP), capture_output=True, text=True)
assert r2.returncode == 0, r2.stdout + r2.stderr
assert not (hooks_dir / "post-merge").exists() and not (hooks_dir / "pre-push").exists()
print("3. uninstall removes both hooks: OK")

print("ALL INSTALL TESTS PASSED")
