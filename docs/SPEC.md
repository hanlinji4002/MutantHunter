# MutantHunter — Design Spec

> Status: design written before the hackathon; it contains no code. All code is written during the event with IBM Bob, and `bob_sessions/` shows that work.
> When this spec and a prompt disagree, this spec wins. Change the spec first, then the code.

## 0. Summary

MutantHunter finds the bugs a test suite misses and writes tests that catch them, then proves the gain on mutants the agents never saw.

For one module, the Bob skill:
1. Injects small bugs (mutants) and runs the human tests. Mutants nobody notices are **survivors**. Only half of the mutants (split A) are ever shown to agents.
2. Spawns two subagents in parallel:
   - a **broad** subagent writes the regression tests a careful developer would write;
   - a **spec** subagent reads the module's specification documents (RFC, ISO, BIP, Wikipedia) and writes tests whose expected results come from the spec.
3. Runs the new tests. A test that fails on the current code is never deleted: it becomes a **suspected spec violation** with a category.
4. Spawns a **targeted** subagent for the split-A survivors that are still alive.
5. Scores everything on the hidden split B.

Everything that can be deterministic is deterministic. The core package never calls an LLM.

## 1. Goals and non-goals

Goals:
- Beat both the human tests and a plain one-prompt AI baseline (B1) on the hold-out mutation score of the 10 `main` modules in `dataset/modules.csv`.
- Surface suspected spec violations, categorized, and confirm the most important ones by hand.
- Catch the historical bugs that today's tests still miss (`extra` set).
- Report every number with n and a 95% confidence interval.
- Keep the core usable without Bob, so the repo still runs after the event.

Non-goals:
- Languages other than Python.
- Fixing the target project. MutantHunter only reports.

## 2. Final deliverables

| Deliverable | Path | Milestone | Done when |
|---|---|---|---|
| Core package + CLI | `mutant_hunter/`, `pyproject.toml` | M1 | `mutanthunter baseline --set all` reproduces the reference exactly |
| Baseline | `results/baseline.csv`, `results/baseline.md` | M1 | `ref_match` is `yes` for all 24 modules |
| Bob skill + rules | `.bob/skills/mutant-hunter/SKILL.md`, `.bob/rules/testing.md` | M2 | one sentence in Bob runs the whole pipeline on `url` |
| MH tests | `targets/validators/tests/mh/<slug>/` | M2–M3 | all pass on the original code |
| B1 tests | `targets/validators/tests/b1/<slug>/` | M3 | one file per module in `main` and `extra` |
| Per-module results | `results/modules/<slug>.json`, `<slug>_rules.md` | M2–M3 | one per module in `main` and `extra` |
| Suspected violations | `results/suspected_bugs/<slug>.md` | M2–M3 | every entry has a category |
| Split-B scores | `results/mutants/<slug>__<suite>__B.json` | M3 | 3 suites × 12 modules |
| Summary | `results/summary.csv` | M3 | one row per module × suite |
| Replay | `results/replay.csv` | M4 | every row of `dataset/bug_commits.csv` × suites human, mh, b1 |
| Statistics | `results/stats.md` | M4 | every headline number has n and a 95% CI |
| Dashboard | `docs/index.html` | M3–M4 | works offline; published by GitHub Pages as the demo URL |
| Raw Bob outputs, costs | `results/raw/`, `results/costs.csv` | M2–M3 | every `bob run` kept unedited |
| README, statements | `README.md`, `docs/problem_solution.md`, `docs/bob_usage.md` | M5 | statements are 500 words or fewer |
| Session evidence | `bob_sessions/` | every milestone | screenshot + exported history per task |

Demo URL: `https://hanlinji4002.github.io/MutantHunter/` (GitHub Pages, `main` branch, `/docs` folder).

## 3. Repository layout (final)

```
MutantHunter/
├── .bob/skills/mutant-hunter/SKILL.md, .bob/rules/testing.md   M2
├── mutant_hunter/                            M1, core, no LLM
│   ├── cli.py         entry point `mutanthunter`
│   ├── registry.py    dataset/modules.csv, paths, suites
│   ├── isolation.py   temp copies, env, pytest runner, guards
│   ├── mutate.py      operators, IDs, splits, parallel runs, coverage
│   ├── check.py       acceptance check for one test file
│   ├── replay.py      historical bug replay                 M4
│   ├── stats.py       Wilson CI, exact McNemar (stdlib)      M4
│   ├── report.py      summary.csv, stats.md, docs/index.html M3–M4
│   └── backends/      base.py (interface, cost log) M1; bob.py M3
├── tests/             unit tests of mutant_hunter itself     M1
├── dataset/           prepared before the event (data only)
├── targets/validators/  validators@70de324 unchanged, plus tests/mh and tests/b1
├── targets/humanize/    stretch goal
├── results/           baseline, mutants/, modules/, suspected_bugs/, equivalent/, raw/, csv and md outputs
├── docs/              SPEC.md, index.html, decisions.md (written by the team), statements
├── bob_sessions/
├── pyproject.toml
└── README.md
```

`../validators-history/` (outside the repo) is a full clone of python-validators, used only by `replay`.

## 4. Terms

| Term | Meaning |
|---|---|
| module | a row of `dataset/modules.csv`, e.g. `url`, `i18n/fr` |
| slug | module with `/` replaced by `__`, e.g. `i18n__fr` |
| mutant | the module's source with exactly one operator change |
| mutant ID | `<slug>:<line>:<col>:<end_line>:<end_col>:<op>`, e.g. `url:75:4:76:19:if_negate` |
| split | `A` (visible to agents) or `B` (held out), fixed per mutant ID |
| suite | `human`, `human+mh`, `human+b1` (mutation runs); `human`, `mh`, `b1` (replay) |
| killed / survivor | the suite fails, errors or times out / passes on the mutant |
| suspected violation | a test that fails on the current code; categorized in 6.5 |

## 5. Core package (`mutant_hunter`, no LLM)

### 5.1 Registry
- Source of truth: `dataset/modules.csv` (`module`, `source_path`, `test_path`, `set`, `specs`, `ref_mutants`, `ref_killed`).
- Target root `targets/validators`; Python `targets/validators/.venv/bin/python`.
- Suite paths, relative to the target root: `human` = `test_path`; `human+mh` adds `tests/mh/<slug>/`; `human+b1` adds `tests/b1/<slug>/`. A missing or empty folder means "no extra tests": print a warning and score the human tests alone.

### 5.2 Isolation — three silent failures to guard against
All three produced plausible but wrong numbers without any error.
1. **Editable install.** The venv imports the original code, so tests run in a copy still test the original. Always run with `PYTHONPATH=<copy>/src`. When creating a workspace, run `python -c "import validators; print(validators.__file__)"` and abort (exit 3) unless the path is inside the copy.
2. **Red baseline.** If the suite fails on the original, every mutant counts as killed. Before any run, the suite must pass on the original and on `ast.unparse(original)`; otherwise exit 2.
3. **Stale bytecode.** A mutant with the same file size, written in the same second as the previous version, loads the old `.pyc` and tests the wrong code. Always set `PYTHONDONTWRITEBYTECODE=1`, and never copy `__pycache__` into a workspace.

Also:
- Never edit the main tree. Each worker has its own temp copy of `src/` and `tests/`; restore the module after each mutant.
- If a run with at least 5 mutants kills none, exit 3 ("isolation suspected").
- `--jobs N` (default 4) must give exactly the same results as `--jobs 1`.

### 5.3 Mutation operators and IDs
Must match the reference values in `dataset/modules.csv` exactly.

| Op code | Node | Change |
|---|---|---|
| `cmp_<a>_to_<b>`, `#i` suffix for the i-th operator of a chained comparison (i ≥ 1) | `ast.Compare` | `<`↔`<=`, `>`↔`>=`, `==`↔`!=`, `in`↔`not in`, `is`↔`is not` |
| `bin_<a>_to_<b>` | `ast.BinOp` | `+`→`-`, `-`→`+`, `*`→`//`, `//`→`*`, `/`→`*`, `%`→`*` |
| `bool_and_to_or`, `bool_or_to_and` | `ast.BoolOp` | swap |
| `if_negate` | `ast.If` | `test` → `not (test)` |
| `int_plus_one` | `ast.Constant`, `type(value) is int` (not bool) | `n` → `n + 1` |
| `return_none` | `ast.Return` with a value | value → `None` |

- Enumerate points in `ast.walk` order; build each mutant from a fresh deep copy; mutants whose unparsed source does not compile are `invalid`.
- IDs include the end position, because nested expressions share a start position.
- Split: `B` if the first byte of `sha256(f"{seed}:{mutant_id}")` is odd, else `A`. Seed `20260925`.
- **Falsy-preserving flag**: `return_none` where the original is `return False`. validators turns any falsy result into a `ValidationError`, so these are equivalent unless the code compares with `is False`. The tool records them automatically in `results/equivalent/<slug>.json` with `kind: "falsy_preserving"`; agents never write reasons for them. They stay in the raw score and are excluded from the adjusted score.

### 5.4 Running one mutant
`python -m pytest -x -q -p no:cacheprovider <suite paths>` in the worker's copy, timeout 60 s. Exit 0 → survived; anything else → killed.

### 5.5 CLI
Global options `--jobs N` and `--seed N` are accepted before or after the subcommand. `cli.py` wires all six subcommands (and `--split C`) from M1 on, importing `report`, `replay`, `stats`, `backends.bob` and `exam_c` lazily; while a module does not exist yet, the subcommand prints "not implemented yet" and exits 1. This lets two people build those modules in parallel without touching `cli.py`.

| Command | Behavior |
|---|---|
| `baseline [--set main\|extra\|reference\|all\|<list>]` | coverage + all mutants with the human suite. Writes `results/baseline.csv` and `.md` with **counts only** (no survivor lists: they would reveal split B). Column `ref_match` compares with `ref_mutants`/`ref_killed`. |
| `mutate <module\|set\|list> [--suite S] [--split A\|B\|all]` | default split **A**. Writes `results/mutants/<slug>__<suite>__<split>.json`. Agents may use only split A. |
| `check <module> --test-file F [--repeat 3]` | runs F 3 times on the original; then, deselecting any failing tests, reports which split-A human survivors the passing tests kill (5.6). |
| `generate <module\|list> --suite mh\|b1 [--max-cost N]` | runs a backend (5.8). |
| `replay [--set ...] [--suite human,mh,b1]` | historical bug replay (7.4) → `results/replay.csv`. |
| `report` | `results/summary.csv`, `results/stats.md`, `docs/index.html`. |

Exit codes: 0 ok, 1 error, 2 baseline not green, 3 isolation suspected.

### 5.6 JSON formats
Mutation run: `module, slug, suite, split, seed, mutants, killed, survived, invalid, falsy_preserving, score, adjusted_score, seconds, results[{id, status}], survivors[{id, op, line, function, original, mutated, falsy_preserving, split}]`. `original`/`mutated` are the changed fragment, not the whole line.

`check` output:
```json
{"test_file": "tests/mh/url/test_url_userinfo.py", "passes_on_original": true, "runs": 3, "flaky": false,
 "collection_error": false, "survivors_checked": 15, "kills": ["url:75:4:76:19:if_negate"], "not_killed": ["..."],
 "kills_note": "", "failing_tests_on_original": ["test_R4_lt_in_username_rejected[us<er]"]}
```
Failing test IDs are complete, including parametrize IDs with spaces.

### 5.7 Statistics (stdlib only)
Wilson 95% interval for every proportion. Exact two-sided McNemar on paired suites (same mutants): b = killed only by suite 1, c = killed only by suite 2, p = min(1, 2·P(X ≤ min(b, c))), X ~ Bin(b + c, ½).

### 5.8 Backends
- `base.py`: `AgentBackend.generate_tests(work_package) -> list[Path]`; `record_cost(...)` appends to `results/costs_<member>.csv` (`timestamp, module, suite, backend, minutes, bobcoins, source`), one file per team member so two people never edit the same file; `report` reads every `results/costs*.csv`.
- `bob.py`: `bob run --mode agent --format json --max-cost N "<prompt>"` from the repo root; keeps stdout unedited in `results/raw/<UTC>__<slug>__<suite>.json`; returns new test files.
  - `mh`: `Use the mutant-hunter skill on the module <module>.`
  - `b1` (with `--disable-subagents`): `Write additional pytest tests for the module <module> of the validators package. Put them in targets/validators/tests/b1/<slug>/test_<slug>_b1.py. Make sure they pass.` Do not mention specs, survivors or results/.
- If `bob` is not installed, raise a clear error; the IDE path still works.

## 6. Bob layer

### 6.1 Skill procedure (`.bob/skills/mutant-hunter/SKILL.md`)
Input: one module. Never run `--split B` or `--split all`; never open `results/mutants/*__B.json`.
1. `mutanthunter mutate <module>` (split A, human suite).
2. **In parallel**, spawn two general subagents with the briefs in 6.2: `broad` and `spec`. Record the start time.
3. When both return, run `mutanthunter check` on every returned file. Move tests that fail on the original into `results/suspected_bugs/<slug>.md` (6.5), then re-check. Keep every file that passes 3 times.
3b. **Reconcile.** The broad subagent cannot see the specs, so it may pin a behavior the spec subagent reported as a violation. For every suspected violation, remove the broad test cases that assert the current behavior and note them in the violation entry. The spec wins.
4. `mutanthunter mutate <module> --suite human+mh`. If split-A survivors remain that are not falsy-preserving, spawn one `targeted` subagent (6.2) and repeat step 3 for its file. Skip it only when Bobcoins are tight.
5. Write `results/modules/<slug>.json` (6.6) and `results/equivalent/<slug>.json` (6.7).

This means 2–3 subagent spawns per module, each needing one approval in the IDE.

### 6.2 Subagent briefs
All three write only under `targets/validators/tests/mh/<slug>/`, with unique file names, and follow `.bob/rules/testing.md`.
- **broad**: "Write the regression tests a careful developer would add for the public functions of `<module>`: typical values, boundaries, options, error cases. Use the source, its docstrings and the existing tests. If a test you believe is correct fails on the current code, do not delete it: report it." File: `test_<slug>_broad.py`.
- **spec**: "Read the documents in the `specs` column (PDF in `dataset/specs/`, searchable text in `dataset/specs/txt/`). Write numbered rules R1…Rn with their source to `results/modules/<slug>_rules.md`, then tests whose expected results follow from those rules." Files: `test_<slug>_spec_<topic>.py`.
- **targeted**: receives the remaining split-A survivors and the rules file. "Pick public-API inputs that make each survivor's change observable. The expected result must come from a rule, the docstring, or — only when both are silent and no rule contradicts it — the current behavior, marked `Characterization:`. Mutants cluster: around every survivor's line, also test both sides of each comparison and the neighbouring values, because similar mutants you cannot see exist. If the only killing input would assert behavior the spec says is wrong, classify the survivor `blocked_by_bug`; otherwise `equivalent` or `spec_silent` with a reason." File: `test_<slug>_targeted.py`.

Each returns: files written, number of test functions, failing tests with the rule they rely on, and equivalence claims.

### 6.3 Rules (`.bob/rules/testing.md`)
- Never weaken, skip or delete an assertion to make a test pass. A test that fails on the current code is a suspected violation (6.5).
- Never modify `targets/*/src/`. Never use split B.
- Precedence of sources: spec document > the function's docstring > the existing human tests. Record conflicts as `spec-ambiguous`.
- Check digits and other algorithms may be computed by a small oracle function written in the test file from the spec's algorithm. It must not import or copy the module under test.
- Docstring first line: `Spec: <document> <section> — <rule ID>`, `Docstring: <function>`, or `Characterization: <reason>`.
- validators returns `True` or a falsy `ValidationError`: use `assert fn(x)` / `assert not fn(x)`, never `is False`.
- Public API only (`import validators`). Environment variables or options only if they are documented (docstring, README or docs/). No network, randomness or sleeps.
- File names are unique across the repo: `test_<slug>_<topic>.py`.
- Run pytest with `PYTHONDONTWRITEBYTECODE=1` (or only through `mutanthunter`).

### 6.4 Counting
- "Tests" means test functions (not files, not parametrized cases).
- Scores are reported raw and adjusted, always both.

### 6.5 Suspected violation entry (`results/suspected_bugs/<slug>.md`)
```
## <short title>
- Category: logic | data-staleness | spec-ambiguous | human-test-conflict
- Spec: <document> <section> — <rule ID>
- Input: `<value>` (several allowed)
- Spec says: valid | invalid | <value>
- Code returns: <value>
- Test: <self-contained test code, including any helper>
- Status: unconfirmed | confirmed | rejected
```
- `logic`: the code's algorithm is wrong (e.g. a checksum never verified).
- `data-staleness`: the code's tables are older than the spec snapshot (country or currency lists). Reported separately, never in the headline.
- `human-test-conflict`: an existing human test asserts something the spec contradicts.

### 6.6 Module result (`results/modules/<slug>.json`)
```json
{"module": "url", "spec_documents": ["rfc3986.pdf"], "rules_extracted": 0, "subagents": 0,
 "tests_generated": 0, "tests_kept": 0, "suspected_bugs": {"logic": 0, "data-staleness": 0, "spec-ambiguous": 0, "human-test-conflict": 0},
 "split_A": {"before": 0.0, "after": 0.0, "before_adjusted": 0.0, "after_adjusted": 0.0},
 "started_at": "<ISO time>", "finished_at": "<ISO time>", "minutes": 0.0, "bobcoins": null, "notes": ""}
```
`subagents` is the number actually spawned. Split B is never written here.

### 6.7 Equivalence records (`results/equivalent/<slug>.json`)
List of `{"id", "kind", "reason", "conditional_on"}` where `kind` is `falsy_preserving` (written by the tool), `equivalent` (no input changes the observable result), `blocked_by_bug` (killable only by a test that asserts a suspected violation; `conditional_on` names it) or `spec_silent` (killable, but no source defines the expected result).

## 7. Evaluation protocol

### 7.1 Suites
| Name | Tests | Produced by |
|---|---|---|
| B0 | human tests | the project |
| B1 | human + B1 tests | `mutanthunter generate <module> --suite b1`: one Bob agent, subagents disabled, the one-sentence prompt of 5.8 |
| MH | human + MH tests | the skill (6.1) |

### 7.2 Metrics
- Hold-out score on split B, raw and adjusted, per module and pooled over the 10 `main` modules.
- Extra kills = split-B mutants killed by MH and not by B1 (and the reverse).
- Suspected violations by category, and how many are confirmed by a human.
- Acceptance rate = tests kept / tests generated.
- Minutes and Bobcoins per module.

### 7.2b Hold-out discipline
- Score split B only after all test generation for that round is final.
- If tests are generated again after a split-B run (a new design iteration), first move every `*__B.json`, `summary.csv`, `stats.md` and `replay.csv` out of `results/` so agents cannot read them, and state in the README how many times split B was evaluated. Each extra evaluation is test-set reuse; report it, don't hide it.
- Never target a split-B number. Improve the pipeline on split A, then report whatever split B gives.

### 7.2c Exam C: an out-of-distribution hold-out
Split B is drawn from the same operator family the pipeline was tuned on, and every extra look at it is test-set reuse. Exam C is a second, independent exam made of operator types that are never used while building or tuning the pipeline:
- flip a boolean constant (`True` ↔ `False`);
- drop a `not`;
- string constant → `"XX" + s + "XX"` (skip docstrings, f-string parts, and elements of data tables with more than 8 entries);
- drop a no-argument `.lower()`, `.upper()`, `.strip()`, `.lstrip()`, `.rstrip()`, `.casefold()`, `.title()` call;
- `+=` ↔ `-=`.

Rules:
- Implement exam C only after all test generation is final (M4), in its own module `mutant_hunter/exam_c.py`, so no agent sees the operators while writing tests. Keep them out of sight until then: not in `mutate.py`, not in any file an agent reads while writing tests.
- Score B0, B1 and MH on exam C once and report it next to split B. It is the cleanest evidence the project has, because nothing was tuned on it.

### 7.3 Statistics
Every proportion as `k/n (p%, 95% CI a–b%)`. McNemar B1 vs MH on the pooled split-B mutants.

### 7.4 Historical bug replay
For each row of `dataset/bug_commits.csv`, run a suite against the pre-fix and the fix version of the module (each in a clean copy). Caught = a test fails on pre-fix and passes on fix. Rows whose tests cannot even be collected on one version are `not_replayable`.

How to read it (important):
- Tests written today encode today's (fixed) behavior. Any test that pins current behavior "catches" a reverted fix, so B1 and the human tests look good here for reasons that say nothing about finding bugs before release. Report B1 replay as context only, never as a comparison with MH.
- The meaningful replay result is the `extra` set: bugs that the human tests still miss today.
- For a stronger claim, run the spec subagent on the pre-fix version of `mac_address` and `hostname` and check whether it reports the bug as a suspected violation (optional, 7.5).
- Row `1231f6a` is spec-ambiguous; report it but do not count it.

### 7.5 Optional
- Pre-release replay (above) for the two `extra` bugs.
- Ablation: MH without the targeted step, or without subagents (`--disable-subagents`), on 3 modules.
- Generalization: `humanize` `number.py`.

## 8. Dashboard (`docs/index.html`)
One static file from `mutanthunter report`: inline SVG, no external scripts, light and dark mode, hover tooltips, readable at 500 px wide.
1. Hero: pooled hold-out score B0 → MH, with B1 and the 95% CI beside it.
2. Tiles: extra kills over B1; suspected violations (logic category); extra-set historical bugs caught.
3. Grouped bars per module: B0 / B1 / MH (legend + value labels on MH).
4. Per-module table (the table view of the chart).
5. Suspected violations: logic and human-test-conflict first; data-staleness collapsed.
6. Replay table with the reading notes of 7.4.
7. Method and limits.

## 9. Final results

### 9.1 Headline numbers (from `results/`, never typed by hand)
1. Pooled hold-out score, main set: B0 → B1 → MH, raw and adjusted, with CIs — on split B and on exam C.
2. Extra kills of MH over B1 (and the reverse), with the McNemar p-value.
3. Suspected violations by category; confirmed logic bugs listed by name.
4. Extra-set historical bugs caught by MH (k of 2).
5. Acceptance rate; median minutes and Bobcoins per module.

### 9.2 `summary.csv`
`module, set, suite, split, mutants, killed, score, ci_low, ci_high, adjusted_score, falsy_preserving, tests_kept, suspected_bugs, minutes, bobcoins`

## 10. README outline (M5)
1. One-line pitch, demo URL.
2. The problem: coverage vs mutation score (`url.py`: 91.9% line+branch coverage, 35/58 mutants killed by the human tests).
3. How it works: section 0 and one diagram.
4. Results: `stats.md` tables, with the reading notes of 7.4.
5. Confirmed bugs found, each with the responsible code line and a link to any existing upstream issue.
6. How IBM Bob was used: `docs/bob_usage.md`, `bob_sessions/`.
7. Reproduce: setup, `mutanthunter baseline`, `mutanthunter report`.
8. Limits and threats to validity. Data sources: `dataset/SOURCES.md`.

## 11. Milestone acceptance

| Milestone | Accept when |
|---|---|
| M0 | plan covers sections 5–9; no code written |
| M1 | `baseline --set all` gives `ref_match = yes` for all 24 modules; `--jobs 1` and `--jobs 8` give identical results on `url`; unit tests pass, including one each for exit codes 2 and 3 and one for unique IDs on nested expressions |
| M2 | skill runs on `url` in one request; broad and spec subagents ran in parallel; `results/modules/url.json` complete; split-A score went up |
| M3 | every `main` and `extra` module has MH and B1 tests; split-B runs for 3 suites; `summary.csv` and `docs/index.html` exist |
| M4 | exam C implemented after generation and scored for B0, B1 and MH; `replay.csv` and `stats.md` exist; every headline number has n and a CI; at least one logic violation confirmed by reading the code |
| M5 | README, both statements (500 words or fewer), `bob_sessions/` complete, GitHub Pages live |

## 12. Minimum viable version and fallbacks

| Level | Contents |
|---|---|
| 1 (must) | M1 harness; skill on `url` with broad + spec subagents; split A and B before/after; suspected violations for `url` |
| 2 | 4–6 main modules including `finance`; B1 for the same; summary and dashboard |
| 3 | all 10 main modules + 2 extra; McNemar |
| 4 (full) | exam C; replay; stats; confirmed bugs; optional pre-release replay |

Fallbacks:
- Subagents not spawned in parallel from the skill → one IDE task per subagent role in the background, or parallel `bob run` processes.
- No `bob` CLI → run the skill and the B1 prompt in the IDE, one task per module; copy costs from the task summaries.
- Bobcoins low → drop a level; keep enough for the demo recording.
- A spec PDF too long → search `dataset/specs/txt/` first, then read only the relevant PDF pages.
