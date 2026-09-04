import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate


def main():
    workdir = sys.argv[1]
    doc = generate()
    path = os.path.join(workdir, "document.json")
    with open(path, "w") as f:
        json.dump(doc, f, indent=2, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    main()
