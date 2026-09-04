"""Shared generator/reference for codefix_median_sort. Stays in tasks_v2/,
never copied into the subject's working directory."""
import random

SEED = 20260904

BUGGY_SOURCE = '''"""Median of a list of numbers."""


def median(numbers):
    """Return the median of `numbers`.

    The median is the middle value once the numbers are sorted. For a
    list with an odd number of elements, return that single middle value.
    For a list with an even number of elements, return the exact
    arithmetic average of the two middle values, as a float (so the two
    middle values 3 and 4 average to 3.5, not 3). Raises ValueError on an
    empty list. Does not require the input to already be sorted, and does
    not mutate the input list.
    """
    if not numbers:
        raise ValueError("median of empty list")
    n = len(numbers)
    mid = n // 2
    if n % 2 == 1:
        return numbers[mid]
    return (numbers[mid - 1] + numbers[mid]) // 2
'''

FIXED_SOURCE = '''"""Median of a list of numbers."""


def median(numbers):
    """Return the median of `numbers`.

    The median is the middle value once the numbers are sorted. For a
    list with an odd number of elements, return that single middle value.
    For a list with an even number of elements, return the exact
    arithmetic average of the two middle values, as a float (so the two
    middle values 3 and 4 average to 3.5, not 3). Raises ValueError on an
    empty list. Does not require the input to already be sorted, and does
    not mutate the input list.
    """
    if not numbers:
        raise ValueError("median of empty list")
    s = sorted(numbers)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2
'''

VISIBLE_TEST_SOURCE = '''import unittest

from stats import median


class TestMedian(unittest.TestCase):
    def test_odd_length_sorted_input(self):
        self.assertEqual(median([1, 2, 3, 4, 5]), 3)

    def test_even_length_sorted_input(self):
        self.assertEqual(median([1, 2, 4, 5]), 3.0)

    def test_single_element(self):
        self.assertEqual(median([7]), 7)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            median([])


if __name__ == "__main__":
    unittest.main()
'''


def reference_median(numbers):
    if not numbers:
        raise ValueError("median of empty list")
    s = sorted(numbers)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2


def hidden_cases(seed=SEED):
    """Deterministic list of {"input": [...]} cases, none of them
    pre-sorted, planted so the shipped tests' blind spots (unsorted input,
    an even-length list whose middle two values sum to an odd number,
    duplicates, negatives) are all covered."""
    rng = random.Random(seed)
    cases = []

    # Planted: unsorted odd-length list.
    cases.append([5, 1, 4, 2, 3])
    # Planted: unsorted even-length list whose sorted middle two sum to an
    # odd number -> integer division and float division disagree.
    cases.append([10, 1, 2, 3])  # sorted: [1,2,3,10] -> (2+3)/2=2.5 vs //2=2
    # Planted: single element, unsorted N/A.
    cases.append([42])
    # Planted: duplicates.
    cases.append([3, 3, 3, 3])
    # Planted: negative numbers, unsorted, odd sum at middle.
    cases.append([-1, -10, 3, 2])  # sorted: [-10,-1,2,3] -> (-1+2)/2=0.5 vs //2 floors to -1 (wrong sign too)
    # Planted: two-element list.
    cases.append([8, 3])  # sorted [3,8] -> 5.5

    for _ in range(8):
        n = rng.randint(1, 9)
        vals = [rng.randint(-50, 50) for _ in range(n)]
        rng.shuffle(vals)
        cases.append(vals)

    return [{"input": c} for c in cases]
