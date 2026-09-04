#!/usr/bin/env python3
"""setup.py <workdir> -- writes the buggy module and its visible test file."""
import sys
from pathlib import Path

BILLING_PY = '''"""Currency rounding and tax totals."""


def round_currency(amount):
    """Round a non-negative dollar amount to the nearest cent using
    round-half-up: a value exactly halfway between two cents (e.g. an
    amount ending in ...0.005) always rounds to the higher cent. This is
    NOT Python's default round-half-to-even behavior.
    """
    return round(amount, 2)


def total_with_tax(prices, tax_rate):
    """Given a list of non-negative dollar amounts `prices` and a
    non-negative `tax_rate` (e.g. 0.08 for 8% tax), compute the total
    owed as follows:

      1. For each price, compute its tax = price * tax_rate, and round
         that tax to the nearest cent with round_currency.
      2. Add the rounded tax to the price to get that line's total, and
         round the line's total to the nearest cent with round_currency.
      3. Sum all the rounded line totals, then round the final sum to the
         nearest cent with round_currency, and return it.

    Rounding must happen at each of these steps -- rounding only once at
    the very end on unrounded intermediate values gives the wrong answer
    whenever a per-line total falls exactly on a half-cent boundary.
    """
    total = 0.0
    for p in prices:
        tax = p * tax_rate
        total += p + tax
    return round_currency(total)
'''

TEST_PY = '''import unittest

from billing import round_currency, total_with_tax


class TestBilling(unittest.TestCase):
    def test_round_currency_half_up_basic(self):
        self.assertEqual(round_currency(1.005), 1.01)

    def test_round_currency_no_rounding_needed(self):
        self.assertEqual(round_currency(2.50), 2.50)

    def test_round_currency_rounds_down(self):
        self.assertEqual(round_currency(1.004), 1.00)

    def test_total_with_tax_simple(self):
        self.assertEqual(total_with_tax([10.00], 0.10), 11.00)

    def test_total_with_tax_half_cent_boundary(self):
        # Each item: tax = 0.10 * 0.05 = 0.005 -> rounds up to 0.01 per
        # item (half-up), giving a line total of 0.11 each, summing to
        # 0.22. Rounding only the raw float sum at the end gives 0.21.
        self.assertEqual(total_with_tax([0.10, 0.10], 0.05), 0.22)


if __name__ == "__main__":
    unittest.main()
'''


def main():
    if len(sys.argv) != 2:
        print("usage: setup.py <workdir>", file=sys.stderr)
        sys.exit(1)
    workdir = Path(sys.argv[1])
    (workdir / "billing.py").write_bytes(BILLING_PY.encode("utf-8"))
    (workdir / "test_billing.py").write_bytes(TEST_PY.encode("utf-8"))


if __name__ == "__main__":
    main()
