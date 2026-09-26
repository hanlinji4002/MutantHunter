# Track A Build Plan — MutantHunter

> Status: pending implementation. Track A owns all items marked below.
> Track B plugs into the interfaces listed at the bottom of this file.
> When this plan and SPEC.md disagree, SPEC.md wins; amend this file first.

---

## Top-Level Overview

Track A builds the deterministic core of MutantHunter (no LLM calls) and runs
the full mutation pipeline on all 12 target modules (10 main + 2 extra).

The deliverables are:
- `pyproject.toml` — installable package exposing the `mutanthunter` CLI
- `mutant_hunter/registry.py` — dataset source of truth
- `mutant_hunter/isolation.py` — safe workspace + pytest runner
- `mutant_hunter/mutate.py` — mutation operators, IDs, splits, parallel runs
- `mutant_hunter/check.py` — acceptance checker for one test file
- `mutant_hunter/cli.py` — six subcommands; unimplemented ones print a stub
- `mutant_hunter/backends/base.py` — AgentBackend interface + cost logger
- `tests/` — unit tests for the core package (M1 acceptance criteria)
- `.bob/skills/mutant-hunter/SKILL.md` — Bob skill
- `.bob/rules/testing.md` — testing rules enforced on every subagent
- Mutation runs (`mutanthunter mutate`) for all 12 modules, suites
  `human` and `human+mh`, stored in `results/mutants/`
- `results/modules/<slug>.json` and `results/suspected_bugs/<slug>.md`
  for all 12 modules
- `results/equivalent/<slug>.json` for all 12 modules
- `results/baseline.csv` and `results/baseline.md` (ref_match=yes for all 24)

Track B's modules (`replay.py`, `stats.py`, `report.py`, `exam_c.py`) are
imported lazily by `cli.py`; while they do not exist the subcommand prints
"not implemented yet" and exits 1.

Track B owns all B1 test generation (`targets/validators/tests/b1/`) and
`exam_c.py`. Track A never writes to those paths.

Milestone targets in this plan: M1 → M2 → M3 (track-A portion only).

---

## Sub-Task 1 — `pyproject.toml` and package scaffold

**Status:** [x] done

**Intent**
Create the root `pyproject.toml` that makes `mutant_hunter` pip-installable and
registers the `mutanthunter` console script. Without this, no other sub-task can
import or invoke the package.

**Expected Outcomes**
- `pip install -e .` succeeds from the repo root.
- `mutanthunter --help` is available in the shell.
- `mutant_hunter/` package directory exists with an `__init__.py`.

**Todo List**
1. Create `pyproject.toml` at the repo root with `[project]`, `[build-system]`
   (setuptools), `[project.scripts]` mapping `mutanthunter = "mutant_hunter.cli:main"`.
2. Declare Python ≥ 3.9, zero runtime dependencies (stdlib only).
3. Create `mutant_hunter/__init__.py` (empty) and `mutant_hunter/backends/__init__.py` (empty).
4. Verify `pip install -e .` and `mutanthunter --help` run without error.

**Relevant Context**
- `targets/validators/pyproject.toml` — reference for field names and style.
- No external runtime deps; subprocess, ast, hashlib, tempfile, shutil are all stdlib.

---

## Sub-Task 2 — `registry.py`

**Status:** [x] done

**Intent**
Provide a single source of truth for every module's source path, test path,
set membership, spec list, and reference baseline numbers. All other modules
import from here; nothing else parses `modules.csv`.

**Expected Outcomes**
- `Registry` (or equivalent) loads `dataset/modules.csv` relative to the repo root.
- All paths are resolved relative to the repo root: the directory that contains
  `dataset/modules.csv`, found by walking up from `__file__` until that file
  exists. Never use `os.getcwd()`.
- Callers can filter by `set` (`main`, `extra`, `reference`, `all`).
- Suite paths are computed per spec 5.1:
  - `human` → `test_path`
  - `human+mh` → `test_path` + `tests/mh/<slug>/` (warn + fall back if missing)
  - `human+b1` → `test_path` + `tests/b1/<slug>/` (warn + fall back if missing)
- A slug is the module name with `/` replaced by `__`.
- `ref_mutants` and `ref_killed` are accessible for each module.

**Todo List**
1. Write `registry.py`; parse CSV with `csv.DictReader`; no third-party imports.
2. Implement a `_repo_root()` helper: walk up from `Path(__file__)` until a
   directory containing `dataset/modules.csv` is found; raise `RuntimeError`
   if not found.
3. Implement `Module` dataclass: `module`, `slug`, `source_path`, `test_path`,
   `set`, `specs`, `ref_mutants`, `ref_killed`. All path fields are absolute
   `Path` objects resolved against `REPO_ROOT`.
4. Implement `all_modules()`, `modules_by_set(set_name)`, `get_module(name)`.
5. Implement `suite_test_paths(module, suite, target_root)` with the missing-folder
   warning. `target_root` defaults to `REPO_ROOT / "targets/validators"`.
6. Set `REPO_ROOT`, `TARGET_ROOT`, and `VENV_PYTHON` as module-level constants
   derived from `_repo_root()`.

**Relevant Context**
- `dataset/modules.csv` columns: `module, source_path, test_path, set, specs,
  ref_line_branch_cov, ref_mutants, ref_killed, ref_mutation_score`.
- All 12 target modules (10 main + 2 extra) listed in the CSV.
- Slugs needed: `country`, `cron`, `domain`, `email`, `finance`, `hostname`,
  `ip_address`, `mac_address`, `url`, `uuid`, `i18n__fi`, `i18n__fr`.

---

## Sub-Task 3 — `isolation.py`

**Status:** [x] done

**Intent**
Guard against the three silent failures documented in spec 5.2 and provide a
safe, parallel-compatible workspace for each mutation run. This is the most
critical correctness guarantee in the entire harness.

**Expected Outcomes**
- Each worker gets an independent temp copy of `src/` and `tests/`; originals
  are never modified.
- `__pycache__` is never copied; `PYTHONDONTWRITEBYTECODE=1` is always set.
- Editable-install guard: import path confirmed inside the copy (exit 3 on fail).
- Red-baseline guard: suite must pass on original AND on `ast.unparse(original)`;
  exit 2 on failure.
- Stale-bytecode guard: `PYTHONDONTWRITEBYTECODE=1` environment variable set for
  all subprocess calls.
- `--jobs N` gives identical results to `--jobs 1`.

**Todo List**
1. Write `Workspace` context manager: creates temp dir, copies `src/` and
   `tests/` (excluding `__pycache__`), sets env vars.
2. Write `run_pytest(workspace, suite_paths, timeout=60)` → `"survived" | "killed"`.
   Command: `python -m pytest -x -q -p no:cacheprovider <paths>`.
3. Write `check_isolation(workspace, module)`: runs the import-path assertion;
   raises `IsolationError` (exit 3) on failure.
4. Write `check_baseline(workspace, module, suite_paths)`: runs suite on original
   then on `ast.unparse`-round-tripped source; raises `BaselineError` (exit 2) on
   failure.
5. Write `run_all_mutants(mutants, suite_paths, jobs)` using
   `concurrent.futures.ProcessPoolExecutor` (or `ThreadPoolExecutor` for
   subprocess); deterministic ordering of results regardless of completion order.
6. Add the "kills none of 5+" check: if ≥ 5 mutants run and none are killed,
   raise `IsolationError` (exit 3).

**Relevant Context**
- Spec 5.2 enumerates exactly three silent failures and the remedies.
- Worker PYTHONPATH must be `<copy>/src` (not the editable install).
- `VENV_PYTHON` from `registry.py` is the interpreter.

---

## Sub-Task 4 — `mutate.py`

**Status:** [x] done

**Intent**
Enumerate mutants deterministically, assign stable IDs, assign A/B splits, and
run the full mutation suite for one module. The reference counts in `modules.csv`
must be reproduced exactly; any discrepancy is a harness bug.

**Expected Outcomes**
- `enumerate_mutants(source_path)` produces the same ordered list on every call.
- Mutant IDs are `<slug>:<line>:<col>:<end_line>:<end_col>:<op>` (end position
  disambiguates nested expressions).
- All six operator families from spec 5.3 are implemented.
- Split assignment: `B` if first byte of `sha256(f"20260925:{mutant_id}")` is odd,
  else `A`.
- `falsy_preserving` flag set automatically for `return_none` where original is
  `return False`; logged to `results/equivalent/<slug>.json`.
- `run_mutation(module, suite, split, jobs, seed)` writes
  `results/mutants/<slug>__<suite>__<split>.json` in the format of spec 5.6.
- `ref_mutants` and `ref_killed` match CSV exactly for all 24 modules.
- `mutate --split C` lazily imports
  `mutant_hunter.exam_c.enumerate_exam_c(source, slug) -> list[Mutant]`; if
  `exam_c` is not importable, prints "not implemented yet" and exits 1.

**Todo List**
1. Implement AST visitor that walks `ast.walk` order and records all operator
   application sites.
2. Implement each operator from spec 5.3 table; use deep copies for every mutant.
3. Implement `mutant_id(slug, node, op, op_index)` with end-position encoding.
4. Implement `split(mutant_id, seed=20260925)`: sha256 first-byte parity.
5. Implement `falsy_preserving` detection: `return_none` on `return False` nodes.
6. Implement the JSON result writer using the schema from spec 5.6.
7. Wire the `--split C` lazy-import stub: `try: from mutant_hunter import exam_c`
   around the `enumerate_exam_c` call; print stub and exit 1 if import fails.
8. Cross-check against `ref_mutants` / `ref_killed` in CSV for all 24 modules
   (run `baseline --set all` and inspect `ref_match`).

**Relevant Context**
- Spec 5.3 table: `cmp_<a>_to_<b>`, `bin_<a>_to_<b>`, `bool_and_to_or`,
  `bool_or_to_and`, `if_negate`, `int_plus_one`, `return_none`.
- `#i` suffix for chained comparisons (i ≥ 1, 1-indexed).
- Seed is the string `"20260925"`, not an integer, in the hash input.
- Exam-C operators (`flip_bool`, `drop_not`, `string_mutate`, `drop_case_method`,
  `aug_assign_swap`) must NOT appear here; they live in `exam_c.py` (M4, track B).
- The `Mutant` dataclass is defined here (canonical definition); `exam_c.py`
  builds objects of this type. See interface contracts for the full field list.

---

## Sub-Task 5 — `check.py`

**Status:** [x] done

**Intent**
Let agents verify a single test file before committing it: confirms it passes 3
times on the original code, identifies which split-A human survivors it kills,
and surfaces failing tests (suspected violations) without hiding them.

**Expected Outcomes**
- `check_file(module, test_file, repeat=3)` returns the JSON schema from spec 5.6.
- `passes_on_original`: all tests pass on the original in `repeat` runs.
- `flaky`: any test that passes on some runs but not others.
- `kills`: list of split-A survivor IDs the file kills.
- `not_killed`: split-A survivors not killed.
- `failing_tests_on_original`: full pytest node IDs including parametrize IDs.
- A failing test is never deleted; it is collected and reported.

**Todo List**
1. Write `check_file(module, test_file, repeat=3)` using `Workspace` from
   `isolation.py`.
2. Run the file alone on the original `repeat` times; detect flakiness.
3. Load split-A survivors from the most recent
   `results/mutants/<slug>__human__A.json`.
4. For each survivor, run the test file in a mutant workspace; collect kills.
5. Output JSON matching the spec 5.6 schema exactly; print to stdout.

**Relevant Context**
- Spec 5.6 check output schema.
- Relies on `isolation.Workspace` and `run_pytest`.
- `failing_tests_on_original` must include the full pytest node ID
  (parametrize brackets and spaces included).

---

## Sub-Task 6 — `cli.py`

**Status:** [x] done

**Intent**
Wire all six subcommands behind a single `mutanthunter` entry point. Unimplemented
modules (track B's `report`, `replay`, `stats`, `exam_c`) and the optional
`backends.bob` are imported lazily so two people can build in parallel without
merge conflicts.

**Expected Outcomes**
- `mutanthunter --help` lists all six subcommands.
- Global flags `--jobs N` and `--seed N` accepted before or after subcommand.
- `baseline`, `mutate`, `check`, `generate` are functional (M1–M3).
- `mutate --split C` delegates to `mutate.py`'s lazy exam-C stub.
- `replay`, `report` print "not implemented yet" and exit 1 while their modules
  are absent.
- `generate` lazy-imports `backends.bob`; prints "not implemented yet" and
  exits 1 if absent. (`bob.py` is never written by track A.)
- Exit codes: 0 ok, 1 error/not-implemented, 2 baseline not green, 3 isolation
  suspected.

**Todo List**
1. Use `argparse` (stdlib); define parent parser with `--jobs` and `--seed`.
2. Add `baseline` subcommand: calls `mutate.run_mutation` for each module in the
   set with the human suite; writes `results/baseline.csv` and `results/baseline.md`;
   computes `ref_match`.
3. Add `mutate` subcommand: wraps `mutate.run_mutation`; default split A; accepts
   `--split A|B|all|C`.
4. Add `check` subcommand: wraps `check.check_file`.
5. Add `generate` subcommand: lazy-imports `backends.bob`; prints stub and exits
   1 if absent.
6. Add `replay` subcommand: lazy-imports `replay`; prints stub if absent.
7. Add `report` subcommand: lazy-imports `report`; prints stub if absent.
8. Map `IsolationError` → exit 3, `BaselineError` → exit 2, all other errors
   → exit 1.

**Relevant Context**
- Spec 5.5 command table and `--split` flag.
- `baseline` writes counts only (no survivor lists) — split B must not be revealed.
- `--split` default is `A`; `--split all` is allowed for `baseline`.

---

## Sub-Task 7 — `backends/base.py`

**Status:** [x] done

**Intent**
Define the `AgentBackend` interface that any future backend must implement.
Provide the shared cost-logging helper that writes per-member CSV files so two
contributors never edit the same file.

**Expected Outcomes**
- `AgentBackend` abstract class with `generate_tests(work_package) -> list[Path]`.
- `record_cost(member, module, suite, backend, minutes, bobcoins, source)` appends
  one row to `results/costs_<member>.csv`.
- `report` (track B) reads every `results/costs*.csv` glob.
- `BackendError` raised with a human-readable message when a backend binary is
  not installed.

**Todo List**
1. Write `AgentBackend` as an `abc.ABC` with one abstract method.
2. Define `WorkPackage` dataclass: `module`, `suite`, `split_a_survivors`,
   `rules_file`, `max_cost`.
3. Write `record_cost(...)` using `csv` stdlib; create file + header on first write;
   append thereafter.
4. Write `BackendError(RuntimeError)` for missing backend binaries.

**Relevant Context**
- Spec 5.8 interface description.
- Cost CSV columns: `timestamp, module, suite, backend, minutes, bobcoins, source`.
- One file per team member: `results/costs_<member>.csv`.
- `bob.py` is not written by track A; `generate` subcommand lazily imports it
  and stubs if absent.

---

## Sub-Task 8 — Unit tests (`tests/`)

**Status:** [x] done

**Intent**
Verify the M1 acceptance criteria with automated tests. These tests run on the
MutantHunter package itself, not on validators.

**Expected Outcomes**
- All unit tests pass (`pytest tests/`).
- At least one test each for:
  - Exit code 2 (red baseline triggers `BaselineError`).
  - Exit code 3 (isolation failure triggers `IsolationError`).
  - Unique mutant IDs on nested expressions (spec 5.3).
  - Deterministic split assignment (`sha256` parity).
  - `--jobs 1` and `--jobs 4` produce identical results on `url`.
  - `ref_match = yes` for all 24 modules via `baseline --set all`.

**Todo List**
1. Create `tests/` directory with `conftest.py`.
2. Write `test_registry.py`: module loading, slug conversion, suite path logic,
   repo-root resolution (verify paths are absolute and independent of cwd).
3. Write `test_mutate.py`: operator enumeration, ID uniqueness on nested
   expressions, split determinism.
4. Write `test_isolation.py`: exit-2 and exit-3 scenarios (use synthetic minimal
   Python files as fixtures, not the real validators project).
5. Write `test_baseline.py`: integration test running `baseline --set all` and
   asserting `ref_match = yes` for all 24 rows.
6. Write `test_jobs.py`: `url` module results identical with `--jobs 1` and
   `--jobs 4`.

**Relevant Context**
- M1 acceptance: `baseline --set all` reproduces ref exactly; `--jobs 1` and
  `--jobs 8` identical on `url`; exit codes 2 and 3; unique IDs on nested exprs.
- Spec 11 milestone table.

---

## Sub-Task 9 — `.bob/skills/mutant-hunter/SKILL.md` and `.bob/rules/testing.md`

**Status:** [ ] pending

**Intent**
Give IBM Bob the structured procedure for running the full MutantHunter pipeline
on one module (skill) and the invariants every generated test file must satisfy
(rules). These are the primary Bob artifacts for track A.

**Expected Outcomes**
- Typing the one-sentence trigger in the IDE chat runs the full procedure
  (steps 1–5 of spec 6.1) within a single IDE task.
- Broad and spec subagents are both spawned inside that same task and run in
  parallel (Bob's native parallel-subagent mechanism, not two separate IDE tasks).
- The targeted subagent (step 4), if needed, is also spawned within the same
  task.
- The skill procedure never uses `--split B` or opens `*__B.json` files.
- `testing.md` is followed by all three subagent roles.

**Todo List**
1. Create `.bob/skills/mutant-hunter/SKILL.md`:
   - Input slot: `module` name.
   - Step 1: `mutanthunter mutate <module>` (split A, human suite).
   - Step 2: spawn broad + spec subagents **in parallel within this task** with
     the briefs from spec 6.2. Record the start time.
   - Step 3: `mutanthunter check` on every returned file; failing tests →
     `results/suspected_bugs/<slug>.md`; reconcile broad vs spec (spec 3b).
   - Step 4: `mutanthunter mutate <module> --suite human+mh`; if split-A
     survivors remain that are not falsy-preserving, spawn targeted subagent
     within this task; repeat step 3 for its file.
   - Step 5: write `results/modules/<slug>.json` and
     `results/equivalent/<slug>.json`.
2. Create `.bob/rules/testing.md` with all rules from spec 6.3 verbatim,
   formatted for Bob consumption.
3. Smoke-test the skill on `url` by typing the trigger in the IDE chat; confirm
   `results/modules/url.json` is written and split-A score improved.

**Relevant Context**
- Spec 6.1 step-by-step procedure and step 3b reconciliation rule.
- Spec 6.2 subagent briefs (broad, spec, targeted).
- Spec 6.3 rules text (verbatim reproduction required).
- M2 acceptance: skill runs on `url` in one IDE chat request; parallel subagents;
  `results/modules/url.json` complete; split-A score went up.

---

## Sub-Task 10 — Mutation runs for all 12 modules

**Status:** [ ] pending

**Intent**
Execute the MutantHunter pipeline on every `main` and `extra` module, producing
all required result files that track B will read for evaluation.

**Expected Outcomes**
For each of the 12 modules (country, cron, domain, email, finance, hostname,
ip_address, mac_address, url, uuid, i18n/fi, i18n/fr):
- `results/mutants/<slug>__human__A.json` — human suite, split A.
- `results/mutants/<slug>__human+mh__A.json` — human+mh suite, split A.
- `results/modules/<slug>.json` — complete, with `finished_at` set.
- `results/suspected_bugs/<slug>.md` — every entry has a category.
- `results/equivalent/<slug>.json` — includes all `falsy_preserving` entries.
- `targets/validators/tests/mh/<slug>/` — at least one test file.

**Todo List**
1. Run `mutanthunter baseline --set main` and `--set extra`; confirm
   `ref_match = yes` for all 12 modules.
2. Run the Bob skill on `url` first as a solo IDE task; verify all 5 artefacts
   before proceeding.
3. Run the remaining 11 modules in pairs as parallel IDE tasks (two at a time),
   following the sequence:
   - Pair 1: `country`, `cron`
   - Pair 2: `domain`, `email`
   - Pair 3: `finance`, `ip_address`
   - Pair 4: `uuid`, `hostname`
   - Pair 5: `mac_address`, `i18n/fi`
   - Solo: `i18n/fr`
4. After each module: `mutanthunter check` on every new test file; accept or
   move to `suspected_bugs`.
5. Run `mutanthunter mutate <module> --suite human+mh --split A` for each module.
6. Collect and verify all 5 output artefacts per module listed above.
7. Save a screenshot + exported Bob history to `bob_sessions/` for each module
   run (session evidence, required for every milestone).

**Relevant Context**
- 12 target modules: `country`, `cron`, `domain`, `email`, `finance`, `hostname`,
  `ip_address`, `mac_address`, `url`, `uuid`, `i18n/fi`, `i18n/fr`.
- Slugs for i18n: `i18n__fi`, `i18n__fr`.
- Spec 7.2b hold-out discipline: do NOT run `--split B` or `--split all` during
  generation; split B is track B's domain.
- Track B owns `targets/validators/tests/b1/`; track A never writes to that path.

---

## Track B Interface Contracts

The following are the precise interfaces and file formats that track B plugs into.
Track A must not change these contracts after handing off.

### Files track B reads (written by track A)

| Path pattern | Format | Spec section |
|---|---|---|
| `results/baseline.csv` | CSV: `module, set, suite, split, mutants, killed, score, ref_mutants, ref_killed, ref_match` | 5.5 |
| `results/mutants/<slug>__<suite>__A.json` | JSON schema spec 5.6 (mutation run) | 5.6 |
| `results/modules/<slug>.json` | JSON schema spec 6.6 | 6.6 |
| `results/equivalent/<slug>.json` | List of `{id, kind, reason, conditional_on}` | 6.7 |
| `results/suspected_bugs/<slug>.md` | Markdown, one `## <title>` section per violation, fields per spec 6.5 | 6.5 |
| `targets/validators/tests/mh/<slug>/` | Pytest files, all passing on original | 5.1 |
| `results/costs_<member>.csv` | CSV: `timestamp, module, suite, backend, minutes, bobcoins, source` | 5.8 |
| `results/raw/<UTC>__<slug>__<suite>.json` | Unedited `bob run --format json` stdout (written manually by track A per IDE session) | 5.8 |

### Python interfaces track B imports from track A modules

| Symbol | Module | Signature |
|---|---|---|
| `AgentBackend` | `mutant_hunter.backends.base` | ABC; `generate_tests(WorkPackage) -> list[Path]` |
| `record_cost` | `mutant_hunter.backends.base` | `(member, module, suite, backend, minutes, bobcoins, source) -> None` |
| `modules_by_set` | `mutant_hunter.registry` | `(set_name: str) -> list[Module]` |
| `get_module` | `mutant_hunter.registry` | `(name: str) -> Module` |
| `suite_test_paths` | `mutant_hunter.registry` | `(module, suite, target_root) -> list[Path]` |
| `run_mutation` | `mutant_hunter.mutate` | `(module, suite, split, jobs, seed) -> Path` (path to JSON) |
| `Mutant` | `mutant_hunter.mutate` | dataclass — see schema below |

### CLI subcommands track B adds to `cli.py`

Track B must implement the lazy-import stubs already registered in `cli.py`:

| Subcommand | Module to implement | Spec section |
|---|---|---|
| `report` | `mutant_hunter/report.py` | 5.5, 8 |
| `replay` | `mutant_hunter/replay.py` | 7.4 |
| (stats helper) | `mutant_hunter/stats.py` | 5.7 |
| (exam-C scoring) | `mutant_hunter/exam_c.py` | 7.2c |

Track B's `exam_c.py` must export:

```python
def enumerate_exam_c(source: str, slug: str) -> list[Mutant]: ...
```

`mutate --split C` calls this function via lazy import. Track B must implement
it only after all test generation is frozen (M4), and must not expose the
exam-C operators to any file an agent reads while writing tests.

### `Mutant` dataclass — canonical definition (in `mutant_hunter/mutate.py`)

| Field | Type | Description |
|---|---|---|
| `id` | `str` | Full mutant ID: `<slug>:<line>:<col>:<end_line>:<end_col>:<op>` |
| `op` | `str` | Operator code, e.g. `if_negate` |
| `line` | `int` | 1-based start line of the mutated node |
| `function` | `str` | Name of the enclosing function (or `<module>` if top-level) |
| `original` | `str` | The changed fragment before mutation (not the whole line) |
| `mutated` | `str` | The changed fragment after mutation |
| `falsy_preserving` | `bool` | `True` for `return_none` on `return False` |
| `split` | `str` | `"A"` or `"B"` |
| `source` | `str` | Unparsed source of the full mutated module |

### Mutation run JSON schema (spec 5.6) — canonical contract

```json
{
  "module": "url",
  "slug": "url",
  "suite": "human+mh",
  "split": "A",
  "seed": 20260925,
  "mutants": 58,
  "killed": 45,
  "survived": 10,
  "invalid": 3,
  "falsy_preserving": 2,
  "score": 0.818,
  "adjusted_score": 0.833,
  "seconds": 120.4,
  "results": [{"id": "url:75:4:76:19:if_negate", "status": "killed"}],
  "survivors": [{
    "id": "url:75:4:76:19:if_negate",
    "op": "if_negate",
    "line": 75,
    "function": "url",
    "original": "if re.match(...)",
    "mutated": "if not (re.match(...))",
    "falsy_preserving": false,
    "split": "A"
  }]
}
```

### `summary.csv` schema (written by track B `report.py`, read by track B dashboard)

`module, set, suite, split, mutants, killed, score, ci_low, ci_high, adjusted_score, falsy_preserving, tests_kept, suspected_bugs, minutes, bobcoins`
