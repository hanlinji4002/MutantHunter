## Simple hostname regex caps at 61 characters instead of 63

- Category: logic
- Spec: rfc1123.pdf Section 2.1 — R8
- Input: `"a" * 62`  (and `"a" * 63`)
- Spec says: valid — RFC 1123 §2.1 states "Host software MUST handle host names of up to 63 characters"
- Code returns: `ValidationError` — the `_simple_hostname_regex` in `hostname.py` uses `{0,59}` for the middle segment which, combined with the mandatory first char and optional last char, caps the total at 61 characters (1 + 59 + 1 = 61). The comment in the source even acknowledges the range should be `{1, 61}` but that is already incorrect per the spec (should be `{1, 63}`).
- Test:
  ```python
  def test_label_63_chars_valid():
      label = "a" * 63
      assert hostname(label)

  def test_label_62_chars_valid():
      label = "a" * 62
      assert hostname(label)

  def test_label_63_chars_with_hyphen_valid():
      label = "a" + "b" * 61 + "c"  # 63 chars total
      assert hostname(label)
  ```
- Broad-test removed: `test_simple_62_chars_invalid` — asserted current behavior (62-char label invalid)
- Status: confirmed
- Bug: hostname-63-characters
- Code: `src/validators/hostname.py:27-29` — `[a-z0-9-]{0,59}` between the first and last character caps a single-label hostname at 61 characters; RFC 1123 section 2.1 requires up to 63. Labels inside a dotted name are checked by `domain()` and are not affected.
- Upstream: no issue for this cap (related feature request #433 on RFC 1123 support); still present on master.
