import csv
import os
import re
import sys

LINE_RE = re.compile(
    r"^(?P<ts>\S+) (?P<req>\S+) (?P<method>\S+) (?P<path>\S+) (?P<dur>\d+)ms$"
)

TOP_N = 12


def main():
    workdir = sys.argv[1]
    rows = []
    with open(os.path.join(workdir, "access.log")) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            m = LINE_RE.match(line)
            if not m:
                continue
            rows.append({
                "timestamp": m.group("ts"),
                "request_id": m.group("req"),
                "path": m.group("path"),
                "duration_ms": int(m.group("dur")),
            })

    ordered = sorted(rows, key=lambda r: (-r["duration_ms"], r["request_id"]))
    top = ordered[:TOP_N]

    with open(os.path.join(workdir, "slowest.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["request_id", "duration_ms", "timestamp", "path"])
        for r in top:
            w.writerow([r["request_id"], r["duration_ms"], r["timestamp"], r["path"]])


if __name__ == "__main__":
    main()
