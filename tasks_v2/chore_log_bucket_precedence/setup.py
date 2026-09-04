import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate  # noqa: E402


def main():
    workdir = sys.argv[1]
    lines = generate()
    with open(os.path.join(workdir, "events.log"), "w") as f:
        for line in lines:
            f.write(line + "\n")


if __name__ == "__main__":
    main()
