# WP-5.8 — The four rulings, and a correction that did not land

*27 August 2026. Lucas ruled on the three open questions WP-5.7's audit raised and on the one it
widened. This package executes those rulings — and opens by fixing an error in the commit that
raised them.*

---

## 0. The correction that did not land

Commit `529310c` states, in its message, in the WP-5.7 report addendum and in the summary given to
Lucas, that two `width_parts` figures were corrected to their sources. **They were not.** The values
in the corpus never changed.

The cause is worth recording because it is a general one. The rewrite loop copied each member key in
order and, on reaching `spacing_parts`, assigned the corrected `width_parts` — then kept iterating,
reached the file's own `width_parts` key, and copied the original value back over the correction.
`gibbs-corinthian` landed only because it had no prior value to clobber. The **notes were rewritten
regardless**, so two members ended up carrying a provenance sentence reading *"CORRECTED 27 Aug 2026:
first written as 6.5…"* beside a value that was still 6.5.

So the corpus briefly held the exact failure the audit existed to catch — prose asserting what the
code does not do — introduced while writing up that audit. Fixed, and verified this time by reading
the file back from disk rather than trusting the write.

**The guard added alongside it could not have caught this, and that is the more useful finding.**
`test_a_width_survives_inheritance_in_the_same_unit_as_its_own_pitch` checks the width/pitch ratio,
so halving both numbers preserves it: 6.5/17.5 and 13/35 both read 37%. It catches a *mismatch*
between two fields and is structurally blind to a *uniform* error in both — which is precisely what
OQ 81 turned out to be. A transcription must be pinned against its quoted source, not its neighbour.
`TestTheTranscribedWidthsAreTheAuthoritiesOwnFigures` now pins all fifteen authored widths against
the words each was read from, and a mutation test confirms it fails on the exact halving that
shipped while the ratio test stays green.

## 1. OQ 78 — detect the datum per assembly-group

**Ruled: detect it, in one place.** The declaration is the *column's* and is correct there; the
question was what to do about the assemblies it does not describe.

`pack_geometry::axis_holds_for()` decides on two signals, either of which settles it:

1. **A recorded 0.** Under the radius reading that member stands on the centre line, which is
   impossible for anything with width. This is the signal an entablature gives.
2. **Nothing in the group reaches its own naked.** Every member would then sit inside the shaft.
   This is the signal a capital gives, whose figures are all real and all small.

It only ever downgrades `axis` to `naked`, never the reverse. Grouping matters and cost a first
attempt: judged per *assembly*, `gibbs-ionic`'s cornice still read `axis` because its corona reaches
well past the shaft, while its frieze read `naked` — an entablature in two coordinate systems. The
entablature is therefore judged as **one group**, the pedestal likewise, and the column's three
assemblies separately because each has its own naked.

`build/elevation.py::eave_cornice` carried a private copy of this detection and now delegates, which
closes the 2.37× divergence between the elevation inset and the two order plates.

**Measured:** faces drawn flush with their own naked **192 → 81**. Sixty assemblies across the
fourteen `axis` packs now read naked-relative — 14 cornices, 14 friezes, 14 architraves, 10
pedestals, 5 bases, 2 subplinths, 1 capital. `palladio-corinthian`'s cornice was 5 of 5 flat.

`check_orders.py` gained a third reporter — `note()`, beside `err()` and `warn()` — and prints, for
every axis pack, exactly which of its assemblies contradict its declaration. Fourteen do. The
silence was the whole cost of this question: the published account of OQ 78 said the column family
was sound because the check read the shaft and nothing else.

## 2. OQ 81 — correct the Benjamin pitches

**Ruled: correct them.** `benjamin-corinthian` 17.5 → **35**, `benjamin-ionic` 15.5 → **31**, matching
each pack's own module block (*"Every figure here is in minutes"*) and its own quoted authority. The
halving sentences inside both member notes were corrected with them. The other Benjamin members were
swept for the same conversion error and carry none — it was confined to these two.

With §0's widths this gives 13/35 and 10.5/31: 37% and 34% solid, where every other modillion in the
corpus sits.

## 3. OQ 82 — draw the teeth

**Ruled: wire it in.** `repeat_positions()` had two bugs before it had a caller. Its `centre_on`
branch filled forward only, so an anchored band left everything before the first anchor bare; and
two anchors filling toward each other both claimed the teeth between them, so every middle tooth was
emitted twice — invisible on a sheet, and a wrong count to anyone measuring the drawing. Both fixed.

The elevation cornice now lays its band out tooth by tooth, anchored on the bay centres, which is
what Gibbs's rule (*"always the centre of a Modillion exactly over the centre of each column"*) means
on a wall with no columns.

**Where the authority published no width the band draws solid and the sheet prints the reason.** That
behaviour was described in the schema, in `proportion_engine.py` and in `docs/proportion.md` and
performed nowhere. The Tidewater cornice takes exactly that path: `gibbs-ionic`'s modillion note
gives the pitch (three quarters of a diameter, 27 parts) and never the width, so the honest output is
a solid band that says why.

**The ruling is narrower than it looks, and the report should say so.** The order plates draw a
*section*, and a section cannot show repetition — teeth are an elevation phenomenon. So the elevation
sheet gets them; a half-section plate correctly does not.

## 4. OQ 83 — serve the paths, retire both copies

**Ruled: serve them from Python.** `build/profiles.py` emits `path` per pack and per face in MODEL
inches (x out from the axis, y up). The order tool and the workbench plate apply an SVG
`<g transform="translate(…) scale(k,-k)">`.

**A model-space path has no handedness for a consumer to get wrong.** SVG mirrors the arcs itself —
that is its job — and the flip that used to need detecting is a negative number in a matrix. This is
a better answer than testing the two copies against each other, because it removes the thing that was
being tested: `segCmds` (with `silhouettePathFromGeometry`, 106 lines) and `edgeCmds` are gone.
`vector-effect="non-scaling-stroke"` keeps the pen off the scale.

Guarded two ways in `workbench/server/tests/test_grammar_agreement.py`, beside the citation-grammar
test it is modelled on: one reads both JavaScript files **with comments stripped** — the history is
worth keeping in prose — and fails if arc-sweep arithmetic reappears in live code; the other asserts
Python is actually serving paths with arcs in them, so the two cannot both pass while a plate is
blank. Both were mutation-tested.

---

## What was found

**A ratio invariant cannot police a transcription.** The most transferable finding here. A guard that
relates two fields to each other is blind to any error that moves both — and "both fields halved" is
not an exotic failure, it is what a bad conversion looks like. Where a figure comes from a source,
the source has to be in the test.

**A write that reports success is not a write.** The 529310c loop printed a confirmation line for
every member it "corrected". Reading the file back afterwards costs one line and would have caught it
immediately; it is now the habit in this package.

**Grouping is part of a datum, not an afterthought.** The first cut of OQ 78's fix judged each
assembly on its own evidence and produced an entablature whose frieze and cornice were measured from
different origins — a subtler wrong answer than the one it replaced, and one that would have looked
plausible on the sheet.

**A promise made in three documents is still not a feature.** OQ 82's "drawn solid AND SAYS SO" was
described in the schema, the engine and the layer doc while no surface performed it — the same shape
as the chimney judgment the audit found asserted in a comment, a report and a commit message and
printed on no sheet. Two instances in two days suggests the failure mode is documentation written at
the moment of *intending* the behaviour.

### The datum detection's own blind spot, found by attacking it

The rule downgrades on either of two signals. The second — *nothing in the group reaches its own
naked* — is self-evidently safe: if no figure reaches the naked, none can be a radius. **The first
is not, on its own.** A group holding genuine radii *and* one unrecorded 0 would be downgraded on
the strength of the zero, and its real radii would then be added to the naked and drawn about twice
too wide. That is the OQ 65 bug returning by the back door.

Checked rather than assumed. The combination occurs in exactly twelve groups and every one of them
is an **entablature** — where it is the correct reading and the case OQ 78 was raised about: the
frieze records 0 because it *is* the naked, and the cornice's larger figures are relief from it.
Confirmed independently, and this is the satisfying part: under the naked reading the Tidewater
cornice's relief is **24.558 in against a height of 24.558 in** — exactly Gibbs's own stated rule
that the projection of the cornice equals its height. Under the other reading it is 21.8 against
24.6 and matches nothing.

Every downgraded *base* was justified by the second signal independently (`chambers-corinthian`'s
plinth records 24 against a radius of 36 — inside its own shaft, so it cannot be a radius). The
dangerous class has no data in it today, so the limitation is watched rather than engineered
around: `TestTheDatumDetectionsOwnBlindSpot` fails if a column or pedestal group is ever authored
holding both a real radius and an unrecorded zero, and says what to narrow.

## What was deliberately not done

- **The order plates do not draw teeth.** A section cannot show repetition; claiming otherwise would
  be a drawing that asserts something its own projection cannot see.
- **`benjamin-*` `spacing_parts` beyond the two corrected** were swept and found clean; nothing was
  changed speculatively.
- **The entasis construction** remains a smoothstep, disclosed — no authority in this corpus records
  one, and the facsimiles are the network-blocked OQ 7–11 class.
- **`gibbs-ionic`'s modillion width** was not authored. Its note publishes the pitch and the soffit
  division between modillions, and never the modillion's own breadth. The band draws solid and says
  so, which is the mechanism working rather than a gap in it.
