import csv
import decimal
import math
import os
import sys


def main():
    workdir = sys.argv[1]
    in_path = os.path.join(workdir, "pairs.csv")
    pairs = []
    excluded = 0
    with open(in_path, newline="") as f:
        for row in csv.DictReader(f):
            xs, ys = row["x"], row["y"]
            if xs == "NA" or ys == "NA":
                excluded += 1
                continue
            x, y = int(xs), int(ys)
            if y < 0:
                excluded += 1
                continue
            pairs.append((x, y))

    n = len(pairs)
    sx = sum(x for x, y in pairs)
    sy = sum(y for x, y in pairs)
    sxy = sum(x * y for x, y in pairs)
    sxx = sum(x * x for x, y in pairs)
    syy = sum(y * y for x, y in pairs)
    num = n * sxy - sx * sy
    den = math.sqrt((n * sxx - sx * sx) * (n * syy - sy * sy))
    r = num / den

    d = decimal.Decimal(repr(r)).quantize(
        decimal.Decimal("0.0001"), rounding=decimal.ROUND_HALF_UP
    )

    out_path = os.path.join(workdir, "corr_result.txt")
    with open(out_path, "w") as f:
        f.write(f"r={d}\n")
        f.write(f"excluded={excluded}")


if __name__ == "__main__":
    main()


