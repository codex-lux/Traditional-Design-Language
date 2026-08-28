# WP-8.1 — a citation you cannot find is a citation you cannot renumber

*28 August 2026. One commit. Raised by Lucas, from a screenshot of a merge-conflict banner —
the package exists because chasing that conflict turned up something else.*

---

## What this package is

The open-question register has collided across parallel sessions **four times in four days**.
Each collision is followed by a renumbering pass over the whole tree, and every pass so far —
mine and, independently, the dormer/geometry session's — has been a regex of the shape
`\bOQ (7[89]|8[0-5])\b`.

**That regex cannot see the second number in a list.** Given `(WP-7.4, OQ 82 and 84 CLOSED)`
it matches `OQ 82`, renumbers it, and leaves `84` exactly where it was, because `84` carries no
`OQ` prefix and is not a citation as far as any tool in this repository is concerned.

The result is the most dangerous shape a wrong reference can take: **the stale number still
names a real entry.** Nothing dangles. No existence check fires. The sentence reads perfectly
and points at the wrong question.

---

## What was found

Three live instances were on `main`:

| file | said | should say | whose |
|---|---|---|---|
| `PLAN-OF-ACTION.md:19` | `OQ 95, 79 and 78` | `OQ 95, OQ 92 and OQ 91` | mine |
| `CLAUDE.md:286` | `OQ 95 and 84` | `OQ 95 and OQ 97` | mine |
| `PLAN-OF-ACTION.md:589` | `OQ 78, 73, 74` | `OQ 78, OQ 79 and OQ 80` | **another session's** |

**The third is the one that makes this a class rather than a slip.** Main's own WP-5.7 report
cites OQ 78, OQ 79 and OQ 80 correctly; only the progress-board line was missed — by the same
mechanism, in a different session, on a different branch, four days apart. Two independent
people wrote the same regex and both were bitten by the same blind spot in it.

Measured on `b155861`: **1,502 OQ citations, 0 dangling, 22 genuine bare-continuation lists
across 6 files.**

---

## The trap in building the detector, which cost a wrong number before it cost anything else

The obvious detector over-reports by **3x**, and I hit it while measuring rather than while
designing. A naive `OQ \d+((,|and) \d+)+` returns **68** hits. Forty-six of them are dates:

```
"OQ 18, 24 Aug 2026: reclassified from ..."      <- a citation followed by a DATE
"OQ 68, 26 Aug 2026). The band the author ..."
```

Those are correct prose, and they run right through the kit files. A checker that convicts 46
correct lines is turned off within a day, which is this repository's own `load.py` lesson in a
new place: **an instrument that misreports is worse than no instrument**, because its output is
a number rather than a red tick. The detector refuses a continuation number followed by a month
name, and `tests/test_citations.py` pins the three real date forms as explicitly allowed so a
future tightening cannot quietly start convicting them.

I reported "68 instances" out loud before checking them. The corrected figure is 22. Recording
that here rather than quietly shipping the right number is the point of the discipline.

---

## What was built

**The three citations are corrected**, and the 22 bare-continuation lists are normalised so
that every cited id carries its own prefix: `OQ 47, 48 and 49` became `OQ 47, OQ 48 and OQ 49`.
That normalisation is the change that does the actual work — after it, *any* future renumbering
regex finds every citation, because there is no longer such a thing as an unprefixed one. 63
continuation numbers were prefixed and the set of (file, cited id) pairs was compared before and
after: **identical except for the three intended corrections**, which is the only way to know a
cosmetic pass was cosmetic.

**`build/check_citations.py`**, wired into `check_all` (37 checks now), with three checks:

- **A — every `OQ N` names an entry that exists.** 1,570 citations, 0 dangling. This is a
  ratchet and **it would have caught none of the three bugs**, because every wrong id named a
  real entry. The module says so in its own header and `test_citations.py` asserts that
  sentence is still there, because a checker that implies coverage it does not have is worse
  than one that admits the gap.
- **B — no bare continuation number.** The load-bearing check; month-aware per the trap above.
  `--fix` inserts the prefixes.
- **C — reissue-table integrity.** Every conversion row must land on an id that exists, and no
  two rows in one table may land on the same id. The tables are the only thing that makes a
  pre-merge commit message readable, so a row that lands nowhere is a broken audit trail.

Each check was verified to fail with its target reverted: restoring `OQ 95 and 84` fires B at
`CLAUDE.md:286` by name; `OQ 999` fires A; a row pointed at 911 fires C.

---

## Two things the tests found that the plan did not anticipate

**The register records its four collisions in two different forms.** My first version of
`test_the_four_collisions_are_all_still_recorded` counted `## Reissued ...` headings and found
three: the third collision's table sits under a bold `A THIRD PARALLEL-SESSION COLLISION`
paragraph instead. All four mappings are present and correct; only the presentation is
inconsistent. The test counts **tables**, by contiguous runs of mapping rows, rather than
headings — pinning the heading would have pinned a house style nobody agreed to and would break
the moment someone tidied it. The inconsistency is recorded here rather than silently fixed.

**Two guards are in tension on exactly one line, and nothing said so.**
`test_wp46_packs.py`'s derivation test reads CLAUDE.md's open-question list with the character
class `[\d, ]+`, so that list must be **bare** numbers. Check B forbids the opposite — a bare
number after an `OQ N` citation. They coexist only because the tally line carries no `OQ`
prefix at all, so check B's anchor never engages on it. Anyone tidying that line into
`OQ 7, OQ 8, …` would be following the instinct check B teaches, and would break the derivation
test. That is now pinned by a test that says it out loud.

---

## What this deliberately does not do — and the new open question

**It does not stop collisions.** Ids are still issued from the working tree, which is the actual
cause. This package makes the *aftermath* of a collision mechanically complete; it does not
prevent one, and the checker's header says that rather than implying the problem is solved.

**OQ 99 IS NOW CLOSED, RULED AND EXECUTED IN THE SAME PACKAGE** — Lucas said go ahead, and
costing the three candidates collapsed them. **The numbers are frozen at 99 and every new
question is named** (`### oq/<slug>`); `check_citations.py` refuses a numbered entry above the
ceiling, so the mechanism that collided four times is unavailable rather than discouraged.

The measurement that decided it: **nothing in the codebase parses an OQ id.** All 1,640
citations are human references in prose and comments, and only two things read the register
structurally. So a full renumber was *possible* — and pointless, because commit messages carry
the old numbers and cannot be rewritten. **A uniform scheme was never on the table**; the only
choice was which inconsistency to keep, and two namespaces is cheaper than 1,640 rewritten
citations plus a history that still disagrees with them. An out-of-tree registry has no shared
state to live in but the repository itself, so its claim step collides identically; reserved
blocks need the same coordination or produce sparse meaningless numbers.

Closing it opened one honest successor, `oq/two-id-namespaces`, which is also the first entry
under the new scheme: a slug can restate a numbered question's subject and **nothing can tell**,
because WP-8.1 established that no machine can verify a citation's subject matches its entry —
the same argument one level up. Quieter than a collision, since there is no duplicate id to make
it visible. A subject index over the 99 legacy entries would help and is unbuilt.

*The original entry, before the ruling, named three candidate mechanisms and none costed:*
an out-of-tree registry, a reserved block per session, or slugs (`oq/span-partial-bearing-wall`)
— the last being the only one that makes the ambiguity impossible rather than unlikely, and also
the only one that invalidates 1,570 existing citations and every reference in the commit history.
It wants a ruling, not an afternoon.

**Raising OQ 99 is itself an instance of the problem**, and the entry says so: its id was taken
by reading the highest number in this working copy. If another session is open right now, this
is number 99 there too, and the fifth collision is already written. That is not a joke at the
register's expense — it is the argument in the smallest available form.

Also not done: no semantic check that a citation's *subject* matches the entry it names. It
cannot be done honestly by a machine — all three wrong ids named real entries — and a check
that pretended to would be "unjudged reported as passed" in a new place. The four conversion
tables were left in prose rather than converted to a machine-readable format; check C parses
them as they are, and converting them would damage the historical record they exist to preserve.

---

## Verification

`All 37 checks passed`, exit 0, run locally with every optional dependency present so nothing
was skipped into a pass. `check_counts.py` 24 claims, 0 stale. The register guard still derives
CLAUDE.md's open list from the file: **99 entries, no duplicate id, no gap, 34 open, no
unrecognised status word.** `check_citations.py`: 1,570 citations, 26 reissue rows, 0 faults.

The counts guard added in WP-7.5 fired twice during this package — once when the new check took
`TOTAL_CHECKS` 36 → 37, and again on the test count — which is the second and third time it has
earned itself since it was written, both at the exact moment the number would otherwise have
gone stale.
