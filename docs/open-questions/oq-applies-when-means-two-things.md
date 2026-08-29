# oq/applies-when-means-two-things — one field name, two preconditions, three schemas

*Status: OPEN · Raised in: From WP-8.4, the exception precondition (28 Aug 2026)*

**OPEN — `applies_when` means a precondition on MEASUREMENTS in one schema and a precondition
on CONTEXT in two others, and WP-8.4 fixed the collision inside one file rather than the
corpus-wide one.**

Three fields carry the name today, and they are not the same mechanism:

| where | on what | populated | read by |
|---|---|---|---|
| `fault.schema.json` `test.applies_when` | MEASUREMENTS — expression, direction, threshold | 13 records | `core._eval_test`, `measurement_vocabulary`, `plan_check` |
| `kit.schema.json` `$defs.applies_when` | CONTEXT — date_range, regions, construction, climate_zones | 155 kit variants | `resolve_kit.filter_variants_by_date` reads `date_range` ONLY |
| `proportion-pack.schema.json` `derived_rules[].scope` | CONTEXT — construction, slot_variant | 3 rules | `proportion_engine.rule_scope` |

WP-8.4 renamed the fourth — `exceptions[].applies_when`, 331 records, read by nothing — to
`granted_when`, because two fields of one name inside `fault.schema.json` made "the guard
exists" and "the guard runs" indistinguishable to a reader, and that pair spent a year in
exactly that state. **That fixed the file and left the corpus.** After the rename the dominant
meaning of the surviving name is CONTEXT (155 records in `kit.schema.json`) and the minority
is MEASUREMENTS (13 in `fault.schema.json`), which is the opposite of how a reader arriving at
`fault.schema.json` will read it.

**The kit one is also half-read, which is the sharper half of this.** `resolve_kit` evaluates
its `date_range` and ignores its `regions`, `construction` and `climate_zones` — 15 variants
name a construction and 39 a region, and no code consults either. That is the same shape as
the exception precondition WP-8.4 just closed, one schema over, and it was found while
closing it.

**What a ruling would decide.** Whether the measurement precondition is renamed (13 records,
but every one of them live and load-bearing), whether the kit's context precondition is
renamed to match `scope`, or whether the corpus accepts one name with two meanings and says so
in both schemas. Doing nothing is a choice too, and it is the current one.

**Why it is not settled here.** Renaming the live measurement field touches `core.py`,
`plan_check`, `measurement_vocabulary`, four test files and the fault schema's own long note;
renaming the kit field touches 155 records and a reader that runs on every resolve. Neither is
a patch, and WP-8.4 had already changed the shape of the thing it was closing.
