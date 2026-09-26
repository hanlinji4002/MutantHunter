"""Integration test — jobs 1 vs jobs 4 give identical results on url.

Marked @pytest.mark.slow — run with: pytest -m slow

Must not leave results/mutants/*__all.json or *__B.json behind.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from mutant_hunter.registry import REPO_ROOT


@pytest.mark.slow
def test_url_jobs_1_vs_4_identical(tmp_path):
    """mutate url --split A with --jobs 1 and --jobs 4 must give identical results."""
    env = os.environ.copy()
    env["MH_MEMBER"] = "test_jobs"

    def run_mutate(jobs: int) -> dict:
        result = subprocess.run(
            [sys.executable, "-m", "mutant_hunter.cli",
             "mutate", "url", "--suite", "human", "--split", "A",
             "--jobs", str(jobs)],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            env=env,
            timeout=1200,
        )
        assert result.returncode == 0, (
            f"mutate url --jobs {jobs} failed with code {result.returncode}\n"
            f"stderr: {result.stderr[:2000]}"
        )
        json_path = REPO_ROOT / "results" / "mutants" / "url__human__A.json"
        assert json_path.exists(), f"Output JSON not found: {json_path}"
        return json.loads(json_path.read_text(encoding="utf-8"))

    data_j1 = run_mutate(1)
    data_j4 = run_mutate(4)

    # The key fields that must be identical
    assert data_j1["mutants"] == data_j4["mutants"], "mutant count differs"
    assert data_j1["killed"] == data_j4["killed"], "killed count differs"
    assert data_j1["survived"] == data_j4["survived"], "survived count differs"
    assert data_j1["score"] == data_j4["score"], "score differs"

    # Results list must be in the same order with the same statuses
    r1 = {r["id"]: r["status"] for r in data_j1["results"]}
    r4 = {r["id"]: r["status"] for r in data_j4["results"]}
    assert r1 == r4, (
        f"Result statuses differ between jobs=1 and jobs=4.\n"
        f"Differences: "
        + str({k: (r1[k], r4[k]) for k in r1 if r1[k] != r4.get(k)})
    )

    # Hold-out discipline: split A file is OK to exist; all/B must not
    _assert_no_holdout_leakage()


@pytest.mark.slow
def test_url_jobs_1_vs_8_identical(tmp_path):
    """mutate url --split A with --jobs 1 and --jobs 8 must give identical results."""
    env = os.environ.copy()
    env["MH_MEMBER"] = "test_jobs8"

    def run_mutate(jobs: int) -> dict:
        result = subprocess.run(
            [sys.executable, "-m", "mutant_hunter.cli",
             "mutate", "url", "--suite", "human", "--split", "A",
             "--jobs", str(jobs)],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            env=env,
            timeout=1200,
        )
        assert result.returncode == 0, (
            f"mutate url --jobs {jobs} failed: {result.stderr[:1000]}"
        )
        json_path = REPO_ROOT / "results" / "mutants" / "url__human__A.json"
        return json.loads(json_path.read_text(encoding="utf-8"))

    data_j1 = run_mutate(1)
    data_j8 = run_mutate(8)

    r1 = {r["id"]: r["status"] for r in data_j1["results"]}
    r8 = {r["id"]: r["status"] for r in data_j8["results"]}
    assert r1 == r8, "jobs=1 and jobs=8 produced different results"
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
        f"Hold-out leakage detected:\n"
        + "\n".join(f"  {f}" for f in leaked)
    )
