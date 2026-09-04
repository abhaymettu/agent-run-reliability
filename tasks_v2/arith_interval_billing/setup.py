import csv
import os
import sys

from gen import generate, _hm


def main():
    workdir = sys.argv[1]
    rows = generate()
    path = os.path.join(workdir, "reservations.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["room", "reservation_id", "start", "end"])
        for r in rows:
            w.writerow([r["room"], r["reservation_id"], _hm(r["start_min"]), _hm(r["end_min"])])


if __name__ == "__main__":
    main()
