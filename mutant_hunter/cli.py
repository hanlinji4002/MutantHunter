"""CLI — mutanthunter entry point.

All six subcommands (baseline, mutate, check, generate, replay, report) are
registered here.  Modules not yet implemented (track B: report, replay, stats,
exam_c; and optional backends.bob) are imported lazily: if the import fails the
subcommand prints "not implemented yet" and exits 1.

Exit codes: 0 ok, 1 error/not-implemented, 2 BaselineError, 3 IsolationError.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import List


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _not_implemented(name: str) -> None:
    print("not implemented yet")
    sys.exit(1)


def _resolve_modules(value: str):
    """Resolve a --set or module argument to a list of Module objects."""
    from .registry import modules_by_set, get_module

    if value in ("main", "extra", "reference", "all"):
        return modules_by_set(value)
    # Try comma-separated list of module names
    names = [n.strip() for n in value.split(",")]
    mods = []
    for name in names:
        try:
            mods.append(get_module(name))
        except KeyError:
            # Try as a set name (shouldn't happen, but defensive)
            try:
                mods.extend(modules_by_set(name))
            except (KeyError, ValueError):
                print(f"error: unknown module or set: {name!r}", file=sys.stderr)
                sys.exit(1)
    return mods


# ---------------------------------------------------------------------------
# baseline
# ---------------------------------------------------------------------------

def _cmd_baseline(args: argparse.Namespace) -> None:
    from .mutate import run_baseline
    from .registry import REPO_ROOT

    set_name = args.set if hasattr(args, "set") and args.set else "all"
    modules = _resolve_modules(set_name)
    jobs = args.jobs
    seed = args.seed

    rows = []
    for mod in modules:
        print(f"  baseline {mod.module} ...", end="", flush=True)
        try:
            row = run_baseline(mod, jobs=jobs, seed=seed)
            match = row["ref_match"]
            print(f" {row['mutants']} mutants, {row['killed']} killed "
                  f"(ref {row['ref_mutants']}/{row['ref_killed']}) ref_match={match}")
            rows.append(row)
        except Exception as exc:
            print(f" ERROR: {exc}", file=sys.stderr)
            raise

    # Write results/baseline.csv
    results_dir = REPO_ROOT / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    csv_path = results_dir / "baseline.csv"
    fieldnames = [
        "module", "set", "suite", "split",
        "mutants", "killed", "score",
        "ref_mutants", "ref_killed", "ref_match",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row[k] for k in fieldnames})

    # Write results/baseline.md
    md_path = results_dir / "baseline.md"
    _write_baseline_md(md_path, rows, fieldnames)

    print(f"\nbaseline.csv written → {csv_path}")
    all_match = all(r["ref_match"] == "yes" for r in rows)
    if not all_match:
        mismatches = [r["module"] for r in rows if r["ref_match"] != "yes"]
        print(f"WARNING: ref_match=no for: {mismatches}", file=sys.stderr)


def _write_baseline_md(path: Path, rows: list, fieldnames: list) -> None:
    header = "| " + " | ".join(fieldnames) + " |"
    sep = "| " + " | ".join("---" for _ in fieldnames) + " |"
    lines = ["# MutantHunter Baseline Results", "", header, sep]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(k, "")) for k in fieldnames) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# mutate
# ---------------------------------------------------------------------------

def _cmd_mutate(args: argparse.Namespace) -> None:
    from .mutate import run_mutation

    # Resolve modules
    module_arg = args.module
    try:
        modules = _resolve_modules(module_arg)
    except SystemExit:
        raise

    suite = getattr(args, "suite", "human") or "human"
    split = getattr(args, "split", "A") or "A"
    jobs = args.jobs
    seed = args.seed

    for mod in modules:
        print(f"  mutate {mod.module} suite={suite} split={split} jobs={jobs} ...")
        out = run_mutation(mod, suite, split, jobs=jobs, seed=seed)
        if out is not None:
            print(f"    → {out}")


# ---------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------

def _cmd_check(args: argparse.Namespace) -> None:
    from .check import check_file
    from .registry import get_module

    mod = get_module(args.module)
    test_file = Path(args.test_file).resolve()
    repeat = getattr(args, "repeat", 3) or 3
    jobs = args.jobs

    result = check_file(mod, test_file, repeat=repeat, jobs=jobs)
    print(json.dumps(result, indent=2))


# ---------------------------------------------------------------------------
# generate (lazy import of backends.bob)
# ---------------------------------------------------------------------------

def _cmd_generate(args: argparse.Namespace) -> None:
    try:
        from .backends import bob as bob_backend  # type: ignore
    except ImportError:
        _not_implemented("generate")

    from .registry import get_module
    mod = get_module(args.module)
    suite = getattr(args, "suite", "mh") or "mh"
    max_cost = getattr(args, "max_cost", None)

    backend = bob_backend.BobBackend(max_cost=max_cost)
    work_package = {
        "module": mod.module,
        "suite": suite,
        "split_a_survivors": [],
        "rules_file": None,
        "max_cost": max_cost,
    }
    files = backend.generate_tests(work_package)
    print(f"Generated {len(files)} test file(s):")
    for f in files:
        print(f"  {f}")


# ---------------------------------------------------------------------------
# replay (lazy import)
# ---------------------------------------------------------------------------

def _cmd_replay(args: argparse.Namespace) -> None:
    try:
        from . import replay as replay_mod  # type: ignore
    except ImportError:
        _not_implemented("replay")

    set_name = getattr(args, "set", "all") or "all"
    suites_raw = getattr(args, "suite", "human,mh,b1") or "human,mh,b1"
    suites = [s.strip() for s in suites_raw.split(",")]

    results = replay_mod.replay(which=set_name, suites=suites)
    print(json.dumps(results, indent=2))


# ---------------------------------------------------------------------------
# report (lazy import)
# ---------------------------------------------------------------------------

def _cmd_report(args: argparse.Namespace) -> None:
    try:
        from . import report as report_mod  # type: ignore
    except ImportError:
        _not_implemented("report")

    from .registry import REPO_ROOT
    results_dir = REPO_ROOT / "results"
    docs_dir = REPO_ROOT / "docs"
    modules_csv = REPO_ROOT / "dataset" / "modules.csv"

    report_mod.report(
        results_dir=results_dir,
        docs_dir=docs_dir,
        modules_csv=modules_csv,
    )


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def _add_global_flags(p: argparse.ArgumentParser) -> None:
    """Add --jobs and --seed to a (sub)parser."""
    p.add_argument("--jobs", type=int, default=4, metavar="N",
                   help="Number of parallel workers (default: 4)")
    p.add_argument("--seed", type=int, default=20260925, metavar="N",
                   help="Seed for split assignment (default: 20260925)")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mutanthunter",
        description="MutantHunter — mutation testing for python-validators",
    )
    _add_global_flags(parser)

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    # baseline
    p_base = sub.add_parser("baseline", help="Compute mutation baseline")
    _add_global_flags(p_base)
    p_base.add_argument(
        "--set", dest="set", default="all",
        metavar="SET",
        help="Module set: main, extra, reference, all, or comma-separated names",
    )

    # mutate
    p_mut = sub.add_parser("mutate", help="Run mutation testing")
    _add_global_flags(p_mut)
    p_mut.add_argument("module", metavar="MODULE|SET|LIST",
                       help="Module name, set name, or comma-separated list")
    p_mut.add_argument("--suite", default="human",
                       help="Test suite: human, human+mh, human+b1 (default: human)")
    p_mut.add_argument("--split", default="A", choices=["A", "B", "all", "C"],
                       help="Mutant split: A, B, all, or C (default: A)")

    # check
    p_chk = sub.add_parser("check", help="Check a test file against survivors")
    _add_global_flags(p_chk)
    p_chk.add_argument("module", metavar="MODULE", help="Module name")
    p_chk.add_argument("--test-file", required=True, dest="test_file",
                       metavar="FILE", help="Path to the test file to check")
    p_chk.add_argument("--repeat", type=int, default=3,
                       help="Number of runs on original (default: 3)")

    # generate
    p_gen = sub.add_parser("generate", help="Generate tests using a backend")
    _add_global_flags(p_gen)
    p_gen.add_argument("module", metavar="MODULE|LIST")
    p_gen.add_argument("--suite", default="mh", choices=["mh", "b1"])
    p_gen.add_argument("--max-cost", type=float, dest="max_cost", default=None)

    # replay
    p_rep = sub.add_parser("replay", help="Historical bug replay")
    _add_global_flags(p_rep)
    p_rep.add_argument("--set", dest="set", default="all")
    p_rep.add_argument("--suite", default="human,mh,b1")

    # report
    p_rpt = sub.add_parser("report", help="Generate summary.csv, stats.md, docs/index.html")
    _add_global_flags(p_rpt)

    return parser


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    from .isolation import IsolationError, BaselineError

    parser = _build_parser()
    argv = sys.argv[1:]

    try:
        args = parser.parse_args(argv)
        dispatch = {
            "baseline": _cmd_baseline,
            "mutate": _cmd_mutate,
            "check": _cmd_check,
            "generate": _cmd_generate,
            "replay": _cmd_replay,
            "report": _cmd_report,
        }
        handler = dispatch.get(args.command)
        if handler is None:
            parser.print_help()
            sys.exit(1)
        handler(args)

    except SystemExit:
        raise
    except IsolationError as exc:
        print(f"isolation error: {exc}", file=sys.stderr)
        sys.exit(3)
    except BaselineError as exc:
        print(f"baseline error: {exc}", file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
