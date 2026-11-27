# The garage is its own mass, the range stands at the rear, and the prover sizes the wing

*26 to 27 November 2026. Branch `claude/hopeful-ramanujan-fk4s72`, on `cc98832` ("the prover
decides").*

## I. The result

On `briefs/family-georgian.json` the native `centre-passage-double-pile` was refused, PROVEN. On
four workers it now places with every type fact held, reads DRAWABLE WHERE JUDGED and leads the
returned set, on four runs of four. On one worker it comes back refused UNDECIDED on four runs of
four. §V has every run and the measured reason for the one-worker result.

So the task's "done" is met on four workers and not on one, and the reason is stated.

Four rulings got it there. Each was asked of Lucas as a direct question and answered as a separate
act, and each is recorded in
`docs/open-questions/oq-the-double-piles-service-wing-cannot-tile-on-its-hyphens-face.md`.

| # | asked | answered |
|---|---|---|
| 1 | Where does the garage stand? | Its own mass beyond the service wing, linked by the mudroom |
| 2 | What lets the four-room wing tile? | Size the wing for its door set (the unbuilt third part of ruling 4 of 29 Oct) |
| 3 | Where does a single service range stand along the main block's flank? | Against the rear wall |
| 4 | How is the wing's box found? | The prover finds it, smallest whole-foot box first |

Questions 3 and 4 were not in the task. They came from measuring the house after the first two
were built, and the work stopped for them.

Not changed: `TILING`, `COVERAGE`, any room band, `build/typefacts.py`, and every room and door of
the parti. `partis/centre-passage-double-pile.json` gained two sentences in its `note`.

## II. What was built

**Ruling 1, the garage.** `compose.attach_garage`, only where the kitchen carries a `block`: the
garage takes `block: garage`; the mudroom takes that block and `hyphen: true` and doors the kitchen
and the garage. Its door to the back hall is dropped, because the wing now stands between them. The
garage's free walls follow the side the wing is on. With an untagged kitchen the function's output
is unchanged.

`geometry.flank_sizes` reads the chain off the door graph: a link room that doors a room of another
element puts its own element beyond that one, on the same side, parent first. A link may be a
`threshold` room as well as a `circulation` one. An element of one room is that room's declared
rectangle (22 x 20 ft for the garage; it was an 18 x 25 ft single-pile reshaping of the same area)
and does not grow with the house.

**Ruling 3, the rear wall.** `geometry.flank_laying` is the one reader. Where the record states
`flank_laying: rear`, the flanking elements are on one side and the entrance front is N or S,
`blocks_for` lays each element with its rear wall on the main block's rear wall and centres each
link on the shallower of the two masses it joins. Otherwise the axis, as before. The basis is
`groupings/dependency-and-hyphen.json`, hard: "Where dependencies are paired they are symmetrical
about the main block's axis; where there is one, it does not sit on the entrance elevation."

`flank_laying` is a new field of the plan record (schema 0.14.0). The composer writes `rear` on a
house with a `block` tag and says so in its decision log.

**Rulings 2 and 4, the wing's box.** `geometry_cp.size_wings` runs at the start of a prover solve.
Each dependency of more than one room is posed alone over whole-foot boxes, smallest first; the
first that holds is its box. The wing's own tiling, bands, doors and links are held in every box
posed. The box goes onto the footprint as `flank_box`, the wing does not then take the depth
growth, and `solver.wing_sizing`, `solver.wing_sizing_note` and the block's own `note` say what
happened. A decided search is kept for the process.

Decisions of mine inside the rulings, each open to being overturned:

- the one-room element is its room's declared rectangle;
- the garage's 22 ft face is to the rear and the flank, vehicle doors off the entrance front;
- a `threshold` room may be a link;
- the mudroom's door to the back hall is dropped;
- the link is centred on the shallower mass (offered to Lucas as "centred on the wing");
- the sizing window: derived width to one bay wider, derived depth to 4 ft deeper, never deeper
  than the main block or past the lot; 5 s a box; at most a fifth of the solve's budget.

## III. What was found

**The main block was a second cause, and the open question had it the other way.** The question
said "the main block holds every fact in 7.4 s" and put the whole proof in the wing. With the
garage moved out, the main block alone could not hold its facts with the range centred on its
axis, at the derived depth or 2, 4 or 6 ft deeper, on this tree; and at the derived depth on the
parent commit too. How the 7.4 s run was posed is not recorded. The session that made it was asked
and had not answered when this was written.

At 4 ft deeper the centred main block holds if any one of these is released: the butler's pantry's
band, `primary` over `drawing`, `upperpassage` over `passage`, or the butler's pantry's door to the
back hall. None was released. With the link 6 ft or more toward the rear it holds as it stands.

**The wing tiles in a small island.** Of 40 boxes from 18 x 17 to 26 x 25 ft, posed alone and
centred: 22 x 21, 22 x 23, 21 x 23 and 23 x 23 ft, and no other. Not at its derived 18 ft width at
any depth. The kitchen opens off a link on each of the wing's opposite faces, so it spans the wing,
and the powder room, pantry and breakfast room stand in a row beside it. Against the rear wall,
with even depths allowed, the first box the step finds is 21 x 22 ft.

**The depth growth undid the wing.** `flank_grow_ft` takes a 22 x 21 ft wing to 22 x 25 ft at
+4 ft, which does not tile. So a sized wing does not grow.

**The rear laying, read off the flank alone, moved the one shipped record with a dependency.**
Measured on `plans/tidewater-georgian-careful.json` before anything was pinned, one run each:

| engine | on the axis (parent) | against the rear wall |
|---|---|---|
| search, refused for | bearing, stacks | bearing, hearth, stacks |
| search, findings | 6 fatal, 59 serious | 9 fatal, 65 serious |
| prover, refused for | bearing, hearth, tiling, PROVEN | the same, PROVEN |
| prover, findings | 1 fatal, 45 serious | 1 fatal, 45 serious |

Fourteen of the 361 tests in the seventeen element test files went red on that record. So the
laying became a statement the record carries, and the shipped record does not carry it. **This
departs from the plan Lucas approved**, which said the record would move and be re-derived. The
reason is the table and this project's own precedent of keeping a shipped placement out of a
package about something else. `oq/the-shipped-range-is-still-laid-on-the-axis`.

**A composed linen press is shorter than its own door.** As first composed it is 1.3 x 2.9 ft
with a 2 ft 3 in door whose leaf and jambs need 2.95 ft. The prover asks for the 2 ft the room can
offer, so the door is seated only where the press happens to be drawn 3 ft on the passage. The
composer's declared loop widens the press to 3.0 ft before a compose places the house, so the
whole compose seats it; a bare `instantiate` then `solve` may not, and on one worker did not.
`oq/a-composed-linen-press-is-shorter-than-its-own-door`. Not fixed: each remedy changes what is
asked of every composed house with a linen press.

**Three of my own mistakes, each caught by a check or a run.**

- A comment in the first code commit wrapped an open-question slug across a line, and
  `check_citations.py` read the left half as dangling. Fixed in the next commit.
- The first code commit (`2263ab0`) left `test_THE_FLANK_IS_THE_PLACEMENTS_OWN_ARITHMETIC_on_a_
  three_element_house` red: its hand-built one-room east element is 12 x 14 ft under the one-room
  rule and was 9 x 19. I had not run that file. Re-cut with the movement attributed against the
  parent.
- My first "main block alone" measurement set the wing aside at a box the wing cannot fit even
  loosely, so it could not tell the two causes apart. Re-run with a wing box that tiles.

## IV. What was not done

- **The shipped Tidewater record is not moved.** See above and its question.
- **The linen press's door is not fixed.**
- **The search engine keeps the derived wing box.** It has no prover. A house with a wing placed
  by `engine="heuristic"` is laid against the rear wall and not sized for its door set.
- **`typefacts` labels a block by its role**, so this house's two dependencies read the same word
  in a refusal's text. `build/typefacts.py` was not to be loosened and was not touched.
- **`export_ifc.slab_boxes` gives a link room its wing's slab**, so a back hall or a mudroom link
  stands over no slab in the IFC. Older than this work; the chain adds one more link to it.
- **The back hall's `should_adjoin mudroom`** (strong) is no longer met by a door.
- **The mudroom link is 7 ft long** against the grouping's 12 to 20 ft, as the back hall's 5 ft
  already is: `oq/a-back-hall-cannot-be-a-hyphen-and-stay-inside-its-own-width-band`.
- **Lucas's own Tidewater brief** (Phase 17's "about once in nine") is not in the tree as a file
  and was not re-measured.

## V. The product, measured

`compose(briefs/family-georgian.json, 4)` at production defaults, one run at a time on one
four-core container, the worker count set with `TDL_CP_WORKERS`. "Not refused" and "drawable where
judged" are the set's own two counts (`compose.set_drawability`).

| workers | run | wall | returned | not refused | drawable where judged | the native double pile |
|---|---|---|---|---|---|---|
| 4 | 1 | 583 s | 6 | 4 | 2 | first; every fact held; DRAWABLE WHERE JUDGED |
| 4 | 2 | 582 s | 6 | 4 | 2 | the same |
| 4 | 3 | 546 s | 6 | 4 | 2 | the same |
| 4 | 4 | 569 s | 6 | 4 | 2 | the same |
| 1 | 1 | 538 s | 6 | 3 | 1 | last; refused UNDECIDED for bearing, stacks, tiling |
| 1 | 2 | 541 s | 6 | 3 | 1 | the same |
| 1 | 3 | 541 s | 6 | 3 | 1 | the same |
| 1 | 4 | 542 s | 6 | 3 | 1 | the same |

Two of the eight runs are not as clean as the rest and are said: four-worker run 1 was made before
the laying became a statement of the record (the composed house was laid the same way in both),
and one-worker run 4 ran while the mutation check used another core.

On every four-worker run the set was, in order: the double pile and the side hall, both DRAWABLE
WHERE JUDGED with the hearth unjudged; the living hall and the courtyard, placed and NOT DRAWABLE
(one door, and three doors with five rooms past their band); the five-part and the single pile,
refused and not proven.

For comparison, the parent's own report gives one run each on the same brief: four workers, 3 of 6
not refused and 1 drawable where judged; one worker, 2 of 5 and 0.

**The double pile placed alone.** `compose.instantiate` then `geometry.solve(engine="cp",
time_limit_s=60)`:

| workers | record | result |
|---|---|---|
| 4 | as first composed | 61.6 s; hard steps INFEASIBLE, INFEASIBLE, OPTIMAL at +0, +2, +4 ft; DRAWABLE WHERE JUDGED |
| 1 | as first composed | 61.0, 61.0 and 61.1 s; INFEASIBLE, UNKNOWN, OPTIMAL; every fact held; NOT DRAWABLE on the two runs that were assessed, for the linen press's door |
| 1 | as first composed, 120 s | 121.0 s; INFEASIBLE, INFEASIBLE, OPTIMAL |
| 1 | as the declared loop hands it on | 69.9 s at 60 s and 130.5 s at 120 s; UNKNOWN at all three depths both times |

**Why one worker does not decide inside a compose.** The composer's declared loop runs before the
house is placed and resizes thirteen of its rooms: the butler's pantry from 5.6 x 9.5 to
9.1 x 11.1 ft, the dressing room from 6.2 x 10.0 to 10.1 x 14.1, the three chamber closets from
2.2 to 5.2 ft wide, the passages from 8.5 to 10.0 ft, and eight smaller changes. On that record
the three hard steps each run out their slice undecided on one worker, at 60 s and at 120 s, so
the retry Lucas ruled on 30 Oct would not have helped; in the compose it was not begun, because
the set's budget had 40 s left. Four workers decide the same record inside the budget. Which of
the thirteen resizes costs the one-worker proof was not measured.

**The wing-sizing step's cost.** 3.0 to 3.8 s on the record as first composed (19 boxes posed,
21 x 22 ft taken) and 2.4 to 2.5 s on the declared loop's record (10 posed, 21 x 20 ft taken), on
one worker or four, no box undecided. On the shipped Tidewater record: 4.5 s, 50 posed, none held.

## VI. Tests and the whole build

**New tests.** 18 in `tests/test_garage_mass.py`, 2 in `tests/test_element_awareness.py`; one
re-cut away there. Three existing tests re-cut, each with its movement attributed against the
parent: the plan schema version pin (`tests/test_ingest.py`); the wing-growth test
(`tests/test_cp_portfolio.py`), which reads the composed record both ways now; and the
three-element lot fixture (`tests/test_element_awareness.py`), whose one-room east element is
12 x 14 ft and was 9 x 19.

**Mutation check.** 18 mutations over the new guards, each asserted to have landed and each
restored byte for byte. All 18 went red, in the tests written for them (checked by name on a second
pass without `-x`).

**The shipped plans.** With the laying a statement of the record, the corpus placement and
openings digests (`tests/test_elements.py`, `tests/test_appendages.py`) and the four CP model
hashes (`tests/test_cp_elements.py`) are unmoved.

