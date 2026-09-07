# Precedents — `centre-passage-double-pile`

*6 September 2026 (WP-11.11). The FIRST of twenty-one, and it is the pattern rather than the
survey: Lucas ruled "one parti, done properly, as the pattern". What is reusable here is the
METHOD and the generated Part VI, not the eleven houses — those were reached for the Tidewater
diagnosis and belong to this diagram alone.*

---

## 0. What this file is, and what it is not

`PLAN-OF-ACTION.md`'s WP-11.11 asks for two things per parti: a **Part II** table of the
precedent, from the parti's own `exemplars`, and a **Part VI** list of that parti's prose rules
without tests. This file delivers both for `centre-passage-double-pile`, and the split between
them is the point:

- **Part II is RESEARCH and cannot be generated.** Every figure in it was reached through the
  HABS written data at `tile.loc.gov` or a house's own institution, and every one carries the
  sentence it came from. Nothing below was re-derived here; §1 says where each was established
  and by which pass, because **re-quoting a measurement without its provenance is how a figure
  becomes "measured" without anyone measuring it** — the failure this corpus names first.
- **Part VI is ENUMERATION and now IS generated.** `build/parti_prose.py` produces it from the
  parti's own groupings, massing and room records. The diagnosis's twenty-row table took a
  session to assemble by hand; the equivalent for any of the twenty-one is now one command.

**The one number that matters for the other twenty**: this parti's Part VI has **50 rows**, not
twenty. The hand-assembled table was a reading of one sheet and caught what that sheet broke; the
generated one is the whole surface.

---

## 1. Part II — the precedent, and where each figure was established

**NOTHING IN THIS SECTION WAS MEASURED HERE.** Both passes that produced it are named, and the
marks are theirs: **M** a survey or museum measurement, **A** an author's or owner's figure,
**via** read in a work quoting it rather than in the original.

| established in | what it reached |
|---|---|
| `docs/reports/tidewater-layout-diagnosis-2026-09-04.md` §II.1 | eleven houses through HABS written data and the houses' own institutions — Gunston Hall (VA-141, M), George Wythe House (CW RR1483, M), Westover (VA-402, A), Wilton (DHR 127-0141, A), Carter's Grove (VA-351, A), Kenmore (VA-305, A), Mount Vernon (museum, M), Hammond-Harwood (MD-251, A), Chase-Lloyd (A), Berkeley (VA-363, A), Drayton Hall (SC-377, M) |
| `docs/reports/wp-9.2-the-parti-is-not-the-type.md` | the enclosed-space counts and the envelope comparison, and the correction that **Hammond-Harwood's count is NOT established** — two of the three, not three |
| `oq/fetching-through-a-tier-the-proxy-denies` | that `tile.loc.gov` is reachable at all, ruled 31 Aug 2026. WP-9.2 re-derived it, which is what that entry exists to prevent. **Read the register before announcing a route.** |

### 1.1 The parti's own three exemplars against what was reached

The parti names **Drayton Hall 1742, Hammond-Harwood House 1774, Gunston Hall 1759**. The
diagnosis reached eleven houses; the parti's own three are a subset, and the coverage is uneven in
a way worth stating rather than smoothing:

| exemplar the parti names | envelope | enclosed ground spaces | stair | kitchen |
|---|---|---|---|---|
| **Gunston Hall** | 60'-10" x 40'-11½" exterior foundation, walls *"about two feet thick"* (M) | **six**, enumerated by HABS VA-141 | in the passage | detached, foundation NE of the house |
| **Drayton Hall** | 70'-5" x 52'-2" excluding portico, 7-bay front (M) | **six**, named in SC-377 | in its own hall behind the great hall | not stated in the span reached |
| **Hammond-Harwood** | *"approximately 44x42'"* main block (A, 1940, an approximation and low); **49 ft on the house's own institution's figure** | **NOT ESTABLISHED HERE** | a stair hall behind the west parlor | in a wing |

**Two of the three, not three.** An earlier line in `CLAUDE.md` said "six enclosed spaces EACH"
of all three and was corrected: Hammond-Harwood is a five-part scheme whose main block is not
comparable to a bare double pile without care. That correction is why this table has a cell
reading NOT ESTABLISHED rather than a number.

### 1.2 What the parti declares against what the precedent shows

This is the comparison the per-parti pass exists to make, and on this parti it was already made —
`oq/the-parti-dissolved-its-own-dependencies`:

| | the parti | the precedent |
|---|---|---|
| enclosed ground rooms | **eleven**, plus a porch — twelve spaces on level 0 of `partis/centre-passage-double-pile.json`, and the distinction matters because a porch is not a room the precedent has to house | **six**, in the two exemplars where the count is established |
| service rooms | **six of the eleven** (butler's pantry, back hall, powder room, kitchen, pantry, breakfast room), all in the main block | a basement, an outbuilding or a wing, at every exemplar whose source says |
| envelope | 60.0 x 40.0 ft of ROOM extent, no wall thickness | Gunston 60'-10" x 40'-11½" over two-foot walls — a clear extent about 3 ft larger each way |
| clear area | 2,400 sf | 2,100–2,195 sf — the parti puts **9 to 14% more program** in a smaller clear envelope |
| bay module | `bay_module_ft: 9` | Gunston measures **12.17 ft** over five bays — `oq/the-partis-bay-module-contradicts-its-own-exemplars` |

**The envelope is right and the subdivision is not**, and no score term fixes that. Read
`docs/reports/wp-9.2-the-parti-is-not-the-type.md` before proposing a placement change here.

### 1.3 What the sources could not settle

Named, because an agent's *"not in the source"* is a search result and not evidence of absence —
WP-9.2's own method finding, and it applies to every row above.

- **Drayton Hall's kitchen** — not stated in the span reached. One extract does not return the
  whole document; re-query the same URL with a different `query` and a different span comes back.
- **Hammond-Harwood's enclosed count** — two figures exist for its envelope and they disagree by
  five feet; the room count was never reached.
- **Gunston's passage width** — HABS does not state it. The *"12-foot-wide"* figure is an
  author's, and it is the only passage width any pass reached for the parti's own three.
- **Every exemplar's room-by-room dimensions but Mount Vernon's**, which is not one of the three.
  The study of 2 Sep already warned that a distribution built on one house may be characteristic
  of that house and not of the tradition.

---

## 2. The method, for the other twenty

1. **Generate Part VI first** — `python3 build/parti_prose.py <parti-id> --md`. It costs a second
   and it tells you what the diagram already claims, which is the cheapest possible orientation
   before any research.
2. **Read the parti's own `exemplars`, and reach them through the register's route** —
   `oq/fetching-through-a-tier-the-proxy-denies`. Do not re-derive the route; it is recorded.
3. **Quote the sentence, mark the kind (M/A/via), and name what was not reached.** A blank cell
   is a finding. A number without its sentence is how a guess becomes a measurement.
4. **Compare the parti's DECLARED record against the precedent** — §1.2's shape. Room count,
   service arrangement, envelope, bay module. That comparison is what produced
   `oq/the-parti-dissolved-its-own-dependencies` and
   `oq/the-partis-bay-module-contradicts-its-own-exemplars`, the two sharpest findings this
   corpus has about its own diagrams.
5. **Do not close a gap by authoring a number.** Three of the four rows in §1.3 could be filled
   plausibly and none could be filled honestly.

---

## Part VI — what `centre-passage-double-pile` says and cannot execute

*Generated by `build/parti_prose.py`. A rule with no test is not a defect: several are a human's to check, one is a REPORT by ruling, and WP-11.9's §IV names nine that cannot be executed until a fact exists that does not.*

| where | severity | state | statement |
|---|---|---|---|
| `centre-passage-core[0]` | hard | executed | Both ends of the passage have doors. A passage closed at the back is a corridor and loses the reason the type exists. Split from the alignment rule b… |
| `centre-passage-core[1]` | strong | by hand | The two end doors are aligned, so the view runs through the house. Carries no test: the quantity is a relation between two PLACED doors and every lay… |
| `centre-passage-core[2]` | preferred | reported | The passage takes a BAY of the front, and its share of the facade follows -- observed at roughly one fifth to one quarter. Below 8 ft the stair canno… |
| `centre-passage-core[3]` | hard | executed | Passage width 8 to 14 ft. Below 8 ft the stair cannot turn and the passage stops being a room. Stated as a rule of its own because the ratio rule abo… |
| `centre-passage-core[4]` | strong | by hand | Flanking rooms are equal or near-equal, and their windows align vertically with those above. The passage buys the symmetry and the symmetry has to be… |
| `centre-passage-core[5]` | hard | executed | The stair rises in the passage or in a hall opening off it, never through a room. The test holds the SECOND half only: that a separate stair hall is … |
| `centre-passage-core[6]` | preferred | by hand | Where the plan is single-pile, the passage cross-ventilates the whole house. Filling in behind to make it double-pile buys area and loses the draft, … |
| `entry-sequence[0]` | strong | executed | At least two thresholds between the public way and any room with a door that closes. One is a motel. |
| `entry-sequence[1]` | hard | by hand | Each step changes at least one condition: level, enclosure, light, or direction. Three doors in a row on one axis at one level is one threshold repea… |
| `entry-sequence[2]` | strong | executed | The sequence rises. Entering downward reads as a basement whatever the finishes; two to five risers from the walk to the porch floor is the tradition… |
| `entry-sequence[3]` | strong | by hand | A vestibule is a thermal airlock and needs two doors that are never open at once; a vestibule with a single door is a hallway with pretensions. |
| `entry-sequence[4]` | hard | by hand | Nothing in the sequence may be the only route to a service area. A mudroom reached through the formal hall means the formal hall becomes the mudroom. |
| `public-enfilade[0]` | hard | executed | Doors align on one axis so the view runs through. A single offset door breaks the enfilade and it cannot be recovered with finishes. |
| `public-enfilade[1]` | strong | by hand | Rooms diminish or grow in one direction, never alternate. Hierarchy has to be legible as you move. |
| `public-enfilade[2]` | hard | by hand | Each room in the sequence is also reachable from the hall or passage, so the enfilade is a choice and not the only route. An enfilade that is the sol… |
| `public-enfilade[3]` | strong | by hand | Openings are wide — 5 to 8 ft with pocket or double doors — or the sequence reads as a row of doorways rather than a run of space. |
| `stair-and-landing-core[0]` | strong | by hand | A window on the half-pace or at the head. A stair lit only from the floors it connects is a shaft. |
| `stair-and-landing-core[1]` | hard | executed | Landing depth not less than the stair width. Below that it is a turn, not a landing. |
| `stair-and-landing-core[2]` | preferred | by hand | No bedroom door opens directly onto a landing visible from the hall below. |
| `stair-and-landing-core[3]` | hard | executed | Riser and tread constant through the whole flight, including at landings. A single odd riser is the most common cause of a domestic fall. |
| `stair-and-landing-core[4]` | strong | by hand | Where a back stair exists it lands in the service zone, never on the formal landing. |
| `secondary-bedroom-cluster[0]` | hard | executed | Every bedroom takes a double bed, two tables and a chest with clearances: 10 ft in the short dimension is the floor, and 11 is workable. Below 10 ft … |
| `secondary-bedroom-cluster[1]` | hard | by hand | No bedroom is entered through another. This is the oldest rule in domestic planning and it is still broken in bonus rooms and third bedrooms. |
| `secondary-bedroom-cluster[2]` | strong | by hand | The shared bathroom is reached from the corridor, not through a bedroom. A jack-and-jill bath serves two rooms and privatises a fixture the other bed… |
| `secondary-bedroom-cluster[3]` | preferred | by hand | Bathroom and linen store buffer bedrooms from each other where the wall is shared head to head. |
| `secondary-bedroom-cluster[4]` | hard | by hand | Every sleeping room has an emergency escape opening, and a fixed or high transom window does not count. |
| `four-over-four.constraints` | — | by hand | Facade symmetry is a hard constraint, not a preference. |
| `four-over-four.constraints` | — | by hand | Window bays must align vertically; a misaligned upper window is a structural admission that the plan is not really Georgian. |
| `four-over-four.structural_logic` | zero readers (WP-9.2) | by hand | Two rooms deep requires an interior bearing wall, which the stair hall supplies. Paired end chimneys serve four fireplaces per floor. |
| `four-over-four.expansion_logic` | a counter, an HTML dump and an API echo; nothing acts on it (WP-9.2) | by hand | Flanking dependencies connected by hyphens (the five-part scheme), or a rear service ell. Growth must respect the axis or the whole logic fails. |
| `rooms/back-hall.daylight.orientation` | preferred | executed | North or whatever is left. |
| `rooms/bathroom.daylight.orientation` | preferred | executed | East if there is a choice. |
| `rooms/bedroom.daylight.orientation` | preferred | executed | East. A bedroom wants morning light and does not want a western afternoon |
| `rooms/breakfast-room.daylight.orientation` | preferred | executed | East. The room's whole argument is morning light, and a north-facing breakfast room has lost its reason to exist. |
| `rooms/butlers-pantry.daylight.orientation` | declines | reported | The record requires none and calls north merely pleasant. A preference that the record itself declines to require is not one this check may enforce. |
| `rooms/centre-passage.daylight.orientation` | declines | reported | What follows in the record is a rule about the two ENDS being on opposite pressure faces -- a door axis across the summer breeze, and regional. Not a… |
| `rooms/closet.daylight.orientation` | declines | reported | The record refuses the question: a closet should not be on an exterior wall at all. |
| `rooms/dining-room.daylight.orientation` | preferred | executed | East or south-east for a breakfast-doubling room; west where the room is used at night and the low sun is wanted on the table. |
| `rooms/drawing-room.daylight.orientation` | preferred | executed | South and west, and the reason is the hour |
| `rooms/entry-porch.daylight.orientation` | preferred | executed | West and south porches are the ones people use |
| `rooms/kitchen.daylight.orientation` | preferred | executed | EAST for the morning, and this is one of the oldest orientation rules in domestic building. |
| `rooms/landing.daylight.orientation` | preferred | executed | North is fine and often best |
| `rooms/library.daylight.orientation` | preferred | executed | A north or north-east library is the historic preference and the correct one. |
| `rooms/linen-press.daylight.orientation` | declines | reported | The record says irrelevant. What it does state is a construction rule about the wall, not an aspect. |
| `rooms/pantry.daylight.orientation` | preferred | executed | None needed; away from west if there is a choice |
| `rooms/powder-room.daylight.orientation` | declines | reported | The record answers "Any". Its own point is that a small window beats a fan, which is about ventilation rather than about which way the room faces. |
| `rooms/primary-bathroom.daylight.orientation` | preferred | executed | East. This room is used at 6 am |
| `rooms/primary-bedroom.daylight.orientation` | preferred | executed | East or south-east, and this is where the suite most often goes wrong |
| `rooms/stair-hall.daylight.orientation` | preferred | executed | North is best and is the historic choice where there is one |
| `rooms/walk-in-closet.daylight.orientation` | preferred | executed | North or east if it is glazed at all, because south and west sun fades textiles |

### Figures stated in prose that no band or test carries

| kind | where | figure | the sentence |
|---|---|---|---|
| room | `bedroom.width_ft` | 9.0 | Bed head against the room's width: 60 + 24 + 24 = 108 in, a 9 ft 0 in clear width, and that is the ABSOLUTE floor - it … |
| room | `bedroom.width_ft` | 10.0 | A 10 ft bedroom is a fault dressed as a room: it dimensions correctly, it passes every code check, and it can only be f… |
| room | `bedroom.width_ft` | 12.0 | The depth follows: 86 (bed) + 36 (passing at the foot) + 20 (chest) = 142 in, 11 ft 10 in, so 12 ft 0 in. |
| room | `centre-passage.width_ft` | 7.0 | SIX TO SEVEN FEET is a passage that circulates: two people pass, a stair fits against one wall, doors swing. |
| room | `centre-passage.width_ft` | 12.0 | TEN TO TWELVE FEET is a passage that is a room: it takes chairs down one side, a table, a settee, and people sit in it. |
| room | `centre-passage.width_ft` | 9.0 | The dead zone is 8 to 9 ft, which is too wide to be economical and too narrow to furnish - a 9 ft passage with 20 in ch… |
| room | `centre-passage.width_ft` | 5.0 | SECOND NUMBER: 5 ft 6 in is the floor. |

**24 executed, 6 reported, 20 handed to a reader, 7 prose figure(s) nothing carries.**

---

## 3. What the generated Part VI shows about this parti

**Fifty rows: 24 executed, 6 reported, 20 handed to a reader, and 7 prose figures no band or test
carries.** Three things in that are worth naming.

**The twenty by-hand rows are not a backlog.** WP-11.9's §IV worked the diagnosis's twenty-row
hand-made table and found nine that cannot be executed until a fact exists that does not — a
machine-readable facade symmetry, a stated massing, a stair window field, an enfilade order. The
same is true here in proportion. The number is a work list in leverage order, which is what
`check_inheritance.py --unendorsed` is one layer over.

**The `four-over-four` massing contributes four by-hand rows and every one of them is a sentence
nothing anywhere reads.** Its two `constraints` are an array of prose; `structural_logic` has zero
readers corpus-wide and `expansion_logic` has a counter, an HTML dump and an API echo (WP-9.2).
Two of those four are rows 1 and 2 of the diagnosis's own table.

**All twenty room-orientation rows have left the by-hand column, and that is the evidence the
instrument is worth having.** The parti names **20 distinct room types and every one of them
states an aspect in words**; before WP-11.9 all twenty were `by hand`, because nothing in the tree
read `daylight.orientation`. They now read **15 `executed` and 5 `reported`** — the five being
records that answer the compass question with something that is not a compass (`closet`: *"None"*;
`powder-room`: *"Any"*), which is a judged verdict and not a gap. **A row that has LEFT this table
is the only thing that distinguishes a generated Part VI from a list of complaints**, and it is
also why the by-hand column must be re-generated rather than quoted: this file's own first draft
said twenty-six.

The other three columns, for the record, because a total hides which layer is where the work is:
**grouping rules 9 executed / 1 reported / 16 by hand** (26 rows over five groupings), **massing
prose 0 / 0 / 4**, **orientation 15 / 5 / 0**.

**The seven prose figures are the crude-regex meter's, imported rather than transcribed.**
`check_grouping_rules.prose_meter` is the one spelling; its own docstring records that its first
version returned fifty figures of which forty-five were arithmetic steps and missed the single
case it exists for. **The way to lower this number is to author a figure into a test, never to
tighten the pattern until it looks better.** Four of the seven are the centre passage's, which is
`oq/a-grouping-rule-and-a-room-record-can-disagree`'s own headline instance — seven statements
across five files spanning 3.0 to 10 ft — so the count is not a surprise here; it is that
question surfacing through a second instrument.

---

## 4. What this file deliberately does not do

- **It does not survey the other twenty partis.** Ruled: one parti, done properly, as the
  pattern. `build/parti_prose.py --all` prints one line each and shows the shape of the work —
  `five-part-palladian` is the largest at 30 executed and 26 by hand, and `single-cell-hall`
  the smallest at 12 rows in total — but a Part II for each is twenty research passes and is not this package.
- **It does not re-measure a single house.** Everything in §1 is cited to the pass that
  established it. Re-quoting without provenance is the failure this corpus names first, and a
  precedent file is exactly where it would happen.
- **It makes no judgment about the twenty by-hand rows.** A rule with no test is not a defect —
  one of them is a REPORT by ruling (`oq/the-facade-is-a-result-not-an-input`), several are
  genuinely a reader's, and nine of the diagnosis's own were refused with a reason in WP-11.9.
  A file that called them all debt would be arguing for exactly the mechanical execution the
  facade ruling refused.
