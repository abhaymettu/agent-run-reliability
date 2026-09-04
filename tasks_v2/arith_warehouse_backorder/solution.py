import csv
import os
import sys

STOCK_START = 100


def main():
    workdir = sys.argv[1]
    in_path = os.path.join(workdir, "events.csv")
    rows = []
    with open(in_path, newline="") as f:
        for row in csv.DictReader(f):
            rows.append(row)

    stock = STOCK_START
    total_fulfilled = 0
    total_backordered = 0
    first_partial = None
    for row in rows:
        qty = int(row["qty"])
        if row["type"] == "restock":
            stock += qty
            continue
        if stock >= qty:
            fulfilled = qty
            stock -= qty
        elif stock > 0:
            fulfilled = stock
            stock = 0
        else:
            fulfilled = 0
        backordered = qty - fulfilled
        total_fulfilled += fulfilled
        total_backordered += backordered
        if first_partial is None and 0 < fulfilled < qty:
            first_partial = row["order_id"]

    expected_fp = first_partial if first_partial is not None else "none"
    out_path = os.path.join(workdir, "warehouse_result.txt")
    with open(out_path, "w") as f:
        f.write(f"total_fulfilled={total_fulfilled}\n")
        f.write(f"total_backordered={total_backordered}\n")
        f.write(f"final_stock={stock}\n")
        f.write(f"first_partial_order={expected_fp}")


if __name__ == "__main__":
    main()
