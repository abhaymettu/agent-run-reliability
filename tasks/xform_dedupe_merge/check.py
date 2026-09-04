import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, fmt_ts


def expected():
    primary_rows, secondary_rows = generate()
    p_by_id = {r["id"]: r for r in primary_rows}
    s_by_id = {r["id"]: r for r in secondary_rows}
    all_ids = set(p_by_id) | set(s_by_id)

    result = {}
    for rid in all_ids:
        p = p_by_id.get(rid)
        s = s_by_id.get(rid)
        if p and not s:
            chosen = p
        elif s and not p:
            chosen = s
        else:
            if s["updated_at"] >= p["updated_at"]:
                chosen = s
            else:
                chosen = p
        result[rid] = (chosen["id"], chosen["name"], str(chosen["value"]), fmt_ts(chosen["updated_at"]))
    return result


def main():
    if len(sys.argv) < 2:
        print("FAIL: no workdir given")
        return 1
    workdir = sys.argv[1]
    path = os.path.join(workdir, "merged.csv")
    if not os.path.isfile(path):
        print("FAIL: merged.csv not found")
        return 1

    try:
        with open(path, newline="") as f:
            reader = list(csv.reader(f))
    except Exception as e:
        print(f"FAIL: could not read merged.csv: {e}")
        return 1

    if not reader:
        print("FAIL: merged.csv is empty")
        return 1

    header = [h.strip() for h in reader[0]]
    if header != ["id", "name", "value", "updated_at"]:
        print(f"FAIL: bad header {header}")
        return 1

    exp = expected()
    expected_ids = sorted(exp.keys())
    data_rows = reader[1:]

    if len(data_rows) != len(expected_ids):
        print(f"FAIL: expected {len(expected_ids)} rows, got {len(data_rows)}")
        return 1

    for i, row in enumerate(data_rows):
        if len(row) != 4:
            print(f"FAIL: row {i} has {len(row)} fields, want 4")
            return 1
        row = tuple(v.strip() for v in row)
        exp_id = expected_ids[i]
        if row[0] != exp_id:
            print(f"FAIL: row {i} id '{row[0]}' != expected '{exp_id}' (check sort order)")
            return 1
        if row != exp[exp_id]:
            print(f"FAIL: row {i} ({exp_id}) got {row} != expected {exp[exp_id]}")
            return 1

    print(f"PASS: merged.csv matches {len(expected_ids)} expected merged rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
