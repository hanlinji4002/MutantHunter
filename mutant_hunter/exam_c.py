"""Exam C — out-of-distribution mutation operators (SPEC § 7.2c).

Operators (never used while building/tuning the pipeline):
  1. bool_flip      — True ↔ False
  2. not_drop       — drop a `not` (UnaryOp with Not)
  3. str_surround   — string constant → "XX" + s + "XX"  (skips docstrings,
                      f-string parts, and data tables with > 8 entries)
  4. method_drop    — drop a no-arg .lower/.upper/.strip/.lstrip/.rstrip/
                      .casefold/.title call
  5. augassign_flip — += ↔ -=

Public API: enumerate_exam_c(source, slug) -> list[Mutant]
"""

from __future__ import annotations

import ast
import copy
import hashlib
from typing import Dict, List, Optional

from .mutate import Mutant  # canonical dataclass

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

_METHOD_DROP_NAMES = frozenset(
    ["lower", "upper", "strip", "lstrip", "rstrip", "casefold", "title"]
)

_DATA_TABLE_THRESHOLD = 8  # skip strings inside containers larger than this


# --------------------------------------------------------------------------- #
# Helpers shared with mutate.py (duplicated to keep exam_c self-contained)
# --------------------------------------------------------------------------- #

def _build_parent_map(tree: ast.AST) -> Dict[ast.AST, ast.AST]:
    parents: Dict[ast.AST, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    return parents


def _enclosing_function(node: ast.AST, parents: Dict[ast.AST, ast.AST]) -> str:
    current = parents.get(node)
    while current is not None:
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return current.name
        current = parents.get(current)
    return "<module>"


def _mutant_id(slug: str, node: ast.AST, op: str) -> str:
    line = getattr(node, "lineno", 0)
    col = getattr(node, "col_offset", 0)
    end_line = getattr(node, "end_lineno", line)
    end_col = getattr(node, "end_col_offset", col)
    return f"{slug}:{line}:{col}:{end_line}:{end_col}:{op}"


def _split_c(mutant_id: str, seed: int = 20270101) -> str:
    """Always returns 'C' — exam-C mutants form their own split."""
    return "C"


def _make(
    *,
    mid: str,
    op: str,
    node: ast.AST,
    func: str,
    orig: str,
    mutated: str,
    falsy: bool = False,
    applied_source: str,
) -> Mutant:
    return Mutant(
        id=mid,
        op=op,
        line=getattr(node, "lineno", 0),
        col=getattr(node, "col_offset", 0),
        end_line=getattr(node, "end_lineno", getattr(node, "lineno", 0)),
        end_col=getattr(node, "end_col_offset", getattr(node, "col_offset", 0)),
        function=func,
        original=orig,
        mutated=mutated,
        falsy_preserving=falsy,
        split="C",
        source=applied_source,
    )


# --------------------------------------------------------------------------- #
# Operator 1: bool_flip  (True ↔ False)
# --------------------------------------------------------------------------- #

def _enum_bool_flip(
    node: ast.Constant,
    slug: str,
    parents: Dict[ast.AST, ast.AST],
    source: str,
    tree: ast.AST,
) -> Optional[Mutant]:
    if not isinstance(node.value, bool):
        return None
    new_val = not node.value
    op = "bool_flip_true_to_false" if node.value else "bool_flip_false_to_true"
    mid = _mutant_id(slug, node, op)
    orig = ast.unparse(node)
    applied = _apply_bool_flip(source, tree, node, new_val)
    if applied is None:
        return None
    return _make(
        mid=mid, op=op, node=node,
        func=_enclosing_function(node, parents),
        orig=orig, mutated=str(new_val),
        applied_source=applied,
    )


def _apply_bool_flip(source: str, tree: ast.AST, target: ast.Constant, new_val: bool) -> Optional[str]:
    new_tree = copy.deepcopy(tree)
    for node in ast.walk(new_tree):
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, bool)
            and node.lineno == target.lineno
            and node.col_offset == target.col_offset
        ):
            node.value = new_val
            break
    try:
        result = ast.unparse(new_tree)
        ast.parse(result)
        return result
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# Operator 2: not_drop  (remove UnaryOp(Not, ...))
# --------------------------------------------------------------------------- #

def _enum_not_drop(
    node: ast.UnaryOp,
    slug: str,
    parents: Dict[ast.AST, ast.AST],
    source: str,
    tree: ast.AST,
) -> Optional[Mutant]:
    if not isinstance(node.op, ast.Not):
        return None
    op = "not_drop"
    mid = _mutant_id(slug, node, op)
    orig = ast.unparse(node)
    mut = ast.unparse(node.operand)
    applied = _apply_not_drop(source, tree, node)
    if applied is None:
        return None
    return _make(
        mid=mid, op=op, node=node,
        func=_enclosing_function(node, parents),
        orig=orig, mutated=mut,
        applied_source=applied,
    )


def _apply_not_drop(source: str, tree: ast.AST, target: ast.UnaryOp) -> Optional[str]:
    new_tree = copy.deepcopy(tree)
    parents = _build_parent_map(new_tree)
    for node in ast.walk(new_tree):
        if (
            isinstance(node, ast.UnaryOp)
            and isinstance(node.op, ast.Not)
            and node.lineno == target.lineno
            and node.col_offset == target.col_offset
        ):
            parent = parents.get(node)
            if parent is None:
                return None
            operand = copy.deepcopy(node.operand)
            ast.copy_location(operand, node)
            for field, value in ast.iter_fields(parent):
                if value is node:
                    setattr(parent, field, operand)
                elif isinstance(value, list) and node in value:
                    value[value.index(node)] = operand
            break
    try:
        result = ast.unparse(new_tree)
        ast.parse(result)
        return result
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# Operator 3: str_surround  (s → "XX" + s + "XX")
# --------------------------------------------------------------------------- #

def _is_docstring(node: ast.Constant, parents: Dict[ast.AST, ast.AST]) -> bool:
    """Return True if this Constant is a module/class/function docstring."""
    parent = parents.get(node)
    if parent is None:
        return False
    if isinstance(parent, ast.Expr):
        grandparent = parents.get(parent)
        if isinstance(grandparent, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            # Check it's the first statement
            body = grandparent.body
            if body and body[0] is parent:
                return True
    return False


def _in_large_container(node: ast.Constant, parents: Dict[ast.AST, ast.AST]) -> bool:
    """Return True if this constant is an element of a list/tuple/set/dict
    with more than _DATA_TABLE_THRESHOLD entries."""
    parent = parents.get(node)
    if isinstance(parent, (ast.List, ast.Tuple, ast.Set)):
        return len(parent.elts) > _DATA_TABLE_THRESHOLD
    if isinstance(parent, ast.Dict):
        return len(parent.keys) > _DATA_TABLE_THRESHOLD
    return False


def _enum_str_surround(
    node: ast.Constant,
    slug: str,
    parents: Dict[ast.AST, ast.AST],
    source: str,
    tree: ast.AST,
) -> Optional[Mutant]:
    if not isinstance(node.value, str):
        return None
    if _is_docstring(node, parents):
        return None
    if _in_large_container(node, parents):
        return None
    # Skip f-string parts: their parent is a JoinedStr
    parent = parents.get(node)
    if isinstance(parent, ast.JoinedStr):
        return None
    op = "str_surround"
    mid = _mutant_id(slug, node, op)
    orig = ast.unparse(node)
    mut = f'"XX" + {orig} + "XX"'
    applied = _apply_str_surround(source, tree, node)
    if applied is None:
        return None
    return _make(
        mid=mid, op=op, node=node,
        func=_enclosing_function(node, parents),
        orig=orig, mutated=mut,
        applied_source=applied,
    )


def _apply_str_surround(source: str, tree: ast.AST, target: ast.Constant) -> Optional[str]:
    new_tree = copy.deepcopy(tree)
    parents = _build_parent_map(new_tree)
    for node in ast.walk(new_tree):
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and node.lineno == target.lineno
            and node.col_offset == target.col_offset
        ):
            parent = parents.get(node)
            if parent is None:
                return None
            xx = ast.Constant(value="XX")
            ast.copy_location(xx, node)
            new_expr = ast.BinOp(
                left=ast.BinOp(left=xx, op=ast.Add(), right=copy.deepcopy(node)),
                op=ast.Add(),
                right=ast.Constant(value="XX"),
            )
            ast.copy_location(new_expr, node)
            ast.fix_missing_locations(new_expr)
            for field, value in ast.iter_fields(parent):
                if value is node:
                    setattr(parent, field, new_expr)
                elif isinstance(value, list) and node in value:
                    value[value.index(node)] = new_expr
            break
    try:
        result = ast.unparse(new_tree)
        ast.parse(result)
        return result
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# Operator 4: method_drop  (drop no-arg .lower() / .upper() / etc.)
# --------------------------------------------------------------------------- #

def _enum_method_drop(
    node: ast.Call,
    slug: str,
    parents: Dict[ast.AST, ast.AST],
    source: str,
    tree: ast.AST,
) -> Optional[Mutant]:
    if node.args or node.keywords or node.starargs if hasattr(node, "starargs") else node.args or node.keywords:
        return None
    func = node.func
    if not (isinstance(func, ast.Attribute) and func.attr in _METHOD_DROP_NAMES):
        return None
    op = f"method_drop_{func.attr}"
    mid = _mutant_id(slug, node, op)
    orig = ast.unparse(node)
    mut = ast.unparse(func.value)
    applied = _apply_method_drop(source, tree, node)
    if applied is None:
        return None
    return _make(
        mid=mid, op=op, node=node,
        func=_enclosing_function(node, parents),
        orig=orig, mutated=mut,
        applied_source=applied,
    )


def _apply_method_drop(source: str, tree: ast.AST, target: ast.Call) -> Optional[str]:
    new_tree = copy.deepcopy(tree)
    parents = _build_parent_map(new_tree)
    for node in ast.walk(new_tree):
        if (
            isinstance(node, ast.Call)
            and not node.args and not node.keywords
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in _METHOD_DROP_NAMES
            and node.lineno == target.lineno
            and node.col_offset == target.col_offset
        ):
            parent = parents.get(node)
            if parent is None:
                return None
            replacement = copy.deepcopy(node.func.value)
            ast.copy_location(replacement, node)
            for field, value in ast.iter_fields(parent):
                if value is node:
                    setattr(parent, field, replacement)
                elif isinstance(value, list) and node in value:
                    value[value.index(node)] = replacement
            break
    try:
        result = ast.unparse(new_tree)
        ast.parse(result)
        return result
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# Operator 5: augassign_flip  (+= ↔ -=)
# --------------------------------------------------------------------------- #

def _enum_augassign_flip(
    node: ast.AugAssign,
    slug: str,
    parents: Dict[ast.AST, ast.AST],
    source: str,
    tree: ast.AST,
) -> Optional[Mutant]:
    if isinstance(node.op, ast.Add):
        op = "augassign_add_to_sub"
        new_op_type = ast.Sub
    elif isinstance(node.op, ast.Sub):
        op = "augassign_sub_to_add"
        new_op_type = ast.Add
    else:
        return None
    mid = _mutant_id(slug, node, op)
    orig = ast.unparse(node)
    applied = _apply_augassign_flip(source, tree, node, new_op_type)
    if applied is None:
        return None
    new_node = copy.deepcopy(node)
    new_node.op = new_op_type()
    mut = ast.unparse(new_node)
    return _make(
        mid=mid, op=op, node=node,
        func=_enclosing_function(node, parents),
        orig=orig, mutated=mut,
        applied_source=applied,
    )


def _apply_augassign_flip(source: str, tree: ast.AST, target: ast.AugAssign, new_op_type: type) -> Optional[str]:
    new_tree = copy.deepcopy(tree)
    for node in ast.walk(new_tree):
        if (
            isinstance(node, ast.AugAssign)
            and node.lineno == target.lineno
            and node.col_offset == target.col_offset
        ):
            node.op = new_op_type()
            break
    try:
        result = ast.unparse(new_tree)
        ast.parse(result)
        return result
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def enumerate_exam_c(source: str, slug: str) -> List[Mutant]:
    """Enumerate all exam-C mutants for *source*.

    All returned mutants have split='C'.  Invalid mutations (those that
    don't compile after application) are silently omitted.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    parents = _build_parent_map(tree)
    mutants: List[Mutant] = []

    for node in ast.walk(tree):
        m: Optional[Mutant] = None
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                m = _enum_bool_flip(node, slug, parents, source, tree)
            elif isinstance(node.value, str):
                m = _enum_str_surround(node, slug, parents, source, tree)
        elif isinstance(node, ast.UnaryOp):
            m = _enum_not_drop(node, slug, parents, source, tree)
        elif isinstance(node, ast.Call):
            m = _enum_method_drop(node, slug, parents, source, tree)
        elif isinstance(node, ast.AugAssign):
            m = _enum_augassign_flip(node, slug, parents, source, tree)
        if m is not None:
            mutants.append(m)

    return mutants
