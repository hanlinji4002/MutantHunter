"""Spec-driven tests for URI fragment component (RFC 3986 §3.5).

Rules covered: R21, R22, R30
"""
import pytest
from validators import url


# ---------------------------------------------------------------------------
# Valid fragment strings
# ---------------------------------------------------------------------------

def test_fragment_simple():
    """Spec: rfc3986 §3.5 — R21/R22: '#' introduces a fragment; simple fragment is valid."""
    assert url("http://foo.com/blah_(wikipedia)#cite-1")


def test_fragment_alphanumeric():
    """Spec: rfc3986 §3.5 — R21: fragment chars include ALPHA/DIGIT (unreserved)."""
    assert url("http://example.com/path#section1")


def test_fragment_with_slash_and_question():
    """Spec: rfc3986 §3.5 — R21: '/' and '?' are explicitly allowed in fragment."""
    assert url("http://example.com/path#a/b?c")


def test_fragment_with_pct_encoded():
    """Spec: rfc3986 §3.5 — R21/R23: pct-encoded octets are valid in fragment."""
    assert url("https://example.org/path#2022%201040%20(Cornelius%20Morgan%20G).pdf")


def test_fragment_with_hash_anchor_ref():
    """Spec: rfc3986 §3.5 — R22: '#' followed by anchor text is a valid fragment."""
    assert url("https://exchange.jetswap.finance/#/swap")


def test_fragment_sub_delims_allowed():
    """Spec: rfc3986 §3.5 — R21/R26: sub-delims are allowed in fragment (pchar includes sub-delims)."""
    assert url("http://example.com/path#anchor!ref$ok")


def test_fragment_at_and_colon_allowed():
    """Spec: rfc3986 §3.5 — R21: ':' and '@' (from pchar) are allowed in fragment."""
    assert url("http://example.com/path#user:pass@host")


def test_fragment_complex():
    """Spec: rfc3986 §3.5 — R21: complex fragment with pchar, '/', '?' chars is valid."""
    assert url("https://matrix.to/#/!BSqRHgvCtIsGittkBG:talk.puri.sm/$1551464398"
               "853539kMJNP:matrix.org?via=talk.puri.sm&via=matrix.org")


# ---------------------------------------------------------------------------
# Fragment delimiter behaviour
# ---------------------------------------------------------------------------

def test_no_fragment_is_valid():
    """Spec: rfc3986 §3.5 — R22: fragment is optional; URI without '#' is valid."""
    assert url("http://example.com/path?q=1")


def test_empty_fragment_distinct_from_no_fragment():
    """Spec: rfc3986 §3.5 / §5.3 — R30: '#' with empty fragment is syntactically valid.

    Per RFC 3986, empty fragment is syntactically valid.
    NOTE: implementation behaviour on 'http://example.com/#' is recorded here.
    """
    # RFC says fragment = *(...), so zero-length fragment is valid after '#'
    assert url("http://example.com/#")
