import csv
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, QUARTERS


def expected():
    rows = generate()
    sums = defaultdict(lambda: defaultdict(int))
    regions = set()
    for region, quarter, amount in rows:
        sums[region][quarter] += amount
        regions.add(region)
    out = {}
    for region in regions:
        out[region] = [sums[region].get(q, 0) for q in QUARTERS]
    return out


def main():
    if len(sys.argv) < 2:
        print("FAIL: no workdir given")
        return 1
    workdir = sys.argv[1]
    path = os.path.join(workdir, "pivot.csv")
    if not os.path.isfile(path):
        print("FAIL: pivot.csv not found")
        return 1

    try:
        with open(path, newline="") as f:
            reader = list(csv.reader(f))
    except Exception as e:
        print(f"FAIL: could not read pivot.csv: {e}")
        return 1

    if not reader:
        print("FAIL: pivot.csv is empty")
        return 1

    header = [h.strip() for h in reader[0]]
    if header != ["region"] + QUARTERS:
        print(f"FAIL: bad header {header}")
        return 1

    exp = expected()
    expected_regions = sorted(exp.keys())
    data_rows = reader[1:]

    if len(data_rows) != len(expected_regions):
        print(f"FAIL: expected {len(expected_regions)} region rows, got {len(data_rows)}")
        return 1

    for i, row in enumerate(data_rows):
        if len(row) != 5:
            print(f"FAIL: row {i} has {len(row)} fields, want 5")
            return 1
        region = row[0].strip()
        exp_region = expected_regions[i]
        if region != exp_region:
            print(f"FAIL: row {i} region '{region}' != expected '{exp_region}' (check sort order)")
            return 1
        try:
            vals = [int(v.strip()) for v in row[1:]]
        except ValueError:
            print(f"FAIL: row {i} has non-integer amount(s): {row[1:]}")
            return 1
        if vals != exp[exp_region]:
            print(f"FAIL: row {i} ({region}) values {vals} != expected {exp[exp_region]}")
            return 1

    print("PASS: pivot.csv matches expected region-by-quarter matrix")
    return 0


if __name__ == "__main__":
    sys.exit(main())
