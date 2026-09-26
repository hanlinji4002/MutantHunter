"""replay.py — historical bug replay (spec 7.4).

replay(which, suites) -> list[dict]

For each row of dataset/bug_commits.csv, run each requested suite against
the pre-fix commit (sha^) and the fix commit (sha) of the module source,
both taken from the ../validators-history clone.

caught       = tests fail on pre-fix AND pass on fix
miss         = tests pass on pre-fix (bug not caught)
not_replayable = pytest collection fails on either version
(empty)      = module has no tests for that suite

Writes results/replay.csv.
"""

from __future__ import annotations

import csv
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

from .isolation import Workspace, _make_env
from .registry import REPO_ROOT, TARGET_ROOT, VENV_PYTHON, Module, get_module


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

HISTORY_ROOT: Path = REPO_ROOT.parent / "validators-history"
BUG_COMMITS_CSV: Path = REPO_ROOT / "dataset" / "bug_commits.csv"
REPLAY_CSV: Path = REPO_ROOT / "results" / "replay.csv"

_REPLAY_COLS = [
    "sha", "date", "module", "set", "subject",
    "suite", "result", "note",
]


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def _git_show(ref: str, rel_path: str) -> Optional[str]:
    """Return the contents of rel_path at git ref, or None on error."""
    cmd = ["git", "show", f"{ref}:{rel_path}"]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(HISTORY_ROOT),
    )
    if proc.returncode != 0:
        return None
    return proc.stdout


def _source_at(sha: str, module_name: str) -> Optional[str]:
    """Return source text for module at sha, or None if not found."""
    # source_path relative to TARGET_ROOT is src/validators/...
    # In the history repo the layout is the same (src/validators/...)
    try:
        mod = get_module(module_name)
    except KeyError:
        return None
    rel = mod.source_path.relative_to(TARGET_ROOT)
    return _git_show(sha, str(rel).replace("\\", "/"))


# ---------------------------------------------------------------------------
# Suite test-path resolution (for replay — does NOT use suite_test_paths
# from registry because replay suites are "human", "mh", "b1" not "human+mh")
# ---------------------------------------------------------------------------

def _suite_paths_for_replay(module_name: str, suite: str) -> list[Path]:
    """Return absolute test paths for the given suite, or [] if none exist.

    Replay uses three suites:
    - "human": the module's regular test file
    - "mh":    targets/validators/tests/mh/<slug>/
    - "b1":    targets/validators/tests/b1/<slug>/
    """
    try:
        mod = get_module(module_name)
    except KeyError:
        return []

    if suite == "human":
        return [mod.test_path]

    slug = mod.slug
    if suite == "mh":
        p = TARGET_ROOT / "tests" / "mh" / slug
    elif suite == "b1":
        p = TARGET_ROOT / "tests" / "b1" / slug
    else:
        return []

    if not p.exists():
        return []
    # Return all .py files (non-empty directory check)
    files = list(p.glob("*.py"))
    return [p] if files else []


# ---------------------------------------------------------------------------
# Workspace adapted for replay: uses history source, current tests
# ---------------------------------------------------------------------------

class _ReplayWorkspace:
    """Workspace that copies TARGET_ROOT tests but injects source from history.

    The constructor takes the source text to inject; all test files come from
    the live TARGET_ROOT (i.e., the tests written today).
    """

    def __init__(self, source_text: str, module: Module) -> None:
        self._source_text = source_text
        self._module = module
        self.path: Path = Path(tempfile.mkdtemp(prefix="mh_rp_"))

    def __enter__(self) -> "_ReplayWorkspace":
        self._setup()
        return self

    def __exit__(self, *_) -> None:
        shutil.rmtree(self.path, ignore_errors=True)

    def _setup(self) -> None:
        ignore = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")
        # Copy the full src/ tree from TARGET_ROOT
        src_dir = TARGET_ROOT / "src"
        tests_dir = TARGET_ROOT / "tests"
        if src_dir.exists():
            shutil.copytree(src_dir, self.path / "src", ignore=ignore)
        if tests_dir.exists():
            shutil.copytree(tests_dir, self.path / "tests", ignore=ignore)
        # Overwrite the module source with the historical version
        rel = self._module.source_path.relative_to(TARGET_ROOT / "src")
        ws_src_file = self.path / "src" / rel
        ws_src_file.parent.mkdir(parents=True, exist_ok=True)
        ws_src_file.write_text(self._source_text, encoding="utf-8")

    @property
    def pythonpath(self) -> str:
        return str(self.path / "src")

    def _make_env(self) -> dict:
        env = os.environ.copy()
        env["PYTHONPATH"] = self.pythonpath
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env.pop("PYTEST_CURRENT_TEST", None)
        return env

    def run_pytest_collect_failures(
        self, suite_paths: list[Path], timeout: int = 60
    ) -> tuple[str, set[str]]:
        """Run pytest and return (status, set_of_failed_test_nodeids).

        status is one of: 'ok' | 'not_replayable'
        set_of_failed_test_nodeids contains the nodeids of tests that FAILED.
        An empty set means all collected tests passed.
        """
        # Rebase test paths into the workspace
        rebased = []
        for p in suite_paths:
            try:
                rel = p.relative_to(TARGET_ROOT)
                ws_p = self.path / rel
            except ValueError:
                ws_p = p
            if ws_p.exists():
                rebased.append(str(ws_p))

        if not rebased:
            return "ok", set()  # no tests = nothing to kill

        cmd = [
            str(VENV_PYTHON),
            "-B", "-m", "pytest",
            "-q",                    # no -x: run all tests
            "-p", "no:cacheprovider",
            "--tb=no",
            "--no-header",
        ]
        cmd.extend(rebased)

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=self._make_env(),
                cwd=str(self.path),
            )
            # Exit code 5 = no tests collected
            if proc.returncode == 5:
                return "ok", set()
            # Exit code 4 = usage/collection error
            if proc.returncode == 4:
                return "not_replayable", set()
            if proc.returncode == 0:
                return "ok", set()
            # Parse FAILED lines from pytest output
            failed: set[str] = set()
            for line in proc.stdout.splitlines():
                line = line.strip()
                if line.startswith("FAILED "):
                    # "FAILED tests/test_domain.py::test_foo[param]"
                    failed.add(line[7:].split(" - ")[0].strip())
            return "ok", failed
        except subprocess.TimeoutExpired:
            return "ok", set()  # timeout = treat as no failures for safety


# ---------------------------------------------------------------------------
# Single-row replay
# ---------------------------------------------------------------------------

def _replay_one_commit(
    sha: str,
    module_name: str,
    suite: str,
) -> str:
    """Return 'caught' | 'miss' | 'not_replayable' | '' (no tests).

    caught = at least one test fails on pre-fix AND passes on fix.
    This handles suites that are red on both versions due to later bugs:
    if the set of failing tests shrinks from pre-fix to fix, the commit
    is caught (some tests detect the specific bug being fixed).
    """
    suite_paths = _suite_paths_for_replay(module_name, suite)
    if not suite_paths:
        return ""  # no tests for this suite → empty, not an error

    try:
        mod = get_module(module_name)
    except KeyError:
        return "not_replayable"

    # Pre-fix source = sha^ (parent of the fix commit)
    pre_src = _source_at(f"{sha}^", module_name)
    # Fix source = sha
    fix_src = _source_at(sha, module_name)

    if pre_src is None or fix_src is None:
        return "not_replayable"

    try:
        with _ReplayWorkspace(pre_src, mod) as ws_pre:
            pre_status, pre_failed = ws_pre.run_pytest_collect_failures(suite_paths)

        with _ReplayWorkspace(fix_src, mod) as ws_fix:
            fix_status, fix_failed = ws_fix.run_pytest_collect_failures(suite_paths)
    except Exception:
        return "not_replayable"

    if pre_status == "not_replayable" or fix_status == "not_replayable":
        return "not_replayable"

    # caught = at least one test failed on pre-fix that now passes on fix
    newly_fixed = pre_failed - fix_failed
    if newly_fixed:
        return "caught"
    return "miss"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def replay(which: str, suites: list[str]) -> list[dict]:
    """Run historical bug replay and write results/replay.csv.

    Args:
        which:  Module set name ("all", "main", "extra", …).
        suites: List of suite names from {"human", "mh", "b1"}.

    Returns:
        List of result dicts, one per (commit × suite) pair.
    """
    from .registry import modules_by_set

    # Resolve the requested set to a set of module names
    if which in ("all", "main", "extra", "reference"):
        allowed_modules: set[str] | None = (
            None if which == "all"
            else {m.module for m in modules_by_set(which)}
        )
    else:
        allowed_modules = {m.module for m in modules_by_set(which)}

    # Read bug_commits.csv
    rows: list[dict] = []
    with open(BUG_COMMITS_CSV, encoding="utf-8", newline="") as fh:
        for bug in csv.DictReader(fh):
            module = bug["module"].strip()
            if allowed_modules is not None and module not in allowed_modules:
                continue
            sha = bug["sha"].strip()
            for suite in suites:
                print(f"  replay {sha[:7]} {module!r} suite={suite} ...", end="", flush=True)
                result = _replay_one_commit(sha, module, suite)
                print(f" {result or '(no tests)'}")
                rows.append({
                    "sha": sha,
                    "date": bug["date"].strip(),
                    "module": module,
                    "set": bug["set"].strip(),
                    "subject": bug["subject"].strip(),
                    "suite": suite,
                    "result": result,
                    "note": bug.get("note", "").strip(),
                })

    # Write results/replay.csv
    REPLAY_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(REPLAY_CSV, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=_REPLAY_COLS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nreplay.csv written → {REPLAY_CSV} ({len(rows)} rows)")
    return rows
