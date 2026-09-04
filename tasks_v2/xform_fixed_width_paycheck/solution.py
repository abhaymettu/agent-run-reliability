import os
import sys


def parse_amount(field):
    field = field.strip()
    neg = field.startswith("(") and field.endswith(")")
    if neg:
        field = field[1:-1]
    dollars, cents = field.split(".")
    total = int(dollars) * 100 + int(cents)
    return -total if neg else total


def format_cents(cents):
    sign = "-" if cents < 0 else ""
    c = abs(cents)
    return f"{sign}{c // 100}.{c % 100:02d}"


def main():
    workdir = sys.argv[1]
    in_path = os.path.join(workdir, "paychecks.txt")
    totals = {}
    counts = {}
    with open(in_path) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            eid = line[0:6].strip()
            amount_field = line[22:34]
            flag = line[34:35]
            void = flag == "V"
            counts[eid] = counts.get(eid, 0) + 1
            totals.setdefault(eid, 0)
            if not void:
                totals[eid] += parse_amount(amount_field)

    out_path = os.path.join(workdir, "paycheck_totals.csv")
    with open(out_path, "w") as f:
        f.write("employee_id,total,record_count\n")
        for eid in sorted(counts):
            f.write(f"{eid},{format_cents(totals[eid])},{counts[eid]}\n")


if __name__ == "__main__":
    main()
