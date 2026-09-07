# oq/the-facade-is-a-result-not-an-input — the bay rhythm follows the plan's organising move, and one hard test is inverted by saying so

*Status: RULED 4 Sep 2026 · Raised in: Q2 of `docs/reports/wp-9.2-what-the-tradition-actually-does.md` §7 (2 Sep 2026), put again by `docs/reports/tidewater-layout-diagnosis-2026-09-04.md` Part VII item 5*

**Lucas's ruling, 4 September 2026: the facade is a RESULT.** The bay rhythm follows from the
plan's organising move — for a centre-door diagram, the centred passage — and not the other way
round. And the second half of the same ruling, which is about the compiler rather than the
tradition: **the ordering of commitments is how findings are EXPLAINED, not how they are
resolved.** The system stays a constraint system; the sequence establishment → storey → breadth →
pile → hall and stair → length → doors → facade is the order a finding is narrated in, because
Glassie is explicit that his own rule sets are order-independent and reversible — *"It may start at
any point, take any route, and yet come to the same end"* — and because a pipeline cannot backtrack
when a dependency will not fit the lot.

## What the ruling is against

`docs/reports/wp-9.2-what-the-tradition-actually-does.md` reconstructed the tradition's sequence of
commitments from Glassie, Ware, Palladio-and-Scamozzi and Kerr and found the facade at the END of
it, as a consequence. Wenger's chronology is the historical form of the same dependency: *"Virginia
houses with advanced, raised, or pedimented central bays gained popularity in Virginia only after
the central passage had achieved status as an important social space"* — the facade followed the
plan's organising move, over a generation, in the buildings themselves.

The generator runs it backwards. `derive_footprint` picks a bay module and a count from the summed
room areas; `openings.py` then places each room's declared windows on whatever boundary wall the
room reached, after placement. So the front elevation has whatever number of openings the rooms
that happened to reach it declared. Measured on the shipped Tidewater plan on CP-SAT: **27 of 35
declared window units unplaced**, five openings on the ground front and three above, none over
another (`tidewater-layout-diagnosis-2026-09-04.md` Part I.1 and G1–G3).

## What it commits the corpus to, and none of it is free

**1. `groupings/centre-passage-core.json`'s hard test inverts.** *"Passage width 8 to 14 ft, and
roughly one fifth to one quarter of the facade"* sizes the passage FROM the facade, which under
this ruling is backwards: the passage takes a bay (or the middle bay of an odd count), and its
share of the facade is a consequence to be REPORTED rather than a rule to be satisfied. The prose
`statement` stays — the ratio is a real observation about the type — and the `test` becomes a
report of the resulting share, with the band as an advisory. **This is the one place the ruling
makes a currently-executable rule less executable, and it is deliberate**: a test that measures a
consequence as though it were an input is the error the ruling names.

**2. `faults/passage-that-is-a-corridor.json`'s `correct_practice` is wrong in its instruction as
well as in its number.** It says to size the passage from the facade. It has to say to take the
bay.

**3. The bay rhythm becomes derived and the door's bay a fact.** For a centre-door diagram the
count is odd, the door is in the middle bay, and growth adds TWO bays so the middle survives —
which is WP-11.2's odd-bay growth and is the cheap half.

**4. A room's windows become the bays its front wall spans.** Not a declared count placed where it
fits. The DECLARED count is still never overwritten (WP-6.2's rule stands); where the two disagree
the record says so, which is a finding and not a silent correction.

## What is NOT ruled

**Whether a non-centre-door diagram derives its facade the same way.** A Charleston single house is
entered sideways off a piazza; a shotgun's front is one bay and a door; a Craftsman's front is
composed around a porch. The ruling is stated for diagrams whose `circulation_parti` is
`center-hall` and the generalisation to the other twenty partis is not made here — that is the
per-parti pass `tidewater-layout-diagnosis-2026-09-04.md` Part IX describes, and each parti's
facade rule is that parti's to state.

**And the trap this ruling walks toward.** A derived facade is a facade the generator can be WRONG
about with confidence. Today the front elevation is an accident and reads as one; after this it is
a claim. Every bay it states must be traceable to a bay the plan states, and where the plan cannot
say, the facade must report COULD NOT EVALUATE rather than composing something plausible. The
window that gets invented to complete a rhythm is this ruling's version of the invented
measurement OQ 52 swept out of the elevation.

Built by **WP-11.7**, after **WP-11.2** (odd bay counts) and **WP-11.3** (the axis), because a
facade derived about an axis needs the axis first.
