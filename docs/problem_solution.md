# Problem & Solution

## Problem

Coverage shows that a line ran, not that a test would notice if it were wrong. In python-validators, a widely used validation library, `url.py` has 91.9% line and branch coverage, yet its human tests miss 23 of 58 small injected bugs (mutants). Across the ten weakest modules, 155 of 481 mutants survive.

Asking an AI assistant to "write more tests" has a hidden flaw: a plain prompt writes tests that pin down what the code does today, bugs included. In our run, it noticed that the ISIN check digit is never verified and wrote its tests around the flaw.

## Solution

MutantHunter is an IBM Bob skill plus a deterministic Python harness. One sentence in Bob runs the whole loop:

1. The harness injects mutants into an isolated copy of the module. Only half of them (split A) are shown to the agents; split B stays hidden.
2. Bob spawns two subagents in parallel. A broad subagent writes regression tests. A spec subagent reads the module's specification (RFCs, Wikipedia pages on ISIN, cron and more), writes numbered rules, and takes expected results from the spec, not the code.
3. A test that fails on the current code is never deleted; it becomes a suspected spec violation with a category.
4. A targeted subagent attacks the remaining survivors (run for url only, to save Bobcoins).
5. After generation is frozen, the tests are scored once on split B and on exam C, mutant operators that did not exist while the tests were written.

## Results

Six modules, three suites: human tests (B0), plus one plain Bob prompt (B1), plus MutantHunter (MH).

- Hold-out split B, four main modules (141 mutants): B0 60.3%, B1 77.3%, MH 78.0%. MH and the plain prompt tie (p = 1.00).
- Exam C, unseen operators, main modules (146 mutants): B0 65.8%, B1 76.7%, MH 82.2%; nine mutants killed only by MH, one only by B1 (p = 0.02, not significant after correcting for four tests).
- Historical bugs that today's human tests still miss: MH's tests catch both (mac_address mixed separators, hostname single-character labels), and so do B1's.
- Bugs: of 13 suspected violations, reviewed against the code and upstream issues, five distinct bugs are confirmed, four not reported upstream: a 61-character cap on hostnames where RFC 1123 requires 63, the RFC 5321 `[IPv6:...]` email form being rejected, quoted email local parts with spaces or `@` being rejected, and URLs with an empty port being rejected. The fifth, the never-verified ISIN check digit, matches open issue #440.

## Why it matters

Honestly, spec-derived tests do not kill more of the mutants a plain prompt already sees. Their value is that they appear to generalise better to unseen bugs (a trend, not yet significant) and turn disagreements with the specification into reviewable bug reports instead of silently encoding them. Every number is reported with its sample size, confidence interval and cost.
