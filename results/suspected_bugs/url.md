# Suspected Violations — `url`

## Port zero rejected by implementation

- Category: logic
- Spec: rfc3986 §3.2.3 — R14
- Input: `"http://example.com:0/path"`
- Spec says: valid — `port = *DIGIT`; port 0 is a single digit and is syntactically legal per the RFC grammar
- Code returns: `ValidationError` — the hostname validator rejects port 0 (treats it as invalid rather than applying a pure syntax check)
- Test:
  ```python
  from validators import url
  def test_port_zero():
      """Spec: rfc3986 §3.2.3 — R14: port 0 is syntactically valid per *DIGIT grammar."""
      assert url("http://example.com:0/path")
  ```
- Status: unconfirmed

## Empty port (trailing colon) rejected by implementation

- Category: logic
- Spec: rfc3986 §3.2.3 — R14
- Input: `"http://example.com:"`
- Spec says: valid — `port = *DIGIT` allows zero digits; RFC 3986 §3.2.3 says producers SHOULD omit the `:` when port is empty but parsers must accept it
- Code returns: `ValidationError` — the hostname validator rejects a trailing `:` with no port digits
- Test:
  ```python
  from validators import url
  def test_port_empty_is_spec_valid():
      """Spec: rfc3986 §3.2.3 — R14: port = *DIGIT; empty port (host:) is syntactically valid."""
      assert url("http://example.com:")
  ```
- Status: unconfirmed

## Strict-query rejects RFC-valid pchar characters in query (`:` and `@`)

- Category: spec-ambiguous
- Spec: rfc3986 §3.4 — R19
- Input: `"http://example.com/path?user:name@host"`
- Spec says: valid — `query = *(pchar / "/" / "?")` and `pchar` includes both `:` and `@`; the query string `user:name@host` is syntactically correct per RFC 3986
- Code returns: `ValidationError(reason="bad query field: 'user:name@host'")` — `parse_qs` with `strict_parsing=True` (the default) treats an unquoted field with no `=` separator as a parse error
- Test:
  ```python
  from validators import url
  def test_query_colon_at_allowed():
      """Spec: rfc3986 §3.4 — R19: ':' and '@' (pchar) are allowed in query."""
      assert url("http://example.com/path?user:name@host")
  ```
- Status: unconfirmed
- Note: The `strict_query=True` default is an application-level policy choice, not an RFC grammar rule. The human tests at `tests/test_url.py` are consistent with `strict_query=True` (e.g. they mark `?bar=baz&inga=42&quux` as invalid). This is therefore `spec-ambiguous` rather than a clear logic bug.
