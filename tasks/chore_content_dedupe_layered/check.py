import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, compute_expected  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def walk_files(workdir):
    out = {}
    for dirpath, dirnames, filenames in os.walk(workdir):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for fname in filenames:
            if fname.startswith("."):
                continue
            full = os.path.join(dirpath, fname)
            rel = os.path.relpath(full, workdir).replace(os.sep, "/")
            with open(full) as f:
                out[rel] = f.read()
    return out


def main():
    workdir = sys.argv[1]
    files = generate()
    content_by_path = dict(files)
    kept_set, deletions = compute_expected(files)

    actual = walk_files(workdir)

    for relpath in kept_set:
        if relpath not in actual:
            fail(f"file that should survive is missing: {relpath}")
        if actual[relpath] != content_by_path[relpath]:
            fail(f"content changed for surviving file: {relpath}")

    deleted_paths = set(d for _k, d in deletions)
    for relpath in deleted_paths:
        if relpath in actual:
            fail(f"file that should have been deleted is still present: {relpath}")

    expected_all_names = set(r for r, _c in files) - deleted_paths
    extra = set(actual.keys()) - expected_all_names - {"dedupe_manifest.txt"}
    if extra:
        fail(f"unexpected extra file(s) present: {sorted(extra)[:5]}")
    missing = expected_all_names - set(actual.keys())
    if missing:
        fail(f"expected file(s) missing: {sorted(missing)[:5]}")

    manifest_path = os.path.join(workdir, "dedupe_manifest.txt")
    if not os.path.isfile(manifest_path):
        fail("dedupe_manifest.txt not found")
    with open(manifest_path) as f:
        manifest_content = f.read()

    lines = [f"{keep} <- {loser}" for keep, loser in deletions]
    expected_manifest = "\n".join(lines) + "\n"
    if manifest_content != expected_manifest:
        fail("dedupe_manifest.txt content does not match expected")

    print("PASS: duplicates removed with correct tie-break, empty files preserved")
    sys.exit(0)


if __name__ == "__main__":
    main()
