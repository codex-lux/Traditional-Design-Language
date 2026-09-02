# oq/the-revision-loops-authority-over-topology — what the generator may change when the critic tells it to

*Status: RULED 1 Sep 2026 · Raised in: The Phase 9 planning session (1 Sep 2026)*

**RULED — the revision loop may change dimensions, declared choices, openings AND rooms; it may
not add a room the parti has no place for, fill a judgment slot, edit geometry, act on a
critic-suspect, or write a measurement the record did not declare.** Lucas, 1 Sep 2026, put as
three choices and answered in one sitting.

**The question.** Phase 9 builds a loop in which `plan_check` judges the drawn house,
`build/critique.py` says what each finding means, and `build/revise.py` applies a registered
move and re-judges, round after round. The composer's standing refusals were written for a
single pass: *"It will not invent a room the diagram has no place for"*, *"It will not drop a
room that is load-bearing for a rule"*, and a door was the parti's and the author's intent. A
loop that may only resize rooms hands every stranded room to the architect; a loop that may
re-draw the topology is a different generator. Where is the line?

**The ruling, as three answers:**

1. *What does the reflecting?* A deterministic loop: a named move registry
   (`moves/registry.json`, `build/moves.py`) executing corpus rules, `plan_check` re-judging
   every round, no language model editing the record. The rail may narrate a critique; it may
   not author a move.
2. *How much authority?* Dimensions and declared choices — and also openings and rooms: the
   loop may add or move a window on a declared exterior wall, add the door
   `openings/grammar.json` prescribes between a stranded room and a placed neighbour, drop a
   room the parti marks `required: false` that the placement cannot hold, and split a room
   where its grouping's own record says to split rather than enlarge. This reverses the
   composer's refusal on rooms and openings **for these cases only**. Still refused: a room the
   parti has no place for (decision #3 — a scullery `kitchen-work-core` says to add is a room
   the diagram did not draw); a judgment slot (decision #6); geometry, `exterior_walls`,
   `stacks_over` (decision #11 and CLAUDE.md's trap list); a `must_have`; a critic-suspect; a
   measurement the plan did not itself declare; calling a plan good (decision #10).
3. *When does it run?* By default, everywhere a product is made — the MCP composer, the bench's
   compose job, the CLI — on the RETURNED candidates after ranking, with a round cap and a
   per-candidate budget; `--no-revise` / `revise: false` opts out.

**Recorded** in `moves/registry.json`'s `authority` block (what it may and may not do, verified
by `build/check_moves.py`'s allow-list, which admits no placement key), in `PLAN-OF-ACTION.md`
§2, and in WP-9.2's report.

**What the ruling did not decide, and is left open here:** whether a move may ever re-point an
author's door at a different room (`move-door-to-a-shared-wall`, refused in the registry as
superseded by adding one), and whether the loop may run the composer's own `reclaim` more than
once (it runs it once, after the loop, under the brief's tolerance).
