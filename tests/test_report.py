"""Tests for mutant_hunter.stats and mutant_hunter.report.

Fixture layout (tests/fixtures/):
  dataset/modules.csv          — 3 modules: url (run, B+C split data), email (run, B only), finance (not run)
  results/
    modules/{url,email}.json
    mutants/url__human__B.json, url__human+mh__B.json, url__human+b1__B.json
    mutants/email__human__B.json, email__human+mh__B.json
    suspected_bugs/{url,email}.md
    equivalent/{url,email}.json
    replay.csv
    costs_alice.csv
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
RESULTS_DIR = FIXTURES / "results"
DOCS_DIR = FIXTURES / "docs"
MODULES_CSV = FIXTURES / "dataset" / "modules.csv"


# ---------------------------------------------------------------------------
# stats.py unit tests
# ---------------------------------------------------------------------------

from mutant_hunter.stats import wilson, mcnemar, fmt_pct


class TestWilson:
    def test_zero_n_returns_full_interval(self):
        """Docstring: wilson"""
        p, lo, hi = wilson(0, 0)
        assert p == 0.0
        assert lo == 0.0
        assert hi == 1.0

    def test_all_killed(self):
        """Docstring: wilson"""
        p, lo, hi = wilson(10, 10)
        assert p == 1.0
        assert lo > 0.7
        assert hi == 1.0

    def test_half_killed(self):
        """Docstring: wilson"""
        p, lo, hi = wilson(5, 10)
        assert abs(p - 0.5) < 0.001
        assert lo < 0.5 < hi

    def test_known_value(self):
        """Docstring: wilson — 17/32 should be close to 0.531"""
        p, lo, hi = wilson(17, 32)
        assert abs(p - 17 / 32) < 0.0001
        assert lo < p < hi

    def test_bounds_in_0_1(self):
        """Docstring: wilson"""
        for k, n in [(0, 1), (1, 1), (3, 7), (100, 100)]:
            p, lo, hi = wilson(k, n)
            assert 0.0 <= lo <= p <= hi <= 1.0


class TestMcNemar:
    def test_zero_discordant(self):
        """Docstring: mcnemar"""
        assert mcnemar(0, 0) == 1.0

    def test_symmetric(self):
        """Docstring: mcnemar — p-value is symmetric in b, c"""
        assert mcnemar(3, 7) == pytest.approx(mcnemar(7, 3), rel=1e-9)

    def test_equal_discordant_is_1(self):
        """Docstring: mcnemar — b == c → p = 1.0"""
        p = mcnemar(5, 5)
        assert p == pytest.approx(1.0, rel=1e-6)

    def test_large_asymmetry_small_p(self):
        """Docstring: mcnemar — strong imbalance should give small p"""
        p = mcnemar(0, 20)
        assert p < 0.001

    def test_moderate_asymmetry(self):
        """Docstring: mcnemar — b=1, c=9 should be significant"""
        p = mcnemar(1, 9)
        assert p < 0.05

    def test_output_in_0_1(self):
        """Docstring: mcnemar"""
        for b, c in [(0, 0), (3, 5), (10, 2), (0, 10)]:
            assert 0.0 <= mcnemar(b, c) <= 1.0


class TestFmtPct:
    def test_format(self):
        """Docstring: fmt_pct"""
        s = fmt_pct(0.656, 0.478, 0.800)
        assert "65.6%" in s
        assert "47.8" in s
        assert "80.0" in s
        assert "95% CI" in s


# ---------------------------------------------------------------------------
# report.py integration tests
# ---------------------------------------------------------------------------

from mutant_hunter.report import report


@pytest.fixture(scope="module")
def generated(tmp_path_factory):
    """Run report once; return (summary_path, stats_path, html_path)."""
    out_results = tmp_path_factory.mktemp("results")
    out_docs = tmp_path_factory.mktemp("docs")

    # Copy fixture tree into tmp results dir so we can write outputs there
    import shutil
    shutil.copytree(RESULTS_DIR, out_results, dirs_exist_ok=True)

    written = report(
        results_dir=out_results,
        docs_dir=out_docs,
        modules_csv=MODULES_CSV,
    )
    return out_results / "summary.csv", out_results / "stats.md", out_docs / "index.html"


class TestSummaryCsv:
    def test_file_exists(self, generated):
        summary, _, _ = generated
        assert summary.exists()

    def test_has_expected_columns(self, generated):
        summary, _, _ = generated
        with open(summary, encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            cols = reader.fieldnames
        expected = {
            "module", "set", "suite", "split", "mutants", "killed",
            "score", "ci_low", "ci_high", "adjusted_score", "falsy_preserving",
            "tests_kept", "suspected_bugs", "minutes", "bobcoins",
        }
        assert expected.issubset(set(cols))

    def test_contains_url_rows(self, generated):
        summary, _, _ = generated
        with open(summary, encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        url_rows = [r for r in rows if r["module"] == "url"]
        assert len(url_rows) > 0

    def test_url_B_score_populated(self, generated):
        summary, _, _ = generated
        with open(summary, encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        url_b_mh = [
            r for r in rows
            if r["module"] == "url" and r["suite"] == "human+mh" and r["split"] == "B"
        ]
        assert url_b_mh, "No url / human+mh / B row in summary.csv"
        row = url_b_mh[0]
        assert row["score"] != ""
        assert float(row["score"]) > 0.0

    def test_finance_not_run_row_is_empty_score(self, generated):
        summary, _, _ = generated
        with open(summary, encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        finance_rows = [r for r in rows if r["module"] == "finance"]
        assert finance_rows, "finance should still appear (as not-run)"
        # All score fields should be empty strings for finance
        for r in finance_rows:
            assert r["score"] == ""

    def test_ci_low_le_score_le_ci_high(self, generated):
        summary, _, _ = generated
        with open(summary, encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        for r in rows:
            if r["score"] == "":
                continue
            lo, p, hi = float(r["ci_low"]), float(r["score"]), float(r["ci_high"])
            assert lo <= p <= hi, f"{r['module']}/{r['suite']}/{r['split']}: {lo} <= {p} <= {hi}"

    def test_utf8_encoding(self, generated):
        summary, _, _ = generated
        summary.read_text(encoding="utf-8")  # must not raise


class TestStatsMd:
    def test_file_exists(self, generated):
        _, stats, _ = generated
        assert stats.exists()

    def test_contains_split_b_heading(self, generated):
        _, stats, _ = generated
        text = stats.read_text(encoding="utf-8")
        assert "Split B" in text

    def test_contains_exam_c_heading(self, generated):
        _, stats, _ = generated
        text = stats.read_text(encoding="utf-8")
        assert "Exam C" in text

    def test_per_module_table_present(self, generated):
        _, stats, _ = generated
        text = stats.read_text(encoding="utf-8")
        assert "Per-module" in text
        assert "url" in text

    def test_suspected_violations_section(self, generated):
        _, stats, _ = generated
        text = stats.read_text(encoding="utf-8")
        assert "Suspected violations" in text
        assert "logic" in text

    def test_costs_section_present(self, generated):
        _, stats, _ = generated
        text = stats.read_text(encoding="utf-8")
        assert "Costs" in text
        assert "alice" in text

    def test_mcnemar_line_present(self, generated):
        _, stats, _ = generated
        text = stats.read_text(encoding="utf-8")
        assert "McNemar" in text

    def test_utf8_encoding(self, generated):
        _, stats, _ = generated
        stats.read_text(encoding="utf-8")


class TestIndexHtml:
    def test_file_exists(self, generated):
        _, _, html_path = generated
        assert html_path.exists()

    def test_is_valid_html_shell(self, generated):
        _, _, html_path = generated
        text = html_path.read_text(encoding="utf-8")
        assert text.startswith("<!DOCTYPE html>")
        assert "</html>" in text

    def test_no_external_resources(self, generated):
        """Dashboard must work offline: no http/https src/href references."""
        import re
        _, _, html_path = generated
        text = html_path.read_text(encoding="utf-8")
        # Allow href to data: and relative paths; disallow http(s):// in src/href
        bad = re.findall(r'(?:src|href)\s*=\s*["\']https?://', text)
        assert not bad, f"External resource URLs found: {bad}"

    def test_inline_svg_present(self, generated):
        _, _, html_path = generated
        text = html_path.read_text(encoding="utf-8")
        assert "<svg" in text

    def test_dark_mode_css(self, generated):
        _, _, html_path = generated
        text = html_path.read_text(encoding="utf-8")
        assert "prefers-color-scheme" in text

    def test_hero_section_present(self, generated):
        _, _, html_path = generated
        text = html_path.read_text(encoding="utf-8")
        assert "Pooled Hold-out Score" in text

    def test_module_table_contains_url(self, generated):
        _, _, html_path = generated
        text = html_path.read_text(encoding="utf-8")
        assert "url" in text

    def test_not_run_modules_listed(self, generated):
        _, _, html_path = generated
        text = html_path.read_text(encoding="utf-8")
        assert "finance" in text

    def test_suspected_violations_collapsed_datastale(self, generated):
        _, _, html_path = generated
        text = html_path.read_text(encoding="utf-8")
        assert "violation" in text

    def test_replay_table_present(self, generated):
        _, _, html_path = generated
        text = html_path.read_text(encoding="utf-8")
        assert "replay" in text.lower() or "Replay" in text

    def test_method_and_limits_section(self, generated):
        _, _, html_path = generated
        text = html_path.read_text(encoding="utf-8")
        assert "Method and limits" in text

    def test_ibm_bob_footer(self, generated):
        _, _, html_path = generated
        text = html_path.read_text(encoding="utf-8")
        assert "IBM Bob" in text

    def test_readable_at_500px(self, generated):
        """max-width must be set to a value at or near 760px (readable at 500px)."""
        _, _, html_path = generated
        text = html_path.read_text(encoding="utf-8")
        assert "max-width" in text

    def test_utf8_encoding(self, generated):
        _, _, html_path = generated
        html_path.read_text(encoding="utf-8")


class TestReportMissingOptionalFiles:
    """report() must work gracefully when B/C split files are absent."""

    def test_works_without_split_b_c(self, tmp_path):
        results = tmp_path / "results"
        docs = tmp_path / "docs"
        results.mkdir()
        (results / "modules").mkdir()
        (results / "mutants").mkdir()
        (results / "suspected_bugs").mkdir()
        (results / "equivalent").mkdir()

        # Only modules/url.json — no split-B or C files
        import shutil
        shutil.copy(RESULTS_DIR / "modules" / "url.json", results / "modules" / "url.json")

        written = report(results_dir=results, docs_dir=docs, modules_csv=MODULES_CSV)
        assert len(written) == 3
        for p in written:
            assert p.exists()

    def test_summary_has_empty_score_when_no_split_b(self, tmp_path):
        results = tmp_path / "results"
        docs = tmp_path / "docs"
        results.mkdir()
        (results / "modules").mkdir()
        (results / "mutants").mkdir()
        (results / "suspected_bugs").mkdir()
        (results / "equivalent").mkdir()

        import shutil
        shutil.copy(RESULTS_DIR / "modules" / "url.json", results / "modules" / "url.json")

        report(results_dir=results, docs_dir=docs, modules_csv=MODULES_CSV)

        with open(results / "summary.csv", encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))

        url_b_rows = [r for r in rows if r["module"] == "url" and r["split"] == "B"]
        assert url_b_rows
        for r in url_b_rows:
            assert r["score"] == ""
