import csv
import os
import sys


def to_min(hm):
    h, m = hm.split(":")
    return int(h) * 60 + int(m)


def main():
    workdir = sys.argv[1]
    in_path = os.path.join(workdir, "reservations.csv")
    by_room = {}
    with open(in_path, newline="") as f:
        for row in csv.DictReader(f):
            by_room.setdefault(row["room"], []).append(
                (to_min(row["start"]), to_min(row["end"]))
            )

    result = {}
    for room, intervals in by_room.items():
        events = []
        for s, e in intervals:
            events.append((s, 1))
            events.append((e, -1))
        events.sort()
        overlap = 0
        count = 0
        prev_t = None
        for t, delta in events:
            if prev_t is not None and count >= 2:
                overlap += t - prev_t
            count += delta
            prev_t = t
        result[room] = overlap

    rooms_sorted = sorted(result.keys())
    max_val = max(result.values())
    max_room = min(r for r in rooms_sorted if result[r] == max_val)

    out_path = os.path.join(workdir, "billing_result.txt")
    with open(out_path, "w") as f:
        for room in rooms_sorted:
            f.write(f"{room}={result[room]}\n")
        f.write(f"max_room={max_room}\n")


if __name__ == "__main__":
    main()
