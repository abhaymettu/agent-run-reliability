import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, expected_name


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


def main():
    if len(sys.argv) < 2:
        fail("usage: check.py <workdir>")
    workdir = sys.argv[1]
    if not os.path.isdir(workdir):
        fail("workdir missing")

    try:
        files = generate()
    except Exception as e:
        fail(f"generator error: {e}")

    expected = {}
    orig_names = set()
    for orig_name, content, seq in files:
        new_name = expected_name(orig_name, seq)
        expected[new_name] = content
        orig_names.add(orig_name)

    try:
        actual_names = set(
            n for n in os.listdir(workdir) if os.path.isfile(os.path.join(workdir, n))
        )
    except Exception as e:
        fail(f"cannot list workdir: {e}")

    if actual_names != set(expected.keys()):
        missing = set(expected.keys()) - actual_names
        extra = actual_names - set(expected.keys())
        fail(f"filename set mismatch (missing={sorted(missing)[:3]}, extra={sorted(extra)[:3]})")

    for new_name, content in expected.items():
        path = os.path.join(workdir, new_name)
        with open(path, "rb") as f:
            actual = f.read()
        if actual != content:
            fail(f"content mismatch for {new_name}")

    print("PASS: all files renamed correctly")
    sys.exit(0)


if __name__ == "__main__":
    main()
