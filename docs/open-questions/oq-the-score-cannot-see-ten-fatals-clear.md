# oq/the-score-cannot-see-ten-fatals-clear — the axes are bit-identical across the loop's best round in this corpus

*Status: OPEN · Raised in: WP-14.2, one house one verdict (20 September 2026)*

**Measured on `briefs/family-georgian.json`, `candidates=2`, `revise_engine="heuristic"`,
two rounds: the revision loop took `side-hall-townhouse` from eleven placed fatals to one, and
every one of the candidate's eight score axes came back bit-identical.**

    side-hall-townhouse   counts_before {fatal 11, serious 55, minor 79, info 26}
                          counts        {fatal  1, serious 58, minor 83, info 26}
      score_before 50.7                 score 50.7

      solecisms      0.725   of 80      w=20     unmoved
      rooms          0.5556  of 18      w=18     unmoved
      connections    0.0238  of 21      w=16     unmoved
      fidelity       0.5143  of  7.0    w=25     unmoved
      area           0.6626  of  1      w= 7     unmoved
      bedrooms       1.0     of  4      w= 4     unmoved
      canon          0.8571  of  7      w= 5     unmoved
      buildability   0.0     of  2      w= 5     unmoved

Not one part in forty-two on `connections`, the axis those fatals live in.

## This is not WP-14.2's defect and WP-14.2 is why anyone can see it

`SEV_CREDIT` gives `fatal` and `serious` the same 0.0, and `build/compose.py`'s own module
header states that as the design: *"a fatal spends its room exactly as a serious does … The
difference between wrong and worse is carried by `disqualified`, in words."* That ruling is
about a finding that gets WORSE or BETTER without leaving, and it is not in question here.

What is in question is a finding that **leaves**. `_axis_from_layers` takes the worst finding per
room (`min(per_room, credit)`), so a room whose fatal clears while it still carries a serious
contributes exactly what it did before. The loop cleared ten fatals and added three serious and
four minors, and the share of rooms that came back clean did not move at all.

Before WP-14.2 the card read `counts 1 → 1` (the declared reading, which the loop does not touch)
beside `score 56.5 → 56.5`, and nothing looked strange. Now both ends of both numbers are of the
placed house, and the card says `fatal 11 → 1` beside `score 50.7 → 50.7`. **The behaviour is
unchanged and four packages old; the only new thing is that a reader can see it.**

## What is genuinely unhandled

`_sort_key`'s primary key is the fatal count, and since WP-14.2 that is the placed count — so the
RANKING does see the loop's work, at the first key, and a candidate revised from eleven fatals to
one correctly overtakes one left at two. It is the **headline 0–100 number** that cannot, and that
is the number on the card, in the axis breakdown, and in `score_before`/`score`.

So a reader is handed two instruments about one act of revision, one of which reports a large
improvement and the other of which reports none, with nothing saying why they differ.

## What has to be ruled

1. **Is "share of rooms that came back clean" the right shape for this axis at all?** It
   saturates by construction: a room with one finding and a room with nine score the same, so
   the axes are blind to depth in both directions, not only this one. Counting findings rather
   than rooms is the obvious alternative and it is a different instrument, not a fix.
2. **Should a cleared fatal be credited even where the room stays dirty?** A bonus term outside
   the per-room `min` would do it, and it would be the first thing in this score that is not a
   share of checks — worth doing only if the answer to 1 is that the shape stays.
3. **Or is nothing wrong, and the surface owes the sentence?** `revisedLine` already prints the
   drawn key before and after, so the improvement IS on the card. The finding may be simply that
   the score's silence needs a word beside it rather than a new term.

Reading 3 is not obviously wrong, which is why this is a question.

## What must not be done

- **Do not move `SEV_CREDIT["fatal"]` below `serious` to make the number move.** That reopens a
  ruling stated with its reasons in the module header, on one session's reading, and
  `oq/066-score-s-eight-axis-weights-editorial-never-been` already records that these weights
  have never been measured.
- **Do not quote the table above as a general figure.** It is one brief, one returned set, one
  engine, two rounds. The interesting quantity — how often the loop's best round moves no axis —
  is a sweep nobody has run.
- **Do not read it as the loop failing.** Eleven fatals to one is the loop working; this entry is
  about the meter, not the engine.
