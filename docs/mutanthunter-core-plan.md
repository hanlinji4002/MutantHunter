# MutantHunter Core Implementation Plan (ST1–ST8 + M1 Verification)

> Scope: implement and verify M1 of MutantHunter.
> This plan covers Sub-Tasks ST1–ST8 of `docs/track-a-plan.md` and satisfies the M1
> acceptance row of `docs/SPEC.md` § 11:
> "`baseline --set all` gives `ref_match = yes` for all 24 modules; `--jobs 1` and
> `--jobs 8` give identical results on `url`; unit tests pass, including one each
> for exit codes 2 and 3 and one for unique IDs on nested expressions."
>
> **Out of scope**: `report.py`, `stats.py`, `replay.py`, `exam_c.py`, `backends/bob.py`,
> Bob skill/rules (ST9), mutation runs (ST10). Those belong to Track B or later milestones.

---

## Repository State at Plan Time

- `targets/validators/` — python-validators @ 70de324; `.venv/` already exists with
  Python 3.12.6 at `targets/validators/.venv/bin/python`.
- `dataset/modules.csv` — 24 rows; `ref_mutants` / `ref_killed` are the ground truth.
- No `mutant_hunter/`, no `tests/`, no `results/` yet.

---

## Top-Level Architecture

```
mutant_hunter/
├── __init__.py          (empty)
├── registry.py          (ST2)  — dataset/modules.csv reader
├── isolation.py         (ST3)  — workspace, pytest runner, three guards
├── mutate.py            (ST4)  — AST operators, IDs, splits, parallel runs
├── check.py             (ST5)  — single test-file checker
├── cli.py               (ST6)  — argparse entry point, lazy imports
└── backends/
    ├── __init__.py      (empty)
    └── base.py          (ST7)  — AgentBackend ABC, record_cost

tests/
├── conftest.py
├── test_registry.py
├── test_mutate.py
├── test_isolation.py
├── test_baseline.py     (integration — runs real baseline)
└── test_jobs.py         (integration — jobs 1 vs 4 on url)

pyproject.toml           (ST1)  — console script, zero runtime deps
results/                 (created at runtime)
```

---

## Sub-Task ST1 — `pyproject.toml` and package scaffold

**Status:** [ ] pending

**Intent**
Make `mutant_hunter` pip-installable and register the `mutanthunter` console script.
This must be done first; everything else depends on being able to `import mutant_hunter`.

**Expected Outcomes**
- `uv pip install -e .` (inside `targets/validators/.venv`) succeeds.
- `mutanthunter --help` prints usage.
- `mutant_hunter/__init__.py` and `mutant_hunter/backends/__init__.py` exist.

**Todo List**
1. Create `pyproject.toml` at repo root:
   - `[build-system]` using setuptools.
   - `[project]`: name `mutant-hunter`, requires-python `>=3.9`, no runtime deps.
   - `[project.scripts]`: `mutanthunter = "mutant_hunter.cli:main"`.
   - `[tool.setuptools.packages.find]` to discover `mutant_hunter`.
2. Create `mutant_hunter/__init__.py` (empty).
3. Create `mutant_hunter/backends/__init__.py` (empty).
4. Install: `cd <repo root> && uv pip install -e . --python targets/validators/.venv/bin/python`.
5. Smoke-test: `targets/validators/.venv/bin/mutanthunter --help`.

**Relevant Context**
- `targets/validators/pyproject.toml` for field names and style.
- The installed package must be importable from within `targets/validators/.venv`.
- Later, `isolation.py` will run with `PYTHONPATH=<copy>/src` to override the editable
  install for the validators package — but `mutant_hunter` itself is imported normally.

---

## Sub-Task ST2 — `mutant_hunter/registry.py`

**Status:** [ ] pending

**Intent**
Single source of truth: parse `dataset/modules.csv`, resolve paths relative to the
repo root (never `os.getcwd()`), expose `Module` dataclass and suite-path logic.

**Expected Outcomes**
- `_repo_root()` walks up from `__file__` until it finds a dir containing `dataset/modules.csv`.
- `Module` dataclass fields: `module`, `slug`, `source_path`, `test_path`, `set`,
  `specs`, `ref_mutants`, `ref_killed`. Paths are absolute `Path` objects.
- `all_modules()` → all 24 rows.
- `modules_by_set("main"|"extra"|"reference"|"all")` → filtered list.
- `get_module(name)` → single Module or raises `KeyError`.
- `suite_test_paths(module, suite, target_root)`:
  - `human` → `[target_root / module.test_path]`
  - `human+mh` → above + `target_root / "tests/mh/<slug>/"` (warn if absent/empty)
  - `human+b1` → above + `target_root / "tests/b1/<slug>/"` (warn if absent/empty)
- Module-level constants: `REPO_ROOT`, `TARGET_ROOT`, `VENV_PYTHON`.

**Todo List**
1. Write `_repo_root()` helper using `Path(__file__).resolve().parents` iteration.
2. Define `Module` dataclass with all fields; parse CSV using `csv.DictReader`.
3. Build `_modules: list[Module]` at import time from CSV.
4. Implement `all_modules()`, `modules_by_set()`, `get_module()`.
5. Implement `suite_test_paths()` with the warning for missing/empty extra dirs.
6. Expose `REPO_ROOT`, `TARGET_ROOT = REPO_ROOT / "targets/validators"`,
   `VENV_PYTHON = TARGET_ROOT / ".venv/bin/python"`.

**Relevant Context**
- `dataset/modules.csv` header: `module,source_path,test_path,set,specs,ref_line_branch_cov,ref_mutants,ref_killed,ref_mutation_score`
- Slugs: `module.replace("/", "__")`.
- `source_path` and `test_path` are relative to `targets/validators/`.
- 24 modules total (10 main + 2 extra + 12 reference).

---

## Sub-Task ST3 — `mutant_hunter/isolation.py`

**Status:** [ ] pending

**Intent**
Guard against the three silent failures in SPEC § 5.2 and provide a
parallel-safe workspace for mutation runs.

**The Three Failures and Remedies**

| Failure | Symptom | Remedy |
|---|---|---|
| Editable install | Tests still run against original | `PYTHONPATH=<copy>/src`; verify import path with `python -c "import validators; print(validators.__file__)"` |
| Red baseline | Every mutant counts as killed | Run suite on original AND `ast.unparse(original)`; exit 2 on failure |
| Stale bytecode | Old `.pyc` loaded for mutant | `PYTHONDONTWRITEBYTECODE=1`; never copy `__pycache__` |

**Expected Outcomes**
- `Workspace` context manager: `tempfile.mkdtemp`, copies `src/` and `tests/`
  (via `shutil.copytree(ignore=shutil.ignore_patterns("__pycache__"))`), sets env.
- `run_pytest(workspace, suite_paths, timeout=60)` → `"survived" | "killed"`.
  Command: `<venv_python> -m pytest -x -q -p no:cacheprovider <paths>`.
  Suite paths are rebased to the workspace copy.
- `check_isolation(workspace, module)`: runs the import-path check; raises
  `IsolationError` (exit 3) if path is not inside workspace.
- `check_baseline(workspace, module, suite_paths)`: runs suite on original,
  then on ast-unparse round-trip; raises `BaselineError` (exit 2) on failure.
- `run_all_mutants(mutants, suite_paths, jobs, workspace_factory)` using
  `concurrent.futures.ProcessPoolExecutor`; results returned in deterministic
  (original enumeration) order regardless of completion order.
- Kills-none check: if ≥ 5 mutants ran and none killed, raise `IsolationError`.

**Todo List**
1. Define `IsolationError(RuntimeError)` and `BaselineError(RuntimeError)`.
2. Implement `Workspace` context manager.
3. Implement `run_pytest()`.
4. Implement `check_isolation()`.
5. Implement `check_baseline()` — both passes (original + ast-unparse).
6. Implement `run_all_mutants()` with `ProcessPoolExecutor`; each worker receives
   its own workspace (not shared state).
7. Add kills-none guard at the end of `run_all_mutants`.

**Relevant Context**
- Each worker needs its own temp copy; workers must not share a workspace.
- `VENV_PYTHON` from `registry.py` is the interpreter.
- Suite paths passed to the subprocess must point inside the copy, not the original.
- The `ast.unparse` round-trip catches baseline failures caused by unparsing producing
  slightly different but semantically equivalent code.

---

## Sub-Task ST4 — `mutant_hunter/mutate.py`

**Status:** [ ] pending

**Intent**
Enumerate all mutants deterministically using AST-walk order, assign stable IDs
(including end positions), compute A/B splits, and write the run JSON.

**Operators (SPEC § 5.3)**

| Op code | Node | Change |
|---|---|---|
| `cmp_<a>_to_<b>` / `#i` suffix | `ast.Compare` | flip each comparator pair |
| `bin_<a>_to_<b>` | `ast.BinOp` | `+→-`, `-→+`, `*→//`, `//→*`, `/→*`, `%→*` |
| `bool_and_to_or` / `bool_or_to_and` | `ast.BoolOp` | swap |
| `if_negate` | `ast.If` | `test → not (test)` |
| `int_plus_one` | `ast.Constant`, int not bool | `n → n+1` |
| `return_none` | `ast.Return` with value | `value → None` |

**Expected Outcomes**
- `Mutant` dataclass: `id, op, line, col, end_line, end_col, function, original,
  mutated, falsy_preserving, split, source`.
- Mutant ID: `<slug>:<line>:<col>:<end_line>:<end_col>:<op>` (end positions
  disambiguate nested expressions).
- Split: `B` if `sha256(f"20260925:{mutant_id}".encode())[0] & 1 == 1`, else `A`.
- `falsy_preserving`: `return_none` where original is `return False`.
- `falsy_preserving` entries auto-logged to `results/equivalent/<slug>.json`.
- `run_mutation(module, suite, split, jobs, seed)` writes
  `results/mutants/<slug>__<suite>__<split>.json` per SPEC § 5.6.
- `--split C` lazy-imports `exam_c.enumerate_exam_c`; stubs + exits 1 if absent.
- `ref_mutants` count matches CSV for all 24 modules (verified by `baseline`).

**Todo List**
1. Define `Mutant` dataclass (canonical; track B imports this type).
2. Implement `_enclosing_function(node, tree)` — walks parents to find enclosing
   `FunctionDef` / `AsyncFunctionDef`, or returns `"<module>"`.
3. Implement AST visitor (`ast.walk` order) for each of the six operator families.
   - `cmp`: iterate `node.ops`; each pair yields one mutant with `#i` if chained.
   - `bin`: map op type to name; emit only pairs listed in spec.
   - `bool`: `And→Or`, `Or→And`.
   - `if_negate`: wrap test in `ast.UnaryOp(ast.Not(), ...)`.
   - `int_plus_one`: `Constant` where `type(value) is int and not isinstance(value, bool)`.
   - `return_none`: `Return` where value is not `None`; set `falsy_preserving` if `ast.unparse(node.value) == "False"`.
4. Implement `mutant_id(slug, node, op, op_index=None)`.
5. Implement `split_assign(mutant_id, seed=20260925)`.
6. Implement `enumerate_mutants(source_path, slug)`.
7. Implement `apply_mutant(tree, mutant)` → mutated source string (deep copy + unparse).
8. Validate compiled: skip mutants whose applied source does not compile.
9. Implement `run_mutation(module, suite, split, jobs, seed)`.
10. Implement JSON writer per SPEC § 5.6.
11. Write `falsy_preserving` entries to `results/equivalent/<slug>.json`.
12. Wire `--split C` stub.

**Relevant Context**
- `ast.walk` yields nodes in breadth-first order — must be consistent across calls.
- IDs include `end_line` and `end_col_offset` from the AST node.
- Exam-C operators (`flip_bool`, `drop_not`, etc.) must NOT appear here.
- Score: `killed / (total - invalid)`. Adjusted: `killed / (total - invalid - falsy_preserving)`.

---

## Sub-Task ST5 — `mutant_hunter/check.py`

**Status:** [ ] pending

**Intent**
Allow agents to verify a single test file: confirm it passes on the original,
detect flakiness, and score it against split-A human survivors.

**Expected Outcomes**
- `check_file(module, test_file, repeat=3)` → dict matching SPEC § 5.6 check schema.
- Loads split-A survivors from `results/mutants/<slug>__human__A.json`.
- `passes_on_original`: all runs pass (no collection errors, no test failures).
- `flaky`: any test that passes on some runs but not others.
- `kills` / `not_killed`: split-A survivor IDs.
- `failing_tests_on_original`: full pytest node IDs (including parametrize brackets/spaces).
- A failing test is never deleted or hidden; it is reported.

**Todo List**
1. Implement `check_file(module, test_file, repeat=3)`:
   a. Load split-A survivors from `results/mutants/<slug>__human__A.json`.
   b. Create a `Workspace`; run `test_file` alone `repeat` times; detect flakiness by
      tracking per-test pass/fail across runs (use `--tb=no -v` for node IDs).
   c. For each survivor, run `test_file` in a mutant workspace; record kills.
   d. Return the SPEC § 5.6 dict.
2. Handle missing JSON gracefully (file not found → `survivors_checked = 0`).

**Relevant Context**
- Relies on `isolation.Workspace` and `run_pytest`.
- `failing_tests_on_original` requires parsing pytest output for full node IDs.
- SPEC § 5.6 check output schema (see `docs/track-a-plan.md` Track B contracts).

---

## Sub-Task ST6 — `mutant_hunter/cli.py`

**Status:** [ ] pending

**Intent**
Wire all six subcommands behind a single `mutanthunter` entry point. Track B's
four modules are imported lazily so the two tracks can develop independently.

**Expected Outcomes**
- `mutanthunter --help` lists `baseline`, `mutate`, `check`, `generate`, `replay`, `report`.
- Global `--jobs N` and `--seed N` accepted before or after the subcommand.
- `baseline [--set main|extra|reference|all|<list>]`:
  - Runs human-suite mutation for each module in the set.
  - Writes `results/baseline.csv` and `results/baseline.md` with **counts only**.
  - Columns: `module, set, suite, split, mutants, killed, score, ref_mutants,
    ref_killed, ref_match`.
  - `ref_match` is `yes` if `mutants == ref_mutants and killed == ref_killed`.
- `mutate <module|set|list> [--suite S] [--split A|B|all|C]` — default split A.
- `check <module> --test-file F [--repeat N]` — wraps `check.check_file`.
- `generate` — lazy-imports `backends.bob`; prints "not implemented yet" + exits 1 if absent.
- `replay` — lazy-imports `replay`; prints "not implemented yet" + exits 1 if absent.
- `report` — lazy-imports `report`; prints "not implemented yet" + exits 1 if absent.
- Exit codes: 0 ok, 1 error/not-implemented, 2 `BaselineError`, 3 `IsolationError`.

**Todo List**
1. Create `cli.py` with `argparse`; parent parser with `--jobs` (default 4) and
   `--seed` (default 20260925).
2. Implement `baseline` subcommand handler.
3. Implement `mutate` subcommand handler.
4. Implement `check` subcommand handler.
5. Implement `generate` stub with lazy import.
6. Implement `replay` stub with lazy import.
7. Implement `report` stub with lazy import.
8. Add top-level try/except that maps `IsolationError` → sys.exit(3),
   `BaselineError` → sys.exit(2), all other exceptions → print + sys.exit(1).

**Relevant Context**
- `baseline` must write counts only — no survivor lists, no split info beyond split label.
- `mutate --split all` runs both A and B; writes two JSON files.
- Lazy-import pattern: `try: from mutant_hunter import report; report.report(...)
  except ImportError: print("not implemented yet"); sys.exit(1)`.

---

## Sub-Task ST7 — `mutant_hunter/backends/base.py`

**Status:** [ ] pending

**Intent**
Define the `AgentBackend` interface and the shared cost-logging helper. Track B's
`bob.py` subclasses `AgentBackend`; `record_cost` is called by any backend.

**Expected Outcomes**
- `AgentBackend` ABC with `generate_tests(work_package: dict) -> list[Path]`.
- `WorkPackage` dataclass: `module, suite, split_a_survivors, rules_file, max_cost`.
- `record_cost(member, module, suite, backend, minutes, bobcoins, source)`:
  - Creates `results/costs_<member>.csv` with header on first write.
  - Appends one row thereafter.
  - Columns: `timestamp, module, suite, backend, minutes, bobcoins, source`.
- `BackendError(RuntimeError)` for missing backend binaries.

**Todo List**
1. Write `AgentBackend` ABC using `abc.ABC` and `@abc.abstractmethod`.
2. Define `WorkPackage` dataclass.
3. Implement `record_cost()` using `csv` and `pathlib` (create `results/` if absent).
4. Implement `BackendError`.

**Relevant Context**
- Cost files are per-member (`MH_MEMBER` env var) so two contributors never conflict.
- `report` (track B) globs `results/costs*.csv`.
- `bob.py` is not implemented by track A.

---

## Sub-Task ST8 — Unit tests (`tests/`)

**Status:** [ ] pending

**Intent**
Verify M1 acceptance criteria with automated, fast tests. Integration tests
(`test_baseline.py`, `test_jobs.py`) run the real CLI against the real validators
project and may be slow; they are clearly marked.

**Expected Outcomes**
- `pytest tests/` passes with no errors.
- Coverage of M1 acceptance criteria:
  - `BaselineError` exit 2 triggered by synthetic red-baseline fixture.
  - `IsolationError` exit 3 triggered by synthetic isolation fixture.
  - Unique mutant IDs on nested expressions (e.g., `a < b < c`).
  - Deterministic split assignment: same ID → same split across calls.
  - `baseline --set all` ref_match = yes for all 24 rows.
  - `--jobs 1` and `--jobs 4` identical results on `url`.

**Todo List**
1. Create `tests/conftest.py` with fixtures for synthetic Python source files.
2. Write `tests/test_registry.py`:
   - Repo-root resolution (correct even when cwd ≠ repo root).
   - Module loading (24 rows, slugs correct).
   - Suite path logic for human, human+mh, human+b1.
3. Write `tests/test_mutate.py`:
   - Operator enumeration (spot-check known counts on a synthetic module).
   - ID uniqueness on nested expressions.
   - Split determinism (same ID always yields same A/B).
   - `falsy_preserving` flag on `return False`.
4. Write `tests/test_isolation.py`:
   - `BaselineError` on a synthetic module whose tests are red.
   - `IsolationError` on a synthetic module that fools the import-path check.
   - `PYTHONDONTWRITEBYTECODE=1` is set in subprocess env.
5. Write `tests/test_baseline.py` (slow, integration):
   - Runs `mutanthunter baseline --set all --jobs 8` via subprocess.
   - Reads `results/baseline.csv`; asserts `ref_match == yes` for all 24 rows.
6. Write `tests/test_jobs.py` (slow, integration):
   - Runs `url` with `--jobs 1` and `--jobs 4`; compares result JSONs field-by-field.

**Constraints**
- Synthetic fixtures must not create `results/mutants/*__all.json` or `*__B.json` files.
- After each integration test run, delete any `*__all.json` or `*__B.json` artefacts
  created (these must not exist per the hold-out discipline of SPEC § 7.2b).

---

## M1 Verification Checklist

After ST1–ST8 are implemented, the following must all pass before marking M1 done:

| Check | Command / Assertion |
|---|---|
| Package installs | `uv pip install -e .` exits 0 |
| CLI available | `mutanthunter --help` exits 0 |
| Baseline ref_match | `mutanthunter baseline --set all --jobs 8` → all 24 `ref_match = yes` |
| Jobs determinism | `mutate url --jobs 1` and `--jobs 8` identical results |
| Unit tests pass | `pytest tests/` exits 0 |
| No __all.json or __B.json | `results/mutants/` must not contain `*__all.json` or `*__B.json` |
| Not-implemented stubs | `mutanthunter report` / `replay` → print stub, exit 1 |

---

## Key Design Decisions

1. **`ProcessPoolExecutor` for isolation**: each worker gets its own temp workspace via
   `Workspace` inside the worker function. This avoids shared-state issues.

2. **Deterministic result ordering**: workers return `(index, result)` pairs; the caller
   sorts by index before assembling the final list.

3. **`ast.walk` order for mutant enumeration**: `ast.walk` uses BFS, which is
   deterministic for a given source. Order is preserved; IDs are stable.

4. **Baseline writes counts only**: `baseline.csv` has no `survivors` column; the hold-out
   split B is never exposed.

5. **Lazy imports for track B modules**: `try: import ...; except ImportError: stub`.
   The stub prints the exact string "not implemented yet" (lowercase) and exits 1.

6. **`results/equivalent/<slug>.json` written by `mutate.py`**, not by `cli.py`,
   so it is populated regardless of which entry point is used.

7. **`--jobs 1` vs `--jobs N` identical results**: ProcessPoolExecutor returns results
   in submission order (via `executor.map` or by collecting futures with original index).
   Using `executor.map` with the same ordered mutant list guarantees this.

---

## Track B Interface Contracts (reference)

Track A must not change these after handoff:

- `Mutant` dataclass in `mutant_hunter.mutate` — see ST4 field list above.
- `run_mutation(module, suite, split, jobs, seed) -> Path` in `mutant_hunter.mutate`.
- `AgentBackend`, `record_cost`, `WorkPackage` in `mutant_hunter.backends.base`.
- `modules_by_set`, `get_module`, `suite_test_paths` in `mutant_hunter.registry`.
- JSON schema of `results/mutants/<slug>__<suite>__<split>.json` per SPEC § 5.6.
