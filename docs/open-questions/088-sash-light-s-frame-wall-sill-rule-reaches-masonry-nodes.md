# OQ 88 — `sash-light`'s frame-wall sill rule reaches 27 masonry nodes, and two more pack rules have the same shape

*Status: CLOSED · Raised in: From the adversarial audit of WP-5.14 (28 Aug 2026)*

**CLOSED 28 Aug 2026 (WP-5.11) — ruled: one scope field, honoured in one place, with a third state for the styles that were built both ways.** `derived_rules` gained a `scope`, decided in `proportion_engine.rule_scope()` beside the numeric `out_of_calibration()` it is modelled on and for the same stated reason (OQ 68): judging a rule against a binding its own note tells you not to use is unjudged reported as failed. `eval_packs` is the single enforcement point, as it is for OQ 49's `slots` and WP-5.10's `slots_except`. **Measured: 102 rule deliveries dropped as out of scope** (opening-proportion's head assembly 54, sash-light's sill 34, facade-gable's parapet 14) **and 120 delivered but flagged `scope_unjudged`** — `english-georgian` no longer resolves a 2.25 in sloped timber sill on a brick wall.

**This entry's own numbers were wrong and the correction is the finding.** It said 27 masonry nodes. Measured: the sill rule reaches **86** nodes, **47** make a masonry cladding canonical, **34** only masonry — and **13 make BOTH masonry and frame canonical** (`charleston-georgian`, `georgian-colonial-american`, `greek-revival-american`, `federal-style`, `new-england-federal`…). For those the construction is a fact about the HOUSE, not the style, so the "27+ scoped bindings" this entry named as the worse option is not merely tedious but **impossible** — no per-node scope can decide a style that was genuinely built both ways. They are delivered WITH the reason attached rather than silently resolved or silently dropped.

**The near-miss, pinned as a test.** The variant predicate was first written with an `any_of` list invented from the rule's prose, reading "not in my list" as OUT — and not one id in it matched the vocabulary the corpus actually uses, so `facade-gable`'s parapet rule would have been dropped on all twelve of its own nodes with nothing said. A scope may only rule on variants somebody has classified; anything else is UNKNOWN. The lists are classified from each variant's own record.

**Not done, and why:** `elevation.py` consumes none of the three scoped rules, so there is no plan-time consumer to wire the better construction fact into. Adding that plumbing would be a second reading of "is this a brick house" with no caller, which is the drift this corpus has been bitten by three times. Original entry follows.<br><br>**OPEN — `sash-light`'s frame-wall sill rule reaches 27 masonry nodes, and two more pack rules have
the same shape.** WP-5.10 scoped `sash-light`'s `window_sill/projection` (2.25 in, *"sloped about 1 in
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

`slots_except` (WP-5.10) is the mechanism and it works per binding. What is wanted is either a
per-rule construction scope — the thing each of these notes actually describes — or 27+ scoped
bindings. That is a migration and a schema decision, not a patch.
