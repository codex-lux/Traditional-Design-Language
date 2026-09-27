# oq/which-end-of-a-moulding-its-projection-names — 25 curves the record gives no run, for two different reasons

*Status: OPEN · Raised in: WP-14.2, the orders and mouldings (27 September 2026)*

**OPEN — a quarter or a cyma is a curve between two faces, and 25 of the 161 published curved
members in the order stacks are handed two faces that are the same face.** `build/profiles.py`
draws each as the vertical line its figures describe, and since WP-14.2 every surface says so
(`drawn_straight`; "N CURVED MEMBER(S) DRAWN STRAIGHT" on the profile plates and the elevation's
cornice inset). What it does not do is decide why the run is missing, because the two causes are two
different questions about how the record is read, and either answer moves ink the corpus has drawn
the same way since WP-5.11.

Measured over all 26 order packs at a 36 in module, every stack assembly, `pack_geometry` as of
WP-14.2 step 4:

| cause | members | where |
|---|---:|---|
| the walk restarts each assembly at its own datum | 14 | `shaft.apophyge_lower` on every Ionic, Corinthian and Composite pack of Vignola, Palladio, Gibbs, Chambers and Benjamin |
| the figure equals the face of the member below | 8 | `pedestal.ped_base_cyma` / `ped_base_ogee` on vignola-ionic, -corinthian, -composite, palladio-ionic and gibbs-doric, -ionic, -corinthian, -composite |
| the same | 3 | `capital.cap_cyma` on vignola-doric, gibbs-doric and chambers-doric |

## The first cause: an apophyge cannot flare from a fillet it is never shown

`pack_geometry` walks each assembly from that assembly's own datum, so the shaft's first member starts
at the column's radius, not at the face of the base's top fillet that it physically meets. The lower
apophyge is the flare between the two. Given a start at the radius and a face at the radius, it has
nothing to flare across, and the drawn column steps square from fillet to shaft at every foot.
Carrying the previous assembly's last face into the next assembly's first member would draw the
flare. It would also change the start of every assembly's first member in every stack. On the
members measured that change is confined to the 14 apophyges, but it is a change to the walk itself,
not to the 14.

## The second cause: which end of a moulding its figure names

`member_path` reads a member's projection as its face at the TOP of its height: the walk arrives at
`x_from` at the member's foot and leaves at the face. Eleven records give a curved member the same
figure as the member below it:
- Vignola's Ionic pedestal carries `ped_plinth` 11.0, `ped_base_cyma` 11.0 and `ped_base_fillet` 8.5.
  Read as its foot, the cyma recedes from 11.0 to 8.5, which is what a pedestal's base moulding does.
- Read as its top, as the walk reads it, the cyma cannot curve at all.

The Doric capital's cymatium is the same pattern above the abacus. A table of mouldings commonly
gives a receding member's GREATEST projection, which is its foot. The record never says which end it
means, and no note in the eleven says either.

## What would have to be ruled

1. Whether a curved member's `projection_parts` names its top face, its greatest projection, or the
   end that meets its neighbour. The third reading would need the schema to say so per member, since
   the notes do not.
2. Whether the walk carries a face across an assembly boundary, and for which assemblies. The
   base-to-shaft joint is the case measured here. The shaft-to-capital and pedestal-to-base joints
   are the ones to measure next.
3. Whether the plates that would settle the eleven are the first entries on
   `Plan Examples/Plates/WANTED.md` (WP-14.5): the plates show the curve, and the record does not.

Until then the drawing is the honest one: a vertical line at the face the record states, counted and
said on every surface that draws it.
