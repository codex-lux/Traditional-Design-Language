# WP-5.10 — the four rulings from the dormer layer

Four questions came out of WP-5.9 and Lucas ruled on all four. Three were corpus-truth fixes; one
added a measurement so a fault that had been inert for two packages could be judged on evidence.

**A theme runs through all four, and it is worth stating once because it decided how each was
fixed: in every case the corpus already contained the right answer, in prose, in a field nothing
executes.**

| | the prose | where it was |
|---|---|---|
| OQ 84 | *"Choose the test by whether an order is present, not by preference."* | the fault's own note |
| the sill | *"in a masonry wall it is a rowlock or a stone and belongs to the brick-course pack, **not this one**"* | the pack rule's own note |
| OQ 85 | *"where a portico occurs it is one bay wide, centred"* | the kit's own rule |
| the CR dormer | `binding: "open"` — the style declining to constrain the slot | the kit's own binding |

The work was mostly making that prose executable. It also raised two new open questions, one of
them larger than anything it closed.

---

## OQ 84 — two rival cornice rules, and the trap in the obvious fix

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

## OQ 85 — the centre bay is blind

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
loopholes"*, and it was right. The nuance is real and belongs in OQ 85's closure instead: the kit
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

## OQ 86 (new, and the largest thing here) — 133 addresses nobody was comparing

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

## OQ 87 (new) — `open` does not mean open

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
- **`open`'s semantics are not changed.** One instance is fixed; the mechanism is OQ 87.
- **The `paired-and-joined-by-arched-curtain` simplification is not corrected** — `roof.py` still
  places one stack per gable end where the kit's canonical variant describes a joined pair.
- **`spec-builder-colonial`'s roof still judges no pitch and no ridge.** The sheet says so now
  instead of quietly dropping the dormers, but the underlying gap — a reference plan whose roof
  the corpus cannot dimension — is untouched and is worth its own look.

---

# The adversarial audit, 28 Aug 2026

Three independent auditors were run over `7f1892f..HEAD` — one on broken contracts and unhandled
consumers, one on whether the new tests actually guard anything, one on second-order risk and
repeat occurrences. **The suite was green at 1,018 tests before any of them started**, and between
them they found two live false judgements, three of my own new tests that do not test what they
claim, and a corruption count that was measured with the wrong instrument.

That is the finding above all the others: **a green suite is necessary and it is not evidence.**
Every item below passed 1,018 tests.

## Live defects — fixed

**A false conviction on Second Empire.** A fault's tests live in **three** places, not two:
`test`, `secondary_tests`, and `exceptions[].bounds_test`, which `check_measurements` substitutes
for the *primary* on a matching style. OQ 84 and OQ 79 guarded the first two. Second Empire's
bounds_test is `dormer_count / bay_count == 1.0`, so a house stating **no dormers** evaluated 0.0
and was convicted of *Dormers Off the Rhythm* — the exact OQ 52 failure this package exists to
prevent, in the one location neither ruling touched. Found by sweeping all 164 styles with one
plan's measurements; the two reference plans are not Second Empire. `craftsman`'s bounds_test had
the same shape in the other direction: `dormer_count at-most 1` read a stated zero as CLEAR, an
acquittal rather than a conviction, on 1 style of 164.

**The DXF drew the collision the SVG had just stopped drawing.** `export_dxf.py`'s bay loop reads
`if kind == "door" … else: window`, so OQ 85's new `"blind"` fell into the `else` and the CAD file
put an opening where the chimney stands. Two surfaces disagreeing about one record. The export
selftest could not see it — it round-trips *findings*, not geometry, which is WP-5.7's lesson
recurring in the CAD path.

**Dormers were placed on the wrong face.** `dormers()` was handed `faces[entrance_face]`
unconditionally, so a record declaring `{"count": 3, "face": "E"}` got the *south* front's bay
centres laid out on an east elevation 20 ft narrower — the third dormer standing 1.15 ft past the
corner of the wall. Worse, the generator then published `count_of_dormers_centred_on_a_window_
below: 3` and `dormer-off-the-bay` **cleared** the house on a number nobody had measured.

**`ORDER_AT_THE_EAVE` answered confidently about what it did not know.** The hand list of four
missed every giant-order variant the corpus actually names, so `beaux-arts-american`,
`neoclassical-revival` and `english-baroque` returned `0` with a note saying every canonical
variant was "a void or an attached structure" — selecting the *domestic* cornice band for fronts
whose cornice legitimately runs 0.85–1.2. OQ 84 had replaced "both rivals run, one convicts" with
"the wrong one runs, silently." Nine variants are now classified from the corpus's own words, and
anything canonical that reads like an applied order and is *not* classified returns **unjudged**
rather than 0.

**`applies_when` had two silent failure modes.** Omit `expression` and the guard vanishes — the
test runs unguarded and convicts. Omit `direction` and `passes` is `None`, so the test is
**permanently** not-applicable: a fault switched off for the life of the corpus, reporting
`required: "None 1"` to anyone who looks. Both were schema-valid. The failure state of a mistyped
guard is a fault going quiet, and this package had just taught every reader that quiet is benign.
Now required in the schema *and* refused in the evaluator, because the schema is only checked when
`jsonschema` is installed.

**`kit_vs_pack` compared across units, and OQ 86's number was wrong.** 71 of the 133 "corruptions"
were cross-unit: 70 comparing a kit figure in **inches** against a pack rule stating a **ratio**,
and one comparing `dutch-colonial-american`'s `gambrel_lower_slope` of **60–72 degrees** against
`dutch-gambrel`'s **1.7321** — which is tan 60, *the same slope*, reported as a contradiction.
That is **OQ 53 verbatim**, the open question recording that this very file compares `quantity`
without `units`, reproduced ninety lines below the docstring documenting it. Unit-aware, the real
count is **62**, and the ratchet is re-pinned there.

**Two more measurement leaks.** `sum_of_dormer_face_widths_in` was computed from *placed*
positions, capped at the bay count — so a record declaring 24 dormers reported the face width of
five, and the **fatal** `dormer-wall` read 0.248 instead of 1.188 and cleared it. And blind bays
were still counted as openings by `upper_floor_opening_count`, `openings_on_the_front_elevation`
and `glazed_area`.

**The fourth state stopped at the API boundary.** `not_applicable` reached `plan_check` and went
no further: `workbench/server/evaluate.py` forwarded only `fault_unjudged`, the bench rendered
only `fault_unjudged`, and `rail.py` still told the model to build its mandatory `<unjudged>` block
from three fields. A fault in that state appeared in **no list on the bench** — the precise
sentence the state was invented to prevent, relocated one boundary out.

## Three of my own tests did not test what they claim — rewritten

- **The cornice-return guard scanned a class the gabled path never emits** (`pf w-fine` is only
  ever a *polygon*). The loop body never executed. Re-adding the returns in the class the renderer
  actually uses passed it. It now asserts over every element drawn above the cornice line, whatever
  its tag or class, permitting only the roof polygon and its shingles.
- **"Carries all its glazing bars" counted meeting rails.** `_window` emits exactly one per window
  whatever the light counts are, so the assertion meant "twelve windows are drawn" — true before
  the fix and after. It computed the right number and discarded it. Forcing the sashes to 1×1
  deleted all 18 dormer bars and the test passed. It now counts the bars, differentially against a
  sheet with no dormers.
- **The blind-bay position check compared a left edge against a bay centre** with a 24 px
  threshold, while an opening is 34–39 px wide — so a window drawn dead on the stack's axis passed.
  Now compares centres against the stack's own half-width.

Each was verified by reverting the fix and confirming the rewritten test fails.

**And one test was asserting the opposite of another.** `test_long_face_of_a_side_gable_shows_no_
chimney` pinned `'class="ch"' not in text`. WP-5.9 gave the stack a weight rung, the class became
`ch w-prof`, and a *negative* assertion whose selector breaks inverts into a tautology — leaving
the suite simultaneously asserting "no chimney on the front" and "two stacks on the front". Only
the broken selector kept them apart. Its intent was reversed by OQ 80 on purpose; it is rewritten
to assert what the ruling chose, plus the stack's drawn **width**, which nothing had ever asserted.

**And one hid a live disagreement.** `test_a_count_the_bays_can_carry_passes` recomputed
`int(width_ft // (bay_module_ft or 10.0))` — `roof.py`'s own line, copied into the test — and
`bay_module_ft` is absent, so both sides fell back to the same invented 10.0. It concealed this:
the roof said **6** bays and passed a record at `{"count": 6}` while the elevation laid out **5**
and the fault corpus convicted the same house. Two records built from different rules that nothing
compared — **OQ 85's own thesis, one layer up, shipped inside the package that closed OQ 85.** The
roof no longer invents a module: the bay rhythm belongs to the facade layer, and where the
footprint states none the roof declines.

## Considered and deliberately not changed

**`dormer-wall` and `overscaled-dormer` return CLEAR on a house that states no dormers, and that
is correct.** One auditor called this a false acquittal of a *fatal* fault. It is not the same
shape as the parity rule: `sum_of_dormer_face_widths_in / building_width_in = 0` is a real
measurement of a real quantity, and a roof with no dormers has definitively not become a storey.
`dormer_count % 2 == 1` is different — "is the number odd" presupposes there is a number. The
distinction is where a fault's expression *measures* something at zero versus where it
*presupposes* something. Left as clear, with the reasoning recorded here rather than silently.

## Deferred, with reasons — raised as open questions

- **The `sash-light` sill scope is one node of 27** that make a masonry cladding canonical, and two
  more pack rules have the same shape (a note stating a scope the data does not carry). That is a
  corpus migration, not a patch — **OQ 88**.
- **Three measurements are still withheld** from `elevation.py` to work around conditional-test
  gaps that `applies_when` now covers, and `total_shutter_leaves` is supplied as an unconditional
  constant of 2.0 regardless of whether the style carries shutters — **OQ 89**, and the second half
  is OQ 52 residue in `_derive_measurements`, outside `NOT_MODELLED`'s reach.
- **15 more `exceptions[].bounds_test` entries divide by a count with no guard.** None is live
  today. Named in OQ 89 rather than guarded speculatively.
- **`check_addresses.py` is 27× slower** (0.11 s → 3.0 s) because `kit_vs_pack` re-resolves the
  cascade per node. Measured and accepted: 3 s on a build check that already takes twelve minutes.


---

## The merge with main, 28 August 2026

This branch merged `origin/main` at `9d918f1`. Three files conflicted and both of the things
they conflicted over were **id collisions between two sessions that ran at the same time** —
the third such collision in three days.

### The open-question block, renumbered for the third time

Both sides issued from 72. Main's block — the atlas's fine coastline tier (72) and the five from
the infrastructure audit (73–77) — **keeps its numbers**, because it merged first and its own
reports cite them; that is the rule this register states and has now applied three times. **This
branch's twelve moved by six: 72–83 became 78–89**, converted across 34 files and 90 citation
sites, with the conversion table in `docs/open-questions.md`. Main's own note for 73–77
anticipated the collision and offered to renumber; the merged-first rule settles which side moves
and it is not the side that merged.

Two commit messages — `f768c02` and `426ed35` — were written under the old numbers and cannot be
changed. Everything inside the tree was converted, and main's own citations were left untouched:
each citing line was classified by whether it already exists on `origin/main` before anything was
rewritten, rather than by which file it sits in, because `CLAUDE.md` and `PLAN-OF-ACTION.md` carry
citations from both sides.

### The work-package numbers collided too, and were NOT renumbered

**There are two different WP-5.7s** — main's atlas and this branch's geometry layer — and unlike
the open questions they were left alone. That asymmetry is deliberate and is recorded as **OQ 90**
rather than decided in a merge commit: an open question is cited by number and nothing else, but a
work package is cited by its REPORT, and the two reports have always had distinct filenames, so no
citation in this corpus is ambiguous today. Renumbering either would rename report files, break the
`wp-<id>-<slug>.md` convention, and — for this branch's — break the chain where WP-5.8 exists to
execute WP-5.7's rulings. **Until it is ruled, cite the report and never the number.**

### Two stale claims in CLAUDE.md that the merge surfaced

Both were this branch's, both were prose asserting what the code no longer does, which is the
failure this corpus polices hardest — and both had been green through a full suite.

- The kit-versus-pack trap still said **133, ratcheted** and "five nodes carry 116 of them". The
  audit's unit-aware fix had already taken it to **62 across 13 nodes, four of which carry 47**.
  Corrected against `check_addresses.py`'s own output rather than arithmetic.
- The `projection_datum` trap said the entablature question was **open** and that
  `dist/orders.html` "still draws it that way". Both had stopped being true: OQ 78 closed when the
  datum moved into `profiles.py::axis_holds_for`, and `dist/orders.html` stopped clamping when it
  stopped computing geometry at all (OQ 83). Verified in the code before rewriting the prose.

### A broken skip path in a test that arrived from main

`workbench/server/tests/test_compression_and_caching.py` calls `pytest.skip()` at **four** sites
and imports `pytest` at none of them. Every one is a could-not-evaluate path — no built frontend,
no precompressed assets — so main's CI, which builds and precompresses, had never reached one. The
merge did, and the result was not a skip but a `NameError`: **a test that cannot report its own
unjudged state and fails instead.** One import fixes all four, and the fix was proved by removing a
`.gz` and confirming the test now reports SKIP with its own reason where it previously raised.
Pre-existing on main, introduced by nothing here, and exactly the corpus's own discipline one layer
out: a guard whose unjudged path is broken is not a guard.

### What the merge did not change

The two reference elevations render **byte-identical** before and after, front and gable end. Both
were re-rendered and looked at in the delivered light theme rather than the dark dev one: the
blinded centre bay of OQ 85 is drawn and disclosed, the stacks clear the roof at both gable ends,
and the measured widths hold — wall face at 46 px, cornice projecting 21.1 px (10.5″, the envelope
rule the legend prints) and the stacks 44 px (22″, the figure the legend flags as a judgment).
`check_frontend.py` failed once on a `dist/` built before main's atlas work; rebuilding and
precompressing settled it, and it was a stale artifact rather than a defect.
