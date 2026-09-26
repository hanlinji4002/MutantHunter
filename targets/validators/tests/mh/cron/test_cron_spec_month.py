"""Spec-based tests for cron month field range (1–12)."""

from validators import cron


# ── valid boundary values ──────────────────────────────────────────────────

def test_month_1_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R5

    Month value 1 (January, lower bound) must be valid.
    """
    assert cron("0 0 1 1 *")


def test_month_12_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R5

    Month value 12 (December, upper bound) must be valid.
    """
    assert cron("0 0 1 12 *")


def test_month_6_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R5

    A mid-range month value (6) must be valid.
    """
    assert cron("0 0 1 6 *")


# ── invalid values ─────────────────────────────────────────────────────────

def test_month_zero_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R13

    Month value 0 is below the lower bound and must be invalid.
    """
    assert not cron("0 0 1 0 *")


def test_month_13_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R13

    Month value 13 is one past the upper bound and must be invalid.
    """
    assert not cron("0 0 1 13 *")


# ── wildcard ───────────────────────────────────────────────────────────────

def test_month_wildcard_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R7

    '*' in the month field is always valid.
    """
    assert cron("0 0 1 * *")


# ── step values ────────────────────────────────────────────────────────────

def test_month_step_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R10

    '*/2' in the month field means every other month and must be valid.
    """
    assert cron("0 0 1 */2 *")


# ── range ──────────────────────────────────────────────────────────────────

def test_month_range_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R9

    '1-6' is a valid month range (January to June).
    """
    assert cron("0 0 * 1-6 *")


def test_month_range_full_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R9

    '1-12' spans the full month range and must be valid.
    """
    assert cron("0 0 * 1-12 *")


def test_month_range_inverted_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R9

    '12-1' has start > end and must be invalid.
    """
    assert not cron("0 0 * 12-1 *")


def test_month_range_out_of_bounds_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R13

    '1-13' has an end value out of range and must be invalid.
    """
    assert not cron("0 0 * 1-13 *")


def test_month_range_start_zero_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R13

    '0-6' starts at 0 which is below the lower bound and must be invalid.
    """
    assert not cron("0 0 * 0-6 *")


# ── comma list ─────────────────────────────────────────────────────────────

def test_month_list_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R8

    '1,6,12' is a valid comma list of months.
    """
    assert cron("0 0 * 1,6,12 *")


def test_month_list_zero_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R8

    '0,6' includes month 0 which is out of range and must be invalid.
    """
    assert not cron("0 0 * 0,6 *")
