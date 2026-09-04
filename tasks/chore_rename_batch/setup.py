import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate


def main():
    workdir = sys.argv[1]
    files = generate()
    for name, content, _seq in files:
        path = os.path.join(workdir, name)
        with open(path, "wb") as f:
            f.write(content)


if __name__ == "__main__":
    main()
