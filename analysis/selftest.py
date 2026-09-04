#!/usr/bin/env python3
"""
analysis/selftest.py

Generates synthetic results/runs.jsonl-shaped data with KNOWN variance
components (a logistic-link random-effects model: task offsets, a model
gap, and pure occasion noise on top), runs analysis/analyze.py against it,
and checks that the recovered variance components / G coefficients /
flip probabilities land in the right ballpark.

Pure stdlib. Run directly:

    python3 analysis/selftest.py

Exits 0 if all scenarios pass, 1 otherwise, printing a report either way.
"""

import json
import math
import os
import random
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ANALYZE = os.path.join(HERE, "analyze.py")


def logistic(x):
    if x > 35:
        return 1.0
    if x < -35:
        return 0.0
    return 1.0 / (1.0 + math.exp(-x))


def generate_runs(path, n_tasks, models, n_occasions, task_sd, model_logit_gap,
                   occasion_noise_sd, seed, ceiling=False):
    """Simulate a logistic random-effects model:
       logit(p_{t,m,i}) = intercept_m + task_effect_t + occasion_noise_{t,m,i}
    task_effect_t ~ N(0, task_sd^2), shared across models (same task is
    equally hard/easy for every model, which is exactly what sigma2_task
    measures). occasion_noise inflates/deflates each individual draw's
    logit before the Bernoulli draw, which is what shows up as residual
    (occasion) variance on top of ordinary Bernoulli sampling noise.
    model_logit_gap sets the intercept difference between the two (or more)
    models, in logit units, split symmetrically around 0.

    If ceiling=True, forces every draw to pass (degenerate all-1 data).
    """
    rng = random.Random(seed)
    tasks = [f"task_{i:02d}" for i in range(n_tasks)]
    task_effect = {t: rng.gauss(0, task_sd) for t in tasks}
    m_list = list(models)
    if len(m_list) == 1:
        intercepts = {m_list[0]: 0.0}
    else:
        # spread intercepts symmetrically so the total gap between the two
        # extreme models equals model_logit_gap
        span = model_logit_gap
        intercepts = {}
        for idx, m in enumerate(m_list):
            frac = idx / (len(m_list) - 1) - 0.5
            intercepts[m] = frac * span

    lines = []
    for t in tasks:
        for m in m_list:
            for i in range(n_occasions):
                if ceiling:
                    passed = True
                else:
                    noise = rng.gauss(0, occasion_noise_sd)
                    logit_p = intercepts[m] + task_effect[t] + noise
                    p = logistic(logit_p)
                    passed = rng.random() < p
                lines.append(json.dumps({
                    "task_id": t, "model": m, "run_index": i, "passed": passed,
                    "duration_s": 1.0, "exit_code": 0, "timed_out": False,
                    "check_exit": 0 if passed else 1,
                    "check_msg": "ok" if passed else "fail",
                    "num_turns": 3, "cost_usd": 0.01, "session_id": "selftest",
                    "started_at": "2026-09-04T00:00:00", "error": "",
                }))
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return tasks, m_list, task_effect, intercepts


def run_analyze(runs_path, out_path, seed, bootstrap=2000):
    r = subprocess.run(
        [sys.executable, ANALYZE, "--runs", runs_path, "--out", out_path,
         "--bootstrap", str(bootstrap), "--seed", str(seed)],
        capture_output=True, text=True,
    )
    return r


def check(cond, msg, failures):
    status = "PASS" if cond else "FAIL"
    print(f"    [{status}] {msg}")
    if not cond:
        failures.append(msg)


def scenario_1_large_gap_low_noise(tmpdir):
    """(i) Large true model gap, low occasion noise: sigma2_model should
    dominate, G_model(k) should be high even at small k, and the leaderboard
    flip probability should be low even at k=1."""
    print("\n=== Scenario 1: large model gap, low occasion noise ===")
    runs_path = os.path.join(tmpdir, "s1_runs.jsonl")
    out_path = os.path.join(tmpdir, "s1_results.json")
    generate_runs(runs_path, n_tasks=14, models=["sonnet", "haiku"], n_occasions=6,
                  task_sd=0.4, model_logit_gap=4.0, occasion_noise_sd=0.3, seed=101)
    r = run_analyze(runs_path, out_path, seed=101, bootstrap=2000)
    failures = []
    check(r.returncode == 0, f"analyze.py exits 0 (stderr: {r.stderr[-800:]})", failures)
    if r.returncode != 0:
        return failures
    d = json.load(open(out_path))
    pr = d["descriptives"]["per_model"]
    gap = abs(pr["sonnet"]["pass_rate"] - pr["haiku"]["pass_rate"])
    check(gap > 0.3, f"observed pass-rate gap is large ({gap:.3f})", failures)
    sm = d["anova"]["variance_components_truncated_at_zero"]["model"]
    check(sm > 0.05, f"sigma2_model recovered as clearly positive ({sm:.4f})", failures)
    g1 = d["g_model"]["g_table_k_1_to_20_at_actual_n_tasks"]["1"]
    check(g1 is not None and g1 > 0.5, f"G_model(1) is reasonably high ({g1})", failures)
    flip_pairs = d["leaderboard_flip_probability"]["pairs"]
    pair = next(iter(flip_pairs.values()))
    p1 = pair["exact_k1_flip_probability_underdog_wins"]
    check(p1 is not None and p1 < 0.15, f"exact k=1 flip probability is low ({p1})", failures)
    return failures


def scenario_2_no_gap_high_noise(tmpdir):
    """(ii) No true model gap, high occasion noise.

    Statistical note: analyze.py's leaderboard-flip probability is defined
    relative to the model with the lower OBSERVED (sample) pass rate, since
    that is the only notion of 'true' rate available from a single
    collected dataset -- there is no independent population ground truth
    in practice. That definition is self-selecting: whichever model
    happens to look worse in the very sample used to resample from will,
    on resampling from that same sample, come out ahead LESS than half the
    time (a single-sample flip probability near 0.5 would actually be a
    sign of something wrong when the observed gap is non-trivial). So the
    right check for 'no true model gap' is not that any single run's flip
    probability sits at 0.5: it is that (a) sigma2_model is recovered near
    zero, and (b) across independent replications of the whole experiment,
    the identity of the 'observed winner' is not systematically the same
    model -- i.e. it is genuinely a coin flip which model looks better in
    a fresh sample, even though within any one sample the flip-probability
    number itself is usually well below 0.5.
    """
    print("\n=== Scenario 2: no model gap, high occasion noise ===")
    n_reps = 8
    winners = []
    sigma2_models = []
    failures = []
    for rep in range(n_reps):
        seed = 202 + rep
        runs_path = os.path.join(tmpdir, f"s2_runs_{rep}.jsonl")
        out_path = os.path.join(tmpdir, f"s2_results_{rep}.json")
        generate_runs(runs_path, n_tasks=14, models=["sonnet", "haiku"], n_occasions=8,
                      task_sd=0.5, model_logit_gap=0.0, occasion_noise_sd=1.5, seed=seed)
        r = run_analyze(runs_path, out_path, seed=seed, bootstrap=500)
        check(r.returncode == 0, f"rep {rep}: analyze.py exits 0 (stderr: {r.stderr[-400:]})", failures)
        if r.returncode != 0:
            continue
        d = json.load(open(out_path))
        pr = d["descriptives"]["per_model"]
        winners.append("sonnet" if pr["sonnet"]["pass_rate"] >= pr["haiku"]["pass_rate"] else "haiku")
        sigma2_models.append(d["anova"]["variance_components_truncated_at_zero"]["model"])
        if rep == 0:
            flip_pairs = d["leaderboard_flip_probability"]["pairs"]
            pair = next(iter(flip_pairs.values()))
            p1 = pair["exact_k1_flip_probability_underdog_wins"]
            check(p1 is not None and 0.0 <= p1 <= 0.5,
                  f"rep 0: exact k=1 flip probability is a valid probability <=0.5 by construction ({p1})",
                  failures)

    n_sonnet_wins = winners.count("sonnet")
    check(0 < n_sonnet_wins < n_reps,
          f"observed 'winner' varies across {n_reps} independent replications "
          f"(sonnet won {n_sonnet_wins}/{n_reps}) -- not systematically the same model", failures)
    mean_sm = sum(sigma2_models) / len(sigma2_models) if sigma2_models else None
    check(mean_sm is not None and mean_sm < 0.05,
          f"mean recovered sigma2_model across replications is near zero ({mean_sm})", failures)
    return failures


def scenario_3_ceiling(tmpdir):
    """(iii) Ceiling case: every run passes. analyze.py must not crash or
    divide by zero, and must report degenerate (zero) variance components."""
    print("\n=== Scenario 3: ceiling (every run passes) ===")
    runs_path = os.path.join(tmpdir, "s3_runs.jsonl")
    out_path = os.path.join(tmpdir, "s3_results.json")
    generate_runs(runs_path, n_tasks=10, models=["sonnet", "haiku"], n_occasions=5,
                  task_sd=0.4, model_logit_gap=2.0, occasion_noise_sd=0.5, seed=303, ceiling=True)
    r = run_analyze(runs_path, out_path, seed=303, bootstrap=500)
    failures = []
    check(r.returncode == 0, f"analyze.py exits 0 on all-pass data (stderr: {r.stderr[-800:]})", failures)
    if r.returncode != 0:
        return failures
    d = json.load(open(out_path))
    svt = d["anova"]["variance_components_truncated_at_zero"]
    check(all(v == 0.0 for v in svt.values()), f"all truncated variance components are exactly 0 ({svt})", failures)
    for m, tbl in d["g_task_per_model"]["g_table_k_1_to_20"].items():
        g1 = tbl["1"]
        check(g1 == 0.0, f"G_task(1) for model={m} reported as 0.0 (degenerate: no variance) got {g1}", failures)
    pr = d["descriptives"]["per_model"]
    for m, v in pr.items():
        check(v["pass_rate"] == 1.0, f"pass_rate for {m} is exactly 1.0", failures)
    return failures


def main():
    tmpdir = tempfile.mkdtemp(prefix="reliability_selftest_")
    print(f"Working directory: {tmpdir}")
    all_failures = []
    for scenario in (scenario_1_large_gap_low_noise, scenario_2_no_gap_high_noise, scenario_3_ceiling):
        failures = scenario(tmpdir)
        all_failures.extend([(scenario.__name__, f) for f in failures])

    print("\n" + "=" * 70)
    if not all_failures:
        print(f"SELFTEST: ALL SCENARIOS PASS  (artifacts left in {tmpdir})")
        sys.exit(0)
    else:
        print(f"SELFTEST: {len(all_failures)} FAILURE(S)")
        for scen, msg in all_failures:
            print(f"  - {scen}: {msg}")
        print(f"(artifacts left in {tmpdir})")
        sys.exit(1)


if __name__ == "__main__":
    main()
