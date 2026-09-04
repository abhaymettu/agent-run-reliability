#!/usr/bin/env python3
"""check.py <workdir> -- runs a hidden superset test suite against the
agent's billing.py. Exits 0 only if every hidden test passes."""
import importlib.util
import signal
import sys
import unittest
from pathlib import Path


def load_module(workdir):
    path = Path(workdir) / "billing.py"
    if not path.exists() or path.stat().st_size == 0:
        print("FAIL: billing.py missing or empty")
        sys.exit(1)
    try:
        spec = importlib.util.spec_from_file_location("billing_under_test", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as exc:
        print(f"FAIL: could not import billing.py: {exc}")
        sys.exit(1)
    for name in ("round_currency", "total_with_tax"):
        if not hasattr(module, name):
            print(f"FAIL: {name} is not defined")
            sys.exit(1)
    return module


class HiddenTests(unittest.TestCase):
    round_currency = None
    total_with_tax = None

    def test_round_currency_half_up_basic(self):
        self.assertEqual(self.round_currency(1.005), 1.01)

    def test_round_currency_no_rounding_needed(self):
        self.assertEqual(self.round_currency(2.50), 2.50)

    def test_round_currency_rounds_down(self):
        self.assertEqual(self.round_currency(1.004), 1.00)

    def test_round_currency_zero(self):
        self.assertEqual(self.round_currency(0.0), 0.0)

    def test_round_currency_another_half_boundary(self):
        self.assertEqual(self.round_currency(3.145), 3.15)

    def test_round_currency_far_below_half(self):
        self.assertEqual(self.round_currency(0.001), 0.00)

    def test_total_with_tax_simple(self):
        self.assertEqual(self.total_with_tax([10.00], 0.10), 11.00)

    def test_total_with_tax_half_cent_boundary(self):
        self.assertEqual(self.total_with_tax([0.10, 0.10], 0.05), 0.22)

    def test_total_with_tax_zero_rate(self):
        self.assertEqual(self.total_with_tax([5.00, 3.00], 0.0), 8.00)

    def test_total_with_tax_multiple_items(self):
        self.assertEqual(
            self.total_with_tax([0.10, 0.10, 0.10, 0.10], 0.05), 0.44
        )

    def test_total_with_tax_empty(self):
        self.assertEqual(self.total_with_tax([], 0.08), 0.0)

    def test_total_with_tax_larger_amounts(self):
        # 19.99 * 0.0825 = 1.6491750... -> tax rounds to 1.65 (half not
        # exactly on boundary here, but rounding order still matters)
        self.assertEqual(self.total_with_tax([19.99], 0.0825), 21.64)


def main():
    if len(sys.argv) != 2:
        print("FAIL: usage check.py <workdir>")
        sys.exit(1)
    workdir = sys.argv[1]
    module = load_module(workdir)
    HiddenTests.round_currency = staticmethod(module.round_currency)
    HiddenTests.total_with_tax = staticmethod(module.total_with_tax)

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
