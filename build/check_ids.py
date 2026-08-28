#!/usr/bin/env python3
"""Hold the open-question register's ids to their filenames, and the work-package
reports to theirs.

WHY THIS EXISTS
---------------
Four id collisions in four days, every one by the same mechanism: an agent reads
the working tree, finds the highest number, and adds one. Two agents on two
branches both find 98 and both write 99. The register renumbered a block at the
merge four times -- 32-41 -> 54-63, 64-66 -> 66-68, 64-66 -> 69-71, 72-83 -> 78-89,
then 78-85 -> 91-98 -- and after the fourth, reading a bare "OQ 78" in this
branch's history is ambiguous BY DATE.

The cause was structural and it was one line of it: `docs/open-questions.md` was a
SINGLE FILE. Two branches appending an entry to one file produce a *text* conflict,
and git resolves a text conflict by juxtaposition -- both entries survive, both
numbered 99, and nothing anywhere notices. Every other id family in this corpus is
one record per file (`faults/`, `rooms/`, `partis/`, `proportions/`, `styles/`),
where two sessions issuing the same id create the same PATH and git raises an
add/add conflict it refuses to auto-resolve. Open questions were the only ids kept
in a shared file and the only ids that have ever collided. WP-5.11's audit measured
it: 1,522 `OQ <n>` references across the tree, 218 of them in the contested 72-98
block, and 197 stamped into a single kit file.

So the register is a directory now, and this checker is what makes the guarantee
legible rather than accidental.

WHAT WAS NOT CHECKED BEFORE, AND IS NOW
---------------------------------------
Nothing anywhere checked that two open questions did not share an id.
`tests/test_wp46_packs.py`'s derivation test parses the register with `re.findall`
and collects the result into a **set** -- so two entries both numbered 78 collapse
to one member and the assertion passes. The guard against the exact failure this
corpus suffered four times was structurally incapable of seeing it.

UNJUDGED IS NOT PASSED
----------------------
A status word this checker does not recognise is an ERROR, not a shrug. An entry
whose state cannot be read must never be counted as settled -- that is the same
discipline every other checker here keeps, and the reason the vocabulary is a
named list rather than a regex for "some bold word".
"""
import os, re, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QDIR = os.path.join(ROOT, "docs", "open-questions")
REPORTS = os.path.join(ROOT, "docs", "reports")

COULD_NOT_EVALUATE = 3

# The vocabulary actually in use, measured from the register rather than imagined.
# A word outside these two tuples fails the run; it is never assumed benign.
SETTLED = ("CLOSED", "RESOLVED", "RULED", "FIXED", "CONFIRMED", "ANSWERED",
           "LEFT AS A STANDING DISCLOSURE", "SUPERSEDED", "WITHDRAWN")
OPEN = ("OPEN", "STILL OPEN", "HALF CLOSED", "PARTLY", "IN PROGRESS")

FILENAME = re.compile(r"^(\d{3})-([a-z0-9][a-z0-9-]*)\.md$")
HEADING = re.compile(r"^# OQ (\d+) — ", re.M)
STATUS_LINE = re.compile(r"^\*Status: (.+?) · Raised in: (.+?)\*$", re.M)


def normalise(word):
    """`HALF-CLOSED 26 Aug 2026` and `Half closed` are the same status."""
    head = re.split(r"[—.:*(,]", word, 1)[0]
    return re.sub(r"[\s\-]+", " ", head).strip().upper()


def read_questions():
    out, errors = {}, []
    for name in sorted(os.listdir(QDIR)):
        if name == "README.md" or not name.endswith(".md"):
            continue
        m = FILENAME.match(name)
        if not m:
            errors.append(f"{name}: filename must be <nnn>-<slug>.md, three digits "
                          f"and a lowercase-hyphen slug — the id IS the filename")
            continue
        fid = int(m.group(1))
        text = open(os.path.join(QDIR, name), encoding="utf-8").read()

        h = HEADING.search(text)
        if not h:
            errors.append(f"{name}: no `# OQ <n> — <title>` heading")
        elif int(h.group(1)) != fid:
            # The one disagreement a directory cannot prevent by itself.
            errors.append(f"{name}: heading says OQ {h.group(1)} but the filename "
                          f"says {fid}. The filename wins; fix the heading.")

        s = STATUS_LINE.search(text)
        if not s:
            errors.append(f"{name}: no `*Status: … · Raised in: …*` line")
            continue
        word = normalise(s.group(1))
        if word.startswith(SETTLED):
            state = "settled"
        elif word.startswith(OPEN):
            state = "open"
        else:
            errors.append(f"{name}: unrecognised status {s.group(1)!r}. Add the word "
                          f"to SETTLED or OPEN in this file — an unclassified entry "
                          f"must never silently count as settled.")
            state = "unjudged"
        if fid in out:
            # The one collision a directory does NOT prevent by itself, and the reason the CI
            # gate below exists: two sessions issuing id 99 with DIFFERENT slugs create two
            # different paths, so git merges both without a word and the register carries two
            # entries numbered 99 -- which is exactly what happened four times in a single file.
            errors.append(f"DUPLICATE ID {fid}: {out[fid]['file']} and {name}. Ids are never "
                          f"reused (PLAN-OF-ACTION.md §1). One of these was issued by reading "
                          f"the working tree; give it the next free id and say so in the "
                          f"register's README.")
            continue
        out[fid] = {"file": name, "status": s.group(1), "state": state,
                    "raised": s.group(2)}
    return out, errors


def check_reports():
    """A work-package report is cited by its filename, so two packages may not share
    one. WP-5.12 and WP-5.14 both shipped `-the-four-rulings.md`, which is why OQ 90's
    own fallback -- "cite the report, never the number" -- did not actually
    disambiguate anything."""
    errors = []
    by_number = collections.defaultdict(list)
    by_slug = collections.defaultdict(list)
    for name in sorted(os.listdir(REPORTS)):
        m = re.match(r"^wp-(\d+\.\d+)-(.+)\.md$", name)
        if not m:
            continue
        by_number[m.group(1)].append(name)
        by_slug[m.group(2)].append(name)
    for slug, names in sorted(by_slug.items()):
        if len(names) > 1:
            errors.append(f"two reports share the slug {slug!r}: {', '.join(names)}. "
                          f"A package is cited by its report, so the slug has to be "
                          f"distinctive on its own.")

    # A citation that does not resolve is the same defect one layer out: OQ 90's whole
    # fallback was "cite the report, never the number", and a dangling path makes that
    # advice useless. Found one on the first run -- `wp-2.3-real-solver.md`, which has
    # never existed; the file is `wp-2.3-the-real-solver.md` and had been cited wrong
    # since WP-2.3 shipped.
    have = set(sorted(os.listdir(REPORTS)))
    cited = set()
    # sorted(), because an unsorted directory read makes the order machine-specific
    # and tests/test_determinism.py holds the whole corpus to that.
    for base, _dirs, names in sorted(os.walk(ROOT)):
        if any(p in base for p in ("node_modules", "/.git", "/dist")):
            continue
        for n in sorted(names):
            if not n.endswith((".md", ".py", ".json", ".jsx", ".js", ".mjs")):
                continue
            try:
                text = open(os.path.join(base, n), encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            cited |= set(re.findall(r"docs/reports/([A-Za-z0-9][A-Za-z0-9._-]*\.md)", text))
    for miss in sorted(cited - have):
        errors.append(f"docs/reports/{miss} is cited somewhere and does not exist")
    return by_number, errors


def main():
    if not os.path.isdir(QDIR):
        print(f"COULD NOT EVALUATE — {QDIR} does not exist")
        return COULD_NOT_EVALUATE

    qs, errors = read_questions()
    by_number, report_errors = check_reports()
    errors += report_errors

    if qs:
        ids = sorted(qs)
        missing = sorted(set(range(1, max(ids) + 1)) - set(ids))
        if missing:
            # Not fatal on its own -- a withdrawn question leaves a hole and the id is
            # never reused -- but it is always worth saying out loud.
            print(f"note: ids not present: {missing} (ids are never reused, so a hole "
                  f"is legitimate; say so in the register's README)")

    states = collections.Counter(q["state"] for q in qs.values())
    print(f"{len(qs)} open question(s) — {states['open']} open, "
          f"{states['settled']} settled, {states['unjudged']} UNJUDGED")
    print(f"{sum(len(v) for v in by_number.values())} work-package report(s) "
          f"across {len(by_number)} number(s)")
    for num, names in sorted(by_number.items()):
        if len(names) > 1:
            # Legitimate where they are waves of ONE package (WP-1.1, WP-4.2); an
            # error only when the slugs collide, which is checked above.
            print(f"  note: WP-{num} has {len(names)} reports: {', '.join(names)}")

    if errors:
        print("\nFAILED:")
        for e in errors:
            print(f"  {e}")
        return 1
    print("\nEvery id matches its filename; every status is a word this checker knows.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
