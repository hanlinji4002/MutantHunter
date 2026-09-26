# Suspected Violations — mac_address

## Dot-grouped notation not supported (three groups of four hex digits)

- Category: logic
- Spec: wiki-MAC_address.pdf Notational conventions — R4
- Input: `"0123.4567.89AB"`
- Spec says: valid (three groups of four hexadecimal digits separated by dots is an accepted human-friendly notation)
- Code returns: `ValidationError(func=mac_address, args={'value': '0123.4567.89AB'})`
- Test:
  ```python
  from validators import mac_address

  def test_dot_notation_basic():
      assert mac_address("0123.4567.89AB")

  def test_dot_notation_lowercase():
      assert mac_address("0123.4567.89ab")

  def test_dot_notation_mixed_case():
      assert mac_address("aAbB.cCdD.eEfF")

  def test_dot_notation_all_zeros():
      assert mac_address("0000.0000.0000")

  def test_dot_notation_broadcast():
      assert mac_address("FFFF.FFFF.FFFF")
  ```
- Status: unconfirmed

---

### Root cause

The validator's regex `^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$` only
matches six 2-digit groups separated by `:` or `-`.  
It does not include a branch for three 4-digit groups separated by `.`
(`^([0-9A-Fa-f]{4}\.){2}([0-9A-Fa-f]{4})$`), which the Wikipedia
Notational conventions section explicitly lists as a valid notation (Cisco
format, e.g. `0123.4567.89AB`).
