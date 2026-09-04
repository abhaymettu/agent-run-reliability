import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate  # noqa: E402


def main():
    workdir = sys.argv[1]
    records = generate()
    for name, prio, created, body in records:
        content = f"PRIORITY: {prio}\nCREATED: {created}\n{body}"
        with open(os.path.join(workdir, name), "w") as f:
            f.write(content)


if __name__ == "__main__":
    main()
