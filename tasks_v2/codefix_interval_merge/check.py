#!/usr/bin/env python3
"""check.py <workdir> -- runs a hidden battery of merge_intervals() cases,
recomputed from gen.py, against the agent's intervals.py. Exits 0 only if
every case matches. Never crashes: any failure mode prints one FAIL line
and exits 1."""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import hidden_cases, reference_merge  # noqa: E402

RUNNER = '''
import json
import sys

sys.path.insert(0, sys.argv[1])
try:
    from intervals import merge_intervals
except Exception as exc:
    print(json.dumps({"import_error": repr(exc)}))
    sys.exit(0)

cases = json.loads(sys.argv[2])
out = []
for c in cases:
    try:
        val = merge_intervals([list(iv) for iv in c["input"]])
        out.append({"ok": True, "value": val})
    except Exception as exc:
        out.append({"ok": False, "error": type(exc).__name__})
print(json.dumps({"results": out}))
'''


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


def normalize(intervals):
    return sorted([list(iv) for iv in intervals])


def main():
    if len(sys.argv) != 2:
        fail("usage check.py <workdir>")
    workdir = os.path.abspath(sys.argv[1])

    if not os.path.isfile(os.path.join(workdir, "intervals.py")):
        fail("intervals.py not found")

    cases = hidden_cases()
    expected = [{"ok": True, "value": reference_merge(c["input"])} for c in cases]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(RUNNER)
        runner_path = f.name

    try:
        try:
            proc = subprocess.run(
                [sys.executable, runner_path, workdir, json.dumps(cases)],
                capture_output=True, text=True, timeout=15,
            )
        except subprocess.TimeoutExpired:
            fail("intervals.py timed out (possible infinite loop)")
        except Exception as exc:
            fail(f"could not run intervals.py: {exc}")

        if proc.returncode != 0:
            fail(f"intervals.py crashed: {proc.stderr.strip()[-300:]}")

        try:
            payload = json.loads(proc.stdout.strip().splitlines()[-1])
        except Exception:
            fail(f"could not parse output: {proc.stdout[:300]!r}")

        if "import_error" in payload:
            fail(f"could not import intervals.py: {payload['import_error']}")

        results = payload.get("results")
        if not isinstance(results, list) or len(results) != len(expected):
            fail("unexpected result shape from intervals.py")

        for i, (got, exp) in enumerate(zip(results, expected)):
            if not got.get("ok"):
                fail(f"case {i} input={cases[i]['input']}: raised {got.get('error')} unexpectedly")
            gv = got.get("value")
            if not isinstance(gv, list) or normalize(gv) != normalize(exp["value"]):
                fail(f"case {i} input={cases[i]['input']}: expected {exp['value']!r}, got {gv!r}")
    finally:
        try:
            os.unlink(runner_path)
        except OSError:
            pass

    print(f"PASS: merge_intervals() matched the expected result on all {len(expected)} hidden cases")
    sys.exit(0)


if __name__ == "__main__":
    main()
