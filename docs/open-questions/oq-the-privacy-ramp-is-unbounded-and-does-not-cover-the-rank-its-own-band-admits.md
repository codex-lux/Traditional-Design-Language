# oq/the-privacy-ramp-is-unbounded-and-does-not-cover-the-rank-its-own-band-admits — and a falsy guard covers exactly one bad case by accident

*Status: OPEN · Raised in: WP-12.5, the overlays and the modifiers (9 September 2026)*

**The privacy overlay's opacity ramp is `0.04 + ((rank - 1) / 4) * 0.20`, guarded only by
`if (!rank) return null`.** It has no upper bound and no lower bound, and the falsy guard
happens to catch one of the three ranks that break it.

Derived rather than re-read:

```
rank  −1  →  −0.06   a NEGATIVE opacity              not authorised
rank   0  →   null   dropped as though unranked      AUTHORISED
rank 1-5  →   0.04 … 0.24                            authorised, and correct
rank   6  →   0.29   darker than the deepest room    not authorised
```

`build/check_rooms.py::PRIVACY_BANDS` states the range the corpus allows and it is **0 to 5** —
*"0 street, 1 threshold, 2 public, 3 family, 4 private, 5 intimate"* — with the `threshold` and
`outdoor` classes both admitting 0. Measured over all 60 room records: ranks 1-5 are in use
(8/13/23/12/4) and **no record carries 0**.

So there are two questions here and they are different.

## 1. What does a street-rank room look like on this ramp?

Rank 0 is authorised and unused. `if (!rank)` treats it as falsy, so today it is silently
dropped as though the catalogue stated no rank at all — an **evaluated** rank rendered as
**unjudged**, which is the collapse this corpus names first, in the direction that is usually
the safer-looking one.

WP-12.5 made it a third state rather than deciding it: `privacyOpacity` returns `null` and
`privacyRefusal` says *why* — `outside the ramp this sheet draws`. That is honest and it is not
an answer. The two answers available are both authoring:

- **Clamp to the base.** Draws a street-rank room exactly like rank 1, which asserts the two are
  the same thing. They are not: the band separates them deliberately.
- **Re-ramp over 0-5.** Moves all five ranks a reader has been looking at since WP-5.2 —
  rank 1 goes 0.04 → 0.08 — to accommodate a room that does not exist. And it repeats the error
  that produced the current ramp: WP-5.2's own fix read the range off *what the records use*
  rather than off *what the band admits*, and re-ramping now would read it off the band while
  the records still use 1-5.

**A third possibility is that the band is wrong and no room should ever be rank 0**, in which
case `check_rooms.py` should refuse it rather than the drawing accommodating it. Nothing in
`rooms/` has ever needed it.

## 2. Why is the ramp unbounded at all?

Ranks −1 and 6 are not authorised by anything, so they can only arrive from a malformed record.
The shipped expression washes them anyway — one at a negative opacity, one darker than the
deepest legitimate room. WP-12.5 refuses both by name. That half needs no ruling; it is
recorded here because it is the half a mutation can see, and because it is *why* the rank-0
question could not be tested into existence: a guard asserting `privacyOpacity(0) === null`
passes against the shipped expression too, and the first version of that test was green under a
full revert.

## What would have to be true to close this

A ruling on where a street-rank room sits on the ramp, **or** a ruling that `privacy_rank: 0`
is not a value a room record may carry, in which case `build/check_rooms.py::PRIVACY_BANDS`
narrows to 1-5 and the refusal becomes unreachable rather than merely unused.

Do not close it by picking whichever reading makes a counter look better: the corpus states the
band in one place and uses a narrower range in another, and reconciling those by editing the
one that is easier to edit is the move `oq/a-grouping-rule-and-a-room-record-can-disagree`
exists to refuse.

## Where it lives

`workbench/app/src/sheet/overlayRules.js` (`privacyOpacity`, `privacyRefusal`), read by
`workbench/app/src/sheet/Sheet.jsx` and `workbench/app/src/round/overlays.js`. Driven by
`workbench/app/src/overlays.test.mjs`.
