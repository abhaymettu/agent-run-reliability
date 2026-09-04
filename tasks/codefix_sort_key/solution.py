#!/usr/bin/env python3
"""solution.py <workdir> -- overwrites ranking.py with a correct fix, for
validation purposes only. Never shown to the subject agent."""
import sys
from pathlib import Path

FIXED = '''"""Leaderboard ranking utility."""


def rank_entries(entries):
    """Given a list of (name, score) tuples, return a new list sorted for
    a leaderboard: highest score first. Ties (equal scores) are broken by
    name, ascending, case-insensitively (so "bob" and "Bob" sort as
    equal-case neighbors, ordered by their lowercase form). The input list
    is not modified.
    """
    return sorted(entries, key=lambda e: (-e[1], e[0].lower()))
'''


def main():
    if len(sys.argv) != 2:
        print("usage: solution.py <workdir>", file=sys.stderr)
        sys.exit(1)
    workdir = Path(sys.argv[1])
    (workdir / "ranking.py").write_bytes(FIXED.encode("utf-8"))


if __name__ == "__main__":
    main()
