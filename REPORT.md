# How many runs does an agent evaluation need?

Across 384 runs of a 24-task battery against two models at eight independent
occasions each, the largest single source of variance in pass/fail is not the
task and not the model but the run: the occasion residual is 0.118 of a total
0.236, 50.1 percent, against 0.100 (42.4 percent) for the task, 0.012 (5.2
percent) for the model-by-task interaction, and 0.005 (2.3 percent) for the
model itself, the quantity the evaluation exists to measure. Run-to-run noise
is 21.8 times the between-model signal. The consequences are direct. One run
per task per model puts the two models in the correct order 84.7 percent of the
time, with the underdog winning outright 7.2 percent and a dead tie 8.4
percent; two independent single-run evaluations of the same two models disagree
about the winner 27.5 percent of the time (95 percent CI 26.9 to 28.1). Three
runs per cell brings that disagreement to 4.2 percent, four runs to 1.8
percent. A model-level score reaches the conventional G >= 0.8 at six runs per
task over 24 tasks, from G = 0.500 at a single run. Sonnet passed 135 of 192
(0.703) and haiku 113 of 192 (0.589), a gap of 0.115 whose cluster-bootstrap
interval over tasks is -0.208 to -0.031: real, but a gap this size is
indistinguishable from noise in any evaluation that runs each task once. The
often-quoted default of a single run per task is not a small economy on this
battery; it is roughly a one-in-four chance of publishing the wrong ranking.

## Design

The design is fully crossed: 24 tasks x 2 models (`sonnet`, `haiku`) x 8
occasions = 384 runs. Each run is one measurement occasion: a fresh temporary
working directory, a fresh `claude -p` subprocess, a fixed prompt, and a
checker that recomputes ground truth from the task's seeded generator and exits
0 or non-zero. Nothing carries between occasions except the constant
environment. Runs are executed run-index-major, so an interruption at any point
leaves a balanced design rather than a partial block, and the analysis
truncates to the smallest per-cell count if they ever differ.

Tasks come in four families of six. `xform_*` reshapes or joins delimited and
semi-structured files. `arith_*` computes a figure whose value depends on the
order in which rules are applied. `codefix_*` repairs a supplied program that
passes an obvious smoke case and fails a stated one. `chore_*` reorganises a
directory tree under precedence rules. Every task is five files (`gen.py`,
`setup.py`, `prompt.txt`, `check.py`, `solution.py`), is standard library only,
and generates byte-identical inputs on every invocation from a hardcoded seed.
Ground truth is never written into the subject's working directory; the checker
re-derives it. `solution.py` exists so the validator can run each task in both
directions: setup alone must make the checker fail, which catches a checker
that would pass an untouched directory, and setup plus solution must make it
pass, which catches a task nobody could solve. The validator also plants a
hidden dot-prefixed directory in a solved workdir and requires the checker to
still pass.

Difficulty is set by the turn budget, not by the specification. Each subject is
invoked with `--max-turns 3`, recorded per run as `max_turns_cap`. That choice
has its own section below.

## Method

Scoring is binary per run. Variance in the pass indicator is decomposed by
generalizability theory into four components: model, task, model-by-task
interaction, and the occasion residual that remains within a cell. The
decomposition is computed from the expected mean squares of the fully crossed
two-facet design, with negative estimates truncated at zero. Two dependability
coefficients follow. G_task(k) is the reliability of a single model's score
averaged over k occasions on a fixed task set, computed within each model from
its own one-way decomposition; G_model(k, n_tasks) is the reliability of the
model-level score when both tasks and occasions are treated as sampled. The
decision study inverts these to report the k at which each crosses 0.8.
Uncertainty is a cluster bootstrap over whole tasks, 2000 resamples, since
occasions within a task are not independent.

Two estimators address the ranking question directly. The flip probability
resamples k occasions per cell and counts how often the winner differs from the
winner on the full data; at k = 1 it is computed in closed form rather than by
simulation. The disagreement probability draws two independent evaluations of k
occasions each, 20000 iterations per k, and counts how often they name
different winners, a tie counting as a disagreement. The disagreement floor for
two identical models is not 0.5: with three outcomes, two tied Bernoulli(0.8)
models over 14 tasks at k = 1 give P(win) = 0.405, P(tie) = 0.188, P(lose) =
0.408 and so disagree 0.635 of the time. A large disagreement number is what
near-equal models look like, not a defect in the estimator.

The analysis is standard library Python; every statistic is written out rather
than called from a library. The study measures two models from one provider on
one battery under one harness and its numbers describe the reliability of this
instrument rather than of agent evaluation in general; subject sessions inherit
the operator's global configuration and session-hook output, which could not be
suppressed without losing authentication and is constant in form across every
cell; runs executed at concurrency four on one machine, so the occasion
component carries whatever machine-level noise that introduces; scoring is
binary, so a run that misses by one field is indistinguishable from one that
does nothing; and with eight occasions per cell the resampling estimators share
their sample across the two evaluations they compare, which makes the numbers
at k = 8 lower bounds rather than estimates, so k is reported through 4.

## Results

The grid ran with zero timeouts and zero harness errors, at a mean run duration
of 14.5 s and a total cost of $31.35.

    variance component      estimate   share   95% CI (cluster bootstrap)
    occasion (residual)      0.1183    50.1%   0.081 to 0.158
    task                     0.1001    42.4%   0.043 to 0.146
    task x model             0.0123     5.2%   0.000 to 0.028
    model                    0.0054     2.3%   0.000 to 0.021

The model component is the one an evaluation is built to detect and it is the
smallest of the four, with a bootstrap interval that includes zero. This is not
a statement that the models are equal: the direct comparison of pass rates
separates them (0.703 against 0.589, difference interval -0.208 to -0.031).
It is a statement about proportions. Choosing which model to ask is a smaller
lever on whether a given run passes than choosing which task to ask, and both
are smaller than the luck of the individual run.

    k    G_model(k)   G_task(k) haiku   G_task(k) sonnet
    1      0.500          0.542            0.424
    2      0.646          0.703            0.596
    3      0.716          0.780            0.688
    4      0.757          0.825            0.746
    6      0.803          0.876            0.815
    8      0.828          0.904            0.855

At the conventional 0.8 threshold the decision study asks for 6 runs per task
for the model-level score at 24 tasks, 4 for haiku's task-level scores and 6
for sonnet's. The difference between the two models here is itself informative:
sonnet's true-score variance across tasks is smaller (0.090 against haiku's
0.135) while its residual is slightly larger (0.123 against 0.114), so the
stronger model needs more runs to rank its own tasks reliably, not fewer.

    k    P(correct order)   P(flip)   P(tie)   P(two evaluations disagree)
    1        0.847           0.072    0.084          0.2745
    2        0.944           0.028    0.029          0.1059
    3        0.975           0.014    0.012          0.0417
    4        0.988           0.007    0.006          0.0183

The two ranking estimators do not agree on how many runs are enough, and the
gap between them is the point. The flip probability falls below 0.05 at k = 2,
the disagreement probability at k = 3. The flip estimator is optimistic by
construction: it labels the favourite from the same pooled sample it then
resamples, so it grades a comparison against its own answer key. The
disagreement estimator asks the question a practitioner actually faces, which
is whether rerunning the evaluation next week would name the same winner, and
it is the one to quote.

Test-retest on an odd/even split of occasions gives a pooled Pearson r of 0.849
over the 48 task-model scores (95 percent CI 0.736 to 0.922) and a
Spearman-Brown full-length estimate of 0.918; a seeded random split of the same
data gives r = 0.738, which is a fair indication of how much a single split
flatters itself.

Per-task, 4 of the 24 tasks landed with both models inside the 0.3 to 0.8 band.
The six `codefix_*` tasks are at or near ceiling for both models, and two
`chore_*` tasks (`chore_priority_sequence_rename`, `chore_stage_prune`) are at
0/8 for both, a floor. A battery built to sit in the band would need those ten
tasks replaced; the numbers above are what the instrument gives with them in.

Of the 136 failures, 78 wrote no output file at all and 58 wrote an output that
was wrong, counting the in-place `chore_*` tasks conservatively so that an
untouched tree reads as wrong rather than as unwritten. 334 of the 384 runs exited
non-zero, which is how the turn cap ends a run, and 332 of those had used more
turns than the cap allowed; 199 of the 334 passed anyway. Hitting the cap is
the normal case on this battery, not a pathological one.

## How the instrument got here: two ceilings

The first battery of 24 tasks was run in full and is useless as a measuring
instrument: 373 of 384 runs passed, sonnet 0.9896 and haiku 0.9531, with 20 of
the 24 tasks at 8/8 for both models and not one task inside the band. When
almost every run passes, the between-task and between-model variance a G-study
needs is not there to find, and every coefficient collapses toward zero for
lack of true-score variance rather than for excess noise. That dataset is kept
at `results/battery_v1/` and the instrument at the tag `battery-v1`.

A second battery was written from scratch against a harder specification. Task
authors were required to name the plausible wrong implementation, plant data
that punishes it, and demonstrate that the checker rejects it. Prompts that
telegraphed the trap ("an implementation that does not X will be wrong") were
stripped, since they hand over the answer. A 144-run calibration pilot came in
at 140/144 = 0.972 pooled, sonnet 0.9861 and haiku 0.9583, with 0 of 24 tasks
in band: the same ceiling, one decimal place away, after a full rebuild. What a
careful author can plant in a specification, a competent agent reads back out
of it. Specification-level difficulty was abandoned as a control at that point;
the pilot is at `results/pilot_v2/`.

Difficulty was then set with the turn budget, the one lever that moves
monotonically and can be calibrated. Sweeping it over the whole battery, one
occasion per cell:

    budget   sonnet        haiku         pooled
    40       71/72 0.986   69/72 0.958   140/144 0.972
     6       23/24 0.958   19/24 0.792    42/48  0.875
     4       22/24 0.917   18/24 0.750    40/48  0.833
     3       18/24 0.750   16/24 0.667    34/48  0.708

The knob is weaker than the turn distribution suggests. Under the 40-turn
budget sonnet's median usage was 5 turns and haiku's 7, yet cutting the cap to
4 moved the pooled pass rate only from 0.97 to 0.83: most runs do the real work
in the first two or three turns and spend the rest verifying, so trimming turns
removes verification, not work. A budget of 3 was taken for the full grid as
the tightest setting with both models inside the band and close together, which
is the case where the ranking question bites.

This buys a usable spread at a cost that has to be stated plainly: the
construct changed. Under a 3-turn budget a failure can be a wrong answer or a
run cut off before it wrote its output, and the results above show the split is
roughly even. The study therefore measures task completion under a tight
budget, not unconstrained capability. Whether run-to-run variance would still
dominate under a generous budget is not answered here; on this battery a
generous budget produces no variance to decompose at all.

## One part of the grid was not a run

The grid was interrupted by an account session limit five minutes in. From
02:19:48 EDT every subprocess returned without reaching a model, and the
harness recorded each as an ordinary task failure: 301 of 384 records with
`cost_usd == 0`, `num_turns == 1`, and no pass, against 83 real runs that all
cost something, used more than one turn, and took at least 4.8 s. The groups
separate cleanly on cost, on turns, on duration and in time. Left in the
dataset they would have read as a pooled pass rate of 52/384 = 0.135, which is
a billing outage wearing the clothes of task difficulty. The 301 are in
`results/discarded/quota_limited_cap3.jsonl`, those cells were re-run after the
limit window reset, and `tools/difficulty_report.py` now warns when a dataset
contains a run that cost nothing. It is worth recording as a result in its own
right: a failure outside the system under test arrived pre-labelled as a
failure of the system under test, and only the cost and turn-count fields told
them apart. An evaluation harness that does not record what each run cost
cannot make that distinction after the fact.

## Reproducing

    python3 tools/validate_tasks.py
    python3 harness/run_grid.py --models sonnet,haiku --runs 8 \
        --concurrency 4 --timeout 300 --max-turns 3 \
        --out results/battery_v2_cap3.jsonl
    python3 tools/difficulty_report.py results/battery_v2_cap3.jsonl
    python3 analysis/analyze.py --runs results/battery_v2_cap3.jsonl \
        --out results/analysis.json --bootstrap 2000 --seed 20260904 \
        --disagreement-iterations 20000 --disagreement-ci-bootstrap 500

The harness skips cells already present in its output file, so an interrupted
grid resumes by re-running the same command. `results/analysis.json` holds
every number quoted above.
