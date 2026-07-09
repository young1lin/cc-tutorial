"""Tests for anticorruption: checks, masking, changelog pruning, split guard."""

import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import anticorruption as ac  # noqa: E402

TMP = REPO / "tests" / "tmp" / "anticorruption"
shutil.rmtree(TMP, ignore_errors=True)
DATA = TMP / "data"
STATE = TMP / "state"
DOMAIN = DATA / "order"
DOMAIN.mkdir(parents=True)
STATE.mkdir(parents=True)

# Make the good overview's source_packages resolve on disk so a clean doc
# produces no findings.
(TMP / "src" / "main" / "java" / "com" / "example" / "order").mkdir(parents=True, exist_ok=True)


def overview(text):
    return text


GOOD = overview(
    "> last_verified_commit: abc1234\n"
    "> source_packages:\n> - com.example.order\n\n"
    "## Quick Index\n## Business Overview\n## API Entry Points\n"
    "## Core Flow\n## Business Rules\n## Code Location\n"
    "## Database\n## Potential Pitfalls\n## Related Docs\n"
)

# 1. Clean doc -> no findings.
(DOMAIN / "overview.md").write_text(GOOD, encoding="utf-8")
r = ac.run_gate(DATA, TMP, STATE)
assert not r.hard and not r.soft, r.soft
print("1. clean overview -> no findings: OK")

# 2. Secret hit is masked in the finding detail (raw value never persisted).
(DOMAIN / "overview.md").write_text(
    GOOD + "\nThe key is ghp_" + "a" * 36 + " here.\n", encoding="utf-8")
r = ac.run_gate(DATA, TMP, STATE)
assert len(r.hard) == 1 and r.hard[0].check == "secrets"
assert "a" * 36 not in r.hard[0].detail, "raw secret leaked into finding"
assert "ghp***" in r.hard[0].detail and "***" in r.hard[0].detail
print("2. secret masked before entering finding: OK")

# 3. Merge-conflict marker is a hard violation.
(DOMAIN / "overview.md").write_text(GOOD + "\n<<<<<<< HEAD\nx\n>>>>>>> feat\n", encoding="utf-8")
r = ac.run_gate(DATA, TMP, STATE)
assert any(f.check == "conflict_markers" and f.severity == "hard" for f in r.hard)
print("3. merge-conflict marker is hard: OK")

# 4. Oversize -> soft finding + split candidate.
(DOMAIN / "overview.md").write_text(GOOD + "\n" + ("x" * (ac.MAX_DOC_BYTES + 10)) + "\n", encoding="utf-8")
r = ac.run_gate(DATA, TMP, STATE)
sizes = [f for f in r.soft if f.check == "size"]
assert sizes and r.split_candidates, "oversize not flagged"
print("4. oversize -> soft + split candidate: OK")

# 5. Missing section -> soft structure finding.
(DOMAIN / "overview.md").write_text(GOOD.replace("## Related Docs\n", ""), encoding="utf-8")
r = ac.run_gate(DATA, TMP, STATE)
assert any(f.check == "structure" for f in r.soft)
print("5. missing section detected: OK")

# 6. BOM -> soft encoding finding.
(DOMAIN / "overview.md").write_bytes(b"\xef\xbb\xbf" + GOOD.encode("utf-8"))
r = ac.run_gate(DATA, TMP, STATE)
assert any(f.check == "encoding" and "BOM" in f.detail for f in r.soft)
print("6. BOM detected: OK")

# 7. Dead source_packages -> soft finding (no matching dir under project).
(DOMAIN / "overview.md").write_text(
    GOOD.replace("com.example.order", "com.does.not.exist"), encoding="utf-8")
r = ac.run_gate(DATA, TMP, STATE)
assert any(f.check == "source_packages" for f in r.soft)
print("7. dead source_packages detected: OK")

# 8. CHANGELOG pruning keeps newest-first and drops the oldest.
# Newest-first, matching real CHANGELOG order (latest entry at the top).
entries = []
for i in range(40):
    day = 40 - i  # 40 (newest) down to 1 (oldest)
    entries.append("## 2026-01-{:02d} 10:00\n- **Commits**: {:07x}..{:07x} (1 commits)\n".format(day, i, i + 1))
(DATA / "CHANGELOG.md").write_text("# Changelog\n\n" + "".join(entries), encoding="utf-8")
removed = ac.prune_changelog(DATA)
assert removed == 40 - ac.MAX_CHANGELOG_ENTRIES
pruned = (DATA / "CHANGELOG.md").read_text(encoding="utf-8")
assert "## 2026-01-40" in pruned and "## 2026-01-01" not in pruned
print("8. changelog pruned newest-first: OK")

# 9. Non-convergence guard: after SPLIT_MAX_RETRIES attempts, escalate to nag.
shutil.rmtree(STATE, ignore_errors=True); STATE.mkdir(parents=True)
report = ac.GateReport(split_candidates=["order/overview.md"])
for _ in range(ac.SPLIT_MAX_RETRIES):
    directive, files = ac.build_split_directive(report, STATE)
    ac.persist_split_history(STATE, report, files)
directive, files = ac.build_split_directive(report, STATE)
assert directive is None and files == []
assert any(f.detail.endswith("MANUAL SPLIT REQUIRED") for f in report.soft)
print("9. non-convergence -> manual-split nag: OK")

# 10. mask_secret shape.
assert ac.mask_secret("sk-234132312") == "sk-***...***312"
assert set(ac.mask_secret("ab")) == {"*"}
print("10. mask_secret shape: OK")

print("ALL ANTICORRUPTION TESTS PASSED")
