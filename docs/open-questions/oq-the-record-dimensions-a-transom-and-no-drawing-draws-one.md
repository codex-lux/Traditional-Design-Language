# oq/the-record-dimensions-a-transom-and-no-drawing-draws-one — and two faults judge it

*Status: OPEN · Raised in: WP-12.7, the entrance and the porch (9 September 2026)*

**`build/elevation.py` dimensions a rectangular transom over the entrance door, feeds it to two
faults, and no surface in this project draws one.**

The whole family is supplied together, and `elevation.py` says in its own comment why it must be:

```
"transom_height_in": ent["transom_height_in"],
"transom_width_in":  (None if forbidden else ent["door_leaf_width_in"]),
"transom_head_rise_in": None if forbidden else 0.0,   # rectangular, not a fanlight
```

> THE WHOLE TRANSOM FAMILY GOES ABSENT TOGETHER, or none of it does. Nulling
> `transom_height_in` alone left `transom_width_in` and `transom_head_rise_in` supplied, and
> `fanlight-before-its-date` and `transom-bar-at-the-wrong-height` immediately convicted
> `spec-builder-colonial` on the half that remained.

So on both shipped plans the record states a transom **18.524 in** and **15.157 in** high, the
width of the door leaf, with a head rise of zero. `render_elevation._entrance` draws the door
leaf, its six panels, the casing band and the two sidelights. It draws no transom.

## Why this is a question and not a patch

The transom's dimensions come from the SAME pack variant as the sidelights —
`transom_sidelight`, read for a `width` and a `height` at `elevation.py` 347-348 — and
`sidelights_present` is the only gate either half has. So the record does not offer a state in
which the sidelights are present and the transom is not: **on the corpus's own reading, a
doorcase with sidelights has a transom.** The drawing disagrees with that reading and nothing
compares the two.

Three answers are available and they are not the same:

1. **The sheet owes a transom.** `render_elevation._entrance` gains one and sixteen shipped
   plates move. If this is right it is a small, contained change — and it is a change to a
   renderer, which is its own package.
2. **The composition does not carry one and the measurement is wrong.** Then two faults have
   been judging a member that is not there, which is OQ 52's family, and the fix is at the
   measurement rather than at the drawing.
3. **A transom is separately optional and no field says so.** Then the record wants a
   `transom_present` beside `sidelights_present`, and today's silence is the gap.

## What WP-12.7 did

`build/scene.py::_entrance` **refuses** the transom by name and states the disagreement as the
reason. Drawing one in the model while the plate beside it draws none would make the two
surfaces different doorcases, which is the one thing WP-12.0 forbids — and this project's rule
is that a drawing set is one building.

`tests/test_scene_entrance.py::test_the_transom_is_stated_and_refused_and_the_premise_is_asserted`
reads `render_elevation.py`'s own source, so the refusal cannot outlive the omission it is
about: the day the sheet draws a transom, the scene's refusal goes red and sends the reader
here.

## Where it lives

`build/elevation.py` (`entrance_composition`, and the measurement block that supplies the
family), `build/render_elevation.py::_entrance`, `build/scene.py::_entrance`, and the faults
`fanlight-before-its-date` and `transom-bar-at-the-wrong-height`.
