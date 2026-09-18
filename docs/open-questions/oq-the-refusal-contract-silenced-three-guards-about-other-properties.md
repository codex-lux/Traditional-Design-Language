# oq/the-refusal-contract-silenced-three-guards-about-other-properties — and each now fails before it asserts anything

*Status: OPEN · Raised in: WP-13.7, the adversarial audit of Phase 13 (16 September 2026)*

**Lucas's 15 Sep ruling — a placement that breaks a hard fact of the type is REFUSED, not drawn
— reaches `corpus._placed` and `export_dxf.export_plan_dxf`. Three guards written for OTHER
properties run through those two doors, and all three now fail before they assert anything. The
properties they were written to hold are, today, tested by nothing.**

## The three, measured against a control

Each PASSES on a `git archive` checkout of `49e2389` (WP-13.2 complete, before WP-13.3 and
WP-13.4) and FAILS on `86bc607`. Three passed in 163.5 s on the control; on the merged tree:

| guard | what it was written to hold | how it fails now |
|---|---|---|
| `tests/test_proof_and_search.py::TestTheBenchRecordsWhatItDrewAndOnWhat::test_placed_records_the_surface_the_engine_asked_for_and_the_inputs_digest` | WP-11.8 finding J6 — `solver.drawn_by`, the surface, the engine asked for and the INPUT's digest | `KeyError: 'geometry_report'` |
| `…::test_the_digest_is_of_the_INPUT_and_two_different_records_differ` | that the digest is of the INPUT, so two sheets of "the same house" that disagree name the difference | `KeyError: 'geometry_report'` |
| `tests/test_ingest.py::test_tdl_sheet_short_circuits_to_the_complete_record` | that a complete record short-circuits to the DXF without re-deriving | `assert 'error' not in {...'unsolved': True, 'unexported': True}` |

The mechanism is one line. `corpus._placed` returns `refused_response(ref)` for a record whose
type facts are downgraded, and that response carries no `geometry_report`; `spec-builder-colonial`
has `bearing` and `stacks` downgraded on the deterministic engine, and `tidewater-georgian-careful`
has `bearing`, `hearth` and `stacks`. Both were drawable before the ruling.

**So WP-11.8's disclosure is no longer guarded at all.** Neither test reaches an assertion, so
`solver.drawn_by` and `input_digest` could be dropped from the record tomorrow and both would go
on failing in exactly the same way, with exactly the same message.

## Why this is a ruling and not a repair

WP-13.4's report says *"Pins were rewritten and not loosened"* and names `tests/test_solver.py`'s
25 Aug pin and two face tests in `test_drawing_set_one_building.py`. These three are not named
there, and the right re-cut for each depends on a contract decision nobody has taken:

1. **Does a refusal response carry `solver.drawn_by`?** It is a statement about what was HANDED
   to the solver, and it is just as true of a record the solver then refused. If it should, the
   two `test_proof_and_search` guards are restored by the record rather than by the test. If it
   should not, they must be re-cut onto a drawable record — and then they stop being about the
   two shipped plans, which is what they were written to be about.
2. **What should the DXF short-circuit guard assert now?** That a refused complete record is
   REFUSED (a different property from the one it was written for), or that a DRAWABLE complete
   record short-circuits (the original property, on a different plan)? Both are defensible and
   they are not the same test.

**Nothing here was re-cut**, because re-cutting a guard onto a different record or a different
property is authoring a claim about what the contract means, and the contract is Lucas's. The
measurement is published instead, with the control that establishes it.

## The general shape, which is the part worth keeping

A ruling that changes what a FUNCTION returns reaches every guard that calls it, including the
ones about something else entirely. WP-13.4 swept the surfaces the refusal is FOR and found
them; what it did not sweep is the guards that merely pass through the same door. The cheap
instrument is a full `pytest tests/` attributed against a pre-ruling control — which is how
these three were found, forty-eight minutes in.
