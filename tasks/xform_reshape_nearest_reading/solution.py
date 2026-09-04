import csv
import os
import sys


def main():
    workdir = sys.argv[1]
    readings = []
    with open(os.path.join(workdir, "readings.csv"), newline="") as f:
        for row in csv.DictReader(f):
            readings.append({
                "sensor_id": row["sensor_id"],
                "field": row["field"],
                "timestamp": int(row["timestamp"]),
                "value": row["value"],
            })

    targets = []
    with open(os.path.join(workdir, "targets.csv"), newline="") as f:
        for row in csv.DictReader(f):
            targets.append({
                "sensor_id": row["sensor_id"],
                "field": row["field"],
                "target_timestamp": int(row["target_timestamp"]),
            })

    out_rows = []
    for t in targets:
        sid, field, tgt = t["sensor_id"], t["field"], t["target_timestamp"]
        candidates = [
            r for r in readings if r["sensor_id"] == sid and r["field"] == field
        ]
        best = min(candidates, key=lambda r: (abs(r["timestamp"] - tgt), r["timestamp"]))
        out_rows.append([sid, field, best["timestamp"], best["value"]])

    out_path = os.path.join(workdir, "nearest.csv")
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["sensor_id", "field", "timestamp", "value"])
        writer.writerows(out_rows)


if __name__ == "__main__":
    main()
