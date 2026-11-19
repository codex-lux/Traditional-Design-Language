# The refusal repaired, then retried (19 November 2026)

No WP number: the two Phase 17s share theirs, and this follows
`docs/reports/the-refusal-that-blamed-the-brief-2026-10-30.md`, whose §X left it as the next
package. Branch `claude/tender-ride-p9d1w0`, PR #46.

## I. What was asked, and what was ruled

That report's §X closed by naming what it had not done: no repair move reads a refusal. A refused
native candidate was only placed again, on the same declared record, at twice the compose budget.
Nothing in the revision loop read `geometry_report.refused` except as a guard. The registry's
authority block bars `exterior_walls`, `stacks_over` and geometry. `align-upper-walls-to-the-room-below`
was a stated refusal: *"No corpus record states that a room's declared exterior walls should match
the room it stacks over."*

Lucas chose that work and was asked four questions, each with the corpus's position beside it.
The questions and the answers are two acts, and both are recorded here verbatim.

| # | Asked | Answered |
|---|---|---|
| 1 | Stacks: when a placement is refused because an upper room is not over the room it is declared to stack over, may a repair move resize that upper room's declared width and length to match the room below? It is refused today for want of a corpus sentence; if allowed it is editorial, its basis the record's own claim. | **Allow, editorial.** |
| 2 | Hearth: when a fire stands on a wall the massing does not put a flue on, may a repair move re-author that room's declared hearth wall to the flue wall the massing names, on the 26 Sep ruling that the style's massing and kit govern the fire's wall? | **Allow.** |
| 3 | Bearing continuity and tiling: no corpus rule says where a wall should go to restore them. Should those two refusals get a repair move? | **No move; retry only.** |
| 4 | How should the composer use a repair? Today an unproven native refusal is placed once more at 2x the budget on the same record. | **Repair, then retry.** |

## II. What was built

**Two moves** (`moves/registry.json`, `build/moves.py`, held by `build/check_moves.py`).
- **`size-the-upper-room-to-the-room-it-stacks-over`** answers `drawn / stack-broken`.
  - It is editorial with `judgment: true`. Its basis quotes the drawn layer's own fix text,
    *"Place the two together, or drop the stacks_over claim."*, and it says in its own words that
    no corpus sentence makes the two rooms one size.
  - It writes the upper room's declared width and length, and nothing a placement writes.
  - It refuses by name where the room below falls outside the upper room's own area, width or
    proportion band, states no dimensions, or is already that size.
  - The stated refusal `align-upper-walls-to-the-room-below` is removed. Its reason is quoted in
    the new move's note, and the authority block's `may` list carries the ruling.
- **`put-the-fire-on-the-flue-wall`** answers `hearth / hearth-off-the-stack-wall`.
  - It writes `levels[].rooms[].hearth[].wall` only, under the `declared` authority.
  - It reads the wall from `hearths.flue_walls`, the one reader of the massing. That function's
    docstring now carries the 26 Sep sentence its basis quotes.
  - It refuses where `flue_walls` refuses, on a central stack, and where the room declares none or
    several of the flue walls, because choosing between two would be authoring.
  - `check_moves.LAYERS` gains `hearth`, and `ALLOWED_TOUCHES` gains the hearth wall.
- **`critique._intended_move`** names each move for its kind.
  - A broken stack stays a placement outcome on the SEARCH (`_is_placement`, unchanged), so the
    stack move is offered where the engine proves.
  - Only `hearth-off-the-stack-wall` gains a move. `room-without-a-hearth` asks the author for a
    fire, and no move may state one for them.

**The composer's branch** (`build/compose.py`).
- **The gate.** `repair_decision` is a pure function beside `retry_decision`. It repairs only:
  - a native diagram;
  - a refusal that names `stacks` or `hearth`;
  - a compose that did not ask for the search by name;
  - a set with budget left for one placement.

  A PROVEN refusal is eligible, because a changed record is what can move a proof.
- **The evidence.** `repair_findings` reads the refusal's own evidence off the placed record's
  `type_facts`: each broken claim, and each downgraded fire. It does not run a second critique.
- **The edit.** `apply_repair` applies each move to a copy of the record as composed, through
  `moves.apply`, so the touches-and-diff guard holds.
- **The placement.** The repaired record is placed once at the compose budget. It is adopted
  only where that placement is not refused and its judged key is no worse.
- **The fallback.** Otherwise the repaired record is discarded and the 30 Oct retry runs
  unchanged on the record as composed. A proven refusal is repaired once and never retried.
- **`card.repair`** names the moves and their logs, the outcome and the time. `as_composed: false`
  says the card's record is no longer the one the composer wrote, and the decisions say each
  branch.

**The surface.** The card adapter carries `repair` and reads `repaired` true only where the server
kept the repaired record. A placed card says *"repaired, not as composed"*.
- The plan named a glossary record for that line. It follows the retry's precedent instead: the
  neighbouring retry phrases are inline, under the copy ratchet's threshold.

**The words.** `how_to_read_this`, the `tdl_compose` description and `docs/compose.md` say what a
repair is and that it changes the record.

## III. What was found

**A repair can only make a refused house drawable where every refused fact is one it repairs.** On
both refused shipped records the refusal also names `bearing`, which has no move by ruling 3. On
the search (deterministic):

| record | refused for | broken stacks | the move | after re-placing |
|---|---|---|---|---|
| `spec-builder-colonial` | bearing, stacks | primary over garage | refused: the garage is 484 sf, outside the primary bedroom's 220-400 sf band | — |
| | | hall bath over laundry | applied: 5 x 9 to 6 x 7 ft | the hall bath's stack is KEPT; still refused (bearing, stacks: the primary's); fatal 14 to 13, serious 96 to 98, minor 96 to 99 |
| `tidewater-georgian-careful` | bearing, stacks | landing over stair | refused: the stair hall's 126 sf is outside the landing's 16-60 sf band | — |
| | | upper passage over passage | refused: 408 sf against 130-400 | — |
| | | principal chamber over drawing room | applied: 17 x 20 to 18 x 22 ft | that stack STILL broke and the upper passage's landed; the hearth was newly downgraded; fatal 6 to 10 |
| | | principal bath over butler's pantry | refused: 84 sf against 90-190 | — |

So of six broken claims on the two shipped records, two have an applicable move, one of the two
lands where it was meant to, and neither house leaves refusal. **A size is a weak lever on where a
placement puts a room.** Sizing the upper room to the room below makes a landing possible, and it
does not make the placer land it. On the Tidewater the repair moved the placement enough to land a
DIFFERENT claim and break the hearth. The composer would discard both repairs: one is still
refused, and the other is still refused and worse.

**The band guard refused four of six, and that is the guard working.** A stair landing the size of
a stair hall, or a bath the size of a pantry, would trade a broken stack for a room out of its own
band. The move says which band each time.

**The hearth move has nothing to act on in a composed set**: no composed house states a fire. On
the sixteen shipped plans `hearth-off-the-stack-wall` is emitted on none. The move is built and held by tests, and it
reaches a hand-authored record that disagrees with its massing.

## IV. The composes

(§IV is filled from the run recorded below.)

## V. What was deliberately not done

- **Bearing continuity and tiling**: no move, by ruling 3. On every refused record measured here,
  bearing is what keeps the house refused after the stack repair, so the refusals that ruling 3
  leaves are the ones that matter. The open question is the placer's:
  `oq/the-reinstatement-pass-gets-no-time-after-an-undecided-portfolio` and
  `oq/an-undecided-scout-releases-every-type-fact-at-once`.
- **Borrowed and lineage diagrams** are not repaired, matching the retry's ruled scope.
- **A broken stack on the search** stays a placement outcome, so the bench's inline revision on the
  search does not offer the stack move. A broken stack there is usually the search's own noise.
- **No glossary record** for the card's line (§II).
