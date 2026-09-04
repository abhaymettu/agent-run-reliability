"""Shared generator for arith_warehouse_backorder. Stays in tasks_v2/, never copied to workdir."""
import random

SEED = 20260401
STOCK_START = 100


def generate(seed=SEED):
    """Return a list of event dicts in application order:
      {seq, type: "order"|"restock", order_id (str or None), qty (int > 0)}

    Deliberately plants:
      - index 10: an order whose qty exactly equals stock-at-that-point
        (fully fulfilled, NOT partial -- boundary case for "partial" test)
      - index 11: an order right after stock hits exactly 0 (fully
        backordered, qty>0, fulfilled=0 -- also NOT "partial")
      - a restock placed between two orders such that processing events
        out of sequence order (e.g. all restocks first) changes the
        outcome of the order right after it
      - index ~25: the first genuinely partial order (0 < fulfilled < qty)
      - a restock of qty 0 is never generated (qty always > 0) but a
        restock immediately followed by an order that exactly drains it
    """
    rng = random.Random(seed)
    events = []
    order_counter = 1

    def add_order(qty):
        nonlocal order_counter
        oid = f"O{order_counter:04d}"
        order_counter += 1
        events.append({"type": "order", "order_id": oid, "qty": qty})

    def add_restock(qty):
        events.append({"type": "restock", "order_id": None, "qty": qty})

    # organic prefix
    for _ in range(9):
        if rng.random() < 0.7:
            add_order(rng.randint(3, 15))
        else:
            add_restock(rng.randint(10, 40))

    # --- planted boundary: order exactly drains stock (index 9 slot ~10) ---
    # placeholder qty; fixed up after simulating prefix below
    add_order(None)   # index 9 (0-based) -> will become "exact drain"
    add_order(rng.randint(5, 20))  # will be fully backordered (stock will be 0)

    # a restock sitting right before an order that would otherwise be
    # partial -- moving it out of sequence changes the answer
    add_restock(rng.randint(20, 30))
    add_order(None)  # will become the first genuine partial order

    for _ in range(30):
        if rng.random() < 0.55:
            add_order(rng.randint(3, 25))
        else:
            add_restock(rng.randint(5, 35))

    # Now simulate the organic prefix (events[0:9]) to know stock right
    # before the planted "exact drain" order, so we can set its qty exactly.
    stock = STOCK_START
    for e in events[:9]:
        if e["type"] == "restock":
            stock += e["qty"]
        else:
            q = e["qty"]
            if stock >= q:
                stock -= q
            elif stock > 0:
                stock = 0
            else:
                pass

    events[9]["qty"] = stock  # exact drain: fully fulfilled, stock -> 0
    # events[10] stays as-is: stock is 0, so it is fully backordered

    # After events[10] (fully backordered, stock still 0), events[11] is a
    # restock (already added), then events[12] is the planted partial order:
    # set its qty to be strictly greater than the restock amount so it is
    # a genuine partial fulfillment.
    restock_qty = events[11]["qty"]
    events[12]["qty"] = restock_qty + rng.randint(3, 10)

    for i, e in enumerate(events):
        e["seq"] = i + 1

    return events


def process(events, stock_start=STOCK_START):
    """Apply events strictly in list order (== seq order).

    Returns (total_fulfilled, total_backordered, final_stock,
             first_partial_order_id_or_None).
    A "partial" order is one where 0 < fulfilled < qty (strictly between).
    """
    stock = stock_start
    total_fulfilled = 0
    total_backordered = 0
    first_partial = None
    for e in events:
        if e["type"] == "restock":
            stock += e["qty"]
            continue
        qty = e["qty"]
        if stock >= qty:
            fulfilled = qty
            stock -= qty
        elif stock > 0:
            fulfilled = stock
            stock = 0
        else:
            fulfilled = 0
        backordered = qty - fulfilled
        total_fulfilled += fulfilled
        total_backordered += backordered
        if first_partial is None and 0 < fulfilled < qty:
            first_partial = e["order_id"]
    return total_fulfilled, total_backordered, stock, first_partial
