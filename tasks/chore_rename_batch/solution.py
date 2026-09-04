import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import expected_name


def main():
    workdir = sys.argv[1]
    names = [
        n for n in os.listdir(workdir)
        if not n.startswith(".") and os.path.isfile(os.path.join(workdir, n))
    ]
    renames = []
    for name in names:
        path = os.path.join(workdir, name)
        with open(path, "r") as f:
            first_line = f.readline().strip()
        seq = int(first_line.split("SEQ:")[1].strip())
        new_name = expected_name(name, seq)
        renames.append((path, os.path.join(workdir, new_name)))
    for src, dst in renames:
        os.rename(src, dst)


if __name__ == "__main__":
    main()
