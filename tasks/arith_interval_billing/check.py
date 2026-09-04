import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, compute_overlap_minutes  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def main():
    workdir = sys.argv[1]
    out_path = os.path.join(workdir, "billing_result.txt")
    if not os.path.isfile(out_path):
        fail("billing_result.txt not found")

    try:
        with open(out_path) as f:
            content = f.read()
    except Exception as e:
        fail(f"could not read output file: {e}")

    rows = generate()
    result = compute_overlap_minutes(rows)
    rooms_sorted = sorted(result.keys())
    max_room = min(
        (r for r in rooms_sorted if result[r] == max(result.values())),
    )

    lines = [f"{room}={result[room]}" for room in rooms_sorted]
    lines.append(f"max_room={max_room}")
    expected_text = "\n".join(lines) + "\n"

    if content != expected_text:
        fail("billing_result.txt does not match expected content")

    print("PASS: billing_result.txt matches expected overlap result")
    sys.exit(0)


if __name__ == "__main__":
    main()
