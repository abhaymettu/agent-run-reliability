# Run record schema

`results/runs.jsonl`, one JSON object per completed run, appended and flushed
after every run.

    task_id       str    e.g. "arith_group_median"
    model         str    "sonnet" | "haiku"  (the --model alias passed to claude)
    run_index     int    0-based occasion index within (task, model)
    passed        bool   check.py exited 0
    duration_s    float  wall clock of the claude subprocess
    exit_code     int    claude subprocess exit status (-1 if killed on timeout)
    timed_out     bool
    check_exit    int    check.py exit status
    check_msg     str    check.py stdout, first line, truncated to 300 chars
    max_turns_cap int    the --max-turns budget the subject was given
    num_turns     int    from claude --output-format json, -1 if unavailable
    cost_usd      float  from claude --output-format json, 0.0 if unavailable
    session_id    str    from claude --output-format json, "" if unavailable
    started_at    str    ISO 8601 local time
    error         str    "" when the run completed normally
