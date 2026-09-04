"""Generator for xform_dedupe_merge. Stays in tasks/, never copied to workdir."""
import random
from datetime import datetime, timedelta

SEED = 90210555

NAMES = [
    "widget", "gadget", "gizmo", "sprocket", "bolt", "gear", "hinge",
    "bracket", "valve", "sensor", "motor", "cable", "panel", "frame",
    "switch", "relay", "filter", "pump", "clamp", "washer",
]

N_IDS = 90


def _rand_date(rng, base):
    return base + timedelta(days=rng.randint(0, 400), hours=rng.randint(0, 23))


def generate(seed=SEED):
    """Return (primary_rows, secondary_rows), each a list of dicts with
    keys: id, name, value, updated_at (a datetime). Within each list ids
    are unique. Roughly half the ids are shared between the two lists,
    each occurrence with its own updated_at (sometimes equal, to force
    the source-priority tie-break), so a real merge/dedupe is required.
    """
    rng = random.Random(seed)
    base = datetime(2024, 1, 1)
    all_ids = [f"P{100 + i}" for i in range(N_IDS)]

    primary_ids = sorted(rng.sample(all_ids, int(N_IDS * 0.75)))
    secondary_ids = sorted(rng.sample(all_ids, int(N_IDS * 0.65)))

    shared = set(primary_ids) & set(secondary_ids)
    tie_ids = set(rng.sample(sorted(shared), min(8, len(shared))))

    primary_rows = []
    for rid in primary_ids:
        primary_rows.append({
            "id": rid,
            "name": rng.choice(NAMES),
            "value": rng.randint(1, 5000),
            "updated_at": _rand_date(rng, base),
        })

    secondary_rows = []
    for rid in secondary_ids:
        if rid in tie_ids:
            # Force an exact-timestamp collision with this id's primary row.
            p_row = next(r for r in primary_rows if r["id"] == rid)
            ts = p_row["updated_at"]
        else:
            ts = _rand_date(rng, base)
        secondary_rows.append({
            "id": rid,
            "name": rng.choice(NAMES),
            "value": rng.randint(1, 5000),
            "updated_at": ts,
        })

    rng.shuffle(primary_rows)
    rng.shuffle(secondary_rows)
    return primary_rows, secondary_rows


def fmt_ts(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S")
