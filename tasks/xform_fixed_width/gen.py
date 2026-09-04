"""Generator for xform_fixed_width. Stays in tasks/, never copied to workdir."""
import random

SEED = 13579246

FIRST = [
    "Amara", "Kenji", "Priya", "Diego", "Freya", "Omar", "Lucia", "Ivan",
    "Noor", "Theo", "Sana", "Mateo", "Yara", "Felix", "Nadia", "Bram",
]
LAST = [
    "Osei", "Tanaka", "Sharma", "Reyes", "Nilsson", "Haddad", "Rossi",
    "Petrov", "Khan", "Larsen", "Costa", "Weber", "Silva", "Novak",
]
DEPTS = ["OPS", "ENG", "FIN", "HR", "MKT", "LEG", "SLS", "R&D"]

N_ROWS = 160

NAME_W = 18
ID_W = 8
DEPT_W = 6
AMOUNT_W = 12


def generate(seed=SEED):
    """Return list of dicts: name (str), emp_id (int), dept (str),
    amount (float, 2 decimals, can be negative).
    """
    rng = random.Random(seed)
    rows = []
    for i in range(N_ROWS):
        name = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
        emp_id = 100000 + i * 3 + rng.randint(0, 2)
        dept = rng.choice(DEPTS)
        cents = rng.randint(-999999, 999999)
        amount = cents / 100.0
        rows.append({"name": name, "emp_id": emp_id, "dept": dept, "amount": amount})
    return rows


def format_record(row):
    name_field = row["name"].ljust(NAME_W)[:NAME_W]
    id_field = str(row["emp_id"]).rjust(ID_W)
    dept_field = row["dept"].ljust(DEPT_W)[:DEPT_W]
    amount_field = f"{row['amount']:.2f}".rjust(AMOUNT_W)
    return name_field + id_field + dept_field + amount_field
