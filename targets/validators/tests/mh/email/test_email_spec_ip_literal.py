"""Spec tests for email IP-literal domain rules.

Rules covered: R10, R11
Sources: RFC 5321 §4.1.3 / RFC 5322 §3.4.1
"""

import validators


# ---------------------------------------------------------------------------
# R10 — IPv4 address literal in brackets
# ---------------------------------------------------------------------------

def test_ipv4_literal_valid():
    """Spec: RFC 5321 4.1.3 — R10

    An IPv4 address literal enclosed in brackets is a valid domain for
    an email address when ipv4_address=True is passed.
    """
    assert validators.email("user@[192.168.1.1]", ipv4_address=True)


def test_ipv4_literal_loopback_valid():
    """Spec: RFC 5321 4.1.3 — R10

    The loopback address [127.0.0.1] is a valid IPv4 address literal.
    """
    assert validators.email("user@[127.0.0.1]", ipv4_address=True)


def test_ipv4_literal_without_brackets_invalid():
    """Spec: RFC 5321 4.1.3 — R10

    An IPv4 address used as a domain WITHOUT the enclosing brackets is
    invalid; the brackets are mandatory per the spec.
    """
    assert not validators.email("user@192.168.1.1", ipv4_address=True)


def test_ipv4_literal_not_accepted_without_flag():
    """Spec: RFC 5321 4.1.3 — R10

    Without ipv4_address=True the validator treats [d.d.d.d] as a domain
    literal and rejects it (default mode requires a hostname domain).
    """
    assert not validators.email("user@[192.168.1.1]")


def test_ipv4_literal_all_zeros_valid():
    """Spec: RFC 5321 4.1.3 — R10

    [0.0.0.0] is a syntactically valid IPv4 address literal.
    """
    assert validators.email("user@[0.0.0.0]", ipv4_address=True)


def test_ipv4_literal_max_octets_valid():
    """Spec: RFC 5321 4.1.3 — R10

    [255.255.255.255] is a syntactically valid IPv4 address literal.
    """
    assert validators.email("user@[255.255.255.255]", ipv4_address=True)


# ---------------------------------------------------------------------------
# R11 — IPv6 address literal in brackets with IPv6: tag
# ---------------------------------------------------------------------------

def test_ipv6_literal_without_brackets_invalid():
    """Spec: RFC 5321 4.1.3 — R11

    An IPv6 literal without the enclosing brackets is invalid.
    """
    assert not validators.email("user@IPv6:::1", ipv6_address=True)


def test_ipv6_literal_not_accepted_without_flag():
    """Spec: RFC 5321 4.1.3 — R11

    Without ipv6_address=True the validator should not accept an IPv6
    literal domain.
    """
    assert not validators.email("user@[IPv6:::1]")
