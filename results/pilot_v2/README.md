# Battery v2 calibration pilot

144 runs: 24 tasks x 2 models x 3 occasions, 2026-09-04 01:39-01:55 EDT, turn
budget 40, concurrency 4, zero timeouts and zero harness errors, $15.17.

The pilot was run to place battery v2 against the 0.3-0.8 target band in
`docs/DIFFICULTY.md` before committing to a full grid. It did not reach the
band. Pooled pass rate was 140/144 = 0.972: sonnet 71/72 = 0.986, haiku
69/72 = 0.958, with 0 of 24 tasks inside the band for both models.

All four failures were `chore_*` tasks, which manipulate a directory tree
under precedence rules: chore_stage_prune (haiku, twice), chore_rename_collide
(haiku), chore_manifest_multiuse_sync (sonnet). Every `arith_*`, `codefix_*`
and `xform_*` task passed on all six of its runs.

This is the second battery to hit the ceiling, after v1 at 0.990 / 0.953. Both
were authored specifically to be hard: v2's authors had to name the plausible
wrong implementation, plant data that punishes it, and demonstrate the checker
rejects it. That the pass rate barely moved between rounds is the reason
difficulty was subsequently set with the turn budget rather than with the task
specifications.

Turn usage under the 40-turn budget, which never bound: sonnet median 5
(p25 4, p75 6, max 27), haiku median 7 (p25 5, p75 8, max 42).
