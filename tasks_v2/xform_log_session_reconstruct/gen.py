"""Shared generator for xform_log_session_reconstruct. Stays in tasks_v2/, never copied to workdir."""
import datetime

SEED = 20260904
USERS = ["alice", "bob", "carol", "dave", "erin", "frank"]


def generate(seed=SEED):
    """Return a chronological list of (timestamp_iso_str, user, event) tuples.

    event is "LOGIN" or "LOGOUT". The list is already in the exact file
    order / chronological order events must be applied in.

    Deliberately plants:
      - a double LOGIN for the same user with no LOGOUT in between (the
        first session must be implicitly closed at the second LOGIN's
        timestamp, not merged into one long session and not dropped)
      - a LOGOUT with no matching open session (must be ignored, contributes
        nothing)
      - a user whose last event is a LOGIN with no closing LOGOUT before
        end of file (must be closed at the timestamp of the very last
        event line in the whole file)
      - a user with zero events who never appears in the output
    """
    rng_state = seed
    events = []
    base = datetime.datetime(2026, 1, 5, 8, 0, 0)
    t = base

    def step(minutes):
        nonlocal t
        t = t + datetime.timedelta(minutes=minutes)
        return t

    def add(user, event):
        events.append((t.strftime("%Y-%m-%dT%H:%M:%S"), user, event))

    # deterministic pseudo-random minute gaps without importing random,
    # to keep the sequence trivially reproducible and easy to audit
    gaps = [3, 7, 2, 11, 5, 13, 4, 9, 6, 17, 8, 1, 14, 10, 3, 19, 5, 2, 12, 7,
            4, 16, 3, 9, 21, 6, 2, 8, 15, 5]
    gi = 0

    def g():
        nonlocal gi
        v = gaps[gi % len(gaps)]
        gi += 1
        return v

    # alice: normal login/logout pairs, several sessions
    step(g()); add("alice", "LOGIN")
    step(g()); add("alice", "LOGOUT")
    step(g()); add("alice", "LOGIN")
    step(g()); add("alice", "LOGOUT")

    # bob: a stray LOGOUT with no open session first (must be ignored)
    step(g()); add("bob", "LOGOUT")
    step(g()); add("bob", "LOGIN")
    step(g()); add("bob", "LOGOUT")

    # carol: double LOGIN with no LOGOUT between -> first session must be
    # closed at the second LOGIN's timestamp
    step(g()); add("carol", "LOGIN")
    step(g()); add("carol", "LOGIN")
    step(g()); add("carol", "LOGOUT")

    # dave: interleaved with other users, normal session
    step(g()); add("dave", "LOGIN")
    step(g()); add("alice", "LOGIN")
    step(g()); add("dave", "LOGOUT")
    step(g()); add("alice", "LOGOUT")

    # erin: LOGIN with no LOGOUT anywhere before EOF -> must be closed at
    # the very last event's timestamp (which belongs to a different user)
    step(g()); add("erin", "LOGIN")

    # more filler activity for bob and carol, and one more stray LOGOUT
    step(g()); add("bob", "LOGIN")
    step(g()); add("carol", "LOGOUT")  # stray, carol has no open session
    step(g()); add("bob", "LOGOUT")

    # triple LOGIN in a row for dave (each LOGIN closes the previous open one)
    step(g()); add("dave", "LOGIN")
    step(g()); add("dave", "LOGIN")
    step(g()); add("dave", "LOGIN")
    step(g()); add("dave", "LOGOUT")

    # final event in the whole file: this timestamp is what closes erin's
    # still-open session
    step(g()); add("alice", "LOGIN")
    step(g()); add("alice", "LOGOUT")

    return events


def process(events):
    """Return {user: total_seconds} following the session reconstruction rule.

    - LOGIN while no open session: opens a session at that timestamp.
    - LOGIN while a session is already open for that user: closes the prior
      session at this new LOGIN's timestamp (duration added), then opens a
      new session at this timestamp.
    - LOGOUT while no open session: ignored.
    - LOGOUT while a session is open: closes it, duration added.
    - Any session still open after the last event in the file is closed
      using the timestamp of that last event line.
    """
    fmt = "%Y-%m-%dT%H:%M:%S"
    open_since = {}
    totals = {}

    def parse(s):
        return datetime.datetime.strptime(s, fmt)

    for ts, user, event in events:
        when = parse(ts)
        if event == "LOGIN":
            if user in open_since:
                dur = (when - open_since[user]).total_seconds()
                totals[user] = totals.get(user, 0) + dur
            open_since[user] = when
        elif event == "LOGOUT":
            if user in open_since:
                dur = (when - open_since[user]).total_seconds()
                totals[user] = totals.get(user, 0) + dur
                del open_since[user]

    if events:
        last_ts = parse(events[-1][0])
        for user, start in open_since.items():
            dur = (last_ts - start).total_seconds()
            totals[user] = totals.get(user, 0) + dur

    return {u: int(round(s)) for u, s in totals.items()}
