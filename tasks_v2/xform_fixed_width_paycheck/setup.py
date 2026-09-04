import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, render_line  # noqa: E402


def main():
    workdir = sys.argv[1]
    rows = generate()
    lines = [render_line(r) for r in rows]
    with open(os.path.join(workdir, "paychecks.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
