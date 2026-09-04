import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, compute_commissions, format_cents  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def main():
    workdir = sys.argv[1]
    out_path = os.path.join(workdir, "commission_result.txt")
    if not os.path.isfile(out_path):
        fail("commission_result.txt not found")

    try:
        with open(out_path) as f:
            content = f.read()
    except Exception as e:
        fail(f"could not read output file: {e}")

    rows = generate()
    totals = compute_commissions(rows)
    reps_sorted = sorted(totals.keys())
    expected_lines = [f"{rep}={format_cents(totals[rep])}" for rep in reps_sorted]
    expected_text = "\n".join(expected_lines) + "\n"

    if content != expected_text:
        fail("commission_result.txt does not match expected content")

    print("PASS: commission_result.txt matches expected tiered commissions")
    sys.exit(0)


if __name__ == "__main__":
    main()
