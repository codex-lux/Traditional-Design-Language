# oq/a-brief-cannot-name-a-parti — the dossier lists a style's plan types and the brief has no field that could carry one

*Status: OPEN · Raised in: WP-14.0 (24 September 2026)*

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
