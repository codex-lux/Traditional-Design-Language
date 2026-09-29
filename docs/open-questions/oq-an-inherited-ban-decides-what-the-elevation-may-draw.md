# oq/an-inherited-ban-decides-what-the-elevation-may-draw — most of what the elevation is forbidden to draw, a style never forbade

*Status: IN PROGRESS (ruled 29 September 2026; executed by Phase 16) · Raised in: WP-14.1, the ink read back (27 September 2026)*

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
