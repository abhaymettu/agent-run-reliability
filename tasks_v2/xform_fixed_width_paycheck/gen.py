"""Shared generator for xform_fixed_width_paycheck. Stays in tasks_v2/, never copied to workdir."""

SEED = 20260904

# Fixed column layout, 0-indexed, half-open ranges:
#   employee_id : [0, 6)   6 chars, e.g. "EMP001"
#   name        : [6, 22)  16 chars, left-justified, space padded
#   amount      : [22, 34) 12 chars, right-justified; plain "1234.56" style
#                 or parenthesized "(123.45)" for a negative amount
#   flag        : [34, 35) 1 char: "V" (void) or " " (normal)
LINE_LEN = 35


def _amount_field(cents):
    neg = cents < 0
    c = abs(cents)
    s = f"{c // 100}.{c % 100:02d}"
    if neg:
        s = f"({s})"
    return s.rjust(12)


def _make_line(emp_id, name, cents, void):
    id_field = emp_id.ljust(6)[:6]
    name_field = name.ljust(16)[:16]
    amt_field = _amount_field(cents)
    flag_field = "V" if void else " "
    line = id_field + name_field + amt_field + flag_field
    assert len(line) == LINE_LEN, len(line)
    return line


def generate(seed=SEED):
    """Return a list of dicts: {employee_id, name, cents, void} in file order.

    Deliberately plants:
      - a voided row with a large nonzero amount that must be excluded from
        the employee's total but still counted in their record_count
      - an employee whose non-void amounts sum to exactly 0.00 (a positive
        and an equal negative), to check "0.00" is emitted (not "-0.00")
      - a negative amount expressed with the parenthesis convention
      - an employee's rows scattered non-contiguously through the file
      - a name field containing embedded spaces (breaks naive .split())
    """
    rows = []

    def add(emp_id, name, cents, void=False):
        rows.append({"employee_id": emp_id, "name": name, "cents": cents, "void": void})

    add("EMP001", "Alice Nguyen", 145000, False)
    add("EMP002", "Bob T Reyes", 98050, False)
    add("EMP003", "Carol Osei", 250000, True)   # voided, large amount
    add("EMP001", "Alice Nguyen", 32000, False)  # scattered, same employee
    add("EMP004", "Dave M Kim", 60000, False)
    add("EMP004", "Dave M Kim", -60000, False)   # nets to exactly 0.00
    add("EMP002", "Bob T Reyes", -15075, False)  # negative, parens style
    add("EMP005", "Erin de la Cruz", 120000, False)
    add("EMP003", "Carol Osei", 88800, False)    # non-void row for EMP003
    add("EMP006", "Frank O", 5000, True)         # voided, only row for EMP006
    add("EMP001", "Alice Nguyen", -2000, True)   # voided AND negative
    add("EMP005", "Erin de la Cruz", 33300, False)

    return rows


def render_line(row):
    return _make_line(row["employee_id"], row["name"], row["cents"], row["void"])


def process(rows):
    """Return {employee_id: (total_cents, record_count)}.

    total_cents sums only non-void rows' amounts; record_count counts every
    row for that employee, void or not.
    """
    totals = {}
    counts = {}
    for r in rows:
        eid = r["employee_id"]
        counts[eid] = counts.get(eid, 0) + 1
        if not r["void"]:
            totals[eid] = totals.get(eid, 0) + r["cents"]
        else:
            totals.setdefault(eid, 0)
    return {eid: (totals[eid], counts[eid]) for eid in counts}


def format_cents(cents):
    sign = "-" if cents < 0 else ""
    c = abs(cents)
    return f"{sign}{c // 100}.{c % 100:02d}"
