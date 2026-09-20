# oq/the-material-shed-limit-runs-every-material-against-every-house — a slate floor on a wood-shingle roof

*Status: OPEN · Raised in: WP-14.5, the fault is universal and its number is not (20 Sep 2026)*

**OPEN — `faults/pitch-below-material-shed-limit.json` states two roof-pitch floors, one for
lapped wood shingle and one for slate or flat tile, and runs BOTH against every house at once.**
Its own primary note says what it means:

> "6:12, the floor for a lapped wood-shingle roof laid at not more than one third of its length
> to the weather. **Apply the material's own historic minimum, not the code's**: wood shingle
> 26.6 deg, wood shake 26.6, slate 33.7, flat clay tile 40."

and the very next test is the slate floor of 33.7, with no precondition of any kind. So a house
roofed in wood shingle at 30.3 deg passes the floor its material requires and is convicted by the
floor for a material it does not have.

**This is `truss-flattened-pitch`'s defect one axis over — a test written for one material run
against every material — and it is a genuinely different axis, which is why it is a separate
question.** A pitch band is a fact about a TRADITION and is substitutable from the style node
(WP-14.5 did that). A shed limit is a fact about a MATERIAL and is physics: a lapped shingle roof
below its natural slope leaks whatever tradition built it. **Substituting the style's own pitch
band here would be lowering a threshold to make a style clean**, which WP-14.5's own plan forbids
in as many words, so the substitution mechanism must NOT be reached for.

**The corpus can already say which material, and this fault reads none of it.** `roof_material`
is an ontology slot and **99 of 164 styles resolve a canonical value for it** — 29
`wood-shingle`, 16 `plain-clay-tile`+`slate`, 13 `slate`, 11 `plain-clay-tile`, 7 `pantile`, and
a tail. `cape-cod-colonial`'s is `["wood-shingle"]` with the rule *"Side-gable roof of wood
shingle (own defining characteristic #4)"*.

**Measured, over the 41 styles the elevation layer speaks for**, holding one plan and swapping
the style label: 14 convictions on `roof_slope_angle_deg`, of which **8 are on the slate floor
(33.7), and 4 of those 8 are styles whose own kit makes wood shingle canonical and names no
slate**:

    greek-revival-american    22.6 deg  against at-least 33.7   canonical roof material: wood-shingle
    greek-revival-northern    22.6 deg  against at-least 33.7   canonical roof material: wood-shingle
    jeffersonian-classicism   18.4 deg  against at-least 33.7   canonical roof material: wood-shingle
    new-england-federal       30.3 deg  against at-least 33.7   canonical roof material: wood-shingle

A fifth, `minimal-traditional`, states no canonical roof material at all and is the case that
must NOT be read as a pass: a house whose material is unknown cannot be judged by a
material-specific floor, and *unjudged is not passed*.

**`new-england-federal` is the clean instance**: 30.3 deg clears the wood-shingle floor of 26.6
and fails the slate floor of 33.7, on a house the corpus says has a wood-shingle roof. The other
three fail both floors, so the conviction stands and only the second row is false — and that
second row is invisible, because `plan_check` prints only the first failing test
(`oq/a-fault-present-finding-names-one-of-its-failing-tests`).

**Two things must be ruled before anything is built, and they are Lucas's:**

1. **What is a test preconditioned on a canonical SLOT VALUE?** `applies_to_styles` preconditions
   on a style, `applies_when` on a measurement, `granted_when` on a construction context. None of
   the three reads a resolved kit slot, and a material is not any of those things. A fourth
   precondition axis is a schema change and it deserves to be designed once rather than four
   times.
2. **Where do the per-material minimums live?** Today they exist in one sentence of this fault's
   own prose. Transcribing that sentence into a table would be authoring numbers from a note —
   which is what `truss-flattened-pitch`'s band table turned out NOT to require, because the
   style nodes already held those figures. **Nothing in this corpus states a roofing material's
   minimum slope as a record.** So this one is not derivable the way the pitch band was, and the
   honest answer may be that the table has to be authored with a source, `kind: editorial`, or
   not at all.

**Do not close it by scoping the slate test to the slate styles by hand.** That is the 48 copies
argument in a smaller coat: a list of style ids inside a fault is a second spelling of
`roof_material`, and it goes stale the moment a kit moves.

**Related:** `oq/a-test-scope-is-matched-against-the-kit-cascade` (the scope this fault would
reach for, and why it is the wrong instrument here) and
`oq/a-fault-present-finding-names-one-of-its-failing-tests` (why the four rows above are invisible
on every surface a reader opens).
