# oq/two-hundred-and-seventy-six-measurements-nobody-refuses-and-nobody-supplies — the real shape of "120 faults unjudged"

*Status: OPEN · Raised in: WP-13.1, the detection layer (15 September 2026)*

On `tidewater-georgian-careful`, this corpus's own most carefully authored plan, **120 of 210
faults come back COULD NOT EVALUATE**, naming **299 distinct missing measurements**. WP-13.1 sorted
the 299 by what this corpus has already decided about each name:

| | names | faults whose whole `needs` list is of this kind |
|---|---|---|
| **refused** — a layer names the quantity and declines it, with a reason written beside the code that would have derived it | **23** | **8** |
| **unsupplied** — nobody refuses it and nobody supplies it | **276** | **107** |
| mixed | — | 5 |

The 23 are now quoted to the reader: `plan_check`'s unjudged rows carry the refusal and its reason,
so *"needs `dedicated_plant_room_area_sqft`"* is no longer handed out as a work item for a question
that was built, measured, found to convict both reference plans and deliberately withdrawn.

**The 276 are the question.** They are not a backlog and they are not impossible, and which of the
two each one is cannot be decided from the record — that is the whole reason the verdict is
`unsupplied` rather than `gap`.

## Two discriminators were built for them and both were falsified by measurement

Recorded because each reads perfectly well and is wrong, and because the second cost more to
falsify than to build.

1. **"`measurable_from: photograph` means this compiler can never reach it."** It would have made a
   clean story: 175 of 210 primary tests declare `photograph`, and this system holds no
   photographs. **FALSE.** 54 photograph-only faults are JUDGED on this plan, because
   `build/elevation.py` supplies 184 quantities a photograph test reads perfectly well.
   `measurable_from` says what a photograph SUFFICES for; it does not say a drawing cannot.
   A census built on it reported the work list as 15 names. It is 276.
2. **"The detection prose names its own surface, so hold it against the tests'
   `measurable_from`."** Unusable: **the word `elevation` in this prose means the FACE of the
   building, not the drawing** — *"count exterior doors on the rear elevation of the main block"* —
   and a naive word match reports 22 records whose prose and tests share no surface at all.
   **Twelve of the 22 are that word sense and vanish when `elevation` and `section` are excluded
   from the vocabulary**, which `detection.surface_words()` does, in a comment, with a test pinning
   both the exclusion and the naive vocabulary the 22 was measured against — the naive figure is a
   property of the regex, not of the corpus. The 10 that survive are not errors either —
   `stair-at-the-front-door` really does describe a photograph procedure for a test stated on a
   plan — so nothing is ratcheted on it and no check convicts on it.

## What has to be ruled

1. **Is `unsupplied` a work list at all?** A quantity nothing in the corpus models is not a debt
   in the sense `unendorsed` is a debt. Some of the 276 are real omissions the drawn record could
   close tomorrow (`main_block_depth_ft` is `footprint.depth_ft`; `room_depth` is on every room);
   most are properties of buildings this system does not model at all (`quoin_bed_joints`,
   `trough_fall_in_per_ft`, `reflected_colour_temperature_kelvin`).
2. **Should a name be refusable without being derivable?** Today a refusal lives beside the layer
   that would otherwise have derived the quantity, which is right — the reason can be checked
   against the code. But a quantity no layer would ever derive has nowhere to be refused FROM, so
   the honest refusals are structurally confined to the names a layer nearly supplied.
3. **The cheap first step, if one is wanted:** take the eight faults whose `needs` list is
   *entirely* refused and decide whether each refusal still holds. Two of the thirty-six refusal
   reasons were already found to be claims a later package had falsified (see WP-13.1's report);
   nobody has re-read the other thirty-four.

## Do not close this by lowering the bar

Supplying a name to make a fault judgeable arms every rule that presupposed it (OQ 89), and
supplying it from a constant is how 26 of this plan's 65 *clear* verdicts came to be cleared on the
generator's own output — `oq/clear-counts-a-pass-and-a-tautology-as-one-thing`. An unjudged fault
is the honest answer and is not a pass; 276 honest unjudged is not worse than 276 invented numbers.
