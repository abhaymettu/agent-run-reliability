"""Shared generator for arith_percentile. Stays in tasks/, never copied to workdir."""
import random
from fractions import Fraction

SEED = 20260904
N = 158
PERCENTILE = 90  # the specific percentile the task asks for


def generate(seed=SEED):
    """Return a list of dicts: {id, value} where value is an int (can be
    negative), representing e.g. a temperature-delta measurement column.
    Includes duplicate values (ties) by construction (randint over a small
    range with N=137 draws is guaranteed to repeat)."""
    rng = random.Random(seed)
    values = [rng.randint(-40, 120) for _ in range(N)]
    return [{"id": i + 1, "value": v} for i, v in enumerate(values)]


def _percentile(sorted_vals, p):
    """Linear-interpolation percentile (numpy's default / Excel PERCENTILE.INC),
    computed exactly with Fractions to avoid float error:
      r = (p/100) * (n-1)   (0-based rank)
      lo = floor(r), hi = ceil(r)
      result = v[lo] + (r - lo) * (v[hi] - v[lo])
    """
    n = len(sorted_vals)
    r = Fraction(p, 100) * (n - 1)
    lo = r.numerator // r.denominator  # floor
    hi = lo if r == lo else lo + 1
    if lo == hi:
        return Fraction(sorted_vals[lo])
    frac = r - lo
    return Fraction(sorted_vals[lo]) + frac * (sorted_vals[hi] - sorted_vals[lo])


def stats(records):
    vals = sorted(r["value"] for r in records)
    p90 = _percentile(vals, PERCENTILE)
    p25 = _percentile(vals, 25)
    p75 = _percentile(vals, 75)
    iqr = p75 - p25
    return p90, iqr


def fmt(frac):
    # round-half-up to 2 decimals, exact via Fraction arithmetic
    import math
    scaled = frac * 100
    sign = 1 if scaled >= 0 else -1
    rounded = sign * math.floor(abs(scaled) + Fraction(1, 2))
    s = "-" if rounded < 0 else ""
    r = abs(rounded)
    return f"{s}{r // 100}.{r % 100:02d}"
