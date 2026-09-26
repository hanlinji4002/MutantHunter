"""Spec-driven tests for URI authority component (RFC 3986 §3.2).

Rules covered: R5, R6, R7, R8, R31
"""
import pytest
from validators import url


# ---------------------------------------------------------------------------
# Authority present — basic valid cases
# ---------------------------------------------------------------------------

def test_authority_host_only():
    """Spec: rfc3986 §3.2 — R6: bare host is the minimum valid authority."""
    assert url("http://example.com")


def test_authority_with_port():
    """Spec: rfc3986 §3.2 — R6: authority may include port."""
    assert url("http://example.com:8080")


def test_authority_with_userinfo():
    """Spec: rfc3986 §3.2 — R6/R7: authority may include userinfo@host."""
    assert url("http://user@example.com")


def test_authority_with_userinfo_and_port():
    """Spec: rfc3986 §3.2 — R6: full authority userinfo@host:port is valid."""
    assert url("http://user:password@example.com:8080")


# ---------------------------------------------------------------------------
# Userinfo characters — RFC 3986 §3.2.1
# ---------------------------------------------------------------------------

def test_userinfo_colon_allowed():
    """Spec: rfc3986 §3.2.1 — R7: ':' is explicitly allowed in userinfo."""
    assert url("http://userid:password@example.com")


def test_userinfo_multiple_colons_allowed():
    """Spec: rfc3986 §3.2.1 — R7: multiple ':' in userinfo are syntactically valid."""
    assert url("http://:::::::::::::@exmp.com")


def test_userinfo_unreserved_chars():
    """Spec: rfc3986 §3.2.1 — R7: unreserved chars (ALPHA, DIGIT, -, ., _, ~) allowed in userinfo."""
    assert url("http://user.name_test~ok@example.com")


def test_userinfo_sub_delims_in_userinfo():
    """Spec: rfc3986 §3.2.1 — R7: sub-delims are allowed in userinfo."""
    # sub-delims: ! $ & ' ( ) * + , ; =
    assert url("http://-.~_!$&'()*+,;=:%40:80%2f::::::@example.com")


def test_userinfo_pct_encoded():
    """Spec: rfc3986 §3.2.1 — R7/R23: pct-encoded octets are valid in userinfo."""
    assert url("http://user%40name@example.com")


# ---------------------------------------------------------------------------
# Userinfo @ delimiter rules
# ---------------------------------------------------------------------------

def test_single_at_sign_valid():
    """Spec: rfc3986 §3.2.1 — R8: exactly one '@' separates userinfo from host."""
    assert url("http://user@example.com")


def test_multiple_at_signs_invalid():
    """Spec: rfc3986 §3.2 / §3.2.1 — R31: more than one '@' in the authority is invalid."""
    assert not url("http://user@evil@example.com")


# ---------------------------------------------------------------------------
# Path must be empty or start with "/" when authority is present
# ---------------------------------------------------------------------------

def test_authority_with_empty_path_valid():
    """Spec: rfc3986 §3.2 — R16: empty path is valid when authority is present."""
    assert url("http://example.com")


def test_authority_with_slash_path_valid():
    """Spec: rfc3986 §3.2 — R16: path starting with '/' is valid when authority present."""
    assert url("http://example.com/path/to/resource")
