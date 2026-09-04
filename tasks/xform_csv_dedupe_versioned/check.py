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
    out_path = os.path.join(workdir, "deduped.csv")
    if not os.path.isfile(out_path):
        fail("deduped.csv not found")

    try:
        with open(out_path, newline="") as f:
            rows = list(csv.reader(f))
    except Exception as e:
        fail(f"could not read/parse output file: {e}")

    if not rows:
        fail("output file is empty")
    if rows[0] != ["key", "version", "seq", "payload"]:
        fail(f"unexpected header: {rows[0]}")

    body = rows[1:]
    winners = process(generate())
    expected_keys = sorted(winners)

    if len(body) != len(expected_keys):
        fail(f"expected {len(expected_keys)} data rows, got {len(body)}")

    for i, key in enumerate(expected_keys):
        version, seq, payload = winners[key]
        expected_row = [key, str(version), str(seq), payload]
        if body[i] != expected_row:
            fail(f"row {i} mismatch: expected {expected_row}, got {body[i]}")

    print("PASS: deduped.csv matches expected version-priority dedupe")
    sys.exit(0)


if __name__ == "__main__":
    main()
