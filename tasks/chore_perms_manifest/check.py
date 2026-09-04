import os
import stat
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, expected_mode


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
        entries, all_dirs = generate()
    except Exception as e:
        fail(f"generator error: {e}")

    expected = {}
    for relpath, content in entries:
        full = os.path.join(workdir, relpath)
        if not os.path.isfile(full):
            fail(f"missing expected file: {relpath}")
        with open(full, "rb") as f:
            actual_content = f.read()
        if actual_content != content:
            fail(f"content changed: {relpath}")
        mode = expected_mode(relpath, content)
        expected[relpath] = mode
        actual_mode = stat.S_IMODE(os.stat(full).st_mode)
        if actual_mode != mode:
            fail(f"wrong mode for {relpath}: got {oct(actual_mode)}, want {oct(mode)}")

    for d in all_dirs:
        full = os.path.join(workdir, d)
        if not os.path.isdir(full):
            fail(f"missing expected directory: {d}")
        actual_mode = stat.S_IMODE(os.stat(full).st_mode)
        if actual_mode != 0o755:
            fail(f"wrong mode for directory {d}: got {oct(actual_mode)}, want 0o755")

    manifest_path = os.path.join(workdir, "manifest.txt")
    if not os.path.isfile(manifest_path):
        fail("manifest.txt missing")
    with open(manifest_path, "r") as f:
        content = f.read()
    lines = content.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]

    expected_lines = [f"{p} {expected[p]:03o}" for p in sorted(expected.keys())]
    if lines != expected_lines:
        fail(f"manifest.txt content mismatch (got {len(lines)} lines, expected {len(expected_lines)})")

    print("PASS: modes and manifest correct")
    sys.exit(0)


if __name__ == "__main__":
    main()
