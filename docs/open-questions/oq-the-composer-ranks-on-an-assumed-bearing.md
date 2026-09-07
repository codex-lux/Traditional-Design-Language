# oq/the-composer-ranks-on-an-assumed-bearing — an aspect verdict entered the fitness function without being ruled into it

*Status: OPEN · Raised in: the adversarial audit of WP-11.9, WP-11.10 and WP-11.11 (7 September 2026)*

WP-11.9 gave `plan_check` a `daylight` aspect block. Its findings are `serious` and `minor`, not
`info`; `compose.SCORE_LAYERS` already maps `daylight` to the `rooms` axis; so **the composer's
fitness function gained a term the day that package landed, and the package's own report does not
contain the words *score*, *compose*, *rank* or *key_of***. The term is not wrong. It was silent,
and the thing it is computed from is an assumption.

## What it moves

Measured here, by suppressing `compass.read` on the checker's own module object and re-running.
(The first attempt at this measurement patched a compass loaded through a SECOND `modcache`
instance, so nothing was suppressed and every delta read 0.00 — this repo's own lesson, met while
applying it. The assertion `nb == 0` is in the harness now.)

Rooms axis, out of 18 points, on the 16 shipped plan records:

| plan | aspect findings | without | with | delta |
|---|---|---|---|---|
| `good-05-lobby-gallery-mansion` | 8 | 0.8056 | 0.6389 | **−3.00** |
| `tidewater-georgian-careful` | 9 | 0.5600 | 0.4400 | −2.16 |
| `good-04-rambling-porch-farmhouse` | 3 | 0.5769 | 0.4615 | −2.08 |
| `bad-04-log-cabin`, `bad-06-open-concept-render` | 3 | | | −1.29 each |
| `bad-05-two-story-spec-colonial` | 7 | | | −1.17 |
| `good-02`, `bad-03`, `good-01` | 4/4/3 | | | −0.82 / −0.64 / −0.45 |
| six others, `spec-builder-colonial` among them | 2–5 | | | **0.00** |

And on a real compose, at 8 candidates, with the term firing 719 and 510 times respectively:

| brief | winner moves? | order below it |
|---|---|---|
| `family-georgian` | no | **positions 3 and 4 swap** (`tower-villa` / `foursquare-quadrant`) |
| `bungalow-small` | no | **positions 4–7 reshuffle** |

So it re-ranks. Not the top choice on either brief tried, but the ordering under it, which is what
a reader comparing candidates is looking at.

## Why this is a question and not a defect

Three things make it defensible, and they are why nothing here has been reverted:

1. **It reads the DECLARED record.** A window's `wall` is authored. This is not a placement term
   sneaking into the key — it is a fact about the house the author described, which is exactly
   what the `rooms` axis is for.
2. **Every candidate is judged under the same north**, so the assumption does not advantage one
   candidate over another arbitrarily.
3. **Plan-N is true-N is a RULING** (5 Sep 2026). Applying a ruled convention is not inventing one.

Two things make it a question:

1. **0 of 16 plan records state a bearing** (`oq/no-plan-record-states-its-bearing`), and a brief
   states none either. So for the composer's entire traffic the term is computed from an
   assumption about the site — and the ruling that made the assumption was taken about a
   CHECKER, which reports, not about a fitness function, which decides.
2. **The penalty lands hardest on the cleanest candidate.** `_axis_from_layers` takes
   `min(per_room, credit)`, so a room already carrying a finding absorbs the aspect finding for
   free: −3.00 on the cleanest of the sixteen and 0.00 on six of the messier ones. That is a
   property of the axis rather than of this layer — every finding kind ever added has it — but
   it is the reason the delta is not uniform, and a reader comparing two candidates deserves to
   know that the tidier one paid more.

## What is being asked

- May a verdict computed under `compass.assumption()` enter the scored key at all, or should an
  ASSUMED bearing report and an assumed bearing only? (Note the shape of the trap in either
  direction: excluded, the corpus states 35 aspect rules and ranks on none of them; included, it
  ranks 16 of 16 plans on a site fact nobody wrote down.)
- If it may, should the term be weighted DOWN relative to a stated-bearing verdict, and by what?
  There is no source for such a weight and inventing one is the move this corpus refuses.
- Should `plan_check` emit the aspect finding at `info` where `plan_north().stated` is False —
  which would keep the census, keep the reader's warning, and keep it out of the key?

## What must not be done to close it

- **Do not carve `daylight` out of `SCORE_LAYERS` for this one kind.** Splitting one layer
  across two axes is the re-weighting the `drawn` note already declines, and it would move the
  depth rule and `sides-lit` with it.
- **Do not default a bearing.** `oq/no-plan-record-states-its-bearing` forbids it and states why:
  zero is not a measured north.
