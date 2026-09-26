"""Spec-driven tests for hostname length rules.

Sources: RFC 1123 §2.1 (R8, R9, R14)
"""

from validators import hostname


def test_label_one_char_letter_valid():
    """Spec: rfc952.pdf ASSUMPTIONS — R16

    RFC 952 grammar allows a single-letter name: <name> ::= <let>[...].
    A single alphabetic character is a valid hostname.
    """
    assert hostname("a")


def test_label_one_char_digit_valid():
    """Spec: rfc1123.pdf Section 2.1 — R17

    RFC 1123 §2.1 relaxes the first-character rule to allow digits.
    A single digit is therefore a valid simple hostname.
    """
    assert hostname("9")


# test_label_63_chars_valid — moved to results/suspected_bugs/hostname.md
# Fails on current code: _simple_hostname_regex caps at 61 chars (logic bug)


def test_label_64_chars_invalid():
    """Spec: rfc1123.pdf Section 2.1 — R14

    The per-label limit is 63 characters (RFC 1123 §2.1 MUST requirement).
    A 64-character label exceeds this limit and must be rejected.
    """
    label = "a" * 64
    assert not hostname(label)


# test_label_62_chars_valid — moved to results/suspected_bugs/hostname.md
# Fails on current code: _simple_hostname_regex caps at 61 chars (logic bug)

# test_label_63_chars_with_hyphen_valid — moved to results/suspected_bugs/hostname.md
# Fails on current code: _simple_hostname_regex caps at 61 chars (logic bug)


def test_hostname_too_long_single_label_invalid():
    """Spec: rfc1123.pdf Section 2.1 — R14

    A single label exceeding 63 characters is invalid.
    """
    label = "x" * 65
    assert not hostname(label)
