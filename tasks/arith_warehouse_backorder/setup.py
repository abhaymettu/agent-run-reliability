import csv
import os
import sys

from gen import generate


def main():
    workdir = sys.argv[1]
    events = generate()
    path = os.path.join(workdir, "events.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["seq", "type", "order_id", "qty"])
        for e in events:
            oid = e["order_id"] if e["order_id"] is not None else ""
            w.writerow([e["seq"], e["type"], oid, e["qty"]])


if __name__ == "__main__":
    main()
