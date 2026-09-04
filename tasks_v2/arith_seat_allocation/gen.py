"""Shared generator for arith_seat_allocation. Stays in tasks_v2/, never copied to workdir."""
from fractions import Fraction

SEED = 20260919
TOTAL_SEATS = 100

# Hand-tuned vote counts (total votes = 10000, so each party's exact
# quota is votes/100 and its fractional remainder is (votes % 100) / 100
# -- this keeps the arithmetic exact and lets the tie below be planted
# precisely). Deliberately NOT in alphabetical order in the source file,
# so a checker that sorts only by remainder (stable sort) without an
# explicit alphabetical tie-break would keep BIRCHWOOD ahead of ALDER.
#
# Remainders, descending: GRANITE .60, CASCADE .55, ALDER .50 == BIRCHWOOD
# .50 (exact tie), DELTA .30, FALCON .25, FILLER .20, ELMSTEAD .10.
# Floor seats sum to 97, leaving exactly 3 seats to distribute by largest
# remainder: GRANITE and CASCADE clearly qualify, and the tie between
# ALDER and BIRCHWOOD decides who gets the third and last remaining seat
# -- the alphabetical tie-break must pick ALDER, even though BIRCHWOOD
# appears earlier in the source data.
_VOTES = [
    ("BIRCHWOOD", 1850),
    ("CASCADE", 1555),
    ("ALDER", 1850),
    ("DELTA", 1530),
    ("ELMSTEAD", 10),
    ("FALCON", 1225),
    ("FILLER", 920),
    ("GRANITE", 1060),
]


def generate(seed=SEED):
    """Return a list of dicts {party, votes (int)}, in the fixed planted
    order described above. `seed` is accepted for interface consistency
    with other tasks but the data here is fully hand-tuned."""
    return [{"party": p, "votes": v} for p, v in _VOTES]


def compute_allocation(rows):
    """Largest Remainder (Hamilton) method. Returns {party: seats}."""
    total_votes = sum(r["votes"] for r in rows)
    quotas = {}
    floors = {}
    for r in rows:
        p, v = r["party"], r["votes"]
        exact = Fraction(v * TOTAL_SEATS, total_votes)
        floor_seats = exact.numerator // exact.denominator
        quotas[p] = exact - floor_seats
        floors[p] = floor_seats

    allocated = sum(floors.values())
    remaining = TOTAL_SEATS - allocated

    # sort by remainder descending, tie-break by party name ascending
    order = sorted(rows, key=lambda r: (-quotas[r["party"]], r["party"]))
    seats = dict(floors)
    for r in order[:remaining]:
        seats[r["party"]] += 1

    return seats
