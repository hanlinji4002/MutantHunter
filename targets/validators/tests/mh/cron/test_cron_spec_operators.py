"""Spec-based tests for cron special-character operators (*, , - /)."""

from validators import cron


# ── wildcard * ────────────────────────────────────────────────────────────

def test_wildcard_in_all_fields_valid():
    """Spec: wiki-Cron.pdf Cron-expression Asterisk — R7

    '* * * * *' with wildcards in all five fields must be valid.
    """
    assert cron("* * * * *")


def test_wildcard_in_minute_valid():
    """Spec: wiki-Cron.pdf Cron-expression Asterisk — R7

    '*' is valid in the minute field.
    """
    assert cron("* 0 1 1 0")


def test_wildcard_in_hour_valid():
    """Spec: wiki-Cron.pdf Cron-expression Asterisk — R7

    '*' is valid in the hour field.
    """
    assert cron("0 * 1 1 0")


def test_wildcard_in_dom_valid():
    """Spec: wiki-Cron.pdf Cron-expression Asterisk — R7

    '*' is valid in the day-of-month field.
    """
    assert cron("0 0 * 1 0")


def test_wildcard_in_month_valid():
    """Spec: wiki-Cron.pdf Cron-expression Asterisk — R7

    '*' is valid in the month field.
    """
    assert cron("0 0 1 * 0")


def test_wildcard_in_dow_valid():
    """Spec: wiki-Cron.pdf Cron-expression Asterisk — R7

    '*' is valid in the day-of-week field.
    """
    assert cron("0 0 1 1 *")


# ── comma , ───────────────────────────────────────────────────────────────

def test_comma_list_minutes_valid():
    """Spec: wiki-Cron.pdf Cron-expression Comma — R8

    Comma separates valid list items; '0,15,30,45' must be valid for minutes.
    """
    assert cron("0,15,30,45 * * * *")


def test_comma_list_hours_spec_example_valid():
    """Spec: wiki-Cron.pdf Overview — R8

    The spec example '*/5 1,2,3 * * *' (echo hello world) must be valid.
    """
    assert cron("*/5 1,2,3 * * *")


def test_comma_list_dow_valid():
    """Spec: wiki-Cron.pdf Cron-expression Comma — R8

    'MON,WED,FRI' equivalent as numbers '1,3,5' must be valid in day-of-week.
    """
    assert cron("0 0 * * 1,3,5")


def test_comma_list_invalid_item_invalid():
    """Spec: wiki-Cron.pdf Cron-expression Comma — R8

    Each comma list item must be individually valid; an out-of-range item
    makes the whole field invalid.
    """
    assert not cron("0,60 * * * *")


# ── hyphen - ──────────────────────────────────────────────────────────────

def test_hyphen_range_valid():
    """Spec: wiki-Cron.pdf Cron-expression Hyphen — R9

    '2000-2010' style inclusive range; for minutes '10-20' must be valid.
    """
    assert cron("10-20 * * * *")


def test_hyphen_range_same_start_end_valid():
    """Spec: wiki-Cron.pdf Cron-expression Hyphen — R9

    A range where start == end is degenerate but valid (start <= end holds).
    """
    assert cron("5-5 * * * *")


def test_hyphen_range_inverted_invalid():
    """Spec: wiki-Cron.pdf Cron-expression Hyphen — R9

    The docstring example '30-20' (start > end) must be invalid.
    """
    assert not cron("30-20 * * * *")


def test_hyphen_range_out_of_bounds_start_invalid():
    """Spec: wiki-Cron.pdf Cron-expression Hyphen — R9

    A range whose start is out of the field's allowed range must be invalid.
    """
    assert not cron("60-70 * * * *")


def test_hyphen_range_out_of_bounds_end_invalid():
    """Spec: wiki-Cron.pdf Cron-expression Hyphen — R9

    A range whose end is out of the field's allowed range must be invalid.
    """
    assert not cron("0-60 * * * *")


def test_hyphen_with_wildcard_start_invalid():
    """Spec: wiki-Cron.pdf Cron-expression Hyphen — R9

    '10-*' mixes wildcard and hyphen which is not a valid range syntax.
    """
    assert not cron("10-* * * * *")


# ── slash / ───────────────────────────────────────────────────────────────

def test_slash_wildcard_step_valid():
    """Spec: wiki-Cron.pdf Cron-expression Slash — R10

    '*/5' in the minutes field is valid (every 5 minutes).
    """
    assert cron("*/5 * * * *")


def test_slash_wildcard_step_15_valid():
    """Spec: wiki-Cron.pdf Cron-expression Slash — R10

    '*/15' in the minutes field must be valid.
    """
    assert cron("*/15 * * * *")


def test_slash_start_step_valid():
    """Spec: wiki-Cron.pdf Cron-expression Slash — R10

    'start/n' where start is in range and n >= 1 must be valid.
    '0/5' in the minutes field must be valid.
    """
    assert cron("0/5 * * * *")


def test_slash_step_zero_invalid():
    """Spec: wiki-Cron.pdf Cron-expression Slash — R10

    A step value of 0 ('*/0') is invalid; step must be >= 1.
    """
    assert not cron("*/0 * * * *")


def test_slash_start_out_of_range_invalid():
    """Spec: wiki-Cron.pdf Cron-expression Slash — R10

    'start/n' where start is outside the field range is invalid.
    '60/5' has start=60 which is out of range for minutes.
    """
    assert not cron("60/5 * * * *")


# ── non-standard characters ────────────────────────────────────────────────

def test_non_standard_char_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R15

    '&' is not an allowed character in standard 5-field cron and must be
    invalid.
    """
    assert not cron("& * * * *")


def test_letter_char_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R15

    Alphabetic characters (e.g. 'A') are not allowed in standard 5-field
    Vixie cron fields.
    """
    assert not cron("A * * * *")
