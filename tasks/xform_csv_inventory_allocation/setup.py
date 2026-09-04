import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate  # noqa: E402


def main():
    workdir = sys.argv[1]
    stock, orders = generate()

    with open(os.path.join(workdir, "stock.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["sku", "qty"])
        for s in stock:
            writer.writerow([s["sku"], s["qty"]])

    with open(os.path.join(workdir, "orders.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["seq", "warehouse", "sku", "qty"])
        for o in orders:
            writer.writerow([o["seq"], o["warehouse"], o["sku"], o["qty"]])


if __name__ == "__main__":
    main()
