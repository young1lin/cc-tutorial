"""
Ensure .env secrets and runtime artifacts under this skill are git-ignored.

This is the security guard for the business-logic skill template. It is called
in two places, with identical behavior:

  1. At install time -- by install_hooks.py, right after the hooks are written.
  2. At runtime      -- by auto_sync.py at the top of every sync run, so that a
                        user who creates .env *after* install is still protected.

Behavior:
  * If any .env file under the skill is already TRACKED by git, refuse loudly and
    print the `git rm --cached` commands needed to untrack it. Return non-zero so
    callers abort.
  * Otherwise, make sure the repo .gitignore contains the canonical ignore block
    for this skill (secrets + runtime artifacts). Append only the missing lines.
    `.env.example` is intentionally NOT ignored.
  * Finally, ground-truth verify: if scripts/.env exists, confirm git truly
    ignores it (catches a conflicting `!` un-ignore rule that defeats the
    patterns). If it is still not ignored, refuse.

Exit codes:
  0 -- safe (ignored, or no .env present, or not in a repo)
  2 -- unsafe (a .env is tracked, or a .env exists but is not ignored)

Usage:
  python ensure_env_ignored.py
"""

import subprocess
import sys
from pathlib import Path

# Default target: the data dir of the project containing the current working
# directory. Callers (auto_sync, install_hooks) pass the data dir explicitly.
def _default_data_dir():
    root = find_git_root(Path.cwd())
    return root / ".claude" / "business-logic" if root else None

# Marker comment used for the ignore block. Kept generic (no skill name) so it
# never goes stale if the folder is renamed.
MARKER_COMMENT = "# Claude Code skill: secrets + runtime artifacts (do not commit)"


def find_git_root(start):
    """Walk up from `start` until a directory containing `.git` is found."""
    start = Path(start).resolve()
    for candidate in [start, *start.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None


def run_git(git_root, args):
    """Run a git command in git_root, returning the completed process."""
    return subprocess.run(
        ["git", "-C", str(git_root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def canonical_patterns(rel):
    """Return the list of gitignore lines that must cover this skill.

    `rel` is the data dir relative to the git root, in posix form
    (e.g. ".claude/business-logic"). Patterns are scoped to `rel` so
    they never affect unrelated parts of the user's repo.
    """
    return [
        MARKER_COMMENT,
        "{}/.env".format(rel),
        "{}/**/.env".format(rel),
        "{}/**/.env.local".format(rel),
        "{}/**/.env.*.local".format(rel),
        "{}/state/".format(rel),
        "{}/scripts/__pycache__/".format(rel),
    ]


def append_missing(gitignore_path, lines):
    """Append any lines not already present in gitignore_path. Returns count added."""
    content = gitignore_path.read_text(encoding="utf-8") if gitignore_path.exists() else ""
    existing = set(content.splitlines())
    missing = [ln for ln in lines if ln not in existing]
    if not missing:
        return 0
    # Ensure we start on a fresh line.
    prefix = "" if (not content or content.endswith("\n")) else "\n"
    with open(gitignore_path, "a", encoding="utf-8") as fh:
        fh.write(prefix + "\n".join(missing) + "\n")
    return len(missing)


def list_tracked_env(git_root, rel):
    """Return tracked files under the skill whose basename is exactly `.env`."""
    result = run_git(git_root, ["ls-files", "--", rel])
    if result.returncode != 0:
        return []
    return [p for p in result.stdout.splitlines() if Path(p).name == ".env"]


def is_ignored(git_root, rel_path):
    """True if rel_path (posix, relative to git_root) matches a gitignore rule."""
    result = run_git(git_root, ["check-ignore", "--quiet", rel_path])
    # git check-ignore exits 0 when the path IS ignored, 1 when it is not.
    return result.returncode == 0


def main(data_dir=None):
    data_dir = Path(data_dir).resolve() if data_dir else _default_data_dir()
    if data_dir is None:
        print("[ensure_env_ignored] Not inside a git repository; nothing to enforce.")
        return 0
    skill_dir = data_dir

    git_root = find_git_root(skill_dir)

    if git_root is None:
        print("[ensure_env_ignored] Not inside a git repository; nothing to enforce.")
        print("[ensure_env_ignored] If you share this folder another way, exclude .env manually.")
        return 0

    rel = skill_dir.relative_to(git_root).as_posix()

    # 1. Hard refuse if a .env is already tracked by git.
    tracked = list_tracked_env(git_root, rel)
    if tracked:
        print("[ensure_env_ignored] ERROR: a .env file is TRACKED by git -- refusing to proceed.")
        for path in tracked:
            print("  git rm --cached {}".format(path))
        print("[ensure_env_ignored] Commit that removal, then re-run. Secrets must not be committed.")
        return 2

    # 2. Ensure the canonical ignore block is present (self-heal).
    gitignore_path = git_root / ".gitignore"
    added = append_missing(gitignore_path, canonical_patterns(rel))
    if added:
        print("[ensure_env_ignored] Added {} ignore line(s) to .gitignore.".format(added))
    else:
        print("[ensure_env_ignored] All required ignore patterns already present.")

    # 3. Ground-truth check: if scripts/.env exists, verify git truly ignores it.
    #    This catches a conflicting `!` un-ignore rule that would defeat our
    #    patterns (git uses last-match-wins).
    env_probe = skill_dir / "scripts" / ".env"
    if env_probe.exists():
        probe_rel = env_probe.relative_to(git_root).as_posix()
        if not is_ignored(git_root, probe_rel):
            print("[ensure_env_ignored] ERROR: scripts/.env exists but is NOT git-ignored.")
            print("[ensure_env_ignored] A conflicting `!` rule may defeat the ignore patterns.")
            print("[ensure_env_ignored] Run: python scripts/install_hooks.py  or fix .gitignore.")
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
