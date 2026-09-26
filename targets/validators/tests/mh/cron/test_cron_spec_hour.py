"""Spec-based tests for cron hour-field range (0–23)."""

from validators import cron


# ── valid boundary values ──────────────────────────────────────────────────

def test_hour_zero_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R3

    Hour value 0 (lower bound) must be valid.
    """
    assert cron("0 0 * * *")


def test_hour_23_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R3

    Hour value 23 (upper bound) must be valid.
    """
    assert cron("0 23 * * *")


def test_hour_12_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R3

    A mid-range hour value (12) must be valid.
    """
    assert cron("0 12 * * *")


# ── invalid values ─────────────────────────────────────────────────────────

def test_hour_24_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R13

    Hour value 24 is one past the upper bound and must be invalid.
    """
    assert not cron("0 24 * * *")


def test_hour_negative_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R15

    A negative hour representation is not in allowed range and must be invalid.
    """
    assert not cron("0 -1 * * *")


# ── wildcard ───────────────────────────────────────────────────────────────

def test_hour_wildcard_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R7

    '*' in the hour field is always valid.
    """
    assert cron("0 * * * *")


# ── step values ────────────────────────────────────────────────────────────

def test_hour_step_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R10

    '*/3' in the hour field means every 3 hours and must be valid.
    """
    assert cron("0 */3 * * *")


def test_hour_step_zero_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R10

    '*/0' in the hour field has a zero step which is invalid.
    """
    assert not cron("0 */0 * * *")


# ── range ──────────────────────────────────────────────────────────────────

def test_hour_range_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R9

    '0-23' is a valid hour range spanning the full range.
    """
    assert cron("0 0-23 * * *")


def test_hour_range_inverted_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R9

    '23-0' has start > end and must be invalid.
    """
    assert not cron("0 23-0 * * *")


def test_hour_range_out_of_bounds_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R13

    '0-24' has an end value of 24 which is out of range.
    """
    assert not cron("0 0-24 * * *")


# ── comma list ─────────────────────────────────────────────────────────────

def test_hour_list_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R8

    '1,2,3' is a valid comma-separated list from the spec example.
    (*/5 1,2,3 * * * — echo hello world)
    """
    assert cron("*/5 1,2,3 * * *")


def test_hour_list_out_of_bounds_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R8

    '0,6,12,24' has an out-of-range item (24) and must be invalid.
    """
    assert not cron("*/15 0,6,12,24 * * *")
