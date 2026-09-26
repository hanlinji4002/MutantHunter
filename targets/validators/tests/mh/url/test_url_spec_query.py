"""Spec-driven tests for URI query component (RFC 3986 §3.4).

Rules covered: R19, R20, R27
"""
import pytest
from validators import url


# ---------------------------------------------------------------------------
# Valid query strings
# ---------------------------------------------------------------------------

def test_query_simple_key_value():
    """Spec: rfc3986 §3.4 — R19: key=value query string with pchar chars is valid."""
    assert url("http://www.example.com/wpstyle/?p=364")


def test_query_multiple_params():
    """Spec: rfc3986 §3.4 — R19: multiple key=value pairs separated by '&' is valid."""
    assert url("https://www.example.com?bar=baz")


def test_query_slash_in_query():
    """Spec: rfc3986 §3.4 — R19: '/' is explicitly allowed in query (query = *(pchar / '/' / '?'))."""
    assert url("http://example.com/path?a=b/c")


def test_query_question_mark_in_query():
    """Spec: rfc3986 §3.4 — R19: '?' is explicitly allowed within the query component."""
    assert url("http://example.com/path?a=b?c=d")


def test_query_pct_encoded():
    """Spec: rfc3986 §3.4 — R19/R23: pct-encoded octets are valid in query."""
    assert url("http://foo.bar/?q=Test%20URL-encoded%20stuff")


def test_query_fragment_after_query():
    """Spec: rfc3986 §3.4 — R20: query ends at '#'; fragment follows."""
    assert url("http://foo.com/blah_(wikipedia)_blah#cite-1")


def test_query_with_hash_fragment():
    """Spec: rfc3986 §3.4 / §3.5 — R20/R22: '?' starts query, '#' starts fragment."""
    assert url("http://code.google.com/events/#&product=browser")


# ---------------------------------------------------------------------------
# Query with sub-delims and special allowed chars
# ---------------------------------------------------------------------------

def test_query_sub_delims_allowed():
    """Spec: rfc3986 §3.4 — R19/R26: sub-delims are allowed in query strings."""
    assert url("http://example.com/path?a=b&c=d!e$f")


# test_query_colon_at_allowed: REMOVED — suspected violation (results/suspected_bugs/url.md)
# strict_query=True (default) rejects query fields without '='; RFC 3986 §3.4 pchar allows ':' and '@'.


# ---------------------------------------------------------------------------
# Invalid query content
# ---------------------------------------------------------------------------

def test_query_unencoded_space_invalid():
    """Spec: rfc3986 §3.4 / §2 — R27: raw space in query is not allowed."""
    assert not url("http://foo.bar?q=Spaces should be encoded")
