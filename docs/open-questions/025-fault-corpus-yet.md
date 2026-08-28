# OQ 25 — No fault corpus yet

*Status: RESOLVED · Raised in: Structural, unresolved*

**RESOLVED — No fault corpus yet.** This was the seed-stage note as of the original drafting. It is no longer a gap: `faults/` now holds 209 named, tested faults with 846 style exceptions (496 numerically bounded), a `test` object on every one, and `check_faults.py` is green. Slot coverage was full (93 of 93) at the time of this ruling; WP-1.3's `wall_thickness_masonry`/`wall_thickness_frame` split (see item 12) added two slots with no fault authored against them yet, so coverage is currently 93 of 95 — not a regression in the fault corpus, a consequence of the ontology growing after it.
