"""Broad regression tests for the mac_address validator."""

# local
from validators import mac_address


# ---------------------------------------------------------------------------
# Valid MAC addresses — colon-separated
# ---------------------------------------------------------------------------


def test_valid_colon_lowercase():
    """Docstring: mac_address"""
    assert mac_address("01:23:45:67:ab:cd")


def test_valid_colon_uppercase():
    """Docstring: mac_address"""
    assert mac_address("01:23:45:67:AB:CD")


def test_valid_colon_mixed_case():
    """Docstring: mac_address"""
    assert mac_address("01:23:45:67:ab:CD")


def test_valid_colon_all_zeros():
    """Characterization: all-zero MAC is structurally valid"""
    assert mac_address("00:00:00:00:00:00")


def test_valid_colon_all_fs():
    """Characterization: broadcast MAC ff:ff:ff:ff:ff:ff is structurally valid"""
    assert mac_address("ff:ff:ff:ff:ff:ff")


def test_valid_colon_all_Fs_uppercase():
    """Characterization: broadcast MAC FF:FF:FF:FF:FF:FF is structurally valid"""
    assert mac_address("FF:FF:FF:FF:FF:FF")


def test_valid_colon_hex_digits_0_to_9():
    """Characterization: colon-separated MAC using digits 0–9 only"""
    assert mac_address("01:23:45:67:89:00")


def test_valid_colon_hex_a_to_f_lowercase():
    """Characterization: colon-separated MAC using a–f only"""
    assert mac_address("aa:bb:cc:dd:ee:ff")


def test_valid_colon_hex_A_to_F_uppercase():
    """Characterization: colon-separated MAC using A–F only"""
    assert mac_address("AA:BB:CC:DD:EE:FF")


def test_valid_colon_leading_zero_octets():
    """Characterization: octets that start with 0 are valid"""
    assert mac_address("0A:0B:0C:0D:0E:0F")


def test_valid_colon_docstring_example():
    """Docstring: mac_address"""
    assert mac_address("01:23:45:67:ab:CD")


# ---------------------------------------------------------------------------
# Valid MAC addresses — hyphen-separated
# ---------------------------------------------------------------------------


def test_valid_hyphen_lowercase():
    """Characterization: hyphen-separated MAC with lowercase hex digits"""
    assert mac_address("01-23-45-67-ab-cd")


def test_valid_hyphen_uppercase():
    """Characterization: hyphen-separated MAC with uppercase hex digits"""
    assert mac_address("01-23-45-67-AB-CD")


def test_valid_hyphen_mixed_case():
    """Characterization: hyphen-separated MAC with mixed-case hex digits"""
    assert mac_address("01-23-45-67-ab-CD")


def test_valid_hyphen_all_zeros():
    """Characterization: all-zero hyphen-separated MAC is structurally valid"""
    assert mac_address("00-00-00-00-00-00")


def test_valid_hyphen_all_fs_lowercase():
    """Characterization: broadcast hyphen-separated MAC ff-ff-ff-ff-ff-ff"""
    assert mac_address("ff-ff-ff-ff-ff-ff")


def test_valid_hyphen_all_Fs_uppercase():
    """Characterization: broadcast hyphen-separated MAC FF-FF-FF-FF-FF-FF"""
    assert mac_address("FF-FF-FF-FF-FF-FF")


def test_valid_hyphen_docstring_example():
    """Docstring: mac_address"""
    assert mac_address("01-23-45-67-ab-CD")


# ---------------------------------------------------------------------------
# Invalid: wrong number of octets
# ---------------------------------------------------------------------------


def test_invalid_five_octets_colon():
    """Docstring: mac_address"""
    assert not mac_address("00:00:00:00:00")


def test_invalid_four_octets_colon():
    """Characterization: too few octets"""
    assert not mac_address("00:00:00:00")


def test_invalid_seven_octets_colon():
    """Characterization: too many octets"""
    assert not mac_address("00:00:00:00:00:00:00")


def test_invalid_five_octets_hyphen():
    """Characterization: five hyphen-separated octets are invalid"""
    assert not mac_address("00-00-00-00-00")


def test_invalid_seven_octets_hyphen():
    """Characterization: seven hyphen-separated octets are invalid"""
    assert not mac_address("00-00-00-00-00-00-00")


# ---------------------------------------------------------------------------
# Invalid: wrong octet length
# ---------------------------------------------------------------------------


def test_invalid_single_digit_octet_colon():
    """Characterization: octets must be exactly 2 hex digits"""
    assert not mac_address("1:23:45:67:89:ab")


def test_invalid_three_digit_octet_colon():
    """Characterization: octets with 3 digits are invalid"""
    assert not mac_address("123:23:45:67:89:00")


def test_invalid_single_digit_octet_hyphen():
    """Characterization: single-digit octets with hyphens are invalid"""
    assert not mac_address("1-23-45-67-89-ab")


def test_invalid_three_digit_octet_hyphen():
    """Characterization: three-digit octets with hyphens are invalid"""
    assert not mac_address("123-23-45-67-89-00")


# ---------------------------------------------------------------------------
# Invalid: non-hex characters
# ---------------------------------------------------------------------------


def test_invalid_non_hex_letter_g():
    """Characterization: 'g' is not a hex digit"""
    assert not mac_address("01:23:45:67:89:gh")


def test_invalid_non_hex_letter_z():
    """Characterization: 'z' is not a hex digit"""
    assert not mac_address("01:23:45:67:89:zz")


def test_invalid_non_hex_colon_mixed():
    """Characterization: mixed colon/non-hex characters"""
    assert not mac_address("01:23-45:67-89:gh")


# ---------------------------------------------------------------------------
# Invalid: mixed separators
# ---------------------------------------------------------------------------


def test_invalid_mixed_colon_and_hyphen():
    """Characterization: mixing ':' and '-' separators is invalid"""
    assert not mac_address("01:23-45:67-89:00")


def test_invalid_mixed_hyphen_then_colon():
    """Characterization: any mix of ':' and '-' is rejected"""
    assert not mac_address("00-00:00-00:00-00")


def test_invalid_mixed_separators_one_switch():
    """Characterization: a single separator switch makes the MAC invalid"""
    assert not mac_address("01:23:45:67:89-cd")


# ---------------------------------------------------------------------------
# Invalid: trailing/leading/internal separator
# ---------------------------------------------------------------------------


def test_invalid_trailing_separator_colon():
    """Characterization: trailing separator produces invalid MAC"""
    assert not mac_address("01:23:45:67:89:")


def test_invalid_leading_separator_colon():
    """Characterization: leading separator produces invalid MAC"""
    assert not mac_address(":01:23:45:67:89")


def test_invalid_trailing_separator_hyphen():
    """Characterization: trailing hyphen produces invalid MAC"""
    assert not mac_address("01-23-45-67-89-")


def test_invalid_leading_separator_hyphen():
    """Characterization: leading hyphen produces invalid MAC"""
    assert not mac_address("-01-23-45-67-89")


# ---------------------------------------------------------------------------
# Invalid: wrong separators altogether
# ---------------------------------------------------------------------------


def test_invalid_dot_separator():
    """Characterization: dot '.' is not a valid MAC separator"""
    assert not mac_address("01.23.45.67.89.ab")


def test_invalid_space_separator():
    """Characterization: space is not a valid MAC separator"""
    assert not mac_address("01 23 45 67 89 ab")


def test_invalid_no_separator():
    """Characterization: 12-digit string without separators is invalid"""
    assert not mac_address("0123456789ab")


# ---------------------------------------------------------------------------
# Invalid: empty / whitespace input
# ---------------------------------------------------------------------------


def test_invalid_empty_string():
    """Characterization: empty string is not a valid MAC address"""
    assert not mac_address("")


def test_invalid_whitespace_only():
    """Characterization: whitespace-only string is not a valid MAC address"""
    assert not mac_address("   ")


def test_invalid_newline_in_value():
    """Characterization: newline inside value is not a valid MAC address"""
    assert not mac_address("01:23:45:67:89:\n")


# ---------------------------------------------------------------------------
# Invalid: extra content
# ---------------------------------------------------------------------------


def test_invalid_extra_leading_chars():
    """Characterization: extra characters before the MAC pattern are invalid"""
    assert not mac_address("x01:23:45:67:89:ab")


def test_invalid_extra_trailing_chars():
    """Characterization: extra characters after the MAC pattern are invalid"""
    assert not mac_address("01:23:45:67:89:abx")


def test_invalid_surrounding_whitespace():
    """Characterization: surrounding whitespace is not stripped — invalid"""
    assert not mac_address(" 01:23:45:67:89:ab ")
