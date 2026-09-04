import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, format_log_line, TOP_N


def expected():
    rows = generate()
    ordered = sorted(rows, key=lambda r: (-r["duration_ms"], r["request_id"]))
    top = ordered[:TOP_N]
    return [
        (r["request_id"], r["duration_ms"], r["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"), r["path"])
        for r in top
    ]


def main():
    if len(sys.argv) < 2:
        print("FAIL: no workdir given")
        return 1
    workdir = sys.argv[1]
    path = os.path.join(workdir, "slowest.csv")
    if not os.path.isfile(path):
        print("FAIL: slowest.csv not found")
        return 1

    try:
        with open(path, newline="") as f:
            reader = list(csv.reader(f))
    except Exception as e:
        print(f"FAIL: could not read slowest.csv: {e}")
        return 1

    if not reader:
        print("FAIL: slowest.csv is empty")
        return 1

    header = [h.strip() for h in reader[0]]
    if header != ["request_id", "duration_ms", "timestamp", "path"]:
        print(f"FAIL: bad header {header}")
        return 1

    exp = expected()
    data_rows = reader[1:]

    if len(data_rows) != len(exp):
        print(f"FAIL: expected {len(exp)} rows, got {len(data_rows)}")
        return 1

    for i, row in enumerate(data_rows):
        if len(row) != 4:
            print(f"FAIL: row {i} has {len(row)} fields, want 4")
            return 1
        req_id, dur, ts, path_val = [v.strip() for v in row]
        exp_req, exp_dur, exp_ts, exp_path = exp[i]
        try:
            dur_int = int(dur)
        except ValueError:
            print(f"FAIL: row {i} duration_ms '{dur}' is not an integer")
            return 1
        if (req_id, dur_int, ts, path_val) != (exp_req, exp_dur, exp_ts, exp_path):
            print(f"FAIL: row {i} got {(req_id, dur_int, ts, path_val)} != expected {(exp_req, exp_dur, exp_ts, exp_path)}")
            return 1

    print(f"PASS: slowest.csv matches {len(exp)} expected slowest requests")
    return 0


if __name__ == "__main__":
    sys.exit(main())
