import hashlib
import os
import sys


def _is_dotted(name):
    return name.startswith(".")


def main():
    workdir = sys.argv[1]
    by_hash = {}
    for root, dirs, fnames in os.walk(workdir):
        dirs[:] = [d for d in dirs if not _is_dotted(d)]
        for fn in fnames:
            if _is_dotted(fn):
                continue
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, workdir).replace(os.sep, "/")
            with open(full, "rb") as f:
                data = f.read()
            h = hashlib.sha256(data).hexdigest()
            by_hash.setdefault(h, []).append(rel)

    manifest_lines = []
    for h, paths in by_hash.items():
        if len(paths) < 2:
            continue
        paths_sorted = sorted(paths)
        kept = paths_sorted[0]
        removed = paths_sorted[1:]
        for r in removed:
            manifest_lines.append((kept, r))
            os.remove(os.path.join(workdir, r))

    manifest_lines.sort()
    with open(os.path.join(workdir, "manifest.txt"), "w") as f:
        for kept, removed in manifest_lines:
            f.write(f"{kept} <- {removed}\n")


if __name__ == "__main__":
    main()
