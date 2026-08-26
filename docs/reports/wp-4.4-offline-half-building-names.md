# WP-4.4, the offline half — 161 records given a building to look for, and the other 161 cannot have one

*26 August 2026. WP-4.4's harvest is environment-blocked: the proxy answers 403 to CONNECT for
`www.loc.gov`. The package's own named next step needs no network — give the 322 asset records
their `provenance.building` names, without which every harvest query degrades to a style-name
search and one photograph ends up cited by many records. This is that step. It closes exactly
half of it, and the half it cannot close turns out to be a property of the corpus rather than a
gap in the work.*

---

## What was done

`build/harvest_habs.py::query_for()` builds its query from `provenance.building` when a record
names one and falls back to the depicted style node plus slot when it does not. The harvester
refuses to `--write` while any selected record would be searched on style alone, which is the
right refusal and is why this had to happen first.

**161 records now name a building**, taken from the depicted node's own `exemplars` list — the
corpus's own canonical examples, with their locations. Nothing was invented: every name and every
location is quoted from a style record that already carried it.

Before, the dry run's first four requests were all `?q=english+georgian`. Now the correct-role
records ask for `Queen Square Bath, England`, `Bedford Square Bloomsbury, London, England`,
`Fairfax House Castlegate, York, England` — a query that can return the building it names.

### One thing was measured and changed the method

A first pass took each node's **first** exemplar. That produced **151 of 161 records pointing at
Westover**, because `georgian-colonial-american` and `tidewater-georgian` both list it first. That
is the same degenerate outcome the package was trying to avoid — one image cited by many records —
wearing a building's name instead of a style's.

The assignment is now a deterministic round-robin across each node's own exemplars, ordered by
asset id so a re-run reproduces it exactly. Every exemplar is equally canonical for its node, so
which of four a given shot targets is arbitrary **between sourced names**, which is a different
thing from inventing one. The spread:

| building | shots | | building | shots |
|---|---|---|---|---|
| Westover | 38 | | Stratford Hall | 6 |
| Drayton Hall | 32 | | Carter's Grove | 6 |
| Mount Pleasant | 32 | | Gunston Hall | 5 |
| Hammond-Harwood House | 32 | | Bedford Square · Queen Square | 3 · 3 |
| | | | Fairfax House · Merrion Square | 2 · 2 |

---

## What was found, and it is the more useful half

### The image layer covers three style nodes, not the corpus

All 322 records depict **`georgian-colonial-american` (247), `tidewater-georgian` (46) and
`english-georgian` (18)** — three of 164 nodes. The manifest is a Georgian shot list. Nothing in
the counts says so: "322 image records, 0 sourced" reads corpus-wide everywhere it appears, and it
is not. Sourcing every one of them would leave 161 nodes with no image at all, and the number
would then read as a solved problem.

### 150 records cannot be given a building name, and should not be

Half the corpus is `role: incorrect` — a record paired with a correct one, depicting the error
condition. There is no exemplar for "an English Georgian house whose parti is picturesque-
asymmetrical", because the corpus names buildings that exemplify a style, not buildings that
exemplify a fault. Naming a real building as an instance of an error would be both unsourced and
a claim about somebody's house.

So those 150 keep no `provenance.building`, and the harvester goes on refusing them — correctly.
Eleven more are diagrams whose node names no exemplar. **The honest split is 161 harvestable and
161 not**, and the harvester's own warning now reports exactly that count.

**What this means for the package's acceptance.** WP-4.4 asks for ≥100 records `sourced` or
`generated` and zero `license: unknown`. The correct half alone can reach 100 the day the network
opens. **The incorrect half cannot be harvested at any point**, from any archive, because the
image it wants does not exist as a catalogued photograph of a named building. That half needs a
different strategy — a modern building photographed as a negative example, which raises its own
licensing and fairness questions, or a generated diagram — and it is a decision, not a fetch. It
is named here rather than left to be discovered when a harvest run comes back half empty.

---

## What was deliberately not done

- **No `license` was touched.** Every record stays `unknown` until a file actually lands; the
  harvester sets it from what it fetched. Writing `public-domain` in advance would be asserting a
  provenance for a file that does not exist.
- **No record was marked `sourced`.** Nothing was fetched. The network is still closed.
- **The 11 exemplar-less diagrams were left alone** rather than pointed at a neighbouring node's
  building, which would have been a guess dressed as a target.
- **The three-node coverage was not widened.** Authoring a shot list for the other 161 nodes is a
  work package, not a note; this one records that it is missing.

## For whoever runs the harvest

The blocker is unchanged and is stated verbatim in WP-4.4's own status block: `curl
https://www.loc.gov/... → curl: (56) CONNECT tunnel failed, response 403`. What is different now
is that the day it opens, `--live --write` will work on 161 records instead of refusing on all
322, and each of those 161 asks for a building by name and place rather than for a style.
