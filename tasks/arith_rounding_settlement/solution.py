import csv
import os
import sys
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP

CENT = Decimal("0.01")
FEE_RATE = Decimal("0.015")


def format_amount(value_cents):
    if value_cents == 0:
        return "0.00"
    sign = "-" if value_cents < 0 else ""
    c = abs(value_cents)
    return f"{sign}{c // 100}.{c % 100:02d}"


def main():
    workdir = sys.argv[1]
    rates = {}
    with open(os.path.join(workdir, "rates.csv"), newline="") as f:
        for row in csv.DictReader(f):
            rates[row["currency"]] = Decimal(row["rate"])

    total_cents = 0
    with open(os.path.join(workdir, "charges.csv"), newline="") as f:
        for row in csv.DictReader(f):
            amount = Decimal(row["amount"])
            rate = rates[row["currency"]]
            converted = (amount * rate).quantize(CENT, rounding=ROUND_HALF_EVEN)
            total_cents += int(converted * 100)

    total = Decimal(total_cents) / 100
    fee = (total * FEE_RATE).quantize(CENT, rounding=ROUND_HALF_UP)
    net = total - fee
    net_cents = int(net * 100)
    if net_cents == 0:
        net_cents = 0

    out_path = os.path.join(workdir, "settlement_result.txt")
    with open(out_path, "w") as f:
        f.write(f"net_payout={format_amount(net_cents)}")


if __name__ == "__main__":
    main()
