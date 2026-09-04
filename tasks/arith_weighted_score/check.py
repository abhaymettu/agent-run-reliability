import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, top_k, format_cents  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def main():
    workdir = sys.argv[1]
    out_path = os.path.join(workdir, "top_scores.csv")
    if not os.path.isfile(out_path):
        fail("top_scores.csv not found")

    try:
        with open(out_path) as f:
            content = f.read()
    except Exception as e:
        fail(f"could not read output file: {e}")

    records = generate()
    top = top_k(records, 5)
    expected_lines = ["id,weighted_score"]
    for rid, cents in top:
        expected_lines.append(f"{rid},{format_cents(cents)}")
    expected_text = "\n".join(expected_lines)

    if content.strip() != expected_text.strip():
        fail("output does not match expected top_scores.csv content")

    print("PASS: top_scores.csv matches expected top-5 weighted scores")
    sys.exit(0)


if __name__ == "__main__":
    main()
