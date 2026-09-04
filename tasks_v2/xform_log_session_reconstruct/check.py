import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, process  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def main():
    workdir = sys.argv[1]
    out_path = os.path.join(workdir, "session_totals.txt")
    if not os.path.isfile(out_path):
        fail("session_totals.txt not found")

    try:
        with open(out_path) as f:
            content = f.read()
    except Exception as e:
        fail(f"could not read output file: {e}")

    events = generate()
    totals = process(events)
    expected_lines = [f"{u}={totals[u]}" for u in sorted(totals)]
    expected_text = "\n".join(expected_lines)

    if content.strip("\n") != expected_text:
        fail("session_totals.txt does not match expected session totals")

    print("PASS: session_totals.txt matches expected session reconstruction")
    sys.exit(0)


if __name__ == "__main__":
    main()
