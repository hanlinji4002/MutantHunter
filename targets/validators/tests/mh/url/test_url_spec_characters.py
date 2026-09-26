"""Spec-driven tests for URI character classes (RFC 3986 §2).

Rules covered: R23, R24, R25, R26, R27
"""
import pytest
from validators import url


# ---------------------------------------------------------------------------
# Percent-encoding (§2.1, R23)
# ---------------------------------------------------------------------------

def test_pct_encoded_uppercase_hex():
    """Spec: rfc3986 §2.1 — R23: '%' followed by two uppercase hex digits is valid pct-encoded."""
    assert url("http://foo.bar/?q=Test%20URL-encoded%20stuff")


def test_pct_encoded_lowercase_hex():
    """Spec: rfc3986 §2.1 — R23: '%' followed by two lowercase hex digits is equally valid."""
    assert url("http://example.com/path%2fmore")


def test_pct_encoded_mixed_case_hex():
    """Spec: rfc3986 §2.1 — R23: mixed-case hex in pct-encoded is valid (%2F and %2f are equal)."""
    assert url("http://example.com/%2Fpath")


def test_pct_encoded_in_query():
    """Spec: rfc3986 §2.1 — R23: pct-encoded allowed in query component."""
    assert url("http://example.com/?name=Jo%C3%ABl")


def test_pct_encoded_in_fragment():
    """Spec: rfc3986 §2.1 — R23: pct-encoded allowed in fragment component."""
    assert url("https://example.org/path#2022%201040%20(Cornelius%20Morgan%20G).pdf")


# ---------------------------------------------------------------------------
# Unreserved characters (§2.3, R24)
# ---------------------------------------------------------------------------

def test_unreserved_alpha_in_path():
    """Spec: rfc3986 §2.3 — R24: ALPHA is unreserved; letters in path are valid."""
    assert url("http://example.com/SomePath")


def test_unreserved_digit_in_path():
    """Spec: rfc3986 §2.3 — R24: DIGIT is unreserved; digits in path are valid."""
    assert url("http://example.com/path123")


def test_unreserved_hyphen_in_path():
    """Spec: rfc3986 §2.3 — R24: '-' is unreserved; hyphen in path is valid."""
    assert url("http://example.com/path-to-resource")


def test_unreserved_period_in_path():
    """Spec: rfc3986 §2.3 — R24: '.' is unreserved; period in path is valid."""
    assert url("http://example.com/resource.html")


def test_unreserved_underscore_in_path():
    """Spec: rfc3986 §2.3 — R24: '_' is unreserved; underscore in path is valid."""
    assert url("http://example.com/path_to_resource")


def test_unreserved_tilde_in_path():
    """Spec: rfc3986 §2.3 — R24: '~' is unreserved; tilde in path is valid."""
    assert url("http://example.com/~user/page")


# ---------------------------------------------------------------------------
# Sub-delimiters (§2.2, R26)
# ---------------------------------------------------------------------------

def test_sub_delims_exclamation_in_path():
    """Spec: rfc3986 §2.2 — R26: '!' is a sub-delim and is allowed in path segments."""
    assert url("http://example.com/path!resource")


def test_sub_delims_dollar_in_path():
    """Spec: rfc3986 §2.2 — R26: '$' is a sub-delim and is allowed in path segments."""
    assert url("http://example.com/path$resource")


def test_sub_delims_ampersand_in_query():
    """Spec: rfc3986 §2.2 — R26: '&' is a sub-delim and is allowed in query strings."""
    assert url("http://example.com/?a=1&b=2")


def test_sub_delims_parens_in_path():
    """Spec: rfc3986 §2.2 — R26: '(' and ')' are sub-delims and allowed in path."""
    assert url("http://foo.com/blah_(wikipedia)")


def test_sub_delims_asterisk_in_path():
    """Spec: rfc3986 §2.2 — R26: '*' is a sub-delim and is allowed in path segments."""
    assert url("http://example.com/path*resource")


def test_sub_delims_plus_in_query():
    """Spec: rfc3986 §2.2 — R26: '+' is a sub-delim and is allowed in query."""
    assert url("http://example.com/?q=hello+world")


def test_sub_delims_semicolon_in_path():
    """Spec: rfc3986 §2.2 — R26: ';' is a sub-delim and is allowed in path segments."""
    assert url("http://example.com/path;param=value")


def test_sub_delims_equals_in_query():
    """Spec: rfc3986 §2.2 — R26: '=' is a sub-delim and is allowed in query."""
    assert url("http://example.com/?key=value")


# ---------------------------------------------------------------------------
# Whitespace is forbidden (§2 / §1.2.1, R27)
# ---------------------------------------------------------------------------

def test_space_in_uri_invalid():
    """Spec: rfc3986 §2 — R27: raw space character is not a valid URI character."""
    assert not url("http://foo.bar/foo(bar)baz quux")


def test_space_in_query_invalid():
    """Spec: rfc3986 §2 — R27: raw space in query string is invalid."""
    assert not url("http://foo.bar?q=Spaces should be encoded")


def test_space_in_scheme_invalid():
    """Spec: rfc3986 §2 / §3.1 — R27: space inside scheme is invalid."""
    assert not url("htt p://example.com")
