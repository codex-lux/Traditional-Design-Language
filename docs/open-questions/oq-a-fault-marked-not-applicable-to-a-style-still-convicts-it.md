# oq/a-fault-marked-not-applicable-to-a-style-still-convicts-it — a severity that is not a severity

*Status: OPEN · Raised in: WP-16.1, the governing test (29 September 2026)*

**A fault's `severity_by_style` may say `not-applicable` for a style, and nothing reads it as
that.** The schema admits the value (`schema/fault.schema.json`, `severity_by_style[].severity`).
**156 (fault, style) pairs carry it, on 94 faults over 39 styles**, and each carries a `why` that
reads as a licence:

- *"A plain fascia and plain soffit are correct"* (`bed-mould-omitted`, craftsman);
- *"4:12 to 6:12 is the style's own band and its whole point."* (`truss-flattened-pitch`,
  greek-revival-american).

`core.check_measurements` judges the fault for that style like any other, and where a test fails
the fault is PRESENT. `build/plan_check.py` then files it at
`x["severity"] if x["severity"] in SEV_ORDER else "serious"`. `not-applicable` is not in
`SEV_ORDER`, so a fault the record calls not applicable to the style is filed as **serious**.

**Measured at the WP-16.1 tree, over the sixteen shipped plans placed on `engine="heuristic"`, it
convicts once:**

- `good-03-parlor-drawing-room-house` (greek-revival-american) carries *"The Truss Default: 22.6
  against between 33.7 and 39.8."* at serious.
- The same record gives greek-revival-american `not-applicable`, and the same conviction stands at
  `a4abb85`, so WP-16.1 did not cause it.
- Two shipped plans' styles carry such pairs at all: `good-01`'s shingle-style (21 faults, none
  judged, because the elevation does not draw that style) and `good-03`'s greek-revival-american.
- A second good-03 row moved at WP-16.1: `bed-mould-omitted`, also `not-applicable` for this
  style, went from clear to could-not-evaluate under R4. No other row does.

**The conviction comes from a test written for another style, and the record says so three
ways.** The failing test is `truss-flattened-pitch`'s secondary `roof_slope_angle_deg` between
33.7 and 39.8 degrees (8:12 to 10:12).

- It is scoped by `applies_to_styles` to `georgian-colonial-american`, `english-georgian` and
  `georgian-revival`. `core._test_applies` matches that list against the style's whole
  inheritance chain, and greek-revival-american's chain holds the first two, so the Georgian band
  reaches a Greek Revival house.
- The fault's own exception for greek-revival-american licenses exactly this pitch: *"4:12 to 6:12
  is correct and is the style's argument"* (18.4 to 26.6 degrees; the house is 22.6). Its bounds
  test, entablature depth over column height, is the governing test there under R4. It could not
  run, because nothing supplies the entablature depth.
- OQ 63 recorded this as remaining work on 24 Aug 2026: the fault's note asks for a per-style pitch
  substitution (*"Greek Revival 18.4-26.6"*), the ruling then was `applies_to_styles` rather than a
  band table, and *"the table is the remaining work"*.

**It is not a clean defect, and that is why it is a question.** The exception carries its own
bounds, and they say when the licence holds: *"The low pitch has to be paid for with a deep
entablature, one quarter to one fifth of the column height ... A 4:12 gable with a thin trim board
is not Greek Revival; it is a truss."* Read that way, the fault can be present on a Greek Revival
house, where the bounds fail. Read the severity way, it never is. The record states both.

**What must be ruled:**

1. Does `severity: not-applicable` mean the fault does not apply to the style? Then
   `check_measurements` reports it not applicable, and the style's own exception for that fault
   becomes a dead record.
2. Or does it mean the fault is not a defect within the licence's bounds? Then the severity field
   is the wrong place for that, and a failed bounds test needs a severity of its own.
3. Should a secondary scoped to a parent style reach a descendant whose own exception licenses the
   quantity it tests? `_test_applies` says yes by design (*"a test scoped to a parent still applies
   to its descendants"*). Here that puts the Georgian pitch band on a Greek Revival roof.
4. What severity does a fault filed against a `not-applicable` style carry until then?
   `plan_check`'s fallback to serious was written for a malformed severity, not for this.

**Not done in WP-16.1, deliberately.** That package's ruling (R4) is about when a fault is clear.
This question is about whether a fault applies at all. The 156 pairs are counted, the one live
conviction is named, and nothing is changed.

Re-derive rather than quote these figures:
- the pairs from `faults/*.json`'s own `severity_by_style`;
- the conviction from `tests/fault_clears.py`'s per-plan run, or `plan_check.check` on good-03
  placed on the heuristic.
