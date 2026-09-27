# oq/a-brief-cannot-name-a-parti — the dossier lists a style's plan types and the brief has no field that could carry one

*Status: CLOSED 25 SEP 2026 — answer 1, guaranteed a place, executed by WP-14.19 · Raised in: WP-14.0 (24 September 2026)*

**The finding.** Phase 14 gives every style a dossier, and one of its sections lists the partis
native to that style — the plan types. The obvious next affordance is *"start a brief from this
parti"*, and there is nowhere to put the answer. `schema/brief.schema.json` is
`"additionalProperties": false` (line 9) and names no `parti`; `POST /api/compose`
(`workbench/server/app.py:636-679`) reads `body.brief` and the revision knobs and hands
`jobs.submit(brief, …)` nothing else; `jobs.submit` validates the brief against that schema before
the job exists (`workbench/server/jobs.py:260-264`); and `compose.pick_partis`
(`build/compose.py:397`) chooses the diagrams itself, from the style's native partis, the massing
affinity and the brief's bedroom and area ranges.

**Measured, not reasoned.** `briefs/family-georgian.json` validates clean against the schema. The
same record with `"parti": "centre-passage-double-pile"` added is refused by the schema's own
validator: *"Additional properties are not allowed ('parti' was unexpected)"*. So a dossier that
wrote a parti into the brief it seeds would be handing Brief Intake a record the server rejects
whole — which is the exact shape of Phase 14's own finding 6, where three of Brief Intake's four
budget options are outside the schema's enum and choosing one refuses the brief.

**Why it is a ruling and not a missing field.** The brief schema's own description says what a
brief is for: *"What a client asks for. Deliberately short — a brief that specifies everything has
already done the designing … Anything absent is decided by the composer and reported as a
decision."* A client does not ask for a parti; a designer chooses one. The corpus already has the
nearest precedent and it cuts both ways: `massing` IS a brief field, described as *"Force a
skeleton, or leave unset and let style affinity choose"*, and `pick_partis` honours it as a filter
(`build/compose.py:406`). A parti is one layer more specific than a massing — and several partis
share one massing, so seeding `massing` from a parti would be a different request wearing the
parti's name.

## What each answer would change

1. **A brief may name a parti** — an optional `parti` field (brief schema 0.1.0 → 0.2.0) that
   `pick_partis` honours. It then has to decide what "honour" means: return only that diagram (and
   the composer stops returning *contrasting* candidates, which is what `compose` is for), or
   guarantee it a place in the set beside the composer's own choices. A named parti that is not
   native to the brief's style has to be answered too — today `pick_partis` borrows a diagram and
   says so in a `why` string, while `core.list_partis` filters on `p["styles"]` and lists none for
   a style with no native parti, so the two readers already disagree about borrowing. Every
   consumer of the schema moves:
   Brief Intake, the MCP `tdl_brief_schema` and `tdl_compose` tools, and the two shipped briefs'
   validation.
2. **The parti rides on the REQUEST, not the brief** — `POST /api/compose` accepts `parti` beside
   `brief`, the way it already accepts `revise_engine` beside it, and the brief schema stays a
   client's statement. `compose.instantiate(parti, brief)` already builds one parti against one
   brief; this would expose it. The request is then not reproducible from the brief record alone,
   which is a property the job's result currently has.
3. **Neither** — the dossier lists plan types as information and the composer keeps choosing. The
   honest cost is that a reader who has just read a plan type cannot ask for it, and has to discover
   whether the composer offers it.

## What tranche 1 does meanwhile

Answer 3, stated rather than implied. The dossier's plan-types section lists the style's partis as
information only; there is no "start a brief from this parti" control anywhere, and the plan's
*must not* list forbids a parti bridge until this is ruled. "Design a house in this style" seeds
`#/brief?style=<id>` — the one brief field the dossier can honestly fill.

## Related

- `oq/the-composer-returns-a-set-that-satisfies-neither-must-have-room` — a set the composer
  chose, answering the brief with two unusable houses; a named parti is one way a reader might
  try to route around it, which is an argument about this question and not a reason to answer it.

## Ruled 25 September 2026

**Answer 1, guaranteed a place.** Brief schema 0.2.0 gains an optional `parti`. The composer guarantees the named parti one candidate among the contrasting set: it is kept past the cut and, if the returned set does not already hold it, appended as one more candidate, so it displaces nothing. A parti not native to the style is borrowed, and the candidate says so. A named parti that contradicts the brief's own massing is refused by name before a job starts. The contract is `docs/prd/phase-14-tranche-2.md` §C.5. The question closes when WP-14.19 lands.

## Closed 25 September 2026 (WP-14.19)

**Answer 1, as ruled, and the server half only.** `schema/brief.schema.json` is 0.2.0 with an
optional `parti` carrying an id pattern, and both shipped briefs validate under it unchanged.
The composer reads it in four places and they are one mechanism:

- **`compose.nativity(parti, style)`** returns native, lineage or borrowed. It is the one spelling
  of that relation, and both `compose.pick_partis` and `core.list_partis` read it. The two readers
  this entry found disagreeing about borrowing are now held to each other over every style and
  every parti in the corpus.
- **`compose.check_brief_refs(brief)`** refuses an unknown parti by name. It also refuses a parti
  whose own massing and alternates do not include the brief's `massing`, naming both. It reads the
  same predicate the massing filter reads, so the filter and the refusal cannot come to disagree.
  `core.compose`, `workbench/server/jobs.py` and `compose.main` all call it before a job exists,
  and `compose()` calls it again for a direct caller.
- **The guarantee.** The named parti is scored by the same arithmetic as every other diagram. If
  `pick_partis`' cut falls above it, its row is kept anyway, at its own fit. If the composer's
  sorted, revised set does not return it, it is appended after that set, where it displaces
  nothing. The composer's own candidates are the ones it returns with no name, in the same order.
  An appended candidate is revised afterwards, on whatever the set's revise budget left, and says
  so where that budget is spent. A candidate the lot drops is not appended, and `named_parti.why`
  says the lot dropped it.
- **The result** carries `named_parti` (`null` when the brief names none). Every candidate carries
  `named_by_brief` and its `nativity`. A borrowed named candidate's `why_this_diagram` reads *NOT
  native to this style — the brief named this diagram, so the composer is borrowing it*.

**What moved that the ruling did not name.** `core.list_partis` now lists lineage partis beside
native ones, as §C.5 of the tranche-2 contract says. The dossier's Plan types section therefore
moved, measured over all 164 style nodes against a `git archive` of `f0dc52a`. It moved on 106
styles. The partis it lists went from 160 to 422 in total, and its section count, which sums the
massings, the partis and the groupings, went from 830 to 1,092. Both moved by +262, which is
exactly the corpus's lineage pairs; the 160 native pairs were listed already. No section
appeared or disappeared on any dossier. The three styles with no native parti, which
Brief Intake names in its own advisory text, each list lineage partis now: `egyptian-revival` 5,
`new-urbanist-traditional` 8 and `tuscan-vernacular` 1. **The two app readers of `/api/partis`
read every row as native**, so they must read `nativity` before this reaches a person:
`BriefIntake.jsx` (its native count and its no-native advisory) and `CandidateSet.jsx` (its
`nativePartis` set). Both belong to other packages of this tranche, and WP-14.19's report names
the lines.

**Not done here.** The brief-side control is the "start a brief from this parti" bridge the
tranche-1 plan forbade until this was ruled. It belongs to the packages that own Brief Intake and
the Plan types section. The report is `docs/reports/wp-14.19-a-brief-may-name-a-parti.md`.

**The page half (WP-14.25, 25 Sep 2026).** The bridge is built. Each plan type on a style's
dossier links to Brief Intake with the style and the parti named, worded by the glossary record
`start-a-brief-from-a-plan-type`. Brief Intake carries a parti select grouped by the nativity the
server states, with borrowed diagrams only behind an explicit choice, and shows the composer's
refusal in the composer's own words. The Candidate Set marks the candidate the brief named, and
prints `named_parti.why` where the set does not hold it. The two readers named above read
`nativity` now, and so does a third, the feasibility panel's native count. The report is
`docs/reports/wp-14.25-the-plan-type-starts-the-brief.md`.
