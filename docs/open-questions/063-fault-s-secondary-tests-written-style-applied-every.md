# OQ 63 — A fault's secondary tests are written for one style and applied to every style

*Status: CLOSED 24 AUG 2026 · Raised in: Ruled with the rest, 24 August 2026*

**CLOSED 24 Aug 2026 — `applies_to_styles` on a test, and six tests scoped. The sweep is six and not twenty, which is itself the finding.** An optional `applies_to_styles` list joins the test object in `schema/fault.schema.json`; **absent means every style the fault applies to**, so every existing fault stays valid. `mcp_server/core.py` filters the test list by it before evaluating, and a test for another style is **not run** rather than counted as passing — a test that is not for this house says nothing about this house.
**Measured: 17 of 129 styles could not return a clean plan under their own native diagram; it is 15 now**, and the two faults responsible for 11 of the findings — `truss-flattened-pitch` (9 styles) and `chimney-omitted` (2) — no longer fire on styles they were not written for.
**Only six of the twenty-four candidates were scoped.** Twenty-four secondary tests name a style in their own note, and scoping on that keyword would have been worse than scoping nothing: most name a style as *context* (`muntin-wider-than-its-date` — "Federal and Regency sit at the bottom of it"), as a *reference band* (`six-panel-door-everywhere`), or as **the very case the test exists to discriminate** — `frieze-as-fascia-board` separates a genuine Greek Revival frieze-band window from a collision, and scoping it to Greek Revival would remove the case it is for. The six that name a style as a SCOPE: the Tudor chimney-breadth ratio and the Prairie visual-mass test on `chimney-omitted`; the `PUEBLO REVIVAL ONLY, and inverted` parapet rule, which is the only test in the corpus that fails a house for being level and was failing every correctly-built Territorial and Mediterranean parapet there is; the New England Georgian cornice return band; the Georgian dormer-and-eave rule, which a Shingle Style eyebrow and a Craftsman shed dormer break by design; and the Georgian pitch band.
**Two things deliberately not done, both recorded rather than guessed.** (i) `truss-flattened-pitch`'s note asks for a per-style *substitution* — "Cape 36.9-45, Tudor Revival 39.8-53.1, Greek Revival 18.4-26.6, Craftsman 14-26.6" — and the ruling was `applies_to_styles`, not a band table. Those styles are now **unjudged** on pitch by that test rather than wrongly failed, which is the right direction and not the destination; the table is the remaining work. (ii) **The same pattern exists on PRIMARY tests**, and the mechanism already covers them because the field is on the shared test object — but scoping them is a data sweep over 209 faults, not six. The clearest example: `gutter-as-cornice` is `universal` and requires a 7 in cornice projection whose own note derives it from `facade-classical` at a 9 ft bay; a Cape's smaller bay gives 6.89 in, so a correct Cape cornice fails a classical threshold by an eighth of an inch. The *fault* is universal and its *number* is not. That sweep wants its own package. *Original entry follows.*<br><br>**A fault's secondary tests are written for one style and applied to every style.** Found under OQ 37. `faults/chimney-omitted.json` carries two `secondary_tests` whose own notes name their scope explicitly: *"The Tudor Revival rule — chimney breadth at least one sixth of the elevation it stands on"* and *"The Prairie test. If the chimney is not the visually heaviest object present, the composition has been inverted."* `mcp_server/core.py::check_measurements` runs every test in `[test] + secondary_tests` against every style the fault applies to, and a fault is present if **any** of them fails. So a Cape Cod colonial is failed for not having a Tudor chimney. That is three of the four fatals `cape-cod-colonial` produces for **every** parti composed for it — the style cannot currently return a clean plan under any diagram, and the reason is not in its own data. `severity_by_style` and `exceptions` both exist and are honoured; neither scopes a *test*. The concrete proposal: an optional `applies_to_styles` on a secondary test, absent meaning all — which keeps every existing fault valid and lets the two chimney tests say what their notes already say. The alternative is to promote them to faults of their own, which is more honest about them being different claims but costs two new ids and a re-check of everything citing `chimney-omitted`. Needs a ruling; measured impact is at least one style unable to produce a clean plan, and the count is not known until the whole fault corpus is swept for the same pattern.

**AMENDMENT — WP-14.5 (20 Sep 2026): ONE SENTENCE OF THIS ENTRY WAS FALSE, AND THE DEFERRED TABLE
WAS NEVER A RESEARCH PROBLEM.** Deferral (i) says the styles the scope removed are *"now UNJUDGED
on pitch by that test rather than wrongly failed"*. Measured over the 41 styles the elevation
layer speaks for: **15 supply a pitch at all, 10 of those failed the Georgian band, and the scope
removed 3 — leaving SEVEN still wrongly failed**, every one of them on a pitch INSIDE the band its
own style node states (`greek-revival-american` and `greek-revival-northern` at 22.6 in 18.4–26.6,
`italian-renaissance-revival` at 18.4 in 14.0–22.6, `jeffersonian-classicism` at 18.4 in
at-most 18.4, `minimal-traditional` and `neoclassical-revival` at 22.6 in 18.4–26.6,
`new-england-federal` at 30.3 in 26.6–33.7). The cause is that `_test_applies` matches against the
KIT CASCADE, so three Georgian ids reach **77 of 164 styles** —
`oq/a-test-scope-is-matched-against-the-kit-cascade`, which is this entry's mechanism measured
rather than assumed.

**And the table deferral (i) called "the remaining work" was derivable all along.** 48 of 164
styles carry a migrated `roof_pitch_rise_per_12` constraint, `build/elevation.py` DERIVES the
`roof_slope_angle_deg` this test reads from that same constraint — measured, a style supplies a
pitch exactly when it states a band, 15 and 15, 26 and 26 — and four of the five bands the note
names reproduce from those constraints to a tenth of a degree. The Georgian band itself is
`georgian-colonial-american.c02` transcribed. The two halves already met in one place and the
fault was judging one against another tradition's band.

WP-14.5 executed the substitution the note asked for: `band_from_style` on the shared test
object, the band and its DIRECTION read from the style's own constraint, `threshold` and `upper`
refused by the schema, and a style stating no constraint NOT RUN rather than falling back. Seven
false convictions gone, 0 added; one shipped plan moves (`good-03-parlor-drawing-room-house`,
serious 23 → 22) and a second (`good-05-lobby-gallery-mansion`) loses a hidden second failing test
no surface was printing. The fifth band is NOT closed and is recorded rather than invented:
`tudor-revival`'s constraint is `at-least 10:12`, open above — its 39.8 lower reproduces and the
note's 53.1 upper is in no record in this corpus.

**Deferral (ii), the primary sweep, is measured and mostly REFUSED.** 0 of 210 primary tests carry
`applies_to_styles` and none was given one. Over the 41 judged styles the census finds 944
conviction rows, of which **17 rest on a threshold the corpus already states per style** — and
after the pitch substitution those 17 are two faults, neither of which may be scoped:
`pitch-below-material-shed-limit` states a floor per MATERIAL and not per tradition
(`oq/the-material-shed-limit-runs-every-material-against-every-house`), and `raised-cape-eave`'s
band is type-defining and contradicts nine styles including two of its own
(`oq/the-cape-pitch-band-contradicts-nine-styles-own-bands`). The other 927 rows have no second
number anywhere in the corpus and are reported, convicting nothing.

**And `gutter-as-cornice`, the example this entry names, turns out not to be a live case at all —
which only running it showed.** Its primary is a plane-change COUNT and it is CLEAR on 40 of the
41 judged styles; the single conviction is `minimal-traditional`, on an exception's `bounds_test`
about casing width, and not on the cornice projection. The 7 in figure this entry quotes is
`secondary_tests[0]`, its own note derives it from `facade-classical` at a 9 ft bay, and no style
in this corpus states a cornice projection to substitute. So the argument stands as an argument
and the instance does not stand as an instance. Re-derive; do not re-read.
