# WP-9.5 — The corrections that were themselves wrong: the adversarial audit of WP-9.1 and WP-9.2

*Status: the audit ran on 1 Sep 2026 against `e1f34fb..HEAD`. Seven independent read-only auditors
were dispatched; three had returned when this was written and four were still running — what they
find will be treated the same way and appended. Everything below is **found, verified and fixed**,
not reported and left.*

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

**Twenty-four findings survived verification. Eight were blocking. Every one of the blocking
findings was in work this session had produced, and four of them were in corrections this session
had *already made* — a first fix that was itself wrong, or right in one file and left wrong in
another.**

The single most useful result is not any individual finding. It is that **the highest-yield
technique was to re-derive a number rather than re-read the sentence containing it.** Every
blocking finding came from running something; none came from reading.

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
Five instances — the report had found one and called it "the first instance found in it", which
extending the method falsified in twenty minutes. The sharpest is the **piazza**:
`piazza-and-single-house-core` demands `piazza_depth_ft at-least 10`, **hard**, while
`rooms/piazza.json` bands [8, 14] and cites *"the measured Charleston piazzas run 8 to 12 ft"* — so
a 9 ft piazza is inside the band, inside the cited measurement, and fails a hard rule. The
**bedroom** carries three numbers for one quantity (9 in the record's prose, 10 in the grouping, 11
in the band) on the grouping **14 partis** carry. `oq/a-grouping-rule-and-a-room-record-can-disagree`.

**P2. The citation guard cannot see 65% of the namespace it guards.** `check_citations.py` blanks
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

**And that entry's own numbers went stale in the commit that published them.** It measured 100 of
153; the commit adding it introduced 12 more mentions, five of them the illustrative slugs the
entry needed in order to explain itself. Every figure there is now stamped with the commit it was
taken at.

**The audit's own instrument was wrong twice before it was right**, caught by inspecting rather
than publishing: one script derived wall lines from shared rectangle faces instead of calling
`wall_lines()`, and another read `w["on_grid"]` — a key `bearing_lines()` does not emit — and would
have reported "53 of 53 off grid". An auditor's instrument is not exempt from the standard it
audits against.

## What was NOT done

- **No code was changed**, in the audit or in what it audited. Every finding above is either a
  documentation correction or an open question. P1 and P2 both need rulings before a checker moves.
- **No number was reconciled by picking one.** Three of P1's five instances have a source on one
  side only and it is not consistently the same side.
- **Four of seven auditors had not returned** when this was written. Their findings get the same
  treatment.
