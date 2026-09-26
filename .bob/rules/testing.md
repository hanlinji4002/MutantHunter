# Testing Rules — MutantHunter

These rules apply to every test file written by the MutantHunter skill
(broad, spec, and targeted subagents).

---

## 1. Never weaken or skip assertions

Never weaken, skip or delete an assertion to make a test pass.  
A test that **fails on the current code** is a **suspected violation** (spec 6.5).  
Move it to `results/suspected_bugs/<slug>.md`; do not remove it silently.

## 2. Read-only target source

Never modify `targets/*/src/`.  
Never use `--split B` or open `results/mutants/*__B.json`.

## 3. Source precedence

When sources conflict, the priority is:

1. **Spec document** (PDF or txt in `dataset/specs/`)
2. **Function's docstring**
3. **Existing human tests**

Record conflicts as `spec-ambiguous` in the suspected-violation entry.

## 4. Oracle functions

Check-digit algorithms and other deterministic computations **may** be
implemented as a small oracle function written directly in the test file,
derived from the spec's algorithm description.  
The oracle **must not** import or copy the module under test.

## 5. Docstring first line

Every test function's docstring **first line** must be one of:

- `Spec: <document> <section> — <rule ID>` — when the expected result comes from a spec document
- `Docstring: <function>` — when it comes from the target function's docstring
- `Characterization: <reason>` — when neither spec nor docstring defines it (targeted only)

## 6. Assertion style for validators

The validators package returns `True` or a falsy `ValidationError`.  
Always write:

```python
assert fn(x)          # valid input
assert not fn(x)      # invalid input
```

**Never** write `assert fn(x) is True` or `assert fn(x) is False`.

## 7. Public API only

Import only from `validators` (the public API).  
`import validators` or `from validators import <name>`.

Environment variables or options may be used **only if** they are documented
in the function's docstring, the project README, or the project docs.  
No network calls, randomness, or `time.sleep()`.

## 8. File naming

File names must be **unique across the entire repo**:

```
test_<slug>_<topic>.py
```

Examples: `test_url_broad.py`, `test_url_spec_authority.py`, `test_url_targeted.py`.

All MH test files live under `targets/validators/tests/mh/<slug>/`.
Never write under `targets/validators/tests/b1/` (track B owns that path).

## 11. No `__init__.py` files

**Never** create `__init__.py` under `tests/mh/` or `tests/b1/` (or any
subdirectory of either).
An `__init__.py` turns the slug directory into a top-level package; for slugs
like `uuid` or `email` this shadows the standard-library module of the same
name and causes every test in the session to fail at collection time.
Test file names are already unique (rule 8), so no `__init__.py` is needed.

## 9. Running pytest

Use `python -B -m pytest` when running pytest directly (the `-B` flag suppresses
bytecode writing without needing an environment-variable prefix, which does not
work in PowerShell 5.1).
Or run tests only through `mutanthunter check`, which sets this automatically.

## 10. Do not import from the module under test in oracles

An oracle helper that recomputes the expected value (e.g. a checksum) must be
self-contained in the test file. It must not call or import the validator
function it is testing.
