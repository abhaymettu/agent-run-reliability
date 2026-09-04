#!/usr/bin/env python3
"""solution.py <workdir> -- overwrites billing.py with a correct fix, for
validation purposes only. Never shown to the subject agent."""
import sys
from pathlib import Path

FIXED = '''"""Currency rounding and tax totals."""
from decimal import Decimal, ROUND_HALF_UP


def round_currency(amount):
    """Round a non-negative dollar amount to the nearest cent using
    round-half-up: a value exactly halfway between two cents (e.g. an
    amount ending in ...0.005) always rounds to the higher cent. This is
    NOT Python's default round-half-to-even behavior.
    """
    d = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return float(d)


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
        tax = round_currency(p * tax_rate)
        line_total = round_currency(p + tax)
        total += line_total
    return round_currency(total)
'''


def main():
    if len(sys.argv) != 2:
        print("usage: solution.py <workdir>", file=sys.stderr)
        sys.exit(1)
    workdir = Path(sys.argv[1])
    (workdir / "billing.py").write_bytes(FIXED.encode("utf-8"))


if __name__ == "__main__":
    main()
