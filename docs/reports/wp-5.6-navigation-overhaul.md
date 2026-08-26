# WP-5.6 — The navigation overhaul

Lucas, 26 Aug 2026: *"I'm finding the interface to be extraordinarily overwhelming. It's
very thorough and exhaustive, but it's very painfully difficult to navigate with all of the
different filters and all of the different modules. There's no apparent search bar anywhere
for anything… I don't want to compromise the machine usability aspect of this."*

That last clause is the constraint that shaped everything below. The workbench is two
products in one frame: a thing a person reads, and a thing an agent drives through `/mcp`
and the rail. The complaint was entirely about the first. The risk was that fixing it would
quietly damage the second.

---

## 1. The finding that organised the work

**The product already had a complete addressing scheme and was not using it for navigation.**

`app/src/citations.js` held `routeCite()`, which turns `fault:porch-too-shallow-to-inhabit`
into `{surface, selection}`. The rail validates every citation against live corpus ids
before streaming it; `server/citations.py` exists for nothing else. Every cross-surface link
in the product already travelled through it.

And navigation was a `useState` string. So the citation grammar — a precise, validated,
machine-facing way to name any record in the corpus — named *nothing* the browser could
hold. A refresh always landed on the Plan Workbench. The back button left the app. No view
could be handed to anybody.

Once that was seen, the shape of the package followed. The URL is that pair written down.
The command palette dispatches by citation. Filters are the same URL's query. `#/cite/…`
makes a citation a link a person can click, which means the rail can now hand a human a
place rather than a string. **One addressing scheme, three audiences** — the reader, the
rail, and anything driving the HTTP API — instead of one scheme for machines and a
disconnected pile of component state for people.

---

## 2. What was built

Seven stages, each landing green on its own.

| | |
|---|---|
| **A** | `router.js` (pure `parseHash`/`formatHash`), `state/nav.js` (a fourth external store, backed by `location.hash`), `citeFor()` as the inverse of `routeCite` |
| **B** | `GET /api/search/index` + `search/match.js` + the `⌘K` palette + `keys.js` |
| **C** | `filters/useFilters.js`, `FilterInput`, `StylePicker`, `useStyles`, and the `Chip`/`ActionChip`/`ChipGroup`/`FilterGroup` split |
| **D** | the `Overview` surface, and the left rail regrouped by errand |
| **E** | per-surface density passes; `AiRail.jsx` rewritten from precompiled output |
| **G** | the Phylogeny's map reading, `?view=map` |
| **F** | the machine-usability audit, docs, this report |

18 new files, no new npm dependency. The app still has exactly two: `react`, `react-dom`.

### The URL scheme

```
#/                                   the Overview
#/<surface>/<id>[/<sub-id>]          #/kit/tidewater-georgian/cornice
#/cite/<kind>:<id>                   a citation, verbatim, as a link
#/<surface>/<id>?sev=serious&q=porch filters, in the query
#/phylogeny?view=map                 which reading of a surface you are in
```

Place changes push history; filter changes replace it. `#/cite/…` canonicalises in place —
but only when the citation resolved, because quietly redirecting a broken one to a default
surface would disguise a dead link as a working one.

### Search

The palette indexes 665 things: 164 styles, 209 faults, 97 slots, 60 rooms, 57 packs, 40
massings, 21 partis, 17 groupings, plus the twelve surfaces. Every entry carries a `cite`,
so it dispatches through the citation router and cannot reach a place a citation could not
name — `test_search_index.py` runs all 665 through the server's own validator.

Three keys, and that is the whole map: `⌘K`, `/`, `?`, plus `esc`. A fourth would need an
argument; the palette **is** the jump mechanism, and a `g`-then-`x` chord would be a second,
worse one that has to be memorised.

---

## 3. What was found

Six things, in rough order of how long they had been wrong.

**(i) The citation grammar was spelled THREE times, and two of the three disagreed —
660 citations went nowhere.** `server/citations.py`'s `REF_RE` allows dots, with a comment
saying exactly why: constraint ids are `style-id.cNN`. The client's `parseCite` did not. So
every one of the **660 constraint ids** validated on the server and parsed to `null` in the
browser; every `constraint:` chip the rail drew was inert, silently, because the client's
failure mode for an unparseable citation is nothing at all.

**That fix was wrong, and this paragraph said so was fixed for a day.** An adversarial audit
of this package found a THIRD copy of the grammar: `rail.py`'s `CITE_RE`, which extracts
`[[cite:…]]` from the model stream before anything validates it, and which also lacked the
dot. A constraint citation therefore never reached `validate()` at all — it was not
downgraded to plain text, it was never recognised as a citation, and the reader saw the raw
bracket syntax. Widening the client could not help, because the client was never handed
anything to parse. The regression test shipped alongside pinned only the client half, which
is exactly where the false confidence came from.

Now: the two Python copies share `ID_CHARS`/`FRAG_CHARS` from one place, and
`workbench/server/tests/test_grammar_agreement.py` reads the JavaScript to hold the third
against them — including an end-to-end assertion that a real constraint citation leaves
`_emit_text` as a `cites` event rather than as bracket text. The lesson is not "widen the
third one". It is that a grammar spelled three times drifts, and the only durable fix is to
stop spelling it three times.

**(ii) The phylogeny endpoint truncated `regions` to three, and half the corpus lost
precision.** Harmless while the field fed a caption. Wrong the moment a style is placed on a
map by the finest region it names: **82 of 164 styles carry more than three regions**, so
half the corpus was being silently coarsened — styles placed in the middle of a country
whose record names a valley. Found by cross-checking the map's precision tally against the
same computation run directly on `styles/*.json`; the counts moved 84/66/14 → 81/69/14 when
the cut came out. The lesson is the cheap one: a truncation is a decision about a consumer
you have, not about the consumers you will have.

**(iii) `Chip` was three things wearing one coat.** A toggle, a radio, and a plain act —
"download SVG", "undo", "delete room" — rendered identically, with no ARIA at all. A button
that DID something looked exactly like a button that HID something, and Details & Export was
the extreme case: every chip on it is a download, and three used the on-state as a spinner.

**(iv) Filter state was twelve private copies of the same four tokens, and it died on
navigation.** `setX(x === v ? null : v)`, repeated. Filter the fault list, leave to read a
style, come back: set it up again. One clear-all existed in the whole product, hand-built on
one surface. No surface said how many filters were narrowing what you saw — and a filter you
have forgotten is worse than no filter, because it makes a short list look like the corpus.

**(v) A session-scoped test fixture leaks auth state across every later test file.** *(Raised as OQ 64 here; ruled and closed the same day — see §9.)*
`test_mcp_http.py`'s `live` fixture sets `WORKBENCH_API_TOKEN` directly — deliberately, and
its docstring explains why function scope tore down too early — but restores it only at
*session* teardown. Every test file sorting after `test_mcp_http` therefore runs against a
server `auth.required()` considers gated, and a plain `client.get("/api/…")` in one gets a
401 that has nothing to do with the route under test. Found because the new
`test_search_index.py` passed alone and failed in the suite. Not fixed here — the fixture's
reasoning is sound and the repair is somebody's ruling, not a drive-by — but stated in place
and raised as **OQ 64**.

**(vi) Two stale numbers, and the shape of the gap between them.** The Kit's header said
"of 95 slots" while the ontology holds 97 — stale since 0.7.0 added `arch` and
`expressed_frame`. It reads `/api/overview` now, like every other count in the frame. And
CLAUDE.md's own status line said "762 tests" against 886 at the base commit, stale for some
time. Both survived because `check_counts.py` polices counts **derived from the corpus**,
and neither a test count nor a literal inside JSX is one of those. The guard is not wrong —
it is scoped, and the scope is where the stale numbers live. Corrected to 893 with the
scope stated in place; whether to widen the guard is a separate judgment.

---

## 4. The map, and the line it must not cross

The added requirement — *"a global map toggle for the phylogeny so a user can see style
origins and dependencies in global map format"* — is the one piece of this package that
could have laundered a guess into the corpus, so the reasoning is recorded fully.

**The corpus holds no coordinates.** It says "Tidewater Virginia", and it says "the James,
York, Rappahannock and Potomac river plantations, where the tobacco economy put wealth on
navigable water" — which is how a building tradition is actually located. There is no
decimal pair anywhere in `styles/*.json` and there should not be.

So `app/src/data/gazetteer.js` maps region *names* to points and is **interface furniture**,
stated as such in its own header: none of it may migrate into the corpus as measured fact.
It is the same rule the image records live under — the record is the object until a source
arrives — applied to geography.

Three honesties are built into the drawing rather than written beside it:

1. **Precision is drawn.** Each entry records `locality` / `region` / `country`, and a style
   is placed by the *finest* thing its `regions` or its `hearth` names (see §8 — reading the
   hearth as well took locality placements from 15 to 87). A country is not a hearth and a
   firm dot in the middle of Kansas would invent one, so those marks are hollow and hatched,
   in the same `--hatch-unjudged` vocabulary the product uses for "could not evaluate". The
   legend counts all three tiers, says what each means, and attributes the coarse ones: all
   24 are country-wide by the corpus's own account rather than by any failure of the drawing.
2. **Nothing is placed that cannot be.** A style whose regions the gazetteer does not know is
   listed as unplaced, never nudged onto a continent to tidy the picture. The walk asserts
   the arithmetic: placed + unplaced = every taxon, none dropped.
3. **Coincidence is not overlap.** Styles sharing a hearth cluster with a count, because
   twenty-five traditions sharing "England" is a fact about the records and not about
   England. And **16 lineage edges are not drawn at all** — both ends share a hearth, so the
   transmission happened inside one place and has no line to occupy. Counted and said, not
   faked with a decorative loop.

No map library, no tiles, no network at runtime: the basemap is Natural Earth 110m land
(public domain), clipped to the North Atlantic and simplified to 888 points across 33 rings,
generated by a script rather than hand-edited so every coordinate's provenance is a command
somebody else can re-run.

---

## 5. Machine usability: what was proved, not assumed

The constraint was explicit, so the audit is evidence rather than intention.

- **`rail.py`, `mcp_mount.py`, `citations.py` and `tools.py` are byte-identical** to their
  state before this package (`git diff --quiet` against the base commit). `mcp_server/` and
  `build/` are untouched. The only server changes are `corpus.py` (+`search_index`),
  `app.py` (+one route, +the `regions` truncation fix) and one new test file.
- **The `/mcp` mount answers normally**, verified by an `initialize` round trip against the
  running server.
- **The citation grammar did not change** — it got *wider* on the client, to match the
  server it had silently disagreed with. Every existing citation still resolves.
- **The rail's per-turn `context.surface` values are stable**; only `overview` is added.
- **Accessibility improved, which serves both audiences.** The rail is `<nav
  aria-label="surfaces">` with `aria-current="page"`; filters carry `aria-pressed` or
  `role="radio"` in a labelled group; the palette and the style picker are proper comboboxes
  over labelled listboxes. An agent driving the DOM and a person using a screen reader want
  the same thing here.
- **The three-state rule survives by construction**: no judgment-rendering component was
  redesigned. `--hatch-unjudged` usage is unchanged in every file but `AiRail.jsx`, where the
  literal went 2 → 1 because it was extracted to one shared constant used in both places.
- **The new endpoint is gated** like every other `/api/*` route, with a test that says so. It
  carries every name in the corpus in one response and must not be the one route that
  answers a stranger.

---

## 6. What was deliberately not done

- **Rail tools are not in the palette.** Ruled at the outset. The rail is a conversation, not
  a menu, and a palette entry that pre-fills a prompt would suggest otherwise.
- **The other 18 precompiled components were left alone.** Only `AiRail.jsx` needed edits it
  could not take in that form. The rest are working, and rewriting them to be tidy is not a
  navigation improvement.
- **The auth-fixture leak (OQ 64) is stated, not repaired.** The fixture's own reasoning is
  sound and the fix is a ruling about test isolation, not a drive-by.
- **`--strict` filters, drawing kinds and transcription modes were given semantics, not
  redesigns.** The surfaces that were not confusing were left where they were.
- **No responsive layout.** The frame is still fixed at `--rail-left` / `--rail-ai`, and the
  map is the first thing in the product that would benefit from a wider canvas. Noted, not
  attempted.

---

## 7. Verification

```
python3 build/check_all.py                     # 30 checks
node workbench/app/e2e/router-unit.mjs         # 61 checks, no DOM, no server
node workbench/app/e2e/search-unit.mjs         # 13 checks, no DOM, no server
node workbench/app/e2e/walk.mjs                # 56 checks against a running server
```

893 tests collected across the two pytest suites (98 in `workbench/server/tests`).

The two node unit files run on the standard interpreter with no DOM and no server, which is
what lets them pin the things most worth pinning: the URL↔citation bijection for every kind,
and the palette's 24 newcomer synonyms — *if "mistakes" stops finding the Fault Corpus, the
palette has quietly become an index of labels*, which is the thing it was built not to be.

**One intermittent failure, proved pre-existing.** `tests/test_solver.py::
test_check_plans_solve_with_stated_downgrades` reports 9 downgraded wall pins against a pin
of 8. It is **not deterministic**: it failed under `check_all.py` on three consecutive runs,
passed when run alone, and passed once in a direct full-suite `pytest tests/` (793 passed,
0 failed) on the same tree that `check_all` then failed. Its own comment predicts exactly
this — *"engine identity near the budget edge is wall-clock-dependent (a loaded machine
turns a 30s OPTIMAL into UNKNOWN → heuristic fallback)"* — and CP-SAT reaching its time
budget differently is what moves the count.

Proved pre-existing rather than assumed: the pre-package commit was checked out into a
separate worktree and the identical failure reproduced there with none of this work present.
This package touches no Python outside `workbench/server/`, and nothing in the solver's
import graph. Not caused here, not fixed here — but raised as **OQ 66**, because a pin that
depends on machine load is a check that will cry wolf at whoever runs the suite next, and
the thing it defends ("downgrade-without-proof is the failure this pin exists for") is worth
keeping sharp rather than loosening to 9.

**The walk is the honest test of this package**, because it drives the product the way a
person does. Twice it had to be taught something the diff had changed — the style switch is
a combobox now, and a sheet kind is a radio rather than a button. Both times that was the
point rather than an inconvenience.

---

## 8. The adversarial audit of this package, and what it found

Three independent read-only auditors were pointed at the finished diff — regressions and call
chains, whether the new tests were load-bearing, and second-order security/performance risk.
Twenty findings, two of them blocking. **The suite was green throughout, which is the point:
it covered none of this.**

**The two that blocked.** (i) above — the headline fix defeated by a third copy of the grammar
nobody had looked for. And the Fault Corpus's style filter, dead on arrival: `style` is both a
filter axis and a router selection key, so `parseHash` put it in `selection` while
`useSurfaceFilters` read `params`, and the value was permanently `undefined`. The picker
snapped back the instant you chose a style, the style-specific exception set was never
fetched, and clear-all could not clear it. `useFilters` now routes an axis by where the router
actually keeps it.

**The most instructive one is mine.** The OQ 66 work — the test rewritten *that day* to assert
the proof rather than the count — turned out to assert neither. Its skip matched the sentence
`geometry.py` emits for **every** unsolved status, so a structurally invalid CP model skipped
exactly like a loaded machine: the one assertion standing between the corpus and a silently
degraded solver, disarmed by the regression it names. And its "proven-or-carried" check pinned
two string literals copied out of the source, which at 60 s no run ever reaches — 17 restore
attempts, 8 OPTIMAL, 9 UNKNOWN, **0 INFEASIBLE** — so the `PROVEN` branch was dead code and
making `geometry_cp.py` emit `"proven"` unconditionally left the test green. Both fixed:
`geometry.py` now names its fallback (`budget` vs `engine`) and the test asserts against
`attempts`, the pass's own record of what it tried. Proved by mutation: stubbing the
reinstatement bookkeeping now fails.

**A second occurrence of a bug this package had already fixed.** `mcp_server/core.py`'s
`_style_card` carried the same `regions[:3]` truncation as `corpus.py::phylogeny()` — fixed in
one, missed in the other, and live in two UI surfaces. The Phylogeny screen contradicted
itself: the map placing a style from its full region list while the panel beside it named
three of nine, with no ellipsis.

**And the placement reading was picking the wrong place a quarter of the time.**
`placeByHearth` scanned the gazetteer longest-name-first and took the first hit, so it chose
by an accident of key length rather than by what the sentence says. 25 of 93 hearth placements
landed on somewhere named second or later — including **`craftsman`, placed in Los Angeles
while its record reads "Pasadena and Los Angeles"**, Pasadena being the exact word this whole
reading was justified by, in the commit, in `docs/workbench.md`, and in §9 below. Earliest
mentioned now wins, applied *after* the anchor filter — the order matters, because sorting
first would hand `dutch-colonial-american` to Amsterdam, the very bug the anchor rule exists
to catch.

The rest, fixed: 138 palette entries that dispatched to surfaces reading none of their
selection key; the Transcription scan and its hand-tuned calibration destroyed on every
navigation, now in a store; `setPointerCapture` swallowing every click on a map mark, and a
cluster only ever selectable as its first member of 25; `rows`/`edges` rebuilt during render
so `MapView`'s memo was a no-op and every keystroke re-placed 164 styles; `replaceState` per
keystroke, undebounced and unguarded, which Safari throws on; `useStyles` turning a failed
fetch into an empty corpus; three surfaces never migrated to it; `activeCount` counting
*widening* controls as narrowing; unencoded path parameters; the search index rebuilt per
request (3.3 ms → 0.00009 ms); a path traversal in `place_plan(parti=…)`; and
`aria-pressed="false"` stamped on fifteen plain acts.

**And the suites nobody ran.** `router-unit.mjs` and `search-unit.mjs` were wired into
nothing — not `check_all.py`, not `package.json` — so 74 checks ran only when someone
remembered, while §9 cited them as verification. `build/check_frontend.py` runs them now, and
reports COULD NOT EVALUATE without node rather than passing.

## 9. The three questions, ruled and executed the same day

Lucas ruled all three on 26 Aug, and working them turned up more than they were about.

**OQ 66 — assert the proof, not the count.** The property the pin defends is that a
downgrade is never silent, and counting was a proxy for it that made a green suite a fact
about the machine. Every downgraded wall pin must now carry a stated refinement naming its
room and wall, and that refinement must say which of two things it is: proven infeasible
alone at this footprint, or carried from the conflict core and explicitly not re-proved in
budget. Both are honest; an unstated third path is the failure, and so is a pin with no note.
That holds under any load. The other direction keeps a bound but a load-independent one —
fewer pins downgraded than the plan declares, or the model has stopped enforcing walls and
started narrating them. Proving the fix turned up its twin: under 4× CPU oversubscription
CP-SAT does not run at all, so the *engine-identity* assertion failed. Same species, same
discipline — a budget fallback now skips as COULD NOT EVALUATE carrying the dispatcher's own
reason, while a fallback for any other cause still fails.

**OQ 64 — configure the gate per test.** The two constraints were never one constraint. The
client must stay session-scoped (the lifespan may be entered once per process); the token
need only exist while a request in that file is in flight, which is exactly what
`monkeypatch` is. Not done as literally ruled, for a reason worth recording: a client
carrying a default `Authorization` header cannot coexist with `test_bearer_is_required`,
which proves the gate by sending none. `test_zz_auth_leak_guard.py` now asserts no gate
variable survives into it and names the cause and remedy in its failure message; the `zz` is
load-bearing, because a guard against "something earlier leaked" only works if it runs after
everything it guards.

**OQ 65 — and the check was the smaller half.** Ruled: build the check, and chase the
hearths too. Chasing them needed no authoring at all, which is the finding. The map placed
styles from `geography.regions` alone — and **59 of the 81 country-level placements had a
`geography.hearth` naming somewhere finer that nothing was reading.** Craftsman sat in the
middle of Kansas while its own record said "Pasadena and Los Angeles, California". Reading
both fields took locality placements from **15 to 87** and country-wide from **81 to 24**,
without a single new fact being authored. The corpus already knew; the interface was not
listening.

The remaining 24 are correct, and that is the answer to the half of the question that
suspected a gap in hearth coverage: 22 are families and traditions, abstractions over styles
with no birthplace, and two are styles whose hearth says so in its own words —
`neo-eclectic`'s "No design hearth; the style was generated inside production builders' plan
departments", `craftsman-bungalow`'s "Streetcar suburbs nationwide". The map now attributes
them rather than counting them as its own failure.

The rule that makes prose-reading safe: **a hearth may sharpen a region, never contradict
one.** A name found in the prose is refused if it lies more than 45° from *every* region the
style names. The first version anchored to the finest region only and was wrong — it threw
away `churrigueresque`'s Madrid because that style's finest region is in Mexico, while Spain
sat in the same list. Against all of them it still does its job: `dutch-colonial-american`'s
hearth reads "from Nieuw Amsterdam to Beverwijck (Albany)", all six of its regions are
American, so Amsterdam is refused and the sentence resolves to Albany — which is what it
meant.

`build/check_gazetteer.py --strict` joins `check_all.py` and ratchets three numbers, **all
at zero**: unplaced, coarse for any reason but the record's, and hearth sentences it cannot
read. It parses the JS gazetteer rather than keeping a Python copy — a second copy is
precisely how the two halves of the citation grammar came to disagree about dots. Proved by
adding a style naming a place nobody has heard of: the check fails, names it, and says what
to do about it.

## 10. Open questions raised

**OQ 64 — a session-scoped fixture gates every test file that sorts after it.** **CLOSED.** See §3(v).
The mechanism is `test_mcp_http.py::live`; the symptom is a 401 on any unauthenticated
request in a later file; the workaround (state your own baseline) is in
`test_search_index.py` with the reasoning in place. Needs a ruling on whether the fixture
should be reworked or the convention documented.

All three were ruled and executed the same day — see §8 for what each turned up. They are
recorded here as they were raised, because the questions are what the package produced and
the answers came afterwards.

**OQ 66 — a solver pin that depends on machine load.** See §7. Raised only because this
package had to establish it had not broken the solver, and establishing that turned up a
check failing intermittently for reasons unrelated to the code under test. **CLOSED.**

**OQ 65 — the gazetteer is unversioned interface data about a corpus that grows.** **CLOSED**, and the larger half of it was that the corpus already held the answer. 275
entries place all 164 styles today. A style added tomorrow with an unknown region name will
be reported as unplaced, which is the correct failure — but nothing *fails the build* to
tell an author their new style is invisible on the map. A `check_gazetteer.py` that ratchets
placement coverage would close it. Not built, because it is unclear whether the map is
load-bearing enough to be worth a check in `check_all.py`, and that is a judgment about how
the tool is used rather than about the data.
