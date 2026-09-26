"""Mutate — AST mutation operators, IDs, splits, and parallel runs.

Implements all six operator families from SPEC § 5.3 and the full mutation
pipeline (enumerate → apply → run → report).

The Mutant dataclass is the canonical definition imported by track B.
"""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .isolation import (
    BaselineError,
    IsolationError,
    Workspace,
    check_baseline,
    check_isolation,
    run_all_mutants,
)
from .registry import REPO_ROOT, Module, TARGET_ROOT, suite_test_paths


# ---------------------------------------------------------------------------
# Mutant dataclass (canonical; track B imports this)
# ---------------------------------------------------------------------------

@dataclass
class Mutant:
    """Represents one mutation of a source file."""

    id: str             # "<slug>:<line>:<col>:<end_line>:<end_col>:<op>"
    op: str             # operator code, e.g. "if_negate"
    line: int           # 1-based start line
    col: int            # 0-based start column
    end_line: int       # 1-based end line
    end_col: int        # 0-based end column
    function: str       # enclosing function name or "<module>"
    original: str       # the changed fragment before mutation
    mutated: str        # the changed fragment after mutation
    falsy_preserving: bool
    split: str          # "A" or "B"
    source: str         # unparsed source of the full mutated module


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------

def _build_parent_map(tree: ast.AST) -> Dict[ast.AST, ast.AST]:
    """Build a child→parent mapping for the entire AST."""
    parents: Dict[ast.AST, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    return parents


def _enclosing_function(node: ast.AST, parents: Dict[ast.AST, ast.AST]) -> str:
    """Return the name of the innermost enclosing function, or '<module>'."""
    current = parents.get(node)
    while current is not None:
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return current.name
        current = parents.get(current)
    return "<module>"


# ---------------------------------------------------------------------------
# Comparator name mapping
# ---------------------------------------------------------------------------

_CMP_PAIRS: List[Tuple[type, type, str, str]] = [
    (ast.Lt,    ast.LtE,   "lt",    "lte"),
    (ast.LtE,   ast.Lt,    "lte",   "lt"),
    (ast.Gt,    ast.GtE,   "gt",    "gte"),
    (ast.GtE,   ast.Gt,    "gte",   "gt"),
    (ast.Eq,    ast.NotEq, "eq",    "noteq"),
    (ast.NotEq, ast.Eq,    "noteq", "eq"),
    (ast.In,    ast.NotIn, "in",    "notin"),
    (ast.NotIn, ast.In,    "notin", "in"),
    (ast.Is,    ast.IsNot, "is",    "isnot"),
    (ast.IsNot, ast.Is,    "isnot", "is"),
]

_CMP_FROM: Dict[type, Tuple[type, str, str]] = {
    from_type: (to_type, from_name, to_name)
    for from_type, to_type, from_name, to_name in _CMP_PAIRS
}

# BinOp pairs: (from_type, to_type, from_name, to_name)
_BIN_PAIRS: List[Tuple[type, type, str, str]] = [
    (ast.Add,      ast.Sub,      "add",   "sub"),
    (ast.Sub,      ast.Add,      "sub",   "add"),
    (ast.Mult,     ast.FloorDiv, "mult",  "floordiv"),
    (ast.FloorDiv, ast.Mult,     "floordiv", "mult"),
    (ast.Div,      ast.Mult,     "div",   "mult"),
    (ast.Mod,      ast.Mult,     "mod",   "mult"),
]

_BIN_FROM: Dict[type, Tuple[type, str, str]] = {
    from_type: (to_type, from_name, to_name)
    for from_type, to_type, from_name, to_name in _BIN_PAIRS
}


# ---------------------------------------------------------------------------
# Mutant ID and split
# ---------------------------------------------------------------------------

def _mutant_id(
    slug: str,
    node: ast.AST,
    op: str,
) -> str:
    """Build the canonical mutant ID string."""
    line = getattr(node, "lineno", 0)
    col = getattr(node, "col_offset", 0)
    end_line = getattr(node, "end_lineno", line)
    end_col = getattr(node, "end_col_offset", col)
    return f"{slug}:{line}:{col}:{end_line}:{end_col}:{op}"


def split_assign(mutant_id: str, seed: int = 20260925) -> str:
    """Return 'A' or 'B' for the given mutant ID.

    B if the first byte of sha256("<seed>:<mutant_id>") is odd, else A.
    """
    data = f"{seed}:{mutant_id}".encode()
    first_byte = hashlib.sha256(data).digest()[0]
    return "B" if first_byte & 1 else "A"


# ---------------------------------------------------------------------------
# Operator enumeration
# ---------------------------------------------------------------------------

def _enumerate_cmp(
    node: ast.Compare,
    slug: str,
    parents: Dict[ast.AST, ast.AST],
    seed: int,
) -> List[Mutant]:
    """Enumerate compare-operator mutations."""
    mutants = []
    is_chained = len(node.ops) > 1

    for i, op in enumerate(node.ops):
        op_type = type(op)
        if op_type not in _CMP_FROM:
            continue
        to_type, from_name, to_name = _CMP_FROM[op_type]

        if is_chained:
            op_code = f"cmp_{from_name}_to_{to_name}#{i + 1}"
        else:
            op_code = f"cmp_{from_name}_to_{to_name}"

        mid = _mutant_id(slug, node, op_code)

        # Build mutated tree
        new_tree = copy.deepcopy(node)
        new_tree.ops[i] = to_type()
        orig_frag = ast.unparse(node)
        try:
            mut_frag = ast.unparse(new_tree)
        except Exception:
            continue

        func_name = _enclosing_function(node, parents)
        mutants.append(
            Mutant(
                id=mid,
                op=op_code,
                line=node.lineno,
                col=node.col_offset,
                end_line=node.end_lineno,
                end_col=node.end_col_offset,
                function=func_name,
                original=orig_frag,
                mutated=mut_frag,
                falsy_preserving=False,
                split=split_assign(mid, seed),
                source="",  # filled in later
            )
        )
    return mutants


def _enumerate_bin(
    node: ast.BinOp,
    slug: str,
    parents: Dict[ast.AST, ast.AST],
    seed: int,
) -> List[Mutant]:
    """Enumerate binary-operator mutations."""
    op_type = type(node.op)
    if op_type not in _BIN_FROM:
        return []
    to_type, from_name, to_name = _BIN_FROM[op_type]
    op_code = f"bin_{from_name}_to_{to_name}"
    mid = _mutant_id(slug, node, op_code)

    new_tree = copy.deepcopy(node)
    new_tree.op = to_type()
    orig_frag = ast.unparse(node)
    try:
        mut_frag = ast.unparse(new_tree)
    except Exception:
        return []

    func_name = _enclosing_function(node, parents)
    return [
        Mutant(
            id=mid,
            op=op_code,
            line=node.lineno,
            col=node.col_offset,
            end_line=node.end_lineno,
            end_col=node.end_col_offset,
            function=func_name,
            original=orig_frag,
            mutated=mut_frag,
            falsy_preserving=False,
            split=split_assign(mid, seed),
            source="",
        )
    ]


def _enumerate_bool(
    node: ast.BoolOp,
    slug: str,
    parents: Dict[ast.AST, ast.AST],
    seed: int,
) -> List[Mutant]:
    """Enumerate bool-operator mutations (And↔Or)."""
    if isinstance(node.op, ast.And):
        op_code = "bool_and_to_or"
        new_op = ast.Or()
    elif isinstance(node.op, ast.Or):
        op_code = "bool_or_to_and"
        new_op = ast.And()
    else:
        return []

    mid = _mutant_id(slug, node, op_code)
    new_tree = copy.deepcopy(node)
    new_tree.op = new_op
    orig_frag = ast.unparse(node)
    try:
        mut_frag = ast.unparse(new_tree)
    except Exception:
        return []

    func_name = _enclosing_function(node, parents)
    return [
        Mutant(
            id=mid,
            op=op_code,
            line=node.lineno,
            col=node.col_offset,
            end_line=node.end_lineno,
            end_col=node.end_col_offset,
            function=func_name,
            original=orig_frag,
            mutated=mut_frag,
            falsy_preserving=False,
            split=split_assign(mid, seed),
            source="",
        )
    ]


def _enumerate_if_negate(
    node: ast.If,
    slug: str,
    parents: Dict[ast.AST, ast.AST],
    seed: int,
) -> List[Mutant]:
    """Enumerate if-negate mutations."""
    op_code = "if_negate"
    mid = _mutant_id(slug, node, op_code)
    orig_frag = ast.unparse(node.test)
    new_test = ast.UnaryOp(op=ast.Not(), operand=copy.deepcopy(node.test))
    ast.copy_location(new_test, node.test)
    try:
        mut_frag = ast.unparse(new_test)
    except Exception:
        return []

    func_name = _enclosing_function(node, parents)
    return [
        Mutant(
            id=mid,
            op=op_code,
            line=node.lineno,
            col=node.col_offset,
            end_line=node.end_lineno,
            end_col=node.end_col_offset,
            function=func_name,
            original=orig_frag,
            mutated=mut_frag,
            falsy_preserving=False,
            split=split_assign(mid, seed),
            source="",
        )
    ]


def _enumerate_int_plus_one(
    node: ast.Constant,
    slug: str,
    parents: Dict[ast.AST, ast.AST],
    seed: int,
) -> List[Mutant]:
    """Enumerate int-plus-one mutations."""
    # Must be an int but not a bool
    if not (type(node.value) is int and not isinstance(node.value, bool)):
        return []
    op_code = "int_plus_one"
    mid = _mutant_id(slug, node, op_code)
    orig_frag = ast.unparse(node)
    new_node = copy.deepcopy(node)
    new_node.value = node.value + 1
    try:
        mut_frag = ast.unparse(new_node)
    except Exception:
        return []

    func_name = _enclosing_function(node, parents)
    return [
        Mutant(
            id=mid,
            op=op_code,
            line=node.lineno,
            col=node.col_offset,
            end_line=node.end_lineno,
            end_col=node.end_col_offset,
            function=func_name,
            original=orig_frag,
            mutated=mut_frag,
            falsy_preserving=False,
            split=split_assign(mid, seed),
            source="",
        )
    ]


def _enumerate_return_none(
    node: ast.Return,
    slug: str,
    parents: Dict[ast.AST, ast.AST],
    seed: int,
) -> List[Mutant]:
    """Enumerate return-none mutations."""
    if node.value is None:
        return []
    op_code = "return_none"
    mid = _mutant_id(slug, node, op_code)
    orig_frag = ast.unparse(node.value)

    # Check falsy_preserving: original is `return False`
    falsy = orig_frag == "False"

    func_name = _enclosing_function(node, parents)
    return [
        Mutant(
            id=mid,
            op=op_code,
            line=node.lineno,
            col=node.col_offset,
            end_line=node.end_lineno,
            end_col=node.end_col_offset,
            function=func_name,
            original=orig_frag,
            mutated="None",
            falsy_preserving=falsy,
            split=split_assign(mid, seed),
            source="",
        )
    ]


# ---------------------------------------------------------------------------
# Full enumeration
# ---------------------------------------------------------------------------

def enumerate_mutants(source_path: Path, slug: str, seed: int = 20260925) -> List[Mutant]:
    """Enumerate all valid mutants for a source file in ast.walk order.

    Returns mutants whose applied source compiles; invalid mutants are omitted.
    """
    source = source_path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    parents = _build_parent_map(tree)
    mutants: List[Mutant] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            mutants.extend(_enumerate_cmp(node, slug, parents, seed))
        elif isinstance(node, ast.BinOp):
            mutants.extend(_enumerate_bin(node, slug, parents, seed))
        elif isinstance(node, ast.BoolOp):
            mutants.extend(_enumerate_bool(node, slug, parents, seed))
        elif isinstance(node, ast.If):
            mutants.extend(_enumerate_if_negate(node, slug, parents, seed))
        elif isinstance(node, ast.Constant):
            mutants.extend(_enumerate_int_plus_one(node, slug, parents, seed))
        elif isinstance(node, ast.Return):
            mutants.extend(_enumerate_return_none(node, slug, parents, seed))

    # Apply each mutant and fill in .source; discard those that don't compile
    valid: List[Mutant] = []
    for m in mutants:
        applied = _apply_mutant(source, tree, m)
        if applied is None:
            continue
        m.source = applied
        valid.append(m)

    return valid


def _apply_mutant(source: str, tree: ast.AST, mutant: Mutant) -> Optional[str]:
    """Apply a mutant to a fresh copy of the AST and return the unparsed source.

    Returns None if the mutation produces invalid syntax.
    """
    new_tree = copy.deepcopy(tree)
    parents = _build_parent_map(new_tree)

    # Find the target node by walking and matching id
    target = _find_node_for_mutant(new_tree, mutant)
    if target is None:
        return None

    _patch_node(target, mutant, parents)

    try:
        result = ast.unparse(new_tree)
        ast.parse(result)  # validate
        return result
    except Exception:
        return None


def _find_node_for_mutant(tree: ast.AST, mutant: Mutant) -> Optional[ast.AST]:
    """Find the AST node corresponding to this mutant by position."""
    for node in ast.walk(tree):
        if (
            getattr(node, "lineno", None) == mutant.line
            and getattr(node, "col_offset", None) == mutant.col
            and getattr(node, "end_lineno", None) == mutant.end_line
            and getattr(node, "end_col_offset", None) == mutant.end_col
        ):
            # Verify node type matches operator
            if _node_matches_op(node, mutant.op):
                return node
    return None


def _node_matches_op(node: ast.AST, op: str) -> bool:
    """Check if an AST node matches the operator code."""
    if op.startswith("cmp_"):
        return isinstance(node, ast.Compare)
    if op.startswith("bin_"):
        return isinstance(node, ast.BinOp)
    if op.startswith("bool_"):
        return isinstance(node, ast.BoolOp)
    if op == "if_negate":
        return isinstance(node, ast.If)
    if op == "int_plus_one":
        return isinstance(node, ast.Constant)
    if op == "return_none":
        return isinstance(node, ast.Return)
    return False


def _patch_node(node: ast.AST, mutant: Mutant, parents: Dict[ast.AST, ast.AST]) -> None:
    """Mutate the node in-place according to the operator."""
    op = mutant.op

    if op.startswith("cmp_"):
        assert isinstance(node, ast.Compare)
        # Extract index from chained ops
        if "#" in op:
            base_op = op.rsplit("#", 1)[0]
            idx = int(op.rsplit("#", 1)[1]) - 1
        else:
            base_op = op
            idx = 0
        # Parse from/to from op code: cmp_<from>_to_<to>
        parts = base_op[4:].split("_to_")
        to_name = parts[1]
        new_op = _cmp_name_to_node(to_name)
        if new_op is not None and idx < len(node.ops):
            node.ops[idx] = new_op

    elif op.startswith("bin_"):
        assert isinstance(node, ast.BinOp)
        parts = op[4:].split("_to_")
        to_name = parts[1]
        new_op = _bin_name_to_node(to_name)
        if new_op is not None:
            node.op = new_op

    elif op == "bool_and_to_or":
        assert isinstance(node, ast.BoolOp)
        node.op = ast.Or()

    elif op == "bool_or_to_and":
        assert isinstance(node, ast.BoolOp)
        node.op = ast.And()

    elif op == "if_negate":
        assert isinstance(node, ast.If)
        new_test = ast.UnaryOp(op=ast.Not(), operand=copy.deepcopy(node.test))
        ast.copy_location(new_test, node.test)
        node.test = new_test

    elif op == "int_plus_one":
        assert isinstance(node, ast.Constant)
        node.value = node.value + 1

    elif op == "return_none":
        assert isinstance(node, ast.Return)
        node.value = ast.Constant(value=None)


def _cmp_name_to_node(name: str) -> Optional[ast.cmpop]:
    mapping = {
        "lt": ast.Lt(), "lte": ast.LtE(),
        "gt": ast.Gt(), "gte": ast.GtE(),
        "eq": ast.Eq(), "noteq": ast.NotEq(),
        "in": ast.In(), "notin": ast.NotIn(),
        "is": ast.Is(), "isnot": ast.IsNot(),
    }
    return mapping.get(name)


def _bin_name_to_node(name: str) -> Optional[ast.operator]:
    mapping = {
        "add": ast.Add(), "sub": ast.Sub(),
        "mult": ast.Mult(), "floordiv": ast.FloorDiv(),
        "div": ast.Div(), "mod": ast.Mod(),
    }
    return mapping.get(name)


# ---------------------------------------------------------------------------
# Equivalent records writer
# ---------------------------------------------------------------------------

def _write_equivalent_records(slug: str, mutants: List[Mutant]) -> None:
    """Write falsy_preserving entries to results/equivalent/<slug>.json."""
    falsy = [m for m in mutants if m.falsy_preserving]
    if not falsy:
        return

    equiv_dir = REPO_ROOT / "results" / "equivalent"
    equiv_dir.mkdir(parents=True, exist_ok=True)
    equiv_path = equiv_dir / f"{slug}.json"

    records = []
    if equiv_path.exists():
        try:
            records = json.loads(equiv_path.read_text(encoding="utf-8"))
        except Exception:
            records = []

    existing_ids = {r["id"] for r in records}
    for m in falsy:
        if m.id not in existing_ids:
            records.append({
                "id": m.id,
                "kind": "falsy_preserving",
                "reason": "return_none on return False; validators treats falsy as ValidationError",
                "conditional_on": None,
            })

    equiv_path.write_text(json.dumps(records, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Run mutation pipeline
# ---------------------------------------------------------------------------

def run_mutation(
    module: Module,
    suite: str,
    split: str,
    jobs: int = 4,
    seed: int = 20260925,
    skip_baseline_check: bool = False,
) -> Optional[Path]:
    """Run the full mutation pipeline for one module.

    When split is "A" or "B", writes a JSON file and returns its path.
    When split is "all", prints counts only and returns None — no per-mutant
    file is written (hold-out discipline: split-B survivors must not be
    persisted on disk while test generation is active).

    Args:
        module: The Module to mutate.
        suite: e.g. "human", "human+mh".
        split: "A", "B", or "all".
        jobs: Number of parallel workers.
        seed: Seed for split assignment.
        skip_baseline_check: If True, skip the baseline check (for baseline cmd).

    Returns:
        Path to the written JSON file, or None when split == "all".
    """
    if split == "C":
        # Lazy import exam_c
        try:
            from mutant_hunter import exam_c  # type: ignore
            all_mutants = exam_c.enumerate_exam_c(
                module.source_path.read_text(encoding="utf-8"),
                module.slug,
            )
        except ImportError:
            print("not implemented yet")
            raise SystemExit(1)
    else:
        all_mutants = enumerate_mutants(module.source_path, module.slug, seed)

    # Auto-write falsy_preserving records
    _write_equivalent_records(module.slug, all_mutants)

    # Filter by split
    if split == "all":
        selected = all_mutants
    else:
        selected = [m for m in all_mutants if m.split == split]

    suite_paths = suite_test_paths(module, suite)
    start_time = time.time()

    if not skip_baseline_check:
        with Workspace() as ws:
            check_isolation(ws, module)
            check_baseline(ws, module, suite_paths)

    # Run mutants
    mutant_inputs = [(i, m.source) for i, m in enumerate(selected)]
    statuses = run_all_mutants(
        mutant_inputs,
        module.source_path,
        suite_paths,
        jobs=jobs,
        timeout=60,
    )

    elapsed = time.time() - start_time

    # Assemble results
    results_list = []
    survivors_list = []
    killed_count = 0
    invalid_count = 0  # already excluded (apply_mutant returns None for invalids)
    falsy_count = sum(1 for m in selected if m.falsy_preserving)

    for m, status in zip(selected, statuses):
        results_list.append({"id": m.id, "status": status})
        if status == "survived":
            survivors_list.append({
                "id": m.id,
                "op": m.op,
                "line": m.line,
                "function": m.function,
                "original": m.original,
                "mutated": m.mutated,
                "falsy_preserving": m.falsy_preserving,
                "split": m.split,
            })
        else:
            killed_count += 1

    total = len(selected)
    denominator = total - invalid_count
    score = round(killed_count / denominator, 3) if denominator > 0 else 0.0
    adj_denom = denominator - falsy_count
    adj_score = round(killed_count / adj_denom, 3) if adj_denom > 0 else 0.0

    # --split all: print counts only, write NO file (hold-out discipline)
    if split == "all":
        print(
            f"  {module.module} split=all: "
            f"mutants={total} killed={killed_count} survived={total - killed_count} "
            f"score={score:.3f} adj={adj_score:.3f} "
            f"(no file written — split-B survivors not persisted)"
        )
        return None

    payload = {
        "module": module.module,
        "slug": module.slug,
        "suite": suite,
        "split": split,
        "seed": seed,
        "mutants": total,
        "killed": killed_count,
        "survived": total - killed_count,
        "invalid": invalid_count,
        "falsy_preserving": falsy_count,
        "score": score,
        "adjusted_score": adj_score,
        "seconds": round(elapsed, 1),
        "results": results_list,
        "survivors": survivors_list,
    }

    out_dir = REPO_ROOT / "results" / "mutants"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{module.slug}__{suite}__{split}.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return out_path


# ---------------------------------------------------------------------------
# Baseline: run all mutants in-memory and return counts only
# ---------------------------------------------------------------------------

def run_baseline(
    module: Module,
    jobs: int = 4,
    seed: int = 20260925,
) -> Dict:
    """Run all mutants (all splits) and return aggregate counts only.

    Does NOT write per-mutant JSON. Does NOT reveal split-B survivors.

    Returns:
        Dict with keys: module, set, suite, split, mutants, killed, score,
        ref_mutants, ref_killed, ref_match.
    """
    all_mutants = enumerate_mutants(module.source_path, module.slug, seed)
    _write_equivalent_records(module.slug, all_mutants)

    suite = "human"
    suite_paths = suite_test_paths(module, suite)

    # Baseline check
    with Workspace() as ws:
        check_isolation(ws, module)
        check_baseline(ws, module, suite_paths)

    mutant_inputs = [(i, m.source) for i, m in enumerate(all_mutants)]
    statuses = run_all_mutants(
        mutant_inputs,
        module.source_path,
        suite_paths,
        jobs=jobs,
        timeout=60,
    )

    total = len(all_mutants)
    killed = sum(1 for s in statuses if s == "killed")
    score = round(killed / total, 3) if total > 0 else 0.0

    ref_match = (
        "yes"
        if total == module.ref_mutants and killed == module.ref_killed
        else "no"
    )

    return {
        "module": module.module,
        "set": module.set,
        "suite": suite,
        "split": "all",
        "mutants": total,
        "killed": killed,
        "score": score,
        "ref_mutants": module.ref_mutants,
        "ref_killed": module.ref_killed,
        "ref_match": ref_match,
    }
