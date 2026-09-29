# oq/an-elevation-does-not-state-which-end-of-the-face-it-starts-from — and every face in the corpus is symmetric, so nothing can catch it

*Status: CLOSED 29 September 2026 (ruled that day; executed by WP-16.3) · Raised in: WP-12.4, the Round (9 September 2026)*

**`build/elevation.py::_face_bays` computes its bay centres as `(i + 0.5) * bay_w` across the
span and never consults the face.** So an elevation record's `centres_ft` are measured from *an*
end of the face, and nothing in the record says which end, in model terms, that is.

It did not matter while the elevation was only ever drawn flat: a plate is read on its own terms
and its left edge is its left edge. It matters the moment a plate is laid over a model, which is
what WP-12.4's `plate` overlay does — the viewer has to decide whether `u = 0` on the north face
is the east end or the west one, and the record declines to say.

## The measurement

Every face this corpus draws is symmetric, so the question is currently undecidable *and*
harmless. On `tidewater-georgian-careful`'s south front, seven bays across an outside width of
65.58 ft:

```
centres_ft  4.684  14.053  23.421  32.790  42.159  51.527  60.896
mirrored    60.896 51.527  42.159  32.790  23.421  14.053   4.684     ← the same list
```

`65.58 − 60.896 = 4.684`. The door is at index 3, the middle bay, which is symmetric too. So a
plate registered from either end lands in exactly the same place, and no assertion over the
shipped records can tell a right answer from a wrong one. That is the same shape as WP-12.2's
blind bay and WP-12.4's own unreachable lot: **a branch the corpus cannot reach, whose guard
must therefore be driven or the question left open.**

## What WP-12.4 does about it meanwhile

`workbench/app/src/round/frame.js::modelAt` takes `u = 0` to be **the face's left edge as the
camera sees it** — the camera's own `right` vector, so `u` runs the way a reader reads. That is
written into the function with this slug beside it. It is an assumption, it is stated as one,
and it is not laundered into the record.

## What has to be ruled

1. **Does an elevation's `u` run from a fixed model end (say, always west-to-east and
   south-to-north), or from the face's own left as drawn?** These differ on N and W. The second
   is what a draughtsman means; the first is what a serialiser finds easier.
2. **Should the record say so at all**, or is this properly the viewer's convention? The
   argument for the record: `centres_ft` is already published per face and read by the sheet,
   the DXF and now the model, and three readers agreeing by luck is what OQ 85 was about. The
   argument against: which end is *left* is a property of where the reader stands, which is a
   camera fact, and `frame.js` already holds every other camera fact under test.
3. If the record is to say it, the cheapest honest form is a `bays.from` token on each face
   block naming the model end — one field, four values, no new arithmetic.

**Do not close this by making the four faces agree.** They already agree; that is the problem.
The question is what they agree *about*, and today the answer is nothing.

## Amended 28 September 2026 (WP-15.8's audit): the record states it now, and the assumption put two plates on backwards

**The measurement above is no longer true, and the harm it called absent arrived.** Two things
changed after this was raised, and nothing brought them back here:

- **WP-13.3 made the faces asymmetric.** The elevation draws the plan's PLACED openings, so a
  face is as asymmetric as its plan. The "every face is symmetric" premise went with it.
- **The record answers question 3.** `elevation.datum.mirrored` is `FACE_MIRRORED`, and it has
  said since WP-13.3 that no face is mirrored: `u` runs with the plan's own axis on all four
  faces, west to east on S and N and south to north on E and W (`elevation.face_u_ft`).

`frame.js::modelAt` kept the assumption this entry records, `u = 0` at the face's left as the
CAMERA sees it. From the north and the west the plan's axis runs right to left, so the Round laid
the N and W plates over the model **reversed**, every opening at the wrong end. Nothing said so,
and `round.test.mjs` asserted *"the W plate reads u the other way"*, which certified the
assumption. Auditor F found it in the audit of WP-15.8's own diff. It is older than Phase 15:
WP-12.4's assumption met WP-13.3's statement.

**What was done.**
- The server sends each elevation plate's own `mirrored` (`corpus.plate_direction`), and `None`
  where the generator declined the record.
- `modelAt` reads that value and never assumes one.
- `plateRegistration` refuses a plate whose axes run against the screen's, because the affine
  carries no mirror. It says which way the plate reads: *"drawn west to east; seen from the north,
  east is on the left"*.
- A face plate whose direction the record does not state is refused by name.
- So the S and E plates still lie over the model, and the N and W plates are refused and say why.

**What is left, and it is question 1:** whether the N and W faces should be DRAWN as seen from
outside (the draughtsman's convention), which would let those two plates register too.
`FACE_MIRRORED` is the one switch, and `build/elevation.py` records why flipping it is a ruling:
the scene, the stack reader, the DXF and the sheet all read it together. Question 2 is answered
in the record's favour: it says so, and the Round reads it.

## Ruled 29 September 2026 (Lucas, asked directly): the N and W faces are drawn as seen

Asked: *should the north and west elevations be drawn as seen by someone standing in front of them?*
Lucas chose **Draw them as seen**:

> The draughtsman's convention. One switch mirrors N and W for the sheet, the DXF, the 3D scene
> and the stack reader together. Every N and W sheet redraws with the same content reversed, the
> Round lays all four plates, and the pins are re-derived with attribution.

That answers question 1. An elevation's `u` runs from the face's own left, as a person standing
outside sees it. `FACE_MIRRORED` becomes True on N and W. The readers that assume the plan's axis
move with it in one package, WP-16.3 (`PLAN-OF-ACTION.md`, Phase 16). The planning pass counted
seven of them; WP-16.3 re-derives that list rather than quoting it. This entry stays IN PROGRESS
until that package lands.

## Executed 29 September 2026 (WP-16.3)

`elevation.FACE_MIRRORED` is True on N and W, and every reader that assumed the plan's direction
moved with it in one package: the bays, the placed openings and their entrance tie, the dormers'
tie, the stack axes and outlines, the roof profile on the sheet and in the DXF, the scene's face
extrusion and its entrance check. The Round's code did not change: it reads `mirrored`, which is
now true on N and W, so all four plates register.

**The axis is the face's DRAWN width**, the outside figure the footprint states, which the wall
band spans and the roof is laid over. An N or W face is therefore the plan-direction face reversed
end for end and nothing else. A first draft reflected about the exact clear span plus two walls,
and every mirrored opening stood 0.0033 ft off its reflected wall on the Tidewater plan. The
footprint rounds that figure to two places.

**Measured against a worktree of `2ff37e0`:**
- 39 of 208 sheets moved: 14 N and W elevations, their 14 DXFs, and 11 scenes. No S or E sheet,
  plan, section or roof moved.
- The census reports 0 verdict moves.
- The scene is unmoved in model space, to the third decimal's ties.

`tests/test_faces_as_seen.py` holds one asymmetric opening to one model point on the record, the
sheet, the DXF, the scene and the Round, and holds each mirrored face to its plan-direction twin.

**Question 3's `bays.from` token was not needed.** `elevation.datum.mirrored` and the scene's
`faces[f].bays.mirrored` say which way each face runs, and the plate carries it
(`corpus.plate_direction`).

Report: `docs/reports/wp-16.3-the-faces-drawn-as-seen.md`.
