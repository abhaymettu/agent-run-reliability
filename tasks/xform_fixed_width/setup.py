import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, format_record


def main():
    workdir = sys.argv[1]
    rows = generate()
    path = os.path.join(workdir, "employees.fwf")
    with open(path, "w") as f:
        for row in rows:
            f.write(format_record(row) + "\n")


if __name__ == "__main__":
    main()
