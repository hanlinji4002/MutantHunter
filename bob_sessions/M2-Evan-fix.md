# Two fixes to the mutant-hunter skill before running more modules:
1. Delete targets/validators/tests/mh/url/__init__.py and never create __init__.py anywhere under tests/mh/ or tests/b1/. With an __init__.py, pytest imports the folder as a top-level package named after the slug; for uuid and email that shadows the standard-library modules and every test fails at collection (verified: a tests/mh/uuid/__init__.py makes `import validators` fail). Test file names are already unique, so no __init__.py is needed. Add this rule to .bob/rules/testing.md and to every subagent brief in .bob/skills/mutant-hunter/SKILL.md.
2. results/modules/url.json has invented timestamps (2025-07-14) and an invented duration. In SKILL.md, make step 1 and step 5 run `date -u +%Y-%m-%dT%H:%M:%SZ` in the terminal and use its output for started_at and finished_at, and compute minutes from them. For url, replace the invented values with the modification time of the earliest file in targets/validators/tests/mh/url/ and of results/modules/url.json, and say so in notes.
Then run `cd targets/validators && PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q tests/test_url.py tests/mh/url/` and `mutanthunter mutate url --suite human+mh` to confirm nothing else changed (21/32 on split A).

---

**Status:** active  **Date:** 2026-09-26

---

### 👤 User

Two fixes to the mutant-hunter skill before running more modules:
1. Delete targets/validators/tests/mh/url/__init__.py and never create __init__.py anywhere under tests/mh/ or tests/b1/. With an __init__.py, pytest imports the folder as a top-level package named after the slug; for uuid and email that shadows the standard-library modules and every test fails at collection (verified: a tests/mh/uuid/__init__.py makes `import validators` fail). Test file names are already unique, so no __init__.py is needed. Add this rule to .bob/rules/testing.md and to every subagent brief in .bob/skills/mutant-hunter/SKILL.md.
2. results/modules/url.json has invented timestamps (2025-07-14) and an invented duration. In SKILL.md, make step 1 and step 5 run `date -u +%Y-%m-%dT%H:%M:%SZ` in the terminal and use its output for started_at and finished_at, and compute minutes from them. For url, replace the invented values with the modification time of the earliest file in targets/validators/tests/mh/url/ and of results/modules/url.json, and say so in notes.
Then run `cd targets/validators && PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q tests/test_url.py tests/mh/url/` and `mutanthunter mutate url --suite human+mh` to confirm nothing else changed (21/32 on split A).

---

### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[-] Read current SKILL.md and testing.md to understand what needs to change
[ ] Delete targets/validators/tests/mh/url/__init__.py
[ ] Add "no __init__.py" rule to .bob/rules/testing.md
[ ] Update SKILL.md: add no-__init__.py rule to all subagent briefs
[ ] Update SKILL.md: step 1 and step 5 use `date -u` for timestamps
[ ] Fix results/modules/url.json with real timestamps
[ ] Run pytest to confirm tests pass
[ ] Run mutanthunter mutate to confirm 21/32


### 🤖 Assistant

> 🔧 called: read_file, read_file, execute_command



> 🔧 **read_file** — .bob/skills/mutant-hunter/SKILL.md

> 🔧 **read_file** — .bob/rules/testing.md

> 🔧 **execute_command** — ls -la targets/validators/tests/mh/url/

### 🤖 Assistant

> 🔧 called: execute_command, read_file

Now let me get the real timestamps and read url.json:

> 🔧 **execute_command** — date -u +%Y-%m-%dT%H:%M:%SZ && stat -f "%Sm" -t "%Y-%m-%dT%H:%M:%SZ" targets/validators/tests/mh/url/__init__.py && stat -f "%Sm" -t "%Y-%m-%dT%H:%M:%SZ" results/modules/url.json

> 🔧 **read_file** — results/modules/url.json

### 🤖 Assistant

> 🔧 called: update_todo_list

The `__init__.py` was created at `2026-09-26T12:42:39Z` (earliest file in the url dir) and `url.json` was last modified at `2026-09-26T12:55:46Z`. Now I have everything I need. Let me make all the changes in parallel:

> 🔧 **update_todo_list** — 
[x] Read current SKILL.md and testing.md to understand what needs to change
[-] Delete targets/validators/tests/mh/url/__init__.py
[-] Add "no __init__.py" rule to .bob/rules/testing.md
[-] Update SKILL.md: add no-__init__.py rule to all subagent briefs
[-] Update SKILL.md: step 1 and step 5 use `date -u` for timestamps
[-] Fix results/modules/url.json with real timestamps
[ ] Run pytest to confirm tests pass
[ ] Run mutanthunter mutate to confirm 21/32


### 🤖 Assistant

> 🔧 called: execute_command, apply_diff, apply_diff



> 🔧 **execute_command** — rm targets/validators/tests/mh/url/__init__.py

> 🔧 **apply_diff** — .bob/rules/testing.md

> 🔧 **apply_diff** — results/modules/url.json

### 🤖 Assistant

> 🔧 called: apply_diff

Now update SKILL.md — step 1 (add `date -u` for `started_at`), step 5 (add `date -u` for `finished_at`), and all three subagent briefs (add no `__init__.py` rule):

> 🔧 **apply_diff** — .bob/skills/mutant-hunter/SKILL.md

### 🤖 Assistant

> 🔧 called: update_todo_list

All file changes are done. Now run the validation steps:

> 🔧 **update_todo_list** — 
[x] Read current SKILL.md and testing.md to understand what needs to change
[x] Delete targets/validators/tests/mh/url/__init__.py
[x] Add "no __init__.py" rule to .bob/rules/testing.md
[x] Update SKILL.md: add no-__init__.py rule to all subagent briefs
[x] Update SKILL.md: step 1 and step 5 use `date -u` for timestamps
[x] Fix results/modules/url.json with real timestamps
[-] Run pytest to confirm tests pass
[ ] Run mutanthunter mutate to confirm 21/32


### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — cd targets/validators && PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q tests/test_url.py tests/mh/url/

### 🤖 Assistant

> 🔧 called: update_todo_list

369 tests pass. Now the mutation run:

> 🔧 **update_todo_list** — 
[x] Read current SKILL.md and testing.md to understand what needs to change
[x] Delete targets/validators/tests/mh/url/__init__.py
[x] Add "no __init__.py" rule to .bob/rules/testing.md
[x] Update SKILL.md: add no-__init__.py rule to all subagent briefs
[x] Update SKILL.md: step 1 and step 5 use `date -u` for timestamps
[x] Fix results/modules/url.json with real timestamps
[x] Run pytest to confirm tests pass
[-] Run mutanthunter mutate to confirm 21/32


### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — mutanthunter mutate url --suite human+mh

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — which mutanthunter || python -m mutant_hunter --help 2>/dev/null | head -3 || ls mutant_hunter/

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — ls && cat pyproject.toml | head -30

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — pip show mutant-hunter 2>/dev/null | grep Location || python -c "import mutant_hunter; print('found')" 2>/dev/null || echo "not installed"

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — python -m mutant_hunter.cli mutate url --suite human+mh 2>&1 | tail -20

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — python -c "
import json
with open('results/mutants/url__human+mh__A.json') as f:
    d = json.load(f)
print('score:', d['score'])
print('adjusted_score:', d['adjusted_score'])
survivors = [s for s in d.get('survivors', []) if not s.get('falsy_preserving')]
print('non-falsy survivors:', len(survivors))
total = d.get('total_mutants', '?')
killed = d.get('killed', '?')
print(f'killed/total: {killed}/{total}')
"

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — python -c "
import json
with open('results/mutants/url__human+mh__A.json') as f:
    d = json.load(f)
print('total mutants:', len(d.get('survivors', [])) + d.get('killed', 0))
print('killed:', d.get('killed'))
"

### 🤖 Assistant

> 🔧 called: update_todo_list

21/32 confirmed. All done.

> 🔧 **update_todo_list** — 
[x] Read current SKILL.md and testing.md to understand what needs to change
[x] Delete targets/validators/tests/mh/url/__init__.py
[x] Add "no __init__.py" rule to .bob/rules/testing.md
[x] Update SKILL.md: add no-__init__.py rule to all subagent briefs
[x] Update SKILL.md: step 1 and step 5 use `date -u` for timestamps
[x] Fix results/modules/url.json with real timestamps
[x] Run pytest to confirm tests pass (369 passed)
[x] Run mutanthunter mutate to confirm 21/32


### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[x] Read current SKILL.md and testing.md to understand what needs to change
[x] Delete targets/validators/tests/mh/url/__init__.py
[x] Add "no __init__.py" rule to .bob/rules/testing.md
[x] Update SKILL.md: add no-__init__.py rule to all subagent briefs
[x] Update SKILL.md: step 1 and step 5 use `date -u` for timestamps
[x] Fix results/modules/url.json with real timestamps
[x] Run pytest to confirm tests pass
[x] Run mutanthunter mutate to confirm 21/32


### 🤖 Assistant

All done. Summary of every change made:

---

**Fix 1 — No `__init__.py`**

- Deleted [`targets/validators/tests/mh/url/__init__.py`](targets/validators/tests/mh/url/__init__.py)
- Added **rule 11** to [`.bob/rules/testing.md`](.bob/rules/testing.md): never create `__init__.py` under `tests/mh/` or `tests/b1/` — explains the shadowing problem for slugs like `uuid`/`email`
- Updated all three subagent briefs in [`.bob/skills/mutant-hunter/SKILL.md`](.bob/skills/mutant-hunter/SKILL.md) (broad, spec, targeted) to say `Follow .bob/rules/testing.md (including rule 11: no __init__.py)`

**Fix 2 — Real timestamps**

- Step 1 in `SKILL.md` now runs `date -u +%Y-%m-%dT%H:%M:%SZ` **before** `mutanthunter mutate` and saves the output as `started_at`; includes fallback via `stat -f "%Sm"` if the file already exists
- Step 5 in `SKILL.md` now runs `date -u` to capture `finished_at` and computes `minutes` from the two values before writing the JSON
- [`results/modules/url.json`](results/modules/url.json) updated:
  - `started_at`: `2026-09-26T12:42:39Z` (mtime of the now-deleted `__init__.py`, earliest file in the url dir)
  - `finished_at`: `2026-09-26T12:55:46Z` (mtime of `url.json` itself)
  - `minutes`: `13.2` (computed from those two values)
  - `notes` records the correction and source of each value

**Validation**

- `pytest`: **369 passed** in 0.15s
- `mutanthunter mutate url --suite human+mh`: **21/32 killed**, score 0.656, adjusted 0.700 — unchanged ✓