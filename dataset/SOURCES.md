# Data sources and licenses

All data was retrieved on 2026-09-25.

| Data | Source | License |
|---|---|---|
| python-validators source code and git history | https://github.com/python-validators/validators (commit `70de324`) | MIT |
| RFC 791, 952, 1034, 1035, 1123, 2782, 3986, 4291, 4632, 5321, 5322, 5952 | https://www.rfc-editor.org/ (official `.txt`, converted to PDF with macOS `cupsfilter`, content unchanged) | IETF Trust Legal Provisions: may be copied and distributed in full |
| RFC 9562 | https://www.rfc-editor.org/rfc/rfc9562.pdf (official PDF) | IETF Trust Legal Provisions |
| BIP-173, BIP-350 | https://github.com/bitcoin/bips (MediaWiki source, converted to PDF, content unchanged) | BSD-2-Clause |
| Wikipedia (English): ISO 3166-1, ISO 4217, List of country calling codes, Cron, International Securities Identification Number, CUSIP, SEDOL, Base58, INSEE code, Departments of France, MAC address | https://en.wikipedia.org/api/rest_v1/page/pdf/ | CC BY-SA 4.0 (attribution required) |
| Wikipedia (French): Numéro de sécurité sociale en France | https://fr.wikipedia.org/api/rest_v1/page/pdf/ | CC BY-SA 4.0 |
| Wikipedia (Russian): Идентификационный номер налогоплательщика | https://ru.wikipedia.org/api/rest_v1/page/pdf/ | CC BY-SA 4.0 |
| Wikipedia (Finnish): Henkilötunnus, Y-tunnus | https://fi.wikipedia.org/api/rest_v1/page/pdf/ | CC BY-SA 4.0 |
| `specs/txt/` | generated from the PDFs above with `pdftotext -layout` | same as the source document |

`ref_*` values in `modules.csv` and the `human_tests_at_HEAD` column in `bug_commits.csv` were computed by running the project's own test suite on the code above.
