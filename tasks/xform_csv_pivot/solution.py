import csv
import os
import sys
from collections import defaultdict

QUARTERS = ["Q1", "Q2", "Q3", "Q4"]


def main():
    workdir = sys.argv[1]
    with open(os.path.join(workdir, "sales.csv"), newline="") as f:
        reader = csv.DictReader(f)
        sums = defaultdict(lambda: defaultdict(int))
        regions = set()
        for row in reader:
            region = row["region"]
            quarter = row["quarter"]
            amount = int(row["amount"])
            sums[region][quarter] += amount
            regions.add(region)

    with open(os.path.join(workdir, "pivot.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["region"] + QUARTERS)
        for region in sorted(regions):
            w.writerow([region] + [sums[region].get(q, 0) for q in QUARTERS])


if __name__ == "__main__":
    main()
