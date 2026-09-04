"""Generator for xform_csv_pivot. Stays in tasks/, never copied to workdir."""
import random

REGIONS = [
    "Central", "Coastal", "East", "Highland", "Lakeside", "North",
    "Riverside", "South", "Summit", "Valley", "West", "Woodland",
]
QUARTERS = ["Q1", "Q2", "Q3", "Q4"]

SEED = 20240601


def generate(seed=SEED):
    """Return list of (region, quarter, amount) rows, already shuffled."""
    rng = random.Random(seed)
    rows = []
    for region in REGIONS:
        for quarter in QUARTERS:
            # Some region/quarter combos get no rows at all -> must appear as 0.
            if rng.random() < 0.15:
                continue
            n = rng.randint(1, 4)
            for _ in range(n):
                amount = rng.randint(-500, 5000)
                rows.append((region, quarter, amount))
    rng.shuffle(rows)
    return rows
