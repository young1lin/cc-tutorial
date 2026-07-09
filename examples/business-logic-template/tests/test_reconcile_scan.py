"""Tests for reconcile_scan: duplicate detection, oversized, robustness."""

import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import reconcile_scan as rs  # noqa: E402
import anticorruption as ac  # noqa: E402

TMP = REPO / "tests" / "tmp" / "reconcile"
shutil.rmtree(TMP, ignore_errors=True)
DATA = TMP / "data"
ORD = DATA / "order"
PAY = DATA / "payment"
ORD.mkdir(parents=True)
PAY.mkdir(parents=True)

PITFALL = (
    "## Potential Pitfalls\n"
    "Two callers may race on the status column write; the cancel path must take "
    "a distributed lock before flipping status to avoid the lost-update bug.\n"
)

# order and payment overviews share the SAME pitfalls section.
(ORD / "overview.md").write_text(
    "> last_verified_commit: 0000000\n> source_packages:\n\n" + PITFALL, encoding="utf-8")
(PAY / "overview.md").write_text(
    "> last_verified_commit: 0000000\n> source_packages:\n\n" + PITFALL, encoding="utf-8")

# 1. Duplicate section across two docs is detected.
dups = rs.scan_duplicates(DATA)
assert len(dups) == 1, dups
assert dups[0]["count"] == 2
locs = {p for p, _ in dups[0]["locations"]}
assert "order/overview.md" in locs and "payment/overview.md" in locs
print("1. cross-doc duplicate section detected: OK")

# 2. Distinct sections are NOT flagged.
(PAY / "overview.md").write_text(
    "> last_verified_commit: 0000000\n> source_packages:\n\n"
    "## Potential Pitfalls\nRefunds cap at 1000 per day; above that the job queues them.\n",
    encoding="utf-8")
dups2 = rs.scan_duplicates(DATA)
assert dups2 == [], dups2
print("2. distinct sections not flagged: OK")

# 3. Oversized doc is flagged (reuses the gate threshold).
big = ORD / "big-flow.md"
big.write_text("# x\n\n" + "y" * (ac.MAX_DOC_BYTES + 10), encoding="utf-8")
over = rs.scan_oversized(DATA)
assert any(p == "order/big-flow.md" for p, _ in over), over
print("3. oversized doc flagged: OK")
big.unlink()

# 4. Stale scan does not crash when git cannot resolve the hash (bogus hash).
stale = rs.scan_stale(DATA, TMP)  # TMP is in a git repo but 0000000 is not a commit
assert isinstance(stale, list)
print("4. stale scan robust to unresolvable hash: OK")

# 5. run() writes the candidates report.
(PAY / "overview.md").write_text(
    "> last_verified_commit: 0000000\n> source_packages:\n\n" + PITFALL, encoding="utf-8")
report, counts = rs.run(DATA, TMP)
assert report.exists() and "Duplicate sections" in report.read_text(encoding="utf-8")
assert counts["duplicates"] >= 1
print("5. run() writes reconcile-candidates.md: OK")

print("ALL RECONCILE SCAN TESTS PASSED")
