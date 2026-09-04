#!/usr/bin/env python3
"""check.py <workdir> -- runs a hidden superset test suite against the
agent's nested.py. Exits 0 only if every hidden test passes."""
import importlib.util
import signal
import sys
import unittest
from pathlib import Path


def load_module(workdir):
    path = Path(workdir) / "nested.py"
    if not path.exists() or path.stat().st_size == 0:
        print("FAIL: nested.py missing or empty")
        sys.exit(1)
    try:
        spec = importlib.util.spec_from_file_location("nested_under_test", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as exc:
        print(f"FAIL: could not import nested.py: {exc}")
        sys.exit(1)
    if not hasattr(module, "flatten_and_sum"):
        print("FAIL: flatten_and_sum is not defined")
        sys.exit(1)
    return module


class HiddenTests(unittest.TestCase):
    fn = None

    def test_flat_list(self):
        self.assertEqual(self.fn([1, 2, 3]), 6)

    def test_empty_list(self):
        self.assertEqual(self.fn([]), 0)

    def test_one_level_nesting(self):
        self.assertEqual(self.fn([1, [2, 3], 4]), 10)

    def test_sibling_sublists(self):
        self.assertEqual(self.fn([[1, 2], [3, 4]]), 10)

    def test_deep_nesting(self):
        self.assertEqual(self.fn([1, [2, [3, [4, 5]]]]), 15)

    def test_nested_empty_lists(self):
        self.assertEqual(self.fn([1, [], [2, []], 3]), 6)

    def test_all_empty_at_every_level(self):
        self.assertEqual(self.fn([[], [[], []], []]), 0)

    def test_single_int(self):
        self.assertEqual(self.fn([42]), 42)

    def test_negative_numbers(self):
        self.assertEqual(self.fn([1, [-5, 3], -2]), -3)

    def test_many_siblings(self):
        self.assertEqual(self.fn([[1], [2], [3], [4], [5]]), 15)

    def test_deeply_nested_single_value(self):
        self.assertEqual(self.fn([[[[[7]]]]]), 7)

    def test_non_int_element_raises(self):
        with self.assertRaises(TypeError):
            self.fn([1, "two", 3])


def main():
    if len(sys.argv) != 2:
        print("FAIL: usage check.py <workdir>")
        sys.exit(1)
    workdir = sys.argv[1]
    module = load_module(workdir)
    HiddenTests.fn = staticmethod(module.flatten_and_sum)

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
