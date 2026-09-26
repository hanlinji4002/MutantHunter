# Suspected Violations — `email`

## Space in quoted-string local part rejected

- Category: logic
- Spec: rfc5321 §4.1.2 — R3
- Input: `'"John Doe"@example.com'`
- Spec says: valid — quoted-string may contain spaces
- Code returns: `ValidationError`
- Test:
  ```python
  from validators import email
  def test_quoted_string_space():
      """Spec: rfc5321 §4.1.2 — R3"""
      assert email('"John Doe"@example.com')
  ```
- Status: unconfirmed

## Single-character TLD rejected

- Category: logic
- Spec: rfc5321 §2.3.5 — R8
- Input: `'user@example.x'`
- Spec says: valid — no minimum TLD length in the RFC grammar
- Code returns: `ValidationError`
- Test:
  ```python
  from validators import email
  def test_single_char_tld():
      """Spec: rfc5321 §2.3.5 — R8"""
      assert email('user@example.x')
  ```
- Status: unconfirmed

## IPv6 literal with 'IPv6:' tag not accepted

- Category: logic
- Spec: rfc5321 §4.1.3 — R11
- Input: `'user@[IPv6:2001:db8::1]'`
- Spec says: valid
- Code returns: `ValidationError`
- Test:
  ```python
  from validators import email
  def test_ipv6_literal_tag():
      """Spec: rfc5321 §4.1.3 — R11"""
      assert email('user@[IPv6:2001:db8::1]')
  ```
- Status: unconfirmed

## @ inside quoted-string local part rejected

- Category: logic
- Spec: rfc5321 §4.1.2 — R4
- Input: `'"user@old"@example.com'`
- Spec says: valid — @ is allowed inside a quoted string
- Code returns: `ValidationError`
- Test:
  ```python
  from validators import email
  def test_at_in_quoted_string():
      """Spec: rfc5321 §4.1.2 — R4"""
      assert email('"user@old"@example.com')
  ```
- Status: unconfirmed
