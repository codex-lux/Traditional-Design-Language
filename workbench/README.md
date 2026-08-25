# The Workbench

The human interface to the Traditional Design Language (WP-5.2): a local web app —
the drawing with the critique on it — over the same corpus and toolchain the CLI and
MCP server drive. Eight surfaces are live (Phylogeny, Style Record, Kit, Fault Corpus, Proportions,
Brief Intake, Candidate Set, Plan Workbench); two are listed as forthcoming rather
than hidden (Drawing Set, Details & Export).

## Run it

```
pip install -r workbench/requirements.txt
cd workbench/app && npm install && npm run build && cd ../..
make workbench          # → http://127.0.0.1:8177
```

Dev mode (`make workbench-dev` prints this): `uvicorn workbench.server.app:app
--reload --port 8177` in one terminal, `npm run dev` in `workbench/app` in another —
vite proxies `/api`, so there is no CORS anywhere.

The AI rail needs `ANTHROPIC_API_KEY` in the environment. Without it the server runs
and the rail says plainly that it is off — the three-state discipline applies to the
rail's own availability.

## What it will not claim

The interface renders the system's honest states rather than hiding them: unjudged is
never collapsed into passed; the solver is named as a hill-climb (re-solve is explicit,
candidate count exposed); an infeasible brief is never presented as proof of anything
(the conflict-set panel is designed and marked forthcoming until WP-2.3); the code
layer is advisory, never compliance; no candidate is ever crowned; and no plan is ever
called good.

## Architecture, one paragraph

`server/` is a thin FastAPI skin over `mcp_server/core.py` — pure pass-through routes,
two small aggregations (`/api/phylogeny`, kit cascade rows), one combined
`/api/plan/evaluate` (validator + placement per edit gesture), an in-memory compose
job registry with SSE progress, and the rail: an Anthropic tool loop over the same 24
tools the MCP server exposes (loaded from `server.py` itself via a stub, so they
cannot drift), with every citation validated against live corpus ids before it is
streamed. `app/` is Vite + React, ported from the design mockup: the Drawn Language
tokens verbatim, the 19-component design system, and a plan Sheet drawn only from the
record and its placement. The plan record is a document the browser owns; the server
is stateless except the job registry. Corpus edits during dev are picked up via
`POST /api/dev/reload` (explicit by design — see OQ 28).

See `docs/workbench.md` for the layer doc and `docs/reports/wp-5.2-the-workbench.md`
for what was built, found, and deliberately not done.

## Verify

```
make workbench-test         # server suites: endpoints, CLI parity, rail loop, citations
bash workbench/scripts/smoke.sh   # live server: health, parity diff vs CLI, one compose job
cd workbench/app && node e2e/walk.mjs  # browser walk of every surface + screenshots
```
