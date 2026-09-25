# oq/casings-are-measured-across-and-drawn-upright — an assembly's axis and its zones are stated only in prose, so a plate can draw neither

*Status: CLOSED 25 Sep 2026 — answer 1, executed by WP-14.18 (data and checker) and WP-14.24 (the plate) · Raised in: WP-14.0 (24 September 2026)*

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

## Ruled 25 September 2026

**Answer 1: axis and zones as data.** An assembly may declare `axis` and optional `zones`. `build/check_orders.py` holds every zone boundary to a cumulative member-height sum. The plate draws casings turned and prints the zone string, and the MCP payload carries both fields. Zones are declared only where the pack's own words give them; nothing is authored from outside the pack. The contract is `docs/prd/phase-14-tranche-2.md` §C.3 and §C.9. The question closes when WP-14.24 lands, the second of the two.

## Amended 25 September 2026: the data and checker half is built (WP-14.18); the plate half is WP-14.24's

WP-14.18 built the half this question gave it (`docs/reports/wp-14.18-proportions-served-whole.md`),
and the question stays IN PROGRESS because the plate does not yet read either field.

- **The schema** admits `axis` (`up-the-wall` | `across-from-the-jamb`, absent meaning
  up-the-wall) and `zones` (`[{name, to_parts}]`, at least two) on the assembly object. Answer 1
  says *"a version bump"*, and `schema/proportion-pack.schema.json` carries no version field, so
  there was nothing to bump. Both fields are optional, and no order pack declares either.
- **The checker.** `build/check_orders.py::assembly_declaration_errors`, called from `check_pack`
  beside the sum check, holds four rules: zones strictly increase, every boundary is a running
  member total, the last is the assembly's whole height, and a `sums_check: false` assembly
  declares none. Every error names the pack, the assembly and the zone.
  `tests/test_assembly_zones.py` drives each rule. **The Federal wall given the Georgian
  4 / 16 / 19 goes red on its pedestal and its field and not on its entablature**, which is this
  entry's own case.
- **The data, and only what the pack's words give.** The three casings are
  `across-from-the-jamb` on their reveal notes: *"This assembly is measured ACROSS the casing from
  the jamb outward rather than vertically; height_parts is therefore a width."*, *"Measured across
  the casing, as in the Georgian assembly."* and *"Measured across the casing, as in the other two
  families."* The Georgian wall section takes zones pedestal 4, wall field 16, entablature 19, from
  *"Pedestal 4, wall field 12, entablature 3"*. Its running totals really pass through 4, 16 and
  19 (after `geo_surbase_listel`, `geo_wall_field` and `geo_cornice_fillet`).
  **The Federal and the Greek Revival sections take NO zones.** The Federal's pedestal ends at
  3.75 parts and its field at 16.25, so the pack's one stated division is false of it, and no
  sentence gives its own. The Greek Revival's base ends at 1.9 parts because *"the dado has been
  abandoned and the pedestal has collapsed into the base board"*. That sentence states the
  collapse and not a figure, so a zone there would be read back off the members.
- **Where the fields travel.** Both are passed through exactly as declared, on the MCP payload's
  assembly rows and on the workbench route's members rows (`corpus._wall_assemblies`). They are
  not put inside `profiles.pack_geometry`'s geometry, which stays upright. Turning is the plate's
  work, one `rotate` per §C.9 of the tranche-2 PRD, and `build/profiles.py` and
  `render_profile.py` are unchanged.

**Two sentences are now ahead of what they describe, until WP-14.24 lands.** The Proportions
page's refusal note (`data-refused="zones"`) says *"nothing in the record says where a zone
ends"*, which is false of `trim-classical`'s Georgian wall from this commit. The
`figure-drawn-upright` glossary record says *"the plate does not turn it"*, which is still true of
the plate, and the record now holds the axis the plate will turn by. Both are WP-14.24's to
change: the page file is outside WP-14.18's lane, and `glossary/figure-drawn-turned.json` is
written here for the caption that package will draw.

## Amended 25 September 2026: the plate half is built (WP-14.24), and the question closes

WP-14.24 built the plate half (`docs/reports/wp-14.24-plates-at-the-packs-word.md`). The ruling
said the question closes when that package lands, and it closes here.

- **The casings are drawn turned.** `plate/assemblyLayout.js::extentOf` swaps the extent of an
  assembly declaring `across-from-the-jamb`, and `plate/assemblyPlan.js::bandTransform` adds one
  `rotate(90)` between the translate and the scale. The served paths are not touched, so no arc
  arithmetic reaches JavaScript and `OrderPlate` is unchanged. On `trim-classical` the three
  casings stand in a frame of their own, hanging from their wall plane with the jamb at the left,
  and each drawn box is wider than it is tall (measured in the browser walk, `⑩c`). The wall
  sections stay upright.
- **The Georgian wall prints its zones.** `zoneString` is the one reading of the served
  `to_parts`: the differences `4 + 12 + 3`, and the same in feet and inches through
  `feetInches16`, under the wall with zone ticks on a dimension line beside it. The Federal and
  the Greek Revival sections, which carry no zones, print no string. A constant `4 + 12 + 3`
  drawn on a Federal fixture turns `src/assemblyPlan.test.mjs` red, and the same mutation turns
  the walk red.
- **The two sentences this entry said were ahead of what they describe.** The page's
  `data-refused="zones"` note is now true per assembly: it names the assemblies that carry the
  pack's division and, separately, those the record gives none (`zonesByAssembly`). The
  `figure-drawn-upright` record is rewritten for the plate that turns, and the caption is shown
  only on a frame that draws something upright. *Drawn turned* (`figure-drawn-turned`, written by
  WP-14.18) is shown only on a frame that draws something turned.

**What this closure does not answer.** The entry's other finding was that four assemblies write
a horizontal run, a face length or a pier width in `projection_parts`. It was offered as
answer 2 and not ruled. It is raised as its own question,
`oq/four-assemblies-state-projection-parts-as-a-run-a-face-or-a-width`, so that closing this one
does not leave it with no home. Zones on the ORDER packs are
`oq/six-order-assemblies-state-a-division-and-carry-no-zones` (WP-14.18), and nothing here
changes it.
