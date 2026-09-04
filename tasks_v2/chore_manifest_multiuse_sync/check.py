import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, compute_expected  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def walk_files(root):
    out = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for fname in filenames:
            if fname.startswith("."):
                continue
            full = os.path.join(dirpath, fname)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            with open(full) as f:
                out[rel] = f.read()
    return out


def main():
    workdir = sys.argv[1]
    sources, manifest_entries, _prebuilt = generate()
    expected_build = compute_expected(sources, manifest_entries)

    sources_dir = os.path.join(workdir, "sources")
    actual_sources = walk_files(sources_dir)
    expected_sources = dict(sources)
    if actual_sources != expected_sources:
        missing = set(expected_sources) - set(actual_sources)
        extra = set(actual_sources) - set(expected_sources)
        changed = [
            k for k in (set(expected_sources) & set(actual_sources))
            if actual_sources[k] != expected_sources[k]
        ]
        fail(
            f"sources/ was modified (missing={sorted(missing)}, "
            f"extra={sorted(extra)}, changed={sorted(changed)})"
        )

    build_dir = os.path.join(workdir, "build")
    if not os.path.isdir(build_dir):
        fail("build/ directory not found")
    actual_build = walk_files(build_dir)

    if set(actual_build.keys()) != set(expected_build.keys()):
        missing = set(expected_build) - set(actual_build)
        extra = set(actual_build) - set(expected_build)
        fail(f"build/ contents mismatch (missing={sorted(missing)}, extra={sorted(extra)})")

    for target, content in expected_build.items():
        if actual_build[target] != content:
            fail(f"content mismatch for build/{target}")

    # no leftover empty directories (e.g. a decoy's now-empty parent dir)
    for dirpath, dirnames, filenames in os.walk(build_dir):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        real_files = [f for f in filenames if not f.startswith(".")]
        if dirpath == build_dir:
            continue
        rel = os.path.relpath(dirpath, build_dir).replace(os.sep, "/")
        has_expected_descendant = any(
            t == rel or t.startswith(rel + "/") for t in expected_build
        )
        if not real_files and not has_expected_descendant:
            fail(f"leftover empty directory under build/: {rel}")

    print("PASS: build/ matches manifest, sources/ untouched")
    sys.exit(0)


if __name__ == "__main__":
    main()
