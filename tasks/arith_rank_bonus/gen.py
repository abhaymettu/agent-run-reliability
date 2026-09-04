"""Shared generator for arith_rank_bonus. Stays in tasks_v2/, never copied to workdir."""
import random

SEED = 20260617

BONUS_TOP = 500      # ranks 1-3
BONUS_MID = 200      # ranks 4-10
BONUS_NONE = 0        # rank 11+


def generate(seed=SEED):
    """Return a list of dicts {employee_id, score (int, may be negative)}.

    Deliberately plants:
      - a 3-way tie for the top score (all rank 1; standard competition
        ranking then skips straight to rank 4 for the next distinct score)
      - a 2-way tie straddling the rank-3/rank-4 boundary: two employees
        tied at what would be rank 3 in dense ranking, but under standard
        competition ranking they are BOTH rank 3 (both still get the top
        bonus) and the employee after them is rank 5, not rank 4
      - a 2-way tie straddling the rank-10/rank-11 boundary the same way
      - a negative score
      - a lone employee with a unique minimum score (rank == count)
    """
    rng = random.Random(seed)
    n = 22
    scores = {}

    # organic distinct scores, spaced out, descending-ish range
    pool = list(range(200, 200 - n * 7, -7))
    rng.shuffle(pool)

    ids = [f"E{idx:03d}" for idx in range(1, n + 1)]
    for i, eid in enumerate(ids):
        scores[eid] = pool[i]

    # sort ids by their currently-assigned score descending to know positions
    order = sorted(ids, key=lambda e: -scores[e])

    # 3-way tie for the very top score
    top_score = scores[order[0]]
    scores[order[1]] = top_score
    scores[order[2]] = top_score

    # recompute order after the top tie
    order = sorted(ids, key=lambda e: -scores[e])

    # Place a 2-way tie so that, under standard competition ranking, it
    # lands exactly straddling rank 3/4: after the 3-way tie at rank 1
    # (occupying ranks 1,1,1), the 4th and 5th distinct-score slots are
    # candidates for ranks 4 and 5. Force employees at sorted positions
    # 3 and 4 (0-indexed, i.e. the 4th and 5th highest) to tie, so both
    # get rank 4, and the employee after them gets rank 6.
    e_a, e_b = order[3], order[4]
    scores[e_b] = scores[e_a]
    order = sorted(ids, key=lambda e: -scores[e])

    # Place a 2-way tie straddling the rank-10/11 boundary: make the
    # employees at sorted positions 9 and 10 (0-indexed) tie, so both
    # land on the same rank and the bonus tier boundary (rank 11+) is
    # tested against a tie rather than a clean cut.
    e_c, e_d = order[9], order[10]
    scores[e_d] = scores[e_c]
    order = sorted(ids, key=lambda e: -scores[e])

    # give the lowest-scoring employee a negative score
    lowest = order[-1]
    scores[lowest] = -13

    return [{"employee_id": eid, "score": scores[eid]} for eid in ids]


def compute_ranks_and_bonuses(rows):
    """Standard competition ranking (1,2,2,4,...) by score descending.
    Returns {employee_id: (rank, bonus)}."""
    ordered = sorted(rows, key=lambda r: -r["score"])
    result = {}
    rank = 0
    prev_score = None
    for i, r in enumerate(ordered):
        if r["score"] != prev_score:
            rank = i + 1
            prev_score = r["score"]
        if rank <= 3:
            bonus = BONUS_TOP
        elif rank <= 10:
            bonus = BONUS_MID
        else:
            bonus = BONUS_NONE
        result[r["employee_id"]] = (rank, bonus)
    return result
