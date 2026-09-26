"""Tests for mutant_hunter.mutate — operators, IDs, splits."""
from __future__ import annotations

import ast
import hashlib
import textwrap
from pathlib import Path

import pytest

from mutant_hunter.mutate import (
    Mutant,
    enumerate_mutants,
    split_assign,
    _mutant_id,
)


# ---------------------------------------------------------------------------
# Synthetic sources
# ---------------------------------------------------------------------------

CHAINED_CMP_SOURCE = textwrap.dedent("""\
    def f(a, b, c):
        if a < b < c:
            return True
        return False
""")

NESTED_CMP_SOURCE = textwrap.dedent("""\
    def g(x, y, z):
        return (x < y) and (x < z)
""")

ALL_OPS_SOURCE = textwrap.dedent("""\
    def ops(a, b):
        r1 = a + b
        r2 = a - b
        r3 = a * b
        r4 = a // b
        r5 = a / b
        r6 = a % b
        if a > b:
            return a
        if a == b:
            return b
        if a and b:
            return True
        if a or b:
            return False
        return None

    def falsy(x):
        if x < 0:
            return False
        return x + 1
""")

RETURN_NONE_SOURCE = textwrap.dedent("""\
    def valid(x):
        if x < 0:
            return False
        if x > 100:
            return True
        return x
""")


class TestEnumerateMutants:
    def test_produces_mutants(self, simple_source_file):
        mutants = enumerate_mutants(simple_source_file, "simple")
        assert len(mutants) > 0

    def test_all_have_ids(self, simple_source_file):
        mutants = enumerate_mutants(simple_source_file, "simple")
        for m in mutants:
            assert m.id.startswith("simple:")
            assert len(m.id.split(":")) == 6

    def test_all_have_source(self, simple_source_file):
        mutants = enumerate_mutants(simple_source_file, "simple")
        for m in mutants:
            assert m.source, f"Mutant {m.id} has empty source"

    def test_all_source_compiles(self, simple_source_file):
        mutants = enumerate_mutants(simple_source_file, "simple")
        for m in mutants:
            try:
                ast.parse(m.source)
            except SyntaxError as exc:
                pytest.fail(f"Mutant {m.id} produced invalid source: {exc}")

    def test_deterministic_order(self, simple_source_file):
        """Calling enumerate_mutants twice returns the same ordered list."""
        m1 = enumerate_mutants(simple_source_file, "simple")
        m2 = enumerate_mutants(simple_source_file, "simple")
        assert [m.id for m in m1] == [m.id for m in m2]

    def test_all_ops_present(self, tmp_path):
        f = tmp_path / "all_ops.py"
        f.write_text(ALL_OPS_SOURCE, encoding="utf-8")
        mutants = enumerate_mutants(f, "all_ops")
        ops = {m.op for m in mutants}
        # Check each op family is present
        assert any(op.startswith("bin_") for op in ops), "No bin_ operators"
        assert any(op.startswith("cmp_") for op in ops), "No cmp_ operators"
        assert any(op.startswith("bool_") for op in ops), "No bool_ operators"
        assert "if_negate" in ops
        assert "return_none" in ops

    def test_int_plus_one_present(self, tmp_path):
        src = "def f(n):\n    return n + 1\n"
        f = tmp_path / "int_src.py"
        f.write_text(src, encoding="utf-8")
        mutants = enumerate_mutants(f, "int_src")
        ops = {m.op for m in mutants}
        assert "int_plus_one" in ops


class TestUniqueIDsOnNestedExpressions:
    """SPEC § 5.3: IDs include end positions to disambiguate nested expressions."""

    def test_chained_comparison_has_hash_suffixes(self, tmp_path):
        """a < b < c should produce two mutants with #1 and #2 suffixes."""
        f = tmp_path / "chained.py"
        f.write_text(CHAINED_CMP_SOURCE, encoding="utf-8")
        mutants = enumerate_mutants(f, "chained")
        chained_ids = [m.id for m in mutants if "#" in m.id]
        assert len(chained_ids) >= 2, f"Expected ≥2 chained mutants, got: {chained_ids}"
        suffixes = [mid.split("#")[1] for mid in chained_ids]
        assert "1" in suffixes
        assert "2" in suffixes

    def test_nested_compares_have_unique_ids(self, tmp_path):
        """(x < y) and (x < z) should produce two distinct cmp mutants."""
        f = tmp_path / "nested.py"
        f.write_text(NESTED_CMP_SOURCE, encoding="utf-8")
        mutants = enumerate_mutants(f, "nested")
        cmp_ids = [m.id for m in mutants if m.op.startswith("cmp_")]
        assert len(cmp_ids) == len(set(cmp_ids)), "Duplicate mutant IDs found"
        assert len(cmp_ids) >= 2, f"Expected ≥2 cmp mutants, got {len(cmp_ids)}"

    def test_all_ids_globally_unique(self, simple_source_file):
        mutants = enumerate_mutants(simple_source_file, "simple")
        ids = [m.id for m in mutants]
        assert len(ids) == len(set(ids)), "Duplicate mutant IDs detected"


class TestSplitAssignment:
    def test_deterministic(self):
        mid = "url:75:4:76:19:if_negate"
        s1 = split_assign(mid)
        s2 = split_assign(mid)
        assert s1 == s2

    def test_returns_a_or_b(self):
        for i in range(50):
            mid = f"url:{i}:0:{i}:10:if_negate"
            assert split_assign(mid) in ("A", "B")

    def test_sha256_parity(self):
        """Manually verify the sha256 parity logic."""
        mid = "url:75:4:76:19:if_negate"
        data = f"20260925:{mid}".encode()
        first_byte = hashlib.sha256(data).digest()[0]
        expected = "B" if first_byte & 1 else "A"
        assert split_assign(mid) == expected

    def test_both_splits_produced_in_practice(self, simple_source_file):
        """With enough mutants, both A and B should appear."""
        mutants = enumerate_mutants(simple_source_file, "simple")
        splits = {m.split for m in mutants}
        assert "A" in splits
        assert "B" in splits

    def test_different_seeds(self):
        mid = "url:75:4:76:19:if_negate"
        s1 = split_assign(mid, seed=20260925)
        s2 = split_assign(mid, seed=99999999)
        # Different seeds should generally produce at least some different results
        # (this just confirms the seed is used)
        data1 = f"20260925:{mid}".encode()
        data2 = f"99999999:{mid}".encode()
        b1 = hashlib.sha256(data1).digest()[0]
        b2 = hashlib.sha256(data2).digest()[0]
        expected1 = "B" if b1 & 1 else "A"
        expected2 = "B" if b2 & 1 else "A"
        assert s1 == expected1
        assert s2 == expected2


class TestFalsyPreserving:
    def test_return_false_flagged(self, tmp_path):
        f = tmp_path / "rf.py"
        f.write_text(RETURN_NONE_SOURCE, encoding="utf-8")
        mutants = enumerate_mutants(f, "rf")
        rn_mutants = [m for m in mutants if m.op == "return_none"]
        assert len(rn_mutants) >= 3  # return False, return True, return x

        falsy = [m for m in rn_mutants if m.falsy_preserving]
        assert len(falsy) >= 1
        for m in falsy:
            assert m.original == "False"

        non_falsy = [m for m in rn_mutants if not m.falsy_preserving]
        for m in non_falsy:
            assert m.original != "False"


class TestMutantFields:
    def test_mutant_has_all_required_fields(self, simple_source_file):
        mutants = enumerate_mutants(simple_source_file, "simple")
        assert mutants, "No mutants produced"
        m = mutants[0]
        # All required fields exist
        assert isinstance(m.id, str)
        assert isinstance(m.op, str)
        assert isinstance(m.line, int) and m.line >= 1
        assert isinstance(m.col, int)
        assert isinstance(m.end_line, int)
        assert isinstance(m.end_col, int)
        assert isinstance(m.function, str)
        assert isinstance(m.original, str)
        assert isinstance(m.mutated, str)
        assert isinstance(m.falsy_preserving, bool)
        assert m.split in ("A", "B")
        assert isinstance(m.source, str) and m.source

    def test_function_name_captured(self, simple_source_file):
        mutants = enumerate_mutants(simple_source_file, "simple")
        # Mutants from is_positive should have function == "is_positive"
        ip_mutants = [m for m in mutants if m.function == "is_positive"]
        assert ip_mutants, "No mutants found for is_positive"

    def test_id_format(self, simple_source_file):
        mutants = enumerate_mutants(simple_source_file, "simple")
        for m in mutants:
            parts = m.id.split(":")
            # format: slug:line:col:end_line:end_col:op (op may contain #)
            assert len(parts) >= 6, f"Bad ID format: {m.id}"
            slug = parts[0]
            assert slug == "simple"
            assert parts[1].isdigit()  # line
            assert parts[2].isdigit()  # col
            assert parts[3].isdigit()  # end_line
            assert parts[4].isdigit()  # end_col
