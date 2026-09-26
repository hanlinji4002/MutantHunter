"""Targeted mutant-killing tests for the url() validator.

Survivors addressed
-------------------
url:75:4:76:19:if_negate          _validate_auth_segment  line 75   — KILLABLE
url:81:7:81:22:cmp_lt_to_lte      _validate_auth_segment  line 81   — EQUIVALENT (see note)
url:81:21:81:22:int_plus_one       _validate_auth_segment  line 81   — EQUIVALENT (see note)
url:83:43:83:44:int_plus_one       _validate_auth_segment  line 83   — EQUIVALENT
url:108:56:108:57:int_plus_one     _validate_netloc        line 108  — EQUIVALENT
url:119:41:119:42:int_plus_one     _validate_netloc        line 119  — EQUIVALENT
url:123:59:123:72:cmp_in_to_notin  _validate_netloc        line 123  — KILLABLE
url:124:51:124:52:int_plus_one     _validate_netloc        line 124  — EQUIVALENT
url:143:8:149:37:if_negate         _validate_optionals     line 143  — EQUIVALENT
url:152:8:153:37:if_negate         _validate_optionals     line 152  — EQUIVALENT (platform-gated)
url:152:11:152:65:bool_and_to_or   _validate_optionals     line 152  — EQUIVALENT (platform-gated)

Equivalence notes
-----------------
lines 81–83 (cmp_lt_to_lte, int_plus_one):
  The password forbidden-char check (line 84-86) tests for literal '/', '?', '#', '@'
  in the password string.  However urlsplit() intercepts all of these before
  _validate_auth_segment() is reached:
    '/' → urlsplit ends netloc; no '@' in netloc, so _validate_auth_segment not called
    '?' → urlsplit starts query component; same result
    '#' → urlsplit starts fragment component; same result
    '@' → produces a second '@', blocked by the count('@') > 1 guard at line 101
  Percent-encoded forms (%2F, %3F, %23) are not unquoted before the check, so
  they pass the check in both original and mutant alike.
  Therefore the password character check can never fail via the public API; both
  cmp_lt_to_lte and int_plus_one route the colon==1 case to a path that produces
  the same observable output as the original.

line 83 int_plus_one:
  At line 83 colon_count is always exactly 1 (higher/lower values return earlier).
  rsplit(":", 1) and rsplit(":", 2) on a string with one colon give identical lists.

lines 108/124 int_plus_one:
  A well-formed IPv6 literal contains exactly one ']'.  replace(']', '', 1) and
  replace(']', '', 2) produce the same string.

line 119 int_plus_one:
  The count('@') > 1 guard ensures exactly one '@' at line 119.
  rsplit('@', 1) and rsplit('@', 2) on a string with one '@' give identical results.

lines 143/152 if_negate, line 152 bool_and_to_or:
  optional_segments &= True is always a no-op regardless of optional_segments'
  current value (True & True = True, False & True = False — neither branch can
  flip the value).  The except block at line 150 is only reached on Python < 3.9.2;
  on the current test interpreter (Python 3.12) it is never executed.
"""

from validators import url


# ===========================================================================
# GROUP 1 — _validate_auth_segment, line 75: if_negate
# Original:  if not value: return True   → empty auth → early True
# Mutant:    if not not value: return True  ≡  if value: return True
#            → any non-empty auth → early True, bypassing all validation
# Kill: a URL whose auth segment is non-empty but invalid must be rejected.
# ===========================================================================


def test_line75_kill_invalid_unicode_username_rejected():
    """Docstring: _validate_auth_segment

    Non-empty auth segment whose username contains characters outside the
    username regex (here Greek letters αβγ which are not in _username_regex)
    must be rejected.
    Original: not value is False → skips early-return → validates → regex fails → invalid.
    Mutant:   if value is True → returns True early → accepts invalid username.
    urlsplit preserves the Greek letters in netloc; _validate_auth_segment
    receives 'αβγ' and its regex returns None (falsy).
    """
    assert not url("http://αβγ@example.com")


def test_line75_nonempty_valid_username_accepted():
    """Docstring: _validate_auth_segment

    Positive counterpart: a non-empty valid username must still be accepted.
    Confirms the non-mutant path does not over-reject.
    """
    assert url("http://user@example.com")


def test_line75_empty_auth_still_valid():
    """Docstring: _validate_auth_segment

    Empty auth segment (URL http://@host.com) must be valid.
    Original returns True for empty string at line 75.
    Mutant skips the empty-string branch (if value is False → no early return);
    the empty string then reaches colon_count checks without issue and returns
    the username-regex match of '', which is also falsy — so the mutant would
    REJECT this, while the original ACCEPTS it.
    This provides a second kill vector for the line-75 mutant.
    """
    assert url("http://@example.com")


# ===========================================================================
# GROUP 2 — _validate_auth_segment, lines 81-83: cmp_lt_to_lte / int_plus_one
# Conclusion: EQUIVALENT via public API.
# Reason: the password forbidden-char check (/, ?, #, @) can never fail
# because urlsplit intercepts those characters before _validate_auth_segment
# receives the auth string (see module docstring for full explanation).
#
# Tests below confirm the surrounding behavior is correct and provide
# boundary coverage on both sides of the colon_count thresholds.
# ===========================================================================


def test_line81_colon_count_zero_username_only_valid():
    """Docstring: _validate_auth_segment

    Boundary colon_count == 0 (below threshold 1).
    Both original and all mutants route here to username-only path; result
    must be identical.  Valid plain username must be accepted.
    """
    assert url("http://alice@example.com")


def test_line81_colon_count_one_valid_password_accepted():
    """Docstring: _validate_auth_segment

    Boundary colon_count == 1 (the exact threshold tested by lines 81-83).
    Both cmp_lt_to_lte and int_plus_one mutants route colon_count==1 to the
    username-only regex.  For a password with no forbidden chars the result
    is the same as the original (password check passes anyway).
    """
    assert url("http://alice:wonderland@example.com")


def test_line81_colon_count_two_multi_colon_valid():
    """Docstring: _validate_auth_segment

    Boundary colon_count == 2 (just above > 1 threshold at line 77).
    Neither cmp_lt_to_lte nor int_plus_one mutants affect this branch.
    Must be accepted (whole segment treated as username).
    """
    assert url("http://a:b:c@example.com")


def test_line83_rsplit_one_colon_identical():
    """Docstring: _validate_auth_segment

    With exactly one colon in the auth segment, rsplit(':', 1) and
    rsplit(':', 2) produce identical results.  int_plus_one at line 83 is
    therefore equivalent.  Positive case: must be valid.
    """
    assert url("http://user:pass@example.com")


# ===========================================================================
# GROUP 3 — _validate_netloc, line 108: int_plus_one
# Original:  value.lstrip("[").replace("]", "", 1)
# Mutant:    value.lstrip("[").replace("]", "", 2)
# Conclusion: EQUIVALENT — well-formed IPv6 literal has exactly one ']'.
# ===========================================================================


def test_line108_ipv6_no_auth_no_port_valid():
    """Docstring: _validate_netloc

    IPv6 without port and without auth goes through the bracket-stripping
    code at line 108.  Single ']' means replace(']','',1) == replace(']','',2).
    Positive case to confirm this path is correct.
    """
    assert url("http://[::1]")


def test_line108_ipv6_no_auth_with_port_bypasses_strip():
    """Docstring: _validate_netloc

    IPv6 with port (']:' present) uses raw value at line 107, so line 108
    bracket-strip code is not reached.  Confirms the ']:' guard still works.
    """
    assert url("http://[::1]:8080/path")


# ===========================================================================
# GROUP 4 — _validate_netloc, line 119: int_plus_one
# Original:  value.rsplit("@", 1)
# Mutant:    value.rsplit("@", 2)
# Conclusion: EQUIVALENT — exactly one '@' guaranteed by line 101 guard.
# ===========================================================================


def test_line119_single_at_rsplit_equivalent_valid():
    """Docstring: _validate_netloc

    With exactly one '@' in netloc, rsplit('@', 1) and rsplit('@', 2) return
    the same two-element list.  int_plus_one mutant at line 119 is equivalent.
    Positive case: single-'@' URL must be valid.
    """
    assert url("http://user@example.com")


def test_line119_double_at_blocked_before_line119():
    """Docstring: _validate_netloc

    Two '@' in netloc triggers count('@') > 1 → False at line 101, before
    line 119 is reached.  The rsplit mutation is irrelevant here.
    """
    assert not url("http://a@b@example.com")


# ===========================================================================
# GROUP 5 — _validate_netloc, line 123: cmp_in_to_notin  ← KILLABLE
# Original:  ']:' in value   → True for IPv6+port → use raw bracketed host
# Mutant:    ']:' not in value → False for IPv6+port → strip brackets
#
# Context: auth branch (line 119+). netloc = "user@[::1]:8080"
#   value = "user@[::1]:8080"
#   host  = "[::1]:8080"  (after rsplit('@', 1))
#   _confirm_ipv6_skip(host, False) = False (starts '[', 2+ colons)
#   Original: False OR (']:' in "user@[::1]:8080") = False OR True = True
#             → pass raw host "[::1]:8080" to hostname  ✓
#   Mutant:   False OR (']:' NOT in "user@[::1]:8080") = False OR False = False
#             → strip brackets: "::1:8080" → malformed input to hostname ✗
# ===========================================================================


def test_line123_ipv6_port_auth_valid():
    """Docstring: _validate_netloc

    IPv6 address with port AND userinfo: '']:'' is present in the full
    netloc value, so original uses the raw bracketed host form which
    hostname() can validate correctly.
    Mutant flips '']:'' not in value → True → strips brackets → passes
    malformed '::1:8080' to hostname → rejected.
    A valid URL with auth + IPv6 + port must succeed.
    """
    assert url("http://user@[::1]:8080/path")


def test_line123_ipv6_port_auth_full_addr_valid():
    """Docstring: _validate_netloc

    Same kill vector with a full 128-bit IPv6 address to confirm the
    ']:' detection is robust with longer addresses.
    """
    assert url("http://user@[FEDC:BA98:7654:3210:FEDC:BA98:7654:3210]:80")


def test_line123_ipv6_port_auth_standard_port_valid():
    """Docstring: _validate_netloc

    IPv6+port+auth on port 443 — exercises the same ']:' path.
    """
    assert url("http://user@[2001:db8::1]:443/secure")


def test_line123_ipv6_no_port_auth_both_sides():
    """Docstring: _validate_netloc

    Boundary: IPv6 without port in auth netloc.
    '']:'' is NOT present → both original and mutant take the bracket-strip path.
    _confirm_ipv6_skip is still False (starts '[', 2+ colons) so brackets are
    stripped and '::1' is passed to hostname.  Must be valid for both.
    """
    assert url("http://user@[::1]")


def test_line123_regular_host_auth_no_ipv6():
    """Docstring: _validate_netloc

    Regular domain with auth: no ']:' in value; _confirm_ipv6_skip is True
    (no IPv6 markers) so the condition short-circuits and raw host is used.
    Neither branch of ']:' check matters.
    """
    assert url("http://user:password@example.com:8080/path")


# ===========================================================================
# GROUP 6 — _validate_netloc, line 124: int_plus_one
# Original:  host.lstrip("[").replace("]", "", 1)
# Mutant:    host.lstrip("[").replace("]", "", 2)
# Conclusion: EQUIVALENT — same single-']' argument as line 108.
# ===========================================================================


def test_line124_ipv6_auth_no_port_bracket_strip_equivalent():
    """Docstring: _validate_netloc

    IPv6 without port in auth branch: brackets stripped at line 124.
    Single ']' means replace(']','',1) == replace(']','',2). Equivalent.
    Positive case: must be valid.
    """
    assert url("http://user@[::1]")


# ===========================================================================
# GROUP 7 — _validate_optionals, line 143: if_negate
# Original:  if (query and parse_qs(…)): optional_segments &= True
# Mutant:    if not (query and parse_qs(…)): optional_segments &= True
# Conclusion: EQUIVALENT — &= True is a no-op in all cases.
#   optional_segments starts True; True & True = True; False & True = False.
#   Neither branch can change optional_segments' value.
#   A ValueError from parse_qs (strict mode, invalid query) propagates before
#   any &= is evaluated — identical for original and mutant.
# ===========================================================================


def test_line143_valid_query_accepted():
    """Docstring: _validate_optionals

    Well-formed key=value query is accepted (try-branch path through line 143).
    if_negate mutant is equivalent; test confirms no regression.
    """
    assert url("http://example.com/path?key=value")


def test_line143_multiple_kv_accepted():
    """Docstring: _validate_optionals

    Multiple key=value pairs separated by '&' are accepted.
    """
    assert url("http://example.com/?a=1&b=2&c=3")


def test_line143_strict_invalid_query_rejected():
    """Docstring: _validate_optionals

    strict_query=True (default) rejects a bare key with no '='.
    parse_qs raises ValueError → propagates out; identical for original and mutant.
    """
    assert not url("http://example.com/?badkey")


def test_line143_no_query_valid():
    """Docstring: _validate_optionals

    URL with no query: query is '' (falsy), neither branch entered. No-op.
    """
    assert url("http://example.com/path")


# ===========================================================================
# GROUP 8 — _validate_optionals, lines 152-153 (except TypeError path)
# url:152:8:153:37:if_negate
# url:152:11:152:65:bool_and_to_or
# Conclusion: EQUIVALENT (platform-gated)
#   The except block is only reached on Python < 3.9.2 when the separator=
#   keyword argument raises TypeError.  On Python 3.12 (current env) this
#   block is never executed.  These mutants are unreachable via public API.
# ===========================================================================


def test_line152_modern_python_try_branch_not_except():
    """Docstring: _validate_optionals

    On Python ≥ 3.9.2, parse_qs accepts separator= without raising TypeError,
    so the except block at line 150 is never reached.  The if_negate and
    bool_and_to_or mutations at line 152 are unreachable; their equivalence
    is confirmed by the try-branch handling valid queries correctly.
    """
    assert url("http://example.com/?name=ferret&color=brown")
