"""Shared generator/reference for codefix_batch_chunks. Stays in
tasks_v2/, never copied into the subject's working directory."""
import random

SEED = 20260904

BUGGY_SOURCE = '''"""Split a list into fixed-size batches."""


def chunk(items, size):
    """Split `items` into consecutive batches of at most `size` items
    each, preserving order. Every item appears in exactly one batch. The
    final batch may be smaller than `size` if `len(items)` is not a
    multiple of `size` -- it must still be included, never dropped.
    Raises ValueError if `size` is less than 1. Returns [] for an empty
    `items`. Does not mutate the input list.
    """
    if size < 1:
        raise ValueError("size must be at least 1")
    n_batches = len(items) // size
    batches = []
    for i in range(n_batches):
        batches.append(items[i * size:(i + 1) * size])
    return batches
'''

FIXED_SOURCE = '''"""Split a list into fixed-size batches."""


def chunk(items, size):
    """Split `items` into consecutive batches of at most `size` items
    each, preserving order. Every item appears in exactly one batch. The
    final batch may be smaller than `size` if `len(items)` is not a
    multiple of `size` -- it must still be included, never dropped.
    Raises ValueError if `size` is less than 1. Returns [] for an empty
    `items`. Does not mutate the input list.
    """
    if size < 1:
        raise ValueError("size must be at least 1")
    batches = []
    for i in range(0, len(items), size):
        batches.append(items[i:i + size])
    return batches
'''

VISIBLE_TEST_SOURCE = '''import unittest

from chunker import chunk


class TestChunk(unittest.TestCase):
    def test_evenly_divisible(self):
        self.assertEqual(
            chunk([1, 2, 3, 4, 5, 6], 3),
            [[1, 2, 3], [4, 5, 6]],
        )

    def test_size_one(self):
        self.assertEqual(chunk([1, 2, 3], 1), [[1], [2], [3]])

    def test_empty(self):
        self.assertEqual(chunk([], 4), [])

    def test_invalid_size_raises(self):
        with self.assertRaises(ValueError):
            chunk([1, 2, 3], 0)


if __name__ == "__main__":
    unittest.main()
'''


def reference_chunk(items, size):
    if size < 1:
        raise ValueError("size must be at least 1")
    batches = []
    for i in range(0, len(items), size):
        batches.append(items[i:i + size])
    return batches


def hidden_cases(seed=SEED):
    """Deterministic list of {"items", "size"} cases. Planted: lengths not
    evenly divisible by size (final partial batch must survive), size
    exactly equal to len(items) (one full batch, no dropped remainder),
    size 1 greater than len(items), and size larger than len(items)."""
    rng = random.Random(seed)
    cases = []

    cases.append({"items": list(range(7)), "size": 3})   # 7 % 3 != 0 -> partial last batch
    cases.append({"items": list(range(5)), "size": 5})   # exactly one full batch
    cases.append({"items": list(range(5)), "size": 6})   # size > len
    cases.append({"items": [], "size": 1})
    cases.append({"items": list(range(1)), "size": 1})
    cases.append({"items": list(range(10)), "size": 4})  # 10 % 4 != 0
    cases.append({"items": [-1, -0, 0, 1], "size": 3})

    for _ in range(6):
        n = rng.randint(0, 15)
        size = rng.randint(1, 6)
        cases.append({"items": list(range(n)), "size": size})

    return cases
