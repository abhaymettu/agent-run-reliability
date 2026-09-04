#!/usr/bin/env python3
"""
analysis/analyze.py

Reads results/runs.jsonl (see docs/RUN_SCHEMA.md) and produces a full
reliability / generalizability analysis of a fully-crossed task x model
design with repeated occasions (runs) per cell.

Pure Python 3 standard library. No third-party packages. Every statistical
routine (mean, variance, Pearson r, Spearman rho, percentile, bootstrap,
random-effects ANOVA) is implemented here by hand.

Usage:
    python3 analysis/analyze.py --runs results/runs.jsonl --out analysis/results.json \
        [--bootstrap 10000] [--seed 20260904]
"""

import argparse
import json
import math
import random
import sys
from collections import defaultdict, Counter

# --------------------------------------------------------------------------
# Basic stats primitives (stdlib only)
# --------------------------------------------------------------------------

def mean(xs):
    xs = list(xs)
    if not xs:
        return None
    return sum(xs) / len(xs)


def variance(xs, ddof=1):
    """Sample variance (ddof=1) or population variance (ddof=0)."""
    xs = list(xs)
    n = len(xs)
    if n - ddof <= 0:
        return None
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (n - ddof)


def pearson(xs, ys):
    """Pearson correlation. Returns None if undefined (n<2 or zero variance)."""
    n = len(xs)
    if n != len(ys) or n < 2:
        return None
    mx, my = mean(xs), mean(ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0 or syy <= 0:
        return None
    return sxy / math.sqrt(sxx * syy)


def _average_ranks(xs):
    """Rank values with average ranks for ties (1-based)."""
    n = len(xs)
    order = sorted(range(n), key=lambda i: xs[i])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg_rank = (i + 1 + j + 1) / 2.0  # 1-based average rank over tied block
        for k in range(i, j + 1):
            ranks[order[k]] = avg_rank
        i = j + 1
    return ranks


def spearman(xs, ys):
    n = len(xs)
    if n != len(ys) or n < 2:
        return None
    rx = _average_ranks(xs)
    ry = _average_ranks(ys)
    return pearson(rx, ry)


def spearman_brown(r, factor=2.0):
    """Step up a correlation measured on a half-length test to full length
    (factor=2 doubles the length, as with an odd/even split)."""
    if r is None:
        return None
    denom = 1 + (factor - 1) * r
    if denom == 0:
        return None
    return (factor * r) / denom


def percentile(sorted_xs, p):
    """Linear-interpolation percentile (numpy 'linear' method), p in [0,100].
    sorted_xs must already be sorted ascending."""
    n = len(sorted_xs)
    if n == 0:
        return None
    if n == 1:
        return sorted_xs[0]
    idx = (p / 100.0) * (n - 1)
    lo = math.floor(idx)
    hi = math.ceil(idx)
    if lo == hi:
        return sorted_xs[int(idx)]
    frac = idx - lo
    return sorted_xs[lo] + (sorted_xs[hi] - sorted_xs[lo]) * frac


def percentile_ci(values, lo_p=2.5, hi_p=97.5):
    vals = [v for v in values if v is not None and not (isinstance(v, float) and math.isnan(v))]
    if not vals:
        return {"lo": None, "hi": None, "n_valid": 0, "n_total": len(values)}
    vals.sort()
    return {
        "lo": percentile(vals, lo_p),
        "hi": percentile(vals, hi_p),
        "n_valid": len(vals),
        "n_total": len(values),
    }


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------

def load_runs(path):
    runs = []
    with open(path) as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"WARNING: skipping malformed line {line_no}: {e}", file=sys.stderr)
                continue
            runs.append(rec)
    return runs


# --------------------------------------------------------------------------
# Grid construction / balancing
# --------------------------------------------------------------------------

def build_cells(runs):
    """cell[(task,model)] -> list of run dicts, deduped by run_index, sorted
    ascending by run_index."""
    cell = defaultdict(dict)  # (t,m) -> {run_index: record}
    for r in runs:
        t, m = r.get("task_id"), r.get("model")
        ri = r.get("run_index")
        if t is None or m is None or ri is None:
            continue
        cell[(t, m)][ri] = r  # last one wins on duplicate run_index
    out = {}
    for key, d in cell.items():
        out[key] = [d[i] for i in sorted(d.keys())]
    return out


def prune_to_full_grid(tasks, models, counts):
    """Drop tasks/models with any missing cell until the remaining tasks x
    models grid is fully crossed (every cell present with count>=1). Prefers
    to drop tasks over models (models are the facet of primary interest and
    we want to keep both), then whichever entity clears the most missing
    cells. Returns (tasks_kept, models_kept, dropped_tasks, dropped_models)."""
    tasks = list(tasks)
    models = list(models)
    dropped_tasks, dropped_models = [], []
    while True:
        missing = [(t, m) for t in tasks for m in models if counts.get((t, m), 0) == 0]
        if not missing or not tasks or not models:
            break
        miss_t = Counter(t for t, m in missing)
        miss_m = Counter(m for t, m in missing)
        worst_t = miss_t.most_common(1)[0] if miss_t else (None, -1)
        worst_m = miss_m.most_common(1)[0] if miss_m else (None, -1)
        # Prefer to preserve models (only a couple, primary facet of interest);
        # drop the task causing the most missing cells unless every remaining
        # missing cell traces to a single model with no missing-task option.
        if worst_t[1] >= 0 and len(tasks) > 1 and (worst_t[1] >= worst_m[1] or len(models) <= 1):
            tasks = [t for t in tasks if t != worst_t[0]]
            dropped_tasks.append(worst_t[0])
        elif len(models) > 1:
            models = [m for m in models if m != worst_m[0]]
            dropped_models.append(worst_m[0])
        else:
            break
    return tasks, models, dropped_tasks, dropped_models


def make_balanced(task_list, model_list, cells, n):
    """data[t][m] = list of n boolean-as-int pass values, using the first n
    (by run_index) available runs in that cell."""
    data = {t: {} for t in task_list}
    for t in task_list:
        for m in model_list:
            recs = cells.get((t, m), [])
            vals = [1 if r.get("passed") else 0 for r in recs[:n]]
            data[t][m] = vals
    return data


# --------------------------------------------------------------------------
# Random-effects two-way ANOVA with replication (balanced)
# --------------------------------------------------------------------------

def anova_two_way(task_list, model_list, data, n):
    """Balanced two-way random-effects ANOVA with n replicates (occasions)
    per cell. task_list x model_list is the crossed design; both factors
    are treated as random for the purpose of estimating variance
    components (model is additionally the facet of substantive interest,
    but the EMS algebra used here is the standard fully-random two-way
    layout with replication).

    Standard expected-mean-squares (Searle, Casella & McCulloch, 'Variance
    Components', balanced two-factor random model with replication):

        E[MS_task]  = sigma2_res + n*sigma2_TM + M*n*sigma2_task
        E[MS_model] = sigma2_res + n*sigma2_TM + T*n*sigma2_model
        E[MS_TM]    = sigma2_res + n*sigma2_TM
        E[MS_res]   = sigma2_res

    giving the method-of-moments (ANOVA) estimators:

        sigma2_res  = MS_res
        sigma2_TM   = (MS_TM  - MS_res) / n
        sigma2_task = (MS_task - MS_TM) / (M*n)
        sigma2_model= (MS_model- MS_TM) / (T*n)
    """
    T, M = len(task_list), len(model_list)
    all_vals = [data[t][m][i] for t in task_list for m in model_list for i in range(n)]
    N = len(all_vals)
    grand = mean(all_vals)

    task_mean = {t: mean([data[t][m][i] for m in model_list for i in range(n)]) for t in task_list}
    model_mean = {m: mean([data[t][m][i] for t in task_list for i in range(n)]) for m in model_list}
    cell_mean = {(t, m): mean(data[t][m]) for t in task_list for m in model_list}

    SS_task = M * n * sum((task_mean[t] - grand) ** 2 for t in task_list)
    SS_model = T * n * sum((model_mean[m] - grand) ** 2 for m in model_list)
    SS_TM = n * sum(
        (cell_mean[(t, m)] - task_mean[t] - model_mean[m] + grand) ** 2
        for t in task_list for m in model_list
    )
    SS_res = sum(
        (data[t][m][i] - cell_mean[(t, m)]) ** 2
        for t in task_list for m in model_list for i in range(n)
    )
    SS_total = sum((v - grand) ** 2 for v in all_vals)

    df_task = T - 1
    df_model = M - 1
    df_TM = (T - 1) * (M - 1)
    df_res = T * M * (n - 1)

    MS_task = SS_task / df_task if df_task > 0 else None
    MS_model = SS_model / df_model if df_model > 0 else None
    MS_TM = SS_TM / df_TM if df_TM > 0 else None
    MS_res = SS_res / df_res if df_res > 0 else None

    sigma2_res = MS_res
    sigma2_TM = ((MS_TM - MS_res) / n) if (MS_TM is not None and MS_res is not None) else None
    sigma2_task = (
        ((MS_task - MS_TM) / (M * n)) if (MS_task is not None and MS_TM is not None) else None
    )
    sigma2_model = (
        ((MS_model - MS_TM) / (T * n)) if (MS_model is not None and MS_TM is not None) else None
    )

    def trunc(x):
        return None if x is None else max(0.0, x)

    return {
        "T": T, "M": M, "n": n, "N": N,
        "grand_mean": grand,
        "SS": {"task": SS_task, "model": SS_model, "task_x_model": SS_TM,
               "residual": SS_res, "total": SS_total},
        "df": {"task": df_task, "model": df_model, "task_x_model": df_TM, "residual": df_res},
        "MS": {"task": MS_task, "model": MS_model, "task_x_model": MS_TM, "residual": MS_res},
        "sigma2_raw": {
            "task": sigma2_task, "model": sigma2_model,
            "task_x_model": sigma2_TM, "residual": sigma2_res,
        },
        "sigma2_truncated_at_zero": {
            "task": trunc(sigma2_task), "model": trunc(sigma2_model),
            "task_x_model": trunc(sigma2_TM), "residual": trunc(sigma2_res),
        },
    }


def anova_one_way(item_list, data_by_item, n):
    """Balanced one-way random-effects ANOVA (items random, n replicates
    per item). Used for the per-model G_task(k) computation: tasks are the
    random items, occasions are the residual, for a single fixed model.

    E[MS_item] = sigma2_res + n*sigma2_item
    E[MS_res]  = sigma2_res
    """
    I = len(item_list)
    all_vals = [data_by_item[it][i] for it in item_list for i in range(n)]
    grand = mean(all_vals)
    item_mean = {it: mean(data_by_item[it]) for it in item_list}

    SS_item = n * sum((item_mean[it] - grand) ** 2 for it in item_list)
    SS_res = sum((data_by_item[it][i] - item_mean[it]) ** 2 for it in item_list for i in range(n))

    df_item = I - 1
    df_res = I * (n - 1)

    MS_item = SS_item / df_item if df_item > 0 else None
    MS_res = SS_res / df_res if df_res > 0 else None

    sigma2_res = MS_res
    sigma2_item = ((MS_item - MS_res) / n) if (MS_item is not None and MS_res is not None) else None

    def trunc(x):
        return None if x is None else max(0.0, x)

    return {
        "I": I, "n": n,
        "MS": {"item": MS_item, "residual": MS_res},
        "sigma2_raw": {"item": sigma2_item, "residual": sigma2_res},
        "sigma2_truncated_at_zero": {"item": trunc(sigma2_item), "residual": trunc(sigma2_res)},
    }


# --------------------------------------------------------------------------
# G coefficients
# --------------------------------------------------------------------------

def g_task_table(sigma2_task, sigma2_res, ks):
    """Relative-error G for a task score averaged over k occasions, for a
    fixed model: sigma2_task / (sigma2_task + sigma2_res/k). Variance
    components used here are truncated-at-zero (a negative estimate is
    treated as zero signal for reliability purposes -- see README note in
    output)."""
    out = {}
    for k in ks:
        if sigma2_task is None or sigma2_res is None:
            out[k] = None
            continue
        st = max(0.0, sigma2_task)
        sr = max(0.0, sigma2_res)
        denom = st + (sr / k if k > 0 else 0.0)
        out[k] = (st / denom) if denom > 0 else (1.0 if st > 0 else 0.0)
    return out


def g_model_value(sigma2_model, sigma2_tm, sigma2_res, n_tasks, k):
    if sigma2_model is None or sigma2_tm is None or sigma2_res is None:
        return None
    sm = max(0.0, sigma2_model)
    stm = max(0.0, sigma2_tm)
    sr = max(0.0, sigma2_res)
    denom = sm + (stm / n_tasks if n_tasks > 0 else 0.0) + (sr / (n_tasks * k) if n_tasks > 0 and k > 0 else 0.0)
    if denom <= 0:
        return 1.0 if sm > 0 else 0.0
    return sm / denom


def g_model_table(sigma2_model, sigma2_tm, sigma2_res, n_tasks, ks):
    return {k: g_model_value(sigma2_model, sigma2_tm, sigma2_res, n_tasks, k) for k in ks}


def smallest_k_for_g_task(sigma2_task, sigma2_res, target=0.8, cap=20):
    if sigma2_task is None or sigma2_res is None:
        return {"k": None, "reachable": False, "reason": "variance components unavailable"}
    st = max(0.0, sigma2_task)
    sr = max(0.0, sigma2_res)
    if st <= 0:
        return {"k": None, "reachable": False,
                "reason": "sigma2_task truncated to 0: no detectable task-level signal, "
                          "G_task(k)=0 for all k regardless of replication"}
    if sr <= 0:
        return {"k": 1, "reachable": True, "reason": "sigma2_residual truncated to 0: G_task(1) already 1.0"}
    # solve sigma2_task/(sigma2_task+sigma2_res/k) = target  =>  k = sr*target / (st*(1-target))
    k_exact = (sr * target) / (st * (1 - target))
    k_int = max(1, math.ceil(k_exact - 1e-9))
    if k_int <= cap:
        return {"k": k_int, "reachable": True, "reason": f"analytic solve, k>=~{k_exact:.3f}"}
    return {"k": f">{cap}", "reachable": True,
            "reason": f"analytic solve gives k~{k_exact:.1f}, beyond the k=1..{cap} table but reachable in principle"}


def smallest_k_for_g_model(sigma2_model, sigma2_tm, sigma2_res, n_tasks, target=0.8, cap=20):
    if sigma2_model is None or sigma2_tm is None or sigma2_res is None:
        return {"k": None, "reachable": False, "reason": "variance components unavailable"}
    sm = max(0.0, sigma2_model)
    stm = max(0.0, sigma2_tm)
    sr = max(0.0, sigma2_res)
    if sm <= 0:
        return {"k": None, "reachable": False,
                "reason": "sigma2_model truncated to 0: no detectable model-to-model signal"}
    g_inf = sm / (sm + (stm / n_tasks if n_tasks > 0 else 0.0)) if (sm + stm) > 0 else 1.0
    if g_inf < target:
        return {"k": None, "reachable": False,
                "reason": (f"as k->infinity G_model -> {g_inf:.4f} < {target} at n_tasks={n_tasks}; "
                           "the task x model interaction variance is too large relative to sigma2_model "
                           "for any number of occasions per task to close the gap -- more tasks, not more "
                           "occasions, would be needed")}
    rhs = sm * ((1 / target) - 1) - (stm / n_tasks)
    if rhs <= 0:
        return {"k": 1, "reachable": True, "reason": "already at/above target by k=1"}
    k_exact = sr / (n_tasks * rhs)
    k_int = max(1, math.ceil(k_exact - 1e-9))
    if k_int <= cap:
        return {"k": k_int, "reachable": True, "reason": f"analytic solve, k>=~{k_exact:.3f}"}
    return {"k": f">{cap}", "reachable": True,
            "reason": f"analytic solve gives k~{k_exact:.1f}, beyond the k=1..{cap} table but reachable in principle"}


# --------------------------------------------------------------------------
# Leaderboard flip probability
# --------------------------------------------------------------------------

def exact_single_run_flip(task_list, modelA, modelB, cells_full):
    """Exact single-occasion (k=1) flip probability between two models.
    A single resampled occasion per (task, model) cell is, under
    with-replacement bootstrap resampling of that cell's observed runs,
    exactly a Bernoulli draw with success probability equal to the cell's
    observed pass rate. The per-model score is the unweighted mean over
    tasks of these iid Bernoulli draws. We compute the exact distribution
    of the sum-of-passes for each model via DP convolution (each task
    contributes an independent Bernoulli), then combine the two
    independent per-model sum distributions to get exact P(flip)/P(tie)."""
    def cell_p(t, m):
        recs = cells_full.get((t, m), [])
        if not recs:
            return None
        return mean([1 if r.get("passed") else 0 for r in recs])

    pA = [cell_p(t, modelA) for t in task_list]
    pB = [cell_p(t, modelB) for t in task_list]
    if any(p is None for p in pA) or any(p is None for p in pB):
        return None  # some task missing data for one of the two models

    def dist_of_sum(ps):
        # dist[s] = P(sum of independent Bernoulli(ps) == s)
        dist = [1.0]
        for p in ps:
            new = [0.0] * (len(dist) + 1)
            for s, prob in enumerate(dist):
                if prob == 0:
                    continue
                new[s] += prob * (1 - p)
                new[s + 1] += prob * p
            dist = new
        return dist

    dA = dist_of_sum(pA)
    dB = dist_of_sum(pB)
    T = len(task_list)
    p_a_higher = p_b_higher = p_tie = 0.0
    for sa, pa in enumerate(dA):
        if pa == 0:
            continue
        for sb, pb in enumerate(dB):
            if pb == 0:
                continue
            joint = pa * pb
            if sa > sb:
                p_a_higher += joint
            elif sa < sb:
                p_b_higher += joint
            else:
                p_tie += joint
    return {"p_a_higher": p_a_higher, "p_b_higher": p_b_higher, "p_tie": p_tie, "T": T}


def empirical_flip_probability(task_list, modelA, modelB, cells_full, k, rng, n_resamples):
    """Monte Carlo estimate: resample k occasions with replacement per
    (task, model) cell, average within model over all tasks, record which
    model comes out ahead."""
    cellA = {t: [1 if r.get("passed") else 0 for r in cells_full.get((t, modelA), [])] for t in task_list}
    cellB = {t: [1 if r.get("passed") else 0 for r in cells_full.get((t, modelB), [])] for t in task_list}
    if any(len(v) == 0 for v in cellA.values()) or any(len(v) == 0 for v in cellB.values()):
        return None

    flips_to_a = flips_to_b = ties = 0
    for _ in range(n_resamples):
        avgA = sum(rng.choice(cellA[t]) for t in task_list) / len(task_list) if k == 1 else \
            mean([mean([rng.choice(cellA[t]) for _ in range(k)]) for t in task_list])
        avgB = sum(rng.choice(cellB[t]) for t in task_list) / len(task_list) if k == 1 else \
            mean([mean([rng.choice(cellB[t]) for _ in range(k)]) for t in task_list])
        if avgA > avgB:
            flips_to_a += 1
        elif avgB > avgA:
            flips_to_b += 1
        else:
            ties += 1
    return {
        "p_a_higher": flips_to_a / n_resamples,
        "p_b_higher": flips_to_b / n_resamples,
        "p_tie": ties / n_resamples,
        "n_resamples": n_resamples,
    }


# --------------------------------------------------------------------------
# Test-retest split-half
# --------------------------------------------------------------------------

def split_half_rates(task_list, model_list, cells_full, parity="odd_even", rng=None):
    """Per (task, model), split available occasions into two halves and
    return per-task pass rate vectors for each model, in each half.
    parity='odd_even' splits by run_index % 2; parity='random' shuffles
    (using rng) before splitting in half. Cells with fewer than 2 occasions
    are skipped (task dropped from that model's pair for this split)."""
    half1 = {m: {} for m in model_list}
    half2 = {m: {} for m in model_list}
    for m in model_list:
        for t in task_list:
            recs = cells_full.get((t, m), [])
            if len(recs) < 2:
                continue
            if parity == "odd_even":
                a = [1 if r.get("passed") else 0 for r in recs if r.get("run_index", 0) % 2 == 0]
                b = [1 if r.get("passed") else 0 for r in recs if r.get("run_index", 0) % 2 == 1]
            else:
                idx = list(range(len(recs)))
                rng.shuffle(idx)
                mid = len(idx) // 2
                a_idx, b_idx = idx[:mid], idx[mid:]
                a = [1 if recs[i].get("passed") else 0 for i in a_idx]
                b = [1 if recs[i].get("passed") else 0 for i in b_idx]
            if not a or not b:
                continue
            half1[m][t] = mean(a)
            half2[m][t] = mean(b)
    return half1, half2


def correlate_halves(half1, half2, model_list):
    per_model = {}
    pooled_x, pooled_y = [], []
    for m in model_list:
        common = sorted(set(half1[m]) & set(half2[m]))
        xs = [half1[m][t] for t in common]
        ys = [half2[m][t] for t in common]
        r = pearson(xs, ys)
        rho = spearman(xs, ys)
        per_model[m] = {
            "n_tasks": len(common),
            "pearson_r": r,
            "spearman_rho": rho,
            "spearman_brown_full_length_pearson": spearman_brown(r),
            "spearman_brown_full_length_spearman": spearman_brown(rho),
        }
        pooled_x.extend(xs)
        pooled_y.extend(ys)
    r_pooled = pearson(pooled_x, pooled_y)
    rho_pooled = spearman(pooled_x, pooled_y)
    pooled = {
        "n_points": len(pooled_x),
        "pearson_r": r_pooled,
        "spearman_rho": rho_pooled,
        "spearman_brown_full_length_pearson": spearman_brown(r_pooled),
        "spearman_brown_full_length_spearman": spearman_brown(rho_pooled),
    }
    return per_model, pooled


# --------------------------------------------------------------------------
# Main analysis pipeline (reused for point estimate & each bootstrap replicate)
# --------------------------------------------------------------------------

K_TABLE = list(range(1, 21))


def full_point_estimate(task_list, model_list, cells_full, n_balanced):
    """Compute every headline quantity for a given task list (with possible
    repeats, for bootstrap use) and fixed model list, at balanced n =
    n_balanced occasions/cell. Returns a flat-ish dict of results."""
    data = make_balanced(task_list, model_list, cells_full, n_balanced)
    anova = anova_two_way(task_list, model_list, data, n_balanced)
    s = anova["sigma2_truncated_at_zero"]
    s_raw = anova["sigma2_raw"]

    T = len(task_list)

    # G_task per model (one-way anova within model, on the same task list/n)
    g_task_per_model = {}
    g_task_anova_per_model = {}
    for m in model_list:
        data_m = {t: data[t][m] for t in task_list}
        ow = anova_one_way(task_list, data_m, n_balanced)
        st = ow["sigma2_truncated_at_zero"]["item"]
        sr = ow["sigma2_truncated_at_zero"]["residual"]
        g_task_per_model[m] = g_task_table(st, sr, K_TABLE)
        g_task_anova_per_model[m] = ow

    # G_model table (pooled variance components) over k=1..20 at n_tasks=T,
    # and additionally the actual-n_tasks value is just the T used here.
    g_model_tbl = g_model_table(s["model"], s["task_x_model"], s["residual"], T, K_TABLE)

    # overall pass rates (pooled over the resampled task list's runs)
    pass_rates = {}
    for m in model_list:
        vals = [v for t in task_list for v in data[t][m]]
        pass_rates[m] = mean(vals)

    return {
        "anova": anova,
        "g_task_per_model": g_task_per_model,
        "g_task_anova_per_model": g_task_anova_per_model,
        "g_model_table": g_model_tbl,
        "pass_rates": pass_rates,
        "T": T,
        "n_balanced": n_balanced,
    }


# --------------------------------------------------------------------------
# Reporting helpers
# --------------------------------------------------------------------------

def fmt(x, nd=4):
    if x is None:
        return "NA"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--bootstrap", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=20260904)
    args = ap.parse_args()

    runs = load_runs(args.runs)
    if not runs:
        print(f"ERROR: no runs loaded from {args.runs}", file=sys.stderr)
        sys.exit(1)

    cells_full = build_cells(runs)
    tasks_all = sorted(set(t for t, m in cells_full))
    models_all = sorted(set(m for t, m in cells_full))
    counts = {k: len(v) for k, v in cells_full.items()}

    # ---------------- Descriptives ----------------
    per_cell = {}
    for t in tasks_all:
        for m in models_all:
            recs = cells_full.get((t, m), [])
            if not recs:
                continue
            passed = [1 if r.get("passed") else 0 for r in recs]
            per_cell[f"{t}|{m}"] = {
                "task": t, "model": m,
                "n_runs": len(recs),
                "pass_rate": mean(passed),
                "n_timeouts": sum(1 for r in recs if r.get("timed_out")),
                "n_errors": sum(1 for r in recs if r.get("error")),
            }

    per_model = {}
    for m in models_all:
        recs = [r for (t, mm), rs in cells_full.items() if mm == m for r in rs]
        passed = [1 if r.get("passed") else 0 for r in recs]
        per_model[m] = {
            "n_runs": len(recs),
            "pass_rate": mean(passed),
            "n_timeouts": sum(1 for r in recs if r.get("timed_out")),
            "n_errors": sum(1 for r in recs if r.get("error")),
        }

    per_task = {}
    for t in tasks_all:
        recs = [r for (tt, m), rs in cells_full.items() if tt == t for r in rs]
        passed = [1 if r.get("passed") else 0 for r in recs]
        per_task[t] = {
            "n_runs": len(recs),
            "pass_rate": mean(passed),
            "n_timeouts": sum(1 for r in recs if r.get("timed_out")),
            "n_errors": sum(1 for r in recs if r.get("error")),
        }

    totals = {
        "n_runs": len(runs),
        "n_timeouts": sum(1 for r in runs if r.get("timed_out")),
        "n_errors": sum(1 for r in runs if r.get("error")),
        "n_tasks": len(tasks_all),
        "n_models": len(models_all),
    }

    # ---------------- Balanced subgrid for ANOVA ----------------
    tasks_used, models_used, dropped_tasks, dropped_models = prune_to_full_grid(tasks_all, models_all, counts)
    if not tasks_used or not models_used:
        print("ERROR: no fully-crossed task x model subgrid available; refusing to compute ANOVA.",
              file=sys.stderr)
        sys.exit(1)
    n_balanced = min(counts[(t, m)] for t in tasks_used for m in models_used)

    balance_note = (
        f"Full grid seen: {len(tasks_all)} tasks x {len(models_all)} models. "
        f"Used balanced fully-crossed subgrid: {len(tasks_used)} tasks x {len(models_used)} models, "
        f"n={n_balanced} occasions/cell (first n runs by run_index in each cell). "
    )
    if dropped_tasks or dropped_models:
        balance_note += (
            f"DROPPED to achieve balance -- tasks: {dropped_tasks or 'none'}; "
            f"models: {dropped_models or 'none'} (cells missing entirely for these)."
        )
    else:
        balance_note += "Grid was already fully crossed; only truncated to the min count per cell if counts varied."
    print(balance_note, file=sys.stderr)

    if n_balanced < 2:
        print("ERROR: fewer than 2 occasions per cell in the balanced subgrid; "
              "residual (occasion) variance cannot be estimated. Refusing ANOVA.", file=sys.stderr)
        sys.exit(1)

    point = full_point_estimate(tasks_used, models_used, cells_full, n_balanced)
    anova = point["anova"]
    T = point["T"]

    d_study_task = {m: smallest_k_for_g_task(
        point["g_task_anova_per_model"][m]["sigma2_truncated_at_zero"]["item"],
        point["g_task_anova_per_model"][m]["sigma2_truncated_at_zero"]["residual"])
        for m in models_used}
    d_study_model = smallest_k_for_g_model(
        anova["sigma2_truncated_at_zero"]["model"],
        anova["sigma2_truncated_at_zero"]["task_x_model"],
        anova["sigma2_truncated_at_zero"]["residual"], T)

    # ---------------- Leaderboard flip probability ----------------
    flip = {}
    model_pairs = [(models_used[i], models_used[j])
                    for i in range(len(models_used)) for j in range(i + 1, len(models_used))]
    # "all k up to the number of runs actually collected", capped at n_balanced (the balanced subgrid
    # depth) to keep every cell's resampling pool well-defined and consistent with the rest of the report.
    ks_for_flip = sorted(set([1, 2, 3, 5, 8] + list(range(1, n_balanced + 1))))
    rng_flip = random.Random(args.seed)
    smallest_k_flip_below_05 = {}
    for (a, b) in model_pairs:
        pair_key = f"{a}_vs_{b}"
        true_rate_a = point["pass_rates"][a]
        true_rate_b = point["pass_rates"][b]
        # underdog = the model with the lower true (observed, full balanced-subgrid) overall pass rate
        underdog, favorite = (a, b) if true_rate_a <= true_rate_b else (b, a)
        exact = exact_single_run_flip(tasks_used, favorite, underdog, cells_full)
        mc = {}
        for k in ks_for_flip:
            mc[k] = empirical_flip_probability(tasks_used, favorite, underdog, cells_full, k, rng_flip, args.bootstrap)
        flip[pair_key] = {
            "true_pass_rate": {a: true_rate_a, b: true_rate_b},
            "underdog_model": underdog,
            "favorite_model": favorite,
            "exact_k1": exact,
            "exact_k1_flip_probability_underdog_wins": exact["p_b_higher"] if exact else None,
            "exact_k1_tie_probability": exact["p_tie"] if exact else None,
            "monte_carlo": mc,
            "monte_carlo_flip_probability_underdog_wins": {k: (v["p_b_higher"] if v else None) for k, v in mc.items()},
            "monte_carlo_tie_probability": {k: (v["p_tie"] if v else None) for k, v in mc.items()},
        }
        # smallest k with flip probability < 0.05 (search k=1 exact, then the monte-carlo table in order)
        found = None
        k1_flip = exact["p_b_higher"] if exact else None
        if k1_flip is not None and k1_flip < 0.05:
            found = 1
        else:
            for k in sorted(mc.keys()):
                pf = mc[k]["p_b_higher"] if mc[k] else None
                if pf is not None and pf < 0.05:
                    found = k
                    break
        if found is None:
            smallest_k_flip_below_05[pair_key] = f">{max(ks_for_flip)} (not reached within the k table computed)"
        else:
            smallest_k_flip_below_05[pair_key] = found

    # ---------------- Test-retest ----------------
    rng_split = random.Random(args.seed + 1)
    half1_oe, half2_oe = split_half_rates(tasks_used, models_used, cells_full, parity="odd_even")
    per_model_oe, pooled_oe = correlate_halves(half1_oe, half2_oe, models_used)
    half1_rand, half2_rand = split_half_rates(tasks_used, models_used, cells_full, parity="random", rng=rng_split)
    per_model_rand, pooled_rand = correlate_halves(half1_rand, half2_rand, models_used)

    # ---------------- Bootstrap (cluster over tasks) ----------------
    rng_boot = random.Random(args.seed + 2)
    B = args.bootstrap
    boot = {
        "pass_rate": {m: [] for m in models_used},
        "pass_rate_diff": {f"{a}_minus_{b}": [] for (a, b) in model_pairs},
        "sigma2_task": [], "sigma2_model": [], "sigma2_task_x_model": [], "sigma2_residual": [],
        "g_task_1": {m: [] for m in models_used},
        "g_task_8": {m: [] for m in models_used},
        "g_model_1": [], "g_model_8": [],
        "retest_pearson_pooled_oe": [], "retest_spearman_pooled_oe": [],
    }
    for _ in range(B):
        resample = [rng_boot.choice(tasks_used) for _ in range(len(tasks_used))]
        try:
            res = full_point_estimate(resample, models_used, cells_full, n_balanced)
        except Exception:
            continue
        a2 = res["anova"]
        s = a2["sigma2_truncated_at_zero"]
        for m in models_used:
            boot["pass_rate"][m].append(res["pass_rates"][m])
        for (a, b) in model_pairs:
            boot["pass_rate_diff"][f"{a}_minus_{b}"].append(res["pass_rates"][a] - res["pass_rates"][b])
        boot["sigma2_task"].append(s["task"])
        boot["sigma2_model"].append(s["model"])
        boot["sigma2_task_x_model"].append(s["task_x_model"])
        boot["sigma2_residual"].append(s["residual"])
        for m in models_used:
            gt = res["g_task_per_model"][m]
            boot["g_task_1"][m].append(gt.get(1))
            boot["g_task_8"][m].append(gt.get(8))
        boot["g_model_1"].append(res["g_model_table"].get(1))
        boot["g_model_8"].append(res["g_model_table"].get(8))
        # test-retest on this resample (odd/even split)
        h1, h2 = split_half_rates(resample, models_used, cells_full, parity="odd_even")
        _, pooled_b = correlate_halves(h1, h2, models_used)
        boot["retest_pearson_pooled_oe"].append(pooled_b["pearson_r"])
        boot["retest_spearman_pooled_oe"].append(pooled_b["spearman_rho"])

    ci = {"bootstrap_unit": "tasks (cluster bootstrap: whole tasks resampled with replacement; "
                             "all cells/runs for a resampled task are kept together)",
          "n_bootstrap_requested": B,
          "seed": args.seed}
    ci["pass_rate"] = {m: percentile_ci(boot["pass_rate"][m]) for m in models_used}
    ci["pass_rate_diff"] = {k: percentile_ci(v) for k, v in boot["pass_rate_diff"].items()}
    ci["sigma2_task"] = percentile_ci(boot["sigma2_task"])
    ci["sigma2_model"] = percentile_ci(boot["sigma2_model"])
    ci["sigma2_task_x_model"] = percentile_ci(boot["sigma2_task_x_model"])
    ci["sigma2_residual"] = percentile_ci(boot["sigma2_residual"])
    ci["g_task_1"] = {m: percentile_ci(boot["g_task_1"][m]) for m in models_used}
    ci["g_task_8"] = {m: percentile_ci(boot["g_task_8"][m]) for m in models_used}
    ci["g_model_1"] = percentile_ci(boot["g_model_1"])
    ci["g_model_8"] = percentile_ci(boot["g_model_8"])
    ci["retest_pearson_pooled_odd_even"] = percentile_ci(boot["retest_pearson_pooled_oe"])
    ci["retest_spearman_pooled_odd_even"] = percentile_ci(boot["retest_spearman_pooled_oe"])

    # ---------------- Assemble output ----------------
    out = {
        "meta": {
            "runs_file": args.runs,
            "seed": args.seed,
            "bootstrap_resamples": args.bootstrap,
            "design": "fully crossed task x model, occasions nested within cell as the residual "
                      "replication facet; tasks treated as random, model is the facet of measurement "
                      "interest (also treated as random for variance-component estimation).",
        },
        "descriptives": {
            "totals": totals,
            "per_model": per_model,
            "per_task": per_task,
            "per_task_model_cell": per_cell,
        },
        "balanced_subgrid": {
            "note": balance_note,
            "tasks_used": tasks_used,
            "models_used": models_used,
            "n_occasions_per_cell": n_balanced,
            "dropped_tasks": dropped_tasks,
            "dropped_models": dropped_models,
        },
        "anova": {
            "formula_used": (
                "Balanced two-way fully-random-effects ANOVA with n replicates per cell "
                "(Searle/Casella/McCulloch expected-mean-squares method of moments). "
                "sigma2_residual=MS_res; sigma2_task_x_model=(MS_TM-MS_res)/n; "
                "sigma2_task=(MS_task-MS_TM)/(M*n); sigma2_model=(MS_model-MS_TM)/(T*n)."
            ),
            "T_tasks": T, "M_models": anova["M"], "n_occasions": anova["n"],
            "mean_squares": anova["MS"],
            "sum_of_squares": anova["SS"],
            "degrees_of_freedom": anova["df"],
            "variance_components_raw": anova["sigma2_raw"],
            "variance_components_truncated_at_zero": anova["sigma2_truncated_at_zero"],
            "note_on_negative_estimates": (
                "Method-of-moments variance component estimates can be negative when the "
                "corresponding mean square is smaller than the one it's differenced against; "
                "this is a valid (if inconvenient) point estimate of a component near zero. "
                "Both raw and zero-truncated versions are reported; truncated versions are what "
                "feed the G-coefficient and D-study computations below."
            ),
        },
        "g_task_per_model": {
            "definition": "G_task(k) = sigma2_task / (sigma2_task + sigma2_residual/k), relative-error G "
                           "for a task's score averaged over k occasions, computed SEPARATELY within each "
                           "model via its own one-way random-effects ANOVA over tasks (task random, "
                           "occasion residual) -- so sigma2_task and sigma2_residual here are model-specific, "
                           "not the pooled two-way components above. This is an explicit choice: the task "
                           "wording says 'computed within each model', which we read as a fully separate "
                           "per-model one-way decomposition rather than reusing the pooled ANOVA components "
                           "for every model (which would give identical G_task(k) across models).",
            "per_model_anova": {
                m: {
                    "MS": point["g_task_anova_per_model"][m]["MS"],
                    "sigma2_raw": point["g_task_anova_per_model"][m]["sigma2_raw"],
                    "sigma2_truncated_at_zero": point["g_task_anova_per_model"][m]["sigma2_truncated_at_zero"],
                } for m in models_used
            },
            "g_table_k_1_to_20": point["g_task_per_model"],
        },
        "g_model": {
            "definition": "G_model(k, n_tasks) = sigma2_model / (sigma2_model + sigma2_task_x_model/n_tasks "
                           "+ sigma2_residual/(n_tasks*k)); reliability of a model-level score averaged over "
                           "n_tasks tasks and k occasions per task, using the pooled two-way variance "
                           "components (truncated at zero).",
            "g_table_k_1_to_20_at_actual_n_tasks": point["g_model_table"],
            "n_tasks_used": T,
        },
        "d_study": {
            "target_g": 0.8,
            "g_task_per_model_smallest_k": d_study_task,
            "g_model_smallest_k_at_actual_n_tasks": d_study_model,
            "leaderboard_flip_smallest_k": {
                "definition": "Smallest k (occasions per task per model) at which the probability that "
                               "the model with the lower true (observed) overall pass rate ('underdog') "
                               "comes out ahead of the model with the higher true pass rate ('favorite') "
                               "in a resampled comparison drops below 0.05. k=1 uses the exact closed-form "
                               "value; k>1 uses the Monte Carlo table below.",
                "per_pair": smallest_k_flip_below_05,
            },
        },
        "leaderboard_flip_probability": {
            "definition": "For each pair of models, and for k in {1,2,3,5,8} plus all k from 1 up to "
                           "min(n_balanced,20): resample k occasions with replacement independently per "
                           "(task, model) cell, average within model (unweighted mean) over all tasks in "
                           "the balanced subgrid, and record which model's resampled average is higher. "
                           "'exact_k1' is computed in closed form (DP convolution of independent per-task "
                           "Bernoulli draws at the observed cell pass rate) rather than by Monte Carlo, "
                           "since k=1 resampling from a cell is exactly Bernoulli(observed cell pass rate). "
                           "'monte_carlo' entries use --bootstrap resamples, seeded.",
            "pairs": flip,
        },
        "test_retest": {
            "odd_even_split": {"per_model": per_model_oe, "pooled": pooled_oe},
            "random_split_seeded": {"per_model": per_model_rand, "pooled": pooled_rand, "seed": args.seed + 1},
            "note": "Per-task pass rate computed within each half (cells with <2 occasions are excluded from "
                    "that split). Spearman-Brown stepped-up estimate projects the half-length correlation "
                    "to the full (both-halves-combined) test length.",
        },
        "bootstrap_confidence_intervals": ci,
    }

    with open(args.out, "w") as f:
        json.dump(out, f, indent=2, sort_keys=False)

    # ---------------- stdout text summary ----------------
    print("=" * 78)
    print("AGENT RUN RELIABILITY ANALYSIS")
    print("=" * 78)
    print(balance_note)
    print()
    print("-- Descriptives --")
    print(f"Total runs: {totals['n_runs']}  timeouts: {totals['n_timeouts']}  errors: {totals['n_errors']}")
    for m in models_all:
        pm = per_model[m]
        print(f"  model={m:12s} n={pm['n_runs']:5d}  pass_rate={fmt(pm['pass_rate'])}  "
              f"timeouts={pm['n_timeouts']}  errors={pm['n_errors']}")
    print()
    print("-- ANOVA variance components (truncated at zero) --")
    svt = anova["sigma2_truncated_at_zero"]
    svr = anova["sigma2_raw"]
    for key in ["task", "model", "task_x_model", "residual"]:
        print(f"  sigma2_{key:14s} raw={fmt(svr[key])}   truncated={fmt(svt[key])}")
    print()
    print("-- G_model(k) at actual n_tasks=%d --" % T)
    for k in [1, 2, 3, 5, 8, 10, 20]:
        print(f"  k={k:2d}  G_model={fmt(point['g_model_table'].get(k))}")
    print()
    print("-- D-study (target G>=0.8) --")
    for m in models_used:
        print(f"  G_task smallest k, model={m}: {d_study_task[m]}")
    print(f"  G_model smallest k (n_tasks={T}): {d_study_model}")
    print()
    print("-- Leaderboard flip probability (exact k=1, underdog beats favorite) --")
    for pair_key, v in flip.items():
        print(f"  {pair_key}: underdog={v['underdog_model']}  "
              f"P(flip)={fmt(v['exact_k1_flip_probability_underdog_wins'])}  "
              f"tie={fmt(v['exact_k1_tie_probability'])}  "
              f"smallest_k(P<0.05)={smallest_k_flip_below_05.get(pair_key)}")
    print()
    print("-- Test-retest (odd/even split, pooled) --")
    print(f"  Pearson r={fmt(pooled_oe['pearson_r'])}  Spearman rho={fmt(pooled_oe['spearman_rho'])}  "
          f"Spearman-Brown (Pearson)={fmt(pooled_oe['spearman_brown_full_length_pearson'])}")
    print()
    print(f"Full results written to: {args.out}")


if __name__ == "__main__":
    main()
