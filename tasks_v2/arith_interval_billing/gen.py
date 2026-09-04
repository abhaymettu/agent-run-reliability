"""Shared generator for arith_interval_billing. Stays in tasks_v2/, never copied to workdir."""
import random

SEED = 20260703

ROOMS = ["ATRIUM", "BIRCH", "CEDAR"]


def _hm(minutes):
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def generate(seed=SEED):
    """Return a list of dicts {room, reservation_id, start_min, end_min}
    (minutes since 00:00, half-open interval [start, end)).

    Deliberately plants:
      - ATRIUM: two reservations that touch exactly at an endpoint
        (end of one == start of the next) -> must NOT count as overlap
      - BIRCH: three reservations whose common intersection is a real
        triple overlap -> summing pairwise overlap minutes double-counts
        this window; correct answer counts each minute once if covered
        by 2 or more reservations
      - CEDAR: a reservation nested entirely inside another (proper
        containment, not just partial overlap)
      - ATRIUM: also a genuine partial overlap elsewhere in the day
    """
    rng = random.Random(seed)
    rows = []
    rid = 1

    def add(room, start, end):
        nonlocal rid
        rows.append({
            "room": room, "reservation_id": f"R{rid:03d}",
            "start_min": start, "end_min": end,
        })
        rid += 1

    # --- ATRIUM: touching endpoints (no overlap) ---
    add("ATRIUM", 540, 600)   # 09:00-10:00
    add("ATRIUM", 600, 660)   # 10:00-11:00 (touches, not overlapping)
    # a genuine partial overlap later in the day
    add("ATRIUM", 700, 760)   # 11:40-12:40
    add("ATRIUM", 730, 800)   # 12:10-13:20 (overlaps 700-760 by 30 min)
    # organic filler, non-overlapping
    add("ATRIUM", 900, 930)
    add("ATRIUM", 960, 1000)

    # --- BIRCH: real triple overlap ---
    add("BIRCH", 480, 600)    # 08:00-10:00
    add("BIRCH", 540, 660)    # 09:00-11:00
    add("BIRCH", 570, 630)    # 09:30-10:30  (all three overlap 09:30-10:00)
    # organic filler
    add("BIRCH", 800, 850)
    add("BIRCH", 850, 900)    # touches the previous one, no overlap

    # --- CEDAR: proper containment ---
    add("CEDAR", 600, 900)    # 10:00-15:00 (big block)
    add("CEDAR", 660, 720)    # 11:00-12:00 (nested entirely inside)
    add("CEDAR", 1000, 1020)  # organic filler, isolated

    # a bit more organic random filler across rooms, guaranteed not to
    # touch existing planted windows (placed late in the day)
    for room in ROOMS:
        base = 1100 + rng.randint(0, 60)
        dur = rng.randint(20, 45)
        add(room, base, base + dur)

    return rows


def compute_overlap_minutes(rows):
    """Return {room: overlap_minutes} where overlap_minutes is the total
    number of minutes in the day covered by 2 or more reservations for
    that room, using half-open interval semantics (touching endpoints do
    not count as overlap). Uses a sweep line so triple+ overlaps are not
    double-counted."""
    by_room = {}
    for r in rows:
        by_room.setdefault(r["room"], []).append((r["start_min"], r["end_min"]))

    result = {}
    for room, intervals in by_room.items():
        events = []
        for s, e in intervals:
            events.append((s, 1))
            events.append((e, -1))
        events.sort()
        overlap_minutes = 0
        count = 0
        prev_t = None
        for t, delta in events:
            if prev_t is not None and count >= 2:
                overlap_minutes += t - prev_t
            count += delta
            prev_t = t
        result[room] = overlap_minutes
    return result
