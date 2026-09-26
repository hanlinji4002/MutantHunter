"""Spec-driven tests for the ISIN validator.

Rules source: dataset/specs/txt/wiki-ISIN.txt
"""

# public API only
from validators import isin


# ---------------------------------------------------------------------------
# Oracle — self-contained ISIN check-digit calculator (must NOT import the
# validator being tested).
# ---------------------------------------------------------------------------

def _letter_to_digits(c: str) -> str:
    """Convert a single letter to its numeric string (ASCII(upper) - 55)."""
    return str(ord(c.upper()) - 55)


def _expand_isin_body(body: str) -> str:
    """Expand the 11-character ISIN body (without check digit) to all digits."""
    result = ""
    for c in body:
        if c.isdigit():
            result += c
        else:
            result += _letter_to_digits(c)
    return result


def _luhn_check_digit(digit_string: str) -> int:
    """Compute the Luhn check digit for a string of digits.

    Implements the algorithm from wiki-ISIN.txt § Examples:
    - Starting from the rightmost digit, double every second digit.
      The *rightmost* digit (distance 0 from right, i.e. i=0 when reversed)
      is in the group that gets doubled.
    - Sum all individual digits of the products.
    - check = (10 - (sum mod 10)) mod 10

    Spec example (Apple): expanded '3028037833100' → sum 45 → check 5.
    """
    total = 0
    digits = [int(d) for d in digit_string]
    # i=0 → rightmost → doubled; i=1 → second from right → not doubled; etc.
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 0:          # 0-indexed: even distance from right → doubled
            d *= 2
            total += (d // 10) + (d % 10)
        else:
            total += d
    return (10 - (total % 10)) % 10


def _oracle_isin_check_digit(isin_body_11: str) -> int:
    """Compute expected ISIN check digit for the first 11 characters."""
    expanded = _expand_isin_body(isin_body_11)
    return _luhn_check_digit(expanded)


# ---------------------------------------------------------------------------
# R13 — ISIN length must be exactly 12 characters
# ---------------------------------------------------------------------------

def test_isin_length_11_is_invalid():
    """Spec: wiki-ISIN.txt § Description — R13
    An 11-character string must not validate as an ISIN.
    """
    assert not isin("US037833100")


def test_isin_length_13_is_invalid():
    """Spec: wiki-ISIN.txt § Description — R13
    A 13-character string must not validate as an ISIN.
    """
    assert not isin("US0378331005X")


def test_isin_length_0_is_invalid():
    """Spec: wiki-ISIN.txt § Description — R13
    An empty string must not validate as an ISIN.
    """
    assert not isin("")


# ---------------------------------------------------------------------------
# R14 / R15 — First two characters must be letters (country code)
# ---------------------------------------------------------------------------

def test_isin_numeric_prefix_is_invalid():
    """Spec: wiki-ISIN.txt § Description — R14, R15
    A string whose first two characters are digits (no country code) must be invalid.
    '010378331005' starts with '01' — not a valid alphabetic country code.
    """
    assert not isin("010378331005")


def test_isin_mixed_first_char_digit_is_invalid():
    """Spec: wiki-ISIN.txt § Description — R15
    A string whose first character is a digit must be invalid.
    """
    assert not isin("1S0378331005")


# ---------------------------------------------------------------------------
# R17 — Luhn check digit algorithm on expanded string
# ---------------------------------------------------------------------------

def test_isin_oracle_apple_check_digit_is_5():
    """Spec: wiki-ISIN.txt § Examples — Apple, Inc. — R17
    The oracle must compute check digit 5 for 'US0378331005' body 'US037833100'.
    wiki-ISIN.txt explicitly states 'the ISIN check digit is five'.
    """
    assert _oracle_isin_check_digit("US037833100") == 5


def test_isin_oracle_treasury_vic_check_digit_is_3():
    """Spec: wiki-ISIN.txt § Examples — Treasury Corporation of Victoria — R17
    The oracle must compute check digit 3 for body 'AU0000XVGZA'.
    wiki-ISIN.txt explicitly states 'the ISIN check digit is three'.
    """
    assert _oracle_isin_check_digit("AU0000XVGZA") == 3


# ---------------------------------------------------------------------------
# R18 — Example: Apple Inc. (US0378331005)
# ---------------------------------------------------------------------------

def test_isin_valid_apple():
    """Spec: wiki-ISIN.txt § Examples — Apple, Inc. — R18
    'US0378331005' must be a valid ISIN.
    """
    assert isin("US0378331005")


# ---------------------------------------------------------------------------
# R19 — Example: Treasury Corporation of Victoria (AU0000XVGZA3)
# ---------------------------------------------------------------------------

def test_isin_valid_treasury_corp_victoria():
    """Spec: wiki-ISIN.txt § Examples — Treasury Corporation of Victoria — R19
    'AU0000XVGZA3' must be a valid ISIN.
    """
    assert isin("AU0000XVGZA3")


# ---------------------------------------------------------------------------
# R20 — Example: BAE Systems (GB0002634946)
# ---------------------------------------------------------------------------

def test_isin_valid_bae_systems():
    """Spec: wiki-ISIN.txt § Examples — BAE Systems — R20
    'GB0002634946' must be a valid ISIN.
    """
    assert isin("GB0002634946")


# ---------------------------------------------------------------------------
# R22 — Non-letter country code prefix is invalid
# ---------------------------------------------------------------------------

def test_isin_digits_only_12_chars_is_invalid():
    """Spec: wiki-ISIN.txt § Description — R22
    A 12-digit string with no letter prefix must be invalid.
    """
    assert not isin("123456789012")


# ---------------------------------------------------------------------------
# R23 — Known flaw: transposed letters AU0000VXGZA3 also validates (documented)
# ---------------------------------------------------------------------------

def test_isin_known_flaw_transposed_letters_also_valid():
    """Spec: wiki-ISIN.txt § Check-digit flaw in ISIN — R23
    'AU0000VXGZA3' (V and X transposed vs. 'AU0000XVGZA3') also has check
    digit 3 per the spec's own worked example, and therefore also validates.
    This is a documented limitation, not a code error.
    """
    assert isin("AU0000VXGZA3")
