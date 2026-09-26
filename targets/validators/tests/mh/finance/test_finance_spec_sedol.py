"""Spec-driven tests for the SEDOL validator.

Rules source: dataset/specs/txt/wiki-SEDOL.txt
"""

# public API only
from validators import sedol


# ---------------------------------------------------------------------------
# Oracle — self-contained SEDOL check-digit calculator (must NOT import the
# validator being tested).
# ---------------------------------------------------------------------------

_SEDOL_WEIGHTS = [1, 3, 1, 7, 3, 9, 1]


def _char_value(c: str) -> int:
    """Return the numeric value of a single SEDOL character.

    Digits → face value (0–9).
    Letters → 9 + alphabet position (A=10, B=11, …, Z=35).
    wiki-SEDOL.txt § Description: 'Letters have the value of 9 plus their
    alphabet position, such that B = 11 and Z = 35.'
    """
    if c.isdigit():
        return int(c)
    return 9 + (ord(c.upper()) - ord("A") + 1)


def _oracle_sedol_check_digit(first6: str) -> int:
    """Compute the expected SEDOL check digit from the first 6 characters.

    wiki-SEDOL.txt § Description:
    check = (10 − (weighted_sum mod 10)) mod 10
    """
    total = sum(_char_value(c) * _SEDOL_WEIGHTS[i] for i, c in enumerate(first6))
    return (10 - (total % 10)) % 10


# ---------------------------------------------------------------------------
# R24 — SEDOL length must be exactly 7 characters
# ---------------------------------------------------------------------------

def test_sedol_length_6_is_invalid():
    """Spec: wiki-SEDOL.txt § Description — R24
    A 6-character string must not validate as a SEDOL.
    """
    assert not sedol("026349")


def test_sedol_length_8_is_invalid():
    """Spec: wiki-SEDOL.txt § Description — R24
    An 8-character string must not validate as a SEDOL.
    """
    assert not sedol("02634940")


def test_sedol_length_0_is_invalid():
    """Spec: wiki-SEDOL.txt § Description — R24
    An empty string must not validate as a SEDOL.
    """
    assert not sedol("")


# ---------------------------------------------------------------------------
# R26 — Vowels are never allowed in a SEDOL
# ---------------------------------------------------------------------------

def test_sedol_vowel_A_is_invalid():
    """Spec: wiki-SEDOL.txt § Description — R26
    A SEDOL containing 'A' must be invalid (vowels not permitted).
    """
    assert not sedol("A000009")


def test_sedol_vowel_E_is_invalid():
    """Spec: wiki-SEDOL.txt § Description — R26
    A SEDOL containing 'E' must be invalid (vowels not permitted).
    """
    # Compute a string with 'E' and correct-looking check digit just to test
    # the character-set check; actual check digit doesn't matter here.
    assert not sedol("E000001")


def test_sedol_vowel_I_is_invalid():
    """Spec: wiki-SEDOL.txt § Description — R26
    A SEDOL containing 'I' must be invalid (vowels not permitted).
    """
    assert not sedol("I000001")


def test_sedol_vowel_O_is_invalid():
    """Spec: wiki-SEDOL.txt § Description — R26
    A SEDOL containing 'O' must be invalid (vowels not permitted).
    """
    assert not sedol("O000001")


def test_sedol_vowel_U_is_invalid():
    """Spec: wiki-SEDOL.txt § Description — R26
    A SEDOL containing 'U' must be invalid (vowels not permitted).
    """
    assert not sedol("U000001")


def test_sedol_vowel_in_non_first_position_is_invalid():
    """Spec: wiki-SEDOL.txt § Description — R26
    A SEDOL with a vowel in a non-first position must also be invalid.
    '0A0000x' contains 'A' at position 2.
    """
    assert not sedol("0A00001")


# ---------------------------------------------------------------------------
# R27 — Letter values: 9 + alphabet position (B=11, Z=35)
# ---------------------------------------------------------------------------

def test_sedol_oracle_char_value_B_is_11():
    """Spec: wiki-SEDOL.txt § Description — R27
    The oracle must return 11 for letter 'B' (9 + 2 = 11).
    """
    assert _char_value("B") == 11


def test_sedol_oracle_char_value_Z_is_35():
    """Spec: wiki-SEDOL.txt § Description — R27
    The oracle must return 35 for letter 'Z' (9 + 26 = 35).
    """
    assert _char_value("Z") == 35


def test_sedol_oracle_char_value_digit_7_is_7():
    """Spec: wiki-SEDOL.txt § Description — R27
    The oracle must return 7 for digit '7'.
    """
    assert _char_value("7") == 7


# ---------------------------------------------------------------------------
# R28 — Weights are [1, 3, 1, 7, 3, 9, 1]
# ---------------------------------------------------------------------------

def test_sedol_weights_correct():
    """Spec: wiki-SEDOL.txt § Description — R28
    The weight array must be exactly [1, 3, 1, 7, 3, 9, 1].
    """
    assert _SEDOL_WEIGHTS == [1, 3, 1, 7, 3, 9, 1]


# ---------------------------------------------------------------------------
# R29 — Check digit algorithm: (10 - sum mod 10) mod 10
# ---------------------------------------------------------------------------

def test_sedol_oracle_bae_check_digit_is_4():
    """Spec: wiki-SEDOL.txt § Example — R29, R30
    Oracle must compute check digit 4 for BAE Systems first-6 '026349'.
    Spec states: (10 − 126 mod 10) mod 10 = 4.
    """
    assert _oracle_sedol_check_digit("026349") == 4


# ---------------------------------------------------------------------------
# R30 — Example: BAE Systems (0263494)
# ---------------------------------------------------------------------------

def test_sedol_valid_bae_systems():
    """Spec: wiki-SEDOL.txt § Example — R30
    '0263494' (BAE Systems) must be a valid SEDOL.
    """
    assert sedol("0263494")


# ---------------------------------------------------------------------------
# R31 — Example: B000009 (first alphanumeric SEDOL after Jan 2004)
# ---------------------------------------------------------------------------

def test_sedol_valid_b000009():
    """Spec: wiki-SEDOL.txt § Description — R31
    'B000009' is the first alphanumeric SEDOL issued after January 2004 and
    must be valid.
    """
    assert sedol("B000009")


# ---------------------------------------------------------------------------
# R32 — Wrong check digit is invalid
# ---------------------------------------------------------------------------

def test_sedol_invalid_wrong_check_digit_bae():
    """Spec: wiki-SEDOL.txt § Example — R32
    '0263495' (check digit 5 instead of 4 for BAE Systems) must be invalid.
    """
    assert not sedol("0263495")


def test_sedol_invalid_wrong_check_digit_b000009():
    """Spec: wiki-SEDOL.txt § Description — R32
    'B000001' has incorrect check digit (should be 9) and must be invalid.
    """
    assert not sedol("B000001")


# ---------------------------------------------------------------------------
# R33 — Invalid characters (non-digit, non-consonant)
# ---------------------------------------------------------------------------

def test_sedol_invalid_special_char():
    """Spec: wiki-SEDOL.txt § Description / JavaScript code — R33
    A SEDOL containing a special character ('@') must be invalid.
    """
    assert not sedol("@26349X")


def test_sedol_invalid_space():
    """Spec: wiki-SEDOL.txt § Description — R33
    A SEDOL containing a space must be invalid.
    """
    assert not sedol("026 494")


# ---------------------------------------------------------------------------
# Positive: additional consonant-letter SEDOL validated against oracle
# ---------------------------------------------------------------------------

def test_sedol_valid_consonant_sedol_oracle_derived():
    """Spec: wiki-SEDOL.txt § Description — R25, R29
    Build a valid SEDOL 'B000009' via oracle to confirm the algorithm is
    consistent with a known-good example.
    """
    first6 = "B00000"
    check = _oracle_sedol_check_digit(first6)
    candidate = first6 + str(check)
    assert sedol(candidate)
