#!/usr/bin/env python3
"""setup.py <workdir> -- writes the buggy module and its visible test file."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import BUGGY_SOURCE, VISIBLE_TEST_SOURCE  # noqa: E402


def main():
    if len(sys.argv) != 2:
        print("usage: setup.py <workdir>", file=sys.stderr)
        sys.exit(1)
    workdir = sys.argv[1]
    with open(os.path.join(workdir, "intervals.py"), "w") as f:
        f.write(BUGGY_SOURCE)
    with open(os.path.join(workdir, "test_intervals.py"), "w") as f:
        f.write(VISIBLE_TEST_SOURCE)


if __name__ == "__main__":
    main()
