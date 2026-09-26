# Finance Validation Rules

Extracted from:
- `wiki-CUSIP.txt` (CUSIP spec)
- `wiki-ISIN.txt` (ISIN spec)
- `wiki-SEDOL.txt` (SEDOL spec)

---

## CUSIP Rules

## R1 — CUSIP total length is exactly 9 characters
- Source: wiki-CUSIP.txt § Format
- Rule: A CUSIP is a nine-character alphanumeric code.

## R2 — CUSIP character set (positions 1–8)
- Source: wiki-CUSIP.txt § Format / Check digit pseudocode
- Rule: Each of the first 8 characters must be a digit (0–9), an uppercase or lowercase letter (A–Z, a–z), or one of the three special characters `*`, `@`, `#`. Any other character is invalid.

## R3 — CUSIP letters map to values A=10…Z=35
- Source: wiki-CUSIP.txt § Format
- Rule: Letters are converted to numbers based on their ordinal position in the alphabet, starting with A equal to 10 (i.e., value = ordinal_position + 9). Lowercase treated identically to uppercase.

## R4 — CUSIP special-character values
- Source: wiki-CUSIP.txt § Check digit pseudocode
- Rule: `*` = 36, `@` = 37, `#` = 38.

## R5 — CUSIP check digit algorithm (Modulus 10 Double Add Double / Luhn-derived)
- Source: wiki-CUSIP.txt § Format, Check digit pseudocode
- Rule: For each of the first 8 characters (0-indexed i = 0…7): compute value v (digit → face value; letter → ordinal+9; special → 36/37/38). If i is **odd** (1-based even position), double v. Add `floor(v/10) + (v mod 10)` to a running sum. The 9th character is valid when `sum mod 10 == 0`.

## R6 — CUSIP example: Apple Inc.
- Source: wiki-CUSIP.txt § Examples
- Rule: `037833100` is a valid CUSIP.

## R7 — CUSIP example: Cisco Systems
- Source: wiki-CUSIP.txt § Examples
- Rule: `17275R102` is a valid CUSIP.

## R8 — CUSIP example: Google Inc.
- Source: wiki-CUSIP.txt § Examples
- Rule: `38259P508` is a valid CUSIP.

## R9 — CUSIP example: Microsoft Corporation
- Source: wiki-CUSIP.txt § Examples
- Rule: `594918104` is a valid CUSIP.

## R10 — CUSIP example: Oracle Corporation
- Source: wiki-CUSIP.txt § Examples
- Rule: `68389X105` is a valid CUSIP.

## R11 — CUSIP example: 3½% Treasury Gilt 2068
- Source: wiki-CUSIP.txt § Examples
- Rule: `EJ7125481` is a valid CUSIP.

## R12 — CUSIP wrong check digit is invalid
- Source: wiki-CUSIP.txt § Check digit pseudocode (implied)
- Rule: A 9-character string that is otherwise well-formed but has an incorrect check digit must not validate.

---

## ISIN Rules

## R13 — ISIN total length is exactly 12 characters
- Source: wiki-ISIN.txt § Description
- Rule: ISINs are always 12 characters in length.

## R14 — ISIN structure: 2-letter country code + 9-character NSIN + 1 check digit
- Source: wiki-ISIN.txt § Description
- Rule: An ISIN consists of two alphabetic characters (ISO 3166-1 alpha-2 country code), nine alpha-numeric characters (the NSIN), and one numerical check digit.

## R15 — ISIN first two characters must be letters (country code)
- Source: wiki-ISIN.txt § Description
- Rule: The first two positions must be alphabetic (A–Z or a–z), representing the country code.

## R16 — ISIN check digit is a single decimal digit
- Source: wiki-ISIN.txt § Description
- Rule: The last character of an ISIN is a single numerical check digit (0–9).

## R17 — ISIN check digit algorithm (Luhn on expanded string)
- Source: wiki-ISIN.txt § Examples (Apple and Treasury Corp Victoria)
- Rule: Each letter in positions 1–11 is replaced by its numeric value = ASCII(uppercase_letter) − 55 (i.e., A=10, B=11, …, Z=35). The resulting all-digit string (without the check digit) is then subjected to the Luhn algorithm: starting from the rightmost digit, alternately double every second digit; sum all individual digits; the check digit is `(10 − (sum mod 10)) mod 10`.

## R18 — ISIN example: Apple Inc.
- Source: wiki-ISIN.txt § Examples — Apple, Inc.
- Rule: `US0378331005` is a valid ISIN (check digit = 5).

## R19 — ISIN example: Treasury Corporation of Victoria
- Source: wiki-ISIN.txt § Examples — Treasury Corporation of Victoria
- Rule: `AU0000XVGZA3` is a valid ISIN (check digit = 3).

## R20 — ISIN example: BAE Systems
- Source: wiki-ISIN.txt § Examples — BAE Systems
- Rule: `GB0002634946` is a valid ISIN.

## R21 — ISIN wrong check digit is invalid
- Source: wiki-ISIN.txt § Examples (implied by algorithm)
- Rule: A 12-character string that is otherwise well-formed but whose last digit does not satisfy the Luhn check must not validate.

## R22 — ISIN with non-letter country code prefix is invalid
- Source: wiki-ISIN.txt § Description
- Rule: A string whose first two characters are not alphabetic (e.g., starts with digits) must not validate as an ISIN, even if it is otherwise 12 characters long.

## R23 — ISIN check digit flaw: transposed letters can pass (known limitation, not a code bug)
- Source: wiki-ISIN.txt § Check-digit flaw in ISIN
- Rule: `AU0000VXGZA3` (letters V and X transposed relative to the valid `AU0000XVGZA3`) also produces check digit 3 and therefore also passes the Luhn check. Both strings validate as true — this is a documented property of the algorithm, not an error.

---

## SEDOL Rules

## R24 — SEDOL total length is exactly 7 characters
- Source: wiki-SEDOL.txt § Description
- Rule: SEDOLs are seven characters in length.

## R25 — SEDOL structure: 6 alphanumeric characters + 1 check digit
- Source: wiki-SEDOL.txt § Description
- Rule: A SEDOL consists of a six-place alphanumeric code followed by a trailing check digit.

## R26 — SEDOL character set: digits and consonants only (no vowels A, E, I, O, U)
- Source: wiki-SEDOL.txt § Description / JavaScript code
- Rule: Valid SEDOL characters are digits 0–9 and uppercase consonants (B, C, D, F, G, H, J, K, L, M, N, P, Q, R, S, T, V, W, X, Y, Z). Vowels (A, E, I, O, U) must never appear in a SEDOL.

## R27 — SEDOL letter values: B=11, C=12, …, Z=35 (9 + alphabet position, vowels skipped in issuance but valued continuously)
- Source: wiki-SEDOL.txt § Description
- Rule: Letters have the value of 9 plus their alphabet position (A=10, B=11, …, Z=35). Although vowels are never used in SEDOLs, they are not ignored when computing the weighted sum — the alphabet is continuous.

## R28 — SEDOL check digit weights
- Source: wiki-SEDOL.txt § Description
- Rule: The weights for positions 1–7 are [1, 3, 1, 7, 3, 9, 1]. The check digit (position 7) has weight 1.

## R29 — SEDOL check digit algorithm
- Source: wiki-SEDOL.txt § Description
- Rule: The check digit is chosen to make the total weighted sum of all seven characters a multiple of 10. It is calculated from the first six characters as: `check = (10 − (weighted_sum mod 10)) mod 10`.

## R30 — SEDOL example: BAE Systems
- Source: wiki-SEDOL.txt § Example
- Rule: `0263494` is a valid SEDOL. Weighted sum of first 6 = (0×1 + 2×3 + 6×1 + 3×7 + 4×3 + 9×9) = 126; check digit = (10 − 126 mod 10) mod 10 = 4.

## R31 — SEDOL example from existing tests: B000009
- Source: wiki-SEDOL.txt § Description (sequential issuance begins with B000009)
- Rule: `B000009` is a valid SEDOL (first alphanumeric SEDOL issued after January 2004).

## R32 — SEDOL wrong check digit is invalid
- Source: wiki-SEDOL.txt § Description (implied by algorithm)
- Rule: A 7-character SEDOL-format string with an incorrect check digit must not validate.

## R33 — SEDOL with vowel in any position is invalid
- Source: wiki-SEDOL.txt § Description / JavaScript code (`/^[0-9BCDFGHJKLMNPQRSTVWXYZ]{6}$/`)
- Rule: A SEDOL string containing a vowel (A, E, I, O, U) in any position is invalid.
