#!/usr/bin/env python3
"""solution.py <workdir> -- overwrites grouping.py with a correct fix, for
validation purposes only. Never shown to the subject agent."""
import sys
from pathlib import Path

FIXED = '''"""Group items by a key function."""


def group_by_key(items, key_func, groups=None):
    """Group `items` into a dict mapping key_func(item) -> list of items
    with that key, preserving each item's original relative order within
    its group. Returns a fresh dict; does not mutate any dict passed in
    via `groups` and is safe to call repeatedly with different `items`
    without state leaking between calls.
    """
    if groups is None:
        groups = {}
    for item in items:
        k = key_func(item)
        groups.setdefault(k, []).append(item)
    return groups
'''


def main():
    if len(sys.argv) != 2:
        print("usage: solution.py <workdir>", file=sys.stderr)
        sys.exit(1)
    workdir = Path(sys.argv[1])
    (workdir / "grouping.py").write_bytes(FIXED.encode("utf-8"))


if __name__ == "__main__":
    main()
