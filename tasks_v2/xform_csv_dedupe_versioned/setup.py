import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate  # noqa: E402


def main():
    workdir = sys.argv[1]
    rows = generate()
    with open(os.path.join(workdir, "records.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["key", "version", "seq", "payload"])
        for r in rows:
            writer.writerow([r["key"], r["version"], r["seq"], r["payload"]])


if __name__ == "__main__":
    main()
