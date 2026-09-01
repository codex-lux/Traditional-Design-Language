# WP-9.2 — The precedents, measured: the parti is not the type

*Status: the text-first half of WP-9.2 is done and this is its report. The image half — the
transcription of measured sheets into `plans/precedents/` — still waits on the batch Lucas
downloads; `Plan Examples/HABS/WANTED.md` is the list.*

*This report had a sentence here saying a parallel study of the compositional literature was
"running as this is written" and that its synthesis "will be appended". **It landed, and it was
not appended.** It has its own report, `docs/reports/wp-9.2-what-the-tradition-actually-does.md`,
because it is long and it is differently sourced — this one works from HABS written data and the
code, that one from the treatises and the state-register files. **They were produced by different
routes and they agree everywhere they touch**, which is the useful fact about having two. The
sentence is replaced rather than deleted because "X will be appended when it lands" is exactly the
promise WP-6.4 found eleven of, unkept, across source, schema and docs.*

Lucas read a `tidewater-georgian-careful` sheet on 1 Sep 2026 and listed seven incoherences,
then said what he thought was wrong with the process: *"it's still being procedurally generated
at a lower level than the idiom, which, when put together, doesn't actually make sense at a
higher literary level … the unit of room organization is already established, and you're playing
with units at a higher level of sense-making."* He asked for the program to be measured against
real, fully laid-out plans of the period before any more code was written. WP-9.4 did not do
that — it did code archaeology and got a negative result. This does it.

**The finding is that the diagram is wrong, not the search.** `centre-passage-double-pile` names
eleven enclosed ground-floor rooms and a porch, and the plan built from it places twelve enclosed
spaces. Its own three named exemplars have six apiece, in the same or a larger footprint. Every
sliver on Lucas's sheet is what happens when you cut six rooms' worth of compartments into twelve. The tradition's answer to the same pressure is written in the corpus
already, in the massing record's own `expansion_logic` field, and nothing reads it.

**The second finding is a measurement of the consequence.** Lucas asked, mid-study, that furniture
be studied too — *"I don't think furniture layout should govern room sizes, but some room sizes
are awkward or entirely impossible to effectively furnish."* The corpus already takes that exact
position and already implements it, well. But the furniture check reads the **declared** record and
never the drawing, so: over all sixteen plans, **50 of 231 placed rooms — one in five — cannot hold
an essential piece of furniture that their own declared record can, and not one of those is
reported.** Eight of the thirteen dining rooms in the corpus fail their own dining table. §8.

---

## 1. The route: loc.gov is reachable after all

`build/harvest_habs.py` has been queued since WP-4.4 against a proxy that answers 403 to CONNECT
for www.loc.gov. That is still true of the plain proxy. **It is not true of the Tavily MCP tier**,
which reaches loc.gov and — more usefully — `tile.loc.gov`, where the HABS *written historical and
descriptive data* PDFs live. Those are text, not images: they carry overall dimensions, floor-plan
descriptions room by room, structural systems and fenestration counts, and they extract cleanly.

The URL is derivable from the item id:

```
https://tile.loc.gov/storage-services/master/pnp/habshaer/<st>/<st>NN00/<item>/data/<item>data.pdf
```

`va0433` is Gunston Hall, `sc0132` Drayton Hall, `md0035` Hammond-Harwood, `va0313` Shirley,
`va0892` Mount Airy, `va0315` Westover. One
extract does not return the whole document — re-query the same URL with a different `query` string
and a different span comes back. That is a property of the extractor, not of the file, and an
agent that queries once and concludes "the report does not say" is wrong.

**This does not close OQ 7–11 or OQ 18's source half.** Those need legible *facsimiles* — the
plates themselves — and this is prose about the plates. It does mean the arrangement half of the
precedent work can proceed now, without waiting on a download.

## 2. What the exemplars actually measure

`partis/centre-passage-double-pile.json` names Drayton Hall, Hammond-Harwood and Gunston Hall.
All three are in HABS. All three are quoted here verbatim from the written data.

| Building | HABS | item | Main block | Bays | ft/bay | Gross/floor |
|---|---|---|---|---|---|---|
| Drayton Hall, 1738–42 | SC-377 | `sc0132` | 70'-5" × 52'-2" excl. portico | 7 | 10.06 | 3,674 sf |
| Gunston Hall, 1755–59 | VA-141 | `va0433` | 60'-10" × 40'-11½" | 5 | 12.17 | 2,492 sf |
| Hammond-Harwood, 1774–77 | MD-251 | `md0035` | approx. 44' × 42' | 5 | 8.80 | 1,848 sf |

> Drayton Hall: "Rectangular, with projecting portico on the southwest (land) facade; 70'-5" x
> 52'-2", excluding portico; 7-bay front; 2 stories plus raised basement."

> Gunston Hall: "The mansion is a rectangle of [4]0 feet 11-1/2 inches by 60 feet 10 inches,
> exterior foundation measurements." (The OCR renders the leading 4 as `h`.) Its front is five
> bays: "There are four large windows on each of the north and south facades, with a pair of
> smaller windows flanking the main doors" — two large each side of a tripartite centre — and
> "The north and south facades have five dormer windows each."

> Hammond-Harwood: "The two-story main block is approximately 44x42', the end wings are about
> 34' x l8, and the connecting links are 18 long." / "Central portion five bays wide."

Observed bay module: **8.8, 10.06, 12.17 ft.** The parti declares `bay_module_ft: 9` — inside the
observed range, at its low end. That is defensible and is not the problem.

**Two more of the exemplars WP-9.2 was told to gather, and both say the same thing as the first
three.**

> **Mount Airy**, HABS VA-72 (`va0892`), c. 1758: "**5-part plan, with main house, covered
> passageways and flanking dependencies**; main house is 2-story, 7-bay front; passageways are
> 1-story; dependencies are 2-story, 3-bay fronts." The survey calls it "the earliest known full
> Palladian villa constructed in the American colonies."

> **Westover**, HABS VA-402 (`va0315`), c. 1726: "Brick, Flemish bond; two stories; hipped roof;
> two chimneys each end; **front seven bays** … **Plan — off center through hall; pair of large
> rooms toward east; smaller rooms toward west** … **The house has balancing wings**." Its kitchen
> is a separate HABS record, VA-402-A, "Westover, Kitchen Building".

Five houses, and **all five put their service outside the main block** — a detached kitchen
(Gunston Hall, Westover), a raised basement (Drayton Hall), or flanking dependencies on hyphens
(Hammond-Harwood, Mount Airy). Not one of them holds a kitchen, a pantry and a breakfast room in
the same rectangle as the drawing room.

**And Westover states a compositional rule the corpus does not have: a symmetrical facade over a
deliberately asymmetrical plan.** Seven regular bays, a centred front door with a stone pedimented
doorway — and behind it an *off-centre* through hall with a pair of large rooms one side and a
pair of smaller rooms the other. The hierarchy is in the room sizes and the passage moves to let
them differ. The corpus's centre-passage partis assume the plan is as symmetrical as the
elevation; one of the canonical Tidewater houses says otherwise, and says it in 1726. That is not
a defect to fix here — it is a fact the diagram layer does not model, and it bears directly on
`oq/the-parti-dissolved-its-own-dependencies`, because unequal room pairs are one of the ways a
main block absorbs an unequal program honestly.

## 3. The envelope is right. The subdivision is not.

`plans/tidewater-georgian-careful.json` placed on `auto` comes out at **60.0 × 40.0 ft, 6 bays of
10.0 ft, 2,400 sf gross per floor**. That is within one foot of Gunston Hall on both dimensions.
The program's own declared area bands sum to 1,376–4,402 sf on the ground floor, so 2,400 sf sits
comfortably inside them. **Nothing is wrong with the envelope and nothing is wrong with the area.**

What is wrong is how many pieces it is cut into.

| | Gunston Hall | the generated plan |
|---|---|---|
| Gross ground floor | 2,492 sf | 2,400 sf |
| Enclosed ground spaces | **6** | **12** |
| Mean space | 415 sf | 200 sf |

Gunston Hall's first floor, from the survey: a central passage, a narrow side passage, and four
rooms — the Palladian Room, the Chinese Room (northwest Chamber), the Chamber and the Little
Parlour. Six spaces. Drayton Hall names a Great Hall, a Stair Hall, a Library, an Ionic Room and a
Dining Room, with a further room completing the symmetry: six or seven spaces in 3,674 sf.

The generated plan puts twelve enclosed spaces in Gunston Hall's footprint. Halve every
compartment in a house whose depth is fixed at 40 ft and the compartments become slivers. That is
the whole of Lucas's list:

```
kitchen      10.00 x 30.00   ar 3.00   length 30 against its own [12,22] ceiling
breakfast    27.00 x  7.00   ar 3.86   width 7 against its own [8,13] floor
library      10.00 x 24.00   ar 2.40   width 10 against its own [13,22] floor
passage      10.00 x 37.00   ar 3.70   legal on every band it declares
porch        23.00 x  3.00   ar 7.67   width 3 against its own [5,10] floor
dining       17.00 x 17.00   ar 1.00   at (23,7): interior, no exterior wall
stair        10.00 x 13.00   ar 1.30   at (50,27): the far corner
backhall      5.00 x 27.00   ar 5.40
upper: primarybath 29 x 6 (ar 4.83) · cl3 2.00 x 18.97 (ar 9.48) · dressing 18 x 6 (ar 3.00)
```

Every one of those rooms is **inside its area band and outside its width or proportion band**. The
kitchen at 10 × 30 = 300 sf sits inside its 120–340 sf band while standing 67% over its proportion
ceiling of 1.8. Area was never the constraint that was binding, which is why WP-9.4's scoring
changes moved nothing: they re-ranked candidates drawn from a pool that had already accepted the
wrong number of rooms.

## 4. Where the twelve rooms come from, and where the tradition puts them

`partis/centre-passage-double-pile.json` names, on level 0: `porch, passage, stair, drawing,
dining, library, butlers, backhall, powder, kitchen, pantry, breakfast` — eleven enclosed rooms
and a porch. **Six of the eleven are service**: butler's pantry, back hall, powder room, kitchen,
pantry and breakfast room. The plan adds a second back hall (`cellarstair`) and a terrace, which
is how twelve enclosed spaces get placed.

**Gunston Hall's kitchen was a separate building.** So was Drayton Hall's; its service is in the
raised basement, around a Servant's Hall with an 8'-0" fireplace. Hammond-Harwood puts its service
in wings: "the end wings are about 34' x 18, and the connecting links are 18 long." All three
exemplars solve the service program by *not putting it in the main block*.

The corpus knows this. Three separate records say so:

- `massings/catalog.json`, `four-over-four` — the massing this very plan declares —
  `expansion_logic`: **"Flanking dependencies connected by hyphens (the five-part scheme), or a
  rear service ell. Growth must respect the axis or the whole logic fails."**
- The parti's own `scaling.note`: **"Grows to seven bays and then wants dependencies rather than
  more width. Beyond about 5,000 sf the passage becomes a corridor and the diagram stops
  working."**
- `partis/five-part-palladian.json` does it correctly: it carries `westhyphen` and `easthyphen`
  (both typed `gallery-corridor`) and puts kitchen, pantry, breakfast, butler's, powder, mud,
  laundry and garage beyond them, with the groupings `dependency-and-hyphen` and
  `garage-and-hyphen`.

So the corpus contains a faithful diagram of the type with its service in dependencies, and a
second diagram calling itself the same type with the dependencies dissolved into the main block.
The plan Lucas read was composed on the second.

**Nothing can act on any of it.** `grows_by` is read in exactly one place —
`mcp_server/core.py:1364`, echoing it into an API response. `expansion_logic` has three readers:
a counter in `gen_readme_counts.py`, an HTML dump in `render_html.py`, and another API echo.
`structural_logic` has **zero**. The generator's only growth mode is widening: `derive_footprint`
adds bays until the rooms fit or the lot stops it. It cannot add a dependency, and no room type
for one exists outside `five-part-palladian`'s two hyphens.

## 5. The structure is the plan, and the corpus says so in a field nobody reads

> Gunston Hall: "Gunston Hall has solid brick walls including **all but one interior bearing
> wall**, which is a stud framed wall."

> Drayton Hall: "In addition to the exterior bearing walls there are **two interior brick bearing
> walls** parallel to the northwest and southeast walls." And, of the service stair, it "occupies
> the space between the chimney and **the brick bearing wall between this room and the Great
> Hall**."

In both exemplars the principal interior partitions *are* the structure: masonry, continuous, and
few. A room is a compartment between two bearing lines. You cannot make a 10 × 30 sliver in such a
house, because the lines that could bound it do not exist.

`massings/catalog.json` states this exactly, for this massing:

> `structural_logic`: **"Two rooms deep requires an interior bearing wall, which the stair hall
> supplies. Paired end chimneys serve four fireplaces per floor."**

Zero readers. And the placement contradicts it directly: the stair is a 10 × 13 room at (50, 27),
in the corner, supplying no wall to anything. That is Lucas's complaint 6 — *"the stairs are shoved
off into the corner"* — and it is not a matter of taste. The stair hall is supposed to be the
spine wall of a double-pile house, and the search does not know it has a structural job.

This is also the unexamined half of OQ 98 and of WP-7.4's 49.93 ft clear span. Real double-pile
houses do not span 50 ft because they have a masonry spine. The corpus's plans have no spine
because the slicer has no reason to make one.

## 6. The passage: legal, and still wrong

`passage 10.00 x 37.00` is within every band `rooms/centre-passage.json` declares — width 10 in
[6,14], length 37 in [20,40], proportion 3.70 in [2.0,5.0], area 370 in [130,400]. The fault
`passage-that-is-a-corridor` tests `passage_clear_width_ft at-least 8.0` **and nothing else**, so a
10 ft passage passes it at any length whatever. The corpus cannot presently say that a 37 ft
undivided passage is wrong.

Two things are missing, and the second is the interesting one.

**(a) The record already contains the arithmetic that condemns it.** The `centre-passage` daylight
note reads: *"Light from a fanlight and sidelights at the front reaches about 16 ft; the same at
the rear reaches back the other 16; the two overlap in the middle and the passage is lit end to
end."* 16 + 16 = 32, and the passage is 37 ft. By the corpus's own sentence this passage has a
five-foot dark band in its middle. Nothing computes it; the 16 ft reach is prose, and
`depth_multiplier` — the field that *is* read — is a different quantity.

**(b) The tradition divides the passage, and the corpus has no word for it.** In a double-pile
house the centre passage is not one long slot. It is divided at the pile line into an entrance
hall in the front pile and a stair hall in the rear:

> Gunston Hall: "The central passage shows French roccoco detail with the carved C-scrolls in the
> spandrels of **the double elliptical arch that spans the center of the space**."

> Drayton Hall: "Entering the Great Hall from the raised open terrace and recessed portico on the
> southwest (land side) … **Immediately behind the Great Hall is the two-story stair Hall** with
> double doors leading to the exterior porch on the northeast."

A transverse arch at Gunston Hall; a wall and double doors at Drayton. Searching `rooms/`,
`groupings/`, `partis/` and `faults/` for a transverse arch, a divided passage, or a passage
subdivided at the pile line returns nothing. The corpus's answer to a passage that has become a
corridor is to widen it; the eighteenth century's answer was to cut it in half across its length.
Those are different moves and only one of them was available to the search.

Also worth recording, from Gunston Hall: "The center passage has two small windows flanking the
doors at each end of the house." The passage is lit by a door *plus a pair of windows* at each end
— the corpus's "glazed at both ends" note, executed, and a stronger requirement than a fanlight.

One measured passage width, from physical evidence rather than a drawing: Mount Pleasant's
passage "measured 10'-11 1/2" brick to brick", read from the racking left by its dismantled masonry
partitions. That is a secondary source reporting primary evidence and is cited as such — it is not
enough on its own to move a band.

### And the passage's width is stated four times, with four different floors

Verified by reading the files. This is the repo's most-repeated wound — one rule spelled more than
once — in a place nothing checks:

| where | what it says | floor |
|---|---|---|
| `rooms/centre-passage.json` `width_ft` | the band | **6** |
| the same file's `critical_dimension` | *"5 ft 6 in is the floor. Below that two people cannot pass while a door is open"* | **5.5** |
| `groupings/centre-passage-core.json`, severity **hard** | *"Passage width 8 to 14 ft … Below 8 ft the stair cannot turn and the passage stops being a room."* | **8** |
| `faults/passage-that-is-a-corridor.json` `test` | `passage_clear_width_ft at-least 8.0` | **8** |

**And the fault contradicts itself inside one record**: its test hard-fails below 8.0 while its own
note reads *"8 ft for a formal centre-passage plan and 6 ft for a northern vernacular one."* The
room record's `critical_dimension` describes six-to-seven feet as one of two valid populations —
*"SIX TO SEVEN FEET is a passage that circulates"* — which the grouping's hard rule and the fault's
test both reject. Any check that enforces 8 ft convicts a passage the corpus elsewhere calls
correct.

Nothing here is invented: all four are in the tree today, and the disagreement is only invisible
because `passage_clear_width_ft` had no supplier until WP-9.1 built one. **Do not reconcile these
by picking a number.** No source in reach states a passage minimum, and the honest fix is to say
which establishment each floor is conditioned on — the same shape as `applies_when` on the fault
side.

### A second instance one layer out: two hard rules on one volume under two names

`groupings/georgian-service-core.json` carries `wing_ridge_ft / main_ridge_ft at-most 0.85`.
`groupings/dependency-and-hyphen.json` carries `dependency_ridge_ft / main_ridge_ft between 0.6
and 0.8`. Both are **hard**, and **two partis carry both groupings** — `five-part-palladian` and
`connected-farmstead`. On a five-part plan the flanking dependencies *are* the service wings, so
these are two hard rules about one volume under two names.

**The conflict is latent rather than live, and the reason is worth stating precisely.**
`roof.py:348` selects the rule whose test `startswith("dependency_ridge_ft")` — so it reads the
0.6–0.8 band, builds the wing to it, and names its own local variable `wing_ridge_ft`.
`georgian-service-core`'s rule is evaluated by nothing; it is satisfied by accident, because
0.6–0.8 is a subset of ≤0.85. Loosen the dependency band, or ever evaluate the service-core rule
against a wing built at 0.85, and the two disagree.

This is OQ 48's shape one layer out: *two records meaning the same quantity under different names
is a silent corruption, and the fix is a named dimension.* But `check_addresses.py` polices
pack-versus-pack and kit-versus-pack, and **it does not see groupings at all** — there is no
equivalent check for the grouping layer, and this is the first instance found in it.

## 7. The module is a nudge, not a generator

`geometry.snap(v, module, tol)` returns the raw `v` unless the nearest bay line falls within `tol`,
and `tol = bay * 0.28` (`geometry.py:1113`) — 2.8 ft on a 10 ft module. The function's own
docstring already records the consequence, measured: *"18 of 30 ground wall lines on the shipped
plans are themselves off the bay grid."* Sixty per cent of the wall lines miss the module the
diagram declares.

This is the difference between the corpus's process and the tradition's, stated at the smallest
scale. Set against Glassie's account of Middle Virginia folk building, where the builder starts
from a module and the room *is* the module, the corpus starts from an area fraction and then
nudges the cut toward the module if it happens to land nearby.

**What is actually established about Glassie's rule set, and what is not.** Established, from
Deetz's *In Small Things Forgotten* (pp. 108–109), reading Glassie 1975: *"a relatively small set
of rules, nine sub-divided sets, accounts for the complete generation of the folk house of middle
Virginia"*; *"The unit in question is a square, ideally sixteen feet on a side … It is the same as
the rod … Glassie sees it as a multiple of the cubit (18 inches), and his measurements of many
houses support this proposition"*; *"Rooms tend to be sixteen feet square, chimney sections of
houses eight feet (half the unit) wide."* The notation `XY3X` for a Georgian I house is confirmed
by the book's index and by Vlach's 1978 review. **The rule text itself is NOT established** —
*Folk Housing in Middle Virginia* is under lending restriction at archive.org and Google Books
offers no preview of Chapter IV, "The Architectural Competence". Nobody should write Glassie's
rules into this corpus from memory; that is precisely the laundering the first rule forbids.

## 8. Furniture: it does not size a room, it falsifies one — and it is aimed at the wrong record

Lucas, mid-study: *"be sure to study how furniture layout informs room size/shape. I don't think
furniture layout should govern room sizes, but some room sizes are awkward or entirely impossible
to effectively furnish."*

**That is already the corpus's position and it is already built.** OQ 92 ruled furniture-driven
sizing out — *"the tail wagging the dog"* — and arrangement in. `plan_check.py:1250-1288` reads
each room type's `furniture` array (278 items across the catalogue, each carrying `footprint_in`,
`clearance_in`, `placement` and `essential`) and asks whether the room can take each essential
piece with its stated clearance. It fires **13 findings on `tidewater-georgian-careful`** and
quotes the room's own `critical_dimension` prose as the rule for each. So the relation is right:
**furniture sets floors, never sizes.** A floor is exactly a falsifier.

And the corpus is very good on where those floors come from. Read across the catalogue, the rooms
where furniture genuinely decides a dimension all decide it the same way — as a clear aisle,
stated as arithmetic:

- kitchen: *"a galley is 24 + 42 + 24 = 90 in, 7 ft 6 in clear, and a two-cook galley is 8 ft 0 in"*
- butler's pantry: *"Double-sided is 24 + 42 + 24 = 90 in, 7 ft 6 in, and the 42 in is not
  negotiable because two people pass in here carrying plates"*
- walk-in closet: *"Double-loaded, 24 + 36 + 24 = 84 in … There is no useful walk-in between 5 ft
  and 7 ft wide"*
- entry porch: *"DEPTH, and the number is 8 ft, not 6. A rocking chair is 30 in deep and rocks
  through another 24 to 30 in; a person passing behind it needs 36 in"*
- stair hall: *"THE ARITHMETIC OF THE RUN, WHICH SIZES THE ROOM AND IS ALMOST NEVER DONE FIRST …
  The choice between a straight flight and a dog-leg is therefore a decision about the plan's
  proportion and not about the stair, and it must be made before the walls are drawn."*

**Three defects, and the first is the one that matters.**

**(1) It never sees the drawing.** `w, l = r.get("width_ft"), r.get("length_ft")` — the DECLARED
record. So a room declared adequate and drawn as a sliver passes its own furniture check:

| room | declared | drawn | verdict |
|---|---|---|---|
| `breakfast` | 12 × 14 | **7.0 × 27.0** | declared passes; drawn cannot take its essential table (needs 9.0 ft across, has 7.0) — **silent** |
| `cl3` | 3 × 7 | 2.0 × 19.0 | fires, but the statement says "has 3 ft" |
| `dressing` | 8 × 12 | 6.0 × 18.0 | fires, but says "has 8 ft" |
| `porch` | 6 × 12 | 3.0 × 23.0 | fires, but says "has 6 ft" |

The breakfast room is Lucas's second complaint exactly, and **the corpus holds the rule that
convicts it and never runs it against the thing that was drawn.** Where the check does fire, it
quotes the declared shortfall, so every one of them is understated — the OQ 52 family again, a
defect reported smaller than it is.

**Swept over all sixteen plans rather than the two that ship, because two plans is not a corpus:**

```
placed rooms carrying a catalogue type                                231
across-fails on the DECLARED record  (what the critic reports today)   73
across-fails on the DRAWN rectangle  (what is actually drawn)         133
rooms failing an item their own declared record passes                 50   = 22% of placed rooms

by type, failing / placed:   bedroom 13/19 · dining-room 8/13 · kitchen 6/16
                             entry-porch 4/16 · breakfast-room 3/5 · laundry 3/6
                             entrance-hall 2/10 · study 2/8 · closet 2/11
```

**One placed room in five cannot hold furniture its own record says it can, and nothing reports
it.** The pattern is not random. **Eight of the thirteen dining rooms in the corpus fail their own
dining table** — the table needs (40 + 2 × 54) / 12 = 12.33 ft across and the slicer draws them
10, 11, 6 ft wide while their records declare 14 to 18. Thirteen of nineteen bedrooms fail their
beds. `spec-builder-colonial` draws `bed3` at **6.0 × 38.0 ft** and two closets at **1.0 ft wide**.
These are not near-misses; they are rooms nobody could build.

The fix is bounded by the OQ 54 ruling: the `drawn` layer is the only layer permitted to read
placement, so this is a drawn-layer re-run of the same arithmetic, one function with two callers,
on the `openings.required_wall_ft` precedent. It must not become a second transcription of the
rule. **And it should be ratcheted, not just fixed** — 50 and 133 are ceilings that may only come
down, and they are the honest measure of whether anything WP-9.3 or WP-9.4 does to the placement
actually helps.

**(2) Every item is assumed to rotate, and that is why the kitchen passes.**
`fw, fl = sorted(it["footprint_in"])` takes the SHORT dimension as the across-the-room
requirement — right for a chair, wrong for anything whose orientation is fixed by what it serves.
The kitchen island is `[84, 27]`; sorted gives 27, so a 10 ft kitchen needs
(27 + 2 × 42) / 12 = 9.25 ft and passes. Laid the way an island is actually built — parallel to
its counter run — it needs (84 + 2 × 42) / 12 = **14.0 ft**, and the 10 × 30 kitchen Lucas called
far too narrow fails by four feet. **The kitchen survives its own furniture check because the
check turns the island sideways.** The same is true of a counter run, a bed, a sofa against a
wall, and the stair itself. The fix is a typed field on the item — rotatable, fixed to a wall,
fixed to a run — authored, never guessed from the item's name: WP-7.2 already paid for inferring
`placement` from a regex and getting 84 items where the authored data says 159.

**(3) Items are checked one at a time and nothing sums them — but the obvious whole-room test
does not bite, and here is the measurement rather than a silence.** Summing every essential
against-wall item's run against the room's own perimeter flags **nothing** on either shipped plan.
The kitchen's five against-wall appliances total 12.75 ft against an 80 ft perimeter — 16%. The
test is too lenient because perimeter is not available wall: doors, windows, the chimney breast
and the room's own openings take most of it, and `needs_uninterrupted_wall_ft` (five items,
WP-7.4) is the only place in the corpus that states a run requirement at all. A whole-room
furnishability test needs the placed openings, which means it belongs in the drawn layer beside
them and not in the room layer where the per-item check lives. Recorded as refused-for-now with
its number, not as an idea.

**A caution about the model itself, marked editorial.** The furniture catalogue describes a
modern household — an island, a dishwasher, a pair of sofas facing each other. Eighteenth-century
rooms were furnished round the walls, with chairs and tables brought out to the centre when wanted
and pushed back after, which would make a Georgian room's size a function of available wall run
plus what the centre must clear when a table is brought out. That is the standard account in the
furniture-history literature and it is repeated in period-interior writing, but **nothing reachable
from here states it with the authority a corpus rule needs, so it is recorded as a reading and
nothing is built on it.** It matters only as a caution: do not take the furniture model's silence
about a Georgian room as evidence the room is right, and do not run the argument backwards to
justify a band. The bands come from the room catalogue and the precedents. Furniture falsifies.

## 9. The corpus forbids the square, and the tradition prefers it

*This section comes from the parallel study of the compositional literature, whose adversarial
sourcing pass rated the whole study "partly-sourced" and named this its clearest actionable
result. I have re-verified the two halves that carry it — the corpus counts, by reading the files,
and the Mount Vernon dimensions, on the owning institution's own page. The period quotations below
were checked verbatim by that pass against reproductions; **I have not read Morris or Scamozzi in a
facsimile**, and they are cited at that strength.*

**Thirty-five of sixty room records carry a `proportion` lower bound above 1.0, and twenty-nine of
those are not circulation rooms** — that is my own count, by `function_class`, and it is stated
that way because the parallel study counts the same defect as "13 of 23 habitable" against a
narrower denominator. The 35 is the same number in both. Among them:

```
drawing-room     [1.25, 2.0]        hall             [1.3,  2.2]
parlor           [1.1,  1.45]       best-parlor      [1.1,  1.4]
dining-room      [1.15, 1.8]        library          [1.1,  1.6]
primary-bedroom  [1.05, 1.4]        kitchen          [1.05, 1.8]
```

A drawing room may not be squarer than 1.25. A hall may not be squarer than 1.3.

**Mount Vernon, from the Mount Vernon Ladies' Association's own room-by-room page:**

| room | dimensions | ratio | corpus band for its type |
|---|---|---|---|
| **Front Parlor** | 16' 9" × 16' 6" × 10' 10⅜" | **1.015** | `parlor` [1.1, 1.45] — **below** |
| **Dining Room** | 15' × 17' × 10' 9½" | **1.133** | `dining-room` [1.15, 1.8] — **below** |
| New Room | 22' 9" × 30' 6" × 16' 6" | 1.341 | `drawing-room` [1.25, 2.0] — inside |

The Front Parlor is the room Washington called *"the best place in my House."* Mount Vernon's own
FAQ for it: *"The current dimensions of the room are approximately 17 feet square … Historically,
George Washington described the room as being 18 feet square."* **The corpus's band forbids the
shape of the best room in the best-documented Georgian house in America, and its owner described
that shape as a square on purpose.**

The period sources run the same way. Palladio's seven room shapes begin with the round and the
square. Morris, *Lectures on Architecture* (1734), Lecture VII: *"the nearer a Room (in particular
a Hall) is to a Square, the more uniform and commodious they will be."* Kerr's own recommended
bedroom sizes, from the 1865 text: *"a square of 16 feet makes a good ordinary room, or 16 feet by
20; 20 feet square is a very commodious size; 18 by 24 feet makes a room of the first class"* —
ratios 1.0, 1.25, 1.0, 1.333. **No source found in the study states a minimum room ratio at all.**
The prestige direction runs toward the square, not away from it.

**The floors are inert today, and that is the only reason this has done no damage yet.** `plo` is
unpacked in exactly two places in `plan_check.py` (706 and 1237) and used for nothing but the
message text; both checks charge `ar > phi` alone. `geometry.shape_band()` returns the ceiling and
never the floor, and `WIDTH_W` ships at 0.0. So nothing in this corpus presently convicts a square
room — while twenty-nine records declare that it should.

**WP-9.4 nearly built the charge.** It added a squarer-than-the-band direction to `level_score`,
watched it convict both good reference plans, and deleted it, recording that it had invented a
direction with no corpus prose behind it. That was the right call for a shallower reason than the
real one: **the direction is not merely unsupported, it is backwards.** The next package to read
those thirty-five bands as a rule will build it again, and this is the note that should stop it.

### The 2:1 ceiling, and why the passage is exempt by definition rather than by a wider band

The other half is the best-sourced rule the study found, and it is a ceiling with no floor.
Morris (1734) again: *"the Length of no Room exceed a Double Cube, or what he there terms two
Squares."* And Scamozzi (1615), independently, 119 years earlier and in another country, gives the
same ceiling **and its reason**: beyond two squares one gets *"halls, galleries or passageways
rather than rooms to live in."*

That is a definition, not a band. **A room over 2:1 has stopped being a room.** It makes the
generated kitchen at 3.0 and the breakfast room at 3.86 not merely out of band but out of
category — and it says exactly why the passage at 3.70 is exempt: the exemption is the rule's own
reason. If this is ever encoded, the exemption belongs to the room as a declared property, not to
a widened band; widening the band to swallow the passage would lose the reason and license every
sliver in §3.

### The caution that comes with it

Wells (1998), quoted verbatim by the sourcing pass: *"Mount Airy is the only surviving colonial
Virginia house to manifest a clear compositional debt to an English pattern book."* So the
Palladian shape rules must not be coded as rules **of the American tradition** — which bears
directly on §2, where Mount Airy's five-part plan is quoted. Mount Airy corroborates the
service-in-dependencies finding because five houses do; it is not evidence that Virginia builders
worked from Palladio's seven shapes, and this report does not claim they did.

## 10. What this says about WP-9.3 and WP-9.4

WP-9.4's negative result stands and is now explained. It refused a stated macro-tree on the ground
that the quadrant structure was already effectively determined, and it found that no scoring change
moved the ledger. Both are true, and neither reaches this: **you cannot score your way out of a
program that does not fit the type.** A stated tree that arranges twelve rooms in a Georgian main
block arranges the wrong twelve rooms more tidily.

The one number from WP-9.4 that survives intact and now has an architectural reading: changing only
the engine takes fatals 123 → 36 and unreachable rooms 121 → 34, and 121 of 123 heuristic fatals
are *"cannot be reached from outside the house."* A house whose rooms cannot be reached is a house
with no spine and no hierarchy of circulation — the same absence as §5.

## 11. The seven complaints, against the critic as it stands today

`plan_check` on the placed record now produces 45 drawn findings for this plan. Mapped to Lucas's
original list — and the two it cannot name are exactly the two questions §11 raises, which is the
reason to trust the mapping rather than treat it as a coincidence:

| # | complaint | named? | what the critic says |
|---|---|---|---|
| 1 | kitchen far too narrow | **yes** | "DRAWN 10.0 × 30.0 ft — 3.0 to 1, against the 1.05–1.8 band a kitchen is drawn to. The record declares 16 × 20; the placement kept the area and lost the room." |
| 2 | breakfast room too narrow | **yes** | "DRAWN 7.0 ft in its short dimension, below the 8 ft floor for a breakfast room" |
| 3 | portico narrow, off the passage axis | **yes, both halves** | "DRAWN 3.0 ft … below the 5 ft floor" and "The front door is 3.5 ft off the axis of Centre Passage — the two openings do not overlap at all (3.2 ft would just touch)" |
| 4 | dining room landlocked, no light | **yes** | "drawn in the middle of the house: it reaches no exterior wall on any side, so none of the 3 windows the record declares could be placed" |
| 5 | library narrow | **yes** | "DRAWN 10.0 ft in its short dimension, below the 13 ft floor for a library" |
| 6 | stair hall misshapen, **stair shoved into a corner** | **half** | the hall's own furniture check fires ("the stair itself … needs 9.5 ft across, has 9"); **the stair being in a corner is not named by anything** |
| 7 | centre passage huge | **no** | its findings are "no window" and two adjacency notes; 10 × 37 is legal on every band it declares |

**Six of seven, and the two failures are the two open questions.** Complaint 6's unnamed half is
`oq/a-massing-states-its-structure-and-nothing-reads-it` — nothing in the corpus can say the stair
hall has a structural position to hold.

**And WP-9.1's stair-setback check makes the point sharper than the table does.** It is not a
guard that cannot fire — checked both ways: on this plan it evaluates and publishes
`first_riser_setback_ft: 27.04` on `drawn_summary`, and on `spec-builder-colonial` it names the
refusal (*"The stair is not drawn: The stair hall is placed at 8.0 x 9.0 ft and a dog-leg with
this storey's 17 risers needs 10.2 x 7.5 ft"*). But **27.04 ft is a pass**, and it is a pass
*because* the stair has been banished to the corner at (50, 27), twenty-seven feet from the front
door. The corpus has `faults/stair-at-the-front-door.json` for a stair too close and **nothing at
all for a stair too far**, so the one measurement that touches complaint 6 rewards the very thing
Lucas objected to. That asymmetry is not an oversight in the check — the rule it implements
(`openings/grammar.json[op-stair-setback]`, 6.0 ft, sourced in three records) is a minimum by
design. What is missing is the other end, and the other end is not a distance: in this type the
stair belongs *in the passage*, which is `oq/a-massing-states-its-structure-and-nothing-reads-it`
again. Complaint 7 is
`oq/the-passage-is-divided-and-the-corpus-has-no-word-for-it` — the passage is not out of band, it
is undivided, and there is no vocabulary for that. Neither is a missing check; both are missing
words.

## 12. What was deliberately not done

- **No band was changed and no threshold authored.** Five measured buildings are not a
  calibration set either, and one of the three (Hammond-Harwood) is a five-part scheme whose main-block
  figure is not comparable to a bare double pile without care.
- **No parti was edited.** Whether `centre-passage-double-pile` should lose its service rooms, or
  gain hyphens, or be split into two diagrams, is Lucas's decision and §11 puts it to him.
- **No transverse-arch record was authored.** It would be a new vocabulary item in the room or
  grouping schema and it needs a ruling first; it is raised as an open question, not invented.
- **The Shirley attribution was not corrected.** `centre-passage-single-pile` names Shirley
  Plantation, and `va0313`'s written data says of it: *"There is no hallway in the usual sense of
  the word, the stairhall being the architectural feature of the house."* That reads like a
  misattribution, but a single extracted span of one HABS report is not enough to overturn an
  exemplar, and Shirley's Great House is not a simple case. Flagged, not changed.
- **The image half of WP-9.2 is untouched.** No sheet has been transcribed; `plans/precedents/`
  does not exist yet.

## 13. New open questions

- `oq/the-parti-dissolved-its-own-dependencies` — `centre-passage-double-pile` names eleven
  enclosed ground-floor rooms where its three named exemplars have six, because the service program the
  type housed in dependencies has been folded into the main block. Is the fix to move the service
  out (and give the generator a way to build a dependency), to split the diagram in two, or to let
  the composer choose `five-part-palladian` when the brief's service program will not fit?
- `oq/a-massing-states-its-structure-and-nothing-reads-it` — `structural_logic` has zero readers
  across the tree, and the one it states for `four-over-four` ("the stair hall supplies the
  interior bearing wall") is contradicted by every placement the search produces. Should the
  massing's structural statement bind the placement, and if so as a constraint or a charge?
- `oq/the-passage-is-divided-and-the-corpus-has-no-word-for-it` — the transverse arch (Gunston
  Hall) and the hall/stair-hall division (Drayton Hall) are how the type keeps a full-depth
  passage from reading as a corridor. There is no vocabulary for a room divided across its length
  by anything but a wall.
- `oq/the-proportion-band-forbids-the-square` — 29 habitable room types carry a `proportion` floor
  above 1.0, no period source states a minimum ratio, and Mount Vernon's Front Parlor (1.015, "the
  best place in my House") falls below its band. The floors are inert today; the question is
  whether to delete them, re-read them as typicals, or scope them by establishment.

## 14. For Lucas

Four questions, and only the first is urgent. **The furniture defects in §8 are not among them:
both are plain bugs with a clear fix, they are recorded as WP-9.3 work rather than as questions,
and nothing about them needs a ruling.**

1. **The parti.** `centre-passage-double-pile` asks a Georgian main block to hold a kitchen, a
   breakfast room, a pantry, a butler's pantry, a powder room and a back hall — and the shipped
   plan carries a second back hall on top of that. Drayton Hall,
   Gunston Hall and Hammond-Harwood — the parti's own exemplars — put all of that in a basement,
   an outbuilding or a wing. Do we (a) strip the service rooms out of the diagram and teach the
   generator to build a dependency, (b) keep the diagram and accept that it is a modern house
   wearing a Georgian envelope, or (c) make the composer prefer `five-part-palladian` whenever the
   brief carries a service program this size? (a) is the honest one and it is also the most work:
   it needs a hyphen and a dependency in the placement, which nothing today can produce.

2. **The stair as structure.** The massing record says the stair hall supplies the interior bearing
   wall of a double-pile house. Should that be enforced — the stair hall placed as a full-depth
   spine rather than as a room the slicer drops wherever it fits?

3. **The divided passage.** Do you want a transverse division at the pile line as a piece of
   vocabulary — a passage that is two rooms with an arch between them — or is that detail rather
   than plan, and better left to the elevation and section?

4. **Whose furniture?** The catalogue's 278 items describe a modern household — an island, a
   dishwasher, sofas facing each other. Eighteenth-century rooms were furnished round the walls
   with the centre kept clear and chairs brought out when wanted, which would make a Georgian
   room's size a function of wall run plus what the centre must clear. If that is right, the
   furniture check is asking a modern question of a Georgian room and its silences mean less than
   they look like they mean. **Is it worth a period furnishing mode at all, or is one modern
   floor-set per room the right simplification for a program people will actually live in?** I
   could not source the convention to the standard this corpus needs, so this is a question about
   what to build rather than a finding — and nothing has been built on it.

---

## Sources

- Historic American Buildings Survey, **Drayton Hall**, HABS SC-377, written historical and
  descriptive data, `tile.loc.gov/…/sc/sc0100/sc0132/data/sc0132data.pdf`. Prepared by Woodrow W.
  Wilkins, revised and edited by Druscilla J. Null, July 1984.
- HABS, **Gunston Hall**, HABS VA-141, `…/va/va0400/va0433/data/va0433data.pdf`.
- HABS, **Hammond-Harwood House**, HABS MD-251, `…/md/md0000/md0035/data/md0035data.pdf`.
  Original data prepared by Delos E. Smith, 1940.
- HABS, **Shirley**, `…/va/va0300/va0313/data/va0313data.pdf`.
- HABS, **Mount Airy**, HABS VA-72, `…/va/va0800/va0892/data/va0892data.pdf`.
- HABS, **Westover**, HABS VA-402, `…/va/va0300/va0315/data/va0315data.pdf`. Its 1939 entry cites
  Waterman and Barrows, *Domestic and Colonial Architecture of Tidewater Virginia*, p. 71.
- **Mount Vernon Ladies' Association**, "The Mansion Room by Room" and the Front Parlor
  restoration FAQ, mountvernon.org — read directly for the room dimensions in §9.
- Robert Morris, *Lectures on Architecture* (1734), Lecture VII; Vincenzo Scamozzi (1615) in
  Barbieri's EAHN translation; Palladio via Ware (1738); Robert Kerr, *The Gentleman's House*
  (1865). **All four reach this report through one adversarial sourcing pass that checked them
  verbatim against reproductions; no facsimile was read here**, and §9 says so where it uses them.
- Camille Wells, 1998, for the caution that Mount Airy is the only surviving colonial Virginia
  house with a clear compositional debt to an English pattern book. Same provenance caveat.
- James Deetz, *In Small Things Forgotten*, pp. 108–109, reading Henry Glassie, *Folk Housing in
  Middle Virginia* (Knoxville: University of Tennessee Press, 1975). Reproduced at
  `histarch.illinois.edu/plymouth/house.html`.
- John Michael Vlach, review of Glassie, *Folk Housing in Middle Virginia*, 1978 (JSTOR 1499320),
  for the `XY3X` notation.
- Mount Pleasant Plantation, architectural history, Period 1, for the 10'-11½" brick-to-brick
  passage measurement read from partition racking. Secondary, reporting primary evidence.
- Dell Upton, "Vernacular Domestic Architecture in Eighteenth-Century Virginia", *Winterthur
  Portfolio* 17:2–3 (1982), 95–119 — cited by `rooms/centre-passage.json`'s own history note;
  **the article itself was not read here** and nothing in this report rests on it.

*Corpus files read: `partis/centre-passage-{double,single}-pile.json`,
`partis/five-part-palladian.json`, `partis/hall-and-parlor.json`, `massings/catalog.json`,
`rooms/centre-passage.json`, `faults/passage-that-is-a-corridor.json`,
`plans/tidewater-georgian-careful.json`, `build/geometry.py`, `build/structure.py`.*
