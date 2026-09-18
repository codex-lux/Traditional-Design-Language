# oq/the-front-door-is-chosen-by-a-width-the-record-need-not-state — the widest-door rule is applied to a field a door record may omit, and a stated 3 ft then beats an unstated 3.5

*Status: OPEN · Raised in: the merge of Phase 13 into the second Phase 11 line (17 September 2026)*

**Two readers implement one rule — *the widest door on the front is the front door* — and they
rank on two different numbers. `axis.front_openings` copies `d.get("width_ft")` straight off the
room's own door record, so a door the record writes as `{"to": "exterior"}` reaches
`axis.door_bay`'s `max(doors, key=lambda o: o.get("width_ft") or 0)` scoring **ZERO**;
`openings.place` supplies 3.5 ft for that same door (`build/openings.py:494`'s `or 3.5`) and the
elevation ranks on the supplied figure. Where a front carries two doors and one omits its width,
the two answer differently — and `plan_check` convicts the placement on `door_bay`'s answer.**

## The measurement

`plans/tidewater-georgian-careful.json` writes the porch's front door with no `width_ft`:

    "porch": { "doors": [ {"to": "passage", "width_ft": 3.5}, {"to": "exterior"} ] }

On the ONE-ELEMENT reading of that record (`engine="heuristic"`, the deterministic engine), the
S front carries two placed doors:

| door | position | width the RECORD states | width `openings.place` supplies | bay |
|---|---|---|---|---|
| porch | 31.5 ft | — | 3.5 ft | **3, the centre bay of seven** |
| kitchen | 6.78 ft | 3.0 ft | 3.0 ft | 0 |

- `elevation.placed_openings` dresses the **porch** door — the widest, in the centre bay.
- `axis.door_bay` returns **`off-the-centre-bay`, bay 0, room `kitchen`** — the narrower door,
  because the wider one scored zero.
- `plan_check` emits `drawn-door-off-the-centre-bay` off `axis.door_bay` (CLAUDE.md records that
  reader by name), so **the corpus criticises a placement whose widest front door stands dead on
  the centre line.** That is the OQ 52 family: a defect reported where none exists.

## It was inert until the merge, and it is still right on every shipped record

Swept over the sixteen shipped plans on the deterministic engine: **exactly ONE places more than
one exterior door on the MAIN BLOCK's entrance front**, and it is the tagged
`tidewater-georgian-careful` — where the door that *does* state a width (`passage`, 18.0 ft) is
the real entrance, so both readers agree and the answer is correct **by luck rather than by
rule**. Fourteen plans place nought or one front door, and `max` over one element cannot be
wrong. Before the merge the one-element reading also carried one front door; main's WP-11.17
entrance front and WP-11.18 partition share re-place that ground floor and put a second door on
it, which is what made the defect reachable.

## The question

**What does a door record that states no width mean to a rule that ranks widths?** Three answers
are available and they are not the same:

1. **Read the drawing's figure.** `axis` ranks on the width `openings.place` supplied, so the two
   readers agree by construction. It is the one-spelling answer — but `axis.py` would then need
   the placer's `or 3.5` fallback, and that fallback is an unnamed literal in `openings.py`
   rather than a stated default anybody has ruled on. Copying it into a second module is this
   repository's most-repeated defect.
2. **Refuse to rank.** Where more than one door stands on the front and any of them states no
   width, `door_bay` returns COULD NOT EVALUATE with the reason. Honest, and **it costs the
   shipped Tidewater record a verdict that is currently CORRECT** (`in-the-centre-bay`) — which
   is the fake-unjudged direction this corpus calls exactly as dishonest as a fake pass.
3. **Require the width.** A placed exterior door must state its own `width_ft`, enforced in
   `schema/plan.schema.json` or by `check_plans.py`, and the two records above are edited. That
   makes the rule applicable everywhere and is a data edit that moves a shipped placement, which
   WP-11.13 ruled is its own package.

## What must not happen

- **Do not make `test_one_bay_system.py::test_the_entrance_is_the_widest_door_and_agrees_with_axis_door_bay`
  green by dropping the comparison.** It is the only thing in the tree that holds the two readers
  to one answer, and it is re-cut to state this divergence BY NAME so a second one fails.
- **Do not change `axis.door_bay`'s choice inside a merge resolution.** It moves a checker's
  verdict on a shipped record; that is a package with a measurement behind it.
- **Do not read the shipped corpus's agreement as evidence the rule works.** It agrees on one
  plan, for a reason that has nothing to do with the rule: the door with a stated width happens
  to be the real entrance there.
