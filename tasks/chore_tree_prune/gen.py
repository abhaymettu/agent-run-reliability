"""Deterministic generator for chore_tree_prune.

Produces a nested tree of files plus a top-level "meta.json" recording each
file's age in days (age is data, never a real mtime). The task is to prune
files matching a multi-condition rule, then remove any directory left empty
as a result (recursively), and write a report.
"""
import json
import random

SEED = 61803398

WORDS = [
    "alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel",
    "india", "juliet", "kilo", "lima", "mike", "november",
]

# (relative_path, extension, age_days, target_size_bytes)
PLAN = [
    ("keep_small.txt", 5, 40),
    ("old_log.log", 40, 40),           # age>30 & ext in {.log,.tmp} -> remove
    ("recent.log", 10, 40),            # keep (age ok, not big, not .bak)
    ("big_file.txt", 5, 6000),         # size>5000 -> remove
    ("archive.bak", 5, 40),            # .bak -> remove regardless
    ("nested/keep2.md", 2, 50),
    ("nested/old.tmp", 45, 30),        # age>30 & .tmp -> remove
    ("nested/deep/only.log", 8, 20),   # keep; but dir becomes empty only if this removed
    ("nested/deep/big.dat", 3, 5500),  # size>5000 -> remove; makes deep/ empty after only.log stays? no only.log kept so not empty
    ("solo/lonely.bak", 1, 10),        # .bak -> remove; solo/ becomes empty -> pruned
    ("keep_dir/a.txt", 1, 10),
    ("keep_dir/b.txt", 60, 60),        # age>30 but ext .txt not in {.log,.tmp} -> keep
]

SIZE_LIMIT = 5000
AGE_LIMIT = 30
AGE_EXTS = {".log", ".tmp"}
ALWAYS_REMOVE_EXTS = {".bak"}


def _content(rng, target_size):
    lines = []
    total = 0
    while total < target_size:
        n_words = rng.randint(3, 8)
        line = " ".join(rng.choice(WORDS) for _ in range(n_words)) + "\n"
        lines.append(line)
        total += len(line)
    return "".join(lines).encode()


def generate(seed=SEED):
    """Return (entries, meta) where entries is a list of
    (relative_path, content_bytes) and meta is {relative_path: age_days}.
    """
    rng = random.Random(seed)
    entries = []
    meta = {}
    for relpath, age, size in PLAN:
        content = _content(rng, size)
        entries.append((relpath, content))
        meta[relpath] = age
    return entries, meta


def _ext(relpath):
    base = relpath.rsplit("/", 1)[-1]
    return "." + base.rsplit(".", 1)[-1] if "." in base else ""


def should_remove(relpath, content, age_days):
    ext = _ext(relpath)
    if age_days > AGE_LIMIT and ext in AGE_EXTS:
        return True
    if len(content) > SIZE_LIMIT:
        return True
    if ext in ALWAYS_REMOVE_EXTS:
        return True
    return False


def expected_state(entries, meta):
    """Return (removed_paths, survived_paths, survived_dirs) sorted lists."""
    removed = []
    survived = []
    for relpath, content in entries:
        age = meta[relpath]
        if should_remove(relpath, content, age):
            removed.append(relpath)
        else:
            survived.append(relpath)

    # directories that exist after pruning: a directory survives iff it (or
    # one of its descendant directories) still contains a surviving file.
    survived_set = set(survived)
    all_dirs = set()
    for relpath, _content in entries:
        parts = relpath.split("/")[:-1]
        for i in range(1, len(parts) + 1):
            all_dirs.add("/".join(parts[:i]))

    survived_dirs = set()
    for d in all_dirs:
        prefix = d + "/"
        if any(s.startswith(prefix) for s in survived_set):
            survived_dirs.add(d)

    return sorted(removed), sorted(survived), sorted(survived_dirs)
