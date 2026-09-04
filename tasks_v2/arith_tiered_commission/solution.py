import csv
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

TIERS = [
    (Decimal("0"), Decimal("5000"), Decimal("0.05")),
    (Decimal("5000"), Decimal("15000"), Decimal("0.08")),
    (Decimal("15000"), None, Decimal("0.12")),
]
CENT = Decimal("0.01")


def commission_for(cum_before, amount):
    cum_after = cum_before + amount
    total = Decimal(0)
    for lo, hi, rate in TIERS:
        seg_lo = max(cum_before, lo)
        seg_hi = cum_after if hi is None else min(cum_after, hi)
        if seg_hi > seg_lo:
            total += (seg_hi - seg_lo) * rate
    return total


def main():
    workdir = sys.argv[1]
    in_path = os.path.join(workdir, "sales.csv")
    rows = []
    with open(in_path, newline="") as f:
        for row in csv.DictReader(f):
            rows.append((row["rep"], Decimal(row["amount"])))

    cum = {}
    totals = {}
    for rep, amount in rows:
        cb = cum.get(rep, Decimal("0"))
        raw = commission_for(cb, amount)
        rounded = raw.quantize(CENT, rounding=ROUND_HALF_UP)
        totals[rep] = totals.get(rep, Decimal("0")) + rounded
        cum[rep] = cb + amount

    out_path = os.path.join(workdir, "commission_result.txt")
    with open(out_path, "w") as f:
        for rep in sorted(totals.keys()):
            f.write(f"{rep}={totals[rep]:.2f}\n")


if __name__ == "__main__":
    main()
