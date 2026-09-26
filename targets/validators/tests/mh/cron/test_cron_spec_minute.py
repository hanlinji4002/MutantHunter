"""Spec-based tests for cron minute-field range (0–59)."""

from validators import cron


# ── valid boundary values ──────────────────────────────────────────────────

def test_minute_zero_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R2

    Minute value 0 (lower bound) must be valid.
    """
    assert cron("0 * * * *")


def test_minute_59_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R2

    Minute value 59 (upper bound) must be valid.
    """
    assert cron("59 * * * *")


def test_minute_30_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R2

    A mid-range minute value (30) must be valid.
    """
    assert cron("30 * * * *")


# ── invalid values ─────────────────────────────────────────────────────────

def test_minute_60_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R13

    Minute value 60 is one past the upper bound and must be invalid.
    """
    assert not cron("60 * * * *")


def test_minute_negative_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R15

    A negative minute value is not in the allowed set and must be invalid.
    """
    assert not cron("-1 * * * *")


# ── wildcard in minute field ───────────────────────────────────────────────

def test_minute_wildcard_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R7

    '*' in the minute field is always valid.
    """
    assert cron("* * * * *")


# ── step values in minute field ────────────────────────────────────────────

def test_minute_step_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R10

    '*/5' means every 5 minutes and must be valid.
    """
    assert cron("*/5 * * * *")


def test_minute_step_1_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R10

    '*/1' (step of 1) is a valid step value.
    """
    assert cron("*/1 * * * *")


def test_minute_step_zero_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R10

    '*/0' has a step of zero which is invalid per spec (step must be >= 1).
    """
    assert not cron("*/0 * * * *")


# ── range in minute field ──────────────────────────────────────────────────

def test_minute_range_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R9

    '0-30' is a valid minute range (start <= end, both in bounds).
    """
    assert cron("0-30 * * * *")


def test_minute_range_boundary_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R9

    '0-59' spans the full minute range and must be valid.
    """
    assert cron("0-59 * * * *")


def test_minute_range_inverted_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R9

    '30-20' has start > end and must be invalid.
    """
    assert not cron("30-20 * * * *")


def test_minute_range_out_of_bounds_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R13

    '0-60' has an end value of 60 which is out of range and must be invalid.
    """
    assert not cron("0-60 * * * *")


# ── comma list in minute field ─────────────────────────────────────────────

def test_minute_list_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R8

    '0,15,30,45' is a valid comma-separated list of minutes.
    """
    assert cron("0,15,30,45 * * * *")


def test_minute_list_out_of_bounds_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R8

    '0,60' has an out-of-range item and must be invalid.
    """
    assert not cron("0,60 * * * *")
