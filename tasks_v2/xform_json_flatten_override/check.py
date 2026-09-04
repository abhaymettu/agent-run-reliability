import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, process  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def main():
    workdir = sys.argv[1]
    out_path = os.path.join(workdir, "flattened.txt")
    if not os.path.isfile(out_path):
        fail("flattened.txt not found")

    try:
        with open(out_path) as f:
            content = f.read()
    except Exception as e:
        fail(f"could not read output file: {e}")

    base, overrides = generate()
    pairs = process(base, overrides)
    expected_text = "\n".join(f"{p}={v}" for p, v in pairs)

    if content.strip("\n") != expected_text:
        fail("flattened.txt does not match expected merged/flattened output")

    print("PASS: flattened.txt matches expected merge+flatten result")
    sys.exit(0)


if __name__ == "__main__":
    main()
