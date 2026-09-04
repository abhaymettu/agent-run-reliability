import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate


def main():
    workdir = sys.argv[1]
    entries, meta = generate()
    for relpath, content in entries:
        full = os.path.join(workdir, relpath)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb") as f:
            f.write(content)

    with open(os.path.join(workdir, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    main()
