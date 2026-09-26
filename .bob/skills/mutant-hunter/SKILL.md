---
name: mutant-hunter
description: >
  Run the full MutantHunter pipeline on one Python module from the validators
  package. Trigger phrase: "Use the mutant-hunter skill on the module <module>."
input:
  module: name from dataset/modules.csv (e.g. url, domain, i18n/fi)
---

# MutantHunter Skill

## Constraints (read first, never violate)

- **Never** run `--split B` or `--split all`.  
- **Never** open, read or reference any file matching `results/mutants/*__B.json`.  
- **Never** modify `targets/*/src/`.  
- **Never** write under `targets/validators/tests/b1/` (track B owns that path).  
- Follow `.bob/rules/testing.md` for every test file written by any subagent.

---

## Inputs

```
module  = <module>                          # e.g. "url"
slug    = module.replace("/", "__")         # e.g. "url", "i18n__fi"
```

---

## Step 1 — Baseline mutation run (split A, human suite)

```
python -c "import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))"
mutanthunter mutate <module>
```

Run the `python` timestamp command **first** (before `mutanthunter mutate`) and save its
output as `started_at`.
This writes `results/mutants/<slug>__human__A.json`.
Record the baseline split-A score (`score` and `adjusted_score`) from that
file. These are the **before** numbers.

If the file already exists and was written in this session, skip re-running
(but you still need a real `started_at` — read the file's mtime using Python:
`python -c "import os, datetime; t=os.path.getmtime('results/mutants/<slug>__human__A.json'); print(datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))"`).

---

## Step 2 — Parallel subagents: broad + spec

**Spawn both subagents in parallel within this task** (Bob's native parallel
subagent mechanism, not two separate IDE tasks). Record the spawns in the
task's subagent counter.

### Brief for the `broad` subagent

> Write the regression tests a careful developer would add for the public
> functions of `<module>` in the validators package:
> typical values, boundaries, edge cases, option combinations, and error cases.
>
> Use the module source at `targets/validators/src/validators/<source_path>`,
> its docstrings, and the existing human tests at `targets/validators/<test_path>`.
>
> Put all tests in a **single file**:
> `targets/validators/tests/mh/<slug>/test_<slug>_broad.py`
>
> If a test you believe is correct fails on the current code, **do not delete
> it**. Instead report it as a potential issue: include the test unchanged and
> note it in your return message under "Failing tests".
>
> Follow `.bob/rules/testing.md` (including rule 11: **no `__init__.py`**).
>
> Return:
> - files written
> - number of test functions written
> - list of tests that fail on the current code, each with the assertion and why you believe it is correct

### Brief for the `spec` subagent

> Read the specification documents listed for module `<module>` in
> `dataset/modules.csv` (column `specs`). PDF files are at
> `dataset/specs/<filename>`; searchable plain text versions are at
> `dataset/specs/txt/<filename>.txt` — prefer the txt versions for speed.
>
> First write numbered rules **R1…Rn** with their source reference
> (document + section) to `results/modules/<slug>_rules.md`.
>
> Then write test files whose **expected results follow directly from those
> rules**. For each test function add a docstring whose first line is:
> `Spec: <document> <section> — <rule ID>`
>
> Put test files under `targets/validators/tests/mh/<slug>/`, one file per
> topic, named `test_<slug>_spec_<topic>.py`.
>
> If a test that follows from the spec fails on the current code, **do not
> delete it**. Report it under "Failing tests" in your return message, with
> the rule it relies on.
>
> Follow `.bob/rules/testing.md` (including rule 11: **no `__init__.py`**).
>
> Return:
> - files written
> - number of rules extracted
> - number of test functions written
> - list of tests that fail on the current code, each with: the test, the rule it relies on, what the spec says, what the code returns

---

## Step 3 — Accept, classify, reconcile

For every file returned by both subagents, run:

```bash
mutanthunter check <module> --test-file <path>
```

### 3a — Suspected violations

Any test that **fails on the current code** is a **suspected violation**.
Do NOT delete it. Instead:

1. Move it (copy the test body) into `results/suspected_bugs/<slug>.md` using
   the template from spec 6.5:

   ```
   ## <short title>
   - Category: logic | data-staleness | spec-ambiguous | human-test-conflict
   - Spec: <document> <section> — <rule ID>
   - Input: `<value>`
   - Spec says: valid | invalid | <value>
   - Code returns: <value>
   - Test: <self-contained test code, including any helper>
   - Status: unconfirmed
   ```

   Categories:
   - `logic` — the code's algorithm is wrong (checksum never verified, wrong boundary, etc.)
   - `data-staleness` — the code's tables are older than the spec snapshot
   - `spec-ambiguous` — the spec and the existing human tests contradict each other
   - `human-test-conflict` — an existing human test asserts something the spec contradicts

2. Remove the failing test from the test file (or comment it out with a note),
   then re-run `mutanthunter check` on the cleaned file.

3. Keep every test that passes on the original code 3 times in a row.

### 3b — Reconcile broad vs spec (spec wins)

After both subagents have returned and suspected violations are recorded:

1. For every entry in `results/suspected_bugs/<slug>.md`, examine the broad
   test file for test cases that assert the **current (possibly wrong) behavior**
   for the same input.
2. Remove those broad test cases from `test_<slug>_broad.py`.
3. Add a note to the violation entry:
   ```
   - Broad-test removed: `<test function name>` — asserted current behavior
   ```
4. The spec test (which fails) remains in `suspected_bugs` and is **not** added
   to the `tests/mh/` folder until the bug is confirmed and fixed upstream.

---

## Step 4 — Targeted subagent (split-A survivors)

Run:

```bash
mutanthunter mutate <module> --suite human+mh
```

This writes `results/mutants/<slug>__human+mh__A.json`.

Read the `survivors` array. Remove any entry where `falsy_preserving` is `true`.

If **any non-falsy-preserving split-A survivors remain**, and Bobcoins allow it,
**spawn one `targeted` subagent** within this task:

### Brief for the `targeted` subagent

> You are given the split-A survivors still alive after the human + MH tests,
> and the rules file for module `<module>`.
>
> **Survivors:**
> ```json
> <paste the survivors array from results/mutants/<slug>__human+mh__A.json,
>  filtering out falsy_preserving=true entries>
> ```
>
> **Rules file:** `results/modules/<slug>_rules.md`
>
> For each survivor:
> - Pick public-API inputs (`import validators`) that make the survivor's change
>   observable.
> - The expected result **must** come from a rule in the rules file, the
>   function's docstring, or — only when both are silent and no rule contradicts
>   it — the current behavior, marked `Characterization:` in the test docstring.
> - Mutants cluster: around every survivor's line, also test **both sides** of
>   each comparison and the neighbouring values, because similar hidden mutants
>   exist nearby.
> - If the only killing input would assert behavior the spec says is wrong:
>   classify the survivor `blocked_by_bug` (name the suspected violation).
> - If no public input can distinguish the mutant from the original:
>   classify it `equivalent` with a reason.
> - If killable but no source (spec, docstring, human test) defines the expected
>   result: classify it `spec_silent` with a reason.
>
> Put the tests in:
> `targets/validators/tests/mh/<slug>/test_<slug>_targeted.py`
>
> Follow `.bob/rules/testing.md` (including rule 11: **no `__init__.py`**).
>
> Return:
> - files written
> - number of test functions written
> - equivalence claims: list of `{"id", "kind", "reason", "conditional_on"}`
> - failing tests on the current code (same format as step 2)

After the targeted subagent returns, run step 3 again (accept / classify /
reconcile) for `test_<slug>_targeted.py`.

---

## Step 5 — Write result files

Before writing `results/modules/<slug>.json`, run:

```
python -c "import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))"
```

Compute `minutes` as `(finished_at − started_at)` in minutes (round to one
decimal place).

### `results/modules/<slug>.json`

Write the following JSON (all fields required, spec 6.6):

```json
{
  "module": "<module>",
  "spec_documents": ["<list from dataset/modules.csv specs column>"],
  "rules_extracted": <int — from spec subagent return message>,
  "subagents": <int — number actually spawned (2 or 3)>,
  "tests_generated": <int — total test functions from all subagents before filtering>,
  "tests_kept": <int — test functions kept after step 3>,
  "suspected_bugs": {
    "logic": <int>,
    "data-staleness": <int>,
    "spec-ambiguous": <int>,
    "human-test-conflict": <int>
  },
  "split_A": {
    "before": <float — score from step 1>,
    "after":  <float — score from results/mutants/<slug>__human+mh__A.json>,
    "before_adjusted": <float>,
    "after_adjusted":  <float>
  },
  "started_at": "<ISO 8601 UTC from step 1>",
  "finished_at": "<ISO 8601 UTC now>",
  "minutes": <float — elapsed wall-clock minutes>,
  "bobcoins": null,
  "notes": ""
}
```

**Never** write split-B numbers here.

### `results/equivalent/<slug>.json`

Merge the tool's existing `falsy_preserving` entries (already in the file)
with the targeted subagent's equivalence claims. Produce a JSON array of:

```json
{"id": "<mutant id>", "kind": "<falsy_preserving|equivalent|blocked_by_bug|spec_silent>",
 "reason": "<one sentence>", "conditional_on": "<violation title or null>"}
```

Do **not** remove existing `falsy_preserving` entries.

---

## Counting rules (spec 6.4)

- "Tests" = test functions, not files, not parametrized cases.
- Report scores raw and adjusted, always both.
- `subagents` = number actually spawned in this run (2 if targeted was skipped,
  3 if all three ran).
