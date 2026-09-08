# oq/a-source-that-agrees-numerically-may-be-the-wrong-quantity — the guard compares numbers and cannot compare meanings

*Status: OPEN · Raised in: WP-11.4, executing Ruling A (5 Sep 2026)*

**OPEN — a mechanism, and it is OQ 48's own problem arriving one layer up.** Ruling A let a
`measured` kit parameter cite a survey measurement, and `check_precedents.py::kit_source_agrees`
holds the parameter's number against the measurement's `value` in the same `unit`, in three verdicts.
That closes the trap the ruling's own entry named — *"a source pointer that resolves is not a source
that agrees"*. It does not close the one behind it.

**A `unit` is not a `quantity`.** `ft`, `in`, `count`, `ratio`, `deg`, `rise_in_12` say what KIND of
number it is and nothing about WHAT WAS MEASURED. Two figures in `count` may be a chimney count and a
storey count, and the checker will call them agreed if the numbers overlap.

**Found while writing the test for the ruling, and the way it was found is the argument.**
`tests/test_research.py::test_the_unsourced_count_falls_when_a_figure_gains_a_source` needed one
unsourced `measured` parameter on `tidewater-georgian` to point at one Westover measurement. **There
is no semantically matching pair on that node**: Westover's survey states a bay count, a storey
count, a chimney-stack count, a dormer count and a sash-light count, and the node's only numeric
unsourced `count` parameters are `steps_and_stoop.riser_count_from_grade`, `hearth_position.count`
and `hearth_position.fireplaces_per_stack`. The test uses `fireplaces_per_stack` [2, 4] against
`chimney_stack_count` 4 — **two different quantities sharing a number and a unit** — and the guard
passes it. The test says so in its own docstring rather than hiding it.

**The corpus already has the field this wants.** OQ 48 gave every pack rule a `quantity` naming what
it measures, precisely because two rules at one address meaning different things is a silent
corruption. `measurements[].name` is that field here in all but name — `overall_width_ft`,
`wall_thickness_in`, `chimney_stack_count` — and the schema's own description says it is *"the
corpus's measurement vocabulary where one fits"*. Nothing holds a kit parameter's identity against
it.

**Three options.**
1. **A `quantity` on the kit parameter, checked against `measurements[].name`.** Strongest, and it is
   the OQ 48 remedy applied unchanged. The cost is a new field on 1,161 `measured` parameters, of
   which six are cited today — so it would be authored almost entirely for figures nobody cites yet.
2. **A NAME-SIMILARITY warning**, not an error: flag a citation where the parameter key and the
   measurement name share no token. Cheap, catches `fireplaces_per_stack` against
   `chimney_stack_count` only weakly (both carry "stack"), and a warning nobody must clear is a
   warning nobody reads.
3. **Leave it to the reader and say so.** The six citations were each adjudicated by hand and each
   carries a `note` arguing the pairing. At six, a reader is the right instrument; at six hundred it
   is not.

Recommended: **(3) now and (1) at the threshold** — with the threshold NAMED rather than left to
feel, because "we will do it when there are enough" is how a guard never gets built. Twenty cited
figures is a reasonable line: below it every citation has been read by somebody, above it nobody has
read them all. **Do not adopt (2)**: a similarity heuristic that passes the very pair that raised the
question would be a guard that cannot fire, which this corpus has shipped four times and caught four
times.

**And a second, smaller finding from the same hour.** `tidewater-georgian.roof_pitch.pitch_typical`
is `kind: measured`, `unit: rise_in_12`, and its `value` is the STRING `"8:12"`. No comparison can
reach it: `kit_source_agrees` returns could-not-compare, correctly, and would for every parameter
written this way. A measured figure whose value is not a number cannot be held against anything —
neither a survey, nor a fault test, nor a generator. Nobody has counted how many there are.
