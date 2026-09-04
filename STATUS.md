# Status

Last updated 2026-09-04 06:05 EDT. The study is complete.

## What this is

A study of how many independent runs an agent evaluation needs before a score,
or a ranking between two models, means anything. One run is treated as a
measurement occasion and the pass/fail variance is decomposed into model, task,
model x task, and residual between-run components. `README.md` describes the
apparatus, `REPORT.md` holds the findings.

## Where it stands

Finished. The full grid ran to completion, 384 runs at a turn budget of 3,
complete and balanced at 8 occasions in every one of the 48 cells, zero
timeouts, zero harness errors, $31.35. `REPORT.md` holds the findings.

Headline: the occasion residual is the largest variance component, 0.118 of a
total 0.236 (50.1%), against 0.100 for task (42.4%), 0.012 for task x model
(5.2%) and 0.005 for model (2.3%) -- run-to-run noise is 21.8x the between-model
signal. Sonnet 135/192 = 0.703, haiku 113/192 = 0.589, difference interval
-0.208 to -0.031. One run per cell orders the two models correctly 84.7% of the
time and two independent single-run evaluations disagree 27.5% of the time
(CI 26.9-28.1); 3 runs bring disagreement under 5%, 6 runs bring the model-level
score to G >= 0.8, from G = 0.500 at a single run.

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

## Battery v2

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

The three-occasion calibration pilot (144 runs, `results/pilot_v2/`) put the
battery at 0.972 pooled, sonnet 0.986 and haiku 0.958, with zero of the
twenty-four tasks in band. Two rounds of deliberate hardening had moved the
pass rate by about one point, so specification-level difficulty was abandoned
as a control.

Difficulty is now set with the turn budget. `harness/run_grid.py --max-turns`
is recorded per run as `max_turns_cap`, and `results/calibration/` holds the
sweep: 0.972 at 40 turns, 0.875 at 6, 0.833 at 4, 0.708 at 3. A budget of 3 is
the tightest setting with both models inside the band (sonnet 0.750, haiku
0.667) and was chosen for the full grid. Prompts were also stripped of
sentences that telegraphed each task's trap.

`tasks_v2/` has been promoted to `tasks/`; the v1 battery is at the tag
`battery-v1`.

## The grid, and the session limit that interrupted it

The full grid was launched at 02:14:49 EDT and the account hit a session limit
at 02:19:48, partway through. From that moment every call returned without
reaching a model and the harness logged each as an ordinary task failure: 301
of the 384 records had `cost_usd == 0`, `num_turns == 1`, and no pass, against
83 real runs that all cost something, used more than one turn, and took at
least 4.8 s. The two groups do not overlap on any of those fields or in time.
Left in place they would have put the pooled pass rate at 52/384 = 0.135 and
charged a billing outage to task difficulty.

The 301 were moved to `results/discarded/quota_limited_cap3.jsonl` with a note
and removed from the grid file. The harness skips cells already present in its
output, so re-running the same command refilled exactly those cells. The
re-run started 05:33 EDT after a single probe call confirmed the limit window
had reset. `tools/difficulty_report.py` now warns if any zero-cost run appears
in a dataset.

## Earlier: the discarded pilot

An earlier 59-run pilot was discarded because a session hook on the host writes
a hidden `.remember/` directory into every working directory, and four chore
checkers rejected correct work because of it. The tasks now ignore dot-prefixed
paths and `tools/validate_tasks.py` plants the directory and asserts a solved
workdir still passes. Those runs are in `results/discarded/`.

## Next

Nothing outstanding. If the work is picked up again, the obvious extension is
the ten tasks that are not in band: the six `codefix_*` tasks sit at ceiling for
both models and `chore_priority_sequence_rename` and `chore_stage_prune` sit at
0/8 for both. Replacing them would sharpen the same design rather than change
it. The other open question the report names is whether the occasion component
still dominates under a generous turn budget, which this battery cannot answer
because a generous budget puts it at ceiling.

## Known limitations, to be stated in the report

Subject sessions cannot be isolated from the operator's global configuration on
this machine. `CLAUDE_CONFIG_DIR` pointed at a fresh directory loses
authentication, `--settings '{"hooks":{}}'` does not actually suppress hooks,
and `--bare` skips hooks but requires an API key that is not available here.
Every subject session therefore inherits the same global instructions and
session-hook output. This is constant in form across every cell of the design,
so it does not confound the model comparison, but it does mean the absolute
pass rates describe agents in this environment rather than agents in general.
