"""Shared generator/reference for codefix_skip_invalid. Stays in
tasks_v2/, never copied into the subject's working directory."""
import random

SEED = 20260904

BUGGY_SOURCE = '''"""Sum valid transaction amounts, skipping malformed records."""


def total_valid(records):
    """Given a list of record dicts, return (total, count) where `total`
    is the sum (as a float) of the "amount" field of every valid record,
    and `count` is how many records were valid.

    A record is malformed -- and must be skipped, not counted, without
    affecting any record processed after it -- if it has no "amount" key,
    or if its "amount" value cannot be parsed as a float (e.g. it is the
    string "N/A" or an empty string). Processing must continue with the
    remaining records after skipping a malformed one. An empty list of
    records returns (0.0, 0).
    """
    total = 0.0
    count = 0
    for r in records:
        if "amount" not in r:
            return total, count
        try:
            val = float(r["amount"])
        except (TypeError, ValueError):
            count += 0
            continue
        total += val
        count += 1
    return total, count
'''

FIXED_SOURCE = '''"""Sum valid transaction amounts, skipping malformed records."""


def total_valid(records):
    """Given a list of record dicts, return (total, count) where `total`
    is the sum (as a float) of the "amount" field of every valid record,
    and `count` is how many records were valid.

    A record is malformed -- and must be skipped, not counted, without
    affecting any record processed after it -- if it has no "amount" key,
    or if its "amount" value cannot be parsed as a float (e.g. it is the
    string "N/A" or an empty string). Processing must continue with the
    remaining records after skipping a malformed one. An empty list of
    records returns (0.0, 0).
    """
    total = 0.0
    count = 0
    for r in records:
        if "amount" not in r:
            continue
        try:
            val = float(r["amount"])
        except (TypeError, ValueError):
            continue
        total += val
        count += 1
    return total, count
'''

VISIBLE_TEST_SOURCE = '''import unittest

from ledger import total_valid


class TestTotalValid(unittest.TestCase):
    def test_all_valid(self):
        records = [{"amount": "10.00"}, {"amount": "5.50"}]
        self.assertEqual(total_valid(records), (15.5, 2))

    def test_missing_key_at_end(self):
        # the malformed record is last, so skip-and-stop and
        # skip-and-continue give the same answer here.
        records = [{"amount": "10.00"}, {"amount": "5.00"}, {"note": "oops"}]
        self.assertEqual(total_valid(records), (15.0, 2))

    def test_empty(self):
        self.assertEqual(total_valid([]), (0.0, 0))


if __name__ == "__main__":
    unittest.main()
'''


def reference_total_valid(records):
    total = 0.0
    count = 0
    for r in records:
        if "amount" not in r:
            continue
        try:
            val = float(r["amount"])
        except (TypeError, ValueError):
            continue
        total += val
        count += 1
    return total, count


def hidden_cases(seed=SEED):
    """Deterministic list of record-list cases. Planted: a malformed
    record (missing key, and separately a bad numeric string) placed in
    the MIDDLE of the list, so records after it are dropped by the
    early-return bug but must be included by a correct skip. Also plants
    two malformed records back to back, and a malformed record as the
    very first element."""
    rng = random.Random(seed)
    cases = []

    cases.append([
        {"amount": "10.00"},
        {"note": "malformed, missing key"},
        {"amount": "5.00"},
        {"amount": "2.50"},
    ])
    cases.append([
        {"amount": "1.00"},
        {"amount": "N/A"},
        {"amount": "3.00"},
    ])
    cases.append([
        {"note": "first record is malformed"},
        {"amount": "8.00"},
    ])
    cases.append([
        {"amount": "1.00"},
        {"note": "bad"},
        {"amount": "bad-number"},
        {"amount": "4.00"},
        {"amount": "5.00"},
    ])
    cases.append([{"amount": ""}, {"amount": "9.00"}])
    cases.append([])
    cases.append([{"amount": "0.00"}])

    for _ in range(6):
        n = rng.randint(2, 8)
        records = []
        for _ in range(n):
            choice = rng.random()
            if choice < 0.3:
                records.append({"note": "no amount field"})
            elif choice < 0.5:
                records.append({"amount": rng.choice(["bad", "", "N/A"])})
            else:
                records.append({"amount": f"{rng.uniform(-50, 50):.2f}"})
        cases.append(records)

    return [{"input": c} for c in cases]
