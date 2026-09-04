"""Shared generator for chore_manifest_multiuse_sync. Stays in tasks_v2/,
never copied to workdir."""
import random

SEED = 88112233


def generate(seed=SEED):
    """Return (sources, manifest_entries, prebuilt).

    sources: list of (source_relname, content_str) -- files that live under
      "sources/" in the workdir.
    manifest_entries: list of (target_relpath, source_relname) describing
      "manifest.json" (target paths are relative to "build/"). One source,
      "config_base.ini", is deliberately referenced by TWO different
      targets -- a naive sync that treats each source as consumable once
      (moves it, or skips a source it has already "used") satisfies only
      one of the two targets, and/or ends up mutating or losing the
      original under sources/.
    prebuilt: list of (relpath_under_build, content_str) -- files that
      already exist under "build/" before the task starts:
        - "stale/old_report.txt": a decoy not referenced by any manifest
          entry, in a directory that exists only because of the decoy, so
          the directory must be removed once the decoy is removed.
        - "app/config.ini": pre-existing but with stale WRONG content that
          must be overwritten to match the source.
        - "docs/notes.txt": pre-existing and already correct.
    """
    rng = random.Random(seed)

    def body(tag):
        return f"{tag}-payload-{rng.randint(0, 999999)}\n"

    sources = [
        ("logo.png", "PNGDATA " + body("logo")),
        ("config_base.ini", "[base]\n" + body("config")),
        ("report_template.txt", "REPORT TEMPLATE\n" + body("report")),
        ("notes_raw.txt", "RAW NOTES\n" + body("notes")),
    ]
    source_content = dict(sources)

    manifest_entries = [
        ("app/config.ini", "config_base.ini"),
        ("backup/config.ini", "config_base.ini"),
        ("assets/logo.png", "logo.png"),
        ("docs/report.txt", "report_template.txt"),
        ("docs/notes.txt", "notes_raw.txt"),
    ]

    prebuilt = [
        ("stale/old_report.txt", "STALE LEFTOVER\n" + body("stale")),
        ("app/config.ini", "[base]\nOLD STALE CONFIG\n"),
        ("docs/notes.txt", source_content["notes_raw.txt"]),
    ]

    return sources, manifest_entries, prebuilt


def compute_expected(sources, manifest_entries):
    """Return {target_relpath: content_str}."""
    source_content = dict(sources)
    return {target: source_content[src] for target, src in manifest_entries}
