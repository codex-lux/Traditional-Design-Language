# oq/an-inherited-ban-decides-what-the-elevation-may-draw — most of what the elevation is forbidden to draw, a style never forbade

*Status: OPEN · Raised in: WP-14.1, the ink read back (27 September 2026)*

**Lucas ruled on 27 Sep 2026 that the elevation should refuse, and say, whatever a style's
resolved kit forbids, whether a whole slot or one variant (Phase 14, decision 4). WP-14.1's census
then measured where those prohibitions come from, and most of them are not the style's.** The
elevation draws the same five packs for every style (`oq/the-elevation-reads-five-packs-whatever-the-style-binds`),
so on the Tidewater placement with each style swapped in, 79 of the 159 nodes with a kit draw
something their resolved kit forbids (census check V2):

| feature drawn | forbidden by the style's own record | forbidden by an ancestor's |
|---|---:|---:|
| belt course | 8 | 17 |
| cornice | 10 | 14 |
| doorcase (pilasters and entablature) | 9 | 29 |
| frieze | 5 | 21 |
| modillions | 16 | 37 |
| sidelights | 8 | 39 |
| water table | 4 | 21 |

**Of the 79 styles, 11 are convicted only by their own record, 51 only by an ancestor's, and 17
by both.** The largest donors of inherited prohibitions are `gothic-revival-british` (61),
`shingle-style` (36) and `mediterranean-vernacular` (21).

## The case that decides nothing either way

**`colonial-revival`**, the style the shipped spec Colonial resolves to, inherits its bans on the
water table, the belt and the frieze from `shingle-style`, two steps up its lineage. Its own
`door_surround` is an `extends` delta whose BASE the cascade took from `gothic-revival-british`,
the nearest ancestor that binds the slot. That base makes `pointed-arch-hood-mould-buttressed-porch`
canonical and forbids `pilasters-and-entablature`, while the delta's own note reads: *"The
inherited pilasters-and-entablature binding (english-georgian) is the right assembly."* The node's
author wrote the delta against a base the cascade does not deliver. Refusing on the resolved kit
would strip the spec Colonial of its water table, belt, frieze, modillion cornice and doorcase.

**`tidewater-georgian`'s sidelights are the counter-case.** They are forbidden by
`georgian-colonial-american` ("Same date boundary as the fanlight, and they normally arrive
together"), an ancestor, and that prohibition is plainly meant to reach a house dated 1765. So
"own against inherited" does not sort the right prohibitions from the wrong ones. That sort is a
judgment per case, the shape of OQ 51's adjudication, one layer over, on slots instead of packs.

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
