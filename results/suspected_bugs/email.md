# Suspected Bugs — email

## SV-1: Quoted-string local part with space is rejected

- Category: logic
- Spec: RFC 5321 4.1.2 — R6
- Input: `'" "@example.com'`
- Spec says: valid — qtextSMTP is `%d32-33 / %d35-91 / %d93-126`; space (0x20 = %d32) is explicitly permitted inside a quoted-string
- Code returns: `ValidationError` (falsy)
- Test:
  ```python
  from validators import email
  assert email('" "@example.com')
  ```
- Status: confirmed
- Code: `src/validators/email.py:93-95` — the quoted-string character class `[... !#-\[\]-\177]` omits 0x20 (space), which RFC 5321 qtextSMTP (`%d32-33`) allows.
- Upstream: no existing issue found (searched python-validators/validators issues on 2026-09-26); still present on master.
- Same root cause as SV-4 (quoted-string handling); counted once.
- Broad-test removed: `test_quoted_string_with_space` — asserted current behavior

## SV-2: Single-character TLD is rejected

- Category: logic
- Spec: RFC 5321 4.1.2 / RFC 1034 — R7
- Input: `'user@example.a'`
- Spec says: valid — neither RFC 5321 nor RFC 1034 imposes a minimum TLD length; a single-label TLD is syntactically legal
- Code returns: `ValidationError` (falsy)
- Test:
  ```python
  from validators import email
  assert email("user@example.a")
  ```
- Status: rejected
- Review: design choice, not a logic bug. The library requires a TLD of 2-63 letters (see upstream PR #476, which kept that rule), and no single-character TLD exists in the DNS root.

## SV-3: IPv6 address literal with `IPv6:` tag is rejected

- Category: logic
- Spec: RFC 5321 4.1.3 — R11
- Input: `'user@[IPv6:::1]'` with `ipv6_address=True` / `'user@[IPv6:2001:0db8:85a3:0000:0000:8a2e:0370:7334]'` with `ipv6_address=True`
- Spec says: valid — IPv6 literals in email domains MUST use the `IPv6:` prefix inside brackets; `[IPv6:::1]` and `[IPv6:2001:…]` are the correct form
- Code returns: `ValidationError` (falsy) — the implementation strips brackets with `lstrip("[").rstrip("]")`, leaving `IPv6:::1`, but then passes it directly to the `hostname` validator which does not know how to handle the `IPv6:` prefix
- Test:
  ```python
  from validators import email
  assert email("user@[IPv6:::1]", ipv6_address=True)
  assert email("user@[IPv6:2001:0db8:85a3:0000:0000:8a2e:0370:7334]", ipv6_address=True)
  ```
- Status: confirmed
- Code: `src/validators/email.py:70` — `domain_part.lstrip("[").rstrip("]")` keeps the `IPv6:` tag, so the RFC 5321 form `[IPv6:::1]` is rejected while the non-standard `[::1]` is accepted.
- Upstream: no existing issue found (searched 2026-09-26); still present on master.

## SV-4: Quoted-string local part containing `@` or special characters is rejected

- Category: logic
- Spec: RFC 5322 3.2.4 / RFC 5321 4.1.2 — R6
- Input: `'"user@name"@example.com'` / `'"user name"@example.com'`
- Spec says: valid — any printable ASCII character except unescaped `"` and `\` is allowed inside a quoted-string, including `@`, spaces, and `(`, `)`, `,`, `;`, `<`, `>`, `:`
- Code returns: `ValidationError` (falsy) — for `@` inside quotes, the count-`@` check at line 58 rejects addresses with more than one `@`; for spaces, the quoted-string regex character class omits 0x20
- Test:
  ```python
  from validators import email
  assert email('"user name"@example.com')
  assert email('"user@name"@example.com')
  ```
- Status: confirmed
- Code: `src/validators/email.py:58` — `value.count("@") != 1` rejects any `@` inside a quoted local part before the quoted-string regex runs; spaces fail at `email.py:93-95` (see SV-1).
- Upstream: no existing issue found (searched 2026-09-26); still present on master.
- Same root cause as SV-1; counted once together with SV-1.
