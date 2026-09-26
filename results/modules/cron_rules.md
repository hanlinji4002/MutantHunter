# Cron — Rules extracted from wiki-Cron.pdf

Source document: **wiki-Cron.pdf** (Wikipedia article on Cron)

---

## Field layout (Cron expression table)

| Field       | Required | Allowed values | Allowed special characters |
|-------------|----------|----------------|---------------------------|
| Minutes     | Yes      | 0–59           | `*` `,` `-` `/`           |
| Hours       | Yes      | 0–23           | `*` `,` `-` `/`           |
| Day-of-month| Yes      | 1–31           | `*` `,` `-` `/`           |
| Month       | Yes      | 1–12           | `*` `,` `-` `/`           |
| Day-of-week | Yes      | 0–6            | `*` `,` `-` `/`           |

Source: wiki-Cron.pdf, "Cron expression" table.

---

## Rules

**R1** — A standard cron expression has **exactly five** whitespace-separated fields.  
Source: wiki-Cron.pdf §"Cron expression" — "A cron expression is a string comprising five … fields separated by white space".

**R2** — The **minutes** field accepts values 0–59.  
Source: wiki-Cron.pdf §"Cron expression" table row "Minutes".

**R3** — The **hours** field accepts values 0–23.  
Source: wiki-Cron.pdf §"Cron expression" table row "Hours".

**R4** — The **day-of-month** field accepts values 1–31.  
Source: wiki-Cron.pdf §"Cron expression" table row "Day of month".

**R5** — The **month** field accepts values 1–12.  
Source: wiki-Cron.pdf §"Cron expression" table row "Month".

**R6** — The **day-of-week** field accepts values 0–6 (Sunday=0, Saturday=6).  
Source: wiki-Cron.pdf §"Cron expression" table row "Day of week".

**R7** — An asterisk `*` represents "all" valid values for a field (wildcard).  
Source: wiki-Cron.pdf §"Asterisk ( * )".

**R8** — A comma `,` separates items of a list; each item must itself be valid for the field.  
Source: wiki-Cron.pdf §"Comma ( , )".

**R9** — A hyphen `-` defines an inclusive range; start must be ≤ end and both must be within the field's allowed values.  
Source: wiki-Cron.pdf §"Hyphen ( - )".

**R10** — A slash `/` defines a step interval. In the form `*/n`, n must be ≥ 1.  
Source: wiki-Cron.pdf §"Slash ( / )" — "*/5 in the minutes field indicates every 5 minutes".

**R11** — Minutes=0, Hours=0, DOM=1, Month=1, DOW=* is the equivalent schedule for `@yearly` / `@annually`.  
Source: wiki-Cron.pdf §"Nonstandard predefined scheduling definitions" table.

**R12** — Minutes=0, Hours=0, DOM=*, Month=*, DOW=0 is the equivalent for `@weekly` (midnight Sunday).  
Source: wiki-Cron.pdf §"Nonstandard predefined scheduling definitions" table.

**R13** — Minutes=0, Hours=0, DOM=*, Month=*, DOW=* is the equivalent for `@daily` / `@midnight`.  
Source: wiki-Cron.pdf §"Nonstandard predefined scheduling definitions" table.

**R14** — Minutes=0, Hours=*, DOM=*, Month=*, DOW=* is the equivalent for `@hourly`.  
Source: wiki-Cron.pdf §"Nonstandard predefined scheduling definitions" table.

**R15** — `*/5 1,2,3 * * *` is cited in the spec as a valid expression (every 5th minute of hours 1, 2, and 3).  
Source: wiki-Cron.pdf §"Overview" example.

**R16** — `1 0 * * *` is valid (one minute past midnight every day).  
Source: wiki-Cron.pdf §"Overview" example.

**R17** — `45 23 * * 6` is valid (23:45 every Saturday).  
Source: wiki-Cron.pdf §"Overview" example.
