# Bob task sessions

Evidence for judging: every IBM Bob task used to build and evaluate this project (22 tasks, about 88.4 Bobcoins: Evan 8 tasks, 47.3; chu 14 tasks, 41.1).

Each task has files with the same name:
- `<milestone>-<member>-<topic>.md`: the exported task history
- `<milestone>-<member>-<topic>.png`: a screenshot of the task, including the consumption summary (context tokens and Bobcoins)
- `<milestone>-<member>-<topic>.json` (chu's tasks only): the full JSON export; `tasks[].task.costs.cost` holds the Bobcoin cost

Members: `Evan` (track A: plan, harness, skill, test generation for url, mac_address, hostname) and `chu` (track B: Windows port, test generation for finance, cron, email, the B1 baseline, statistics, dashboard, replay, exam C).

Milestones follow `docs/SPEC.md` section 11: M0 plan, M1 harness, M2 skill on url, M3 generation and scoring, M4 replay, exam C and dashboard.

How to export in Bob IDE: chat panel → Views and More Actions → History → open the task → click the task header (consumption summary) → Export task history.
