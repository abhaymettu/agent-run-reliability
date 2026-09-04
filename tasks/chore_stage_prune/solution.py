import os
import shutil
import sys


def main():
    workdir = sys.argv[1]
    inbox = os.path.join(workdir, "inbox")
    archive = os.path.join(workdir, "archive")

    # Step 1: find all files (pre-move state), decide which are flagged.
    to_archive = []  # (full_path, rel_path)
    all_files_by_dir = {}  # dir_full_path -> count of files in its subtree (pre-move)
    for dirpath, dirnames, filenames in os.walk(inbox):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for fname in filenames:
            if fname.startswith("."):
                continue
            full = os.path.join(dirpath, fname)
            with open(full) as f:
                first_line = f.readline().rstrip("\n")
            if first_line == "ARCHIVE: yes":
                rel = os.path.relpath(full, workdir).replace(os.sep, "/")
                to_archive.append((full, rel))

    os.makedirs(archive, exist_ok=True)
    manifest_lines = []
    for full, rel in sorted(to_archive, key=lambda t: t[1]):
        base = os.path.basename(full)
        dest = os.path.join(archive, base)
        shutil.move(full, dest)
        manifest_lines.append(f"{rel} -> archive/{base}")

    # Step 2: prune directories that now contain zero files in their subtree,
    # but only those that had at least one file before step 1. Walk bottom-up.
    # Compute "had at least one file before step 1" using remembered set of
    # archived+surviving relative dirs -- recompute by checking whether the
    # directory (or any descendant) appears as an ancestor of any moved or
    # currently-present file, tracked before we deleted anything: since we
    # only moved files (didn't delete unflagged ones), "had files before" for
    # any directory still standing is: (has any file remaining now) or (had
    # any file that got archived from within it). Track archived dirs.
    archived_dirs = set()
    for full, rel in to_archive:
        d = os.path.dirname(rel)
        while d and d != "inbox":
            archived_dirs.add(d)
            d = os.path.dirname(d)
    for dirpath, dirnames, filenames in os.walk(inbox, topdown=False):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        if dirpath == inbox:
            continue
        rel = os.path.relpath(dirpath, workdir).replace(os.sep, "/")
        now_has_file = has_any_file(dirpath)
        if now_has_file:
            continue
        # empty now -- was it ever populated (directly or via a now-archived
        # descendant)?
        was_populated = rel in archived_dirs
        if was_populated:
            try:
                os.rmdir(dirpath)
            except OSError:
                pass
        # else: pre-existing empty directory -- leave untouched

    manifest_path = os.path.join(workdir, "archive_manifest.txt")
    with open(manifest_path, "w") as f:
        for line in manifest_lines:
            f.write(line + "\n")


def has_any_file(dirpath):
    for _dp, dirnames, filenames in os.walk(dirpath):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for fname in filenames:
            if not fname.startswith("."):
                return True
    return False


if __name__ == "__main__":
    main()
