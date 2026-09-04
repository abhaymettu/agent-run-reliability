import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate


def fmt(v):
    if v is True:
        return "true"
    if v is False:
        return "false"
    if v is None:
        return "null"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return v
    raise TypeError(f"unexpected leaf type: {type(v)}")


def flatten(v, prefix, out):
    if isinstance(v, dict):
        for k in v:
            newp = f"{prefix}.{k}" if prefix else k
            flatten(v[k], newp, out)
    elif isinstance(v, list):
        for i, item in enumerate(v):
            newp = f"{prefix}[{i}]"
            flatten(item, newp, out)
    else:
        out.append(f"{prefix}={fmt(v)}")


def expected():
    doc = generate()
    out = []
    flatten(doc, "", out)
    out.sort()
    return out


def main():
    if len(sys.argv) < 2:
        print("FAIL: no workdir given")
        return 1
    workdir = sys.argv[1]
    path = os.path.join(workdir, "flat.txt")
    if not os.path.isfile(path):
        print("FAIL: flat.txt not found")
        return 1

    try:
        with open(path) as f:
            lines = [ln for ln in f.read().split("\n")]
    except Exception as e:
        print(f"FAIL: could not read flat.txt: {e}")
        return 1

    # allow (and ignore) a single trailing empty line from a final newline
    if lines and lines[-1] == "":
        lines = lines[:-1]

    exp = expected()

    if len(lines) != len(exp):
        print(f"FAIL: expected {len(exp)} lines, got {len(lines)}")
        return 1

    for i, (got, want) in enumerate(zip(lines, exp)):
        if got.strip("\r") != want:
            print(f"FAIL: line {i+1} '{got}' != expected '{want}'")
            return 1

    print(f"PASS: flat.txt matches {len(exp)} expected leaf lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
