"""Deterministic generator for chore_archive_split.

Produces one large text file whose lines are grouped into chunks separated
by boundary lines that are exactly "---SPLIT---".
"""
import random

SEED = 9182736

WORDS = [
    "alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel",
    "india", "juliet", "kilo", "lima", "mike", "november", "oscar",
]

SOURCE_NAME = "archive.txt"
BOUNDARY = "---SPLIT---"


def generate(seed=SEED):
    """Return (full_text, chunks) where chunks is a list of lists-of-lines
    (each inner list is the lines belonging to one chunk, in order, boundary
    lines excluded). An empty chunk (two boundaries back to back, or a
    boundary at the very start/end) is represented as an empty list.
    """
    rng = random.Random(seed)

    n_chunks = 7
    chunks = []
    for i in range(n_chunks):
        if i == 3:
            # force one deliberately empty chunk (edge case)
            chunks.append([])
            continue
        n_lines = rng.randint(0, 4) if i != n_chunks - 1 else rng.randint(1, 4)
        lines = []
        for _ in range(n_lines):
            n_words = rng.randint(2, 6)
            lines.append(" ".join(rng.choice(WORDS) for _ in range(n_words)))
        chunks.append(lines)

    parts = []
    for i, chunk_lines in enumerate(chunks):
        parts.extend(chunk_lines)
        if i != len(chunks) - 1:
            parts.append(BOUNDARY)

    full_text = "\n".join(parts) + "\n"
    return full_text, chunks
