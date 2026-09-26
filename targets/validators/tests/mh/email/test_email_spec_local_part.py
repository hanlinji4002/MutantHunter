"""Spec tests for email local-part rules.

Rules covered: R1, R2, R4, R5, R12, R14, R15, R16, R18, R19
Sources: RFC 5322 §3.2.3, §3.4.1 / RFC 5321 §4.5.3.1.1, §4.1.2, §2.4
"""

import validators


# ---------------------------------------------------------------------------
# R1 — exactly one @ sign
# ---------------------------------------------------------------------------

def test_no_at_sign_invalid():
    """Spec: RFC 5322 3.4.1 — R1

    addr-spec requires exactly one '@'. An address with no '@' is invalid.
    """
    assert not validators.email("userwithoutatsign.com")


def test_two_at_signs_invalid():
    """Spec: RFC 5322 3.4.1 — R1

    addr-spec requires exactly one '@'. Two '@' signs are invalid.
    """
    assert not validators.email("user@@example.com")


def test_single_at_sign_valid():
    """Spec: RFC 5322 3.4.1 — R1

    A properly formed addr-spec with exactly one '@' is valid.
    """
    assert validators.email("user@example.com")


# ---------------------------------------------------------------------------
# R2 — local-part max 64 octets
# ---------------------------------------------------------------------------

def test_local_part_exactly_64_chars_valid():
    """Spec: RFC 5321 4.5.3.1.1 — R2

    Local-part of exactly 64 characters (the maximum) MUST be accepted.
    """
    local = "a" * 64
    assert validators.email(f"{local}@example.com")


def test_local_part_65_chars_invalid():
    """Spec: RFC 5321 4.5.3.1.1 — R2

    Local-part exceeding 64 octets MUST be rejected.
    """
    local = "a" * 65
    assert not validators.email(f"{local}@example.com")


def test_local_part_1_char_valid():
    """Spec: RFC 5321 4.5.3.1.1 — R2

    A single-character local-part is within the 64-octet limit and is valid.
    """
    assert validators.email("a@example.com")


# ---------------------------------------------------------------------------
# R4 — dot-atom atext characters
# ---------------------------------------------------------------------------

def test_local_part_all_atext_valid():
    """Spec: RFC 5322 3.2.3 — R4

    All atext characters are valid in an unquoted local-part.
    atext = ALPHA / DIGIT / ! # $ % & ' * + - / = ? ^ _ ` { | } ~
    """
    assert validators.email("a1!#$%&'*+/=?^_`{|}~-z@example.com")


def test_local_part_digits_valid():
    """Spec: RFC 5322 3.2.3 — R4

    Digits are valid atext characters in the local-part.
    """
    assert validators.email("123@example.com")


def test_local_part_mixed_alpha_digit_valid():
    """Spec: RFC 5322 3.2.3 — R4

    Mixed alphanumeric local-parts are valid.
    """
    assert validators.email("user123@example.com")


def test_local_part_uppercase_valid():
    """Spec: RFC 5322 3.2.3 — R19

    Uppercase letters are valid atext characters (ALPHA includes A-Z).
    """
    assert validators.email("User@example.com")


# ---------------------------------------------------------------------------
# R5 — no leading, trailing, or consecutive dots
# ---------------------------------------------------------------------------

def test_local_part_dot_in_middle_valid():
    """Spec: RFC 5322 3.2.3 — R5

    Dots are allowed in the middle of the local-part (dot-atom form).
    """
    assert validators.email("first.last@example.com")


def test_local_part_leading_dot_invalid():
    """Spec: RFC 5322 3.2.3 — R5

    dot-atom-text requires 1*atext before any dot; a leading dot is invalid.
    """
    assert not validators.email(".user@example.com")


def test_local_part_trailing_dot_invalid():
    """Spec: RFC 5322 3.2.3 — R5

    dot-atom-text requires 1*atext after each dot; a trailing dot is invalid.
    """
    assert not validators.email("user.@example.com")


def test_local_part_consecutive_dots_invalid():
    """Spec: RFC 5322 3.2.3 — R5

    Two consecutive dots in the local-part are invalid in dot-atom form
    because each dot must be surrounded by 1*atext on both sides.
    """
    assert not validators.email("us..er@example.com")


# ---------------------------------------------------------------------------
# R14 / R18 — non-empty local-part and non-empty domain
# ---------------------------------------------------------------------------

def test_empty_local_part_invalid():
    """Spec: RFC 5322 3.4.1 — R14, R18

    An empty local-part (bare '@domain') is invalid.
    """
    assert not validators.email("@example.com")


def test_empty_string_invalid():
    """Spec: RFC 5322 3.4.1 — R14

    An empty string has no '@' and is invalid.
    """
    assert not validators.email("")


# ---------------------------------------------------------------------------
# R15 — specials not allowed outside quoted-string
# ---------------------------------------------------------------------------

def test_local_part_parenthesis_invalid():
    """Spec: RFC 5322 3.2.3 — R15

    '(' and ')' are 'specials', not 'atext', so they are invalid in an
    unquoted local-part.
    """
    assert not validators.email("us(er@example.com")


def test_local_part_angle_bracket_invalid():
    """Spec: RFC 5322 3.2.3 — R15

    '<' is a 'special', not 'atext', so it is invalid in an unquoted
    local-part.
    """
    assert not validators.email("us<er@example.com")


def test_local_part_comma_invalid():
    """Spec: RFC 5322 3.2.3 — R15

    ',' is a 'special', not 'atext', so it is invalid in an unquoted
    local-part.
    """
    assert not validators.email("us,er@example.com")


def test_local_part_colon_invalid():
    """Spec: RFC 5322 3.2.3 — R15

    ':' is a 'special', not 'atext', so it is invalid in an unquoted
    local-part.
    """
    assert not validators.email("us:er@example.com")


# ---------------------------------------------------------------------------
# R16 — no whitespace in unquoted local-part
# ---------------------------------------------------------------------------

def test_local_part_space_invalid():
    """Spec: RFC 5322 3.2.3 — R16

    Space (SP) is not an atext character and must not appear in an unquoted
    local-part.
    """
    assert not validators.email("us er@example.com")
