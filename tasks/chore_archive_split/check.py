import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate


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
        _full_text, chunks = generate()
    except Exception as e:
        fail(f"generator error: {e}")

    chunks_dir = os.path.join(workdir, "chunks")
    if not os.path.isdir(chunks_dir):
        fail("chunks/ directory missing")

    expected_index_lines = []
    for i, lines in enumerate(chunks, start=1):
        fname = f"chunk_{i:03d}.txt"
        path = os.path.join(chunks_dir, fname)
        if not os.path.isfile(path):
            fail(f"missing {fname}")
        with open(path, "rb") as f:
            data = f.read()
        if lines:
            expected_content = ("\n".join(lines) + "\n").encode()
        else:
            expected_content = b""
        if data != expected_content:
            fail(f"content mismatch in {fname}")
        first_line = lines[0] if lines else "EMPTY"
        expected_index_lines.append(f"{fname} {len(lines)} {first_line}")

    index_path = os.path.join(chunks_dir, "index.txt")
    if not os.path.isfile(index_path):
        fail("chunks/index.txt missing")
    with open(index_path, "r") as f:
        content = f.read()
    actual_lines = content.split("\n")
    if actual_lines and actual_lines[-1] == "":
        actual_lines = actual_lines[:-1]

    if actual_lines != expected_index_lines:
        fail(f"index.txt mismatch (got {len(actual_lines)} lines, expected {len(expected_index_lines)})")

    # no extra chunk files
    actual_files = {n for n in os.listdir(chunks_dir) if not _is_dotted(n)}
    expected_files = {f"chunk_{i:03d}.txt" for i in range(1, len(chunks) + 1)} | {"index.txt"}
    if actual_files != expected_files:
        extra = actual_files - expected_files
        fail(f"unexpected files in chunks/: {sorted(extra)[:3]}")

    print("PASS: archive split into correct chunks with matching index")
    sys.exit(0)


if __name__ == "__main__":
    main()
