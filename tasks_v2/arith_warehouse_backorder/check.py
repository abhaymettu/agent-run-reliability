import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, process  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def main():
    workdir = sys.argv[1]
    out_path = os.path.join(workdir, "warehouse_result.txt")
    if not os.path.isfile(out_path):
        fail("warehouse_result.txt not found")

    try:
        with open(out_path) as f:
            content = f.read()
    except Exception as e:
        fail(f"could not read output file: {e}")

    events = generate()
    tf, tb, fs, fp = process(events)
    expected_fp = fp if fp is not None else "none"
    expected_text = (
        f"total_fulfilled={tf}\n"
        f"total_backordered={tb}\n"
        f"final_stock={fs}\n"
        f"first_partial_order={expected_fp}"
    )

    if content.strip() != expected_text.strip():
        fail("warehouse_result.txt does not match expected content")

    print("PASS: warehouse_result.txt matches expected backorder result")
    sys.exit(0)


if __name__ == "__main__":
    main()
