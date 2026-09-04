import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, group_medians  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def main():
    workdir = sys.argv[1]
    out_path = os.path.join(workdir, "median_by_group.csv")
    if not os.path.isfile(out_path):
        fail("median_by_group.csv not found")

    try:
        with open(out_path) as f:
            content = f.read()
    except Exception as e:
        fail(f"could not read output file: {e}")

    records = generate()
    expected = group_medians(records)
    expected_lines = ["group,median"]
    for g in sorted(expected.keys()):
        expected_lines.append(f"{g},{expected[g]:.1f}")
    expected_text = "\n".join(expected_lines)

    if content.strip() != expected_text.strip():
        fail("output does not match expected median_by_group.csv content")

    print("PASS: median_by_group.csv matches expected group medians")
    sys.exit(0)


if __name__ == "__main__":
    main()
