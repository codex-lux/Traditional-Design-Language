# WP-8.1 — The register, the id, and OQ 90

*28 August 2026. Four open-question id collisions in four days, every one found at a merge and
paid for afterwards. This package fixes the cause rather than recording it a fifth time, and
settles OQ 90 — the two work packages both numbered WP-5.7 — on the way past.*

---

## The cause, and why every previous fix was a description of it

The register had predicted its own next collision three times and been right three times. Each
prediction named the habit — *"an id issued by reading the working tree collides whenever two
sessions run at once"* — and none named the mechanism that let the collision **survive a merge**.

`docs/open-questions.md` was **one file**. Two branches appending id 99 to one file produce a
*text* conflict, and git resolves a text conflict by juxtaposition: both entries survive, both
numbered 99, and nothing anywhere notices.

Every other id family in this corpus has the opposite property and always has.
`build/check_faults.py:107` enforces `filename == id + ".json"`, so two sessions issuing the
same fault id create the same **path**, and git raises an add/add conflict it refuses to
auto-resolve. The same one-record-per-file rule is enforced by `check_modules`, `check_systems`,
`check_orders`, `check_rooms`, `check_partis`, `check_openings`/`check_windows` and
`validate.py`.

**Open questions were the only ids in this corpus kept in a single shared file, and the only ids
that have ever collided.** That is the finding, and it was available for four days.

### Three more things nothing checked

- **No uniqueness check on open-question ids existed anywhere.** The derivation test in
  `tests/test_wp46_packs.py` parsed the register with `re.findall` and collected the result into
  a **`set`** — two entries both numbered 78 collapse to one member and the assertion passes.
  The guard against the exact failure this project suffered four times was structurally
  incapable of seeing it.
- **`PLAN-OF-ACTION.md` §1's "Ids are stable and never reused" enumerated *style, slot, room,
  grouping, parti, fault, pack*** and omitted open questions and work packages. That omission is
  why four block renumbers felt permissible: nobody thought a rule was being broken.
- **CI already had the only place a cross-branch collision is detectable before it lands** —
  `pull_request` gives both `github.base_ref` and the head — and nothing used it.

---

## What was built

**The register is a directory.** `docs/open-questions/<nnn>-<slug>.md`, 98 files, filename ==
id. The migration was written to prove itself: it reassembles the original register from the
split pieces and compares byte for byte before writing anything, and it round-tripped
**291,341 characters identical**. Three shapes in the source had to be read rather than assumed,
and each broke a first attempt — a section is not "heading, entries, trailer" (`From the
proportion layer` puts twenty lines of prose *before* its entries); two continuation lines are
not indented (one is a hard-wrapped sentence inside entry 47, one opens two conversion tables
that belong to the section and not to entry 71); and the ids are not in ascending file order.

Two transformations, and nothing else touched the text: the leading `N. ` is dropped, because
the id is the filename now and stating it twice is how two copies come to disagree; and
continuation lines are dedented, because four spaces inside a list item is a continuation and
four spaces outside one is a **code block**, which would have rendered half the register as
source. Every layered `*Original entry follows.*` history survives verbatim.

**`build/check_ids.py`**, wired into `check_all.py` and therefore into CI. It holds filename,
heading and status to each other; **it fails on a duplicate id**; it fails on a status word
outside a named vocabulary rather than assuming an unclassified entry is settled; it fails on
two work-package reports sharing a slug; and it fails on any `docs/reports/…md` path cited
anywhere in the tree that does not resolve.

**`build/gen_open_questions.py`** regenerates `docs/open-questions.md` as an index — 128 lines
instead of 760 of wall-of-text, open questions first. `--check` fails if the committed index has
drifted, which is the guarantee `dist/taxonomy.json` needed and did not have when seventeen
tests read it as though it were source.

**A CI gate that fires before the merge, not after it.** The directory is most of the fix but
not all of it: two sessions issuing id 99 with **different slugs** create two different paths, so
git merges both without a conflict. The new step compares the branch's id set against
`github.base_ref` and fails the second pull request to issue an id, naming it. PR #14's
successor — the fourth collision — would have been caught here.

**§1 amended.** Open questions and work packages are on the never-reuse list. The merged-first
rule, applied four times by convention and written down nowhere, is written down. And the
habit itself is named: *issuing an id: never by reading the working tree.*

## OQ 90, executed

**This branch's chain moved: WP-5.7 → 5.11, 5.8 → 5.12, 5.9 → 5.13, 5.10 → 5.14. Main's atlas
keeps 5.7.**

5.8, 5.9 and 5.10 name one package each and converted mechanically — 9, 63 and 45 references.
**WP-5.7's 87 did not**, because two packages shared the number and a `sed` would have corrupted
half of them. Every reference was attributed by `git blame` to the commit that wrote it
(`7beb40a`/`529310c` and the chain after them are the geometry package; `958276b`/`2c77499` the
atlas), and the sixteen written by later commits were read one at a time. The single genuinely
unclear one was the check-count claim — *"the CHECK figure said 32 against a suite of 33 until
WP-5.7 read the total"*, in `CLAUDE.md`, `build/check_all.py` and `tests/test_counts_guard.py`.
`7beb40a` is the only WP-5.7 commit that touches `check_all.py`, so it is the geometry
package's. **Final split: 53 moved, 21 stayed.**

### The entry's own preferred option was refused, because its premise was false

OQ 90 offered three options and leaned on the third: *"rule that work-package numbers are labels
rather than identifiers, cite the report always, and stop pretending the number is unique —
which is what is true today and would cost nothing but an admission."*

It was not true today. `wp-5.8-the-four-rulings.md` and `wp-5.10-the-four-rulings.md` were
**different packages with identical slugs**, distinguished only by the number the option said to
stop relying on. Citing the report did not disambiguate them and never had. Both now say which
four rulings they carry, and the checker fails the build on two reports sharing a slug.

## What was found on the way

- **A report filename `wp-2.3-real-solver.md` has never existed.** It was cited under
  `docs/reports/` in `STATE-OF-THE-PROJECT.md` and `CHANGELOG.md`; the file is
  `wp-2.3-the-real-solver.md`. (Written without its directory here on purpose — the new check
  reads paths out of prose, and an example of a broken path is still a broken path.) Fixed,
  and the checker now catches the class — which is OQ 90's own fallback failing one layer out.
- **The status legend was stale**, naming two of the ten words in use. The index now prints the
  whole vocabulary from `check_ids.py`, so it cannot go stale separately.
- **Phases 6 and 7 have reports and no `PLAN-OF-ACTION.md` sections.** Its `###` headings stop at
  WP-6.3, so WP-5.9, 5.10, 6.4 and 7.1–7.5 — eight packages — have no section for a report to
  match. Named, not fixed: it is a documentation package, not this one.
- **The check total moved 36 → 38 and the test total 1,071 → 1,081**, and
  `tests/test_counts_guard.py` failed on the first run rather than a reader noticing later. That
  guard has now earned itself at every single merge that moved these numbers.

## What was deliberately not done

- **No open-question id was renumbered.** Four renumbers is enough, and §1 now forbids a fifth.
- **The status vocabulary was not extended.** Ten words were measured in use; anything else fails
  the build and gets classified by a person.
- **The `wp-<id>-<slug>.md` ↔ plan-section correspondence is not enforced**, because eight
  packages would fail it immediately. Counted and named above instead.

## Verifying

```
python3 build/check_ids.py
python3 build/gen_open_questions.py --check
python3 -m pytest tests/test_open_question_ids.py       # 10 tests, mutation-checked
python3 build/check_all.py                              # 38 checks
```

`tests/test_open_question_ids.py` plants a duplicate id and requires the checker to name it,
mutates a status word to one outside the vocabulary and requires the same, and asserts the
derivation test no longer carries its own copy of that vocabulary — the duplication that let
`check_inheritance.py`'s `RATCHET` drift stale-high while its own comment claimed the test
imported it. Each of those was run against the unfixed code and confirmed to fail.
