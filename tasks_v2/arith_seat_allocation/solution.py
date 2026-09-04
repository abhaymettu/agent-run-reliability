import csv
import os
import sys
from fractions import Fraction

TOTAL_SEATS = 100


def main():
    workdir = sys.argv[1]
    rows = []
    with open(os.path.join(workdir, "votes.csv"), newline="") as f:
        for row in csv.DictReader(f):
            rows.append({"party": row["party"], "votes": int(row["votes"])})

    total_votes = sum(r["votes"] for r in rows)
    quotas = {}
    floors = {}
    for r in rows:
        p, v = r["party"], r["votes"]
        exact = Fraction(v * TOTAL_SEATS, total_votes)
        floor_seats = exact.numerator // exact.denominator
        quotas[p] = exact - floor_seats
        floors[p] = floor_seats

    allocated = sum(floors.values())
    remaining = TOTAL_SEATS - allocated

    order = sorted(rows, key=lambda r: (-quotas[r["party"]], r["party"]))
    seats = dict(floors)
    for r in order[:remaining]:
        seats[r["party"]] += 1

    out_path = os.path.join(workdir, "allocation_result.txt")
    with open(out_path, "w") as f:
        for p in sorted(seats.keys()):
            f.write(f"{p}={seats[p]}\n")
        f.write(f"seats_total={sum(seats.values())}\n")


if __name__ == "__main__":
    main()
