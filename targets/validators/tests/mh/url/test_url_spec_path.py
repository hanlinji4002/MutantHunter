"""Spec-driven tests for URI path component (RFC 3986 §3.3).

Rules covered: R16, R17, R18
"""
import pytest
from validators import url


# ---------------------------------------------------------------------------
# Valid path characters
# ---------------------------------------------------------------------------

def test_path_empty_with_authority():
    """Spec: rfc3986 §3.3 — R16: empty path is valid when authority is present."""
    assert url("http://example.com")


def test_path_slash_only():
    """Spec: rfc3986 §3.3 — R16/R18: path consisting of single '/' is valid."""
    assert url("http://example.com/")


def test_path_simple_segments():
    """Spec: rfc3986 §3.3 — R18: path with simple alpha segments is valid."""
    assert url("http://foo.com/blah_blah")


def test_path_unreserved_chars():
    """Spec: rfc3986 §3.3 — R17/R18: unreserved chars (ALPHA, DIGIT, -, ., _, ~) valid in path."""
    assert url("http://example.com/path-to_resource.here~ok")


def test_path_colon_in_segment():
    """Spec: rfc3986 §3.3 — R17: ':' is a valid pchar and may appear in path segments."""
    assert url("http://example.com/over:there")


def test_path_at_in_segment():
    """Spec: rfc3986 §3.3 — R17: '@' is a valid pchar and may appear in path segments."""
    assert url("http://example.com/path@segment")


def test_path_sub_delims_in_segment():
    """Spec: rfc3986 §3.3 — R18: sub-delims are allowed in path segments (e.g. '(', ')')."""
    assert url("http://foo.com/blah_(wikipedia)")


def test_path_pct_encoded_in_segment():
    """Spec: rfc3986 §3.3 — R17/R18/R23: pct-encoded octets are valid in path."""
    assert url("http://foo.bar/?q=Test%20URL-encoded%20stuff")


def test_path_multiple_segments():
    """Spec: rfc3986 §3.3 — R18: slash-separated multi-segment path is valid."""
    assert url("http://foo.com/blah_blah_(wikipedia)_(again)")


def test_path_with_query_and_fragment():
    """Spec: rfc3986 §3.3 — R18: path followed by query and fragment is valid."""
    assert url("http://foo.com/blah_(wikipedia)#cite-1")


# ---------------------------------------------------------------------------
# Invalid path content (when authority is present, path must start with / or be empty)
# ---------------------------------------------------------------------------

def test_path_whitespace_invalid():
    """Spec: rfc3986 §3.3 / §2 — R27: whitespace is not allowed in a URI path."""
    assert not url("http://foo.bar/foo(bar)baz quux")


def test_path_with_unencoded_space_in_query_invalid():
    """Spec: rfc3986 §3.4 / §2 — R27: spaces must be percent-encoded in query."""
    assert not url("http://foo.bar?q=Spaces should be encoded")
