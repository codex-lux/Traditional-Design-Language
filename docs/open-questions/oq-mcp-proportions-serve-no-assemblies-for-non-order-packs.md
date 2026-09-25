# oq/mcp-proportions-serve-no-assemblies-for-non-order-packs — the workbench will draw twenty-seven packs the MCP tool still reports as having no assemblies

*Status: CLOSED — ruled 25 Sep 2026 (answer 1), executed by WP-14.18 on 25 Sep 2026 · Raised in: WP-14.0 (24 September 2026)*

**The finding.** `tdl_get_proportions` (`mcp_server/server.py:117`) calls
`core.get_proportions`, which dimensions the pack with
`pe.dimension(pk, mod, [assembly] if assembly else None)` (`mcp_server/core.py:459`). With no
`assembly` argument the engine falls back to `stack_for(pack)` (`build/proportion_engine.py:292`),
and `stack_for` (`:254-266`) knows only the names of an ORDER's stack — pedestal, subplinth, base,
shaft, capital, architrave, frieze, cornice, entablature. Every other pack gets an empty stack and
therefore an empty `assemblies` list.

**Measured on this tree, over all 57 packs:** 27 have assemblies and an empty stack — `adobe-module,
balcony-gallery, brick-course, corbel-course, dutch-gambrel, facade-arcade, facade-classical,
facade-gable, facade-medieval-english, facade-pavilion, facade-peristyle, facade-picturesque,
facade-portada, jetty-overhang, log-module, moorish-arch, octagon-geometry, opening-craftsman,
opening-mullioned, opening-pointed, sash-light, stone-course, timber-panel, trim-classical,
trim-craftsman, trim-prairie, trim-sawn` — holding **50 assemblies and 237 members** between them,
all of which the tool reports as none. Five more have no assemblies at all. `moorish-arch` is the
instructive one: its three assemblies are `impost`, `arch` and `alfiz`, none an order name.

**What the payload for `trim-classical` says instead**, called with no arguments:

- `assemblies: []`, `totals: {stack_height_in: 0.0, lower_diameter_in: 228.0}` — a column
  diameter of nineteen feet for a pack with no column, because `proportion_engine.py:343-345`
  divides the module by `diameters_per_module` for every pack and reads the 9′-6″ ceiling as a
  semidiameter. The workbench's `profiles.pack_geometry` reads the same figure as the column's
  radius (`build/profiles.py:522`), which is the misreading WP-14.4 corrects on the drawing side
  with a wall datum.
- `hint: "pass assembly='cornice' (or capital, base, entablature, pedestal) for member-by-member
  dimensions"` (`core.py:514`) — order vocabulary, none of which this pack has.
- **The tool CAN return the members, and a caller cannot find out how.** Called with
  `assembly='wall_section_georgian'` it returns that assembly with 20 members; the six assemblies
  together return 20, 21, 12, 7, 7 and 4 — **71**, the figure the workbench plate will draw. But
  the no-argument response names no assembly id anywhere except inside the invariant EXPRESSIONS
  (`assemblies.wall_section_georgian.members.geo_wall_field.height_parts == 12`), so a machine
  client must parse an expression string to learn what to ask for.

**The workbench path had the same defect and WP-14.4 fixes it there only.**
`corpus.proportions_with_members` (`workbench/server/corpus.py:317-358`) calls
`pe.dimension(pk, out["module_in"], None)` at `:328`; WP-14.4 dimensions each assembly with
`include=[aid]` when the stack is empty, and asserts the MCP `get_proportions` payload unchanged,
because tranche 1 keeps every MCP payload byte-stable.

## What each answer would change

1. **The MCP tool follows the workbench** — `core.get_proportions` lists every assembly of a
   stackless pack (id, height, member COUNT, keeping its progressive-disclosure convention of
   members only on request), the hint names the pack's own assembly ids, and `lower_diameter_in`
   is withheld where the pack declares no column. That changes the payload of 27 packs for every
   MCP client, the rail's tool results, and whatever pins `get_proportions` output
   (`tests/test_score.py`'s `RULE_KEYS` guard reads the rule rows, not the assemblies, so the pin to
   move has to be found rather than assumed).
2. **Discovery only** — keep `assemblies: []` for the stack and add an `assembly_ids` list and a
   correct hint. Smallest change that lets a machine reach the 71 members, and it leaves the false
   `lower_diameter_in` in place, which is OQ 52's shape (a measurement stated where none was taken).
3. **Leave it, and say so** — the workbench is the drawing surface and the MCP tool is text; the
   tool's docstring states that non-order packs must be asked per assembly and names where the ids
   are. Cheapest; it keeps two answers to *"what is in this pack"* in one repository, which is the
   defect this corpus keeps meeting.

Whichever is chosen, the `lower_diameter_in: 228.0` is a separate defect in the same payload and
should not wait on the ruling about assemblies — it is served today, to every caller, for every
stackless pack.

## What tranche 1 does meanwhile

WP-14.4 changes the workbench route and nothing in `mcp_server/`; its tests assert the MCP payload
is byte-identical before and after. The asymmetry is recorded here rather than closed by the
package that creates it.

## Related

- `oq/the-assistant-is-blind-to-the-page` — the assistant drives these same tools, so it inherits
  the empty list.
- `oq/casings-are-measured-across-and-drawn-upright` — what a payload that does list these
  assemblies would still not say about them.

## Ruled 25 September 2026

**Answer 1, full parity.** It follows the ruling that lifts tranche 1's freezes per item, named. `tdl_get_proportions` lists a stackless pack's own assemblies. Its hint names them. It withholds the column diameter on a pack with no column. It reads the module binding from the one spelling the workbench also reads. A digest pin holds the stacked packs' payloads byte-identical. The contract is `docs/prd/phase-14-tranche-2.md` §C.4. The question closes when WP-14.18 lands.

## Closed 25 September 2026, by WP-14.18

Answer 1 is built (`docs/reports/wp-14.18-proportions-served-whole.md`), and the freeze on this
one MCP payload is lifted by name. Measured on that package's tree, over all 57 packs, with
`core.get_proportions` called with no arguments:

- **The 27 stackless packs with assemblies list all 50 of them**, each as
  `{id, height_modules, height_in, members: <count>}` plus `axis` and `zones` where the pack
  declares them. The counts sum to **237**, the figure this entry published, and
  `trim-classical`'s six are 20, 21, 12, 7, 7 and 4 (71). Members still come one assembly at a
  time, which keeps the tool's progressive disclosure.
- **The hint names the pack's own assembly ids on all 27**, with no misses. A pack with no
  assemblies (the five named above) says it states none and does not name an order's.
- **`lower_diameter_in` is withheld on all 32 stackless packs**, and none of them declares a
  column. `trim-classical`'s totals were `{stack_height_in: 0.0, lower_diameter_in: 228.0}` on
  `f0dc52a` and are `{stack_height_in: 0.0}` now. This is done in `core`, and
  `build/proportion_engine.py` is unchanged.
- **The module binding has one spelling**, `core.module_binding`, and
  `corpus.proportions_with_members` reads it. That settles the 108-against-114 disagreement: a
  pack bound to a building dimension, with that dimension not given, is worked at its own
  `default_size_in` on both surfaces, and the payload says so (`module_bound_to`, `module_from`).
  Measured on a `git archive` of `f0dc52a`, the tool dimensioned `trim-classical` at 114 in and
  evaluated its rules at a ceiling of 108, so its base board read **8.5263 in** beside members
  drawn at a 6 in part. It reads **9.0** now, at 114 on both.
- **A contradictory call is refused by name**: a column diameter on a pack whose module is a
  building dimension, or a `module` that differs from the dimension the module IS. The
  workbench route answers 422 with the same refusal.
- **The pin.** `workbench/server/tests/test_pack_plates.py` hashes the payload of every STACKED
  pack (25) over seven call shapes to `7ac8e89730301b1d`. It was derived first on a `git archive`
  of `f0dc52a` and reproduced on the package's tree, and a wrapper that adds one key to one
  stacked payload turns it red.

What stays open is the plate's half of `oq/casings-are-measured-across-and-drawn-upright`, which
is WP-14.24's, and the two class-A packs `oq/two-class-a-modules-are-refused-for-a-rule-that-reads-the-input-and-its-part`
records.
