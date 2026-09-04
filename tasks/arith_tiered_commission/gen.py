"""Shared generator for arith_tiered_commission. Stays in tasks_v2/, never copied to workdir."""
import random
from decimal import Decimal, ROUND_HALF_UP

SEED = 20260512

# Tiers are on CUMULATIVE monthly sales for a rep, half-open intervals.
# (lower_cents, upper_cents_or_None, rate)
TIERS = [
    (0, 500000, Decimal("0.05")),        # [0, 5000.00)      5%
    (500000, 1500000, Decimal("0.08")),  # [5000.00,15000.00) 8%
    (1500000, None, Decimal("0.12")),    # [15000.00, inf)   12%
]

REPS = ["ADAMS", "BAXTER", "CRUZ"]

CENT = Decimal("0.01")


def _tier_commission_cents(cum_before, amount_cents):
    """Marginal commission (as Decimal dollars, unrounded) for a transaction
    of amount_cents starting at cumulative cum_before (both integer cents)."""
    cum_after = cum_before + amount_cents
    total = Decimal(0)
    for lo, hi, rate in TIERS:
        seg_lo = max(cum_before, lo)
        seg_hi = cum_after if hi is None else min(cum_after, hi)
        if seg_hi > seg_lo:
            seg_amount = Decimal(seg_hi - seg_lo) / 100  # dollars
            total += seg_amount * rate
    return total


def generate(seed=SEED):
    """Return a list of dicts {seq, rep, amount_cents} in application order.

    Deliberately plants (per rep, at specific cumulative points):
      - a transaction whose cum_after lands exactly on the 5000.00 boundary
        (entire amount must be taxed at the 5% tier, since tier 1 is
        half-open [0,5000))
      - a transaction whose cum_before lands exactly on the 5000.00
        boundary (entire amount taxed at 8%)
      - a transaction that spans all the way across the 15000.00 boundary
        in one shot (marginal split across two tiers within one row)
      - a transaction whose raw (unrounded) commission ends in exactly
        .xx5 cents, to test round-half-up
    """
    rng = random.Random(seed)
    rows = []
    seq = 1
    cum = {r: 0 for r in REPS}  # cumulative cents per rep

    def add(rep, amount_cents):
        nonlocal seq
        rows.append({"seq": seq, "rep": rep, "amount_cents": amount_cents})
        cum[rep] += amount_cents
        seq += 1

    # organic warm-up for each rep
    for rep in REPS:
        for _ in range(6):
            add(rep, rng.randint(20000, 90000))

    # ADAMS: land exactly on the 5000.00 boundary
    remaining = 500000 - cum["ADAMS"]
    add("ADAMS", remaining)  # cum_after == 500000 exactly -> all tier1

    # BAXTER: overshoot then land exactly with cum_before == 5000.00
    target = 500000
    diff = target - cum["BAXTER"]
    if diff > 0:
        add("BAXTER", diff)
    else:
        add("BAXTER", rng.randint(5000, 9000))
        diff2 = target - cum["BAXTER"]
        add("BAXTER", diff2 if diff2 > 0 else rng.randint(1000, 2000))
    add("BAXTER", rng.randint(15000, 30000))  # cum_before == 5000.00 exactly

    # CRUZ: single transaction spanning across the 15000.00 boundary
    for _ in range(4):
        add("CRUZ", rng.randint(200000, 300000))  # push cum up near/over 5000-15000 range
    # now force a big single jump across 15000.00
    pre = cum["CRUZ"]
    if pre < 1500000:
        add("CRUZ", 1500000 - pre + 400000)  # crosses the 15000 boundary within one row
    else:
        add("CRUZ", 400000)

    # more organic rows for all reps, with one planted half-cent case
    for _ in range(20):
        rep = rng.choice(REPS)
        amt = rng.randint(1000, 50000)
        add(rep, amt)

    # plant an exact .xx5-cent raw commission for ADAMS: pick an amount such
    # that amount * 0.05 (current tier is tier1 or whichever ADAMS is in)
    # ends in exactly half a cent. Determine ADAMS's current tier rate.
    def rate_at(cum_before):
        for lo, hi, rate in TIERS:
            if cum_before >= lo and (hi is None or cum_before < hi):
                return rate
        return TIERS[-1][2]

    rate = rate_at(cum["ADAMS"])
    # amount_cents * rate must be X.XX5 in dollars -> amount_cents * rate * 100
    # ends in .5 cents. rate is 0.05/0.08/0.12; pick amount_cents = 10 giving
    # 10 cents * rate; simpler: solve amount_cents such that (amount_cents/100)*rate*100
    # has fractional cents .5. amount_cents * rate = commission dollars *100 cents.
    # commission_cents = amount_cents * rate (since amount_cents already /100 *100).
    # Actually commission_dollars = (amount_cents/100)*rate; commission_cents =
    # amount_cents*rate. We want amount_cents*rate to end in .5 exactly.
    for cand in range(1, 400):
        val = Decimal(cand) * rate
        if val == val.to_integral_value() + Decimal("0.5"):
            add("ADAMS", cand)
            break

    for i, r in enumerate(rows):
        r["seq"] = i + 1

    return rows


def compute_commissions(rows):
    """Return {rep: total_commission_cents} using the spec:
    per-transaction marginal commission across tier boundaries, rounded
    half-up to the cent, then summed per rep."""
    cum = {}
    totals = {}
    for row in rows:
        rep = row["rep"]
        amt = row["amount_cents"]
        cum_before = cum.get(rep, 0)
        raw = _tier_commission_cents(cum_before, amt)  # Decimal dollars
        rounded = raw.quantize(CENT, rounding=ROUND_HALF_UP)
        cents = int(rounded * 100)
        totals[rep] = totals.get(rep, 0) + cents
        cum[rep] = cum_before + amt
    return totals


def format_cents(cents):
    sign = "-" if cents < 0 else ""
    c = abs(cents)
    return f"{sign}{c // 100}.{c % 100:02d}"
