"""Spec-based tests for cron expression field-count (structure) rules."""

from validators import cron


def test_five_fields_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R1

    A five-field expression is valid.
    """
    assert cron("* * * * *")


def test_six_fields_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R1

    Six fields must be rejected (standard 5-field Vixie cron).
    """
    assert not cron("* * * * * *")


def test_four_fields_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R1

    Four fields must be rejected.
    """
    assert not cron("* * * *")


def test_three_fields_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R1

    Three fields must be rejected.
    """
    assert not cron("* * *")


def test_one_field_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R1

    A single field must be rejected.
    """
    assert not cron("*")


def test_empty_string_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R11

    An empty string is not a valid cron expression.
    """
    assert not cron("")


def test_all_wildcards_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R14

    '* * * * *' means every minute and must be valid.
    """
    assert cron("* * * * *")
