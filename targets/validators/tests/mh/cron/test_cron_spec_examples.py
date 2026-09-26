"""Spec-based tests derived from concrete examples in wiki-Cron.pdf."""

from validators import cron


def test_spec_example_every_minute():
    """Spec: wiki-Cron.pdf Cron-expression Asterisk — R16

    '* * * * *' runs every minute (spec wildcard example).
    """
    assert cron("* * * * *")


def test_spec_example_clear_apache_log():
    """Spec: wiki-Cron.pdf Overview — R16

    '1 0 * * *' — at one minute past midnight every day (spec example).
    """
    assert cron("1 0 * * *")


def test_spec_example_export_dump():
    """Spec: wiki-Cron.pdf Overview — R16

    '45 23 * * 6' — at 23:45 every Saturday (spec example).
    """
    assert cron("45 23 * * 6")


def test_spec_example_echo_hello_world():
    """Spec: wiki-Cron.pdf Overview — R16

    '*/5 1,2,3 * * *' — every 5th minute of hours 1, 2, 3 (spec example).
    """
    assert cron("*/5 1,2,3 * * *")


def test_spec_example_every_5_minutes():
    """Spec: wiki-Cron.pdf Cron-expression Slash — R10, R16

    '*/5 * * * *' — every 5 minutes (docstring and spec example).
    """
    assert cron("*/5 * * * *")


def test_spec_example_range_inverted_invalid():
    """Spec: wiki-Cron.pdf Cron-expression Hyphen — R9, R16

    '30-20 * * * *' — docstring explicitly marks this as invalid
    (ValidationError).
    """
    assert not cron("30-20 * * * *")


def test_spec_example_midnight_daily():
    """Spec: wiki-Cron.pdf Nonstandard-predefined Scheduling — R16

    '@daily' is equivalent to '0 0 * * *'; that literal expression must be
    valid.
    """
    assert cron("0 0 * * *")


def test_spec_example_midnight_1st_of_month():
    """Spec: wiki-Cron.pdf Nonstandard-predefined Scheduling — R16

    '@monthly' equivalent '0 0 1 * *' must be valid.
    """
    assert cron("0 0 1 * *")


def test_spec_example_midnight_sunday():
    """Spec: wiki-Cron.pdf Nonstandard-predefined Scheduling — R16

    '@weekly' equivalent '0 0 * * 0' must be valid.
    """
    assert cron("0 0 * * 0")


def test_spec_example_top_of_every_hour():
    """Spec: wiki-Cron.pdf Nonstandard-predefined Scheduling — R16

    '@hourly' equivalent '0 * * * *' must be valid.
    """
    assert cron("0 * * * *")


def test_spec_example_1_january_midnight():
    """Spec: wiki-Cron.pdf Nonstandard-predefined Scheduling — R16

    '@yearly' equivalent '0 0 1 1 *' must be valid.
    """
    assert cron("0 0 1 1 *")
