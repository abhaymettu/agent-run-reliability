import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, compute_expected  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def main():
    workdir = sys.argv[1]
    records = generate()
    valid_renames, rejected = compute_expected(records)
    content_by_name = {name: f"PRIORITY: {p}\nCREATED: {c}\n{b}" for name, p, c, b in records}

    top_level = set(n for n in os.listdir(workdir) if not n.startswith("."))

    expected_top = set(new for _o, new, _p, _c, _i in valid_renames)
    expected_top.add("rejected")
    expected_top.add("ticket_manifest.txt")
    if top_level != expected_top:
        fail(f"top-level contents mismatch: expected {sorted(expected_top)}, got {sorted(top_level)}")

    for orig, new_name, _p, _c, _i in valid_renames:
        path = os.path.join(workdir, new_name)
        if not os.path.isfile(path):
            fail(f"missing renamed file: {new_name}")
        with open(path) as f:
            content = f.read()
        if content != content_by_name[orig]:
            fail(f"content mismatch for {new_name}")

    rejected_dir = os.path.join(workdir, "rejected")
    if not os.path.isdir(rejected_dir):
        fail("rejected/ directory not found")
    actual_rejected = set(n for n in os.listdir(rejected_dir) if not n.startswith("."))
    if actual_rejected != set(rejected):
        fail(f"rejected/ contents mismatch: expected {sorted(rejected)}, got {sorted(actual_rejected)}")
    for name in rejected:
        path = os.path.join(rejected_dir, name)
        with open(path) as f:
            content = f.read()
        if content != content_by_name[name]:
            fail(f"rejected file content changed: {name}")

    manifest_path = os.path.join(workdir, "ticket_manifest.txt")
    if not os.path.isfile(manifest_path):
        fail("ticket_manifest.txt not found")
    with open(manifest_path) as f:
        manifest_content = f.read()

    lines = []
    for _orig, new_name, p, c, _i in valid_renames:
        lines.append(f"{new_name} priority={p} created={c}")
    expected_manifest = "\n".join(lines) + "\n"
    if manifest_content != expected_manifest:
        fail("ticket_manifest.txt content does not match expected")

    print("PASS: tickets numbered in priority/created order, rejects untouched")
    sys.exit(0)


if __name__ == "__main__":
    main()
