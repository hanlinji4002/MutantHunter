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

import base64
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


_ASSETS = Path(__file__).parent / "assets" / "fonts"
_FONT_FILES = [
    ("Source Serif 4", "SourceSerif4-latin.woff2", "200 900", "normal"),
    ("IBM Plex Sans", "IBMPlexSans-latin.woff2", "100 700", "normal"),
    ("IBM Plex Mono", "IBMPlexMono-latin.woff2", "400", "normal"),
]
_SERIES = [("human", "b0", "B0", "human tests"), ("human+b1", "b1", "B1", "plain prompt"), ("human+mh", "mh", "MH", "MutantHunter")]


def _font_face_css() -> str:
    """Inline the bundled fonts so the dashboard works offline; fall back silently."""
    rules = []
    for family, fname, weight, style in _FONT_FILES:
        p = _ASSETS / fname
        if not p.exists():
            continue
        data = base64.b64encode(p.read_bytes()).decode("ascii")
        rules.append(
            f"@font-face{{font-family:'{family}';font-style:{style};font-weight:{weight};"
            f"font-display:swap;src:url(data:font/woff2;base64,{data}) format('woff2');}}"
        )
    return "\n".join(rules)


def _inline_md(s: str) -> str:
    """Escape text and turn `code` spans into <code>."""
    parts = s.split("`")
    return "".join(f"<code>{_esc(p)}</code>" if i % 2 else _esc(p) for i, p in enumerate(parts))


def _parse_violations(results_dir: Path, registry: dict) -> list[dict]:
    """Parse results/suspected_bugs/*.md into entries with their fields."""
    slug_to_module = {_slug(m): m for m in registry}
    entries = []
    for p in sorted((results_dir / "suspected_bugs").glob("*.md")):
        module = slug_to_module.get(p.stem, p.stem)
        text = p.read_text(encoding="utf-8")
        for block in re.split(r"\n(?=## )", text):
            block = block.strip()
            if not block.startswith("## "):
                continue
            fields: dict[str, str] = {}
            for line in block.splitlines():
                m = re.match(r"^- ([A-Za-z][A-Za-z -]*):\s*(.*)$", line)
                if m and m.group(1) not in fields:
                    fields[m.group(1)] = m.group(2).strip()
            title = re.sub(r"^SV-\d+:\s*", "", block.split("\n", 1)[0][3:].strip())
            entries.append({"module": module, "title": title, "fields": fields, "raw": block})
    return entries


def _column_chart_svg(pool: dict[str, Any], split_name: str) -> str:
    """Pooled score per suite as columns with 95% CI whiskers."""
    W, H, left, right, top, bottom = 360, 250, 46, 10, 30, 46
    pw, ph = W - left - right, H - top - bottom
    y = lambda v: top + ph * (1 - v)
    out = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Pooled {split_name} score by suite">']
    for g in (0, 0.25, 0.5, 0.75, 1.0):
        out.append(f'<line class="grid" x1="{left}" x2="{W - right}" y1="{y(g):.1f}" y2="{y(g):.1f}"/>')
        out.append(f'<text class="tick" x="{left - 8}" y="{y(g) + 4:.1f}" text-anchor="end">{int(g * 100)}%</text>')
    bw = 44
    for i, (suite, cls, short, desc) in enumerate(_SERIES):
        d = pool[suite]
        cx = left + pw * (i + 0.5) / 3
        x0 = cx - bw / 2
        out.append(f'<text class="xlab" x="{cx:.1f}" y="{H - 24}" text-anchor="middle">{short}</text>')
        out.append(f'<text class="xsub" x="{cx:.1f}" y="{H - 8}" text-anchor="middle">{desc}</text>')
        if not d["n"]:
            out.append(f'<text class="val" x="{cx:.1f}" y="{y(0) - 8:.1f}" text-anchor="middle">—</text>')
            continue
        yt, yb, r = y(d["p"]), y(0), 4
        tip = f'{short} ({desc}): {d["k"]}/{d["n"]} killed, {d["p"] * 100:.1f}% (95% CI {d["lo"] * 100:.1f}–{d["hi"] * 100:.1f}%)'
        out.append(
            f'<g class="mark"><title>{_esc(tip)}</title>'
            f'<path class="s-{cls}" d="M{x0:.1f},{yb:.1f} L{x0:.1f},{yt + r:.1f} Q{x0:.1f},{yt:.1f} {x0 + r:.1f},{yt:.1f} '
            f'L{x0 + bw - r:.1f},{yt:.1f} Q{x0 + bw:.1f},{yt:.1f} {x0 + bw:.1f},{yt + r:.1f} L{x0 + bw:.1f},{yb:.1f} Z"/>'
            f'<line class="ci" x1="{cx:.1f}" x2="{cx:.1f}" y1="{y(d["lo"]):.1f}" y2="{y(d["hi"]):.1f}"/>'
            f'<line class="ci" x1="{cx - 6:.1f}" x2="{cx + 6:.1f}" y1="{y(d["lo"]):.1f}" y2="{y(d["lo"]):.1f}"/>'
            f'<line class="ci" x1="{cx - 6:.1f}" x2="{cx + 6:.1f}" y1="{y(d["hi"]):.1f}" y2="{y(d["hi"]):.1f}"/>'
            f'<rect class="hit" x="{x0 - 8:.1f}" y="{top:.1f}" width="{bw + 16}" height="{ph:.1f}"/></g>'
        )
        out.append(f'<text class="val" x="{cx:.1f}" y="{y(d["hi"]) - 8:.1f}" text-anchor="middle">{d["p"] * 100:.1f}%</text>')
    out.append("</svg>")
    return "".join(out)


def _module_chart_svg(rows: list[dict], split: str) -> str:
    """Grouped horizontal bars per module: B0 / B1 / MH, value label on MH."""
    W, label_w, right, top = 440, 118, 52, 26
    bar_h, gap, group_gap = 8, 2, 16
    group_h = 3 * bar_h + 2 * gap
    H = top + len(rows) * (group_h + group_gap) + 4
    pw = W - label_w - right
    x = lambda v: label_w + pw * v
    out = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Split {split} score by module">']
    for g in (0, 0.5, 1.0):
        out.append(f'<line class="grid" x1="{x(g):.1f}" x2="{x(g):.1f}" y1="{top - 6}" y2="{H - 4}"/>')
        out.append(f'<text class="tick" x="{x(g):.1f}" y="{top - 12}" text-anchor="middle">{int(g * 100)}%</text>')
    for j, row in enumerate(rows):
        gy = top + j * (group_h + group_gap)
        out.append(f'<text class="rowlab" x="{label_w - 12}" y="{gy + group_h / 2 + 1:.1f}" text-anchor="end">{_esc(row["module"])}</text>')
        if row["set"] == "extra":
            out.append(f'<text class="rowsub" x="{label_w - 12}" y="{gy + group_h / 2 + 14:.1f}" text-anchor="end">extra</text>')
        for i, (suite, cls, short, desc) in enumerate(_SERIES):
            k, n = row[split].get(suite, (None, None))
            by = gy + i * (bar_h + gap)
            if not n:
                continue
            v = k / n
            x0, x1, r = x(0), max(x(v), x(0) + 2), 3
            tip = f'{row["module"]} · {short} ({desc}): {k}/{n} killed, {v * 100:.1f}%'
            out.append(
                f'<g class="mark"><title>{_esc(tip)}</title>'
                f'<path class="s-{cls}" d="M{x0:.1f},{by:.1f} L{x1 - r:.1f},{by:.1f} Q{x1:.1f},{by:.1f} {x1:.1f},{by + r:.1f} '
                f'L{x1:.1f},{by + bar_h - r:.1f} Q{x1:.1f},{by + bar_h:.1f} {x1 - r:.1f},{by + bar_h:.1f} L{x0:.1f},{by + bar_h:.1f} Z"/>'
                f'<rect class="hit" x="{x0:.1f}" y="{by - 1:.1f}" width="{pw:.1f}" height="{bar_h + 2}"/></g>'
            )
            if cls == "mh":
                out.append(f'<text class="val sm" x="{x1 + 6:.1f}" y="{by + bar_h:.1f}">{v * 100:.1f}%</text>')
    out.append("</svg>")
    return "".join(out)


def _legend_html() -> str:
    items = "".join(
        f'<span class="key"><i class="sw s-{cls}"></i><b>{short}</b> {desc}</span>' for _, cls, short, desc in _SERIES
    )
    return f'<div class="legend">{items}</div>'


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

    pool_b = _pooled_stats(registry, results_dir, mutant_files, "main", "B")
    pool_c = _pooled_stats(registry, results_dir, mutant_files, "main", "C")
    b_only_b, c_only_b, p_b = _mcnemar_b1_vs_mh(registry, results_dir, mutant_files, "main", "B")
    b_only_c, c_only_c, p_c = _mcnemar_b1_vs_mh(registry, results_dir, mutant_files, "main", "C")

    cat_totals: dict[str, int] = {"logic": 0, "data-staleness": 0, "spec-ambiguous": 0, "human-test-conflict": 0}
    for m in run_mods:
        for cat in cat_totals:
            cat_totals[cat] += m.get("bugs", {}).get(cat, 0)

    # Per-module kill counts for the charts and the table view
    set_order = {"main": 0, "extra": 1}
    chart_rows = []
    for m in sorted(run_mods, key=lambda m: (set_order.get(m["set"], 2), m["module"])):
        row = {"module": m["module"], "set": m["set"], "m": m, "B": {}, "C": {}}
        for split in ("B", "C"):
            for suite, *_ in _SERIES:
                key = (m["slug"], suite, split)
                if key in mutant_files:
                    d = _load_mutant_file(mutant_files[key])
                    row[split][suite] = (d.get("killed", 0), d.get("mutants", 0))
        chart_rows.append(row)

    def pct_cell(row: dict, split: str, suite: str, strong: bool = False) -> str:
        k, n = row[split].get(suite, (None, None))
        if not n:
            return "<td class='num'>—</td>"
        v = f"{k / n * 100:.1f}%"
        return f"<td class='num' title='{k}/{n} killed'>{'<b>' + v + '</b>' if strong else v}</td>"

    table_rows = []
    for row in chart_rows:
        m = row["m"]
        coins = m.get("bobcoins")
        table_rows.append(
            "<tr>"
            f"<td>{_esc(row['module'])}</td><td>{_esc(row['set'])}</td>"
            + pct_cell(row, "B", "human") + pct_cell(row, "B", "human+b1") + pct_cell(row, "B", "human+mh", True)
            + pct_cell(row, "C", "human") + pct_cell(row, "C", "human+b1") + pct_cell(row, "C", "human+mh", True)
            + f"<td class='num'>{m.get('tests_kept', '—')}</td>"
            + f"<td class='num'>{sum(m.get('bugs', {}).values())}</td>"
            + f"<td class='num'>{m.get('minutes', '—')}</td>"
            + f"<td class='num'>{coins if coins is not None else '—'}</td>"
            "</tr>"
        )

    # Suspected violations: confirmed bugs grouped by their Bug key
    entries = _parse_violations(results_dir, registry)
    groups: dict[str, list[dict]] = {}
    for e in entries:
        if e["fields"].get("Status", "").lower().startswith("confirmed"):
            groups.setdefault(e["fields"].get("Bug") or e["title"], []).append(e)
    rejected = [e for e in entries if e["fields"].get("Status", "").lower().startswith("rejected")]
    unconfirmed = [e for e in entries if e not in rejected and not e["fields"].get("Status", "").lower().startswith("confirmed")]

    cards, n_new = [], 0
    for key, group in groups.items():
        first = group[0]
        f = next((g["fields"] for g in group if "Code" in g["fields"]), first["fields"])
        upstream = f.get("Upstream", "")
        known = "known" in upstream.lower()
        n_new += 0 if known else 1
        tag = "<span class='tag tag-gray'>known upstream</span>" if known else "<span class='tag tag-blue'>new</span>"
        inputs = [g["fields"].get("Input", "") for g in group if g["fields"].get("Input")]
        cards.append(
            "<article class='bug'>"
            f"<div class='bug-meta'><span class='tag tag-module'>{_esc(first['module'])}</span>{tag}"
            f"<span class='muted'>{len(group)} test entr{'y' if len(group) == 1 else 'ies'}</span></div>"
            f"<h3>{_inline_md(first['title'])}</h3>"
            + (f"<p><span class='k'>Input</span> {_inline_md(inputs[0])}</p>" if inputs else "")
            + (f"<p><span class='k'>Code</span> {_inline_md(f['Code'])}</p>" if f.get("Code") else "")
            + (f"<p><span class='k'>Upstream</span> {_inline_md(upstream)}</p>" if upstream else "")
            + "</article>"
        )
    rejected_items = "".join(
        f"<li><b>{_esc(e['module'])}</b>: {_inline_md(e['title'])}. <span class='muted'>{_inline_md(e['fields'].get('Review', ''))}</span></li>"
        for e in rejected
    )
    raw_items = "".join(
        f"<details class='{'violation-datastale' if e['fields'].get('Category') == 'data-staleness' else 'violation'}'>"
        f"<summary>{_esc(e['module'])}: {_inline_md(e['title'])} <span class='cat'>{_esc(e['fields'].get('Category', ''))} · {_esc(e['fields'].get('Status', 'unconfirmed'))}</span></summary>"
        f"<pre class='vbody'>{_esc(e['raw'])}</pre></details>"
        for e in entries
    )

    # Historical replay: extra-set bugs that the human tests still miss
    extra_rows = [r for r in replay_rows if r.get("set") == "extra"]
    extra_keys = {(r.get("sha") or r.get("commit", ""), r.get("module", "")) for r in extra_rows}
    mh_caught_extra = {(r.get("sha") or r.get("commit", ""), r.get("module", "")) for r in extra_rows if r.get("suite") == "mh" and r.get("result") == "caught"}
    human_caught_extra = {(r.get("sha") or r.get("commit", ""), r.get("module", "")) for r in extra_rows if r.get("suite") == "human" and r.get("result") == "caught"}

    def replay_table() -> str:
        if not replay_rows:
            return "<p class='muted'>No replay data yet (<code>results/replay.csv</code> missing).</p>"
        pivot: dict[tuple[str, str], dict] = {}
        for row in replay_rows:
            sha = row.get("sha") or row.get("commit", "")
            key = (sha, row.get("module", ""))
            d = pivot.setdefault(key, {"sha": sha, "date": row.get("date", ""), "module": row.get("module", ""),
                                       "set": row.get("set", ""), "subject": row.get("subject", ""),
                                       "note": row.get("note", ""), "human": "", "mh": "", "b1": ""})
            if row.get("suite") in ("human", "mh", "b1"):
                d[row["suite"]] = row.get("result", "")
        order = {"extra": 0, "main": 1, "reference": 2}
        rows = sorted(pivot.values(), key=lambda r: (order.get(r["set"], 9), r["date"], r["module"]))

        def cell(v: str) -> str:
            if v == "caught":
                return "<td><span class='tag tag-green'>caught</span></td>"
            if v == "miss":
                return "<td><span class='tag tag-red'>miss</span></td>"
            return "<td class='muted'>—</td>"

        body = "".join(
            f"<tr class='{'row-extra' if r['set'] == 'extra' else ''}'>"
            f"<td><code>{_esc(r['sha'][:7])}</code></td><td class='col-date'>{_esc(r['date'])}</td>"
            f"<td>{_esc(r['module'])}</td><td>{_esc(r['set'])}</td>"
            f"<td class='subject col-subject'>{_esc(r['subject'])}</td>"
            + cell(r["human"]) + cell(r["mh"]) + cell(r["b1"])
            + f"<td class='note'>{_esc(r['note'])}</td></tr>"
            for r in rows
        )
        head = ("<tr><th>SHA</th><th class='col-date'>Date</th><th>Module</th><th>Set</th>"
                "<th class='col-subject'>Subject</th><th>Human</th><th>MH</th><th>B1</th><th>Note</th></tr>")
        return f"<table class='data-table replay-table'>{head}{body}</table>"

    def score_card(pool: dict[str, Any], name: str, sub: str, b: int, c: int, p: float) -> str:
        b0, b1, mh = pool["human"], pool["human+b1"], pool["human+mh"]
        if not mh["n"]:
            return (f"<div class='card'><div class='card-head'><h3>{name}</h3><p class='muted'>{sub}</p></div>"
                    f"<p class='muted'>Not scored yet.</p>{_column_chart_svg(pool, name)}</div>")
        return (
            f"<div class='card'><div class='card-head'><h3>{name}</h3><p class='muted'>{sub}</p></div>"
            f"<div class='figure'><span class='from'>{b0['p'] * 100:.1f}%</span><span class='arrow'>→</span>"
            f"<span class='to'>{mh['p'] * 100:.1f}%</span></div>"
            f"<p class='figure-note'>Human tests → with MutantHunter · plain prompt (B1) {b1['p'] * 100:.1f}% · "
            f"{mh['n']} mutants · McNemar B1 vs MH: {b} only B1, {c} only MH, p = {p:.3f}</p>"
            f"{_column_chart_svg(pool, name)}</div>"
        )

    not_run_html = ""
    if not_run:
        items = ", ".join(_esc(m["module"]) for m in not_run)
        not_run_html = f"<p class='muted small'>Not run in this study: {items}</p>"

    kpi_hist = (f"{len(mh_caught_extra)}/{len(extra_keys)}" if extra_keys else "—")
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MutantHunter Dashboard</title>
<style>
{_font_face_css()}
:root {{
  --bg:#ffffff; --layer:#f4f4f4; --layer-2:#e8e8e8; --border:#e0e0e0; --border-strong:#c6c6c6;
  --text:#161616; --text-2:#525252; --text-3:#6f6f6f; --link:#0f62fe; --accent:#0f62fe;
  --b0:#b28600; --b1:#ee538b; --mh:#0f62fe;
  --grid:#e0e0e0; --ci:#161616;
  --green-bg:#a7f0ba; --green-fg:#0e6027; --red-bg:#ffd7d9; --red-fg:#a2191f;
  --blue-bg:#d0e2ff; --blue-fg:#0043ce; --gray-bg:#e0e0e0; --gray-fg:#393939;
  --serif:'Source Serif 4',Georgia,'Times New Roman',serif;
  --sans:'IBM Plex Sans','Helvetica Neue',Arial,sans-serif;
  --mono:'IBM Plex Mono',Menlo,Consolas,monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg:#161616; --layer:#262626; --layer-2:#393939; --border:#393939; --border-strong:#6f6f6f;
    --text:#f4f4f4; --text-2:#c6c6c6; --text-3:#a8a8a8; --link:#78a9ff; --accent:#4589ff;
    --b0:#b28600; --b1:#ee538b; --mh:#4589ff;
    --grid:#393939; --ci:#f4f4f4;
    --green-bg:#044317; --green-fg:#6fdc8c; --red-bg:#750e13; --red-fg:#ffb3b8;
    --blue-bg:#002d9c; --blue-fg:#a6c8ff; --gray-bg:#393939; --gray-fg:#e0e0e0;
  }}
}}
*{{box-sizing:border-box;margin:0;padding:0;}}
html{{-webkit-text-size-adjust:100%;}}
body{{background:var(--bg);color:var(--text);font-family:var(--serif);font-size:17px;line-height:1.6;}}
a{{color:var(--link);text-decoration:none;}} a:hover{{text-decoration:underline;}}
code{{font-family:var(--mono);font-size:0.82em;background:var(--layer);padding:1px 4px;}}
.shell{{position:sticky;top:0;z-index:5;background:#161616;color:#f4f4f4;border-bottom:1px solid #393939;
  font-family:var(--sans);font-size:14px;height:48px;display:flex;align-items:center;gap:16px;padding:0 16px;}}
.shell .brand{{white-space:nowrap;}} .shell .brand b{{font-weight:600;}}
.shell .div{{width:1px;height:20px;background:#525252;}}
.shell nav{{margin-left:auto;display:flex;gap:18px;overflow-x:auto;}}
.shell nav a{{color:#c6c6c6;white-space:nowrap;}} .shell nav a:hover{{color:#fff;text-decoration:none;}}
.wrap{{max-width:1120px;margin:0 auto;padding:0 16px 48px;}}
.intro{{padding:48px 0 32px;border-bottom:1px solid var(--border);}}
.eyebrow{{font-family:var(--sans);font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin-bottom:10px;}}
h1{{font-weight:600;font-size:clamp(34px,6vw,52px);line-height:1.1;letter-spacing:-.01em;}}
.lede{{max-width:760px;font-size:19px;color:var(--text-2);margin-top:14px;}}
section{{padding:40px 0 8px;}}
h2{{font-weight:600;font-size:28px;line-height:1.25;margin-bottom:8px;}}
h3{{font-weight:600;font-size:19px;line-height:1.35;}}
.section-note{{color:var(--text-2);max-width:820px;margin-bottom:18px;font-size:16px;}}
.muted{{color:var(--text-3);}} .small{{font-size:14px;margin-top:10px;}}
.grid-2{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px;}}
.card{{background:var(--layer);padding:20px 20px 12px;border-top:4px solid var(--accent);}}
.card-head{{display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:4px 12px;}}
.card-head p{{font-family:var(--sans);font-size:13px;}}
.figure{{font-family:var(--sans);display:flex;align-items:baseline;gap:10px;margin:10px 0 2px;}}
.figure .from{{font-size:26px;color:var(--text-3);}}
.figure .arrow{{font-size:22px;color:var(--text-3);}}
.figure .to{{font-size:48px;font-weight:600;line-height:1;color:var(--text);}}
.figure-note{{font-family:var(--sans);font-size:13px;color:var(--text-2);margin-bottom:6px;}}
.legend{{font-family:var(--sans);font-size:14px;color:var(--text-2);display:flex;flex-wrap:wrap;gap:6px 20px;margin:0 0 14px;}}
.legend .key{{display:inline-flex;align-items:center;gap:6px;}} .legend b{{color:var(--text);font-weight:600;}}
.sw{{display:inline-block;width:12px;height:12px;border-radius:2px;}}
.s-b0{{fill:var(--b0);background:var(--b0);}} .s-b1{{fill:var(--b1);background:var(--b1);}} .s-mh{{fill:var(--mh);background:var(--mh);}}
svg.chart{{width:100%;height:auto;display:block;font-family:var(--sans);}}
.chart .grid{{stroke:var(--grid);stroke-width:1;}}
.chart .tick{{fill:var(--text-3);font-size:11px;}}
.chart .xlab{{fill:var(--text);font-size:14px;font-weight:600;}}
.chart .xsub{{fill:var(--text-3);font-size:11px;}}
.chart .val{{fill:var(--text);font-size:14px;font-weight:600;}} .chart .val.sm{{font-size:11px;}}
.chart .rowlab{{fill:var(--text);font-size:13px;}} .chart .rowsub{{fill:var(--text-3);font-size:10px;}}
.chart .ci{{stroke:var(--ci);stroke-width:1.5;opacity:.75;}}
.chart .hit{{fill:transparent;}}
.chart .mark:hover path{{opacity:.8;}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;padding-top:24px;}}
.kpi{{background:var(--layer);padding:18px 20px;}}
.kpi .label{{font-family:var(--sans);font-size:13px;color:var(--text-2);}}
.kpi .value{{font-family:var(--sans);font-size:36px;font-weight:600;line-height:1.15;margin-top:6px;}}
.kpi .sub{{font-family:var(--sans);font-size:13px;color:var(--text-3);margin-top:4px;}}
.table-wrap{{overflow-x:auto;margin-top:16px;}}
table.data-table{{width:100%;border-collapse:collapse;font-family:var(--sans);font-size:14px;}}
.data-table th{{text-align:left;font-weight:600;background:var(--layer-2);padding:10px 12px;white-space:nowrap;}}
.data-table td{{padding:9px 12px;border-bottom:1px solid var(--border);vertical-align:top;}}
.data-table td.num{{text-align:right;font-variant-numeric:tabular-nums;}}
.data-table tr:hover td{{background:var(--layer);}}
.data-table th.grp{{text-align:center;border-left:2px solid var(--bg);}}
.data-table th.num{{text-align:right;}}
.replay-table td.subject{{max-width:260px;color:var(--text-2);}}
.replay-table td.note{{max-width:220px;color:var(--text-3);font-size:12px;}}
.replay-table tr.row-extra td{{background:var(--layer);}}
.tag{{display:inline-block;font-family:var(--sans);font-size:12px;line-height:18px;padding:1px 8px;border-radius:12px;white-space:nowrap;}}
.tag-green{{background:var(--green-bg);color:var(--green-fg);}} .tag-red{{background:var(--red-bg);color:var(--red-fg);}}
.tag-blue{{background:var(--blue-bg);color:var(--blue-fg);}} .tag-gray{{background:var(--gray-bg);color:var(--gray-fg);}}
.tag-module{{background:transparent;border:1px solid var(--border-strong);color:var(--text);}}
.bugs{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px;}}
.bug{{background:var(--layer);padding:18px 20px;border-left:4px solid var(--accent);}}
.bug-meta{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:8px;font-family:var(--sans);font-size:12px;}}
.bug h3{{margin-bottom:8px;}}
.bug p{{font-size:15px;color:var(--text-2);margin-top:6px;overflow-wrap:anywhere;}}
.bug .k{{font-family:var(--sans);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--text-3);margin-right:6px;}}
details{{margin-top:14px;}}
details>summary{{cursor:pointer;font-family:var(--sans);font-size:15px;color:var(--link);}}
details ul{{margin:10px 0 0 20px;font-size:15px;}} details li{{margin:6px 0;}}
details.violation,details.violation-datastale{{margin:6px 0;background:var(--layer);padding:8px 12px;}}
details.violation>summary,details.violation-datastale>summary{{color:var(--text);font-size:14px;}}
details.violation-datastale{{opacity:.75;}}
.cat{{color:var(--text-3);font-size:12px;margin-left:6px;}}
pre.vbody{{font-family:var(--mono);font-size:12px;white-space:pre-wrap;overflow-wrap:anywhere;margin-top:8px;color:var(--text-2);}}
.method ul{{margin-left:20px;max-width:880px;}} .method li{{margin:6px 0;}}
footer{{border-top:1px solid var(--border);margin-top:40px;padding:20px 16px;text-align:center;font-family:var(--sans);font-size:13px;color:var(--text-3);}}
@media (max-width:700px){{ .col-date,.col-subject{{display:none;}} body{{font-size:16px;}} .shell nav{{display:none;}} }}
</style>
</head>
<body>
<header class="shell"><span class="brand">IBM <b>Bob</b> Hackathon</span><span class="div"></span><span>MutantHunter</span>
<nav><a href="#results">Results</a><a href="#modules">Modules</a><a href="#bugs">Bugs</a><a href="#replay">Replay</a><a href="#method">Method</a></nav></header>
<main class="wrap">
<div class="intro">
  <p class="eyebrow">Mutation testing · specification-derived tests · python-validators</p>
  <h1>MutantHunter</h1>
  <p class="lede">Finds the bugs a test suite misses, writes tests that catch them, and proves the gain on mutants the agents never saw. Generated by <code>mutanthunter report</code> from the files in <code>results/</code>.</p>
</div>

<section id="results">
<h2>Pooled Hold-out Score — main modules</h2>
<p class="section-note">Share of mutants killed, pooled over the main modules. Split B is the hidden half of the mutants; exam C uses mutant operators that did not exist while the tests were written. Whiskers are 95% Wilson intervals.</p>
{_legend_html()}
<div class="grid-2">
{score_card(pool_b, "Split B", "hold-out half", b_only_b, c_only_b, p_b)}
{score_card(pool_c, "Exam C", "unseen operators", b_only_c, c_only_c, p_c)}
</div>
</section>

<div class="kpis">
  <div class="kpi" title="Mutants killed by MH but not by B1 (and the reverse), main modules"><div class="label">Extra kills over the plain prompt</div><div class="value">+{c_only_c} / −{b_only_c}</div><div class="sub">exam C · split B: +{c_only_b} / −{b_only_b}</div></div>
  <div class="kpi" title="Distinct bugs confirmed by reading the code"><div class="label">Bugs confirmed</div><div class="value">{len(groups)}</div><div class="sub">{n_new} not reported upstream · {len(entries)} suspected, {cat_totals['logic']} logic</div></div>
  <div class="kpi" title="Historical bugs that today's human tests still miss"><div class="label">Missed historical bugs caught</div><div class="value">{kpi_hist}</div><div class="sub">by the MH tests · human tests {len(human_caught_extra)}/{len(extra_keys)}</div></div>
</div>

<section id="modules">
<h2>Per-module scores</h2>
<p class="section-note">Each module on the hidden split B and on exam C. Hover a bar for the counts; the table below holds every value.</p>
{_legend_html()}
<div class="grid-2">
<div class="card"><div class="card-head"><h3>Split B</h3><p class="muted">hold-out half</p></div>{_module_chart_svg(chart_rows, "B")}</div>
<div class="card"><div class="card-head"><h3>Exam C</h3><p class="muted">unseen operators</p></div>{_module_chart_svg(chart_rows, "C")}</div>
</div>
<div class="table-wrap">
<table class="data-table">
<thead>
<tr><th rowspan="2">Module</th><th rowspan="2">Set</th><th colspan="3" class="grp">Split B</th><th colspan="3" class="grp">Exam C</th><th rowspan="2" class="num">Tests</th><th rowspan="2" class="num">Suspected</th><th rowspan="2" class="num">Min</th><th rowspan="2" class="num">Bobcoins</th></tr>
<tr><th class="num">B0</th><th class="num">B1</th><th class="num">MH</th><th class="num">B0</th><th class="num">B1</th><th class="num">MH</th></tr>
</thead>
<tbody>{"".join(table_rows)}</tbody>
</table>
</div>
{not_run_html}
</section>

<section id="bugs">
<h2>Bugs found</h2>
<p class="section-note">The spec subagents turn every test that fails on the current code into a suspected violation. Each one was reviewed by reading the code and searching the upstream issues.</p>
<div class="bugs">{"".join(cards) if cards else "<p class='muted'>No confirmed bugs yet.</p>"}</div>
{f"<details><summary>Rejected after review ({len(rejected)})</summary><ul>{rejected_items}</ul></details>" if rejected else ""}
{f"<p class='muted small'>{len(unconfirmed)} suspected violations not reviewed yet.</p>" if unconfirmed else ""}
<details><summary>All suspected violations ({len(entries)}), raw entries</summary>{raw_items}</details>
</section>

<section id="replay">
<h2>Historical bug replay</h2>
<p class="section-note">Caught = at least one test fails on the pre-fix commit and passes on the fix. <b>Reading notes (spec §7.4):</b> tests written today encode today's fixed behaviour, so any test that pins current behaviour "catches" a reverted fix. The meaningful rows are the <em>extra</em> set (highlighted): bugs the human tests still miss. Report B1 as context only. Row <code>1231f6a</code> is spec-ambiguous (RFC 3986 vs WHATWG) and not counted.</p>
<div class="table-wrap">{replay_table()}</div>
</section>

<section id="method" class="method">
<h2>Method and limits</h2>
<ul>
  <li>Mutant operators: comparison flips, boolean swaps, if-negate, return-none, int±1, binary-op changes.</li>
  <li>Split B is a fixed hidden half (seed 20260925), never shown during test generation and scored once after generation was frozen.</li>
  <li>Exam C uses independent operators (boolean flip, drop-not, string-wrap, drop-case-methods, ±= swap), written and scored after the freeze.</li>
  <li>95% confidence intervals are Wilson score intervals; McNemar tests are exact and two-sided, four in total, without correction.</li>
  <li>Suspected violations are unconfirmed until a human reads the code and the spec; data-staleness entries are excluded from the headline count.</li>
</ul>
</section>
</main>
<footer>Made with IBM Bob · MutantHunter · every number on this page comes from <code>results/</code></footer>
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
