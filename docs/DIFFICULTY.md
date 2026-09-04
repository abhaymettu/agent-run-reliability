# Difficulty target

A reliability study needs tasks whose pass rate sits away from both floor and
ceiling. Near 1.0 there is no variance to decompose and every estimate is zero;
near 0.0 the same. The target band is a pass rate of roughly 0.3 to 0.8 per
task per model.

Battery v1 missed badly: sonnet 0.990, haiku 0.953, with twenty of twenty-four
tasks passed by both models on all eight occasions. Its tasks were precisely
specified and mechanically simple, so a competent agent solved them on the
first try every time.

The one task in v1 that discriminated was `arith_running_balance`, and the
reason is worth copying. It asks for a running balance under an overdraft rule
that must be tested *before* each transaction is applied. The state trajectory
depends on the guard, so an agent that writes the obvious loop and applies the
guard after the fact produces a plausible, wrong answer. The task is hard
without being ambiguous.

## Levers that raise difficulty legitimately

- **Sequential state whose trajectory depends on a condition.** Rejecting an
  item changes what the next item sees. Order of test and update matters.
- **Interacting rules with an explicit precedence order**, where the naive
  order of application gives a different answer than the specified one.
- **Planted edge cases in the generated data**: exact boundary equality, ties
  that must be broken by a stated rule, empty groups, a group of size one,
  negative and zero values, a duplicate key, an entry that matches two rules.
  Put them in deliberately, and make sure the reference solution and the naive
  approach disagree on them.
- **Two stages where the second depends on the first**, so a stage-one error
  propagates rather than cancelling.
- **Exact output format**: field order, number formatting, rounding mode,
  trailing newline. Specify it precisely and check it exactly.

## What does not count

- Ambiguity. If two careful readers could produce different correct answers,
  the task is broken, not hard. Every rule must be stated, including tie-breaks
  and boundary behaviour.
- Volume for its own sake. A task that is only long is a timeout risk, not a
  difficulty control. Every task must be solvable well inside 40 agent turns
  and a 300 second wall clock; the reference solution must run in under 20
  seconds.
- Trickery in the prompt. No misdirection, no buried contradictions, no
  information withheld that the task requires.

The test of a good hard task: the reference solution is short and obviously
correct once you see it, and a plausible first attempt gets it wrong.
