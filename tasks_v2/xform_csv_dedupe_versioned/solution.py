import csv
import os
import sys


def main():
    workdir = sys.argv[1]
    in_path = os.path.join(workdir, "records.csv")
    winners = {}
    with open(in_path, newline="") as f:
        for row in csv.DictReader(f):
            key = row["key"]
            version = int(row["version"])
            seq = int(row["seq"])
            payload = row["payload"]
            cur = winners.get(key)
            if cur is None or (version, seq) > (cur[0], cur[1]):
                winners[key] = (version, seq, payload)

    out_path = os.path.join(workdir, "deduped.csv")
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["key", "version", "seq", "payload"])
        for key in sorted(winners):
            version, seq, payload = winners[key]
            writer.writerow([key, version, seq, payload])


if __name__ == "__main__":
    main()
