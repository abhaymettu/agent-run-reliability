"""Shared generator for xform_csv_dedupe_versioned. Stays in tasks_v2/, never copied to workdir."""

SEED = 20260904


def generate(seed=SEED):
    """Return a list of dicts: {key, version, seq, payload}, in the exact
    file order rows should be written in.

    Deliberately plants:
      - a key whose highest-version row appears EARLIER in the file than a
        lower-version row for the same key (breaks "last occurrence in
        file wins")
      - a key with two rows sharing the same (tied) highest version,
        broken by the higher "seq" value, where that higher-seq row is
        NOT the one that appears last in the file either
      - a key that appears only once (nothing to dedupe)
      - a key whose rows are scattered non-contiguously through the file
    """
    rows = []

    def add(key, version, seq, payload):
        rows.append({"key": key, "version": version, "seq": seq, "payload": payload})

    # k1: highest version (v3) appears BEFORE a lower version (v2) in the file
    add("k1", 3, 101, "k1-v3-payload")
    add("k2", 1, 102, "k2-v1-payload")
    add("k1", 2, 103, "k1-v2-payload")

    # k3: single occurrence, nothing to dedupe
    add("k3", 1, 104, "k3-only")

    # k4: tie on highest version (v5), broken by seq; the higher-seq row
    # (seq=210) appears BEFORE the lower-seq row (seq=150) in the file,
    # so "last wins" and "first wins" both give the wrong answer
    add("k4", 5, 210, "k4-tie-higher-seq-earlier")
    add("k4", 4, 108, "k4-v4-lower")
    add("k4", 5, 150, "k4-tie-lower-seq-later")

    # k2: scattered, another lower-version row appears later in the file
    add("k2", 3, 109, "k2-v3-payload")

    add("k5", 1, 111, "k5-only")
    add("k2", 2, 112, "k2-v2-payload")

    # k1: another late, low-version straggler
    add("k1", 1, 113, "k1-v1-straggler")

    add("k6", 7, 114, "k6-only")

    return rows


def process(rows):
    """Return {key: (version, seq, payload)} for the winning row per key:
    highest version; ties broken by highest seq."""
    winners = {}
    for r in rows:
        key = r["key"]
        cur = winners.get(key)
        cand = (r["version"], r["seq"], r["payload"])
        if cur is None or (cand[0], cand[1]) > (cur[0], cur[1]):
            winners[key] = cand
    return winners
