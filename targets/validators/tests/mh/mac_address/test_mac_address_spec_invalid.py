"""Spec-driven tests for invalid MAC address inputs.

Covers: wrong group count, wrong digit count per group, non-hex characters,
mixed separators, empty string.

Source: wiki-MAC_address.pdf
"""

from validators import mac_address


# ---------------------------------------------------------------------------
# R10 — fewer than six groups
# ---------------------------------------------------------------------------

def test_five_groups_colon():
    """Spec: wiki-MAC_address.pdf Notational conventions — R10

    Five colon-separated groups is not a valid MAC-48 address (must be six).
    """
    assert not mac_address("00:00:00:00:00")


def test_four_groups_colon():
    """Spec: wiki-MAC_address.pdf Notational conventions — R10

    Four groups is not a valid MAC-48 address.
    """
    assert not mac_address("01:23:45:67")


def test_one_group():
    """Spec: wiki-MAC_address.pdf Notational conventions — R10

    A single octet is not a valid MAC address.
    """
    assert not mac_address("AB")


# ---------------------------------------------------------------------------
# R11 — more than six groups
# ---------------------------------------------------------------------------

def test_seven_groups_colon():
    """Spec: wiki-MAC_address.pdf Address details — R11

    Seven colon-separated groups exceed the 48-bit (6 octet) maximum.
    """
    assert not mac_address("01:23:45:67:89:AB:CD")


def test_seven_groups_hyphen():
    """Spec: wiki-MAC_address.pdf Address details — R11

    Seven hyphen-separated groups exceed the 48-bit maximum.
    """
    assert not mac_address("01-23-45-67-89-AB-CD")


# ---------------------------------------------------------------------------
# R12 — each group must have exactly two hex digits
# ---------------------------------------------------------------------------

def test_single_digit_group_colon():
    """Spec: wiki-MAC_address.pdf Notational conventions — R12

    A group with only one hex digit is invalid (spec requires two).
    """
    assert not mac_address("1:23:45:67:89:AB")


def test_three_digit_group_colon():
    """Spec: wiki-MAC_address.pdf Notational conventions — R12

    A group with three hex digits is invalid.
    """
    assert not mac_address("123:23:45:67:89:00")


def test_trailing_separator_colon():
    """Spec: wiki-MAC_address.pdf Notational conventions — R12

    A trailing colon produces an empty last group, which is invalid.
    """
    assert not mac_address("01:23:45:67:89:")


def test_leading_separator_colon():
    """Spec: wiki-MAC_address.pdf Notational conventions — R12

    A leading colon produces an empty first group, which is invalid.
    """
    assert not mac_address(":01:23:45:67:89")


# ---------------------------------------------------------------------------
# R13 — non-hexadecimal characters
# ---------------------------------------------------------------------------

def test_non_hex_letter_g():
    """Spec: wiki-MAC_address.pdf Notational conventions — R13

    'G' is not a hexadecimal digit; the address is invalid.
    """
    assert not mac_address("GG:23:45:67:89:AB")


def test_non_hex_letter_z():
    """Spec: wiki-MAC_address.pdf Notational conventions — R13

    'Z' is not a hexadecimal digit; the address is invalid.
    """
    assert not mac_address("ZZ:23:45:67:89:AB")


def test_non_hex_special_char():
    """Spec: wiki-MAC_address.pdf Notational conventions — R13

    Special character '*' is not valid in a MAC address.
    """
    assert not mac_address("**:23:45:67:89:AB")


def test_non_hex_space():
    """Spec: wiki-MAC_address.pdf Notational conventions — R13

    Spaces are not hexadecimal digits; the address is invalid.
    """
    assert not mac_address("01 23 45 67 89 AB")


# ---------------------------------------------------------------------------
# R14 — empty string
# ---------------------------------------------------------------------------

def test_empty_string():
    """Spec: wiki-MAC_address.pdf Notational conventions — R14

    An empty string has no groups at all and is not a valid MAC address.
    """
    assert not mac_address("")


# ---------------------------------------------------------------------------
# R16 — mixed separators
# ---------------------------------------------------------------------------

def test_mixed_colon_and_hyphen():
    """Spec: wiki-MAC_address.pdf Notational conventions — R16

    Mixing colons and hyphens within a single address is not a valid notation.
    """
    assert not mac_address("01:23-45:67-89:AB")


def test_mixed_hyphen_and_colon_variant():
    """Spec: wiki-MAC_address.pdf Notational conventions — R16

    Another mixed-separator combination; each valid notation uses one
    separator type exclusively.
    """
    assert not mac_address("00-00:-00-00-00")
