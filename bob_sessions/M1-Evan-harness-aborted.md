# Follow sub-tasks ST1–ST8 of @/docs/track-a-plan.md.
Implement the core of section 5 of @/docs/SPEC.md: mutant_hunter/registry.py, isolation.py, mutate.py, check.py, cli.py and backends/base.py, pyproject.toml with the `mutanthunter` console script, and unit tests in tests/.
Section 5.2 is critical: guard against all three silent failures (editable install → run tests with PYTHONPATH=<copy>/src and verify the import path; red baseline → exit 2; stale bytecode → PYTHONDONTWRITEBYTECODE=1 and never copy __pycache__). Mutant IDs include end positions (5.3). `baseline` writes counts only. `mutate` defaults to split A.
My teammate will implement report.py, stats.py, replay.py and exam_c.py later. Do not implement them. In cli.py import them lazily and print "not implemented yet" if a module is missing, using exactly these interfaces:
- report.report(results_dir: Path, docs_dir: Path, modules_csv: Path) -> list[Path]
- replay.replay(which: str, suites: list[str]) -> list[dict]
- exam_c.enumerate_exam_c(source: str, slug: str) -> list[Mutant]  (mutate uses it when --split C)
- backends.bob.BobBackend(max_cost: float).generate_tests(work_package: dict) -> list[Path]  (optional; may never be implemented)
Cost logging writes results/costs_<member>.csv, where <member> is the environment variable MH_MEMBER.
Then install the package into targets/validators/.venv (`uv pip install -e .`), run `mutanthunter baseline --set all --jobs 8` and make ref_match "yes" for all 24 modules. Also run `mutanthunter mutate url --split all` with --jobs 1 and with --jobs 8 and confirm identical results. Afterwards delete results/mutants/*__all.json and any *__B.json: they list split-B survivors and must not exist when the skill runs. Unit tests must not leave such files behind either.
Stop when the M1 row of section 11 is satisfied.

---

**Status:** active  **Date:** 2026-09-26

---

### 👤 User

Follow sub-tasks ST1–ST8 of @/docs/track-a-plan.md.
Implement the core of section 5 of @/docs/SPEC.md: mutant_hunter/registry.py, isolation.py, mutate.py, check.py, cli.py and backends/base.py, pyproject.toml with the `mutanthunter` console script, and unit tests in tests/.
Section 5.2 is critical: guard against all three silent failures (editable install → run tests with PYTHONPATH=<copy>/src and verify the import path; red baseline → exit 2; stale bytecode → PYTHONDONTWRITEBYTECODE=1 and never copy __pycache__). Mutant IDs include end positions (5.3). `baseline` writes counts only. `mutate` defaults to split A.
My teammate will implement report.py, stats.py, replay.py and exam_c.py later. Do not implement them. In cli.py import them lazily and print "not implemented yet" if a module is missing, using exactly these interfaces:
- report.report(results_dir: Path, docs_dir: Path, modules_csv: Path) -> list[Path]
- replay.replay(which: str, suites: list[str]) -> list[dict]
- exam_c.enumerate_exam_c(source: str, slug: str) -> list[Mutant]  (mutate uses it when --split C)
- backends.bob.BobBackend(max_cost: float).generate_tests(work_package: dict) -> list[Path]  (optional; may never be implemented)
Cost logging writes results/costs_<member>.csv, where <member> is the environment variable MH_MEMBER.
Then install the package into targets/validators/.venv (`uv pip install -e .`), run `mutanthunter baseline --set all --jobs 8` and make ref_match "yes" for all 24 modules. Also run `mutanthunter mutate url --split all` with --jobs 1 and with --jobs 8 and confirm identical results. Afterwards delete results/mutants/*__all.json and any *__B.json: they list split-B survivors and must not exist when the skill runs. Unit tests must not leave such files behind either.
Stop when the M1 row of section 11 is satisfied.

---

### 🤖 Assistant

> 🔧 called: use_skill



> 🔧 **use_skill** — create-plan

### 🤖 Assistant

> 🔧 called: read_file, read_file

Let me start by reading the referenced documents to understand the full scope.

> 🔧 **read_file** — docs/SPEC.md

> 🔧 **read_file** — docs/track-a-plan.md