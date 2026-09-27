# oq/a-room-name-is-drawn-over-its-furniture — the name at the middle, where the table is

*Status: OPEN · Raised in: WP-14.6, the adversarial audit of Phase 14 (27 Sep 2026)*

**OPEN — the plan sheet sets each room's name at the room's centre, and the furniture pass puts a
room's principal piece there too.** Measured over the sixteen shipped plans, placed on
`engine="heuristic"` and drawn in the presentation register, **123 of the 267 room-name lines are
drawn over a piece of furniture** -- a dining room's name across its table, a bedroom's across its
bed. The estimate reads each line at 0.6 em a character in the size the fitter set it at; the
adversarial audit that raised this measured 140 of 270 with a different estimate, and the two agree
that it is about half.

The label fitter (`render_plan.py`, and `sheet/label.js` on the bench) keeps a name inside its
room's walls and breaks or turns it to fit; it has never been told about the furniture, which
WP-11.3 began drawing after it was written. Nothing is illegible in the sense the fitter guards --
the name stays inside the room -- but a name printed across the object it names reads as
annotation on the table rather than the room.

**What must be ruled:** whether a name yields to the furniture (the fitter searches the room's free
floor, and a room with none says so), the furniture yields to the name (a reserved label band the
furniture pass does not seat into), or the sheet keeps both and draws the name in a register that
reads over line work. Each moves every sheet in the corpus.
