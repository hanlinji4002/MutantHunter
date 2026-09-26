"""Registry — dataset/modules.csv reader and path resolver.

Single source of truth for every module's paths, set membership, spec list,
and reference baseline counts. Nothing else in the package parses modules.csv.
"""

from __future__ import annotations

import csv
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


# ---------------------------------------------------------------------------
# Repo-root discovery
# ---------------------------------------------------------------------------

def _repo_root() -> Path:
    """Walk up from this file until a directory containing dataset/modules.csv is found."""
    candidate = Path(__file__).resolve().parent
    for p in [candidate, *candidate.parents]:
        if (p / "dataset" / "modules.csv").exists():
            return p
    raise RuntimeError(
        "Cannot find repo root: no ancestor of "
        f"{Path(__file__)} contains dataset/modules.csv"
    )


REPO_ROOT: Path = _repo_root()
TARGET_ROOT: Path = REPO_ROOT / "targets" / "validators"
import os as _os
VENV_PYTHON: Path = (
    TARGET_ROOT / ".venv" / "Scripts" / "python.exe"
    if _os.name == "nt"
    else TARGET_ROOT / ".venv" / "bin" / "python"
)


# ---------------------------------------------------------------------------
# Module dataclass
# ---------------------------------------------------------------------------

@dataclass
class Module:
    """One row of dataset/modules.csv."""

    module: str          # e.g. "url" or "i18n/fi"
    slug: str            # module with "/" replaced by "__"
    source_path: Path    # absolute path to the .py source file
    test_path: Path      # absolute path to the test file
    set: str             # "main" | "extra" | "reference"
    specs: List[str]     # list of spec document filenames (may be empty)
    ref_mutants: int
    ref_killed: int


# ---------------------------------------------------------------------------
# CSV loading
# ---------------------------------------------------------------------------

def _load_modules() -> List[Module]:
    csv_path = REPO_ROOT / "dataset" / "modules.csv"
    modules: List[Module] = []
    with open(csv_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            module = row["module"].strip()
            slug = module.replace("/", "__")
            specs_raw = row.get("specs", "").strip()
            specs = [s.strip() for s in specs_raw.split(";") if s.strip()]
            modules.append(
                Module(
                    module=module,
                    slug=slug,
                    source_path=TARGET_ROOT / row["source_path"].strip(),
                    test_path=TARGET_ROOT / row["test_path"].strip(),
                    set=row["set"].strip(),
                    specs=specs,
                    ref_mutants=int(row["ref_mutants"].strip()),
                    ref_killed=int(row["ref_killed"].strip()),
                )
            )
    return modules


_MODULES: List[Module] = _load_modules()
_BY_NAME: dict = {m.module: m for m in _MODULES}


# ---------------------------------------------------------------------------
# Public accessors
# ---------------------------------------------------------------------------

def all_modules() -> List[Module]:
    """Return all 24 modules in CSV order."""
    return list(_MODULES)


def modules_by_set(set_name: str) -> List[Module]:
    """Return modules filtered by set name.

    Args:
        set_name: "main", "extra", "reference", or "all".
                  Also accepts a comma-separated list of module names.

    Returns:
        List of matching Module objects.
    """
    if set_name == "all":
        return list(_MODULES)
    if set_name in ("main", "extra", "reference"):
        return [m for m in _MODULES if m.set == set_name]
    # Treat as comma-separated list of module names
    names = [n.strip() for n in set_name.split(",")]
    result = []
    for name in names:
        if name in _BY_NAME:
            result.append(_BY_NAME[name])
        else:
            raise KeyError(f"Unknown module: {name!r}")
    return result


def get_module(name: str) -> Module:
    """Return a single Module by name; raises KeyError if not found."""
    try:
        return _BY_NAME[name]
    except KeyError:
        raise KeyError(f"Unknown module: {name!r}")


def suite_test_paths(
    module: Module,
    suite: str,
    target_root: Optional[Path] = None,
) -> List[Path]:
    """Return the list of test paths for the given suite.

    Args:
        module: A Module instance.
        suite: "human", "human+mh", or "human+b1".
        target_root: Root of the validators project; defaults to TARGET_ROOT.

    Returns:
        List of absolute Path objects for pytest to collect.
    """
    root = target_root if target_root is not None else TARGET_ROOT
    base = root / module.test_path.relative_to(TARGET_ROOT)
    paths = [base]

    if suite in ("human+mh", "human+b1"):
        subfolder_name = "mh" if suite == "human+mh" else "b1"
        extra = root / "tests" / subfolder_name / module.slug
        if not extra.exists() or not any(extra.iterdir()):
            warnings.warn(
                f"Suite {suite!r}: extra test dir {extra} is missing or empty; "
                f"falling back to human suite only.",
                stacklevel=2,
            )
        else:
            paths.append(extra)
    elif suite != "human":
        raise ValueError(f"Unknown suite: {suite!r}")

    return paths
