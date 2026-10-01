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
