import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate, compute_ranks_and_bonuses  # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def main():
    workdir = sys.argv[1]
    out_path = os.path.join(workdir, "bonus_result.txt")
    if not os.path.isfile(out_path):
        fail("bonus_result.txt not found")

    try:
        with open(out_path) as f:
            content = f.read()
    except Exception as e:
        fail(f"could not read output file: {e}")

    rows = generate()
    result = compute_ranks_and_bonuses(rows)
    total_bonus = sum(b for _, b in result.values())

    lines = []
    for eid in sorted(result.keys()):
        rank, bonus = result[eid]
        lines.append(f"{eid},{rank},{bonus}")
    lines.append(f"total_bonus={total_bonus}")
    expected_text = "\n".join(lines) + "\n"

    if content != expected_text:
        fail("bonus_result.txt does not match expected content")

    print("PASS: bonus_result.txt matches expected ranking/bonus result")
    sys.exit(0)


if __name__ == "__main__":
    main()
