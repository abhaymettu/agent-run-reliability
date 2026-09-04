"""Shared generator/reference for codefix_bucket_alias. Stays in
tasks_v2/, never copied into the subject's working directory."""
import random

SEED = 20260904

BUGGY_SOURCE = '''"""Bucket items into named groups."""


def bucket_items(items, key_func, keys):
    """Sort `items` into buckets, one per name in `keys`.

    `key_func(item)` returns the bucket name an item belongs to; it is
    guaranteed to be one of the names in `keys` for every item in `items`.
    Returns a dict mapping each name in `keys` to a list of the items
    whose key_func result equals that name, in their original relative
    order. A bucket for a name that no item maps to is an empty list. Each
    bucket's list is independent: appending to one bucket must never
    affect any other bucket's contents.
    """
    template = []
    buckets = dict.fromkeys(keys, template)
    for item in items:
        buckets[key_func(item)].append(item)
    return buckets
'''

FIXED_SOURCE = '''"""Bucket items into named groups."""


def bucket_items(items, key_func, keys):
    """Sort `items` into buckets, one per name in `keys`.

    `key_func(item)` returns the bucket name an item belongs to; it is
    guaranteed to be one of the names in `keys` for every item in `items`.
    Returns a dict mapping each name in `keys` to a list of the items
    whose key_func result equals that name, in their original relative
    order. A bucket for a name that no item maps to is an empty list. Each
    bucket's list is independent: appending to one bucket must never
    affect any other bucket's contents.
    """
    buckets = {k: [] for k in keys}
    for item in items:
        buckets[key_func(item)].append(item)
    return buckets
'''

VISIBLE_TEST_SOURCE = '''import unittest

from buckets import bucket_items


class TestBucketItems(unittest.TestCase):
    def test_single_key_all_items(self):
        result = bucket_items([1, 2, 3], lambda x: "only", ["only"])
        self.assertEqual(result["only"], [1, 2, 3])

    def test_item_lands_in_its_own_bucket(self):
        result = bucket_items(
            ["apple", "banana", "avocado"], lambda s: s[0], ["a", "b"]
        )
        self.assertIn("apple", result["a"])
        self.assertIn("avocado", result["a"])
        self.assertIn("banana", result["b"])

    def test_empty_items(self):
        result = bucket_items([], lambda x: x, ["a", "b"])
        self.assertEqual(result["a"], [])
        self.assertEqual(result["b"], [])


if __name__ == "__main__":
    unittest.main()
'''


def reference_bucket(items, key_func, keys):
    buckets = {k: [] for k in keys}
    for item in items:
        buckets[key_func(item)].append(item)
    return buckets


def hidden_cases(seed=SEED):
    """Deterministic list of {"items", "keys"} cases, each paired with a
    key function name ("first_char" or "mod"). Planted: at least two
    distinct non-empty buckets checked for mutual EXCLUSION (an item in
    bucket A must be absent from bucket B), which the shipped tests never
    assert -- they only ever check that an item IS present somewhere,
    never that it is absent from a bucket it does not belong to. Also
    plants an unused (empty) bucket name and a bucket receiving every
    item but one."""
    rng = random.Random(seed)
    cases = []

    cases.append({
        "keyfn": "first_char",
        "items": ["apple", "banana", "avocado", "blueberry", "cherry"],
        "keys": ["a", "b", "c", "d"],
    })
    cases.append({
        "keyfn": "mod3",
        "items": list(range(9)),
        "keys": [0, 1, 2],
    })
    cases.append({
        "keyfn": "mod3",
        "items": [0, 3, 6, 9],
        "keys": [0, 1, 2],
    })
    cases.append({
        "keyfn": "first_char",
        "items": [],
        "keys": ["a", "b"],
    })
    cases.append({
        "keyfn": "first_char",
        "items": ["xylophone"],
        "keys": ["x", "y", "z"],
    })

    for _ in range(6):
        n = rng.randint(2, 10)
        items = [rng.randint(0, 8) for _ in range(n)]
        cases.append({"keyfn": "mod3", "items": items, "keys": [0, 1, 2]})

    return cases


def apply_keyfn(name, item):
    if name == "first_char":
        return item[0]
    if name == "mod3":
        return item % 3
    raise ValueError(f"unknown keyfn {name}")
