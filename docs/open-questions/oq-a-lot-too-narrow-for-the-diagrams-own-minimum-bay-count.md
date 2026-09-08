# oq/a-lot-too-narrow-for-the-diagrams-own-minimum-bay-count — does a physical fact outrank a diagram's floor?

*Status: OPEN · Raised in: WP-11.6 layer 4, the lot cap on the built extent (5 September 2026)*

## The measurement that raised it

WP-11.6's layer 4 put the lot cap on the BUILT EXTENT, hyphen included, as
`oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it` item 2 rules. The cap now
bounds two things it did not bound before — the growth loop's ceiling and the centre-bay parity
bump — and there is a third it does not bound, on purpose, because nobody has ruled it.

`derive_footprint` starts the bay count at the massing's own stated minimum:

```
start = max(mb["min"], from_area)
```

`mb["min"]` is read from the massing record's own `bays` field (`four-over-four` states `"5"`),
and that line does not consult `maxbay`, which is where the lot cap lives. So a five-bay diagram on
a lot that holds four bays builds five. Measured on `tidewater-georgian-careful`, one rectangle, no
dependency, at a 9 ft bay module:

| usable lot width | bays the lot holds | bays built | built extent | over |
|---|---|---|---|---|
| 45 ft | 5 | 5 | 45 ft | — |
| **36 ft** | **4** | **5** | **45 ft** | **9 ft** |
| **27 ft** | **3** | **5** | **45 ft** | **18 ft** |
| **18 ft** | **2** | **5** | **45 ft** | **27 ft** |

The overrun is capped at the diagram's floor rather than growing without limit, which is why it
looks the same at every narrow lot. It is nonetheless a house drawn outside its own lot line.

## Why this is a question rather than a patch

**Both answers compromise something the corpus states, and the corpus states both.**

*The lot should win.* `derive_footprint`'s own comment already argues it, in the sentence that
bounds the growth loop: the lot "is a physical fact, not a diagram convention". A drawing whose
building crosses its own lot line is a drawing that cannot be built, and the renderer draws that
line. This is the reading that made the growth ceiling `min(catalog_maxbay + 3, lot_maxbay)`.

*The diagram should win.* Decision #11 — settled, not to be reopened — is *"grow the footprint
before compromising a room: the stated infeasibility ordering"*. Shrinking the main block below the
count its own massing states is compromising the diagram to save the site, which is that ordering
run backwards. And a four-bay `four-over-four` is not a four-over-four: the massing's `bays` field
is a statement about what the type IS, in the same way `centre-passage-double-pile`'s centre bay
is (WP-11.3), not a preference the placer may trade.

**A third answer is available and is what the code does today: refuse to choose, and say so.**
`geometry_report.lot` reports the usable width, the main block, the flank, the built extent and the
overrun, and where the residue is the massing's floor its `note` names the floor, the lot's count
and this question. Nothing is silently obeyed on either side and nothing is claimed to fit.

## What must be ruled

1. **Does a lot outrank a massing's stated minimum bay count?** If yes, `start` clamps to
   `lot_maxbay` and a diagram that will not fit is built smaller than the diagram — and the record
   must then say the massing's stated count was not honoured, in the way `bay_count_forced_even`
   already says the parity was not.
2. **Or is a lot too narrow for the diagram a REFUSAL?** `derive_footprint` already refuses a lot
   too narrow for two bays (`{"error": "lot too narrow: …"}`), and extending that to the massing's
   own minimum is the smallest consistent rule. The cost is that a brief with a narrow lot returns
   no placement at all rather than a placement with a stated problem, which is a worse answer for a
   reader who wants to see how badly it does not fit.
3. **If neither — if the overrun stands as disclosed — does anything downstream have to act on
   it?** No fault in the corpus tests a building against its lot line today, and
   `plan_check` has no site layer at all. A number in `geometry_report` that no checker reads is
   the shape this project keeps meeting.

**The trap, stated because this package met its twin one function away.** Whichever answer is
taken, the SECOND bypass must stay closed. The centre-bay parity bump used to cross the cap on a
one-rectangle plan — a lot holding six bays got a seven-bay house, 3 ft over — and
`bay_count_forced_even`, the field written to name exactly that refusal, could never fire, because
the bump made the count odd whatever the lot said. A rule that says "the diagram's floor wins" must
not be read as "the diagram wins", or the parity bypass comes straight back.
