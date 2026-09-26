# Suspected Bugs — finance

## ISIN checksum never accumulates — `_isin_checksum` loop does not update `check`
- Category: logic
- Spec: wiki-ISIN.txt § Examples — R21
- Input: `"US0378331006"` (wrong check digit; correct is `"US0378331005"`)
- Spec says: invalid (Luhn check digit must be 5, not 6)
- Code returns: True (check is always 0 because the loop never adds val to check)
- Test:
  ```python
  from validators import isin
  def test_isin_invalid_wrong_check_digit_apple():
      """Spec: wiki-ISIN.txt § Examples — Apple, Inc. — R21
      'US0378331006' (check digit 6 instead of 5) must be invalid.
      """
      assert not isin("US0378331006")
  ```
- Status: confirmed
- Bug: isin-check-digit
- Code: `src/validators/finance.py:34-51` — `_isin_checksum` computes `val` but never adds it to `check`, so `return (check % 10) == 0` is always True and any check digit is accepted.
- Upstream: known bug, issue #440 (open) with open fix PRs #464, #468 and #473; still present on master. MutantHunter rediscovered it from the spec, it is not new.
- The other three ISIN entries below have the same root cause; the four entries count as one bug.
- Broad-test removed: `test_isin_wrong_checksum_passes_due_to_bug` — asserted current behavior

## ISIN checksum never accumulates — last char letter incorrectly accepted
- Category: logic
- Spec: wiki-ISIN.txt § Description — R16
- Input: `"US037833100A"` (last character is letter 'A', not a digit)
- Spec says: invalid (last character must be a numerical check digit 0–9)
- Code returns: True (check is always 0 because the loop never adds val to check)
- Test:
  ```python
  from validators import isin
  def test_isin_last_char_letter_is_invalid():
      """Spec: wiki-ISIN.txt § Description — R16
      An ISIN whose last character is a letter rather than a digit must be invalid.
      """
      assert not isin("US037833100A")
  ```
- Status: confirmed
- Bug: isin-check-digit
- Review: same root cause as the first ISIN entry (#440); counted once.
- Broad-test removed: `test_isin_12_letter_string_passes_due_to_bug` — asserted current behavior

## ISIN checksum never accumulates — wrong check digit for Treasury Corp Victoria
- Category: logic
- Spec: wiki-ISIN.txt § Examples — R21
- Input: `"AU0000XVGZA4"` (wrong check digit; correct is `"AU0000XVGZA3"`)
- Spec says: invalid (Luhn check digit must be 3, not 4)
- Code returns: True
- Test:
  ```python
  from validators import isin
  def test_isin_invalid_wrong_check_digit_treasury():
      """Spec: wiki-ISIN.txt § Examples — Treasury Corp Victoria — R21
      'AU0000XVGZA4' (check digit 4 instead of 3) must be invalid.
      """
      assert not isin("AU0000XVGZA4")
  ```
- Status: confirmed
- Bug: isin-check-digit
- Review: same root cause as the first ISIN entry (#440); counted once.

## ISIN checksum never accumulates — wrong check digit for BAE Systems
- Category: logic
- Spec: wiki-ISIN.txt § Examples — BAE Systems — R21
- Input: `"GB0002634947"` (wrong check digit; correct is `"GB0002634946"`)
- Spec says: invalid (correct check digit is 6)
- Code returns: True
- Test:
  ```python
  from validators import isin
  def test_isin_invalid_wrong_check_digit_bae():
      """Spec: wiki-ISIN.txt § Examples — BAE Systems — R21
      'GB0002634947' (check digit 7 instead of 6) must be invalid.
      """
      assert not isin("GB0002634947")
  ```
- Status: confirmed
- Bug: isin-check-digit
- Review: same root cause as the first ISIN entry (#440); counted once.
