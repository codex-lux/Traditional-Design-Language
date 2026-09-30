# oq/an-inherited-ban-decides-what-the-elevation-may-draw — most of what the elevation is forbidden to draw, a style never forbade

*Status: CLOSED 30 September 2026 (ruled 29 September 2026; executed by WP-16.2 and WP-16.4; question 3 is `oq/an-extends-delta-is-applied-to-a-base-it-was-not-written-against`) · Raised in: WP-14.1, the ink read back (27 September 2026)*

**The figures below were corrected on 27 September 2026, the day they were first published.** The
first version of this entry was measured by a census sweep that set a field nothing reads, so it
drew the Tidewater elevation 159 times and held it against 159 different kits. The amendment at
the foot says what that got wrong. The question itself survives the correction; its scale does not.

**Lucas ruled on 27 Sep 2026 that the elevation should refuse, and say, whatever a style's
resolved kit forbids, whether a whole slot or one variant (Phase 14, decision 4). The census then
measured where those prohibitions come from, and most of them are not the style's.** The
elevation draws the same five packs for every style it draws
(`oq/the-elevation-reads-five-packs-whatever-the-style-binds`), and it draws only the styles those
packs name: of the 159 nodes with a kit, drawn on the Tidewater placement with each style in turn,
**118 are refused by the elevation's own gate** (the style is outside `opening-proportion.json`'s
and `facade-classical.json`'s `applies_to`, and the record says so) and **41 are drawn**. Of the
41, **21 draw something their resolved kit forbids** (census check V2):

| feature drawn | forbidden by the style's own record | forbidden by an ancestor's |
|---|---:|---:|
| belt course | 1 | 5 |
| cornice | 0 | 1 |
| doorcase (pilasters and entablature) | 3 | 6 |
| frieze | 1 | 8 |
| modillions | 2 | 2 |
| sidelights | 2 | 5 |
| water table | 1 | 5 |

**Of the 21 styles, 2 are convicted only by their own record, 15 only by an ancestor's, and 4 by
both.** The largest donors of inherited prohibitions are `shingle-style` (12), then
`new-england-colonial` and `georgian-colonial-american` (5 each) and `gothic-revival-british` (4).
The 20 drawn styles that agree are `adam-style`, `beaux-arts-american`, `beaux-arts-french`,
`dutch-colonial-american`, `english-baroque`, `english-classical`, `english-georgian`,
`english-georgian-country-house`, `english-georgian-townhouse`, `english-palladian`,
`federal-style`, `french-neoclassical`, `greek-revival-american`, `greek-revival-northern`,
`greek-revival-southern-plantation`, `italian-renaissance`, `new-england-federal`, `palladian`,
`regency` and `southern-federal`.

## The case that decides nothing either way

**`colonial-revival`**, the style the shipped spec Colonial resolves to, inherits its bans on the
water table, the belt and the frieze from `shingle-style`, two steps up its lineage. Its own
`door_surround` is an `extends` delta whose BASE the cascade took from `gothic-revival-british`,
the nearest ancestor that binds the slot. That base makes `pointed-arch-hood-mould-buttressed-porch`
canonical and forbids `pilasters-and-entablature`, while the delta's own note reads: *"The
inherited pilasters-and-entablature binding (english-georgian) is the right assembly."* The node's
author wrote the delta against a base the cascade does not deliver. Refusing on the resolved kit
would strip the spec Colonial of its water table, belt, frieze, modillion cornice and doorcase.
**Its row survives the correction unchanged** (water table, belt and frieze inherited from
`shingle-style`; modillions and doorcase its own).

**`tidewater-georgian`'s sidelights are the counter-case.** They are forbidden by
`georgian-colonial-american` ("Same date boundary as the fanlight, and they normally arrive
together"), an ancestor, and that prohibition is plainly meant to reach a house dated 1765. The
same inherited ban convicts `charleston-georgian`, `jeffersonian-classicism`,
`mid-atlantic-georgian` and `new-england-georgian`, and `georgian-colonial-american` states it of
itself. So "own against inherited" does not sort the right prohibitions from the wrong ones. That
sort is a judgment per case, the shape of OQ 51's adjudication, one layer over, on slots instead
of packs.

## What would have to be ruled

1. Whether decision 4 stands as ruled (refuse everything the resolved kit forbids, and name the
   node the prohibition comes from on the sheet), or narrows.
2. If it stands, whether the styles an inherited ban strips wrongly are corrected in their own
   kits (colonial-revival binding its own water table, belt, frieze and doorcase) before the
   refusal lands, after it, or not at all.
3. Whether `extends` should take its base from the node the delta was written against rather
   than the nearest ancestor that binds the slot. That is OQ 87's question ("`open` does not mean
   open") on the `extends` side.

The census row V2 carries each prohibition's source, so whichever way this is ruled the count is
measured rather than assumed.

## Amendment — the first table was measured on one drawing (27 September 2026)

The first version of this entry said that **79 of the 159 nodes with a kit** draw something their
resolved kit forbids, that **11 are convicted only by their own record, 51 only by an ancestor's
and 17 by both**, and that the largest donors were `gothic-revival-british` (61), `shingle-style`
(36) and `mediterranean-vernacular` (21). **Every one of those figures was a property of the
instrument.** The census's style sweep (`tests/svg_census.py::_style_sweep`) swapped each style in
by writing `declared.style`. Nothing reads that field: `build_elevation`, `build_section` and
`build_roof` read the plan's own `style`, and every other style sweep in `tests/` writes that. So
the sweep drew `tidewater-georgian`'s elevation 159 times and held the one drawing against 159
kits, and a style the elevation refuses to draw at all was convicted of drawing what Tidewater
draws.

It was found in WP-14.3, and not by reading. The rectangular transom that package draws came back
drawn for `adam-style`, whose kit makes a radiating fanlight canonical, and asking why was the
first time anybody looked at which style the sweep's elevation was of. The sweep now writes
`style` and asserts, per style, that the elevation it built is of the style it asked for, so an
instrument that stops swapping fails loudly instead of measuring one house.

The two cases that give the question its shape, `colonial-revival` and `tidewater-georgian`, read
the same on the corrected sweep.

## Amendment — the counter-case left the census for a different reason (WP-14.6, 27 September 2026)

**The census now convicts 15 of the 41 drawn styles, not 21: 1 by its own record alone
(`new-england-colonial`), 10 only by an ancestor's, and 4 by both.** The largest donors of
inherited prohibitions are `shingle-style` (12), `new-england-colonial` (5),
`gothic-revival-british` (4), and `colonial-revival` and `american-farmhouse-vernacular` (3 each).
`georgian-colonial-american` is no longer among them. Every row the table above counts stands
unchanged except the sidelights, which go from 2 own and 5 inherited to none. **The ban did not
cause that.**

WP-14.6's `elevation._clearances` refuses a sidelight pair where the plan's placed openings leave
it no wall. The census draws every style on the Tidewater placement, and there the passage window
stands 12.0 in from the leaf, where the casing and a sidelight need 21.1. So no style drawn there
draws sidelights, and each sheet says why ("SIDELIGHTS NOT DRAWN — THE LEFT SIDELIGHT WOULD STAND
9.0 IN OVER PASSAGE'S WINDOW"). Six styles left V2 by this route:

- `tidewater-georgian`, the counter-case above;
- `charleston-georgian`, `jeffersonian-classicism`, `mid-atlantic-georgian`,
  `new-england-georgian` and `georgian-colonial-american` itself.

`minimal-traditional` lost its own sidelight clause and kept the rest.

**So the counter-case still stands and the census can no longer show it.** On a placement with room
beside the door, the Tidewater sidelights would be drawn again, over a ban meant to reach a house
dated 1765. Decision 4 is what refuses them on the ban's own terms. What this amendment changes is
the census's count, and it does not answer the question: the six were fixed by where a window
stands, not by what the kit forbids.

## Ruled 29 September 2026 (Lucas, asked directly): fix the wrong bans, then refuse

Asked: *decision 4 — should the elevation refuse whatever a style's resolved kit forbids?*
Lucas chose **Fix wrong bans, then refuse**:

> Decision 4 stands. First, each inherited ban that strips a style wrongly is corrected in that
> style's own kit, case by case (for example, colonial-revival binds its own water table, belt,
> frieze and doorcase). Then the elevation refuses what remains and names the node each ban
> comes from.

That answers questions 1 and 2. Question 3 is not ruled and stays open here: whether `extends`
should take its base from the node the delta was written against.

**Two findings from the planning pass qualify the figures above. WP-16.2 re-derives both before
anything is pinned:**

- **The census names the wrong node.** It names the nearest `extends` delta as a ban's source,
  not the node that wrote the ban (`resolve_kit.py` records `_source` that way). A read-only
  trace of the writers moves the own / inherited / both split. The sheet must name the writer,
  as the ruling says.
- **The gable-return bans are not colonial-revival's.** On eight of the nine shipped plans that
  would lose their gable band, the ban is `gothic-revival-american`'s bargeboard rule, reaching
  them through an `extends` base. On the ninth (bad-03) it is `american-farmhouse-vernacular`'s.

**How it is executed.**

- **WP-16.2** fixes the writer attribution and adjudicates, grouped by (writer, feature).
- Groups the records do not decide go to Lucas as direct questions.
- **WP-16.4** carries out the refusal.

## Asked 29–30 September 2026, answered 30 September 2026: the groups the records did not decide (WP-16.2 stage 2)

WP-16.2 tabled every ban a drawn style inherits, grouped by (writer, feature), and read each one
against the ban's own reason and the receiving style's own record. Where the records decided a
case, the style's own kit was corrected on the template this question's ruling names, after an
independent adversarial check. The groups the records did not decide were put to Lucas as direct
questions, in three rounds. Each question is quoted as it was put (shortened where marked
`[...]`), and then each answer as it came.

### The questions, as put

**Round one, asked 29 September 2026 (22:37 UTC).**

1. *Colonial Revival trim.* "Colonial Revival: its own record never names a water table, a belt
   course or a frieze. All three are refused today on Shingle Style's reason: 'No water table may
   interrupt the shingle field.' Your ruling's example read 'colonial-revival binds its own water
   table, belt, frieze and doorcase'. Against that, georgian-revival's record contrasts itself with
   general Colonial Revival, which shows 'no water table' and does not carry a belt course. Once
   bound, the elevation draws all three on every Colonial Revival front: the belt at any status,
   because it reads no belt variant. What should colonial-revival's own kit say?"
2. *A record's silence.* "Where a style's own record is silent and the ban it inherits plainly
   belongs to another style, what should its kit say? The live cases: sidelights and transom on
   second-empire, italian-renaissance-revival and italianate-townhouse. All three are refused on
   Gothic Revival's c05 ('no classical apparatus'), and none of their records names or rules out a
   transom or sidelight."
3. *Dated bans.* "georgian-colonial-american forbids sidelights on a row dated 1700 to 1780, and
   jeffersonian-classicism (floruit 1785 to 1826) inherits the ban. Should the elevation read a
   forbidden row's own date range against the house's date? No shipped plan states a date today,
   so nothing drawn moves now either way."
4. *The Italianate family.* "Four styles inherit Gothic Revival's refusal of the pilastered
   doorcase, and three inherit its refusal of the cornice return: italian-renaissance-revival,
   italianate-townhouse, second-empire and renaissance-revival-american. The Gothic reason does not
   fit any of them, but their own records say nothing or point the same way. [...] None has a gable
   a return could stand on (hip, mansard, party-wall row). What should they carry?"

**Round two, asked 30 September 2026 (01:00 UTC).**

5. *Cape and saltbox transom.* "new-england-colonial forbids the whole transom_sidelight slot ('no
   place on an unadorned First Period door'), so once WP-16.4 lands the elevation will refuse the
   transom as well as the sidelights. The records disagree: the saltbox's own exemplar note gives
   Hyland House (1713) 'a simply framed door with a five-light transom', and HABS surveys of the
   Cape's exemplars record transoms [...]. On sidelights the ban holds in each style's own words.
   What should cape-cod-colonial and saltbox-colonial bind?"
6. *Jeffersonian keystone.* "jeffersonian-classicism inherits tidewater-georgian's ban on the
   keystoned flat arch [...]. Its record says Tidewater-trained Virginia masons built it, but 'to
   unfamiliar drawings' with 'the Georgian conventions all missing', and it never names a window
   head. No keystone is drawn for it today. [...] What should it do?"
7. *New-urbanist modillions.* "The farmhouse's cornice and frieze bans don't fit
   new-urbanist-traditional: its eave is folk-victorian's bracketed box, and its lineage keeps the
   Greek Revival 'pedimented gable, simple pilaster and entablature'. [...] The record is mixed: it
   declined the Ionic pack ('answered it against a richer order') and binds Tuscan, yet names
   Colonial Revival as a dialect. What should its cornice record say of modillions?"
8. *New-urbanist gable return.* "The farmhouse's ban says 'the fascia simply dies into the rake',
   which describes the farmhouse's plain fascia, not this style's bracketed boxed eave.
   new-urbanist-traditional's record never names a return; its lineage keeps a 'pedimented
   gable'. [...] What should it bind?"

**Round three, asked 30 September 2026 (02:31 UTC),** after the independent check of the records
written on answers 1 to 8 found two descendants they reach:

9. *minimal-traditional's water table.* "minimal-traditional (a drawn style) inherits Colonial
   Revival's water table from A1: permitted, nothing canonical. [...] It never names a water table.
   Should its water table stay permitted, or be forbidden in its own words?"
10. *neo-eclectic's belt course.* "The independent check wrote a minimal-traditional belt-course
    ban (on its three-ornament cap and one-and-a-half storeys). That ban descends to neo-eclectic,
    whose record never names a belt course and says 'neo-eclectic is two-storey, vertical in its
    entry, and heavily ornamented'. Should neo-eclectic bind its own belt course, and how?"

### Lucas's answers

Round one was answered on 30 September 2026 at 00:48 UTC, round two at 01:29 UTC and round three
at 12:03 UTC. Each time Lucas chose the recommended answer:

- **A1:** colonial-revival binds its own water table, belt course and frieze: each permitted,
  nothing canonical, marked editorial and citing the ruling. The Shingle Style refusals lift.
  georgian-revival's frieze and neoclassical-revival's water table inherit these records.
- **A2:** the silence reads as **permitted, unsettled**. second-empire, italian-renaissance-revival
  and italianate-townhouse each bind `transom_sidelight`, with sidelights and a transom permitted
  and nothing canonical, marked editorial.
- **A3:** a forbidden row's own date range is read against the house's date. A dated house outside
  it draws the feature. An undated house keeps the refusal, and the sheet says the date is
  unstated. This is WP-16.4's code, not a record.
- **A4:** each of the four binds `door_surround`, forbidding the pilaster doorcase on its own
  record's reason, so the door gets the plain casing and the refusal names the style. Each binds
  `cornice_return` forbidden on its own roof (hip, mansard, party wall).
  renaissance-revival-american also forbids the fanlight and the sidelights, on its own
  "enrichment confined" note.
- **A5:** each binds `transom_sidelight` itself: the rectangular transom permitted, citing its
  evidence; sidelights forbidden in the style's own words.
- **A6:** jeffersonian-classicism keeps the inherited ban. No record changes, and a refusal names
  tidewater-georgian as the writer.
- **A7:** new-urbanist-traditional's cornice and frieze get records of their own, permitted and
  marked judgment, and the cornice carries one forbidden `modillion-cornice` row quoting its own
  decline of vignola-ionic.
- **A8:** new-urbanist-traditional binds its own `cornice_return`, nothing canonical: permitted,
  unsettled. The gable end keeps its cornice band and the sheet says the return is unstated.
- **A9:** minimal-traditional's water table is **permitted, unsettled**. It inherits A1's record,
  and no record changes.
- **A10:** neo-eclectic binds its own `belt_course`: a `none` row permitted, nothing canonical,
  marked judgment, its silence read as in A2, so it does not inherit minimal-traditional's reason.

### What was bound, 30 September 2026

- **Thirteen records on cases the records decided**, checked independently: nine adjudicated,
  and four companions the first check wrote.
  - colonial-revival's `cornice`, `door_surround` and `cornice_return`;
  - minimal-traditional's `cornice`, `cornice_return` and `frieze`;
  - the `water_table` of georgian-revival, cape-cod-revival and new-classical;
  - garrison-revival's `door_surround` and `cornice`;
  - modern-farmhouse-traditional's `cornice_return`;
  - neo-eclectic's `cornice`.
- **Twenty records on answers 1, 2, 4, 5, 7 and 8.** The independent check upheld seven and
  amended thirteen.
- **Four companions the second check wrote**, each where a descendant's own words contradict what
  the twenty would hand it:
  - cape-cod-revival's `frieze`, forbidden on its own c05 ("Cornice returns, modillions, friezes,
    pediments over windows, and full-width porches are forbidden."), and its `belt_course`,
    forbidden as a judgment on the same constraint's cap on ornament;
  - mediterranean-revival's `door_surround`, which permits the doorcase its own record puts at the
    entrance;
  - minimal-traditional's `belt_course`, forbidden as a judgment on its ornament cap and storey
    count. It reaches ranch-style and modern-farmhouse-traditional, whose own words the check found
    support it, weakly.
- **neo-eclectic's `belt_course`**, on answer 10, checked independently.

Answers 6 and 9 change no record. Answer 3 is WP-16.4's.

### What the records leave, and what they expose

- **Three styles draw sidelights their own kits forbid, until WP-16.4:** cape-cod-colonial,
  saltbox-colonial and renaissance-revival-american.
  - `doorcase.forbidden_of` reads only a slot bound `forbidden` whole. Each of these now forbids
    the sidelights ROW of a slot it binds `specified`.
  - Census V2 names each as the style's own ban.
  - No shipped plan is on any of them, and no sheet moves.
- **One fault verdict moves on a shipped plan, and the move is a vacuous clear.**
  - On good-05 (italian-renaissance-revival), answer 2 lifts the sidelight ban. The entrance
    composition then leaves the sidelights out for facade-classical's composition cap, and the
    elevation publishes `sidelight_width_in` as 0.0.
  - So `sidelights-as-storefront-glass` goes from could-not-evaluate to clear, on a front with no
    sidelights.
  - The honest verdict there is not-applicable. Making the sidelight measurement honest is WP-16.4's.
- **The bans were shields over OQ 51 deliveries.** With the slots freed, packs bound on
  unrelated ancestors dimension them:
  - timber-panel, through tudor and french-manoir;
  - stone-course, through italian-villa-vernacular;
  - chambers-ionic, through english-georgian;
  - opening-mullioned, through french-renaissance-chateau and jacobean.

  A record that frees a slot for such a pack says so in its own note ("OQ 51's delivery, counted
  and not endorsed"). A descendant that inherits the record has no record of its own, so WP-16.2's
  report lists those. `check_inheritance.py --strict` does not see any of this, because its role
  meter does not count slot-level deliveries.
- **Three residuals the records do not settle.** None of the three styles is drawn, and none is
  asked here:
  - chateauesque's `cornice_return`: its own record is silent on returns and does not contradict
    the ban's outcome, but the writer the ban names is second-empire, whose reason is the mansard
    chateauesque's own record denies;
  - chateauesque's `transom_sidelight`: it inherits second-empire's permitted record, and its own
    record is silent;
  - garrison-revival's `belt_course`: the corpus maps the jetty to this slot, so the answer is a
    pack-and-slot decision, not a kit record.

Questions 1 and 2 above stay answered. Question 3, whether `extends` should take its base from the
node the delta was written against, is still not ruled. The refusal itself is WP-16.4, and this
question stays IN PROGRESS until it lands.

## Executed 30 September 2026 (WP-16.4): what the kit forbids is refused, and the writer is named

WP-16.4 carries out the refusal, and with it answer A3 (30 September 2026): a forbidden row's own
`applies_when.date_range` is read against the house's date. The report is
`docs/reports/wp-16.4-the-refusal-names-who-forbade-it.md`.

- **One reading of a ban.** `resolve_kit.ban(rec, words, date)` answers whether a slot or a feature
  is forbidden at the house's date, and names the nodes that wrote the ban. The placer, the
  elevation, the DXF, the scene and the stack pass all read it, and all print its words.
- **What is refused.** The sidelights (a row ban, or the whole `transom_sidelight` slot with the
  transom), the pilaster doorcase (the door keeps the doorcase's own casing), the water table, the
  belt course, the frieze, the cornice and the order's modillions, and an exterior stack. A refused
  feature's measurements are withheld, not zeroed.
- **The dated ban.** georgian-colonial-american forbids the sidelights for houses of 1700–1780. On
  the Tidewater record, dated 1765, they are refused and the placer reserves no run for them; the
  same house dated 1790 draws them. An undated house keeps the ban, and the sheet says the date is
  unstated.
- **Census V2 went from 17 known disagreements to 0.** Of its 159 rows, 38 agree and 121 could not
  be evaluated: 118 styles the elevation does not draw, and three whose only open item is an
  exterior stack the census sweep does not place (cape-cod-colonial, new-england-colonial,
  new-england-georgian). The placer refuses such a stack, and `tests/test_kit_refusal.py` drives
  that refusal.
- **What WP-16.2 handed over is done.** The sidelights cape-cod-colonial, saltbox-colonial and
  renaissance-revival-american forbid are refused. good-05's `sidelights-as-storefront-glass` is not
  applicable, where it cleared on a published 0.0. new-urbanist-traditional's modillions are refused
  on bad-03.

**Questions 1 and 2 are answered and executed, so this question is closed.** Question 3, whether
`extends` should take its base from the node the delta was written against, is not ruled. It is
`oq/an-extends-delta-is-applied-to-a-base-it-was-not-written-against` now, so it is not lost with
this entry.

**Left open, and named in the report.** minimal-traditional forbids `door_surround` whole, and its
door keeps the doorcase's own casing, whose width is that slot's pack rule; the record lists the
slot as READ ANYWAY. renaissance-revival-american's `window_head_wood` is read anyway as before.
