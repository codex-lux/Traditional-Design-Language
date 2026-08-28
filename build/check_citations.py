#!/usr/bin/env python3
"""Keep every `OQ N` citation findable, resolvable, and convertible.

WHY THIS EXISTS, precisely -- because the failure it guards is subtle and has
already happened twice, in two different sessions, four days apart.

The open-question register has collided across parallel sessions four times in
four days. Each collision is followed by a renumbering pass over the whole tree,
and each pass so far has been a regex of the form `\\bOQ (7[89]|8[0-5])\\b`.
That regex CANNOT SEE THE SECOND NUMBER IN A LIST. Given

    (WP-7.4, OQ 82 and 84 CLOSED)

it matches `OQ 82`, renumbers it, and leaves `84` untouched -- because `84`
carries no `OQ` prefix and is therefore not a citation as far as any tool is
concerned. The reference is then silently wrong, and wrong in the worst
available way: the stale number still names a REAL entry, so nothing dangles,
no existence check fires, and the sentence reads perfectly.

Three live instances were on main when this was written:

    PLAN-OF-ACTION.md:19    OQ 95, 79 and 78   -> OQ 95, OQ 92 and OQ 91
    CLAUDE.md:286           OQ 95 and 84       -> OQ 95 and OQ 97
    PLAN-OF-ACTION.md:589   OQ 78, 73, 74      -> OQ 78, OQ 79 and OQ 80

The third was produced by a different session, on a different branch, by the
same mechanism -- which is what makes this a class and not a slip.

WHAT THIS DOES AND DOES NOT PROVE. Check B below is the one that would have
caught all three. Check A is a ratchet (1,502 citations, 0 dangling when
written) and would have caught NONE of them, because every wrong id named a
real entry; it is here to stop a typo, not this bug, and saying so is the
point. Nothing here verifies that a citation's SUBJECT matches the entry it
names -- that cannot be done honestly by a machine, and a check that pretended
to would be "unjudged reported as passed" in a new place.

AND THIS DOES NOT STOP COLLISIONS. Ids are still issued from the working tree,
which is the actual cause, and the register has now predicted its own next
collision three times and been right three times. This file makes the
AFTERMATH of a collision mechanically complete. It does not prevent one.

Run:  python3 build/check_citations.py [--fix] [--verbose]
Exit: 0 clean, 1 if any check fails (or anything was rewritten under --fix).
"""
import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTER = os.path.join("docs", "open-questions.md")
# The two files that contain the malformed shape on purpose (see tracked_files).
SPECIMEN = {"build/check_citations.py", "tests/test_citations.py"}
# Entries 1-99 are the legacy numeric block and are frozen. Every question raised after
# 28 Aug 2026 is NAMED (`### oq/<slug>`), because a sequential id has to be issued from
# somewhere and the only shared state two parallel sessions have is the repo they both
# branched from -- which is how the same block collided four times in four days. A slug is
# derived from the subject rather than issued, so two sessions choosing one have raised the
# same question, and that conflict is one you want to see.
FROZEN_CEILING = 99

# A month name after a number means the number is a DATE, not a citation.
# "OQ 18, 24 Aug 2026: reclassified from ..." is correct prose and must never be
# flagged. The first version of this detector omitted this and reported 68 hits
# of which 46 were dates -- a checker that cries wolf on correct lines gets
# turned off within a day, which is this codebase's own load.py lesson (an
# instrument that misreports is worse than no instrument).
MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"

# `OQ 12` and the run of bare continuation numbers that follows it, if any.
CITE = re.compile(rf"\bOQ (\d+)((?:\s*(?:,|and|or|&)\s*\d+(?!\s+{MONTH})(?!\d))*)")
# One continuation number inside that run, with the separator that introduced it.
# An inline code span: a literal being shown, not a reference being made.
CODE = re.compile(r"`[^`]*`")
# A named entry's heading, and a citation of one.
SLUG_ENTRY = re.compile(r"^###\s+`?(oq/[a-z0-9][a-z0-9-]*)`?\s*$", re.M)
SLUG_CITE = re.compile(r"\boq/[a-z0-9][a-z0-9-]*")
CONT = re.compile(rf"(\s*(?:,|and|or|&)\s*)(\d+)(?!\s+{MONTH})(?!\d)")


def entry_ids(text):
    """The ids the register actually defines, as `N. **STATUS ...` list items."""
    return {int(n) for n in re.findall(r"^(\d+)\. ", text, re.M)}


def slug_ids(text):
    """The NAMED entries -- everything raised after the numbers were frozen."""
    return set(SLUG_ENTRY.findall(text))


def tracked_files():
    # --untracked, because a NEW file is exactly where a fresh citation lives. Without it the
    # checker read only committed files: this package's own report quoted the bug form and was
    # invisible until `git add`, which is the worst possible moment to start checking.
    out = subprocess.run(["git", "grep", "--untracked", "-lE", r"OQ [0-9]+", "--", "."],
                         cwd=ROOT, capture_output=True, text=True).stdout.split()
    # The register defines the ids; it does not cite them, and its conversion
    # tables carry bare historical numbers ON PURPOSE (see check C).
    #
    # And two files hold the bad form deliberately: this checker's own docstring, which shows
    # what the bug looks like, and its test fixtures, which feed it. A checker that convicts
    # its own specification is a checker nobody can keep. The exemption is BY NAME and only
    # these two -- everything else complies, this package's own report included, which was
    # caught by exactly this run and fixed rather than exempted.
    return [f for f in out
            if os.path.basename(f) != "open-questions.md"
            and f not in SPECIMEN]


def conversion_rows(text):
    """Rows of the reissue tables: `| 72 | **78** | subject |`, and the
    four-column form the fourth collision needed: `| 72 | 78 | **91** | ... |`.
    The LAST numeric cell before the subject is the id the row lands on."""
    rows = []
    for ln, line in enumerate(text.split("\n"), 1):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        nums = []
        for c in cells[:-1]:
            m = re.fullmatch(r"\*{0,2}(\d+)\*{0,2}", c)
            if m:
                nums.append(int(m.group(1)))
        if len(nums) >= 2 and len(nums) == len(cells) - 1:
            rows.append((ln, nums[:-1], nums[-1], cells[-1]))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fix", action="store_true",
                    help="give every bare continuation number its own OQ prefix")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    reg = open(os.path.join(ROOT, REGISTER), encoding="utf-8").read()
    ids = entry_ids(reg)
    if not ids:
        print("FAIL  the register defines no entries -- this checker just stopped "
              "checking anything. Its `N. **STATUS` shape has changed.", file=sys.stderr)
        return 1

    slugs = slug_ids(reg)
    dangling, bare, n_cites = [], [], 0

    # D -- THE ENFORCEMENT. A numbered entry above the ceiling means somebody issued a
    # sequential id from their working tree again, which is the mechanism that collided four
    # times in four days. Refusing it here is what makes the scheme a rule rather than a note
    # in a file nobody re-reads.
    over = sorted(n for n in ids if n > FROZEN_CEILING)
    ceiling = [f"{REGISTER}: entry {n} is above the frozen ceiling of {FROZEN_CEILING} -- "
               f"the numeric block is closed. Raise it as `### oq/<slug>` instead; see "
               f"'How an id is issued' at the head of that file." for n in over]

    for rel in sorted(tracked_files()):
        full = os.path.join(ROOT, rel)
        try:
            text = open(full, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            continue

        for ln, line in enumerate(text.split("\n"), 1):
            # An inline code span is a QUOTATION, not a citation. Documents that discuss this
            # bug have to be able to write `OQ 82 and 84` to show what it looks like -- this
            # file's own report and PLAN-OF-ACTION's board row both do, and without this the
            # checker convicts every description of the thing it checks for.
            line = CODE.sub(lambda c: " " * len(c.group(0)), line)
            for m in CITE.finditer(line):
                n_cites += 1
                if int(m.group(1)) not in ids:
                    dangling.append(f"{rel}:{ln}: OQ {m.group(1)} names no entry")
                tail = m.group(2) or ""
                for c in CONT.finditer(tail):
                    n_cites += 1
                    if int(c.group(2)) not in ids:
                        dangling.append(f"{rel}:{ln}: OQ {c.group(2)} names no entry")
                    bare.append((rel, ln, m.group(0).strip(), c.group(2)))
            for sm in SLUG_CITE.finditer(line):
                n_cites += 1
                if sm.group(0) not in slugs:
                    dangling.append(f"{rel}:{ln}: {sm.group(0)} names no entry")

        if args.fix and any(b[0] == rel for b in bare):
            fixed = CITE.sub(
                lambda m: m.group(0)[:m.start(2) - m.start(0)]
                + CONT.sub(lambda c: f"{c.group(1)}OQ {c.group(2)}", m.group(2) or ""),
                text)
            if fixed != text:
                open(full, "w", encoding="utf-8").write(fixed)

    # C -- the conversion tables are the only thing that makes an old commit
    # message readable, so a row that lands nowhere is a broken audit trail.
    table_bad, n_rows = [], 0
    seen = {}
    for ln, froms, to, subject in conversion_rows(reg):
        n_rows += 1
        if to not in ids:
            table_bad.append(f"{REGISTER}:{ln}: reissue row lands on {to}, which no entry defines")
        if to in seen:
            table_bad.append(
                f"{REGISTER}:{ln}: two rows both land on {to} "
                f"(also line {seen[to]}) -- one of the two renumberings is lost")
        seen[to] = ln

    if args.verbose:
        print(f"  register entries   {len(ids)} (max {max(ids)}, frozen at {FROZEN_CEILING})")
        print(f"  named entries      {len(slugs)}")
        print(f"  citations          {n_cites}")
        print(f"  reissue rows       {n_rows}")

    for d in dangling:
        print("DANGLING  " + d)
    for rel, ln, span, num in bare:
        print(("FIXED     " if args.fix else "BARE      ")
              + f"{rel}:{ln}: `{span}` -- {num} has no OQ of its own, so a "
                f"renumbering pass cannot see it")
    for t in table_bad:
        print("TABLE     " + t)
    for c in ceiling:
        print("CEILING   " + c)

    print(f"\n{n_cites} citation(s) checked across {len(tracked_files())} file(s), "
          f"{n_rows} reissue row(s), {len(slugs)} named entry(s); {len(dangling)} dangling, "
          f"{len(bare)} bare, {len(table_bad)} table fault(s), {len(ceiling)} over the ceiling.")
    if bare and not args.fix:
        print("A bare continuation number is invisible to the regex every renumbering "
              "pass has used. Write `OQ 95 and OQ 97`, never `OQ 95 and 97`. "
              "Run with --fix to insert the prefixes.")
    return 1 if (dangling or bare or table_bad or ceiling) else 0


if __name__ == "__main__":
    sys.exit(main())
