import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, compute_expected  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def main():
    workdir = sys.argv[1]
    records = generate()
    expected = compute_expected(records)  # original_name -> (final_name, content)

    expected_finals = {}
    for orig, (final, content) in expected.items():
        expected_finals[final] = content

    actual = {}
    for name in os.listdir(workdir):
        if name.startswith("."):
            continue
        full = os.path.join(workdir, name)
        if not os.path.isfile(full):
            continue
        with open(full) as f:
            actual[name] = f.read()

    for final, content in expected_finals.items():
        if final not in actual:
            fail(f"missing expected renamed file: {final}")
        if actual[final] != content:
            fail(f"content mismatch for {final}")

    extra = set(actual.keys()) - set(expected_finals.keys())
    if extra:
        fail(f"unexpected extra file(s) present: {sorted(extra)}")

    if len(actual) != len(expected_finals):
        fail("wrong number of files in working directory")

    print("PASS: all files renamed to their computed target names")
    sys.exit(0)


if __name__ == "__main__":
    main()
