# IBM Bob Usage Statement

Two team members used IBM Bob in 22 tasks. Evan (8 tasks, about 47.3 Bobcoins) planned and built the harness and the skill and generated tests for url, hostname and mac_address. chu (14 tasks, about 41.1 Bobcoins) ported the harness to Windows, generated tests for finance, cron and email, and ran the whole evaluation. Every task is exported in `bob_sessions/` with a screenshot of its consumption summary. Total cost: about 88.4 Bobcoins.

## Plan mode

Bob read the design (`docs/SPEC.md`, 13 sections) and the dataset notes and wrote the build plan `docs/track-a-plan.md`, splitting the work into ten sub-tasks (ST1–ST10) and listing the interfaces the second track would plug into. The core and skill tasks followed ST1–ST9; before coding the harness, Bob also wrote a detailed implementation plan, `docs/mutanthunter-core-plan.md`.

## Agent mode

Bob wrote all product code, apart from the small edits listed at the end: the deterministic harness (`registry`, `isolation`, `mutate`, `check`, `cli`), statistics (Wilson intervals, exact McNemar), the dashboard generator, historical bug replay, the exam C operators, and 128 unit tests. When we found defects by testing the tools directly (a check command that never ran mutants, pytest node IDs that differed between runs, test folders shadowing the standard library, invented timestamps), Bob fixed them. It also ported the harness from macOS to Windows in one task.

## Skills and rules

`.bob/skills/mutant-hunter/SKILL.md` turns the whole method into one sentence: "Use the mutant-hunter skill on the module <name>." We ran it on 6 modules. `.bob/rules/testing.md` holds the testing rules every subagent follows: expected values come from the spec, failing tests become reported violations and are never deleted, no `__init__.py`, and split B is never touched.

## Parallel subagents

Each skill run spawned a broad and a spec subagent in parallel, plus a targeted subagent for `url`: 13 subagents in total. The broad and spec subagents work independently; the main task reconciles their results.

## Document understanding

The spec subagents read 10 specification PDFs (RFC 3986, 5321, 5322, 1123, 952 and Wikipedia pages on ISIN, CUSIP, SEDOL, cron and MAC addresses) and turned them into 137 numbered rules, each cited by the tests derived from it. This is where the confirmed bugs came from, for example RFC 1123's 63-character hostname rule.

## A plain prompt as the baseline

For the B1 baseline, Bob received one plain sentence per module without subagents, skills or rules. Six B1 tasks cost 2.9 Bobcoins; six MutantHunter runs cost 37.5.

## Work outside Bob

We reviewed the 13 suspected violations by reading the code and searching the upstream issues, and recorded the verdicts by hand. We also corrected the cron test count in `results/modules/cron.json` after a subagent stopped with an error, and made a small layout fix to the dashboard. These edits were made outside Bob.
