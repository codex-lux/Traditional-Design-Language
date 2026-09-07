# oq/fourteen-of-sixteen-plans-name-no-massing — every massing-gated check is silent on 87.5% of the plan records

*Status: OPEN · Raised in: WP-11.4, the hearth (4 September 2026)*

## The measurement

Fourteen of the sixteen plan records in this tree state no `massing` at all. Only
`plans/tidewater-georgian-careful.json` and `plans/spec-builder-colonial.json` name one, and both
name `gable-end-paired`. Every one of the fourteen in `plans/reference/` — the seven `good-*` and
the seven `bad-*` — has `massing: null`.

`massing` is an optional field on `schema/plan.schema.json` and always has been, so nothing is
malformed. What is worth ruling on is the consequence, which nothing publishes today: a check
written on the massing does not evaluate on 87.5% of the corpus's own plan records, and it does not
say so.

Three such checks were found by grepping every reader of a plan's own `massing`:

| reader | what it cannot judge without one |
|---|---|
| `plan_check.py`, grouping `attaches_to` | whether the plan's groupings attach to the massing they say they attach to |
| `plan_check.py`, style `massing_affinities` | whether the style holds this massing as canonical, common, or forbidden |
| `build/hearths.py` (WP-11.4) | where a flue may stand, so no room can be judged as missing a fire |

`build/roof.py` reads it twice more, and falls back to a default rather than reporting.

## Why it matters more than a missing optional field usually does

**The seven `good-*` plans are the corpus's own account of what a well-made plan looks like**, and
they are the fixtures a corpus-wide sweep runs on. A checker gated on the massing is therefore
exercised, in the whole test suite, by two records — both of one massing, out of forty in
`massings/catalog.json`. WP-8.11 met the same shape from the other end: a test fixture driving a
gate through a pack the corpus happened to leave unflipped was green and vacuous, and had to be
moved. Here the corpus itself is the vacuous fixture.

**And the silence has no name.** `hearth_report` publishes `readable: false` with the reason, which
is this package honouring *unjudged is not passed*. The grouping-attachment and massing-affinity
grouping `attaches_to` and style `massing_affinities` branches simply do not run: no finding, no census entry, nothing in
`drawn_summary` distinguishing "this plan's groupings attach correctly" from "nobody could tell".
That is the third state collapsing into the second, on fourteen records.

## What is NOT being claimed

**Not that the fourteen should be given a massing.** Several probably should not: a reference plan
exists to exercise one rule and a `massing` it does not need is a fact the author did not want to
assert. `bad-04-log-cabin.json` has five rooms and no business claiming a place in a
forty-entry catalogue of massing types.

**Not that this is a defect in any of the three readers.** Each behaves correctly on a record that
says nothing. The question is whether the corpus should be able to see that they said nothing.

## What must be ruled

1. **Does a plan's `massing` become required?** If it does, fourteen records need one authored, and
   the honest answer for some of them may be a new catalogue entry rather than the nearest fit —
   which is the authoring act `massing_hearth` refuses to perform for exactly this reason.
2. **Or does the plan layer gain an `unjudged` census for massing-gated checks**, the way
   `hearth_report` has one, so a check that could not run is counted rather than absent? This is
   the cheaper half and does not require a single new fact.
3. **Should `check_plans.py` report it?** That checker already holds a hand-authored plan to the
   parti it names and has an `EXPOSURE_CEILING`; a `massing`-stated meter would fit beside it, as
   a ratcheted count rather than a failure.
4. **Is a plan's massing derivable from its parti?** `partis/*.json` state a `massing`, and
   `check_plans.py` already compares the two where both exist. Deriving one where the plan is
   silent would make all three checks live — and would be inferring a fact the author declined to
   state, which is what this corpus calls laundering. It is listed here to be refused explicitly
   rather than to be discovered as a shortcut later.

## The trap, stated because it is predictable

**The cheap fix for the hearth layer specifically is to fall back to the parti's massing, and it
must not be taken alone.** It would take `hearths.py` from judging 2 plans to judging 16 and would
make every `absent` finding rest on a massing nobody authored. If the derivation is ruled sound it
belongs in one place that every massing reader consults, marked as derived, not in the file that
happens to want it first.
