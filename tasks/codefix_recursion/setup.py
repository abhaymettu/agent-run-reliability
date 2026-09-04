#!/usr/bin/env python3
"""setup.py <workdir> -- writes the buggy module and its visible test file."""
import sys
from pathlib import Path

NESTED_PY = '''"""Recursive sum over an arbitrarily nested list of integers."""


def flatten_and_sum(nested):
    """Recursively sum every integer in `nested`, a list whose elements
    are either ints or further lists (nested arbitrarily deep). An empty
    list, at any level, contributes 0 to the sum. Raises TypeError if a
    non-list, non-int element is encountered.
    """
    if not nested:
        return None
    total = 0
    for item in nested:
        if isinstance(item, list):
            total = flatten_and_sum(item)
        elif isinstance(item, int):
            total += item
        else:
            raise TypeError(f"unsupported element: {item!r}")
    return total
'''

TEST_PY = '''import unittest

from nested import flatten_and_sum


class TestFlattenAndSum(unittest.TestCase):
    def test_flat_list(self):
        self.assertEqual(flatten_and_sum([1, 2, 3]), 6)

    def test_empty_list(self):
        self.assertEqual(flatten_and_sum([]), 0)

    def test_one_level_nesting(self):
        self.assertEqual(flatten_and_sum([1, [2, 3], 4]), 10)

    def test_sibling_sublists(self):
        self.assertEqual(flatten_and_sum([[1, 2], [3, 4]]), 10)

    def test_deep_nesting(self):
        self.assertEqual(flatten_and_sum([1, [2, [3, [4, 5]]]]), 15)

    def test_nested_empty_lists(self):
        self.assertEqual(flatten_and_sum([1, [], [2, []], 3]), 6)


if __name__ == "__main__":
    unittest.main()
'''


def main():
    if len(sys.argv) != 2:
        print("usage: setup.py <workdir>", file=sys.stderr)
        sys.exit(1)
    workdir = Path(sys.argv[1])
    (workdir / "nested.py").write_bytes(NESTED_PY.encode("utf-8"))
    (workdir / "test_nested.py").write_bytes(TEST_PY.encode("utf-8"))


if __name__ == "__main__":
    main()
