"""Statistics helpers — stdlib only (spec 5.7).

wilson(k, n) -> (p, lo, hi)   Wilson 95% confidence interval for a proportion.
mcnemar(b, c) -> p_value       Exact two-sided McNemar test.
fmt_pct(p, lo, hi) -> str      Format as "p% (95% CI lo–hi%)".
"""

from __future__ import annotations

import math
from fractions import Fraction


# ---------------------------------------------------------------------------
# Wilson 95% CI
# ---------------------------------------------------------------------------

def wilson(k: int, n: int) -> tuple[float, float, float]:
    """Return (proportion, ci_low, ci_high) using the Wilson score interval.

    z = 1.96 (95% two-tailed). Returns (0.0, 0.0, 1.0) when n == 0.
    """
    if n == 0:
        return 0.0, 0.0, 1.0
    z = 1.96
    z2 = z * z
    p_hat = k / n
    centre = (p_hat + z2 / (2 * n)) / (1 + z2 / n)
    margin = (z / (1 + z2 / n)) * math.sqrt(p_hat * (1 - p_hat) / n + z2 / (4 * n * n))
    return (
        round(p_hat, 4),
        round(max(0.0, centre - margin), 4),
        round(min(1.0, centre + margin), 4),
    )


# ---------------------------------------------------------------------------
# Exact two-sided McNemar
# ---------------------------------------------------------------------------

def _binom_cdf(k: int, n: int, p: Fraction) -> Fraction:
    """Exact CDF P(X <= k) where X ~ Bin(n, p), using Fraction arithmetic."""
    total = Fraction(0)
    c = Fraction(1)  # C(n, i) running product
    for i in range(k + 1):
        if i > 0:
            c = c * (n - i + 1) // i
        total += c * (p ** i) * ((1 - p) ** (n - i))
    return total


def mcnemar(b: int, c: int) -> float:
    """Exact two-sided McNemar p-value.

    b = killed only by suite 1, c = killed only by suite 2.
    p = min(1, 2 * P(X <= min(b, c))), X ~ Bin(b+c, 0.5).
    Returns 1.0 when b + c == 0.
    """
    n = b + c
    if n == 0:
        return 1.0
    m = min(b, c)
    cdf = _binom_cdf(m, n, Fraction(1, 2))
    return float(min(Fraction(1), 2 * cdf))


# ---------------------------------------------------------------------------
# Formatter
# ---------------------------------------------------------------------------

def fmt_pct(p: float, lo: float, hi: float) -> str:
    """Format proportion as '65.6% (95% CI 47.8–80.0%)'."""
    return f"{p * 100:.1f}% (95% CI {lo * 100:.1f}\u2013{hi * 100:.1f}%)"
