import os
import sys


def stem_ext(name):
    stem, ext = name.rsplit(".", 1)
    return stem, ext


def main():
    workdir = sys.argv[1]

    records = []  # (name, priority, created, content)
    for name in sorted(os.listdir(workdir)):
        if name.startswith("."):
            continue
        full = os.path.join(workdir, name)
        if not os.path.isfile(full):
            continue
        with open(full) as f:
            content = f.read()
        lines = content.splitlines()
        prio = int(lines[0].split(":", 1)[1].strip())
        created = int(lines[1].split(":", 1)[1].strip())
        records.append((name, prio, created, content))

    invalid = [r for r in records if r[1] == 0]
    valid = [r for r in records if r[1] != 0]

    rejected_dir = os.path.join(workdir, "rejected")
    os.makedirs(rejected_dir, exist_ok=True)
    for name, _p, _c, _content in invalid:
        os.rename(os.path.join(workdir, name), os.path.join(rejected_dir, name))

    ordered = sorted(valid, key=lambda r: (r[1], r[2]))
    manifest_lines = []
    for idx, (name, prio, created, content) in enumerate(ordered, start=1):
        stem, ext = stem_ext(name)
        new_name = f"TCK-{idx:04d}_{stem}.{ext}"
        os.rename(os.path.join(workdir, name), os.path.join(workdir, new_name))
        manifest_lines.append(f"{new_name} priority={prio} created={created}")

    with open(os.path.join(workdir, "ticket_manifest.txt"), "w") as f:
        for line in manifest_lines:
            f.write(line + "\n")


if __name__ == "__main__":
    main()
