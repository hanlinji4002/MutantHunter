"""Spec-based tests for cron day-of-week field range (0–6)."""

from validators import cron


# ── valid boundary values ──────────────────────────────────────────────────

def test_dow_0_valid():
    """Spec: wiki-Cron.pdf Overview — R6

    Day-of-week value 0 (Sunday, lower bound) must be valid.
    """
    assert cron("0 0 * * 0")


def test_dow_6_valid():
    """Spec: wiki-Cron.pdf Overview — R6

    Day-of-week value 6 (Saturday, upper bound) must be valid.
    """
    assert cron("0 0 * * 6")


def test_dow_3_valid():
    """Spec: wiki-Cron.pdf Overview — R6

    A mid-range day-of-week value (3 = Wednesday) must be valid.
    """
    assert cron("0 0 * * 3")


# ── invalid values ─────────────────────────────────────────────────────────

def test_dow_7_invalid():
    """Spec: wiki-Cron.pdf Overview — R6

    Day-of-week value 7 is outside the standard 0–6 range and must be invalid.
    The spec states '0–6 (Sunday to Saturday)'; 7 is non-standard.
    """
    assert not cron("0 0 * * 7")


def test_dow_8_invalid():
    """Spec: wiki-Cron.pdf Overview — R13

    Day-of-week value 8 is well beyond the upper bound and must be invalid.
    """
    assert not cron("0 0 * * 8")


# ── wildcard ───────────────────────────────────────────────────────────────

def test_dow_wildcard_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R7

    '*' in the day-of-week field is always valid.
    """
    assert cron("0 0 * * *")


# ── step values ────────────────────────────────────────────────────────────

def test_dow_step_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R10

    '*/2' in the day-of-week field means every other weekday and must be valid.
    """
    assert cron("0 0 * * */2")


# ── range ──────────────────────────────────────────────────────────────────

def test_dow_range_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R9

    '1-5' means Monday to Friday and must be valid.
    """
    assert cron("30 3 * * 1-5")


def test_dow_range_full_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R9

    '0-6' spans the full day-of-week range and must be valid.
    """
    assert cron("0 0 * * 0-6")


def test_dow_range_inverted_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R9

    '6-0' has start > end and must be invalid.
    """
    assert not cron("0 0 * * 6-0")


def test_dow_range_out_of_bounds_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R13

    '0-7' has an end value of 7 which is out of the standard range.
    """
    assert not cron("0 0 * * 0-7")


# ── comma list ─────────────────────────────────────────────────────────────

def test_dow_list_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R8

    '1,3,5' (Mon, Wed, Fri) is a valid comma-separated list.
    """
    assert cron("15 5 * * 1,3,5")


def test_dow_list_out_of_bounds_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R8

    '1,3,7' includes day 7 which is out of range and must be invalid.
    """
    assert not cron("0 0 * * 1,3,7")
