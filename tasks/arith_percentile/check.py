import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, stats, fmt  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def main():
    workdir = sys.argv[1]
    out_path = os.path.join(workdir, "percentile_result.txt")
    if not os.path.isfile(out_path):
        fail("percentile_result.txt not found")

    try:
        with open(out_path) as f:
            content = f.read()
    except Exception as e:
        fail(f"could not read output file: {e}")

    records = generate()
    p90, iqr = stats(records)
    expected_text = f"p90={fmt(p90)}\niqr={fmt(iqr)}"

    if content.strip() != expected_text.strip():
        fail("output does not match expected percentile_result.txt content")

    print("PASS: percentile_result.txt matches expected p90/IQR")
    sys.exit(0)


if __name__ == "__main__":
    main()
