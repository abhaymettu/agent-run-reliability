import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate


def expected():
    rows = generate()
    out = []
    for r in rows:
        out.append((r["name"], str(r["emp_id"]), r["dept"], f"{r['amount']:.2f}"))
    return out


def main():
    if len(sys.argv) < 2:
        print("FAIL: no workdir given")
        return 1
    workdir = sys.argv[1]
    path = os.path.join(workdir, "employees.tsv")
    if not os.path.isfile(path):
        print("FAIL: employees.tsv not found")
        return 1

    try:
        with open(path) as f:
            lines = f.read().split("\n")
    except Exception as e:
        print(f"FAIL: could not read employees.tsv: {e}")
        return 1

    if lines and lines[-1] == "":
        lines = lines[:-1]

    if not lines:
        print("FAIL: employees.tsv is empty")
        return 1

    header = lines[0].split("\t")
    if header != ["name", "emp_id", "dept", "amount"]:
        print(f"FAIL: bad header {header}")
        return 1

    exp = expected()
    data_lines = lines[1:]

    if len(data_lines) != len(exp):
        print(f"FAIL: expected {len(exp)} data rows, got {len(data_lines)}")
        return 1

    for i, (line, want) in enumerate(zip(data_lines, exp)):
        fields = line.split("\t")
        if len(fields) != 4:
            print(f"FAIL: row {i} has {len(fields)} tab-separated fields, want 4")
            return 1
        got = tuple(fields)
        if got != want:
            print(f"FAIL: row {i} got {got} != expected {want}")
            return 1

    print(f"PASS: employees.tsv matches {len(exp)} expected records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
