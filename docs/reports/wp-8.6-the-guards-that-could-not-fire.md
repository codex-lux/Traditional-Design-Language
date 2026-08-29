# WP-8.6 — the adversarial audit of WP-8.1 through WP-8.4

*28 August 2026. Twelve read-only auditors over the session's whole diff, a verify pass on
every finding, and a completeness critic. **44 findings acted on** — 8 blocking, 16 worth
fixing, 9 tests that could not fail, and 11 published numbers that had gone stale. The three most useful are at the top because they are the ones that say
something about how this corpus fails, not just what was wrong with it.*

---

## The three findings worth reading if you read nothing else

**1. A guard nobody runs is a comment, and three of this session's shipped guards could not
fire.** WP-8.1's CI id-collision gate — *"THE ONLY PLACE A CROSS-BRANCH ID COLLISION IS
DETECTABLE BEFORE IT COSTS A RENUMBER"*, written after four collisions in four days — walked
the ids the branch **added** and then required each to be **in the base branch**. Those two
conditions are complements; the loop body was unreachable on every iteration. The step printed
"No open-question id on this branch collides" for the exact case it exists to catch, in both
checkout shapes. `grep -rn ci.yml tests/` returned nothing.

The same shape twice more, both proved by an auditor mutating the code and watching the suite
stay green: **check A of `check_citations.py`** (the dangling-citation check) can be deleted
with all 18 of its tests passing, and **both frozen-99 enforcement sites** can be disabled with
all 31 open-question and citation tests passing. In each case the test asserted a property of
the *parser* (`999 not in entry_ids()`, `max(entry_ids()) == 99`) and never handed the offending
input to the *checker*. A parser that can see the number is not a checker that refuses it.

All three now run their subject against a fixture and are mutation-proved. And fixing the third
found that `check_citations`' own ceiling branch was **dead code**: `entry_ids()` delegates to
`check_ids.read_questions()`, which refuses an over-ceiling file and drops it, so the id had
already been removed before the branch that looked for it. It delegates now rather than
re-deriving — a dead second copy of a rule is worse than no copy, because it reads as
belt-and-braces and is neither.

**2. A fix that removes a shield has to look at what the shield was covering — and this
session's own fixes are not exempt.** WP-8.3 bound `transom_sidelight` on `colonial-revival` on
that node's own evidence, correctly, to close a forbidden-slot exposure. It carried
`elliptical-fanlight` and `sidelights` **canonical to ten descendants**, three of which say
otherwise in their own files, and it is not inert: `elevation.py:318` reads `sidelights_forbidden`
off exactly this record, so the generator began **drawing an Adamesque fanlight-and-sidelight
entry on a single-storey ranch house**. Binding those three on their own records then carried
`none` canonical one hop further to `neo-eclectic` — which `styles/neo-eclectic.json` calls
ranch-style's *"structural parent"* and whose defining characteristic is *"an entry element
inflated in height and width … frequently rising through two storeys"*. Four nodes bound in the
end, each on its own quoted evidence, and the fourth exists only because the audit re-measured
its own fix. Raised as `oq/a-kit-binding-propagates-to-descendants-nobody-read`.

**The same rule fired on the audit's own fix, and reversed it.** Making `roof.py`'s chimney read
the cascade — which its docstring had claimed since it was written, and which 64 of 164 styles
need — put a **Gothic Revival clustered stack on a Colonial Revival house**: `colonial-revival`
states nothing about chimneys, so the cascade hands it `tall-multiple-vertical-accent` from
`british-picturesque`, *"thin and numerous and well out of proportion"*, seven steps up. It took
`spec-builder-colonial`'s placed chimney positions from 1 to 0, and it was caught by
`tests/test_roof.py` rather than by me — my own before/after check had read the wrong key and
compared `None` to `None`, **a vacuous check inside an audit of vacuous checks**.

That failure produced the distinction the whole raw-kit question turns on: **an inherited
`forbidden` is a prohibition an ancestor made and the descendant never overturned; an inherited
CANONICAL is a positive claim the descendant never made.** The first is safe to read from the
cascade — `plan_check` reads only that kind and keeps the fix. The second is not, until the slot
has been adjudicated on that node. The chimney change was reverted, its docstring made honest
about reading the node's own kit, and the reason pinned as a test so the next reader who notices
the docstring does not re-make it.

And a test fixture that symlinked `build/` into a pytest tmpdir
poisoned `modcache` for the whole session: two files later `check_constraints` was still the
tmp-rooted copy and raised `FileNotFoundError` on a directory pytest had deleted. **It passed
alone and failed in the suite**, which is the worst shape a test defect takes.

**3. Two records of one rule, and this corpus keeps finding a third.** `mcp_server/core.py`
carried a **second, truncated kit cascade**. `_cascade` walked `lineage` edges with
`inherits_kit` and never spliced in a style's family-rank ancestors, which `build/build.py` has
done for every style since WP-4.2 — dated one day after that function was last touched.
Measured: **all 132 buildable styles got a shorter chain than `resolve_kit.chain_for`, 1,308
ancestors dropped and 0 added, and the two disagreed about whether a slot is forbidden on 206
(style, slot) records.**

It was served to users twice — `tdl_resolve_kit`, which `tdl_overview` advertises as *"what the
style actually specifies, slot by slot"*, and `GET /api/kit/{style_id}`, the workbench Kit
surface. Concretely, `resolve_kit('appalachian-log-house', slot='order')` answered `specified`
from `english-palladian`, canonical `ionic`, quoting Palladio's *I Quattro Libri* — **on an
Appalachian log house** — because `nordic-alpine-vernacular` binds `order` FORBIDDEN and is a
family node. And WP-8.4 had made the file self-contradictory by adding `_resolved_kit()` beside
it, which uses `rk.resolve_slots` and is right. `_cascade` delegates now. Cost of correcting it,
measured before the change: 7 additional fault applications corpus-wide, each a fault written
for a family reaching a member of it.

---

## I — What blocked deployment

| # | finding | origin |
|---|---|---|
| 1 | `choose_pack`'s new `kit.forbidden` branch omitted `rejected`/`stale_calibration`, so `resolve_kit.py --slot` raised `KeyError` on any node with a refused slot | introduced |
| 2 | `corpus_tokens()` read `applies_when` after WP-8.4 renamed it to `granted_when`, returned an empty Counter, and every test written to guard the vocabulary passed vacuously | introduced |
| 3 | A `declared` value short-circuited the authority walk, so telling the resolver MORE about a house made it answer WRONG | introduced |
| 4 | The `strength: partial` guard was skipped on the declared path, so `thick-stucco` could return `holds` — the one thing that token must never do | introduced |
| 5 | The CI id-collision gate was structurally incapable of firing (above) | introduced |
| 6 | `grant_exception` dropped `granted_when.slots` — 104 records, the sole precondition on 67, and 54 of those substitute a `bounds_test` for the fault's primary test. They returned `granted / "no precondition" / unevaluated: []`, a false statement about a record that carries one | pre-existing, exposed |
| 7 | `plan_check`'s style layer read the raw kit: blind to **879 forbidden bindings and 3,661 forbidden variants**, on all 132 nodes | pre-existing, exposed |
| 8 | `mcp_server/core.py::_cascade`, truncated (above) | pre-existing, exposed |

On 7: `cape-cod-colonial` forbids the whole classical-apparatus group at the family level and a
plan declaring a balustrade on it went unremarked here while `elevation.py` refused to draw one
— two layers disagreeing about the same record. Swept over all 132 styles before changing it,
per the WP-8.4 ruling that a new conviction is a suspect until read: 110 unchanged, 19 gaining
one finding, 3 gaining two, every one a true call. **Both shipped plans gain nothing**, which is
why nothing caught it.

## II — Worth fixing

**Unjudged reported as something else, four times.**
`check_division_guards.py` declared `COULD_NOT_EVALUATE = 2` against the runner's 3, so a sweep
that could not run would print as a FAILING check (now guarded for every checker in `build/`, by
walking them rather than naming them). `--forbidden` could report **0 pairs over 0 nodes and
satisfy a ratchet that may only fall** — 0 is the most satisfying number such a ratchet can read,
and "fewer overrides than ever" and "the corpus was not read" are the same integer; it exits
COULD NOT EVALUATE now. `baked_vs_refused` and `kit_vs_pack` swallowed per-node exceptions with a
bare `except Exception: continue`, so a change that broke resolution would have LOWERED a
may-only-fall count. And `out_of_calibration` — the engine's own refusal to stand behind a number
— was dropped by **both** key-by-key row rebuilds, so `resolve_kit.py adam-style --slot chair_rail`
printed 1'-10¾" with nothing beside it while the engine row read *"ceiling_height is 108,
calibrated for 142.5-168"*. The identical symptom two files record as already fixed.

**A refusal the meter could not see.** `baked_vs_refused` recognised two refusal shapes — a row
marked `refused_by_kit`, and a rule dropped by scope with the drop recorded — and could not see a
**decline** at all, which leaves neither. `ranch-style` and `minimal-traditional` each decline
`storey-graduation` and each still resolve baked parameters sourced from it, so
`check_inheritance --impact ranch-style storey-graduation` named the declined pack as the slot's
governor. Ratchet **20 → 32**, and the reason is in the ratchet's own comment: the instrument got
sharper, the corpus did not get worse.

**A licence refused for being exactly what it describes, twice.** Evaluating
`granted_when.construction` for the first time refuses 19 of 123 licences **on the style named in
their own `style` key**. Seventeen are substantive and correct — `pueblo-revival` is canonically
`stucco-over-wood-frame`, its own tell reading *"the revival often achieves the look in 2 in. of
stucco over frame"*, so an adobe licence genuinely does not hold — and that is the package
working. Two named an exact variant as a stand-in for a class:
`water-table-that-follows-the-grade`'s Cotswold licence required two wythe variants on a node
canonically `rubble` while its own bounds read *"the one place this reads as licence rather than
error is where the wall itself is **rubble**"*, and `quoin-by-catalogue`'s Baronial licence did
the same against a *why* reading *"**Rubble walling** with dressed ashlar corner dressings"*.
Both corrected on their own prose; nothing new claimed. **WP-8.4's report called the first one
settled and it was not — the verdict was byte-identical before and after the kit binding it
credits.** That paragraph is corrected.

The discriminator is mechanical, so it is now a standing test: a refusal is suspect when a
BROADER vocabulary token — one whose variant list contains the named token's — holds on the same
style. The nineteenth, `porch-ceiling-of-exposed-joists` on `craftsman`, is conditioned on the
wrong axis entirely (its `why` and `bounds` are about the porch members, not the wall) and is
**named in a `KNOWN_WRONG_AXIS` set rather than patched**, because widening it to `wood-frame`
would grant it to every wood house and throw away the discrimination the licence is made of.
Raised as `oq/a-licence-conditioned-on-the-wrong-axis`.

**The second instance of the `brick` bug, found by looking for the sibling.** `stone-rubble`
answered a hard `fails` on `scottish-baronial` — whose `primary_cladding` is canonically
`squared-rubble-granite-ashlar-harled-rubble`, printed in its own refusal detail — because
`construction_type` leads the walk and `solid-masonry-two-wythe` is material-NEUTRAL: it says how
many wythes and nothing about the stone. The same node the `brick` note was written about. Two
tokens read the face first now and four read the assembly first, each with its reason. The
general form, including the `cut-stone`/`beaux-arts-american` case left deliberately undecided,
is `oq/a-material-neutral-assembly-decides-a-material-question`.

**Two hazards on the live request path.** `resolve_any` implemented its token union by writing a
sentinel into the module-level `VOCABULARY` and popping it in a `finally` — on
`/api/plan/evaluate`, which FastAPI serves from a threadpool, concurrently with the compose
worker's own `plan_check`. Two requests inside it at once resolve each other's union, or pop it
out from under each other; both outcomes silent, one of them a **licence granted on another
request's tokens**. `resolve()` takes a spec now. And `corpus.invalidate()` — behind
`POST /api/dev/reload` — missed WP-8.4's two new caches, so after a reload every exception
precondition was still resolved against the pre-edit kit graph for the life of the process. That
is the **third** miss of the same kind in that one function, so its guard now walks the module
for anything with a `cache_clear` instead of naming them.

**Half a pilaster.** `pilaster_projection_in` was gated on the kit and `pilaster_width_in` was
not, so `cape-cod-colonial` — *"The whole classical-apparatus group is forbidden at the family"* —
published a pilaster **width** of 7.655 in to the fault corpus while publishing no projection.
The `total_shutter_leaves` shape exactly, and worse for sitting beside a correctly withheld
sibling, which reads as deliberate.

## III — Tests that could not fail

Nine, every one mutation-proved by an auditor before it was reported and re-proved after the fix.
Beyond the three in §1: the live-hazard test read `LIVE_RATCHET`, a pinned literal only a human
edit can move, and called itself *"the figure that matters"* (a real unguarded division added to
a fault broke the checker's ratchet and left it green — it measures now, via an extracted
`live_hazards()`); the partial-token test picked a witness where the exact token already failed,
so the exclusion it guards could be deleted with the file green (**and the exclusion is inert
corpus-wide** — measured both ways, byte-identical — so the rule is prospective and the test now
says so); `assertIn("_construction_vocabulary()", body)` was satisfied by the helper's own `def`
line; the `window_head_masonry` source read had no negative half where its `shutter` sibling did,
so reverting it was caught only by coupling through a neighbouring test; and the material-token
test's behavioural half survived its own mechanism being reversed.

`denominators()`'s docstring promised that *"names it cannot attribute are reported by `main()`"*
and `main()` had no such branch. Implemented rather than deleted — 0 instances in the corpus
today, so this is a false promise made true rather than a live miss found.

## IV — Numbers that had gone stale

`787 → 776` in two places and in this branch's own WP-8.3 report; `46 → 40` for the elevation
exposure; the OQ 51 meter still published as `294 / 233 / 3,367` in `STATE-OF-THE-PROJECT.md`
line 92 while line 142 of the same file carried the corrected `287 / 249 / 3,356`; OQ 86's
`kit_vs_pack` as **62** when this session's own change of that function from `load_kit()` to
`resolve_slots()` took it to **1,231**; `41 checks, 1,154 tests` against 1,195; `3,366` against
3,356; a citation of a WP-5.17 that has never existed. And `ranch-style`'s slot figures were
stated **three times in one test with no two agreeing** — a docstring saying 69 of 78, a comment
saying 67/60, and the assertion saying 68/61, which is what the checker prints.

## V — What was deliberately not done

- **The other four raw-kit reads** — `compose.ceiling_heights` (**85 styles** state a figure only
  through the cascade and compose at the 9.0 ft default), `compose.canonical_choices` (~30 fewer
  declared slots per style), `corpus.slot_detail`, and the `window_reveal` pair (0 live). A
  ceiling height is the elevation's governing datum; moving it on 85 styles moves every drawn
  sheet and every score those styles produce, and that wants a published diff, which is what a
  package is for. `oq/the-raw-kit-read` carries the table and names the one-accessor fix.
- **`pueblo-revival`'s `clay-tile-barrel`.** Binding `roof_material` on
  `spanish-colonial-revival` propagated a red barrel tile canonical onto a style whose record
  reads *"Flat roof drained through projecting canales behind an irregular, gently undulating
  parapet"*. Not a regression in severity — the value it replaced was French Baroque `slate`,
  also wrong — and left standing rather than patched, because patching instances one at a time is
  what `oq/a-kit-binding-propagates-to-descendants-nobody-read` exists to stop.
- **`_head_radius_in`'s latent 0.0** for a curved wood head on a frame wall: measured at **0 live
  instances** across all 164 styles, and pre-existing in main's code.
- **The `silent` state in `_judge`**: behaviour preserved from main, measured at **0 occurrences**
  across 164 styles.
- **Nine nodes that state their construction in prose with an empty variant list** — already a
  named finding in the WP-8.4 report, and closing it means authoring nine records, not fixing a
  reader.

## VI — A correction to this report's own title

**It said "WP-8.1 through WP-8.5" and there is no WP-8.5.** The plan named one — OQ 89's
withheld measurements and the `total_shutter_leaves` constant — and that work shipped as
`6f9e7c7`, under its OQ id, before the WP-8 numbering existed on this branch. It has a commit
and a closed question and never had a number, so the series is 8.1, 8.2, 8.3, 8.4, 8.6.

It is worth recording where it is rather than quietly deleting a digit, for two reasons. The
commit message of `2601c0e` carries the wrong range and is pushed, so it cannot be corrected —
the same constraint OQ 90 records for `f768c02` and `426ed35`. And the defect is this report's
own subject arriving in this report's own title: **a range stated in prose, that nothing checks,
naming a package that does not exist.** `check_ids.py` holds a report's filename to its id and
`test_open_question_ids.py` holds every cited report PATH to a file that resolves; neither can
see a package named only in a sentence. Found when a pull request's generated summary listed
"WP-8.5: (implied in the series)" and the series was checked.

## VII — What this says about the discipline

Every one of the eight blockers was a case of **something claiming to have been checked**. Two
were guards that could not fire; two were readers pointed at the wrong record; two were verdicts
that stated a precondition had not been read as though there were none; one was a contract broken
by a branch added beside it; one was a table read through a renamed key.

The corpus's own rules caught none of them, and its rules are the reason each was findable: the
four-state discipline is what makes "granted, no precondition" a detectable lie; "unjudged is not
passed" is what makes a ratchet reading 0 a defect rather than a triumph; "sweep all 164 styles"
is what turned two shipped plans that gain nothing into 22 that gain a true finding. **The rules
work and the checking of them did not**, and the difference between those two is the whole of
what an adversarial pass is for.

One thing is worth carrying forward as a rule rather than a story: **three of the four worst
findings were invisible to both shipped reference plans.** `plan_check`'s blind spot, `roof.py`'s
chimney, and the elevation's reveal all produce byte-identical output on
`spec-builder-colonial` and `tidewater-georgian-careful`. CLAUDE.md has said since WP-5.13 that
verifying on the plans that ship is verifying on 2 of 164 styles. It is not a caution. It is the
single highest-yield technique in this repository, and it found all three in seconds.

## Verifying

```
python3 build/check_all.py                                  # every check, then the three suites
python3 -m pytest tests/test_forbidden_slots.py             # 18, incl. the two cascades agreeing
python3 -m pytest tests/test_construction_scope.py          # 44, incl. the licence self-refusal guard
python3 -m pytest tests/test_citations.py                   # 22, incl. the three end-to-end gates
python3 -m pytest tests/test_open_question_ids.py           # 13, incl. the CI gate's own shell
python3 build/check_inheritance.py --forbidden --strict     # 776
python3 build/check_addresses.py --strict                   # kit_vs_pack 1231, baked_vs_refused 32
```

New open questions: `oq/the-raw-kit-read`,
`oq/a-kit-binding-propagates-to-descendants-nobody-read`,
`oq/a-material-neutral-assembly-decides-a-material-question`,
`oq/a-licence-conditioned-on-the-wrong-axis`.
