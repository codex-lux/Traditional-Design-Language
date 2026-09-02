# oq/the-proportion-band-forbids-the-square — 29 room types may not be square, and the square is what the tradition was aiming at

*Status: OPEN · Raised in: WP-9.2, the precedents measured (1 Sep 2026)*

**Thirty-five of sixty room records carry a `proportion` lower bound above 1.0. Twenty-nine of
those are not circulation rooms** (counted by `function_class`; the parallel study counts the same
defect as "13 of 23 habitable" against a narrower denominator — the 35 is common to both). A drawing room may not be squarer than 1.25; a hall may not be
squarer than 1.3.

```
drawing-room     [1.25, 2.0]        hall             [1.3,  2.2]
parlor           [1.1,  1.45]       best-parlor      [1.1,  1.4]
dining-room      [1.15, 1.8]        library          [1.1,  1.6]
primary-bedroom  [1.05, 1.4]        kitchen          [1.05, 1.8]
```

**The measured counter-example is the best-documented Georgian house in America.** From the Mount
Vernon Ladies' Association's own room-by-room page:

| room | dimensions | ratio | band for its type |
|---|---|---|---|
| Front Parlor | 16' 9" × 16' 6" × 10' 10⅜" | **1.015** | `parlor` [1.1, 1.45] — below |
| Dining Room | 15' × 17' × 10' 9½" | **1.133** | `dining-room` [1.15, 1.8] — below |
| New Room | 22' 9" × 30' 6" × 16' 6" | 1.341 | `drawing-room` [1.25, 2.0] — inside |

The Front Parlor is the room Washington called *"the best place in my House"*, and Mount Vernon's
own FAQ for it reads: *"The current dimensions of the room are approximately 17 feet square …
Historically, George Washington described the room as being 18 feet square."* He described its
shape as a square on purpose, and this corpus forbids it.

**No period source found in the study states a minimum room ratio.** Palladio's seven room shapes
begin with the round and the square. Morris, *Lectures on Architecture* (1734), Lecture VII: *"the
nearer a Room (in particular a Hall) is to a Square, the more uniform and commodious they will
be."* Kerr's own recommended bedroom sizes, from the 1865 text: *"a square of 16 feet makes a good
ordinary room, or 16 feet by 20; 20 feet square is a very commodious size; 18 by 24 feet makes a
room of the first class"* — 1.0, 1.25, 1.0, 1.333. The prestige direction runs **toward** the
square.

**Attribution corrected by the audit: in Morris's Lecture VII the grammatical subject of that sentence is PALLADIO** — Morris is reporting *"Palladio has observ'd, that there are seven beautiful Proportions"* and the preference for the square sits inside that report. So Morris is not an INDEPENDENT English witness to the rule; he is Palladio at one remove, and the two must not be counted as two sources. The argument that **no source found states a MINIMUM** is unaffected — nothing here states one — but the corroboration is thinner than an earlier version of this text implied.

## Why this is a question and not simply a fix

**The floors convict nothing today, but they are NOT inert — an audit corrected this.**
`compose.room_default_dims()` sizes every instantiated room from
`ratio = (pr[0] + pr[1]) / 2.0`, so the FLOOR shapes the declared width and length of every room
the composer makes. It does not fail a house; it silently aims every room away from the square.
What convicts nothing is the reading side: `plo` is
unpacked in exactly two places in `plan_check.py` — lines 706 and 1237 — and used for nothing but
the message text; both checks charge `ar > phi` alone. `geometry.shape_band()` returns the ceiling
and never the floor. `WIDTH_W` ships at 0.0. So today the lower bounds are declarations that no
reader acts on.

That makes three genuinely different answers available, and picking one is an authoring decision
about what the band MEANS:

1. **Delete the lower bound on habitable rooms.** A floor of 1.0 (or none) says what every source
   says. Cheapest, and it makes the record honest about what it can support. **An earlier version
   of this entry attached a cost to it that an audit showed is zero**: it claimed
   `check_rooms.py`'s dimension-consistency check would then fire on 29 records. It would fire on
   none — the only clause that reads the floor is `prop[0] > hi_p * 1.25`, and LOWERING `prop[0]`
   makes that strictly less likely to fire. **The real cost is on the generative side, not the
   checking side**: `compose.room_default_dims()` averages the band to size every room it makes, so
   lowering the floors moves the default shape of every composed room toward the square. That is
   the intended direction — but it is a change to every plan the composer produces, not a
   documentation edit, and it should be measured before it is made.
2. **Keep the bound and re-read it as a TYPICAL rather than a LIMIT.** Many of these numbers are
   defensible as descriptions of what the type usually is — a drawing room usually is longer than
   it is wide. Then the band needs a vocabulary distinction the schema does not have (`typical`
   versus `permitted`), and every reader has to be taught which it is looking at. This is the
   honest reading of what the author probably meant, and it is the most work.
3. **Keep it and scope it by establishment.** Kerr's dimensions are for an English gentleman's
   house; a farmhouse parlour is a different question. `applies_when` already exists for exactly
   this shape of precondition on the fault side.

**Option 1 is what the sourcing pass recommends** ("remove the lower bounds on habitable rooms
before adding anything; a floor of 1.0 is the tradition's optimum, not its failure"). Option 2 is
what the records probably meant. They differ in what a future checker is allowed to do, which is
why this needs a ruling rather than a commit.

## The thing that must not happen

**WP-9.4 nearly built the charge.** It added a squarer-than-the-band direction to `level_score`,
watched it convict both good reference plans, and deleted it — recording only that it had invented
a direction with no corpus prose behind it. That was right for a shallower reason than the real
one: the direction is not merely unsupported, **it is backwards**. Twenty-nine records currently
tell the next package to build it again.

## The other half of the same reading, which is a ceiling with no floor

Morris (1734): *"the Length of no Room exceed a Double Cube, or what he there terms two Squares."*
Scamozzi (1615), independently and in another country, gives the same ceiling **and its reason**:
beyond two squares one gets *"halls, galleries or passageways rather than rooms to live in."*

That is a definition, not a band. A room over 2:1 has stopped being a room — which makes the
generated kitchen at 3.0 and breakfast room at 3.86 out of category, not merely out of band, and
says exactly why the passage at 3.70 is exempt. **If it is ever encoded, the exemption belongs to
the room as a declared property and not to a widened band**; widening the band to swallow the
passage loses the reason and licenses every sliver WP-9.2 found.

## Provenance, stated plainly

The corpus counts (35, 29, and the two `plo` call sites) were verified by reading the files. The
Mount Vernon dimensions were verified on the owning institution's own page. **The Morris, Scamozzi,
Palladio and Kerr quotations reach this file through one adversarial sourcing pass that checked
them verbatim against reproductions; no facsimile has been read here**, and none of them may be
cited as `measured` in a record on this strength alone. They are strong enough to stop a rule being
built and not strong enough to build one.

And the caution that travels with them, from Wells (1998): *"Mount Airy is the only surviving
colonial Virginia house to manifest a clear compositional debt to an English pattern book."* The
Palladian shape rules must not be encoded as rules **of the American tradition**.
