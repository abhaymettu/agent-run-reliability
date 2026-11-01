#!/usr/bin/env python3
"""Run the agent-run-reliability experiment grid.

Grid = tasks x models x run_index in [0, N). Launches `claude -p` per cell,
records one JSON line per completed run to a resumable JSONL file.

See docs/TASK_CONTRACT.md and docs/RUN_SCHEMA.md.
"""
import argparse
import concurrent.futures
import datetime
import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
CLAUDE_BIN = shutil.which("claude") or "claude"
EMPTY_MCP_CONFIG = os.path.join(SCRIPT_DIR, "empty-mcp.json")
ALLOWED_TOOLS = "Bash Read Write Edit Glob Grep"

write_lock = threading.Lock()
stop_flag = threading.Event()

SCHEMA_FIELDS = [
    "task_id", "model", "run_index", "passed", "duration_s", "exit_code",
    "timed_out", "check_exit", "check_msg", "num_turns", "cost_usd",
    "session_id", "started_at", "error",
]


def load_existing(out_path):
    done = set()
    if not os.path.isfile(out_path):
        return done
    with open(out_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            done.add((rec.get("task_id"), rec.get("model"), rec.get("run_index")))
    return done


def append_record(out_path, record):
    line = json.dumps(record, sort_keys=True) + "\n"
    with write_lock:
        with open(out_path, "a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())


def discover_tasks(tasks_dir, tasks_arg):
    if tasks_arg:
        return [t.strip() for t in tasks_arg.split(",") if t.strip()]
    return sorted(
        d for d in os.listdir(tasks_dir)
        if os.path.isdir(os.path.join(tasks_dir, d)) and not d.startswith(".")
    )


def build_queue(tasks, models, runs, done):
    queue = []
    for run_index in range(runs):
        for task_id in tasks:
            for model in models:
                key = (task_id, model, run_index)
                if key in done:
                    continue
                queue.append(key)
    return queue


def run_one(task_id, model, run_index, tasks_dir, workroot, timeout, keep_workdirs, max_turns):
    started_at = datetime.datetime.now().isoformat()
    task_dir = os.path.join(tasks_dir, task_id)
    workdir = os.path.join(workroot, task_id, model, str(run_index))

    record = {
        "task_id": task_id,
        "model": model,
        "run_index": run_index,
        "passed": False,
        "duration_s": 0.0,
        "exit_code": -1,
        "timed_out": False,
        "check_exit": -1,
        "check_msg": "",
        "max_turns_cap": max_turns,
        "num_turns": -1,
        "cost_usd": 0.0,
        "session_id": "",
        "started_at": started_at,
        "error": "",
    }

    try:
        if os.path.exists(workdir):
            shutil.rmtree(workdir)
        os.makedirs(workdir, exist_ok=True)
    except Exception as e:  # noqa: BLE001
        record["error"] = f"failed to prepare workdir: {e}"
        return record

    setup_py = os.path.join(task_dir, "setup.py")
    prompt_path = os.path.join(task_dir, "prompt.txt")
    check_py = os.path.join(task_dir, "check.py")

    r = subprocess.run(
        [sys.executable, setup_py, workdir],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    if r.returncode != 0:
        record["error"] = f"setup.py failed: {r.stdout.decode(errors='replace')[:300]}"
        return record

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_text = f.read()
    except Exception as e:  # noqa: BLE001
        record["error"] = f"failed to read prompt.txt: {e}"
        return record

    cmd = [
        CLAUDE_BIN, "-p", "--model", model, "--strict-mcp-config",
        "--mcp-config", EMPTY_MCP_CONFIG,
        "--allowedTools", ALLOWED_TOOLS,
        "--max-turns", str(max_turns),
        "--output-format", "json",
        prompt_text,
    ]

    t0 = time.monotonic()
    stdout_data = b""
    exit_code = -1
    timed_out = False
    try:
        proc = subprocess.Popen(
            cmd, cwd=workdir,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            stdout_data, _ = proc.communicate(timeout=timeout)
            exit_code = proc.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
            try:
                stdout_data, _ = proc.communicate(timeout=10)
            except Exception:  # noqa: BLE001
                stdout_data = b""
            exit_code = -1
    except Exception as e:  # noqa: BLE001
        record["error"] = f"failed to launch claude: {e}"
        record["duration_s"] = time.monotonic() - t0
        return record

    duration_s = time.monotonic() - t0
    record["duration_s"] = duration_s
    record["exit_code"] = exit_code
    record["timed_out"] = timed_out

    # Parse claude's JSON stdout for num_turns / total_cost_usd / session_id.
    parsed = None
    try:
        text = stdout_data.decode("utf-8", errors="replace").strip()
        parsed = json.loads(text)
    except Exception:  # noqa: BLE001
        parsed = None

    if isinstance(parsed, dict):
        if "num_turns" in parsed:
            record["num_turns"] = parsed.get("num_turns", -1)
        if "total_cost_usd" in parsed:
            record["cost_usd"] = parsed.get("total_cost_usd", 0.0)
        if "session_id" in parsed:
            record["session_id"] = parsed.get("session_id", "") or ""
    else:
        note = "claude stdout was not parseable JSON"
        record["error"] = note if not record["error"] else record["error"] + "; " + note

    # Run check.py regardless of claude's outcome -- never skip a cell.
    try:
        cr = subprocess.run(
            [sys.executable, check_py, workdir],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            timeout=60,
        )
        record["check_exit"] = cr.returncode
        first_line = cr.stdout.decode("utf-8", errors="replace").splitlines()
        record["check_msg"] = (first_line[0] if first_line else "")[:300]
        record["passed"] = cr.returncode == 0
    except subprocess.TimeoutExpired:
        record["check_exit"] = -1
        record["check_msg"] = "check.py timed out after 60s"
        record["passed"] = False
    except Exception as e:  # noqa: BLE001
        record["check_exit"] = -1
        record["check_msg"] = f"check.py crashed: {e}"[:300]
        record["passed"] = False

    keep = keep_workdirs == "all" or (keep_workdirs == "failed" and not record["passed"])
    if not keep:
        shutil.rmtree(workdir, ignore_errors=True)

    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", default=None, help="comma-separated task ids")
    parser.add_argument("--tasks-dir", default="tasks")
    parser.add_argument("--models", required=True, help="comma-separated model aliases")
    parser.add_argument("--runs", type=int, required=True)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--max-turns", type=int, default=40)
    parser.add_argument("--out", default="results/runs.jsonl")
    parser.add_argument("--workroot", default="results/runs")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--keep-workdirs", choices=["all", "failed", "none"], default="failed")
    args = parser.parse_args()

    concurrency = min(args.concurrency, 4)
    if args.concurrency > 4:
        print(f"note: concurrency capped at 4 (requested {args.concurrency})", file=sys.stderr)

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    tasks = discover_tasks(args.tasks_dir, args.tasks)
    if not tasks:
        print("no tasks found", file=sys.stderr)
        sys.exit(2)

    out_path = args.out
    out_dir = os.path.dirname(out_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    os.makedirs(args.workroot, exist_ok=True)

    done = load_existing(out_path)
    queue = build_queue(tasks, models, args.runs, done)
    total_grid = len(tasks) * len(models) * args.runs
    skipped = total_grid - len(queue)

    if args.limit is not None:
        queue = queue[: args.limit]

    print(
        f"grid: {len(tasks)} tasks x {len(models)} models x {args.runs} runs = {total_grid} cells; "
        f"{skipped} already done; {len(queue)} queued",
        file=sys.stderr,
    )

    if args.dry_run:
        for task_id, model, run_index in queue:
            print(f"DRY RUN {task_id} {model} run={run_index}")
        return

    def handle_sigint(signum, frame):
        if not stop_flag.is_set():
            print("\nSIGINT received: not launching new runs, waiting for in-flight runs...", file=sys.stderr)
            stop_flag.set()
    signal.signal(signal.SIGINT, handle_sigint)

    total_to_run = len(queue)
    completed = 0
    completed_lock = threading.Lock()
    start_time = time.monotonic()

    def submit_and_run(key):
        task_id, model, run_index = key
        record = run_one(
            task_id, model, run_index, args.tasks_dir, args.workroot,
            args.timeout, args.keep_workdirs, args.max_turns,
        )
        append_record(out_path, record)
        nonlocal completed
        with completed_lock:
            completed += 1
            n = completed
        elapsed = time.monotonic() - start_time
        rate = n / elapsed if elapsed > 0 else 0
        remaining = total_to_run - n
        eta_s = remaining / rate if rate > 0 else float("inf")
        status = "PASS" if record["passed"] else "FAIL"
        print(
            f"[{elapsed:7.1f}s] {n}/{total_to_run} {task_id} {model} run={run_index} "
            f"{status} dur={record['duration_s']:.1f}s "
            f"eta={'?' if eta_s == float('inf') else f'{eta_s:.0f}s'}",
            file=sys.stderr,
        )
        return record

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = []
        for idx, key in enumerate(queue):
            if stop_flag.is_set():
                print("stopped launching new runs (SIGINT)", file=sys.stderr)
                break
            futures.append(executor.submit(submit_and_run, key))
            # Stagger only the initial fill so the machine does not take
            # `concurrency` cold starts at once; after that the pool paces itself.
            if idx < concurrency:
                time.sleep(2)
        concurrent.futures.wait(futures)

    print(f"done: {completed}/{total_to_run} runs completed this invocation", file=sys.stderr)


if __name__ == "__main__":
    main()
