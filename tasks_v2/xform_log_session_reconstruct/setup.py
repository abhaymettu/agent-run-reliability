import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate  # noqa: E402


def main():
    workdir = sys.argv[1]
    events = generate()
    lines = [f"{ts} user={user} event={event}" for ts, user, event in events]
    with open(os.path.join(workdir, "session.log"), "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
