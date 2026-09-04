# Status

Last updated 2026-09-04 00:50 EDT.

## What this is

A study of how many independent runs an agent evaluation needs before a score,
or a ranking between two models, means anything. One run is treated as a
measurement occasion and the pass/fail variance is decomposed into model, task,
model x task, and residual between-run components. `README.md` describes the
apparatus, `REPORT.md` will hold the findings.

## Where it stands

Built and verified:

- 24 tasks in four categories of six, all passing `tools/validate_tasks.py`.
- `harness/run_grid.py`, the concurrent subprocess runner, with append-and-fsync
  checkpointing and resume-by-skipping-completed-cells.
- `analysis/analyze.py` and `analysis/selftest.py`, standard library only, three
  synthetic scenarios recovering known variance components.

Not done:

- The 384-run grid. It has not produced a usable record yet.
- The analysis run, `REPORT.md`, and the final numbers.

## The pilot that was discarded

The grid was launched at 00:38 and killed at 00:47 after 59 runs. A session
hook on the host machine writes a hidden `.remember/` directory into the
working directory of every `claude -p` subject session. Four of the six
`chore_*` tasks enumerate the whole working tree, so that directory appeared in
their end state and their checkers rejected correct agent work. Those four
tasks scored zero across both models for that reason alone.

The tasks are being changed to ignore dot-prefixed paths, in the checkers, in
the reference solutions, and in the prompts. Because the instrument changed, the
59 runs collected before the change are discarded rather than pooled with what
follows; they sit in `results/discarded/` with a note. The grid restarts from
zero.

`tools/validate_tasks.py` is being extended to plant a fake `.remember/`
directory and assert that a solved working directory still passes, so this
failure mode cannot return silently.

Two facts from the pilot are worth keeping. Pass rates over its first 41 runs
were 18/22 for sonnet and 15/19 for haiku, far enough off ceiling that the
battery carries reliability information. Per-run wall time ranged from about 8
to about 236 seconds, and 59 runs completed in 9 minutes at concurrency 4, so
the full grid is comfortably inside the time budget.

## Next

1. Finish and verify the dot-path fix across all affected tasks.
2. Restart the full grid, 24 x 2 x 8.
3. Run the analysis, write `REPORT.md`.

## Known limitations, to be stated in the report

Subject sessions cannot be isolated from the operator's global configuration on
this machine. `CLAUDE_CONFIG_DIR` pointed at a fresh directory loses
authentication, `--settings '{"hooks":{}}'` does not actually suppress hooks,
and `--bare` skips hooks but requires an API key that is not available here.
Every subject session therefore inherits the same global instructions and
session-hook output. This is constant in form across every cell of the design,
so it does not confound the model comparison, but it does mean the absolute
pass rates describe agents in this environment rather than agents in general.
