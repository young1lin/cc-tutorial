# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Install Git hooks for auto-syncing business-logic docs.

Usage:
    uv run --script install_hooks.py             # install all hooks
    uv run --script install_hooks.py --uninstall # remove all hooks
    python install_hooks.py                      # works too; no deps needed here

After installing the hooks this script also runs the .env safety guard
(ensure_env_ignored.py), which makes sure the CLI config dir's .env
(.claude/.env, .agents/.env, ...) can never be committed. If the guard fails
(e.g. a .env is already tracked by git), installation aborts with remediation
instructions.

The generated hooks prefer `uv run --script` and fall back to the interpreter
that ran this installer. The choice is made inside the hook at run time, not
baked in here, so installing uv later upgrades existing hooks for free.
"""

import shutil
import sys
from pathlib import Path

# Make the sibling ensure_env_ignored module importable.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ensure_env_ignored  # noqa: E402

# The engine directory is this script's own folder: <skill>/.scripts/
ENGINE_DIR = Path(__file__).resolve().parent
SKILL_DIR = ENGINE_DIR.parent


def find_git_root(start):
    """Walk up from `start` until a directory containing `.git` is found."""
    start = Path(start).resolve()
    for candidate in [start, *start.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None


# The project is the git repository containing the SKILL (found from the
# script location, not from cwd, so install works from any subdir).
PROJECT_ROOT = find_git_root(SKILL_DIR)
DATA_DIR = SKILL_DIR                                   # skill folder == data dir
GIT_HOOKS_DIR = PROJECT_ROOT / ".git" / "hooks" if PROJECT_ROOT else None
AUTO_SYNC_SCRIPT = ENGINE_DIR / "auto_sync.py"

# CLI_DIR = the config dir that owns this skill (.claude / .agents / .opencode).
# Standard layout <root>/<cli>/skills/<skill>; the .env lives at <cli>/.env.
CLI_DIR = SKILL_DIR.parent.parent

# Memory file the target CLI reads. Claude Code reads CLAUDE.md; opencode and
# codex read AGENTS.md. Order matters: prefer the CLI's OWN config dir first
# (.agents/AGENTS.md, .claude/CLAUDE.md) -- that file belongs to this CLI and
# won't be picked up by a different CLI. Fall back to the project root (also
# read by every CLI). When neither exists we create at the top of the list,
# i.e. under <cli>/. (No <cli>/rules/ -- opencode & codex ignore rules.)
MEMORY_FILENAME = "CLAUDE.md" if CLI_DIR.name == ".claude" else "AGENTS.md"
MEMORY_CANDIDATES = [
    CLI_DIR / MEMORY_FILENAME,        # preferred: .agents/AGENTS.md, .claude/CLAUDE.md
    PROJECT_ROOT / MEMORY_FILENAME,   # fallback: project root (read by every CLI)
]

# Marker pair delimits our managed block: makes install idempotent and lets
# uninstall remove exactly our lines without touching user content.
_MEM_START = "<!-- business-logic-skill: explore-first (managed by install_hooks.py) -->"
_MEM_END = "<!-- /business-logic-skill -->"

# Runner preamble shared by both hooks: prefer uv (resolves the inline PEP 723
# dependencies on its own), otherwise fall back to the recorded interpreter.
_RUNNER = """\
if command -v uv >/dev/null 2>&1; then
  RUNNER=(uv run --script)
else
  RUNNER=("{python}")
fi
"""

HOOK_TEMPLATES = {
    "post-merge": """\
#!/bin/bash
# Auto-sync business-logic docs after git pull.
# Installed by the business-logic skill.
""" + _RUNNER + """\
nohup "${{RUNNER[@]}}" "{sync_script}" post-merge > /dev/null 2>&1 &
""",
    "pre-push": """\
#!/bin/bash
# Auto-sync business-logic docs before git push (runs in the background;
# doc updates ride the next push).
""" + _RUNNER + """\
nohup "${{RUNNER[@]}}" "{sync_script}" pre-push > /dev/null 2>&1 &
""",
}

# Hooks earlier versions installed that must be removed on install/uninstall.
LEGACY_HOOKS = ("post-commit",)


def _memory_block(skill_rel):
    """The 'explore via this skill first' instruction, parameterized by the
    actual skill location. Generic (no slash commands) so it works for Claude
    Code, opencode and codex alike."""
    return "\n".join([
        _MEM_START,
        "",
        "## Explore via the business-logic knowledge base first",
        "",
        "When asked to understand business logic, locate a feature, explain how",
        "something works, or find the code for a given concept, **consult the",
        "living knowledge base at `{rel}/` before re-deriving the design from",
        "source or grepping blindly.** It has one `overview.md` per business",
        "domain, plus flow docs, call-relation graphs, DB schemas and pitfall",
        "notes, kept in sync with the code by auto-sync git hooks -- usually",
        "faster and more accurate than re-reading the source.",
        "",
        "Start by listing `{rel}/` to see the domain directories, then read the",
        "relevant domain's `overview.md` and drill into its docs as needed.",
        "Fall back to reading source only when a doc is missing or stale, and",
        "backfill what you learned so the next exploration is current.",
        "",
        _MEM_END,
    ]).format(rel=skill_rel)


def _strip_memory_block(text):
    """Remove our managed marker block from `text`. Returns (new_text, removed)."""
    if _MEM_START not in text:
        return text, False
    start = text.index(_MEM_START)
    end_marker = text.find(_MEM_END, start)
    cut_end = (end_marker + len(_MEM_END)) if end_marker != -1 else len(text)
    if cut_end < len(text) and text[cut_end] == "\n":
        cut_end += 1
    return text[:start] + text[cut_end:], True


def install_memory_rule():
    """Append the 'explore via this skill first' block to the CLI's memory file
    (CLAUDE.md / AGENTS.md). Reuses an existing file (project root or <cli>/);
    if none exists, creates one at the project root. Idempotent: if our marker
    block is already present, the file is left untouched.
    """
    skill_rel = SKILL_DIR.relative_to(PROJECT_ROOT).as_posix()
    block = _memory_block(skill_rel)
    target = next((p for p in MEMORY_CANDIDATES if p.exists()), MEMORY_CANDIDATES[0])
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    if _MEM_START in existing:
        print("Memory rule already present (leaving as-is): {}".format(target.name))
        return
    prefix = "" if (not existing or existing.endswith("\n")) else "\n"
    sep = "" if (not existing or existing.endswith("\n\n")) else "\n"
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "a", encoding="utf-8") as fh:
        fh.write(prefix + sep + block + "\n")
    print("Installed memory rule: {}".format(target))


def install():
    if GIT_HOOKS_DIR is None:
        print("ERROR: not inside a git repository (no .git found around {}).".format(SKILL_DIR))
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

    # Write the "explore via this skill first" directive into the CLI's memory
    # file (CLAUDE.md / AGENTS.md) so it is the default behavior for this repo.
    install_memory_rule()

    uv_path = shutil.which("uv")
    if uv_path:
        print("\nRunner: uv ({}) -- inline dependencies, no manual install".format(uv_path))
    else:
        print("\nRunner: {} (uv not found)".format(sys.executable))
        print("        Install uv for zero-setup dependency resolution, or run:")
        print("        pip install -r {}".format(ENGINE_DIR / "requirements.txt"))
    print("Script: {}".format(AUTO_SYNC_SCRIPT))
    print("\nHooks configured:")
    print("  - git pull -> auto sync pulled commits")
    print("  - git push -> auto sync all unsynced commits + conversation digest")

    # The example ships inside the skill (fixed content); the filled-in .env
    # lives outside it at <cli>/.env, so copying the skill folder never carries
    # secrets.
    env_file = CLI_DIR / ".env"
    if not env_file.exists():
        skill_rel = SKILL_DIR.relative_to(PROJECT_ROOT).as_posix()
        cli_rel = CLI_DIR.relative_to(PROJECT_ROOT).as_posix()
        print("\nWARNING: {}/.env not found!".format(cli_rel))
        print("Copy the example and fill in your API credentials:")
        print("  cp {}/.scripts/.env.example {}/.env".format(skill_rel, cli_rel))


def uninstall():
    # 1. Remove the memory-rule block from every candidate location (the block
    #    may be in the project root or under <cli>/; clean wherever it is).
    for target in MEMORY_CANDIDATES:
        if not target.exists():
            continue
        text = target.read_text(encoding="utf-8")
        new, removed_block = _strip_memory_block(text)
        if removed_block:
            if new.strip():
                target.write_text(new, encoding="utf-8")
                print("Removed memory rule from: {}".format(target))
            else:
                target.unlink()
                print("Removed empty memory file: {}".format(target))

    # 2. Remove git hooks.
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
