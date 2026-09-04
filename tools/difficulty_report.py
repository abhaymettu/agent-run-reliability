#!/usr/bin/env python3
"""Per-task pass rates from a runs.jsonl, to see where difficulty landed.

Usage: python3 tools/difficulty_report.py results/runs.jsonl
"""
import json
import sys

BAND = (0.3, 0.8)

rows = [json.loads(line) for line in open(sys.argv[1])]
by = {}
for r in rows:
    by.setdefault(r["task_id"], {}).setdefault(r["model"], []).append(bool(r["passed"]))

models = sorted({r["model"] for r in rows})
width = max(len(t) for t in by)
print(f"{'task'.ljust(width)}  " + "  ".join(m.rjust(9) for m in models) + "   in band")
in_band = 0
for task in sorted(by):
    rates = []
    cells = []
    for m in models:
        v = by[task].get(m, [])
        rate = sum(v) / len(v) if v else -1.0  # an empty cell stays out of the band
        rates.append(rate)
        cells.append(f"{sum(v)}/{len(v)} {rate:.2f}".rjust(9))
    ok = all(BAND[0] <= x <= BAND[1] for x in rates)
    in_band += ok
    print(f"{task.ljust(width)}  " + "  ".join(cells) + ("   yes" if ok else ""))

print()
for m in models:
    v = [p for t in by for p in by[t].get(m, [])]
    print(f"{m}: {sum(v)}/{len(v)} = {sum(v)/len(v):.4f}")
print(f"tasks with both models inside [{BAND[0]}, {BAND[1]}]: {in_band}/{len(by)}")

zero_cost = [r for r in rows if r["cost_usd"] == 0 and r["num_turns"] <= 1]
if zero_cost:
    print(f"WARNING: {len(zero_cost)} runs cost nothing and used one turn; "
          "these did not reach a model and are not task failures")

fails = [r for r in rows if not r["passed"]]
absent = [r for r in fails if "not found" in r["check_msg"]]
print(f"failures: {len(fails)}; no output file written: {len(absent)}; "
      f"output written but wrong: {len(fails) - len(absent)} "
      "(chore_* mutate a tree in place, so an untouched tree counts as wrong)")
cut_off = [r for r in rows if r["exit_code"] != 0]
print(f"runs that exited non-zero, which is how the turn cap ends one: "
      f"{len(cut_off)}/{len(rows)}; of those {sum(r['passed'] for r in cut_off)} passed anyway")
