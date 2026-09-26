"""Spec-based tests for cron day-of-month field range (1–31)."""

from validators import cron


# ── valid boundary values ──────────────────────────────────────────────────

def test_dom_1_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R4

    Day-of-month value 1 (lower bound) must be valid.
    """
    assert cron("0 0 1 * *")


def test_dom_31_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R4

    Day-of-month value 31 (upper bound) must be valid.
    """
    assert cron("0 0 31 * *")


def test_dom_15_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R4

    A mid-range day-of-month value (15) must be valid.
    """
    assert cron("0 0 15 * *")


# ── invalid values ─────────────────────────────────────────────────────────

def test_dom_zero_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R13

    Day-of-month value 0 is below the lower bound and must be invalid.
    """
    assert not cron("0 0 0 * *")


def test_dom_32_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R13

    Day-of-month value 32 is one past the upper bound and must be invalid.
    """
    assert not cron("0 0 32 * *")


# ── wildcard ───────────────────────────────────────────────────────────────

def test_dom_wildcard_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R7

    '*' in the day-of-month field is always valid.
    """
    assert cron("0 0 * * *")


# ── step values ────────────────────────────────────────────────────────────

def test_dom_step_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R10

    '*/5' in the day-of-month field must be valid.
    """
    assert cron("0 0 */5 * *")


# ── range ──────────────────────────────────────────────────────────────────

def test_dom_range_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R9

    '1-31' spans the full day-of-month range and must be valid.
    """
    assert cron("0 0 1-31 * *")


def test_dom_range_inverted_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R9

    '31-1' has start > end and must be invalid.
    """
    assert not cron("0 0 31-1 * *")


def test_dom_range_out_of_bounds_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R13

    '1-32' has an end value out of range and must be invalid.
    """
    assert not cron("0 0 1-32 * *")


def test_dom_range_start_zero_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R13

    '0-15' starts at 0 which is below the lower bound and must be invalid.
    """
    assert not cron("0 0 0-15 * *")


# ── comma list ─────────────────────────────────────────────────────────────

def test_dom_list_valid():
    """Spec: wiki-Cron.pdf Cron-expression — R8

    '1,15,31' is a valid comma list for day-of-month.
    """
    assert cron("0 0 1,15,31 * *")


def test_dom_list_zero_invalid():
    """Spec: wiki-Cron.pdf Cron-expression — R8

    '0,15' includes value 0 which is out of range and must be invalid.
    """
    assert not cron("0 0 0,15 * *")
