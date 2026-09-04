import json
import os
import sys


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


def main():
    workdir = sys.argv[1]
    with open(os.path.join(workdir, "document.json")) as f:
        doc = json.load(f)
    lines = []
    flatten(doc, "", lines)
    lines.sort()
    with open(os.path.join(workdir, "flat.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
