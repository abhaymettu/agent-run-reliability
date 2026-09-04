"""Deterministic generator for chore_file_organize.

Produces a flat set of files (name, content bytes) to be placed at the top
level of the workdir. No sub-directories in the input; the agent creates the
category sub-directories.
"""
import random

SEED = 20240601

# extension -> base category
EXT_CATEGORY = {
    ".py": "code",
    ".sh": "code",
    ".csv": "data",
    ".json": "data",
    ".log": "logs",
    ".txt": "docs",
    ".md": "docs",
    ".jpg": "images",
    ".png": "images",
}

WORDS = [
    "alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel",
    "india", "juliet", "kilo", "lima", "mike", "november", "oscar", "papa",
    "quebec", "romeo", "sierra", "tango", "uniform", "victor", "whiskey",
    "xray", "yankee", "zulu", "report", "backup", "notes", "config", "build",
]


def _lorem(rng, n_lines):
    lines = []
    for _ in range(n_lines):
        n_words = rng.randint(3, 9)
        lines.append(" ".join(rng.choice(WORDS) for _ in range(n_words)))
    return "\n".join(lines) + "\n"


def generate(seed=SEED):
    """Return a list of (filename, content_bytes) tuples.

    A handful of .txt files carry a special first line 'TYPE: data' marking
    them as belonging to the data/ category despite their extension -- this
    is the two-rule-overlap case the task tests.
    """
    rng = random.Random(seed)
    files = []
    exts = list(EXT_CATEGORY.keys())

    n_files = 22
    used_names = set()
    txt_indices_forced_data = set()

    # decide which .txt files (by generation order) get the override marker
    txt_slots = []

    for i in range(n_files):
        ext = exts[i % len(exts)]
        # shuffle-ish deterministic spread using rng too
        while True:
            stem = f"{rng.choice(WORDS)}_{i:02d}"
            name = f"{stem}{ext}"
            if name not in used_names:
                used_names.add(name)
                break
        if ext == ".txt":
            txt_slots.append(len(files))
        files.append([name, ext])

    # pick 3 of the .txt files (deterministically) to be forced into data/
    forced = set(rng.sample(txt_slots, k=min(3, len(txt_slots))))

    result = []
    for idx, (name, ext) in enumerate(files):
        if ext in (".jpg", ".png"):
            # fake binary-ish content, deterministic bytes
            body = bytes(rng.randrange(256) for _ in range(40))
            content = b"FAKEIMG:" + name.encode() + b":" + body
        else:
            n_lines = rng.randint(2, 5)
            text = _lorem(rng, n_lines)
            if ext == ".txt" and idx in forced:
                text = "TYPE: data\n" + text
            content = text.encode()
        result.append((name, content))

    return result


def expected_category(name, content):
    """Ground-truth categorization rule (mirrors prompt.txt)."""
    ext = "." + name.rsplit(".", 1)[-1] if "." in name else ""
    if ext == ".txt":
        first_line = content.split(b"\n", 1)[0]
        if first_line == b"TYPE: data":
            return "data"
        return "docs"
    return EXT_CATEGORY.get(ext, "misc")
