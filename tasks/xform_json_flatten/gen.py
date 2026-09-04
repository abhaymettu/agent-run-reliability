"""Generator for xform_json_flatten. Stays in tasks/, never copied to workdir."""
import random

SEED = 7711235

KEYS = [
    "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
    "name", "id", "status", "meta", "tags", "items", "value", "count",
    "flag", "owner", "region", "level", "config", "history", "notes",
]

STRINGS = [
    "red", "blue", "green", "active", "inactive", "pending", "north",
    "south", "east", "west", "draft", "final", "low", "medium", "high",
    "alpha-1", "beta-2", "ok", "error", "unknown",
]


def _rand_leaf(rng):
    t = rng.choice(["str", "int", "bool", "null"])
    if t == "str":
        return rng.choice(STRINGS)
    if t == "int":
        return rng.randint(-1000, 1000)
    if t == "bool":
        return rng.choice([True, False])
    return None


def _rand_value(rng, depth):
    if depth <= 0 or rng.random() < 0.4:
        return _rand_leaf(rng)
    kind = rng.choice(["dict", "list"])
    if kind == "dict":
        nkeys = rng.randint(1, 3)
        keys = rng.sample(KEYS, nkeys)
        return {k: _rand_value(rng, depth - 1) for k in keys}
    else:
        n = rng.randint(1, 8)
        return [_rand_value(rng, depth - 1) for _ in range(n)]


def generate(seed=SEED):
    """Return a nested JSON-serializable document (dict)."""
    rng = random.Random(seed)
    top_keys = rng.sample(KEYS, 9)
    doc = {k: _rand_value(rng, 3) for k in top_keys}
    return doc
