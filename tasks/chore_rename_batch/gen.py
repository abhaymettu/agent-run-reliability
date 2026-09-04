"""Deterministic generator for chore_rename_batch.

Produces a flat set of files with arbitrary original names. Each file's
content contains a line "SEQ: <n>" where <n> is a unique integer in
[1, 500). The task is to rename each file to "item_<n padded to 3 digits>"
plus its original extension.
"""
import random

SEED = 830271

NAME_WORDS = [
    "draft", "final", "copy", "temp", "old", "new", "misc", "notes",
    "scan", "export", "raw", "sample", "test", "backup", "data", "log",
]

EXTS = [".txt", ".csv", ".dat", ".log", ".md"]


def generate(seed=SEED):
    """Return list of (filename, content_bytes, seq) tuples with unique seq."""
    rng = random.Random(seed)
    n_files = 15
    seqs = rng.sample(range(1, 500), n_files)
    rng.shuffle(seqs)

    files = []
    used_names = set()
    for i in range(n_files):
        ext = EXTS[i % len(EXTS)]
        while True:
            stem = f"{rng.choice(NAME_WORDS)}{rng.randint(0, 99)}"
            name = f"{stem}{ext}"
            if name not in used_names:
                used_names.add(name)
                break
        seq = seqs[i]
        n_extra = rng.randint(1, 3)
        extra_lines = [f"note line {rng.randint(0,999)}" for _ in range(n_extra)]
        body = f"SEQ: {seq}\n" + "\n".join(extra_lines) + "\n"
        files.append((name, body.encode(), seq))
    return files


def expected_name(orig_name, seq):
    ext = "." + orig_name.rsplit(".", 1)[-1] if "." in orig_name else ""
    return f"item_{seq:03d}{ext}"
