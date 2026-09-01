# Deployment

*Written 25 August 2026, alongside the change that made the workbench deployable.*

VISION.md §IX names four audiences and the corpus serves two of them through machines: an
agent consulting the MCP server mid-conversation, and a human — builder, plan-development
lead, architect — driving an interface. Until this package the second could only happen on
the machine the repository was cloned onto. `workbench/server/app.py` said so in its own
docstring: *"Binds 127.0.0.1 only. No auth, no network beyond the Anthropic API for the
rail."*

That sentence is now three sentences longer, and this document is the account of what
changed, what turned up while changing it, and what was deliberately left alone.

## The shape, and why it needed almost nothing

The architecture was already right. `workbench/server/corpus.py` opens by naming the
property the whole server leans on — *"core.py is pure functions with no protocol
dependency"* — and that is exactly what lets one corpus serve two protocols. `server.py`
in `mcp_server/` is 26 tools that each return `J(core.something(...))`; `app.py` is ~30
HTTP routes that each return `core.something(...)`. Neither holds corpus logic. Deploying
therefore meant adding a container and a gate, not restructuring anything.

Nor does any of it need a database. The corpus is JSON in git, baked into the image at
build time and read-only at runtime; 164 styles, 159 kits, 209 faults and the rest come to
**12.3 MB across 725 files** — this said 27 MB until the infrastructure audit measured it —
which is nothing to a container image and would be a migration pipeline to no purpose in
Postgres. The whole shipped tree, corpus plus toolchain plus docs, is 20 MB; the image around
it is ~733 MB, and 581 MB of that is Python packages. See
`docs/reports/infrastructure-audit.md` §1. What state exists — a session cookie, rate-limit counters, the compose
job registry — is in memory and is *supposed* to be lost on redeploy. A database becomes
real when saved plans must outlive a deploy, and not before.

## What was built

**The server can bind a container.** `workbench/server/__main__.py` reads `WORKBENCH_HOST`
(default `127.0.0.1`, unchanged) and prefers the platform-injected `PORT` over
`WORKBENCH_PORT`. The existing bind probe — which exists because `uvicorn.run` returns 0 on
a failed bind and so reads as success — now probes the host it will actually use. uvicorn
runs with `proxy_headers=True` and `forwarded_allow_ips="*"`: behind a platform proxy the
peer address is the proxy's, and without this every caller would share one identity and
the per-user rate limit below would silently collapse into a global one.

**A `Dockerfile`, in two stages.** `workbench/app/dist` is gitignored — the built frontend
is an artifact, never a committed file — so the image builds it with Node and copies it
into the Python stage. `.dockerignore` keeps `.git` (16 MB), `Plan Examples/` (6.9 MB) and
`dist/` (5.7 MB) out; none is read at runtime, and `corpus.py:23` says of the last that it
is "a build artifact."

**A password gate** (`workbench/server/auth.py`). One shared password, because that is what
a small private reference wants — not accounts. It keeps three states apart in the way the
rest of the system keeps its three: satisfied, not met, and *not configured at all*. The
third is the local default, and `/api/health` reports it in words rather than letting an
absent check read as a passed one. `/api/health` is itself never gated, because the
platform's healthcheck arrives with no cookie and a gated health endpoint fails every
deploy. Only `/api/*` is gated: the static shell must load in order to draw the password
screen, and it carries no corpus data.

Identity is answered in the same module because the rate limiter needs a stable per-caller
string. A shared password gives no real identity, so each successful login mints a random
subject — two people who typed the same password still get separate budgets. A
`Cf-Access-Authenticated-User-Email` header outranks that, but only when
`WORKBENCH_TRUST_PROXY_AUTH` says a proxy which sets it is genuinely in front — see the
audit below for why that flag exists. Putting Cloudflare Access in front later is
therefore configuration, not a rewrite.

**The rail's key is read once, and stripped** (`workbench/server/rail.py`). `bool(
os.environ.get("ANTHROPIC_API_KEY"))` is true of a key pasted with a trailing newline, and
a newline is not a legal header value — so `/api/health` reported the rail available and
every turn then failed inside the SDK. The rail claiming it can answer and then not
answering is the collapse this project refuses everywhere else, and it should not be
reachable by a paste. `rail.key()` strips, returns None for nothing usable, and is the
single reader: health, the turn's own gate and the client the turn builds all go through
it, so no two of them can disagree about whether the rail is on.

`/api/health` also sends `Cache-Control: no-store` now. It is the endpoint an operator
refreshes to see whether a change took effect and it carries no validators, so a
heuristically cached 200 answers with the state from before the change — which reads
exactly like the change not working. The client had the same hole from the other side:
`fresh: true` skipped the app's own map and then took the browser's cache, which is not
what the flag promises its one caller.

**Caps on the rail** (`workbench/server/limits.py`). Two different things needed bounding
and only one of them is a rate.

The rate is the obvious half: `RAIL_TURNS_PER_HOUR` per identity (20), and
`RAIL_TURNS_PER_DAY` (200) process-wide as a backstop so one shared password cannot become
an open tap.

The size is the half that actually mattered, and it was the sharpest finding of this
package. `rail.stream_turn` takes `messages` straight from the request body — the client
owns conversation state and replays the entire history every turn — and nothing bounded
that array. A single request could carry an arbitrarily long history and be billed for it
before any per-turn counter noticed. `RAIL_MAX_MESSAGES` (40) and `RAIL_MAX_CHARS` (200k)
are checked *before* the first API call, which is the only point at which checking them
saves anything; `test_oversized_history_refused_before_the_transport` asserts the transport
records zero calls.

Every refusal leaves by the same door the missing-key case already used: one SSE `error`
event carrying `honest: true`, which `client.js:75` already treats as terminal. A rail that
will not answer says why, in the voice it uses for everything else it cannot do. No
frontend change was needed to render any of it.

**The rail's model moved to `claude-sonnet-5`**, with `output_config.effort` (default
`medium`, `WORKBENCH_EFFORT`) and `max_tokens` raised from 2000 to 8000. See the finding
below — this is the one change in the package that its tests do not cover.

**The MCP server, over HTTP, at `/mcp`** (`workbench/server/mcp_mount.py`). §IX's other
audience now has an address. `mcp_server/server.py` is unchanged in what it does — the same
26 tools over the same `core.py` — and does not know which transport it is answering on;
stdio works exactly as before. Mounting rather than running a second service gives one
process, one origin, one auth boundary, and one copy of the corpus in memory.

The transport's DNS-rebinding protection has to know its own hostname, and that hostname
does not exist until the platform generates a domain — after the first deploy. Rather than
leave an ordering trap (set a variable you cannot know yet, or get 421 on everything),
`allowed_hosts()` discovers it from the environment: any `RAILWAY_*_DOMAIN` / `*_URL` and
the equivalents for other hosts, matched by shape as well as by name because this was
written without access to the platform's documentation. A wrong guess costs one unused
allowlist entry; a missed one costs a dead endpoint, and the asymmetry says scan wide.
`WORKBENCH_ALLOWED_HOSTS` remains for custom domains, and accepts a pasted URL as readily
as a bare host — the Host header carries no scheme, so an unparsed URL would match nothing
and fail exactly as silently.

Auth needed no new code: `auth.authorised()` already accepted a bearer token, so the gate's
path match simply widened. Clients connect with
`claude mcp add --transport http tdl https://<host>/mcp --header "Authorization: Bearer ..."`.

Three tools are metered — `tdl_check_plan`, `tdl_compose`, `tdl_place_plan`, the only ones
reaching heavy `core` functions and the single compose worker. The other 21 are corpus
lookups and stay free, because capping them would throttle exactly the progressive
disclosure `tdl_overview` instructs agents to perform. The limiter is *injected* into
`mcp_server` (`set_limiter`, the same seam as `rail.set_client_factory`) rather than
imported, so `mcp_server` keeps depending on nothing in `workbench/`, and stdio stays
unmetered. Its honest limitation: the cap is a shared bucket, not per-caller — the MCP
transport does not hand a tool function its request. That bounds total load on the worker
actually at risk, which is the thing worth bounding, and it is not per-user however much
the word "limit" might imply otherwise.

**CI** (`.github/workflows/ci.yml`), where there was no `.github/` at all: the corpus suite,
the workbench suite behind a real frontend build, the smoke script, and a `docker build`.
`build/check_all.py` now runs the workbench tests too, and reports them **SKIP** when the
web dependencies are absent rather than folding them into the pass count.

## What was found

**The size cap, not the rate cap, is the real bound on spend.** Recorded above; it is the
thing most likely to be got wrong by anyone adding a similar gate to a similar server.

**Neither cap is a spend cap.** No amount of application-level limiting is a ceiling in
dollars. The only true ceiling is the budget set on the key in the Anthropic Console. What
these caps do is slow the rate of approach and make one abusive caller bounded rather than
unbounded. The limiter is documented as doing exactly that and nothing more.

**The model switch is not covered by tests.** `test_rail_loop.py` drives a fake transport
that records `create()` kwargs but asserts nothing about them, so every rail test passes
regardless of which model or parameters are sent. The move to Sonnet 5 was checked by
reading rather than by running: the rail passes no `temperature`, `top_p` or `top_k`, sets
no `thinking`, and never prefills an assistant turn (the loop always appends a `user`
message last), so none of the parameters that model family removed are in play. The one
real behavioural consequence is that thinking now runs adaptively unless told otherwise and
those tokens count against `max_tokens` — which is why 2000 was raised and `effort` was set
explicitly. **One live turn against a real key should be run before the URL is shared.**

**`test_example_plan_no_traversal` depends on the frontend being built.** It asserts that a
traversal URL lands on the SPA catch-all and returns `index.html`, and `app.py` mounts that
catch-all only when `workbench/app/dist` exists. Run `pytest` against an unbuilt tree and
it fails for a reason unrelated to any change under test. The CI job therefore builds the
app *before* running the server tests, with a comment saying why.

**`check_all.py` must probe and run in the same interpreter.** The first version of the
workbench check probed `import fastapi` in its own process and then shelled out to a bare
`pytest` on `PATH` — which, on this machine, belongs to a different environment without
fastapi. The result was a missing dependency reported as a failing check: precisely the
collapse the corpus forbids everywhere else. It now probes and runs through
`sys.executable`.

**The first CI run found a nondeterminism the corpus has carried since the composer was
written.** Two composer tests passed here and failed on the runner. Not randomness —
`geometry.solve` is seeded at 7 and `compose.py` imports no RNG — but the corpus loaded
through unsorted `glob.glob`, which returns directory order, and `pick_partis` sorted on
`fit` alone. Python's sort being stable, ties fell back to insertion order, and `out[:limit]`
cut through the middle of one: for `briefs/family-georgian.json` four diagrams tie at fit
2.00 and only three survived, so *which diagram was never scored at all* was decided by
readdir. Fixed in two places, because either alone leaves the other half live — 33 corpus
globs wrapped in `sorted()`, and `pick_partis` given an id tie-break plus a rule never to
truncate through a tie group. The validator now ranks the whole tie, which is what it is
for. `tests/test_determinism.py` pins both halves. Worth stating plainly: this had nothing
to do with deployment, and nothing but CI would have found it.

**Four SDK behaviours that each ship a broken endpoint if missed.** Recorded because none
is discoverable from a stack trace after the fact. (1) `session_manager` does not exist
until `streamable_http_app()` has been called — it is created lazily — which fixes the
order the app must be built in. (2) A mounted sub-application's lifespan never runs, so the
*host* app has to enter `session_manager.run()`; without it every call raises "Task group
is not initialized". (3) It may be entered only once per instance, which is why the tests'
client fixture is module-scoped and why `build()` must not be called twice — a second call
makes a second manager while the mounted app still holds the first. (4) DNS-rebinding
protection is armed at localhost by default, so a real hostname answers `421 Misdirected
Request` to everything until `WORKBENCH_ALLOWED_HOSTS` names it — and passing a
non-localhost `host=` does *not* allowlist it, it merely disarms the protection and accepts
every Host and Origin, so that argument is never used here.

**Starlette's `Mount` does not match a bare prefix.** `Mount("/mcp")` compiles to
`^/mcp(?P<path>/.*)$`, so a POST to `/mcp` — the URL clients are given — fell through to
the SPA catch-all and answered `405 allow=GET`. The gate middleware normalises the path
before routing.

**The rail's tool loader was stubbing out the `mcp` package.** `workbench/server/tools.py`
faked `mcp.server.fastmcp` in `sys.modules` so it could read the 26 tool functions without
the SDK installed. With the SDK now a real dependency that stub was both unnecessary and
harmful — a fake `mcp` left in `sys.modules` poisons the genuine package for everything
importing it later in the same process. It now imports normally and keeps the stub only as
a fallback for an SDK-less environment.

**The compose job registry pins the service to one replica.** `jobs.py` holds `_JOBS = {}`
in process memory with a 30-minute TTL, and its pool is `ThreadPoolExecutor(max_workers=1)`.
Two consequences that are fine at this scale but must be known: a second replica cannot see
the first's jobs, so **replicas must stay at 1**; and compose runs serialize across all
users, so a second person waits behind the first. Recorded as OQ 36.

## What the adversarial audit found

Four independent auditors were run over the finished diff — edge cases and callers, test
meaningfulness, second-order risk, and repeats of each pattern elsewhere — with a brief to
find what was wrong rather than confirm what was right. Everything below was reproduced
before it was fixed, and re-verified after.

**Three ways in, none of which needed the password.**

*Path traversal, unauthenticated.* The SPA catch-all did
`FileResponse(os.path.join(APP_DIST, path))`, and `../../../../etc/passwd` escapes
`APP_DIST` while `os.path.isfile` agrees. The catch-all sits outside the gate on purpose —
the password screen has to load — so this served any file the process could read, to
anyone. The code is older than this package; binding `0.0.0.0` is what turned a local
curiosity into a remote hole, which is the whole lesson: *exposure changes the severity of
code you did not touch.* Now resolved against `realpath` and confined.

*A forged proxy header.* `authorised()` believed
`Cf-Access-Authenticated-User-Email` unconditionally. That header means something only
when Cloudflare Access is in front, because Access overwrites whatever the caller sent;
with nothing in front it is a string the caller chose. `curl -H 'Cf-Access-…: anyone'`
returned the whole corpus and all 26 tools. Now behind `WORKBENCH_TRUST_PROXY_AUTH`,
default off.

*Database credentials, served to the internet.* The environment scan added for hostname
discovery read `RAILWAY_DATABASE_URL=postgres://admin:hunter2@db.internal:5432/tdl` as the
"hostname" `admin:hunter2@db.internal:5432` — and `/api/health`, deliberately ungated for
the platform healthcheck, printed the allowlist. The scan-wide argument had a cost the
argument itself did not account for. Now: datastore keys skipped, userinfo stripped, and
the host list shown only to an authorised caller.

**And several ways to break it without malice.** A non-ASCII password returned 500 rather
than 401, because `hmac.compare_digest` refuses non-ASCII `str` — an accented password made
the deployment unenterable while the login screen said "not accepted". `/mcp` answered 403
to any request carrying an `Origin` header, because the SDK's origin list wants origins and
was handed hostnames; `claude mcp add` sends none, so the documented client worked and every
browser-based one was dead. The rail's env knobs crashed the module on an empty string. The
compose worker, the plan validator and the drawing endpoints were unmetered while the rail
and the MCP tools were capped — the same expensive machinery through a cheaper door.

**The one that only shows up when two changes meet.** Loading the tool functions by real
import instead of the old `sys.modules` stub meant the rail and the `/mcp` mount now share
one module object — so the limiter installed for the remote transport also fired for the
browser rail, on one shared bucket. An agent exhausting its hour made the UI refuse. The
cap now asks whether it *is* the remote transport.

**And a regression from the determinism fix itself.** Returning the whole tie group was
right for a narrow tie and wrong for a wide one: a style with no native parti leaves every
diagram on the same score, and taking all of them doubled compose time while adding nothing
the fit function knew. Measured at 10.4 s against 5.2 s. The expansion is now bounded, and
`pick_partis(limit=0)` no longer indexes from the end and returns the entire corpus.

**A corpus bug the audit found on the way past.** `core.check_measurements` dropped any
fault whose every test *errored* — not present, not clear, not unjudged, absent from the
summary counts. A fault that silently vanishes reads to a caller exactly like a fault that
passed, which is the one collapse this project forbids above all others. Errors now land in
`could_not_judge` carrying their reason, and that list is no longer truncated —
`build/plan_check.py` had already worked around the truncation by passing `limit=10**6`.

**And one the audit found by simply typing `pytest`.** `tests/conftest.py` and
`workbench/server/tests/conftest.py` both claimed the top-level module name `conftest`, so
collecting the two suites in one invocation gave nine collection errors — `from conftest
import ROOT` reaching the wrong file. Pre-existing, reproduces on `main`, and invisible to
everything that checks this repo, because `check_all.py` and CI both run the suites as
separate processes. A package marker fixes it; 393 tests now pass in one run.

**What the audit did NOT change**, with reasons, is in `docs/open-questions.md` 37 and 38:
`find_faults` cutting through tie groups up to 104 wide, and `resolve_kit.choose_pack`
reporting an unranked precedence tie as the author's ruling. Both are real; both are
product decisions about what a ranking means rather than patches, and taking either
unilaterally would be deciding something the corpus is supposed to put to a human.

## What it will actually carry

Measured 27 August 2026 on 4 vCPU / 16 GB, against a real server with a fresh plan per
request. Full method and tables in `docs/reports/infrastructure-audit.md` §2.

**Reading is comfortable for dozens of people at once.** `/api/health` sustains ~560 rps,
`/api/kit/{style}` ~170, `/api/search/index` ~105. None is close to saturated.

**Editing a plan is the ceiling, and the ceiling is about one person.** The Plan Workbench
re-evaluates on a 400 ms debounce after every change, and one `/api/plan/evaluate` costs
338 ms of CPU — so one person dragging a wall consumes roughly 85% of the server's entire
evaluate capacity. A second editor sees 899 ms p50, already past the debounce, so their
edits queue. Four see 2.0 s; eight see 4.2 s. Throughput is flat at ~2 evaluates a second
across the whole range, because it is one core, fully serialised.

**Composing is serialised globally** behind `ThreadPoolExecutor(max_workers=1)`, ~8 s a job,
one at a time, for everyone. That and the in-process job registry are why replicas stay at 1.

So "a handful of people trying it" is right for reading, and optimistic by about a factor of
two for editing. Four uvicorn workers would buy ~4x — measured — and would break compose,
because `_JOBS` is process memory: six jobs submitted across four workers, five answered 404
by a worker that had never seen them. That is OQ 36, and it now has numbers.

**Egress.** A cold visit downloads 1.70 MB uncompressed. The server gzips now, so it is
0.54 MB — 3.1x, and 1.15 MB saved per visitor, most of it the atlas's fine coastline tier.
Check whether the platform edge compresses too:
`curl -H 'Accept-Encoding: gzip' -sI https://<host>/assets/<hashed>.js | grep -i content-encoding`

## Running it, in order

Everything below is done once, by hand, in the named service's own UI.

1. **Anthropic Console** — create a *dedicated* API key for this deployment rather than
   reusing a personal one, and set a spend limit on its workspace. This is the only real
   dollar ceiling; everything in `limits.py` only slows the approach to it.
2. **Railway** — New Project → Deploy from GitHub repo → this repository, branch `main`.
   The `Dockerfile` is detected automatically; there is nothing to configure about the
   build.
3. **Railway → Variables** —
   - `WORKBENCH_PASSWORD` — the shared password.
   - `WORKBENCH_SECRET` — 32 random bytes (`python3 -c "import secrets;
     print(secrets.token_urlsafe(32))"`). Without it sessions still work but are signed
     with a per-process key, so everyone is logged out on every restart.
   - `ANTHROPIC_API_KEY` — the dedicated key from step 1.
   - `WORKBENCH_API_TOKEN` — the bearer token for non-browser callers. Required if you
     want the `/mcp` endpoint reachable; agents authenticate with nothing else.
   - `WORKBENCH_ALLOWED_HOSTS` — *usually unnecessary*. `mcp_mount` scans the environment
     for the hostname the platform advertises (`RAILWAY_*_DOMAIN`, `*_URL`, and the
     equivalents for other hosts) and allowlists it automatically, so `/mcp` works on a
     generated domain with nothing configured. Set this only for a custom domain, or if
     `/api/health` shows the platform's own host missing from `mcp.allowed_hosts`.
     A bare hostname or a full URL both work — it is normalised either way.
   - `PORT` — **set it explicitly**, and use the same number when the platform asks which
     port to route the domain to. Railway's "Generate Domain" dialog asks for a target
     port, and stating the number on both sides removes any dependence on the platform
     auto-injecting `PORT` or auto-detecting the listener. `8080` is a fine choice; the
     app falls back to 8177 only when nothing is set.
   - Optional tuning: `RAIL_TURNS_PER_HOUR`, `RAIL_TURNS_PER_DAY`, `RAIL_MAX_MESSAGES`,
     `RAIL_MAX_CHARS`, `RAIL_MAX_TOOL_ROUNDS`, `WORKBENCH_MODEL`, `WORKBENCH_EFFORT`,
     `HEAVY_CALLS_PER_HOUR` (compose/evaluate/drawings, per user, default 60),
     `MCP_HEAVY_CALLS_PER_HOUR` (the three heavy MCP tools, default 60).
   - `WORKBENCH_TRUST_PROXY_AUTH` — **leave unset.** Setting it makes the server believe
     `Cf-Access-Authenticated-User-Email`, which is only an identity when a proxy that
     overwrites the header is guaranteed to sit in front of every request. On a bare
     platform deployment, setting this is an open door: anyone can send that header.
4. **Railway → Settings → Deploy** — healthcheck path `/api/health`; **replicas 1**, for
   the reason under "what was found".
5. **Railway → Settings → Networking** — Generate Domain. It asks which port to route
   to: give it the same number as `PORT` above. No public domain exists until this step,
   which is why the hostname cannot be known in advance — and why the allowlist is
   discovered from the environment rather than configured ahead of it.
6. **Railway → Settings** — enable "Wait for CI" so a deploy only fires on green.
7. **GitHub → Settings → Branches** — require the `corpus`, `workbench` and `image` checks
   on `main`.
8. Send the URL and the password. A visitor needs nothing installed.
9. For agents, hand out the token instead:
   ```
   claude mcp add --transport http tdl https://<host>/mcp \
     --header "Authorization: Bearer $WORKBENCH_API_TOKEN"
   ```

Locally nothing has changed: `make workbench` still serves `http://127.0.0.1:8177` with no
password, and prints a note saying the server is open when none is set.

## Deliberately not done

**Regenerating `dist/*.html` in CI.** `check_all.py` runs `build.py` (which rebuilds
`dist/taxonomy.json`) but not `render_html.py` or `render_orders.py`, so the committed
`taxonomy.html` and `orders.html` can still drift from the corpus with nothing to catch it.
Harmless while they are read locally; visible to other people once anything is published.
Named here rather than fixed.

**A root `requirements.txt`.** The corpus's own dependencies (`jsonschema`, `pytest`) are
still install-by-README; CI installs them explicitly. Worth adding separately.

**Per-user-type views.** VISION.md §IX names three human audiences, and it was tempting to
give each an entry point. They want the same corpus with different emphases, and the
workbench already carries all three affordances, so role-based anything would have been
complexity serving nobody.
