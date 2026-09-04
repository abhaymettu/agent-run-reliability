import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import group_medians  # noqa: E402


def main():
    workdir = sys.argv[1]
    in_path = os.path.join(workdir, "records.csv")
    records = []
    with open(in_path, newline="") as f:
        for row in csv.DictReader(f):
            records.append({
                "id": int(row["id"]),
                "group": row["group"],
                "value": int(row["value"]),
            })

    medians = group_medians(records)
    out_path = os.path.join(workdir, "median_by_group.csv")
    with open(out_path, "w", newline="") as f:
        f.write("group,median\n")
        for g in sorted(medians.keys()):
            f.write(f"{g},{medians[g]:.1f}\n")


if __name__ == "__main__":
    main()
