"""Shared generator for xform_csv_inventory_allocation. Stays in tasks_v2/, never copied to workdir."""

SEED = 20260904


def generate(seed=SEED):
    """Return (stock, orders).

    stock: list of dicts {sku, qty} - starting global stock pool per sku.
    orders: list of dicts {seq, warehouse, sku, qty}, in SCRAMBLED file
    order (not sorted by seq) - the file's row order is deliberately not
    the processing order.

    A positive qty is a normal order requesting that many units. A
    negative qty is a RETURN: it must be added back to that sku's stock
    pool in full (never partially), and does not itself draw from stock.

    Deliberately plants:
      - orders NOT in seq order in the file (must sort by seq before
        processing)
      - an order requesting more than the currently remaining stock,
        which must be PARTIALLY filled (allocated = remaining stock, not
        0, not rejected outright)
      - a return (negative qty) whose replenishment is required for a
        LATER (by seq) order to be fully fillable - if returns are
        mishandled (skipped, clamped to 0, or misapplied), that later
        order's allocation changes
      - a sku that runs out entirely partway through, so a subsequent
        order for that sku gets allocated exactly 0
    """
    stock = [
        {"sku": "widget", "qty": 50},
        {"sku": "gadget", "qty": 20},
    ]

    orders = [
        # seq 10: normal order, fully fillable
        {"seq": 10, "warehouse": "w1", "sku": "widget", "qty": 30},
        # seq 40 appears before seq 20/30 in the FILE (scrambled order)
        {"seq": 40, "warehouse": "w2", "sku": "widget", "qty": 15},
        # seq 20: requests more widget than remains after seq10 (50-30=20
        # left; requests 25) -> must be PARTIALLY filled: allocated=20
        {"seq": 20, "warehouse": "w1", "sku": "widget", "qty": 25},
        # seq 30: a RETURN of 15 widgets, restoring stock so seq 40 (which
        # is processed AFTER seq30 by seq order despite appearing earlier
        # in the file) can be filled
        {"seq": 30, "warehouse": "w1", "sku": "widget", "qty": -15},
        # seq 50: widget is now fully exhausted (0 remaining) -> allocated 0
        {"seq": 50, "warehouse": "w3", "sku": "widget", "qty": 10},
        # gadget orders, straightforward but out of file order too
        {"seq": 70, "warehouse": "w2", "sku": "gadget", "qty": 5},
        {"seq": 60, "warehouse": "w1", "sku": "gadget", "qty": 12},
        # seq 80: gadget return
        {"seq": 80, "warehouse": "w3", "sku": "gadget", "qty": -3},
        {"seq": 90, "warehouse": "w2", "sku": "gadget", "qty": 6},
    ]

    return stock, orders


def process(stock, orders):
    """Return a list of (seq, warehouse, sku, requested, allocated) in
    ascending seq order, following FIFO-by-seq partial-fulfillment rules
    with returns replenishing the shared pool."""
    remaining = {s["sku"]: s["qty"] for s in stock}
    result = []
    for o in sorted(orders, key=lambda o: o["seq"]):
        sku = o["sku"]
        req = o["qty"]
        if req < 0:
            # return: add back in full, not itself an allocation draw
            remaining[sku] = remaining.get(sku, 0) - req  # req negative -> adds
            result.append((o["seq"], o["warehouse"], sku, req, req))
        else:
            avail = remaining.get(sku, 0)
            allocated = min(req, avail)
            remaining[sku] = avail - allocated
            result.append((o["seq"], o["warehouse"], sku, req, allocated))
    return result
