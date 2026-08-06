# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Planner, progress ledger and DEPTH GATE for `business-logic init`. Zero LLM,
stdlib only -- everything mechanical (counting files, tracking what is done,
proving a doc is not superficial) belongs in a script, so the model spends its
turns on analysis instead of bookkeeping.

Usage:
    init_plan.py suggest [--min-files N] [--limit N]
    init_plan.py plan --spec-file <path|->     # {"domains":[{"name","scan":[...]}]}
    init_plan.py plan --from-docs              # rebuild ledgers from existing overview.md
    init_plan.py progress
    init_plan.py verify [--domain NAME] [--min-coverage 0.70]

Why this exists: an `init` that produces ONE `overview.md` per domain looks
successful and is not. Measured on a 2851-file repo, that shape left 64% of
source files unmentioned anywhere in the docs -- a knowledge base that returns
nothing when a user searches for a real class, table or error code. The gate
below makes "done" objective:

  * min_subdocs  -- ceil(files / FILES_PER_SUBDOC) sub-domain docs per domain,
                    so a big domain cannot be answered with a single file;
  * coverage     -- the fraction of the domain's source files actually named in
                    its docs, computed from the file ledger;
  * banned marks -- `(planned)` / `TBD` links (a doc confessing it was not
                    written) and `Foo.java:123` line refs (they rot);
  * stub check   -- sub-docs below a byte floor, or missing load-bearing
                    sections.

The plan file `.state/init-plan.json` doubles as the resume point: an
interrupted init picks up the pending domains instead of starting over.
"""

import argparse
import fnmatch
import json
import math
import os
import re
import subprocess
import sys
import time
from pathlib import Path

# Force UTF-8 everywhere: this runs on zh-CN Windows where the console codepage
# is GBK, while git output and docs are UTF-8 (see auto_sync.py for the full
# rationale -- mixing the two corrupted real syncs).
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


# ---------------------------------------------------------------------------
# Layout (derived from __file__, exactly like auto_sync.py, so the same script
# serves any skill name and any <cli> dir)
# ---------------------------------------------------------------------------

def find_git_root(start):
    """Walk up from `start` until a directory containing `.git` is found."""
    start = Path(start).resolve()
    for candidate in [start, *start.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None


SCRIPT_DIR = Path(__file__).resolve().parent      # <skill>/.scripts
SKILL_DIR = SCRIPT_DIR.parent                     # the skill folder (== data dir)
GIT_ROOT = find_git_root(SKILL_DIR)

if GIT_ROOT is None:
    print("[init_plan] Not inside a git repository.", file=sys.stderr)
    sys.exit(2)

WORK_ROOT = GIT_ROOT
DATA_DIR = SKILL_DIR
STATE_DIR = SKILL_DIR / ".state"
PLAN_FILE = STATE_DIR / "init-plan.json"

# ---------------------------------------------------------------------------
# Tunables
# ---------------------------------------------------------------------------

# One sub-domain doc per this many source files. 40 is the point where a single
# doc stops being readable and starts being an index of symbols.
FILES_PER_SUBDOC = 40

# A domain at or below this many files may legitimately live in overview.md
# alone -- do not manufacture ceremony for a small domain.
SINGLE_DOC_MAX = 25

# Fraction of a domain's source files that must be named somewhere in its docs.
MIN_COVERAGE = 0.70

# A sub-domain doc smaller than this is a stub, not a document.
MIN_SUBDOC_BYTES = 1200

# Distinct backticked identifiers (`OrderService.create()`, `fee_config`,
# `ORDER_EXPIRED`) a real sub-doc names. This is the searchability floor: a doc
# without concrete literals returns nothing when the user greps for one.
MIN_SYMBOLS = 8

# Docs that are RECORDS, not analysis: changelogs, sync logs, archives. They are
# legitimate and common in a long-running knowledge base, but they must not
# count as decomposition (14 changelog docs is not a documented domain), and the
# substance checks below do not apply to them.
RECORD_DOC_RE = re.compile(r"changelog|sync-log|sync-history|archive|history", re.I)

# Checks are deliberately LANGUAGE-NEUTRAL: real knowledge bases write headings
# in whatever language the team speaks (the reference deployment uses
# `## 业务概述` / `## 快速索引`), so requiring English section names would fail
# every good doc. Substance is measured instead: a flow, a table, and concrete
# identifiers.
MERMAID_RE = re.compile(r"```\s*mermaid", re.I)
ARROW_RE = re.compile(r"(->|-->|→|─►)")
TABLE_ROW_RE = re.compile(r"^\s*\|.+\|", re.MULTILINE)
SYMBOL_RE = re.compile(r"`([A-Za-z_][\w.:#/()-]{2,})`")
MD_LINK_RE = re.compile(r"\]\(\s*\.?/?([^)\s#]+\.md)")

# Java/Kotlin package notation, used by live docs in `source_packages` headers.
PKG_RE = re.compile(r"^[a-zA-Z][\w]*(\.[a-zA-Z][\w]*)+$")

SOURCE_EXTS = {
    ".java", ".kt", ".scala", ".groovy", ".py", ".go", ".rs", ".rb", ".php",
    ".cs", ".swift", ".m", ".mm", ".c", ".cc", ".cpp", ".h", ".hpp",
    ".ts", ".tsx", ".js", ".jsx", ".vue", ".svelte", ".sql", ".proto",
}

# Directories that never hold business logic.
SKIP_DIRS = {
    ".git", "node_modules", "target", "build", "dist", "out", "bin", "obj",
    "vendor", "venv", ".venv", "__pycache__", ".idea", ".vscode", "coverage",
    "generated", "gen", "third_party", "thirdparty",
}

# Path fragments marking test / fixture code, excluded from the ledger.
TEST_HINTS = (
    "/test/", "/tests/", "/__tests__/", "/testdata/", "/fixtures/",
    "/snapshots/", "/mocks/", "/e2e/", "/benches/", "/examples/",
)

# Plumbing files with no business content of their own; excluded from the
# coverage denominator so re-export shims do not dilute the score.
PLUMBING_NAMES = {"mod.rs", "lib.rs", "__init__.py", "index.ts", "index.js",
                  "package-info.java", "main.rs", "build.rs", "conftest.py",
                  "setup.py"}

# `Foo.java:123` style references. Line numbers rot on the next edit; the doc
# standard is symbols only.
LINE_REF_RE = re.compile(
    r"\b[\w./\\-]+\.(?:java|kt|py|go|rs|ts|tsx|js|jsx|rb|php|cs|scala|swift|"
    r"c|cc|cpp|h|hpp|sql|xml|vue)\s*:\s*\d+")

# Phrases where a doc admits it was not actually written.
UNWRITTEN_RE = re.compile(
    r"\(planned\)|\bTBD\b|to be documented|coming soon|^\s*[-*]\s*TODO\b",
    re.IGNORECASE | re.MULTILINE)

FENCE_RE = re.compile(r"```.*?```", re.DOTALL)


# ---------------------------------------------------------------------------
# Git / filesystem helpers
# ---------------------------------------------------------------------------

def git_out(args):
    """Run a git command in WORK_ROOT; return stripped stdout, '' on failure."""
    r = subprocess.run(
        ["git", "-c", "core.quotepath=false", *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(WORK_ROOT))
    return r.stdout.strip() if r.returncode == 0 else ""


def is_test_name(stem):
    """True for test/spec file naming conventions across languages.

    Separator-aware on purpose: a bare `endswith("test")` would classify
    `latest.rs` as a test file and quietly shrink the ledger.
    """
    s = stem.lower()
    if s in ("test", "tests", "conftest", "spec"):
        return True
    if s.startswith(("test_", "tests_", "spec_", "test-", "spec-")):
        return True
    if s.endswith(("_test", "_tests", "_spec", "_specs", ".test", ".tests",
                   ".spec", "-test", "-tests", "-spec")):
        return True
    # Java/Kotlin: FooTest, FooTests, FooIT, FooITCase.
    return bool(re.search(r"(?:Test|Tests|IT|ITCase)$", stem))


def is_source(rel_path):
    """True if a repo-relative path is business source (not test/plumbing/vendor)."""
    p = rel_path.lower()
    if Path(p).suffix not in SOURCE_EXTS:
        return False
    if any(hint in "/" + p for hint in TEST_HINTS):
        return False
    parts = Path(p).parts
    if any(seg in SKIP_DIRS or seg.startswith(".") for seg in parts[:-1]):
        return False
    return not is_test_name(Path(rel_path).stem)


def tracked_source_files():
    """Every tracked source file in the repo, repo-relative, forward slashes."""
    out = git_out(["ls-files"])
    return [f for f in out.splitlines() if f and is_source(f)]


def parse_scan_entry(entry):
    """Split a scan entry into (path, basename-glob or None).

    `service/order`            -> whole directory
    `service:TeamCopy*`        -> only files whose name matches the glob

    The glob form exists because not every codebase separates domains by
    directory: a flat Java package where domains are distinguished by class
    prefix (`TeamCopy*`, `Mt5*`) is common, and a directory-only planner would
    assign that whole package to every domain that shares it.
    """
    entry = (entry or "").strip().strip("/")
    if ":" in entry:
        path, _, pattern = entry.rpartition(":")
        if path and pattern and "/" not in pattern:
            # Several names may share one path, joined by "|" (illegal in
            # filenames, so it can never be part of a real pattern).
            return path.strip("/"), [p for p in pattern.split("|") if p]
    return entry, None


def files_under(all_files, scan_entries):
    """The subset of `all_files` matching any scan entry (path + optional glob)."""
    parsed = [parse_scan_entry(s) for s in scan_entries if s and s.strip()]
    parsed = [(p, g) for p, g in parsed if p]
    if not parsed:
        return []
    hits = []
    for f in all_files:
        stem = Path(f).stem
        for root, patterns in parsed:
            if not (f == root or f.startswith(root + "/")):
                continue
            if patterns and not any(fnmatch.fnmatch(stem, p) for p in patterns):
                continue
            hits.append(f)
            break
    return hits


def churn(scan_paths):
    """Number of commits touching these paths -- how hot the code is."""
    if not scan_paths:
        return 0
    out = git_out(["rev-list", "--count", "HEAD", "--", *scan_paths])
    try:
        return int(out)
    except ValueError:
        return 0


def ledger_denominator(files):
    """Files that must be accounted for (drops re-export / plumbing shims)."""
    return [f for f in files if Path(f).name not in PLUMBING_NAMES]


def min_subdocs_for(n_files, files_per_subdoc=FILES_PER_SUBDOC):
    """Required sub-domain doc count: 0 for a small domain, else ceil(n/40)>=2."""
    if n_files <= SINGLE_DOC_MAX:
        return 0
    return max(2, math.ceil(n_files / files_per_subdoc))


# ---------------------------------------------------------------------------
# Plan file
# ---------------------------------------------------------------------------

def load_plan():
    if not PLAN_FILE.exists():
        return None
    try:
        return json.loads(PLAN_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print("[init_plan] plan file is corrupt ({}); re-run `plan`.".format(e),
              file=sys.stderr)
        return None


def save_plan(plan):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    plan["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    tmp = PLAN_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(PLAN_FILE)


def require_plan():
    plan = load_plan()
    if plan is None:
        print("No plan yet. Run: init_plan.py plan --spec-file <spec>", file=sys.stderr)
        sys.exit(2)
    return plan


# ---------------------------------------------------------------------------
# suggest -- heuristic domain candidates to seed the model's decision
# ---------------------------------------------------------------------------

# Descend into a directory while it holds more files than this and we are still
# shallow; keeps the suggestion at the crate/package level instead of exploding
# into leaf directories.
DESCEND_ABOVE = 400
MAX_DEPTH = 3


def suggest_domains(min_files=10, limit=40):
    """Propose domain candidates: directories that hold a coherent chunk of code."""
    all_files = tracked_source_files()
    counts = {}
    for f in all_files:
        parts = f.split("/")
        for i in range(1, len(parts)):
            key = "/".join(parts[:i])
            counts[key] = counts.get(key, 0) + 1

    accepted, queue = [], [d for d in sorted(counts) if "/" not in d]
    while queue:
        d = queue.pop(0)
        depth = d.count("/") + 1
        n = counts.get(d, 0)
        if n < min_files:
            continue
        children = sorted(k for k in counts
                          if k.startswith(d + "/") and k.count("/") == depth)
        if n > DESCEND_ABOVE and depth < MAX_DEPTH and children:
            queue.extend(children)
        else:
            accepted.append(d)

    rows = []
    for d in accepted:
        files = files_under(all_files, [d])
        rows.append({
            "suggested_name": Path(d).name.lower().replace("_", "-"),
            "scan": [d],
            "files": len(files),
            "churn": churn([d]),
            "min_subdocs": min_subdocs_for(len(ledger_denominator(files))),
        })
    rows.sort(key=lambda r: (r["churn"], r["files"]), reverse=True)
    return rows[:limit], len(all_files)


def cmd_suggest(args):
    rows, total = suggest_domains(args.min_files, args.limit)
    covered = sum(r["files"] for r in rows)
    print("Repo: {} source files tracked; {} candidate(s) cover {}.".format(
        total, len(rows), covered))
    print()
    print("{:<26} {:>7} {:>7} {:>9}  {}".format(
        "SUGGESTED NAME", "FILES", "CHURN", "SUBDOCS", "SCAN"))
    for r in rows:
        print("{:<26} {:>7} {:>7} {:>9}  {}".format(
            r["suggested_name"][:26], r["files"], r["churn"],
            r["min_subdocs"], ", ".join(r["scan"])))
    print()
    print("These are DIRECTORIES, not business domains. Group and rename them into")
    print("real domains, then write the spec and lock it in:")
    print('  {"domains": [{"name": "order", "scan": ["path/a", "path/b"]}, ...]}')
    print("  init_plan.py plan --spec-file <spec.json>")
    return 0


# ---------------------------------------------------------------------------
# plan -- lock the domain list and compute each domain's file ledger
# ---------------------------------------------------------------------------

# Two header shapes in the wild: a bullet list under `source_packages:`, and an
# inline `source_packages: a, b` on one line. Support both.
SOURCE_PKG_RE = re.compile(r"^>\s*-\s*(.+?)\s*$", re.MULTILINE)
INLINE_PKG_RE = re.compile(r"^>\s*source_packages\s*:\s*(.+?)\s*$", re.MULTILINE)


def resolve_scan_token(token):
    """Resolve one scan entry to repo-relative directories.

    Accepts a path (`service/order`) or a Java/Kotlin PACKAGE
    (`com.example.service`) -- long-running docs record packages, not paths, in
    their `source_packages` header, and a planner that only understands paths
    silently assigns those domains zero files.
    """
    token = token.strip().strip("`").rstrip("/")
    if not token:
        return []
    if (WORK_ROOT / token).exists():
        return [token]
    if not PKG_RE.match(token):
        return []
    frag = token.replace(".", "/")
    hits = []
    for root in ("src/main/java", "src/main/kotlin", "src", ""):
        cand = "/".join(p for p in (root, frag) if p)
        if (WORK_ROOT / cand).is_dir():
            hits.append(cand)
    if hits:
        return hits
    # Multi-module layouts: <module>/src/main/<lang>/<package path>.
    for p in WORK_ROOT.glob("*/src/main/*/" + frag):
        if p.is_dir():
            hits.append(p.relative_to(WORK_ROOT).as_posix())
    return hits


def scan_paths_from(raw):
    """Extract scan targets from one `source_packages` header line.

    Hand-written headers carry trailing prose and several entries per line, e.g.
    "com.example.service (Team*), com.example.web.v4". Keep the leading token of
    each comma-separated chunk and resolve it; unresolvable tokens are dropped,
    which discards the commentary without guessing at its shape.
    """
    out = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        token = chunk.strip("`").split()[0].strip("`").rstrip(":;.,)")
        # A parenthetical narrows the package to specific classes, e.g.
        # "com.example.service (TeamCopy*)" or "com.example.web (OrderCtl,
        # OrderQueryCtl)". Both prefixes and exact names occur; without this,
        # every domain sharing a flat package claims all of its files.
        names = []
        m = re.search(r"\(([^)]*)\)", chunk)
        if m:
            names = re.findall(r"[A-Za-z_][\w]*\*?", m.group(1))
        for path in resolve_scan_token(token):
            out.append("{}:{}".format(path, "|".join(names)) if names else path)
    return out


def domains_from_docs():
    """Rebuild the domain spec from existing `<domain>/overview.md` headers."""
    specs = []
    for d in sorted(DATA_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith(".") or d.name == "_example-domain":
            continue
        overview = d / "overview.md"
        if not overview.exists():
            continue
        text = overview.read_text(encoding="utf-8", errors="replace")
        head = text.split("## ", 1)[0]
        scan = []
        for line in INLINE_PKG_RE.findall(head) + SOURCE_PKG_RE.findall(head):
            if line.startswith("last_verified"):
                continue
            scan.extend(scan_paths_from(line))
        specs.append({"name": d.name, "scan": sorted(set(scan))})
    return specs


def cmd_plan(args):
    if args.from_docs:
        specs = domains_from_docs()
        if not specs:
            print("No existing domain docs to rebuild from.", file=sys.stderr)
            return 2
    else:
        raw = sys.stdin.read() if args.spec_file == "-" else \
            Path(args.spec_file).read_text(encoding="utf-8")
        data = json.loads(raw)
        specs = data.get("domains", data) if isinstance(data, dict) else data

    all_files = tracked_source_files()
    domains, seen = [], set()
    for spec in specs:
        name = str(spec.get("name", "")).strip().strip("/")
        if not name or name.startswith("."):
            print("Skipping invalid domain name {!r} (the dot namespace belongs "
                  "to the skill).".format(name), file=sys.stderr)
            continue
        if name in seen:
            print("Skipping duplicate domain {!r}.".format(name), file=sys.stderr)
            continue
        seen.add(name)
        scan = [s for s in (spec.get("scan") or []) if isinstance(s, str)]
        files = files_under(all_files, scan)
        ledger = ledger_denominator(files)
        domains.append({
            "name": name,
            "scan": scan,
            "note": str(spec.get("note", ""))[:300],
            "files": ledger,
            "n_files": len(ledger),
            "churn": churn(scan),
            "min_subdocs": min_subdocs_for(len(ledger), args.files_per_subdoc),
            # A domain whose scan resolves to nothing cannot be measured. Say so
            # instead of silently planning it as an empty, trivially-passing
            # domain -- most existing docs carry no machine-readable scope.
            "status": "pending" if ledger else "unscoped",
            "subdocs": 0,
            "coverage": 0.0,
            "issues": [],
            "checked_at": "",
        })

    if not domains:
        print("Spec produced no valid domains.", file=sys.stderr)
        return 2

    # Preserve status from an earlier plan so re-planning does not lose progress.
    old = load_plan() or {}
    old_by_name = {d["name"]: d for d in old.get("domains", [])}
    for d in domains:
        prev = old_by_name.get(d["name"])
        if prev and prev.get("scan") == d["scan"]:
            d["status"] = prev.get("status", "pending")
            d["checked_at"] = prev.get("checked_at", "")

    plan = {
        "version": 1,
        "created_at": old.get("created_at") or time.strftime("%Y-%m-%d %H:%M:%S"),
        "head": git_out(["rev-parse", "--short", "HEAD"]),
        "config": {
            "files_per_subdoc": args.files_per_subdoc,
            "single_doc_max": SINGLE_DOC_MAX,
            "min_coverage": MIN_COVERAGE,
        },
        "domains": domains,
    }
    save_plan(plan)

    unowned = len(ledger_denominator(all_files)) - sum(d["n_files"] for d in domains)
    unscoped = [d["name"] for d in domains if d["status"] == "unscoped"]
    print("Planned {} domain(s) -> {}".format(len(domains), PLAN_FILE))
    print()
    print_plan_table(plan)
    if unscoped:
        print()
        print("{} domain(s) have no resolvable scope and cannot be measured: {}"
              .format(len(unscoped), ", ".join(unscoped)))
        print("Give each one a scan path in the spec. Forms accepted:")
        print("  \"service/order\"                  a directory")
        print("  \"service:TeamCopy*\"              a class-name prefix inside a flat package")
        print("  \"com.example.service.order\"      a Java/Kotlin package")
    if unowned > 0:
        print()
        print("WARNING: {} source file(s) belong to no domain. Add a domain (or "
              "widen a scan path) so they are not silently skipped.".format(unowned))
    return 0


def print_plan_table(plan):
    print("{:<26} {:>7} {:>7} {:>9} {:>8}  {}".format(
        "DOMAIN", "FILES", "CHURN", "SUBDOCS", "STATUS", "SCAN"))
    for d in plan["domains"]:
        print("{:<26} {:>7} {:>7} {:>9} {:>8}  {}".format(
            d["name"][:26], d["n_files"], d["churn"],
            ">= {}".format(d["min_subdocs"]) if d["min_subdocs"] else "-",
            d["status"], ", ".join(d["scan"])[:60]))


# ---------------------------------------------------------------------------
# progress -- the numbers to report to the user
# ---------------------------------------------------------------------------

def cmd_progress(args):
    plan = require_plan()
    domains = plan["domains"]
    done = [d for d in domains if d["status"] == "done"]
    failed = [d for d in domains if d["status"] == "failed"]
    pending = [d for d in domains if d["status"] not in ("done", "failed")]

    total_files = sum(d["n_files"] for d in domains) or 1
    covered = sum(int(round(d["coverage"] * d["n_files"])) for d in domains)
    written = sum(d["subdocs"] for d in domains)
    required = sum(d["min_subdocs"] for d in domains)

    print("Domains  : {} total | {} done | {} failed | {} remaining".format(
        len(domains), len(done), len(failed), len(pending)))
    print("Sub-docs : {} written / {} required".format(written, required))
    print("Coverage : {:.0f}% of source files named in docs ({}/{})".format(
        100.0 * covered / total_files, covered, total_files))
    print()
    print_plan_table(plan)
    if pending:
        print()
        print("Remaining: {}".format(", ".join(d["name"] for d in pending)))
    return 0


# ---------------------------------------------------------------------------
# verify -- the depth gate
# ---------------------------------------------------------------------------

def domain_docs(name):
    """Every markdown doc belonging to a domain (skips skill-internal dot dirs)."""
    d = DATA_DIR / name
    if not d.is_dir():
        return []
    return sorted(p for p in d.rglob("*.md")
                  if not any(part.startswith(".") for part in p.relative_to(d).parts))


def coverage_of(files, text):
    """Fraction of ledger files actually named in the docs.

    A file counts as named when its full path appears, or its last two path
    components do (docs usually cite `session/turn.rs`, not the full path), or
    its basename is unique within the domain and appears.
    """
    if not files:
        return 1.0, []
    basename_counts = {}
    for f in files:
        n = Path(f).name
        basename_counts[n] = basename_counts.get(n, 0) + 1
    missing = []
    for f in files:
        parts = f.split("/")
        tail = "/".join(parts[-2:])
        name = parts[-1]
        if f in text or tail in text or (basename_counts[name] == 1 and name in text):
            continue
        missing.append(f)
    return (len(files) - len(missing)) / len(files), missing


def substance_issues(path, text):
    """Language-neutral depth check for ONE analysis doc.

    Deliberately not section-name based: real deployments write headings in
    their own language, so the check measures what a useful doc contains
    regardless of language -- a traced flow, a table, and concrete identifiers.
    """
    issues = []
    size = len(text.encode("utf-8"))
    if size < MIN_SUBDOC_BYTES:
        issues.append("{} is a stub ({} bytes < {})".format(
            path.name, size, MIN_SUBDOC_BYTES))
        return issues  # too small to judge further; fixing size comes first

    # Three independent depth signals; a real doc shows at least two. Requiring
    # all three would punish legitimate doc types -- a config guide or a schema
    # reference has tables and identifiers but no call chain, and demanding one
    # invites a fake diagram.
    has_flow = bool(MERMAID_RE.search(text) or ARROW_RE.search(text))
    has_table = bool(TABLE_ROW_RE.search(text))
    symbols = set(SYMBOL_RE.findall(text))
    has_symbols = len(symbols) >= MIN_SYMBOLS

    if sum((has_flow, has_table, has_symbols)) < 2:
        missing = []
        if not has_flow:
            missing.append("no flow (mermaid or `A -> B` chain)")
        if not has_table:
            missing.append("no table")
        if not has_symbols:
            missing.append("only {} distinct identifier(s), needs {}".format(
                len(symbols), MIN_SYMBOLS))
        issues.append("{}: too thin -- {}. A doc needs at least two of: a "
                      "traced flow, a table, concrete identifiers.".format(
                          path.name, "; ".join(missing)))
    return issues


def verify_domain(entry, min_coverage):
    """Check one domain against the depth rules. Returns (ok, issues, stats)."""
    name = entry["name"]
    issues = []
    docs = domain_docs(name)
    overview = DATA_DIR / name / "overview.md"

    if not overview.exists():
        return False, ["{}/overview.md is missing".format(name)], {"subdocs": 0, "coverage": 0.0}

    subdocs = [p for p in docs if p.name != "overview.md"]
    # Records (changelogs, sync logs, archives) are legitimate but are not
    # decomposition -- counting them would let a domain pass on changelogs alone.
    analysis = [p for p in subdocs if not RECORD_DOC_RE.search(p.stem)]
    records = len(subdocs) - len(analysis)

    need = entry.get("min_subdocs", 0)
    if len(analysis) < need:
        issues.append(
            "only {} analysis sub-doc(s){} for {} source files; needs >= {}. "
            "One overview.md cannot carry this domain -- cut it into "
            "sub-domains.".format(
                len(analysis),
                " ({} changelog/record doc(s) do not count)".format(records) if records else "",
                entry["n_files"], need))

    overview_text = overview.read_text(encoding="utf-8", errors="replace")

    # Navigation: every analysis sub-doc must be reachable from SOMEWHERE a
    # reader starts -- the domain's overview, the top-level index, or the
    # skill's own navigation section. Checking for LINKS rather than a section
    # heading keeps this language neutral: the requirement is that the map
    # routes, not that it is titled in English.
    nav_text = overview_text
    for nav in (DATA_DIR / "index.md", DATA_DIR / "SKILL.md"):
        if nav.exists():
            nav_text += "\n" + nav.read_text(encoding="utf-8", errors="replace")
    linked = {Path(t).name for t in MD_LINK_RE.findall(nav_text)}
    orphans = [p.name for p in analysis if p.name not in linked]
    if orphans:
        issues.append("{} sub-doc(s) unreachable -- not linked from overview.md, "
                      "index.md or the navigation ({})".format(
                          len(orphans), ", ".join(orphans[:4])))

    for p in analysis:
        issues.extend(substance_issues(p, p.read_text(encoding="utf-8", errors="replace")))

    # Banned markers. Fenced code is stripped first: a diagram or snippet may
    # legitimately contain something that looks like a line reference.
    all_text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in docs)
    prose = FENCE_RE.sub("", all_text)
    unwritten = UNWRITTEN_RE.findall(prose)
    if unwritten:
        issues.append("{} unwritten-content marker(s) ((planned)/TBD/TODO) -- "
                      "write the doc or drop the reference".format(len(unwritten)))
    line_refs = LINE_REF_RE.findall(prose)
    if line_refs:
        issues.append("{} line-number reference(s) (e.g. {}) -- they rot; cite "
                      "symbols".format(len(line_refs), line_refs[0]))

    cov, missing_files = coverage_of(entry.get("files", []), all_text)
    if cov < min_coverage:
        sample = ", ".join(missing_files[:5])
        issues.append("file coverage {:.0f}% < {:.0f}%: {} file(s) never named, "
                      "e.g. {}".format(cov * 100, min_coverage * 100,
                                       len(missing_files), sample))

    return (not issues), issues, {"subdocs": len(analysis), "records": records,
                                  "coverage": cov}


def cmd_verify(args):
    plan = require_plan()
    min_coverage = args.min_coverage
    targets = [d for d in plan["domains"]
               if args.domain is None or d["name"] == args.domain]
    if not targets:
        print("No such domain in the plan: {}".format(args.domain), file=sys.stderr)
        return 2

    failed = skipped = 0
    for entry in targets:
        if not entry.get("files"):
            # No ledger -> nothing to measure. Skipping is honest; failing it
            # would blame the docs for a missing scan path in the plan.
            print("{:<26} {:<5} no scan scope -- add one to the spec".format(
                entry["name"][:26], "SKIP"))
            entry["status"] = "unscoped"
            skipped += 1
            continue
        ok, issues, stats = verify_domain(entry, min_coverage)
        entry["status"] = "done" if ok else "failed"
        entry["issues"] = issues
        entry["subdocs"] = stats["subdocs"]
        entry["coverage"] = round(stats["coverage"], 4)
        entry["checked_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        print("{:<26} {:<5} subdocs {}/{}  coverage {:>3.0f}%".format(
            entry["name"][:26], "PASS" if ok else "FAIL",
            stats["subdocs"], entry["min_subdocs"], stats["coverage"] * 100))
        for issue in issues:
            print("    - {}".format(issue))
        if not ok:
            failed += 1
    save_plan(plan)

    print()
    checked = len(targets) - skipped
    print("{}/{} measurable domain(s) passed the depth gate{}.".format(
        checked - failed, checked,
        "; {} skipped for lack of scope".format(skipped) if skipped else ""))
    return 1 if failed else 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args(argv):
    p = argparse.ArgumentParser(prog="init_plan.py")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("suggest", help="propose candidate domains from the repo layout")
    s.add_argument("--min-files", type=int, default=10)
    s.add_argument("--limit", type=int, default=40)

    s = sub.add_parser("plan", help="lock the domain list and build the file ledgers")
    s.add_argument("--spec-file", help="JSON spec path, or - for stdin")
    s.add_argument("--from-docs", action="store_true",
                   help="rebuild from existing <domain>/overview.md headers")
    s.add_argument("--files-per-subdoc", type=int, default=FILES_PER_SUBDOC)

    sub.add_parser("progress", help="domains done / remaining, sub-docs, coverage")

    s = sub.add_parser("verify", help="depth gate: mark each domain done or failed")
    s.add_argument("--domain")
    s.add_argument("--min-coverage", type=float, default=MIN_COVERAGE)

    args = p.parse_args(argv)
    if args.command == "plan" and not args.from_docs and not args.spec_file:
        p.error("plan needs --spec-file <path|-> or --from-docs")
    return args


def main():
    args = parse_args(sys.argv[1:])
    return {
        "suggest": cmd_suggest,
        "plan": cmd_plan,
        "progress": cmd_progress,
        "verify": cmd_verify,
    }[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
