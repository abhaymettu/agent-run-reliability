import copy
import glob
import json
import os
import sys


def deep_merge(base, override):
    if isinstance(base, dict) and isinstance(override, dict):
        result = dict(base)
        for k, v in override.items():
            if k in result:
                result[k] = deep_merge(result[k], v)
            else:
                result[k] = copy.deepcopy(v)
        return result
    return copy.deepcopy(override)


def flatten(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k in sorted(obj):
            child_prefix = f"{prefix}.{k}" if prefix else k
            out.update(flatten(obj[k], child_prefix))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            child_prefix = f"{prefix}[{i}]"
            out.update(flatten(v, child_prefix))
    else:
        out[prefix] = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return out


def main():
    workdir = sys.argv[1]
    with open(os.path.join(workdir, "base.json")) as f:
        merged = json.load(f)

    ov_dir = os.path.join(workdir, "overrides")
    names = sorted(
        n for n in os.listdir(ov_dir)
        if not n.startswith(".") and n.endswith(".json")
    )
    for name in names:
        with open(os.path.join(ov_dir, name)) as f:
            ov = json.load(f)
        merged = deep_merge(merged, ov)

    flat = flatten(merged)
    lines = [f"{p}={v}" for p, v in sorted(flat.items())]

    out_path = os.path.join(workdir, "flattened.txt")
    with open(out_path, "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
