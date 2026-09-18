# oq/the-entrance-porch-can-be-drawn-on-the-back-and-no-layer-says-so — the search charges 100 points and the critic is silent

*Status: CLOSED 17 Sep 2026 · Raised in: WP-13.5, the container (16 September 2026)*

**CLOSED BY THE MERGE, BY THE OTHER LINE'S FIX RATHER THAN BY ANYTHING DONE HERE, AND THE HALF
THAT IS NOT CLOSED IS NAMED BELOW.** Main raised the same finding independently as
`oq/the-search-loses-the-entrance-front-on-a-multi-element-plan` and then answered it: WP-11.17
STATES the entrance front, so `geometry.entrance_anchors` lays the one ground room that must
stand on it as a rectangle of its own declared area before the guillotine runs. Re-derived on
the merged tree with `engine="heuristic"`, the deterministic engine, on
`plans/tidewater-georgian-careful.json`:

| reading | main block | porch `y_ft` | on the entrance front |
|---|---|---|---|
| one rectangle (tags stripped) | 63 x 38.17 | 0.0 | yes |
| the shipped container | 45 x 37.24 | **0.0** | **yes** |

Against WP-13.5's own measurement of y 31.51 on the container — the NORTH wall — on a placer
this tree no longer has. The 100-point `entrance_score` charge is not paid by the winning
candidate on either reading.

**The guard is kept and INVERTED rather than deleted**:
`tests/test_composition.py::test_the_container_cost_the_rear_and_the_merge_PAID_BACK_the_front`
asserts both readings put the porch on the front, so a placer that loses it again fails there
instead of passing quietly. The test was RENAMED because its old name asserted a cost that no
longer exists.

**NOT CLOSED, AND IT IS THE HALF THE TITLE IS ABOUT**: `plan_check` still emits no finding about
which face a porch stands on. Both readings report the porch's DEPTH and nothing about its
position. What changed is that no placement in this corpus currently commits the defect, not
that a layer learned to see it — so this is closed as a DEFECT and the reporting gap is a
different question nobody has raised. Do not read a green guard here as the critic having been
taught.

---

*The original entry follows, unedited, as the record of what was measured on the tree that had
the defect.*

**`geometry.entrance_score` charges 100 points — `compose.SEV_W`'s own fatal tier — when a
threshold room does not touch the entrance front, and its docstring says in as many words that
it is *"weighted heavily enough … that no candidate with the porch off the entrance wall can
win against one that has it right, across the 250-candidate search."* On the Tidewater record
with its service programme in the dependency, on `engine="heuristic"`, a candidate wins while
paying it — and `plan_check` emits not one finding about which face the porch stands on.**

## The measurement

`plans/tidewater-georgian-careful.json`, `engine="heuristic"` (deterministic), the same record
read two ways — as shipped, and with its six container tags stripped:

| reading | main block | entry porch | on the S front? |
|---|---|---|---|
| one rectangle | 63.00 × 38.17 ft | x 35.51, y **0.00**, 5.40 × 9.00 | yes |
| as shipped (container) | 45.00 × 37.24 ft | x 31.47, y **31.51**, 13.53 × 5.73 | **no — it is on the N wall** |

The winning candidate's total demerit goes 768.7 → 936.1 across the same edit, and 100 of the
167.4 is this.

**On `engine="cp"` at the 40 s batch budget the porch is on the S front** (y 0.0, depth 7.0,
`FEASIBLE — kept polish from the heuristic hint by the CP objective`), and the one-rectangle
reading of the same record does not reach a placement at all in that budget (`UNKNOWN`). So the
regression belongs to the SEARCH and not to the record, which is why WP-13.5 reverted nothing.

## The half that is not about this plan at all

Both readings were run through `plan_check`. Every finding either mentions the porch's DEPTH or
does not mention the porch:

    The Porch Nobody Can Sit On: 5.73 against at-least 6.0        (fault, serious)
    The Four-Foot Porch: 5.73 against at-least 7.0                (fault, serious)
    Entrance Portico is DRAWN 5.7 ft across and cannot take its rocking chair   (drawn, serious)
    Entrance Portico is DRAWN 5.7 ft across and cannot take its two chairs …    (drawn, serious)
    Entrance Portico is entered from centre passage; the catalogue expects
      entry from street, garden, exterior.                        (adjacency, minor)

Not one of them says the porch is on the back of the house. The last is the closest any layer
comes, and it is a statement about the DOOR GRAPH — it would read identically on a porch
correctly placed on the front and reached through the passage.

This is WP-11.12's own sentence met at the entrance front: **a quantity a SCORE knows about and
a CHECKER does not is invisible in exactly the surfaces a person reads.** The fidelity score the
composer ranks on, the critique, every `revision_report` and both plates are silent, and the
sheet a reader turns to draws a portico on the garden side of a Georgian house without comment.

## What has to be ruled before anything is built

1. **Which layer.** A porch's face is a placement, so the finding belongs in `plan_check`'s
   **drawn** layer — the only layer permitted to read placement (OQ 54). That much is settled by
   the existing rule and needs no ruling.
2. **What it reads.** WP-11.12's precedent is that a finding about a quantity the search charges
   must READ the charge and not recompute it, *"because a second computation could convict a
   placement on numbers it was not chosen by"*. `entrance_score` returns a float and publishes
   nothing; there is no `geometry_report.entrance` to read. Either the score discloses its own
   per-room verdict, or the finding recomputes `_touches_wall` and the corpus acquires a second
   answer to one question. **This is the real question.**
3. **Its severity.** A porch on the rear is not a house that cannot be walked, so `serious`
   argues itself; but `entrance_score` charges it at the FATAL tier and the two surfaces
   disagreeing about one fact is the shape this corpus keeps finding.
4. **Whether a threshold room in a dependency is exempt.** `_touches_wall` takes the main
   block's `W, H`, so a porch on a wing would be convicted for standing on the wing's own front
   — which is the seventh and eighth instances of *the main block read as the whole building*
   already recorded against `principal_and_service_score` and `axis.front_openings`. A rule
   written without that filter would be wrong the day somebody draws a wing with its own door.

## What is NOT the question

**Do not close this by reverting the container**, and do not close it by re-weighting
`entrance_score`. The prover places the porch correctly on the same record; a heavier charge
would change which candidate the SEARCH picks on every plan in the corpus and is a placement
change wearing a reporting question's clothes. And do not close it by reading the adjacency
finding above as the report — a finding that is true of the right answer as well as the wrong
one is not a report of anything.

## Related

- `oq/the-facade-layer-counts-a-dependencys-windows-as-bays-of-the-front` — the same
  main-block-as-the-whole-house reading, one layer over, raised by the same package.
- `oq/the-service-charge-convicts-a-room-for-standing-in-the-wing-it-was-put-in` — the third
  instance, in the placer's own objective.
- `docs/reports/wp-11.12-the-span-nobody-was-told-about.md` is the worked precedent for adding a
  finding for a quantity the search already charges — including its rule that the finding READS
  the charge. (There are two WP-11.12s; cite the report by filename, as CLAUDE.md requires.)
