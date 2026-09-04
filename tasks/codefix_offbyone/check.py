#!/usr/bin/env python3
"""check.py <workdir> -- runs a hidden superset test suite against the
agent's windows.py. Exits 0 only if every hidden test passes."""
import importlib.util
import signal
import sys
import unittest
from pathlib import Path


def load_module(workdir):
    path = Path(workdir) / "windows.py"
    if not path.exists() or path.stat().st_size == 0:
        print("FAIL: windows.py missing or empty")
        sys.exit(1)
    try:
        spec = importlib.util.spec_from_file_location("windows_under_test", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as exc:
        print(f"FAIL: could not import windows.py: {exc}")
        sys.exit(1)
    if not hasattr(module, "sliding_windows"):
        print("FAIL: sliding_windows is not defined")
        sys.exit(1)
    return module


class HiddenTests(unittest.TestCase):
    fn = None  # bound to module.sliding_windows below

    def test_basic(self):
        self.assertEqual(
            self.fn([1, 2, 3, 4, 5], 2),
            [[1, 2], [2, 3], [3, 4], [4, 5]],
        )

    def test_size_equals_length(self):
        self.assertEqual(self.fn([1, 2, 3], 3), [[1, 2, 3]])

    def test_size_greater_than_length(self):
        self.assertEqual(self.fn([1, 2], 5), [])

    def test_window_count(self):
        seq = list(range(10))
        result = self.fn(seq, 4)
        self.assertEqual(len(result), len(seq) - 4 + 1)

    def test_size_one(self):
        self.assertEqual(self.fn([1, 2, 3], 1), [[1], [2], [3]])

    def test_empty_seq(self):
        self.assertEqual(self.fn([], 3), [])

    def test_size_zero_or_negative(self):
        self.assertEqual(self.fn([1, 2, 3], 0), [])
        self.assertEqual(self.fn([1, 2, 3], -1), [])

    def test_last_window_included(self):
        result = self.fn([10, 20, 30], 2)
        self.assertEqual(result[-1], [20, 30])

    def test_tuple_input(self):
        self.assertEqual(self.fn((1, 2, 3), 2), [[1, 2], [2, 3]])

    def test_single_element_seq_full_window(self):
        self.assertEqual(self.fn([7], 1), [[7]])


def main():
    if len(sys.argv) != 2:
        print("FAIL: usage check.py <workdir>")
        sys.exit(1)
    workdir = sys.argv[1]
    module = load_module(workdir)
    HiddenTests.fn = staticmethod(module.sliding_windows)

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
