# Implement mutant_hunter/replay.py (section 7.4 of @/docs/SPEC.md) using the Workspace class in mutant_hunter/isolation.py: replay.replay(which: str, suites: list[str]) -> list[dict], writing results/replay.csv. Suites are human, mh and b1 (the generated tests alone); a module without mh or b1 tests gets an empty result for that suite, not an error. The history clone is ../validators-history. This machine runs Windows.
Run `mutanthunter replay --set all --suite human,mh,b1` and check that the human rows match the human_tests_at_HEAD column of dataset/bug_commits.csv.
Then add the replay table to report.py (section 8, item 6) with the reading notes of section 7.4. In the same change, fix two dashboard issues: at 500 px the per-module table overflows to the right (wrap it in a horizontally scrollable container), and stats.md prints "no paired data yet" when paired data exist but b = c = 0 (print b, c and p instead). Then run `mutanthunter report`. Do not run --split B or --split C.

---

**Status:** active  **Date:** 2026-09-26

---

### 👤 User

Implement mutant_hunter/replay.py (section 7.4 of @/docs/SPEC.md) using the Workspace class in mutant_hunter/isolation.py: replay.replay(which: str, suites: list[str]) -> list[dict], writing results/replay.csv. Suites are human, mh and b1 (the generated tests alone); a module without mh or b1 tests gets an empty result for that suite, not an error. The history clone is ../validators-history. This machine runs Windows.
Run `mutanthunter replay --set all --suite human,mh,b1` and check that the human rows match the human_tests_at_HEAD column of dataset/bug_commits.csv.
Then add the replay table to report.py (section 8, item 6) with the reading notes of section 7.4. In the same change, fix two dashboard issues: at 500 px the per-module table overflows to the right (wrap it in a horizontally scrollable container), and stats.md prints "no paired data yet" when paired data exist but b = c = 0 (print b, c and p instead). Then run `mutanthunter report`. Do not run --split B or --split C.

---

### 🤖 Assistant

> 🔧 called: use_skill



> 🔧 **use_skill** — mutant-hunter

### 🤖 Assistant

> 🔧 called: read_file, list_files

Let me start by exploring the codebase to understand the existing structure.

> 🔧 **list_files** — mutant_hunter

> 🔧 **read_file** — docs/SPEC.md

### 🤖 Assistant

> 🔧 called: grep, read_file



> 🔧 **read_file** — mutant_hunter/isolation.py

> 🔧 **grep** — 7\.4|replay

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — mutant_hunter/cli.py

> 🔧 **read_file** — docs/SPEC.md

### 🤖 Assistant

> 🔧 called: read_file, list_files



> 🔧 **list_files** — dataset

> 🔧 **read_file** — mutant_hunter/registry.py

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — dataset/bug_commits.csv

> 🔧 **read_file** — mutant_hunter/report.py

### 🤖 Assistant

> 🔧 called: execute_command, read_file

Now let me look at the history repo and check existing tests:

> 🔧 **execute_command** — if (Test-Path '../validators-history') { Get-Item '../validators-history' | Format-List } else { Write-Host 'NOT FOUND' }

> 🔧 **read_file** — mutant_hunter/stats.py

### 🤖 Assistant

> 🔧 called: execute_command, execute_command



> 🔧 **execute_command** — Get-ChildItem targets/validators/tests -Recurse -Directory | Select-Object FullName

> 🔧 **execute_command** — cd ..; git -C validators-history log --oneline -5 2>&1; git -C validators-history remote -v 2>&1

### 🤖 Assistant

> 🔧 called: execute_command, execute_command



> 🔧 **execute_command** — Get-ChildItem targets/validators/tests/mh -Recurse -Filter "*.py" | Select-Object FullName | Sort-Object FullName

> 🔧 **execute_command** — cd ..; git -C validators-history log --oneline --all | head -5; git -C validators-history log --oneline 402b351 -3 2>&1

### 🤖 Assistant

> 🔧 called: execute_command, execute_command



> 🔧 **execute_command** — cd ..; git -C validators-history log --oneline 402b351 -1 2>&1; git -C validators-history log --oneline 402b351^1 -1 2>&1

> 🔧 **execute_command** — cd ..; git -C validators-history show 402b351 --stat 2>&1 | Select-String -Pattern "mac_address|commit"

### 🤖 Assistant

> 🔧 called: execute_command, execute_command



> 🔧 **execute_command** — cd ..; git -C validators-history log --oneline | Select-Object -First 30

> 🔧 **execute_command** — cd ..; git -C validators-history show 402b351 2>&1 | Select-Object -First 50

### 🤖 Assistant

> 🔧 called: execute_command, read_file



> 🔧 **execute_command** — cd ..; git -C validators-history log --oneline 1231f6a -1 2>&1; git -C validators-history log --oneline 41f3d6d -1 2>&1; git -C validators-history log --oneline 41f3d6d^1 -1 2>&1

> 🔧 **read_file** — dataset/modules.csv

### 🤖 Assistant

> 🔧 called: update_todo_list

Now I have a clear picture. Let me understand the full structure needed and set up the todo list before implementing:

> 🔧 **update_todo_list** — 
[-] Implement mutant_hunter/replay.py (spec 7.4)
[ ] Run `mutanthunter replay --set all --suite human,mh,b1`
[ ] Verify human rows match bug_commits.csv human_tests_at_HEAD column
[ ] Fix report.py: add replay table reading notes (spec 8, item 6)
[ ] Fix report.py: wrap per-module table in horizontally scrollable container (500px overflow)
[ ] Fix stats.md: print b, c, p when paired data exist but b=c=0 instead of "no paired data yet"
[ ] Run `mutanthunter report`


### 🤖 Assistant

> 🔧 called: execute_command, execute_command

Let me understand the structure needed for replay.py by checking how the history repo is organized and the test structure:

> 🔧 **execute_command** — cd ..; git -C validators-history show 402b351:src/validators/mac_address.py 2>&1 | Select-Object -First 5; Write-Host "---PRE-FIX---"; git -C validators-history show 402b351^1:src/validators/mac_address.py 2>&1 | Select-Object -First 5

> 🔧 **execute_command** — cd ..; git -C validators-history show 41f3d6d:src/validators/hostname.py 2>&1 | Select-Object -First 5; Write-Host "---"; git -C validators-history show 41f3d6d^1:src/validators/hostname.py 2>&1 | Select-Object -First 5

### 🤖 Assistant

> 🔧 called: execute_command, execute_command



> 🔧 **execute_command** — cd ..; git -C validators-history cat-file -t 402b351 2>&1; git -C validators-history log 402b351^..402b351 --format="%H %T" 2>&1

> 🔧 **execute_command** — cd ..; git -C validators-history diff 402b351^ 402b351 -- src/validators/mac_address.py 2>&1

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — cd ..; git -C validators-history show 402b351^:src/validators/mac_address.py

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — cd ..; git -C validators-history show 402b351:src/validators/mac_address.py

### 🤖 Assistant

> 🔧 called: execute_command, execute_command

Good, I understand the structure now. Let me also check how the target project is laid out to understand how to create workspaces from the history:

> 🔧 **execute_command** — Get-ChildItem targets/validators -Directory | Select-Object Name

> 🔧 **execute_command** — cd ..; Get-ChildItem validators-history -Directory | Select-Object Name

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — cd ..; git -C validators-history show 25fcef0:src/validators/email.py 2>&1 | Select-Object -First 3; Write-Host "parent:"; git -C validators-history show 25fcef0^:src/validators/email.py 2>&1 | Select-Object -First 3

### 🤖 Assistant

> 🔧 called: execute_command

Now I have enough information to implement `replay.py`. The key logic:

1. For each row in `bug_commits.csv`, for each suite (human, mh, b1):
   - Checkout the pre-fix version (`sha^`) of the module's source into a workspace
   - Run the suite's tests → if they fail, that's not `caught`
   - Checkout the fix version (`sha`) of the module's source into a workspace  
   - Run the suite's tests → need: tests FAIL on pre-fix AND PASS on fix = "caught"
   - If collection fails on either = "not_replayable"
   - If module has no mh or b1 tests → empty result (not error)

> 🔧 **execute_command** — Get-ChildItem targets/validators/tests/b1 -Recurse -Filter "*.py" | Select-Object Name | Sort-Object Name

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — Get-ChildItem targets/validators/tests -Filter "*.py" | Select-Object Name | Sort-Object Name

### 🤖 Assistant

> 🔧 called: write_file

Now I have all the information I need. Let me write `replay.py`:

> 🔧 **write_file** — mutant_hunter/replay.py

### 🤖 Assistant

> 🔧 called: update_todo_list

Now let's run the replay command:

> 🔧 **update_todo_list** — 
[x] Implement mutant_hunter/replay.py (spec 7.4)
[-] Run `mutanthunter replay --set all --suite human,mh,b1`
[ ] Verify human rows match bug_commits.csv human_tests_at_HEAD column
[ ] Fix report.py: add replay table reading notes (spec 8, item 6)
[ ] Fix report.py: wrap per-module table in horizontally scrollable container (500px overflow)
[ ] Fix stats.md: print b, c, p when paired data exist but b=c=0 instead of "no paired data yet"
[ ] Run `mutanthunter report`


### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — python -B -m mutant_hunter.cli replay --set all --suite human,mh,b1 2>&1

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — mutanthunter replay --set all --suite human,mh,b1 2>&1

### 🤖 Assistant

> 🔧 called: execute_command, execute_command



---

### 👤 User

Continue

---

### 🤖 Assistant

> 🔧 called: execute_command

Let me check the Python/venv setup:

> 🔧 **execute_command** — Get-Command py -ErrorAction SilentlyContinue; Get-Command python3 -ErrorAction SilentlyContinue; Get-ChildItem "targets\validators\.venv\Scripts" -Filter "python*" | Select-Object Name

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — & "targets\validators\.venv\Scripts\python.exe" -c "import sys; print(sys.executable)"

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — & "targets\validators\.venv\Scripts\python.exe" -B -m mutant_hunter.cli replay --set all --suite human,mh,b1 2>&1

### 🤖 Assistant

> 🔧 called: update_todo_list

The replay ran successfully. Now let me verify the human rows against the `human_tests_at_HEAD` column:

> 🔧 **update_todo_list** — 
[x] Implement mutant_hunter/replay.py (spec 7.4)
[x] Run `mutanthunter replay --set all --suite human,mh,b1`
[-] Verify human rows match bug_commits.csv human_tests_at_HEAD column
[ ] Fix report.py: add replay table reading notes (spec 8, item 6)
[ ] Fix report.py: wrap per-module table in horizontally scrollable container (500px overflow)
[ ] Fix stats.md: print b, c, p when paired data exist but b=c=0 instead of "no paired data yet"
[ ] Run `mutanthunter report`


### 🤖 Assistant

> 🔧 called: execute_command, execute_command

Cross-checking the `human` rows against `bug_commits.csv`:

| sha | module | `human_tests_at_HEAD` in CSV | replay `human` result | Match? |
|---|---|---|---|---|
| 402b351 | mac_address | MISS | miss | ✓ |
| 7c97eca | i18n/es | catch | caught | ✓ |
| 25fcef0 | email | catch | caught | ✓ |
| 1231f6a | url | MISS | miss | ✓ |
| 0a791b6 | domain | catch | caught | ✓ |
| 7c0e605 | ip_address | catch | caught | ✓ |
| 181f6dc | domain | catch | **miss** | ✗ |

There's a mismatch at `181f6dc` (domain). The CSV says `catch` but replay returned `miss`. Let me investigate:

> 🔧 **execute_command** — cd ..; git -C validators-history show 181f6dc --stat 2>&1

> 🔧 **execute_command** — cd ..; git -C validators-history diff 181f6dc^ 181f6dc -- src/validators/domain.py 2>&1

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — cd ..; git -C validators-history show 181f6dc -- tests/test_domain.py | Select-String "^\+" | Select-Object -First 20

### 🤖 Assistant

> 🔧 called: execute_command

The fix added 4 test cases. The test file in `targets/validators/tests/test_domain.py` reflects today's HEAD (which includes these tests). Let me check whether today's test file already has those cases — the human suite test runs against HEAD tests on both pre-fix and fix source, so if the HEAD tests already include those assertions from the fix commit, they should catch the pre-fix version. Let me debug this:

> 🔧 **execute_command** — & "targets\validators\.venv\Scripts\python.exe" -B -c "
import tempfile, shutil, subprocess, os
from pathlib import Path

HISTORY = Path('../validators-history')
TARGET  = Path('targets/validators')
VENV_PY = TARGET / '.venv/Scripts/python.exe'

# get pre-fix source
proc = subprocess.run(['git','show','181f6dc^:src/validators/domain.py'], capture_output=True, text=True, cwd=str(HISTORY))
pre_src = proc.stdout

# build a temp workspace
ws = Path(tempfile.mkdtemp(prefix='dbg_'))
shutil.copytree(TARGET/'src', ws/'src', ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
shutil.copytree(TARGET/'tests', ws/'tests', ignore=shutil.ignore_patterns('__pycache__','*.pyc'))

# inject pre-fix source
(ws/'src/validators/domain.py').write_text(pre_src, encoding='utf-8')

env = os.environ.copy()
env['PYTHONPATH'] = str(ws/'src')
env['PYTHONDONTWRITEBYTECODE'] = '1'

r = subprocess.run(
    [str(VENV_PY), '-B', '-m', 'pytest', str(ws/'tests/test_domain.py'), '-v', '--tb=short', '-q'],
    capture_output=True, text=True, env=env, cwd=str(ws)
)
print('RC:', r.returncode)
print(r.stdout[-3000:])
shutil.rmtree(ws, ignore_errors=True)
"


### 🤖 Assistant

> 🔧 called: execute_command

So the tests DO fail on the pre-fix source (3 failures, RC=1). But our replay returned `miss`. The issue is in our `-x` flag — we run with `-x` which stops at the first failure. But the actual problem must be that the tests ALSO fail on the fix source (or our workspace is doing something wrong). Let me check the fix source:

> 🔧 **execute_command** — & "targets\validators\.venv\Scripts\python.exe" -B -c "
import tempfile, shutil, subprocess, os
from pathlib import Path

HISTORY = Path('../validators-history')
TARGET  = Path('targets/validators')
VENV_PY = TARGET / '.venv/Scripts/python.exe'

# get fix source (the sha itself)
proc = subprocess.run(['git','show','181f6dc:src/validators/domain.py'], capture_output=True, text=True, cwd=str(HISTORY))
fix_src = proc.stdout

# build a temp workspace
ws = Path(tempfile.mkdtemp(prefix='dbg2_'))
shutil.copytree(TARGET/'src', ws/'src', ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
shutil.copytree(TARGET/'tests', ws/'tests', ignore=shutil.ignore_patterns('__pycache__','*.pyc'))

# inject fix source
(ws/'src/validators/domain.py').write_text(fix_src, encoding='utf-8')

env = os.environ.copy()
env['PYTHONPATH'] = str(ws/'src')
env['PYTHONDONTWRITEBYTECODE'] = '1'

r = subprocess.run(
    [str(VENV_PY), '-B', '-m', 'pytest', str(ws/'tests/test_domain.py'), '-q', '--tb=short'],
    capture_output=True, text=True, env=env, cwd=str(ws)
)
print('RC:', r.returncode)
print(r.stdout[-2000:])
shutil.rmtree(ws, ignore_errors=True)
"


### 🤖 Assistant

> 🔧 called: execute_command, execute_command

The fix source also fails (on the `.onion` test which was from the later `0a791b6` commit). So both pre-fix and fix fail the test suite — the condition `pre_result == killed AND fix_result == survived` is not met because the fix source also returns `killed` (still fails the `.onion` test). That's correct behavior from the replay logic: the test we're interested in (`example.com!` etc.) is still red on the fix because there's a **subsequent** breaking change (`somerandomexample.onion`) that appears later.

But `human_tests_at_HEAD` says `catch` for `181f6dc`. This is the crucial distinction: the spec's "catch" in `bug_commits.csv` represents whether the _current_ HEAD human tests would catch that bug. Our replay correctly runs the current tests against pre-fix vs fix.

The reason it returns `miss` is that with `-x`, the first failure encountered on the pre-fix (`.onion` test, which tests a different subsequent bug) stops execution before we even get to the `181f6dc` failures. With `-x`, both pre-fix and fix end up `killed` (one fails for a later bug, the other for the target bug).

The fix is: instead of using `-x` (stop at first failure), we should run **without** `-x`, and check if the set of failing tests changes between pre-fix and fix. Or, more simply: we should compare **without** the `-x` flag and check if the test that was broken gets fixed.

The correct logic should be: pre-fix fails with MORE test failures than fix → "caught". But that's complex. The proper approach from spec 7.4: "Caught = a test fails on pre-fix and passes on fix." This means we need pair-level detection: some test(s) must fail on pre-fix AND pass on fix.

The simplest correct approach: drop `-x` and just compare whether the total failure count is higher on pre-fix than fix. But actually, the even simpler approach matching the spec: the suite fails (any test fails) on pre-fix AND the suite passes entirely on fix. Since the fix source also breaks on later bugs, this particular commit is indeed un-catchable by the current test suite in isolation.

Wait — let me re-read `human_tests_at_HEAD` more carefully. That column says `catch` for `181f6dc`. But our analysis shows the fix source also fails (`.onion` test). This seems like the CSV expected value is wrong, OR the intent is different from my interpretation. Let me re-check:

The `.onion` test failure is from commit `0a791b6` (which came AFTER `181f6dc` in the timeline). The `.onion` test exists in today's HEAD test file. So:
- Pre-fix of `181f6dc`: breaks `example.com!` test + still fails `.onion` test  
- Fix of `181f6dc`: fixes `example.com!` but still fails `.onion` test

Both are "killed" so our replay says `miss`. But the CSV says `catch`. The CSV column `bug_attributable_tests: 2` suggests 2 tests are attributable to THIS specific commit's bug. 

The intent of `human_tests_at_HEAD` in the CSV seems to mean: "do tests added attributable to this bug exist in the current HEAD?" — not whether a full pre/fix run succeeds. Our replay implementation correctly tests the full end-to-end: "does any test fail on pre and pass on fix?" — which is the spec's definition.

So the mismatch for `181f6dc` is actually **correct behavior** from our replay: the current tests can't cleanly catch that commit in isolation because later commits introduced further regressions. Our implementation is correct per spec 7.4.

Let me verify the remaining rows quickly:
- `af69a68 email`: CSV=MISS, replay=miss ✓
- `af69a68 url`: CSV=MISS, replay=miss ✓  
- `b6cfb43 domain`: CSV=MISS, replay=miss ✓
- `c0e29cf domain`: CSV=MISS, replay=miss ✓
- `5f6437c domain`: CSV=catch, replay=miss — let me check
- `5f6437c url`: CSV=catch, replay=miss — let me check

> 🔧 **execute_command** — cd ..; git -C validators-history diff 5f6437c^ 5f6437c -- src/validators/domain.py 2>&1 | Select-Object -First 30

> 🔧 **execute_command** — cd ..; git -C validators-history diff 5f6437c^ 5f6437c -- src/validators/url.py 2>&1 | Select-Object -First 40

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — & "targets\validators\.venv\Scripts\python.exe" -B -c "
import tempfile, shutil, subprocess, os
from pathlib import Path

HISTORY = Path('../validators-history')
TARGET  = Path('targets/validators')
VENV_PY = TARGET / '.venv/Scripts/python.exe'

for sha, mod, testfile in [('5f6437c', 'domain', 'tests/test_domain.py'), ('5f6437c', 'url', 'tests/test_url.py')]:
    for version, label in [('{}^'.format(sha), 'PRE'), (sha, 'FIX')]:
        proc = subprocess.run(['git','show','{}:src/validators/{}.py'.format(version, mod)],
                              capture_output=True, text=True, cwd=str(HISTORY))
        src = proc.stdout
        ws = Path(tempfile.mkdtemp(prefix='dbg3_'))
        shutil.copytree(TARGET/'src', ws/'src', ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        shutil.copytree(TARGET/'tests', ws/'tests', ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        (ws/'src/validators/{}.py'.format(mod)).write_text(src, encoding='utf-8')
        env = os.environ.copy(); env['PYTHONPATH'] = str(ws/'src'); env['PYTHONDONTWRITEBYTECODE'] = '1'
        r = subprocess.run([str(VENV_PY),'-B','-m','pytest',str(ws/testfile),'-q','--tb=line','--no-header'],
                           capture_output=True, text=True, env=env, cwd=str(ws))
        lines = r.stdout.strip().split('\n')
        print(f'{sha} {mod} {label} RC={r.returncode}: {lines[-1]}')
        shutil.rmtree(ws, ignore_errors=True)
"


### 🤖 Assistant

> 🔧 called: apply_diff

The fix source also fails tests (for later commits). With `-x` (stop-at-first-failure), both pre and fix get `killed` and we return `miss`. But the actual "attributable" tests do catch the bug — the failure count changes from 5→4 and 14→13.

The problem: our `_x` flag stops at the first failure even if that's a different bug. We need to run **without `-x`** and compare exit codes — both are 1 (failed) so we still get `miss`. 

The right interpretation for "caught" with today's HEAD tests: **the current test suite is red on both** (due to later unfixed bugs). But the spec says "caught = a test fails on pre-fix and passes on fix." Since different tests fail, we need per-test comparison, not whole-suite pass/fail.

The correct implementation for the spec's definition is to **count the failures**: if the suite fails MORE on pre-fix than on fix, some test(s) are being caught. Or better: run without `-x`, parse FAILED tests on both sides, and check if any test that failed on pre-fix passes on fix.

Let me update `replay.py` to implement proper per-test comparison:

---

### 👤 User

Continue

---

### 🤖 Assistant

> 🔧 called: apply_diff



> 🔧 **apply_diff** — mutant_hunter/replay.py

### 🤖 Assistant

> 🔧 called: apply_diff

Now update `_replay_one_commit` to use the new method:

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:228
-------
def _replay_one_commit(
    sha: str,
    module_name: str,
    suite: str,
) -> str:
    """Return 'caught' | 'miss' | 'not_replayable' | '' (no tests)."""
    suite_paths = _suite_paths_for_replay(module_name, suite)
    if not suite_paths:
        return ""  # no tests for this suite → empty, not an error

    try:
        mod = get_module(module_name)
    except KeyError:
        return "not_replayable"

    # Pre-fix source = sha^ (parent of the fix commit)
    pre_src = _source_at(f"{sha}^", module_name)
    # Fix source = sha
    fix_src = _source_at(sha, module_name)

    if pre_src is None or fix_src is None:
        return "not_replayable"

    try:
        with _ReplayWorkspace(pre_src, mod) as ws_pre:
            pre_result = ws_pre.run_pytest(suite_paths)

        with _ReplayWorkspace(fix_src, mod) as ws_fix:
            fix_result = ws_fix.run_pytest(suite_paths)
    except Exception:
        return "not_replayable"

    if pre_result == "not_replayable" or fix_result == "not_replayable":
        return "not_replayable"

    # caught = fails on pre-fix AND passes on fix
    if pre_result == "killed" and fix_result == "survived":
        return "caught"
    return "miss"
=======
def _replay_one_commit(
    sha: str,
    module_name: str,
    suite: str,
) -> str:
    """Return 'caught' | 'miss' | 'not_replayable' | '' (no tests).

    caught = at least one test fails on pre-fix AND passes on fix.
    This handles suites that are red on both versions due to later bugs:
    if the set of failing tests shrinks from pre-fix to fix, the commit
    is caught (some tests detect the specific bug being fixed).
    """
    suite_paths = _suite_paths_for_replay(module_name, suite)
    if not suite_paths:
        return ""  # no tests for this suite → empty, not an error

    try:
        mod = get_module(module_name)
    except KeyError:
        return "not_replayable"

    # Pre-fix source = sha^ (parent of the fix commit)
    pre_src = _source_at(f"{sha}^", module_name)
    # Fix source = sha
    fix_src = _source_at(sha, module_name)

    if pre_src is None or fix_src is None:
        return "not_replayable"

    try:
        with _ReplayWorkspace(pre_src, mod) as ws_pre:
            pre_status, pre_failed = ws_pre.run_pytest_collect_failures(suite_paths)

        with _ReplayWorkspace(fix_src, mod) as ws_fix:
            fix_status, fix_failed = ws_fix.run_pytest_collect_failures(suite_paths)
    except Exception:
        return "not_replayable"

    if pre_status == "not_replayable" or fix_status == "not_replayable":
        return "not_replayable"

    # caught = at least one test failed on pre-fix that now passes on fix
    newly_fixed = pre_failed - fix_failed
    if newly_fixed:
        return "caught"
    return "miss"
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: execute_command

Now re-run the replay:

> 🔧 **execute_command** — & "targets\validators\.venv\Scripts\python.exe" -B -m mutant_hunter.cli replay --set all --suite human,mh,b1 2>&1

### 🤖 Assistant

> 🔧 called: update_todo_list

Now let me verify the human rows against `bug_commits.csv`:

| sha | module | CSV `human_tests_at_HEAD` | replay `human` | Match? |
|---|---|---|---|---|
| 402b351 | mac_address | MISS | miss | ✓ |
| 7c97eca | i18n/es | catch | caught | ✓ |
| 25fcef0 | email | catch | caught | ✓ |
| 1231f6a | url | MISS | miss | ✓ |
| 0a791b6 | domain | catch | caught | ✓ |
| 7c0e605 | ip_address | catch | caught | ✓ |
| 181f6dc | domain | catch | caught | ✓ |
| af69a68 | email | catch | caught | ✓ |
| af69a68 | url | MISS | miss | ✓ |
| b6cfb43 | domain | MISS | miss | ✓ |
| c0e29cf | domain | MISS | miss | ✓ |
| 5f6437c | domain | catch | caught | ✓ |
| 5f6437c | url | catch | caught | ✓ |
| d1a5b22 | between | MISS | miss | ✓ |
| d1a5b22 | length | MISS | miss | ✓ |
| 38d196a | url | catch | caught | ✓ |
| 15984e8 | url | catch | caught | ✓ |
| f7aa593 | between | catch | caught | ✓ |
| 960b48b | url | catch | caught | ✓ |
| 41f3d6d | hostname | MISS | miss | ✓ |
| 4015e8e | url | catch | caught | ✓ |

**All 21 human rows match the `human_tests_at_HEAD` column exactly.** ✓

Now let's implement the three fixes in `report.py`:

> 🔧 **update_todo_list** — 
[x] Implement mutant_hunter/replay.py (spec 7.4)
[x] Run `mutanthunter replay --set all --suite human,mh,b1`
[x] Verify human rows match bug_commits.csv human_tests_at_HEAD column
[-] Fix report.py: add replay table reading notes (spec 8, item 6)
[-] Fix report.py: wrap per-module table in horizontally scrollable container (500px overflow)
[-] Fix stats.md: print b, c, p when paired data exist but b=c=0 instead of "no paired data yet"
[ ] Run `mutanthunter report`


### 🤖 Assistant

> 🔧 called: apply_diff

All three fixes are in `report.py`. I'll apply them in a single `apply_diff` call:

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:302
-------
            b, c, p_val = _mcnemar_b1_vs_mh(
                registry, results_dir, mutant_files, mod_set, split
            )
            if b + c > 0:
                lines.append(
                    f"McNemar B1 vs MH (split {split}, {mod_set}): "
                    f"b={b}, c={c}, p={p_val:.4f}\n"
                )
            else:
                lines.append(
                    f"McNemar B1 vs MH (split {split}, {mod_set}): no paired data yet\n"
                )
=======
            b, c, p_val = _mcnemar_b1_vs_mh(
                registry, results_dir, mutant_files, mod_set, split
            )
            # Print b, c, p even when b=c=0 (paired data exist but no discordant pairs)
            mods_with_both = sum(
                1 for m in [mm for mm, rr in registry.items() if rr.get("set") == mod_set]
                if (_slug(m), "human+b1", split) in mutant_files
                and (_slug(m), "human+mh", split) in mutant_files
            )
            if mods_with_both > 0:
                lines.append(
                    f"McNemar B1 vs MH (split {split}, {mod_set}): "
                    f"b={b}, c={c}, p={p_val:.4f}\n"
                )
            else:
                lines.append(
                    f"McNemar B1 vs MH (split {split}, {mod_set}): no paired data yet\n"
                )
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:683
-------
<h2>Per-module scores</h2>
<p class="section-note">Scores shown are split-B when available, otherwise split-A. B0 = human tests; B1 = human+B1; MH = human+MH.</p>
<div class="legend">
  <span class="b0">B0</span><span class="b1">B1</span><span class="mh">MH</span>
</div>
<table class="data-table">
<thead><tr><th>Module</th><th>Set</th><th>Bars</th><th>B0</th><th>B1</th><th>MH</th><th>Tests kept</th><th>Bugs</th><th>Min</th></tr></thead>
<tbody>
{"".join(mod_row(m) for m in mods if m["run"])}
</tbody>
</table>
{not_run_html}
=======
<h2>Per-module scores</h2>
<p class="section-note">Scores shown are split-B when available, otherwise split-A. B0 = human tests; B1 = human+B1; MH = human+MH.</p>
<div class="legend">
  <span class="b0">B0</span><span class="b1">B1</span><span class="mh">MH</span>
</div>
<div style="overflow-x:auto;">
<table class="data-table">
<thead><tr><th>Module</th><th>Set</th><th>Bars</th><th>B0</th><th>B1</th><th>MH</th><th>Tests kept</th><th>Bugs</th><th>Min</th></tr></thead>
<tbody>
{"".join(mod_row(m) for m in mods if m["run"])}
</tbody>
</table>
</div>
{not_run_html}
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:700
-------
<h2>Historical bug replay</h2>
<p class="section-note">Caught = test fails on pre-fix commit and passes on fix commit. B0/B1 replay is context only (see spec §7.4).</p>
{replay_table()}
=======
<h2>Historical bug replay</h2>
<p class="section-note">
  Caught = at least one test fails on the pre-fix commit and passes on the fix commit.
  <strong>Reading notes (spec §7.4):</strong>
  Tests written today encode today's fixed behavior — any test that pins current behavior "catches"
  a reverted fix, so B1 and the human tests look good here for reasons unrelated to finding bugs
  before release. Report B1 replay as context only, never as a comparison with MH.
  The meaningful result is the <em>extra</em> set (mac_address, hostname): bugs the human tests
  still miss at HEAD. Row <code>1231f6a</code> is spec-ambiguous (RFC 3986 vs WHATWG); reported
  but not counted.
</p>
<div style="overflow-x:auto;">
{replay_table()}
</div>
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: update_todo_list

Now run `mutanthunter report`:

> 🔧 **update_todo_list** — 
[x] Implement mutant_hunter/replay.py (spec 7.4)
[x] Run `mutanthunter replay --set all --suite human,mh,b1`
[x] Verify human rows match bug_commits.csv human_tests_at_HEAD column
[x] Fix report.py: add replay table reading notes (spec 8, item 6)
[x] Fix report.py: wrap per-module table in horizontally scrollable container (500px overflow)
[x] Fix stats.md: print b, c, p when paired data exist but b=c=0 instead of "no paired data yet"
[-] Run `mutanthunter report`


### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — & "targets\validators\.venv\Scripts\python.exe" -B -m mutant_hunter.cli report 2>&1

### 🤖 Assistant

> 🔧 called: execute_command, execute_command

Clean. Let me verify the stats.md McNemar fix and the replay table in index.html:

> 🔧 **execute_command** — Select-String "replay|Reading notes|1231f6a|overflow-x" docs\index.html | Select-Object -First 15

> 🔧 **execute_command** — Select-String "McNemar" results\stats.md

### 🤖 Assistant

> 🔧 called: update_todo_list

Everything is working correctly. Let me do a final check to confirm all the output files look clean:

> 🔧 **update_todo_list** — 
[x] Implement mutant_hunter/replay.py (spec 7.4)
[x] Run `mutanthunter replay --set all --suite human,mh,b1`
[x] Verify human rows match bug_commits.csv human_tests_at_HEAD column
[x] Fix report.py: add replay table reading notes (spec 8, item 6)
[x] Fix report.py: wrap per-module table in horizontally scrollable container (500px overflow)
[x] Fix stats.md: print b, c, p when paired data exist but b=c=0 instead of "no paired data yet"
[x] Run `mutanthunter report`


### 🤖 Assistant

All done. Here's a summary of everything that was implemented and fixed:

---

## What was done

### `mutant_hunter/replay.py` — new file (spec 7.4)

[`replay.py`](mutant_hunter/replay.py) implements `replay(which, suites) -> list[dict]`:

- For each row of [`bug_commits.csv`](dataset/bug_commits.csv) × each suite, it:
  - Checks out the **pre-fix** (`sha^`) and **fix** (`sha`) source from `../validators-history` using `git show`
  - Creates two `_ReplayWorkspace` instances that inject that historical source into a copy of the current `targets/validators/` tree (so today's tests run against historical code)
  - Runs pytest **without `-x`** on both, collecting the set of failing test node-IDs for each side
  - **`caught`** = at least one test that failed on pre-fix now passes on fix (`pre_failed - fix_failed` is non-empty)
  - **`miss`** = no such test
  - **`not_replayable`** = collection error / source not found
  - **`""`** (empty) = no tests exist for that suite — not an error
- Writes [`results/replay.csv`](results/replay.csv) with 63 rows

The per-test comparison (rather than whole-suite pass/fail) is essential: many commits are followed by later commits that also break tests, so both pre-fix and fix are "red", but the attributable tests change.

### Human row verification

All 21 `human`-suite rows match the `human_tests_at_HEAD` column in `bug_commits.csv` exactly.

### `mutant_hunter/report.py` — three fixes

1. **Replay table reading notes** (spec 8.6): The "Historical bug replay" section now includes the full reading notes from §7.4 — warning that B1/human catches are context-only, naming the meaningful `extra`-set results, and flagging `1231f6a` as spec-ambiguous.

2. **Per-module table overflow** at 500 px: the table is now wrapped in `<div style="overflow-x:auto;">` so it scrolls horizontally instead of overflowing.

3. **`stats.md` McNemar b=c=0 bug**: the condition now checks whether any module has **both** B1 and MH split files (i.e., paired data genuinely exist), and if so prints `b=0, c=0, p=1.0000` instead of the misleading "no paired data yet" message.