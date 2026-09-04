import csv
import os
import sys

from gen import generate


def to_amount_str(cents):
    return f"{cents // 100}.{cents % 100:02d}"


def main():
    workdir = sys.argv[1]
    rows = generate()
    path = os.path.join(workdir, "sales.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["seq", "rep", "amount"])
        for r in rows:
            w.writerow([r["seq"], r["rep"], to_amount_str(r["amount_cents"])])


if __name__ == "__main__":
    main()
