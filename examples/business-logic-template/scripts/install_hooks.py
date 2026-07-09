"""
Install Git hooks for auto-syncing business-logic docs.

Usage:
    python install_hooks.py             # install all hooks
    python install_hooks.py --uninstall # remove all hooks

After installing the hooks this script also runs the .env safety guard
(ensure_env_ignored.py), which makes sure no .env secret under the skill can
ever be committed. If the guard fails (e.g. a .env is already tracked by git),
installation aborts with remediation instructions.
"""

import sys
from pathlib import Path

# Make the sibling ensure_env_ignored module importable.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ensure_env_ignored  # noqa: E402

# The engine directory is wherever this script lives (vendored into the
# project's .claude/business-logic/scripts/, or ~/.claude/business-logic/bin/).
ENGINE_DIR = Path(__file__).resolve().parent


def find_git_root(start):
    """Walk up from `start` until a directory containing `.git` is found."""
    start = Path(start).resolve()
    for candidate in [start, *start.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None


# The project is the git repository containing the CURRENT WORKING DIRECTORY.
PROJECT_ROOT = find_git_root(Path.cwd())
DATA_DIR = PROJECT_ROOT / ".claude" / "business-logic" if PROJECT_ROOT else None
GIT_HOOKS_DIR = PROJECT_ROOT / ".git" / "hooks" if PROJECT_ROOT else None
AUTO_SYNC_SCRIPT = ENGINE_DIR / "auto_sync.py"

# The project rule that makes "explore via this skill" the default behavior.
# Present in the plugin checkout; absent when vendored (the /business-logic
# install command copies the rule itself in that case).
RULE_SOURCE = ENGINE_DIR.parent / "rules" / "explore-with-business-logic.md"
RULE_DEST_DIR = PROJECT_ROOT / ".claude" / "rules" if PROJECT_ROOT else None
RULE_DEST = RULE_DEST_DIR / "explore-with-business-logic.md" if RULE_DEST_DIR else None

HOOK_TEMPLATES = {
    "post-merge": """\
#!/bin/bash
# Auto-sync business-logic docs after git pull.
# Installed by the business-logic plugin.
nohup "{python}" "{sync_script}" post-merge > /dev/null 2>&1 &
""",
    "pre-push": """\
#!/bin/bash
# Auto-sync business-logic docs before git push (runs in the background;
# doc updates ride the next push).
nohup "{python}" "{sync_script}" pre-push > /dev/null 2>&1 &
""",
}

# Hooks earlier versions installed that must be removed on install/uninstall.
LEGACY_HOOKS = ("post-commit",)


def install_rule():
    """Copy the 'explore via skill' rule into the project's .claude/rules/.

    Non-destructive: if the destination already exists (the user may have edited
    it), leave their version alone.
    """
    if RULE_DEST_DIR is None:
        return
    if not RULE_SOURCE.exists():
        print("Rule source not found (skipping): {}".format(RULE_SOURCE))
        return
    RULE_DEST_DIR.mkdir(parents=True, exist_ok=True)
    if RULE_DEST.exists():
        print("Rule already present (leaving as-is): {}".format(RULE_DEST))
        return
    RULE_DEST.write_text(RULE_SOURCE.read_text(encoding="utf-8"), encoding="utf-8")
    print("Installed project rule: {}".format(RULE_DEST))


def install():
    if DATA_DIR is None or not DATA_DIR.exists():
        print("ERROR: {} does not exist.".format(DATA_DIR or ".claude/business-logic"))
        print("       Run `/business-logic install` from Claude Code first, or create the data dir.")
        sys.exit(1)

    if GIT_HOOKS_DIR is None:
        print("ERROR: not inside a git repository (no .git found).")
        print("       Run this from a project that is a git repo.")
        sys.exit(1)

    if not GIT_HOOKS_DIR.exists():
        print("Creating git hooks directory: {}".format(GIT_HOOKS_DIR))
        GIT_HOOKS_DIR.mkdir(parents=True, exist_ok=True)

    installed = []
    for hook_name, template in HOOK_TEMPLATES.items():
        hook_path = GIT_HOOKS_DIR / hook_name
        content = template.format(
            python=sys.executable.replace("\\", "/"),
            sync_script=str(AUTO_SYNC_SCRIPT).replace("\\", "/"),
        )

        # Back up an existing hook if it is not ours.
        if hook_path.exists():
            existing = hook_path.read_text(encoding="utf-8")
            if "auto_sync.py" not in existing:
                backup = hook_path.with_name("{}.bak".format(hook_name))
                hook_path.rename(backup)
                print("Backed up existing hook to: {}".format(backup))

        hook_path.write_text(content, encoding="utf-8")
        try:
            hook_path.chmod(0o755)
        except OSError:
            pass
        installed.append(hook_name)

    # Remove hooks that older engine versions installed.
    for hook_name in LEGACY_HOOKS:
        hook_path = GIT_HOOKS_DIR / hook_name
        if hook_path.exists() and "auto_sync.py" in hook_path.read_text(encoding="utf-8"):
            hook_path.unlink()
            print("Removed legacy hook: .git/hooks/{}".format(hook_name))

    print("\nInstalled {} git hooks:".format(len(installed)))
    for name in installed:
        print("  - .git/hooks/{}".format(name))

    # Security guard: ensure .env secrets and runtime artifacts are git-ignored.
    print("\nRunning .env safety guard...")
    guard_rc = ensure_env_ignored.main(DATA_DIR)
    if guard_rc != 0:
        print("\nERROR: .env safety guard failed (exit {}).".format(guard_rc))
        print("       Fix the issue above, then re-run install_hooks.py.")
        sys.exit(guard_rc)
    print(".env safety guard OK.")

    # Install the project rule so "prefer this skill over Explore Agent" becomes
    # the default behavior for this repo without any extra setup.
    install_rule()

    print("\nPython: {}".format(sys.executable))
    print("Script: {}".format(AUTO_SYNC_SCRIPT))
    print("\nHooks configured:")
    print("  - git pull -> auto sync pulled commits")
    print("  - git push -> auto sync all unsynced commits + conversation digest")

    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("\nWARNING: {} not found!".format(env_file))
        print("Copy .env.example to .env and fill in your API key:")
        print("  cp scripts/.env.example scripts/.env")


def uninstall():
    if GIT_HOOKS_DIR is None or not GIT_HOOKS_DIR.exists():
        print("No git hooks directory found.")
        return

    removed = []
    for hook_name in (*HOOK_TEMPLATES, *LEGACY_HOOKS):
        hook_path = GIT_HOOKS_DIR / hook_name
        if hook_path.exists():
            content = hook_path.read_text(encoding="utf-8")
            if "auto_sync.py" in content:
                hook_path.unlink()
                removed.append(hook_name)

    if removed:
        print("Removed {} git hooks: {}".format(len(removed), ", ".join(removed)))
    else:
        print("No auto-sync hooks found to remove.")


if __name__ == "__main__":
    if "--uninstall" in sys.argv:
        uninstall()
    else:
        install()
