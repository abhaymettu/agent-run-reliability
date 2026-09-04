import csv
import os
import sys


def main():
    workdir = sys.argv[1]
    in_path = os.path.join(workdir, "scores.csv")
    rows = []
    with open(in_path, newline="") as f:
        for row in csv.DictReader(f):
            rows.append({"employee_id": row["employee_id"], "score": int(row["score"])})

    ordered = sorted(rows, key=lambda r: -r["score"])
    result = {}
    rank = 0
    prev_score = None
    for i, r in enumerate(ordered):
        if r["score"] != prev_score:
            rank = i + 1
            prev_score = r["score"]
        if rank <= 3:
            bonus = 500
        elif rank <= 10:
            bonus = 200
        else:
            bonus = 0
        result[r["employee_id"]] = (rank, bonus)

    total_bonus = sum(b for _, b in result.values())

    out_path = os.path.join(workdir, "bonus_result.txt")
    with open(out_path, "w") as f:
        for eid in sorted(result.keys()):
            rank, bonus = result[eid]
            f.write(f"{eid},{rank},{bonus}\n")
        f.write(f"total_bonus={total_bonus}\n")


if __name__ == "__main__":
    main()
