"""Spec-driven tests for MAC address notation and format rules.

Covers: six groups of two hex digits, hyphen separator, colon separator,
mixed-case digits, broadcast address, all-zeros address.

Source: wiki-MAC_address.pdf
"""

from validators import mac_address


# ---------------------------------------------------------------------------
# R1 + R3 — six groups, colon-separated
# ---------------------------------------------------------------------------

def test_colon_separated_lowercase():
    """Spec: wiki-MAC_address.pdf Notational conventions — R3

    Six groups of two hex digits separated by colons; lowercase letters.
    """
    assert mac_address("01:23:45:67:89:ab")


def test_colon_separated_uppercase():
    """Spec: wiki-MAC_address.pdf Notational conventions — R3

    Six groups of two hex digits separated by colons; uppercase letters.
    """
    assert mac_address("01:23:45:67:89:AB")


def test_colon_separated_mixed_case():
    """Spec: wiki-MAC_address.pdf Notational conventions — R3, R5

    Example from the spec: '01:23:45:67:89:AB' — mixed case is valid.
    """
    assert mac_address("01:23:45:67:ab:CD")


# ---------------------------------------------------------------------------
# R1 + R2 — six groups, hyphen-separated
# ---------------------------------------------------------------------------

def test_hyphen_separated_lowercase():
    """Spec: wiki-MAC_address.pdf Notational conventions — R2

    Six groups of two hex digits separated by hyphens; lowercase letters.
    """
    assert mac_address("01-23-45-67-89-ab")


def test_hyphen_separated_uppercase():
    """Spec: wiki-MAC_address.pdf Notational conventions — R2

    Six groups of two hex digits separated by hyphens; uppercase letters.
    The spec example is '01-23-45-67-89-AB'.
    """
    assert mac_address("01-23-45-67-89-AB")


def test_hyphen_separated_mixed_case():
    """Spec: wiki-MAC_address.pdf Notational conventions — R2, R5

    Mixed-case hex digits are valid in the hyphen notation.
    """
    assert mac_address("A1-2F-4E-68-ab-CD")


# ---------------------------------------------------------------------------
# R5 — case insensitivity
# ---------------------------------------------------------------------------

def test_all_uppercase_colon():
    """Spec: wiki-MAC_address.pdf Notational conventions — R5

    All-uppercase hex digits with colon separator.
    """
    assert mac_address("AA:BB:CC:DD:EE:FF")


def test_all_lowercase_colon():
    """Spec: wiki-MAC_address.pdf Notational conventions — R5

    All-lowercase hex digits with colon separator.
    """
    assert mac_address("aa:bb:cc:dd:ee:ff")


def test_all_uppercase_hyphen():
    """Spec: wiki-MAC_address.pdf Notational conventions — R5

    All-uppercase hex digits with hyphen separator.
    """
    assert mac_address("AA-BB-CC-DD-EE-FF")


def test_all_lowercase_hyphen():
    """Spec: wiki-MAC_address.pdf Notational conventions — R5

    All-lowercase hex digits with hyphen separator.
    """
    assert mac_address("aa-bb-cc-dd-ee-ff")


# ---------------------------------------------------------------------------
# R7 — broadcast address
# ---------------------------------------------------------------------------

def test_broadcast_address_colon():
    """Spec: wiki-MAC_address.pdf Unicast vs. multicast (I/G bit) — R7

    The broadcast address FF:FF:FF:FF:FF:FF is explicitly named in the spec
    and must be a valid MAC address.
    """
    assert mac_address("FF:FF:FF:FF:FF:FF")


def test_broadcast_address_hyphen():
    """Spec: wiki-MAC_address.pdf Unicast vs. multicast (I/G bit) — R7

    Broadcast address in hyphen notation.
    """
    assert mac_address("FF-FF-FF-FF-FF-FF")


def test_broadcast_address_lowercase_colon():
    """Spec: wiki-MAC_address.pdf Unicast vs. multicast (I/G bit) — R7, R5

    Broadcast address using lowercase hex digits.
    """
    assert mac_address("ff:ff:ff:ff:ff:ff")


# ---------------------------------------------------------------------------
# R17 — all-zeros address
# ---------------------------------------------------------------------------

def test_all_zeros_colon():
    """Spec: wiki-MAC_address.pdf Notational conventions — R17

    All-zeros address is structurally valid: no octet value is excluded.
    """
    assert mac_address("00:00:00:00:00:00")


def test_all_zeros_hyphen():
    """Spec: wiki-MAC_address.pdf Notational conventions — R17

    All-zeros address with hyphen separator is structurally valid.
    """
    assert mac_address("00-00-00-00-00-00")


# ---------------------------------------------------------------------------
# R9 — locally administered address (LAA)
# ---------------------------------------------------------------------------

def test_locally_administered_address_hyphen():
    """Spec: wiki-MAC_address.pdf Universal vs. local (U/L bit) — R9

    The spec example '06-00-00-00-00-00' is a locally administered address
    and must be accepted as a valid MAC address format.
    """
    assert mac_address("06-00-00-00-00-00")


def test_locally_administered_address_colon():
    """Spec: wiki-MAC_address.pdf Universal vs. local (U/L bit) — R9

    Locally administered address in colon notation.
    """
    assert mac_address("06:00:00:00:00:00")


# ---------------------------------------------------------------------------
# R8 — multicast address
# ---------------------------------------------------------------------------

def test_multicast_address_colon():
    """Spec: wiki-MAC_address.pdf Unicast vs. multicast (I/G bit) — R8

    A multicast address (LSB of first octet = 1) is a valid MAC address.
    Example: first octet 01 has LSB=1.
    """
    assert mac_address("01:00:5E:00:00:01")


def test_ipv6_multicast_mac_colon():
    """Spec: wiki-MAC_address.pdf Ranges of group and locally administered addresses — R8

    IPv6 multicast uses MAC addresses in the range 33-33-XX-XX-XX-XX.
    These are valid MAC addresses.
    """
    assert mac_address("33:33:00:00:00:01")
