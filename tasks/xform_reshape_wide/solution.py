import csv
import os
import sys


def main():
    workdir = sys.argv[1]
    last = {}
    ids = []
    seen_ids = set()
    attrs = set()

    with open(os.path.join(workdir, "measurements.csv"), newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = row["id"]
            attr = row["attribute"]
            value = row["value"]
            last[(sid, attr)] = value
            attrs.add(attr)
            if sid not in seen_ids:
                seen_ids.add(sid)
                ids.append(sid)

    attr_list = sorted(attrs)
    with open(os.path.join(workdir, "measurements_wide.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id"] + attr_list)
        for sid in sorted(seen_ids):
            row = [sid] + [last.get((sid, a), "") for a in attr_list]
            w.writerow(row)


if __name__ == "__main__":
    main()
