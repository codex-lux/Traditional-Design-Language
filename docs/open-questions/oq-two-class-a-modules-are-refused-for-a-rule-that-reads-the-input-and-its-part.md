# oq/two-class-a-modules-are-refused-for-a-rule-that-reads-the-input-and-its-part — `storey-graduation` and `opening-pointed` each carry one rule that reads the building input AND the module's part, so declaring the module equal to that input counts the input twice

*Status: OPEN · Raised in: WP-14.18 (25 September 2026)*

**The finding.** `oq/which-packs-module-is-a-building-input` was ruled on 25 Sep 2026 (answer 1,
class A only): declare `module.equals` on `storey-graduation`, `room-harmonic` and
`opening-pointed` where `build/check_systems.py` check 19 passes, and where it fails author no
number and say why. Measured by WP-14.18, check 19 passes on ONE of the three. `room-harmonic`
declares `module.equals: room_width` now. The other two are refused by condition (c), *a rule
reads the input together with `module` or `part`*, and each is refused by exactly one rule of its
own:

| pack | the rule | expression |
|---|---|---|
| `storey-graduation` (`proportions/modules/storey-graduation.json`, 12 parts, default 120 in) | `derived_rules[8]`, `belt_course.height` | `storey_height + part * 0.6` |
| `opening-pointed` (`proportions/systems/opening-pointed.json`, 12 parts, default 36 in) | `derived_rules[5]`, `window_lite_pattern.count` | `max(2, round(opening_width / (part * 5)))` |

Every other rule in both packs that reads the input reads it alone
(`storey-graduation`'s `window_proportion` and `window_head_masonry`), so the declaration is
refused on these two rules and on nothing else. `tests/test_module_equals.py::TestTheClassAOutcome`
holds that: a copy of each pack with the declaration added is refused ONLY on the named rule.

**Why check 19 is right to refuse, measured rather than argued.** With the module left alone,
`part` is a fixed length (10 in for the storey pack, 3 in for the opening pack) and the input
moves. With `module.equals` declared, `part` becomes the input over the parts, so the input is
read twice, once directly and once through `part`. The numbers, at the input's own values
(`python3` over `proportion_engine.evaluate_expr` at 0.75x, 1x, 4/3x and 5/3x the pack's default):

| `storey_height` (in) | `belt_course.height`, undeclared | declared |
|---|---|---|
| 90 | 96.0 | 94.5 |
| 120 | 126.0 | 126.0 |
| 160 | 166.0 | 168.0 |
| 200 | 206.0 | 210.0 |

| `opening_width` (in) | `window_lite_pattern.count`, undeclared | declared |
|---|---|---|
| 27 | 2 | 2 |
| 36 | 2 | 2 |
| 48 | 3 | 2 |
| 60 | 4 | 2 |

The belt course's offset above the storey is *"about six inches above the top of the first
storey on the default, i.e. on the joist zone"* (the rule's own note). Undeclared it is 6 in at
every storey; declared it is five per cent of the storey and grows with it. The window's light
count undeclared follows the opening across its own stated range of 2 to 4; declared, it is
`opening / (opening × 5 / 12)`, which is 2.4 for every opening, so the rule can never say three
or four lights. The declaration would change what the rule MEANS on both packs, and on the
opening pack it would make the rule constant.

**Why it is a question and not a fix.** Each refusal can be dissolved by rewriting its rule on an
independent quantity: the belt course as `storey_height + 6` (a stated joist-zone depth in inches)
and the light count as `opening_width / 15` (a stated light width). But both figures exist today
only as consequences of each pack's DEFAULT module, 6 = 10 × 0.6 and 15 = 3 × 5, and neither pack
states either as a measurement. Writing them in would author two numbers no source gives, and the
ruling says author no number. The reading that decides it is the tradition's: does a belt course
sit a joist's depth above the storey whatever the storey (a fixed length), or at a proportion of
it? Does a window take a light width and repeat it (a fixed length), or divide its opening into
a stated number of lights (a proportion)?

**The answers available.**

1. **Re-express each rule on an independent quantity** and then declare. This needs a source, or
   an `editorial` rule with its basis stated, for the joist-zone depth and the light width. Once
   they are in, check 19 passes on both packs and the class-A ruling completes.
2. **Leave both packs undeclared** and accept the double reading `oq/which-packs-module-is-a-building-input`
   describes. On the Proportions page the opening slider changes how many lights a window has and
   not the arch they sit under; the storey pack's module and its `storey_height` binding stay two
   numbers that agree only at 120 in.
3. **Widen check 19(c)** to admit a rule that reads the input and `part` together. REFUSED here,
   because it admits the exact double reading the check exists to catch. It is listed so the
   next reader does not take it for an overlooked route.

**What does not depend on the answer.** `room-harmonic` is declared and served at the reader's
room width by one spelling, `mcp_server/core.py::module_binding`. The MCP tool and the workbench
route both take `storey_height` and `room_width` as of WP-14.18, so answer 1 needs no surface work
once the rules are re-expressed.
