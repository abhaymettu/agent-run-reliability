import os
import sys


def depth_of(relpath):
    return relpath.count("/")


def main():
    workdir = sys.argv[1]

    by_content = {}
    for dirpath, dirnames, filenames in os.walk(workdir):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for fname in filenames:
            if fname.startswith("."):
                continue
            full = os.path.join(dirpath, fname)
            rel = os.path.relpath(full, workdir).replace(os.sep, "/")
            with open(full, "rb") as f:
                content = f.read()
            if content == b"":
                continue  # empty files never count as duplicates
            by_content.setdefault(content, []).append(rel)

    manifest_lines = []
    for content, paths in by_content.items():
        if len(paths) < 2:
            continue
        ordered = sorted(paths, key=lambda p: (depth_of(p), p))
        keep = ordered[0]
        for loser in ordered[1:]:
            os.remove(os.path.join(workdir, *loser.split("/")))
            manifest_lines.append((keep, loser))

    manifest_lines.sort(key=lambda t: (t[0], t[1]))
    with open(os.path.join(workdir, "dedupe_manifest.txt"), "w") as f:
        for keep, loser in manifest_lines:
            f.write(f"{keep} <- {loser}\n")


if __name__ == "__main__":
    main()
