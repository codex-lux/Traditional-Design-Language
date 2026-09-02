# WP-9.7 — The checker that must not say "agrees"

*2 Sep 2026. Builds `oq/a-grouping-rule-and-a-room-record-can-disagree`, ruled the same day as
shape (1). Cite reports by filename, never the bare WP number (OQ 90).*

## The measurement that changed the package before a line was written

The register entry says its checker "catches all six above except the keeping room" — five of six.
Measured against the tree first, that claim does not survive:

| # | instance | grouping side | room side | what a band comparison does |
|---|---|---|---|---|
| 1 | passage | 8–14 ft is in the **`statement`**; the `test` measures a *ratio* of another quantity | `width_ft [6, 14]` | **misses it** — the figure is prose |
| 2 | piazza | `piazza_depth_ft at-least 10`, hard | `width_ft [8, 14]` | catches it |
| 3 | bedroom | `bedroom_short_dimension_ft at-least 10`, hard | `width_ft [11, 14]` | catches it |
| 4 | sleeping porch | `porch_depth_ft at-least 8`, hard | `width_ft [8, 12]` — **floors coincide** | **reports AGREES** |
| 5 | keeping room | prose 12 against its own test's 14, one record | — | misses it, by design |
| 6 | ridge pair | one measure spelled twice, both hard, co-carried | — no room, no band | catches it |

**Three of six, and instance 4 is worse than a miss.** `sleeping-porch-cluster`'s 8 and the band's
floor of 8 coincide exactly, so the two executable numbers agree while the record's own
`critical_dimension` says *"NINE FEET OF DEPTH IF THE BED RUNS ACROSS, seven if it runs along"* — a
conditional floor with no axis to be conditional on, which is `oq/register-is-not-style`'s first
customer. A green tick there is this project's founding failure in miniature: every part
well-formed and the whole saying nothing.

So the deliverable was never just the comparison. **The most dangerous output of this checker is
the word "agrees"**, and most of the design below exists to stop that word being unearned.

## What was built

`build/check_grouping_rules.py`, on `check_addresses.py`'s model, registered in `check_all.py`
with `--strict`. `TOTAL_CHECKS` 43 → 44.

**The join is an authored `measures` object**, because nothing could join the two layers: a
grouping test names `piazza_depth_ft` and a room record keys its band `width_ft`, and no grouping
test name matches any band key in the corpus. Schema change required — `internal_rules.items` sets
`additionalProperties: false`. All **26 tested rules of the 84** are annotated (0 carried a
`quantity` or `units` before).

```json
"measures": {"quantity": "piazza_depth", "units": "ft", "room": "piazza", "band": "width_ft"}
```

**`quantity` sits inside `measures` rather than beside it, and that is a deviation from the
ruling's letter with a reason.** Lucas chose the structured form over a bare `quantity` string;
but instance 6 — the ridge pair — measures a *building-level ratio* with no room and no band, so a
`{room, band}`-only field would have lost it. One field carrying both joins keeps the chosen shape
and covers both axes: `room`+`band` joins a rule to a band, `quantity`+`units` joins a rule to
another grouping's rule.

**The pack `units` enum was left alone.** It is closed at `in / parts / modules / ratio / count`,
has no `ft`, and 761 `derived_rules` depend on it. Room bands are in feet, so the grouping layer
got its own enum rather than the pack's being widened to suit a neighbour.

### Three comparisons

**(A) rule vs room band — only the bound the rule actually states.** `at-least 10` claims a floor
and says nothing about a ceiling; comparing whole intervals would report every one-sided rule as
looser than its band and bury three real findings under twenty of the instrument's own noise.
Verdicts: agrees / rule-stricter / rule-looser / cannot-compare.

**(B) rule vs co-carried rule** — for every pair of groupings a parti carries together, rules
sharing a `measures.quantity`, comparing only the ends both state. `cobinding()` one layer out.

**(C) the prose meter** — figures stated in prose that no test or band carries, reported as
uncompared with the sentence quoted. This is the answer to instance 4.

### What it found

```
compared 5 rule(s) against a band and 2 co-carried pair(s); 3 band disagreement(s),
2 co-carried disagreement(s); 22 rule(s) and 35 prose figure(s) COULD NOT BE COMPARED
-- which is not agreement.
```

**The three band disagreements are the register's instances 1, 2 and 3**, and they are the
deliverable rather than a debt:

- `centre-passage-core[2]` floor **8** against `centre-passage`'s band floor of **6** — rule-stricter
- `piazza-and-single-house-core[1]` floor **10** against `piazza`'s **8** — rule-stricter
- `secondary-bedroom-cluster[0]` floor **10** against `bedroom`'s **11** — rule-**looser**, the
  opposite direction, on the grouping 14 partis carry

**The ridge pair is TWO co-carried disagreements, not one.** The register recorded a single latent
conflict; `five-part-palladian` carries `georgian-service-core` alongside **both**
`dependency-and-hyphen` and `garage-and-hyphen`, so `dependency_ridge_to_main_ridge` disagrees at
0.8 against 0.85 on two grouping pairs. Latent only because 0.6–0.8 is a subset of ≤0.85.

**And the prose meter found a third statement of the keeping room's radiant reach.** The register
recorded two — the grouping's prose reasoning to 12 ft and its own test admitting 14.
`rooms/keeping-room.json` says *"THE RADIANT REACH OF THE FIRE, AND IT IS 10 FT"*. **Three numbers
for one measure, and the entry that was audited twice found two of them.** Nobody knows the true
count because nothing counted them; that is now one command.

## The one authoring change, and the one this package refused

Per the ruling — author a test only where the room record has a comparable band — that is **exactly
one rule**, added to `groupings/centre-passage-core.json`: `passage_width_ft between 8 and 14`,
carrying the same statement's own figure and its own reason. No number is invented; the standing
rule permits precisely this (*"making a rule executable adds a `test`; it does not replace the
human-readable `statement`"*). Its floor of 8 then meets the band's 6 and **instance 1 surfaces**.

**Refused: rewriting any existing test.** Turning the piazza's `at-least 10` into `between 10 and
14` to make its prose ceiling executable would change what `plan_check` convicts on live plans —
a generator change wearing an authoring hat.

**Refused: binding `mudroom_clear_width` to `rooms/mudroom.json`'s `width_ft`.** The register held
it back on the grounds that "clear width" may be a different quantity from the band's nominal
width, and reading the rule confirms it: *"not less than 5 ft **where it is also a passage**"* — a
conditional with no axis. It is annotated and reported uncomparable, which is the honest state.
Worth recording that the record's own prose says *"DEPTH ACROSS THE BENCH, AND IT IS 5 FT, NOT 4"*
against a band floor of **6**, so the grouping agrees with the room's prose and disagrees with the
room's band. A seventh instance of the class, in the file the register declined to claim.

**Not asserted: the candidate seventh** the plan flagged. `piazza-and-single-house-core`'s
`principal_ceiling_ft at-least 11.5` against `rooms/piazza.json`'s `ceiling_min_ft: 10` looks like
instance 2's shape, but "principal-floor ceiling" is a storey quantity applying to every room on
that floor, not the piazza's own band. Binding it would have manufactured a finding by asserting an
identity nobody has established. Annotated with a quantity and no room.

## The guards, and the mutation that did not land

`tests/test_grouping_rules.py`, 14 guards. **Seven mutations, each asserted to have LANDED before
the colour was believed, each red:**

| mutation | guard that fired |
|---|---|
| `stated_bounds` invents a ceiling for `at-least` | only-the-stated-bound |
| a rule with no `measures` is skipped silently | unjudged-is-not-agreement |
| units converted instead of refused | units-never-converted |
| the prose meter loses its number-word branch | reads-a-figure-in-WORDS |
| co-carried comparison looks only within one grouping | the-ridge-pair |
| **the piazza band floor edited to make the check green** | the-register's-instances |
| a `measures` annotation deleted from the corpus | the `compared` FLOOR |

**The harness caught itself first, which is why it is worth describing.** The sixth snippet matched
**zero** times — `rooms/*.json` nests at a different indent than `groupings/*.json` — and a harness
that only ran the test would have printed green and been read as "the guard is fine". That is
WP-9.6's finding recurring inside the tooling written in response to it. Assert the mutation
landed; never infer it from the colour.

**Two guards exist only to stop a silence being misread.** One asserts the sleeping porch's band
comparison *agrees* and that the prose meter carries its NINE FEET anyway — two meters, one
instance, so the next reader cannot take the agreement for a clean bill. The other is the
`compared` **floor**: deleting an annotation makes every ceiling look better because the instrument
stopped looking, which is the one way a may-only-fall ratchet lies. `check_addresses` guards the
same hole by failing on a node that would not resolve.

## The prose meter was rebuilt after its first version failed at its one job

The first version scanned digits with any unit suffix, returned **50** figures of which roughly 45
were inch-steps inside an arithmetic derivation (*"a queen mattress is 60 by 80 … you need 24 in
clear"*), and **missed the sleeping porch's NINE FEET, because it is spelled in words.** An
instrument that buries its signal in its own noise and then does not contain the signal is worse
than none, because its output is a number rather than a green tick.

Rebuilt to read the band's own units, digits and number-words both, and to quote the sentence the
figure sits in: **35 figures**, and the signal is legible — the passage's *"SECOND NUMBER: 5 ft 6 in
is the floor"*, the piazza's *"the measured Charleston piazzas run 8 to 12 ft"*, the bedroom's
*"9 ft 0 in clear width, and that is the ABSOLUTE floor"*, and the sleeping porch's nine. It still
overcounts and says so: a rule's prose legitimately states a band ceiling where its test states
only a floor. **Ratchet it down by authoring a figure into a test — never by tightening the regex
until the number looks better.**

## Ratchets

Five ceilings that may only fall and one floor that may only rise, every one measured on the first
run rather than inherited: `rule_vs_band` 3, `rule_vs_rule` 2, `unit_splits` 0, `uncomparable` 22,
`prose_uncompared` 35, **`compared` 5 as a FLOOR**. Each carries its own comment in the source
saying what it means, because two of them are supposed to be non-zero: the three band
disagreements are the deliverable, and the 22 uncomparable are mostly correct and permanent — a
building-level quantity has no band to be held against, and binding one to a band it does not mean
would be the OQ 48 error in a new place.

## What was deliberately not done

- **No number reconciled.** Three of the six have a source on one side only and it is not
  consistently the same side — the piazza's evidence is on the *room record* and the grouping rule
  demanding 10 ft has none. The ruling says the disagreements go to an architect.
- **No existing test rewritten**, and no second parser: `arrangement.parse_rule_test` is called,
  per its own *"ONE PARSER, and it lives here"*, with a source-reading guard.
- **The keeping room's internal disagreement stays open** — now known to be three-way, not two.
- **No general vocabulary check on `quantity` names.** `build/constraint_vocabulary.py` is the
  model if one is ever wanted; 26 free-text names did not justify it, and `porch_depth` was
  deliberately spelled to match the pack quantity that already exists nine times.
- **No generator change.** Neither placement engine is touched.

## Neither WP-9.6 nor WP-9.7 has a section in `PLAN-OF-ACTION.md`, and that is not a missing report

Both were ruling-driven rather than planned: Lucas ruled and the work followed the same day.
Recorded here because **WP-8.6 exists entirely because a package with no plan section was read as
a missing one** — there is no WP-8.5 and the gap is deliberate, and the audit's own report then
claimed a range it did not cover. A number with a report and a commit and no plan section is
complete. What this package DID correct in that file are two Status lines that had frozen at the
moment they were written: WP-9.3 said "NOT STARTED" while its own body recorded WP-9.6 building
item (a) and withdrawing item (b), and WP-9.5's said "24 findings, 8 blocking, four of seven
auditors still reporting" against a finished run and its own report's 42 and 10 — the 8 being
WP-8.6's figure, one package over.

## New open question

`oq/a-room-records-prose-states-a-floor-its-own-band-does-not`. The demonstrated instance is
`rooms/centre-passage.json`, whose prose says *"SECOND NUMBER: 5 ft 6 in is the floor"* against a
band starting at 6. 35 prose figures are uncompared and **the meter cannot tell a governing floor
from an arithmetic step, a cited measurement, or a deliberate two-tier statement** — `bedroom`
names a 9 ft absolute floor and an 11 ft real minimum and bands the 11, which is the record doing
exactly what it should and would be a false positive for any tightening of this meter. Four jobs,
one syntax; that is why it is a question and not a patch.
