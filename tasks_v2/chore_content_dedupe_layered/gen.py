"""Shared generator for chore_content_dedupe_layered. Stays in tasks_v2/,
never copied to workdir."""
import random

SEED = 19840318


def generate(seed=SEED):
    """Return a list of (relpath, content_str).

    Deliberately includes:
      - a duplicate set spread across three different depths, where the
        shallowest copy is not the alphabetically-first one, so a
        depth-first tie-break and an alphabetical-only tie-break disagree.
      - a duplicate pair at equal depth, to exercise the alphabetical
        secondary tie-break.
      - a duplicate pair at equal depth in different subtrees (further
        exercise of the same rule).
      - three empty (0-byte) files scattered across different
        directories: they are byte-for-byte identical to each other, but
        empty files are explicitly excluded from the dedup rule, so all
        three must survive untouched. A content-hash dedupe that does not
        special-case empty content would collapse them to one.
      - two files that share a basename ("notes.txt") but have different
        content: they are not duplicates of each other and must both
        survive.
      - one file with genuinely unique content.
    """
    rng = random.Random(seed)

    def filler(tag):
        return f"filler-{tag}-{rng.randint(0, 999999)}\n"

    files = [
        ("top_summary.txt", "QUARTERLY SUMMARY\n" + filler("sum")),
    ]
    summary_content = files[0][1]
    files.append(("reports/summary.txt", summary_content))
    files.append(("reports/archive/summary_copy.txt", summary_content))

    rowset = "id,value\n1,10\n2,20\n" + filler("rows")
    files.append(("data/b_file.csv", rowset))
    files.append(("data/a_file.csv", rowset))

    mval = "shared payload\n" + filler("m")
    files.append(("x/m.txt", mval))
    files.append(("y/m.txt", mval))

    files.append(("logs/empty1.log", ""))
    files.append(("logs/sub/empty2.log", ""))
    files.append(("empty3.log", ""))

    files.append(("notes/notes.txt", "note A\n" + filler("noteA")))
    files.append(("archive/notes.txt", "note B, unrelated\n" + filler("noteB")))

    files.append(("readme.md", "unique readme content\n" + filler("readme")))

    return files


def depth_of(relpath):
    return relpath.count("/")


def compute_expected(files):
    """Return (kept_set, deletions) where deletions is a list of
    (kept_relpath, deleted_relpath) sorted by kept then deleted."""
    by_content = {}
    for relpath, content in files:
        if content == "":
            continue  # empty files are excluded from the dedup rule
        by_content.setdefault(content, []).append(relpath)

    deletions = []
    kept_set = set(r for r, _c in files)
    for content, paths in by_content.items():
        if len(paths) < 2:
            continue
        ordered = sorted(paths, key=lambda p: (depth_of(p), p))
        keep = ordered[0]
        for loser in ordered[1:]:
            kept_set.discard(loser)
            deletions.append((keep, loser))

    deletions.sort(key=lambda t: (t[0], t[1]))
    return kept_set, deletions
