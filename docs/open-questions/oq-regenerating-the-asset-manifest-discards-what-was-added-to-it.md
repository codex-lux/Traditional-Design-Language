# oq/regenerating-the-asset-manifest-discards-what-was-added-to-it — gen_assets.py is a generator over a file three other tools now write

*Status: OPEN · Raised in: From the network-egress work (WP-4.4, 31 Aug 2026)*

**OPEN — `build/gen_assets.py` rebuilds `assets/manifest.json` from scratch, and three other
tools now write to it.** It hardcodes `"provenance": {"license": "unknown"}` at three sites and
emits no `building`, no `location`, no `file`, no `depicts.faults`. So a run of it silently
discards: WP-4.4's 161 hand-added building names (commit `347d0ab`), the eleven `file` blocks and
`sourced` statuses this package wrote, the 209 asset-to-fault links
`build/link_asset_faults.py` derives, and anything `build/harvest_habs.py --write` ever records.
Every one of those resets to `wanted` with no warning and no diff anybody would read as a loss —
the file is 601 KB and the change would look like a reformat.

**Nothing catches it.** `gen_assets.py` is in neither `build/check_all.py` nor the Makefile; it is
mentioned once, at `README.md:134`. It is not run by CI, so the loss would happen on somebody's
laptop and arrive as a commit.

**The shape of the fix is a merge, not a rebuild**: generate the derivable fields, then carry
forward every field the generator does not own, keyed by asset id. That is a small change and it
was not made here because it deserves its own pass — the interesting part is deciding which fields
the generator OWNS (id, kind, role, depicts.nodes, depicts.slots, caption, alt_text, shot_spec) and
which belong to whoever filled them in (provenance, file, status, review_note, depicts.faults), and
that division is the actual question.

**Related and unfixed:** the same file is written by `harvest_habs.py` and `link_asset_faults.py`
at `indent=2` and by `gen_assets.py` at `indent=2`, which agree now only because the harvester's
`indent=1` was corrected in this package. Three writers, one file, no owner.
