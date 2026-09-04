"""Deterministic generator for chore_dedupe_files.

Produces a nested tree of files, some of which are byte-for-byte duplicates
of each other (placed at different paths), some unique.
"""
import random

SEED = 55443322

WORDS = [
    "alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel",
    "india", "juliet", "kilo", "lima", "mike", "november", "oscar", "papa",
]

DIRS = [
    "a", "a/sub1", "a/sub2", "b", "b/deep/deeper", "c", "",
]


def _content(rng, tag, n_lines=4):
    lines = [f"content-block-{tag}"]
    for _ in range(n_lines):
        n_words = rng.randint(3, 7)
        lines.append(" ".join(rng.choice(WORDS) for _ in range(n_words)))
    return ("\n".join(lines) + "\n").encode()


def generate(seed=SEED):
    """Return list of (relative_path, content_bytes)."""
    rng = random.Random(seed)

    # 6 distinct content "blobs"; some get used more than once (duplicates),
    # some exactly once (unique).
    blob_ids = list(range(6))
    blobs = {bid: _content(rng, bid) for bid in blob_ids}

    # usage plan: blob 0 -> 3 copies, blob 1 -> 2 copies, blob 2 -> 2 copies,
    # blobs 3,4,5 -> 1 copy each (unique)
    usage = {0: 3, 1: 2, 2: 2, 3: 1, 4: 1, 5: 1}

    files = []
    counter = 0
    for bid, count in usage.items():
        for _ in range(count):
            d = DIRS[counter % len(DIRS)]
            fname = f"file_{rng.choice(WORDS)}_{counter:02d}.txt"
            relpath = f"{d}/{fname}" if d else fname
            files.append((relpath, blobs[bid]))
            counter += 1

    # shuffle order deterministically so path order doesn't reveal grouping
    rng.shuffle(files)
    return files


def duplicate_manifest(files):
    """Compute expected (kept, [removed...]) groups per the precedence rule:
    within each set of files sharing identical content, keep the file whose
    relative path sorts first (ascending, '/'-separated); the rest are
    removed. Groups of size 1 are not duplicates and are left untouched.
    Returns a dict: kept_path -> sorted list of removed_paths (only for
    groups with duplicates), plus the set of all untouched (unique) paths.
    """
    by_content = {}
    for relpath, content in files:
        by_content.setdefault(content, []).append(relpath)

    groups = {}
    unique_paths = set()
    for content, paths in by_content.items():
        if len(paths) == 1:
            unique_paths.add(paths[0])
            continue
        paths_sorted = sorted(paths)
        kept = paths_sorted[0]
        removed = paths_sorted[1:]
        groups[kept] = removed
    return groups, unique_paths
