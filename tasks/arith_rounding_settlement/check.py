import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, compute_net_payout_cents, format_cents  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def main():
    workdir = sys.argv[1]
    out_path = os.path.join(workdir, "settlement_result.txt")
    if not os.path.isfile(out_path):
        fail("settlement_result.txt not found")

    try:
        with open(out_path) as f:
            content = f.read()
    except Exception as e:
        fail(f"could not read output file: {e}")

    rows = generate()
    net_cents = compute_net_payout_cents(rows)
    expected_text = f"net_payout={format_cents(net_cents)}"

    if content.strip() != expected_text:
        fail("settlement_result.txt does not match expected content")

    print("PASS: settlement_result.txt matches expected net payout")
    sys.exit(0)


if __name__ == "__main__":
    main()
