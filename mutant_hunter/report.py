"""report.py — generate summary.csv, stats.md, and docs/index.html (spec 8, 9).

report(results_dir, docs_dir, modules_csv) -> list[Path]

Reads (all optional unless noted):
  results_dir/mutants/<slug>__<suite>__<split>.json  splits B and C
  results_dir/modules/<slug>.json                    (required to count a module as "run")
  results_dir/suspected_bugs/<slug>*.md
  results_dir/equivalent/<slug>.json
  results_dir/replay.csv
  every results_dir/costs*.csv
  modules_csv

Writes:
  results_dir/summary.csv
  results_dir/stats.md
  docs_dir/index.html
"""

from __future__ import annotations

import csv
import glob as _glob
import json
import re
from pathlib import Path
from typing import Any

from .stats import wilson, mcnemar, fmt_pct

# Suites shown in the dashboard, in order
_SUITES = ["human", "human+b1", "human+mh"]
_SUITE_LABELS = {"human": "B0", "human+b1": "B1", "human+mh": "MH"}

# summary.csv columns (spec 9.2)
_SUMMARY_COLS = [
    "module", "set", "suite", "split",
    "mutants", "killed", "score", "ci_low", "ci_high",
    "adjusted_score", "falsy_preserving",
    "tests_kept", "suspected_bugs", "minutes", "bobcoins",
]


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------

def _load_modules_csv(modules_csv: Path) -> dict[str, dict]:
    """Return {module_name: row_dict} from dataset/modules.csv."""
    registry: dict[str, dict] = {}
    with open(modules_csv, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            registry[row["module"]] = row
    return registry


def _slug(module: str) -> str:
    return module.replace("/", "__")


def _load_mutant_file(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _count_suspected_bugs(results_dir: Path, slug: str) -> int:
    """Count ## headings in any suspected_bugs/<slug>*.md file."""
    total = 0
    for p in sorted((results_dir / "suspected_bugs").glob(f"{slug}*.md")):
        text = p.read_text(encoding="utf-8")
        total += len(re.findall(r"^##\s", text, re.MULTILINE))
    return total


def _load_module_result(results_dir: Path, slug: str) -> dict | None:
    p = results_dir / "modules" / f"{slug}.json"
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _load_equivalent(results_dir: Path, slug: str) -> list:
    p = results_dir / "equivalent" / f"{slug}.json"
    if not p.exists():
        return []
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _load_replay(results_dir: Path) -> list[dict]:
    p = results_dir / "replay.csv"
    if not p.exists():
        return []
    with open(p, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _load_costs(results_dir: Path) -> list[dict]:
    rows: list[dict] = []
    for path in sorted(results_dir.glob("costs*.csv")):
        with open(path, encoding="utf-8", newline="") as fh:
            rows.extend(csv.DictReader(fh))
    return rows


def _find_mutant_files(results_dir: Path) -> dict[tuple[str, str, str], Path]:
    """Return {(slug, suite, split): path} for B and C split files only."""
    result: dict[tuple[str, str, str], Path] = {}
    pattern = str(results_dir / "mutants" / "*__*__[BC].json")
    for p in _glob.glob(pattern):
        path = Path(p)
        stem = path.stem  # e.g. "url__human+mh__B"
        parts = stem.rsplit("__", 1)
        if len(parts) != 2:
            continue
        suite_slug, split = parts  # split is "B" or "C"
        # suite_slug is like "url__human+mh" -> slug = last __ part
        # Find where suite starts: suite is one of human, human+mh, human+b1
        for suite in ("human+mh", "human+b1", "human"):
            if suite_slug.endswith(f"__{suite}") or suite_slug == suite:
                slug = suite_slug[: -(len(suite) + 2)] if f"__{suite}" in suite_slug else ""
                result[(slug, suite, split)] = path
                break
    return result


# ---------------------------------------------------------------------------
# Build summary rows
# ---------------------------------------------------------------------------

def _build_summary_rows(
    registry: dict[str, dict],
    results_dir: Path,
    mutant_files: dict[tuple[str, str, str], Path],
) -> list[dict]:
    rows: list[dict] = []
    for module, reg_row in sorted(registry.items()):
        slug = _slug(module)
        mod_result = _load_module_result(results_dir, slug)
        mod_set = reg_row.get("set", "")

        if mod_result is None:
            # Module not yet run — emit placeholder rows for reference
            for suite in _SUITES:
                for split in ("B", "C"):
                    rows.append({
                        "module": module, "set": mod_set, "suite": suite,
                        "split": split,
                        "mutants": "", "killed": "", "score": "",
                        "ci_low": "", "ci_high": "",
                        "adjusted_score": "", "falsy_preserving": "",
                        "tests_kept": "", "suspected_bugs": "", "minutes": "",
                        "bobcoins": "",
                    })
            continue

        tests_kept = mod_result.get("tests_kept", "")
        minutes = mod_result.get("minutes", "")
        bobcoins = mod_result.get("bobcoins", "")
        bug_counts = mod_result.get("suspected_bugs", {})
        total_bugs = sum(bug_counts.values()) if isinstance(bug_counts, dict) else 0

        for suite in _SUITES:
            for split in ("B", "C"):
                key = (slug, suite, split)
                if key in mutant_files:
                    data = _load_mutant_file(mutant_files[key])
                    n = data.get("mutants", 0)
                    k = data.get("killed", 0)
                    fp = data.get("falsy_preserving", 0)
                    raw_score = data.get("score", k / n if n else 0.0)
                    adj_score = data.get("adjusted_score", raw_score)
                    _p, lo, hi = wilson(k, n)
                    rows.append({
                        "module": module, "set": mod_set, "suite": suite,
                        "split": split,
                        "mutants": n, "killed": k,
                        "score": round(raw_score, 4),
                        "ci_low": round(lo, 4), "ci_high": round(hi, 4),
                        "adjusted_score": round(adj_score, 4),
                        "falsy_preserving": fp,
                        "tests_kept": tests_kept,
                        "suspected_bugs": total_bugs,
                        "minutes": minutes,
                        "bobcoins": bobcoins if bobcoins is not None else "",
                    })
                else:
                    rows.append({
                        "module": module, "set": mod_set, "suite": suite,
                        "split": split,
                        "mutants": "", "killed": "", "score": "",
                        "ci_low": "", "ci_high": "",
                        "adjusted_score": "", "falsy_preserving": "",
                        "tests_kept": tests_kept,
                        "suspected_bugs": total_bugs,
                        "minutes": minutes,
                        "bobcoins": bobcoins if bobcoins is not None else "",
                    })
    return rows


# ---------------------------------------------------------------------------
# Build stats data for stats.md
# ---------------------------------------------------------------------------

def _pooled_stats(
    registry: dict,
    results_dir: Path,
    mutant_files: dict,
    mod_set: str,
    split: str,
) -> dict[str, Any]:
    """Compute pooled killed/total for each suite on the given set+split."""
    mods = [m for m, r in registry.items() if r.get("set") == mod_set]
    totals: dict[str, dict[str, int]] = {s: {"k": 0, "n": 0} for s in _SUITES}
    for module in mods:
        slug = _slug(module)
        for suite in _SUITES:
            key = (slug, suite, split)
            if key in mutant_files:
                data = _load_mutant_file(mutant_files[key])
                totals[suite]["k"] += data.get("killed", 0)
                totals[suite]["n"] += data.get("mutants", 0)
    result: dict[str, Any] = {}
    for suite in _SUITES:
        k, n = totals[suite]["k"], totals[suite]["n"]
        p, lo, hi = wilson(k, n)
        result[suite] = {"k": k, "n": n, "p": p, "lo": lo, "hi": hi}
    return result


def _mcnemar_b1_vs_mh(
    registry: dict,
    results_dir: Path,
    mutant_files: dict,
    mod_set: str,
    split: str,
) -> tuple[int, int, float]:
    """Return (b, c, p_value) for McNemar B1 vs MH on pooled mutants."""
    mods = [m for m, r in registry.items() if r.get("set") == mod_set]
    b_only = 0  # killed by human+b1 only
    c_only = 0  # killed by human+mh only
    for module in mods:
        slug = _slug(module)
        key_b1 = (slug, "human+b1", split)
        key_mh = (slug, "human+mh", split)
        if key_b1 not in mutant_files or key_mh not in mutant_files:
            continue
        d_b1 = _load_mutant_file(mutant_files[key_b1])
        d_mh = _load_mutant_file(mutant_files[key_mh])
        ids_b1 = {r["id"] for r in d_b1.get("results", []) if r["status"] == "killed"}
        ids_mh = {r["id"] for r in d_mh.get("results", []) if r["status"] == "killed"}
        b_only += len(ids_b1 - ids_mh)
        c_only += len(ids_mh - ids_b1)
    p = mcnemar(b_only, c_only)
    return b_only, c_only, p


# ---------------------------------------------------------------------------
# Write summary.csv
# ---------------------------------------------------------------------------

def _write_summary_csv(path: Path, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=_SUMMARY_COLS)
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# Write stats.md
# ---------------------------------------------------------------------------

def _write_stats_md(
    path: Path,
    registry: dict,
    results_dir: Path,
    mutant_files: dict,
    costs_rows: list[dict],
) -> None:
    lines: list[str] = ["# MutantHunter — Statistics\n"]

    for split_label, split in [("Split B (hold-out)", "B"), ("Exam C (out-of-distribution)", "C")]:
        lines.append(f"## {split_label}\n")
        for mod_set in ("main", "extra"):
            pool = _pooled_stats(registry, results_dir, mutant_files, mod_set, split)
            lines.append(f"### {mod_set.capitalize()} modules\n")
            lines.append("| Suite | k | n | Score | 95% CI |")
            lines.append("|---|---|---|---|---|")
            for suite in _SUITES:
                d = pool[suite]
                if d["n"] == 0:
                    lines.append(f"| {_SUITE_LABELS[suite]} | — | — | — | — |")
                else:
                    lines.append(
                        f"| {_SUITE_LABELS[suite]} | {d['k']} | {d['n']} "
                        f"| {d['p']*100:.1f}% | {d['lo']*100:.1f}–{d['hi']*100:.1f}% |"
                    )
            lines.append("")

            # McNemar B1 vs MH
            b, c, p_val = _mcnemar_b1_vs_mh(
                registry, results_dir, mutant_files, mod_set, split
            )
            # Print b, c, p even when b=c=0 (paired data exist but no discordant pairs)
            mods_with_both = sum(
                1 for m in [mm for mm, rr in registry.items() if rr.get("set") == mod_set]
                if (_slug(m), "human+b1", split) in mutant_files
                and (_slug(m), "human+mh", split) in mutant_files
            )
            if mods_with_both > 0:
                lines.append(
                    f"McNemar B1 vs MH (split {split}, {mod_set}): "
                    f"b={b}, c={c}, p={p_val:.4f}\n"
                )
            else:
                lines.append(
                    f"McNemar B1 vs MH (split {split}, {mod_set}): no paired data yet\n"
                )

    # Per-module table: split A before/after (always available)
    lines.append("## Per-module split-A scores\n")
    lines.append("| Module | Set | B0 before | MH after | Δ | Tests kept | Bugs | Minutes | Bobcoins |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for module, reg_row in sorted(registry.items()):
        slug = _slug(module)
        mod_result = _load_module_result(results_dir, slug)
        if mod_result is None:
            lines.append(f"| {module} | {reg_row.get('set','')} | — | — | — | — | — | — | — |")
            continue
        sa = mod_result.get("split_A", {})
        before = sa.get("before", "—")
        after = sa.get("after", "—")
        delta = (
            f"+{(after - before)*100:.1f}%"
            if isinstance(before, (int, float)) and isinstance(after, (int, float))
            else "—"
        )
        bugs = mod_result.get("suspected_bugs", {})
        total_bugs = sum(bugs.values()) if isinstance(bugs, dict) else 0
        bc_val = mod_result.get("bobcoins")
        lines.append(
            f"| {module} | {reg_row.get('set','')} "
            f"| {before if isinstance(before, float) else '—':.1%} "
            f"| {after if isinstance(after, float) else '—':.1%} "
            f"| {delta} "
            f"| {mod_result.get('tests_kept','—')} "
            f"| {total_bugs} "
            f"| {mod_result.get('minutes','—')} "
            f"| {bc_val if bc_val is not None else '—'} |"
        )
    lines.append("")

    # Suspected violations summary
    lines.append("## Suspected violations\n")
    cat_totals: dict[str, int] = {
        "logic": 0, "data-staleness": 0,
        "spec-ambiguous": 0, "human-test-conflict": 0,
    }
    for module, reg_row in sorted(registry.items()):
        slug = _slug(module)
        mod_result = _load_module_result(results_dir, slug)
        if mod_result is None:
            continue
        for cat, v in mod_result.get("suspected_bugs", {}).items():
            cat_totals[cat] = cat_totals.get(cat, 0) + v
    lines.append("| Category | Count |")
    lines.append("|---|---|")
    for cat, count in cat_totals.items():
        lines.append(f"| {cat} | {count} |")
    lines.append("")

    # Costs summary
    if costs_rows:
        lines.append("## Costs\n")
        lines.append("| Module | Suite | Minutes | Bobcoins | Member |")
        lines.append("|---|---|---|---|---|")
        for r in costs_rows:
            lines.append(
                f"| {r.get('module','')} | {r.get('suite','')} "
                f"| {r.get('minutes','')} | {r.get('bobcoins','')} "
                f"| {r.get('source','')} |"
            )
        lines.append("")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Build per-module data for the dashboard
# ---------------------------------------------------------------------------

def _module_dashboard_data(
    registry: dict,
    results_dir: Path,
    mutant_files: dict,
) -> list[dict]:
    """One dict per module with all data needed for the dashboard."""
    result = []
    for module, reg_row in sorted(registry.items()):
        slug = _slug(module)
        mod_result = _load_module_result(results_dir, slug)
        d: dict[str, Any] = {
            "module": module,
            "slug": slug,
            "set": reg_row.get("set", ""),
            "run": mod_result is not None,
        }
        if mod_result:
            sa = mod_result.get("split_A", {})
            d["b0_before"] = sa.get("before", None)
            d["mh_after"] = sa.get("after", None)
            d["b0_adj_before"] = sa.get("before_adjusted", None)
            d["mh_adj_after"] = sa.get("after_adjusted", None)
            d["tests_kept"] = mod_result.get("tests_kept", 0)
            d["minutes"] = mod_result.get("minutes", 0)
            d["bobcoins"] = mod_result.get("bobcoins")
            d["bugs"] = mod_result.get("suspected_bugs", {})

        # Split-B scores (if present)
        for suite in _SUITES:
            key = (slug, suite, "B")
            if key in mutant_files:
                data = _load_mutant_file(mutant_files[key])
                d[f"b_{suite}_k"] = data.get("killed", 0)
                d[f"b_{suite}_n"] = data.get("mutants", 0)
                d[f"b_{suite}_score"] = data.get("score", 0.0)
            else:
                d[f"b_{suite}_k"] = None
                d[f"b_{suite}_n"] = None
                d[f"b_{suite}_score"] = None
        result.append(d)
    return result


# ---------------------------------------------------------------------------
# HTML dashboard (spec section 8)
# ---------------------------------------------------------------------------

def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def _pct(v: float | None) -> str:
    if v is None:
        return "—"
    return f"{v * 100:.1f}%"


def _score_bar_svg(b0: float | None, b1: float | None, mh: float | None, width: int = 200, height: int = 20) -> str:
    """Inline SVG grouped-bar for one module."""
    vals = [b0, b1, mh]
    colours = ["#6b7280", "#3b82d4", "#7c5cd8"]
    bw = width // 3 - 4
    bars = []
    for i, (v, col) in enumerate(zip(vals, colours)):
        x = i * (width // 3) + 2
        if v is not None:
            bh = max(2, int(v * height))
            y = height - bh
            bars.append(
                f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" fill="{col}" />'
            )
        else:
            bars.append(
                f'<rect x="{x}" y="{height-2}" width="{bw}" height="2" fill="#e5e7eb" />'
            )
    return (
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
        + "".join(bars) + "</svg>"
    )


def _write_index_html(
    path: Path,
    registry: dict,
    results_dir: Path,
    mutant_files: dict,
    replay_rows: list[dict],
    costs_rows: list[dict],
) -> None:
    mods = _module_dashboard_data(registry, results_dir, mutant_files)
    run_mods = [m for m in mods if m["run"]]
    not_run = [m for m in mods if not m["run"]]

    # Pooled main split-B
    pool_b = _pooled_stats(registry, results_dir, mutant_files, "main", "B")
    # Pooled main exam-C
    pool_c = _pooled_stats(registry, results_dir, mutant_files, "main", "C")

    # Hero numbers
    def hero_row(pool: dict[str, Any], label: str) -> str:
        parts = []
        for suite in _SUITES:
            d = pool[suite]
            if d["n"] == 0:
                parts.append(f"<span class='metric'><span class='lbl'>{_SUITE_LABELS[suite]}</span><span class='val'>—</span></span>")
            else:
                ci = f"{d['lo']*100:.1f}–{d['hi']*100:.1f}%"
                parts.append(
                    f"<span class='metric'>"
                    f"<span class='lbl'>{_SUITE_LABELS[suite]}</span>"
                    f"<span class='val'>{d['p']*100:.1f}%</span>"
                    f"<span class='ci'>{ci}</span>"
                    f"</span>"
                )
        return f"<div class='hero-row'><span class='hero-label'>{label}</span>{''.join(parts)}</div>"

    # Suspected violation totals
    cat_totals: dict[str, int] = {"logic": 0, "data-staleness": 0, "spec-ambiguous": 0, "human-test-conflict": 0}
    for m in run_mods:
        bugs = m.get("bugs", {})
        for cat in cat_totals:
            cat_totals[cat] += bugs.get(cat, 0)

    # Extra kills (MH over B1) on split B and exam C
    mh_extra_b = 0
    b1_extra_b = 0
    mh_extra_c = 0
    b1_extra_c = 0
    for module, reg_row in registry.items():
        if reg_row.get("set") != "main":
            continue
        slug = _slug(module)
        for split, mh_ref, b1_ref in [
            ("B", "mh_extra_b", "b1_extra_b"),
            ("C", "mh_extra_c", "b1_extra_c"),
        ]:
            key_b1 = (slug, "human+b1", split)
            key_mh = (slug, "human+mh", split)
            if key_b1 in mutant_files and key_mh in mutant_files:
                d_b1 = _load_mutant_file(mutant_files[key_b1])
                d_mh = _load_mutant_file(mutant_files[key_mh])
                ids_b1 = {r["id"] for r in d_b1.get("results", []) if r["status"] == "killed"}
                ids_mh = {r["id"] for r in d_mh.get("results", []) if r["status"] == "killed"}
                if split == "B":
                    mh_extra_b += len(ids_mh - ids_b1)
                    b1_extra_b += len(ids_b1 - ids_mh)
                else:
                    mh_extra_c += len(ids_mh - ids_b1)
                    b1_extra_c += len(ids_b1 - ids_mh)

    # Per-module table rows (split B + exam C columns)
    def _score_for(m: dict, suite_key: str, split: str) -> float | None:
        """Get score for a given suite/split combo from mutant_files."""
        slug = m["slug"]
        key = (slug, suite_key, split)
        if key in mutant_files:
            data = _load_mutant_file(mutant_files[key])
            return data.get("score")
        return None

    def mod_row(m: dict) -> str:
        # Split B
        b0_b = _score_for(m, "human", "B")
        b1_b = _score_for(m, "human+b1", "B")
        mh_b = _score_for(m, "human+mh", "B")
        # Exam C
        b0_c = _score_for(m, "human", "C")
        b1_c = _score_for(m, "human+b1", "C")
        mh_c = _score_for(m, "human+mh", "C")
        # Fall back to split-A when split-B missing
        b0_disp = b0_b if b0_b is not None else m.get("b0_before")
        mh_disp = mh_b if mh_b is not None else m.get("mh_after")
        b1_disp = b1_b
        bugs = m.get("bugs", {})
        total_bugs = sum(bugs.values()) if isinstance(bugs, dict) else 0
        tooltip = f"Split-B: B0={_pct(b0_disp)} B1={_pct(b1_disp)} MH={_pct(mh_disp)} | Exam-C: B0={_pct(b0_c)} B1={_pct(b1_c)} MH={_pct(mh_c)}"
        bar = _score_bar_svg(b0_disp, b1_disp, mh_disp, width=120)
        return (
            f"<tr title='{_esc(tooltip)}'>"
            f"<td>{_esc(m['module'])}</td>"
            f"<td>{_esc(m['set'])}</td>"
            f"<td class='col-bars'>{bar}</td>"
            f"<td>{_pct(b0_disp)}</td>"
            f"<td>{_pct(b1_disp)}</td>"
            f"<td><strong>{_pct(mh_disp)}</strong></td>"
            f"<td>{_pct(b0_c)}</td>"
            f"<td>{_pct(b1_c)}</td>"
            f"<td><strong>{_pct(mh_c)}</strong></td>"
            f"<td>{m.get('tests_kept','—')}</td>"
            f"<td>{total_bugs}</td>"
            f"<td>{m.get('minutes','—')}</td>"
            f"</tr>"
        )

    # Suspected violations detail
    def violation_section() -> str:
        sections = []
        for module, reg_row in sorted(registry.items()):
            slug = _slug(module)
            mod_result = _load_module_result(results_dir, slug)
            if mod_result is None:
                continue
            bugs = mod_result.get("suspected_bugs", {})
            if not any(bugs.values()):
                continue
            # Read md files
            for p in sorted((results_dir / "suspected_bugs").glob(f"{slug}*.md")):
                text = p.read_text(encoding="utf-8")
                # Extract ## entries
                entries = re.split(r"\n(?=## )", text)
                for entry in entries:
                    entry = entry.strip()
                    if not entry or not entry.startswith("## "):
                        continue
                    # Determine category
                    cat_match = re.search(r"- Category:\s*(.+)", entry)
                    cat = cat_match.group(1).strip() if cat_match else "unknown"
                    is_datastale = cat == "data-staleness"
                    title_line = entry.split("\n", 1)[0][3:]  # drop "## "
                    body_html = "<pre class='vbody'>" + _esc(entry) + "</pre>"
                    cls = "violation-datastale" if is_datastale else "violation"
                    sections.append(f"<details class='{cls}'><summary>{_esc(module)}: {_esc(title_line)} <span class='cat'>[{_esc(cat)}]</span></summary>{body_html}</details>")
        return "\n".join(sections) if sections else "<p>No suspected violations recorded yet.</p>"

    # Replay table — pivot: one row per (sha, module), columns: human / MH / B1
    # Order: extra first, then main, then reference
    def replay_table() -> str:
        if not replay_rows:
            return "<p>No replay data yet (<code>results/replay.csv</code> missing).</p>"

        # Build a lookup: (sha, module) -> {suite: result, ...} + metadata
        from collections import OrderedDict
        pivot: dict[tuple[str, str], dict] = OrderedDict()
        set_order = {"extra": 0, "main": 1, "reference": 2}
        for row in replay_rows:
            sha = row.get("sha") or row.get("commit", "")
            key = (sha, row.get("module", ""))
            if key not in pivot:
                pivot[key] = {
                    "sha": sha,
                    "date": row.get("date", ""),
                    "module": row.get("module", ""),
                    "set": row.get("set", ""),
                    "subject": row.get("subject", ""),
                    "note": row.get("note", ""),
                    "human": "",
                    "mh": "",
                    "b1": "",
                }
            suite = row.get("suite", "")
            result = row.get("result", "")
            if suite in ("human", "mh", "b1"):
                pivot[key][suite] = result

        # Sort by set order, then date descending, then module
        sorted_rows = sorted(
            pivot.values(),
            key=lambda r: (set_order.get(r["set"], 9), r["date"], r["module"])
        )

        def _result_cell(val: str) -> str:
            if val == "caught":
                return "<td class='caught'>caught</td>"
            elif val == "miss":
                return "<td class='miss'>miss</td>"
            else:
                return "<td class='blank'>—</td>"

        hdr = (
            "<tr>"
            "<th>SHA</th><th class='col-date'>Date</th><th>Module</th><th>Set</th>"
            "<th class='col-subject'>Subject</th>"
            "<th>Human</th><th>MH</th><th>B1</th>"
            "<th>Note</th>"
            "</tr>"
        )
        body = ""
        for r in sorted_rows:
            sha_short = r["sha"][:7]
            note_html = _esc(r["note"]) if r["note"] else ""
            body += (
                f"<tr>"
                f"<td><code>{_esc(sha_short)}</code></td>"
                f"<td class='col-date'>{_esc(r['date'])}</td>"
                f"<td>{_esc(r['module'])}</td>"
                f"<td>{_esc(r['set'])}</td>"
                f"<td class='subject col-subject'>{_esc(r['subject'])}</td>"
                + _result_cell(r["human"])
                + _result_cell(r["mh"])
                + _result_cell(r["b1"])
                + f"<td class='note'>{note_html}</td>"
                f"</tr>"
            )
        return f"<table class='data-table replay-table'>{hdr}{body}</table>"

    not_run_html = ""
    if not_run:
        items = ", ".join(_esc(m["module"]) for m in not_run)
        not_run_html = f"<p class='muted'>Not yet run: {items}</p>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MutantHunter Dashboard</title>
<style>
:root {{
  --bg:#ffffff; --surface:#f7f8fa; --border:#e5e7eb;
  --text:#1f2328; --muted:#57606a; --accent:#3b82d4; --purple:#7c5cd8;
  --font:-apple-system,"Segoe UI",system-ui,sans-serif;
  --caught:#166534; --caught-bg:#dcfce7; --miss:#7f1d1d; --miss-bg:#fee2e2;
}}
@media(prefers-color-scheme:dark){{
  :root{{
    --bg:#0d1117;--surface:#161b22;--border:#30363d;
    --text:#c9d1d9;--muted:#8b949e;
    --caught:#86efac;--caught-bg:#14532d;
    --miss:#fca5a5;--miss-bg:#450a0a;
  }}
}}
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:var(--font);font-size:14px;line-height:1.6;background:var(--bg);color:var(--text);padding:16px;}}
.wrap{{max-width:960px;margin:0 auto;}}
h1{{font-size:1.4em;margin:0 0 4px;}}
h2{{font-size:1.1em;margin:24px 0 8px;border-bottom:1px solid var(--border);padding-bottom:4px;}}
h3{{font-size:0.95em;margin:16px 0 6px;color:var(--muted);}}
.muted{{color:var(--muted);font-size:0.85em;}}
.hero{{background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:16px;margin:16px 0;}}
.hero-row{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:4px 0;}}
.hero-label{{min-width:100px;color:var(--muted);font-size:0.85em;}}
.metric{{display:flex;flex-direction:column;align-items:center;min-width:80px;background:var(--bg);border:1px solid var(--border);border-radius:4px;padding:6px 8px;}}
.lbl{{font-size:0.75em;color:var(--muted);}}
.val{{font-size:1.1em;font-weight:600;color:var(--accent);}}
.ci{{font-size:0.68em;color:var(--muted);}}
.tiles{{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0;}}
.tile-group{{flex:1 1 200px;border:1px solid var(--border);border-radius:6px;padding:10px;background:var(--surface);}}
.tile-group-label{{font-size:0.75em;color:var(--muted);text-transform:uppercase;letter-spacing:0.04em;margin-bottom:6px;}}
.tile-row{{display:flex;gap:8px;}}
.tile{{flex:1 1 80px;background:var(--bg);border:1px solid var(--border);border-radius:5px;padding:8px 6px;text-align:center;}}
.tile .big{{font-size:1.6em;font-weight:700;color:var(--purple);}}
.tile .label{{font-size:0.75em;color:var(--muted);margin-top:1px;}}
.tile-misc{{flex:1 1 120px;background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:10px;text-align:center;}}
.tile-misc .big{{font-size:1.8em;font-weight:700;color:var(--purple);}}
.tile-misc .label{{font-size:0.78em;color:var(--muted);margin-top:2px;}}
table.data-table{{width:100%;border-collapse:collapse;font-size:0.82em;margin:8px 0;}}
.data-table th,.data-table td{{border:1px solid var(--border);padding:3px 6px;text-align:left;}}
.data-table th{{background:var(--surface);font-weight:600;white-space:nowrap;}}
.data-table tr:hover{{background:var(--surface);}}
.col-group-b{{border-left:2px solid var(--accent);}}
.col-group-c{{border-left:2px solid var(--purple);}}
details.violation{{margin:4px 0;border:1px solid var(--border);border-radius:4px;}}
details.violation-datastale{{margin:4px 0;border:1px dashed var(--border);border-radius:4px;opacity:0.7;}}
details summary{{padding:6px 10px;cursor:pointer;font-size:0.85em;}}
.cat{{color:var(--muted);font-size:0.8em;}}
pre.vbody{{font-size:0.75em;padding:8px;background:var(--bg);overflow-x:auto;white-space:pre-wrap;word-break:break-word;}}
.section-note{{font-size:0.8em;color:var(--muted);margin-bottom:8px;}}
.legend{{display:flex;flex-wrap:wrap;gap:10px;font-size:0.8em;color:var(--muted);margin:4px 0 8px;}}
.legend span::before{{content:"■ ";}}
.legend .b0::before{{color:#6b7280;}}
.legend .b1::before{{color:#3b82d4;}}
.legend .mh::before{{color:#7c5cd8;}}
.replay-table td.caught{{color:var(--caught);background:var(--caught-bg);font-weight:600;}}
.replay-table td.miss{{color:var(--miss);background:var(--miss-bg);font-weight:600;}}
.replay-table td.blank{{color:var(--muted);}}
.replay-table td.subject{{font-size:0.8em;max-width:200px;word-break:break-word;}}
.replay-table td.note{{font-size:0.75em;color:var(--muted);max-width:160px;word-break:break-word;}}
@media(max-width:700px){{.col-bars,.col-date,.col-subject{{display:none;}}}}
footer{{margin-top:32px;padding-top:12px;border-top:1px solid var(--border);text-align:center;font-size:0.75em;color:var(--muted);}}
</style>
</head>
<body>
<div class="wrap">
<h1>MutantHunter Dashboard</h1>
<p class="muted">Mutation testing results for the <em>validators</em> package. Generated by <code>mutanthunter report</code>.</p>

<div class="hero">
<h2 style="border:none;margin-top:0;">Pooled Hold-out Score — main modules</h2>
{hero_row(pool_b, "Split B")}
{hero_row(pool_c, "Exam C")}
</div>

<div class="tiles">
  <div class="tile-group">
    <div class="tile-group-label">Extra kills — Split B</div>
    <div class="tile-row">
      <div class="tile" title="Split-B mutants killed by MH but not by B1">
        <div class="big">{mh_extra_b if mh_extra_b else "—"}</div>
        <div class="label">MH over B1</div>
      </div>
      <div class="tile" title="Split-B mutants killed by B1 but not by MH">
        <div class="big">{b1_extra_b if b1_extra_b else "—"}</div>
        <div class="label">B1 over MH</div>
      </div>
    </div>
  </div>
  <div class="tile-group">
    <div class="tile-group-label">Extra kills — Exam C</div>
    <div class="tile-row">
      <div class="tile" title="Exam-C mutants killed by MH but not by B1">
        <div class="big">{mh_extra_c if mh_extra_c else "—"}</div>
        <div class="label">MH over B1</div>
      </div>
      <div class="tile" title="Exam-C mutants killed by B1 but not by MH">
        <div class="big">{b1_extra_c if b1_extra_c else "—"}</div>
        <div class="label">B1 over MH</div>
      </div>
    </div>
  </div>
  <div class="tile-misc" title="Suspected logic violations found">
    <div class="big">{cat_totals['logic']}</div>
    <div class="label">Logic violations suspected</div>
  </div>
  <div class="tile-misc" title="Total suspected violations (all categories)">
    <div class="big">{sum(cat_totals.values())}</div>
    <div class="label">Total suspected violations</div>
  </div>
</div>

<h2>Per-module scores</h2>
<p class="section-note">Split B = hold-out half; Exam C = out-of-distribution operators. B0 = human; B1 = human+B1; MH = human+MH. Bars show split-B (falls back to split-A).</p>
<div class="legend">
  <span class="b0">B0</span><span class="b1">B1</span><span class="mh">MH</span>
</div>
<div style="overflow-x:auto;">
<table class="data-table">
<thead>
  <tr>
    <th rowspan="2">Module</th>
    <th rowspan="2">Set</th>
    <th rowspan="2" class="col-bars">Bars</th>
    <th colspan="3" class="col-group-b" style="text-align:center;">Split B</th>
    <th colspan="3" class="col-group-c" style="text-align:center;">Exam C</th>
    <th rowspan="2">Tests</th>
    <th rowspan="2">Bugs</th>
    <th rowspan="2">Min</th>
  </tr>
  <tr>
    <th class="col-group-b">B0</th><th>B1</th><th>MH</th>
    <th class="col-group-c">B0</th><th>B1</th><th>MH</th>
  </tr>
</thead>
<tbody>
{"".join(mod_row(m) for m in mods if m["run"])}
</tbody>
</table>
</div>
{not_run_html}

<h2>Suspected violations</h2>
<p class="section-note">Logic and human-test-conflict first; data-staleness entries are collapsed.</p>
{violation_section()}

<h2>Historical bug replay</h2>
<p class="section-note">
  Caught = at least one test fails on the pre-fix commit and passes on the fix commit.
  <strong>Reading notes (spec §7.4):</strong>
  Tests written today encode today's fixed behavior — any test that pins current behavior "catches"
  a reverted fix, so B1 and the human tests look good here for reasons unrelated to finding bugs
  before release. Report B1 replay as context only, never as a comparison with MH.
  The meaningful result is the <em>extra</em> set (mac_address, hostname): bugs the human tests
  still miss at HEAD. Row <code>1231f6a</code> is spec-ambiguous (RFC 3986 vs WHATWG); reported
  but not counted.
</p>
<div style="overflow-x:auto;">
{replay_table()}
</div>

<h2>Method and limits</h2>
<ul>
  <li>Mutant operators: comparison flips, boolean swaps, if-negate, return-none, int±1, binary-op changes.</li>
  <li>Split B is a fixed held-out half (seed 20260925); never used during test generation.</li>
  <li>Exam C uses independent operator types (boolean flip, drop-not, string-wrap, drop-case-methods, ±= swap); scored after generation is final.</li>
  <li>Suspected violations are unconfirmed until a human reads the code and the spec.</li>
  <li>95% confidence intervals are Wilson score intervals. McNemar test is exact two-sided.</li>
  <li>data-staleness violations (country/currency tables) are reported separately and excluded from the headline count.</li>
</ul>
</div>
<footer>Made with IBM Bob</footer>
</body>
</html>"""

    path.write_text(html, encoding="utf-8")


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def report(results_dir: Path, docs_dir: Path, modules_csv: Path) -> list[Path]:
    """Generate summary.csv, stats.md, and docs/index.html.

    Returns the list of paths written.
    """
    registry = _load_modules_csv(modules_csv)
    mutant_files = _find_mutant_files(results_dir)
    replay_rows = _load_replay(results_dir)
    costs_rows = _load_costs(results_dir)

    # summary.csv
    summary_rows = _build_summary_rows(registry, results_dir, mutant_files)
    summary_path = results_dir / "summary.csv"
    _write_summary_csv(summary_path, summary_rows)

    # stats.md
    stats_path = results_dir / "stats.md"
    _write_stats_md(stats_path, registry, results_dir, mutant_files, costs_rows)

    # docs/index.html
    docs_dir.mkdir(parents=True, exist_ok=True)
    html_path = docs_dir / "index.html"
    _write_index_html(html_path, registry, results_dir, mutant_files, replay_rows, costs_rows)

    written = [summary_path, stats_path, html_path]
    for p in written:
        print(f"  wrote {p}")
    return written
