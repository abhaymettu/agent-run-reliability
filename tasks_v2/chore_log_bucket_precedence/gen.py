"""Shared generator for chore_log_bucket_precedence. Stays in tasks_v2/,
never copied to workdir."""
import datetime
import random

SEED = 30071996


def classify(line):
    """Apply the bucket rules in the specified precedence order (first
    match wins). Returns the bucket filename."""
    if "CRITICAL" in line:
        return "critical"
    if "ERROR" in line and "db" in line:
        return "db_errors"
    if "ERROR" in line:
        return "errors"
    if "WARN" in line:
        return "warnings"
    return "other"


def generate(seed=SEED):
    """Return a list of log line strings (no trailing newlines), in file
    order.

    Deliberately includes lines that match more than one rule, to test that
    the specified precedence order (checked top to bottom, first match
    wins) is followed rather than some other order:

      - a line containing CRITICAL, ERROR, and "db" -> must go to
        critical.log (rule 1 beats rules 2 and 3).
      - a line containing ERROR and "db" but not CRITICAL -> must go to
        db_errors.log (rule 2, the specific rule, beats rule 3, the
        generic ERROR rule -- an implementation that checks the generic
        ERROR rule before the specific db+ERROR rule gets this wrong).
      - a line containing ERROR but not "db" -> errors.log (rule 3).
      - a line containing WARN and "db" but no ERROR/CRITICAL -> must go
        to warnings.log, NOT db_errors.log (rule 2 requires ERROR; "db"
        alone never triggers it).
      - a line containing both CRITICAL and WARN -> critical.log (rule 1
        beats rule 4).
      - a line with none of the keywords -> other.log.
    """
    rng = random.Random(seed)
    services = ["auth", "payments", "cache", "api", "worker"]
    plain_msgs = ["heartbeat ok", "request served", "cache warmed", "startup complete", "shutdown clean"]
    error_msgs = ["disk write failed", "connection refused", "invalid response", "socket closed"]
    warn_msgs = ["slow response", "queue backing up", "retry scheduled", "memory climbing"]

    lines = []
    ts = datetime.datetime(2026, 2, 1, 0, 0, 0)
    for i in range(36):
        ts += datetime.timedelta(minutes=rng.randint(1, 9))
        kind = rng.choice(["plain", "plain", "error", "warn"])
        svc = rng.choice(services)
        if kind == "plain":
            msg = rng.choice(plain_msgs)
            text = f"{ts.isoformat()} INFO {svc} {msg}"
        elif kind == "error":
            msg = rng.choice(error_msgs)
            text = f"{ts.isoformat()} ERROR {svc} {msg}"
        else:
            msg = rng.choice(warn_msgs)
            text = f"{ts.isoformat()} WARN {svc} {msg}"
        lines.append(text)

    def stamp(i):
        return (datetime.datetime(2026, 2, 1, 0, 0, 0) + datetime.timedelta(minutes=5 * i + 3)).isoformat()

    # Planted precedence-conflict lines at fixed positions.
    lines[4] = f"{stamp(4)} CRITICAL ERROR db connection pool exhausted"
    lines[9] = f"{stamp(9)} ERROR db query failed for payments"
    lines[14] = f"{stamp(14)} ERROR disk write failed"
    lines[19] = f"{stamp(19)} WARN db connection pool nearing limit"
    lines[24] = f"{stamp(24)} CRITICAL WARN memory threshold exceeded"
    lines[29] = f"{stamp(29)} INFO worker node heartbeat ok"

    return lines


def compute_expected(lines):
    """Return {bucket_name: [line, ...]} preserving original order, only for
    buckets with at least one line."""
    buckets = {}
    for line in lines:
        b = classify(line)
        buckets.setdefault(b, []).append(line)
    return buckets
