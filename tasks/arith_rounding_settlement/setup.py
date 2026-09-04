import csv
import os
import sys

from gen import generate, RATES


def main():
    workdir = sys.argv[1]
    rows = generate()

    charges_path = os.path.join(workdir, "charges.csv")
    with open(charges_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["charge_id", "amount", "currency"])
        for r in rows:
            w.writerow([r["charge_id"], f"{r['amount']:.2f}", r["currency"]])

    rates_path = os.path.join(workdir, "rates.csv")
    with open(rates_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["currency", "rate"])
        for cur in sorted(RATES.keys()):
            w.writerow([cur, str(RATES[cur])])


if __name__ == "__main__":
    main()
