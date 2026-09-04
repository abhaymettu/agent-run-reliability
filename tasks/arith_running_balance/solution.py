import csv
import os
import sys

START_BALANCE_CENTS = 100000
OVERDRAFT_LIMIT_CENTS = -50000


def to_cents(s):
    neg = s.startswith("-")
    s = s[1:] if neg else s
    dollars, cents = s.split(".")
    total = int(dollars) * 100 + int(cents)
    return -total if neg else total


def format_cents(cents):
    sign = "-" if cents < 0 else ""
    c = abs(cents)
    return f"{sign}{c // 100}.{c % 100:02d}"


def main():
    workdir = sys.argv[1]
    in_path = os.path.join(workdir, "transactions.csv")
    rows = []
    with open(in_path, newline="") as f:
        for row in csv.DictReader(f):
            rows.append((row["date"], to_cents(row["amount"])))

    balance = START_BALANCE_CENTS
    first_negative_date = None
    for date, amt in rows:
        if balance + amt >= OVERDRAFT_LIMIT_CENTS:
            balance += amt
        if first_negative_date is None and balance < 0:
            first_negative_date = date

    expected_date = first_negative_date if first_negative_date is not None else "none"
    out_path = os.path.join(workdir, "balance_result.txt")
    with open(out_path, "w") as f:
        f.write(f"first_negative_date={expected_date}\n")
        f.write(f"final_balance={format_cents(balance)}")


if __name__ == "__main__":
    main()
