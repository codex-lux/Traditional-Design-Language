# oq/casings-are-measured-across-and-drawn-upright — an assembly's axis and its zones are stated only in prose, so a plate can draw neither

*Status: OPEN · Raised in: WP-14.0 (24 September 2026)*

**The finding.** WP-14.4 serves every pack that has assemblies and no order stack, and WP-14.9
draws them — `trim-classical` among them, the page Lucas was reading. Two facts a draughtsman would
put on that plate first are in the pack only as sentences, so the plate cannot draw them without
inventing a reading, and tranche 1 refuses both.

## 1. Which way an assembly runs

`schema/proportion-pack.schema.json:165-177` gives an assembly three fields —
`height_modules`, `sums_check`, `members` — under `additionalProperties: false`, and describes
every assembly as *"a stack of members, bottom to top, dimensioned in PARTS of the module"*
(`:167`). `trim-classical`'s three casings are not bottom to top. The pack says so in a member's
NOTE and nowhere else: `geo_cas_reveal` at `proportions/systems/trim-classical.json:511` — *"This
assembly is measured ACROSS the casing from the jamb outward rather than vertically;
height_parts is therefore a width"* — and the Federal and Greek Revival casings repeat it in notes
at `:575` and `:641`. So `height_parts` means a height on three assemblies of that pack and a width
on the other three, and the only record of which is prose attached to one member.

**It is not one pack.** A sweep of member notes for the same move found four more assemblies where
a field means something other than the schema's description of it — here `projection_parts`, which
the schema defines as *"Projection in PARTS, measured from the datum this pack's projection_datum
names"* (`:204-205`): `proportions/modules/dutch-gambrel.json:36` and
`proportions/systems/facade-pavilion.json:78` (a horizontal RUN), `proportions/modules/stone-course.json:78`
(a FACE LENGTH), `proportions/systems/facade-arcade.json:46` (a pier's WIDTH on the face). The
sweep was a regex over notes and is a floor, not a census; OQ 65 is the precedent for declaring a
datum per pack rather than leaving each reader to derive it.

## 2. How the wall divides

The pack's argument is that a room is an order and its wall divides in nineteen parts, pedestal 4,
wall field 12, entablature 3. That division is stated three times, all prose: the module note
(`:24`), the pack notes (`:1053`), and an invariant sentence (`:680`) whose EXPRESSION is
`module.parts == 4 + 12 + 3` (`:681`) — which checks that `parts` is 19 and nothing about where
any member ends. **And the division is true of one family in three.** Summing member heights up
each wall section:

| wall section | pedestal ends at | wall field ends at | top |
|---|---|---|---|
| Georgian | 4.00 (`geo_surbase_listel`) | 16.00 | 19.00 |
| Federal | 3.75 (`fed_surbase_listel`) | 16.25 | 19.00 |
| Greek Revival | 1.90 (`grk_base_cap_fillet`) — no dado | 16.00 | 19.00 |

So a `4 + 12 + 3` dimension string drawn on every wall section would be false on two of the three
plates. The two invariants that touch a zone (`:685-691`) read the Georgian wall field's own
`height_parts` and nothing else — the second derives the pedestal as a third of the field
(`19 - 12 - 12/3 == 12/4`) rather than summing the members under it — so a member moved from the
dado into the base board would pass both. The Greek Revival row is the pack's own claim that *"the
pedestal has collapsed into the base board"* (the invariant at `:721`, and `grk_wall_field`'s note
at `:427`), which is exactly what a zone field would have to be able to say.

## What each answer would change

1. **Packs declare both, per ASSEMBLY.** An `axis` (`up-the-wall` | `across-from-the-jamb` | …)
   and optional `zones` (`[{name, to_parts}]`) on the assembly object; the schema's
   `additionalProperties: false` means a version bump. A checker holds each zone boundary to the
   cumulative member sums, so the Federal cannot declare 4 + 12 + 3 and pass. The plate then draws
   casings turned and dimensions each wall by its own zones. `profiles.pack_geometry` and the MCP
   payload both gain the fields; `render_profile.py` and every order pack are untouched only if
   the fields are optional and absent there, which is a test to write rather than assume.
2. **The meaning of `projection_parts` is declared too** — the four packs above either move their
   figure to a named field or declare the reading, on OQ 65's precedent. Larger, because a reader
   of `projection_parts` today (`build/profiles.py`, the elevation cornice, `export_dxf`) would
   have to consult the declaration or be shown not to reach those assemblies.
3. **Prose stays the record.** Every non-order assembly is drawn upright forever, with the
   caption saying so, and a zone string is never drawn. Cheapest, and it leaves the one number the
   pack exists to teach — the division — invisible on the drawing of it.

## What tranche 1 does meanwhile

WP-14.9 draws every assembly upright, in its served order, and its foot line says *"drawn from the
record · drawn upright"*. Three things are refused out loud rather than approximated: the
4 + 12 + 3 dimension string, turned casings, and a picture for the five packs that have no
assemblies at all (`opening-proportion`, `room-harmonic`, `room-vernacular`, `storey-graduation`,
`timber-bay`). No field is added to any pack for this.

## Related

- `oq/which-packs-module-is-a-building-input` — the other half of drawing this plate truthfully:
  at what size.
