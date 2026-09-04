#!/usr/bin/env python3
"""check.py <workdir> -- runs a hidden superset test suite against the
agent's machine.py. Exits 0 only if every hidden test passes."""
import importlib.util
import signal
import sys
import unittest
from pathlib import Path


def load_module(workdir):
    path = Path(workdir) / "machine.py"
    if not path.exists() or path.stat().st_size == 0:
        print("FAIL: machine.py missing or empty")
        sys.exit(1)
    try:
        spec = importlib.util.spec_from_file_location("machine_under_test", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as exc:
        print(f"FAIL: could not import machine.py: {exc}")
        sys.exit(1)
    if not hasattr(module, "transition"):
        print("FAIL: transition is not defined")
        sys.exit(1)
    return module


class HiddenTests(unittest.TestCase):
    fn = None

    def test_unlock_from_locked(self):
        self.assertEqual(self.fn("locked", "unlock"), "unlocked")

    def test_lock_from_unlocked(self):
        self.assertEqual(self.fn("unlocked", "lock"), "locked")

    def test_open_from_unlocked(self):
        self.assertEqual(self.fn("unlocked", "open"), "open")

    def test_close_from_open(self):
        self.assertEqual(self.fn("open", "close"), "unlocked")

    def test_noop_lock_already_locked(self):
        self.assertEqual(self.fn("locked", "lock"), "locked")

    def test_noop_unlock_already_unlocked(self):
        self.assertEqual(self.fn("unlocked", "unlock"), "unlocked")

    def test_invalid_open_while_locked(self):
        with self.assertRaises(ValueError):
            self.fn("locked", "open")

    def test_invalid_close_while_locked(self):
        with self.assertRaises(ValueError):
            self.fn("locked", "close")

    def test_invalid_lock_while_open(self):
        with self.assertRaises(ValueError):
            self.fn("open", "lock")

    def test_invalid_unlock_while_open(self):
        with self.assertRaises(ValueError):
            self.fn("open", "unlock")

    def test_invalid_open_while_open(self):
        with self.assertRaises(ValueError):
            self.fn("open", "open")

    def test_invalid_close_while_unlocked(self):
        with self.assertRaises(ValueError):
            self.fn("unlocked", "close")

    def test_unknown_state_raises(self):
        with self.assertRaises(ValueError):
            self.fn("bogus", "unlock")

    def test_full_lifecycle(self):
        state = "locked"
        for event, expected in [
            ("unlock", "unlocked"),
            ("open", "open"),
            ("close", "unlocked"),
            ("lock", "locked"),
        ]:
            state = self.fn(state, event)
            self.assertEqual(state, expected)


def main():
    if len(sys.argv) != 2:
        print("FAIL: usage check.py <workdir>")
        sys.exit(1)
    workdir = sys.argv[1]
    module = load_module(workdir)
    HiddenTests.fn = staticmethod(module.transition)

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
