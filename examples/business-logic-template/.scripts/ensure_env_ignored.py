# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Ensure .env secrets and runtime artifacts under this skill are git-ignored.

This is the security guard for the business-logic skill template. It is called
in two places, with identical behavior:

  1. At install time -- by install_hooks.py, right after the hooks are written.
  2. At runtime      -- by auto_sync.py at the top of every sync run, so that a
                        user who creates .env *after* install is still protected.

Scope: the secret lives at <project>/<cli>/.env (.claude, .agents, .opencode)
-- outside the skill folder, because it is per-machine environment config
rather than skill content. The skill's own docs MUST stay committable (that is
the point of the knowledge base), so only its dot-prefixed runtime dirs are
ignored.

Behavior:
  * If any .env file under <cli>/ is already TRACKED by git, refuse loudly and
    print the `git rm --cached` commands needed to untrack it. Return non-zero so
    callers abort.
  * Otherwise, make sure the repo .gitignore contains the canonical ignore block
    (the .env secret + the skill's runtime dirs). Append only the missing lines.
    `.env.example` is intentionally NOT ignored.
  * Independently, ensure virtualenv dirs (`.venv/`) are ignored -- that check
    must not hang off the .env branch, or a repo that already ignores `<cli>/`
    would silently skip it.
  * Finally, ground-truth verify: if <cli>/.env exists, confirm git truly
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

# Default target: derived from THIS script's location (<skill>/.scripts/ ->
# <skill>), so the guard works wherever the skill lives. Callers (auto_sync,
# install_hooks) pass the data dir explicitly and bypass this default.
def _default_data_dir():
    return Path(__file__).resolve().parent.parent

# Marker comment used for the ignore block. Kept generic (no skill name) so it
# never goes stale if the folder is renamed.
MARKER_COMMENT = "# Claude Code skill: secrets + runtime artifacts (do not commit)"

# The scripts are PEP 723 self-contained and run under `uv run --script`, which
# resolves into uv's own cache. But `uv venv` / `uv sync` create <project>/.venv,
# and a committed virtualenv is large, machine-specific and hard to undo.
VENV_COMMENT = "# Python virtualenv (uv / venv) -- machine-specific, never commit"


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


def canonical_patterns(rel, cli_rel):
    """Return the list of gitignore lines that must be present.

    `rel` is the skill dir relative to the git root, in posix form
    (e.g. ".agents/skills/business-logic"); `cli_rel` is its CLI config-dir
    ancestor (.claude / .agents / .opencode). Patterns are scoped to those
    prefixes so they never affect unrelated parts of the user's repo.

    Only dot-prefixed runtime dirs are ignored -- the skill's business-domain
    directories and markdown docs are meant to be committed and reviewed.
    """
    return [
        MARKER_COMMENT,
        "{}/.env".format(cli_rel),
        "{}/.env.local".format(cli_rel),
        "{}/.env.*.local".format(cli_rel),
        # Defense in depth: a stray .env dropped inside the skill folder.
        "{}/**/.env".format(rel),
        "{}/.state/".format(rel),
        "{}/.tmp/".format(rel),
        "{}/.scripts/__pycache__/".format(rel),
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
    """Return tracked files under `rel` whose basename is exactly `.env`."""
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
    # The .env lives in the skill's CLI config-dir ancestor (<cli>), not in the
    # skill itself.
    cli_dir = skill_dir.parent.parent
    cli_rel = cli_dir.relative_to(git_root).as_posix()

    # 1. Hard refuse if a .env is already tracked by git. Scan the whole <cli>
    #    tree: that covers both the real location and a stray one in the skill.
    tracked = list_tracked_env(git_root, cli_rel)
    if tracked:
        print("[ensure_env_ignored] ERROR: a .env file is TRACKED by git -- refusing to proceed.")
        for path in tracked:
            print("  git rm --cached {}".format(path))
        print("[ensure_env_ignored] Commit that removal, then re-run. Secrets must not be committed.")
        return 2

    # 2. Ensure ignore coverage. Key the decision on the .env path rather than on
    #    the skill dir: a project that wholesale-ignores `<cli>/` already covers
    #    the secret, and appending would dirty a tracked .gitignore for no reason.
    #    Only self-heal when the secret is actually uncovered.
    env_rel = "{}/.env".format(cli_rel)
    gitignore_path = git_root / ".gitignore"
    if is_ignored(git_root, env_rel):
        print("[ensure_env_ignored] .env already git-ignored by existing rules; not appending.")
    else:
        added = append_missing(gitignore_path, canonical_patterns(rel, cli_rel))
        if added:
            print("[ensure_env_ignored] Added {} ignore line(s) to .gitignore.".format(added))
        else:
            print("[ensure_env_ignored] All required ignore patterns already present.")

    # 2b. Virtualenv dirs. Decided INDEPENDENTLY of the .env branch above: a repo
    #     that wholesale-ignores `<cli>/` skips that branch entirely, but a
    #     virtualenv at the project root would still be committable.
    #     One pattern suffices: `.venv/` has no leading slash, so git matches it
    #     at ANY depth -- the project root and inside the skill folder alike.
    if is_ignored(git_root, ".venv"):
        print("[ensure_env_ignored] Virtualenv dirs already git-ignored.")
    elif append_missing(gitignore_path, [VENV_COMMENT, ".venv/"]):
        print("[ensure_env_ignored] Added virtualenv ignore lines (.venv/).")

    # 3. Ground-truth check: if the .env exists, verify git truly ignores it.
    #    This catches a conflicting `!` un-ignore rule that would defeat our
    #    patterns (git uses last-match-wins).
    env_probe = cli_dir / ".env"
    if env_probe.exists() and not is_ignored(git_root, env_rel):
        print("[ensure_env_ignored] ERROR: {} exists but is NOT git-ignored.".format(env_rel))
        print("[ensure_env_ignored] A conflicting `!` rule may defeat the ignore patterns.")
        print("[ensure_env_ignored] Fix .gitignore, then re-run.")
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
