# oq/a-grouping-rule-and-a-room-record-can-disagree — six instances, one of them on fourteen partis, and nothing checks the class

*Status: CLOSED 2 Sep 2026 · Raised in: the WP-9.2 adversarial audit (1 Sep 2026)*

**`check_addresses.py` polices pack-versus-pack and kit-versus-pack at one address. It does not see
groupings, room bands or fault tests at all.** So a grouping's `internal_rules` test and the room
record it constrains can state different numbers for the same quantity, and nothing in the corpus
notices. Six instances, all found by hand, all pre-existing.

The corpus already has the vocabulary for this problem one layer down: OQ 48 established that *two
records meaning the same quantity under different names is a silent corruption, and the fix is a
named dimension*. Nobody has applied it to the grouping layer.

**The count moved from four to six while this entry was being audited**, which is itself the
argument for a checker: two more turned up in twenty minutes of the same hand method, and the first
instance grew from four statements to seven. Nobody knows the true number because nothing counts
them.

## The six

**1. The passage — seven statements across five files spanning 3.0 to 10 ft, and a fault and a
pack each contradicting themselves.**

| where | what it says | floor |
|---|---|---|
| `proportions/systems/room-vernacular.json` rule 8, `quantity: passage_clear_width` | `range: [36.0, 120.0]` in | **3.0** |
| the same rule's `authority_note` | *"Measured central passages run 6 to 12 ft"* | **6** |
| `rooms/centre-passage.json` `width_ft` | the band | **6** |
| the same file's `critical_dimension` | *"5 ft 6 in is the floor"* | **5.5** |
| `groupings/centre-passage-core.json`, **hard** | *"Passage width 8 to 14 ft … Below 8 ft the stair cannot turn"* | **8** |
| `faults/passage-that-is-a-corridor.json` `test` | `passage_clear_width_ft at-least 8.0` | **8** |
| `kits/georgian-colonial-american.kit.json` `circulation_parti.passage_width_ft` | `[10, 14]` ft | **10** |

The fault's own note reads *"8 ft for a formal centre-passage plan and 6 ft for a northern
vernacular one"* — a conditional its unconditional test cannot express. Any check enforcing 8 ft
convicts the passage the room record calls correct.

**The pack rule is the sharpest of the seven statements and was missed on the first pass.** It
carries `quantity: "passage_clear_width"` — the fault's expression under the same name minus its
`_ft` suffix — so it is the ONE statement `check_addresses.py` can see, and it can only be compared
against other packs. Its stated range floor is **3.0 ft** while its own `authority_note` in the same
object says 6, and its ceiling of 10 ft is exactly the kit's floor: a Georgian passage satisfying
the kit is out of the pack's range at every width but one. Nothing compares them, because one is a
pack and one is a kit parameter under a different name — which is `oq/a-baked-pack-value-is-a-second-delivery-path`'s
neighbourhood and OQ 86's exactly.

**2. The piazza — a hard rule against a record that cites measurement.**
`groupings/piazza-and-single-house-core.json`: `piazza_depth_ft at-least 10`, **hard**.
`rooms/piazza.json`: `width_ft [8, 14]`, and *"DEPTH, AND 8 FT IS THE FLOOR BECAUSE THE PIAZZA IS
A DINING ROOM"*, citing *"the measured Charleston piazzas run 8 to 12 ft for exactly this reason"*.
**A 9 ft piazza is inside the band, inside the cited measured range, and fails a hard rule.** This
is the sharpest of the six, because the record is the side with the evidence.

**3. The bedroom — nine, ten and eleven, on the widest-reaching grouping in the corpus.**
`groupings/secondary-bedroom-cluster.json`: `bedroom_short_dimension_ft at-least 10`, **hard**,
carried by **14 partis**. `rooms/bedroom.json`: band `width_ft [11, 14]`; and its own prose:
*"60 + 24 + 24 = 108 in, a 9 ft 0 in clear width, and that is the ABSOLUTE floor"*. A bedroom at
10.5 ft passes the hard rule and fails its own band.

**4. The sleeping porch — an unconditional rule against a conditional record.**
`groupings/sleeping-porch-cluster.json`: `porch_depth_ft at-least 8`, **hard**.
`rooms/sleeping-porch.json`: *"NINE FEET OF DEPTH IF THE BED RUNS ACROSS, seven if it runs along"*.

**5. The keeping room — a rule's own prose against its own test, with no second record involved.**
`groupings/keeping-room-hearth-cluster.json`: *"The keeping room is within about 12 ft of the fire,
which is the radiant reach of an open hearth. Beyond that the room is not warm and the household
will not use it"* — `test: hearth_to_far_wall_ft at-most 14`. The prose gives a reason for 12 and
the test admits 14, so a room the record says will not be used passes the rule that says so. This
is the sub-class instance 1's fault note belongs to as well: **the executable half and the
human-readable half of one rule state different numbers**, which the corpus's own standing rule
("prose stays beside the test; making a rule executable adds a `test`, it does not replace the
`statement`") makes possible and nothing checks. It is listed here rather than split off because
the remedy is the same — a `quantity` and a comparison — but a ruling could reasonably treat it
separately, since no second record is involved and the fix is a one-file edit rather than a
decision about which record wins.

## Deliberately not claimed as instances

- `contemporary-service-core`'s `mudroom_clear_width_ft at-least 5` against `rooms/mudroom.json`'s
  `width_ft [6, 10]`. "Clear width" may be a different quantity from the band's nominal width —
  which is itself the OQ 48 problem (nothing says whether it is), but it is a naming gap rather
  than a demonstrated contradiction.
- `primary-suite`'s `bed_wall_clear_ft at-least 12` against `primary-bedroom`'s *"THIRTEEN FEET
  SIX"*. A wall run is not a room width.

And one duplication that does not yet disagree: `dependency-and-hyphen` and `garage-and-hyphen`
carry `dependency_ridge_ft / main_ridge_ft between 0.6 and 0.8` and `hyphen_length_ft between 12
and 20` **identically**, and `five-part-palladian` carries both groupings. One rule spelled twice,
agreeing today, with nothing holding the spellings together — which is how the next instance will
start.

## The sixth, which is the same class under different names

`groupings/georgian-service-core.json` carries `wing_ridge_ft / main_ridge_ft at-most 0.85`,
**hard**; `dependency-and-hyphen` and `garage-and-hyphen` carry `dependency_ridge_ft /
main_ridge_ft between 0.6 and 0.8`, **hard**. `five-part-palladian` and `connected-farmstead` carry
both groupings, and on a five-part plan the flanking dependencies **are** the service wings.
The conflict is latent rather than live: `roof.py:348` selects the rule whose test
`startswith("dependency_ridge_ft")`, builds the wing to 0.6–0.8, and names its own local variable
`wing_ridge_ft`. **`georgian-service-core`'s rule is not "evaluated by nothing" — an audit
corrected that** (the sibling report carries the correction and this file did not): `plan_check`
parses it and reports it **UNJUDGED** for want of a supplier, which is the corpus's own discipline
working rather than a silence. What is true is that no supplier exists, so the rule never resolves,
and it is satisfied in practice only because 0.6–0.8 is a subset of ≤0.85. Loosen the dependency
band and they disagree, with nothing to notice.

## BUILT 2 Sep 2026 — and the ruling's own scope claim did not survive measurement

`build/check_grouping_rules.py`, in `check_all.py` with `--strict`; `TOTAL_CHECKS` 43 → 44.
Report: `docs/reports/wp-9.7-the-checker-that-must-not-say-agrees.md`.

**THE SCOPE CLAIM BELOW SAYS THIS CATCHES ALL SIX EXCEPT THE KEEPING ROOM. IT CATCHES THREE, AND
ONE OF THE THREE IT MISSES IS REPORTED AS AGREEING.** Measured before the checker was written:

| # | instance | what a band comparison does |
|---|---|---|
| 1 | passage | **missed as ruled** — its 8–14 ft is in the `statement` and its `test` measures a ratio of another quantity. WP-9.7 authored the figure into a test, per Lucas's second ruling of the day, and it then surfaces |
| 2 | piazza | caught — floor 10 against a band floor of 8, rule-stricter |
| 3 | bedroom | caught — floor 10 against a band floor of 11, rule-**looser**, the other direction |
| 4 | sleeping porch | **reports AGREES.** The rule's 8 and the band's floor of 8 coincide exactly; the disagreement the entry records is with the record's PROSE |
| 5 | keeping room | missed, as the ruling says — and it is **three** statements, not two: `rooms/keeping-room.json` says the radiant reach "IS 10 FT" beside the grouping's 12 and its test's 14 |
| 6 | ridge pair | caught, and it is **two** co-carried pairs rather than one — `five-part-palladian` carries `georgian-service-core` alongside both hyphen groupings |

Instance 4 is why the checker carries a **third meter**: 35 figures stated in prose that no test or
band carries, reported unjudged with the sentence quoted, so that agreement on the two numbers a
machine can see is never read as nothing-to-see. That meter's first version scanned digits only,
returned 50 figures of which most were arithmetic steps, and **missed the sleeping porch's NINE
FEET because it is spelled in words** — the one case it exists for.

**Two of the six therefore remain open in a new entry**, because the remedy is not this checker's:
`oq/a-room-records-prose-states-a-floor-its-own-band-does-not`.

## Lucas's ruling, 2 Sep 2026: (1) — a checker, on the `check_addresses.py` model

**Grouping tests get a `quantity`, and a new check compares every grouping rule against every room
band naming the same quantity, and against every other grouping a parti co-carries.** Catches all
six above except the keeping room's internal one, and ratchets so a seventh cannot arrive silently.
Costs a schema field on 26 rules and one new check (`TOTAL_CHECKS` moves; so does
`tests/test_counts_guard.py`).

**The ruling deliberately does NOT decide a single number, and that is why it was chosen.**
Precedence was refused because it would enforce the unsourced side at least once: the piazza's
room record is the one citing *"the measured Charleston piazzas run 8 to 12 ft"* and the grouping
rule demanding 10 ft has no source at all. The checker's job is to make each disagreement visible
and unjudged, and hand it to an architect.

**So the checker must report three states, never two** — agrees / disagrees / cannot be compared
(no `quantity` on one side). A pair it cannot compare is unjudged and is counted; collapsing that
into "agrees" is the failure this corpus names first. And **`quantity` is not `units`**: OQ 53
records two live wrong dimensions from comparing one without the other.

**What must not happen, restated because a checker makes it tempting.** Do not reconcile any
instance by picking the stricter or looser number to turn the new check green. Three of the six
have a source on one side only and it is not consistently the same side; at least one — the
sleeping porch, arguably the passage — is a conditional floor with no axis to be conditional on,
which is `oq/register-is-not-style`'s first customer and not this checker's to settle.

## The question, as it was put

**Should a grouping rule be checkable against the room record it constrains, and if so how?**
Three shapes, and they are not equivalent:

1. **A checker, on the `check_addresses.py` model.** Give grouping tests a `quantity` the way
   pack rules have one, then compare every grouping rule against every room band naming the same
   quantity, and against every other grouping a parti co-carries. Catches every instance above except the
   keeping room's internal one, and ratchets. Costs a schema field on 26 rules and a new check.
2. **Precedence, on the packs' model.** Declare which record wins when a grouping and a room
   record disagree. Cheaper, and wrong for at least the piazza, where the room record is the one
   citing measurement and the grouping is the one with no source.
3. **Neither — the numbers are genuinely different quantities and the fix is to name them.** This
   is OQ 48's own answer one layer out, and it is probably right for the mudroom and the bed wall.
   It does not help the piazza or the bedroom, where the quantity is plainly the same.

**A ruling is needed before any of it**, because the instances split three ways: some are naming
gaps (fix by naming), some are real contradictions (fix by deciding a number), one is a rule
disagreeing with its own prose (fix in one file), and at least one — the sleeping porch, and
arguably the passage — is a **conditional floor with no axis to be conditional on**,
which is `oq/register-is-not-style`'s first concrete customer rather than a number to pick.

## What must not happen

Do not reconcile any of these by picking the stricter number, or the looser one, to make a checker
green. Three have a source on one side only, and the sourced side is not consistently the same
side — the piazza's evidence is on the room record, the passage's is split between a pack's
`authority_note` and a fault's note, and they do not agree with each other. The corpus's first rule applies: a number authored to settle a disagreement, with
no source, is `editorial` / `judgment: true` and says so in its own note.
