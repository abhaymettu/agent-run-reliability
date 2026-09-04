import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, fmt_ts


def _write(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "name", "value", "updated_at"])
        for r in rows:
            w.writerow([r["id"], r["name"], r["value"], fmt_ts(r["updated_at"])])


def main():
    workdir = sys.argv[1]
    primary_rows, secondary_rows = generate()
    _write(os.path.join(workdir, "primary.csv"), primary_rows)
    _write(os.path.join(workdir, "secondary.csv"), secondary_rows)


if __name__ == "__main__":
    main()
