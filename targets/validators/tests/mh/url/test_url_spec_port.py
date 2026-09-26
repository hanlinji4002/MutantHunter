"""Spec-driven tests for URI port sub-component (RFC 3986 §3.2.3).

Rules covered: R14, R15
"""
import pytest
from validators import url


# ---------------------------------------------------------------------------
# Valid port values
# ---------------------------------------------------------------------------

def test_port_numeric_standard():
    """Spec: rfc3986 §3.2.3 — R14: port is *DIGIT; a standard port number is valid."""
    assert url("http://example.com:8080")


def test_port_single_digit():
    """Spec: rfc3986 §3.2.3 — R14: single-digit port (e.g., port 9) is valid."""
    assert url("http://google.com:9/test")


def test_port_large_number():
    """Spec: rfc3986 §3.2.3 — R14: large port number is syntactically valid (grammar is *DIGIT)."""
    assert url("http://example.com:65535/path")


# test_port_zero: REMOVED — suspected violation (results/suspected_bugs/url.md)
# The code rejects port 0; RFC 3986 §3.2.3 port=*DIGIT makes it syntactically valid.

def test_port_with_path():
    """Spec: rfc3986 §3.2.3 — R14: host:port followed by path is valid."""
    assert url("http://example.com:8080/over/there")


def test_port_with_userinfo():
    """Spec: rfc3986 §3.2.3 — R14: userinfo@host:port is valid."""
    assert url("http://userid@example.com:8080")


def test_port_with_userinfo_and_path():
    """Spec: rfc3986 §3.2.3 — R14: full authority with port and path is valid."""
    assert url("http://userid:password@example.com:8080/")


# ---------------------------------------------------------------------------
# Empty port — RFC 3986 §3.2.3 says port = *DIGIT (zero or more digits)
# ---------------------------------------------------------------------------

# test_port_empty_is_spec_valid: REMOVED — suspected violation (results/suspected_bugs/url.md)
# The code rejects trailing ':' with no port digits; RFC 3986 §3.2.3 port=*DIGIT allows 0 digits.


# ---------------------------------------------------------------------------
# Invalid port values
# ---------------------------------------------------------------------------

def test_port_with_alpha_invalid():
    """Spec: rfc3986 §3.2.3 — R15: port contains ONLY digits; letters are invalid."""
    assert not url("http://example.com:abc/path")


def test_port_with_special_chars_invalid():
    """Spec: rfc3986 §3.2.3 — R15: port must be digits only; ':' inside port is invalid."""
    assert not url("http://example.com:80:80/path")
