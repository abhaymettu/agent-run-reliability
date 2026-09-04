import os
import sys

NAME_W = 18
ID_W = 8
DEPT_W = 6
AMOUNT_W = 12


def main():
    workdir = sys.argv[1]
    out_rows = []
    with open(os.path.join(workdir, "employees.fwf")) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            name = line[0:NAME_W].strip()
            emp_id = line[NAME_W:NAME_W + ID_W].strip()
            dept = line[NAME_W + ID_W:NAME_W + ID_W + DEPT_W].strip()
            amount = line[NAME_W + ID_W + DEPT_W:NAME_W + ID_W + DEPT_W + AMOUNT_W].strip()
            emp_id = str(int(emp_id))
            amount = f"{float(amount):.2f}"
            out_rows.append((name, emp_id, dept, amount))

    with open(os.path.join(workdir, "employees.tsv"), "w") as f:
        f.write("name\temp_id\tdept\tamount\n")
        for row in out_rows:
            f.write("\t".join(row) + "\n")


if __name__ == "__main__":
    main()
