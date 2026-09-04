import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate


def main():
    workdir = sys.argv[1]
    files = generate()
    for relpath, content in files:
        full = os.path.join(workdir, relpath)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb") as f:
            f.write(content)


if __name__ == "__main__":
    main()
