#!/usr/bin/env python3
"""setup.py <workdir> -- writes the buggy module and its visible test file."""
import sys
from pathlib import Path

MACHINE_PY = '''"""A small door-lock state machine."""

_STATES = ("locked", "unlocked", "open")

_TRANSITIONS = {
    ("locked", "unlock"): "open",
    ("unlocked", "lock"): "open",
    ("unlocked", "open"): "open",
    ("locked", "lock"): "locked",
    ("unlocked", "unlock"): "unlocked",
}


def transition(state, event):
    """Given the current state ("locked", "unlocked", or "open") and an
    event ("lock", "unlock", "open", or "close"), return the next state.

    Valid transitions:
      locked   + unlock -> unlocked
      unlocked + lock   -> locked
      unlocked + open   -> open
      open     + close  -> unlocked

    No-op transitions (the state does not change, but the transition is
    still valid, not an error):
      locked   + lock   -> locked
      unlocked + unlock -> unlocked

    Every other (state, event) pair -- including any event while the door
    is "open" other than "close" -- is invalid and must raise ValueError.
    An unrecognized state also raises ValueError.
    """
    if state not in _STATES:
        raise ValueError(f"unknown state: {state}")
    key = (state, event)
    if key in _TRANSITIONS:
        return _TRANSITIONS[key]
    raise ValueError(f"invalid transition: {state} + {event}")
'''

TEST_PY = '''import unittest

from machine import transition


class TestTransition(unittest.TestCase):
    def test_unlock_from_locked(self):
        self.assertEqual(transition("locked", "unlock"), "unlocked")

    def test_lock_from_unlocked(self):
        self.assertEqual(transition("unlocked", "lock"), "locked")

    def test_open_from_unlocked(self):
        self.assertEqual(transition("unlocked", "open"), "open")

    def test_close_from_open(self):
        self.assertEqual(transition("open", "close"), "unlocked")

    def test_noop_lock_already_locked(self):
        self.assertEqual(transition("locked", "lock"), "locked")

    def test_noop_unlock_already_unlocked(self):
        self.assertEqual(transition("unlocked", "unlock"), "unlocked")

    def test_invalid_open_while_locked(self):
        with self.assertRaises(ValueError):
            transition("locked", "open")

    def test_invalid_lock_while_open(self):
        with self.assertRaises(ValueError):
            transition("open", "lock")


if __name__ == "__main__":
    unittest.main()
'''


def main():
    if len(sys.argv) != 2:
        print("usage: setup.py <workdir>", file=sys.stderr)
        sys.exit(1)
    workdir = Path(sys.argv[1])
    (workdir / "machine.py").write_bytes(MACHINE_PY.encode("utf-8"))
    (workdir / "test_machine.py").write_bytes(TEST_PY.encode("utf-8"))


if __name__ == "__main__":
    main()
