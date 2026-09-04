"""Shared generator for arith_pairwise_corr. Stays in tasks/, never copied to workdir."""
import random
import math
import decimal

SEED = 20260904
N = 180


def generate(seed=SEED):
    """Return a list of dicts: {id, x, y} where x and y are ints, OR the
    string "NA" (a missing value), for some rows.

    Deliberately includes:
      - several rows with x = "NA" or y = "NA" (missing)
      - several rows with a negative y (to be filtered out)
      - an exact tie: two different records with the same x value
    """
    rng = random.Random(seed)
    records = []
    for i in range(1, N + 1):
        x = rng.randint(0, 200)
        # y correlated with x plus noise, some negative values allowed
        y = int(round(0.8 * x - 40 + rng.gauss(0, 15)))
        records.append({"id": i, "x": x, "y": y})

    # missing values
    for idx in (5, 6, 40, 41, 90):
        records[idx]["x"] = "NA"
    for idx in (10, 42, 91, 92):
        records[idx]["y"] = "NA"

    # exact tie in x between two records that both survive filtering
    records[100]["x"] = 77
    records[101]["x"] = 77
    records[100]["y"] = 30
    records[101]["y"] = 45

    return records


def _is_missing(v):
    return v == "NA"


def filtered(records):
    kept = []
    excluded = 0
    for r in records:
        x, y = r["x"], r["y"]
        if _is_missing(x) or _is_missing(y) or (isinstance(y, int) and y < 0):
            excluded += 1
            continue
        kept.append((x, y))
    return kept, excluded


def pearson_r(pairs):
    n = len(pairs)
    sx = sum(x for x, y in pairs)
    sy = sum(y for x, y in pairs)
    sxy = sum(x * y for x, y in pairs)
    sxx = sum(x * x for x, y in pairs)
    syy = sum(y * y for x, y in pairs)
    num = n * sxy - sx * sy
    den = math.sqrt((n * sxx - sx * sx) * (n * syy - sy * sy))
    return num / den


def fmt_r(r):
    d = decimal.Decimal(repr(r)).quantize(
        decimal.Decimal("0.0001"), rounding=decimal.ROUND_HALF_UP
    )
    return str(d)


def result(records):
    pairs, excluded = filtered(records)
    r = pearson_r(pairs)
    return fmt_r(r), excluded
