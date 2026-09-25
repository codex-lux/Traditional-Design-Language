# oq/which-packs-module-is-a-building-input — `trim-classical`'s module is the ceiling the reader sets; which other packs' modules are, and which only look as if they are

*Status: HALF CLOSED — ruled 25 Sep 2026; WP-14.18 declared `room-harmonic` and check 19 refused the other two class-A packs · Raised in: WP-14.0 (24 September 2026)*

**The finding that makes this a question.** On the Proportions page one pack could describe two
different walls at once. `trim-classical`'s module is, in its own words, *"The finished ceiling
height of the room, finished floor to finished ceiling"* (`proportions/systems/trim-classical.json:21`),
defaulting to 114 in. Its eighteen rules do not read `module` at all; they read the binding
`ceiling_height`, which the page's ceiling slider sets (`workbench/app/src/surfaces/Proportions.jsx:367`,
default 108) and `core.get_proportions` passes to the engine (`mcp_server/core.py:480`). The
members are dimensioned at the module. So at the page's defaults the rules table says the base
board is `ceiling_height * 1.5 / 19` = **8.53 in** on a 9′-0″ wall while the Georgian wall section,
drawn at 114 in, has a base of 1.5 parts = **9 in** on a 9′-6″ wall — a plate and a table of one
pack disagreeing about one board. WP-14.4 closes it for this pack by declaring
`module.equals: "ceiling_height"` — a restatement of the module's own `name`, lie-checked by a new
`check_systems` check — so the plate and the table are drawn at the reader's ceiling together.
That field does not exist yet (`schema/proportion-pack.schema.json`'s `module` object is
`additionalProperties: false`, `:87` on), and the question is who else carries it.

## What the reader can set today, and what nobody sets

The page has three sliders — column diameter (orders only), ceiling and opening
(`Proportions.jsx:366-368`) — and the engine is handed exactly two bindings,
`ceiling_height` and `opening_width` (`core.py:480`). Every other binding a rule reads —
`storey_height`, `room_width`, `room_length`, `span`, `wall_thickness`, `opening_height` — takes
`DEFAULT_BINDINGS` (`build/proportion_engine.py:388-391`) on every call, whatever the building.

## Candidates, read off each pack's `module.name`

A first reading, editorial and meant to be attacked — the ruling is what decides the class.

**A. The module names a quantity the rules ALSO read under a binding.** These are
`trim-classical`'s shape: two numbers for one quantity, which agree only because their defaults
were written equal.

| pack | `module.name` (abridged) | default | the same quantity as a binding |
|---|---|---|---|
| `storey-graduation` | one storey height of the principal floor | 120 | `storey_height` (120): `window_proportion`, `window_head_masonry` and `belt_course` read it while `ceiling_height_rule`, `cornice`, `baseboard`, `chair_rail` and `stair_type` read `module` |
| `room-harmonic` | the short dimension of the room in plan — its breadth | 192 | `room_width` (192): the vaulted-ceiling means read `room_width` and `room_length` while every width rule reads `module` |
| `opening-pointed` | the span of the opening at the springing line | 36 | `opening_width` (36): `window_lite_pattern` reads the slider while `arch`, `dormer`, `gable_treatment` and `chimney` read `module` |

Moving the slider on `opening-pointed` today changes how many lights the window has and not the
arch those lights sit under.

**B. The trap: `opening-proportion`, whose module and slider are two DIFFERENT openings.** Its
module is *"The width of the principal door leaf"* (default 36) and its door rules read it —
`entry_door` height `module * 2`, `interior_door` `module * 2.17`, `door_surround`,
`transom_sidelight`, `secondary_door`. Its window rules read `opening_width` — `window_sill`,
`window_surround_wood`, `special_window`. The defaults are both 36 and they are not the same
thing: making the module follow the opening slider would move the front door every time a reader
sized a window. That is OQ 48's error — two quantities under one name — arriving through a UI
control. The honest version is a second input (*door leaf*), not `equals: "opening_width"`.

**C. The module names a building dimension no slider sets but a plan record could.** The bay
(`facade-classical` 108, `timber-bay` 192, `facade-medieval-english` 156, `facade-pavilion` 192) —
a placed plan states its bay module in `footprint.bays`; the half-span (`dutch-gambrel` 144) and the
gable's width at the eave (`facade-gable` 144) — the footprint's depth and width; the joist span
(`room-vernacular` 168), the side of an octagon (`octagon-geometry` 192), an arch's clear span
(`facade-arcade` 96), the axial intercolumniation (`facade-peristyle` 144), the portada's width
(`facade-portada` 144), the dominant mass (`facade-picturesque` 288).

**D. The module is a material or a component, set by a mould, a mason or a mill, not by the
building.** One adobe (`adobe-module`), a coursing measure (`brick-course`, `corbel-course`,
`stone-course`), one pane (`sash-light`), one carriable log (`log-module`), a joist's depth
(`jetty-overhang`), one board (`trim-craftsman`, `trim-prairie`), a pattern repeat (`trim-sawn`),
a panel between studs (`timber-panel`), a rail bay (`balcony-gallery`), one light between mullions
(`opening-mullioned`). A slider on these would be a lie about how they were set out.

(`moorish-arch` and the order packs are outside this question: an order's module is a function of
the column diameter the page already asks for.)

## What each answer would change

1. **`equals` for class A only** — three more declarations, each lie-checked the way WP-14.4's is,
   and the page gains a storey and a room-breadth input. The engine then binds `module` from the
   named binding, so the two readings inside each pack cannot part.
2. **A and a door-leaf input for B** — the page gains a fourth input; `opening-proportion`
   declares its module equal to *that*, and the window rules keep the opening slider.
3. **A, B and C from the plan on the bench** — the module of a class-C pack is read from the placed
   record (bay, width, depth) rather than set by a slider. It ties the Proportions page to the house
   journey, which is Phase 14's design, and it makes a pack page depend on a plan that may be
   refused (`oq/the-worked-house-has-no-plan-that-places`).
4. **`trim-classical` alone** — every other pack keeps its default module and the page says, per
   pack, *"drawn at the pack's default module, not at your building"*.

Whichever is ruled, class A's double reading is a defect in the DATA today whether or not any
slider moves, because an MCP caller passing `module=` to `tdl_get_proportions` on
`storey-graduation` changes half its rules and not the other half.

## What tranche 1 does meanwhile

WP-14.4 declares `equals` on `trim-classical` and nowhere else, adds the `check_systems` lie-check
for that field, and serves `module_name` so the page can print what the module IS beside its size.
Every other pack is drawn and dimensioned at its default module, and the payload's `at` and
`module_bound_to` (the phase PRD's contract) say which figure was the reader's and which was the
pack's default, so the page never implies a building the reader did not describe.

## Related

- `oq/casings-are-measured-across-and-drawn-upright` — the other half of drawing a trim pack
  truthfully: which way it runs, and where its zones fall.

## Ruled 25 September 2026

**Answer 1, class A only**, taken with the tranche-2 plan's approval. `module.equals` gains the storey, room-width and opening-width dimensions, and the three class-A packs declare them. Each declaration is made only where the existing lie-check (check 19(c)) passes. Where it fails, the package files a question and authors no number. The contract is `docs/prd/phase-14-tranche-2.md` §C.3. The question closes when WP-14.18 lands.

## Executed 25 September 2026, by WP-14.18, and half closed

The enum is `ceiling_height`, `storey_height`, `room_width` and `opening_width`, each a variable
the engine binds (`tests/test_module_equals.py` holds the enum inside `check_systems.RULE_VARS`).
Check 19 was run on each class-A pack before anything was written, and it passed on ONE:

- **`room-harmonic` declares `module.equals: room_width`.** Its module name is *"The short
  dimension of the room in plan - its breadth"*. Its three vaulted-ceiling means read
  `room_width` and `room_length` alone, and every other rule reads `module` or no variable at all,
  so no rule counts the breadth twice. The MCP tool and the workbench route take `room_width` now, and with none given
  the pack is worked at its own 192 in (`module_from: "default"`).
- **`storey-graduation` and `opening-pointed` are REFUSED**, each by one rule that reads the input
  together with `part`: `belt_course.height = storey_height + part * 0.6` and
  `window_lite_pattern.count = max(2, round(opening_width / (part * 5)))`. Declared, the first
  would move the belt course from six inches above every storey to five per cent of the storey,
  and the second would give two lights at every opening width, never reaching its own range of 2
  to 4. No number was authored to dissolve either. The measurements and the answers are in
  `oq/two-class-a-modules-are-refused-for-a-rule-that-reads-the-input-and-its-part`.

**What this leaves open.** The half of answer 1 that is built is closed. The refusals are
recorded in their own question, and classes B, C and D are unruled here, as they were. **One
thing measured while doing it belongs to class A's own half:** `room-harmonic` generates the
room's LENGTH from its module (`room_adjacency_overrides`, `module * 4 / 3` and the rest), while
the vaulted-ceiling means read a `room_length` binding that nobody sets and that defaults to
288 in, which is 192 × 3/2 and no other ratio. With the module following the reader's breadth,
the length those means read is still the default's. That is the same two-numbers-for-one-quantity
shape one dimension over, and declaring `room_width` did not create it: before the declaration
the module stayed at 192 whatever breadth was given, so the means and the widths already
disagreed. The report names it and nothing was changed for it.
