import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, count_and_sum  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def main():
    workdir = sys.argv[1]
    out_path = os.path.join(workdir, "modular_result.txt")
    if not os.path.isfile(out_path):
        fail("modular_result.txt not found")

    try:
        with open(out_path) as f:
            content = f.read()
    except Exception as e:
        fail(f"could not read output file: {e}")

    values = generate()
    count, total = count_and_sum(values)
    expected_text = f"count={count}\nsum={total}"

    if content.strip() != expected_text.strip():
        fail("output does not match expected modular_result.txt content")

    print("PASS: modular_result.txt matches expected count/sum")
    sys.exit(0)


if __name__ == "__main__":
    main()
