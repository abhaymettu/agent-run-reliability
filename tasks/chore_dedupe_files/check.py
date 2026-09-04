import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, duplicate_manifest


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


def _is_dotted(name):
    """True if a path component (file or dir name) starts with a dot."""
    return name.startswith(".")


def main():
    if len(sys.argv) < 2:
        fail("usage: check.py <workdir>")
    workdir = sys.argv[1]
    if not os.path.isdir(workdir):
        fail("workdir missing")

    try:
        files = generate()
    except Exception as e:
        fail(f"generator error: {e}")

    groups, unique_paths = duplicate_manifest(files)
    orig_content = {relpath: content for relpath, content in files}

    removed_set = set()
    expected_lines = []
    for kept in sorted(groups.keys()):
        for removed in sorted(groups[kept]):
            expected_lines.append(f"{kept} <- {removed}")
            removed_set.add(removed)

    kept_set = set(groups.keys()) | unique_paths
    survivors = kept_set  # exact set of files expected to remain

    # walk actual tree, collect actual file relpaths (posix-style)
    actual_files = {}
    for root, dirs, fnames in os.walk(workdir):
        dirs[:] = [d for d in dirs if not _is_dotted(d)]
        for fn in fnames:
            if _is_dotted(fn):
                continue
            if fn == "manifest.txt" and os.path.abspath(root) == os.path.abspath(workdir):
                continue
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, workdir).replace(os.sep, "/")
            with open(full, "rb") as f:
                actual_files[rel] = f.read()

    if set(actual_files.keys()) != survivors:
        missing = survivors - set(actual_files.keys())
        extra = set(actual_files.keys()) - survivors
        fail(f"survivor set mismatch (missing={sorted(missing)[:3]}, extra={sorted(extra)[:3]})")

    for rel, content in actual_files.items():
        if content != orig_content[rel]:
            fail(f"content changed for surviving file: {rel}")

    orig_dirs = set()
    for relpath, _content in files:
        d = os.path.dirname(relpath)
        while d:
            orig_dirs.add(d)
            d = os.path.dirname(d)
    for d in orig_dirs:
        if not os.path.isdir(os.path.join(workdir, d)):
            fail(f"directory removed but should have been left in place: {d}")

    manifest_path = os.path.join(workdir, "manifest.txt")
    if not os.path.isfile(manifest_path):
        fail("manifest.txt missing")
    with open(manifest_path, "r") as f:
        actual_manifest_lines = [ln for ln in f.read().split("\n")]
    if actual_manifest_lines and actual_manifest_lines[-1] == "":
        actual_manifest_lines = actual_manifest_lines[:-1]

    if actual_manifest_lines != expected_lines:
        fail(f"manifest.txt content mismatch (got {len(actual_manifest_lines)} lines, expected {len(expected_lines)})")

    print("PASS: duplicates removed correctly and manifest matches")
    sys.exit(0)


if __name__ == "__main__":
    main()
