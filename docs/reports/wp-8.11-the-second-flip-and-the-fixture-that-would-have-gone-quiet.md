# WP-8.11 — the second flip, and the test fixture that would have gone quiet

*3 September 2026. Closes `oq/a-pack-can-be-the-only-writer-a-node-has` and flips `facade-gable`.*

## The ruling

WP-8.10 raised the question because the reason it gave for choosing `trim-classical` was wrong: a
corpus-level writer count described no node, and per node **zero of its ten stranded nodes** could
reach an alternative writer of `trim_family`.

**Lucas ruled the same day: no new rule, stage by size.** Sole-writer status is not a precondition
on flipping, because WP-8.10 made a stranded slot NAME the pack withheld and why — so a node with no
alternative writer is not a casualty, it is a node whose author has a located question where a
silent wrong dimension used to be. Both refusals are recorded in the entry with the costs that
refused them: a standing precondition disqualifies every candidate measured and halts the flip after
one pack; per-pack adjudication costs ~29 readings for this pack alone at the ~1-in-6 overturn rate
that held across three WP-8.7 passes.

## The flip

`facade-gable` → `delivery: opt-in`. **32 slots over 29 nodes**, the measured figure exactly.

**The two-gate gap was 32 against 33, and the shape is worth carrying**: `applies_to` names 14
nodes, but **twelve of them BIND the pack themselves** and are never gated — only
`gothic-revival-american` and `queen-anne-british` receive it by descent, and only the second loses
a slot (`cornice_return`). Both were opted in; without them the flip would have stranded 33.
On `trim-classical` the same gap was 10 against 15. **It is a property of the pack, measured per
pack, and the ratio is nothing like stable.**

**29 of the 32 stranded slots are `cornice_return`, whose only writer in the corpus is this pack.**
That is the ruling being exercised rather than a surprise, and it is why the question was asked.

## THE FIXTURE THAT WOULD HAVE GONE QUIET

The finding of the package, and it is about tests rather than data.

`tests/test_opt_in_packs.py` and `tests/test_loud_stranding.py` both drove the gate through
`facade-gable` on `north-german-hall-house` — chosen in WP-8.10 **precisely because the corpus left
that pack on `cascade`**, so the fixture could flip it in a scratch graph and prove the gate bites.
Flipping it for real turns every one of those assertions into a statement about the shipped corpus:
the "counterfactual" becomes the status quo, the tests stay **green**, and they stop testing
anything. A mechanism that changes nothing on the day it ships reads exactly like one that does not
work — WP-8.9's own words — and this is that failure arriving from the other side.

Both fixtures moved to `trim-craftsman` on `mediterranean-revival` (three slots, still on
`cascade`), and both files now carry the rule in their own docstrings: **a driven fixture must name
a pack nobody has flipped, so check that before flipping the next one.** `sash-light` is next by
size and is not used as a fixture.

Three assertions had to change shape rather than value, because the fixture node now also carries
the corpus's real flips: asserting the withheld set *equals* one pack was a coincidence of WP-8.10's
node, and it broke the moment a real flip touched the same node. They hold the property now — the
driven pack is among the withheld, and none of the withheld was delivered.

One test got **stronger** by the change: `withheld_for` was asserted empty on the real graph
("a reporting function that always has something to say is not reporting"). It now names exactly the
two shipped flips that reach the node and nothing else, which is falsifiable where the empty
assertion was not.

## A scoping defect WP-8.10 shipped

`--stranding facade-gable` printed **"32 slot(s) over 36 node(s)"**. The slot counter was scoped to
the pack and the node counter was not, so the slots were one pack's and the nodes were every flipped
pack's. More nodes than slots is impossible for a single pack, which is how it showed. Two counters,
one scoped and one not — this package's own recurring shape, now with three instances.

## A THIRD REFUSAL MECHANISM, arriving exactly as the second one did

Found only by the whole-suite run, in a file this package had no reason to touch.

`test_construction_scope.py` holds a FLOOR on what each OQ 88 scope refuses — "a scope that stops
refusing reports success". It already counted **two** mechanisms, because counting one had made a
real refusal look like a scope going quiet: WP-8.7's declines stopped `opening-proportion` reaching
three nodes, so the scope never got to drop it and `refused` fell 59 → 56.

The flip is a **third**. `facade-gable/gable_treatment/parapet_height` went from 14 refusals to
**3** the moment the pack flipped — the rule no longer arrives at 11 nodes, so the scope never sees
it. Identical false signal, from a mechanism that did not exist when the second counter was added.

**The floor was not lowered**, for the reason that file already gives about declines: a floor that
drops every time a pack is flipped protects nothing by the last flip. The third mechanism is
counted, by the same in-place counterfactual the decline probe uses — lift the gate, re-resolve, ask
whether the scope would have dropped this rule here. 3 + 0 + 11 = 14, and the floor holds.

The test's docstring now says to expect a fourth: **any mechanism that stops a delivery before the
scope sees it looks, to this counter, like the scope failing.**

## The refill is not falling, and it can promote a live gate

WP-8.10 found that a flip refills the backlog exactly as a decline does. Two data points now:

| flip | slots stranded | new gaps promoted |
|---|---|---|
| `trim-classical` | 10 | **4** |
| `facade-gable` | 32 | **13** |

Roughly proportional, not decaying. And **three of the thirteen promote `facade-classical`, one of
the five packs whose `applies_to` arms a live behavioural gate** — so a flip can hand a reader a row
where ruling authorises a behaviour change rather than restoring a dimension. Those rows are marked
⚡ in the register's unread section, under the same rule the tabled sections already follow.

**Thirteen tabled rows were withdrawn and not one was decided**, kept verbatim under their own
heading. Twenty-nine nodes lost a slot and only thirteen had been tabled — not an oversight in the
table, but the size of the flip against the size of the reading.

## Counts

`RATCHET` 258/3123/217 → **256/3056/215** · `FORBIDDEN_RATCHET` 761 → **723** · `STRANDING` before
7820 → **7788**, stranded 2889 → **2857**, `rehoused` **1980 unmoved** (this pack re-housed nothing,
which its pre-flip 0/0 had said), `dimensioned_after` **4931 unmoved for the third package running**
— the end state was always going to be this corpus, whichever order the packs flip in, which is the
clearest demonstration that these are equalities describing a path and not ceilings describing
quality.

**`judged` is still 249.** Two flips, 102 withheld arrivals, zero cases read. The `withheld` line
`--strict` prints beside the three ceilings names both packs and says so.

## Deliberately not done

`sash-light` (70 slots, sole writer of `window_type` and `shutter`) — next by size, and the fixture
check above must be run before it moves. The five live-gate packs after that. The 181 tabled cases,
the 53 unread gaps, the 111 addresses that survive any flip, the 8 unjudgeable baked snapshots.
