#!/usr/bin/env python3
"""Validate tasks in tasks/<task_id>/ against docs/TASK_CONTRACT.md.

Usage: python3 tools/validate_tasks.py [--tasks-dir tasks] [task_id ...]
"""
import argparse
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time

REQUIRED_FILES = ["setup.py", "prompt.txt", "check.py", "solution.py"]

# A filesystem absolute path leaking into a prompt. Restricted to the real
# roots on this machine so that URL paths inside generated sample data
# ("GET /api/inventory") do not trip it.
ABS_PATH_RE = re.compile(
    r"(?:^|\s)/(?:Users|private|tmp|var|home|opt|usr|etc|Volumes)/[^\s]+"
)


def run(cmd, cwd=None, timeout=60):
    return subprocess.run(
        cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        timeout=timeout,
    )


def snapshot_tree(root):
    """Return {relpath: (contents_bytes, mode)} for every file under root."""
    snap = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for fname in sorted(filenames):
            full = os.path.join(dirpath, fname)
            rel = os.path.relpath(full, root)
            with open(full, "rb") as f:
                data = f.read()
            mode = stat.S_IMODE(os.stat(full).st_mode)
            snap[rel] = (data, mode)
    return snap


# The host machine writes a hidden .remember/ directory into the working
# directory of every subject session. A task whose checker enumerates the tree
# must ignore dot-prefixed paths or it will fail correct work. plant_dotdir
# reproduces that directory so the assertion below tests the real condition.
def plant_dotdir(root):
    d = os.path.join(root, ".remember", "logs")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(root, ".remember", ".gitignore"), "w") as f:
        f.write("*\n")
    with open(os.path.join(d, "hook-errors.log"), "w") as f:
        f.write("hook wrote this\n" * 3)


class TaskFailure(Exception):
    pass


def check_task(task_dir, task_id):
    for fname in REQUIRED_FILES:
        if not os.path.isfile(os.path.join(task_dir, fname)):
            raise TaskFailure(f"missing {fname}")

    prompt_path = os.path.join(task_dir, "prompt.txt")
    prompt_text = open(prompt_path, "r", encoding="utf-8").read()
    if not prompt_text.strip():
        raise TaskFailure("prompt.txt is empty")
    m = ABS_PATH_RE.search(prompt_text)
    if m:
        raise TaskFailure(f"prompt.txt contains an absolute path: {m.group(0).strip()!r}")

    setup_py = os.path.join(task_dir, "setup.py")
    check_py = os.path.join(task_dir, "check.py")
    solution_py = os.path.join(task_dir, "solution.py")

    tmp_base = tempfile.mkdtemp(prefix=f"validate_{task_id}_")
    try:
        work1 = os.path.join(tmp_base, "setup1")
        work2 = os.path.join(tmp_base, "setup2")
        os.makedirs(work1)
        os.makedirs(work2)

        r = run([sys.executable, setup_py, work1])
        if r.returncode != 0:
            raise TaskFailure(f"setup.py failed (run 1): {r.stdout.decode(errors='replace')[:300]}")
        r = run([sys.executable, setup_py, work2])
        if r.returncode != 0:
            raise TaskFailure(f"setup.py failed (run 2): {r.stdout.decode(errors='replace')[:300]}")

        snap1 = snapshot_tree(work1)
        snap2 = snapshot_tree(work2)
        if snap1.keys() != snap2.keys():
            only1 = snap1.keys() - snap2.keys()
            only2 = snap2.keys() - snap1.keys()
            raise TaskFailure(f"setup.py not deterministic: path sets differ (only in run1={sorted(only1)}, only in run2={sorted(only2)})")
        for rel in snap1:
            data1, mode1 = snap1[rel]
            data2, mode2 = snap2[rel]
            if data1 != data2:
                raise TaskFailure(f"setup.py not deterministic: contents differ for {rel}")
            if mode1 != mode2:
                raise TaskFailure(f"setup.py not deterministic: file mode differs for {rel} ({oct(mode1)} vs {oct(mode2)})")

        # check.py on setup-only workdir must fail (non-zero)
        setup_only = os.path.join(tmp_base, "setup_only")
        os.makedirs(setup_only)
        r = run([sys.executable, setup_py, setup_only])
        if r.returncode != 0:
            raise TaskFailure(f"setup.py failed (setup_only): {r.stdout.decode(errors='replace')[:300]}")
        r = run([sys.executable, check_py, setup_only])
        if r.returncode == 0:
            raise TaskFailure("check.py passed on a setup-only workdir (checker is degenerate)")

        # setup + solution -> check must pass
        solved = os.path.join(tmp_base, "solved")
        os.makedirs(solved)
        r = run([sys.executable, setup_py, solved])
        if r.returncode != 0:
            raise TaskFailure(f"setup.py failed (solved): {r.stdout.decode(errors='replace')[:300]}")

        t0 = time.monotonic()
        r = run([sys.executable, solution_py, solved])
        sol_time = time.monotonic() - t0
        if r.returncode != 0:
            raise TaskFailure(f"solution.py failed: {r.stdout.decode(errors='replace')[:300]}")

        r = run([sys.executable, check_py, solved])
        if r.returncode != 0:
            raise TaskFailure(f"check.py failed after solution.py: {r.stdout.decode(errors='replace')[:300]}")

        # The solved direction again, with the host's hidden .remember/
        # directory present, which is the state every real run sees.
        contam = os.path.join(tmp_base, "contaminated")
        os.makedirs(contam)
        r = run([sys.executable, setup_py, contam])
        if r.returncode != 0:
            raise TaskFailure(f"setup.py failed (contaminated): {r.stdout.decode(errors='replace')[:300]}")
        plant_dotdir(contam)
        r = run([sys.executable, solution_py, contam])
        if r.returncode != 0:
            raise TaskFailure(f"solution.py failed with .remember/ present: {r.stdout.decode(errors='replace')[:300]}")
        r = run([sys.executable, check_py, contam])
        if r.returncode != 0:
            raise TaskFailure(f"check.py rejected a solved workdir because of .remember/: {r.stdout.decode(errors='replace')[:300]}")

        warning = None
        if sol_time > 20:
            warning = f"WARNING solution.py took {sol_time:.1f}s (>20s)"

        return warning
    finally:
        shutil.rmtree(tmp_base, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks-dir", default="tasks")
    parser.add_argument("task_ids", nargs="*")
    args = parser.parse_args()

    tasks_dir = args.tasks_dir
    if args.task_ids:
        task_ids = args.task_ids
    else:
        if not os.path.isdir(tasks_dir):
            print(f"no such tasks dir: {tasks_dir}", file=sys.stderr)
            sys.exit(2)
        task_ids = sorted(
            d for d in os.listdir(tasks_dir)
            if os.path.isdir(os.path.join(tasks_dir, d)) and not d.startswith(".")
        )

    if not task_ids:
        print("no tasks found")
        sys.exit(0)

    results = []
    any_failed = False
    for task_id in task_ids:
        task_dir = os.path.join(tasks_dir, task_id)
        if not os.path.isdir(task_dir):
            results.append((task_id, "FAIL", "task directory not found"))
            any_failed = True
            continue
        try:
            warning = check_task(task_dir, task_id)
            if warning:
                results.append((task_id, "PASS", warning))
            else:
                results.append((task_id, "PASS", ""))
        except TaskFailure as e:
            results.append((task_id, "FAIL", str(e)))
            any_failed = True
        except subprocess.TimeoutExpired:
            results.append((task_id, "FAIL", "subprocess timed out"))
            any_failed = True
        except Exception as e:  # noqa: BLE001
            results.append((task_id, "FAIL", f"unexpected error: {e}"))
            any_failed = True

    width = max((len(t) for t, _, _ in results), default=8)
    for task_id, status, note in results:
        line = f"{task_id.ljust(width)}  {status}"
        if note:
            line += f"  {note}"
        print(line)

    sys.exit(1 if any_failed else 0)


if __name__ == "__main__":
    main()
