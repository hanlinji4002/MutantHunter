# Polish the dashboard in report.py (section 8 of @/docs/SPEC.md), then run `mutanthunter report`:
1. Historical bug replay: one row per bug commit and module, with human, MH and B1 as three columns (caught / miss / blank), instead of one row per suite. List extra-set rows first, then main, then reference.
2. Per-module scores: add exam C columns (B0, B1, MH) next to the split-B columns.
3. Extra-kill tiles: show split B and exam C separately.
Keep index.html readable at 500 px and in dark mode. Do not re-run any mutate command.

---

**Status:** active  **Date:** 2026-09-26

---

### 👤 User

Polish the dashboard in report.py (section 8 of @/docs/SPEC.md), then run `mutanthunter report`:
1. Historical bug replay: one row per bug commit and module, with human, MH and B1 as three columns (caught / miss / blank), instead of one row per suite. List extra-set rows first, then main, then reference.
2. Per-module scores: add exam C columns (B0, B1, MH) next to the split-B columns.
3. Extra-kill tiles: show split B and exam C separately.
Keep index.html readable at 500 px and in dark mode. Do not re-run any mutate command.

---

### 🤖 Assistant

> 🔧 called: use_skill, read_file



> 🔧 **use_skill** — mutant-hunter

> 🔧 **read_file** — docs/SPEC.md

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — report.py

> 🔧 **read_file** — docs/SPEC.md

### 🤖 Assistant

> 🔧 called: read_file, glob



> 🔧 **read_file** — docs/SPEC.md

> 🔧 **glob** — mutant_hunter/report.py

### 🤖 Assistant

> 🔧 called: glob, glob



> 🔧 **glob** — mutant_hunter/**/*.py

> 🔧 **glob** — results/**/*.csv

### 🤖 Assistant

> 🔧 called: list_files



> 🔧 **list_files** — .

### 🤖 Assistant

> 🔧 called: list_files, list_files



> 🔧 **list_files** — results

> 🔧 **list_files** — mutant_hunter

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — results/summary.csv

> 🔧 **read_file** — mutant_hunter/report.py

### 🤖 Assistant

> 🔧 called: read_file

Now let me look at the replay.csv to understand its current structure:

> 🔧 **read_file** — results/replay.csv

### 🤖 Assistant

> 🔧 called: update_todo_list

Now I have a clear picture of the data and what changes are needed. Let me set up the todo list and then implement all three changes.

> 🔧 **update_todo_list** — 
[-] Rewrite replay table: pivot to one row per (sha, module), with human/MH/B1 as columns; extra-set first, then main, then reference
[ ] Per-module scores: add exam C columns (B0, B1, MH for split C) next to split-B columns
[ ] Extra-kill tiles: show split B and exam C separately (4 tiles → 6 tiles)
[ ] Ensure 500px readability and dark mode work
[ ] Run `mutanthunter report` and verify


### 🤖 Assistant

> 🔧 called: apply_diff

Now let me implement all three changes at once in `report.py`:

> 🔧 **apply_diff** — mutant_hunter/report.py

### 🤖 Assistant

> 🔧 called: execute_command

Now run `mutanthunter report`:

> 🔧 **execute_command** — python -B -m mutant_hunter.cli report 2>&1

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — mutanthunter report 2>&1

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — .\.venv\Scripts\mutanthunter.exe report 2>&1

### 🤖 Assistant

> 🔧 called: execute_command

All three files written successfully. Let me verify the HTML output looks correct:

> 🔧 **execute_command** — Select-String -Path docs\index.html -Pattern "col-group-b|col-group-c|Split B|Exam C|replay-table|caught|tile-group" | Select-Object -First 30 | ForEach-Object { $_.Line.Trim() }

### 🤖 Assistant

> 🔧 called: update_todo_list

Everything is working. The output confirms:

1. **Replay table is correctly pivoted** — `extra` rows first (`41f3d6d` hostname, `402b351` mac_address), then `main`, then `reference`. Each row has Human / MH / B1 as three columns with `caught`/`miss`/`—` cells.

2. **Per-module scores** — the table now has a two-row header with Split B (B0, B1, MH) and Exam C (B0, B1, MH) column groups, visually distinguished with colored left borders.

3. **Extra-kill tiles** — now two grouped tile panels: "Extra kills — Split B" and "Extra kills — Exam C", each with two sub-tiles (MH over B1 / B1 over MH).

4. **Dark mode** — `caught`/`miss` colors have dark-mode variants (green/red adapted for dark backgrounds), and the existing dark theme is intact.

> 🔧 **update_todo_list** — 
[x] Rewrite replay table: pivot to one row per (sha, module), with human/MH/B1 as columns; extra-set first, then main, then reference
[x] Per-module scores: add exam C columns (B0, B1, MH for split C) next to split-B columns
[x] Extra-kill tiles: show split B and exam C separately (4 tiles → 6 tiles)
[x] Ensure 500px readability and dark mode work
[x] Run `mutanthunter report` and verify


### 🤖 Assistant

All three changes are done and `mutanthunter report` ran clean. Here's what changed in [`mutant_hunter/report.py`](mutant_hunter/report.py):

---

### 1. Historical bug replay — pivoted table
The `replay_table()` function now groups the raw CSV rows by `(sha, module)` into a dict, then sorts by set order (`extra → main → reference`) and emits one row per bug with **Human / MH / B1** as columns. Each result cell gets a CSS class (`caught` / `miss` / `blank`) styled in green/red with full dark-mode variants.

### 2. Per-module scores — Exam C columns added
`mod_row()` now calls a new helper `_score_for(m, suite_key, split)` to pull scores for both splits. The table header is a **two-row header group**: a "Split B" colspan-3 (blue left border) and an "Exam C" colspan-3 (purple left border), each containing B0 / B1 / **MH**.

### 3. Extra-kill tiles — split B and exam C separated
The single pair of tiles became two `tile-group` panels side by side: **Extra kills — Split B** and **Extra kills — Exam C**, each grouping the MH-over-B1 and B1-over-MH sub-tiles. Logic/violations tiles remain as `tile-misc` alongside them.

### 500 px / dark mode
- Metric cards, hero labels, and table font-size are all slightly tighter so everything still fits at 500 px.
- `flex-wrap` on `.tiles` and `.legend` ensures no horizontal overflow at narrow viewports.
- `white-space:nowrap` on `<th>` prevents column headers from wrapping awkwardly.