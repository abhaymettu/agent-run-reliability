#!/usr/bin/env python3
"""check.py <workdir> -- runs a hidden battery of top_k() cases, recomputed
from gen.py, against the agent's leaderboard.py. Exits 0 only if every case
matches, including exact tie-break order. Never crashes: any failure mode
prints one FAIL line and exits 1."""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import hidden_cases, reference_top_k  # noqa: E402

RUNNER = '''
import json
import sys

sys.path.insert(0, sys.argv[1])
try:
    from leaderboard import top_k
except Exception as exc:
    print(json.dumps({"import_error": repr(exc)}))
    sys.exit(0)

cases = json.loads(sys.argv[2])
out = []
for c in cases:
    try:
        val = top_k([dict(e) for e in c["entries"]], c["k"])
        out.append({"ok": True, "value": [e["name"] for e in val]})
    except Exception as exc:
        out.append({"ok": False, "error": type(exc).__name__})
print(json.dumps({"results": out}))
'''


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


def main():
    if len(sys.argv) != 2:
        fail("usage check.py <workdir>")
    workdir = os.path.abspath(sys.argv[1])

    if not os.path.isfile(os.path.join(workdir, "leaderboard.py")):
        fail("leaderboard.py not found")

    cases = hidden_cases()
    expected = [
        {"ok": True, "value": [e["name"] for e in reference_top_k(c["entries"], c["k"])]}
        for c in cases
    ]

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
            fail("leaderboard.py timed out (possible infinite loop)")
        except Exception as exc:
            fail(f"could not run leaderboard.py: {exc}")

        if proc.returncode != 0:
            fail(f"leaderboard.py crashed: {proc.stderr.strip()[-300:]}")

        try:
            payload = json.loads(proc.stdout.strip().splitlines()[-1])
        except Exception:
            fail(f"could not parse output: {proc.stdout[:300]!r}")

        if "import_error" in payload:
            fail(f"could not import leaderboard.py: {payload['import_error']}")

        results = payload.get("results")
        if not isinstance(results, list) or len(results) != len(expected):
            fail("unexpected result shape from leaderboard.py")

        for i, (got, exp) in enumerate(zip(results, expected)):
            if not got.get("ok"):
                fail(f"case {i}: raised {got.get('error')} unexpectedly")
            if got.get("value") != exp["value"]:
                fail(f"case {i}: expected order {exp['value']!r}, got {got.get('value')!r}")
    finally:
        try:
            os.unlink(runner_path)
        except OSError:
            pass

    print(f"PASS: top_k() matched the expected order on all {len(expected)} hidden cases")
    sys.exit(0)


if __name__ == "__main__":
    main()
