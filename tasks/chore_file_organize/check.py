import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, expected_category


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

    expected = {}
    for name, content in files:
        cat = expected_category(name, content)
        expected[name] = (cat, content)

    # no loose files at top level
    try:
        top_entries = os.listdir(workdir)
    except Exception as e:
        fail(f"cannot list workdir: {e}")

    for entry in top_entries:
        if _is_dotted(entry):
            continue
        full = os.path.join(workdir, entry)
        if os.path.isfile(full):
            fail(f"loose file left at top level: {entry}")

    allowed_dirs = {"code", "data", "logs", "docs", "images", "misc"}
    for entry in top_entries:
        if _is_dotted(entry):
            continue
        full = os.path.join(workdir, entry)
        if os.path.isdir(full) and entry not in allowed_dirs:
            fail(f"unexpected directory: {entry}")

    seen = set()
    for name, (cat, content) in expected.items():
        path = os.path.join(workdir, cat, name)
        if not os.path.isfile(path):
            fail(f"missing expected file: {cat}/{name}")
        with open(path, "rb") as f:
            actual_content = f.read()
        if actual_content != content:
            fail(f"content mismatch: {cat}/{name}")
        seen.add((cat, name))

    # ensure no extra files inside category dirs
    for cat in allowed_dirs:
        catdir = os.path.join(workdir, cat)
        if not os.path.isdir(catdir):
            continue
        for root, dirs, files_in in os.walk(catdir):
            dirs[:] = [d for d in dirs if not _is_dotted(d)]
            rel_root = os.path.relpath(root, catdir)
            if rel_root != ".":
                fail(f"unexpected nesting inside {cat}/")
            for fn in files_in:
                if _is_dotted(fn):
                    continue
                if (cat, fn) not in seen:
                    fail(f"unexpected extra file: {cat}/{fn}")

    print("PASS: all files sorted into correct categories")
    sys.exit(0)


if __name__ == "__main__":
    main()
