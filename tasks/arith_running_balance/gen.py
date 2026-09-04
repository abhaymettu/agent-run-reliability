"""Shared generator for arith_running_balance. Stays in tasks/, never copied to workdir."""
import datetime
import random

SEED = 20260904
START_BALANCE_CENTS = 100000  # 1000.00
OVERDRAFT_LIMIT_CENTS = -50000  # -500.00


def generate(seed=SEED):
    """Return a list of dicts: {date (YYYY-MM-DD str), amount_cents (int)}.

    Amounts are stored as integer cents internally (exact arithmetic); the
    file on disk holds a decimal string like "-120.50". Rows are already in
    the order transactions must be applied (chronological, and for same-day
    rows, file order = application order).

    Deliberately includes:
      - a withdrawal that lands the balance at exactly the overdraft limit
        (-500.00), which is allowed (the rule is "would go BELOW the limit")
      - a withdrawal immediately after that would go below the limit, which
        must be skipped (rejected, balance unchanged)
      - a later transaction that brings the balance to exactly 0.00 (not
        negative)
      - two transactions sharing the same date
    """
    rng = random.Random(seed)
    txns = []
    date = datetime.date(2026, 1, 5)
    for i in range(150):
        gap = rng.choice([1, 1, 1, 2, 3])
        date = date + datetime.timedelta(days=gap)
        amount_cents = rng.randint(-30000, 20000)
        txns.append({"date": date.isoformat(), "amount_cents": amount_cents})

    # two transactions sharing the same date, applied in this file order
    txns[10]["date"] = txns[9]["date"]

    # Determine the balance right before index 40 to plant boundary cases,
    # by replaying the rule up to (not including) index 40.
    balance = START_BALANCE_CENTS
    for i in range(40):
        amt = txns[i]["amount_cents"]
        if balance + amt >= OVERDRAFT_LIMIT_CENTS:
            balance += amt

    # index 40: withdrawal landing exactly on the overdraft limit (allowed)
    txns[40]["amount_cents"] = OVERDRAFT_LIMIT_CENTS - balance
    # index 41: a further withdrawal that would go below the limit -> skipped
    txns[41]["amount_cents"] = -5000

    # Replay forward from index 42 to find a point to plant an exact 0.00 balance.
    balance2 = OVERDRAFT_LIMIT_CENTS  # after index 40; index 41 is skipped, no change
    for i in range(42, 60):
        amt = txns[i]["amount_cents"]
        if balance2 + amt >= OVERDRAFT_LIMIT_CENTS:
            balance2 += amt
    # plant an exact-zero balance at index 60
    txns[60]["amount_cents"] = -balance2

    return txns


def process(txns, start_balance_cents=START_BALANCE_CENTS,
            overdraft_limit_cents=OVERDRAFT_LIMIT_CENTS):
    """Apply transactions in order under the overdraft rule.

    A transaction applies unless doing so would take the balance below the
    overdraft limit (strictly below); a transaction landing exactly on the
    limit is applied. Skipped transactions leave the balance unchanged and
    processing continues with the next transaction.

    Returns (first_negative_date_or_None, final_balance_cents).
    """
    balance = start_balance_cents
    first_negative_date = None
    for t in txns:
        amt = t["amount_cents"]
        if balance + amt >= overdraft_limit_cents:
            balance += amt
        if first_negative_date is None and balance < 0:
            first_negative_date = t["date"]
    return first_negative_date, balance


def format_cents(cents):
    sign = "-" if cents < 0 else ""
    c = abs(cents)
    return f"{sign}{c // 100}.{c % 100:02d}"
