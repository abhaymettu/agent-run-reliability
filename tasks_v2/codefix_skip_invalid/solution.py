#!/usr/bin/env python3
"""solution.py <workdir> -- overwrites ledger.py with a correct fix, for
validation purposes only. Never shown to the subject agent."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import FIXED_SOURCE  # noqa: E402


def main():
    if len(sys.argv) != 2:
        print("usage: solution.py <workdir>", file=sys.stderr)
        sys.exit(1)
    workdir = sys.argv[1]
    with open(os.path.join(workdir, "ledger.py"), "w") as f:
        f.write(FIXED_SOURCE)


if __name__ == "__main__":
    main()
