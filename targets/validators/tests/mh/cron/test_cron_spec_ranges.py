"""Spec-based tests for the cron validator — field ranges and allowed values.

Source: wiki-Cron.pdf (Wikipedia article on Cron).
"""

import validators


# ---------------------------------------------------------------------------
# R1 — Five-field structure
# ---------------------------------------------------------------------------

def test_exactly_five_fields_valid():
    """Spec: wiki-Cron.pdf §Cron expression — R1

    Five whitespace-separated fields constitute a valid standard expression.
    """
    assert validators.cron("* * * * *")


def test_six_fields_invalid():
    """Spec: wiki-Cron.pdf §Cron expression — R1

    Six fields are not a valid standard five-field cron expression.
    """
    assert not validators.cron("* * * * * *")


def test_four_fields_invalid():
    """Spec: wiki-Cron.pdf §Cron expression — R1

    Four fields are not a valid standard five-field cron expression.
    """
    assert not validators.cron("* * * *")


# ---------------------------------------------------------------------------
# R2 — Minute field: 0–59
# ---------------------------------------------------------------------------

def test_minute_boundary_low():
    """Spec: wiki-Cron.pdf §Cron expression table — R2

    Minute value 0 (lower boundary) is valid.
    """
    assert validators.cron("0 * * * *")


def test_minute_boundary_high():
    """Spec: wiki-Cron.pdf §Cron expression table — R2

    Minute value 59 (upper boundary) is valid.
    """
    assert validators.cron("59 * * * *")


def test_minute_above_max():
    """Spec: wiki-Cron.pdf §Cron expression table — R2

    Minute value 60 exceeds the maximum of 59 and is invalid.
    """
    assert not validators.cron("60 * * * *")


# ---------------------------------------------------------------------------
# R3 — Hour field: 0–23
# ---------------------------------------------------------------------------

def test_hour_boundary_low():
    """Spec: wiki-Cron.pdf §Cron expression table — R3

    Hour value 0 (lower boundary) is valid.
    """
    assert validators.cron("* 0 * * *")


def test_hour_boundary_high():
    """Spec: wiki-Cron.pdf §Cron expression table — R3

    Hour value 23 (upper boundary) is valid.
    """
    assert validators.cron("* 23 * * *")


def test_hour_above_max():
    """Spec: wiki-Cron.pdf §Cron expression table — R3

    Hour value 24 exceeds the maximum of 23 and is invalid.
    """
    assert not validators.cron("* 24 * * *")


# ---------------------------------------------------------------------------
# R4 — Day-of-month field: 1–31
# ---------------------------------------------------------------------------

def test_dom_boundary_low():
    """Spec: wiki-Cron.pdf §Cron expression table — R4

    Day-of-month value 1 (lower boundary) is valid.
    """
    assert validators.cron("* * 1 * *")


def test_dom_boundary_high():
    """Spec: wiki-Cron.pdf §Cron expression table — R4

    Day-of-month value 31 (upper boundary) is valid.
    """
    assert validators.cron("* * 31 * *")


def test_dom_zero():
    """Spec: wiki-Cron.pdf §Cron expression table — R4

    Day-of-month value 0 is below the minimum of 1 and is invalid.
    """
    assert not validators.cron("* * 0 * *")


def test_dom_above_max():
    """Spec: wiki-Cron.pdf §Cron expression table — R4

    Day-of-month value 32 exceeds the maximum of 31 and is invalid.
    """
    assert not validators.cron("0 12 32 * *")


# ---------------------------------------------------------------------------
# R5 — Month field: 1–12
# ---------------------------------------------------------------------------

def test_month_boundary_low():
    """Spec: wiki-Cron.pdf §Cron expression table — R5

    Month value 1 (lower boundary, January) is valid.
    """
    assert validators.cron("* * * 1 *")


def test_month_boundary_high():
    """Spec: wiki-Cron.pdf §Cron expression table — R5

    Month value 12 (upper boundary, December) is valid.
    """
    assert validators.cron("* * * 12 *")


def test_month_zero():
    """Spec: wiki-Cron.pdf §Cron expression table — R5

    Month value 0 is below the minimum of 1 and is invalid.
    """
    assert not validators.cron("* * * 0 *")


def test_month_above_max():
    """Spec: wiki-Cron.pdf §Cron expression table — R5

    Month value 13 exceeds the maximum of 12 and is invalid.
    """
    assert not validators.cron("* * * 13 *")


# ---------------------------------------------------------------------------
# R6 — Day-of-week field: 0–6
# ---------------------------------------------------------------------------

def test_dow_boundary_low():
    """Spec: wiki-Cron.pdf §Cron expression table / Overview — R6

    Day-of-week value 0 (Sunday, lower boundary) is valid.
    """
    assert validators.cron("* * * * 0")


def test_dow_boundary_high():
    """Spec: wiki-Cron.pdf §Cron expression table / Overview — R6

    Day-of-week value 6 (Saturday, upper boundary) is valid.
    """
    assert validators.cron("* * * * 6")


def test_dow_above_max():
    """Spec: wiki-Cron.pdf §Cron expression table / Overview — R6

    Day-of-week value 7 exceeds the maximum of 6 and is invalid.
    """
    assert not validators.cron("0 12 * * 7")


def test_dow_8_invalid():
    """Spec: wiki-Cron.pdf §Cron expression table / Overview — R6

    Day-of-week value 8 exceeds the maximum of 6 and is invalid.
    """
    assert not validators.cron("0 12 * * 8")


# ---------------------------------------------------------------------------
# R7 — Wildcard asterisk
# ---------------------------------------------------------------------------

def test_wildcard_in_every_field():
    """Spec: wiki-Cron.pdf §Asterisk — R7

    Five asterisks (wildcard in every field) is a valid expression meaning
    "every minute of every hour of every day".
    """
    assert validators.cron("* * * * *")


# ---------------------------------------------------------------------------
# R8 — Comma list
# ---------------------------------------------------------------------------

def test_comma_list_minutes():
    """Spec: wiki-Cron.pdf §Comma — R8

    A comma-separated list of valid minute values is valid.
    """
    assert validators.cron("0,15,30,45 * * * *")


def test_comma_list_hours():
    """Spec: wiki-Cron.pdf §Comma — R8

    Comma-separated hours 1,2,3 (from spec example) are valid.
    """
    assert validators.cron("*/5 1,2,3 * * *")


def test_comma_list_dow():
    """Spec: wiki-Cron.pdf §Comma — R8

    Comma list for day-of-week (MON,WED,FRI = 1,3,5) is valid.
    """
    assert validators.cron("15 5 * * 1,3,5")


def test_comma_list_out_of_range():
    """Spec: wiki-Cron.pdf §Comma — R8

    A comma list containing an out-of-range value (24 in hours) is invalid.
    """
    assert not validators.cron("*/15 0,6,12,24 * * *")


# ---------------------------------------------------------------------------
# R9 — Hyphen range
# ---------------------------------------------------------------------------

def test_range_valid_minutes():
    """Spec: wiki-Cron.pdf §Hyphen — R9

    An in-range hyphenated range (start ≤ end) in minutes is valid.
    """
    assert validators.cron("10-30 * * * *")


def test_range_start_greater_than_end():
    """Spec: wiki-Cron.pdf §Hyphen — R9

    A range where start > end (30-20) is invalid.
    """
    assert not validators.cron("30-20 * * * *")


def test_range_dow():
    """Spec: wiki-Cron.pdf §Hyphen — R9

    A valid day-of-week range (Monday–Friday: 1-5) is valid.
    """
    assert validators.cron("30 3 * * 1-5")


def test_range_months():
    """Spec: wiki-Cron.pdf §Hyphen — R9

    A valid month range (January–June: 1-6) is valid.
    """
    assert validators.cron("0 12 * 1-6 1-5")


# ---------------------------------------------------------------------------
# R10 — Slash step
# ---------------------------------------------------------------------------

def test_step_wildcard_minutes():
    """Spec: wiki-Cron.pdf §Slash — R10

    */5 in the minutes field (every 5 minutes) is valid.
    """
    assert validators.cron("*/5 * * * *")


def test_step_wildcard_month():
    """Spec: wiki-Cron.pdf §Slash — R10

    */2 step notation in the month field is valid.
    """
    assert validators.cron("0 12 1 */2 *")


def test_step_zero_invalid():
    """Spec: wiki-Cron.pdf §Slash — R10

    */0 (step of zero) is invalid; step must be ≥ 1.
    """
    assert not validators.cron("* */0 * * *")


# ---------------------------------------------------------------------------
# R15 — Spec example: */5 1,2,3 * * *
# ---------------------------------------------------------------------------

def test_spec_example_every5min_three_hours():
    """Spec: wiki-Cron.pdf §Overview — R15

    '*/5 1,2,3 * * *' is cited explicitly in the spec as valid.
    """
    assert validators.cron("*/5 1,2,3 * * *")


# ---------------------------------------------------------------------------
# R16 — Spec example: 1 0 * * *
# ---------------------------------------------------------------------------

def test_spec_example_one_minute_past_midnight():
    """Spec: wiki-Cron.pdf §Overview — R16

    '1 0 * * *' (one minute past midnight every day) is cited as valid.
    """
    assert validators.cron("1 0 * * *")


# ---------------------------------------------------------------------------
# R17 — Spec example: 45 23 * * 6
# ---------------------------------------------------------------------------

def test_spec_example_saturday_2345():
    """Spec: wiki-Cron.pdf §Overview — R17

    '45 23 * * 6' (23:45 every Saturday) is cited as valid.
    """
    assert validators.cron("45 23 * * 6")
