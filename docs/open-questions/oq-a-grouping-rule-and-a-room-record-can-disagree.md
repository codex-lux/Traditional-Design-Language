# oq/a-grouping-rule-and-a-room-record-can-disagree — four instances, one of them on fourteen partis, and nothing checks the class

*Status: OPEN · Raised in: the WP-9.2 adversarial audit (1 Sep 2026)*

**`check_addresses.py` polices pack-versus-pack and kit-versus-pack at one address. It does not see
groupings at all.** So a grouping's `internal_rules` test and the room record it constrains can
state different numbers for the same quantity, and nothing in the corpus notices. Four instances,
all found by hand, all pre-existing.

The corpus already has the vocabulary for this problem one layer down: OQ 48 established that *two
records meaning the same quantity under different names is a silent corruption, and the fix is a
named dimension*. Nobody has applied it to the grouping layer.

## The four

**1. The passage — four floors across four files, and a fault contradicting itself.**

| where | what it says | floor |
|---|---|---|
| `rooms/centre-passage.json` `width_ft` | the band | **6** |
| the same file's `critical_dimension` | *"5 ft 6 in is the floor"* | **5.5** |
| `groupings/centre-passage-core.json`, **hard** | *"Passage width 8 to 14 ft … Below 8 ft the stair cannot turn"* | **8** |
| `faults/passage-that-is-a-corridor.json` `test` | `passage_clear_width_ft at-least 8.0` | **8** |

The fault's own note reads *"8 ft for a formal centre-passage plan and 6 ft for a northern
vernacular one"* — a conditional its unconditional test cannot express. Any check enforcing 8 ft
convicts the passage the room record calls correct.

**2. The piazza — a hard rule against a record that cites measurement.**
`groupings/piazza-and-single-house-core.json`: `piazza_depth_ft at-least 10`, **hard**.
`rooms/piazza.json`: `width_ft [8, 14]`, and *"DEPTH, AND 8 FT IS THE FLOOR BECAUSE THE PIAZZA IS
A DINING ROOM"*, citing *"the measured Charleston piazzas run 8 to 12 ft for exactly this reason"*.
**A 9 ft piazza is inside the band, inside the cited measured range, and fails a hard rule.** This
is the sharpest of the four, because the record is the side with the evidence.

**3. The bedroom — nine, ten and eleven, on the widest-reaching grouping in the corpus.**
`groupings/secondary-bedroom-cluster.json`: `bedroom_short_dimension_ft at-least 10`, **hard**,
carried by **14 partis**. `rooms/bedroom.json`: band `width_ft [11, 14]`; and its own prose:
*"60 + 24 + 24 = 108 in, a 9 ft 0 in clear width, and that is the ABSOLUTE floor"*. A bedroom at
10.5 ft passes the hard rule and fails its own band.

**4. The sleeping porch — an unconditional rule against a conditional record.**
`groupings/sleeping-porch-cluster.json`: `porch_depth_ft at-least 8`, **hard**.
`rooms/sleeping-porch.json`: *"NINE FEET OF DEPTH IF THE BED RUNS ACROSS, seven if it runs along"*.

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
agreeing today, with nothing holding the spellings together — which is how instance 5 will start.

## The fifth, which is the same class under different names

`groupings/georgian-service-core.json` carries `wing_ridge_ft / main_ridge_ft at-most 0.85`,
**hard**; `dependency-and-hyphen` and `garage-and-hyphen` carry `dependency_ridge_ft /
main_ridge_ft between 0.6 and 0.8`, **hard**. `five-part-palladian` and `connected-farmstead` carry
both groupings, and on a five-part plan the flanking dependencies **are** the service wings.
The conflict is latent rather than live: `roof.py:348` selects the rule whose test
`startswith("dependency_ridge_ft")`, builds the wing to 0.6–0.8, and names its own local variable
`wing_ridge_ft`. `georgian-service-core`'s rule is evaluated by nothing and is satisfied by
accident, because 0.6–0.8 is a subset of ≤0.85. Loosen the dependency band and they disagree.

## The question

**Should a grouping rule be checkable against the room record it constrains, and if so how?**
Three shapes, and they are not equivalent:

1. **A checker, on the `check_addresses.py` model.** Give grouping tests a `quantity` the way
   pack rules have one, then compare every grouping rule against every room band naming the same
   quantity, and against every other grouping a parti co-carries. Catches all five above and
   ratchets. Costs a schema field on 26 rules and a new check.
2. **Precedence, on the packs' model.** Declare which record wins when a grouping and a room
   record disagree. Cheaper, and wrong for at least the piazza, where the room record is the one
   citing measurement and the grouping is the one with no source.
3. **Neither — the numbers are genuinely different quantities and the fix is to name them.** This
   is OQ 48's own answer one layer out, and it is probably right for the mudroom and the bed wall.
   It does not help the piazza or the bedroom, where the quantity is plainly the same.

**A ruling is needed before any of it**, because the instances split: some are naming gaps (fix by
naming), some are real contradictions (fix by deciding a number), and at least one — the sleeping
porch, and arguably the passage — is a **conditional floor with no axis to be conditional on**,
which is `oq/register-is-not-style`'s first concrete customer rather than a number to pick.

## What must not happen

Do not reconcile any of these by picking the stricter number, or the looser one, to make a checker
green. Three of the five have a source on one side only, and the sourced side is not consistently
the same side. The corpus's first rule applies: a number authored to settle a disagreement, with
no source, is `editorial` / `judgment: true` and says so in its own note.
