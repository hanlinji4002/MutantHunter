"""Integration test — baseline --set all --jobs 8.

Marked @pytest.mark.slow — run with: pytest -m slow

Asserts ref_match = yes for all 24 modules.
Must not leave results/mutants/*__all.json or *__B.json behind.
"""
from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

import pytest

from mutant_hunter.registry import REPO_ROOT


@pytest.mark.slow
def test_baseline_all_ref_match():
    """Run baseline --set all --jobs 8 and assert ref_match=yes for all 24 modules."""
    result = subprocess.run(
        [sys.executable, "-m", "mutant_hunter.cli",
         "baseline", "--set", "all", "--jobs", "8"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        timeout=3600,  # generous timeout for 24 modules
    )

    print("STDOUT:", result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout)
    print("STDERR:", result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)

    assert result.returncode == 0, (
        f"baseline exited with code {result.returncode}\n"
        f"stderr: {result.stderr[:2000]}"
    )

    csv_path = REPO_ROOT / "results" / "baseline.csv"
    assert csv_path.exists(), "results/baseline.csv was not written"

    with open(csv_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    assert len(rows) == 24, f"Expected 24 rows in baseline.csv, got {len(rows)}"

    mismatches = [r["module"] for r in rows if r.get("ref_match") != "yes"]
    assert mismatches == [], (
        f"ref_match != yes for modules: {mismatches}\n"
        f"Full baseline:\n" + "\n".join(
            f"  {r['module']}: mutants={r['mutants']}/{r['ref_mutants']} "
            f"killed={r['killed']}/{r['ref_killed']} ref_match={r['ref_match']}"
            for r in rows
        )
    )

    # Hold-out discipline: must not leave __all.json or __B.json behind
    _assert_no_holdout_leakage()


def _assert_no_holdout_leakage():
    """Assert that no *__all.json or *__B.json files exist in results/mutants/."""
    mutants_dir = REPO_ROOT / "results" / "mutants"
    if not mutants_dir.exists():
        return
    all_files = list(mutants_dir.glob("*__all.json"))
    b_files = list(mutants_dir.glob("*__B.json"))
    leaked = all_files + b_files
    assert leaked == [], (
        f"Hold-out leakage: the following files must not exist:\n"
        + "\n".join(f"  {f}" for f in leaked)
    )
