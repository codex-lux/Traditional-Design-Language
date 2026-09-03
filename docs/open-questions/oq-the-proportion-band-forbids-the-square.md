# oq/the-proportion-band-forbids-the-square — 29 room types may not be square, and the square is what the tradition was aiming at

*Status: RULED 3 Sep 2026 · Raised in: WP-9.2, the precedents measured (1 Sep 2026)*

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

## Lucas's ruling, 3 Sep 2026: every floor goes to 1.0 — option 2, and NOT the study's own preference

**All 35 records now read `[1.0, hi]`.** The ceiling is untouched on every one of them.

**The ruling went against the study's stated preference, on a measurement taken to decide it.**
`docs/reports/wp-9.2-what-the-tradition-actually-does.md` §7 Q3 offered three options and its own
reading favoured the third — replace the floor with a DIRECTION, "this room wants to be square;
report distance from the square". Measured across the sixteen plans before choosing: **220 declared
rooms carry a proportion band and 38 sit BELOW their floor, and 14 of those 38 are in `good-*`
reference plans.** Every good plan but one has at least one. So a floor charge in any form —
a band test, a direction, a distance-from-square report with a threshold — **convicts all seven
plans this project holds up as good.** That is not a tuning problem, it is the direction being
backwards, and it is the second time this corpus has found it: WP-9.4 built the charge, watched it
convict the good plans, and deleted it as unsupported.

Option 2 over option 1 (delete the floors outright) purely on cost: identical behaviour, and it
needs no schema change (`room.schema.json` requires exactly two items), no `check_rooms.py` change,
and leaves `tests/test_voids.py` alone. A one-sided band would have bought nothing and touched three
more files.

### What actually changed, and what did not

- **35 room records**, floor only. Verified per file by deep-comparing everything except the
  proportion band, so no note, no ordering and no neighbouring figure moved.
- **`build/compose.py::room_default_dims` is the only behaviour that changes.** It sizes every
  instantiated room from `ratio = (pr[0] + pr[1]) / 2`, so the floor was half of what the composer
  aimed at: it never failed a house, it silently aimed **every room the composer makes** away from
  the square. That is why this was worth doing even though nothing convicts on the floor.
- **The 36th floor, which was in code.** `room_default_dims` fell back to a literal `[1.2, 1.4]`
  for the six types that state no band at all (`attic`, `cellar`, `garage`, `landing`, `terrace`,
  `workshop`). Removing 35 floors from the data while leaving a 1.2 floor invented in the composer
  would have missed the point of the ruling; it is `UNBANDED_PROPORTION = [1.0, 1.4]` now, named,
  commented as editorial, and its ceiling deliberately unmoved.
- **No reader changed, because no reader charges the floor.** `plan_check.py`'s room layer and its
  drawn layer both unpack `plo` and use it only in the message; both test `ar > phi` alone.
  `geometry.shape_band()` returns the ceiling. `WIDTH_W` is a different floor (`width_ft[0]`, in
  feet) and was not touched.
- **`geometry.py`'s courtyard bay-count is the one live floor reader** — it averages `prop[0]` and
  `prop[1]` and bounds the ratio with both. `courtyard` was already `[1.0, 2.2]`, so this ruling is
  a no-op there. Asserted rather than assumed.
- **`check_grouping_rules.py` already knows the `proportion` key** and would compare both ends the
  moment a grouping rule `measures` one. None does today; its ratchet is unmoved by this change.

### What stays open, and it is the better half of the entry

The **ceiling** is the well-sourced half and this ruling does not touch it. And the reading the
study proposed is still worth having as a REPORT: nearest canonical shape with a percentage error,
carrying no pass/fail threshold at all. What is refused is a floor that CONVICTS, in any spelling.
The distinction is the entry's own, and §"The thing that must not happen" below still governs.

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
