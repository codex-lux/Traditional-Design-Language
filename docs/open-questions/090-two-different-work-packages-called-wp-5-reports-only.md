# OQ 90 — two different work packages were both called WP-5.7

*Status: CLOSED 28 Aug 2026 · Raised in: From the third collision (28 Aug 2026)*

**CLOSED 28 Aug 2026 — ruled: this branch's chain moves. WP-5.7 → 5.11, 5.8 → 5.12, 5.9 → 5.13,
5.10 → 5.14; main's atlas keeps 5.7.** By the rule the register has now applied to ids four
times — whoever merged first keeps the numbers, and it is never the side still on a branch. The
asymmetry this entry complained about (ids renumbered at the merge, work packages not) is gone.

**The entry's own preferred option was refused, because its premise was false.** Option (c) was
to *"rule that work-package numbers are labels rather than identifiers, cite the report always,
and stop pretending the number is unique — which is what is true today and would cost nothing
but an admission."* It was not true today. `wp-5.8-the-four-rulings.md` and
`wp-5.10-the-four-rulings.md` were **different packages with identical slugs**, distinguished
only by the number the option said to stop relying on. Citing the report did not disambiguate
them and never had. Both were renamed to say which four rulings they carry, and
`build/check_ids.py` fails the build on two reports sharing a slug.

**What it cost, measured rather than estimated.** 5.8, 5.9 and 5.10 name one package each and
converted mechanically (9, 63 and 45 references). WP-5.7's **87** did not: each was attributed
by `git blame` to the commit that wrote it, and the sixteen written by later commits were read
one at a time. **53 moved, 21 stayed with the atlas.** The one genuinely unclear reference was
the check-count claim in CLAUDE.md, `build/check_all.py` and `tests/test_counts_guard.py`;
`7beb40a` is the only WP-5.7 commit touching `check_all.py`, so it is the geometry package's.
Four report files renamed. Eight commit subjects still carry the old numbers and cannot be
changed — read them against the conversion table in `README.md`.

**Found while executing it:** a report filename `wp-2.3-real-solver.md` was cited under
`docs/reports/` in `STATE-OF-THE-PROJECT.md` and `CHANGELOG.md` and has never existed — the file
is `wp-2.3-the-real-solver.md`. (Written without its directory here on purpose: the new check
reads paths out of prose, and an example of a broken path is still a broken path.) `check_ids.py` now fails on any `docs/reports/…md` path cited
anywhere in the tree that does not resolve — the same defect one layer out from this entry's
own fallback.

**The cause is fixed rather than recorded this time.** Work packages and open questions are both
on `PLAN-OF-ACTION.md` §1's never-reuse list now, and the register is a directory: one file per
question, so two sessions issuing id 99 collide on a PATH git refuses to auto-merge instead of
inside a file git silently juxtaposes. *Original entry follows.*<br><br>**OPEN — two different work packages are both called WP-5.7, and the reports are the only thing keeping the citations apart.** The same two sessions that collided over open-question ids 72–83 collided over the work-package number, in the same three days, by the same mechanism: read the working tree, add one. The OQ block was renumbered at the merge and the work packages were not, and that asymmetry wants a ruling rather than a default. **Main's WP-5.7 is the atlas and the shell's proportions; this branch's is the geometry layer**, and this branch's WP-5.12, 5.9 and 5.10 chain off its own — WP-5.12 exists precisely to execute WP-5.7's rulings, so renumbering the geometry layer breaks a sequence and renumbering the atlas breaks nothing but is the side that merged first, which is the opposite of the rule applied to the ids. **Nothing is ambiguous today and that is the whole reason this can wait**: a work package is cited by its REPORT, never by its number alone, and `docs/reports/wp-5.7-the-atlas-and-the-shell.md` and `docs/reports/wp-5.11-real-2d-geometry.md` have always been distinct files. What a renumbering would cost is real and is why it is not being done in a merge commit: two report filenames, the `wp-<id>-<slug>.md` convention's match between a report and the section it reports on, CLAUDE.md, the progress board, and five commit messages that cannot be changed. Three options: rename main's atlas package (cheapest, contradicts the merged-first rule); rename this branch's chain 5.7–5.10 to 5.11–5.14 (consistent with the rule, four renames and a broken narrative order in the plan); or rule that work-package numbers are labels rather than identifiers, cite the report always, and stop pretending the number is unique — which is what is true today and would cost nothing but an admission. **The underlying cause is unchanged and is now three-for-three: an id issued by reading the working tree collides whenever two sessions run at once.** Neither this entry nor the two before it fixes that.
