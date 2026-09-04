"""Shared generator for arith_weighted_score. Stays in tasks/, never copied to workdir."""
import random
from fractions import Fraction

SEED = 20260904

# Weights are eighths so 4x+3y+z is an integer numerator over 8; whenever that
# numerator is odd, value/8 lands exactly on a .xx5 boundary (.125/.375/.625/.875),
# forcing a genuine round-half-up decision rather than a no-op rounding.
WX, WY, WZ = Fraction(1, 2), Fraction(3, 8), Fraction(1, 8)


def generate(seed=SEED):
    """Return a list of dicts: {id, x, y, z} with x,y,z in [0, 60].

    Deliberately built so, among the top-scoring records:
      - id 3 and id 4 produce an exact tie in the rounded weighted_score
        (both near-max), forcing the id-ascending tie-break
      - id 5 lands exactly on a .xx5 rounding boundary where round-half-up
        and Python's default round-half-even disagree (59.625 -> 59.63 under
        the stated rule, but round(59.625, 2) gives 59.62)
    """
    rng = random.Random(seed)
    records = []
    for rid in range(1, 81):
        x = rng.randint(0, 60)
        y = rng.randint(0, 60)
        z = rng.randint(0, 60)
        records.append({"id": rid, "x": x, "y": y, "z": z})

    # exact tie: 4x+3y+z = 472 for both -> raw score 59.00 for both
    records[2] = {"id": 3, "x": 60, "y": 60, "z": 52}   # 240+180+52=472
    records[3] = {"id": 4, "x": 59, "y": 60, "z": 56}   # 236+180+56=472

    # round-half-up vs round-half-even divergence: 4x+3y+z = 477 -> 59.625
    records[4] = {"id": 5, "x": 60, "y": 60, "z": 57}   # 240+180+57=477

    rng.shuffle(records)
    return records


def weighted_score_cents(rec):
    """Weighted score rounded to 2 decimals (round-half-up), returned as an
    integer number of hundredths. Computed exactly via Fraction so there is
    no floating-point ambiguity."""
    raw = WX * rec["x"] + WY * rec["y"] + WZ * rec["z"]
    scaled = raw * 100  # shift 2 decimals
    # round half up (away from zero; all values here are non-negative)
    import math
    rounded = math.floor(scaled + Fraction(1, 2))
    return rounded


def format_cents(cents):
    return f"{cents // 100}.{abs(cents) % 100:02d}"


def top_k(records, k=5):
    scored = [(r["id"], weighted_score_cents(r)) for r in records]
    scored.sort(key=lambda t: (-t[1], t[0]))
    return scored[:k]
