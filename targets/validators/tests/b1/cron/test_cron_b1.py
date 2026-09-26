"""Additional pytest tests for validators.cron (batch 1)."""

# external
import pytest

# local
from validators import ValidationError, cron


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _valid(value):
    """Assert that cron() returns truthy for value."""
    result = cron(value)
    assert result, f"Expected valid for {value!r}, got {result!r}"


def _invalid(value):
    """Assert that cron() returns a ValidationError for value."""
    result = cron(value)
    assert isinstance(result, ValidationError), (
        f"Expected ValidationError for {value!r}, got {result!r}"
    )


# ---------------------------------------------------------------------------
# Docstring examples
# ---------------------------------------------------------------------------

class TestDocstringExamples:
    """Docstring examples taken verbatim from the cron() docstring."""

    def test_every_five_minutes(self):
        """Docstring: cron"""
        _valid("*/5 * * * *")

    def test_invalid_range_30_20(self):
        """Docstring: cron"""
        _invalid("30-20 * * * *")


# ---------------------------------------------------------------------------
# Wildcard (*)
# ---------------------------------------------------------------------------

class TestWildcard:
    """All-wildcard and single-field wildcard expressions."""

    def test_all_wildcards(self):
        """Docstring: cron"""
        _valid("* * * * *")

    def test_wildcard_minute_only(self):
        """Docstring: cron"""
        _valid("* 0 1 1 0")

    def test_wildcard_hour_only(self):
        """Docstring: cron"""
        _valid("0 * 1 1 0")

    def test_wildcard_day_only(self):
        """Docstring: cron"""
        _valid("0 0 * 1 0")

    def test_wildcard_month_only(self):
        """Docstring: cron"""
        _valid("0 0 1 * 0")

    def test_wildcard_weekday_only(self):
        """Docstring: cron"""
        _valid("0 0 1 1 *")


# ---------------------------------------------------------------------------
# Plain decimal values — boundary testing for every field
# ---------------------------------------------------------------------------

class TestDecimalBoundaries:
    """Boundary values for each cron field."""

    # minutes: 0-59
    @pytest.mark.parametrize("minute", ["0", "59"])
    def test_minute_boundaries_valid(self, minute):
        """Docstring: cron"""
        _valid(f"{minute} * * * *")

    @pytest.mark.parametrize("minute", ["60", "100"])
    def test_minute_above_max_invalid(self, minute):
        """Docstring: cron"""
        _invalid(f"{minute} * * * *")

    # hours: 0-23
    @pytest.mark.parametrize("hour", ["0", "23"])
    def test_hour_boundaries_valid(self, hour):
        """Docstring: cron"""
        _valid(f"* {hour} * * *")

    @pytest.mark.parametrize("hour", ["24", "99"])
    def test_hour_above_max_invalid(self, hour):
        """Docstring: cron"""
        _invalid(f"* {hour} * * *")

    # days: 1-31
    @pytest.mark.parametrize("day", ["1", "31"])
    def test_day_boundaries_valid(self, day):
        """Docstring: cron"""
        _valid(f"* * {day} * *")

    def test_day_zero_invalid(self):
        """Docstring: cron"""
        _invalid("* * 0 * *")

    def test_day_above_max_invalid(self):
        """Docstring: cron"""
        _invalid("* * 32 * *")

    # months: 1-12
    @pytest.mark.parametrize("month", ["1", "12"])
    def test_month_boundaries_valid(self, month):
        """Docstring: cron"""
        _valid(f"* * * {month} *")

    def test_month_zero_invalid(self):
        """Docstring: cron"""
        _invalid("* * * 0 *")

    def test_month_above_max_invalid(self):
        """Docstring: cron"""
        _invalid("* * * 13 *")

    # weekdays: 0-6
    @pytest.mark.parametrize("wd", ["0", "6"])
    def test_weekday_boundaries_valid(self, wd):
        """Docstring: cron"""
        _valid(f"* * * * {wd}")

    def test_weekday_above_max_invalid(self):
        """Docstring: cron"""
        _invalid("* * * * 7")


# ---------------------------------------------------------------------------
# Step expressions (/)
# ---------------------------------------------------------------------------

class TestStepExpressions:
    """Slash / step expressions."""

    @pytest.mark.parametrize("expr", [
        "*/5 * * * *",
        "*/1 * * * *",
        "*/59 * * * *",
        "0/5 * * * *",     # base/step
        "* */2 * * *",
        "* * */3 * *",
        "* * * */4 *",
        "* * * * */2",
    ])
    def test_valid_step_expressions(self, expr):
        """Docstring: cron"""
        _valid(expr)

    @pytest.mark.parametrize("expr", [
        "*/0 * * * *",      # step of 0 is invalid
        "*/ * * * *",       # empty step
        "/5 * * * *",       # missing base
        "*/5/2 * * * *",    # too many slashes
        "60/5 * * * *",     # base out of range for minutes
    ])
    def test_invalid_step_expressions(self, expr):
        """Docstring: cron"""
        _invalid(expr)


# ---------------------------------------------------------------------------
# Range expressions (-)
# ---------------------------------------------------------------------------

class TestRangeExpressions:
    """Hyphen range expressions."""

    @pytest.mark.parametrize("expr", [
        "0-59 * * * *",
        "0-0 * * * *",     # single-value range
        "* 0-23 * * *",
        "* * 1-31 * *",
        "* * * 1-12 *",
        "* * * * 0-6",
        "10-20 * * * *",
    ])
    def test_valid_range_expressions(self, expr):
        """Docstring: cron"""
        _valid(expr)

    @pytest.mark.parametrize("expr", [
        "30-20 * * * *",    # start > end
        "0-60 * * * *",     # end out of range for minutes
        "* 0-24 * * *",     # end out of range for hours
        "* * 0-31 * *",     # start out of range for days (0 < min 1)
        "* * * 0-12 *",     # start out of range for months (0 < min 1)
        "* * * * 0-7",      # end out of range for weekdays
        "5- * * * *",       # missing end
        "-5 * * * *",       # missing start
        "a-b * * * *",      # non-decimal
    ])
    def test_invalid_range_expressions(self, expr):
        """Docstring: cron"""
        _invalid(expr)


# ---------------------------------------------------------------------------
# List expressions (,)
# ---------------------------------------------------------------------------

class TestListExpressions:
    """Comma list expressions."""

    @pytest.mark.parametrize("expr", [
        "0,30 * * * *",
        "1,15,45 * * * *",
        "* 0,12 * * *",
        "* * 1,15,31 * *",
        "* * * 1,6,12 *",
        "* * * * 0,3,6",
    ])
    def test_valid_list_expressions(self, expr):
        """Docstring: cron"""
        _valid(expr)

    @pytest.mark.parametrize("expr", [
        "0,60 * * * *",     # 60 out of range for minutes
        "* 0,24 * * *",     # 24 out of range for hours
        "* * 0,15 * *",     # 0 out of range for days
        "* * * 0,6 *",      # 0 out of range for months
        "* * * * 0,7",      # 7 out of range for weekdays
        ",5 * * * *",       # leading comma (empty first item)
        "5, * * * *",       # trailing comma (empty last item)
    ])
    def test_invalid_list_expressions(self, expr):
        """Docstring: cron"""
        _invalid(expr)


# ---------------------------------------------------------------------------
# Empty / malformed overall string
# ---------------------------------------------------------------------------

class TestMalformedString:
    """Strings that are not well-formed five-field cron expressions."""

    def test_empty_string_invalid(self):
        """Docstring: cron"""
        _invalid("")

    @pytest.mark.parametrize("expr", [
        "* * * *",          # only 4 fields
        "* * * * * *",      # 6 fields
        "* * *",            # 3 fields
        "*",                # 1 field
    ])
    def test_wrong_field_count_is_invalid(self, expr):
        """Docstring: cron"""
        _invalid(expr)

    def test_whitespace_only_invalid(self):
        """Docstring: cron"""
        _invalid("     ")

    def test_leading_trailing_whitespace_valid(self):
        """Docstring: cron — value.strip() is applied before splitting"""
        _valid("  * * * * *  ")


# ---------------------------------------------------------------------------
# Typical real-world expressions
# ---------------------------------------------------------------------------

class TestRealWorldExpressions:
    """Common real-world cron schedule strings."""

    @pytest.mark.parametrize("expr", [
        "0 0 * * *",         # daily midnight
        "0 12 * * 1",        # every Monday noon
        "30 4 1,15 * 5",     # 4:30 on 1st, 15th, and Fridays
        "0 */6 * * *",       # every 6 hours
        "5 4 * * 0",         # Sunday 4:05
        "0 0 1 1 *",         # yearly on Jan 1
        "59 23 31 12 *",     # last minute of the year
        "0 0 * * 1-5",       # weekdays midnight
        "0 9-17 * * 1-5",    # business hours weekdays
    ])
    def test_valid_real_world(self, expr):
        """Docstring: cron"""
        _valid(expr)
