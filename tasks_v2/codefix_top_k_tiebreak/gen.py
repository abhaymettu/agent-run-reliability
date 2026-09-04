"""Shared generator/reference for codefix_top_k_tiebreak. Stays in
tasks_v2/, never copied into the subject's working directory."""
import random

SEED = 20260904

BUGGY_SOURCE = '''"""Rank entries and return the top k."""


def top_k(entries, k):
    """Return the top `k` entries by score, highest first.

    Each entry is a dict with "name" (str) and "score" (int). Ties in
    score are broken by name in ascending alphabetical order (so among
    equal scores, "alice" ranks above "bob"). If `k` is greater than or
    equal to len(entries), return all entries ranked. If `k` is 0, return
    an empty list. Does not mutate the input list.
    """
    ranked = sorted(
        entries,
        key=lambda e: (e["score"], e["name"]),
        reverse=True,
    )
    return ranked[:k]
'''

FIXED_SOURCE = '''"""Rank entries and return the top k."""


def top_k(entries, k):
    """Return the top `k` entries by score, highest first.

    Each entry is a dict with "name" (str) and "score" (int). Ties in
    score are broken by name in ascending alphabetical order (so among
    equal scores, "alice" ranks above "bob"). If `k` is greater than or
    equal to len(entries), return all entries ranked. If `k` is 0, return
    an empty list. Does not mutate the input list.
    """
    by_name = sorted(entries, key=lambda e: e["name"])
    ranked = sorted(by_name, key=lambda e: e["score"], reverse=True)
    return ranked[:k]
'''

VISIBLE_TEST_SOURCE = '''import unittest

from leaderboard import top_k


class TestTopK(unittest.TestCase):
    def test_distinct_scores(self):
        entries = [
            {"name": "alice", "score": 10},
            {"name": "bob", "score": 30},
            {"name": "carol", "score": 20},
        ]
        result = top_k(entries, 2)
        self.assertEqual([e["name"] for e in result], ["bob", "carol"])

    def test_k_zero(self):
        entries = [{"name": "alice", "score": 10}]
        self.assertEqual(top_k(entries, 0), [])

    def test_k_larger_than_entries(self):
        entries = [{"name": "alice", "score": 5}, {"name": "bob", "score": 9}]
        result = top_k(entries, 10)
        self.assertEqual([e["name"] for e in result], ["bob", "alice"])


if __name__ == "__main__":
    unittest.main()
'''


def reference_top_k(entries, k):
    by_name = sorted(entries, key=lambda e: e["name"])
    ranked = sorted(by_name, key=lambda e: e["score"], reverse=True)
    return ranked[:k]


def hidden_cases(seed=SEED):
    """Deterministic list of {"entries", "k"} cases. Planted: a score tie
    between two entries whose names are NOT already in alphabetical order
    in the input, a three-way tie, k landing exactly inside a tied group
    (cutting it), and k=0 / k>=len."""
    rng = random.Random(seed)
    cases = []

    cases.append({
        "entries": [{"name": "zeta", "score": 5}, {"name": "alpha", "score": 5}],
        "k": 2,
    })
    cases.append({
        "entries": [
            {"name": "dave", "score": 7},
            {"name": "carol", "score": 7},
            {"name": "bob", "score": 7},
            {"name": "alice", "score": 9},
        ],
        "k": 3,
    })
    cases.append({
        "entries": [
            {"name": "yara", "score": 3},
            {"name": "xena", "score": 3},
            {"name": "wade", "score": 1},
        ],
        "k": 1,
    })
    cases.append({"entries": [], "k": 0})
    cases.append({"entries": [{"name": "solo", "score": 1}], "k": 5})

    names = list("abcdefghij")
    for _ in range(6):
        n = rng.randint(2, 8)
        picked = rng.sample(names, k=n)
        scores = [rng.choice([1, 2, 2, 3]) for _ in picked]  # biased to create ties
        entries = [{"name": nm, "score": sc} for nm, sc in zip(picked, scores)]
        k = rng.randint(0, n)
        cases.append({"entries": entries, "k": k})

    return cases
