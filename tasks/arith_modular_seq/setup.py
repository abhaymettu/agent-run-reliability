import os
import sys

from gen import generate


def main():
    workdir = sys.argv[1]
    values = generate()
    path = os.path.join(workdir, "numbers.txt")
    with open(path, "w") as f:
        for v in values:
            f.write(f"{v}\n")


if __name__ == "__main__":
    main()
