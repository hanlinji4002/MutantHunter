"""Check — acceptance checker for one test file.

Confirms a test file passes on the original code, detects flakiness, and
scores it against split-A human survivors (from the most recent
results/mutants/<slug>__human__A.json).

Fixes applied:
- Fix 1: re-enumerates mutants via enumerate_mutants; runs each survivor in its
  own workspace in parallel (no longer relies on a "source" field in the JSON).
- Fix 2: when some tests fail on original, deselects them with --deselect when
  running the kill phase so a single failing baseline test doesn't swamp kills.
- Fix 3: drops -x from the original-check run; parses ALL failing test node IDs
  including parametrize IDs with spaces via -rf short-test-form.

Node-ID stability fix (Fixes 2 & 3 in practice):
  Pytest emits node IDs whose path prefix is whatever path you pass it.  Each
  baseline run uses a freshly-created workspace directory, so passing the
  absolute workspace path produces IDs like
    /private/var/.../mh_ws_abc/tests/test_foo.py::test_x
  which differ across the three runs, making set-intersection always empty and
  leaving always_failed == {}.  The fix is to invoke pytest with the test file
  as a *relative* path from ws.path (e.g. "tests/test_foo.py"), so every run
  and every kill-worker emits the same stable node ID form and --deselect
  matches correctly.
"""

from __future__ import annotations

import json
import re
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .isolation import Workspace, _make_env
from .mutate import enumerate_mutants
from .registry import REPO_ROOT, Module, TARGET_ROOT, VENV_PYTHON, suite_test_paths


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _copy_test_file_into_workspace(ws: Workspace, test_file: Path) -> Path:
    """Place the test file in the workspace and return its workspace-absolute path."""
    try:
        rel = test_file.relative_to(TARGET_ROOT)
        ws_path = ws.path / rel
    except ValueError:
        # External file — place it directly under workspace/tests/
        ws_path = ws.path / "tests" / test_file.name

    ws_path.parent.mkdir(parents=True, exist_ok=True)
    ws_path.write_text(test_file.read_text(encoding="utf-8"), encoding="utf-8")
    return ws_path


def _ws_rel_test_path(ws: Workspace, ws_file: Path) -> str:
    """Return the test file path relative to the workspace root as a POSIX string.

    Passing this relative string to pytest (with cwd=ws.path) ensures the node
    IDs emitted are identical across all workspace copies, e.g.:
      tests/test_foo.py::test_bar[not a url]
    regardless of the random workspace directory name.  This is required for
    set-intersection across repeat runs and for --deselect to match in the kill
    workers.
    """
    return ws_file.relative_to(ws.path).as_posix()


def _run_file_on_original(
    test_file: Path,
    deselect: Optional[List[str]] = None,
    timeout: int = 120,
) -> Tuple[int, str, str]:
    """Run the test file on the original code.

    Returns (returncode, stdout, stderr).
    Uses -v and -rf so we can harvest full node IDs.
    Does NOT use -x so all failures are reported.

    The test file is passed to pytest as a *relative* path from ws.path so
    that node IDs are workspace-independent (stable across the repeat runs).
    """
    with Workspace(target_root=TARGET_ROOT) as ws:
        ws_file = _copy_test_file_into_workspace(ws, test_file)
        rel_path = _ws_rel_test_path(ws, ws_file)
        cmd = [
            str(VENV_PYTHON),
            "-m", "pytest",
            "-v",
            "-p", "no:cacheprovider",
            "--tb=no",
            "--no-header",
            "-rf",           # show extra test summary for failed tests
        ]
        if deselect:
            for nid in deselect:
                cmd += ["--deselect", nid]
        cmd.append(rel_path)

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=_make_env(ws),
                cwd=str(ws.path),
            )
            return proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "TIMEOUT"


def _parse_failed_node_ids(stdout: str, stderr: str) -> List[str]:
    """Extract full pytest node IDs of FAILED tests from verbose output.

    Handles parametrize IDs with spaces by matching the -rf summary section:
      FAILED tests/...::test_name[param with spaces] - reason
    and the verbose per-test lines:
      FAILED tests/...::test_name[param with spaces]
    """
    failed: List[str] = []
    seen: Set[str] = set()

    for line in (stdout + "\n" + stderr).splitlines():
        # -rf summary line: "FAILED path::test[...] - reason"
        m = re.match(r"^FAILED\s+(\S.*?)(?:\s+-\s+.*)?$", line.rstrip())
        if m:
            nid = m.group(1).strip()
            if nid not in seen:
                seen.add(nid)
                failed.append(nid)
            continue
        # Verbose per-test line: "FAILED path::test[...]"  (no " - " suffix)
        m2 = re.match(r"^FAILED\s+(\S.+)$", line.rstrip())
        if m2:
            nid = m2.group(1).strip()
            if nid not in seen:
                seen.add(nid)
                failed.append(nid)

    return failed


# ---------------------------------------------------------------------------
# Worker for parallel kill check
# ---------------------------------------------------------------------------

def _check_one_mutant(args: Tuple) -> Tuple[str, str]:
    """Worker: run one mutant and return (mutant_id, 'killed'|'survived')."""
    (
        mutant_id,
        mutant_source,
        source_path_str,
        test_file_str,
        target_root_str,
        deselect_node_ids,
        timeout,
    ) = args

    source_path = Path(source_path_str)
    test_file = Path(test_file_str)
    target_root = Path(target_root_str)

    with Workspace(target_root=target_root) as ws:
        ws.write_source(source_path, mutant_source)
        ws_file = _copy_test_file_into_workspace(ws, test_file)
        # Use a workspace-relative path so node IDs match the stable form
        # produced by _run_file_on_original, making --deselect work correctly.
        rel_path = _ws_rel_test_path(ws, ws_file)

        cmd = [
            str(VENV_PYTHON),
            "-m", "pytest",
            "-x", "-q",
            "-p", "no:cacheprovider",
            "--tb=no",
        ]
        for nid in deselect_node_ids:
            cmd += ["--deselect", nid]
        cmd.append(rel_path)

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                timeout=timeout,
                env=_make_env(ws),
                cwd=str(ws.path),
            )
            status = "killed" if proc.returncode != 0 else "survived"
        except subprocess.TimeoutExpired:
            status = "killed"

    return mutant_id, status


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def check_file(
    module: Module,
    test_file: Path,
    repeat: int = 3,
    jobs: int = 4,
) -> Dict:
    """Check a single test file against split-A human survivors.

    Args:
        module: The module being tested.
        test_file: Path to the test file to check.
        repeat: Number of times to run the file on the original.
        jobs: Number of parallel workers for the kill phase.

    Returns:
        Dict matching the SPEC § 5.6 check output schema.
    """
    test_file = test_file.resolve()

    # ------------------------------------------------------------------
    # Step 1: load split-A survivor IDs from the most recent run JSON
    # ------------------------------------------------------------------
    survivors_path = (
        REPO_ROOT / "results" / "mutants"
        / f"{module.slug}__human__A.json"
    )
    survivor_ids: List[str] = []
    if survivors_path.exists():
        try:
            data = json.loads(survivors_path.read_text(encoding="utf-8"))
            survivor_ids = [s["id"] for s in data.get("survivors", [])]
        except Exception:
            survivor_ids = []

    # ------------------------------------------------------------------
    # Step 2: re-enumerate mutants to get their source
    # ------------------------------------------------------------------
    all_mutants = enumerate_mutants(module.source_path, module.slug)
    survivor_id_set = set(survivor_ids)
    survivor_mutants = [m for m in all_mutants if m.id in survivor_id_set]

    # ------------------------------------------------------------------
    # Step 3: run the test file on the original `repeat` times
    #         WITHOUT -x so we collect ALL failures
    # ------------------------------------------------------------------
    run_results: List[Tuple[int, List[str]]] = []
    collection_error = False

    for _ in range(repeat):
        rc, stdout, stderr = _run_file_on_original(test_file)
        if rc == 4:
            collection_error = True
        failed = _parse_failed_node_ids(stdout, stderr)
        run_results.append((rc, failed))

    all_failed_sets = [set(f) for _, f in run_results]
    any_failed = set.union(*all_failed_sets) if all_failed_sets else set()
    always_failed = set.intersection(*all_failed_sets) if all_failed_sets else set()

    passes_on_original = all(rc == 0 for rc, _ in run_results)
    flaky = bool(any_failed - always_failed)
    # Fix 3: full node IDs, sorted, including parametrize IDs with spaces
    failing_tests_on_original = sorted(always_failed)

    # ------------------------------------------------------------------
    # Step 4: kill phase — run each survivor's mutant in parallel
    #         Deselect always-failing tests so a red baseline test
    #         doesn't cause every mutant to appear killed.
    # ------------------------------------------------------------------
    # Deselect tests that always fail on original (Fix 2)
    deselect = list(always_failed)

    args_list = [
        (
            m.id,
            m.source,
            str(module.source_path),
            str(test_file),
            str(TARGET_ROOT),
            deselect,
            60,
        )
        for m in survivor_mutants
    ]

    kill_results: Dict[str, str] = {}
    if args_list:
        if jobs == 1:
            for args in args_list:
                mid, status = _check_one_mutant(args)
                kill_results[mid] = status
        else:
            with ProcessPoolExecutor(max_workers=jobs) as executor:
                futures = {executor.submit(_check_one_mutant, a): a[0] for a in args_list}
                for future in as_completed(futures):
                    mid, status = future.result()
                    kill_results[mid] = status

    kills = [mid for mid in survivor_ids if kill_results.get(mid) == "killed"]
    not_killed = [mid for mid in survivor_ids if kill_results.get(mid) != "killed"]

    return {
        "test_file": str(test_file),
        "passes_on_original": passes_on_original,
        "runs": repeat,
        "flaky": flaky,
        "collection_error": collection_error,
        "survivors_checked": len(survivor_mutants),
        "kills": kills,
        "not_killed": not_killed,
        "kills_note": "",
        "failing_tests_on_original": failing_tests_on_original,
    }
