import csv
import math
import os
import sys
from fractions import Fraction


def weighted_score_cents(x, y, z):
    raw = Fraction(1, 2) * x + Fraction(3, 8) * y + Fraction(1, 8) * z
    scaled = raw * 100
    return math.floor(scaled + Fraction(1, 2))  # round half up


def format_cents(cents):
    return f"{cents // 100}.{cents % 100:02d}"


def main():
    workdir = sys.argv[1]
    in_path = os.path.join(workdir, "records.csv")
    records = []
    with open(in_path, newline="") as f:
        for row in csv.DictReader(f):
            rid = int(row["id"])
            cents = weighted_score_cents(int(row["x"]), int(row["y"]), int(row["z"]))
            records.append((rid, cents))

    records.sort(key=lambda t: (-t[1], t[0]))
    top5 = records[:5]

    out_path = os.path.join(workdir, "top_scores.csv")
    with open(out_path, "w", newline="") as f:
        f.write("id,weighted_score\n")
        for rid, cents in top5:
            f.write(f"{rid},{format_cents(cents)}\n")


if __name__ == "__main__":
    main()
