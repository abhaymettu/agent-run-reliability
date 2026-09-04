import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate  # noqa: E402


def main():
    workdir = sys.argv[1]
    readings, targets = generate()

    with open(os.path.join(workdir, "readings.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["sensor_id", "field", "timestamp", "value"])
        for r in readings:
            writer.writerow([r["sensor_id"], r["field"], r["timestamp"], r["value"]])

    with open(os.path.join(workdir, "targets.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["sensor_id", "field", "target_timestamp"])
        for t in targets:
            writer.writerow([t["sensor_id"], t["field"], t["target_timestamp"]])


if __name__ == "__main__":
    main()
