# WP-1.1 (continued) — migrating the remaining 25 families

*23 August 2026. Companion to `docs/reports/wp-1.1-constraint-rule-language.md` (the worked example) and `docs/constraints.md` (the language and the procedure, updated by this pass). This report covers the second half of WP-1.1: taking the corpus from the worked example's 140 migrated constraints to all 660.*

## Why this ran now

Phase 3 (the elevation generator, WP-3.1/3.2/3.3) closed out this session. Asked what was next, the honest answer — checked against `PLAN-OF-ACTION.md` directly rather than assumed — was that Phase 4 (the 130-kit breadth pass) is explicitly sequenced *after* Phase 1 for a stated reason: "authoring 130 kits against a system that cannot yet read its own constraints produces data that will need a second pass." Phase 1's constraint migration was at 140 of 660 constraints (21%), well under its own ≥60%-of-hard-constraints acceptance bar (it was at 17.7%). Lucas chose to finish Phase 1 before starting Phase 4, which is what this package does.

## What was built

**Batching.** The 25 remaining families (520 constraints across 104 nodes) were split into 8 batches by constraint count rather than a fixed family count, so each batch runs to roughly the same size (30-105 constraints) despite family sizes ranging from 1 node (5 constraints) to 21 nodes (105 constraints). All 8 ran in parallel as independent agents, each scoped to a fixed list of `styles/*.json` files and forbidden from touching the schema, the vocabulary, or any other batch's files. This is `PLAN-OF-ACTION.md`'s own prescribed shape ("one schema owner plus up to nine batch agents... the schema owner merges").

| Batch | Families | Nodes | Constraints | Tested | Judgment |
|---|---|---|---|---|---|
| A | eclectic-revivals | 21 | 105 | 60 | 45 |
| B | victorian, romantic-revivals | 18 | 90 | 34 | 56 |
| C | early-republic, american-folk-vernacular | 14 | 70 | 37 | 33 |
| D | american-arts-and-crafts, continental-baroque-neoclassical, british-arts-and-crafts, iberian-vernacular | 11 | 55 | 22 | 33 |
| E | british-picturesque, low-countries-vernacular, tudor-jacobean, renaissance-classical | 12 | 60 | 17 | 43 |
| F | medieval-british, mid-century-traditional, french-vernacular, contemporary-traditional | 12 | 60 | 32 | 28 |
| G | germanic-vernacular, nordic-alpine-vernacular, antique-classical, british-vernacular, spanish-classical | 10 | 50 | 16 | 34 |
| H | colonial-iberian-americas, mediterranean-vernacular, iberian-islamic | 6 | 30 | 12 | 18 |
| **Total (before reconciliation)** | 25 families | 104 | 520 | 230 | 290 |

Every batch verified its own work (`check_constraints.py` and `validate.py` green for its files) before reporting, and every batch confirmed it touched only its assigned files.

**Reconciliation.** Each batch reported the vocabulary variables it genuinely needed and didn't have, per `docs/constraints.md`'s discipline (list a gap, don't invent one silently — that's the batch agent's job; extending the vocabulary is the schema owner's). Collecting all 8 reports surfaced a lot of overlap — several families independently asked for the same missing concept, which is exactly the "second family that needs it earns it a name" signal `docs/constraints.md` sets as the bar for adding one. 15 new variables were added to `build/constraint_vocabulary.py` (72 → 87 entries), each because at least two independent batches asked for it on unrelated style nodes:

- **Classical order proportion** (`column_height_diameters`, `entablature_depth_ratio`, `intercolumniation_diameters`) — the single largest gap, blocking hard rules across Greek Revival, Jeffersonian Classicism, Beaux-Arts, Neoclassical Revival, French Neoclassical and the antique-classical family.
- **`clear_span_ft`** — a generic structural/opening span, distinct from the existing `room_clear_span_ft` (a *room's* span).
- **`arch_rise_to_span_ratio`** — a full arch's own rise:span proportion, distinct from `window_head_rise_in` (a shallow segmental arch's absolute camber).
- **`wall_material_count`**, **`ornament_area_pct_wall`**, **`gable_count`**, **`floor_area_sqft`**, **`chimney_width_in`**, **`window_head_alignment_in`** (same-storey, distinct from the existing storey-to-storey `opening_vertical_alignment_in`), **`court_width_ft`**.
- **`log_wall_run_ft`** — the single generative rule of the whole log-construction tradition ("no log wall may exceed N feet") turned up, near-verbatim, in five style nodes across two unrelated family trunks (Appalachian, Scandinavian, Swiss) and was untestable in every one before this entry.
- **`garage_door_width_ft`**, **`garage_setback_ft`** — named early because WP-4.3 (a dedicated future work package) exists specifically to give every contemporary buildable variant a garage strategy; three styles' migrated constraints already stated numeric garage rules that needed these.

With the vocabulary extended, a second pass converted 29 of the newly-judgment constraints across 22 files to tested, using the numbers already quoted in the batches' own reports (never re-guessed). This is real, bounded reconciliation work, not automatic — each conversion was checked against the constraint's exact statement, and several genuine gaps were deliberately **not** converted because forcing a test would have meant testing something the statement didn't quite say (`arts-and-crafts-british.c02`'s "one primary material" — ambiguous whether accent materials count — stayed `judgment` rather than guess `wall_material_count == 1`; `jacobean.c01`'s gable rule is conditional on shaped gables being used at all, so an unconditional `gable_count >= 3` test would wrongly fail a house with none; `new-urbanist-traditional.c01`'s garage rule branches on whether an alley exists, with no `alley_present` variable to gate on).

**Corpus-wide result:**

```
660 migrated constraint(s) across 132 node(s)
  tested: 365   judgment: 295
  hard constraints: 441, hard tested: 271 (61.5%)
```

61.5% of hard constraints are now tested, clearing `PLAN-OF-ACTION.md`'s own ≥60% acceptance bar for WP-1.1 (the corpus was at 17.7% before this pass, 56.0% before the reconciliation conversions).

## What was found

**The judgment fraction is real, not a shortfall.** 45% of the full corpus is `scope: judgment`, against the worked example's 24%. This is not under-effort — it is what these particular 25 families' constraints actually state. The two worked-example families (English Classical, American Colonial) are dimension-heavy: sash ratios, storey-height diminishment, wall thickness, all clean numeric rules. Several of the later families are dominated by compositional and hierarchical rules with no number in them at all — Beaux-Arts, French Baroque and French Renaissance Chateau's civic-massing rules (base/shaft/attic division, ornament concentration at accents, *caractère*), Tudor-Jacobean and Renaissance-classical's co-occurrence rules (ornament placement, symmetry, material-and-colour pairing), Queen Anne Free Classic and Queen Anne Spindled's millwork-dimension rules (spindle diameter, bracket spacing, frieze depth — real numbers, just not ones any existing variable names). Batch B's report names this precisely: two Queen Anne subtypes came out 0-of-5 tested, every single judgment call a genuine vocabulary gap rather than a qualitative statement.

**A new disjunction pattern, not seen in the worked example.** The worked example's one disjunction case (`spanish-colonial-american`'s roof pitch) had a safe shared bound — an unconditional ceiling covering both branches. Batch G found two cases with a genuine *gap* between the branches and no such rescue: `scandinavian-log-vernacular.c04` (sod roof 22-30°, split-shingle 35-45°, nothing said about 25-35°) and `swiss-chalet.c04` (snow-precipitation 18-25°, rain-precipitation 35-45°). Both correctly stayed `judgment` — testing at either branch's bound would falsely accept or reject the gap range.

**A rule shape the schema doesn't have a name for.** Batch H's `mexican-hacienda.c04` requires the casco to include several named building types (casa grande, chapel, production building) — a categorical multi-component presence rule. Not a per-room universal claim (the schema's existing judgment category), not a disjunction, not unmeasurable — just a checklist the current `test` object (one expression, one threshold or set) can't express. Left `judgment`, flagged as a possibly-distinct fifth reason alongside `docs/constraints.md`'s existing four.

**A genuine performance cost, found during verification, not caused by the constraint language itself.** Re-running the full test suite after migration surfaced that `build/plan_check.py`'s `_load()` helper re-imports `mcp_server/core.py` fresh via `importlib` on every single `check()` call — which means `core.py`'s own `@functools.lru_cache` on `_data()` (the function that reads every style, fault, kit, room and grouping file off disk) never persists across calls, because each fresh module exec gets a brand-new, empty cache. This is a pre-existing pattern, not something this migration introduced — but a smaller constraint payload kept it cheap enough that nobody had profiled it. With every one of 660 constraints now carrying a full `id`/`scope`/`test` object, `compose()`'s repair loop (which calls `check()` roughly 15-20 times per brief) profiles at 30-40 seconds per brief, and the full pytest suite (287 tests) no longer completes inside a single 10-minute window — it was chunked by file to verify instead. Recorded as open question 28 rather than fixed here: this touches a loading convention (`_load()`/`_mod()`, fresh `importlib.util.spec_from_file_location` per call) used the same way across several files, and choosing a fix wasn't this package's call to make unilaterally.

## Verified against the acceptance criteria

- Every constraint has an id and a scope: yes, 660 of 660, `check_constraints.py` confirms.
- ≥60% of hard constraints carry a test: **yes, 61.5%** (271 of 441), after the reconciliation pass (56.0% before it).
- `check_constraints.py` green: yes, corpus-wide, 0 errors.
- "Which hard constraints of style X are evaluable from a plan record?" answerable: yes, by `scope` and `measurable_from` on every tested constraint.
- No regression on the two shipped plans: **re-verified directly.** `spec-builder-colonial.json` still reports fatal 4 / serious 70 / minor 59 (unchanged — the newly-migrated `colonial-revival` constraints on this exact plan all report `Cannot evaluate`, i.e. correctly unjudged, because this plan doesn't declare the measurements those specific constraints need). `tidewater-georgian-careful.json` still reports fatal 0 / serious 39 / minor 67 (unchanged).
- No regression on the two pinned composer briefs: **re-verified directly.** `family-georgian` still ranks Side-Hall Town House first at fatal 0, and Centre Passage Single Pile still carries exactly its pinned 2 fatal findings. `bungalow-small` still ranks Bungalow, Open and Linear first at fatal 0.
- Full pytest suite: 287 of 287 passing after one stale pinned test was updated (below) — run in three chunks rather than one, per the performance finding above.

## What was deliberately not done

- **Not every reported vocabulary gap was converted.** The reconciliation pass converted 29 constraints using the 15 new variables; every batch report names further gaps (millwork dimensions, mass-comparison ratios, wall-texture counts, per-room universal claims) that either needed a variable this pass judged too speculative to add on a single request, or that this pass simply didn't have the scope to chase all the way through. These remain `scope: judgment`, correctly, and are real bounded follow-up work rather than lost information — every gap is named, with the specific constraint that needs it, in each batch's own report above.
- **The performance finding (OQ 28) was not fixed.** Diagnosed and documented, not repaired — see above.
- **OQ 27 (tagging date-blocked judgment constraints) was not decided.** The remaining families were migrated without an answer, so the un-tagged judgment pool grew from 34 to 295. Still not decided here.

## New open question

Open question 28, appended to `docs/open-questions.md`: `plan_check.py`'s `_load()` helper defeats `core._data()`'s own cache by re-importing the module fresh on every `check()` call, which this migration's larger constraint payload turned from a latent inefficiency into a measurable cost (compose() at 30-40s/brief, full pytest suite over 10 minutes). Two contained fixes are named there; neither was applied, since this package's job was the constraint language, not the loading architecture several files share.

## Files touched

`build/constraint_vocabulary.py` (15 new entries, 72→87); 104 `styles/*.json` files across the 25 remaining families (id/scope/test added by the 8 batches) plus 22 of those same files touched again in the reconciliation pass (test added to a constraint the batch had left `judgment`); `tests/test_constraints.py` (one stale pinned test updated from the worked-example-only counts to the full-corpus counts, its module docstring extended); `docs/constraints.md` (new "The remaining 25 families" section, the stale "68 entries" forward-reference corrected); `docs/open-questions.md` (item 27 annotated, item 28 added); `README.md` (the now-false "constraints are not yet a rule language" line removed, the plan-validator section updated, the spec Colonial's fatal count corrected from 3 to 4 to match its actual current state, counts regenerated via `build/gen_readme_counts.py`); `CHANGELOG.md`; `dist/taxonomy.json` (regenerated build artifact).
