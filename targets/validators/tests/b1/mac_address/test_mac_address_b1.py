"""Additional pytest tests for validators.mac_address."""

import validators


# ---------------------------------------------------------------------------
# Valid MAC addresses
# ---------------------------------------------------------------------------

def test_valid_colon_lowercase():
    """Docstring: mac_address"""
    assert validators.mac_address("01:23:45:67:ab:cd")


def test_valid_colon_uppercase():
    """Docstring: mac_address"""
    assert validators.mac_address("01:23:45:67:AB:CD")


def test_valid_colon_mixed_case():
    """Docstring: mac_address"""
    # From the docstring example
    assert validators.mac_address("01:23:45:67:ab:CD")


def test_valid_hyphen_lowercase():
    """Docstring: mac_address"""
    assert validators.mac_address("01-23-45-67-ab-cd")


def test_valid_hyphen_uppercase():
    """Docstring: mac_address"""
    assert validators.mac_address("01-23-45-67-AB-CD")


def test_valid_all_zeros_colon():
    """Docstring: mac_address"""
    assert validators.mac_address("00:00:00:00:00:00")


def test_valid_all_zeros_hyphen():
    """Docstring: mac_address"""
    assert validators.mac_address("00-00-00-00-00-00")


def test_valid_all_fs_colon():
    """Docstring: mac_address"""
    assert validators.mac_address("ff:ff:ff:ff:ff:ff")


def test_valid_all_fs_hyphen():
    """Docstring: mac_address"""
    assert validators.mac_address("FF-FF-FF-FF-FF-FF")


def test_valid_broadcast():
    """Docstring: mac_address"""
    assert validators.mac_address("FF:FF:FF:FF:FF:FF")


def test_valid_hex_digits_colon():
    """Docstring: mac_address"""
    assert validators.mac_address("0A:1B:2C:3D:4E:5F")


def test_valid_hex_digits_hyphen():
    """Docstring: mac_address"""
    assert validators.mac_address("0A-1B-2C-3D-4E-5F")


# ---------------------------------------------------------------------------
# Invalid MAC addresses
# ---------------------------------------------------------------------------

def test_invalid_five_groups_colon():
    """Docstring: mac_address"""
    # Docstring example: too few groups
    assert not validators.mac_address("00:00:00:00:00")


def test_invalid_five_groups_hyphen():
    """Docstring: mac_address"""
    assert not validators.mac_address("00-00-00-00-00")


def test_invalid_seven_groups():
    """Docstring: mac_address"""
    assert not validators.mac_address("00:00:00:00:00:00:00")


def test_invalid_mixed_separators():
    """Docstring: mac_address"""
    # Cannot mix ':' and '-'
    assert not validators.mac_address("01:23:45:67-ab:cd")


def test_invalid_empty_string():
    """Docstring: mac_address"""
    assert not validators.mac_address("")


def test_invalid_no_separator():
    """Docstring: mac_address"""
    assert not validators.mac_address("0123456789ab")


def test_invalid_dot_separator():
    """Docstring: mac_address"""
    # Dots are not a valid separator
    assert not validators.mac_address("01.23.45.67.ab.cd")


def test_invalid_short_group():
    """Docstring: mac_address"""
    # One octet has only one hex digit
    assert not validators.mac_address("1:23:45:67:ab:cd")


def test_invalid_long_group():
    """Docstring: mac_address"""
    # One octet has three hex digits
    assert not validators.mac_address("001:23:45:67:ab:cd")


def test_invalid_non_hex_char():
    """Docstring: mac_address"""
    assert not validators.mac_address("GG:23:45:67:ab:cd")


def test_invalid_spaces():
    """Docstring: mac_address"""
    assert not validators.mac_address("01 23 45 67 ab cd")


def test_invalid_trailing_separator():
    """Docstring: mac_address"""
    assert not validators.mac_address("01:23:45:67:ab:cd:")


def test_invalid_leading_separator():
    """Docstring: mac_address"""
    assert not validators.mac_address(":01:23:45:67:ab:cd")


def test_invalid_plain_text():
    """Docstring: mac_address"""
    assert not validators.mac_address("not-a-mac-address")


def test_invalid_whitespace_around():
    """Docstring: mac_address"""
    assert not validators.mac_address(" 01:23:45:67:ab:cd")
