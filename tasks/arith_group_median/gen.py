"""Shared generator for arith_group_median. Stays in tasks/, never copied to workdir."""
import random

SEED = 20260904
GROUPS = ["central", "delta", "echo", "foxtrot", "golf",
          "hotel", "north", "south", "east", "west"]


def generate(seed=SEED):
    """Return a list of dicts: {id, group, value} (value is an int, can be negative).

    Deliberately built so:
      - group 'north' has exactly one member (single-member group)
      - group 'south' has an even count (8) so its median is an avg of two middles
      - group 'central' contains an exact tie (two equal values)
    Row order in the returned list is shuffled (not grouped), matching what a
    real dataset dump would look like.
    """
    rng = random.Random(seed)
    sizes = {"north": 1, "south": 8}
    for g in GROUPS:
        if g not in sizes:
            sizes[g] = rng.randint(3, 15)

    records = []
    rid = 1
    for g in GROUPS:
        for _ in range(sizes[g]):
            value = rng.randint(-50, 100)
            records.append({"id": rid, "group": g, "value": value})
            rid += 1

    central_members = [r for r in records if r["group"] == "central"]
    if len(central_members) >= 2:
        central_members[0]["value"] = central_members[1]["value"]

    rng.shuffle(records)
    return records


def group_medians(records):
    by_group = {}
    for r in records:
        by_group.setdefault(r["group"], []).append(r["value"])
    out = {}
    for g, vals in by_group.items():
        vals = sorted(vals)
        n = len(vals)
        if n % 2 == 1:
            median = float(vals[n // 2])
        else:
            median = (vals[n // 2 - 1] + vals[n // 2]) / 2.0
        out[g] = median
    return out
