# MutantHunter — Statistics

## Split B (hold-out)

### Main modules

| Suite | k | n | Score | 95% CI |
|---|---|---|---|---|
| B0 | 85 | 141 | 60.3% | 52.0–68.0% |
| B1 | 109 | 141 | 77.3% | 69.7–83.4% |
| MH | 110 | 141 | 78.0% | 70.5–84.1% |

McNemar B1 vs MH (split B, main): b=2, c=3, p=1.0000

### Extra modules

| Suite | k | n | Score | 95% CI |
|---|---|---|---|---|
| B0 | 17 | 19 | 89.5% | 68.6–97.1% |
| B1 | 17 | 19 | 89.5% | 68.6–97.1% |
| MH | 17 | 19 | 89.5% | 68.6–97.1% |

McNemar B1 vs MH (split B, extra): b=0, c=0, p=1.0000

## Exam C (out-of-distribution)

### Main modules

| Suite | k | n | Score | 95% CI |
|---|---|---|---|---|
| B0 | 96 | 146 | 65.8% | 57.7–73.0% |
| B1 | 112 | 146 | 76.7% | 69.2–82.8% |
| MH | 120 | 146 | 82.2% | 75.2–87.5% |

McNemar B1 vs MH (split C, main): b=1, c=9, p=0.0215

### Extra modules

| Suite | k | n | Score | 95% CI |
|---|---|---|---|---|
| B0 | 14 | 33 | 42.4% | 27.2–59.2% |
| B1 | 25 | 33 | 75.8% | 59.0–87.2% |
| MH | 26 | 33 | 78.8% | 62.3–89.3% |

McNemar B1 vs MH (split C, extra): b=2, c=3, p=1.0000

## Per-module split-A scores

| Module | Set | B0 before | MH after | Δ | Tests kept | Bugs | Minutes | Bobcoins |
|---|---|---|---|---|---|---|---|---|
| between | reference | — | — | — | — | — | — | — |
| card | reference | — | — | — | — | — | — | — |
| country | main | — | — | — | — | — | — | — |
| cron | main | 58.1% | 74.2% | +16.1% | 207 | 0 | 11.1 | 6.54 |
| crypto_addresses/btc_address | reference | — | — | — | — | — | — | — |
| crypto_addresses/trx_address | reference | — | — | — | — | — | — | — |
| domain | main | — | — | — | — | — | — | — |
| email | main | 81.8% | 90.9% | +9.1% | 132 | 4 | 8.5 | 7.9 |
| encoding | reference | — | — | — | — | — | — | — |
| finance | main | 68.9% | 82.0% | +13.1% | 120 | 4 | 9.8 | 5.61 |
| hashes | reference | — | — | — | — | — | — | — |
| hostname | extra | 83.3% | 83.3% | +0.0% | 166 | 1 | 5.0 | 3.84 |
| i18n/es | reference | — | — | — | — | — | — | — |
| i18n/fi | main | — | — | — | — | — | — | — |
| i18n/fr | main | — | — | — | — | — | — | — |
| i18n/ind | reference | — | — | — | — | — | — | — |
| i18n/ru | reference | — | — | — | — | — | — | — |
| iban | reference | — | — | — | — | — | — | — |
| ip_address | main | — | — | — | — | — | — | — |
| length | reference | — | — | — | — | — | — | — |
| mac_address | extra | 80.0% | 80.0% | +0.0% | 83 | 1 | 4.5 | 2.54 |
| slug | reference | — | — | — | — | — | — | — |
| url | main | 53.1% | 65.6% | +12.5% | 234 | 3 | 13.2 | 11.07 |
| uuid | main | — | — | — | — | — | — | — |

## Suspected violations

| Category | Count |
|---|---|
| logic | 12 |
| data-staleness | 0 |
| spec-ambiguous | 1 |
| human-test-conflict | 0 |

