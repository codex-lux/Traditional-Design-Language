# oq/a-bare-gable-row-names-no-orientation — four styles make "gable" canonical and the roof layer cannot say which way it runs

*Status: OPEN · Raised in: WP-16.9, the roof, the rake and the deeper cornice (1 October 2026)*

**The `roof_form` id `gable` names a gabled roof and not its orientation, and four nodes make it
canonical: california-bungalow, craftsman, craftsman-bungalow and shotgun-house.** The closed table
B1 asked for (`build/roof_vocabulary.py`) maps it to no form. Its entry records why: roof.py's bare
gable takes its ridge on the y axis, so it is drawn exactly as a front gable, and mapping the id to
it would assign the front orientation to records that do not state one. So all four read
`undrawable` to the roof layer, and each plan of theirs that declares no roof falls to its massing's
default or the side gable, and says so.

**What each record says.** The table's own entry: *"Of the id's four canonical nodes, only
shotgun-house's record states front."* shotgun-house's defining characteristics include *"Gable end
turned to the street, with a full-width porch under or attached to the front gable"*.
craftsman-bungalow's canonical massing reads *"front-gabled and side-gabled subtypes are both this
massing with the ridge rotated"*.

**Why B1 does not reach it.** B1 corrects INHERITED roof records a style's words contradict.
shotgun-house's row is its own, so B1 does not reach it, and changing it to `front-gable` is a
record edit in its own words that no answer covers. california-bungalow and craftsman-bungalow
inherit craftsman's row, and nothing in their words contradicts it: craftsman's row says the gable
faces front or side, and craftsman-bungalow's massing note says both. Reading `gable` as
`side-gable` or `front-gable` everywhere would give three records an orientation they decline to
state.

**What is not ruled.** Whether a style whose own words state the orientation re-ids its row
(shotgun-house: front), and what a record that states both orientations draws (craftsman-bungalow:
B7's "several", or a declaration the plan must make).

## Amended 3 October 2026 (the audit of WP-16.8's own diff): a declared row is not read through the table

**The closed table reaches the KIT's row and not the PLAN's declaration.**
`threshold.roof_form_for` hands a declared `roof_form` to roof.py as written, and the plan schema
says a declared value is a bare variant id. So the two readers of one vocabulary disagree twice:
- `gable`, declared, is drawn: roof.py's bare gable, ridge on y, a front gable in all but name. The
  same id from a kit is undrawable (the table's entry, above).
- `hipped`, declared, draws no roof, and the sheet says its form is "one this generator does not
  draw". The same id from a kit is a hip.

Found while driving a test of the rake's reasons, by declaring forms the table maps. No shipped plan
reaches the second: the three shipped declarations are `gable` (bad-04) and `side-gable` (two).
The first is how bad-04 is drawn today.

**Not fixed, because the fix is this question's ruling.** Reading a declaration through the table
would make bad-04's declared `gable` undrawable. Keeping roof.py's bare `gable` for a declaration
keeps the orientation the table refuses to assign to a kit row. Either way, which way a bare gable
runs has to be decided first.
