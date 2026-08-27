# WP-5.10 — the four rulings from the dormer layer

Four questions came out of WP-5.9 and Lucas ruled on all four. Three were corpus-truth fixes; one
added a measurement so a fault that had been inert for two packages could be judged on evidence.

**A theme runs through all four, and it is worth stating once because it decided how each was
fixed: in every case the corpus already contained the right answer, in prose, in a field nothing
executes.**

| | the prose | where it was |
|---|---|---|
| OQ 78 | *"Choose the test by whether an order is present, not by preference."* | the fault's own note |
| the sill | *"in a masonry wall it is a rowlock or a stone and belongs to the brick-course pack, **not this one**"* | the pack rule's own note |
| OQ 79 | *"where a portico occurs it is one bay wide, centred"* | the kit's own rule |
| the CR dormer | `binding: "open"` — the style declining to constrain the slot | the kit's own binding |

The work was mostly making that prose executable. It also raised two new open questions, one of
them larger than anything it closed.

---

## OQ 78 — two rival cornice rules, and the trap in the obvious fix

`cornice-that-is-a-fascia` carries two secondaries on ONE expression: the domestic boxed eave at
**0.35–0.55** of its own height, and the full entablature-derived case at **0.85–1.2**. Whichever
is right, the other convicts the house.

**The obvious discriminator is wrong, and it was checked before anything was written.**
`gibbs_order_applies_to_style` is `True` on `tidewater-georgian` — but it means only that Gibbs
Ionic is the order this style's cornice is *generated from*. Read as "an order is applied to this
facade" it selects the entablature test on a house that measures **0.4286**, and convicts it. It is
pinned as a test, because it is the answer a later reader reaches for first.

Nor is a portico enough. `tidewater-georgian`'s own porch rule says *"where a portico occurs it is
one bay wide, centred, and carries the bound order"* — a one-bay portico has its own entablature,
below the eave, and the eave beside it is still a domestic boxed cornice. Only an order engaging
the whole wall makes the eave an entablature, and `ORDER_AT_THE_EAVE` is a short list with the
quotation that justifies each entry (`two-tier-engaged-portico`: *"structurally integral,
superimposed orders. Drayton Hall is the type case."*).

`an_order_is_applied_to_the_wall_carrying_the_eave_cornice` has the three states this package uses
everywhere: 1 where the record or the style puts such an order on the wall, 0 where nothing
available to the house could, **absent** where the style makes one canonical and the record has not
chosen — because then nobody has decided, and a guess picks which of two rival rules judges the
house.

### The half that was easy to miss

**`cornice_projection_in` is supplied now, and that is the point of the exercise.** WP-3.2 had
withheld it to stop the rivals firing, and the comment saying so read like a decision. It was a
workaround: `elevation.py` published `cornice_projection_past_wall_face_in` — the same quantity
under a different name — so the fault was silenced by a *name mismatch*, and came back "clear" on
its wall-height ratio alone.

Measured, on `tidewater-georgian-careful`:

| | before | after |
|---|---|---|
| primary `p/w ≥ 2.0` | need_measurements | **evaluated, 5.10 ✓** |
| domestic `p/h` 0.35–0.55 | need_measurements | **evaluated, 0.4286 ✓** |
| entablature `p/h` 0.85–1.2 | need_measurements | **not applicable** (no order at the eave) |
| wall ratio 1/14–1/12 | evaluated ✓ | evaluated ✓ |
| corona shadow edge | need_measurements | need_measurements |

**1 of 5 tests evaluating → 3.** The fault's verdict did not move; its evidence did. Guarding the
rivals while still withholding the name would have left it just as inert and looked just as green,
so that is a test of its own.

And the same field retired a second WP-3.2 workaround in the same commit: `solar_array_area_sqft`
is supplied at its honest zero, and `entrance-slope-penetration`'s array secondary — preconditioned
on the array's own area since WP-5.9 — declines instead of convicting a house of a patchy array it
does not have. **Two workarounds retired by one field.**

## OQ 79 — the centre bay is blind

`roof.py` puts both stacks at `y_ft` **21.33** on a gable end **42.66 ft** deep — its exact centre
line — and `_face_bays()` independently spaces an odd bay count evenly, putting a window centre at
21.33 too. Two records built from different rules, never compared. The elevation drew a window
where a chimney stands, and it was found by drawing the stack from grade for one revision rather
than by any test: each record is right on its own.

`blind_bays_behind_stacks()` marks the bay `blind`; the renderer draws no opening there **at either
storey**, because an exterior end stack runs the full height of the wall. The gable ends now read
as two glazed bays flanking a blind centre — what a Chesapeake end wall is — and the long faces
lose nothing, because both stacks are at mid-*depth* and stand in neither long wall. That the rule
is a collision test rather than "gable ends have a blind centre" is asserted separately.

**A new fault, `window-on-the-chimney-axis`**, catches the collision where a record states both, so
an ingested or hand-authored drawing is checked rather than trusted. The elevation publishes
`count_of_openings_on_the_axis_of_a_chimney_stack` as a **measured zero** — the generator saying it
*resolved* a collision, not that one never existed — and a test asserts the fault still fires on a
record that states one, because a zero from a rule that can never return anything else proves
nothing.

### Two things that did not happen, deliberately

**The stack was not moved.** No source reachable from here gives an off-centre figure for a paired
exterior end stack, and inventing one is the failure this corpus keeps catching.

**An exception was drafted and removed.** It would have exempted `tidewater-georgian` — the very
style that raised the problem — on the grounds that `paired-and-joined-by-arched-curtain` leaves
the space between two stacks free. `check_faults.py` refused it: *"exceptions without bounds become
loopholes"*, and it was right. The nuance is real and belongs in OQ 79's closure instead: the kit
makes that variant canonical, `roof.py` places a single stack per end, and correcting *that*
simplification would put the stacks either side of the centre bay and might restore the window.
That is a roof-layer question, and it is recorded rather than pre-empted.

## The sill — the forbidden variant wins, and the pack said so all along

`kits/tidewater-georgian.kit.json` forbids `wood-sill-sloped` with a reason: *"the parent's 2 1/4 in
projecting sloped sill throws a shadow under every window and the brick sill does not, so the
elevation is flatter and the openings read as holes cut in a mass."* Two inherited things
contradicted it:

1. The parent's **rule sentence** ended *"...it projects past the wall face with a drip and is
   sloped 1 in 6"* — a description of the forbidden variant, surviving the merge and read back off
   the slot. `rule` is in `MERGE_REPLACE`, so restating it at the child was the whole fix.
2. `sash-light` delivered **2.25 in** as `projection_in`, beside the node's own authored
   `projection` of **0–1 in, `kind: measured`**. Two names for one quantity, differing by more than
   twice, in one slot, with nothing comparing them.

**The pack's own note resolves it**: *"In a frame wall this is a real sill member; in a masonry wall
it is a rowlock or a stone and belongs to the brick-course pack, not this one."* `sash-light`'s
`applies_to` named `tidewater-georgian` anyway. The prose stated the scope and the data contradicted
it.

### A false start worth recording

The fix went to `slots_except` first — a denylist form of OQ 49's binding scope, because refusing
one of `sash-light`'s fourteen addresses with the existing allowlist would have meant naming the
other thirteen by hand, and a hand-maintained allowlist silently stops delivering any rule the pack
gains later. That was built, and then the 2.25 was still there.

**Because the pack rule reaches this node twice.** It is delivered live by `eval_packs`, *and* it is
baked into `kits/georgian-colonial-american.kit.json` as an authored parameter carrying
`source: sash-light`. Scoping the binding closed one path and left the other open. Both are needed,
and the near-miss is the point: the mechanism I assumed was in play was in play, and it was not the
only one. `slots_except` is real and is exercised — the test asserts `sash-light` still reaches its
other addresses, so the exclusion cannot decay into a deletion — but on its own it would have been a
long note claiming a fix that had not happened.

The second path was closed at the child, where the contradiction lives: the node's `projection`
is renamed to `projection_in`, which is the name the parent and every pack actually use, so the
override lands and the slot carries **one** figure.

## OQ 80 (new, and the largest thing here) — 133 addresses nobody was comparing

That sill is not a one-off. `build/check_addresses.py` gained a third reporter, `kit_vs_pack()`,
and the first measurement is **133 node parameters contradicted by a pack rule, 3 could not be
judged.**

OQ 48 measured pack against pack and closed at 0 own-scope collisions. This is the same corruption
one layer over, and it was invisible to that measurement for a plain reason: **the kit writes
`projection_in` and a pack writes dimension `projection`, so the two never met under one name.**

It compares only parameters a node authored as `measured` — a `derived` one is a pack's own value
copied into the kit, agreeing with itself, and reporting those would bury the real cases under
hundreds of tautologies. It compares **values**, not quantities, because a kit parameter has no
`quantity` field; a 10 per cent tolerance keeps it to members drawn twice the size rather than
rounding.

Ratcheted at 133, in the shape OQ 48's original 139 were handled. **The distribution is
concentrated**: `american-farmhouse-vernacular` 32, `federal-style` 31, `greek-revival-american`
24, `craftsman-bungalow` 16, `georgian-colonial-american` 13 — five nodes carry 116 of the 133.

## OQ 81 (new) — `open` does not mean open

`colonial-revival` bound `dormer` as `binding: "open"`, `status: "empty"` — the style explicitly
declining to constrain the slot. `resolve_slots` stops its walk only on `specified` or `forbidden`;
**`open` is skipped entirely**, so the walk continued to `english-cottage-vernacular` and returned
its whole slot: `eyebrow-swept-dormer-within-thatch` **canonical**, and `boxed-dormer` — the only
dormer such a house is ever built with — **forbidden**, on a `c01, hard.`

A production Colonial Revival could not declare its own dormer, and the elevation generator drew a
thatched cottage's on it with full confidence. The style now binds the slot `specified` with
`boxed-dormer` canonical and a sash pattern, so WP-5.9's two disclosures — *"VARIANT INHERITED FROM
ENGLISH COTTAGE VERNACULAR"* and *"SASH PATTERN UNDECLARED"* — are both gone from that sheet.

The mechanism is untouched and reaches all 97 slots. It is OQ 51's question in the kit layer, and
it should probably be settled with OQ 51's opt-in flip rather than before it: making `open` stop
the walk today would strand every slot that is `open` and relying on the cascade, which is most of
them. What is wanted first is the count.

## And one more found by looking at the sheet

Rendering `spec-builder-colonial` with three dormers declared, to check Step 4's work, produced an
elevation with **no dormers on it and nothing saying so**. The cause is honest as far as it goes:
that plan's roof record judges neither a pitch nor a ridge, so `elevation_profile` returns a flat
eave line with nothing invented above it — there is no roof surface for a dormer to stand on. But
`_dormers()` skipped each one silently while `elevation.py` went on publishing `dormer_count: 3`
and the full per-dormer set to the fault corpus.

**The critic was judging three dormers on a sheet that drew none.** That is the record and the ink
disagreeing with nobody in a position to notice — the same shape as every other finding in this
package, arriving through the honest behaviour of two layers that were each right on their own.

The record now carries `placeable` and, where it is false, `not_drawn_reason`; the renderer returns
nothing and the legend says *"DORMERS DECLARED BUT NOT DRAWN — THE ROOF RECORD COULD NOT JUDGE A
PITCH AND A RIDGE HEIGHT FOR THIS HOUSE…"*. The measurements are unchanged: the record states three
dormers and it should keep saying so. What was missing was the sheet admitting it could not draw
them.

WP-5.9's own report had flagged this as *"a silent skip [that] should probably become a stated
refusal"* and left it. It took three minutes to fix and it was found by looking, not by testing —
which is now the fourth time in two packages.

## Two tests were pinning the bugs this package fixed

`test_a_variant_the_cascade_delivered_says_where_it_came_from` pinned that `colonial-revival`'s
dormer variant came from `english-cottage-vernacular`, and
`test_a_sash_pattern_the_kit_does_not_state_is_not_invented` pinned that the style stated no sash
pattern. Both were true, both were the bug, and Step 4 made both false. Left as they were they
would have asserted the corruption.

Rewritten onto the **mechanism** rather than the instance: the first now finds an inherited dormer
slot in the corpus at test time (there are 29) instead of naming one, and asserts separately that
`colonial-revival` owns its own; the second drives `_dormer_lights` directly, including that "6/6"
is six lights in *each* sash. A guard written against a specific broken record has to be moved when
the record is fixed, and moving it is the moment to ask what it was really for.

## What moved

- 209 → **210 faults**; two count pins updated, one of them in the workbench's own overview test.
- **49, not 50**, nodes with no opening-role pack — binding the Colonial Revival dormer moved a
  corpus counter, which is a small demonstration that the cascade was standing in for a real gap.
- `check_addresses.py`: two reporters → **three**, with a third ratchet.
- **OQ 51's meter moved the right way**: `role_gaps` 294 → **293**, `inherited_packs`
  3,367 → **3,366**, `endorsed` 72 → **71**, `unendorsed` unchanged at 222. Binding
  `colonial-revival`'s dormer removed a gap the cascade had been filling — and the gap was
  an *endorsed* one, which is worth noting: an endorsement records that somebody read the
  cascade and agreed with it; a binding means the node says it in its own voice. The pins
  assert equality rather than a bound, so an improvement fails them until the reason is
  written down, which is the discipline working.
- `schema/style-node.schema.json`: `slots_except` on a pack binding.

## Deliberately not done

- **The 133 are not fixed.** They are counted, ratcheted and named. Fixing them is a migration.
- **`open`'s semantics are not changed.** One instance is fixed; the mechanism is OQ 81.
- **The `paired-and-joined-by-arched-curtain` simplification is not corrected** — `roof.py` still
  places one stack per gable end where the kit's canonical variant describes a joined pair.
- **`spec-builder-colonial`'s roof still judges no pitch and no ridge.** The sheet says so now
  instead of quietly dropping the dormers, but the underlying gap — a reference plan whose roof
  the corpus cannot dimension — is untouched and is worth its own look.
