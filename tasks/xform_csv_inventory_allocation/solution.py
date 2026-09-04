import csv
import os
import sys


def main():
    workdir = sys.argv[1]
    remaining = {}
    with open(os.path.join(workdir, "stock.csv"), newline="") as f:
        for row in csv.DictReader(f):
            remaining[row["sku"]] = int(row["qty"])

    orders = []
    with open(os.path.join(workdir, "orders.csv"), newline="") as f:
        for row in csv.DictReader(f):
            orders.append({
                "seq": int(row["seq"]),
                "warehouse": row["warehouse"],
                "sku": row["sku"],
                "qty": int(row["qty"]),
            })

    orders.sort(key=lambda o: o["seq"])

    out_rows = []
    for o in orders:
        sku = o["sku"]
        req = o["qty"]
        if req < 0:
            remaining[sku] = remaining.get(sku, 0) - req
            allocated = req
        else:
            avail = remaining.get(sku, 0)
            allocated = min(req, avail)
            remaining[sku] = avail - allocated
        out_rows.append([o["seq"], o["warehouse"], sku, req, allocated])

    out_path = os.path.join(workdir, "allocations.csv")
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["seq", "warehouse", "sku", "requested", "allocated"])
        writer.writerows(out_rows)


if __name__ == "__main__":
    main()
