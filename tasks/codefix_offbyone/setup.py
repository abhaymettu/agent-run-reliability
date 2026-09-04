#!/usr/bin/env python3
"""setup.py <workdir> -- writes the buggy module and its visible test file."""
import sys
from pathlib import Path

WINDOWS_PY = '''"""Sliding-window utility."""


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
    for i in range(n - size):
        windows.append(seq[i:i + size])
    return windows
'''

TEST_PY = '''import unittest

from windows import sliding_windows


class TestSlidingWindows(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(
            sliding_windows([1, 2, 3, 4, 5], 2),
            [[1, 2], [2, 3], [3, 4], [4, 5]],
        )

    def test_size_equals_length(self):
        self.assertEqual(sliding_windows([1, 2, 3], 3), [[1, 2, 3]])

    def test_size_greater_than_length(self):
        self.assertEqual(sliding_windows([1, 2], 5), [])

    def test_window_count(self):
        seq = list(range(10))
        result = sliding_windows(seq, 4)
        self.assertEqual(len(result), len(seq) - 4 + 1)


if __name__ == "__main__":
    unittest.main()
'''


def main():
    if len(sys.argv) != 2:
        print("usage: setup.py <workdir>", file=sys.stderr)
        sys.exit(1)
    workdir = Path(sys.argv[1])
    (workdir / "windows.py").write_bytes(WINDOWS_PY.encode("utf-8"))
    (workdir / "test_windows.py").write_bytes(TEST_PY.encode("utf-8"))


if __name__ == "__main__":
    main()
