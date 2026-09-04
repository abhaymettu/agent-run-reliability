"""Shared generator for arith_rounding_settlement. Stays in tasks_v2/, never copied to workdir."""
import random
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP

SEED = 20260808

RATES = {
    "EUR": Decimal("1.0850"),
    "GBP": Decimal("1.2735"),
    "JPY": Decimal("0.0067"),
}

FEE_RATE = Decimal("0.015")  # 1.5%
CENT = Decimal("0.01")


def _find_half_cent_amount(rate, cents_limit=20000):
    """Find the smallest positive cents value C such that
    (C/100 * rate) * 100 lands exactly on an X.XX5 half-cent boundary.
    With the fixed rates used here, the digit immediately before the 5 is
    always even at such a boundary, which means round-half-even rounds
    DOWN (keeps that digit) while round-half-up rounds UP -- the two
    rounding rules disagree. Returns the Decimal dollar amount."""
    for cents in range(1, cents_limit):
        amount = Decimal(cents) / 100
        converted = amount * rate
        scaled = converted * 100
        if scaled == scaled.to_integral_value() + Decimal("0.5"):
            return amount
    raise RuntimeError("no half-cent boundary found within limit")


def generate(seed=SEED):
    """Return a list of dicts {charge_id, amount (Decimal, may be
    negative for refunds), currency}.

    Deliberately plants:
      - a GBP charge whose amount*rate lands exactly on a half-cent
        (X.XX5) boundary where the kept digit is even, so
        round-half-even (keep, round down) and round-half-up (always
        round up) give different rounded results
      - a EUR refund (negative amount) sized so that, once converted and
        rounded, it exactly cancels the running total of every charge
        before it -- driving the pre-fee settlement total, the fee, and
        the net payout all to exactly 0.00, which must print as "0.00"
        and never as "-0.00"
    """
    rng = random.Random(seed)
    rows = []
    cid = 1

    def add(amount, currency):
        nonlocal cid
        rows.append({"charge_id": f"C{cid:04d}", "amount": amount, "currency": currency})
        cid += 1

    # organic charges
    currencies = list(RATES.keys())
    for _ in range(18):
        cur = rng.choice(currencies)
        cents = rng.randint(500, 90000)
        add(Decimal(cents) / 100, cur)

    # planted half-cent disagreement case
    half_cent_amount = _find_half_cent_amount(RATES["GBP"])
    add(half_cent_amount, "GBP")

    # negative-zero case: a EUR refund that exactly cancels the running
    # (converted, rounded) total of every charge added so far
    running_total_cents = 0
    for r in rows:
        rate_r = RATES[r["currency"]]
        converted = (r["amount"] * rate_r).quantize(CENT, rounding=ROUND_HALF_EVEN)
        running_total_cents += int(converted * 100)

    target_cents = -running_total_cents
    approx_amount_cents = int((Decimal(target_cents) / RATES["EUR"]).to_integral_value())
    match = None
    for delta in range(-200, 201):
        cand_cents = approx_amount_cents + delta
        cand_amount = Decimal(cand_cents) / 100
        converted = (cand_amount * RATES["EUR"]).quantize(CENT, rounding=ROUND_HALF_EVEN)
        if int(converted * 100) == target_cents:
            match = cand_amount
            break
    if match is None:
        match = (Decimal(target_cents) / 100 / RATES["EUR"]).quantize(Decimal("0.01"))
    add(match, "EUR")

    return rows


def compute_net_payout_cents(rows):
    total_cents = 0
    for r in rows:
        rate = RATES[r["currency"]]
        converted = (r["amount"] * rate).quantize(CENT, rounding=ROUND_HALF_EVEN)
        total_cents += int(converted * 100)

    total = Decimal(total_cents) / 100
    fee = (total * FEE_RATE).quantize(CENT, rounding=ROUND_HALF_UP)
    net = total - fee
    net_cents = int(net * 100)
    if net_cents == 0:
        net_cents = 0  # normalize away any negative-zero Decimal artifact
    return net_cents


def format_cents(cents):
    if cents == 0:
        return "0.00"
    sign = "-" if cents < 0 else ""
    c = abs(cents)
    return f"{sign}{c // 100}.{c % 100:02d}"
