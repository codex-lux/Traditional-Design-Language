# oq/a-held-shape-pin-is-not-held-on-the-hard-only-path — the record says every proportion pin held, and two did not

*Status: OPEN · Raised in: WP-11.15, the phantom storey the disclosure invented (8 September 2026)*

Found in ordinary work: a full `check_all` came back with one failure, and the failure was not
the package's.

`tests/test_shape_pins.py::test_no_room_is_drawn_outside_its_own_band_when_the_pins_hold` fails
**about one run in four**, on `engine="auto"`, on the **pristine tree**. It is not a new defect
and it is not caused by anything WP-11.15 touched.

## The measurement

Sixteen runs of that one test, alternating trees to control for machine load:

| tree | runs | failures |
|---|---|---|
| pristine (`85ba5e0`, no WP-11.15) | 8 | **2** |
| working (WP-11.15 applied) | 8 | **2** |

The same rate on both. WP-11.15's own change cannot reach the placement: its three call sites are
`_disclose_spans` (which runs *after* the solve), `structure.build_section` and `export_ifc`, and
on a one-rectangle house — which `tidewater-georgian-careful` is, untagged —
`elements_on_level` returns exactly what the comprehensions it replaced returned.
`CORPUS_PLACEMENT_SHA` and `CORPUS_OPENINGS_SHA` are both unmoved.

## The discriminator is the solver status, not the machine

Captured over five solves of the shipped Tidewater record:

| solver status | verdict |
|---|---|
| `FEASIBLE — kept polish from the heuristic hint` | passes (4 of 5) |
| `OPTIMAL (hard-only) — kept hard-only phase A` | **fails** |

On the failing solve:

| room | level | declared | drawn | ratio | band ceiling |
|---|---|---|---|---|---|
| `chamber2` | 1 | 224 sf | 234 sf | **1.38** | 1.35 |
| `chamber3` | 1 | 208 sf | **315 sf (+51%)** | **1.40** | 1.35 |

and **`downgraded_shape_pins` is EMPTY**. That is the whole question. The record states that every
proportion pin held, and two rooms are drawn outside the band those pins assert. A reader — and
`plan_check`'s drawn layer, and the critique — has no way to tell this from a placement in which
the bands really did hold.

## What is established, and what is not

**Established.** `_absorb` is not the grower. It is called once, with
`ratios=` populated from `GEO.shape_band()` for every room whose pin was not downgraded, and its
`_fits` test would refuse 21 × 15 against a 1.35 ceiling (the limit is 15 × 1.35 + 0.01 = 20.26).
So the hard-only phase A placement already had `chamber3` at 21 × 15.

**NOT established, and it is the first thing to check.** Whether the phase A model asserts the
shape pin at all. If it does not, then nothing was *downgraded* because nothing was ever
*applied*, and the empty `downgraded_shape_pins` is honest about a question that was never
asked — which is **unjudged reported as passed**, in a new place, and the same family as
`_style_gambrel_geometry`'s `break_ok` that was `True` on all 164 styles forever. If it does
assert it, then a hard constraint is being violated and that is a much larger fact about the
model.

## AMENDED 9 SEPTEMBER 2026 — THE DISCRIMINATOR IS NOT THE SOLVER STATUS

Re-measured during WP-12.2's verification, when a full `check_all` came back `1 of 53 checks
failed` on this same assertion and the package had to establish whose failure it was. The
method is this entry's own: eight runs of the assertion, **alternating trees to control for
machine load**, `9aa3a35` (before WP-12.2) against the working tree after it.

| tree | runs | failures |
|---|---|---|
| `9aa3a35`, before WP-12.2 | 4 | **4** |
| working tree, WP-12.2 applied | 4 | **4** |

Identical on both, which settles the attribution: **the failure is not WP-12.2's.** Nothing that
package touches is in the placement path, and `tests/test_cp_elements.py` passed in the same
build — its four SHA pins cover the serialised `CpModel` proto for both shipped plans in both
phases, so the prover was handed a byte-identical model.

**AND THE TABLE ABOVE THIS SECTION IS FALSIFIED.** It says the discriminator is the solver status:
passing on `FEASIBLE — kept polish from the heuristic hint` (4 of 5) and failing on
`OPTIMAL (hard-only) — kept hard-only phase A`. **All eight of these runs failed, and all eight
were on the FEASIBLE-polish status** — the one the table calls passing. So the pin is not held on
the polish path either, and the entry's own slug, which names the hard-only path, is narrower
than the defect. The slug is NOT changed: ids are stable and never reused, and a slug that has
become too narrow is a smaller cost than a citation that stops resolving.

**The convicted population differs with the path, and that is the new fact.** The hard-only solve
this entry records convicted `chamber2` at 1.38 and `chamber3` at 1.40; every polish solve here
convicts `chamber3` alone, at the same 1.40 against the same 1.35. What survives both is the
central claim: **`downgraded_shape_pins` is EMPTY on all eight**, so the record goes on saying
every proportion pin held while a room is drawn outside the band those pins assert.

**The rate is a property of the machine and the day, and both figures are kept with their dates.**
WP-11.15 measured 2 in 8 on each tree on 8 September; this measures 8 in 8 on each tree on
9 September. Neither is the rate — quoting either as *the* frequency is the error this entry was
written to avoid, and what is stable across both measurements is that the two trees agree.

**What this changes in the questions below.** Question 1 asked whether phase A asserts the pin,
"which decides whether the below are one question or two". It is now established that the failure
does not require phase A at all, so a reading confined to `_finish_feasible`'s hard-only branch
cannot explain it. Question 4 — should the test name the status it is judging — is answered NO on
this evidence: naming the hard-only status would have made the suite green today while the defect
was firing on every single run.

## Why this was not fixed in WP-11.15

WP-11.15's guarantee is that the whole shipped corpus is byte-identical, and every plausible fix
here **moves a placement** on the hard-only path. A package that removes a false measurement and
moves a shipped placement has done two things, which is WP-11.9's own lesson and WP-11.13's
reason for deferring the record edit. It is also not WP-11.15's subject: that package is about a
span published over open sky, and this is about a proportion pin.

**Do not fix it by loosening the test.** The `+ 0.02` tolerance is already generous against
overshoots of 0.03 and 0.05, and three of this repository's guards have been re-cut for pinning
an outcome rather than a property — the opposite error, weakening a guard that is telling the
truth, is the one that costs a defect rather than an afternoon.

## What must be ruled

1. **Does phase A assert the proportion pin?** Read `_build(..., objective=False)` and the
   `_finish_feasible` path. This decides whether the below are one question or two.
2. **What should `downgraded_shape_pins` say when a pin was never asserted?** "Empty" currently
   means both *held* and *never applied*. Those are the evaluated-and-passed and the
   could-not-evaluate states, and the corpus's first rule is that they are not the same. A third
   value — or a sibling key naming the pins the phase did not assert — is the shape of the answer.
3. **Is `OPTIMAL (hard-only)` a placement this corpus should keep at all?** `_finish_feasible`
   keeps it whenever the polish times out. CLAUDE.md already records that on this plan
   "the CP objective cannot reach the drawing" for that reason, and this is a second cost of the
   same behaviour.
4. **Should the test name the status it is judging?** Reporting COULD NOT EVALUATE on the
   hard-only path would make the suite deterministic — but only honestly if (2) establishes that
   the pin really was not asserted. Doing it before that is hiding the defect, not reporting it.

## Related

`oq/the-placement-carries-no-wall-bands` is the other half of what a placement does and does not
state about shape. WP-11.7 is where the proportion pin became hard and where `_absorb` was given
`ratios`; its report records `_absorb` undoing a proof for the third time, and WP-11.11 the
fourth — **this is not a fifth**, and saying so matters: the post-solve pass is behaving, and the
placement it was handed was already out of band.
