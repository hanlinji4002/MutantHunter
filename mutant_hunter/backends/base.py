"""Backends base — AgentBackend interface and shared cost logger.

Defines the abstract base class that all backends must implement, the
WorkPackage dataclass, the shared cost-logging helper, and BackendError.

Cost logs are written to results/costs_<member>.csv (one file per team
member, so two contributors never edit the same file).
"""

from __future__ import annotations

import abc
import csv
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from ..registry import REPO_ROOT


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class BackendError(RuntimeError):
    """Raised when a required backend binary is not installed."""


# ---------------------------------------------------------------------------
# WorkPackage dataclass
# ---------------------------------------------------------------------------

@dataclass
class WorkPackage:
    """Input for a backend generate_tests call."""

    module: str                      # module name, e.g. "url"
    suite: str                       # target suite, e.g. "mh" or "b1"
    split_a_survivors: List[dict]    # survivor dicts from mutation run JSON
    rules_file: Optional[Path]       # path to <slug>_rules.md, or None
    max_cost: Optional[float]        # max cost in bobcoins, or None


# ---------------------------------------------------------------------------
# Abstract base class
# ---------------------------------------------------------------------------

class AgentBackend(abc.ABC):
    """Abstract base for agent-based test generators."""

    @abc.abstractmethod
    def generate_tests(self, work_package: WorkPackage) -> List[Path]:
        """Generate test files for the given work package.

        Args:
            work_package: Input data for test generation.

        Returns:
            List of paths to newly created test files.
        """


# ---------------------------------------------------------------------------
# Cost logger
# ---------------------------------------------------------------------------

_COST_HEADER = ["timestamp", "module", "suite", "backend", "minutes", "bobcoins", "source"]


def record_cost(
    member: str,
    module: str,
    suite: str,
    backend: str,
    minutes: float,
    bobcoins: Optional[float],
    source: str,
) -> None:
    """Append one cost row to results/costs_<member>.csv.

    Creates the file with a header row on first write; appends thereafter.

    Args:
        member: Team member identifier (e.g. the MH_MEMBER env var).
        module: Module name (e.g. "url").
        suite: Suite name (e.g. "mh").
        backend: Backend name (e.g. "bob").
        minutes: Wall-clock minutes consumed.
        bobcoins: Bob credits consumed, or None if not applicable.
        source: Free-text source description.
    """
    results_dir = REPO_ROOT / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / f"costs_{member}.csv"

    write_header = not csv_path.exists()
    with open(csv_path, "a", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        if write_header:
            writer.writerow(_COST_HEADER)
        writer.writerow([
            datetime.now(timezone.utc).isoformat(),
            module,
            suite,
            backend,
            round(minutes, 4),
            bobcoins if bobcoins is not None else "",
            source,
        ])


def get_member() -> str:
    """Return the current team member identifier from the MH_MEMBER env var."""
    return os.environ.get("MH_MEMBER", "unknown")
