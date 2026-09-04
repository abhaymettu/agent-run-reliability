# Task contract

Every task lives in `tasks/<task_id>/` and has exactly three or four files.

    tasks/<task_id>/
      gen.py       # optional but preferred: generate(seed) -> data structures
      setup.py     # python3 setup.py <workdir>   creates the input files
      prompt.txt   # the literal instruction handed to the subject agent
      check.py     # python3 check.py <workdir>   exit 0 = pass, non-zero = fail

Rules, all mandatory:

1. Python 3, standard library only. No third-party imports anywhere.
2. `setup.py <workdir>` writes input files into `<workdir>` (which already
   exists). It is deterministic: a hardcoded seed, identical bytes on every
   invocation, on every machine. It writes nothing outside `<workdir>`.
3. Ground truth is never hand-typed and never appears in `prompt.txt` or in any
   file placed in `<workdir>`. `check.py` recomputes the expected answer from
   the same seeded generator (`gen.py`, which stays in `tasks/`, outside the
   subject's working directory).
4. `prompt.txt` refers to files by bare relative name. It never mentions paths
   outside the working directory, never names the checker, never states the
   answer. It states the required output file and its exact format precisely
   enough that a correct solution is unique.
5. `check.py` prints one short line to stdout explaining the verdict and exits
   0 for pass, 1 for fail. It never crashes: missing file, malformed content,
   wrong type, empty directory all exit 1 with a message. No model judgment,
   no fuzzy matching beyond stripping surrounding whitespace.
6. `check.py` must exit non-zero on a workdir that has only been through
   `setup.py` (no agent work). This is enforced by `tools/validate_tasks.py`.
7. The task must be solvable by a capable agent in under three minutes using
   only Bash, Read, Write, Edit, Glob and Grep, with no network access.
8. Task ids are lowercase, `<category>_<slug>`, where category is one of
   `xform` (file/data transforms), `codefix` (bug fix verified by tests),
   `chore` (multi-step shell chore with a checkable end state), `arith`
   (arithmetic over generated data).

Difficulty: the battery needs a spread. A battery every subject passes every
time carries no information about run-to-run reliability. Make some tasks
fiddly (ties, empty groups, negative numbers, exact rounding rules, off-by-one
boundaries, multi-step ordering) while keeping every specification unambiguous.
Fiddly is wanted; ambiguous is not.

## Reference solution

Each task also ships `tasks/<task_id>/solution.py`, run as
`python3 solution.py <workdir>`. It solves the task correctly, the way a
competent agent would, and exists only so `tools/validate_tasks.py` can assert
two things about every task:

    setup            -> check exits non-zero   (checker is not degenerate)
    setup + solution -> check exits zero       (task is passable, spec is met)

`solution.py` stays in `tasks/`. It is never copied into the working directory
and the subject agent never sees it.
