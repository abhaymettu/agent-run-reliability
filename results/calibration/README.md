# Turn-budget calibration

After battery v2 came in at 0.972 pooled under the default 40-turn budget
(`results/pilot_v2/`), difficulty was set with the budget instead. Each sweep
below is one occasion per cell, 24 tasks x 2 models = 48 runs, on the v2 tasks
with trap-telegraphing removed from the prompts.

    budget   sonnet        haiku         pooled        mean run
    40       71/72 0.986   69/72 0.958   140/144 0.972  25.8 s   (pilot_v2, 3 occasions)
     6       23/24 0.958   19/24 0.792    42/48  0.875  26.9 s
     4       22/24 0.917   18/24 0.750    40/48  0.833  18.2 s
     3       18/24 0.750   16/24 0.667    34/48  0.708  14.5 s

The knob is weaker than the turn distribution suggested: cutting the budget
from 40 to 4 moved the pooled pass rate only from 0.97 to 0.83. Most runs do
their real work in the first two or three turns and spend the rest verifying,
so removing the later turns removes verification rather than the work.

A budget of 3 was chosen for the full grid: it is the tightest setting at which
both models sit inside the 0.3-0.8 target band, and the two models are close
together (0.750 against 0.667), which is the case where the ranking question
actually bites.

At budget 3, nine of the fourteen observed failures were the run being cut off
before it wrote its output, and five were wrong answers written in time. The
same split is computed on the full grid and reported there; it is the reason
the report describes the measured construct as task completion under a tight
budget rather than unconstrained capability.
