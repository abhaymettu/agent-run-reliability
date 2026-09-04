import csv
import os
import sys

from gen import generate


def main():
    workdir = sys.argv[1]
    rows = generate()
    path = os.path.join(workdir, "scores.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["employee_id", "score"])
        for r in rows:
            w.writerow([r["employee_id"], r["score"]])


if __name__ == "__main__":
    main()
