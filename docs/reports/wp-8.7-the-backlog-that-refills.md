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
