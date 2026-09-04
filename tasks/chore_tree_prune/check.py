import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, expected_state


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


def main():
    if len(sys.argv) < 2:
        fail("usage: check.py <workdir>")
    workdir = sys.argv[1]
    if not os.path.isdir(workdir):
        fail("workdir missing")

    try:
        entries, meta = generate()
    except Exception as e:
        fail(f"generator error: {e}")

    removed, survived, survived_dirs = expected_state(entries, meta)
    orig_content = {relpath: content for relpath, content in entries}

    if not os.path.isfile(os.path.join(workdir, "meta.json")):
        fail("meta.json missing (should never be removed)")

    for relpath in removed:
        if os.path.exists(os.path.join(workdir, relpath)):
            fail(f"file should have been removed: {relpath}")

    for relpath in survived:
        full = os.path.join(workdir, relpath)
        if not os.path.isfile(full):
            fail(f"file should have survived: {relpath}")
        with open(full, "rb") as f:
            actual = f.read()
        if actual != orig_content[relpath]:
            fail(f"surviving file content changed: {relpath}")

    # exact set of tree files present (excluding meta.json / report.txt)
    actual_tree_files = set()
    for root, dirs, fnames in os.walk(workdir):
        for fn in fnames:
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, workdir).replace(os.sep, "/")
            if rel in ("meta.json", "report.txt"):
                continue
            actual_tree_files.add(rel)
    if actual_tree_files != set(survived):
        extra = actual_tree_files - set(survived)
        missing = set(survived) - actual_tree_files
        fail(f"tree file set mismatch (extra={sorted(extra)[:3]}, missing={sorted(missing)[:3]})")

    # directories: exactly the surviving dirs must exist, all others pruned
    all_dirs_seen = set()
    for root, dirs, fnames in os.walk(workdir):
        for d in dirs:
            full = os.path.join(root, d)
            rel = os.path.relpath(full, workdir).replace(os.sep, "/")
            all_dirs_seen.add(rel)
    if all_dirs_seen != set(survived_dirs):
        extra = all_dirs_seen - set(survived_dirs)
        missing = set(survived_dirs) - all_dirs_seen
        fail(f"directory set mismatch (extra={sorted(extra)[:3]}, missing={sorted(missing)[:3]})")

    report_path = os.path.join(workdir, "report.txt")
    if not os.path.isfile(report_path):
        fail("report.txt missing")
    with open(report_path, "r") as f:
        content = f.read()
    lines = content.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]

    expected_lines = [f"REMOVED: {len(removed)}"] + removed + [f"SURVIVED: {len(survived)}"] + survived
    if lines != expected_lines:
        fail(f"report.txt content mismatch (got {len(lines)} lines, expected {len(expected_lines)})")

    print("PASS: tree pruned correctly and report matches")
    sys.exit(0)


if __name__ == "__main__":
    main()
