import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, SOURCE_NAME


def main():
    workdir = sys.argv[1]
    full_text, _chunks = generate()
    with open(os.path.join(workdir, SOURCE_NAME), "w") as f:
        f.write(full_text)


if __name__ == "__main__":
    main()
