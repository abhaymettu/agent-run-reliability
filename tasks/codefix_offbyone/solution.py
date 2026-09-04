#!/usr/bin/env python3
"""solution.py <workdir> -- overwrites windows.py with a correct fix, for
validation purposes only. Never shown to the subject agent."""
import sys
from pathlib import Path

FIXED = '''"""Sliding-window utility."""


def sliding_windows(seq, size):
    """Return a list of all contiguous windows of length `size` taken from
    `seq`, in order, sliding one element at a time.

    Example: sliding_windows([1, 2, 3, 4, 5], 2) ==
        [[1, 2], [2, 3], [3, 4], [4, 5]]

    If `size` is less than or equal to 0, or greater than len(seq), return
    an empty list. If `size` equals len(seq), return a list containing one
    window: the whole sequence, as a list.
    """
    seq = list(seq)
    n = len(seq)
    if size <= 0 or size > n:
        return []
    windows = []
    for i in range(n - size + 1):
        windows.append(seq[i:i + size])
    return windows
'''


def main():
    if len(sys.argv) != 2:
        print("usage: solution.py <workdir>", file=sys.stderr)
        sys.exit(1)
    workdir = Path(sys.argv[1])
    (workdir / "windows.py").write_bytes(FIXED.encode("utf-8"))


if __name__ == "__main__":
    main()
