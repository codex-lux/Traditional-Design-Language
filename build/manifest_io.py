#!/usr/bin/env python3
"""manifest_io.py — one atomic writer for `assets/manifest.json`.

FIVE SCRIPTS WRITE THIS FILE AND EVERY ONE OF THEM DID IT THE UNSAFE WAY:

    json.dump(doc, open(ASSETS, "w"), indent=2, ensure_ascii=False)

`open(path, "w")` truncates before a byte is written. The file is 3.4 MB and 74,000 lines, so
the window between truncation and the last byte is real, not theoretical -- and inside it the
manifest on disk is a prefix of valid JSON, which is to say a corrupt file. A Ctrl-C, a full
disk, an OOM kill or a crash inside the encoder leaves it that way. `gen_assets.py` makes this
sharper than the rest: it READS the prior manifest to carry forward provenance, files, statuses
and fault links, so a truncated write destroys the only copy of the thing the next run needs in
order not to destroy it. Recoverable from git, but "recoverable from git" is not a write
guarantee, and nothing warned.

Write to a sibling temp file, fsync it, then `os.replace`. On POSIX that rename is atomic within
a filesystem, so a reader sees the old file or the new one and never a prefix of either.

The temp file is a SIBLING and not in /tmp on purpose: os.replace cannot be atomic across
filesystems, and /tmp is frequently a different one.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets", "manifest.json")


def write_manifest(doc, path=ASSETS):
    """Serialise `doc` over `path` atomically. Returns the path written."""
    tmp = path + ".writing"
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
        # The rename itself is metadata and can outlive the crash that loses it: on ext4 with
        # data=writeback, a crash immediately after os.replace can leave the directory entry
        # unwritten. fsync the containing directory so the rename is durable too.
        dfd = os.open(os.path.dirname(os.path.abspath(path)), os.O_DIRECTORY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except BaseException:
        # BaseException, not Exception: a KeyboardInterrupt in the middle of the dump is the
        # exact case this exists for, and it does not inherit from Exception.
        if os.path.exists(tmp):
            try:
                os.unlink(tmp)
            except OSError:
                pass
        raise
    return path


def recount(doc):
    """Recompute the header tallies from the records, so the two cannot disagree.

    Three scripts each carried their own copy of this loop and one of them (`gen_assets.py`)
    only ever counted `wanted`, so the header said 1,850 wanted while 73 had files."""
    assets = doc.get("assets") or []
    by_status, by_priority = {}, {}
    for a in assets:
        by_status[a.get("status")] = by_status.get(a.get("status"), 0) + 1
        by_priority[a.get("priority")] = by_priority.get(a.get("priority"), 0) + 1
    counts = doc.setdefault("counts", {})
    counts["total"] = len(assets)
    counts["by_status"] = by_status
    counts["by_priority"] = {p: by_priority.get(p, 0)
                             for p in ("critical", "high", "normal", "low")}
    counts["pairs"] = sum(1 for a in assets if a.get("role") == "correct")
    return doc
