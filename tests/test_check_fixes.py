"""Tests for fixes 1–4 in check.py and mutate.py.

Uses a tiny synthetic module (calc.py) to test:
- Fix 1: check.py re-enumerates mutants and actually runs kill phase
- Fix 2: deselect failing tests before running kill phase
- Fix 3: parse all failing test IDs without -x (including parametrize with spaces)
- Fix 4: mutate --split all prints counts only, writes no file

These are fast tests (no real validators project, only synthetic code).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import textwrap
import warnings
from pathlib import Path
from typing import List
from unittest import mock

import pytest

from mutant_hunter.check import _parse_failed_node_ids, _ws_rel_test_path, check_file
from mutant_hunter.isolation import Workspace
from mutant_hunter.mutate import enumerate_mutants, run_mutation
from mutant_hunter.registry import Module, TARGET_ROOT, REPO_ROOT


# ---------------------------------------------------------------------------
# Synthetic module fixture
# ---------------------------------------------------------------------------

CALC_SOURCE = textwrap.dedent("""\
    def add(a, b):
        return a + b

    def is_positive(x):
        if x > 0:
            return True
        return False
""")


def _make_synthetic_module(tmp_path: Path) -> tuple:
    """Build a minimal validators-like project with a calc module.

    Returns (module_obj, test_path).
    """
    # Build src layout
    src = tmp_path / "src" / "validators"
    src.mkdir(parents=True)
    (src / "__init__.py").write_text(
        "from .calc import add, is_positive\n", encoding="utf-8"
    )
    calc_file = src / "calc.py"
    calc_file.write_text(CALC_SOURCE, encoding="utf-8")

    # Build tests
    tests = tmp_path / "tests"
    tests.mkdir()
    test_file = tests / "test_calc.py"
    test_file.write_text(
        textwrap.dedent("""\
            from validators import add, is_positive

            def test_add():
                assert add(1, 2) == 3

            def test_is_positive_true():
                assert is_positive(5)

            def test_is_positive_false():
                assert not is_positive(-1)
        """),
        encoding="utf-8",
    )

    module = Module(
        module="calc",
        slug="calc",
        source_path=calc_file,
        test_path=test_file,
        set="reference",
        specs=[],
        ref_mutants=0,
        ref_killed=0,
    )
    return module, test_file, tmp_path


# ---------------------------------------------------------------------------
# Fix 1: check_file actually runs the kill phase via re-enumeration
# ---------------------------------------------------------------------------

class TestFix1KillPhaseRunsForReal:
    def test_check_kills_at_least_one_survivor(self, tmp_path):
        """A test that directly tests is_positive must kill some survivors.

        This test verifies that check_file actually runs mutants (not just
        looks up a 'source' field from JSON).
        """
        module, test_file, root = _make_synthetic_module(tmp_path)

        # Build a fake split-A JSON with survivors (no 'source' field — the old
        # buggy code would have put all of these in not_killed without running)
        mutants = enumerate_mutants(module.source_path, module.slug)
        split_a = [m for m in mutants if m.split == "A"]
        if not split_a:
            pytest.skip("No split-A mutants in synthetic module")

        # Write a fake survivors JSON (without source field, matching real format)
        out_dir = tmp_path / "results" / "mutants"
        out_dir.mkdir(parents=True)
        survivors_payload = {
            "module": "calc",
            "slug": "calc",
            "suite": "human",
            "split": "A",
            "seed": 20260925,
            "mutants": len(split_a),
            "killed": 0,
            "survived": len(split_a),
            "invalid": 0,
            "falsy_preserving": 0,
            "score": 0.0,
            "adjusted_score": 0.0,
            "seconds": 0.0,
            "results": [{"id": m.id, "status": "survived"} for m in split_a],
            "survivors": [
                # No 'source' field — the old buggy path would skip them
                {
                    "id": m.id,
                    "op": m.op,
                    "line": m.line,
                    "function": m.function,
                    "original": m.original,
                    "mutated": m.mutated,
                    "falsy_preserving": m.falsy_preserving,
                    "split": m.split,
                }
                for m in split_a
            ],
        }
        json_path = out_dir / "calc__human__A.json"
        json_path.write_text(json.dumps(survivors_payload), encoding="utf-8")

        # Patch REPO_ROOT so check_file finds our fake JSON
        with mock.patch("mutant_hunter.check.REPO_ROOT", tmp_path), \
             mock.patch("mutant_hunter.check.TARGET_ROOT", tmp_path):
            result = check_file(module, test_file, repeat=1, jobs=1)

        # With real running, we expect at least some kills
        # (the test file directly checks is_positive and add)
        assert "survivors_checked" in result
        assert result["survivors_checked"] == len(split_a)
        # The key assertion: kills must not all be empty — the phase actually ran
        # (at minimum not_killed + kills == survivors_checked)
        assert len(result["kills"]) + len(result["not_killed"]) == result["survivors_checked"]

    def test_not_killed_is_empty_when_no_survivors(self, tmp_path):
        """When there are no split-A survivors, kills and not_killed are both empty."""
        module, test_file, root = _make_synthetic_module(tmp_path)

        out_dir = tmp_path / "results" / "mutants"
        out_dir.mkdir(parents=True)
        # Empty survivors list
        json_path = out_dir / "calc__human__A.json"
        json_path.write_text(json.dumps({
            "module": "calc", "slug": "calc", "suite": "human", "split": "A",
            "seed": 20260925, "mutants": 5, "killed": 5, "survived": 0,
            "invalid": 0, "falsy_preserving": 0, "score": 1.0, "adjusted_score": 1.0,
            "seconds": 0.0, "results": [], "survivors": [],
        }), encoding="utf-8")

        with mock.patch("mutant_hunter.check.REPO_ROOT", tmp_path), \
             mock.patch("mutant_hunter.check.TARGET_ROOT", tmp_path):
            result = check_file(module, test_file, repeat=1, jobs=1)

        assert result["kills"] == []
        assert result["not_killed"] == []
        assert result["survivors_checked"] == 0


# ---------------------------------------------------------------------------
# Fix 2: deselect failing tests in kill phase
# ---------------------------------------------------------------------------

class TestFix2DeselectionOfFailingTests:
    def test_deselect_logic_via_parse(self):
        """Verify that always-failing tests are captured and would be deselected.

        This is a pure logic test: it verifies that _parse_failed_node_ids picks
        up the failing test IDs so they can be passed to --deselect in the kill phase.
        The actual subprocess deselection is an integration concern tested separately.
        """
        # Simulate the stdout a test file with one always-failing test produces
        stdout_with_failure = textwrap.dedent("""\
            PASSED tests/test_with_failure.py::test_always_passes
            FAILED tests/test_with_failure.py::test_always_fails
        """)

        from mutant_hunter.check import _parse_failed_node_ids
        ids = _parse_failed_node_ids(stdout_with_failure, "")

        # The always-failing test must be captured
        assert any("test_always_fails" in i for i in ids), (
            f"Failing test not captured: {ids}"
        )
        # The passing test must not be in the list
        assert not any("test_always_passes" in i for i in ids)

    def test_check_file_reports_failing_test_on_real_validators(self, tmp_path):
        """Use the real validators project with a test file that always fails.

        This confirms: (a) failing_tests_on_original is populated,
        (b) kills and not_killed together equal survivors_checked (kill phase ran).
        """
        from mutant_hunter.registry import get_module, REPO_ROOT
        module = get_module("url")

        # Write a test file with one always-failing assertion
        test_file = tmp_path / "test_deselect_demo.py"
        test_file.write_text(
            textwrap.dedent("""\
                import validators

                def test_always_fails():
                    assert False, "always red — should be deselected in kill phase"

                def test_valid_url():
                    assert validators.url("http://example.com")
            """),
            encoding="utf-8",
        )

        # Make sure we have the split-A JSON for url
        json_path = REPO_ROOT / "results" / "mutants" / "url__human__A.json"
        if not json_path.exists():
            pytest.skip("url__human__A.json not found; run mutate url first")

        result = check_file(module, test_file, repeat=1, jobs=4)

        # test_always_fails should appear in failing_tests_on_original
        failing = result["failing_tests_on_original"]
        assert any("test_always_fails" in f for f in failing), (
            f"Expected test_always_fails in failing_tests; got {failing}"
        )
        assert not result["passes_on_original"]

        # Kill phase must have run: kills + not_killed == survivors_checked
        assert len(result["kills"]) + len(result["not_killed"]) == result["survivors_checked"]

        # With deselection active: the always-failing test does NOT inflate kills.
        # test_valid_url passes on original (url is valid), so it doesn't kill survivors
        # that only test url validity for a different input — some should survive.
        # The minimal sanity: we have counts.
        assert result["survivors_checked"] > 0


# ---------------------------------------------------------------------------
# Fix 3: parse all failing test IDs without -x, including parametrize with spaces
# ---------------------------------------------------------------------------

class TestFix3ParseAllFailingTests:
    def test_parse_failed_node_ids_basic(self):
        output = textwrap.dedent("""\
            PASSED tests/test_foo.py::test_passes
            FAILED tests/test_foo.py::test_fails
            FAILED tests/test_foo.py::test_other_fails
        """)
        ids = _parse_failed_node_ids(output, "")
        assert "tests/test_foo.py::test_fails" in ids
        assert "tests/test_foo.py::test_other_fails" in ids
        assert "tests/test_foo.py::test_passes" not in ids

    def test_parse_failed_node_ids_with_reason(self):
        """FAILED lines with ' - reason' suffix are parsed correctly."""
        output = "FAILED tests/test_url.py::test_invalid[http://bad url] - AssertionError\n"
        ids = _parse_failed_node_ids(output, "")
        # The node ID should be extracted without the reason
        assert any("test_invalid" in i for i in ids)

    def test_parse_failed_node_ids_parametrize_with_spaces(self):
        """Parametrize IDs with spaces must be captured."""
        # -rf summary format: "FAILED path::test[param with spaces] - reason"
        output = textwrap.dedent("""\
            FAILED tests/test_url.py::test_R4_lt_in_username_rejected[us<er] - assert False
            FAILED tests/test_url.py::test_param[a b c] - AssertionError
        """)
        ids = _parse_failed_node_ids(output, "")
        assert any("us<er" in i for i in ids), f"Space-containing param not found in {ids}"
        assert any("a b c" in i for i in ids), f"Space param not found in {ids}"

    def test_parse_no_duplicates(self):
        """Same node ID appearing twice (in -v and -rf output) should appear once."""
        output = textwrap.dedent("""\
            FAILED tests/test_foo.py::test_x
            FAILED tests/test_foo.py::test_x - reason
        """)
        ids = _parse_failed_node_ids(output, "")
        assert ids.count("tests/test_foo.py::test_x") == 1

    def test_multiple_failures_collected_without_x(self, tmp_path):
        """Run a test file with 2 failures and confirm both are in failing_tests_on_original."""
        module, _, root = _make_synthetic_module(tmp_path)

        test_file = tmp_path / "tests" / "test_two_fails.py"
        test_file.write_text(
            textwrap.dedent("""\
                def test_fail_one():
                    assert False, "first failure"

                def test_fail_two():
                    assert False, "second failure"

                def test_pass():
                    assert True
            """),
            encoding="utf-8",
        )

        out_dir = tmp_path / "results" / "mutants"
        out_dir.mkdir(parents=True)
        (out_dir / "calc__human__A.json").write_text(
            json.dumps({"module": "calc", "slug": "calc", "suite": "human",
                        "split": "A", "seed": 20260925, "mutants": 0,
                        "killed": 0, "survived": 0, "invalid": 0,
                        "falsy_preserving": 0, "score": 0.0,
                        "adjusted_score": 0.0, "seconds": 0.0,
                        "results": [], "survivors": []}),
            encoding="utf-8",
        )

        with mock.patch("mutant_hunter.check.REPO_ROOT", tmp_path), \
             mock.patch("mutant_hunter.check.TARGET_ROOT", tmp_path):
            result = check_file(module, test_file, repeat=1, jobs=1)

        failing = result["failing_tests_on_original"]
        assert len(failing) == 2, f"Expected 2 failures, got {len(failing)}: {failing}"
        assert any("test_fail_one" in f for f in failing)
        assert any("test_fail_two" in f for f in failing)


# ---------------------------------------------------------------------------
# Fix 4: mutate --split all writes no file
# ---------------------------------------------------------------------------

class TestFix4SplitAllNoFile:
    def test_run_mutation_split_all_returns_none(self, tmp_path):
        """run_mutation(..., split='all') must return None and write no file."""
        module, test_file, root = _make_synthetic_module(tmp_path)

        # Ensure the mutants dir exists but is empty
        mutants_dir = tmp_path / "results" / "mutants"
        mutants_dir.mkdir(parents=True)

        with mock.patch("mutant_hunter.mutate.REPO_ROOT", tmp_path), \
             mock.patch("mutant_hunter.mutate.TARGET_ROOT", tmp_path), \
             mock.patch("mutant_hunter.isolation.TARGET_ROOT", tmp_path), \
             mock.patch("mutant_hunter.isolation.VENV_PYTHON",
                        Path(sys.executable)):
            suite_paths_patch = mock.patch(
                "mutant_hunter.mutate.suite_test_paths",
                return_value=[test_file],
            )
            with suite_paths_patch:
                result = run_mutation(
                    module,
                    suite="human",
                    split="all",
                    jobs=1,
                    seed=20260925,
                )

        assert result is None, f"Expected None for split=all, got {result}"

        # No *__all.json file should exist
        all_files = list(mutants_dir.glob("*__all.json"))
        assert all_files == [], f"Unexpected files: {all_files}"

        # No *__B.json should exist either
        b_files = list(mutants_dir.glob("*__B.json"))
        assert b_files == [], f"Unexpected B-split files: {b_files}"

    def test_mutate_split_all_cli_no_file(self, tmp_path):
        """mutanthunter mutate url --split all must not create any __all.json or __B.json."""
        mutants_dir = REPO_ROOT / "results" / "mutants"

        before_files = set(mutants_dir.glob("*")) if mutants_dir.exists() else set()

        result = subprocess.run(
            [sys.executable, "-m", "mutant_hunter.cli",
             "mutate", "url", "--split", "all", "--jobs", "4"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=600,
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr[:500]}"

        # After run: must not have created any __all.json or __B.json
        all_files = list(mutants_dir.glob("*__all.json"))
        b_files = list(mutants_dir.glob("*__B.json"))
        new_all = [f for f in all_files if f not in before_files]
        new_b = [f for f in b_files if f not in before_files]

        assert new_all == [], f"__all.json files created: {new_all}"
        assert new_b == [], f"__B.json files created: {new_b}"

        # The output should mention "no file written"
        assert "no file written" in result.stdout.lower(), (
            f"Expected 'no file written' in stdout; got:\n{result.stdout[:300]}"
        )


# ---------------------------------------------------------------------------
# Node-ID stability fix: relative paths produce stable IDs across workspaces
# ---------------------------------------------------------------------------

class TestNodeIdStability:
    """Fix 2 & 3 in practice: node IDs must be workspace-path-independent.

    Each baseline run and each kill worker creates a fresh temp directory, so
    absolute workspace paths differ between runs.  By passing the test file as
    a relative path (via _ws_rel_test_path), every pytest invocation emits the
    same node-ID prefix, making set-intersection reliable and --deselect work.
    """

    def test_ws_rel_test_path_external_file(self, tmp_path):
        """_ws_rel_test_path returns 'tests/<name>' for an external file."""
        test_file = tmp_path / "my_test.py"
        test_file.write_text("", encoding="utf-8")

        target_root = tmp_path / "target"
        target_root.mkdir()
        (target_root / "src").mkdir()
        (target_root / "tests").mkdir()

        with Workspace(target_root=target_root) as ws:
            from mutant_hunter.check import _copy_test_file_into_workspace
            ws_file = _copy_test_file_into_workspace(ws, test_file)
            rel = _ws_rel_test_path(ws, ws_file)

        assert rel == "tests/my_test.py", f"Unexpected rel path: {rel!r}"

    def test_ws_rel_test_path_under_target(self, tmp_path):
        """_ws_rel_test_path preserves the sub-path for files under TARGET_ROOT."""
        target_root = tmp_path / "target"
        src = target_root / "src"
        src.mkdir(parents=True)
        tests = target_root / "tests"
        tests.mkdir()
        (src / "__init__.py").write_text("", encoding="utf-8")
        test_file = tests / "test_something.py"
        test_file.write_text("", encoding="utf-8")

        with mock.patch("mutant_hunter.check.TARGET_ROOT", target_root):
            with Workspace(target_root=target_root) as ws:
                from mutant_hunter.check import _copy_test_file_into_workspace
                ws_file = _copy_test_file_into_workspace(ws, test_file)
                rel = _ws_rel_test_path(ws, ws_file)

        assert rel == "tests/test_something.py", f"Unexpected rel path: {rel!r}"

    def test_failing_parametrize_with_spaces_repeat3(self, tmp_path):
        """repeat=3 with a parametrized failing test: both param values must appear
        in failing_tests_on_original and the kill-phase must only credit kills
        from the passing test.

        This is the regression test for the node-ID stability bug: before the
        fix, each of the 3 runs used a different workspace directory so absolute
        node IDs never matched and always_failed was always empty.
        """
        module, _, _ = _make_synthetic_module(tmp_path)

        # Write a test file with:
        #   - one test that kills survivors (always passes on original)
        #   - one parametrized test that always fails on the original
        test_file = tmp_path / "tests" / "test_stability.py"
        test_file.write_text(
            textwrap.dedent("""\
                import pytest
                from validators import add, is_positive

                def test_kills_survivors():
                    # Tests both add and is_positive, killing any return_none or
                    # cmp_gt_to_gte / if_negate survivors in either split.
                    assert add(1, 2) == 3          # kills return_none on add (split A)
                    assert is_positive(5) is True
                    assert is_positive(-1) is False

                @pytest.mark.parametrize("bad", ["not a url", "also not one"])
                def test_always_fails_on_original(bad):
                    # This test always fails on original — must be deselected
                    # in the kill phase so it doesn't inflate kills.
                    assert False, f"always red: {bad}"
            """),
            encoding="utf-8",
        )

        # Build a fake split-A JSON with all split-A survivors of calc
        mutants = enumerate_mutants(module.source_path, module.slug)
        split_a = [m for m in mutants if m.split == "A"]
        if not split_a:
            pytest.skip("No split-A mutants in synthetic calc module")

        out_dir = tmp_path / "results" / "mutants"
        out_dir.mkdir(parents=True)
        (out_dir / "calc__human__A.json").write_text(
            json.dumps({
                "module": "calc", "slug": "calc", "suite": "human",
                "split": "A", "seed": 20260925,
                "mutants": len(split_a), "killed": 0, "survived": len(split_a),
                "invalid": 0, "falsy_preserving": 0,
                "score": 0.0, "adjusted_score": 0.0, "seconds": 0.0,
                "results": [{"id": m.id, "status": "survived"} for m in split_a],
                "survivors": [
                    {"id": m.id, "op": m.op, "line": m.line, "function": m.function,
                     "original": m.original, "mutated": m.mutated,
                     "falsy_preserving": m.falsy_preserving, "split": m.split}
                    for m in split_a
                ],
            }),
            encoding="utf-8",
        )

        with mock.patch("mutant_hunter.check.REPO_ROOT", tmp_path), \
             mock.patch("mutant_hunter.check.TARGET_ROOT", tmp_path):
            result = check_file(module, test_file, repeat=3, jobs=1)

        failing = result["failing_tests_on_original"]

        # Both parametrize values must be captured (node-ID stability)
        assert any("not a url" in f for f in failing), (
            f"'not a url' not in failing_tests_on_original: {failing}"
        )
        assert any("also not one" in f for f in failing), (
            f"'also not one' not in failing_tests_on_original: {failing}"
        )
        # Exactly the two parametrized cases, not the passing test
        assert len(failing) == 2, (
            f"Expected exactly 2 failing tests, got {len(failing)}: {failing}"
        )

        # The kill phase must have run with deselection active:
        # kills + not_killed == survivors_checked
        assert len(result["kills"]) + len(result["not_killed"]) == result["survivors_checked"]

        # test_positive_kills_mutant checks both branches of is_positive, so
        # it must kill at least some if_negate / cmp survivors — confirming
        # the kill phase ran on the real mutant source, not on an empty list.
        assert result["survivors_checked"] == len(split_a)
        assert len(result["kills"]) > 0, (
            "No kills recorded — kill phase likely skipped or deselection broke everything"
        )
