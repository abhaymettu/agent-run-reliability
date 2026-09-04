import csv
import os
import sys

from gen import generate


def main():
    workdir = sys.argv[1]
    rows = generate()
    path = os.path.join(workdir, "votes.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["party", "votes"])
        for r in rows:
            w.writerow([r["party"], r["votes"]])


if __name__ == "__main__":
    main()
