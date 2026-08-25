# Documentation index

One doc per layer, in stack order — bottom (the alphabet) to top (the platform). Read `../README.md` first for the overview; this index exists so a doc is never more than one hop from the layer it describes, and so nothing gets re-derived by hand from the data (see `../build/gen_readme_counts.py` for why that matters).

| # | Layer | Doc | What it covers |
|---|---|---|---|
| 1 | Alphabet — style graph | [`model.md`](model.md) | Ranks, the two inheritance hierarchies (`member_of` vs `lineage`), edge semantics (`descends_from` / `references` / `regional_of` / `reacts_against` / `revives`), why the cascade only follows the first two. |
| 2 | Alphabet — element ontology & massing | *(no standalone doc yet — see `../README.md` §2 and `../elements/slots.json`, `../massings/catalog.json` directly)* | 95 universal slots in 8 groups; 40 massings, each with `expansion_logic`. |
| 3 | Alphabet — rooms & groupings | [`rooms.md`](rooms.md) | 58 room types (furniture, clearances, adjacency, privacy gradient, daylight); 16 groupings and `attaches_to`. |
| 4 | Grammar — proportion packs | [`proportion.md`](proportion.md) | 42 packs as functions not tables; Vignola spine, authority overlays as deltas; module normalisation. |
| 5 | Bindings — kits | [`inheritance.md`](inheritance.md) | The kit-of-parts cascade: how `descends_from`/`regional_of` resolve a style to a directory of slot bindings, `extends` vs restatement, provenance. |
| 6 | Solecisms — fault corpus | [`faults.md`](faults.md) | 209 named errors, element-first with style as a facet via `exceptions`; cause, three-tier fixes, two severity axes, executable `test`. |
| 7 | Constraints (style-level, executable) | [`constraints.md`](constraints.md) | The rule language for the corpus's 660 style constraints — extends the fault `test` pattern with `scope` and a named variable vocabulary; which constraints are evaluable and from where. Migration itself is in progress: 140 done (the `english-classical` + `american-colonial` worked example), ~520 remaining across the other families. |
| 8 | Critic — plan validator | [`plans.md`](plans.md) | The plan schema and `plan_check.py`: six layers (rooms, adjacency/privacy, groupings, faults, code, style), "unjudged is not passed." |
| 9 | Generator — composer | [`compose.md`](compose.md) | Template-seeded, validator-scored; N contrasting candidates, never one; decision logs and trade-aways. |
| 10 | Generator — geometry | [`geometry.md`](geometry.md) | Bay-grid placement with counted relaxations, both levels solved jointly; what it satisfies vs. what it composes. Its last section covers the CP-SAT solver (WP-2.3) — enforced room minimums, named conflict sets, and why the tiling had to become structural rather than arithmetic. |
| 11 | Site & settlement | [`site.md`](site.md) | The `site` schema object, lot-width-aware composing (independently, in both `compose.py`'s estimate and `geometry.py`'s solver), site-scope constraint evaluation, the lot drawn in the SVG, and site-and-settlement kit-slot consumption. |
| 12 | Generator — structure | [`structure.md`](structure.md) | Wall thickness and bearing lines from a new `construction/` catalog, outside-to-outside footprint, span checking, storey heights inverted from the ceiling rule, eave/ridge heights against the style's pitch constraint, stair rise/run/landing; roof form, pitch, chimney placement and per-face silhouettes (WP-3.3, in its own "Roof geometry" section). |
| 13 | Generator — elevation | [`elevation.md`](elevation.md) | Bay layout, window sizing (head-first-sill-second-width-third), the entrance composition and its doorcase order, the eave cornice as "the style's entablature reduction," water table and belt course, and a scope gate keeping this Palladian system off styles it was never sourced for. |
| 14 | Evidence — images | [`assets.md`](assets.md) | Records authored before files exist; `license` never `unknown`; good/bad pairs. |
| 15 | Governance | [`open-questions.md`](open-questions.md) | 27 numbered judgement calls, each RESOLVED (with the ruling and where it landed) or OPEN. |
| — | Reports | [`reports/`](reports/) | One file per completed work package from the Plan of Action — `reports/<wp-id>-<slug>.md` — what was built, what was found, what was deliberately not done, and any new open question it raised. |

## Regenerating things instead of hand-editing them

Two files in this repository are meant to be generated, not typed: the counts block at the top of `../README.md` (`python3 build/gen_readme_counts.py`) and the check-suite entry point (`build/check_all.py` / `make check`, which also runs `pytest tests/`). If you find yourself fixing a number by hand in either place, fix the generator instead — that's the whole reason the 23 Aug review found the numbers drifted in the first place.
