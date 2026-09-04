# Status

Last updated: 2026-09-04 00:28 EDT

## Where things stand

Phase: build. Nothing has been run on the grid yet.

Done:
- Repo created and pushed: github.com/abhaymettu/agent-run-reliability (private).
- Environment probed. The `claude` binary is at `/Users/abhay/.local/bin/claude`
  (`claude` on the shell is a zsh function, not the binary). Model aliases
  `haiku`, `sonnet` and `opus` all resolve: `haiku` -> claude-haiku-4-5,
  `sonnet` -> claude-sonnet-5, `opus` -> claude-opus-5. Subjects are therefore
  sonnet and haiku, as originally planned, at the full run count.
- The subject invocation shape is verified end to end on a toy task: cwd set to
  a clean workdir, `-p --model X --strict-mcp-config --mcp-config <file>
  --allowedTools "Bash Read Write Edit Glob Grep" --max-turns 40 --output-format
  json`. No permission denials, trivial task solved in 7.7 s at $0.033 on haiku.
- Contract specs written: `docs/TASK_CONTRACT.md`, `docs/RUN_SCHEMA.md`.

In flight (six parallel build agents):
- 24 tasks in four categories, 6 each: xform, codefix, chore, arith.
- `harness/run_grid.py` and `tools/validate_tasks.py`.
- `analysis/analyze.py` and `analysis/selftest.py`.

## Target design

24 tasks x 8 runs x 2 models (sonnet, haiku) = 384 runs, 4 concurrent, 300 s
timeout per run. Queue ordered by run_index so an interrupt leaves a balanced
design. Fallback if throughput after the first hour will not finish by 06:00:
shrink to 16 tasks x 6 runs before dropping a model or going unbalanced.

## Known caveats to carry into the report

Subject sessions inherit the operator's global CLAUDE.md and SessionStart hook
output; an isolated `CLAUDE_CONFIG_DIR` loses authentication and `--settings`
does not suppress hooks, so this contamination could not be removed. It is
constant in form across every cell.

## Next

Wait on the build agents, validate all 24 tasks, pilot one run per cell, then
launch the grid.
