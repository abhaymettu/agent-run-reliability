#!/usr/bin/env python3
"""setup.py <workdir> -- writes the buggy module and its visible test file."""
import sys
from pathlib import Path

GROUPING_PY = '''"""Group items by a key function."""


def group_by_key(items, key_func, groups={}):
    """Group `items` into a dict mapping key_func(item) -> list of items
    with that key, preserving each item's original relative order within
    its group. Returns a fresh dict; does not mutate any dict passed in
    via `groups` and is safe to call repeatedly with different `items`
    without state leaking between calls.
    """
    for item in items:
        k = key_func(item)
        groups[k].append(item)
    return groups
'''

TEST_PY = '''import unittest

from grouping import group_by_key


class TestGroupByKey(unittest.TestCase):
    def test_basic_grouping(self):
        items = [1, 2, 3, 4, 5, 6]
        result = group_by_key(items, lambda x: x % 2)
        self.assertEqual(result, {1: [1, 3, 5], 0: [2, 4, 6]})

    def test_new_key_not_seen_before(self):
        result = group_by_key(["apple", "banana", "avocado"], lambda s: s[0])
        self.assertEqual(result, {"a": ["apple", "avocado"], "b": ["banana"]})

    def test_no_state_leaks_between_calls(self):
        first = group_by_key([1, 2], lambda x: "same")
        second = group_by_key([3, 4], lambda x: "same")
        self.assertEqual(second, {"same": [3, 4]})

    def test_empty_items(self):
        self.assertEqual(group_by_key([], lambda x: x), {})


if __name__ == "__main__":
    unittest.main()
'''


def main():
    if len(sys.argv) != 2:
        print("usage: setup.py <workdir>", file=sys.stderr)
        sys.exit(1)
    workdir = Path(sys.argv[1])
    (workdir / "grouping.py").write_bytes(GROUPING_PY.encode("utf-8"))
    (workdir / "test_grouping.py").write_bytes(TEST_PY.encode("utf-8"))


if __name__ == "__main__":
    main()
