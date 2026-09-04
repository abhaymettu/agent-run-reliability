"""Generator for xform_reshape_wide. Stays in tasks/, never copied to workdir."""
import random

SEED = 33445566

ATTRS = ["height", "weight", "score", "rating", "duration", "temperature"]

N_IDS = 24


def generate(seed=SEED):
    """Return list of (id, attribute, value) rows, long format, in
    deliberately non-sorted, non-grouped order. Not every id has every
    attribute (missing combos), and some (id, attribute) pairs appear
    more than once (the row appearing LATER in this list, i.e. later
    in the file setup.py writes, is the one that must win).
    """
    rng = random.Random(seed)
    ids = [f"S{i:03d}" for i in range(1, N_IDS + 1)]

    base_rows = []
    for sid in ids:
        chosen_attrs = rng.sample(ATTRS, rng.randint(2, len(ATTRS)))
        for attr in chosen_attrs:
            value = round(rng.uniform(0, 500), 1)
            base_rows.append((sid, attr, value))

    # Inject duplicate (id, attribute) pairs with a different value, to be
    # appended strictly after the original occurrence.
    dup_candidates = rng.sample(base_rows, min(10, len(base_rows)))
    dup_rows = []
    for sid, attr, _old_value in dup_candidates:
        new_value = round(rng.uniform(0, 500), 1)
        dup_rows.append((sid, attr, new_value))

    all_rows = base_rows + dup_rows
    # Shuffle within a fixed structure: interleave everything except we
    # must guarantee dup rows physically follow their originals in file
    # order, so shuffle base_rows and dup_rows separately, then append.
    rng.shuffle(base_rows)
    all_rows = base_rows + dup_rows
    return all_rows
