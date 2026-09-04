import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate  # noqa: E402


def main():
    workdir = sys.argv[1]
    files, pre_empty_dirs = generate()

    for relpath, content, _flagged in files:
        full = os.path.join(workdir, *relpath.split("/"))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(content)

    for d in pre_empty_dirs:
        full = os.path.join(workdir, *d.split("/"))
        os.makedirs(full, exist_ok=True)


if __name__ == "__main__":
    main()
