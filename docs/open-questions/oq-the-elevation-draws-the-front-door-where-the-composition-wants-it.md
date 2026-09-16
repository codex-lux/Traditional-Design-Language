# oq/the-elevation-draws-the-front-door-where-the-composition-wants-it — and the placement puts it somewhere else

*Status: OPEN · Raised in: WP-12.7, the entrance and the porch (9 September 2026)*

**Two records of one front door, built from different rules, and until now nothing drew both.**

| | the elevation draws it at | the placement puts it at | apart | the drawn door falls in |
|---|---|---|---|---|
| `tidewater-georgian-careful` | 32.79 ft | 38.21 ft | **5.42 ft** | the centre passage |
| `spec-builder-colonial` | 25.67 ft | 47.00 ft | **21.33 ft** | **the garage** |

`elevation._face_bays` writes `kinds[mid] = "door"` — the entrance door goes in the **middle bay
of the front**, always — and `elevation.opening_rects` then dimensions it there. The placement
seats the real door where the porch room's own wall allows it: `openings.place` writes
`position_ft` on the room's door, and `plan.threshold` carries the same figure as
`door_position_ft`.

On the spec Colonial the drawn front door stands over the garage.

## Why this went unseen

Each record is right on its own, and no surface drew both until WP-12.7. The scene draws the
**doorcase** from `opening_rects` — the elevation's position — and the **stoop** from
`plan.threshold` — the placement's — so the model is the first picture in this project with the
two in it at once. On the Tidewater approach view the stoop stands five and a half feet east of
the door it serves, which is how this was found.

That is WP-12.1's own lesson repeated: *"invisible for as long as no surface drew a roof and a
room in one picture"*.

## And the checker convicts the half that is not drawn

`plan_check` already emits **`drawn-door-off-the-centre-bay`**, `serious`, reading
`axis.door_bay`:

```
verdict off-the-centre-bay · bay 4 · centre_bay 3 · bays 7 · room porch · position_ft 38.21
"The front door stands in bay 5 of 7, not the middle bay (4)."
```

So the corpus criticises the PLACEMENT for a displacement the DRAWING silently corrects. A
reader who takes the finding at face value and then looks at the elevation plate sees a
centre-bay door and no displacement at all — the plate is evidence against the finding beside it.

## The question

**Which door does the elevation draw — the one the composition wants, or the one the house
has?**

WP-11.7's ruling that *the facade is a RESULT and not an input* argues for the placement: an
elevation that composes its own front is drawing a house nobody placed, and the finding above
becomes unreadable. Against that, `_face_bays` is what makes a five-bay front five bays, and a
door drawn wherever the slicer happened to put it may fall between bays and read as a mistake in
the drawing rather than in the plan.

A third answer is that both are right and the drawing owes a DISCLOSURE — the composed front
with the placed door marked on it — which is what the sheet already does for a relaxation.

**Do not close it by moving the placement to the centre bay.** WP-11.3 built a `centre_bay_score`
for exactly that, swept it, and deleted it: *"a door in the centre bay is a property of a plan
organised about an axis, not of a placement scored for one"*, and at 1,500 candidates the term
moved the door to the wrong side of the centre.

## What WP-12.7 did

It changed neither. `build/scene.py` draws both where their own records put them and states the
disagreement in `not_modelled` — what cannot be modelled is a single coherent entrance — naming
both positions and the distance. Correcting the elevation would move sixteen shipped plates and
is a renderer package with a ruling in front of it.

## Where it lives

`build/elevation.py::_face_bays` and `opening_rects`, `build/openings.py::place`,
`build/threshold.py` (`door_position_ft`), `build/axis.py::door_bay`, `build/plan_check.py`
(`drawn-door-off-the-centre-bay`), and `build/scene.py::_entrance_agreement`.
