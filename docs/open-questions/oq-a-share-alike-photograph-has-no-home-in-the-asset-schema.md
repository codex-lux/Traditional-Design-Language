# oq/a-share-alike-photograph-has-no-home-in-the-asset-schema — the English records can have a licence or an image, not both

*Status: RULED 31 Aug 2026, and the ruling is a refusal · Raised in: From the network-egress work (WP-4.4)*

**RULED — public domain and CC0 only, for now.** 125 of the 305 distinct harvest queries name buildings outside the United States -- English,
Irish, Scottish and continental European. The original ten were English and
Irish buildings: Bedford Square 3, Queen Square 2, Merrion Square 2, Fairfax House 1, and two
more. HABS cannot hold any of them — it is a United States survey by charter, which
`build/harvest_habs.py` now says in the refusal itself rather than reporting "no result holds a
photograph", which is true and names the wrong cause. Every English photograph checked for these
buildings is share-alike: CC BY-SA 2.0 and CC BY-SA 4.0, whose obligations are not compatible with
each other.

**Why a refusal rather than a licence field.** This corpus DERIVES from its images by design — it
traces them, measures them, redraws them, and `schema/plan.schema.json` has a whole `provenance`
block for records produced that way. Accepting share-alike source material commits those
derivatives, and that is a decision about what the corpus is, not a field somebody forgot to fill
in. `schema/asset.schema.json`'s `license` enum carries `cc-by-sa` but no licence VERSION and
nothing that carries the obligation forward to a derivative, so the schema cannot currently express
what accepting one would mean.

**What was fixed rather than deferred.** `mcp_server/core.py::find_assets` returned a `file` path
and no licence, no attribution, no author — and it is the only programmatic route by which an asset
reaches anyone, serving the MCP tool, the workbench API and the app alike. So the moment a licensed
image entered the manifest the corpus would have handed every consumer a file with no way to
attribute it: non-compliance by construction rather than by oversight. It serves a `rights` object
now, and `rights.publishable` is false until a person records a licence.

**What is still open:** whether to accept share-alike at all, and if so what the schema must carry
(version, obligation-on-derivative, and how a redrawing of a BY-SA photograph is marked). Until
that is ruled, those ten records stay `wanted`, or become drawings.
