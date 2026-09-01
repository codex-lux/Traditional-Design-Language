# WP-4.4: the eleven that were never blocked, and four defects in a script nobody can run

*31 Aug 2026. Raised by Lucas: "Let's start looking into the issues that you're not able to
address because of network egress issues... I simply can't personally find all of the relevant
imagery by hand."*

## What was asked, and what was actually in the way

Seven items are carried as environment-blocked: WP-4.4's harvest (322 image records, 0 sourced),
OQ 7 through 11 (five treatise plates whose engraved numerals no reachable scan renders legibly),
and OQ 18's source half. The ask was to find a way through.

**Three routes were measured.** The shell proxy answers `403 Forbidden` to CONNECT and logs
`connect_rejected` — a policy denial, not a network fault. The built-in `WebFetch` refuses the same
hosts with `EGRESS_BLOCKED`. The **Tavily** connector reaches them, because it fetches on Tavily's
servers; a **GitHub Actions** runner reaches everything. Lucas ruled to build on both, recorded at
`oq/fetching-through-a-tier-the-proxy-denies`.

**Then the routes turned out not to be the binding constraint, and four findings said so.**

## Finding 1 — OCR cannot supply a number, and the cleanest source is the inadmissible one

Four independent scans of Vignola's *Regola* were compared through Tavily. **Every figure
disagreed.** Digits drop (`4` for 14, `9` for 18); glyphs are invented (`y8`, `t8`, `ii`); one
document says 12 in one passage and **11** in another for the same module.

The decisive case is the fraction. Vignola's Ionic order is **22½** modules. Three scans read
`22 +`, `22 3`, `22 2` — **integer agreed 3 of 3, fraction agreed 0 of 3.** Three mutually
incompatible glyphs for the same half.

One source was correct on every reading: the 1889 English translation. It is a *secondary work*,
which OQ 7-11 explicitly forbid. **The cleanest OCR in the experiment is the least admissible
witness**, and a pipeline that preferred agreement would have preferred it. An OCR-derived numeral
may never become a `measured` figure.

## Finding 2 — the plate numerals are probably unreadable even with the bytes

Images reaching a model downsample to roughly 1,568 px on the long edge. A 38 cm folio at 1,568 px
is ~4 px/mm; Vignola's engraved part-numbers are 1.5-2 mm, so 6-8 px of numeral height.
Corroborated directly: the largest image in this repository is 687x999 — *under* the ceiling — and
fine dimension text on it was still not resolvable. **Committing full-page plates would produce
plausible-looking, unreadable files**, which is the failure mode this project is most alert to. The
only remedy is a server-side IIIF region crop, confirmed available on archive.org and e-rara.

## Finding 3 — WP-4.4's own harvester had four defects, and none was findable by running it

`www.loc.gov` has answered 403 since the script was written, so `build/harvest_habs.py` has never
executed against the live API. Every defect below would have produced a confident wrong result on
the first run somebody managed.

- **The rate limit was three times the ceiling.** `PAUSE_S = 1.0` is 60 requests a minute against
  loc.gov's documented 20, which blocks for an hour above it. The first live run earns the block
  inside the first minute, counts every subsequent record as a `FAIL`, and **returns 0**.
- **It asserted a licence the source does not state.** `provenance_from` wrote
  `license: "public-domain"` before reading a field, its own docstring conceding this was "the one
  claim here that does not come from the response". The Library's sentence is collection-level
  boilerplate, byte-identical on a government photograph and on Mount Pleasant `pa0824` index 10 —
  a HABS photograph **of a third party's 1897 drawing**. It records the sentence verbatim now, in a
  new `rights_evidence` field, and writes no licence at all.
- **It picked the record with no pictures in it.** For Carter's Grove, `best_result` took `va2290`,
  a HALS record whose whole holding is "Data Page(s): 9", because its title matched the manifest's
  county — while `va0654`, holding 82 photographs, says Williamsburg and does not match.
- **161 records collapsed onto eleven queries and the guard tested the wrong condition.** The 161
  building-named records name only eleven buildings. All 32 Hammond-Harwood records issued the
  identical query. The guard refused to write when a record had *no* building — the opposite
  condition. Records are grouped by building now; 161 requests became 7.

Four of the eleven buildings are English or Irish. HABS is a US survey **by charter**, so those
returned "no result holds a photograph" — true, and the wrong reason. They are named and skipped
with jurisdiction as the cause.

## Finding 4 — acquiring an image would have changed nothing anybody could see

Three independent consumer gaps, all live:

- `UnsourcedImageRecord.jsx` drew the hatched "specified · unsourced" plate **unconditionally**. A
  record with a file rendered identically to one without.
- `find_assets` returned a `file` path and **no licence, no attribution, no author** — and it is the
  only route by which an asset reaches the MCP tool, the workbench API and the app. Any licensed
  image would have made non-compliance structural rather than merely likely.
- `depicts.faults` was empty on **all 322** records while the Fault Corpus surface queries by
  fault, so its evidence rail printed "no image records are filed against this fault yet" for every
  one of 210 faults, with 322 records sitting one join away.

## What shipped

**Eleven records are sourced, and none of them ever needed the network.** They carry a
`generated_from` block naming a proportion pack and an assembly; everything required to draw them
has been in the corpus since WP-5.11. `build/render_profile.py` draws them from
`profiles.pack_geometry()` and `proportion_engine.dimension()` and constructs nothing of its own.
**322 wanted / 0 sourced became 311 / 11** — the first movement on this package.

Three of the eleven failed on the first run, and **the most interesting was the raw-record read**:
`gibbs-ionic` is an overlay on Vignola and states no `base` assembly of its own, so reading its own
file finds no base and the plate simply does not exist. The answer lives in the inheritance. That
is the same defect class as `oq/the-raw-kit-read` and WP-8.6's two truncated cascades, in a fourth
place.

**The refusals are on the plate.** A member `profiles.py` reports as unconstructed — an acanthus
row, a volute's spiral — is NAMED and not drawn as something plausible; `vignola-corinthian`'s
capital draws as the plain bell it is with three members disclosed under it. Every plate carries
`GENERATED FROM THE RECORD — NOT A DRAWING OF A REAL BUILDING`, on the plate rather than in prose
beside it, because a printed or exported plate leaves prose behind.

**An unplanned cross-check turned up.** The eleven captions were authored from the same packs,
independently of this renderer. All eleven member counts agree — 6/6, 5/5, 8/8, 4/4, 7/7, 10/10,
6/6, 6/6, 13/13, 4/4, 3/3. It is pinned as a test.

Also: `find_assets` serves a `rights` object with `publishable` false until a person records a
licence; `build/link_asset_faults.py` derives 209 asset-to-fault links over 94 assets, reaching 20
of 210 faults, from a rule stated once — *the fault names a slot the asset depicts AND applies to a
style the asset depicts*. Slot alone gives 2,156 links and puts fourteen faults on one porch
record; both halves are load-bearing.

## Deliberately not done

- **No `.github/workflows/harvest.yml`.** Landing a `workflow_dispatch` job with `contents: write`
  that fetches arbitrary bytes and commits them is a standing capability on the default branch and
  the least reversible step in the programme. Nothing here needed it.
- **No OQ 7-11 closure.** Findings 1 and 2 say what it would take: IIIF region crops, edition
  identity established from `archive.org/metadata/{id}` before any plate number is cited, and a
  reading recorded for confirmation rather than written into a pack. Note that "plate XXVIII" is a
  coordinate in the 1562/63 32-plate sequence — the e-rara 1607 copy has 45 plates and the c.1692
  Rossi is a wholesale re-engraving, excluded on the same grounds as a modern redrawing.
- **No new provenance vocabulary.** An adversarial audit found the attestation schema drafted for
  this was **opt-in and therefore useless**: a figure written the old way carries no attestation
  block and passes every proposed check, and the mutation that leaves the suite green is deleting
  the block. Worse, `check_kits.py:140` and `:427` mean **a free-text `source` string already buys
  silence from two live checkers**, and nothing anywhere resolves one. No new vocabulary until the
  existing `source` field is validated.
- **The English and Irish records.** Ruled: public domain and CC0 only —
  `oq/a-share-alike-photograph-has-no-home-in-the-asset-schema`.

## And CI is dead, which nothing in the repository says

Verified via the Actions API: the last two runs (29 Aug, a `main` push and a pull request) both
failed in **3 and 4 seconds** with all three jobs failing simultaneously and zero steps executed,
against 457-1,139 s for each of the 28 runs before them. That is a start refusal — exhausted
minutes, a spending limit, or an org stop — not a test failure. **CI has not run for two days**,
and it is the only tier that can fetch image bytes. The cause lives on a dashboard this
environment cannot read.

## New open questions

- `oq/fetching-through-a-tier-the-proxy-denies` — ruled; the decision recorded so it is not
  re-derived.
- `oq/a-share-alike-photograph-has-no-home-in-the-asset-schema` — ruled as a refusal.
- `oq/regenerating-the-asset-manifest-discards-what-was-added-to-it` — open, and the sharpest of
  the three: `gen_assets.py` rebuilds the manifest from scratch and would silently discard the 161
  building names, the eleven files, and the 209 fault links. It is in neither `check_all.py` nor
  the Makefile, so the loss would happen on somebody's laptop and arrive as a commit.

---

# Addendum, same day: Lucas ruled regenerate, and eleven became seventy-three

*The report above was written before the ruling. Its title is left as it was — the eleven were the
finding — and this records what the ruling changed.*

## The manifest covers the corpus now

`322 wanted / 0 sourced` over three style nodes is **`1,777 wanted / 73 sourced` over 142**.

The regeneration itself was uneventful, which was the point of fixing `gen_assets.py` first:
**zero records lost**, and all 11 sourced records, all 161 building names and all 94 fault links
carried through. A regeneration now carries 3,787 fields the generator does not own.

## Four things the new scale broke, none of them the regeneration

**The profile block named five packs, and the corpus holds twenty-five it can draw.** The five
were a sample from when the layer was authored and nothing said so. Walking all of them takes the
drawn plates from 11 to **73**, with 0 failures. **The authored assembly filter was left alone**:
widening it from `(cornice, capital, base, entablature)` to include architrave and pedestal would
add 46 more and carry this package past WP-4.4's "at least 100 sourced" acceptance line. Hitting an
acceptance number by widening somebody else's filter is not meeting it, so the figure is reported at
73 and the line is not met.

**The building names.** 161 records named **eleven** buildings, so a perfect harvest would have
returned eleven photographs for 161 records. `build/name_asset_buildings.py` deals each node's
records round its own exemplars — deterministic, sorted by id — and takes it to **845 records
naming 327 buildings over 330 distinct queries**. It never touches `role: incorrect`: the corpus
names buildings that exemplify a style and never ones that exemplify a fault, so those 858 keep no
building and the harvester goes on skipping them. Its own first report was wrong in a way worth
recording — it counted the remainder BEFORE the assignment it describes, so a dry run filed the 684
records it was about to name under "its style records no exemplars."

**The jurisdiction test was a denylist and had to become an allowlist.** It named
england/scotland/wales/ireland, which was right for three style nodes. At 142 the locations run to
Belgium, France, Germany, Greece, Italy, Mexico, the Netherlands, Norway, **Ontario**, South
Africa, Spain, Sweden, Switzerland and Vatican City. A denylist is wrong by default on the next
country nobody thought of, and wrong in the expensive direction — it spends a rate-limited request
and then misreports the cause. An allowlist of US states is wrong only by letting a request
through. Ontario is the case that makes it concrete: not a country name, so no plausible denylist
of countries would have caught it. 188 of the 330 queries are within HABS's charter; the other 142
are named and skipped.

**`check_counts.py --fix` corrupted a file, and the comment above the bug named it.** One pattern
matching twice: `hits` is materialised once, so every span indexes the text as it was before any
rewrite, and writing forwards shifts each later span. `**311 wanted, 11 sourced**` became
`*17771 wanted, 11 sourced**` — an asterisk eaten, a number invented, and the pattern no longer
matching, so **the claim silently left the checked population**. The old code carried the comment
`# offsets moved` and then recompiled the regex, which does nothing once the list is built: a
guard that named the problem and did not address it, which is WP-8.6's category exactly. Writing
highest-offset-first fixes it, and the guard drives the real two-hit case.

That the asset counts were caught at all is the checker added earlier the same day: **sixteen stale
claims across four files**, in a layer whose numbers had been policed by nothing.

## What the ruling cost, stated plainly

The visible gap is five and a half times larger: 1,777 wanted against 311. That is the honest state
rather than a regression — the records were always implied by the corpus and the manifest simply
had not been regenerated since it covered three nodes. But 1,466 of them are gaps nobody can act on
today, and 858 of those can never be closed from any archive at all.

`oq/regenerating-the-asset-manifest-discards-what-was-added-to-it` is CLOSED, both halves.

## And the plates were laundering, on OQ 7's own subject

Found by looking at a drawing, after everything above was committed.

`palladio-tuscan` records a base, a shaft, a capital and a pedestal, and **deliberately no
entablature**: Palladio does not dimension his Tuscan entablature in the text and the plate
numerals are illegible in every reachable scan. That is the whole of OQ 7, stated in the pack's
own notes — *"WHAT IT DOES NOT ASSERT. Palladio's Tuscan entablature."*

`proportion_engine.resolve()` then supplies a cornice from `vignola-tuscan`. Correctly — that is
what an overlay is for, and using `resolve()` rather than the raw pack is what let `gibbs-ionic`
find a base at all. But the plate came out titled **"Palladio's Tuscan Order — cornice"**, drawing
**Vignola's** members, footed **"AFTER: Palladio, I Quattro Libri dell'Architettura, Venice 1570"**.

One authority's figures under another's citation, on the exact assembly the corpus keeps an open
question about *because that authority does not give it.* **34 of the 73 plates were doing it** —
across Palladio, Gibbs, Chambers and Benjamin, which is to say across the four works OQ 7 through
OQ 11 are about.

The plate names the pack that actually states the members now and cites THAT authority:

> INHERITED: palladio-tuscan STATES NO CORNICE OF ITS OWN. These members are vignola-tuscan's,
> delivered by the overlay, and the citation below is THEIRS.
> AFTER: Vignola, Regola delli cinque ordini d'architettura, Rome 1562, Tavole IV-VIII

Two things worth carrying. **The resolved read is right and is not sufficient**: `resolve()` was
the fix for reading a pack's own file, and it introduced this in the same motion, because
inheritance supplies what a pack declines as readily as what it merely omits — and the corpus has
no way to tell those apart today. **And a record-level check could not have caught it**: the
manifest, the packs and the engine were all correct. The false claim existed only in ink, which is
this repository's own repeated lesson — 245 arcs drawn as their own mirror through 34 checks and
970 tests, because every one of them interrogated the model and none asked where the ink went.

---

# The adversarial audit, 1 Sep 2026

Four independent read-only auditors over the six commits: consumers and call chains, whether the
new tests can fail, second-order risk, and second occurrences of each fixed pattern. They found
things the work itself did not, and three of them blocked deployment.

## Blocking

**`/corpus/assets` served the whole corpus directory, unauthenticated.** The auth gate matches
only `/api/` and `/mcp`, so `/api/assets` answered 401 while `/corpus/assets/manifest.json`
answered 200 with **3.4 MB** — all 1,850 records with every provenance block, review note and
hand-assigned building name, unprojected and unlimited. This module's own docstring said the
ungated surface "carries no corpus data"; that sentence had become false in the same commit.

It was also **33.5 ms of server CPU per request**, because 3.4 MB compresses inline on the event
loop — `FileResponse` streams 64 KiB chunks and `GZipMiddleware` only offloads above 128 KiB,
which is exactly what the `/assets` exemption exists for. **31.5 requests a second from one
anonymous caller saturated the deployment's single core**, each shipping 286 KB.

One fix closes all of it: mount `assets/generated`, which is the only directory the app ever asks
for, so the URLs are unchanged. `/corpus/` joins the gzip exemption; the plates carry `nosniff`,
a CSP sandbox and `no-cache, must-revalidate`. That last matters because the paths are stable
across regenerations, so heuristic freshness would have kept a corrected moulding from a
returning viewer. And it closes a door before it opened: `harvest_habs.py` exists to put
downloaded archive material under `assets/`, and the wide mount would have made a remote file
same-origin active content on this origin the day it landed.

**The traversal test was green exactly when it was meaningless.** It asserted a status code for
`/corpus/assets/../../CLAUDE.md`. httpx normalises dot-segments client-side, so the request never
reached the mount — it passed where `workbench/app/dist` is absent (404 from nothing) and
**failed where CI builds the app** (200 from the SPA). An auditor replaced the mount with a
hand-rolled handler having no containment check at all — an unauthenticated arbitrary file read —
and all four tests stayed green. It asserts on the bytes now, against the real mount prefix, and
declares which regime it is running in.

**Five scripts wrote a 3.5 MB manifest by truncating it first.** Measured: an encoder error
mid-write left 1.7 MB of unparseable JSON. `gen_assets.py` makes it sharp — it READS that file to
carry forward 786 building names, 73 file blocks and 322 fault links, so a truncated write
destroys the only input the next run needs in order not to destroy anything. `build/manifest_io.py`
is the one atomic writer: temp sibling, fsync, `os.replace`, directory fsync, `except BaseException`
so a Ctrl-C is caught.

## What the tests could not catch

The header of `tests/test_harvest_habs.py` claimed every test in it was mutation-checked. Eleven
of fifteen were. **The four defects the harvester's own docstring says are "ALL FIXED HERE" live
in `main()`, and `main()` had no test**: an auditor reverted each one inside it and the file
stayed green — one request per record, no jurisdiction skip, `status: sourced` on write, a licence
conclusion written by machine. `tests/test_harvest_habs_main.py` drives the real `main()` over a
fake transport now, and killed all five reverts. **It found a live `NameError` on the `--write`
path immediately** — `manifest_io` was used and never imported, so the only code that writes the
manifest was broken and only source-greps existed to notice.

`test_counts_guard`'s new test was worse: its docstring said it drove the real script and it never
called it, reimplementing the algorithm inline and asserting on its own output. `--fix` never
writing the file at all left it green. It drives the real `main()` now with ROOT and CLAIMS
patched.

Three tests passed vacuously under exactly the data loss this package exists to prevent — null
every `file`, reset every `status`, drop every link, and `test_sourced_means_a_file_is_actually_present`
passes because its loop body never runs. All three carry a `checked == N` guard now.
`test_the_committed_manifest_is_what_the_generator_emits` compared id sets only, so mangling every
caption passed; it compares the generated fields too.

Two docstrings claimed more than they did and now say what they are: the member-count cross-check
is **not** independent (caption and plate come from the same `dimension()` call — an auditor
regressed the engine, re-ran the generator, and it went green), and the generator tests' restore
is **not** unconditional (a `finally` does not run for SIGKILL).

## Second occurrences of the patterns this session fixed

**The raw-record read had one**, latent: `build/elevation.py:441` re-entered `PE.PACKS[...]` on an
object already resolved, correct for `gibbs-ionic` and a `KeyError` for 14 of the 26 order packs.

**The inherited-authority defect had four more**, and fixing the ink had left the catalogue: 34
asset RECORDS still carried `provenance.source` naming a pack that does not state the assembly,
served through `find_assets` to every consumer, while the plate they point at said otherwise — and
the record's own alt_text closes "the drawing and the data cannot silently disagree".
`tdl_get_proportions` and `tdl_compare_authorities` did the same; the comparison table published
Vignola's Tuscan entablature as Palladio's while its own note said Palladio makes it a fifth. The
walk now lives in `proportion_engine.assembly_owner`, one place with five readers, rather than the
two hand-rolled copies that had appeared within an hour of each other.

**The denylist had one, inside this session's own fix.** In the same commit that turned the
harvester's country denylist into a US-state allowlist, the manifest carry-forward was written the
other way round — four fields to KEEP, denying everything else, with the allowlist sitting unused
above it. The next field any tool added would have been destroyed while the run printed "carried
forward N field(s)".

**The hardcoded sample had one**: `render_orders.py` walked an authority × order grid, so
`greek-doric` and `moorish-arch` — bound to 5 and 8 styles — fell through both loops and
`dist/orders.html` served 55 of 57 packs silently.

**A guard naming a problem it does not address had none** beyond the one already fixed. That is a
real negative result.

## Also fixed

52 line-diagrams whose own alt_text says "there is nothing to photograph" had been given a real
building, because the assigner keyed on `role` when the question is `kind`; the harvester would
have spent rate-limited requests on them and stamped a HABS survey number onto a drawing of an
invented rule. The harvester would also have **overwritten all 786 curated building names** with
LoC titles — the field it searches ON — making the next run's query worse than the first; the
archive's title goes to `found_title` beside it now. It returned 0 after failing every request,
which is the defect its own docstring claims to have fixed. `link_asset_faults` could not clear a
stale link. `check_assets` crashed instead of reporting on a missing file, and never checked that
every file on disk is claimed by a record — so deleting the manifest orphaned all 73 SVGs while it
printed "every sourced record has the file it claims". `find_assets` had no `pack` filter, so not
one of the 73 records that actually have a file was reachable by any query. `rights.publishable`
was a bool that could not tell "nobody has looked" from "ruled share-alike", and called 61
file-less records publishable. Vite's dev server did not proxy `/corpus`. And `FaultCorpus.jsx`
told the user, in the shipped app, that "the corpus holds 322 specified records and none has a
photograph".

## Verdict

`check_all.py`: **40 of 42 passed, 0 failed**; the two unjudged are `export_ifc` and `geometry_cp`,
which need optional libraries CI installs and which report COULD NOT EVALUATE rather than passing.
1,251 tests, 62 app tests, 151 workbench server tests.
