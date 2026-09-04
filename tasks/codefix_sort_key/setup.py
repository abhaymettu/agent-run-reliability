#!/usr/bin/env python3
"""setup.py <workdir> -- writes the buggy module and its visible test file."""
import sys
from pathlib import Path

RANKING_PY = '''"""Leaderboard ranking utility."""


def rank_entries(entries):
    """Given a list of (name, score) tuples, return a new list sorted for
    a leaderboard: highest score first. Ties (equal scores) are broken by
    name, ascending, case-insensitively (so "bob" and "Bob" sort as
    equal-case neighbors, ordered by their lowercase form). The input list
    is not modified.
    """
    return sorted(entries, key=lambda e: (e[1], e[0]))
'''

TEST_PY = '''import unittest

from ranking import rank_entries


class TestRankEntries(unittest.TestCase):
    def test_sorts_by_score_descending(self):
        entries = [("alice", 10), ("bob", 30), ("carol", 20)]
        self.assertEqual(
            rank_entries(entries),
            [("bob", 30), ("carol", 20), ("alice", 10)],
        )

    def test_ties_broken_by_name_ascending(self):
        entries = [("zeb", 50), ("amy", 50), ("mona", 50)]
        self.assertEqual(
            rank_entries(entries),
            [("amy", 50), ("mona", 50), ("zeb", 50)],
        )

    def test_ties_case_insensitive(self):
        entries = [("Bob", 5), ("alice", 5), ("Amy", 5)]
        self.assertEqual(
            rank_entries(entries),
            [("alice", 5), ("Amy", 5), ("Bob", 5)],
        )

    def test_does_not_mutate_input(self):
        entries = [("a", 1), ("b", 2)]
        original = list(entries)
        rank_entries(entries)
        self.assertEqual(entries, original)


if __name__ == "__main__":
    unittest.main()
'''


def main():
    if len(sys.argv) != 2:
        print("usage: setup.py <workdir>", file=sys.stderr)
        sys.exit(1)
    workdir = Path(sys.argv[1])
    (workdir / "ranking.py").write_bytes(RANKING_PY.encode("utf-8"))
    (workdir / "test_ranking.py").write_bytes(TEST_PY.encode("utf-8"))


if __name__ == "__main__":
    main()
