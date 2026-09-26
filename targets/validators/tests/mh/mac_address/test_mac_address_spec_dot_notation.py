"""Spec-driven tests for the dot-grouped (Cisco) MAC address notation.

The Wikipedia spec (Notational conventions) lists three groups of four hex
digits separated by dots as a valid human-friendly notation.
The current validator implementation does NOT support dot notation; those
tests are recorded in results/suspected_bugs/mac_address.md and are not
included here pending a fix upstream.

Source: wiki-MAC_address.pdf
"""

from validators import mac_address


def test_dot_notation_wrong_group_count():
    """Spec: wiki-MAC_address.pdf Notational conventions — R4, R6

    Six groups of two digits separated by dots is NOT the dot notation
    described in the spec (which requires three groups of four digits).
    """
    assert not mac_address("01.23.45.67.89.AB")


def test_dot_notation_two_groups_invalid():
    """Spec: wiki-MAC_address.pdf Notational conventions — R4, R6

    Two dot-separated groups of six hex digits is not a valid MAC notation.
    """
    assert not mac_address("012345.6789AB")
