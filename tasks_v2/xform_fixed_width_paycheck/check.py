import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, process, format_cents  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def main():
    workdir = sys.argv[1]
    out_path = os.path.join(workdir, "paycheck_totals.csv")
    if not os.path.isfile(out_path):
        fail("paycheck_totals.csv not found")

    try:
        with open(out_path, newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
    except Exception as e:
        fail(f"could not read/parse output file: {e}")

    if not rows:
        fail("output file is empty")
    if rows[0] != ["employee_id", "total", "record_count"]:
        fail(f"unexpected header: {rows[0]}")

    body = rows[1:]

    results = process(generate())
    expected_ids = sorted(results)

    if len(body) != len(expected_ids):
        fail(f"expected {len(expected_ids)} data rows, got {len(body)}")

    for i, eid in enumerate(expected_ids):
        total_cents, count = results[eid]
        expected_row = [eid, format_cents(total_cents), str(count)]
        if body[i] != expected_row:
            fail(f"row {i} mismatch: expected {expected_row}, got {body[i]}")

    print("PASS: paycheck_totals.csv matches expected per-employee totals")
    sys.exit(0)


if __name__ == "__main__":
    main()
