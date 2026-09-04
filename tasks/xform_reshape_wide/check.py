import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate


def expected():
    rows = generate()
    last = {}
    ids = set()
    attrs = set()
    for sid, attr, value in rows:
        last[(sid, attr)] = value
        ids.add(sid)
        attrs.add(attr)
    return ids, sorted(attrs), last


def main():
    if len(sys.argv) < 2:
        print("FAIL: no workdir given")
        return 1
    workdir = sys.argv[1]
    path = os.path.join(workdir, "measurements_wide.csv")
    if not os.path.isfile(path):
        print("FAIL: measurements_wide.csv not found")
        return 1

    try:
        with open(path, newline="") as f:
            reader = list(csv.reader(f))
    except Exception as e:
        print(f"FAIL: could not read measurements_wide.csv: {e}")
        return 1

    if not reader:
        print("FAIL: measurements_wide.csv is empty")
        return 1

    ids, exp_attrs, last = expected()
    exp_header = ["id"] + exp_attrs
    header = [h.strip() for h in reader[0]]
    if header != exp_header:
        print(f"FAIL: bad header {header} != {exp_header}")
        return 1

    expected_ids = sorted(ids)
    data_rows = reader[1:]

    if len(data_rows) != len(expected_ids):
        print(f"FAIL: expected {len(expected_ids)} rows, got {len(data_rows)}")
        return 1

    for i, row in enumerate(data_rows):
        if len(row) != len(exp_header):
            print(f"FAIL: row {i} has {len(row)} fields, want {len(exp_header)}")
            return 1
        sid = row[0].strip()
        exp_id = expected_ids[i]
        if sid != exp_id:
            print(f"FAIL: row {i} id '{sid}' != expected '{exp_id}' (check sort order)")
            return 1
        for j, attr in enumerate(exp_attrs):
            cell = row[1 + j].strip()
            exp_val = last.get((exp_id, attr))
            exp_cell = "" if exp_val is None else str(exp_val)
            if cell != exp_cell:
                print(f"FAIL: row {i} ({exp_id}) attribute '{attr}' got '{cell}' != expected '{exp_cell}'")
                return 1

    print(f"PASS: measurements_wide.csv matches {len(expected_ids)} ids x {len(exp_attrs)} attributes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
