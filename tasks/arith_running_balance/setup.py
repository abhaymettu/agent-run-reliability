import csv
import os
import sys

from gen import generate, format_cents


def main():
    workdir = sys.argv[1]
    txns = generate()
    path = os.path.join(workdir, "transactions.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "amount"])
        for t in txns:
            w.writerow([t["date"], format_cents(t["amount_cents"])])


if __name__ == "__main__":
    main()
