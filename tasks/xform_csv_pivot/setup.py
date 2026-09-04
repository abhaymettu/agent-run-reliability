import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate


def main():
    workdir = sys.argv[1]
    rows = generate()
    path = os.path.join(workdir, "sales.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["region", "quarter", "amount"])
        for region, quarter, amount in rows:
            w.writerow([region, quarter, amount])


if __name__ == "__main__":
    main()
