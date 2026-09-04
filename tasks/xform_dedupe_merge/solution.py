import csv
import os
import sys


def _read(path):
    with open(path, newline="") as f:
        return {row["id"]: row for row in csv.DictReader(f)}


def main():
    workdir = sys.argv[1]
    primary = _read(os.path.join(workdir, "primary.csv"))
    secondary = _read(os.path.join(workdir, "secondary.csv"))
    all_ids = set(primary) | set(secondary)

    with open(os.path.join(workdir, "merged.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "name", "value", "updated_at"])
        for rid in sorted(all_ids):
            p = primary.get(rid)
            s = secondary.get(rid)
            if p and not s:
                chosen = p
            elif s and not p:
                chosen = s
            else:
                chosen = s if s["updated_at"] >= p["updated_at"] else p
            w.writerow([chosen["id"], chosen["name"], chosen["value"], chosen["updated_at"]])


if __name__ == "__main__":
    main()
