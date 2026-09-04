"""Shared generator for chore_priority_sequence_rename. Stays in
tasks_v2/, never copied to workdir."""
import random

SEED = 62051977


def generate(seed=SEED):
    """Return a list of (filename, priority_int, created_int, body_str).

    filenames are deliberately chosen so alphabetical order over filenames
    disagrees with the required processing order (ascending priority, then
    ascending created-counter within a priority). Two files (kappa.txt,
    theta.txt) have priority 0 and must be rejected without consuming a
    sequence number -- a naive implementation that numbers every file
    (including the rejected ones) before filtering, or that numbers files
    in filename order, produces different names.
    """
    rng = random.Random(seed)

    def body(tag):
        return f"details for {tag} #{rng.randint(0, 999999)}\n"

    records = [
        ("zeta.txt", 2, 100),
        ("alpha.txt", 1, 300),
        ("mango.log", 1, 50),
        ("delta.csv", 3, 10),
        ("omega.md", 2, 20),
        ("kappa.txt", 0, 5),
        ("theta.txt", 0, 999),
        ("beta.dat", 1, 200),
    ]

    out = []
    for name, prio, created in records:
        out.append((name, prio, created, body(name)))
    return out


def stem_ext(name):
    stem, ext = name.rsplit(".", 1)
    return stem, ext


def compute_expected(records):
    """Return (valid_renames, rejected_names).

    valid_renames: list of (original_name, new_name, priority, created,
      assigned_id), in assigned-id order.
    rejected_names: list of original names (priority == 0), unchanged.
    """
    valid = [r for r in records if r[1] != 0]
    rejected = [r[0] for r in records if r[1] == 0]

    ordered = sorted(valid, key=lambda r: (r[1], r[2]))
    valid_renames = []
    for idx, (name, prio, created, _body) in enumerate(ordered, start=1):
        stem, ext = stem_ext(name)
        new_name = f"TCK-{idx:04d}_{stem}.{ext}"
        valid_renames.append((name, new_name, prio, created, idx))

    return valid_renames, rejected
