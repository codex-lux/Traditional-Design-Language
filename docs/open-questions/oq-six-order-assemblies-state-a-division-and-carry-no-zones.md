# oq/six-order-assemblies-state-a-division-and-carry-no-zones — the order packs state how six of their assemblies divide, and WP-14.18 declared zones on a wall section only

*Status: OPEN · Raised in: WP-14.18 (25 September 2026)*

**The finding.** WP-14.18 gave an assembly `zones` (`schema/proportion-pack.schema.json`), the
divisions a pack's own words give it, each ending on a member boundary and held there by
`build/check_orders.py::assembly_declaration_errors`. It declared zones on one assembly,
`trim-classical`'s `wall_section_georgian` (*"Pedestal 4, wall field 12, entablature 3"*). A
finder over every pack's prose (a sequence of numbers whose running sums all land on member
boundaries of one of that pack's own assemblies and whose total is that assembly's height) turns
up six more, all in STACKED packs, the orders:

| pack / assembly | the pack's words | zones they would give | members per zone |
|---|---|---|---|
| `vignola-corinthian` / `capital` | `notes`: 12 : 12 : 12 : 6 | two acanthus rows, the caulicoli, the abacus | 1, 1, 1, **3** |
| `vignola-corinthian` / `cornice` | `notes`: 14.4, 7.2, 14.4 | the bed mouldings, the modillions, the corona and cymatium | **6, 3, 4** |
| `vignola-composite` / `entablature` | `notes`: 27, 27 and 36 | architrave, frieze, cornice | 1, 1, 1 |
| `benjamin-corinthian` / `entablature` | `notes`, an invariant and a member note: 31 : 41 : 48 | architrave, frieze, cornice | 1, 1, 1 |
| `gibbs-doric` / `cornice` | `notes`: 2 : 4 : 4 : 4 : 4 | five members | 1 each |
| `gibbs-tuscan` / `entablature` | `notes`: 12 : 12 : 18 | architrave, frieze, cornice | 1, 1, 1 |

Four of the six are ONE-TO-ONE: each zone is exactly one member, so zones would restate the
member list. The schema's own description says why that is not wanted: a zone *"that merely
restates the members says nothing a reader could not already see"*. Two are SUBSTANTIVE,
`vignola-corinthian`'s capital (the abacus is three members) and its cornice (thirteen members in
three stated runs). They carry the same kind of information the Georgian wall's zones carry.

**Why none was declared.** Three reasons, and the first is the ruling's:

1. **The payload of a stacked pack is frozen.** The 25 Sep ruling lifted tranche 1's freeze on
   `tdl_get_proportions` for the stackless packs' assemblies and nothing else, and WP-14.18
   proves it with a digest pin: `workbench/server/tests/test_pack_plates.py` hashes every stacked
   pack's MCP payload over seven call shapes (`7ac8e89730301b1d`, derived first on a `git archive`
   of `f0dc52a`). `core._assembly_row` passes a declared `zones` through on ANY pack, so a zone
   written on `vignola-corinthian` would move that pin. Using the lift for a surface it was not
   given for is the move the ruling forbids.
2. **Nothing would draw them.** The order packs are drawn by `OrderPlate` and `dist/orders.html`,
   and neither reads `zones`. WP-14.24 draws the zone string on the stackless plate, and its
   contract (`docs/prd/phase-14-tranche-2.md` §C.9) leaves `OrderPlate` unchanged.
3. **Benjamin's stated division is not the one his stack draws.** `benjamin-corinthian`'s own
   `entablature` is 31 : 41 : 48 of 120 parts (28 in), while its stack takes `architrave`,
   `frieze` and `cornice` from `vignola-corinthian` at 1.5 + 1.5 + 2 modules (35 in), and its
   `totals.entablature_height_in` reports 28. A zone on Benjamin's entablature would dimension
   an assembly no plate of his order draws. That is a defect of its own and is filed as a task,
   not answered here.

**The question.** Should an order pack declare the divisions its own prose states, and if so:

1. **Only the substantive ones**, the two `vignola-corinthian` assemblies, with the freeze
   lifted for those two payloads by name and a drawing surface named to read them.
2. **All six**, taking the one-to-one cases as a machine-readable statement of what the prose
   already says, against the schema's own reason for not restating members.
3. **None**, leaving the prose as the only statement for orders and `zones` a property of the
   stackless families. That is the state WP-14.18 leaves, and it is recorded here so it is a
   decision rather than a default.
