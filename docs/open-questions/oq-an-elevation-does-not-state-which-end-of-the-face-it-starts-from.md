# oq/an-elevation-does-not-state-which-end-of-the-face-it-starts-from — and every face in the corpus is symmetric, so nothing can catch it

*Status: OPEN · Raised in: WP-12.4, the Round (9 September 2026)*

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
