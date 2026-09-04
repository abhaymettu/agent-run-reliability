import csv
import math
import os
import sys
from fractions import Fraction


def percentile(sorted_vals, p):
    n = len(sorted_vals)
    r = Fraction(p, 100) * (n - 1)
    lo = r.numerator // r.denominator
    hi = lo if r == lo else lo + 1
    if lo == hi:
        return Fraction(sorted_vals[lo])
    return Fraction(sorted_vals[lo]) + (r - lo) * (sorted_vals[hi] - sorted_vals[lo])


def fmt(frac):
    scaled = frac * 100
    sign = 1 if scaled >= 0 else -1
    rounded = sign * math.floor(abs(scaled) + Fraction(1, 2))
    s = "-" if rounded < 0 else ""
    r = abs(rounded)
    return f"{s}{r // 100}.{r % 100:02d}"


def main():
    workdir = sys.argv[1]
    in_path = os.path.join(workdir, "measurements.csv")
    vals = []
    with open(in_path, newline="") as f:
        for row in csv.DictReader(f):
            vals.append(int(row["value"]))
    vals.sort()

    p90 = percentile(vals, 90)
    p25 = percentile(vals, 25)
    p75 = percentile(vals, 75)
    iqr = p75 - p25

    out_path = os.path.join(workdir, "percentile_result.txt")
    with open(out_path, "w") as f:
        f.write(f"p90={fmt(p90)}\n")
        f.write(f"iqr={fmt(iqr)}")


if __name__ == "__main__":
    main()
