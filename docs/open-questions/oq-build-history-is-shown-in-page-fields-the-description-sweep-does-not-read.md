# oq/build-history-is-shown-in-page-fields-the-description-sweep-does-not-read — R6 reached the description, and the record pages print more than the description

*Status: OPEN · Raised in: WP-14.33's adversarial audit (26 September 2026)*

**The finding.** R6 of 26 September 2026 ruled that a description is for a reader. A work-package
number, an open-question number or slug, and a code span belong in the record's `note`.
`build/validate.py` sweeps every `description` a record page shows (466 of them) and refuses those
forms. The audit widened the forms to a repository path and a snake_case identifier.

**The same pages print other fields as their own prose, and nothing sweeps them.** Measured on
26 September 2026 with the sweep's own `HISTORY_FORMS`:

| Field | Shown by | Records | WP | OQ number | OQ slug | Code span | Path | snake_case |
|---|---|---|---|---|---|---|---|---|
| a room's adjacency `why` | `record/RoomBody.jsx` | 10 | 6 | 11 | 0 | 4 | 0 | 3 |
| a grouping's `internal_rules[].statement` | `record/GroupingBody.jsx` | 2 | 2 | 1 | 1 | 4 | 1 | 1 |
| a kit slot's `note` | the Style Dossier's slot panel | 99 kits | 31 | 40 | 0 | 159 | 42 | 563 |
| an exemplar's `why` | the Dossier's evidence | 39 styles | 1 | 0 | 0 | 131 | 2 | 7 |
| a declined pack's `reason` | the Dossier's proportions | 59 styles | 1 | 1 | 0 | 71 | 0 | 362 |
| a fault's `correct_practice` | the fault card | 5 | 0 | 0 | 1 | 0 | 0 | 4 |

The sharpest instance: `groupings/garage-and-hyphen.json`'s description was reworded twice to take
out a backticked `dependency-and-hyphen`. Its rules 2 and 3 print the same span on the same page.

**The snake_case column is not all build history.** A slot note that names a parameter
(`riser_count_from_grade`) is naming something a reader can find on the same panel, and the exemplar
`why` texts are written by `build/family_specimens.py`, which quotes node ids on purpose. So the
count is an upper bound on the defect, not a measure of it.

**Why it is a question and not a fix.** The ruling was given about `description`, and the fields
above are a different kind of prose: several are the corpus reasoning in its own words, and much of
it cites the questions it rests on. The readings:

1. **Extend the sweep to every field a record page prints**, and move each history into a `note`.
   That is R6 applied as written to more fields. It is a large data edit (over 250 records), and it
   takes the citations out of reasoning that was written to carry them.
2. **Scope R6 to `description` in so many words**, and have the pages print the other fields as a
   record's working, in a register that says so (a smaller type, a "the record's reasoning" label).
3. **Render the forms rather than remove them.** A code span drawn as code and an OQ or WP number
   drawn as a link to the register, so a reader sees them as references and not as noise.

**What was done meanwhile.** The docs that called the sweep "every description a record page shows"
are true of that field and were left saying so. Nothing else was moved, because moving 250 records
on one reading of a ruling given about another field is the move this corpus refuses.
