import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import expected_category


def main():
    workdir = sys.argv[1]
    names = [n for n in os.listdir(workdir) if os.path.isfile(os.path.join(workdir, n))]
    for name in names:
        path = os.path.join(workdir, name)
        with open(path, "rb") as f:
            content = f.read()
        cat = expected_category(name, content)
        catdir = os.path.join(workdir, cat)
        os.makedirs(catdir, exist_ok=True)
        os.rename(path, os.path.join(catdir, name))


if __name__ == "__main__":
    main()
