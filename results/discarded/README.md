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
