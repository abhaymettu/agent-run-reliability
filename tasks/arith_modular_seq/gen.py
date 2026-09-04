"""Shared generator for arith_modular_seq. Stays in tasks/, never copied to workdir."""
import random

SEED = 20260904
N = 220


def generate(seed=SEED):
    """Return a list of positive integers (1..999), with some deliberate
    repeats and values crafted to be divisible by 3 and 5 both (i.e. by 15),
    which the condition below must correctly exclude."""
    rng = random.Random(seed)
    values = [rng.randint(1, 999) for _ in range(N)]
    # force a handful of exact repeats
    values[50] = values[10]
    values[51] = values[10]
    # force values divisible by 15 (both 3 and 5) to test the exclusion
    values[100] = 45
    values[101] = 150
    values[102] = 15
    # force values divisible by exactly one of 3/5
    values[110] = 9
    values[111] = 25
    return values


def count_and_sum(values):
    """Count and sum every n that is divisible by 3 or by 5, but NOT by
    both (i.e. an exclusive-or of the two divisibility conditions)."""
    count = 0
    total = 0
    for n in values:
        div3 = (n % 3 == 0)
        div5 = (n % 5 == 0)
        if div3 != div5:  # exactly one of the two
            count += 1
            total += n
    return count, total
