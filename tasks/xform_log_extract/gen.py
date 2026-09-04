"""Generator for xform_log_extract. Stays in tasks/, never copied to workdir."""
import random
from datetime import datetime, timedelta

SEED = 42042042

METHODS = ["GET", "POST", "PUT", "DELETE"]
PATHS = [
    "/api/users", "/api/orders", "/api/orders/detail", "/api/search",
    "/api/login", "/api/logout", "/api/cart", "/api/checkout",
    "/api/inventory", "/api/reports",
]

N_ROWS = 220
TOP_N = 12


def generate(seed=SEED):
    """Return list of dicts: timestamp, request_id, method, path, duration_ms.
    request_id values are strings like 'req_0001'. Durations are integers
    (milliseconds) and duplicates are deliberately injected so ties occur
    among the slowest requests.
    """
    rng = random.Random(seed)
    start = datetime(2024, 3, 1, 0, 0, 0)
    rows = []

    # Deliberately create a cluster of tied durations near the top, larger
    # than TOP_N, so the tie-break rule actually determines which of the
    # tied requests make the cut.
    tie_duration = 4800
    n_tied = 15

    for i in range(N_ROWS):
        ts = start + timedelta(seconds=rng.randint(0, 200000))
        request_id = f"req_{i:04d}"
        method = rng.choice(METHODS)
        path = rng.choice(PATHS)
        if i < n_tied:
            duration_ms = tie_duration
        else:
            duration_ms = rng.randint(5, 4750)
        rows.append({
            "timestamp": ts,
            "request_id": request_id,
            "method": method,
            "path": path,
            "duration_ms": duration_ms,
        })

    rng.shuffle(rows)
    return rows


def format_log_line(row):
    ts = row["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ")
    return f'{ts} {row["request_id"]} {row["method"]} {row["path"]} {row["duration_ms"]}ms'
