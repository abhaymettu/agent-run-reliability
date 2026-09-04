import datetime
import os
import sys

FMT = "%Y-%m-%dT%H:%M:%S"


def main():
    workdir = sys.argv[1]
    in_path = os.path.join(workdir, "session.log")
    events = []
    with open(in_path) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            ts, rest = line.split(" user=", 1)
            user, event = rest.split(" event=", 1)
            events.append((ts, user, event))

    open_since = {}
    totals = {}

    def parse(s):
        return datetime.datetime.strptime(s, FMT)

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

    out_path = os.path.join(workdir, "session_totals.txt")
    lines = [f"{u}={int(round(totals[u]))}" for u in sorted(totals)]
    with open(out_path, "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
