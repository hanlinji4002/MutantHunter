# Use the mutant-hunter skill on the module finance. Bobcoins are tight: skip the targeted step.

---

**Status:** active  **Date:** 2026-09-26

---

### 👤 User

Use the mutant-hunter skill on the module finance. Bobcoins are tight: skip the targeted step.

---

### 🤖 Assistant

> 🔧 called: use_skill



> 🔧 **use_skill** — mutant-hunter

### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[-] Step 1: Baseline mutation run (split A, human suite) for module `finance`
[ ] Step 2: Spawn broad + spec subagents in parallel
[ ] Step 3: Accept, classify, reconcile test results
[ ] Step 4: SKIPPED (targeted step skipped per user instruction)
[ ] Step 5: Write result files (slug.json, equivalent/slug.json)


### 🤖 Assistant

> 🔧 called: execute_command, grep

First, let me gather some context about the `finance` module before running the baseline.

> 🔧 **execute_command** — python -c "import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))"

> 🔧 **grep** — finance

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — python3 -c "import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))"

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — py -c "import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))"

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — mutanthunter --version

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — Get-Command mutanthunter -ErrorAction SilentlyContinue; Get-Command python -ErrorAction SilentlyContinue; Get-Command python3 -ErrorAction SilentlyContinue; $env:PATH -split ";" | Select-Object -First 20

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — Get-ChildItem "C:\Users\Z2006\.local\bin" | Select-Object Name

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — & "C:\Users\Z2006\.local\bin\python3.12.exe" -c "import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))"

### 🤖 Assistant

> 🔧 called: execute_command

`started_at = 2026-09-26T07:01:17Z`. Now run the baseline mutation.

> 🔧 **execute_command** — & "C:\Users\Z2006\.local\bin\uvx.exe" mutanthunter mutate finance 2>&1

### 🤖 Assistant

> 🔧 called: glob, list_files



> 🔧 **list_files** — .

> 🔧 **glob** — **/*.cfg

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — pyproject.toml

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — & "C:\Users\Z2006\.local\bin\python3.12.exe" -m mutant_hunter.cli mutate finance 2>&1

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — results/mutants/finance__human__A.json

### 🤖 Assistant

> 🔧 called: read_file, read_file

Baseline recorded: **score = 0.689**, **adjusted_score = 0.724**. Now let me read the source and existing tests before spawning subagents.

> 🔧 **read_file** — targets/validators/src/validators/finance.py

> 🔧 **read_file** — targets/validators/tests/test_finance.py

### 🤖 Assistant

> 🔧 called: list_files

Now let me also quickly check for the spec documents before spawning subagents.

> 🔧 **list_files** — dataset/specs/txt

### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[x] Step 1: Baseline mutation run (split A, human suite) for module `finance`
[-] Step 2: Spawn broad + spec subagents in parallel
[ ] Step 3: Accept, classify, reconcile test results
[ ] Step 4: SKIPPED (targeted step skipped per user instruction)
[ ] Step 5: Write result files (slug.json, equivalent/slug.json)


### 🤖 Assistant

> 🔧 called: spawn_subagent, spawn_subagent

Now spawning both subagents in parallel:

> 🔧 **spawn_subagent** — general

> 🔧 **spawn_subagent** — general

### 🤖 Assistant

> 🔧 called: update_todo_list

Both subagents returned. Key findings:
- **Broad**: 64 tests, all passing. Two tests document the ISIN checksum bug (pass because of the bug).
- **Spec**: 62 tests, **4 failing** — all due to the same `_isin_checksum` bug (check accumulator never updated). These are suspected violations.

Now let me run `mutanthunter check` on all test files:

> 🔧 **update_todo_list** — 
[x] Step 1: Baseline mutation run (split A, human suite) for module `finance`
[x] Step 2: Spawn broad + spec subagents in parallel
[-] Step 3: Accept, classify, reconcile test results
[ ] Step 4: SKIPPED (targeted step skipped per user instruction)
[ ] Step 5: Write result files (slug.json, equivalent/slug.json)


### 🤖 Assistant

> 🔧 called: read_file, read_file

First, let me verify the test files and check the broad and spec files before running:

> 🔧 **read_file** — targets/validators/tests/mh/finance/test_finance_broad.py

> 🔧 **read_file** — targets/validators/tests/mh/finance/test_finance_spec_isin.py

### 🤖 Assistant

> 🔧 called: read_file, read_file

Now I need to check the spec test files for CUSIP and SEDOL, and the rules file:

> 🔧 **read_file** — targets/validators/tests/mh/finance/test_finance_spec_sedol.py

> 🔧 **read_file** — targets/validators/tests/mh/finance/test_finance_spec_cusip.py

### 🤖 Assistant

> 🔧 called: execute_command

Now let me run `mutanthunter check` on all four test files:

> 🔧 **execute_command** — & "C:\Users\Z2006\.local\bin\python3.12.exe" -m mutant_hunter.cli check finance --test-file targets/validators/tests/mh/finance/test_finance_broad.py 2>&1

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — & "C:\Users\Z2006\.local\bin\python3.12.exe" -m mutant_hunter.cli check finance --test-file targets/validators/tests/mh/finance/test_finance_spec_cusip.py 2>&1

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — & "C:\Users\Z2006\.local\bin\python3.12.exe" -m mutant_hunter.cli check finance --test-file targets/validators/tests/mh/finance/test_finance_spec_isin.py 2>&1

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — & "C:\Users\Z2006\.local\bin\python3.12.exe" -m mutant_hunter.cli check finance --test-file targets/validators/tests/mh/finance/test_finance_spec_sedol.py 2>&1

### 🤖 Assistant

> 🔧 called: read_file

The spec ISIN file has 4 failing tests. Now I need to:
1. Move the failing tests into `results/suspected_bugs/finance.md` 
2. Remove them from the ISIN spec test file 
3. Also handle the broad file — the two "bug documenting" tests that assert the **current wrong behavior** of ISIN

Let me also check the rules file:

> 🔧 **read_file** — results/modules/finance_rules.md

### 🤖 Assistant

> 🔧 called: write_file

Now I have all the information needed. Let me process step 3:

**Suspected violations** — 4 failing tests from `test_finance_spec_isin.py` (all same root cause: `_isin_checksum` never accumulates into `check`).

**Broad test reconciliation** — the broad file has 2 tests that assert the *current wrong behavior*: `test_isin_12_letter_string_passes_due_to_bug` and `test_isin_wrong_checksum_passes_due_to_bug`. These must be removed from the broad file.

Let me do all of this now:

> 🔧 **write_file** — results/suspected_bugs/finance.md

### 🤖 Assistant

> 🔧 called: apply_diff

Now remove the 4 failing tests from the spec ISIN file and remove the 2 wrong-behavior tests from the broad file:

> 🔧 **apply_diff** — targets/validators/tests/mh/finance/test_finance_spec_isin.py

### 🤖 Assistant

> 🔧 called: apply_diff

Now remove the two bug-asserting tests from the broad file (they assert current broken behavior which conflicts with the spec violations we've recorded):

> 🔧 **apply_diff** — targets/validators/tests/mh/finance/test_finance_broad.py

### 🤖 Assistant

> 🔧 called: execute_command

Now re-run `mutanthunter check` on both cleaned files to confirm they pass on original:

> 🔧 **execute_command** — & "C:\Users\Z2006\.local\bin\python3.12.exe" -m mutant_hunter.cli check finance --test-file targets/validators/tests/mh/finance/test_finance_spec_isin.py 2>&1

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — & "C:\Users\Z2006\.local\bin\python3.12.exe" -m mutant_hunter.cli check finance --test-file targets/validators/tests/mh/finance/test_finance_broad.py 2>&1

### 🤖 Assistant

> 🔧 called: update_todo_list

Both files pass on the original, 3 times in a row. Now let's run the combined `human+mh` mutation:

> 🔧 **update_todo_list** — 
[x] Step 1: Baseline mutation run (split A, human suite) for module `finance`
[x] Step 2: Spawn broad + spec subagents in parallel
[x] Step 3: Accept, classify, reconcile test results
[-] Step 4: SKIPPED — but must run human+mh mutation to get after scores
[ ] Step 5: Write result files (slug.json, equivalent/slug.json)


### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — & "C:\Users\Z2006\.local\bin\python3.12.exe" -m mutant_hunter.cli mutate finance --suite human+mh 2>&1

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — results/mutants/finance__human+mh__A.json

### 🤖 Assistant

> 🔧 called: glob, execute_command

After scores: **score = 0.820**, **adjusted_score = 0.862**. 

Now I have all the data. Let me compute the counts:
- Tests generated: broad 64 + spec 62 = **126**
- Tests removed from broad (bug-asserting): 2
- Tests removed from spec (failed on original): 4
- Tests kept: 64-2 + 62-4 = 62 + 58 = **120**
- Rules extracted: **33**
- Subagents spawned: **2** (broad + spec; targeted skipped)
- Suspected bugs: logic = 4, total all categories = 4

Let me check the existing equivalent file:

> 🔧 **glob** — results/equivalent/finance.json

> 🔧 **execute_command** — & "C:\Users\Z2006\.local\bin\python3.12.exe" -c "import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))"

### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[x] Step 1: Baseline mutation run (split A, human suite) for module `finance`
[x] Step 2: Spawn broad + spec subagents in parallel
[x] Step 3: Accept, classify, reconcile test results
[x] Step 4: SKIPPED — human+mh mutation run done for after scores
[-] Step 5: Write result files (slug.json, equivalent/slug.json)


### 🤖 Assistant

> 🔧 called: write_file, write_file

`finished_at = 2026-09-26T07:11:06Z`, `started_at = 2026-09-26T07:01:17Z` → elapsed = ~9.8 minutes.

> 🔧 **write_file** — results/modules/finance.json

> 🔧 **write_file** — results/equivalent/finance.json

### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[x] Step 1: Baseline mutation run (split A, human suite) for module `finance`
[x] Step 2: Spawn broad + spec subagents in parallel
[x] Step 3: Accept, classify, reconcile test results
[x] Step 4: SKIPPED — human+mh mutation run done for after scores
[x] Step 5: Write result files (slug.json, equivalent/slug.json)


### 🤖 Assistant

All done. Here's the full summary for the `finance` module run:

---

## MutantHunter — `finance` — Run Summary

### Score improvement (split A)
| | Before | After |
|---|---|---|
| Score | 0.689 | **0.820** (+0.131) |
| Adjusted score | 0.724 | **0.862** (+0.138) |

### Tests
- **120 tests kept** across 4 files:
  - [`test_finance_broad.py`](targets/validators/tests/mh/finance/test_finance_broad.py) — 62 tests (2 removed: asserted current buggy ISIN behavior)
  - [`test_finance_spec_cusip.py`](targets/validators/tests/mh/finance/test_finance_spec_cusip.py) — 25 tests
  - [`test_finance_spec_isin.py`](targets/validators/tests/mh/finance/test_finance_spec_isin.py) — 15 tests (4 removed: failed on original)
  - [`test_finance_spec_sedol.py`](targets/validators/tests/mh/finance/test_finance_spec_sedol.py) — 18 tests
- 33 rules extracted from CUSIP/ISIN/SEDOL Wikipedia specs

### Suspected bugs — 4 × `logic` → [`results/suspected_bugs/finance.md`](results/suspected_bugs/finance.md)

All 4 trace to the **same root cause**: [`_isin_checksum`](targets/validators/src/validators/finance.py:51) iterates over all 12 characters computing `val`, but **never adds `val` to `check`**. The accumulator stays `0`, so `(0 % 10) == 0` is always `True`. Consequences:

| Input | Spec says | Code returns |
|---|---|---|
| `"US0378331006"` (wrong Apple check digit) | invalid | `True` |
| `"AU0000XVGZA4"` (wrong Treasury check digit) | invalid | `True` |
| `"GB0002634947"` (wrong BAE Systems check digit) | invalid | `True` |
| `"US037833100A"` (last char is letter, not digit) | invalid | `True` |

### Equivalent mutants — [`results/equivalent/finance.json`](results/equivalent/finance.json)
3 `falsy_preserving` entries: `return None` vs `return False` in `sedol()` and `_cusip_checksum()` — both are falsy and the `@validator` decorator treats them identically.