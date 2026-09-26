"""Spec-driven tests for URI host sub-component (RFC 3986 §3.2.2).

Rules covered: R9, R10, R11, R12, R13, R29
"""
import pytest
from validators import url


# ---------------------------------------------------------------------------
# reg-name (registered / domain name) hosts
# ---------------------------------------------------------------------------

def test_host_reg_name_simple():
    """Spec: rfc3986 §3.2.2 — R9/R13: reg-name with basic domain label is valid."""
    assert url("http://example.com")


def test_host_reg_name_subdomain():
    """Spec: rfc3986 §3.2.2 — R13: multi-label reg-name (subdomain) is valid."""
    assert url("http://www.example.com")


def test_host_reg_name_numeric_label():
    """Spec: rfc3986 §3.2.2 — R13: reg-name may start with digits."""
    assert url("http://1337.net")


def test_host_reg_name_hyphen_in_label():
    """Spec: rfc3986 §3.2.2 — R13: hyphen (unreserved) is allowed inside a label."""
    assert url("http://a.b-c.de")


# ---------------------------------------------------------------------------
# IPv4 address hosts
# ---------------------------------------------------------------------------

def test_host_ipv4_valid_all_zeros():
    """Spec: rfc3986 §3.2.2 — R11/R12: '0.0.0.0' is a valid IPv4 address."""
    assert url("http://0.0.0.0")


def test_host_ipv4_valid_broadcast():
    """Spec: rfc3986 §3.2.2 — R11: each octet 0–255; 223.255.255.254 is valid."""
    assert url("http://223.255.255.254")


def test_host_ipv4_valid_loopback_with_port():
    """Spec: rfc3986 §3.2.2 / §3.2.3 — R11: 127.0.0.1 with port is valid."""
    assert url("http://127.0.0.1:8080")


def test_host_ipv4_octet_256_invalid():
    """Spec: rfc3986 §3.2.2 — R11: octet value 256 exceeds 0–255 range; invalid."""
    assert not url("http://127.12.0.260")


def test_host_ipv4_three_octets_invalid():
    """Spec: rfc3986 §3.2.2 — R12: IPv4 requires exactly four octets; three is invalid."""
    assert not url("http://123.123.123")


def test_host_ipv4_five_octets_invalid():
    """Spec: rfc3986 §3.2.2 — R12: IPv4 requires exactly four octets; five is invalid."""
    assert not url("http://1.1.1.1.1")


def test_host_ipv4_missing_octet_invalid():
    """Spec: rfc3986 §3.2.2 — R12: dotted-decimal with only two octets is invalid."""
    assert not url("http://127.0.0/asdf")


# ---------------------------------------------------------------------------
# IPv6 literal hosts (IP-literal in brackets)
# ---------------------------------------------------------------------------

def test_host_ipv6_full_address_valid():
    """Spec: rfc3986 §3.2.2 — R10: full IPv6 address in brackets is valid."""
    assert url("http://[FEDC:BA98:7654:3210:FEDC:BA98:7654:3210]:80/index.html")


def test_host_ipv6_compressed_valid():
    """Spec: rfc3986 §3.2.2 — R10: compressed IPv6 '::' notation in brackets is valid."""
    assert url("http://[3ffe:2a00:100:7031::1]")


def test_host_ipv6_with_ipv4_suffix_valid():
    """Spec: rfc3986 §3.2.2 — R10: IPv6 with embedded IPv4 suffix in brackets is valid."""
    assert url("http://[::192.9.5.5]/ipng")


def test_host_ipv6_without_brackets_invalid():
    """Spec: rfc3986 §3.2.2 — R29: bare IPv6 address (no brackets) is not valid as host."""
    assert not url("http://2010:836B:4179::836B:4179")


def test_host_ipv6_unclosed_bracket_invalid():
    """Spec: rfc3986 §3.2.2 — R10: IP-literal bracket must be closed; unclosed is invalid."""
    assert not url("http://[2010:836B:4179::836B:4179")


def test_host_ipv6_bare_not_authority_invalid():
    """Spec: rfc3986 §3.2.2 — R29: IPv6 without [] used as host with port is invalid."""
    assert not url("http://2010:836B:4179::836B:4179:80/index.html")
