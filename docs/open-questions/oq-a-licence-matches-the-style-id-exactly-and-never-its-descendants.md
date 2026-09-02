# oq/a-licence-matches-the-style-id-exactly-and-never-its-descendants — a Georgian portico's exception never reaches a Tidewater Georgian house

*Status: OPEN · Raised in: WP-9.1, the critique (1 Sep 2026)*

**OPEN — a fault's `exceptions[]` are matched to a house by `e["style"] == style`, exactly, at
all three selection sites (`mcp_server/core.py:712, 755, 972`), so a licence written on a
parent style never reaches its variants and regional children.** A test's own
`applies_to_styles` (OQ 63) is matched against the whole inheritance chain; an exception is
not.

The case that found it: `plans/tidewater-georgian-careful.json` is convicted of
`porch-too-shallow-to-inhabit` ("The Four-Foot Porch") at 6.0 against at-least 7.0 — and,
under the proving engine, at 3.0. The fault carries a licence on `georgian-colonial-american`
with a `bounds_test` (`porch_width / front_elevation_width at-most 0.35`), a `granted_when`
on the porch slots, and a `severity_by_style` entry of `not-applicable` for that style —
because a Georgian entry portico "is a piece of the order rather than an outdoor room"
(`docs/faults.md`). `tidewater-georgian` is `regional_of` `georgian-colonial-american` and
gets none of it: the general 7 ft rule stands, no licence is considered, and the verdict
carries no `exception_not_applied` note because no exception was ever selected.

An earlier reading of this (in the plan for Phase 9) blamed the licence's `bounds_test` for
needing `porch_width / front_elevation_width`, which nothing supplies. That is also true and
is the smaller half: the bounds test is never reached.

**Two questions, and they are Lucas's:**

1. Should an exception follow the chain the way a test's `applies_to_styles` does? Decision
   #7 says exceptions matter as much as rules, and a rule that reaches a variant through the
   chain while its licence does not is the two halves of one fault disagreeing about scope.
   The cost is real: 846 exceptions were authored against the exact-match reading, and some
   licences are genuinely narrower than the parent (`charleston-single-house`'s eight-foot
   piazza is not every Lowcountry style's).
2. If yes, does `severity_by_style` follow too? Tidewater's portico would then be
   `not-applicable` rather than `serious`, which moves a pinned count.

**Not changed in WP-9.1.** The analyst classifies this finding `architect` (a move would
answer it — `trade-width-for-depth-at-constant-area`, the fault's own cheap fix — and WP-9.2
registers it), so the loop will treat a 6 ft portico as a porch to deepen unless this is
ruled first. The report says so.
