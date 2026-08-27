# The Workbench

The human interface to the Traditional Design Language (WP-5.2): a local web app —
the drawing with the critique on it — over the same corpus and toolchain the CLI and
MCP server drive. Twelve surfaces are live: eleven working surfaces plus the Overview
you land on (WP-5.6). Export ships the plan record, brief, check report and
the five SVG sheets today; DXF/IFC (WP-5.1) ship too, and the guidelines book and
details library (WP-5.3) are named as forthcoming on the Export surface rather than
hidden. Drawing ingestion (WP-5.5) shipped as the Transcription surface, and the card
that used to promise it now says where it went.

## Finding your way around it

Three keys, and they are the whole map:

| | |
|---|---|
| `⌘K` · `ctrl-K` | search everything — 665 named things: styles, slots, faults, packs, rooms, partis, and the surfaces themselves |
| `/` | filter the list in front of you |
| `?` | the keys, and how a thing is addressed |

**Every place is a URL** (WP-5.6), and the URL is the citation grammar written down —
`#/kit/tidewater-georgian/cornice`, `#/faults?sev=serious`, `#/phylogeny?view=map`. So a
view can be refreshed, gone back from, bookmarked or handed to somebody else, and a
citation the rail writes is a link a person can open: `#/cite/fault:porch-too-shallow-to-inhabit`.
Filters live in the URL too, which means "the serious faults driven by budget" is a link.

The palette searches **names, ids and akas — not prose**. For a half-remembered phrase from
a tell or a remedy, ask the rail: it reads the records properly, and says what it could not
evaluate.

## Run it

```
pip install -r workbench/requirements.txt        # to run the server
pip install -r workbench/requirements-dev.txt    # adds pytest + httpx, to test it
cd workbench/app && npm install && npm run build && cd ../..
make workbench          # → http://127.0.0.1:8177
```

Dev mode (`make workbench-dev` prints this): `uvicorn workbench.server.app:app
--reload --port 8177` in one terminal, `npm run dev` in `workbench/app` in another —
vite proxies `/api`, so there is no CORS anywhere.

The AI rail needs `ANTHROPIC_API_KEY` in the environment. Without it the server runs
and the rail says plainly that it is off — the three-state discipline applies to the
rail's own availability.

## Deploying it

`docs/deployment.md` is the account; the short version is that there is a `Dockerfile`
at the repo root and the only things a container must set are `WORKBENCH_HOST=0.0.0.0`
(the image does), `WORKBENCH_PASSWORD` and `WORKBENCH_SECRET` for the gate, and
`ANTHROPIC_API_KEY` for the rail. `PORT` is read in preference to `WORKBENCH_PORT`, so a
platform that injects it needs no configuration.

The same process also serves the MCP server's 24 tools at `/mcp`, gated by the same bearer
token — `mcp_server/README.md` has the client command. Its transport has to recognise its
own hostname, which is discovered from the platform's own environment variables; set
`WORKBENCH_ALLOWED_HOSTS` only for a custom domain, or if `/api/health` shows the host
missing from `mcp.allowed_hosts`.

Two things not to get wrong: **replicas must stay at 1** (the compose job registry is in
process memory — OQ 36), and the rail's caps are not a spend cap. The only ceiling in
dollars is the budget on the key itself.

Locally none of this applies. With no `WORKBENCH_PASSWORD` set the server is open, as it
has always been, and says so at startup and in `/api/health`.

## Reading the drawings

Every plate — the order on ⑩, the sheet on ⑦, the five sheets of ⑧ — is mounted in a loupe:
**fit** by default, ± or ⌘/ctrl-scroll to magnify, drag to pan, **1:1** for the pane's own
width. It scales the whole plate rather than the SVG alone, so the title block and the
caption stay in register with the drawing, and a wall handle on the plan still drags the
wall at any magnification. Room names are fitted to the room they name — broken across lines
before they are shrunk, turned along a slot room, and never truncated.

## What it will not claim

The interface renders the system's honest states rather than hiding them: unjudged is
never collapsed into passed; the per-gesture solver is named as a hill-climb (re-solve is
explicit, candidate count exposed) and the proof is offered beside it as *prove
placement (CP-SAT)*, which names the conflicting requirements when a record's declared
facts cannot all hold; a plan is never presented as proved when it was only searched;
a room the search placed below its own catalogue band is reported, not silently traded
away (OQ 54); a cut off the bay line is counted AND drawn where it falls (P7, OQ 33);
the code
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
