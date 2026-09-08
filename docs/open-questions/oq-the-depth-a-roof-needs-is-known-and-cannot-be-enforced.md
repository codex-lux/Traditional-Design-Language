# oq/the-depth-a-roof-needs-is-known-and-cannot-be-enforced — the floor is derived, and enforcing it would propagate a broken licence

*Status: OPEN · Raised in: WP-11.10, deriving the depth floor from the fault's own rule (7 September 2026)*

**`build/depth_floor.py` computes the shortest span whose roof still clears
`faults/truss-flattened-pitch.json`, by inverting that fault's own test. Nothing acts on it, and
this entry is why.**

    min_outside_span >= threshold * wall_height_ft * 24 / pitch

The threshold is READ from the fault record, the pitch from the style's own migrated constraint,
the wall height from `build/storeys.py`'s derivation. No number in it is invented. It agrees with
the fault's forward verdict on **every plan it judges — 2 agree, 0 disagree, 14 unjudged**.

## Why it is not a cap

Three measurements, and any one of them is sufficient.

**1. A `good-*` reference plan is convicted FATALLY by this fault today, through a licence that
names its sibling.** `good-05-lobby-gallery-mansion` reads **0.2509 against 0.45**. Its style is
`italian-renaissance-revival`; the fault's `exceptions[]` name `italianate-american`. The licence
never reaches it, which is
`oq/a-licence-matches-the-style-id-exactly-and-never-its-descendants` — recorded, unruled. **The
floor that conviction implies is 69.31 ft of depth against a drawn 38.64** — an 80% deeper house,
demanded of a villa whose low pitch is the point of the style.

A finding a reader can weigh is one thing. **A hard floor in the placer is another**: it would
make a known-broken licence mechanism into a constraint that silently reshapes every house of
that family, and the reader would never see the fault it came from.

**2. Only 3 of the 16 plan records have a style with a migrated `roof_pitch_rise_per_12`
constraint at all.** On the other 13 the floor is COULD NOT EVALUATE. That is the right answer —
`structure.roof_heights` refuses identically, "ridge height left unjudged rather than computed off
an invented pitch" — but it means a cap would govern a fifth of the corpus and be silent on the
rest, which is not a rule, it is a coincidence of which styles have been migrated.

**3. The obvious alternative cap was measured and is worse.** A floor at the massing's own pile
(`geometry.PILE["double-pile"] = 36.0`) would move `spec-builder-colonial` from 30.75 to 36.0 ft —
**262 sf of empty floor, 17.1% more footprint than programme** — to satisfy a rule that is not
convicting it. A pile is a TYPICAL depth. Reading a typical value as a hard floor is how an
invented number enters a corpus, and this corpus removed 35 proportion floors on 3 September for
exactly that reason.

## What is true and unhandled

**`derive_footprint` bounds depth from above and from below by nothing.** `H = need / W`, and its
growth loop's exit is `H <= depth_for(W) * 1.18` — a ceiling with no floor. Move a programme into
a wing and the block gets shallower without limit. Measured on the re-authored
`centre-passage-double-pile` fixture: a main block of **45 x 28.89 ft**, convicted at 0.4066.
That fixture is `oq/three-hard-room-rules-forbid-a-detached-kitchen`'s, and this is why it ranks
ninth and is never placed.

So the defect is real, the number that would fix it is known, and it cannot be enforced yet.

## What a ruling has to decide

- **Whether the licence question is ruled first.** If an exception may reach a descendant style,
  `good-05` is excepted, the 69 ft floor disappears, and a cap becomes discussable. That ordering
  is the cheapest route and this entry recommends it.
- **What a cap does on a style with no migrated pitch** — refuse to place, place and disclose, or
  fall back to the pile. *Unjudged is not passed*: the third is the flattering answer and needs
  saying out loud if it is chosen.
- **Whether the placer may read the fault corpus at all.** It does not today. `plan_check` judges
  a house the placer has made; a placer that pre-satisfies one fault has made that fault
  un-failable, which is the pattern `roof.py`'s three un-failable checks record.

## What must not be done to close it

- **Do not cap at the pile.** Measured above: it buys 17.1% of empty floor on a shipped plan to
  satisfy nothing.
- **Do not except `good-05` by editing the fault's exception list.** The licence's scope is the
  question; widening it for one plan settles a corpus-wide mechanism from a single case.
- **Do not read the floor into `geometry.py` "inertly, at weight zero".** WP-11.3 deleted an inert
  score term rather than leave it, and CLAUDE.md's own words are that an inert wrong number is an
  instruction to the next reader. `tests/test_depth_floor.py::TestItIsNotEnforced` fails if
  `geometry.py`, `geometry_cp.py` or `compose.py` so much as imports the module.
