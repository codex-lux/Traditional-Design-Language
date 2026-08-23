# Changelog

One line per layer per notable change. Versions here track the project's own `v0.x` designation, not any single schema's version number (those are tracked in the schema files themselves — `ontology_version`, `kit_version`, and so on).

## Unreleased (this session, 23 Aug 2026 onward — WP-0.1 through in-progress work)

- **Consolidation (WP-0.1).** v0.6 extracted onto disk as the working tree; `Plan Examples/` (26 reference images) folded in; git initialized; stale duplicates and superseded generations identified and moved off the tracked tree (see `docs/reports/wp-0.1-repo-consolidation.md`).
- **Documentation (WP-0.2).** `README.md` counts corrected and made generatable (`build/gen_readme_counts.py`); `mcp_server/README.md` regrouped to list all 23 tools by layer; `docs/open-questions.md` items 1, 2, 12, 13, 17, 23, 24, 25 resolved and recorded; `docs/README.md` index added.
- **Behaviour tests (WP-0.3).** `tests/` — 35 pytest tests pinning validator, composer, kit cascade, proportion engine, and geometry behaviour against the docs' own claims (two counts corrected where they'd drifted); `build/check_all.py` / `make check` as a single entry point over all data checkers plus pytest. OQ 26 raised (undocumented `EQUIVALENT` room-alias groups).
- **Constraint rule language (WP-1.1).** `schema/constraint.schema.json` (reuses the fault corpus's `test` pattern per OQ 24, extended with `one-of` and `scope`); `build/constraint_vocabulary.py` (68 named variables); `build/check_constraints.py` (new 14th check, wired into `check_all.py`); worked-example migration of 140 constraints across the `english-classical` and `american-colonial` families (106 tested, 34 honestly `scope: judgment`); `docs/constraints.md`. Remaining ~520 constraints across ~25 families not yet migrated. OQ 27 raised (tagging judgment-scope constraints blocked by OQ 22 specifically).
- **Correction to WP-0.2's own record.** `docs/open-questions.md` items 12, 13, and 17 falsely claimed "Executed in WP-1.3" — WP-1.3 had not run. Found and corrected in place (with dated correction notes) while migrating constraints; `docs/reports/wp-0.2-documentation-reconciliation.md` carries a matching correction. See `docs/reports/wp-1.1-constraint-rule-language.md`, "what was found."

## v0.6 — 19 August 2026

Rooms (58), groupings (16), partis (12, 39 styles native), fault corpus (209 faults, 846 exceptions), plan schema and validator (`plan_check.py`, two worked examples), composer (`compose.py`, four-candidate ranking), geometry solver (`geometry.py`, `render_plan.py`), MCP server (23 tools). Kit schema bumped to 0.2.1 during the Georgian authoring exercise; element ontology to 0.4.0 (93 slots, up from 82).

## v0.5 and earlier — through 18 August 2026

Style graph (164 taxa, four ranks, 476 lineage edges), element ontology (82 slots at this point), massing catalog (40 types), proportion engine (36 packs across Vignola/Palladio/Gibbs/Chambers/Benjamin plus non-classical modules), kit mechanism proved on Georgian Colonial / Tidewater Georgian / English Georgian, image manifest (322 records, format-agnostic, authored before files).
