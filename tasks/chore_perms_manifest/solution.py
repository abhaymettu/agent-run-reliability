import os
import sys


def _is_dotted(name):
    return name.startswith(".")


def expected_mode(basename, size):
    if "secret" in basename:
        return 0o600
    if basename.endswith(".sh"):
        return 0o755
    if size > 100:
        return 0o664
    return 0o644


def main():
    workdir = sys.argv[1]
    manifest_lines = []
    for root, dirs, fnames in os.walk(workdir):
        dirs[:] = [d for d in dirs if not _is_dotted(d)]
        os.chmod(root, 0o755)
        for fn in fnames:
            if _is_dotted(fn):
                continue
            full = os.path.join(root, fn)
            size = os.path.getsize(full)
            mode = expected_mode(fn, size)
            os.chmod(full, mode)
            rel = os.path.relpath(full, workdir).replace(os.sep, "/")
            manifest_lines.append((rel, mode))

    manifest_lines.sort()
    with open(os.path.join(workdir, "manifest.txt"), "w") as f:
        for rel, mode in manifest_lines:
            f.write(f"{rel} {mode:03o}\n")


if __name__ == "__main__":
    main()
