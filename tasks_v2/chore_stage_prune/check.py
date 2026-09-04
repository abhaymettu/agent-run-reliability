import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, compute_expected  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def rel_to_workdir(workdir, full):
    return os.path.relpath(full, workdir).replace(os.sep, "/")


def walk_files(workdir):
    """Return {relpath: content_bytes}, ignoring dotted path components."""
    out = {}
    for dirpath, dirnames, filenames in os.walk(workdir):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for fname in filenames:
            if fname.startswith("."):
                continue
            full = os.path.join(dirpath, fname)
            rel = rel_to_workdir(workdir, full)
            with open(full, "rb") as f:
                out[rel] = f.read()
    return out


def walk_dirs(workdir):
    """Return set of directory relpaths (excluding workdir root), ignoring
    dotted components and dotted directories themselves."""
    out = set()
    for dirpath, dirnames, _filenames in os.walk(workdir):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for d in dirnames:
            full = os.path.join(dirpath, d)
            rel = rel_to_workdir(workdir, full)
            out.add(rel)
    return out


def main():
    workdir = sys.argv[1]
    files, pre_empty_dirs = generate()
    archived, surviving_files, pruned_dirs, surviving_dirs = compute_expected(files, pre_empty_dirs)

    actual_files = walk_files(workdir)
    actual_dirs = walk_dirs(workdir)

    expected_files = {}
    for orig, content, arc_path in archived:
        expected_files[arc_path] = content.encode()
    for relpath, content in surviving_files:
        expected_files[relpath] = content.encode()

    manifest_path = os.path.join(workdir, "archive_manifest.txt")
    if not os.path.isfile(manifest_path):
        fail("archive_manifest.txt not found")
    expected_files["archive_manifest.txt"] = None  # checked separately

    # every expected file (other than the manifest) must be present with
    # exact content
    for relpath, content in expected_files.items():
        if content is None:
            continue
        if relpath not in actual_files:
            fail(f"missing expected file: {relpath}")
        if actual_files[relpath] != content:
            fail(f"content mismatch for {relpath}")

    # no leftover originals for archived files
    for orig, _content, _arc in archived:
        if orig in actual_files:
            fail(f"original file still present (should have been moved): {orig}")

    # no extra unexpected files
    expected_names = set(expected_files.keys())
    extra = set(actual_files.keys()) - expected_names
    if extra:
        fail(f"unexpected extra file(s) present: {sorted(extra)[:5]}")

    # directories: pruned must be gone, surviving must exist
    for d in pruned_dirs:
        if d in actual_dirs:
            fail(f"directory should have been pruned but still exists: {d}")
    for d in surviving_dirs:
        if d == "inbox":
            continue
        if d not in actual_dirs:
            fail(f"directory should have survived but is missing: {d}")

    if not os.path.isdir(os.path.join(workdir, "inbox")):
        fail("inbox/ itself must not be removed")

    if not os.path.isdir(os.path.join(workdir, "archive")):
        fail("archive/ directory not found")

    # manifest content
    with open(manifest_path) as f:
        manifest_content = f.read()
    lines = []
    for orig, _content, arc_path in sorted(archived, key=lambda t: t[0]):
        lines.append(f"{orig} -> {arc_path}")
    expected_manifest = "\n".join(lines) + "\n"
    if manifest_content != expected_manifest:
        fail("archive_manifest.txt content does not match expected")

    print("PASS: inbox archived, pruned, and manifest match expected result")
    sys.exit(0)


if __name__ == "__main__":
    main()
