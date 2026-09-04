"""Deterministic generator for chore_perms_manifest.

Produces a nested tree of files and directories. The task is to chmod every
file according to a priority rule table, leave directories at 755, and write
a manifest of the resulting octal modes.
"""
import random

SEED = 4477889

WORDS = [
    "alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel",
    "india", "juliet", "kilo", "lima",
]

STRUCTURE = [
    # (dir, [(filename, extension, size_bucket)])
    ("", ["deploy.sh", "notes.txt", "secret_keys.txt", "readme.md"]),
    ("bin", ["run.sh", "install.sh", "config.txt"]),
    ("bin/tools", ["helper.sh", "secret_token.dat", "data.csv"]),
    ("docs", ["guide.md", "big_notes.txt"]),
    ("docs/archive", ["old_secret.md", "plan.txt"]),
]


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
    """Return list of (relative_path, content_bytes, is_dir) covering both
    files and the directories that must exist. Files use a target size
    derived deterministically so the size-based rule is exercised.
    """
    rng = random.Random(seed)
    entries = []
    all_dirs = set()

    size_plan = {
        "deploy.sh": 40,
        "notes.txt": 40,
        "secret_keys.txt": 40,
        "readme.md": 150,
        "run.sh": 40,
        "install.sh": 150,
        "config.txt": 150,
        "helper.sh": 40,
        "secret_token.dat": 150,
        "data.csv": 150,
        "guide.md": 40,
        "big_notes.txt": 150,
        "old_secret.md": 40,
        "plan.txt": 40,
    }

    for d, fnames in STRUCTURE:
        if d:
            parts = d.split("/")
            for i in range(1, len(parts) + 1):
                all_dirs.add("/".join(parts[:i]))
        for fn in fnames:
            relpath = f"{d}/{fn}" if d else fn
            size = size_plan[fn]
            content = _content(rng, size)
            entries.append((relpath, content))

    return entries, sorted(all_dirs)


def expected_mode(relpath, content):
    """Priority rule table (mirrors prompt.txt), first match wins:
    1. filename (basename) contains 'secret'      -> 0o600
    2. extension is '.sh'                          -> 0o755
    3. content size > 100 bytes                     -> 0o664
    4. otherwise                                    -> 0o644
    """
    basename = relpath.rsplit("/", 1)[-1]
    if "secret" in basename:
        return 0o600
    if basename.endswith(".sh"):
        return 0o755
    if len(content) > 100:
        return 0o664
    return 0o644
