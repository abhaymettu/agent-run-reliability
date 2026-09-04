import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate


def main():
    workdir = sys.argv[1]
    rows = generate()
    path = os.path.join(workdir, "measurements.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "attribute", "value"])
        for sid, attr, value in rows:
            w.writerow([sid, attr, value])


if __name__ == "__main__":
    main()
