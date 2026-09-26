"""Unit tests for mutant_hunter.exam_c — one test per operator."""
from __future__ import annotations

import textwrap

import pytest

from mutant_hunter.exam_c import enumerate_exam_c


# --------------------------------------------------------------------------- #
# Operator 1: bool_flip
# --------------------------------------------------------------------------- #

def test_bool_flip_true_to_false():
    """One True constant → flipped to False."""
    src = textwrap.dedent("""\
        def f():
            return True
    """)
    mutants = enumerate_exam_c(src, "test")
    ops = [m.op for m in mutants]
    assert any(op == "bool_flip_true_to_false" for op in ops)
    m = next(m for m in mutants if m.op == "bool_flip_true_to_false")
    assert m.split == "C"
    assert "False" in m.source
    assert m.original == "True"
    assert m.mutated == "False"


def test_bool_flip_false_to_true():
    """One False constant → flipped to True."""
    src = textwrap.dedent("""\
        def f():
            return False
    """)
    mutants = enumerate_exam_c(src, "test")
    ops = [m.op for m in mutants]
    assert any(op == "bool_flip_false_to_true" for op in ops)
    m = next(m for m in mutants if m.op == "bool_flip_false_to_true")
    assert m.original == "False"
    assert m.mutated == "True"


# --------------------------------------------------------------------------- #
# Operator 2: not_drop
# --------------------------------------------------------------------------- #

def test_not_drop():
    """A `not x` expression → the bare `x`."""
    src = textwrap.dedent("""\
        def f(x):
            if not x:
                return 1
            return 2
    """)
    mutants = enumerate_exam_c(src, "test")
    ops = [m.op for m in mutants]
    assert "not_drop" in ops, f"expected not_drop, got {ops}"
    m = next(m for m in mutants if m.op == "not_drop")
    assert m.split == "C"
    assert "not x" in m.original
    assert m.mutated == "x"


# --------------------------------------------------------------------------- #
# Operator 3: str_surround
# --------------------------------------------------------------------------- #

def test_str_surround_basic():
    """A plain string constant is wrapped with 'XX'."""
    src = textwrap.dedent("""\
        def f(v):
            return v == "hello"
    """)
    mutants = enumerate_exam_c(src, "test")
    ops = [m.op for m in mutants]
    assert "str_surround" in ops, f"expected str_surround, got {ops}"
    m = next(m for m in mutants if m.op == "str_surround")
    assert m.split == "C"
    assert "XX" in m.source


def test_str_surround_skips_docstring():
    """The module/function docstring must NOT be mutated."""
    src = textwrap.dedent("""\
        def f(v):
            \"\"\"A docstring.\"\"\"
            return v == "ok"
    """)
    mutants = enumerate_exam_c(src, "test")
    # Only "ok" should be surrounded, not the docstring
    surround = [m for m in mutants if m.op == "str_surround"]
    assert all("docstring" not in m.original for m in surround)


def test_str_surround_skips_large_container():
    """Strings inside a list with > 8 entries are skipped."""
    items = ", ".join(f'"item{i}"' for i in range(10))
    src = f"DATA = [{items}]\n"
    mutants = enumerate_exam_c(src, "test")
    surround = [m for m in mutants if m.op == "str_surround"]
    assert surround == [], f"expected no str_surround mutations, got {surround}"


# --------------------------------------------------------------------------- #
# Operator 4: method_drop
# --------------------------------------------------------------------------- #

def test_method_drop_lower():
    """A no-arg .lower() call is dropped, leaving just the receiver."""
    src = textwrap.dedent("""\
        def f(s):
            return s.lower()
    """)
    mutants = enumerate_exam_c(src, "test")
    ops = [m.op for m in mutants]
    assert "method_drop_lower" in ops, f"expected method_drop_lower, got {ops}"
    m = next(m for m in mutants if m.op == "method_drop_lower")
    assert m.split == "C"
    assert m.mutated == "s"


def test_method_drop_strip():
    """A no-arg .strip() call is dropped."""
    src = textwrap.dedent("""\
        def f(s):
            return s.strip()
    """)
    mutants = enumerate_exam_c(src, "test")
    ops = [m.op for m in mutants]
    assert "method_drop_strip" in ops


def test_method_drop_ignores_args():
    """A .strip('x') call (with argument) must NOT be mutated."""
    src = textwrap.dedent("""\
        def f(s):
            return s.strip('x')
    """)
    mutants = enumerate_exam_c(src, "test")
    ops = [m.op for m in mutants]
    assert "method_drop_strip" not in ops


# --------------------------------------------------------------------------- #
# Operator 5: augassign_flip
# --------------------------------------------------------------------------- #

def test_augassign_add_to_sub():
    """`+=` is flipped to `-=`."""
    src = textwrap.dedent("""\
        def f(x):
            x += 1
            return x
    """)
    mutants = enumerate_exam_c(src, "test")
    ops = [m.op for m in mutants]
    assert "augassign_add_to_sub" in ops, f"expected augassign_add_to_sub, got {ops}"
    m = next(m for m in mutants if m.op == "augassign_add_to_sub")
    assert m.split == "C"
    assert "-=" in m.source


def test_augassign_sub_to_add():
    """`-=` is flipped to `+=`."""
    src = textwrap.dedent("""\
        def f(x):
            x -= 1
            return x
    """)
    mutants = enumerate_exam_c(src, "test")
    ops = [m.op for m in mutants]
    assert "augassign_sub_to_add" in ops, f"expected augassign_sub_to_add, got {ops}"
    m = next(m for m in mutants if m.op == "augassign_sub_to_add")
    assert "+=" in m.source


# --------------------------------------------------------------------------- #
# Cross-cutting: all mutants carry split='C' and a non-empty .source
# --------------------------------------------------------------------------- #

def test_all_mutants_split_c_and_have_source():
    """Every mutant produced by enumerate_exam_c must have split='C' and source set."""
    src = textwrap.dedent("""\
        def process(s, flag=True):
            if not flag:
                return s.lower().strip()
            s += "x"
            return s
    """)
    mutants = enumerate_exam_c(src, "test")
    assert mutants, "expected at least one mutant"
    for m in mutants:
        assert m.split == "C", f"{m.id} has split={m.split!r}"
        assert m.source, f"{m.id} has empty source"
