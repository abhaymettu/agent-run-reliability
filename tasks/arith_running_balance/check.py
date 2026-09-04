import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, process, format_cents  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def main():
    workdir = sys.argv[1]
    out_path = os.path.join(workdir, "balance_result.txt")
    if not os.path.isfile(out_path):
        fail("balance_result.txt not found")

    try:
        with open(out_path) as f:
            content = f.read()
    except Exception as e:
        fail(f"could not read output file: {e}")

    txns = generate()
    first_neg, final_bal = process(txns)
    expected_date = first_neg if first_neg is not None else "none"
    expected_text = (
        f"first_negative_date={expected_date}\n"
        f"final_balance={format_cents(final_bal)}"
    )

    if content.strip() != expected_text.strip():
        fail("output does not match expected balance_result.txt content")

    print("PASS: balance_result.txt matches expected running-balance result")
    sys.exit(0)


if __name__ == "__main__":
    main()
