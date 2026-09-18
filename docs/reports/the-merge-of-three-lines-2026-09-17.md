# The merge of Phase 13 into the second Phase 11 line — 17 September 2026

*Cite this report by FILENAME. There are two Phase 13s, two Phase 11s and two Phase 9s, and no
number in any of them names one package (OQ 90).*

**Three lines met here, two of them had made the same record edit independently, and the file
that carried that edit auto-merged CLEANLY into a record with seven duplicate JSON keys.** That
is the finding this merge is about: `git merge` reported no conflict on
`plans/tidewater-georgian-careful.json` because one session wrote each container tag after
`type` and the other after `doors`, so the two hunks do not overlap as text — and `json.load`
keeps the last of a duplicated key and says nothing. Every reader in this tree parses before it
validates, so `jsonschema` never sees the first copy; `tests/test_duplicate_json_keys.py`, which
main shipped for exactly this shape, is the only thing that could have caught it.

## What met

| line | packages | what it built |
|---|---|---|
| this branch (`ed5ef72`, 68 commits) | WP-13.1 – 13.8 | the gate, the plate telling the truth, the prover learning the type, refuse-to-draw, the container, the furniture grammar, the audit, the front's population |
| main's PR #34 | its OWN WP-13.1, WP-13.2 | `build/detection.py`, `build/check_frontend.py` |
| main's PR #35 | WP-11.16 – 11.18 | the record edit, the entrance front STATED, the hyphen anchor's band |

Merge base `840c7f1`; main at `9eb71c4` (`origin/main` in this checkout was four commits stale,
so the conflict set had to be recomputed after `git fetch`). 38 files touched by both sides, 25
main-only adds, **33 conflicts**. The merge commit is `2129da6`: 64 files, +7,565 −1,152.

**The rule followed is the Phase 11 merge's own**
(`docs/reports/the-merge-of-the-two-phase-11s-2026-09-08.md` §I): where both branches built the
same thing, main's spelling survives and this branch's behaviour is ported into it. So
`geometry_cp`'s proportion-band quantum keeps main's name `_BAND_Q` and main's scale-neutral
overshoot restatement, and this branch's seven-rank `_RANK` ladder, four hard type facts and
budget shares are ported into it. `build/check_plans.py` keeps BOTH new finding kinds, because
`massing-element` (ours, fatal) and `door-across-elements` (main's, reported, with its own
ceiling) are different questions.

## I. Every pin failure was attributed against BOTH parents before one was touched

41 first-wave failures. Run through the same test ids on `git archive` checkouts of each parent:
**36 of 37 pass on this branch's parent and 36 of 36 on main.** So every one was new at the
merge, which is what made the next question answerable: *what moved?*

**Two of the 41 were guards I had broken by taking both sides of a mutually exclusive
resolution.** `tests/test_element_awareness.py` kept main's element census AND this branch's
tag-stripping calls, so the census ran over a record with no container and could not see the
layer it is about. `tests/test_stacking.py` kept main's `>= 3` kept-stacks floor beside the ruled
90%-containment reading, which cannot both hold. **A merge resolution that takes both sides of a
contradiction is not a union, and the suite is the only thing that says so.**

## II. Four corpus digests and the CP proto pins, each with its instrument proved first

Every digest is a THIRD value belonging to neither parent, and the harness that produced it was
first required to reproduce a parent's OLD value on a `git archive` checkout (WP-12.9's rule):

| pin | ours | main | merged |
|---|---|---|---|
| `CORPUS_PLACEMENT_SHA` | `d72265a1935d07f6` | `7f2de7eaa95b84d2` | `0e454336df58c1fa` |
| `CORPUS_OPENINGS_SHA` | `21e7b43085f8f6ad` | `b00db93b584978a0` | `f63f6493a4bc83dd` |
| `CORPUS_SHEET_SHA` | `7ae444c7e5387110` | `c59ccf4f0cbb9a04` | `cc07560ab9eade5a` |
| `CORPUS_SHEET_SHA_NO_FRAME` | `8defa83027786782` | `6e40e16278d1f6e0` | `119e5b40ff69239e` |

**AND THE CONTROL THE ASSERTION NAMES FOUND A PIN I HAD WRITTEN WRONG.** The merge had put
MAIN's spec-Colonial CP proto pair under THIS branch's split dict, so its `objective=False` half
claimed a hard model neither tree builds. **It was never reached, because the Tidewater row is
asserted first and failed before the loop got there: a pin behind a failing pin is a pin nobody
has checked.** The `objective=False` model is byte-identical across the merge on both plans while
both objectives moved, which is the strongest evidence that only main's overshoot restatement
came in.

## III. The findings

### 1. Two readers of one rule rank on two different numbers

`axis.door_bay` and `elevation.placed_openings` both implement *the widest door on the front is
the front door*. `axis.front_openings` copies `d.get("width_ft")` off the room's own door record;
`plans/tidewater-georgian-careful.json` writes the porch's front door as `{"to": "exterior"}`
with no width, so `max(doors, key=width or 0)` scores it **ZERO**, while `openings.place`
supplies 3.5 ft (`openings.py:494`). On the one-element reading the front carries the porch door
(3.5 supplied, the **centre** bay of seven) and the kitchen's (3.0 stated, bay 0): the plate
dresses the porch, `door_bay` returns `off-the-centre-bay` naming the **kitchen**, and
`plan_check` convicts on `door_bay`. The corpus criticises a placement whose widest front door
stands dead on the centre line — the OQ 52 family.

**Swept: exactly ONE of the sixteen shipped plans places more than one exterior door on the main
block's front, and there the door that does state a width IS the real entrance.** So the shipped
answer is right by luck rather than by rule, and before the merge the one-element front carried
one door, where `max` over one element cannot be wrong. **Not fixed**:
`oq/the-front-door-is-chosen-by-a-width-the-record-need-not-state`.

### 2. The two bearing-line readers part on a reserved void's wall

`typefacts.bearing_lines` leaves reserved voids out (its own first line says so);
`structure.build_section` does not, because a piazza's party wall is a real wall. For as long as
no void's wall fell ON the bay module the two lists were identical. Main places
`good-03-parlor-drawing-room-house`'s piazza at x **30.0**, exactly a 10 ft bay line; this branch
had it at 41.74, off the grid; the merge takes main's. **Corpus-wide the divergence is ONE line on
ONE plan, swept** — section-only 1, leaf-only 0.

**A FILTER WAS WRITTEN FIRST AND WAS THE WRONG RULE.** It dropped every section line standing on
a void's edge, and `good-01-veranda-gallery-estate` has two the leaf KEEPS (x 50.0, y 30.0),
because the veranda's east edge is also where two heated rooms meet. The leaf leaves the void
ROOM out of its population; it does not leave out every coordinate a void touches. The comparison
stays strict with the one case named, so a second one fails.

### 3. Three premises ran out in the direction that leaves a guard green over half a defect

- **`tests/test_scene_audit.py`**: the two shipped plans stopped dressing the **E** face (N/S/W
  only, measured), so the N/E outside-face guard could have run with the defect restored on one
  of the two faces it lived on. Swept all sixteen: four dress E, `good-07-diamond-plan-house` (32
  members) is the largest, so the fixture takes it — and its cornice is not modelled, which is
  why the flush/proud premises became corpus-wide rather than per plan.
- **`tests/test_export.py`**: the blind-bay face draws nothing now, so the count assertion passed
  at 0 == 0 and the axis loop ran zero times. The face is chosen from the reading.
- **`tests/test_export_doors.py`**: no non-entrance face places a door on the shipped reading, and
  the docstring's own *"S 1 / N 0 / E 1 / W 0"* was a figure about a tree that no longer exists.

### 4. A guard whose premise is that a house is defective goes quiet when the house is repaired

`test_the_checker_and_the_plate_now_agree_about_the_off_centre_door` asserted `len(off) == 1` —
one `drawn-door-off-the-centre-bay` finding — and main's WP-11.17 puts the shipped record's placed
front door IN the centre bay, so the checker correctly convicts nothing and **the pin read a fix
as a regression.** The subject is the AGREEMENT now, which holds in both states. `a == b != c` is
two assertions wearing one `assert`, and the second is the one that moved.

### 5. `conftest.as_one_element` is not a control for a merge, and a fixture docstring said it was

`tests/test_hearths_on_flue.py`'s module fixture promised *"the drawing room and the dining room
stood on the west gable, the library on the east"* — the pre-WP-13.5 house restored by stripping
the container tags. **The CODE moved as well as the record**, so that reading is a third placement
belonging to neither parent. Three of the file's seven guards had lost their subject entirely: the
released-wall drive had become a mutation that changes no state, no sash is refused for a breast
any more, and **no stack serves two fires, so the gather has no subject at all**. Each is DRIVEN
now with its premise asserted.

### 6. A withdrawn claim still steers the placer

`geometry.bias` reads `stacks_over` while a level is being SLICED, so withdrawing a claim changes
which layouts are PRODUCED. Three extra `unreachable` fatals on the merged tree were attributed to
one deleted record line by measuring it on main's own untouched tree (7 → 10, exactly `landing`,
`library`, `stair`). `oq/a-withdrawn-claim-still-steers-the-placer`.

### 7. One question the merge CLOSED, and one it raised about the prover

`oq/the-entrance-porch-can-be-drawn-on-the-back-and-no-layer-says-so` is closed by main's
WP-11.17. `oq/the-prover-draws-a-centre-passage-that-does-not-go-through` is new: the merged
prover draws the centre passage 17.00 × 22.00 in a 45 × 37 block, stopping fifteen feet short of
the back wall, where main's prover draws it 10.00 × 37.00 and spanning. **The merged placement is
byte-identical to this branch's**, so the merge did not cause it — it made it visible, because the
guard that asks the question is main's.

## IV. The one feature the merge really did drop

**A merge must not drop a feature, and the only thing that has ever noticed is the other side's
test suite.** The check is a name comparison of every `def test_*` in every test file against each
parent, re-derived on the settled tree rather than quoted from the pass that found the loss:

| tree | test files | test names |
|---|---|---|
| this branch `ed5ef72` | 135 | 2,585 |
| main `9eb71c4` | 124 | 2,356 |
| **merged** | **138** | **2,649** |

**Twenty names are absent from their own file across the two parents — ten from each — and all
twenty are accounted.** Nine of main's ten were ALREADY absent on this branch's parent, so they
are spellings this branch had superseded before the merge and the resolution kept ours per the
rule; the other is one test renamed on both sides. This branch's ten are the renames and splits
the repairs made (three in `test_hearths_on_flue.py`, one of them a split into two). **Not one
absent name appears anywhere else in the tree, and no file's count FELL below the higher of its
two parents** — which is the check that separates a rename from a deletion, because a rename
keeps the count.

**The loss that pass DID find is the one it was for**: `tests/test_elements.py`'s per-plan element
ids, which main asserts and the first resolution had replaced with an arity-only census. Restored
as the union of both parents' forms — arity AND ids — so `tidewater-georgian-careful` is held to
`["main", "service-hyphen", "service"]` and every plan to its arity.

## V. What was NOT done, and why

- **`axis.door_bay`'s choice is not changed.** It moves a checker's verdict on a shipped record;
  what an omitted door width means to a rule that ranks widths is a question with a placement
  behind it, and spending a ruling inside a merge resolution is how a merge stops being one thing.
- **The two bearing-line rules are not reconciled.** Whether an unheated roofed room's party wall
  carries a joist is a ruling, not a pin.
- **No gate row is re-baselined and no test was made green by weakening it.** The Phase 13 gate's
  placement rows are red by design and remain so.

## VI. The build on the settled tree

`python3 build/check_all.py` whole, on `6f51195`, with nothing in flight and no edit while it ran
— HEAD was committed at 18:50:59 and the run's `pytest` began after 19:05, which is worth stating
because CLAUDE.md's own rule about a run straddling an edit was broken by the package that keeps
restating it (WP-13.8). **`2 of 53 checks failed.`** `pytest tests/` is **23 failed / 2,595 passed /
29 skipped in 1:00:42**; `pytest workbench/server/tests` is 248 passed / 11 skipped; `node --test
workbench/app` is green.

**The two failing checks are one defect through two readers and not two.** `check_partis.py`
prints `FATAL against its own style 'adam-style': The Front With No Centre: 1 against between 3
and 7` on the composed `side-hall-townhouse`, and
`tests/test_parti_composability.py::test_check_partis_runs_the_composability_check_and_is_green`
asserts the sentence that checker prints — the same finding, verbatim, on both trees. That is
`oq/a-side-hall-front-is-convicted-by-a-band-written-for-centred-fronts`, raised at WP-13.3 and
untouched by this merge; counting them as two would double-count one finding.

**Three checks are UNJUDGED and they are not the three this repository's notes name.** The
canonical trio is `export_dxf`, `export_ifc` and `pytest workbench/server/tests`, unjudged where
the optional packages are absent. Here `fastapi` IS present, so the server suite is judged and
green; and `ezdxf` is present too, so `export_dxf` gets far enough to refuse **both** shipped
plans by name — *"the placement is refused for bearing, stacks, tiling … 1 sheet(s) were not
drawn and the round trip was not exercised"* — which is WP-13.4's refuse-to-draw working, not a
missing library. The third is `check_frontend`'s lazy-tier check on a `dist/` built before 13 of
its sources, which is main's own WP-13.2 third state doing exactly what it was built for. **A
reader holding "three unjudged" against the canonical list would conclude the wrong three.**

**Seventeen of the 23 are the WP-13.1 gate and are red by design** — the placement rows Lucas's
15 Sep ruling put there to stay red until the placer satisfies them:

| gate row | parameterisations red |
|---|---|
| `declared_stacks_land_by_containment` | candidate-cp, candidate-heuristic, careful-heuristic |
| `every_declared_door_is_drawable` | candidate-heuristic, careful-cp, careful-heuristic |
| `every_upper_bearing_line_stands_on_a_ground_bearing_line` | candidate-cp, candidate-heuristic, careful-heuristic |
| `every_hearth_breast_stands_on_a_wall_a_stack_stands_on` | careful-cp, careful-heuristic |
| `every_level_tiles_its_block` | candidate-cp, careful-cp |
| `every_room_edge_carries_a_wall_or_an_opening` | candidate-cp, careful-cp |
| `the_elevations_openings_are_the_plans_placed_openings` | careful-cp, careful-heuristic |

**Fourteen of the gate's rows are parameterised on `cp`, which is wall-clock bounded on a shared
box, so the table above is the row-kind attribution and NOT a reproducible count** — an earlier
roll of the same gate on one tree read 22/47/11 against 21/47/11. Nothing is re-baselined in
either direction.

**The other six are exactly the six CLAUDE.md's WP-13.8 entry already records as pre-existing** —
three `test_composer.py` rows, `test_score.py`'s native-dominance row, `test_solver.py`'s
deliberately-red half bound, and `test_parti_composability.py` — **and they were attributed
against a control rather than by name**: run as those six ids on a checkout of this branch's own
parent `ed5ef72`, **6 failed in 2:41**, the `test_solver.py` failure being the same CARRIED
vocabulary assertion (`L1 primary S` and `L1 primary W` *"carried — off a conflict core or an
undecided round"*) that the WP-13.5 entry records as upstream's constant rather than this line's.
**Not one red is this merge's, and not one is the repair wave's**: all eight files the wave
repaired are green.

### The collection count is a third value and it reconciles exactly

| tree | collected by `pytest tests/ --collect-only` |
|---|---|
| this branch `ed5ef72` | 2,582 |
| main `9eb71c4` | 2,314 |
| **merged `6f51195`** | **2,647** |

The instrument was proved before its new number was believed: run on a checkout of this branch's
own parent it returns **2,582**, which is the figure CLAUDE.md's WP-13.8 entry publishes. The +65
is accounted to the test rather than asserted: **49 from main's three new files**
(`test_detection.py` 26, `test_check_frontend.py` 21, `test_duplicate_json_keys.py` 2) and **16
net inside seven shared files** — 19 test names added, of which **12 are main's and 7 are this
wave's own driven guards**, less **3 renamed away** in `tests/test_hearths_on_flue.py`.
49 + 19 − 3 = 65, and the per-file deltas sum to 65 independently. **Nothing was silently lost or
skipped**, which is the only thing a collection count is evidence of.
