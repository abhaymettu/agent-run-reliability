# Status

Last updated 2026-09-04 01:42 EDT.

## What this is

A study of how many independent runs an agent evaluation needs before a score,
or a ranking between two models, means anything. One run is treated as a
measurement occasion and the pass/fail variance is decomposed into model, task,
model x task, and residual between-run components. `README.md` describes the
apparatus, `REPORT.md` will hold the findings.

## Where it stands

The harness, the validator and the analysis are built and verified. The first
battery has been run to completion, 384 runs, and it hit a ceiling that makes it
useless for the question. A harder battery is being authored to replace it.

## Battery v1 hit the ceiling

384 runs, 24 tasks x 2 models x 8 occasions, complete and balanced, 00:51 to
01:24 EDT, no timeouts and no harness errors. sonnet passed 190 of 192 (0.990),
haiku 183 of 192 (0.953). Twenty of the twenty-four tasks were passed by both
models on all eight occasions, and only one task, arith_running_balance,
separated them at all.

At that pass rate there is essentially no variance to decompose. Every
component estimate would be near zero and the D-study would be reporting noise
about noise. The data is kept in `results/battery_v1/` with a note, because the
ceiling is itself a measurement worth reporting: a task set assembled to look
reasonable landed far above the range where a pass/fail evaluation carries any
reliability information.

## Battery v2, in progress

`docs/DIFFICULTY.md` states the target band, a pass rate of roughly 0.3 to 0.8
per task per model, and the levers that reach it without introducing ambiguity:
sequential state whose trajectory depends on a guard, interacting rules with a
stated precedence, edge cases planted in the generated data so a plausible first
implementation is wrong. The model is arith_running_balance, the one v1 task
that discriminated.

Twenty-four replacement tasks are now written into `tasks_v2/`, six per
category, and all twenty-four pass `tools/validate_tasks.py --tasks-dir
tasks_v2`, re-run here rather than taken from the authors' reports. Each author
also had to name the plausible wrong implementation up front, plant the data
that punishes it, then write that implementation and show the checker rejects
it.

A three-occasion calibration pilot over all 48 cells (144 runs) is running to
measure where the difficulty actually landed before the full grid is committed
to. Three occasions rather than one, so a task's pooled pass rate resolves to
sixths instead of halves.

## Earlier: the discarded pilot

An earlier 59-run pilot was discarded because a session hook on the host writes
a hidden `.remember/` directory into every working directory, and four chore
checkers rejected correct work because of it. The tasks now ignore dot-prefixed
paths and `tools/validate_tasks.py` plants the directory and asserts a solved
workdir still passes. Those runs are in `results/discarded/`.

## Next

1. Validate the twenty-four v2 tasks.
2. Calibration pilot, one occasion per cell, to check the difficulty landed in
   band.
3. Full grid, 24 x 2 x 8.
4. Analysis, then `REPORT.md`.

## Known limitations, to be stated in the report

Subject sessions cannot be isolated from the operator's global configuration on
this machine. `CLAUDE_CONFIG_DIR` pointed at a fresh directory loses
authentication, `--settings '{"hooks":{}}'` does not actually suppress hooks,
and `--bare` skips hooks but requires an API key that is not available here.
Every subject session therefore inherits the same global instructions and
session-hook output. This is constant in form across every cell of the design,
so it does not confound the model comparison, but it does mean the absolute
pass rates describe agents in this environment rather than agents in general.
