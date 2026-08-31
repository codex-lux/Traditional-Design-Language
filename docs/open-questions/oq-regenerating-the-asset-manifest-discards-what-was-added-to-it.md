# oq/regenerating-the-asset-manifest-discards-what-was-added-to-it — and it would also quintuple it

*Status: HALF CLOSED 31 Aug 2026 · Raised in: From the network-egress work (WP-4.4)*

**HALF CLOSED — the destructive half is fixed; what to do about the divergence is not.**

**The half that is fixed.** `build/gen_assets.py` rebuilt `assets/manifest.json` from scratch and
hardcoded `provenance: {"license": "unknown"}`, `file: None` and `status: "wanted"` on every
record. A run silently discarded WP-4.4's 161 hand-added building names (commit `347d0ab`), the
eleven `file` blocks and `sourced` statuses WP-4.4 wrote, the 209 asset-to-fault links
`link_asset_faults.py` derives, and anything `harvest_habs.py --write` recorded — in a 601 KB diff
that reads as a reformat, from a script in neither `check_all.py` nor the Makefile, so the loss
would have happened on somebody's laptop and arrived as a commit. It now carries forward
`provenance`, `file`, `status`, `review_note` and `depicts.faults` by id, and refuses to run over
a manifest it cannot parse rather than treating an unreadable file as an empty one. The division
is the point: the generator owns what it can DERIVE from the corpus — identity, what the record
depicts, the words describing the picture that should exist — and does not own what somebody or
something else went and found out.

**The half that is open, and it is larger than the first.** Running the fixed generator today
emits **1,788 records over 142 style nodes**. The committed file holds **322 over three**
(`georgian-colonial-american` 247, `tidewater-georgian` 46, `english-georgian` 18). Measured: 1,466
records the generator would add, and **zero** in the committed file it would not produce — the
manifest is a strict SUBSET, a frozen snapshot from when this layer was authored, and the
generator has been tracking the corpus's growth ever since without anyone running it.

So "322 image records" is not the shot list. It is the shot list *as it stood over three nodes*,
and every count that quotes it — CLAUDE.md, README.md, STATE-OF-THE-PROJECT.md, `docs/assets.md` —
reads corpus-wide and is not. WP-4.4's own report said the three-node fact "no count anywhere
says"; this is the same finding with the other number attached.

**What needs ruling.** Whether the manifest should become the whole corpus's shot list. It is not
a free change: 1,788 wanted records make the sourced fraction 11/1,788 instead of 11/322, five
times as many gaps become visible at once, and every published figure moves. The argument for is
that the gap is real either way and a shot list that silently stops at three nodes is the quieter
failure. The argument against is that 1,466 new gaps nobody can act on is a number that will sit
there. **Nothing should regenerate until this is ruled** — and now, at least, doing so would not
also destroy what is in the file.
