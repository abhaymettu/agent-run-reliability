import os
import sys


def classify(line):
    if "CRITICAL" in line:
        return "critical"
    if "ERROR" in line and "db" in line:
        return "db_errors"
    if "ERROR" in line:
        return "errors"
    if "WARN" in line:
        return "warnings"
    return "other"


def main():
    workdir = sys.argv[1]
    with open(os.path.join(workdir, "events.log")) as f:
        lines = [l.rstrip("\n") for l in f.readlines()]

    buckets = {}
    for line in lines:
        b = classify(line)
        buckets.setdefault(b, []).append(line)

    buckets_dir = os.path.join(workdir, "buckets")
    os.makedirs(buckets_dir, exist_ok=True)
    for bucket, blines in buckets.items():
        with open(os.path.join(buckets_dir, f"{bucket}.log"), "w") as f:
            for l in blines:
                f.write(l + "\n")

    with open(os.path.join(workdir, "bucket_summary.txt"), "w") as f:
        for bucket in sorted(buckets.keys()):
            f.write(f"{bucket} {len(buckets[bucket])}\n")


if __name__ == "__main__":
    main()
