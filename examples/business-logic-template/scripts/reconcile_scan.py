"""
Manual reconciliation scanner for the business-logic knowledge base.

Zero-LLM, pure stdlib. Surfaces decay candidates the periodic reconcile pass
should address, so the LLM reconcile step (prompts/reconcile.md, run via
`/business-logic reconcile`) works from an explicit list instead of re-reading
the whole corpus every time.

Run it from the project root (project-mode engine) or the global engine dir:
    python .claude/business-logic/scripts/reconcile_scan.py
    python ~/.claude/business-logic/bin/reconcile_scan.py

It writes <data_dir>/state/reconcile-candidates.md and prints a one-line summary.

Signals detected:
  - Duplicate sections: identical normalized section bodies appearing in >= 2
    docs (the main decay mode -- the same pitfall/rule merged in multiple times
    across syncs).
  - Oversized docs: any .md over BL_MAX_DOC_BYTES (reuses the gate threshold).
  - Stale anchors: overview.md whose last_verified_commit is more than
    BL_RECONCILE_STALE_COMMITS behind HEAD (needs git; skipped silently if the
    hash is unresolvable or git is unavailable).

This module never imports the SDK and never makes a network call.
"""

import hashlib
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

# Make the sibling anticorruption module importable (we reuse MAX_DOC_BYTES).
sys.path.insert(0, str(Path(__file__).resolve().parent))
import anticorruption  # noqa: E402


def _env_int(name, default):
    try:
        return int(os.environ.get(name, str(default)))
    except (ValueError, TypeError):
        return default


# An overview is "stale" when its last_verified_commit is this many commits
# behind HEAD. Tune via the env var.
STALE_COMMITS = _env_int("BL_RECONCILE_STALE_COMMITS", 50)

# Sections shorter than this (after normalization) are too trivial to treat as
# duplicate candidates (headers, one-liners).
MIN_SECTION_CHARS = 40

# Strip fenced code (incl. mermaid), blockquote anchor lines, then collapse
# whitespace so two sections that say the same thing hash identically.
_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_BLOCKQUOTE_RE = re.compile(r"^>.*$", re.MULTILINE)
_WS_RE = re.compile(r"\s+")


def normalize(text):
    """Normalize a section body for exact-dupe hashing."""
    text = _FENCE_RE.sub("", text)
    text = _BLOCKQUOTE_RE.sub("", text)
    return _WS_RE.sub(" ", text).strip().lower()


def extract_sections(md_text):
    """Return a list of (heading, body) for each level-2 (##) section."""
    parts = re.split(r"(?m)^(##\s+.+)$", md_text)
    sections = []
    for i in range(1, len(parts), 2):
        heading = parts[i].strip().lstrip("#").strip()
        body = parts[i + 1] if i + 1 < len(parts) else ""
        sections.append((heading, body))
    return sections


def _rel(path, data_dir):
    try:
        return path.relative_to(data_dir).as_posix()
    except ValueError:
        return str(path)


def _md_files(data_dir):
    return sorted(p for p in data_dir.rglob("*.md")
                  if "state" not in p.parts and "scripts" not in p.parts)


def scan_duplicates(data_dir):
    """Return duplicate groups for normalized section bodies in >= 2 docs.

    Each group: {"hash", "count", "heading", "locations": [(path, heading), ...]}.
    """
    by_hash = defaultdict(list)
    for path in _md_files(data_dir):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = _rel(path, data_dir)
        for heading, body in extract_sections(text):
            norm = normalize(body)
            if len(norm) < MIN_SECTION_CHARS:
                continue
            digest = hashlib.sha1(norm.encode("utf-8")).hexdigest()[:12]
            by_hash[digest].append((rel, heading))
    groups = []
    for digest, locs in by_hash.items():
        if len(locs) >= 2:
            groups.append({"hash": digest, "count": len(locs),
                           "heading": locs[0][1], "locations": locs})
    return groups


def scan_oversized(data_dir):
    """Return [(rel_path, size_bytes)] for docs over the gate threshold."""
    out = []
    for path in _md_files(data_dir):
        size = path.stat().st_size
        if size > anticorruption.MAX_DOC_BYTES:
            out.append((_rel(path, data_dir), size))
    return out


def _commits_behind(project_root, commit_hash):
    """Return how many commits HEAD is ahead of commit_hash, or None if the
    hash is unresolvable / git is unavailable."""
    if project_root is None:
        return None
    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", "{}..HEAD".format(commit_hash)],
            capture_output=True, text=True, cwd=str(project_root), timeout=10,
        )
        return int(result.stdout.strip()) if result.returncode == 0 else None
    except Exception:
        return None


def scan_stale(data_dir, project_root):
    """Return [(rel_path, hash, commits_behind)] for stale overview anchors."""
    out = []
    for path in sorted(data_dir.rglob("overview.md")):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        match = re.search(r"last_verified_commit:\s*([0-9a-f]{7,40})", text)
        if not match:
            continue
        behind = _commits_behind(project_root, match.group(1))
        if behind is None:
            continue  # unresolvable hash or no git -- skip, never crash
        if behind > STALE_COMMITS:
            out.append((_rel(path, data_dir), match.group(1), behind))
    return out


def write_report(data_dir, duplicates, oversized, stale):
    """Write state/reconcile-candidates.md. Returns the report path."""
    state = data_dir / "state"
    state.mkdir(parents=True, exist_ok=True)
    report_path = state / "reconcile-candidates.md"

    lines = [
        "# Reconcile candidates", "",
        "> Generated by reconcile_scan.py. Review then run the reconcile pass",
        "> (prompts/reconcile.md via `/business-logic reconcile`) to dedup and",
        "> resolve contradictions. Delete this file after reconciling.", "",
    ]

    lines.append("## Duplicate sections (>= 2 docs)")
    if duplicates:
        for group in sorted(duplicates, key=lambda g: -g["count"]):
            lines.append("- `{}` x{} -- `{}`:".format(
                group["hash"], group["count"], group["heading"]))
            for path, heading in group["locations"]:
                lines.append("    - {} ({})".format(path, heading))
    else:
        lines.append("- none")
    lines.append("")

    lines.append("## Oversized docs (> {} bytes)".format(anticorruption.MAX_DOC_BYTES))
    lines.extend("- {} ({} bytes)".format(p, s) for p, s in oversized) if oversized else lines.append("- none")
    lines.append("")

    lines.append("## Stale anchors (> {} commits behind HEAD)".format(STALE_COMMITS))
    lines.extend("- {} -- last_verified {} ({} behind)".format(p, h, b)
                 for p, h, b in stale) if stale else lines.append("- none")
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def run(data_dir, project_root=None):
    """Run all scans and write the report. Returns (report_path, counts)."""
    duplicates = scan_duplicates(data_dir)
    oversized = scan_oversized(data_dir)
    stale = scan_stale(data_dir, project_root) if project_root else []
    report_path = write_report(data_dir, duplicates, oversized, stale)
    counts = {"duplicates": len(duplicates), "oversized": len(oversized), "stale": len(stale)}
    return report_path, counts


def _find_git_root(start):
    start = Path(start).resolve()
    for candidate in [start, *start.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None


def _default_data_dir():
    root = _find_git_root(Path.cwd())
    return root / ".claude" / "business-logic" if root else None


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    data_dir = Path(argv[0]).resolve() if argv else _default_data_dir()
    if data_dir is None or not data_dir.exists():
        print("[reconcile_scan] data dir not found: {}".format(data_dir), file=sys.stderr)
        return 1
    project_root = _find_git_root(Path.cwd())
    report_path, counts = run(data_dir, project_root)
    print("[reconcile_scan] wrote {} -- {} duplicate group(s), {} oversized, {} stale".format(
        report_path, counts["duplicates"], counts["oversized"], counts["stale"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
