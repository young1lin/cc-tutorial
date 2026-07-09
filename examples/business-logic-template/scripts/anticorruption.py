"""
Anti-corruption gate for the business-logic knowledge base.

Pure Python, zero LLM. Runs inside auto_sync.run_consumer() before the sync
LLM round. Hard violations abort the sync; soft violations are reported; size
violations become split candidates injected into the sync prompt.

All thresholds come from environment variables (loaded by auto_sync.load_env()
into os.environ), each with a baked-in default so the gate works with zero
config.

Usage from auto_sync:
    anticorruption.prune_changelog(DATA_DIR)
    gate = anticorruption.run_gate(DATA_DIR, PROJECT_ROOT, STATE_DIR)
    split_text, split_files = anticorruption.build_split_directive(gate, STATE_DIR)
    anticorruption.write_audit(gate, STATE_DIR / "audit.md")
    if gate.abort: ...return False
    ...run_sync(..., split_directive=split_text)...
    anticorruption.persist_split_history(STATE_DIR, gate, attempted_split)

This module never imports the SDK and never makes a network call. Secrets are
masked before they enter any finding, so logs/reports never hold a raw value.
"""

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path


# --- Thresholds (env-overridable, with defaults) ---------------------------

def _env_int(name, default):
    try:
        return int(os.environ.get(name, str(default)))
    except (ValueError, TypeError):
        return default


def _env_list(name):
    raw = os.environ.get(name, "").strip()
    return [p for p in raw.split(",") if p.strip()]


MAX_DOC_BYTES = _env_int("BL_MAX_DOC_BYTES", 51200)
MAX_CHANGELOG_ENTRIES = _env_int("BL_MAX_CHANGELOG_ENTRIES", 20)
AUDIT_FAIL_SYNC = _env_int("BL_AUDIT_FAIL_SYNC", 1) == 1

# Built-in secret patterns; BL_SECRET_SCAN_EXTRA appends more (comma-separated).
SECRET_PATTERNS = [
    r"sk-[A-Za-z0-9_\-]{16,}",              # OpenAI-style keys
    r"AKIA[0-9A-Z]{16}",                    # AWS access key id
    r"ghp_[A-Za-z0-9]{36}",                 # GitHub personal access token
    r"gho_[A-Za-z0-9]{36}",                 # GitHub OAuth token
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",  # PEM private keys
]
SECRET_PATTERNS.extend(_env_list("BL_SECRET_SCAN_EXTRA"))
_SECRET_RE = re.compile("|".join("(?:%s)" % p for p in SECRET_PATTERNS))

# Nine required section headers, in order, for every overview.md.
REQUIRED_SECTIONS = [
    "## Quick Index",
    "## Business Overview",
    "## API Entry Points",
    "## Core Flow",
    "## Business Rules",
    "## Code Location",
    "## Database",
    "## Potential Pitfalls",
    "## Related Docs",
]

ANCHOR_LAST_VERIFIED = "last_verified_commit:"
ANCHOR_SOURCE_PACKAGES = "source_packages:"
CONFLICT_MARKERS = ("<<<<<<<", ">>>>>>>")

# After this many consecutive still-oversized syncs, stop auto-splitting and
# nag in audit.md instead (prevents loops and cost blowup).
SPLIT_MAX_RETRIES = 2

# Chars of the secret kept at each end when masking; the body is hidden.
MASK_KEEP_PREFIX = 3
MASK_KEEP_SUFFIX = 3


@dataclass
class Finding:
    check: str        # which check produced it (function name)
    severity: str     # "hard" or "soft"
    path: str         # repo-relative path
    line: int = 0
    detail: str = ""  # already masked if it came from a secret hit


@dataclass
class GateReport:
    hard: list = field(default_factory=list)
    soft: list = field(default_factory=list)
    split_candidates: list = field(default_factory=list)  # repo-relative paths

    @property
    def abort(self):
        return bool(self.hard) and AUDIT_FAIL_SYNC


# --- Masking ---------------------------------------------------------------

def mask_secret(value):
    """Mask a secret for logs/reports: keep a short prefix + suffix, hide the
    body. sk-234132312 -> sk-***...***312. The full value never hits disk."""
    if len(value) <= MASK_KEEP_PREFIX + MASK_KEEP_SUFFIX:
        return "*" * len(value)
    return "{}***...***{}".format(value[:MASK_KEEP_PREFIX], value[-MASK_KEEP_SUFFIX:])


# --- Individual checks -----------------------------------------------------
# Each returns a list[Finding] (empty if clean). Secrets are masked before the
# finding is built, so a returned detail is always safe to persist.

def check_secrets(path, rel):
    findings = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings
    for lineno, line in enumerate(text.splitlines(), 1):
        if _SECRET_RE.search(line):
            masked_line = _SECRET_RE.sub(lambda m: mask_secret(m.group(0)), line)
            findings.append(Finding("secrets", "hard", rel, lineno, masked_line))
    return findings


def check_conflict_markers(path, rel):
    findings = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings
    for lineno, line in enumerate(text.splitlines(), 1):
        for marker in CONFLICT_MARKERS:
            if marker in line:
                findings.append(Finding("conflict_markers", "hard", rel, lineno,
                                        "merge-conflict marker present"))
    return findings


def check_encoding(path, rel):
    findings = []
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        findings.append(Finding("encoding", "soft", rel, 1, "UTF-8 BOM present"))
    if b"\x00" in raw:
        findings.append(Finding("encoding", "soft", rel, 1, "NUL byte present"))
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError as e:
        findings.append(Finding("encoding", "soft", rel, 1, "not valid UTF-8: {}".format(e)))
    return findings


def check_structure(path, rel):
    findings = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings
    head = text[:2000]
    if ANCHOR_LAST_VERIFIED not in head:
        findings.append(Finding("structure", "soft", rel, 1, "missing anchor: last_verified_commit"))
    if ANCHOR_SOURCE_PACKAGES not in head:
        findings.append(Finding("structure", "soft", rel, 1, "missing anchor: source_packages"))
    for section in REQUIRED_SECTIONS:
        if section not in text:
            findings.append(Finding("structure", "soft", rel, 1, "missing section: {}".format(section)))
    return findings


LINK_RE = re.compile(r"\[[^\]]+\]\(([^)#]+\.md)(?:#[^)]*)?\)")


def check_links(path, rel, data_dir):
    findings = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings
    base = path.parent
    for lineno, line in enumerate(text.splitlines(), 1):
        for target in LINK_RE.findall(line):
            if not (base / target).resolve().exists():
                findings.append(Finding("links", "soft", rel, lineno, "broken link: {}".format(target)))
    return findings


def _parse_source_packages(text):
    """Return package names listed under the `> source_packages:` anchor."""
    packages = []
    in_block = False
    for line in text.splitlines():
        if not line.startswith(">"):
            if in_block:
                break
            continue
        body = line[1:].strip()
        if body.startswith("source_packages:"):
            in_block = True
            continue
        if in_block:
            if body.startswith("- "):
                packages.append(body[2:].strip())
            elif body:
                break
    return packages


def check_source_packages(path, rel, project_root):
    findings = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings
    for pkg in _parse_source_packages(text):
        rel_dir = pkg.replace(".", "/")
        found = any((project_root / src / rel_dir).exists()
                    for src in ("src/main/java", "src/test/java"))
        if not found:
            findings.append(Finding("source_packages", "soft", rel, 1,
                                    "package not found on disk: {}".format(pkg)))
    return findings


def check_size(path, rel):
    """Return a single Finding if the file exceeds MAX_DOC_BYTES, else None."""
    size = path.stat().st_size
    if size > MAX_DOC_BYTES:
        return Finding("size", "soft", rel, 1,
                       "{} bytes > {} threshold".format(size, MAX_DOC_BYTES))
    return None


# --- CHANGELOG rotation ----------------------------------------------------

def prune_changelog(data_dir):
    """Keep the newest MAX_CHANGELOG_ENTRIES entries; preserve header + first hash.

    CHANGELOG is newest-first; auto_sync.get_last_sync_hash() relies on the
    FIRST 'hash..hash' in the file being the latest sync, so the newest entry
    must stay at the top. Returns the number of entries removed, or None if
    nothing changed.

    The skeleton comment block in data-skeleton/CHANGELOG.md uses the literal
    placeholder 'YYYY-MM-DD', which does not match \\d{4}, so it is preserved
    as part of the header.
    """
    path = data_dir / "CHANGELOG.md"
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"(?=^## \d{4}-\d{2}-\d{2})", text, flags=re.MULTILINE)
    header = parts[0]
    entries = parts[1:]
    if len(entries) <= MAX_CHANGELOG_ENTRIES:
        return None
    kept = entries[:MAX_CHANGELOG_ENTRIES]
    path.write_text(header + "".join(kept), encoding="utf-8")
    return len(entries) - len(kept)


# --- Orchestration ---------------------------------------------------------

def run_gate(data_dir, project_root, state_dir):
    """Run all deterministic checks. Returns a GateReport. Never raises out:
    each check is isolated; a crash becomes a soft finding, never a sync freeze.
    Secrets are masked before they enter any finding."""
    report = GateReport()
    md_files = sorted(p for p in data_dir.rglob("*.md")
                      if "state" not in p.parts and "scripts" not in p.parts)
    for path in md_files:
        try:
            rel = path.relative_to(project_root).as_posix()
        except ValueError:
            rel = str(path)

        checks = [
            (check_secrets, "hard", (path, rel)),
            (check_conflict_markers, "hard", (path, rel)),
            (check_encoding, "soft", (path, rel)),
        ]
        if path.name == "overview.md":
            checks += [
                (check_structure, "soft", (path, rel)),
                (check_source_packages, "soft", (path, rel, project_root)),
            ]
        if path.name != "CHANGELOG.md":
            checks += [(check_links, "soft", (path, rel, data_dir))]

        for fn, sev, args in checks:
            try:
                results = fn(*args)
            except Exception as e:
                report.soft.append(Finding(getattr(fn, "__name__", "check"), "soft",
                                           rel, 0, "check crashed: {}".format(e)))
                continue
            (report.hard if sev == "hard" else report.soft).extend(results)

        # Size is special: soft finding + split candidate.
        try:
            size_finding = check_size(path, rel)
            if size_finding:
                report.soft.append(size_finding)
                report.split_candidates.append(rel)
        except Exception:
            pass

    return report


# --- Split directive + non-convergence guard -------------------------------

def load_split_history(state_dir):
    path = state_dir / "split_history.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_split_history(state_dir, hist):
    path = state_dir / "split_history.json"
    path.write_text(json.dumps(hist, ensure_ascii=False, indent=2), encoding="utf-8")


def build_split_directive(report, state_dir):
    """Return (directive_text_or_None, files_to_split). May append SOFT
    'manual split required' findings for files past the retry budget. Does NOT
    mutate history on disk -- the caller persists after a successful sync."""
    hist = load_split_history(state_dir)
    files_to_split = []
    for path in report.split_candidates:
        count = hist.get(path, 0)
        if count >= SPLIT_MAX_RETRIES:
            # Stop auto-splitting; nag in audit.md until a human fixes it.
            # Count stays high so it keeps nagging, not re-attempting.
            report.soft.append(Finding("size", "soft", path, 0,
                "oversized after {} auto-split attempts; MANUAL SPLIT REQUIRED".format(count)))
            continue
        files_to_split.append(path)

    if not files_to_split:
        return None, []

    body = "\n".join("  - {}".format(p) for p in files_to_split)
    text = (
        "\nSPLIT OVERSIZED DOCS:\n"
        "These overview files exceed {limit} bytes and MUST be split in this round. "
        "Split each into multiple sub-overview files so EVERY resulting file is "
        "<= {limit} bytes. Each new sub-overview MUST contain the two top anchors "
        "(last_verified_commit:, source_packages:) and all nine required section "
        "headers (Quick Index, Business Overview, API Entry Points, Core Flow, "
        "Business Rules, Code Location, Database, Potential Pitfalls, Related Docs). "
        "Update index.md to link the new sub-overviews. Do NOT reorder or truncate "
        "CHANGELOG.md.\nFiles:\n{body}\n"
    ).format(limit=MAX_DOC_BYTES, body=body)
    return text, files_to_split


def persist_split_history(state_dir, report, attempted_files):
    """Persist: reset files no longer oversized (successful split or manual fix),
    increment files we asked the model to split this round."""
    hist = load_split_history(state_dir)
    for stale in [k for k in list(hist) if k not in report.split_candidates]:
        hist[stale] = 0
    for path in attempted_files:
        hist[path] = hist.get(path, 0) + 1
    save_split_history(state_dir, hist)


# --- Audit report ----------------------------------------------------------

def write_audit(report, audit_path):
    """Write a masked audit report. Secrets were masked at detection time, so
    this output is always safe to read and share."""
    lines = ["# Anti-corruption audit", ""]
    if report.hard:
        title = "Hard violations (sync aborted)" if report.abort else "Hard violations"
        lines.append("## " + title)
        for f in report.hard:
            loc = "{}:{}".format(f.path, f.line) if f.line else f.path
            lines.append("- [{}] {} -- {}".format(f.check, loc, f.detail))
        lines.append("")
    if report.soft:
        lines.append("## Soft violations")
        for f in report.soft:
            loc = "{}:{}".format(f.path, f.line) if f.line else f.path
            lines.append("- [{}] {} -- {}".format(f.check, loc, f.detail))
        lines.append("")
    if report.split_candidates:
        lines.append("## Split candidates (> {} bytes)".format(MAX_DOC_BYTES))
        for p in report.split_candidates:
            lines.append("- {}".format(p))
        lines.append("")
    audit_path.write_text("\n".join(lines), encoding="utf-8")
