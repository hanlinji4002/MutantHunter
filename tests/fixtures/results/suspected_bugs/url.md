# Suspected Violations — `url`

## Port zero rejected by implementation

- Category: logic
- Spec: rfc3986 §3.2.3 — R14
- Input: `"http://example.com:0/path"`
- Spec says: valid — `port = *DIGIT`; port 0 is syntactically legal per the RFC grammar
- Code returns: `ValidationError`
- Test:
  ```python
  from validators import url
  def test_port_zero():
      """Spec: rfc3986 §3.2.3 — R14"""
      assert url("http://example.com:0/path")
  ```
- Status: unconfirmed

## Empty port (trailing colon) rejected by implementation

- Category: logic
- Spec: rfc3986 §3.2.3 — R14
- Input: `"http://example.com:"`
- Spec says: valid — `port = *DIGIT` allows zero digits
- Code returns: `ValidationError`
- Test:
  ```python
  from validators import url
  def test_port_empty_is_spec_valid():
      """Spec: rfc3986 §3.2.3 — R14"""
      assert url("http://example.com:")
  ```
- Status: unconfirmed

## Strict-query rejects RFC-valid pchar characters in query

- Category: spec-ambiguous
- Spec: rfc3986 §3.4 — R19
- Input: `"http://example.com/path?user:name@host"`
- Spec says: valid — `query = *(pchar / "/" / "?")`
- Code returns: `ValidationError`
- Test:
  ```python
  from validators import url
  def test_query_colon_at_allowed():
      """Spec: rfc3986 §3.4 — R19"""
      assert url("http://example.com/path?user:name@host")
  ```
- Status: unconfirmed
