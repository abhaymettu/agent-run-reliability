"""Shared generator for chore_stage_prune. Stays in tasks_v2/, never copied to workdir."""
import random

SEED = 71190423


def generate(seed=SEED):
    """Return (files, pre_empty_dirs).

    files: list of (relpath, content_str, flagged_bool). relpath uses "/"
    separators and is rooted at the workdir (e.g. "inbox/a/b/c/only.txt").
    pre_empty_dirs: list of directory relpaths that must exist at setup time
    and contain nothing at all (no files, no subdirectories).

    Deliberately includes:
      - a chain of nested directories (inbox/a/b/c) whose only file is
        flagged, so all three levels must be pruned once the file is moved
        out (recursive, bottom-up).
      - a directory (inbox/mixed) with one flagged and one unflagged file:
        it must survive, because a file remains.
      - a directory (inbox/never_flagged) with only unflagged files: left
        completely alone.
      - a directory (inbox/multi) whose two immediate children are each
        fully flagged: both children prune, then multi itself prunes too,
        even though no file was ever placed directly in multi.
      - a directory (inbox/solo) with a single flagged file: prunes.
      - a directory (inbox/keepme_empty) that is empty at setup time (no
        files anywhere below it, ever) and must be left untouched -- it is
        indistinguishable, after the run, from a directory that just lost
        its last file, unless the checker tracks pre-run state.
    """
    rng = random.Random(seed)
    files = []

    def mk(path, flagged, extra=None):
        marker = "ARCHIVE: yes\n" if flagged else "ARCHIVE: no\n"
        body = extra if extra is not None else f"payload for {path} #{rng.randint(0, 999999)}\n"
        files.append((path, marker + body, flagged))

    mk("inbox/a/b/c/only.txt", True)

    mk("inbox/mixed/flagged_one.txt", True)
    mk("inbox/mixed/keep_one.txt", False)

    mk("inbox/never_flagged/note1.txt", False)
    mk("inbox/never_flagged/note2.txt", False)

    mk("inbox/multi/x1/f1.txt", True)
    mk("inbox/multi/x2/f2.txt", True)
    mk("inbox/multi/x2/f3.txt", True)

    mk("inbox/solo/gone.log", True)

    mk("inbox/bulk/keep_a.dat", False)
    mk("inbox/bulk/keep_b.dat", False)
    mk("inbox/bulk/archived_c.dat", True)

    pre_empty_dirs = ["inbox/keepme_empty"]

    return files, pre_empty_dirs


def all_ancestor_dirs(relpath):
    """Yield every directory ancestor of relpath (not including relpath itself
    if it is a file), stopping before the top-level component."""
    parts = relpath.split("/")[:-1]
    cur = []
    out = []
    for p in parts:
        cur.append(p)
        out.append("/".join(cur))
    return out


def compute_expected(files, pre_empty_dirs):
    """Return (archived, surviving_files, pruned_dirs, surviving_dirs).

    archived: list of (orig_relpath, content, archive_relpath="archive/<base>")
    surviving_files: list of (relpath, content) for files that stay in place
    pruned_dirs: set of directory relpaths (under "inbox") that must not exist
    surviving_dirs: set of directory relpaths (under "inbox") that must exist,
                     including "inbox" itself and pre_empty_dirs
    """
    all_dirs = set(["inbox"])
    for relpath, _content, _flag in files:
        for d in all_ancestor_dirs(relpath):
            all_dirs.add(d)
    for d in pre_empty_dirs:
        all_dirs.add(d)

    archived = []
    surviving_files = []
    for relpath, content, flagged in files:
        if flagged:
            base = relpath.rsplit("/", 1)[-1]
            archived.append((relpath, content, f"archive/{base}"))
        else:
            surviving_files.append((relpath, content))

    pruned_dirs = set()
    surviving_dirs = set()
    for d in all_dirs:
        if d == "inbox":
            surviving_dirs.add(d)
            continue
        prefix = d + "/"
        had_file_at_setup = any(rp.startswith(prefix) for rp, _c, _f in files)
        files_after = [rp for rp, _c, flag in files if (not flag) and rp.startswith(prefix)]
        if had_file_at_setup and len(files_after) == 0:
            pruned_dirs.add(d)
        else:
            surviving_dirs.add(d)

    return archived, surviving_files, pruned_dirs, surviving_dirs
