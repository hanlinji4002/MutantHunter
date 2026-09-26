"""Spec-driven tests for hostname first and last character rules.

Sources: RFC 952 §ASSUMPTIONS and RFC 1123 §2.1
"""

from validators import hostname


def test_label_starting_with_letter_valid():
    """Spec: rfc952.pdf ASSUMPTIONS — R5

    The first character must be an alphabetic character (original RFC 952 rule,
    which remains valid under RFC 1123's relaxed rule).
    """
    assert hostname("abc")


def test_label_starting_with_digit_valid():
    """Spec: rfc1123.pdf Section 2.1 — R7

    RFC 1123 §2.1 relaxes the first-character restriction: a label may begin
    with either a letter or a digit.
    """
    assert hostname("1abc")


def test_label_starting_with_hyphen_invalid():
    """Spec: rfc1123.pdf Section 2.1 — R10

    A hostname label MUST NOT begin with a hyphen.
    """
    assert not hostname("-hostname")


def test_label_ending_with_letter_valid():
    """Spec: rfc952.pdf ASSUMPTIONS — R6

    The last character must not be a minus sign or period; a trailing letter is valid.
    """
    assert hostname("hostname")


def test_label_ending_with_digit_valid():
    """Spec: rfc952.pdf ASSUMPTIONS — R6

    The last character must not be a minus sign or period; a trailing digit is valid.
    """
    assert hostname("host1")


def test_label_ending_with_hyphen_invalid():
    """Spec: rfc952.pdf ASSUMPTIONS — R6

    The last character must not be a minus sign.
    """
    assert not hostname("hostname-")


def test_label_starting_and_ending_with_hyphen_invalid():
    """Spec: rfc952.pdf ASSUMPTIONS — R6, rfc1123.pdf Section 2.1 — R10

    A label must not start with a hyphen (R10) and must not end with a
    minus sign (R6).
    """
    assert not hostname("-hostname-")


def test_label_all_hyphens_invalid():
    """Spec: rfc952.pdf ASSUMPTIONS — R15

    A label consisting solely of hyphens is invalid because both the first
    and last characters are hyphens, violating R10 and R6/R11.
    """
    assert not hostname("---")


def test_single_hyphen_invalid():
    """Spec: rfc952.pdf ASSUMPTIONS — R6, rfc1123.pdf Section 2.1 — R10

    A single hyphen starts and ends with a hyphen, which is invalid.
    """
    assert not hostname("-")


def test_label_hyphen_between_alphanums_valid():
    """Spec: rfc952.pdf ASSUMPTIONS — R6a

    Interior hyphens are valid: label starts and ends with alphanum.
    """
    assert hostname("a-b")


def test_label_leading_digit_ending_letter_valid():
    """Spec: rfc1123.pdf Section 2.1 — R7

    RFC 1123 allows first character to be a digit.
    Combined with a trailing letter this is valid.
    """
    assert hostname("4ever")


def test_label_leading_digit_ending_digit_valid():
    """Spec: rfc1123.pdf Section 2.1 — R7

    RFC 1123 allows first character to be a digit; the label may also end
    with a digit as long as it does not end with a hyphen.
    """
    assert hostname("404")
