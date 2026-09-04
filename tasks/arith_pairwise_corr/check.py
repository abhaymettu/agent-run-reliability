import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, result  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def main():
    workdir = sys.argv[1]
    out_path = os.path.join(workdir, "corr_result.txt")
    if not os.path.isfile(out_path):
        fail("corr_result.txt not found")

    try:
        with open(out_path) as f:
            content = f.read()
    except Exception as e:
        fail(f"could not read output file: {e}")

    records = generate()
    r_str, excluded = result(records)
    expected_text = f"r={r_str}\nexcluded={excluded}"

    if content.strip() != expected_text.strip():
        fail("output does not match expected corr_result.txt content")

    print("PASS: corr_result.txt matches expected Pearson r and excluded count")
    sys.exit(0)


if __name__ == "__main__":
    main()
