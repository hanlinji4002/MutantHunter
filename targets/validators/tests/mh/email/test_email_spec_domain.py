"""Spec tests for email domain part rules.

Rules covered: R3, R7, R8, R9, R13, R17
Sources: RFC 5321 §4.1.2, §4.5.3.1.2, §2.3.5 / RFC 5322 §3.4.1
"""

import validators


# ---------------------------------------------------------------------------
# R3 — domain max 253/255 octets
# ---------------------------------------------------------------------------

def test_domain_253_chars_valid():
    """Spec: RFC 5321 4.5.3.1.2 — R3

    The maximum domain length is 255 octets per RFC 5321. The implementation
    checks <= 253 (consistent with DNS name constraints). A 253-character
    domain is valid.
    """
    # 63-char label + dot + 63-char label + dot + 63-char label + dot + 63-char TLD
    # = 63+1+63+1+63+1+61 = 253 chars total
    label_a = "a" * 63
    label_b = "b" * 63
    label_c = "c" * 63
    label_d = "d" * 61
    domain = f"{label_a}.{label_b}.{label_c}.{label_d}"
    assert len(domain) == 253
    assert validators.email(f"user@{domain}")


def test_domain_exceeds_253_chars_invalid():
    """Spec: RFC 5321 4.5.3.1.2 — R3

    A domain exceeding 253 characters is invalid.
    """
    # 254-character domain
    label = "a" * 63
    domain = f"{label}.{label}.{label}." + "b" * 62
    assert len(domain) == 254
    assert not validators.email(f"user@{domain}")


# ---------------------------------------------------------------------------
# R7 — sub-domain labels: letters, digits, hyphens only
# ---------------------------------------------------------------------------

def test_domain_letters_only_valid():
    """Spec: RFC 5321 4.1.2 — R7

    Domain labels composed solely of letters are valid.
    """
    assert validators.email("user@example.com")


def test_domain_letters_and_digits_valid():
    """Spec: RFC 5321 4.1.2 — R7

    Domain labels with letters and digits are valid.
    """
    assert validators.email("user@example2.com")


def test_domain_with_hyphen_valid():
    """Spec: RFC 5321 4.1.2 — R7

    Hyphens are allowed within domain labels (not at start/end).
    """
    assert validators.email("user@my-host.example.com")


def test_domain_label_underscore_invalid():
    """Spec: RFC 5321 4.1.2 — R7

    RFC 5321 §4.1.2 explicitly states that underscores MUST NOT appear in
    domain name labels for SMTP.
    """
    assert not validators.email("user@my_host.example.com")


# ---------------------------------------------------------------------------
# R8 — no leading or trailing hyphen in domain label
# ---------------------------------------------------------------------------

def test_domain_label_leading_hyphen_invalid():
    """Spec: RFC 5321 4.1.2 — R8

    sub-domain = Let-dig [Ldh-str] requires the first character to be a
    letter or digit; a leading hyphen is not allowed.
    """
    assert not validators.email("user@-example.com")


def test_domain_label_trailing_hyphen_invalid():
    """Spec: RFC 5321 4.1.2 — R8

    Ldh-str ends with Let-dig, so a trailing hyphen is not allowed in a
    domain label.
    """
    assert not validators.email("user@example-.com")


# ---------------------------------------------------------------------------
# R13 — domain case insensitivity
# ---------------------------------------------------------------------------

def test_domain_uppercase_valid():
    """Spec: RFC 5321 2.4 — R13

    Domain names are case-insensitive per DNS rules; uppercase is valid.
    """
    assert validators.email("user@EXAMPLE.COM")


def test_domain_mixed_case_valid():
    """Spec: RFC 5321 2.4 — R13

    Mixed-case domain names are valid.
    """
    assert validators.email("user@Example.Com")


# ---------------------------------------------------------------------------
# R17 — domain must not be empty
# ---------------------------------------------------------------------------

def test_empty_domain_invalid():
    """Spec: RFC 5322 3.4.1 — R17

    addr-spec = local-part "@" domain requires a non-empty domain.
    An address with a trailing '@' is invalid.
    """
    assert not validators.email("user@")


# ---------------------------------------------------------------------------
# R9 — FQDN requirement / simple_host option
# ---------------------------------------------------------------------------

def test_domain_without_dot_rejected_by_default():
    """Spec: RFC 5321 2.3.5 — R9

    On the public Internet only FQDNs (containing at least one dot) are
    valid. By default the validator should reject a single-label domain.
    """
    assert not validators.email("user@localhost")


def test_domain_without_dot_allowed_with_simple_host():
    """Spec: RFC 5321 2.3.5 — R9

    The simple_host option explicitly allows single-label domains for
    local/intranet use cases (validator docstring).
    """
    assert validators.email("user@localhost", simple_host=True)


def test_domain_two_labels_valid():
    """Spec: RFC 5321 2.3.5 — R9

    A domain with at least two labels separated by a dot is a valid FQDN.
    """
    assert validators.email("user@example.com")


def test_domain_multiple_labels_valid():
    """Spec: RFC 5321 2.3.5 — R9

    A domain with multiple dot-separated labels is valid.
    """
    assert validators.email("user@mail.example.co.uk")
