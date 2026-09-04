import os
import sys


def ext_of(name):
    return name.rsplit(".", 1)[-1]


def base_target(name, rid):
    return f"rec_{rid:03d}.{ext_of(name)}"


def main():
    workdir = sys.argv[1]

    # Phase 1: read every file's id and content up front, before touching
    # any file on disk. This avoids any hazard from one file's computed
    # target colliding with another file's still-unread original name.
    records = []  # (orig_name, content, rid)
    for name in sorted(os.listdir(workdir)):
        if name.startswith("."):
            continue
        full = os.path.join(workdir, name)
        if not os.path.isfile(full):
            continue
        with open(full) as f:
            content = f.read()
        first_line = content.splitlines()[0]
        rid = int(first_line.split(":", 1)[1].strip())
        records.append((name, content, rid))

    by_target = {}
    for name, content, rid in records:
        t = base_target(name, rid)
        by_target.setdefault(t, []).append((name, content))

    final_map = {}  # orig_name -> (final_name, content)
    for target, group in by_target.items():
        group_sorted = sorted(group, key=lambda t: t[0])
        stem, ext = target.rsplit(".", 1)
        for idx, (name, content) in enumerate(group_sorted):
            final = target if idx == 0 else f"{stem}_dup{idx}.{ext}"
            final_map[name] = (final, content)

    # Phase 2: remove every original file (content already captured).
    for name, _content, _rid in records:
        os.remove(os.path.join(workdir, name))

    # Phase 3: write every file under its final name.
    for name, (final, content) in final_map.items():
        with open(os.path.join(workdir, final), "w") as f:
            f.write(content)


if __name__ == "__main__":
    main()
