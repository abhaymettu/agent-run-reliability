"""Shared generator for chore_rename_collide. Stays in tasks_v2/, never copied
to workdir."""
import random

SEED = 55010203


def generate(seed=SEED):
    """Return a list of (original_name, content_str, record_id_int).

    Each file's content starts with "ID: <n>\\n" followed by a body. The
    base rename target for a file is "rec_<n padded to 3 digits>.<ext>".

    Deliberately includes two hazards:

      - "aardvark.csv" has id 12, so its target is "rec_012.csv" -- which is
        the *original name* of a different file (id 47, target
        "rec_047.csv"). A rename done file-by-file in naive alphabetical
        order renames "aardvark.csv" to "rec_012.csv" before "rec_012.csv"
        has been read/renamed, clobbering it.

      - "bee.txt" and "cat.txt" both have id 8, so both map to the same
        base target "rec_008.txt": a genuine collision requiring the
        stated tie-break.
    """
    rng = random.Random(seed)

    def body(tag):
        return f"body-{tag}-{rng.randint(0, 999999)}\n"

    records = [
        ("aardvark.csv", 12, body("aardvark")),
        ("rec_012.csv", 47, body("rec012-orig")),
        ("bee.txt", 8, body("bee")),
        ("cat.txt", 8, body("cat")),
        ("dog.log", 3, body("dog")),
        ("fox.json", 100, body("fox")),
    ]

    out = []
    for name, rid, b in records:
        content = f"ID: {rid}\n{b}"
        out.append((name, content, rid))
    return out


def ext_of(name):
    return name.rsplit(".", 1)[-1]


def base_target(name, rid):
    return f"rec_{rid:03d}.{ext_of(name)}"


def compute_expected(records):
    """Return {original_name: (final_name, content)}."""
    by_target = {}
    for name, content, rid in records:
        t = base_target(name, rid)
        by_target.setdefault(t, []).append((name, content))

    result = {}
    for target, group in by_target.items():
        group_sorted = sorted(group, key=lambda t: t[0])
        stem, ext = target.rsplit(".", 1)
        for idx, (name, content) in enumerate(group_sorted):
            if idx == 0:
                final = target
            else:
                final = f"{stem}_dup{idx}.{ext}"
            result[name] = (final, content)
    return result
