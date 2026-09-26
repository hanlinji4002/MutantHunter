"""Spec-driven tests for hostname label character rules.

Sources: RFC 952 §ASSUMPTIONS and RFC 1123 §2.1
"""

from validators import hostname


def test_label_lowercase_letters_valid():
    """Spec: rfc952.pdf ASSUMPTIONS — R1

    A name is drawn from the alphabet (A-Z), digits (0-9), minus sign and period.
    Lowercase letters are valid (case-insensitive per R4).
    """
    assert hostname("abcdef")


def test_label_uppercase_letters_valid():
    """Spec: rfc952.pdf ASSUMPTIONS — R4

    No distinction is made between upper and lower case.
    """
    assert hostname("ABCDEF")


def test_label_mixed_case_valid():
    """Spec: rfc952.pdf ASSUMPTIONS — R4

    No distinction is made between upper and lower case.
    """
    assert hostname("AbCdEf")


def test_label_digits_only_valid():
    """Spec: rfc1123.pdf Section 2.1 — R19

    Under RFC 1123 §2.1, a label beginning with a digit is allowed. A label
    consisting solely of digits is syntactically valid as a simple hostname.
    """
    assert hostname("123456")


def test_label_alphanumeric_valid():
    """Spec: rfc952.pdf ASSUMPTIONS — R1

    A name is drawn from the alphabet (A-Z) and digits (0-9).
    Mixed alphanumeric labels are valid.
    """
    assert hostname("host01")


def test_label_with_interior_hyphen_valid():
    """Spec: rfc952.pdf ASSUMPTIONS — R1

    A name may contain a minus sign (-). Interior hyphens are valid.
    """
    assert hostname("my-host")


def test_label_underscore_invalid():
    """Spec: rfc952.pdf ASSUMPTIONS — R12

    Names are drawn only from alphabet, digits, minus sign, and period.
    Underscore is not in the allowed character set and must be rejected.
    """
    assert not hostname("my_host")


def test_label_space_invalid():
    """Spec: rfc952.pdf ASSUMPTIONS — R3

    No blank or space characters are permitted as part of a name.
    """
    assert not hostname("my host")


def test_label_asterisk_invalid():
    """Spec: rfc952.pdf ASSUMPTIONS — R18

    Labels may not contain characters outside [A-Za-z0-9-]. An asterisk is invalid.
    """
    assert not hostname("my*host")


def test_label_at_sign_invalid():
    """Spec: rfc952.pdf ASSUMPTIONS — R18

    Labels may not contain characters outside [A-Za-z0-9-]. The '@' character is invalid.
    """
    assert not hostname("my@host")


def test_label_exclamation_invalid():
    """Spec: rfc952.pdf ASSUMPTIONS — R18

    Labels may not contain characters outside [A-Za-z0-9-]. '!' is invalid.
    """
    assert not hostname("host!")


def test_label_hash_invalid():
    """Spec: rfc952.pdf ASSUMPTIONS — R18

    Labels may not contain characters outside [A-Za-z0-9-]. '#' is invalid.
    """
    assert not hostname("host#1")


def test_label_dollar_invalid():
    """Spec: rfc952.pdf ASSUMPTIONS — R18

    Labels may not contain characters outside [A-Za-z0-9-]. '$' is invalid.
    """
    assert not hostname("host$")


def test_label_slash_invalid():
    """Spec: rfc952.pdf ASSUMPTIONS — R18

    Labels may not contain characters outside [A-Za-z0-9-]. '/' is invalid.
    """
    assert not hostname("host/name")


def test_label_case_insensitive_with_hyphen():
    """Spec: rfc952.pdf ASSUMPTIONS — R4

    No distinction is made between upper and lower case. Mixed-case with
    interior hyphen is valid.
    """
    assert hostname("My-Host")
