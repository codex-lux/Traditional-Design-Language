# OQ 88 — `sash-light`'s frame-wall sill rule reaches 27 masonry nodes, and two more pack rules have the same shape

*Status: OPEN · Raised in: From the adversarial audit of WP-5.14 (28 Aug 2026)*

**OPEN — `sash-light`'s frame-wall sill rule reaches 27 masonry nodes, and two more pack rules have
the same shape.** WP-5.14 scoped `sash-light`'s `window_sill/projection` (2.25 in, *"sloped about 1 in
6 with a drip"*) away from `tidewater-georgian`, on the strength of the rule's own note: *"In a frame
wall this is a real sill member; in a masonry wall it is a rowlock or a stone and belongs to the
brick-course pack, not this one."* That fixed one node. The cascade delivers the same rule to **86
nodes, of which 27 make a masonry cladding canonical** — `english-georgian`, `charleston-georgian`,
`mid-atlantic-georgian`, `jeffersonian-classicism`, `hudson-valley-dutch`, `italianate-townhouse`,
`brownstone`-clad `renaissance-revival-american` among them. `charleston-georgian` still resolves the
2.25 in sloped sill today.

**Two other rules state a scope their data does not carry**, found by the same sweep:
`opening-proportion`'s `window_surround_wood/exterior_head_assembly_height` (*"On a masonry front this
assembly is a flat arch, a jack arch or a stone lintel instead, and the brick-course pack owns its
coursing"*, `applies_to` 52 nodes, and it resolves onto `tidewater-georgian` and `charleston-georgian`
— the same node, one address over from the rule just fixed); and `facade-gable`'s
`gable_treatment/parapet_height` (*"Where the gable is a roof end this rule does not apply at all"*,
`applies_to` 12 nodes including `tudor-revival` and `dutch-colonial-american`).

`slots_except` (WP-5.14) is the mechanism and it works per binding. What is wanted is either a
per-rule construction scope — the thing each of these notes actually describes — or 27+ scoped
bindings. That is a migration and a schema decision, not a patch.
