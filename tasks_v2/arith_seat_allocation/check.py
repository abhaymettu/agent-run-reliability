import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, compute_allocation  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def main():
    workdir = sys.argv[1]
    out_path = os.path.join(workdir, "allocation_result.txt")
    if not os.path.isfile(out_path):
        fail("allocation_result.txt not found")

    try:
        with open(out_path) as f:
            content = f.read()
    except Exception as e:
        fail(f"could not read output file: {e}")

    rows = generate()
    seats = compute_allocation(rows)
    parties_sorted = sorted(seats.keys())

    lines = [f"{p}={seats[p]}" for p in parties_sorted]
    lines.append(f"seats_total={sum(seats.values())}")
    expected_text = "\n".join(lines) + "\n"

    if content != expected_text:
        fail("allocation_result.txt does not match expected content")

    print("PASS: allocation_result.txt matches expected seat allocation")
    sys.exit(0)


if __name__ == "__main__":
    main()
