# oq/a-fault-present-finding-names-one-of-its-failing-tests — 35 of 251 findings hide a second failure

*Status: OPEN · Raised in: WP-14.5, the fault is universal and its number is not (20 Sep 2026)*

**OPEN — `plan_check` emits ONE `fault-present` finding per fault and quotes
`(failing or results)[0]`, so where a fault fails on two tests the second reaches no surface at
all.** Measured over the sixteen shipped plans: **251 fault-present findings, 35 of them carrying
more than one failing test, and 35 failing tests that nothing prints.** Eleven of the sixteen
plans carry at least one.

The `[0]` is deliberate and its comment is right about what it fixed: it reads `failing` rather
than `results` precisely so a fault whose PRIMARY passes and whose SECONDARY fails does not print
the passing measurement as its own evidence — *"The House With No Fire: 2 against at-least 1"* on
a Cape with two chimneys. What it did not consider is a fault where two tests fail at once.

**The case that found it, and it is the sharp one: a false conviction can hide behind a true
one.** `good-05-lobby-gallery-mansion` is `italian-renaissance-revival` and carries
`truss-flattened-pitch` on two failing tests — the style-independent roof-to-wall ratio at 0.2509
against at-least 0.45, and the pitch band at 18.4 deg against between 33.7 and 39.8. The plate,
the findings list, the critique and every finding digest name only the first. WP-14.5 removed the
second (a Georgian band judging an Italian Renaissance Revival house whose own node states
14.0–22.6), **and a per-finding diff of all sixteen plans could not see the change**: the plan
moved, the row did not. It took a diff at the failing-test level to find it.

So the shape is exactly the one this corpus keeps meeting: a defect invisible in the surface a
reader looks at, because the surface aggregates. It is not a false pass — the fault really is
present on good-05 — it is that the reader cannot tell which of the corpus's claims about the
house they are being shown, and an instrument built to detect movement in the findings cannot
detect movement in the evidence.

**The 35, by fault (over the sixteen shipped plans):**

    lite-count-wrong-for-the-date        10      cornice-sized-off-the-attic           7
    ungraduated-storeys                   6      storeys-out-of-vertical-alignment     4
    one-bay-symmetry-break                3      pitch-below-material-shed-limit       2
    casing-at-a-third-of-palladio         1      transom-bar-at-the-wrong-height       1
    truss-flattened-pitch                 1

**Two of them fail twice on the SAME expression**, which is a different question wearing the same
shape: `good-03` and `good-05` each fail `pitch-below-material-shed-limit` on
`roof_slope_angle_deg` twice, because that fault states a wood-shingle floor of 26.6 deg and a
slate floor of 33.7 deg and runs both against every house —
`oq/the-material-shed-limit-runs-every-material-against-every-house`.

**The question is Lucas's:**

1. **One finding per failing test.** The honest reading of *"findings matter as much as code"*,
   and the cost is measurable and large: it moves every finding count, every finding digest, the
   composer's `counts` and its eight score axes, and `_axis_from_layers` takes the worst finding
   per room, so a second finding in a room that already carries one may cost nothing at all —
   which would make the change look free while changing the sheet.
2. **One finding, every failing test named in its statement.** Cheaper and smaller: the count
   does not move, the digest does, and a reader sees what the corpus actually said.
3. **Keep the `[0]` and publish the rest as evidence** beside `value` and `required`, where
   `critique` and the bench can read it and the printed plate need not change.

**Not changed in WP-14.5.** All three answers move a pinned digest and two move a score, and
picking one on a session's reading is the move this corpus refuses. What WP-14.5 did is publish
the number so the next reader is not measuring the wrong layer: **a diff of `plan_check`'s
findings is not a diff of the corpus's verdicts**, and any package measuring a change to the
fault layer must diff the failing TESTS as well as the findings.
