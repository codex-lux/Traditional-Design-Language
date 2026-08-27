# The infrastructure audit

*27 August 2026. Storage, concurrency, pooling, scaling and security for the Railway
deployment, on branch `claude/infrastructure-resilience-audit-v8p598`.*

The workbench was made deployable on 25 August and `docs/deployment.md` is a careful account
of that package, including an adversarial audit that found three unauthenticated ways in.
What had never been done is a **resource** audit: nobody had measured what the deployment
costs in storage, how many people it serves before it queues, or what breaks first under
load. `docs/deployment.md` names the scale it was built for — "a handful of people trying
it" — and OQ 36 records the ceiling that assumption bought without measuring where it sits.

This report measures it. Every figure below is marked **measured** or **estimated**, and no
estimate is dressed as a measurement.

---

## 0. What could not be done here, and what Lucas has to read off the dashboard

**Live Railway metrics are unreachable from this environment.** The egress proxy answers
`403` to `CONNECT` for the deployment's own hostname — the same organisation policy denial
that blocks `www.loc.gov` for WP-4.4:

```
curl https://traditional-design-language-production.up.railway.app/api/health
  -> curl: (56) CONNECT tunnel failed, response 403
```

There is no `railway` CLI and no token in the environment, and Railway's API would be denied
identically. **There is also no usable Docker daemon**, so the image could not be built and
weighed; it is weighed by parts instead, and the total is labelled an estimate.

Seven things only the dashboard can answer. The first is the one that matters today:

1. **`/api/health` → is `auth.required` true?** Commit `bc2dfec` read this off the running
   service on 26 August and found `auth: {"required": false, "note": "no WORKBENCH_PASSWORD
   is set"}`. `4dcb06a` records that the shared variables had not been attached to the
   Railway project and that they then were — but not whether `WORKBENCH_PASSWORD` was among
   them. If it was not, the server is open, and open includes `POST /api/rail/messages`,
   which spends the `ANTHROPIC_API_KEY`. `limits.py:16-18` says plainly that its caps are
   "not a spend cap in dollars."
   ```
   curl -s https://<host>/api/health | grep -o '"auth":{[^}]*}'
   ```
2. Railway plan tier, and the service's vCPU and RAM limits. Everything in §2 is measured on
   4 vCPU / 16 GB and scales with the first of those.
3. Observed memory and CPU under normal use; any OOM kills or restarts.
4. Egress GB for the current period — §3 says what this audit changed about it.
5. Image size and build time from the most recent deploy log, against §1's estimate.
6. Whether the edge already compresses:
   `curl -H 'Accept-Encoding: gzip' -sI https://<host>/assets/<hashed>.js | grep -i content-encoding`
7. Anthropic Console: spend to date on this key, and whether a workspace budget cap is set.

---

## 1. Storage

**There is no volume and no database, so storage is the container image.** The only runtime
writes are `tempfile` round-trips in `corpus.py` (`drawing()`, `export_cad()`,
`ingest_dxf()`), each unlinked in a `finally`. Railway bills compute and egress here, not
disk.

| layer | size | |
|---|---:|---|
| `python:3.11-slim` base | ~130 MB | estimated (published size) |
| `workbench/requirements.txt`, unpacked | **581 MB** | measured |
| the repo, minus `.dockerignore` (`COPY . .`) | 20 MB | measured |
| the built frontend (stage 1) | 2 MB | measured |
| **estimated image** | **~733 MB** | exact needs one `docker build` |

**The dependency layer is 85.5% optional libraries.** Measured by installing each set with
`pip install --target`:

| set | size |
|---|---:|
| server + rail + MCP only | 84 MB |
| the same plus `ezdxf`, `ifcopenshell`, `ortools` | 581 MB |
| **the three optional libraries and their transitive deps** | **497 MB** |

`ifcopenshell` alone is 189 MB, `ortools` 80 MB, and between them they drag in `pandas`
(76 MB), `numpy` (73 MB with its bundled libs), `fontTools` (28 MB) and `shapely` (12 MB).
All three are optional *at runtime* by design — `geometry.solve` falls back to the heuristic
and says so, and the export endpoints refuse honestly with a 501 — but they are not optional
in the image, because the Dockerfile installs the file wholesale.

Whether to drop them is a product decision and is left as an open question, not taken here.

**Corrections to `docs/deployment.md`.** It states the corpus is "27 MB". Measured: **725
JSON files, 12.3 MB**, and the whole shipped tree is 20 MB. Corrected in that file.

**Fixed:** `pytest` and `httpx` were being built into the production image, because the
Dockerfile installs `workbench/requirements.txt` wholesale and they were in it. Split into
`workbench/requirements-dev.txt`; CI installs both; no runtime module imports either. **20 MB
measured**, which is small beside the 497 MB above but is pure waste.

---

## 2. Concurrency: where the ceiling is

Measured against a real uvicorn server on 4 vCPU / 16 GB, three runs per point, each request
carrying a **fresh plan** so the solve cache cannot answer for the solver. `HEAVY_CALLS_PER_HOUR`
was raised for the run — at its default of 60 the sweep would measure the rate limiter.

**p50 latency, milliseconds, by concurrent callers (single process, as deployed):**

| endpoint | 1 | 2 | 4 | 8 | 16 | sustained rps |
|---|---:|---:|---:|---:|---:|---:|
| `GET /api/health` | 3 | 4 | 6 | 11 | 14 | ~550 |
| `GET /api/kit/{style}` | 7 | 12 | 23 | 47 | 62 | ~150 |
| `GET /api/search/index` | 14 | 24 | 39 | 89 | 115 | ~65–97 |
| `POST /api/drawings/plan` | 208 | 452 | 956 | 1881 | 2888 | **~4.5** |
| `POST /api/plan/evaluate` | **327** | 934 | 2167 | 3970 | 6256 | **~2.0** |

*Re-measured with `Accept-Encoding: gzip` actually sent — see §3. The first version of this
table did not send it, so the read endpoints were faster there than a browser will ever see
them; `/api/search/index` in particular reads 14 ms rather than 10.*

**Read the last column, not the first row.** Throughput is flat across the whole ladder —
about 2 evaluates and 4.5 drawings per second no matter how many callers arrive. That is a
single core, fully serialised. Concurrency does not buy throughput here; it only buys queue.

**The answer to "how many users simultaneously."** It depends entirely on what they are
doing, and the two answers are three orders of magnitude apart:

- **Reading** — browsing styles, kits, faults, the atlas — is comfortable for **dozens to a
  hundred** concurrent people. Those endpoints run at 100–560 rps and none is close to
  saturated.
- **Editing a plan** is the ceiling, and the ceiling is **roughly one person.**
  `PlanWorkbench.jsx:117` re-evaluates on a 400 ms debounce after every plan change, and one
  evaluate costs 338 ms of CPU. One person dragging a wall therefore consumes about **85% of
  the server's entire evaluate capacity.** A second editor puts p50 at 899 ms — already past
  the debounce, so their edits queue behind each other. Four editors see 2.0 s, eight see
  4.2 s.
- **Composing** is serialised globally behind `ThreadPoolExecutor(max_workers=1)`
  (`jobs.py:16`), ~8 s a job, one at a time, for everyone.

So `docs/deployment.md`'s "a handful of people trying it" is right for reading and optimistic
by about a factor of two for editing.

### What the single-process constraint costs, measured

Run with `--workers 4` on the same box:

| | 1 worker | 4 workers | |
|---|---:|---:|---|
| `/api/plan/evaluate` p50 @ c=16 | 6414 ms | 1380 ms | **4.6× better** |
| `/api/plan/evaluate` rps | 1.7 | 6.1 | 3.6× |
| `/api/drawings/plan` p50 @ c=16 | 2901 ms | 672 ms | 4.3× |
| `/api/drawings/plan` rps | 4.2 | 14.0 | 3.3× |

Memory is not what stops this. **The corpus costs ~33 MB resident and 0.09 s to load**
(measured: 722 files, 12.3 MB raw, 2.7× expansion); a warm worker sits around 150–200 MB with
the interpreter and dependencies. Four workers is affordable on any Railway tier that runs
this at all.

**What stops it is OQ 36, and this is the demonstration that entry has been missing.** With
four workers, six composes were submitted and then polled once each:

```
  found 1, lost 5 of 6      — HTTP 404, "the worker that owns it is not the one that answered"
```

`_JOBS` is process memory, so a load-balanced hop lands on a worker that never saw the job.
Four workers buys ~4× on everything and breaks compose five times in six. That is the trade
OQ 36 has to rule on; this audit supplies the numbers and stops.

### Fixed: event streams stopped costing a thread

`jobs.events` was a sync generator whose loop blocked on `job.events.get(timeout=1.0)`.
Starlette wraps a sync iterator in `iterate_in_threadpool`, one anyio threadpool token per
`next()` — and because that `next()` was a blocking wait, an open compose stream held a token
for its entire life rather than for the instant it took to produce a line. The pool is 40
wide for the whole application.

`/api/health` latency while N event streams are held open:

| streams | 8 | 24 | 48 | 80 |
|---|---:|---:|---:|---:|
| before | 25 ms | 40 ms | 194 ms | **1021 ms** |
| after | 19 ms | 4 ms | 13 ms | **11 ms** |

**The earlier claim that forty streams stop the server outright was too strong**, and the
measurement is what corrected it: each blocking `get` releases its token after the 1 s
timeout, so it degrades steeply rather than deadlocking. 40× at eighty streams is the honest
figure. Health still answers — it answers in a second, which a tight healthcheck timeout
reads as a dead container.

---

## 3. Pooling, and what crosses the wire

**There is no database, so there is no connection pool to tune.** The pooling that applies is
to the Anthropic API, and it was absent: `rail.py` called `anthropic.Anthropic()` inside
`stream_turn`, and every one of those builds its own `httpx.Client` with its own connection
pool. Each turn paid a fresh TCP handshake and TLS negotiation before its first token and
dropped the sockets to the garbage collector afterwards. The eight tool rounds *within* one
turn already shared a client; nothing shared across turns, which is the boundary a keep-alive
is for. **Fixed** — pooled, keyed on the API key so a rotated key still takes effect rather
than the cache becoming the one reader that disagrees with the rest of the file.

**Nothing was compressed.** `app.py` registered exactly one middleware, the auth gate.
Measured against a running server:

| | uncompressed | gzipped | |
|---|---:|---:|---:|
| `/api/search/index` | 205,784 B | 51,964 B | 4.0× |
| `/api/phylogeny` | 151,457 B | 30,349 B | 5.0× |
| `/api/vocabulary` | 82,589 B | 12,758 B | 6.5× |
| **the whole frontend, per cold visit** | **1.70 MB** | **0.54 MB** | **3.1×** |

That last row is the one that shows up on an egress bill: **1.15 MB saved per cold visitor**,
most of it the atlas's fine coastline tier, which OQ 72 costs at "363 KB gzipped" — a figure
that was only ever true in principle, because nothing gzipped it.

`GZipMiddleware` alone would have broken both event streams: Starlette buffers a streaming
response, which turns a live progress line into a long pause and then everything at once. SSE
is exempted **by path**, before the compressor sees the request. Verified both ways — with
`Accept-Encoding: gzip` the compose stream still answers with no `content-encoding`, and its
first line arrives at 0.01 s of a 9.9 s job.

**Compression is not free, and the first version of this report said it was.** That claim came
from a sweep that never exercised it: `workbench/scripts/load.py` drove everything through
`urllib.request`, which sends no `Accept-Encoding` header, so every "after" run measured the
UNCOMPRESSED path. With the header sent, `/api/search/index` p50 goes from 9.7 ms to 13.9 ms at
one caller and its sustained rate from ~105 to ~65–97 rps. That is the real trade: **roughly a
third more CPU on the largest read endpoint, for four times fewer bytes.** Worth it on a
platform that bills egress; not worth hiding.

Two settings make it affordable rather than ruinous, and both were wrong when first shipped:

* **Level 4, not Starlette's default of 9.** For `/api/search/index`: level 9 costs 9.01 ms and
  emits 52,293 bytes; level 4 costs 2.58 ms and emits 54,937. 3.5× the CPU for 4.6% fewer bytes.
* **`/assets` is not compressed per request at all.** It was, and that was the single worst
  thing on the server: the 1.19 MB bundle cost **569 ms** at level 9 and 38 ms even at level 4,
  against 8 ms plain — on a route outside both the auth gate and the rate limiter, and on the
  EVENT LOOP, because `FileResponse` streams in 64 KiB chunks and Starlette only offloads a
  chunk of 128 KiB or more. At level 9 one anonymous caller at 1.76 req/s saturated the core,
  making a static GET five times more expensive than `/api/plan/evaluate` — the endpoint §2
  calls the ceiling. `workbench/scripts/precompress.py` now writes a `.gz` beside each asset at
  build time and `ImmutableStatic` serves it: **9.6 ms**, at level-9 ratios, with zero
  per-request compression.

**Also fixed:** things rebuilt per request that cannot change under a running server —
`plan.schema.json` and `brief.schema.json` re-parsed at six sites including `core.check_plan`
(which runs behind that 400 ms debounce), `core.list_partis` re-globbing and re-parsing all 21
parti files a call (0.95 ms → 0.012 ms), and `/assets` carrying no cache headers despite Vite
content-hashing every filename.

**And one "fix" that was a 7.8× pessimisation, reverted.** This section previously claimed
`/api/phylogeny` as a win of the same kind. It was not: measured, the rebuild walks
already-in-memory `core._data()` at **0.23 ms**, while the cache returned `core.copy_json()` of
the result at **1.79 ms** — `copy_json` is `json.loads(json.dumps(o))` over 157 KB. The endpoint
costs 20.79 ms end to end, so the build was 1.1% of it and the rest is FastAPI's encoder. The
premise was wrong too: `search_index`'s rebuild really is expensive (2.74 ms, and it re-globs 21
files) and it returns the **shared** object with no copy. Caching phylogeny was slower than doing
nothing and inconsistent with the neighbour it claimed to imitate. Reverted, with a test that
pins the relation rather than a wall-clock number.

---

## 4. Security

### The live one: a path traversal the previous audit believed it had closed

`mcp_server/core.py` has carried `os.path.basename(str(parti))` since the 25 August audit,
with a comment saying it covered "`/api/plan/evaluate` and `/api/drawings/{kind}`". It covered
the first. **`/api/drawings/{kind}` does not route through `place_plan` at all** —
`workbench/server/corpus.py` had its own two copies of the join, both unsanitised:

```python
f = _os.path.join(ROOT, "partis", f"{parti}.json")   # corpus.py, twice
```

`parti` is `body.get("parti")`. A relative id traverses and an absolute one wins the join
outright. Contents are never returned — the file becomes a parti template inside `geo.solve`
— so this is a filesystem existence-and-JSON-validity oracle plus whatever a foreign
structure discloses through an error string. Medium severity, and anonymous if no password is
set.

**Fixed as a class rather than as two instances.** `core.load_parti` is now the only place a
caller-supplied parti id may become a path, all three call sites go through it, and a test
fails if a fourth copy appears anywhere in the tree — the same shape as
`test_grammar_agreement.py` for the citation grammar's three spellings.

### Re-verifying the three 25 August fixes

Each was reverted, the whole suite run, and the fix restored:

| fix | did the suite catch its reversion? |
|---|---|
| forged `Cf-Access-Authenticated-User-Email` | **caught** |
| `RAILWAY_DATABASE_URL` into the MCP allowlist | **caught** |
| the userinfo strip beside it | **caught** |
| **the SPA catch-all's path confinement** | **NOT caught** — 142 tests passed with it deleted |

The uncaught one is the most severe of the three: an unauthenticated arbitrary file read, on
a route deliberately outside the gate so the password screen can load.

**Its severity, measured rather than assumed**, because the honest answer changes what to do.
With the confinement removed, a running server was attacked with `../../../CLAUDE.md`,
`..%2f..%2f`, `..%2F..%2F`, `%2e%2e/%2e%2e/` and `....//....//` via `curl --path-as-is`. **All
five were blocked** — uvicorn normalises the path before routing, so the traversal never
reaches the handler. Called directly, `spa("../../../CLAUDE.md")` returns a path outside
`APP_DIST`.

So the fix is defence in depth rather than the only thing between the internet and the
filesystem, and `docs/deployment.md` slightly overstates the live exposure. It is still worth
keeping and now has a test, which calls the handler directly — where the property lives —
rather than through a client that normalises the attack away before it arrives.

### Bounds added

Nothing at any layer bounded a request body: not uvicorn, not Starlette, not FastAPI, and not
`schema/plan.schema.json`, which carries no `maxItems` on `levels[].rooms` and no `maxLength`
on a name. Every heavy endpoint's cost scales with the body it is handed.

- **8 MB body cap**, refused on `Content-Length` before anything reads it, plus an ASGI
  middleware counting a chunked body as it streams. The largest real plan is 26 KB.
- **The label fitter, again.** `MAX_WORDS = 12` bounded how many *arrangements* are searched,
  never how much text each is costed over. So the 73-second bomb closed and a quieter one
  stayed open: **twelve words of 20,000 characters measured 1466 ms**, per room, with room
  count unbounded. The cap now falls on the search, not the text, because the rule above the
  function holds — a name is drawn whole or not at all. **1466 ms → 132 ms**, every character
  preserved.
- **The solve cache held the serialised plan inside its own key**, 64 retained. sha256 now,
  and a plan over 1 MB is solved and returned but not remembered.
- `/api/dev/reload` metered — it forces the ~600 ms corpus reload and was the one heavy route
  outside the heavy bucket.
- `POST /api/compose` clamped — it read `candidates` raw while every sibling used
  `_candidates()`, so a non-numeric value raised `ValueError` into an unhandled 500.
- `face` escaped in `render_elevation.py` — user-supplied, interpolated into SVG that
  `DrawingSet.jsx` renders with `dangerouslySetInnerHTML`, protected only by an incidental
  `KeyError` 38 lines earlier.
- `.env`, `*.pem`, `*.key` added to `.gitignore`.

### Confirmed clean

No CORS middleware anywhere — correct, since same-origin plus `samesite=lax` blocks
cross-site reads. `REF_RE` and `CITE_RE` are linear with no backtracking risk. No `eval`,
`subprocess` or `pickle` on any server-reachable path — the `eval` in `check_systems.py` and
`check_modules.py` is CLI-only with `__builtins__` stripped. Every `modcache` load path is a
literal; no user input reaches a module path. No secrets committed. Non-root container user.
The session cookie is `httponly`, so no token is ever readable from JavaScript.

---

## 5. On testing, which is half of what this audit found

Sixteen assertions were written across five new files. **Every one was mutation-checked** —
the fix removed, the test confirmed to fail, the fix restored — and that pass caught **six
tests that could not fail**, before any of them were committed:

1. Three endpoint tests asserting `status_code != 500` on a traversal. All three passed with
   the `basename` removed: a foreign JSON file does not crash the pipeline, so there is no
   observable difference at the HTTP boundary. Rewritten as spies on `core.load_parti`.
2. An evaluate test passing `place: False`, so placement never ran and no parti was ever
   loaded. It was exercising nothing.
3. The label-fitter test compared 12 words of 200 characters against 12 words of 4000 — both
   long, both taking the same path with or without the cap, ratio linear either way.
   Rewritten to compare a 12-word name against the 3-word name it chunks into: **4.0× with
   the cap, 46.2× without.**
4. The SSE compression test opened a real stream and asserted `content-encoding` was not
   gzip. It passed with the exemption **deleted** — Starlette holds a streaming response
   uncompressed until it exceeds `minimum_size`, and the first SSE chunk is a few dozen
   bytes. Rewritten to assert the middleware's dispatch.
5. The phylogeny cache test asserted `_PHYLOGENY is not None` after a call — which the
   *uncached* version also satisfies, since it assigns on the way out. The second call is
   made with `core._data` booby-trapped now.
6. A guard pinned `mcp_server/core.py:859` and went red when an unrelated function was added
   above it. Brittle rather than weak, but it would have been silenced.

**The load harness had the same disease, twice.** It first slept three seconds, probed
`/api/health`, and printed a number — and at 80 and 120 streams it reported **four
milliseconds**, faster than the eight-stream case, because the compose had finished, every
stream had closed, and it was timing an idle server. A load test whose most-loaded points are
its fastest is measuring nothing. It now checks the job is running on both sides of the probe
and reports **COULD NOT EVALUATE** rather than a number it cannot stand behind.

Then the sweep replayed one identical plan, and `geometry.py` keys `_SOLVE_CACHE` on
`json.dumps(plan)`. `POST /api/drawings/plan` measured **5.0 ms p50** — faster than a kit
lookup, for an endpoint that solves a plan and renders an SVG. With a fresh plan id per
request: **215.3 ms**, 43× more.

One mutation silently failed to apply during the re-verification pass and the harness printed
NOT CAUGHT. An `assert` that the source actually changed is what turned that into a visible
failure rather than a false clean bill; it is in the harness now.

**Then a third harness defect, found by the audit of this audit: the sweep never sent
`Accept-Encoding`.** `urllib.request` does not by default, so every run — including the one
used to say compression cost nothing — measured the uncompressed path. Three separate
occasions on which this instrument reported confidently about something it was not touching:
an idle server read as the most-loaded point, a solve cache read as the solver, and now an
uncompressed path read as the compressed one. The pattern is worth more than the three
incidents: **an instrument that cannot fail is as dangerous as a test that cannot fail, and it
is harder to notice, because its output is a number rather than a green tick.**

---

## 6. Found on the way past, reported rather than fixed

- **The corpus suite goes red in a fresh virtualenv.** Nine root tests shell out to a bare
  `python3` on the assumption that the runner's interpreter is the minimal one and `python3`
  is the equipped one — `tests/test_proportion_engine.py:16` says so deliberately. In a venv
  carrying the project's dependencies it is the other way round, and they fail with
  `ModuleNotFoundError: No module named 'jsonschema'`. The codebase is split:
  `test_counts_guard` and `test_parti_composability` use `sys.executable`;
  `test_constraints`, `test_ontology`, `test_kit_cascade` and `test_proportion_bands` use
  `"python3"`. Which half is right depends on how the contributor installed. Same class as
  the trap CLAUDE.md already records for `check_all.py`.
- **`geometry.solve` mutates its input on a cache MISS and not on a HIT**, so an in-process
  caller that reuses one dict never hits the cache and grows it by one per call. The server
  path is safe — `place_plan` copies first.
- **No Python lockfile.** Neither requirements file pins exact versions, so two builds of one
  commit can ship different dependency trees. Only two packages carry upper bounds, and both
  were added reactively after a breakage. The frontend is better: `npm ci` against a committed
  `package-lock.json`.
- **`/api/health` enumerates corpus counts and configuration to unauthenticated callers**,
  by design, so the platform healthcheck works. It already redacts `allowed_hosts`.

## 7. New open questions

Raised by this audit and recorded in `docs/open-questions.md`: **73** (refusing to bind
`0.0.0.0` with no gate configured), **74** (`engine: "cp"` accepted from a request body, worth
a 25–30 s blocking solve), **75** (dropping the 497 MB of optional libraries from the image),
**76** (the heavy limiter simultaneously too loose for ten users and too tight for one), and
**77** (a Python lockfile).

## 7b. The audit of this audit

Three independent read-only auditors were run over the finished branch — edge cases and the
full caller chain, test meaningfulness, second-order risk and repeated patterns — with a brief
to break it rather than confirm it. **None of what follows was caught by the 148 tests that
were green when the branch was first declared done.**

**Critical, and mine.** Dynamic gzip over `/assets` was an unauthenticated CPU amplifier:
569 ms for the 1.19 MB bundle at Starlette's default level 9, on the event loop, on a route
outside both the auth gate and the rate limiter. Fixed by build-time precompression (§3).

**A "fix" that was a 7.8× pessimisation.** The phylogeny cache. Reverted (§3).

**A hand-rolled middleware that Starlette already ships, and mine was wrong in four ways.**
`BodyLimit` returned 500 rather than 413 on `/api/rail/messages` (which reads its body
directly, so nothing converted the resulting `ClientDisconnect`), delivered the handler's parse
error rather than its own message where it did fire, bounded nothing on a handler that never
reads its body, and had its entire streaming half untested — `TestClient` always sends
`Content-Length`, so deleting the middleware left the test green. Replaced with
`RequestBodyLimitMiddleware`, registered **inside** the auth gate: the gate is a
`BaseHTTPMiddleware`, which wraps `receive` in an anyio task group, and an exception raised
inside that wrapper surfaces as an `ExceptionGroup` the limiter's own handler never matches.
Both orders were measured; only one produces a 413.

**The same bug I had just fixed, next door, left unfixed.** `rail.stream_turn` is a sync
generator making up to nine blocking Anthropic calls, handed to `StreamingResponse` — the
identical `iterate_in_threadpool` mechanism, and strictly worse than the one in `jobs.events`,
which at least released its token every second. Worse still, the CLAUDE.md rule I added in the
same commit says every SSE route's body must be an async generator, so I shipped a rule the
codebase broke. Bridged onto a dedicated thread rather than rewriting the one module that
spends real money and cannot be verified end to end from here.

**`/mcp` is a third SSE route** and was missing from the exemption list, protected only by a
Starlette content-type default that no requirements pin guarantees.

**A new unsanitised path join, in the commit that consolidated path joins.** `core.schema()`
built `schema/{name}.schema.json` with no `basename`, one screen above `load_parti`'s docstring
saying that must never happen. Not live — no caller passes user input, and every
`*.schema.json` lives in `schema/`, so the mandatory suffix confines it anyway — but fixed and
guarded, because "one endpoint away from live" is that docstring's whole argument.

**`index.html` had no `Cache-Control` at all**, while `ImmutableStatic`'s docstring asserted it
"must stay revalidated". With `/assets` immutable for a year that response is the only thing
that can carry a deploy to a returning visitor. Now `no-cache`, with a test.

**`core.list_partis` re-globbed and re-parsed all 21 parti files per call** — the same bug the
search-index comment describes fixing, one function over. And `corpus.invalidate()` missed
`citations._parti_ids` and `_constraint_ids`, so `/api/dev/reload` left a newly added parti
uncitable for the life of the process.

**`/api/check/measurements` read `body.get("limit", 40)` raw** — the sibling the compose fix
claimed was "the one heavy route reading the value raw." It was not the one.

**Six more tests that could not fail**, on top of the six caught during the first pass: two of
four parti escape parameters were duds (`../../etc/passwd` lands above the repo; the
percent-encoded one contains no `/`, so `basename` is the identity function and nothing
decodes it), the fitter completeness test asserted non-truncation rather than the cap, the
compose test asserted a 500 `TestClient` can never show, the immutable-assets test grepped
source text that its own docstring satisfied, the heartbeat test multiplied two constants the
fix itself introduced, and `invalidate`'s search-index assertion passed on a cache an unrelated
test 130 lines earlier had filled. All rewritten and mutation-checked.

**Deliberately not changed**, with reasons: the `>1 MB` solve-cache skip is a memory-for-CPU
trade and the right way round (bounded by the body cap and 60 calls/hour, against 640 MB of
retained plans); `HEAD /` returning 405 on the SPA catch-all is pre-existing on `main` and out
of scope; the 8 MB body cap means a ~6.6 MB ceiling on an uploaded DXF after JSON escaping,
which no shipped drawing approaches but a drafter's real floor plan eventually will.

## 8. Verification

```
python3 build/check_all.py                       # all 33 checks pass
python3 -m pytest workbench/server/tests -q      # 148 passed
python3 -m pytest tests/ -q                      # 833 passed, 19 skipped
python3 workbench/scripts/load.py --sweep --url http://127.0.0.1:8178
python3 workbench/scripts/load.py --sse --streams 48 --url http://127.0.0.1:8178
```

The load harness needs a server you started yourself and, for the sweep to measure the
server rather than the rate limiter, `HEAVY_CALLS_PER_HOUR` raised for that run.
