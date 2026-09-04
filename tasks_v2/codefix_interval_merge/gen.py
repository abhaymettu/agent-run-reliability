"""Shared generator/reference for codefix_interval_merge. Stays in
tasks_v2/, never copied into the subject's working directory."""
import random

SEED = 20260904

BUGGY_SOURCE = '''"""Merge overlapping (and touching) intervals."""


def merge_intervals(intervals):
    """Given a list of [start, end] pairs (integers, start <= end for each
    pair), return a new list of merged [start, end] pairs, sorted by start,
    covering the same set of integer points with the fewest intervals.

    Two intervals must be merged into one whenever they overlap OR merely
    touch: if one interval ends exactly where the next begins (end == next
    start), they describe a single contiguous range and must be combined,
    not kept separate. Does not mutate the input list. Returns [] for an
    empty input.
    """
    if not intervals:
        return []
    ordered = sorted(intervals, key=lambda iv: iv[0])
    merged = [list(ordered[0])]
    for start, end in ordered[1:]:
        last = merged[-1]
        if start < last[1]:
            last[1] = max(last[1], end)
        else:
            merged.append([start, end])
    return merged
'''

FIXED_SOURCE = '''"""Merge overlapping (and touching) intervals."""


def merge_intervals(intervals):
    """Given a list of [start, end] pairs (integers, start <= end for each
    pair), return a new list of merged [start, end] pairs, sorted by start,
    covering the same set of integer points with the fewest intervals.

    Two intervals must be merged into one whenever they overlap OR merely
    touch: if one interval ends exactly where the next begins (end == next
    start), they describe a single contiguous range and must be combined,
    not kept separate. Does not mutate the input list. Returns [] for an
    empty input.
    """
    if not intervals:
        return []
    ordered = sorted(intervals, key=lambda iv: iv[0])
    merged = [list(ordered[0])]
    for start, end in ordered[1:]:
        last = merged[-1]
        if start <= last[1]:
            last[1] = max(last[1], end)
        else:
            merged.append([start, end])
    return merged
'''

VISIBLE_TEST_SOURCE = '''import unittest

from intervals import merge_intervals


class TestMergeIntervals(unittest.TestCase):
    def test_clear_overlap(self):
        self.assertEqual(
            merge_intervals([[1, 5], [3, 7]]),
            [[1, 7]],
        )

    def test_clear_gap_stays_separate(self):
        self.assertEqual(
            merge_intervals([[1, 3], [10, 12]]),
            [[1, 3], [10, 12]],
        )

    def test_unsorted_input(self):
        self.assertEqual(
            merge_intervals([[8, 10], [1, 2], [4, 6]]),
            [[1, 2], [4, 6], [8, 10]],
        )

    def test_empty(self):
        self.assertEqual(merge_intervals([]), [])


if __name__ == "__main__":
    unittest.main()
'''


def reference_merge(intervals):
    if not intervals:
        return []
    ordered = sorted(intervals, key=lambda iv: iv[0])
    merged = [list(ordered[0])]
    for start, end in ordered[1:]:
        last = merged[-1]
        if start <= last[1]:
            last[1] = max(last[1], end)
        else:
            merged.append([start, end])
    return merged


def hidden_cases(seed=SEED):
    """Deterministic list of interval-list cases. Planted: intervals that
    exactly touch (must merge), a single interval, an interval fully
    contained within another, three intervals that chain-merge via a touch
    in the middle, negative coordinates, and duplicate intervals."""
    rng = random.Random(seed)
    cases = []

    cases.append([])
    cases.append([[5, 5]])
    cases.append([[1, 5], [5, 9]])          # exact touch, must merge -> [[1,9]]
    cases.append([[1, 5], [5, 5], [6, 9]])  # touch then gap
    cases.append([[1, 10], [2, 4]])         # fully contained
    cases.append([[1, 3], [3, 6], [6, 9]])  # chain of touches
    cases.append([[-5, -2], [-2, 0], [1, 2]])  # touch at negative boundary, then gap
    cases.append([[3, 8], [1, 3]])          # unsorted + touch
    cases.append([[2, 4], [2, 4]])          # exact duplicates

    for _ in range(6):
        n = rng.randint(1, 6)
        pts = sorted(rng.sample(range(-20, 20), k=2 * n))
        ivs = [[pts[2 * i], pts[2 * i + 1]] for i in range(n)]
        rng.shuffle(ivs)
        cases.append(ivs)

    return [{"input": c} for c in cases]
