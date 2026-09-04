#!/usr/bin/env python3
"""check.py <workdir> -- runs a hidden superset test suite against the
agent's grouping.py. Exits 0 only if every hidden test passes."""
import importlib.util
import signal
import sys
import unittest
from pathlib import Path


def load_module(workdir):
    path = Path(workdir) / "grouping.py"
    if not path.exists() or path.stat().st_size == 0:
        print("FAIL: grouping.py missing or empty")
        sys.exit(1)
    try:
        spec = importlib.util.spec_from_file_location("grouping_under_test", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as exc:
        print(f"FAIL: could not import grouping.py: {exc}")
        sys.exit(1)
    if not hasattr(module, "group_by_key"):
        print("FAIL: group_by_key is not defined")
        sys.exit(1)
    return module


class HiddenTests(unittest.TestCase):
    fn = None

    def test_basic_grouping(self):
        items = [1, 2, 3, 4, 5, 6]
        result = self.fn(items, lambda x: x % 2)
        self.assertEqual(result, {1: [1, 3, 5], 0: [2, 4, 6]})

    def test_new_key_not_seen_before(self):
        result = self.fn(["apple", "banana", "avocado"], lambda s: s[0])
        self.assertEqual(result, {"a": ["apple", "avocado"], "b": ["banana"]})

    def test_no_state_leaks_between_calls(self):
        first = self.fn([1, 2], lambda x: "same")
        second = self.fn([3, 4], lambda x: "same")
        self.assertEqual(second, {"same": [3, 4]})
        self.assertEqual(first, {"same": [1, 2]})

    def test_empty_items(self):
        self.assertEqual(self.fn([], lambda x: x), {})

    def test_three_sequential_calls_all_independent(self):
        self.fn([1], lambda x: "k")
        self.fn([2], lambda x: "k")
        third = self.fn([3], lambda x: "k")
        self.assertEqual(third, {"k": [3]})

    def test_single_group_preserves_order(self):
        result = self.fn([5, 1, 4, 2, 3], lambda x: "all")
        self.assertEqual(result, {"all": [5, 1, 4, 2, 3]})

    def test_many_distinct_keys(self):
        items = list(range(20))
        result = self.fn(items, lambda x: x % 5)
        for k in range(5):
            self.assertEqual(result[k], [x for x in items if x % 5 == k])


def main():
    if len(sys.argv) != 2:
        print("FAIL: usage check.py <workdir>")
        sys.exit(1)
    workdir = sys.argv[1]
    module = load_module(workdir)
    HiddenTests.fn = staticmethod(module.group_by_key)

    def handler(signum, frame):
        raise TimeoutError("hidden tests timed out")

    had_alarm = hasattr(signal, "SIGALRM")
    if had_alarm:
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(10)

    try:
        suite = unittest.TestLoader().loadTestsFromTestCase(HiddenTests)
        result = unittest.TextTestRunner(verbosity=0, stream=sys.stderr).run(suite)
    except TimeoutError:
        print("FAIL: hidden tests timed out")
        sys.exit(1)
    finally:
        if had_alarm:
            signal.alarm(0)

    if result.wasSuccessful():
        print("PASS: all hidden tests passed")
        sys.exit(0)
    print(f"FAIL: {len(result.failures)} failures, {len(result.errors)} errors")
    sys.exit(1)


if __name__ == "__main__":
    main()
