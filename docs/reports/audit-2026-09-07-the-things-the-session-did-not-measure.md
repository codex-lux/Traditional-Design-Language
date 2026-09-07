# The adversarial audit of WP-11.9, WP-11.10 and WP-11.11 — the things the session did not measure

*7 September 2026. Four read-only auditors in isolated passes, none of them the agent that wrote
the code, over `git diff 2f91579^ HEAD` plus the uncommitted tree: WP-11.9 (the compass), WP-11.10
(the depth floor), WP-11.11 (the generated Part VI), and the digest correction between them.*

Lucas asked for an attempt to find what is wrong with the work rather than a re-read confirming
it. The four angles were edge cases and every consumer of anything changed; whether each new test
would fail if its fix were reverted; second-order risk (security, cost, performance, data loss);
and second occurrences of each bug pattern elsewhere in the tree.

**Thirty-eight findings. Twenty-four fixed here, fourteen deferred with a reason apiece.** Two
blocked deployment and both were crashes in code written to be the guard against exactly the
malformation that crashed it.

---

## I. The two that blocked

### 1. The guard for the sixty new records died on the malformation it exists to catch

`build/check_rooms.py` validates every `daylight.aspect` object added by WP-11.9. Its verbatim-quote
check read `asp.get("basis") not in (orient or "")`, and **`None not in "some string"` is a
`TypeError`, not a `False`**. Measured, with the aspect mutated on `rooms/library.json`:

| mutation | before | after |
|---|---|---|
| `basis: null` | `TypeError` | reported |
| `basis` absent | `TypeError` | reported |
| `aspect: "N"` (not an object) | `AttributeError` | reported |
| `orientation` a list | wrong-shaped membership test | reported |

`check_room` runs **unconditionally after** schema validation — the caller's loop gates only on
`id`, `function_class` and `privacy_rank` — so a record the schema would have rejected killed the
whole checker process instead of printing the schema error beside the other 59 records. A checker
that dies on bad data reports nothing about the good data either, and this one runs inside
`check_all.py`.

### 2. `compass.read` raised `KeyError: 'basis'` out through `plan_check.check()`

Subscripted on all four judged paths. The schema requires the field, so no corpus record can be
missing it — but `plan_check.check()` is called as a LIBRARY by `critique.py` and `compose.py`,
neither of which validates, and one absent key would have aborted the validation of **every plan
using that room type**, inside a per-candidate compose loop whose own comment records that it has
no guard.

Fuzzing the three new entry points with 18 hostile values found **30 unhandled exceptions**; all 30
now return a verdict. Beyond the two above: a non-numeric `street_bearing_deg` (`ValueError` out of
`float()`), `windows` as a bool/int/string, a window `wall` that is not a string, and an aspect
token outside the eight points (`KeyError` in `POINTS`).

**The block's own "KeyError rather than `.get` ON PURPOSE" comment did not cover any of this.**
That note is about the CENSUS, where a verdict the file grew and the caller did not know about must
be loud. It is not about a data field a schema already polices — and the two had been conflated.

Three of the fixes are four-verdict decisions rather than defensive shrugs:

- **An unplaceable token refuses the whole reading**, in both directions. Dropping it would
  silently weaken an `avoid` (flattering) and silently strengthen a `prefer` (convicting), from
  one bad character.
- **`applies: true` naming neither a prefer nor an avoid is `unjudged`**, not `satisfied`. It had
  been reaching `satisfied`, which makes an empty reading indistinguishable from a room that
  really does take the light its record asks for.
- **A face on a sector boundary is `unjudged`.** `matches` uses `<=` at both ends, so a plan turned
  exactly 22.5° puts a face in a wanted sector and an avoided one at once; the first version
  resolved that by branch order, convicting the house on a coincidence of the tolerance.

---

## II. The finding of the audit: a checker's verdicts entered the composer's fitness function

The aspect findings are `serious` and `minor`, not `info`. `compose.SCORE_LAYERS` already maps
`daylight` to the 18-point `rooms` axis. **So the composer began ranking houses on the compass the
day WP-11.9 landed, and that report does not contain the words *score*, *compose*, *rank* or
*key_of*.**

Rooms axis, out of 18, on the sixteen shipped plan records:

| plan | aspect findings | without | with | delta |
|---|---|---|---|---|
| `good-05-lobby-gallery-mansion` | 8 | 0.8056 | 0.6389 | **−3.00** |
| `tidewater-georgian-careful` | 9 | 0.5600 | 0.4400 | −2.16 |
| `good-04-rambling-porch-farmhouse` | 3 | 0.5769 | 0.4615 | −2.08 |
| six others, `spec-builder-colonial` among them | 2–5 | | | **0.00** |

And on a real compose at 8 candidates, with the term firing 719 and 510 times:

| brief | winner | order below it |
|---|---|---|
| `family-georgian` | unchanged | **positions 3 and 4 swap** |
| `bungalow-small` | unchanged | **positions 4–7 reshuffle** |

It re-ranks. Not reverted — it reads the DECLARED record, every candidate is judged under the same
north, and plan-N-is-true-N is a ruling — but the ruling was taken about a CHECKER, which reports,
and this is a fitness function, which decides, on a site fact 0 of 16 records state.
`oq/the-composer-ranks-on-an-assumed-bearing` carries the question, the numbers, and the three
things that must not be done to close it.

**And the first measurement of all this read 0.00 everywhere.** `plan_check` reaches `compass`
through its own `_load`, which delegates to a `modcache` imported inside that function; a harness
loading `modcache` with raw `importlib` gets a SECOND cache and a second module object, so
monkeypatching `compass.read` there patched nothing. Zero deltas are indistinguishable from an
inert term, and the reading was believed once before the assertion `after == 0` was added. The
repo's own *a mutation that silently does not apply looks exactly like a guard that works*, met in
a measurement rather than in a test. `tests/test_compass.py` now asserts the suppression bit before
reading any delta.

---

## III. Both new passage variables read the flattering way

In `build/arrangement.py`, three statements below a comment reading *"reporting the best would be
the flattering direction, which is the OQ 52 family"*:

- **`passage_ends_with_a_door` counted DOORS**, against a rule whose own `measures.quantity` is
  `passage_ends_reached`, and accepted any threshold-class room whether or not it had a way out.
  Two doors into one porch scored 2.0; a porch plus a landlocked vestibule scored 2.0. False passes
  on a `hard` rule. Both driven cases read 1.0 now; the shipped record is unmoved at 2.0.
- **`stair_hall_opens_off_the_passage` took the BEST of several halls**, so a principal stair off
  the passage excused a service hall reached only from the dining room. **`min` is not the fix**:
  a service stair that does not open off the passage is correct in a house of this kind and this
  model cannot tell one from the other. Where the ground-floor stair halls disagree the variable is
  WITHHELD and the rule reports unjudged naming the variable it could not get.

The count half is also a **necessary and not a sufficient** condition, and that is a property of
the layer rather than a shortcut: a door's `wall` and `position_ft` are solver output and only its
`to` is authored, so a declared record can say a passage reaches outdoors twice and cannot say those
reaches are at its two ENDS.

---

## IV. A finding's identity moved when a sibling cleared

`Findings.add`'s docstring says a finding's identity is WHAT IT IS ABOUT — and it was the one reader
in the tree not looking at `kind`. Two findings of different kinds about one room in one layer were
separated only by an insertion ordinal.

Driven: shrink `backhall` until its depth finding clears, and the aspect finding beneath it —
unchanged in every respect — moved `daylight:backhall#1` → `daylight:backhall`. `PlanWorkbench.jsx`
diffs on `f.id`, so the bench reported a row cleared and a new one opened for a finding nothing had
touched. The same mechanism churned six ids at WP-11.9's merge, for rows whose statements were
byte-identical either side.

Putting `kind` in the key fixes it — ordinal-suffixed ids **472 → 395**, 0 collisions, longest id
66 characters — and **it was built, measured, and then reverted, because the full build caught it
breaking a stated contract.** `tests/test_critique.py::test_the_finding_id_is_unchanged_by_the_
evidence_it_carries` says, citing OQ 32:

> an id is what a finding is ABOUT. Evidence rides beside it and must never enter it, or every
> citation and every open/cleared diff breaks on a number.

and lists `kind` among the evidence, beside `need_ft`, `have_ft`, `axis` and `item`. Changing a
pinned contract on one session's reading is precisely the move this audit criticises WP-11.9 for
making to the composer's score, so the change came out rather than the test being re-pinned. It had
a second measured cost besides: finding ids expressible as a `finding:<id>` citation fell **55 → 12
of 1,620** (§VII½), because each new segment adds a colon the grammar excludes.

**What survives:** the twelve grouping `F.add` calls keep the `kind` they gained — useful, and it
enters no id — and the defect is written down with its measurement in
`oq/a-findings-ordinal-is-not-an-identity`, which asks the question the test does not draw: is
`kind` evidence, or identity? `need_ft=10.667` moves as the plan moves and is plainly evidence; a
`kind` is a closed vocabulary naming what sort of finding this is, and does not change while the
finding is the same finding.

---

## V. The performance finding, which is pre-existing and larger than everything above

`app._plan_validator` compiled the plan validator at the door and its docstring records why:
*"60.5 ms per call rebuilding it, 3.7 ms with it compiled — 17.9% added to the bound route… the
`copy_json` lesson in the other direction."*

**The lesson stopped at the door.** `core.check_plan`, `core.critique_plan` and `core.revise_plan`
each still called `jsonschema.validate(instance, schema)`, which rebuilds the validator every time.
Measured here, same interpreter, on the SOLVED record `evaluate()` actually passes (32,389 B):

| | ms |
|---|---|
| `jsonschema.validate` (`core.check_plan`) | **79.1** |
| compiled `iter_errors` (`app._plan`) | 4.2 |

So `/api/plan/evaluate` validated the same document twice, once compiled and once not — **23% of
the whole server's measured 338 ms bound, spent re-deriving a verdict it already had.** That dwarfs
everything WP-11.9 added by two orders of magnitude: the aspect block itself is **0.226 ms, 0.067%**
of that budget.

`core.validator(name)` is the one compiled spelling now; `app._plan_validator` delegates to it, and
`corpus.invalidate()` clears it. **The walk-the-module cache guard demanded that on the first run,
naming the new cache** — the fourth time it has earned itself.

---

## VI. Tests that could not fail

Eleven were found. The sharpest:

- **`test_every_grouping_rule_speaks` did not.** Its docstring said *"deleting the widened branch
  sends 28 of them quiet again and this is what notices."* Every count in it was read out of
  `groupings/*.json` — a census of the DATA, independent of `plan_check.py` — the `"silent": 0` key
  was never incremented on any path (a literal tautology on the word the test was named after), and
  the source-substring assert beside it **passes with the f-string intact and the branch reverted,
  on exactly the mutation it claimed to catch.** It is behavioural now: count the hand-offs the
  checker EMITTED against the testless rules the named groupings carry, with a precondition
  asserting the fixture contains a non-hard rule so the revert is visible at all. Mutation-checked:
  restoring `elif hard` fails it with "0 of 3 testless rules were handed to a reader".
- **The two re-pinned digests were recorded, not proved.** The docstring accounted for every row of
  the movement — `+9/+5` aspect, `+1/+1` census, `+8/+7` grouping, `−2` each — and **not one of
  those numbers was asserted.** A hash pin cannot tell "the 16 rows I accounted for" from "14 I
  accounted for plus 2 I did not". The row total and a per-layer histogram are pinned beside it now.
  The `info` half — the `elif hard` widening — had been pinned by no count anywhere in the suite.
- **The `check_rooms.py` validator had no test at all.** 44 lines of new production guards; deleting
  the whole block left `check_rooms.py` at `OK errors=0` and the suite green, because four of the
  five rules were re-implemented as direct assertions over `rooms/*.json` — guarding the corpus, not
  the checker. Nine driven tests now run `check_room` on a fixture; deleting the block gives
  8 failed.
- **`test_the_placer_does_not_read_it`** guarded three files by substring and could not see a
  transitive import: `geometry.py` loads `plan_check`, `openings`, `check_openings`, `structure` and
  `geometry_cp`, none of them guarded. It runs a solve and asserts `depth_floor` is in neither
  `sys.modules` nor modcache, plus a source allow-list over every `build/*.py`.
- **`test_the_foundation_constant_matches_structures` guarded a constant that decides nothing.**
  `depth_floor` transcribed `DEFAULT_GRADE_TO_FIRST_FLOOR_FT` under a comment saying the
  transcription was guarded, and **nothing in the module read it, because the constant cancels**:
  `structure.roof_heights` adds it and `elevation.py` subtracts it. Two 2.0s compared. The constant
  is deleted and the IDENTITY is tested instead — run both sides and hold the difference against
  `wall_height_ft`. Mutation-checked: breaking the cancellation turns it red, where the old test
  could not.
- **`test_a_north_library_is_clear`** was `assert _kinds(...) == []` with nothing beside it; every
  mutation that silences the aspect block yields `[]` for every plan. Three of the four `== []`
  tests in that class had a positive assertion beside them and this one did not.
- **`assert serious == 1`** was justified in its own comment by naming a plan and a room and checked
  neither, so any regression making a different room hard-serious while `good-04`'s stopped firing
  kept it green. The identity is asserted.
- **`assert (agree, disagree) == (2, 0)`** — `disagree` was never incremented, because the loop
  asserted instead of collecting. Half a tautology, and the first disagreement stopped a sweep whose
  point is how many there are.
- **`test_it_reproduces_the_between_branch`** said it was driven and globbed the shipped corpus,
  `pytest.skip`ping if `between` disappeared — a skip is a silent pass — then asserted an agreement
  the test above it already asserts over all 164 styles. It writes its own style record now and
  asserts the ARITHMETIC (a band of 6 to 10 reads 8.0). Agreement proves consistency; only an oracle
  proves correctness.
- Three more in `test_parti_prose.py`: a subset assertion that held by construction of the test's
  own input; a doc-literal compared against the same literal in this file; and a test named
  *"every room type states an aspect"* whose assertion was about the block's length and held whether
  or not one of the twenty stated an aspect. All three now assert what their names claim.
- `_kinds`' selector was `startswith("room-o")` — a prefix over an OPEN namespace, one letter from
  `room-without-a-hearth`. The two kinds are named.

---

## VII. Second occurrences of this session's own bug patterns

An auditor swept the tree for each pattern. **Its headline is worth quoting: of everything it
found, nothing was introduced by this session.** The two acted on here:

- **`mcp_server/core.check_style_constraints` dropped 125 of 660 constraints** — the identical
  `if not test: if hard: … continue` narrowing WP-11.9 fixed in the grouping layer. 98 soft and 27
  advisory constraints landed in none of `present` / `clear` / `could_not_judge` / `judgment_only`
  and in none of the summary counts, **while the function's own docstring and its returned `note`
  said *"the rest… come back under judgment_only rather than silently ignored"*.** A false claim in
  a note about a check that was not happening. A fifth list, `not_migrated`, now takes them; the
  worst unaccounted constraint on any of the 164 styles is **0**.
- **`plan_check.py`'s arrangement fold-in was a bare `except Exception: pass`** — sixty lines below
  the same file's own condemnation of that construct by name. It supplies the variables 28 faults
  read, so a throw turned 28 faults into unjudged-for-missing-measurements with nothing saying the
  measurement layer had fallen over: a real failure wearing the face of a corpus gap. It emits an
  `info` naming the exception; driven, and it fires.
- **`structure.py`'s 20 ft timber-frame span cap carried a false citation.** The comment said the
  figure came from `module.default_size_in`'s range; `proportions/modules/timber-bay.json` states
  `default_size_in: 192.0` and no range as data. The 240 in exists in one place in that record —
  inside the TEXT of an invariant. So the number deciding whether every timber-framed floor span in
  the corpus passes was lifted out of an expression string and described as reading a field that
  does not exist. Still transcribed (parsing bounds out of invariants would be a second expression
  reader beside `proportion_engine`'s), but **guarded**: a test reads that invariant and fails if
  the pack's bound moves. Mutation-checked at 216 in.

---

## VII½. And one the auditors did not find, chased out of the id fix

Putting `kind` into a finding's id raised the obvious next question — is a finding id citable at
all? It is not, and it was not before:

| | citable as `finding:<id>` | of |
|---|---|---|
| as shipped (and after the revert below) | **55** | 1,620 |
| under the reverted `kind`-in-the-id change | **12** | 1,620 |

`ID_CHARS = "A-Za-z0-9_.-"` in all three spellings of the citation grammar, and **`:` is not in
it** — while `Findings.add` joins every id with `:`. So `adjacency:great-room` has never been
citable, and the twelve that are are the plan-wide findings whose id is one bare segment. The
grammar carries a `finding` kind that routes correctly the moment an id reaches it, and no id can.

**Pre-existing, and it is one of the two reasons the `kind`-in-the-id change came back out** —
3.4% citable would have become 0.7%. The tree ships at 55. Widening `ID_CHARS` is a change to three spellings held together by `test_grammar_agreement.py` —
which exists because an audit once found two of them disagreeing about a dot — and it would make
`style:craftsman:junk` parse on every kind. That is a grammar ruling, not an audit fix:
`oq/a-finding-citation-cannot-name-a-finding`.

---

## VIII. Deferred, with reasons

| # | Finding | Why not fixed here |
|---|---|---|
| 1 | `plan_check`'s STYLE layer has the same `if not test: if hard` narrowing as the grouping layer | PRE-EXISTING and **disclosed in its own comment** ("only a hard constraint gets a check-by-hand note"). Widening it changes the finding set on all 164 styles and belongs in a package with its own measurement, not in an audit. The two layers of one file now disagree about what silence means, and that is recorded rather than resolved. |
| 2 | A 45°-rotated house matches neither neighbouring cardinal, so a SW drawing room fails a record wanting "south and west" | Correct behaviour under the eight-point compass the records are written in, and **unreachable**: 0 of 16 plans state a bearing. Widening `SECTOR_TOL_DEG` to lower a count would be tuning the instrument, which `oq/no-plan-record-states-its-bearing` already forbids. The rotation IS printed in the assumption sentence, so a reader is told. |
| 3 | `_axis_canon` reports "23 could not be evaluated" against `of: 10` | PRE-EXISTING grain mismatch: `of` counts each grouping once, `unjudged` counts internal rules. Recounting `of` per rule would re-rank every brief — a scoring decision, not an audit's. Clamping would discard the count, which is the flattering direction. Published with `unjudged_of` naming its population; `oq/the-canon-axis-counts-two-grains-as-one`. |
| 4 | Twelve fields the corpus states that nothing reads — `faults.detection` on **210 of 210**, `rooms.servicing.electrical` and `stack_proximity_ft` on 60 of 60, `groupings.servicing_strategy` on 17 of 17 | Real, and exactly the `daylight.orientation` shape WP-11.9 was about. `faults.detection` is the largest instance in the tree. This is a work package (or four), not an audit fix; recorded here so the next reader starts from a census rather than a hunch. |
| 5 | `roof.py`'s gambrel constants bypass its own `_fallback_band` ledger | PRE-EXISTING, one screen from the instrument built to record exactly this. Worth a package. |
| 6 | Four more transcribed band literals (`HYPHEN_DEFAULT_FT`, `WING_RIDGE_RATIO_DEFAULT`, `compose.py`'s garage `bay_w`, `resolve_kit`'s `AUTHORING_CEILING`) | PRE-EXISTING; each needs a reader or a guard, and the timber cap above is the pattern to follow. |
| 7 | `structure.stair_geometry`'s one refusal message for three causes | PRE-EXISTING; the same shape WP-11.4 fixed in `flue_walls`. |
| 8 | Two latent collapses in `core.py` (`"silent"` verdict dropped; `include_needed=False`) | Verified UNREACHABLE today — 210 of 210 faults are accounted for, and no caller passes `include_needed=False`. Holes waiting for a sixth scoped test, not live defects. |
| 9 | Response size +9.5% on the largest plan; nothing caps findings anywhere | PRE-EXISTING and mildly worsened. A cap is a product decision (`oq/a-room-count-cap-on-the-heavy-routes` is its sibling). |
| 10 | `tests/test_depth_floor.py` uses raw `importlib` rather than modcache, and pins `unjudged == 14` over a glob | The pins are the deliverable of WP-11.10 and adding a plan SHOULD make someone re-read them. The loader costs 466 ms at import and is the idiom in 26 of the 59 test files. |
| 11 | `test_the_shipped_corpus_reads_as_published`'s 40/23 aggregate can be satisfied by a mis-assignment that conserves the totals | Partly addressed — the one `serious` now asserts its plan and room. A full per-plan pin is a 16-row literal that would go red on any authoring change, which is WP-9.6's rule about ratcheting a number that drifts. |

---

## IX. What this pass says about the three packages

The code WP-11.9 through WP-11.11 shipped is sound in what it computes: the compass reading, the
depth-floor inversion and the generated Part VI all survived the audit with no arithmetic defect
found. What did not survive is what the packages **said about themselves**. A report that measured
sixty room records and never mentioned that its findings enter a fitness function; a docstring that
said a test noticed a revert it could not see; a comment claiming a transcription was guarded when
the guarded value decides nothing; a note citing a field a record does not carry. Four different
files, one shape — **a claim about a check, standing in for the check.**

That is WP-8.6's finding (*"every one was something CLAIMING to have been checked"*) arriving three
phases later in this session's own work, and the technique that found all of it is the one this tree
already records: **re-derive the number, do not re-read the sentence.** Not one blocking finding
here came from reading. The two crashes came from running the guard against bad input; the score
movement came from suppressing the term and re-running; the blind tests came from reverting the fix
and watching the suite stay green.

The one new lesson is smaller and sharper: **a measurement harness can fail the same way a test
can.** The first reading of the score movement said 0.00 on all sixteen plans because the harness
patched a module the code under test was not holding — and a zero delta reads exactly like an inert
term. Assert that your instrument moved before you believe what it says did not.
