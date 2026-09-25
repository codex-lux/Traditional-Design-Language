# oq/an-evaluation-whose-check-errored-names-no-plan — the journey cannot tell which house an errored evaluation was of, so a refusal the route preserved reaches no step

*Status: CLOSED 25 September 2026 (WP-14.20) — on answer 1: the route names the plan, the journey reads it through one `evalPlanOf` · Raised in: WP-14.6 (24 September 2026), filed by WP-14.10 (25 September 2026)*

**The finding.** `workbench/app/src/journey/journey.js` reads an evaluation only for the plan it
was of: `lastEval.check.plan === plan.id`, because `lastEval` is the shell's and outlives a change
of plan, and a verdict about the house before is not a verdict about this one. `plan_check` writes
that id on every completed check (`build/plan_check.py`, the `"plan": plan["id"]` of its return).
**`core.check_plan`'s two error payloads carry no id** — *"plan does not match the plan schema"*
and *"could not validate: the jsonschema package is not installed"* (`mcp_server/core.py`,
`check_plan`). And `workbench/server/evaluate.py` still attaches `placement_refused` on exactly
that early return; its WP-13.4 comment says why a refusal has to survive a schema error.

So on a record whose check errored and whose placement was refused, the house journey reads the
plan step as **"not yet evaluated"** and the drawings and export steps as **"ready"**, and both
are links. A reader following them reaches the Drawing Set, which re-places the record on its own
route and refuses it there. The bar would have said *ready* over a house that may not be drawn.
WP-14.6 found this in the pure module and wrote it down before any surface drew the bar; WP-14.10
drew the bar, and this is where it becomes visible.

## Measured

- **The shape**, on this tree: `journeyState({ plan: {id: 'p'}, lastEval: { check: { error: '…' },
  placement_refused: {…} } })` gives plan `unevaluated`, drawings `ready`, export `ready`. The
  bar's `barView` makes both links, because neither step's predecessor is blocked.
- **The shipped corpus does not reach it today.** Measured on 25 September 2026 by evaluating each
  of the sixteen plan records through `workbench/server/evaluate.py` exactly as the bench route
  calls it: on `engine="auto"`, **0 of 16 checks errored** and 16 of 16 name their plan, while
  **11 of 16 placements came back refused** — so the half of the precondition that is common is
  common, and the half that is not is absent. On `engine="heuristic"` the same: 0 of 16 errored,
  16 of 16 named, 4 of 16 sketches refused. One run of `auto`, which is wall-clock bounded; the
  zero is the figure, not the refusal count. It is latent rather than live.
- **It has been live three times.** A SOLVED record — the one `evaluate.py` hands to `check_plan`,
  after the gate at the door has passed the DECLARED one — has failed the plan schema at WP-11.3
  (furniture `marks` written before the schema admitted them), at WP-11.4 (`geometry.void.heated`
  on two of the fourteen reference plans, failing since OQ 55) and at WP-13.6 (`corner: true`,
  thirteen of sixteen placed plans). Each time the first reader to notice was something other
  than the schema. The second route is an
  environment without `jsonschema`, which `core.validator` reports as an environment fact rather
  than a verdict (OQ 35's ruling), and which reaches the same early return.

## What each answer would change

1. **`evaluate.py` states the plan id at the top of its response** (`out["plan"] = plan["id"]`),
   and the journey reads `lastEval.plan` before `lastEval.check.plan`. The MCP payload is
   untouched, because `evaluate.py` is the workbench route and not `core.check_plan`. Two files in
   two lanes: the server's (lane L2, WP-14.4/14.3) and the journey's (WP-14.6, now read by
   WP-14.10's bar). This is the smallest change and names the house the evaluation was of in the
   one place that knows.
2. **`core.check_plan` writes `plan` on its error payloads.** The journey then needs no change —
   but this changes an MCP tool's payload, which PRD §J.4 lists under *must not*.
3. **The journey reads a refusal whatever plan it names.** Refused. That is the stale-verdict
   error the identity rule exists to stop: a refusal of the house before would block the drawings
   of this one.

## Why it is not fixed in WP-14.10

The fix is a server line and a journey line, and the server is outside WP-14.10's files. Writing
the journey half alone would read a key nothing writes — a reader of an absent field, which reads
exactly like a reader that works.

## Amendment, 25 September 2026 (WP-14.20) — closed on answer 1

**Answer 1 is built, on both sides, in one package.** `workbench/server/evaluate.py` writes
`out["plan"] = plan["id"]` when it builds its response, which is BEFORE the early return a check
that errored takes, so the route names the house on exactly the path the check cannot.
`workbench/app/src/journey/journey.js` gained `evalPlanOf(lastEval)`, the ONE reader of which plan
an evaluation was of — the route's id first, the check's own second — and both sites that match an
evaluation to a plan read it: `journeyState` and `App.jsx`'s stale-evaluation clear. A source walk in
`src/journey.test.mjs` refuses a `check.plan` read anywhere else in the app, so a third site cannot
spell the rule its own way.

**What it changes, driven.** The body this question measured — `{ plan: 'p', check: { error: … },
placement_refused: {…} }` — reads plan `refused`, drawings `refused`, export `refused` now, and the
bar draws neither the drawings nor the export as a link (`src/journey.test.mjs`, with `barView`).
Dropping the `lastEval.plan` read from `evalPlanOf` turns that test red, and so does reading only the
check. The identity rule is untouched: an errored evaluation naming ANOTHER plan still blocks nothing
here. On the server, `workbench/server/tests/test_evaluation_names_its_plan.py` drives the errored
path (a placer answering with a refused record, a check answering the schema error) and asserts the
route's `plan` beside the surviving `placement_refused`; a completed check over the real route
carries the same id twice.

**What it deliberately does not change.** `core.check_plan`'s error payloads — what the MCP tool
serves — still carry no plan id (answer 2 changes a frozen payload and was not ruled), and a test
holds that. Answer 3 stays refused. **An errored check that was NOT refused now reads `evaluated`
with all three counts `not counted`**, where it read `not yet evaluated`: the evaluation happened and
counted nothing, and the journey says so rather than calling the house unevaluated. Whether the bar
should name the error itself is a word the journey does not have, and is not added here.

**The shipped corpus still does not reach this path** — 0 of 16 checks errored when the question was
measured — so the guards are driven rather than swept, and the premise that the driven check really
errored is asserted before anything else in the server test.
