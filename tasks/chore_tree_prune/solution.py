import json
import os
import sys

SIZE_LIMIT = 5000
AGE_LIMIT = 30
AGE_EXTS = {".log", ".tmp"}
ALWAYS_REMOVE_EXTS = {".bak"}


def _ext(name):
    return "." + name.rsplit(".", 1)[-1] if "." in name else ""


def _is_dotted(name):
    return name.startswith(".")


def should_remove(name, size, age_days):
    ext = _ext(name)
    if age_days > AGE_LIMIT and ext in AGE_EXTS:
        return True
    if size > SIZE_LIMIT:
        return True
    if ext in ALWAYS_REMOVE_EXTS:
        return True
    return False


def main():
    workdir = sys.argv[1]
    with open(os.path.join(workdir, "meta.json")) as f:
        meta = json.load(f)

    removed = []
    survived = []
    for root, dirs, fnames in os.walk(workdir):
        dirs[:] = [d for d in dirs if not _is_dotted(d)]
        for fn in fnames:
            if _is_dotted(fn):
                continue
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, workdir).replace(os.sep, "/")
            if rel in ("meta.json", "report.txt"):
                continue
            size = os.path.getsize(full)
            age = meta[rel]
            if should_remove(fn, size, age):
                os.remove(full)
                removed.append(rel)
            else:
                survived.append(rel)

    # prune now-empty directories, bottom-up
    for root, dirs, fnames in os.walk(workdir, topdown=False):
        if os.path.abspath(root) == os.path.abspath(workdir):
            continue
        rel_root = os.path.relpath(root, workdir).replace(os.sep, "/")
        if any(_is_dotted(part) for part in rel_root.split("/")):
            continue
        if not os.listdir(root):
            os.rmdir(root)

    removed.sort()
    survived.sort()
    lines = [f"REMOVED: {len(removed)}"] + removed + [f"SURVIVED: {len(survived)}"] + survived
    with open(os.path.join(workdir, "report.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
