# WP-8.7: the backlog that refills as you work it

*2 September 2026. OQ 51's adjudication half, first pass. Follows WP-8.2, which built the refusal
mechanism and the meter this package reads.*

## What was built

**`--pair NODE PACK`** on `build/check_inheritance.py`: the one screen an adjudication needs. What
the pack claims to dimension (its `kind`, the first paragraph of its own `notes`, every
`target_slot` its rules touch, how many nodes its `applies_to` holds and whether this one is among
them, and any sentence in the pack's notes that names this node); what the node's own record says
(`governing_logic`, `bay_rhythm`, `symmetry`, `typical_ratios`, the head of `description.long`, its
tells and its `distinguished_from` differences); whether endorsing ARMS a live check; and then the
existing `--impact` report of what declining costs.

`governed()` was hoisted out of `main` to module scope on the way, so `--pair` reads it rather than
restating it, and the CTX dict that four branches each spelled separately is now spelled once.

**Fifteen declines**, on `appalachian-log-house` (8) and `log-vernacular-american` (7), each
carrying a verbatim quote from the node's own file and its measured `--impact`.

## The rule this pass worked to

Endorse or decline **only where a sentence in the node's own record affirms or contradicts what the
pack's own notes say the pack is about**. Not the pack's name, not the ancestor it arrived from.
Everything else goes to a ruling rather than to an editorial guess. No `basis: editorial` decline
was written.

That bar refused work as well as authorising it. **`sash-light` on both log nodes was NOT
declined**, though both records say *"There is no applied proportional system"* and the regex that
finds blanket refusals matches them. The pack's subject is not a proportional system: it is that
light count is *"an arithmetic consequence of one number — the largest pane the glasshouse could
supply."* A log cabin with sash windows takes its light count from the glass trade like everything
else. A decline there would have been an editorial call wearing a `node-record` basis, which is
the one thing this mechanism must not be used for.

## What was found

**The backlog refills as it is worked, and the published number is what is visible rather than
what is required.** `resolve_packs` fills a role from the nearest ancestor that binds one; decline
that pack and the role re-attributes to the next ancestor down, as a new unendorsed gap for the
same node in the same role. WP-8.2 saw the first order of this — *"ten declines and `unendorsed`
did not move once"* — and made `judged` a floor. Read to the end:

| | before | after |
|---|---|---|
| role_gaps | 287 | 283 |
| inherited_packs | 3,356 | 3,341 |
| unendorsed | 249 | 245 |
| judged | 48 | 63 |

**Fifteen declines moved the headline by four.** Simulated to fixpoint,
`appalachian-log-house` needs **26 declines over 9 rounds**; `log-vernacular-american` the same 26
over 10. The queue for the first runs: palladio-corinthian, facade-classical, sash-light,
palladio-doric, facade-peristyle, opening-proportion, vignola-doric, facade-arcade,
opening-mullioned, vignola-ionic, facade-picturesque, opening-pointed, vignola-corinthian,
facade-medieval-english, benjamin-doric, stone-course, corbel-course, gibbs-doric — five classical
orders, a Gothic pointed-arch pack, a Mudejar corbel course and an Iberian arcade, all arriving at a
single-pen log cabin. Eighteen nodes carry a comparable blanket refusal, covering 60 of the 249; at
26 apiece that class alone is roughly 470 declines to settle under a quarter of the backlog. Raised
as `oq/a-node-that-refuses-a-category-must-decline-it-twenty-six-times`, because it bears on OQ 51's
own sequencing: for a node that takes NONE of what the cascade sends, the adjudication and the
opt-in flip reach the same end state and differ only in whether the record says it once or
twenty-six times.

**Declining a wrong pack can hand the slot to a wronger one.** `appalachian-log-house` declining
`brick-course` passes `steps_and_stoop` to `palladio-tuscan` — a Renaissance order, on a log cabin.
Nothing in the mechanism prevents this; OQ 58's stated limit (*a decline stops a pack, it does not
supply one*) is doing real work, and the successor is itself an unendorsed delivery. Recorded in the
decline's own `note` rather than left for a reader to discover.

**A pack whose headline number matches the node's own is the easiest wrong endorsement available.**
`timber-bay` dimensions a 16-20 ft structural bay off English box frames. The Appalachian pen is
16-20 ft — because a hewn log is as long as it is, with no posts for a partition to fall near. The
figure coincides and the mechanism does not exist. Declined, with the coincidence named in the note
so the next reader does not re-derive it as agreement.

**Two declines stopped a pack overwriting a measurement the record already states.**
`timber-panel` dimensions `wall_thickness_frame` on a node whose own `typical_ratios` say *"Hewn
wall thickness 6-9 inches"* — a solid wall. `primary_cladding` and `wall_thickness_frame` lose all
dimensioning on the decline, which is the honest outcome: a log wall has no cladding layer and no
frame to thicken. Both are among the four slots `check_faults.py` reports as covered by no fault at
all, so nothing was checking that figure either.

**One decline costs a slot its only figure and was written anyway.** `storey-graduation` on
`appalachian-log-house` governs `stair_type`, which loses all dimensioning. A log loft is reached by
a ladder or a boxed corner stair and a figure derived from a graduated Georgian stack was never the
right one; no dimension beats a wrong dimension, which is this corpus's own rule. Endorsing was the
alternative, and would have ARMED `structure.graduation_check` for every plan of the style against a
ratio its record refuses. There is no neutral option on a gate pack.

**THE HOIST BROKE A FLAG AND THREE OF THE FOUR STAYED GREEN.** Moving `CTX` to module scope left
the `--slots` branch's own `CTX = {...}` in place, and Python makes a name local to an entire
function if it is assigned anywhere in it — so the module-level constant became unreachable from
every other branch of `main()`. `--slots` worked because it assigns before it reads; `--impact` and
`--pair` worked because they read CTX inside `governed()`, which is a different scope. Only
`--forbidden` raised, and only `check_all` runs it. **No test invoked any of these flags**, which is
the shape this repository keeps finding: a diagnostic that works until it does not, with nothing
watching. `tests/test_declined_packs.py` now runs all seven flags as subprocesses and requires each
to exit 0 and print something, mutation-proved by reintroducing the local rebind.

**AND THE NEW `pack_file()` READ A DIRECTORY UNSORTED.** `glob.glob` returns filesystem order,
which differs between machines, and this glob decides which file wins if two ever declared the same
pack id. `tests/test_determinism.py::test_corpus_globs_are_sorted` greps `build/`, `mcp_server/`,
`workbench/` and `tests/` for every spelling of a directory read and refuses an unguarded one; it
caught this on the full run after the targeted suites were green. Sorted. **Both defects in this
package were in the new tooling rather than in the judgments** — worth saying, because the
adjudication is the part that looks risky and the plumbing is the part that broke.

**AND THE DECLINES WERE CHECKED FOR THE SECOND DELIVERY PATH, WHICH NOBODY HAD ASKED ABOUT.**
`oq/a-baked-pack-value-is-a-second-delivery-path` records that a pack rule reaches a node twice:
live through `eval_packs`, and BAKED into an ancestor's kit file as an authored parameter carrying
`source: <pack>`. A `declined_packs` entry closes the live path only. Three separate checks
established that these fifteen were well-formed — schema, verbatim quote, `check_declines`' own
lie-check — and not one of them asked whether the pack actually stops arriving. Measured directly:
on both nodes, **0 of the declined packs survive in `resolve_packs`, and 0 baked parameters
anywhere in either resolved kit carry a declined pack as their source.** That is a measurement
rather than an assumption, which is why it appears here: an adversarial audit pointed out that the
package had never established it.

**AND IT WAS TRUE OF THOSE TWO NODES AND NOT OF THE CORPUS.** Swept over all 88 declines after the
later batches, `check_addresses.py::baked_vs_refused` went **32 to 64**: **18 of the 88 declines
have a baked survivor**, contributing 44 of those 64 across 15 nodes — `storey-graduation` 12,
`facade-classical` 11, `trim-classical` 10, `gibbs-ionic` 8, `brick-course` 3. Each of those
eighteen is a decline doing exactly half its job: `resolve_packs` stops delivering the pack and an
ancestor's kit file still carries a snapshot of one of its values as an authored parameter, which
nothing refuses.

Two things follow, and the first is about method. **Measuring two nodes and writing "the declines
are clean" was the WP-4.4 error in a new place** — a figure that was true where it was taken and
published as though it described the whole. The sweep is corpus-wide now and the ratchet carries
the number. Second, the declines are NOT withdrawn: the live path really does close, the baked path
was already there and already counted, and what the declines did was make it visible on nodes
nobody had judged. `oq/a-baked-pack-value-is-a-second-delivery-path` now has a measured size on the
records a human has actually ruled on, which is the largest thing this backlog has surfaced.

## The full pass: all 244 read, and reading them made 73 more

The first pass above covered two nodes. The rest of the backlog was then read the same way — one
agent per node, the pack's own stated subject beside the node's own record, `--impact` and the gate
line, and **every proposed data change put to an independent adversarial check before it was
written**. 93 nodes, 244 (node, pack) pairs, five workflows.

| | WP-8.7 start | after |
|---|---|---|
| role_gaps | 287 | 268 |
| inherited_packs | 3,356 | 3,252 |
| unendorsed | 249 | 227 |
| declines | 10 | 114 |
| endorsed | 38 | 41 |
| **judged** | **48** | **155** |

**Twenty-one of the proposed changes were overturned** — about one in five of everything that would
have touched data — and the overturns are the best evidence the bar held. `english-baroque` ×
`storey-graduation` was proposed as a decline on the node's own *"but Georgian has graduated storey
heights"*. The check refused it: the pack carries a fourth rule for a ground storey under a piano
nobile whose own text says *"this is the one case where the graduation inverts at the bottom"*, and
the node's `typical_ratios` state *"Rusticated basement 0.5 to 0.75 the height of the principal
storey above it"* — the same quantity, overlapping bands. The decline rested on negating a
comparison while the record affirmed one of the pack's own rules elsewhere. Four more were the same
shape: a difference of degree read as a contradiction.

**The bar refused work in the other direction too.** `sash-light` was tabled on every log and
vernacular node that carries a blanket refusal of applied systems, because its subject is the
largest pane the glasshouse could supply — a fact about the glass trade, not a proportional system.
The same nodes' `chambers-doric` and `facade-classical` gaps WERE declined, because an order and a
bay count are proportional systems and those records refuse them by name.

**No gate pack was endorsed into by any batch**, so nothing generated changed. The three
endorsements are `facade-gable` (×2) and `balcony-gallery`, all outside the GATES table.

## The ruling file, and why it has two sections

`oq/the-adjudication-cases-the-records-do-not-decide` carries **152 cases grouped by the pack that
settles them all at once** — `opening-proportion` and `storey-graduation` are 42 of them between
them — with the five gated packs marked, because a ruling on those rows authorises generated
behaviour rather than bookkeeping. Twenty-one rows are marked as having arrived by refusal.

It carries a **separate section for 73 pairs nobody has read**. They did not exist when the reading
started: declining 114 packs promoted the next one in each chain into the role it vacated. Listing
them as "cases the records do not decide" would be false, so they are named as what they are.
**Reading 244 gaps produced 73 more** — the refill measured at full scale rather than on one node,
and the reason `oq/a-node-that-refuses-a-category-must-decline-it-twenty-six-times` matters.

**A DECLINE IS A REFUSAL THE SCOPE METERS CANNOT SEE, AND IT TURNED THE SUITE RED THREE NODES
LATER.** `tests/test_construction_scope.py` holds each OQ 88 scope to a FLOOR — the deliveries it
refused when it was written — because a scope that quietly stops refusing reports success. After
the declines landed, `opening-proportion/window_surround_wood/exterior_head_assembly_height` read
**56 against a floor of 59** and the full suite failed.

Nothing had regressed. Three nodes now DECLINE `opening-proportion`, so its rule no longer ARRIVES
at them and the scope never gets the chance to drop it. Measured rather than inferred, by running
the test's own reader over the graph with and without those three declines: **56 against 59, and
the difference is exactly `andalusian-courtyard-vernacular`, `french-provincial-farmhouse` and
`moorish-andalusian`**. The delivery is refused earlier and by a person quoting the node's own
record — strictly stronger than an automatic scope test.

**The floor was NOT lowered.** That file's own note warns that a floor lowered without its reason
reads as a refusal quietly weakened, and a floor that drops by one every time somebody declines a
pack would protect nothing by the end of this backlog. The second mechanism is counted instead —
`declined_away`, measured by lifting each decline in place and re-resolving — and the SUM is held
to the original 59. Both numbers appear in the failure message so the two can be told apart.
Mutation-checked both ways: lifting a decline moves the count between the two columns and holds
the total; neutering `rule_scope` still fails, because a decline the node never made cannot make up
the difference.

The general shape is worth carrying: **two mechanisms can refuse the same delivery, and a meter
built for one reads the other's success as its own failure.** The same will be true of every scope
floor as the backlog is worked.

## What was deliberately not done

**The other 245.** This pass read two nodes to near-fixpoint rather than skimming twenty, because
the finding above is only visible if you follow one node to the end. `--pair` exists so the next
pass is faster than this one was.

**No endorsements.** Every judgment here was a refusal. That is a property of the two nodes chosen —
vernacular types that refuse applied systems outright — and not a policy; the endorsement half is
untested by this pass and `endorsed` stands where WP-8.2 left it, at 38.

**The two log nodes are left short of fixpoint**, at three visible gaps each, so the queue this
package is about stays visible in `--unendorsed` to the next reader instead of being tidied away.

**The opt-in flip.** Not this package. One correction to WP-8.2's account of it: that report named
`mcp_server/core.py`'s private cascade walk as a blocker, and the WP-8.4 audit has since made
`core._cascade` delegate to `resolve_kit.chain_for`. The blocker is stale; the flip is still a
ruling.

## Files

`build/check_inheritance.py` (`--pair`, hoisted `governed`, one CTX, ratchet re-pinned) ·
`styles/appalachian-log-house.json`, `styles/log-vernacular-american.json` (fifteen declines) ·
`tests/test_declined_packs.py` (re-pinned, plus the seven-flag guard and a `--pair` content test), `tests/test_wp46_packs.py` (re-pinned; the CLAUDE.md tally guard
caught the new question before this report was written) ·
`docs/open-questions/oq-a-node-that-refuses-a-category-must-decline-it-twenty-six-times.md`.
