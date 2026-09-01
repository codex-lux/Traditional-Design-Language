# oq/regenerating-the-asset-manifest-discards-what-was-added-to-it — and it would also quintuple it

*Status: CLOSED 31 Aug 2026 · Raised in: From the network-egress work (WP-4.4)*

**CLOSED — both halves, and the second was ruled by Lucas.**

**The destructive half.** `build/gen_assets.py` rebuilt `assets/manifest.json` from scratch and
hardcoded `provenance: {"license": "unknown"}`, `file: None` and `status: "wanted"` on every
record. A run silently discarded WP-4.4's 161 hand-added building names (commit `347d0ab`), the
`file` blocks and `sourced` statuses, the asset-to-fault links `link_asset_faults.py` derives, and
anything `harvest_habs.py --write` recorded — in a 601 KB diff that reads as a reformat, from a
script in neither `check_all.py` nor the Makefile, so the loss would have happened on somebody's
laptop and arrived as a commit.

It carries `provenance`, `file`, `status`, `review_note` and `depicts.faults` forward by id now,
and refuses to run over a manifest it cannot parse rather than treating an unreadable file as an
empty one. The division is the fix: the generator owns what it can DERIVE from the corpus —
identity, what the record depicts, the words describing the picture that should exist — and does
not own what somebody or something else went and found out. A regeneration now carries **3,787
fields** it does not own.

**The larger half, ruled: REGENERATE.** The committed file was a frozen snapshot from when this
layer was authored — 322 records over three style nodes — while the generator, tracking the corpus,
emitted 1,788 over 142. Zero records in the file the generator would not produce: it was a strict
subset, and nothing compared them, so "322 image records" read corpus-wide in four documents while
describing `georgian-colonial-american`, `tidewater-georgian` and `english-georgian`.

Lucas ruled on 31 Aug to regenerate. The manifest now holds **1,850 records over 142 style nodes**
— 1,788 from the pair/diagram/comparison generation plus 62 more when the profile block stopped
naming five packs and started walking all of them.

**What the ruling cost and bought, measured.** 1,777 records are `wanted` against 311 before, so
the visible gap is five and a half times larger and that is the honest state rather than a
regression. Against it: **845 records now name a real building to look for** across **330 distinct
queries**, where before 161 records named **eleven** buildings and a perfect harvest would have
returned eleven photographs; and **73 records are sourced** against 11, because the profile
generator was drawing five packs out of twenty-five it could draw.

**The guard that replaces this entry.** `tests/test_render_profile.py::
test_the_committed_manifest_is_what_the_generator_emits` runs the real generator against a copy of
the real manifest and asserts the id sets are identical — not the whole file, because the carried
fields are not the generator's to produce. The divergence cannot reopen silently; that was the
whole failure.
