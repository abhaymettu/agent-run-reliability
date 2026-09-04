import csv
import os
import sys

from gen import generate


def main():
    workdir = sys.argv[1]
    records = generate()
    path = os.path.join(workdir, "records.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "x", "y", "z"])
        for r in records:
            w.writerow([r["id"], r["x"], r["y"], r["z"]])


if __name__ == "__main__":
    main()
