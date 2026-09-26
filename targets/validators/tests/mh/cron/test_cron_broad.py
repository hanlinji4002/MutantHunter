"""Broad regression tests for the cron validator."""

import validators


# ---------------------------------------------------------------------------
# Valid expressions — wildcard
# ---------------------------------------------------------------------------

def test_all_wildcards():
    """Docstring: cron — five wildcard fields are valid."""
    assert validators.cron("* * * * *")


def test_leading_trailing_spaces_ignored():
    """Docstring: cron — surrounding whitespace is stripped before parsing."""
    assert validators.cron("  * * * * *  ")


# ---------------------------------------------------------------------------
# Valid expressions — minute field (0–59)
# ---------------------------------------------------------------------------

def test_minute_min_boundary():
    """Docstring: cron — minute value 0 is the lower boundary."""
    assert validators.cron("0 * * * *")


def test_minute_max_boundary():
    """Docstring: cron — minute value 59 is the upper boundary."""
    assert validators.cron("59 * * * *")


def test_minute_step():
    """Docstring: cron — */5 step notation in minute field is valid."""
    assert validators.cron("*/5 * * * *")


def test_minute_step_1():
    """Docstring: cron — */1 step notation in minute field is valid."""
    assert validators.cron("*/1 * * * *")


def test_minute_range():
    """Docstring: cron — range 10-30 in minute field is valid."""
    assert validators.cron("10-30 * * * *")


def test_minute_range_same():
    """Docstring: cron — range with equal start and end in minute field is valid."""
    assert validators.cron("5-5 * * * *")


def test_minute_list():
    """Docstring: cron — comma-separated list in minute field is valid."""
    assert validators.cron("0,15,30,45 * * * *")


def test_minute_step_with_base():
    """Docstring: cron — base/step form like 5/10 in minute field is valid."""
    assert validators.cron("5/10 * * * *")


# ---------------------------------------------------------------------------
# Invalid expressions — minute field
# ---------------------------------------------------------------------------

def test_minute_too_large():
    """Docstring: cron — minute value 60 exceeds maximum of 59."""
    assert not validators.cron("60 * * * *")


def test_minute_negative():
    """Docstring: cron — negative minute value is invalid."""
    assert not validators.cron("-1 * * * *")


def test_minute_step_zero():
    """Docstring: cron — step value of 0 (*/0) is invalid."""
    assert not validators.cron("*/0 * * * *")


def test_minute_range_inverted():
    """Docstring: cron — inverted range (start > end) is invalid."""
    assert not validators.cron("30-20 * * * *")


def test_minute_range_end_out_of_bounds():
    """Docstring: cron — range end exceeding max (0-60) is invalid."""
    assert not validators.cron("0-60 * * * *")


def test_minute_range_start_out_of_bounds():
    """Docstring: cron — range start below min (-1-10) is invalid."""
    assert not validators.cron("-1-10 * * * *")


# ---------------------------------------------------------------------------
# Valid expressions — hour field (0–23)
# ---------------------------------------------------------------------------

def test_hour_min_boundary():
    """Docstring: cron — hour value 0 is the lower boundary."""
    assert validators.cron("* 0 * * *")


def test_hour_max_boundary():
    """Docstring: cron — hour value 23 is the upper boundary."""
    assert validators.cron("* 23 * * *")


def test_hour_step():
    """Docstring: cron — */3 step notation in hour field is valid."""
    assert validators.cron("* */3 * * *")


def test_hour_range():
    """Docstring: cron — range 3-6 in hour field is valid."""
    assert validators.cron("0 3-6 * * *")


def test_hour_list():
    """Docstring: cron — comma-separated list 0,6,12,18 in hour field is valid."""
    assert validators.cron("0 0,6,12,18 * * *")


# ---------------------------------------------------------------------------
# Invalid expressions — hour field
# ---------------------------------------------------------------------------

def test_hour_too_large():
    """Docstring: cron — hour value 24 exceeds maximum of 23."""
    assert not validators.cron("* 24 * * *")


def test_hour_step_zero():
    """Docstring: cron — step value of 0 (*/0) in hour field is invalid."""
    assert not validators.cron("* */0 * * *")


def test_hour_list_out_of_bounds():
    """Docstring: cron — list containing 24 in hour field is invalid."""
    assert not validators.cron("*/15 0,6,12,24 * * *")


# ---------------------------------------------------------------------------
# Valid expressions — day-of-month field (1–31)
# ---------------------------------------------------------------------------

def test_dom_min_boundary():
    """Docstring: cron — day-of-month value 1 is the lower boundary."""
    assert validators.cron("* * 1 * *")


def test_dom_max_boundary():
    """Docstring: cron — day-of-month value 31 is the upper boundary."""
    assert validators.cron("* * 31 * *")


def test_dom_step():
    """Docstring: cron — */2 step notation in day-of-month field is valid."""
    assert validators.cron("0 12 */2 * *")


def test_dom_range():
    """Docstring: cron — range 1-15 in day-of-month field is valid."""
    assert validators.cron("* * 1-15 * *")


def test_dom_list():
    """Docstring: cron — comma-separated list 1,15,28 in day-of-month field is valid."""
    assert validators.cron("* * 1,15,28 * *")


# ---------------------------------------------------------------------------
# Invalid expressions — day-of-month field
# ---------------------------------------------------------------------------

def test_dom_zero():
    """Docstring: cron — day-of-month value 0 is below minimum of 1."""
    assert not validators.cron("* * 0 * *")


def test_dom_too_large():
    """Docstring: cron — day-of-month value 32 exceeds maximum of 31."""
    assert not validators.cron("0 12 32 * *")


# ---------------------------------------------------------------------------
# Valid expressions — month field (1–12)
# ---------------------------------------------------------------------------

def test_month_min_boundary():
    """Docstring: cron — month value 1 is the lower boundary."""
    assert validators.cron("* * * 1 *")


def test_month_max_boundary():
    """Docstring: cron — month value 12 is the upper boundary."""
    assert validators.cron("* * * 12 *")


def test_month_step():
    """Docstring: cron — */2 step notation in month field is valid."""
    assert validators.cron("0 12 1 */2 *")


def test_month_range():
    """Docstring: cron — range 1-6 in month field is valid."""
    assert validators.cron("0 12 * 1-6 *")


# ---------------------------------------------------------------------------
# Invalid expressions — month field
# ---------------------------------------------------------------------------

def test_month_zero():
    """Docstring: cron — month value 0 is below minimum of 1."""
    assert not validators.cron("* * * 0 *")


def test_month_too_large():
    """Docstring: cron — month value 13 exceeds maximum of 12."""
    assert not validators.cron("* * * 13 *")


# ---------------------------------------------------------------------------
# Valid expressions — day-of-week field (0–6)
# ---------------------------------------------------------------------------

def test_dow_min_boundary():
    """Docstring: cron — day-of-week value 0 (Sunday) is the lower boundary."""
    assert validators.cron("* * * * 0")


def test_dow_max_boundary():
    """Docstring: cron — day-of-week value 6 (Saturday) is the upper boundary."""
    assert validators.cron("* * * * 6")


def test_dow_range():
    """Docstring: cron — range 1-5 (Monday–Friday) in day-of-week field is valid."""
    assert validators.cron("30 3 * * 1-5")


def test_dow_list():
    """Docstring: cron — comma-separated list 1,3,5 in day-of-week field is valid."""
    assert validators.cron("15 5 * * 1,3,5")


def test_dow_step():
    """Docstring: cron — */2 step notation in day-of-week field is valid."""
    assert validators.cron("* * * * */2")


# ---------------------------------------------------------------------------
# Invalid expressions — day-of-week field
# ---------------------------------------------------------------------------

def test_dow_too_large():
    """Docstring: cron — day-of-week value 8 exceeds maximum of 6."""
    assert not validators.cron("0 12 * * 8")


def test_dow_negative():
    """Docstring: cron — negative day-of-week value is invalid."""
    assert not validators.cron("* * * * -1")


# ---------------------------------------------------------------------------
# Wrong number of fields
# ---------------------------------------------------------------------------

def test_too_many_fields():
    """Docstring: cron — six fields is not a valid standard five-field expression."""
    assert not validators.cron("* * * * * *")


def test_too_few_fields():
    """Docstring: cron — four fields is not a valid standard five-field expression."""
    assert not validators.cron("* * * *")


# ---------------------------------------------------------------------------
# Empty / blank input
# ---------------------------------------------------------------------------

def test_empty_string():
    """Docstring: cron — empty string is invalid."""
    assert not validators.cron("")


# ---------------------------------------------------------------------------
# Step with explicit start (base/step)
# ---------------------------------------------------------------------------

def test_minute_step_explicit_start_valid():
    """Docstring: cron — step expression with valid base 10/5 is valid."""
    assert validators.cron("10/5 * * * *")


def test_hour_step_explicit_start_valid():
    """Docstring: cron — step expression with valid base 6/6 in hour field is valid."""
    assert validators.cron("* 6/6 * * *")


def test_minute_step_invalid_base():
    """Docstring: cron — step expression with base outside range (70/5) is invalid."""
    assert not validators.cron("70/5 * * * *")


# ---------------------------------------------------------------------------
# Combined real-world expressions
# ---------------------------------------------------------------------------

def test_at_midnight():
    """Docstring: cron — '0 0 * * *' represents daily midnight run."""
    assert validators.cron("0 0 * * *")


def test_every_saturday_11_45pm():
    """Docstring: cron — '45 23 * * 6' represents 23:45 every Saturday."""
    assert validators.cron("45 23 * * 6")


def test_first_day_of_month_noon():
    """Docstring: cron — '0 12 1 * *' represents noon on the first of every month."""
    assert validators.cron("0 12 1 * *")


def test_monday_to_friday_3am():
    """Docstring: cron — '0 3 * * 1-5' represents 3am Monday through Friday."""
    assert validators.cron("0 3 * * 1-5")


def test_every_5min_three_hours():
    """Docstring: cron — '*/5 1,2,3 * * *' from spec example is valid."""
    assert validators.cron("*/5 1,2,3 * * *")


def test_list_and_step_combined():
    """Docstring: cron — '*/15 0,6,12,18 * * *' uses step and list together."""
    assert validators.cron("*/15 0,6,12,18 * * *")


# ---------------------------------------------------------------------------
# Slash without proper second part
# ---------------------------------------------------------------------------

def test_slash_no_step():
    """Docstring: cron — '*/' with empty step is invalid."""
    assert not validators.cron("*/ * * * *")


def test_slash_alpha_step():
    """Docstring: cron — '*/x' with non-numeric step is invalid."""
    assert not validators.cron("*/x * * * *")


# ---------------------------------------------------------------------------
# Hyphen edge cases
# ---------------------------------------------------------------------------

def test_range_alpha():
    """Docstring: cron — 'a-b' range with non-numeric values is invalid."""
    assert not validators.cron("a-b * * * *")


def test_range_wildcard_right():
    """Docstring: cron — '10-*' range is invalid."""
    assert not validators.cron("10-* * * * *")


# ---------------------------------------------------------------------------
# Extra special characters
# ---------------------------------------------------------------------------

def test_invalid_special_char_ampersand():
    """Docstring: cron — '&' is not a valid cron character."""
    assert not validators.cron("& * * & * *")


def test_invalid_dash_alone():
    """Docstring: cron — standalone '-' field is invalid."""
    assert not validators.cron("* - * * - *")
