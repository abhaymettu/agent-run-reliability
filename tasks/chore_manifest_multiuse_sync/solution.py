import json
import os
import sys


def main():
    workdir = sys.argv[1]
    sources_dir = os.path.join(workdir, "sources")
    build_dir = os.path.join(workdir, "build")

    with open(os.path.join(workdir, "manifest.json")) as f:
        manifest = json.load(f)

    entries = [(e["target"], e["source"]) for e in manifest]
    expected_targets = set(t for t, _s in entries)

    # Remove build/ files that are not a manifest target, and prune the
    # directories that lose all their files as a result.
    if os.path.isdir(build_dir):
        for dirpath, dirnames, filenames in os.walk(build_dir):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for fname in filenames:
                if fname.startswith("."):
                    continue
                full = os.path.join(dirpath, fname)
                rel = os.path.relpath(full, build_dir).replace(os.sep, "/")
                if rel not in expected_targets:
                    os.remove(full)

        for dirpath, dirnames, _filenames in os.walk(build_dir, topdown=False):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            if dirpath == build_dir:
                continue
            if not os.listdir(dirpath):
                os.rmdir(dirpath)
    else:
        os.makedirs(build_dir)

    # Copy (never move) each source's content to every target that
    # references it. Read sources up front so nothing about the loop order
    # can affect a source used more than once.
    source_cache = {}
    for target, source in entries:
        if source not in source_cache:
            with open(os.path.join(sources_dir, source)) as f:
                source_cache[source] = f.read()

    for target, source in entries:
        content = source_cache[source]
        dest = os.path.join(build_dir, *target.split("/"))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if os.path.isfile(dest):
            with open(dest) as f:
                existing = f.read()
            if existing == content:
                continue
        with open(dest, "w") as f:
            f.write(content)


if __name__ == "__main__":
    main()
