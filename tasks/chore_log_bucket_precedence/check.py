import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, compute_expected  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def main():
    workdir = sys.argv[1]
    lines = generate()
    expected_buckets = compute_expected(lines)  # bucket -> [line,...]

    orig_path = os.path.join(workdir, "events.log")
    if not os.path.isfile(orig_path):
        fail("events.log missing")
    with open(orig_path) as f:
        orig_content = f.read()
    expected_orig = "".join(l + "\n" for l in lines)
    if orig_content != expected_orig:
        fail("events.log was modified")

    buckets_dir = os.path.join(workdir, "buckets")
    if not os.path.isdir(buckets_dir):
        fail("buckets/ directory not found")

    actual_bucket_files = set(
        n for n in os.listdir(buckets_dir) if not n.startswith(".")
    )
    expected_bucket_files = set(f"{b}.log" for b in expected_buckets)
    if actual_bucket_files != expected_bucket_files:
        fail(
            f"bucket files mismatch: expected {sorted(expected_bucket_files)}, "
            f"got {sorted(actual_bucket_files)}"
        )

    for bucket, blines in expected_buckets.items():
        path = os.path.join(buckets_dir, f"{bucket}.log")
        with open(path) as f:
            content = f.read()
        expected_content = "".join(l + "\n" for l in blines)
        if content != expected_content:
            fail(f"content mismatch for buckets/{bucket}.log")

    summary_path = os.path.join(workdir, "bucket_summary.txt")
    if not os.path.isfile(summary_path):
        fail("bucket_summary.txt not found")
    with open(summary_path) as f:
        summary_content = f.read()

    summary_lines = []
    for bucket in sorted(expected_buckets.keys()):
        summary_lines.append(f"{bucket} {len(expected_buckets[bucket])}")
    expected_summary = "\n".join(summary_lines) + "\n"
    if summary_content != expected_summary:
        fail("bucket_summary.txt content does not match expected")

    print("PASS: log lines bucketed per precedence rules, summary matches")
    sys.exit(0)


if __name__ == "__main__":
    main()
