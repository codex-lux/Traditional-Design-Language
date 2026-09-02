# WP-9.5 — The corrections that were themselves wrong: the adversarial audit of WP-9.1 and WP-9.2

*Status: the audit ran on 1 Sep 2026 against `e1f34fb..HEAD`. Seven independent read-only auditors
were dispatched and six returned; their findings are below, and **the corrections they prompted
were then re-audited**, which produced the second pass. Everything below is **found, verified and
fixed**, not reported and left.*

Lucas asked for "a genuine adversarial audit of everything changed — not a re-read confirming your
own work, but an attempt to find what's wrong with it." This is that, and it follows the phase
tradition: `wp-6.4-the-audit.md`, `wp-7.5-the-adversarial-audit.md`,
`wp-8.6-the-guards-that-could-not-fire.md`.

**This file was first named `wp-9.5-the-adversarial-audit.md` and
`tests/test_open_question_ids.py::test_no_two_work_package_reports_share_a_slug` failed the build
for it**, because WP-7.5's report already holds that slug and OQ 90's fallback is *"cite the
report, never the number"* — two reports with one slug distinguish nothing. The guard was written
after `wp-5.8-the-four-rulings.md` and `wp-5.10-the-four-rulings.md` collided the same way. **It
caught this because the FULL suite was run; a subset had passed twenty minutes earlier**, which is
finding B8 below and the reason this report's own verdict was retracted once.

## What was audited, and why a documentation change is not a soft target

The change is ten files and about 1,730 added lines, **all documentation** — two reports, six
open-question files, the generated index, `CLAUDE.md`, `PLAN-OF-ACTION.md` and a download list. No
`.py`, `.js` or corpus `.json` was touched; that was verified by diff rather than asserted.

In this repository that makes the audit *more* pointed, not less. The project's own history is a
list of times prose lied and no test caught it — WP-6.4 found eleven claims in source, schema and
docs that shipped packages had falsified; WP-8.6 found eight blocking defects and every one was
"something CLAIMING to have been checked". A false sentence in `docs/reports/` is a defect of
exactly that class, because the next agent reads these files as fact.

## The headline

**Thirty-five findings survived verification across two passes. Eight were blocking. Every one of
the blocking findings was in work this session had produced, and four of them were in corrections
this session had *already made* — a first fix that was itself wrong, or right in one file and left
wrong in another.**

**The second pass is the more instructive of the two.** Re-auditing the corrections found eleven
more, and **four of those were in the corrections themselves**: the engine rule broken in the
sentence announcing it (S1), a proposed island fix that convicts four of the corpus's own `good`
reference plans (S6), a precedent cited for the opposite of what it is (S7), and a caveat written
about quotations when numbers are what gets reused (S8). The first pass's ratio of
corrections-that-were-wrong held at the second pass almost exactly, which says the rate is a
property of the method rather than of a bad day.

The single most useful result is not any individual finding. It is that **the highest-yield
technique was to re-derive a number rather than re-read the sentence containing it.** Every
blocking finding came from running something; none came from reading. Three of the second pass's
findings (S3, S5, S6) were figures that had been *published* by the first pass and were wrong by
factors of 1.75, 268 and 4.

---

## Blocking — found and fixed

**B1. The bay module was wrong, and correcting it moved a conclusion.**
Hammond-Harwood's ft/bay was printed **8.80**, divided from HABS's *"approximately 44x42'"* by a
source that does not say which of 44 and 42 is the front. A first correction gave 8.4–8.8 to name
the ambiguity. **Both were low**: the Hammond-Harwood House's own institution states *"the actual
house measures 49 feet"*, so 9.80. Observed modules are 9.80, 10.06, 12.17 and the parti's declared
**9 ft is below all three** — not "inside the observed range, at its low end", which is what two
earlier versions said. *Naming an uncertainty is not resolving it, and the comfortable reading
survived two passes.*

**B2. Morris is Palladio at one remove.** Eight places across four files quoted *"the nearer a Room
… is to a Square, the more uniform and commodious they will be"* as **Morris**. The grammatical
subject of that sentence is **Palladio** — Morris is reporting *"Palladio has observ'd, that there
are seven beautiful Proportions"*. So Morris is not an independent English witness and two sources
were being counted where there is one. The argument that no source states a *minimum* is
unaffected; the corroboration is thinner, and every use now says so.

**B3. "Nothing else in the pipeline can make the house bigger" is false** — and it was the newest
and most confident sentence in the report. `derive_footprint`'s loop *is* area-neutral (`H = need /
W`; measured 2,405.0 sf at every bay count from 4 to 10). But **`compose.repair()` widens a room's
declared `width_ft` on a furniture finding and on a width-floor finding**, and since `need` is the
sum of the rooms' `_area`, that grows the footprint on the next pass. The correction is sharper than
the claim: repair reads furniture findings computed from the **declared** record, so it widens rooms
that were already adequate and never sees the one drawn as a sliver.

**B4. The headline furniture figure was engine-dependent and not reproducible.** Published as
"50 of 231 placed rooms — one in five". Re-running gave 48, then 49; the drawn count gave 130, 132,
133. `auto` solves 15 of the 16 plans with CP-SAT under a wall-clock budget, and CP-SAT is not
deterministic under varying load. **`engine="heuristic"` gives 86 and 25, identical on three cold
runs.** No engine had been named at all. *And the engine comparison is a finding nobody had: the
engine that PROVES draws about 131 unfurnishable items where the search draws 86 — it proves what
it is told, and nothing tells it about shape.*

**B5. The ratchet proposal was unsafe, and `CLAUDE.md` then contradicted itself about it.**
Ratcheting a figure that drifts ±3 on an unchanged tree is a build that fails for no reason. The
plan and both reports now say to ratchet the deterministic 86/25. One bullet in `CLAUDE.md` said
both things at once — line 628 the corrected instruction, line 635 the original — because the first
fix stopped halfway down its own paragraph.

**B6. The study's room-shape paragraph contradicted its own enumerated members.** "Maximum 1.464"
and "not one reaches 3:2", against a list that includes Mount Vernon's Central Passage at **2.314**
and a double room at **1.80**. True only of the single non-circulation rooms — which is what "27
single rooms" was reaching for and did not say.

**B7. "29 habitable" is the non-circulation count.** 35 records carry a floor above 1.0, 6 are
circulation, so 29 is *non-circulation*; the habitable figure is 13 of 23, and 16 of the 29 are not
habitable in any sense (bath-house, closet, laundry, scullery…). Corrected in the report and the
open question first, and left wrong in `CLAUDE.md` — the worst of the three places to leave it.

**B8. The audit's own verdict was given on a SUBSET of the test suite, and the full suite then
failed.** After fixing B1–B7 I ran `tests/test_wp46_packs.py`, `tests/test_counts_guard.py` and
`tests/test_citations.py` — the three I judged relevant to a documentation change — got 314 passed,
and declared the work deployment-ready on the strength of that plus an earlier full run. The
confirming full run came back **`FAIL pytest tests/` — 1 of 43 checks failed**, on
`test_no_two_work_package_reports_share_a_slug`: this very report had been filed as
`wp-9.5-the-adversarial-audit.md`, colliding with WP-7.5's slug, and OQ 90's fallback is *"cite the
report, never the number"*, so two reports under one slug distinguish nothing.

Three things worth keeping from it. **The guard was right and I had never run it** — it lives in
`tests/test_open_question_ids.py`, which my subset did not include, and it exists because
`wp-5.8-the-four-rulings.md` and `wp-5.10-the-four-rulings.md` had already collided that way.
**The defect was in the audit's own deliverable**, not in what it audited. And **"the tests I
judged relevant pass" is exactly the reasoning this audit was commissioned to distrust**, committed
in the last five minutes of it, by the person writing this sentence. The verdict was retracted and
re-issued after the full suite.

---

## Second pass — what a re-audit of the corrections found

The corrections above were themselves re-read by a further set of auditors. **Eleven more findings
survived, and four of them are in the corrections rather than in the original work** — the same
result as the first pass, one level in. Nothing here blocks; all eleven are fixed.

**S1. Two `auto` figures survived in the paragraph that announces the engine rule.** B4 fixed the
headline and added the sentence *"Every figure in this section names its engine for that reason"* —
and the two sentences immediately after it were `auto` readings with no engine named ("thirteen of
nineteen bedrooms", `bed3` at 6.0 × 38.0 with 1 ft closets). Measured on both: `engine="heuristic"`
gives **8 of 19**, `bed3` at **8.4 × 22.8** and closets at 6.0 and 4.0 ft; `auto` reproduces the
published illustration and drifts (12 of 19 on one run, 13 on another). Both engines are now
tabled. The rule failed in the sentence stating it, which is the third time in this package.

**S2. The stair transcription does not merely risk drifting — it has already drifted.** The study
report's correction 1 said *"the prose and the Python are two spellings of one rule and nothing
holds them together"*. Fed the prose's own input (9 ft ceiling → `storey_in = 120`),
`openings.stair_pass` returns **17 risers at 7.059 in, 16 treads, 13.33 ft**; `rooms/stair-hall.json`
says **16 risers at 7.5 in, 15 treads, 12 ft 6 in**. The Python follows `storey-graduation.json`'s
`ceil(storey / 7.25)`; the prose works at 7.5 in. A warning has been replaced by a measurement.

**S3. The passage is stated seven times, not four.** Two more suppliers: the Georgian kit's
`circulation_parti.passage_width_ft` at `[10, 14]`, and **`room-vernacular.json`'s rule 8, which
carries `quantity: "passage_clear_width"` and a `range` floor of 36 in against its own
`authority_note` saying 6 to 12 ft in the same object.** That last is the sharpest of the seven
because it is the ONE statement `check_addresses.py` can see, and its ceiling of 10 ft is exactly
the kit's floor. Corrected in four files.

**S4. The grouping-disagreement question said four instances and enumerated five, and there are
six.** Its H1 feeds the generated index, so the count is load-bearing. The sixth is
`keeping-room-hearth-cluster`, whose prose explains why 12 ft is the radiant reach of an open hearth
and whose test admits 14 — a rule disagreeing with its own statement, no second record involved.

**S5. The unquantified-rule finding was a hundredfold understatement.** The study's correction 2
named one rule in `room-harmonic.json` as invisible to `check_addresses.py`. Measured across the
corpus: **268 of 761 derived rules (35.2%) carry no `quantity`, across 46 of the 57 packs, and five
packs have none at all.** OQ 48's published collision ratios are measurements over the 64.8% that
can be compared — honestly unjudged, and worth stating beside the ratio.

**S6. The island fix would have convicted four of the corpus's own `good` reference plans.** The
finding proposed not rotating the island; measured, that fails **11 of 16 declared kitchens (10
newly)**, four of them `good-*`. The cause is applying a two-sided clearance to the item's long
side — 84 + 2 × 42 = 14.0 ft across a room. Pairing each axis with its own clearance (9.25 ft
across the short axis, 14.0 along the long) fails **4 of 16, every one a `bad` plan**. The corpus's
own good/bad split is the nearest thing to a calibration this check has, and the naive fix fails
it. This is the session's second instance of a proposed check convicting the reference plans.

**S7. The `openings.required_wall_ft` precedent was cited for the opposite of what it is.** Three
documents cited it as "one function, two callers, never a second transcription". It is
**deliberately spelled three times** (`openings.py`, `render_plan.py`, `derive.js`) because one is
JavaScript and the app suite may import nothing, with `tests/fixtures/sheet_symbols/` holding all
three to one contract. The discipline is right and the mechanism was taught backwards. Corrected in
`PLAN-OF-ACTION.md` and both WP-9 reports.

**S8. The one-remove caveat was written in terms of attribution markers, and numbers are what a
future package will come for.** The body caveat listed "—Palladio", "—Morris", "—Kerr" and so on —
the parts of a document a reader skims. It now states that every ratio, width, percentage and
ft/bay carries the same standing as the sentence it came from, and that §6's eleven items are the
sharpest cases rather than the boundary.

**S9. A second zero-reader field, in all 60 room records.** `servicing.stack_proximity_ft` appears
nowhere in the tree except its own schema definition — the plumbing-and-flue counterpart of
`structural_logic`. Two on one subject in one section.

**S10. `WANTED.md` said "everything below has been verified to exist" and the drawing counts were
read for two of six.** The item ids are all verified (the written data was fetched by each). The
counts were not, and four blank cells read as "none" rather than "not read". The Drayton row also
gave "14–15 sheets · 14 + 19 data pages", which is 14 drawings and 19 data pages with the drawing
count copied into the wrong column.

**S11. Smaller, each fixed in place.** The register ruling had no back-fill question — the largest
of its undecided items, since 112 records were authored before the axis existed and the honest
default for all of them is *unknown*. Gunston Hall's bay count sat under a bare "HABS VA-141"
attribution in an open-question table when it is a reading of the survey's fenestration prose, and
it is the divisor of that row. A `§11` cross-reference pointed at its own section. "Five measured
buildings" where three were measured. The study preface said none of its questions was answered
after Lucas had ruled Q1.

**And the slug-exemption entry demonstrated itself twice more.** Correcting it took the unchecked
count from 122 to 126 and the deliberate non-resolving illustrations from 10 to 14, because naming
them is writing them. Worse, **its own proposed fix contained the bug it proposes to fix**: it
offered a slug-shaped placeholder as a safe illustration form, and `SLUG_CITE`
(`\boq/[a-z0-9][a-z0-9-]*`) matches any such thing. Only `oq/<slug>` is safe. The CLAUDE.md entry
recording this deliberately does not repeat the offending string.

---

## Worth fixing — found and fixed

- **"The floors are inert"** is wrong. `compose.room_default_dims()` sizes every instantiated room
  from `ratio = (pr[0] + pr[1]) / 2`, so the **floor shapes the declared dimensions of every room
  the composer makes**. It convicts nothing and aims everything.
- **The open question's cost estimate for deleting the floors was wrong in the other direction**: it
  claimed `check_rooms` would then fire on 29 records. The true number is **zero** — lowering
  `prop[0]` makes the only clause reading it strictly *less* likely to fire. The real cost is
  generative, not checking.
- **"Every one of those rooms is inside its area band"** — nine of eleven. `breakfast` at 189 sf
  against [80, 180] and `cl3` at 38 against [6, 24] are outside it, and `plan_check` prints both.
- **"Six apiece" for three exemplars** is established for Gunston Hall, approximated for Drayton
  Hall, and never made for Hammond-Harwood.
- **`essential` is explicit on 78 of 278 furniture items**; the other 200 inherit the schema's
  `"default": true`. Four-fifths of the catalogue is essential by omission.
- **`georgian-service-core`'s ridge rule is not "evaluated by nothing"** — `plan_check` parses it and
  reports it **unjudged** for want of a supplier, which is the corpus's own discipline working.
- **"Five of six measured cases inside the band"** is four of six. **"Wider than any passage in the
  sample"** overlooks Sabine Hall's 18 ft. **The Mount Vernon ground-floor range** silently dropped
  the New Room at 16'6". **The gambrel quotation** stopped mid-sentence, without an ellipsis, right
  before the record's own competing explanation.
- **The one-remove caveat** sat in the preface and the closing line and **nowhere in the body**,
  where every quotation carries an ordinary bibliographic citation. It now heads the body.
- **The two reports contradicted each other about Glassie** — one quoting page numbers, the other
  saying the text could not be established. Reconciled where it occurs.
- **`PLAN-OF-ACTION` named three open questions where six were raised**, and **`measure_precedents.py`
  was written about in the present tense and does not exist.**
- **A correction left a stale figure two sections upstream**: the opening still called
  Hammond-Harwood's block "SMALLER (44 × 42)" after §2 had superseded that figure.
- **Three superseded numbers survived in an open-question file** after the report that raised them
  had been corrected — found by sweeping every changed file for each retired figure, which should
  have been run after the first correction rather than the tenth.

---

## Pre-existing, exposed rather than introduced

**P1. A grouping rule and a room record can disagree, and nothing checks the class.**
`check_addresses.py` polices pack-vs-pack and kit-vs-pack and **does not see groupings at all**.
Six instances — the report had found one and called it "the first instance found in it", which
extending the method falsified in twenty minutes, and re-auditing THAT found two more (S3, S4). The
sharpest is the **piazza**:
`piazza-and-single-house-core` demands `piazza_depth_ft at-least 10`, **hard**, while
`rooms/piazza.json` bands [8, 14] and cites *"the measured Charleston piazzas run 8 to 12 ft"* — so
a 9 ft piazza is inside the band, inside the cited measurement, and fails a hard rule. The
**bedroom** carries three numbers for one quantity (9 in the record's prose, 10 in the grouping, 11
in the band) on the grouping **14 partis** carry. `oq/a-grouping-rule-and-a-room-record-can-disagree`.

**P2. The citation guard cannot see two thirds of the namespace it guards** — 122 of 178 at
`5572866`, 126 of 182 after this audit's corrections, and the checked count has not moved in three
commits while the unchecked one has risen by 26. `check_citations.py` blanks
inline code spans before scanning — written for the numbered namespace, where prose is the citation
form. **For slugs the convention is inverted**, and backticks are how this corpus cites a named
question. Mutation-tested: a fake slug in prose is caught, the same fake slug in backticks passes.
**It must not simply be switched on**: the unresolved mentions inside code spans are all deliberate,
including this checker's own test fixture. `oq/a-slug-in-a-code-span-is-not-checked`.

**P3. `geometry.py::snap`'s docstring figure is stale.** "18 of 30 ground wall lines … off the bay
grid" does not reproduce under any reading; the current figures are 35 of 45 interior segments or
19 of 23 distinct interior lines. `check_counts.py` polices numbers in documentation and not in
source comments, so nothing was going to catch it — and the report gave it authority by quoting it
as "measured".

**P4. The route was ruled the day before.** `oq/fetching-through-a-tier-the-proxy-denies` was RULED
31 Aug 2026 and records that the Tavily connector reaches loc.gov, verified. It closes with its own
purpose: *"This entry exists so the next session finds a ruling instead of re-deriving the bypass."*
WP-9.2 re-derived the bypass and wrote it up under the heading "loc.gov is reachable after all".
What survives as new is narrower: `tile.loc.gov` serves the HABS *written data* as extractable text.

---

## Guards that were mutation-tested and are ALIVE

Reported because "the tests pass" is not evidence and a guard nobody has tried to break is a guard
nobody has tested:

| guard | mutations tried | result |
|---|---|---|
| `test_claude_md_open_question_list…` | wrong tally; removed id; UPPERCASE prose in the parens; lowercase prose in the parens | **4 of 4 failed**, control passed |
| `check_ids.py` | status word outside SETTLED/OPEN; heading disagreeing with filename | both refused, with the right message |
| `check_citations.py` | dangling slug in plain prose | caught |
| `check_citations.py` | dangling slug **in a code span** | **not caught** → P2 |

## Two things the audit did to itself

**The entry about illustrative slugs was convicted for containing an illustrative slug.** The first
draft of `oq/a-slug-in-a-code-span-is-not-checked` wrote its mutation output with a plausible fake
slug in a **fenced** block — and fenced blocks are scanned, only inline spans are exempt. Kept in
the entry, because it shows the corpus has three contexts and only one is safe.

**And that entry's own numbers went stale in the commit that published them, twice.** It measured
100 of 153; the commit adding it introduced 12 more mentions, five of them the illustrative slugs
the entry needed in order to explain itself. **Correcting it in the second audit pass did the same
thing again** — 122/178 became 126/182 and the deliberate non-resolving illustrations went from 10
to 14 — because the correction names each illustrative slug once more in order to count them.
Every figure there is now stamped with the commit it was taken at, and the post-correction delta is
stated as a delta rather than pinned to a hash that does not exist yet. **Its proposed fix also
contained the bug**: the safe illustration form it offered matches `SLUG_CITE` exactly.

**The audit's own instrument was wrong twice before it was right**, caught by inspecting rather
than publishing: one script derived wall lines from shared rectangle faces instead of calling
`wall_lines()`, and another read `w["on_grid"]` — a key `bearing_lines()` does not emit — and would
have reported "53 of 53 off grid". An auditor's instrument is not exempt from the standard it
audits against.

## What was NOT done

- **No code was changed**, in the audit or in what it audited. Every finding above is either a
  documentation correction or an open question. P1 and P2 both need rulings before a checker moves.
- **No number was reconciled by picking one.** Three of P1's six instances have a source on one
  side only and it is not consistently the same side.
- **The stair drift (S2) was measured and not fixed.** Reconciling `openings.stair_pass` with
  `rooms/stair-hall.json` means choosing between 7.25 in (the pack, which the Python follows) and
  7.5 in (the prose), which changes drawn stairs on every plan. That is a generator change and a
  ruling, not an audit correction.
- **The island rule (S6) was measured and not built.** The correctly-paired formulation is stated
  and its effect on all 16 declared kitchens is published; building it is a drawn-layer change and
  belongs with the drawn-record fix the report already recommends.
- **The unquantified-rule class (S5) was measured and not closed.** 268 of 761 derived rules
  without a `quantity` is an authoring backlog with a ruling in front of it, not a patch.

## Verdict

**Yes — deployment-ready, on a full run.** `python3 build/check_all.py` green: 40 of 43 checks
passed, three COULD NOT EVALUATE and named as such (`export_dxf` and `export_ifc` selftests without
`ezdxf`/`ifcopenshell`, `pytest workbench/server/tests` without `fastapi`/`httpx`) — a named
unjudged state, never a pass. The change remains documentation-only: no `.py`, `.js` or corpus
`.json` was touched, verified by diff.

**The verdict is qualified in one direction and it is worth stating plainly.** This audit ran two
passes and the second found eleven more, four of them inside the first pass's own corrections. A
third pass would probably find some. What makes this stopping point defensible rather than
arbitrary is that **the second pass's findings are smaller than the first's** — no conclusion moved,
where the first pass moved three — and that every figure now in these documents has been re-derived
by running something rather than by re-reading the sentence around it. The remaining risk is
concentrated in the numbers nobody has re-derived a second time, and those are named: S3's seven
passage statements, S5's 268, S6's three formulations.
