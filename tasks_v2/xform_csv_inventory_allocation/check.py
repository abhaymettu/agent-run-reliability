import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, process  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def main():
    workdir = sys.argv[1]
    out_path = os.path.join(workdir, "allocations.csv")
    if not os.path.isfile(out_path):
        fail("allocations.csv not found")

    try:
        with open(out_path, newline="") as f:
            rows = list(csv.reader(f))
    except Exception as e:
        fail(f"could not read/parse output file: {e}")

    if not rows:
        fail("output file is empty")
    if rows[0] != ["seq", "warehouse", "sku", "requested", "allocated"]:
        fail(f"unexpected header: {rows[0]}")

    body = rows[1:]

    stock, orders = generate()
    expected = process(stock, orders)

    if len(body) != len(expected):
        fail(f"expected {len(expected)} data rows, got {len(body)}")

    for i, (seq, wh, sku, req, alloc) in enumerate(expected):
        expected_row = [str(seq), wh, sku, str(req), str(alloc)]
        if body[i] != expected_row:
            fail(f"row {i} mismatch: expected {expected_row}, got {body[i]}")

    print("PASS: allocations.csv matches expected seq-ordered allocation")
    sys.exit(0)


if __name__ == "__main__":
    main()
