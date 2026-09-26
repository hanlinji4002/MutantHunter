"""Spec tests for email quoted-string local-part rules.

Rules covered: R6
Sources: RFC 5322 §3.2.4, §3.4.1 / RFC 5321 §4.1.2
"""

import validators


# ---------------------------------------------------------------------------
# R6 — quoted-string local-part
# ---------------------------------------------------------------------------

def test_quoted_local_part_simple_valid():
    """Spec: RFC 5322 3.2.4 — R6

    A quoted-string local-part enclosed in double-quotes is valid.
    """
    assert validators.email('"user"@example.com')


def test_quoted_local_part_empty_quoted_string_valid():
    """Spec: RFC 5322 3.2.4 — R6

    quoted-string = DQUOTE *([FWS] qcontent) [FWS] DQUOTE  — zero
    qcontent characters is syntactically valid (empty quoted-string).
    """
    assert validators.email('""@example.com')


def test_quoted_local_part_unclosed_quote_invalid():
    """Spec: RFC 5322 3.2.4 — R6

    A local-part that starts with a double-quote but does not close it is
    not a valid quoted-string and must be rejected.
    """
    assert not validators.email('"user@example.com')


def test_local_part_bare_double_quote_invalid():
    """Spec: RFC 5322 3.2.3 — R6 / R15

    A bare double-quote that is not part of a properly delimited
    quoted-string is a 'special' and invalid in an unquoted local-part.
    """
    assert not validators.email('u"ser@example.com')
