# WP-9.2 (second report) — The plan layer: what the tradition actually does

*The study Lucas asked for on 1 Sep 2026, before any more generator code. Seven agents: five
research passes over the compositional literature and the measured record, one adversarial pass
that audited their sourcing and rated the whole "partly-sourced", and one synthesis. What follows
below the line is that synthesis as it was written.*

**How to read it, and what I checked myself.** I did not commission this and then relay it. Every
claim below that can be checked against this working tree, I checked, and the three that did not
survive are corrected here rather than silently in the text:

1. **"`critical_dimension` is parsed by nothing" (§4b A10) is true, and "read by nothing" is
   false.** `build/openings.py::stair_pass` opens by quoting `rooms/stair-hall.json`'s
   `critical_dimension` — saying it "has been read by nothing" — and then **hand-ports its
   arithmetic into Python**, citing the prose as its source (`openings.py:400-405, 482, 515`). So
   for one room the generator already does what A10 asks for, by transcription. That is a better
   finding than the one it replaces: **the prose and the Python are now two spellings of one rule
   and nothing holds them together**, which is this repository's most-repeated wound. A10's
   proposal is right; it should be built as one reader, not a second transcription per room.
2. **"nothing that dimensions a room can ever read" the suite rule (§4b A11) is overstated.** The
   fact is verified — `proportions/systems/room-harmonic.json`'s rule at index 17,
   `target_slot: public_private_gradient`, is the only one of its eighteen `derived_rules` without
   a `quantity`. But `proportion_engine.evaluate()` passes `quantity` through as `None` and still
   emits the rule. The real consequence is narrower and still bad: `check_addresses.py` says in
   its own header that *"a rule with no `quantity` cannot be compared, and the pair is reported"*
   unjudged — so the corpus's only compositional proportion rule is permanently invisible to the
   corpus's own collision guard.
3. **The seven-complaint mapping, the exemplar measurements and the furniture sweep** are not from
   this study at all — they are in the first WP-9.2 report,
   `docs/reports/wp-9.2-the-parti-is-not-the-type.md`, and were measured independently. Where the
   two reports touch the same fact they agree, which is worth knowing because they were produced
   by different routes: that report worked from HABS written data and the code, this one from the
   treatises and the state-register files.

**What I verified by script or by reading the files, and found correct:** 35 of 60 room records
carry a `proportion` floor above 1.0; `structural_logic` has zero readers in `build/` or
`mcp_server/`; `never_a_through_room` is 21 true / 39 false / 0 absent, with `dining-room` and
`drawing-room` both false; no M-roof, double roof or valley gutter appears anywhere in `massings/`,
`rooms/`, `groupings/`, `partis/` or `docs/`; the passage width is stated with four different
floors across four files and `faults/passage-that-is-a-corridor.json` contradicts itself inside one
record; `georgian-service-core` and `dependency-and-hyphen` carry two hard ridge rules for one
volume under two names, and two partis carry both groupings; and **§4b A2 holds** — the
`storey_height * 0.78 * 2.25` chain is authored in `proportions/systems/room-vernacular.json` and
no massing reads it. Its one reader, `check_rooms.py:251`, uses the head factor to check a room's
own daylight depth, never to cap the pile.

**A trap found while checking A2, and it is this repository's favourite shape.** Grepping `0.78`
to find that chain also hits `build/geometry.py:495`, where `0.78` is the upper clamp on a
slicing fraction — an unrelated quantity that happens to share the literal. One number, two
meanings, two files apart, in a codebase whose most-repeated wound is one rule spelled twice.
Anyone building the storey→head→depth chain should not assume that hit is part of it. **Mount Vernon's room dimensions I
read on the Mount Vernon Ladies' Association's own page** — Front Parlor 16'9" × 16'6" = 1.015,
Dining Room 15' × 17' = 1.133 — because they are the measurement the largest finding rests on.

**What I did NOT verify, and neither should the next reader assume:** the period quotations.
Palladio via Ware, Morris 1734, Scamozzi via Barbieri, Kerr 1865, Glassie 1975, Ware 1756 — every
one of them reaches this document through the study and its adversarial pass, which checked them
verbatim against reproductions. **No facsimile has been read in this repository.** They are strong
enough to stop a rule being built and not strong enough to build one, and §6 below is the list of
what that means in practice. Nothing here may be written into a record as `measured` on this
strength.

**Status of the questions in §7: none of them is answered.** They are for Lucas. Three of the
findings have already been raised as open questions —
`oq/the-proportion-band-forbids-the-square`, `oq/a-massing-states-its-structure-and-nothing-reads-it`,
`oq/the-parti-dissolved-its-own-dependencies` — and the rest wait on his rulings, because several
of them (Q1 register, Q2 the facade as a result, Q5 pipeline versus constraint system) change what
the model *is* rather than what a number *says*.

---

# THE PLAN LAYER: WHAT THE TRADITION ACTUALLY DOES

*A study for Lucas, before the next line of code. Five research passes plus an adversarial audit of their sourcing; corpus claims re-verified against the files in this working tree on 1 Sep 2026.*

---

## 0. THE SHORT VERSION

Four findings, in the order of how much they should change what gets built next.

**One. The tradition does not compose with proportion bands, and the end of the band this corpus gets wrong is the LOWER one.** No period source in this study states a minimum room ratio. Every rule is either a named shape (Palladio's seven, Morris's seven, Scamozzi's five) or a maximum (two squares), and the prestige direction runs *toward the square*. This corpus forbids **35 of 60** room types from being square, and **13 of 23** habitable ones — including every room in the `public` class, plus the dining room and the library. It convicts Mount Vernon's Front Parlor (1.015), the room Washington called "the best place in my House."

**Two. The facade is a result, not an input, and one hard test in this corpus runs the causation backwards.** `groupings/centre-passage-core.json` carries `passage_width_ft / facade_width_ft between 0.18 and 0.27` at severity `hard`. The band is defensible descriptively — **four** of my six measured cases land inside it (the audit corrected "five": 0.165 is below the band and 0.300 above it) — but as a rule it makes the passage a function of the facade, where in every account of setting-out I found, the passage and the rooms are decided first and the facade is what results. Glassie's grammar is explicit: the door goes in the passage component, one or two windows go in each room component, and *therefore* the front is three bays or five. Nothing else.

**Three. The largest missing thing is not a rule but an object: the circulation system.** Kerr opens his section on thoroughfares with "These the skeleton of plan," and designs the route system first, hanging rooms off it. This corpus has rooms with door lists and lets circulation emerge — which is precisely what WP-9.2 measured when **121 of 123 heuristic fatals** read *cannot be reached from outside the house*. That is not a solver defect. It is a missing object in the model.

**Four. The corpus already contains its own generative model, written in English, in one sentence, and nothing derives from it.** *(Read with the preface's correction 1: `critical_dimension` is parsed by nothing, but `openings.py::stair_pass` HAND-PORTS the stair hall's arithmetic into Python, so "its only readers" below is not a complete enumeration.)* From `proportions/systems/room-vernacular.json`: *"The treatise room is proportioned — its length is chosen for its ratio to its breadth. The vernacular room is constrained — its breadth is set by span, hearth and daylight, and its length is set by what has to go in it."* Every room in the corpus carries the length arithmetic in `dimensions.critical_dimension`. Nothing parses it. Its only readers warn that it is absent (`build/check_rooms.py:288`), quote it as evidence text in a finding (`build/plan_check.py`, seven sites), or echo it over the API (`mcp_server/core.py:1219`).

---

## 1. WHAT THE TRADITION ACTUALLY DOES

> **Every period quotation in this section and the next reaches this repository AT ONE REMOVE.**
> The preface says so once and an audit found the body says it nowhere — the quotations appear
> with ordinary bibliographic citations, several with page numbers, which is the form a reader
> treats as first-hand. They were checked verbatim against reproductions by an adversarial pass;
> **no facsimile has been read here.** Read every "—Palladio", "—Morris", "—Kerr", "—Glassie" and
> "—Ware" below as "as transcribed and checked at one remove". §6 lists what that forbids.

The ordering below is itself a finding. Five sources independently describe a *sequence of commitments*, each of which removes freedom from the next, and none of them describes a simultaneous satisfaction of bands. Where the sequence is my reading rather than a source's, I say so.

### First: the establishment, not the house

Kerr's foremost maxim is not about a room. It is about how many populations the building has to keep apart:

> "It becomes the foremost of all maxims, therefore, however small the establishment, that the Servants' Department shall be separated from the Main House, so that what passes on either side of the boundary shall be both invisible and inaudible on the other."
> — Robert Kerr, *The Gentleman's House* (2nd edn, John Murray, 1865), Pt II Div I ch. II

The "however small the establishment" is the load-bearing clause, and the reason the establishment is decided first is that it changes the *kind* of rule everything downstream obeys. On the dinner route Kerr is weaker than one might expect, and explicitly so:

> "In a small house the room will generally have but one door for both entrance and service… as the dishes must be carried to and from the door through the family part of the house,—the Corridor, for example, Staircase, or Vestibule,—it is essential that they shall not cross the track of family traffic, or otherwise be obtruded upon the notice of the inmates or visitors."

That is a **non-coincidence and visibility rule, not a topological exclusion**. `faults/service-route-through-the-formal-plan.json` tests `service_routes_crossing_a_formal_room` at threshold 0. Threshold 0 is right for a house with a service wing and a back stair. Per Kerr it is *wrong* for a small house, where the crossing is unavoidable and the constraint moves to *when* and *in view of whom*.

The establishment also sets the dining room's floor, and this is where the corpus contradicts a source it names itself (§4).

### Second: the storey height — because ceiling height belongs to the floor, not to the room

This is the best-established finding in the whole study and the one with the most downstream consequence. Palladio offers three means for a vault height, and states his own reason for offering three:

> "[W]e should make use of each of these heights depending on which one will turn out well to ensure that most of the rooms of different sizes have vaults of an equal height and those vaults will still be in proportion to them…"
> — Palladio, *Quattro Libri* I.xxiii, Tavernor & Schofield trans., quoted verbatim in S. R. Wassell, *Nexus Network Journal* 1 (1999)

Scamozzi states the constraint outright: rooms must be *"the same height within one floor"*, otherwise "a most inconvenient and ugly occurrence in a house" (F. Barbieri, 'Scamozzi's Orders and Proportions', *Architectural Histories* / EAHN, 2015, translating *L'Idea della Architettura Universale*, 1615).

**A per-room height formula is a misreading of the source.** The three means exist to make heights *equal*, not to make them individual.

The measured evidence agrees flatly. Mount Vernon's ground floor runs 10 ft 7½ in to 10 ft 10⅜ in **for every room except the New Room, which is 16 ft 6 in and two storeys high — the audit flagged that this range silently dropped it, and a two-storey volume is a declared exception to a per-storey rule rather than a refutation of it** — and its chamber floor 7 ft 9 in to 8 ft 2 in, so height/breadth varies from **0.48 to 0.84 across one floor** (Mount Vernon Ladies' Association, "The Mansion Room by Room"). At Brandon — the one Virginia house built from a Morris plate — every principal room is a flat 13 ft, about three feet short of even the flat-ceiling rule *height = breadth* (*Palladiana*, Center for Palladian Studies in America, Spring 2007). And the 1699 Virginia act for building Williamsburg mandates a **"ten foot pitch"** — a legally required *storey* height, in a statute (Hening, *Statutes at Large*, vol. III).

The consequence for a compiler is bigger than a fault about ceilings. Storey height sets the window head, the head sets the daylight depth, and the daylight depth caps the pile. `proportions/systems/room-vernacular.json` writes the arithmetic — `storey_height * 0.78 * 2.25` — and nothing in `massings/` reads it. **Storey height is upstream of plan depth and the corpus has no chain that says so.**

### Third: the square, which is the room's short dimension

Glassie's grammar sets a square first and then adds and subtracts a unit:

> "The unit varied, both traditionally and idiosyncratically it seems, but once the square was set planning became a matter of adding and subtracting units - 30" or 34" or 36" or halves of these"
> — Henry Glassie, *Folk Housing in Middle Virginia* (Univ. of Tennessee Press, 1975), p. 24

> "the square can be four feet less or three feet more than sixteen feet on each side — but there was no compromise at all with the mind's geometry. The space was square." (p. 119)

This corpus reaches the same place from physics rather than from grammar, and its account is better than Glassie's because it says *why* sixteen feet:

> "(1) THE SPAN caps the breadth at what a hewn or sawn joist will carry, about 14-18 ft; (2) THE HEARTH caps the area at what one fire will warm, which in an uninsulated house is roughly 250-320 sq ft; (3) DAYLIGHT caps the depth from the window wall at about 2 to 2.5 times the head height…; (4) FURNITURE sets a floor… The cluster is not a preference. It is an intersection."
> — `proportions/systems/room-vernacular.json`

Both accounts agree that **the short dimension is constrained and the long one is chosen**, and both agree the choosing is done by what goes in the room.

### Fourth: the front line — the hall and the stair, before the flanking rooms

Ware gives the setting-out sequence directly, and it is not the sequence a rectangle-packer uses:

> "The entrance must be into a hall, which, with the stair-case to the right hand, will necessarily take up more than half the extent in front, the door being in the centre, and opening into it… It is easy to see that no more can be done with the front line of the house, placing the stair-case in this manner; and the architect will find, after a thousand trials, that there is no way of placing it so well, even in point of room."
> — Isaac Ware, *A Complete Body of Architecture* (London, 1756), Book III

Ware then sets the hall's breadth at half its length, and only afterwards the flanking rooms. This corpus says the same thing in one line and acts on it nowhere: `rooms/stair-hall.json` states that the straight-versus-dog-leg choice "is therefore a decision about the plan's proportion and not about the stair, and it must be made before the walls are drawn."

### Fifth: the passage — and this is where register is decided

Glassie's finding here is the sharpest single thing in the study and it inverts the corpus's model completely. In the folk grammar the passage is **Y3 — the square minus 2.5 or 3 units. It is a residue.**

> "the hallway, like the old Y1 and Y2 volumes, was the result of subtracting units from the square. Its Y3 dimensions left it narrower than the hallway of the Georgian type as offered in the builder's manuals of the day or as materialized on the grand plantations farther east."
> — Glassie 1975, p. 89

> **The Glassie page numbers need a caveat the audit demanded, because the other WP-9.2 report
> flatly says the rule text could not be established.** Both are right and they read as a
> contradiction. This section's page-numbered Glassie quotations reach the study through Google
> Books snippets and a PhD paraphrase (Rutherford), **not through a continuous reading** — and the
> paraphrase and the study even disagree on how many rule sets there are, eight against nine. A
> page number is the strongest possible signal of first-hand access and none was had. §6 item 4
> states the consequence: **read Glassie before building on Glassie.**

Read that second sentence carefully. **Glassie is naming two populations in one clause**, and the split is *social register*, not furnishability and not latitude. The folk passage is what is left over; the polite passage is deliberately widened until it is a room. That is a decision an architect makes at this point in the sequence, and it changes the whole plan's width.

The corpus's own room record has the two populations right and the mechanism wrong (§3, §4).

### Sixth: the pile — single or double

Two caps, and the corpus has one of them.

The daylight cap it has, and states beautifully: *"a one-room-deep house exists because a room deeper than about 16 ft has a dark back wall, and no amount of candle or lamp made that acceptable when the alternative was to build long instead of deep"* (`room-vernacular.json`).

The structural cap it also has, filed as a descriptive attribute: `massings/catalog.json`, `four-over-four`, `structural_logic` — *"Two rooms deep requires an interior bearing wall, which the stair hall supplies."* HABS confirms it in fabric at Drayton Hall ("two interior brick bearing walls parallel to the northwest and southeast walls") and Gunston Hall ("solid brick walls including all but one interior bearing wall"). `structural_logic` has **zero readers** in `build/` or `mcp_server/` — I grepped.

The roof cap it does not have at all (§4).

Glassie makes double-piling a hard generative constraint rather than a possibility:

> "RULE SET IV: EXPANSION BACKWARD. The extended base structure is doubled to the rear. In the traditional competence this is possible only with XY3X base structures. All others remain conceptually one room deep." (p. 31)

And Upton's finding, at one remove through Camille Wells, is the one that should worry a program generator: the double pile produces **one room more than the social program needed** — "To the fourth room enclosed within this academic European house form Virginians often assigned no special name or explicit function" (Wells, *VMHB* 106, 1998, p. 402).

### Seventh: the doors — position within the room, ranked

Kerr devotes a ranked four-position diagram to it. The ranking, best to worst: **(b)** centre of an end wall; **(c)** the end-wall extremity adjoining the window wall; **(a)** the same side wall as the fireplace, which is what you usually end up with; **(d)** the end-wall extremity next the fire wall, *"a worse position than any other."*

> "When the room is of large dimensions, probably the most convenient position for the door in any case is the centre of one end; if opening from an Ante-room or Saloon all the better." — Kerr 1865, ch. V

That last sentence is the scoping rule this corpus lacks. **The centred end door that makes an enfilade possible is correct for a LARGE room and incorrect for an ordinary one**, where draught and the fireside circle push the door toward a corner.

The corpus states the door-position rule exactly once, for one room — `rooms/butlers-pantry.json`: *"THE DOORS MUST NOT ALIGN… Offset the two doors by at least the width of one door leaf — 32 in — or better, put them on adjacent rather than opposite walls, so the route through is an L"* — and never generalises it.

### Eighth: the bay rhythm, which falls out

> "X components of XY3X houses by prior rules can have one or two central openings; neither of them can be doors, so they must be windows. III.C.2b. For XY3X forms: III.C.2b.1. one window per X. III.C.2b.2. two windows per X." — Glassie 1975, p. 29

That is the generative source of the three-bay and five-bay front, and it is cleaner than any facade-proportion rule. **The facade is an output.**

### Ninth: the service, outside the block

The Chesapeake answer is a separate building of roughly 350–600 sf, at least 20 ft off (Sara Amy Leach, MA thesis, Univ. of Virginia, 1980) and usually the closest of the outbuildings. At the Wythe House: kitchen 33 × 18 ft, 30 ft from the house; laundry 33 × 18, 10 ft from the kitchen; dairy 10 ft from both (Colonial Williamsburg Research Report RR1483). At Sabine Hall, two brick dependencies spaced 162 ft apart. Where the house is grander the route gets a hyphen — Hammond-Harwood's links are 18 ft (HABS MD-251), inside this corpus's 12–20 ft band.

### Last: the trim grade

Hierarchy is read from trim before it is read from size, and service rooms get none. At Stratford Hall the architrave is shouldered in the main-floor passage and crosetted in the Parlour, and *"There are no ceiling cornices in the ground floor rooms"* (HABS VA-307). At Montpelier the grading mechanism is the same profile minus one enrichment: first-floor cornice heavy moulded with a crenelated moulding, "second-floor cornice is similar but without the crenelation" (HABS MD-535).

And the rule that independently corroborates this project's own OQ 50, from a tradition not among the five that produced it: at the Thoroughgood House the fine woodwork of the stair hall *"ascended as far as the first-floor visitors' eyes could see"* (HABS VA-209). **Ornament stops where the visitor's eye stops.**

---

## 2. THE MEASURED EVIDENCE

### 2a. Passage widths

| Building | Date | Passage W | Passage L | Source |
|---|---|---|---|---|
| High Banks, Frederick Co. VA (stone) | c.1753 | 6 ft 8 in | ~24 ft 6 in | VDHR 034-0109 |
| Hundley Hall, Essex Co. VA (**side** passage) | 1840s | 8 ft 6 in | ~24 ft | VDHR 028-0019 |
| Dumbarton House, Georgetown DC | c.1800 | 9 ft 0 in | 38 ft 0 in | period sale notice, Historic Furnishings Plan |
| Cedar Lane, VA (**side** passage) | 1826 | 9 ft 7 in | — | VDHR 063-0005 |
| Mount Pleasant, Shenandoah Co. VA | 1812 | 9 ft 11 in | — | VDHR 085-0072 |
| Long Meadow, Warren Co. VA | 1848 | 10 ft 0 in | 32 ft 0 in | VDHR 093-0006 |
| Oakley, Spotsylvania Co. VA | — | 10 ft 0 in | — | VDHR 088-0052 |
| Thoroughgood House, VA | C17/C18 | 10 ft 0 in | — | HABS VA-209 |
| Mount Pleasant, MD | mid-C18 | 10 ft 11½ in (brick to brick) | — | mountpleasantplantation.com |
| Windsor Castle Farm, VA | — | ~11 ft | ~38 ft | VDHR 300-5033 |
| Montpelier (HO-38), Howard Co. MD | c.1770 | 12 ft 0 in | — | Maryland MIHP HO-38 |
| **Gunston Hall, VA** — *weak* | 1755-59 | 12 ft 0 in | — | *Pittsburgh Post-Gazette*, quoting the museum |
| Wyoming, Caroline Co. VA | c.1800 | 13 ft 0 in | — | VDHR 050-0075 |
| Mount Vernon, VA | 1758-87 | 13 ft 3 in | 30 ft 8 in | MVLA, "Room by Room" |
| Sabine Hall, Richmond Co. VA | c.1729-30 | "nearly 18 ft" | 38 ft 0 in | NHL nomination |

**n = 15 across 15 buildings; two are side passages and are marked. Distribution: 6.67, 8.5, 9.0, 9.58, 9.92, 10.0, 10.0, 10.0, 10.96, ~11, 12, 12, 13, 13.25, ~18. Median 10 ft 0 in.**

**The distribution is continuous. There is no dead zone at 8–9 ft.** Three points sit at or beside it, and one of them — Dumbarton House at 9 ft — is a substantial house with 17–18 ft principal rooms and two-storey brick offices, which chose a 9 ft passage deliberately.

A supporting but weaker line: the VDHR file for Wyoming calls its 13 ft passage *"about four feet wider than is usual,"* putting the usual near 9 ft. That is a state architectural historian's unquantified aside, written in 1980, about a house the same paragraph calls unusual for its outsized proportions. **The honest refutation of the dead zone is the continuous distribution, not that sentence.**

### 2b. Passage share of the facade

Only where *both* figures rest on a defensible source:

| Building | Passage / facade | Bays | Source of both figures |
|---|---|---|---|
| High Banks | 6.67 / 40.33 = **0.165** | 3 | VDHR 034-0109 |
| Mount Pleasant VA | 9.92 / 51.83 = **0.191** | 5 | VDHR 085-0072 |
| Long Meadow | 10.0 / 48 = **0.208** | — | VDHR 093-0006 |
| Wyoming | 13.0 / 55 = **0.236** | — | VDHR 050-0075 |
| Montpelier HO-38 | 12.0 / 48.33 = **0.248** | 5 | MIHP HO-38 |
| Sabine Hall | 18.0 / 60 = **0.300** | **7** | NHL nomination |

**Range 0.165–0.300, median 0.222, mean 0.225.** Weak additions: Gunston Hall 0.197 (5 bays).

Two things follow. **The passage is about one fifth of the front — roughly one bay of five — not one third.** And **the corpus has the bay-count relation backwards**: `faults/passage-that-is-a-corridor.json` assigns the widest share to a five-bay front, while the widest measured share in the sample belongs to the *seven*-bay Sabine Hall and the five-bay Gunston Hall sits at 0.197.

I have deleted Mount Vernon's 0.138 from this table. Its only overall dimension is a Library of Congress *photo caption* ("96 feet long by 30 feet wide") that is arithmetically impossible against a 30 ft 8 in passage running the full depth. A number shown to be impossible should not be carried with a caveat; it should be dropped.

### 2c. A derived rule worth having

**Passage length = external depth − 4 ft**, in all three cases where a source states both:

- Sabine Hall: 42 − 38 = 4.00 ft
- High Banks: 28.33 − 24.5 = 3.83 ft
- Long Meadow: 36 − 32 = 4.00 ft

Two feet per external wall including finish, holding for brick and for stone. Corroborated at Dumbarton House, where a 38 ft passage sits between front rooms 18 ft deep and back rooms 17 ft deep. **n = 3, all masonry, and it must not be extended to frame** — thinner walls make the constant smaller and I have no frame case with both figures.

### 2d. Room shapes

Of **27 single rooms across 11 buildings** with both dimensions stated: minimum 1.015, median 1.154, maximum 1.464, mean 1.185. Ten of 27 are within 10% of square. **Not one reaches 3:2.**

> **CORRECTION (WP-9.2 audit, 1 Sep 2026).** Those three statements cannot all hold together with the paragraph's own enumerated members. The eleven Mount Vernon rooms listed below include the **Central Passage at 2.314**, and the next sentence names High Banks's double room at **1.80**. So "maximum 1.464" and "not one reaches 3:2" are true only of the SINGLE, NON-CIRCULATION rooms — which is what "27 single rooms" was reaching for and did not say. Read the summary as: *of the single habitable rooms, none reaches 3:2 and the maximum is 1.464; the passage and the double room are outside that population by definition and are listed separately below.* The corrected reading strengthens the section's point rather than weakening it, because a passage at 2.314 is exactly Scamozzi's "beyond two squares … passageways rather than rooms to live in". The only room in the set above 1.5 is High Banks's "living room," explicitly a double-size room the depth of the house (13 ft 7 in × 24 ft 6 in) — two rooms thrown into one.

**A caution the adversarial pass caught and I am repeating because it matters: eleven of those 27 rooms are Mount Vernon, from one MVLA page, and two of the five studies counted them independently.** Two reports agreeing to 0.01 reads as replication and is one source counted twice. The genuinely independent American evidence is roughly sixteen rooms across ten buildings, several from sale advertisements rather than survey.

Mount Vernon's eleven, for the record: New Room 1.341, Front Parlor 1.015, Little Parlor 1.288, Central Passage 2.314, Old Chamber 1.154, Dining Room 1.133, Study 1.164, Blue Room 1.214, Lafayette Room 1.029, Chintz Room 1.107, Washingtons' Bedchamber 1.267.

### 2e. Ceiling heights

Ground: Mount Vernon 10 ft 7½ in – 10 ft 10⅜ in; Mount Pleasant VA 11 ft 1 in; Graeme Park "the story near 13 feet high" (period advertisement, HABS PA-579); Brandon 13 ft; Williamsburg Public Records Office 10 ft 10 in; Robert Carter's Williamsburg house 11 ft parlour and passage, 10 ft stair (Carter–Bladon correspondence, CW RR1604); Hundley Hall 9 ft 4 in.
Chamber: Mount Vernon 7 ft 9 in – 8 ft 2 in; Hundley Hall 8 ft 9 in; Woodlawn MD 10 ft 4¼ in.
Garret: Mount Vernon 7 ft 4 in.

**The upper storey is markedly lower than the lower.** At Mount Vernon the chamber floor is 0.744 of the ground passage's height and the garret 0.690. A Chesapeake gentry house of the 1770s–80s runs roughly 10 ft 6 in over 8 ft, not 10 over 10.

### 2f. What the numbers show, and where they scatter

They **converge** on: rooms close to square; ceilings flat per storey and stepping down by storey; the passage at about a fifth of the front; masonry walls about 2 ft and their foundations 28–30 in.

They **scatter** on: passage width, which runs 6 ft 8 in to 18 ft with no gap and no clean predictor. Register predicts better than latitude — High Banks in the Shenandoah is 6 ft 8 in while Tidewater Gunston Hall is 12 ft — but n = 15 cannot settle it, and the two widest passages sit on two of the widest facades, so absolute width and facade share move together and I cannot say which the builders were setting.

And a corrective worth carrying: **two of the greatest Chesapeake houses have no proper centre passage at all.** Westover: *"Plan - OFF CENTER through hall"* (HABS VA-402). Shirley: *"There is no hallway in the usual sense of the word, the stairhall being the architectural feature of the house"* (HABS VA-388). Stratford Hall is H-plan; Tuckahoe is H-plan. A compiler treating "Tidewater Georgian" as implying a symmetrical central passage will misdescribe four of the family's most famous members.

---

## 3. WHERE THIS CORPUS IS RIGHT

It should be said plainly: the architectural writing in this repository is better than the architectural writing in most of the secondary literature I read to check it. Four things in particular.

**The four-caps intersection is the best piece of reasoning in the corpus, and its corollary is the best sentence.** From `proportions/systems/room-vernacular.json`: *"The cluster is not a preference. It is an intersection."* And then: *"Two of those three are gone — engineered lumber removed the span limit, central heating removed the hearth limit — and the third is not gone and never will be, because it is optics."* That is a genuinely generative claim, it explains why the vernacular band is *narrower* than the treatises, and it is the argument I would build the next work package on. (Its number needs re-calibration — see §6 — but the argument does not.)

**The daylight corollary about the back rooms of a double pile.** *"This is why the back rooms of a double-pile plan are the service rooms, the closets and the stairs, and why putting a principal room there is a mistake that no amount of glazing on the end wall fixes."* Nothing in Kerr, Ware, Palladio or Glassie says this as well.

**The passage's bimodality.** `rooms/centre-passage.json`'s `critical_dimension` is right in kind and it is right for a better reason than it gives: *"SIX TO SEVEN FEET is a passage that circulates… TEN TO TWELVE FEET is a passage that is a room… Decide which of the two it is, because the answer changes the plan's whole width."* Glassie independently names the same two populations (p. 89) and names the axis the corpus does not — social register. The corpus reached the right architectural conclusion from furnishability; the source reaches it from the builders' manuals versus the folk grammar.

**The room is not the bay.** `room-vernacular.json`'s module note: *"the bay is a framing dimension measured centre to centre of the bents, and the room is what is left inside it after the frame, the partitions and the chimney have taken their share… confusing the two is why reconstructed plans so often come out a foot too generous."* Correct, and it is also the missing link between the parti's 9 ft facade bay and the massing's 16 ft structural bay, which this corpus currently carries under one word with no stated relation.

Two smaller ones. `rooms/butlers-pantry.json`'s L-shaped route is Kerr's door rule, independently derived, one room at a time. And the honesty in `room-vernacular.json`'s authority note — *"Nothing here is quoted from a source because there is no source to quote"* — is exactly the OQ 18 discipline working, and it is why I trust that pack's reasoning even where I distrust its numbers.

---

## 4. WHERE THIS CORPUS IS WRONG OR MISSING

### 4a. WRONG — statements that contradict a source, a measurement, or another file

**W1. The proportion lower bound, and it is the largest single defect in the plan layer.**
Verified by script against the working tree: **35 of 60** room records carry a proportion floor above 1.0; **13 of 23** habitable rooms do; and that 13 includes *every room in the `public` class* — `best-parlor` [1.1, 1.4], `parlor` [1.1, 1.45], `drawing-room` [1.25, 2.0], `hall` [1.3, 2.2] — plus `dining-room` [1.15, 1.8], `library` [1.1, 1.6], `music-room` [1.2, 1.7].

No period source in this study states a minimum. Morris: *"the nearer a Room (in particular a Hall) is to a Square, the more uniform and commodious they will be"* (*Lectures on Architecture*, 1734, Lecture VII). Palladio's list begins at the circle and the square. Scamozzi assigns the square to drawing rooms and the 2:1 to antechambers. Kerr's own recommended bedroom sizes include 16 × 16 and 20 × 20.

**Attribution corrected by the audit: in Morris's Lecture VII the grammatical subject of that sentence is PALLADIO** — Morris is reporting *"Palladio has observ'd, that there are seven beautiful Proportions"* and the preference for the square sits inside that report. So Morris is not an INDEPENDENT English witness to the rule; he is Palladio at one remove, and the two must not be counted as two sources. The argument that **no source found states a MINIMUM** is unaffected — nothing here states one — but the corroboration is thinner than an earlier version of this text implied.

The bands convict: Mount Vernon's Front Parlor 1.015 against `best-parlor` [1.1, 1.4]; its Dining Room 1.133 against [1.15, 1.8]; Graeme Park's 23 × 22 principal parlour 1.045 against `parlor` [1.1, 1.45]; a 19-ft-square Williamsburg front room against the same; an 18-ft-square Maryland hall against `hall` [1.3, 2.2]. **Nothing measured fell above a band.** The upper ends are never reached by the evidence and the lower ends convict real rooms.

**W2. Four statements of the passage width, four different floors.**
- `rooms/centre-passage.json`: `width_ft [6, 14]`, prose floor 5 ft 6 in
- `groupings/centre-passage-core.json`: **hard**, "Passage width 8 to 14 ft… Below 8 ft the stair cannot turn"
- `proportions/systems/room-vernacular.json`, via the fault's own citation: default 6 ft, range 3–10 ft
- `faults/passage-that-is-a-corridor.json`: `passage_clear_width_ft at-least 8.0`, whose **own note** reads *"8 ft for a formal centre-passage plan and 6 ft for a northern vernacular one"* — a conditional the unconditional test cannot express

Any check enforcing 8 ft convicts the northern passage the room record calls correct, and convicts High Banks at 6 ft 8 in. The corpus is currently wrong in *both* directions at once.

**W3. "Roughly one third of a five-bay front."** `faults/passage-that-is-a-corridor.json`, `rule_violated[3]`, and repeated in `correct_practice`: *"12 to 14 ft on a 42 to 48 ft front."* Measured share is 0.165–0.300, median 0.222. A third of a 42–48 ft front is 14–16 ft — wider than every passage in the sample **except Sabine Hall's "nearly 18 ft"**, which the audit noted this sentence had overlooked; the clause about the state historian's exceptional case (Wyoming, 13 ft) stands. Delete the figure. `centre-passage-core`'s 0.18–0.27 is the defensible number and it sits one file away.

**W4. `passage_width_ft / facade_width_ft` as a hard *generative* test.** Right band, inverted causation. See §0 and §5.

**W5. The dining room's 12 ft floor, against the source the record itself names.** `rooms/dining-room.json` lists *"Kerr, The Gentleman's House, 1864"* in its `sources`, reproduces his furniture arithmetic (40 + 2×36 + 2×18 = 148 in) and sets `width_ft [12, 18]`. Kerr states that arithmetic and then declines to accept its answer as a room: *"A small Dining-room ought never to be less than 16 feet wide; from 18 to 20 feet is a full width; beyond this is almost matter of state."* The slack is the sideboard end, the fireplace and the service space.
**Do not simply raise the number** — Kerr's 16 ft describes an English gentleman's house with a sideboard and a served course. The correct fix is to say which establishment a band is conditioned on.

**W6. `door_centreline_offset_in at-most 3`, hard, in `groupings/public-enfilade.json`, citing Kerr.** No source anywhere gives a numeric alignment tolerance. Kerr rejects the geometry twice: *"To have the two doors directly opposite to each other across the Corridor is almost worse"* (p. 168), and of serial doors along the window wall, *"Both these ideas would be held objectionable now."* The measured evidence runs the other way — Thoroughgood's passage doorways are recorded as *"not quite in alignment or on center"*, and Graeme Park's mutually aligned doors sit about **3 feet** off the facade centre. The enfilade is real as a Baroque state-apartment device where depth along the axis equals rank (V&A, "Inside the Baroque palace"); scope it there or it will convict correct English and American plans.

**W7. Two incompatible ridge ratios for the same relation.** Verified by enumerating every grouping test: `georgian-service-core` carries `wing_ridge_ft / main_ridge_ft at-most 0.85`, **hard**; `dependency-and-hyphen` and `garage-and-hyphen` both carry `dependency_ridge_ft / main_ridge_ft between 0.6 and 0.8`, **hard**. A wing at 0.82 satisfies one and violates the other. Neither is sourced.

**W8. The coffin set the parlor's dimension.** `rooms/parlor.json` states *"THE COFFIN, WHICH IS THE DIMENSION NOBODY WRITES DOWN AND WHICH SHAPED THE ROOM."* The arithmetic is fine and the funeral was in the parlor. The *causal* claim is unsourced and I doubt it: 13 × 16 is what span, hearth and daylight produce for any principal room of the period, by this corpus's own reasoning three files away. The coffin fits because the room is that size. The record carefully calls the "coffin corner" folklore and then commits the same error one level up.

**W9. `adjacency.never_a_through_room` is FALSE on `dining-room` and `drawing-room`** (verified: 21 true, 39 false, all 60 present). Kerr names exactly those rooms: *"the Dining-room, therefore, even the Drawing-room, the Library frequently, deprived of all privacy."* The American withdrawing door probably makes the flag defensible — but then it means "may legitimately carry the withdrawing route," not "is not a thoroughfare," and the corpus does not say which.

**W10. Unsourced hard numbers, as a class.** Also verified by enumeration: `hyphen_length_ft between 12 and 20`; the covered way *"not more than about 40 ft — beyond that the food arrives cold"*; `entry_rise_in between 14 and 42`; `threshold_count at-least 2` with no definition of a threshold, in a grouping whose next rule says three doors in a row is "one threshold repeated"; `passage_share_of_facade`. Each carries a source for the *idea* and none for the *number*. `entry_rise_in` is additionally falsified by the corpus's own raised cottage, Charleston single house and any house on a raised basement.

### 4b. ABSENT — what a period builder would need that is nowhere stated

**A1. The circulation system as an object.** Kerr designs it first: *"THE THOROUGHFARES… These the skeleton of plan."* A plan record should name its spine, name each branch, and state which branch every room opens off; a room naming no branch should be a defect, not a room to place later. WP-9.2 already measured the cost of the absence.

**A2. The storey → head → depth → pile chain.** The arithmetic is authored in `room-vernacular.json` and no massing reads it.

**A3. The roof as a depth cap.** I grepped `massings/`, `rooms/`, `groupings/`, `partis/` and `docs/`: **no M-roof, no double roof, no valley gutter, no relation between plan depth and ridge height anywhere.** A 40 ft deep block under one gable at 9:12 carries its ridge 15 ft above the eave. The period answers are the hip, the gambrel, the mansard and the M-roof. The corpus knows half of it and files it as a fact about the roof: `gambrel-block`'s `structural_logic` is *"The break in slope allows a shorter rafter run and a usable upper floor without a full second-storey wall …"* — which is the roof answering a depth problem. **The ellipsis matters and the audit added it**: the record continues *"a tax and material advantage as much as a spatial one"*, which is the record's own statement that the driver is not primarily spatial. Quoting only the first half made the record agree with this section more than it does.

**A4. Privacy as a route-crossing count over two populations.** Modelled as a per-room integer (`privacy_rank`, `privacy_span`). Kerr's test is symmetrical and it is a count: *"let the family have free passage-way without encountering the servants unexpectedly; and let the servants have access to all their duties without coming unexpectedly upon the family or visitors. On both sides this privacy is highly valued."* Note also that Kerr uses one word for two quantities — for the family it is seclusion, for the servants it is *"freedom from interruption"* — and they are not interchangeable.

**A5. Door position within a room, generalised.** Kerr's four ranked positions, plus the large-room exception, plus the bedroom rule (*"a straight line from door to fire shall not cross the bed"*), plus the count rule (*"too many doors… must seriously interfere with the fire-side circle"*), plus the per-room-type asymmetry: a door on the fireplace wall is *"generally fatal to a Sitting-room"* and tolerable in a dining room. That last is exactly the shape this corpus wants — identical geometry, a fault in one room and not in another.

**A6. Aspect arbitration.** Sixty of sixty rooms carry an `orientation` string; `build/compose.py:1191` logs *"Editorial, not yet computed into the plan's own orientation."* Kerr arbitrates once, with a single Aspect-Compass, for the whole house. Sixty preferences with no arbiter cannot be satisfied and cannot report which room lost.

**A7. Central stack and through passage as alternatives.** `massings/catalog.json` pairs `hearth: central-stack` with `circulation: central-chimney-lobby` three times and `gable-end-paired` with `center-hall` in every passage type — three instances of the pairing and no statement of the mechanism. A central stack occupies the middle bay; therefore there is no through passage. The corpus knows the fact and files it as history in `rooms/centre-passage.json`.

**A8. The stair hall as the interior bearing line.** Written in `structural_logic`, read by nothing.

**A9. The circuit.** Where reception rooms form a *loop*, Kerr's index records that a corridor is *"not essential"* (p. 196). `public-enfilade`'s hard rule forces exactly the redundancy a loop removes. The corpus has no word for a loop; "circuit" appears in the room records only in the electrical sense.

**A10. `critical_dimension` parsed by nothing.** The length generator is authored on all 60 rooms as arithmetic and read as prose. This is the single highest-leverage change available in the whole plan layer: the arithmetic is already written and already correct.

**A11. `room-harmonic.json`'s suite rule has no `quantity`.** It is the only one of the pack's eighteen derived rules without one — verified — so nothing that dimensions a room can ever read it. Its content is the enfilade's actual dimensional rule and the corpus's only compositional proportion rule: *"in a suite, hold the BREADTH constant and vary the length, so that the doors on the enfilade axis all sit at the same relation to the walls and the ceiling heights step in a series rather than jumping."* Retargeting it is a one-line change.

**A12. The night plan.** Sixty `daylight` blocks, zero firelight blocks. `rooms/dining-room.json` makes the observation and then ignores it: *"A dining room is used more by candle and lamp than by daylight, which is why it tolerates a deeper plan position"* — followed by a `depth_multiplier` of 2.0. `rooms/keeping-room.json` comes closest to the missing model: *"THE RADIANT REACH OF THE FIRE, AND IT IS 10 FT… beyond that the fire is a light source."*

**A13. A fault for two rooms on one storey with different ceiling heights and no declared reason.** The best-sourced positive rule in the study has no checker.

---

## 5. IS THE MODEL RIGHT?

**No — and the diagnosis is precise. An area band plus a width band plus a proportion band plus adjacency edges is a good CHECKER and a bad GENERATOR, because a band carries no direction of causation.**

The evidence is already in this repository. WP-9.2 recorded a kitchen placed 10 × 30. Against `rooms/kitchen.json`: area 300 sf sits comfortably inside `area_sf [120, 340]`; width 10 ft sits exactly *on* the `width_ft` floor of 10; ratio 3.00 breaks `proportion [1.05, 1.8]` by 67%; length 30 ft breaks `length_ft [12, 22]`. The library at 10 × 24: 240 sf inside `area_sf [180, 600]`, length 24 inside `[15, 30]`, ratio 2.40 against `[1.1, 1.6]`, width 10 against `width_ft [13, 22]`.

**Area was satisfiable at any shape, so area is what the generator satisfied.** Four bands over two free variables is an under-determined system, and any of a thousand rectangles satisfies it. The tradition never had that freedom, because it never chose two numbers at once.

### What the right model is

The corpus states it, in English, in one sentence of `room-vernacular.json`. Written as a chain:

1. **Establishment** → whether there are two populations, which sets the *kind* of the service rule and the *conditioning* of every furniture-derived band.
2. **Storey height** → per floor, never per room. → **window head** ≈ 0.78 × storey.
3. **Breadth** ← `min(span cap, daylight depth from head, hearth reach)`. Constrained, not chosen.
4. **Depth / pile** ← daylight depth, the availability of an interior bearing line, and the roof.
5. **Front line** → hall and stair sized first; then the passage, as residue (folk) or as a room (polite) — a *register* decision.
6. **Length** ← each room's own `critical_dimension` arithmetic. Chosen, by what has to go in.
7. **Height per room** ← the storey's, by one of Palladio's three means, chosen so the floor comes out level.
8. **Doors** → position within each room, ranked against fire and window; branch assignment against the spine.
9. **Facade** ← *result*. Bay count falls out of the door-and-window rule.
10. **Bands** → the TEST on the result. Never the input.

### How far the study supports this

**Strongly, on the direction of causation.** Five independent sources — Glassie's subtract-from-the-square, Ware's front-line-first, Palladio's-and-Scamozzi's height-per-floor, Kerr's thoroughfares-first, and this corpus's own four-caps intersection — all describe a sequence of commitments in which each step removes freedom from the next. None describes simultaneous band satisfaction.

**Weakly, on the numbers.** The 2.25 daylight multiplier is a modern office heuristic out of calibration for this latitude and this glazing (§6). The 1.25 central ratio is the corpus's own estimate and says so. The four caps are an *argument*, not a measurement — no one has measured the joist span, the hearth reach and the daylight depth of the same house.

**So: the study settles the shape of the model and does not supply its constants.** That is an honest and useful place to be, and it means the next work package is a *restructuring*, not a re-fitting. Do not let the restructuring smuggle in numbers it has not earned.

One further consequence worth stating. **The rectangle-with-rooms-in-it model cannot express two things the tradition does constantly**: "the passage is what is left over," and "the facade is a result." Both are *derivations*, and a placement search has nowhere to put a derived quantity. That, and not the search's weakness, may be why the heuristic engine keeps producing rooms nobody can reach.

---

## 6. WHAT MUST NOT BE CODED YET

**1. Any tolerance calibrated on "64% of Palladio's rooms match a canonical ratio."** The citation (NNJ 2019, DOI 10.1007/s00004-019-00445-4) is real and the quotation is verbatim, but the paper's ratio set is **every p:q with q ≤ 9, explicitly including ratios above 2** — not Palladio's seven shapes. The true match rate against the seven is necessarily lower. A nearest-shape-with-percentage-error *report* is a good design idea; ship it with **no pass/fail threshold at all** until the rate against the seven is re-derived from the paper's own tables.

**2. Brandon's 1.417 entry hall.** Three problems compounding: the source is a learned-society newsletter, not peer-reviewed; the study's own arithmetic on the newsletter's figures gives 1.4167 where it prints 1.412; and the Virginia DHR register entry (074-0002) states *"The hall was remodeled in the early-19th-century, when the present arcade and stair were installed."* It is the study's most quotable number and it should not leave this document.

**3. Any statistic that treats the two measured datasets as independent.** Eleven Mount Vernon rooms appear in both, from one page.

**4. Glassie's folk passage of 6 to 8.5 ft.** The agent's own multiplication, combining a definition from a Glasgow PhD paraphrase with a scale from a Google Books snippet of a different page — in a book nobody in this study read continuously. The paraphrase and the agent even disagree on how many rule sets there are (eight versus nine). **Read Glassie before building on Glassie.**

**5. The 2.25 daylight multiplier as a hard generative cap.** The underlying rule carries five preconditions — clear glazing, window width about half the perimeter, overcast or north sky, high interior reflectance, no external obstruction — and is validated near 51° latitude; the same literature gives 1 to 2 for a window with blinds. Virginia is 37°, and an eighteenth-century window has shutters, small panes and low transmittance. Keep the four-caps argument as an explanation. Do not let it assert a depth for every room the system draws.

**6. Kerr's dimensions transplanted into American vernacular records.** His 16 ft dining room is verified and it genuinely embarrasses a corpus that cites him for 12 — but importing it into a farmhouse repeats the study's own diagnosed error one level up. Condition the band; do not raise the number.

**7. Anything attributed to Upton 1982, Wenger 1986, Girouard 1978 or Franklin 1981.** All four verified as citations, none read by anyone in this study. Wenger is *the* paper on the central passage, and the entire furnished-passage claim and the post-1750 widening chronology reach us at second and third hand. Upton's "social molecule" adjacency rule — which one pass called *"a directly codable adjacency rule"* — is a **figure caption in a secondary source** summarising a paper nobody has opened.

**8. Serlio's dissent as stated.** The agent's own verdict — *"the least secure item in this report"* — is right, and the confidence in the prose does not match it.

**9. The ergonomic floors presented as measured**: 5 ft 6 in for two people passing, the 20 in chair down a passage wall, 42 in for two abreast, `ceiling_min_ft: 9` on the passage, the room-record `depth_multiplier` of 2.25. Reasonable modern derivations, none a historical measurement. Kerr's *actual* plotting allowances are verified and available — table 4–6 ft, 20 in per seated person each side, 24–30 in of table length per person, 2½–6 ft of passage behind, 20 in for a chair's projection — and they should be used, named as his, rather than unattributed numbers of the same shape.

**10. Mount Vernon's 0.138 facade share and Gunston Hall's 12 ft passage.** The first is impossible; the second is a newspaper travel feature, for one of the study's most-cited buildings.

**11. The studies' own checker specifications.** Four of the five ended by proposing testable rules. They are good ideas and they are *the agents' reading*. If any is built, its note must carry `judgment: true` and must not inherit the confidence of the period quotations sitting beside it in the same report.

**And one method finding, which belongs here because it will recur.** One pass recorded under *what I could not establish*: "Whether Kerr states a general numerical rule for corridor or gallery width… I could not surface a width figure." Kerr states it plainly — *"we may consider any width from 6 to 12 feet as belonging to a Corridor; the suitable width for a Gallery being from 14 to 20 feet"* — and another pass had it. **An agent's "not in the source" is a search result, not evidence of absence, and it must never be recorded as a fact about a source.** That is the same failure mode as WP-8.6's guards that could not fire, one layer out: a negative claim nobody could falsify.

---

## 7. THE QUESTIONS FOR LUCAS

Real ones. Each is a ruling only an architect can make, and each blocks a specific piece of work.

**Q1. Is REGISTER a first-class axis, or is it style?**
Glassie names two passage populations and the axis is folk versus polite — the builders' manuals against the field. This corpus has `style` and it has no register. The same house type at two registers wants different passage widths, different trim grades, different service arrangements and different dining-room floors. If register is an axis, a good deal follows (including the fix to the dining room and the fix to the passage). If it is not, say what carries it instead.
*Proposed slug if this becomes a question: `oq/register-is-not-style`.*

**Q2. Do you accept that the facade is a result?**
If yes, `groupings/centre-passage-core.json`'s hard test inverts, `faults/passage-that-is-a-corridor.json`'s "size the passage from the facade" is wrong in its `correct_practice` as well as its number, and the bay rhythm becomes derived rather than declared. If no — if you hold that a Georgian designer really did set the front and divide it — then the study is wrong about the ordering and I want to know what you are reading that Glassie and Ware are not.

**Q3. The proportion floors: remove, set to 1.0, or replace with a direction?**
Three options and they are not equivalent. Removing the floor means a 1:1 room is silent. Setting it to 1.0 means the same thing but keeps the field shape. Replacing it with a *direction* — "this room wants to be square; report distance from the square" — is what the sources actually say, is what Kerr's, Morris's and Scamozzi's rules all encode, and would let the checker say something useful about a 1.9 parlour without pretending 1.05 is a fault. My reading favours the third; the choice is yours because it changes what a `proportion` field *means* in 54 records.

**Q4. Which establishment is a band conditioned on?**
Kerr's dining room is 16 ft because it has a sideboard, a served course and a serving room. A farmhouse dining room at 13 ft is not a fault. The corpus has one band per room and no way to say "conditioned on a served dinner." Does the room record get an establishment axis, or does the *fault* get an `applies_when` on the establishment — the mechanism WP-5.13 already built for measurements?

**Q5. Is the ordering the compiler's architecture, or only its explanation?**
Glassie is explicit that his rule sets are order-independent and reversible: *"It may start at any point, take any route, and yet come to the same end."* So the sequence in §1 may be how a builder narrates a decision rather than how the constraint system resolves. Do you want a *pipeline of commitments* — which is simple, matches the sources' narration, and cannot backtrack — or a constraint system in which the ordering is only how findings are explained to a reader? This decides whether §5's chain is code or documentation.

**Q6. Will you take the ceiling-height fault?**
"Two rooms on one storey with different ceilings and no declared reason" is the best-sourced positive rule in the study — Palladio's own stated reason for three means, Scamozzi verbatim, Mount Vernon and Brandon measured. It is also a fault this corpus can raise today with no new measurement. Yes or no.

**Q7. What is the enfilade's scope?**
The rank-graded Baroque state apartment is real and the aligned doors are its point. The English corridor plan rejects the geometry outright, twice, in the source `groupings/public-enfilade.json` cites. Does the American double parlour with sliding doors count as an enfilade, or as its own thing? Until this is ruled the grouping will convict correct English and American plans.

**Q8. What does `never_a_through_room: false` mean on the dining room?**
"May legitimately carry the withdrawing route," or "no opinion"? Right now a reader cannot tell, and 39 of 60 rooms carry the value.

**Q9. Does the roof get a vote on plan depth?**
Nothing in the corpus relates the two. If the answer is yes, the gambrel, the hip, the mansard and the M-roof stop being style choices and become answers to a depth problem — which is what `gambrel-block`'s own `structural_logic` already says. If no, then say why a 40 ft double pile may take any roof form it likes.

**Q10. Will you fund reading Wenger 1986 and Upton 1982 properly?**
They are behind JSTOR and the University of Chicago Press. The entire furnished-passage claim, the post-1750 widening chronology, and the "social molecule" adjacency rule flow from them at second and third hand. This is the same class of gap as OQ 7–11: the honest state is *environment-blocked*, not *established*. Two articles would settle more of the plan layer than any amount of further HABS mining — and HABS written data, I should say plainly, is a **poor** source for room dimensions. Of about a dozen reports read across five states, almost all give only overall building dimensions. The room figures live on the measured *drawings*, which are raster images, and in period sale advertisements and insurance policies quoted inside modern nominations — which turned out to be the richest seam in the whole study and is worth mining deliberately.

---

## WHAT COULD NOT BE ESTABLISHED

Stated plainly, because the difference between a study and an opinion is this list.

- **Salmon's Plate K.** *Palladio Londinensis* (1734) is the manual most often documented in American builders' hands, and its chapter *"Of the Proportions of Rooms, as to Length Breadth and Height"* is the only room-proportion chapter in the English carpenter's literature anyone could identify. The heading survives in OCR; the four designs are destroyed. This is the highest-value unrecovered item in the study. (Note also that Wells cites a 1748 edition where the study used 1734.)
- **Glassie's nine rule sets, read continuously.** Recovered only through Google Books snippets and a PhD paraphrase that disagrees with the study on the number of rule sets.
- **Kerr's Aspect-Compass.** He names it, places it at p. 81, and says it governs every aspect argument in the treatise. The OCR returns the prose around it and not the diagram. Anyone coding an aspect arbiter needs that page image.
- **Whether Sabine Hall's "nearly 18 feet" hall is original to c.1729–30.** It is the single most load-bearing outlier in the passage distribution, and an 18 ft passage in 1730 sits awkwardly against the post-1750 widening chronology.
- **A statistically defensible distribution of passage widths.** Fifteen figures, opportunistically gathered from whichever surveys happened to state a width in machine-searchable text, biased toward listed and substantial houses. Enough to refute a claimed gap. Not enough to publish a band, a mean or a percentile.
- **Whether the "passage length = depth − 4 ft" rule holds for frame.** All three cases are masonry.
- **Whether the 1.0–1.35 clustering is characteristic of the tradition or of Mount Vernon.**
- **A period American equivalent of Kerr** — a text stating plan principles as a system rather than presenting plates. Looked for; not found. This corpus's plan layer is, in practice, built against two English books, one of them Victorian, and it should say so.

---

*Corpus figures in this document were re-measured against the working tree on 1 Sep 2026 by script, not quoted from the studies: 60 room records, 54 carrying a proportion band, 35 with a floor above 1.0, 13 of 23 habitable, 21/39 on `never_a_through_room`, and the full enumeration of grouping tests. The architectural quotations are as verified by the adversarial pass; where a quotation reached us at one remove, the document says so at the point of use.*
