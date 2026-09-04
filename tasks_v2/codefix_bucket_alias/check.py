#!/usr/bin/env python3
"""check.py <workdir> -- runs a hidden battery of bucket_items() cases,
recomputed from gen.py, against the agent's buckets.py. Exits 0 only if
every case matches (checking both presence AND absence, which the shipped
tests never do). Never crashes: any failure mode prints one FAIL line and
exits 1."""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import apply_keyfn, hidden_cases, reference_bucket  # noqa: E402

RUNNER = '''
import json
import sys

sys.path.insert(0, sys.argv[1])
try:
    from buckets import bucket_items
except Exception as exc:
    print(json.dumps({"import_error": repr(exc)}))
    sys.exit(0)


def apply_keyfn(name, item):
    if name == "first_char":
        return item[0]
    if name == "mod3":
        return item % 3
    raise ValueError(name)


cases = json.loads(sys.argv[2])
out = []
for c in cases:
    try:
        fn = lambda item, name=c["keyfn"]: apply_keyfn(name, item)
        val = bucket_items(list(c["items"]), fn, list(c["keys"]))
        val = {str(k): v for k, v in val.items()}
        out.append({"ok": True, "value": val})
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

    if not os.path.isfile(os.path.join(workdir, "buckets.py")):
        fail("buckets.py not found")

    cases = hidden_cases()
    expected = []
    for c in cases:
        fn = lambda item, name=c["keyfn"]: apply_keyfn(name, item)
        buckets = reference_bucket(c["items"], fn, c["keys"])
        expected.append({str(k): v for k, v in buckets.items()})

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
            fail("buckets.py timed out (possible infinite loop)")
        except Exception as exc:
            fail(f"could not run buckets.py: {exc}")

        if proc.returncode != 0:
            fail(f"buckets.py crashed: {proc.stderr.strip()[-300:]}")

        try:
            payload = json.loads(proc.stdout.strip().splitlines()[-1])
        except Exception:
            fail(f"could not parse output: {proc.stdout[:300]!r}")

        if "import_error" in payload:
            fail(f"could not import buckets.py: {payload['import_error']}")

        results = payload.get("results")
        if not isinstance(results, list) or len(results) != len(expected):
            fail("unexpected result shape from buckets.py")

        for i, (got, exp) in enumerate(zip(results, expected)):
            if not got.get("ok"):
                fail(f"case {i}: raised {got.get('error')} unexpectedly")
            gv = got.get("value")
            if not isinstance(gv, dict) or gv.keys() != exp.keys():
                fail(f"case {i}: expected bucket names {sorted(exp.keys())}, got {gv}")
            for k in exp:
                if gv.get(k) != exp[k]:
                    fail(f"case {i} bucket {k!r}: expected {exp[k]!r}, got {gv.get(k)!r}")
    finally:
        try:
            os.unlink(runner_path)
        except OSError:
            pass

    print(f"PASS: bucket_items() matched the expected result on all {len(expected)} hidden cases")
    sys.exit(0)


if __name__ == "__main__":
    main()
