# MutantHunter dataset

Prepared on 2026-09-25, before the hackathon. The hackathon guide asks teams to bring their own datasets. This folder contains data only, no product code.

## Files

| File | Content |
|---|---|
| `modules.csv` | 24 modules of python-validators: source path, test path, evaluation set, spec documents, reference baseline |
| `bug_commits.csv` | 21 historical bug fixes for fail-to-pass (F→P) replay |
| `specs/*.pdf` | 30 spec documents (RFCs, BIPs, Wikipedia), for Bob's document understanding |
| `specs/txt/*.txt` | plain-text versions of the same documents (`pdftotext -layout`), for searching; tables may be partly mangled |
| `SOURCES.md` | every data source with its license |

## Target project

- python-validators, commit `70de324` (MIT license).
- All paths in the CSV files are relative to `targets/validators/`.

## modules.csv

`set` column:
- `main`: the 10 modules with a reference mutation score below 80%: country, cron, domain, email, finance, ip_address, url, uuid, i18n/fi, i18n/fr.
- `extra`: `hostname` and `mac_address`. Each has one historical bug that the current tests still miss.
- `reference`: all other modules, kept for comparison only.

`ref_*` columns: coverage and mutation results of the human tests, measured before the event with a reference mutation script (isolated copies, bytecode caching disabled, all mutants, operator set in `docs/SPEC.md` 5.3). The harness built during the event must reproduce `ref_mutants` and `ref_killed` exactly; any difference is a harness bug.

Totals: 601 of 796 mutants killed across all 24 modules (75.5%). The 10 `main` modules: 326 of 481 killed (67.8%), 155 survivors, average line+branch coverage 89.2%.


## bug_commits.csv

Each row is one historical fix × one module.

`human_tests_at_HEAD` column:
- `catch`: after swapping the pre-fix code back in, at least one current human test fails that passes on the fix. `bug_attributable_tests` is the number of such tests.
- `MISS`: no current human test distinguishes the pre-fix code from the fix.

Computed with the harness replay (suite `human`): run the current test file on the pre-fix and on the fix version, each in its own clean copy, and count tests that fail on pre-fix and pass on fix.

Excluded: large refactor or miscellaneous commits, modules without a test file, one packaging-only fix (`8cf75e5`).

Rows that need attention (see `note`):
- `1231f6a` (url, `#` in fragment): RFC 3986 forbids it, browsers (WHATWG) accept it. Spec-ambiguous; reported, not counted.
- `d1a5b22` (between, length): an API contract change; the spec is the library's docstring.
- `402b351` (mac_address) and `41f3d6d` (hostname): confirmed behavior bugs that current tests still miss.

## Summary

| Set | Rows | Current tests catch | Current tests miss |
|---|---|---|---|
| main | 15 | 11 | 4 |
| extra | 2 | 0 | 2 |
| reference | 4 | 2 | 2 |
