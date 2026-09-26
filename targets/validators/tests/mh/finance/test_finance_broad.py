"""Regression tests for validators.finance: cusip, isin, sedol."""

# Imports from public API only (Rule 1)
from validators import cusip, isin, sedol

# ---------------------------------------------------------------------------
# CUSIP
# ---------------------------------------------------------------------------


def test_cusip_known_valid_apple():
    """Docstring: cusip
    Apple Inc CUSIP (037833100) is a well-known valid CUSIP.
    """
    assert cusip("037833100")


def test_cusip_known_valid_037833dp2():
    """Docstring: cusip
    037833DP2 is the docstring example for cusip.
    """
    assert cusip("037833DP2")


def test_cusip_known_valid_912796x38():
    """Docstring: cusip
    912796X38 is listed as valid in the existing test suite.
    """
    assert cusip("912796X38")


def test_cusip_known_valid_912796x20():
    """Docstring: cusip
    912796X20 is listed as valid in the existing test suite.
    """
    assert cusip("912796X20")


def test_cusip_lowercase_accepted():
    """Docstring: cusip
    The checksum function accepts lowercase letters (maps same as uppercase).
    912796x20 (lower-x) should pass.
    """
    assert cusip("912796x20")


def test_cusip_digits_only_valid():
    """Docstring: cusip
    A CUSIP composed entirely of digits with a correct checksum must pass.
    000000000 has check digit 0 and all-zero body yields check==0.
    """
    assert cusip("000000000")


def test_cusip_letters_only_valid():
    """Docstring: cusip
    A CUSIP composed entirely of uppercase letters with a valid checksum must pass.
    AAAAAAAAH was verified by exhaustive search to produce check%10==0.
    """
    assert cusip("AAAAAAAAH")


def test_cusip_special_star_valid():
    """Docstring: cusip
    '*' maps to value 36 in the checksum; 037833*X0 was computed to be valid.
    """
    assert cusip("037833*X0")


def test_cusip_special_at_valid():
    """Docstring: cusip
    '@' maps to value 37 in the checksum; 037833@X9 was computed to be valid.
    """
    assert cusip("037833@X9")


def test_cusip_special_hash_valid():
    """Docstring: cusip
    '#' maps to value 38 in the checksum; 037833#X8 was computed to be valid.
    """
    assert cusip("037833#X8")


def test_cusip_wrong_check_digit():
    """Docstring: cusip
    037833DP3 differs from the valid 037833DP2 only in the last digit.
    """
    assert not cusip("037833DP3")


def test_cusip_wrong_check_digit_912796t67():
    """Docstring: cusip
    912796T67 has an incorrect check digit.
    """
    assert not cusip("912796T67")


def test_cusip_wrong_check_digit_912796t68():
    """Docstring: cusip
    912796T68 has an incorrect check digit.
    """
    assert not cusip("912796T68")


def test_cusip_too_short_8_chars():
    """Docstring: cusip
    A CUSIP of length 8 must be rejected (length must be exactly 9).
    """
    assert not cusip("037833DP")


def test_cusip_too_long_10_chars():
    """Docstring: cusip
    A CUSIP of length 10 must be rejected (length must be exactly 9).
    """
    assert not cusip("037833DP22")


def test_cusip_empty_string():
    """Docstring: cusip
    An empty string has length 0, not 9, so must be rejected.
    """
    assert not cusip("")


def test_cusip_invalid_char_bang():
    """Docstring: cusip
    '!' is not a valid CUSIP character; checksum returns False immediately.
    """
    assert not cusip("037833!P2")


def test_cusip_invalid_char_space():
    """Docstring: cusip
    A space is not a valid CUSIP character; checksum returns False.
    """
    assert not cusip("037833 P2")


def test_cusip_invalid_char_caret():
    """Docstring: cusip
    '^' is not a valid CUSIP character.
    """
    assert not cusip("00^^^1234A")  # also length 10 — doubly invalid


def test_cusip_all_zeros_wrong_check():
    """Docstring: cusip
    000000001 — all zeros body but wrong last digit (1 instead of 0).
    """
    assert not cusip("000000001")


# ---------------------------------------------------------------------------
# ISIN
# ---------------------------------------------------------------------------


def test_isin_known_valid_apple():
    """Docstring: isin
    US0378331005 is Apple Inc's ISIN; listed valid in the existing tests.
    """
    assert isin("US0378331005")


def test_isin_known_valid_us0004026250():
    """Docstring: isin
    US0004026250 is valid per existing test suite.
    """
    assert isin("US0004026250")


def test_isin_known_valid_jp000k0vf054():
    """Docstring: isin
    JP000K0VF054 is valid per existing test suite.
    """
    assert isin("JP000K0VF054")


def test_isin_known_valid_gb0002634946():
    """Docstring: isin
    GB0002634946 is a real, well-known ISIN with correct format.
    """
    assert isin("GB0002634946")


def test_isin_lowercase_country_code_accepted():
    """Docstring: isin
    The _isin_checksum function accepts a-z in addition to A-Z; lowercase
    country codes are treated as valid by the current implementation.
    us0378331005 (lower-case 'us') passes the checksum (check stays 0).
    """
    assert isin("us0378331005")


def test_isin_all_letters_12_chars():
    """Docstring: isin
    AAAAAAAAAAAA — 12 uppercase letters — passes because check==0 always.
    """
    assert isin("AAAAAAAAAAAA")


def test_isin_letters_then_digits():
    """Docstring: isin
    AA0000000000 — first 2 letters, remaining 10 digits — valid chars and
    length 12 so the buggy implementation accepts it.
    """
    assert isin("AA0000000000")


def test_isin_digit_at_position_0_rejected():
    """Docstring: isin
    '0' at index 0 is a digit; the guard (idx > 1) is False so the condition
    'c >= 0 and c <= 9 and idx > 1' is not met, and '0' is not A-Z or a-z
    either, so _isin_checksum returns False.
    """
    assert not isin("010378331005")


def test_isin_digit_at_position_1_rejected():
    """Docstring: isin
    A digit at index 1 also fails the idx > 1 guard, so 'A0XXXXXXXXXX'
    is rejected.
    """
    assert not isin("A0XXXXXXXXXX")


def test_isin_too_short_9_chars():
    """Docstring: isin
    A string of length 9 must be rejected (length must be exactly 12).
    """
    assert not isin("037833DP2")


def test_isin_too_short_11_chars():
    """Docstring: isin
    A string of length 11 must be rejected.
    """
    assert not isin("US037833100")


def test_isin_too_long_13_chars():
    """Docstring: isin
    A string of length 13 must be rejected.
    """
    assert not isin("US03783310050")


def test_isin_empty_string():
    """Docstring: isin
    An empty string must be rejected.
    """
    assert not isin("")


def test_isin_special_char_star_rejected():
    """Docstring: isin
    '*' is not accepted by _isin_checksum (not in 0-9/A-Z/a-z), so
    any ISIN containing it must be rejected.
    """
    assert not isin("US037833100*")


def test_isin_special_char_hash_rejected():
    """Docstring: isin
    '#' is not accepted by _isin_checksum.
    """
    assert not isin("US03783310#5")


def test_isin_digits_only_12_chars_rejected():
    """Docstring: isin
    000000000000 — all digits, length 12 — is rejected because digits at
    indices 0 and 1 are not A-Z/a-z and fail the idx>1 guard.
    """
    assert not isin("000000000000")


def test_isin_caret_chars_rejected():
    """Docstring: isin
    00^^^1234XXXX is rejected: both length and invalid chars.
    """
    assert not isin("00^^^1234XXX")  # length 12 but '^' at idx 2 fails


# ---------------------------------------------------------------------------
# SEDOL
# ---------------------------------------------------------------------------


def test_sedol_known_valid_0263494():
    """Docstring: sedol
    0263494 is listed valid in the existing test suite.
    """
    assert sedol("0263494")


def test_sedol_known_valid_0540528():
    """Docstring: sedol
    0540528 is listed valid in the existing test suite.
    """
    assert sedol("0540528")


def test_sedol_known_valid_b000009():
    """Docstring: sedol
    B000009 is listed valid in the existing test suite.
    """
    assert sedol("B000009")


def test_sedol_known_valid_2936921():
    """Docstring: sedol
    2936921 is the docstring example; weighted sum = 120, 120%10 == 0.
    """
    assert sedol("2936921")


def test_sedol_digits_only_valid():
    """Docstring: sedol
    0000000 — all zeros — has weighted sum 0, which is divisible by 10.
    """
    assert sedol("0000000")


def test_sedol_letters_only_no_vowels_valid():
    """Docstring: sedol
    BBBBBBG — all consonant letters — was verified to produce check%10==0.
    """
    assert sedol("BBBBBBG")


def test_sedol_wrong_check_digit():
    """Docstring: sedol
    0263495 differs from the valid 0263494 only in the last digit.
    """
    assert not sedol("0263495")


def test_sedol_wrong_check_digit_0540526():
    """Docstring: sedol
    0540526 is listed as invalid in the existing test suite.
    """
    assert not sedol("0540526")


def test_sedol_vowel_a_at_position_0():
    """Docstring: sedol
    'A' at position 0: AEIOU are explicitly rejected by the implementation.
    """
    assert not sedol("A000009")


def test_sedol_vowel_e_at_position_0():
    """Docstring: sedol
    'E' at position 0 must be rejected.
    """
    assert not sedol("E000009")


def test_sedol_vowel_i_at_position_0():
    """Docstring: sedol
    'I' at position 0 must be rejected.
    """
    assert not sedol("I000009")


def test_sedol_vowel_o_at_position_0():
    """Docstring: sedol
    'O' at position 0 must be rejected.
    """
    assert not sedol("O000009")


def test_sedol_vowel_u_at_position_0():
    """Docstring: sedol
    'U' at position 0 must be rejected.
    """
    assert not sedol("U000009")


def test_sedol_vowel_at_middle_position():
    """Docstring: sedol
    Vowel at position 2: '02E3494' must be rejected.
    """
    assert not sedol("02E3494")


def test_sedol_vowel_at_last_position():
    """Docstring: sedol
    Vowel at last position (index 6): '000000A' must be rejected.
    """
    assert not sedol("000000A")


def test_sedol_lowercase_rejected():
    """Docstring: sedol
    Lowercase letters are not accepted by sedol (only 0-9 and A-Z);
    'b000009' must be rejected.
    """
    assert not sedol("b000009")


def test_sedol_lowercase_rejected_full_lower():
    """Docstring: sedol
    All-lowercase SEDOL 'bbbbbbb' must be rejected.
    """
    assert not sedol("bbbbbbb")


def test_sedol_too_short_6_chars():
    """Docstring: sedol
    A SEDOL of length 6 must be rejected (length must be exactly 7).
    """
    assert not sedol("026349")


def test_sedol_too_long_8_chars():
    """Docstring: sedol
    A SEDOL of length 8 must be rejected.
    """
    assert not sedol("02634940")


def test_sedol_empty_string():
    """Docstring: sedol
    An empty string must be rejected.
    """
    assert not sedol("")


def test_sedol_special_char_caret_rejected():
    """Docstring: sedol
    '^' is not a digit or uppercase letter; must be rejected.
    """
    assert not sedol("00^^^12")


def test_sedol_special_char_star_rejected():
    """Docstring: sedol
    '*' is not a valid SEDOL character; must be rejected.
    """
    assert not sedol("0263*94")


def test_sedol_space_rejected():
    """Docstring: sedol
    A space character is not valid in a SEDOL.
    """
    assert not sedol("026 494")


def test_sedol_mixed_digit_letter_valid():
    """Docstring: sedol
    3319521 is a real SEDOL (verified checksum).
    """
    assert sedol("3319521")


def test_sedol_mixed_digit_letter_valid_7108899():
    """Docstring: sedol
    7108899 is a real SEDOL (verified checksum).
    """
    assert sedol("7108899")
