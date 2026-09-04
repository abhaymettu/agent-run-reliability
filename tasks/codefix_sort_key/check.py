#!/usr/bin/env python3
"""check.py <workdir> -- runs a hidden superset test suite against the
agent's ranking.py. Exits 0 only if every hidden test passes."""
import importlib.util
import signal
import sys
import unittest
from pathlib import Path


def load_module(workdir):
    path = Path(workdir) / "ranking.py"
    if not path.exists() or path.stat().st_size == 0:
        print("FAIL: ranking.py missing or empty")
        sys.exit(1)
    try:
        spec = importlib.util.spec_from_file_location("ranking_under_test", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as exc:
        print(f"FAIL: could not import ranking.py: {exc}")
        sys.exit(1)
    if not hasattr(module, "rank_entries"):
        print("FAIL: rank_entries is not defined")
        sys.exit(1)
    return module


class HiddenTests(unittest.TestCase):
    fn = None

    def test_sorts_by_score_descending(self):
        entries = [("alice", 10), ("bob", 30), ("carol", 20)]
        self.assertEqual(
            self.fn(entries),
            [("bob", 30), ("carol", 20), ("alice", 10)],
        )

    def test_ties_broken_by_name_ascending(self):
        entries = [("zeb", 50), ("amy", 50), ("mona", 50)]
        self.assertEqual(
            self.fn(entries),
            [("amy", 50), ("mona", 50), ("zeb", 50)],
        )

    def test_ties_case_insensitive(self):
        entries = [("Bob", 5), ("alice", 5), ("Amy", 5)]
        self.assertEqual(
            self.fn(entries),
            [("alice", 5), ("Amy", 5), ("Bob", 5)],
        )

    def test_does_not_mutate_input(self):
        entries = [("a", 1), ("b", 2)]
        original = list(entries)
        self.fn(entries)
        self.assertEqual(entries, original)

    def test_mixed_case_and_score_ties(self):
        entries = [
            ("Delta", 10), ("alpha", 20), ("bravo", 20), ("Charlie", 10)
        ]
        self.assertEqual(
            self.fn(entries),
            [("alpha", 20), ("bravo", 20), ("Charlie", 10), ("Delta", 10)],
        )

    def test_negative_scores(self):
        entries = [("x", -5), ("y", -1), ("z", -10)]
        self.assertEqual(
            self.fn(entries),
            [("y", -1), ("x", -5), ("z", -10)],
        )

    def test_single_entry(self):
        self.assertEqual(self.fn([("only", 1)]), [("only", 1)])

    def test_empty(self):
        self.assertEqual(self.fn([]), [])

    def test_all_same_name_different_case(self):
        entries = [("BOB", 1), ("bob", 1), ("Bob", 1)]
        # All keys equal after lowering; a stable sort preserves input order.
        self.assertEqual(
            self.fn(entries), [("BOB", 1), ("bob", 1), ("Bob", 1)]
        )


def main():
    if len(sys.argv) != 2:
        print("FAIL: usage check.py <workdir>")
        sys.exit(1)
    workdir = sys.argv[1]
    module = load_module(workdir)
    HiddenTests.fn = staticmethod(module.rank_entries)

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
