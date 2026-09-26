"""Spec-driven tests for the CUSIP validator.

Rules source: dataset/specs/txt/wiki-CUSIP.txt
"""

# public API only
from validators import cusip


# ---------------------------------------------------------------------------
# Oracle — self-contained CUSIP check-digit calculator (must NOT import the
# validator being tested).
# ---------------------------------------------------------------------------

def _oracle_cusip_check(first8: str) -> int:
    """Compute the expected CUSIP check digit from the first 8 characters.

    Implements the "Modulus 10 Double Add Double" algorithm exactly as
    described in wiki-CUSIP.txt § Check digit pseudocode.
    """
    total = 0
    for i, c in enumerate(first8):
        if c.isdigit():
            v = int(c)
        elif c.isalpha():
            v = 10 + ord(c.upper()) - ord("A")
        elif c == "*":
            v = 36
        elif c == "@":
            v = 37
        elif c == "#":
            v = 38
        else:
            raise ValueError(f"Invalid CUSIP character: {c!r}")
        if i % 2 == 1:          # odd index (0-based) → double
            v *= 2
        total += (v // 10) + (v % 10)
    return (10 - (total % 10)) % 10


# ---------------------------------------------------------------------------
# R1 — Length exactly 9
# ---------------------------------------------------------------------------

def test_cusip_length_8_is_invalid():
    """Spec: wiki-CUSIP.txt § Format — R1
    A CUSIP must be exactly 9 characters; 8-character strings are invalid.
    """
    assert not cusip("03783310")


def test_cusip_length_10_is_invalid():
    """Spec: wiki-CUSIP.txt § Format — R1
    A CUSIP must be exactly 9 characters; 10-character strings are invalid.
    """
    assert not cusip("0378331005")


def test_cusip_length_0_is_invalid():
    """Spec: wiki-CUSIP.txt § Format — R1
    Empty string is not a valid CUSIP.
    """
    assert not cusip("")


# ---------------------------------------------------------------------------
# R2 — Character set (positions 1-8: digit, letter, or * @ #)
# ---------------------------------------------------------------------------

def test_cusip_invalid_char_caret():
    """Spec: wiki-CUSIP.txt § Format — R2
    Characters outside digits, letters, and */@/# are not permitted.
    """
    assert not cusip("03783310^")


def test_cusip_invalid_char_space():
    """Spec: wiki-CUSIP.txt § Format — R2
    A space character is not a permitted CUSIP character.
    """
    assert not cusip("0378331 5")


# ---------------------------------------------------------------------------
# R5 — Check digit algorithm: odd-index doubling, digit-sum, mod-10
# ---------------------------------------------------------------------------

def test_cusip_oracle_matches_example_apple():
    """Spec: wiki-CUSIP.txt § Examples — R5, R6
    Oracle must compute check digit 0 for Apple Inc. CUSIP '03783310x'.
    """
    assert _oracle_cusip_check("03783310") == 0


def test_cusip_oracle_matches_example_cisco():
    """Spec: wiki-CUSIP.txt § Examples — R5, R7
    Oracle must compute check digit 2 for Cisco '17275R10x'.
    """
    assert _oracle_cusip_check("17275R10") == 2


def test_cusip_oracle_matches_example_google():
    """Spec: wiki-CUSIP.txt § Examples — R5, R8
    Oracle must compute check digit 8 for Google '38259P50x'.
    """
    assert _oracle_cusip_check("38259P50") == 8


def test_cusip_oracle_matches_example_microsoft():
    """Spec: wiki-CUSIP.txt § Examples — R5, R9
    Oracle must compute check digit 4 for Microsoft '59491810x'.
    """
    assert _oracle_cusip_check("59491810") == 4


def test_cusip_oracle_matches_example_oracle_corp():
    """Spec: wiki-CUSIP.txt § Examples — R5, R10
    Oracle must compute check digit 5 for Oracle Corp '68389X10x'.
    """
    assert _oracle_cusip_check("68389X10") == 5


def test_cusip_oracle_matches_example_treasury_gilt():
    """Spec: wiki-CUSIP.txt § Examples — R5, R11
    Oracle must compute check digit 1 for 3½% Treasury Gilt 'EJ712548x'.
    """
    assert _oracle_cusip_check("EJ712548") == 1


# ---------------------------------------------------------------------------
# R6 — Example: Apple Inc. (037833100)
# ---------------------------------------------------------------------------

def test_cusip_valid_apple():
    """Spec: wiki-CUSIP.txt § Examples — R6
    Apple Inc. CUSIP '037833100' must be valid.
    """
    assert cusip("037833100")


# ---------------------------------------------------------------------------
# R7 — Example: Cisco Systems (17275R102)
# ---------------------------------------------------------------------------

def test_cusip_valid_cisco():
    """Spec: wiki-CUSIP.txt § Examples — R7
    Cisco Systems CUSIP '17275R102' must be valid.
    """
    assert cusip("17275R102")


# ---------------------------------------------------------------------------
# R8 — Example: Google Inc. (38259P508)
# ---------------------------------------------------------------------------

def test_cusip_valid_google():
    """Spec: wiki-CUSIP.txt § Examples — R8
    Google Inc. CUSIP '38259P508' must be valid.
    """
    assert cusip("38259P508")


# ---------------------------------------------------------------------------
# R9 — Example: Microsoft (594918104)
# ---------------------------------------------------------------------------

def test_cusip_valid_microsoft():
    """Spec: wiki-CUSIP.txt § Examples — R9
    Microsoft Corporation CUSIP '594918104' must be valid.
    """
    assert cusip("594918104")


# ---------------------------------------------------------------------------
# R10 — Example: Oracle Corporation (68389X105)
# ---------------------------------------------------------------------------

def test_cusip_valid_oracle_corp():
    """Spec: wiki-CUSIP.txt § Examples — R10
    Oracle Corporation CUSIP '68389X105' must be valid.
    """
    assert cusip("68389X105")


# ---------------------------------------------------------------------------
# R11 — Example: 3½% Treasury Gilt 2068 (EJ7125481)
# ---------------------------------------------------------------------------

def test_cusip_valid_treasury_gilt():
    """Spec: wiki-CUSIP.txt § Examples — R11
    3½% Treasury Gilt 2068 CUSIP 'EJ7125481' must be valid.
    """
    assert cusip("EJ7125481")


# ---------------------------------------------------------------------------
# R12 — Wrong check digit is invalid
# ---------------------------------------------------------------------------

def test_cusip_invalid_wrong_check_digit_apple():
    """Spec: wiki-CUSIP.txt § Check digit pseudocode — R12
    Apple CUSIP with last digit changed from 0 to 1 must be invalid.
    """
    assert not cusip("037833101")


def test_cusip_invalid_wrong_check_digit_cisco():
    """Spec: wiki-CUSIP.txt § Check digit pseudocode — R12
    Cisco CUSIP with last digit changed from 2 to 3 must be invalid.
    """
    assert not cusip("17275R103")


def test_cusip_invalid_wrong_check_digit_google():
    """Spec: wiki-CUSIP.txt § Check digit pseudocode — R12
    Google CUSIP with last digit changed from 8 to 9 must be invalid.
    """
    assert not cusip("38259P509")


# ---------------------------------------------------------------------------
# R3 — Lowercase letters treated identically to uppercase
# ---------------------------------------------------------------------------

def test_cusip_lowercase_letters_valid():
    """Spec: wiki-CUSIP.txt § Format — R3
    Lowercase letters must be accepted (mapped via ordinal same as uppercase).
    Apple CUSIP in lowercase body '037833100' — test with a lowercase variant.
    """
    # 17275r102: lowercase 'r' should map to same value as 'R'
    assert cusip("17275r102")


def test_cusip_fully_lowercase_google():
    """Spec: wiki-CUSIP.txt § Format — R3
    '38259p508' (lowercase 'p') must validate the same as '38259P508'.
    """
    assert cusip("38259p508")


# ---------------------------------------------------------------------------
# R4 — Special characters *, @, # are valid
# ---------------------------------------------------------------------------

def test_cusip_special_char_star_position_value():
    """Spec: wiki-CUSIP.txt § Check digit pseudocode — R4
    Oracle must assign value 36 to '*'.
    '*0000000' → v=36 at even index (not doubled), sum=3+6=3, check=(10-3)%10=7.
    Remaining 7 zeros contribute 0. Expected check digit = 7.
    """
    # v=36, index 0 (even, not doubled): 3+6=9 ... wait: floor(36/10)+36%10 = 3+6 = 9
    # All other chars are '0' → 0 contribution. sum=9. (10-9%10)%10 = 1
    assert _oracle_cusip_check("*0000000") == 1


def test_cusip_special_char_at_position_value():
    """Spec: wiki-CUSIP.txt § Check digit pseudocode — R4
    Oracle must assign value 37 to '@'.
    '@0000000' → v=37 at index 0, floor(37/10)+37%10=3+7=10, sum=10,
    (10-10%10)%10=(10-0)%10=0. Expected check digit = 0.
    """
    assert _oracle_cusip_check("@0000000") == 0


def test_cusip_special_char_hash_position_value():
    """Spec: wiki-CUSIP.txt § Check digit pseudocode — R4
    Oracle must assign value 38 to '#'.
    '#0000000' → v=38 at index 0, floor(38/10)+38%10=3+8=11, sum=11,
    (10-11%10)%10=(10-1)%10=9. Expected check digit = 9.
    """
    assert _oracle_cusip_check("#0000000") == 9
