"""Isolation — safe workspaces and pytest runner.

Guards against the three silent failures documented in SPEC § 5.2:

1. Editable install: always run with PYTHONPATH=<copy>/src so the venv's
   editable install does not shadow the mutated copy.  Verified by asserting
   validators.__file__ is inside the workspace directory.

2. Red baseline: the suite must pass on the original source and on the
   ast.unparse()-round-tripped source before any mutant is run.

3. Stale bytecode: PYTHONDONTWRITEBYTECODE=1 is set in every subprocess env;
   __pycache__ directories are never copied into a workspace.
"""

from __future__ import annotations

import ast
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .registry import Module, TARGET_ROOT, VENV_PYTHON


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class IsolationError(RuntimeError):
    """Raised when isolation cannot be confirmed (exit code 3)."""


class BaselineError(RuntimeError):
    """Raised when the baseline suite is not green (exit code 2)."""


# ---------------------------------------------------------------------------
# Workspace context manager
# ---------------------------------------------------------------------------

class Workspace:
    """A temporary copy of src/ and tests/ for one mutation worker.

    Usage::

        with Workspace() as ws:
            ws.write_source(module.source_path, mutated_source)
            result = run_pytest(ws, suite_paths)
    """

    def __init__(self, target_root: Optional[Path] = None) -> None:
        self._target_root = target_root or TARGET_ROOT
        self.path: Path = Path(tempfile.mkdtemp(prefix="mh_ws_"))

    def __enter__(self) -> "Workspace":
        self._setup()
        return self

    def __exit__(self, *_) -> None:
        shutil.rmtree(self.path, ignore_errors=True)

    def _setup(self) -> None:
        """Copy src/ and tests/ into the workspace, skipping __pycache__."""
        ignore = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")
        src_dir = self._target_root / "src"
        tests_dir = self._target_root / "tests"
        if src_dir.exists():
            shutil.copytree(src_dir, self.path / "src", ignore=ignore)
        if tests_dir.exists():
            shutil.copytree(tests_dir, self.path / "tests", ignore=ignore)

    def source_path(self, original: Path) -> Path:
        """Translate an absolute source path to its copy inside the workspace."""
        rel = original.relative_to(self._target_root / "src")
        return self.path / "src" / rel

    def test_path(self, original: Path) -> Path:
        """Translate an absolute test path to its copy inside the workspace."""
        rel = original.relative_to(self._target_root)
        return self.path / rel

    def rebase_paths(self, paths: List[Path]) -> List[Path]:
        """Rebase a list of absolute paths to their workspace equivalents."""
        rebased = []
        for p in paths:
            try:
                rel = p.relative_to(self._target_root)
                rebased.append(self.path / rel)
            except ValueError:
                # Path is already absolute but not under target_root — pass through
                rebased.append(p)
        return rebased

    def write_source(self, original: Path, source: str) -> None:
        """Overwrite the workspace copy of a source file with mutated source."""
        ws_path = self.source_path(original)
        ws_path.write_text(source, encoding="utf-8")

    def restore_source(self, original: Path) -> None:
        """Restore the workspace copy of a source file from the original."""
        ws_path = self.source_path(original)
        ws_path.write_text(original.read_text(encoding="utf-8"), encoding="utf-8")

    @property
    def pythonpath(self) -> str:
        """The PYTHONPATH value for subprocess calls."""
        return str(self.path / "src")


# ---------------------------------------------------------------------------
# subprocess environment
# ---------------------------------------------------------------------------

def _make_env(workspace: Workspace) -> Dict[str, str]:
    """Build the subprocess environment with all isolation guards set."""
    env = os.environ.copy()
    env["PYTHONPATH"] = workspace.pythonpath
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    # Remove any pytest cache env that might interfere
    env.pop("PYTEST_CURRENT_TEST", None)
    return env


# ---------------------------------------------------------------------------
# Pytest runner
# ---------------------------------------------------------------------------

def run_pytest(
    workspace: Workspace,
    suite_paths: List[Path],
    timeout: int = 60,
    extra_args: Optional[List[str]] = None,
) -> str:
    """Run pytest in the workspace and return "survived" or "killed".

    Exit 0 → survived; anything else → killed.
    """
    rebased = workspace.rebase_paths(suite_paths)
    # Filter to only paths that actually exist in the workspace
    existing = [str(p) for p in rebased if p.exists()]
    if not existing:
        # No test files found — treat as survived (nothing to kill it)
        return "survived"

    cmd = [
        str(VENV_PYTHON),
        "-m", "pytest",
        "-x", "-q",
        "-p", "no:cacheprovider",
        "--tb=no",
        "--no-header",
    ]
    if extra_args:
        cmd.extend(extra_args)
    cmd.extend(existing)

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            timeout=timeout,
            env=_make_env(workspace),
            cwd=str(workspace.path),
        )
        return "survived" if proc.returncode == 0 else "killed"
    except subprocess.TimeoutExpired:
        return "killed"


def run_pytest_verbose(
    workspace: Workspace,
    suite_paths: List[Path],
    timeout: int = 60,
) -> Tuple[int, str, str]:
    """Run pytest and return (returncode, stdout, stderr)."""
    rebased = workspace.rebase_paths(suite_paths)
    existing = [str(p) for p in rebased if p.exists()]
    if not existing:
        return 0, "", ""

    cmd = [
        str(VENV_PYTHON),
        "-m", "pytest",
        "-x", "-q",
        "-p", "no:cacheprovider",
        "--tb=short",
        "-v",
    ]
    cmd.extend(existing)

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=_make_env(workspace),
            cwd=str(workspace.path),
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "TIMEOUT"


# ---------------------------------------------------------------------------
# Guard 1: editable-install check
# ---------------------------------------------------------------------------

def check_isolation(workspace: Workspace, module: Module) -> None:
    """Verify that validators is imported from the workspace copy.

    Raises IsolationError if the import path is not inside the workspace.
    """
    cmd = [
        str(VENV_PYTHON),
        "-c",
        "import validators; print(validators.__file__)",
    ]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30,
        env=_make_env(workspace),
        cwd=str(workspace.path),
    )
    if proc.returncode != 0:
        raise IsolationError(
            f"Cannot import validators in workspace {workspace.path}: "
            f"{proc.stderr.strip()}"
        )
    imported_path = proc.stdout.strip()
    ws_src = str(workspace.path / "src")
    if not imported_path.startswith(ws_src):
        raise IsolationError(
            f"Editable-install guard failed: validators imported from "
            f"{imported_path!r} which is not inside workspace {ws_src!r}. "
            "Ensure PYTHONPATH is set to <workspace>/src."
        )


# ---------------------------------------------------------------------------
# Guard 2: red-baseline check
# ---------------------------------------------------------------------------

def check_baseline(
    workspace: Workspace,
    module: Module,
    suite_paths: List[Path],
) -> None:
    """Assert the suite passes on original source and on ast.unparse round-trip.

    Raises BaselineError if either run fails.
    """
    # Pass 1: original source (already copied)
    result = run_pytest(workspace, suite_paths, timeout=120)
    if result != "survived":
        raise BaselineError(
            f"Baseline check failed on original source for module "
            f"{module.module!r}: suite is red."
        )

    # Pass 2: ast.unparse round-trip
    original_source = module.source_path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(original_source)
        unparsed = ast.unparse(tree)
        ast.parse(unparsed)  # confirm it compiles
    except SyntaxError as exc:
        raise BaselineError(
            f"ast.unparse round-trip produced invalid syntax for "
            f"{module.module!r}: {exc}"
        ) from exc

    workspace.write_source(module.source_path, unparsed)
    try:
        result2 = run_pytest(workspace, suite_paths, timeout=120)
    finally:
        workspace.restore_source(module.source_path)

    if result2 != "survived":
        raise BaselineError(
            f"Baseline check failed on ast.unparse round-trip for module "
            f"{module.module!r}: suite is red after unparsing."
        )


# ---------------------------------------------------------------------------
# Worker function (module-level so it is picklable)
# ---------------------------------------------------------------------------

def _run_one_mutant(args: Tuple) -> Tuple[int, str]:
    """Worker: run one mutant in its own workspace and return (index, status)."""
    (
        idx,
        source_path_str,
        mutated_source,
        suite_paths_strs,
        target_root_str,
        timeout,
    ) = args

    source_path = Path(source_path_str)
    suite_paths = [Path(p) for p in suite_paths_strs]
    target_root = Path(target_root_str)

    with Workspace(target_root=target_root) as ws:
        ws.write_source(source_path, mutated_source)
        status = run_pytest(ws, suite_paths, timeout=timeout)

    return idx, status


# ---------------------------------------------------------------------------
# Parallel runner
# ---------------------------------------------------------------------------

def run_all_mutants(
    mutant_sources: List[Tuple[int, str]],  # (index, mutated_source_str)
    source_path: Path,
    suite_paths: List[Path],
    jobs: int = 4,
    target_root: Optional[Path] = None,
    timeout: int = 60,
) -> List[str]:
    """Run all mutants in parallel and return statuses in original order.

    Args:
        mutant_sources: List of (original_index, mutated_source_string).
        source_path: Absolute path to the original source file.
        suite_paths: List of absolute test paths.
        jobs: Number of parallel workers.
        target_root: Root of the validators project.
        timeout: Per-mutant pytest timeout in seconds.

    Returns:
        List of "survived" | "killed" in the same order as mutant_sources.
    """
    root = target_root or TARGET_ROOT
    suite_strs = [str(p) for p in suite_paths]
    source_str = str(source_path)
    root_str = str(root)

    args_list = [
        (idx, source_str, src, suite_strs, root_str, timeout)
        for idx, src in mutant_sources
    ]

    results: Dict[int, str] = {}

    if jobs == 1:
        for args in args_list:
            idx, status = _run_one_mutant(args)
            results[idx] = status
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            futures = {executor.submit(_run_one_mutant, a): a[0] for a in args_list}
            for future in as_completed(futures):
                idx, status = future.result()
                results[idx] = status

    # Return in original enumeration order
    return [results[idx] for idx, _ in mutant_sources]
