"""conftest.py — shared fixtures for MutantHunter unit tests."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Synthetic Python source fixtures
# ---------------------------------------------------------------------------

SIMPLE_SOURCE = textwrap.dedent("""\
    def add(a, b):
        return a + b

    def is_positive(x):
        if x > 0:
            return True
        return False

    def clamp(val, lo, hi):
        if val < lo:
            return lo
        if val > hi:
            return hi
        return val

    def compare_chain(a, b, c):
        if a < b < c:
            return True
        return False
""")

RED_SOURCE = textwrap.dedent("""\
    def broken():
        raise RuntimeError("always fails")
""")

RED_TEST = textwrap.dedent("""\
    from validators_stub import broken

    def test_always_fails():
        broken()  # will raise
""")

GREEN_TEST = textwrap.dedent("""\
    def test_always_passes():
        assert 1 + 1 == 2
""")


@pytest.fixture()
def tmp_src_dir(tmp_path: Path) -> Path:
    """A minimal src/validators directory with a simple module."""
    src = tmp_path / "src" / "validators"
    src.mkdir(parents=True)
    (src / "__init__.py").write_text(
        "from .simple import add, is_positive, clamp, compare_chain\n",
        encoding="utf-8",
    )
    (src / "simple.py").write_text(SIMPLE_SOURCE, encoding="utf-8")
    return src


@pytest.fixture()
def simple_source_file(tmp_path: Path) -> Path:
    """A standalone Python source file for operator enumeration tests."""
    f = tmp_path / "simple.py"
    f.write_text(SIMPLE_SOURCE, encoding="utf-8")
    return f
