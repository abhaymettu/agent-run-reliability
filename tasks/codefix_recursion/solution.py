#!/usr/bin/env python3
"""solution.py <workdir> -- overwrites nested.py with a correct fix, for
validation purposes only. Never shown to the subject agent."""
import sys
from pathlib import Path

FIXED = '''"""Recursive sum over an arbitrarily nested list of integers."""


def flatten_and_sum(nested):
    """Recursively sum every integer in `nested`, a list whose elements
    are either ints or further lists (nested arbitrarily deep). An empty
    list, at any level, contributes 0 to the sum. Raises TypeError if a
    non-list, non-int element is encountered.
    """
    if not nested:
        return 0
    total = 0
    for item in nested:
        if isinstance(item, list):
            total += flatten_and_sum(item)
        elif isinstance(item, int):
            total += item
        else:
            raise TypeError(f"unsupported element: {item!r}")
    return total
'''


def main():
    if len(sys.argv) != 2:
        print("usage: solution.py <workdir>", file=sys.stderr)
        sys.exit(1)
    workdir = Path(sys.argv[1])
    (workdir / "nested.py").write_bytes(FIXED.encode("utf-8"))


if __name__ == "__main__":
    main()
