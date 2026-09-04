#!/usr/bin/env python3
"""solution.py <workdir> -- overwrites machine.py with a correct fix, for
validation purposes only. Never shown to the subject agent."""
import sys
from pathlib import Path

FIXED = '''"""A small door-lock state machine."""

_STATES = ("locked", "unlocked", "open")

_TRANSITIONS = {
    ("locked", "unlock"): "unlocked",
    ("unlocked", "lock"): "locked",
    ("unlocked", "open"): "open",
    ("open", "close"): "unlocked",
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


def main():
    if len(sys.argv) != 2:
        print("usage: solution.py <workdir>", file=sys.stderr)
        sys.exit(1)
    workdir = Path(sys.argv[1])
    (workdir / "machine.py").write_bytes(FIXED.encode("utf-8"))


if __name__ == "__main__":
    main()
