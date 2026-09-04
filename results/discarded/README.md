# Discarded pilot

`pilot_contaminated_runs.jsonl` holds 59 runs from the first launch of the grid,
2026-09-04 00:38 to 00:47 EDT. They are not used in the analysis.

A session hook on the host machine writes a hidden `.remember/` directory into
the working directory of every `claude -p` session. Six tasks in the `chore`
category enumerate the whole working tree, so that directory appeared in their
end state and their checkers rejected correct agent work: `chore_dedupe_files`,
`chore_file_organize`, `chore_tree_prune` and `chore_perms_manifest` scored 0 of
0 across both models for that reason alone.

The tasks were changed to ignore any path with a dot-prefixed component, in the
checkers and in the prompts. Because the instrument changed, every run collected
before the change is discarded rather than pooled. The grid was restarted from
zero.

## quota_limited_cap3.jsonl (301 runs, 2026-09-04 02:19:48-02:22:55 EDT)

The account hit a session limit partway through the 384-run grid at
`--max-turns 3`. Every call after 02:19:45 returned immediately without
reaching a model, and the harness recorded each one as an ordinary task
failure. The signature is unambiguous and does not overlap the real runs:
`cost_usd == 0` and `num_turns == 1` for all 301, none passing, none costing
anything; every surviving run has `cost_usd > 0`, `num_turns > 1`, and a
duration of at least 4.8 s. Keeping them would have put the pooled pass rate at
52/384 = 0.135 and attributed a billing outage to task difficulty.

These 301 cells were removed from `results/battery_v2_cap3.jsonl` and re-run
after the limit window reset; the harness skips cells already present in the
output file, so the re-run refilled exactly these and nothing else.
