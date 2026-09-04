import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate  # noqa: E402


def main():
    workdir = sys.argv[1]
    base, overrides = generate()

    with open(os.path.join(workdir, "base.json"), "w") as f:
        json.dump(base, f, indent=2, sort_keys=True)
        f.write("\n")

    ov_dir = os.path.join(workdir, "overrides")
    os.makedirs(ov_dir, exist_ok=True)
    for i, ov in enumerate(overrides, start=1):
        path = os.path.join(ov_dir, f"override_{i:02d}.json")
        with open(path, "w") as f:
            json.dump(ov, f, indent=2, sort_keys=True)
            f.write("\n")


if __name__ == "__main__":
    main()
