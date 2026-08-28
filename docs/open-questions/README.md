# The open-question register

One file per question, `<nnn>-<slug>.md`, because **the id is the filename**.
That is not tidiness: it is the whole point. Two sessions issuing id 99 into one
shared file produce a *text* conflict, which git merges by juxtaposition and both
entries survive under the same number — which happened four times in four days.
Two sessions issuing id 99 as a *file* produce an add/add conflict git refuses to
resolve. `faults/`, `rooms/`, `partis/`, `proportions/` and `styles/` have all
worked this way from the start; this register was the one that did not, and it was
the only id family that ever collided.

`docs/open-questions.md` is generated from this directory by
`build/gen_open_questions.py`. Edit the files here, never the index.
`build/check_ids.py` holds filename, id and status to each other.


Decisions deferred rather than made quietly. Two of these came from authoring the Georgian kit end to end, which was the point of doing it.

Status legend: **OPEN** — awaiting a ruling. **RESOLVED** — ruled, with the ruling recorded inline and a pointer to where it took effect.

---

## Where each question was raised, and the register's own history

### From the taxonomy

Questions: [OQ 1](001-sketching-tour-styles-cascade.md), [OQ 2](002-charleston-single-house-style-plan-type.md), [OQ 3](003-log-vernacular-american-descends-german-fachwerk-proxy.md), [OQ 4](004-vredeman-de-vries-s-antwerp-engravings-typed-ways.md), [OQ 5](005-shotgun-house-cape-dutch-real-ancestors-graph-cannot-point.md), [OQ 6](006-mid-century-traditional-spans.md)

### From the proportion layer

Questions: [OQ 7](007-palladio-s-tuscan-entablature-dimensioned-text.md), [OQ 8](008-chambers-s-individual-mouldings-ionic-corinthian-composite.md), [OQ 9](009-composite-architrave-cornice-corona.md), [OQ 10](010-benjamin-s-first-edition.md), [OQ 11](011-palladio-chambers-overlays-exist-five-orders-gibbs-benjami.md)


**7 through 11 are ENVIRONMENT-BLOCKED, not unstarted (recorded 25 Aug 2026).** Every one of them is
the same shape: the text does not give the figure, or the plate numerals are illegible, and closing
it needs a better facsimile rather than more code or more thought. They are therefore blocked on
exactly what WP-4.4 is blocked on. Probed on 25 Aug 2026 from this environment:

```
https://www.loc.gov            -> connection failed (000)
https://archive.org            -> connection failed (000)
https://babel.hathitrust.org   -> connection failed (000)
```

Not a 403 from the proxy as WP-4.4 gets, but a failure to connect at all. Until outbound HTTPS to a
facsimile host is available these five cannot move, and the correct handling of each is what has
already been done: the figure is carried as a judgment rule with a range, or inherited from a source
that does state it, and marked unverified rather than assumed. **Do not close any of them from a
secondary source or a modern redrawing** -- that is precisely how a guess gets laundered as
`measured`, which this corpus forbids. Each entry below says what specifically to look for, so a
person with library access can close them in an afternoon.

### From authoring the Georgian kit

Questions: [OQ 12](012-window-head-wants-splitting.md), [OQ 13](013-entablature-scattered-across-three-slot-groups.md), [OQ 14](014-balustrade-porch-rail-newel-balustrade.md), [OQ 15](015-room-adjacency-rules-holds-six-rules-four-different-kinds.md), [OQ 16](016-rule-still-merge-operator.md), [OQ 17](017-two-mechanisms-exist-regional-conditionality.md), [OQ 18](018-kind-editorial-carrying-parameters.md), [OQ 19](019-determined-by-declarative-only.md), [OQ 20](020-cascade-been-proved-real-depth-up-real-populated.md), [OQ 21](021-variant-ops-match-free-string.md)

### Structural, unresolved

Questions: [OQ 22](022-date-conditional-resolution.md), [OQ 23](023-room-room-grouping-catalogue.md), [OQ 24](024-constraints-prose-kind-severity.md), [OQ 25](025-fault-corpus-yet.md)

### From writing the behaviour-test suite (WP-0.3)

Questions: [OQ 26](026-equivalent-room-type-alias-groups-build-plan-check-py-docu.md)

### From migrating constraints (WP-1.1)

Questions: [OQ 27](027-scope-judgment-constraint-blocked-purely-oq-date-condition.md)

### From migrating the remaining families (WP-1.1, 23 Aug 2026)

Questions: [OQ 28](028-build-modcache-py-process-wide-cache-keyed-real-path.md)

### From proportion-pack bindings (WP-4.1, 23 Aug 2026)

Questions: [OQ 29](029-call-stands-oq-s-pack-retire-two-three.md), [OQ 30](030-islamic-moorish-geometric-proportion-system-independently.md)

### From the garage (WP-4.3, 24 Aug 2026)

Questions: [OQ 31](031-daylight-depth-rule-unsatisfiable-garage-probably-every-no.md)

### From the workbench (WP-5.2, 25 Aug 2026)

Questions: [OQ 32](032-findings-carry-stable-id.md), [OQ 33](033-relaxations-counted-located.md), [OQ 34](034-composer-decisions-prose-lines-records.md), [OQ 35](035-core-check-plan-returns-distinct-validate-jsonschema-packa.md)

### From deployment (25 Aug 2026)

Questions: [OQ 36](036-compose-job-registry-pins-service-single-replica-serialize.md)

### From the deployment audit (25 Aug 2026)

Questions: [OQ 37](037-find-faults-cuts-through-tie-groups-up-wide.md), [OQ 38](038-resolve-kit-choose-pack-reports-unranked-tie-author-s-ruli.md)

### From the export layer (WP-5.1, 25 Aug 2026)

Questions: [OQ 39](039-record-s-vertical-opening-data-thin-half-dormant.md)

### From the real solver (WP-2.3, 25 Aug 2026)

Questions: [OQ 40](040-flat-footprint-versus-declared-wings.md), [OQ 41](041-solver-s-door-floor-sits-below-renderers-draw.md), [OQ 42](042-types-present-aliased.md), [OQ 43](043-equivalent-groups-asymmetric-practice-symmetric-code.md), [OQ 44](044-solver-s-answer-depends-how-fast-machine.md), [OQ 45](045-parti-s-area-range-sf-describes-diagram-composer-instantia.md), [OQ 46](046-ontology-arch-slot.md), [OQ 47](047-ontology-slot-exposed-structural-member-wall-face.md), [OQ 48](048-slot-dimension-address-hold-several-rules-nothing-distingu.md), [OQ 49](049-node-need-rule-pack-without-being-instance-pack.md), [OQ 53](053-check-addresses-py-compares-quantity-units-two-rules-agree.md), [OQ 52](052-elevation-generator-invents-measurements-never-took-fault.md), [OQ 51](051-lineage-cascade-delivers-proportion-packs-nobody-bound-bou.md), [OQ 50](050-ornament-works-being-bounded-looks-like-property-corpus.md)

### Reissued 25 August 2026 — ids 32–41 collided, and this block moved


*Two sessions worked in parallel without knowing of each other, and both issued the ids 32 to 41.*
*Main's ten (deployment, the workbench, the export layer, the surviving WP-2.3) were merged first
and keep their numbers; these ten — the WP-4.5 and geometry rulings, all of them already RULED or
CLOSED — were reissued as **54–63** when the branches met. Old id → new id: 32→54, 33→55, 34→56,
35→57, 36→58, 37→59, 38→60, 39→61, 40→62, 41→63. Every reference in this corpus was rewritten with
them; a commit message or a report written before the merge still carries the old number, and this
table is how to read it. The corpus's rule is that ids are stable and never reused, which is exactly
why one block had to move rather than the two being merged into one numbering.*

### From the real solver (WP-2.3, 24 Aug 2026)

Questions: [OQ 54](054-heuristic-places-rooms-below-their-band-nothing-says.md)

### From partis to full coverage (WP-4.5, 24 Aug 2026)

Questions: [OQ 55](055-courtyard-void-geometry-engine-cannot-draw.md), [OQ 56](056-there-half-storey-split-level-cannot-expressed.md), [OQ 57](057-adjacency-cannot-span-levels-room-catalogue-upper-floor-st.md)

### Ruled with the rest, 24 August 2026

Questions: [OQ 58](058-spend-schema-change-slot-scope-allowlist-hybridizes-with.md), [OQ 59](059-five-twenty-one-partis-carry-fatal-findings-against-their.md), [OQ 60](060-roof-over-a-court-stated-or-derived.md), [OQ 61](061-portal-range-rectangle-portal-range-rectangle.md), [OQ 62](062-composer-s-area-weight-share-total-nobody-states.md), [OQ 63](063-fault-s-secondary-tests-written-style-applied-every.md)

### From the workbench legibility pass (26 August 2026)

Questions: [OQ 64](064-loupe-magnifies-pen-drawing-drawn-language-says-pen.md)

### From the adversarial audit of the legibility pass (26 August 2026)

Questions: [OQ 65](065-projection-parts-means-two-different-things-corpus-split-o.md)

### From the candidate score (26 Aug 2026) — reissued 66-68 at the 26 Aug merge

Questions: [OQ 66](066-score-s-eight-axis-weights-editorial-never-been.md), [OQ 67](067-composer-recommends-different-plans-side-effect-rather-dec.md)

### From the second audit round (26 Aug 2026)

Questions: [OQ 68](068-three-four-parts-fixed-two-rules-still-want.md)

### Reissued 26 August 2026 — ids 64 and 65 collided a second time

Questions: [OQ 69](069-session-scoped-test-fixture-gates-every-test-file-sorts.md), [OQ 70](070-map-s-gazetteer-unversioned-interface-data-about-corpus.md), [OQ 71](071-solver-pin-depends-machine-load.md)


The same thing that happened on 25 August happened again, for the same reason: two sessions
ran in parallel and both issued the next free number. `main`'s work on the workbench
legibility pass took **64** (the loupe magnifying the pen) and **65** (the pack's projection
datum); this branch's candidate-score work had independently taken 64 and 65 and had gone on
to a third. **main keeps both of the collided ids**, and this branch's three were reissued:

| written as | now reads | subject |
|---|---|---|
| 64 | **66** | the score's eight axis weights are editorial and unmeasured |
| 65 | **67** | the composer recommends different plans, as a side effect rather than a decision |
| 66 | **68** | derived proportion rules outside their own declared band |

A commit message, a report or a code comment written before this merge may still carry the
old number. The five commits on `claude/plan-ranking-communication-76kl2w` all predate it and
all use the old numbering; every reference inside the tree has been converted.

**A SECOND PARALLEL-SESSION COLLISION, and the same rule applied as the first time.** Two
sessions again ran at once and both issued from 64. Main's block — the loupe's stroke weights,
the projection datum, the score's axis weights, and the two after them — keeps its numbers,
because it merged first and is cited under them from `docs/reports/`. This branch's three were
reissued:

| raised on this branch as | now | subject |
|---|---|---|
| 64 | **69** | a session-scoped test fixture gating every file that sorts after it |
| 65 | **70** | the map's gazetteer, and the hearths nothing was reading |
| 66 | **71** | the solver's downgrade pin, measuring the machine rather than the proof |

A commit message or report written before this merge carries the old number; so does the
WP-5.6 report, which was written while they were 64–66. The conversion table at the foot of
this register now has two rows of history, and that is itself the finding: **parallel sessions
issuing ids by reading the file and adding one will keep colliding.** It has now happened
twice in two days, cost a renumbering both times, and will cost a third unless the id comes
from somewhere that is not the working tree.


**A THIRD PARALLEL-SESSION COLLISION, in three days, and the rule is now a rule.** Two
sessions again ran at once and both issued from 72. Main's block — the atlas's fine coastline
tier and the five from the infrastructure audit — keeps its numbers, because it merged first
and is cited under them from `docs/reports/wp-5.7-the-atlas-and-the-shell.md` and
`docs/reports/infrastructure-audit.md`. This branch's **twelve** were reissued, which is four
times the size of the last renumbering:

| raised on this branch as | now | subject |
|---|---|---|
| 72 | **78** | the entablature's projection datum, and the bed mould it deletes |
| 73 | **79** | two sourced rules giving the eave cornice two different projections |
| 74 | **80** | the long face that could not draw its own chimneys |
| 75 | **81** | two Benjamin modillion pitches against their own pack's stated unit |
| 76 | **82** | `repeat_positions()`, built and documented and never called |
| 77 | **83** | the sweep rule spelled twice in JavaScript |
| 78 | **84** | `cornice-that-is-a-fascia`'s two rival secondaries |
| 79 | **85** | a stack and a window on one axis, with nothing comparing them |
| 80 | **86** | a kit parameter and a pack rule contradicting each other under two names |
| 81 | **87** | a slot bound `open` inheriting the constraint the style declined to make |
| 82 | **88** | the sill scope that reaches 27 masonry nodes |
| 83 | **89** | measurements withheld, and one supplied as an unconditional constant |

Main's own entry for 73–77 anticipated this and said to renumber here if another session had
taken the block; the rule this register has now applied three times settles which side moves,
and it is not the side that merged. **Every reference inside the tree has been converted.** A
commit message carries the old number and cannot be changed: on this branch that is `f768c02`
and `426ed35`, both written while these were 72–83, and the two WP-5.7 reports plus the reports
then numbered WP-5.8, WP-5.9 and WP-5.10 were written under the old numbers and have been
converted in place. *(Those three work packages have since been renumbered 5.12–5.14 by OQ 90 —
see the last table in this file. The numbers in this paragraph are the ones that were true on
27 August, and are left as written.)*

**Three collisions is not bad luck, it is the procedure.** The last note said this would cost a
third renumbering unless the id came from somewhere that is not the working tree. It has, and it
did, and the cost went up rather than down because the block was longer. Nothing here fixes that;
the next session that reads this file and adds one will collide a fourth time.

### From the atlas and the shell (WP-5.7, 26 August 2026)

Questions: [OQ 72](072-fine-coastline-tier-megabyte-geometry-fifth-single-un-cull.md)

### From the infrastructure audit (27 August 2026)

Questions: [OQ 73](073-container-ships-open-configuration-default-only-variable-p.md), [OQ 74](074-engine-cp-accepted-request-body-worth-seconds-blocked.md), [OQ 75](075-mb-image-dependency-layer-three-libraries-every-endpoint.md), [OQ 76](076-heavy-limiter-simultaneously-too-loose-ten-users-too.md), [OQ 77](077-two-builds-same-commit-ship-different-dependency-trees.md)


*Ids 73–77 issued from a branch, with the register's own warning in view: two parallel
sessions have now collided over this block twice in two days. If another session has taken
these numbers, renumber here and add a third row to the conversion table.*

### From the geometry layer (WP-5.11, 26 Aug 2026)

Questions: [OQ 78](078-entablature-projection-datum-and-the-bed-mould-it-deletes.md), [OQ 79](079-two-sourced-rules-give-eave-cornice-two-different.md), [OQ 80](080-the-long-face-that-could-not-draw-its-own-chimneys.md)

### From the adversarial audit of the geometry layer (27 Aug 2026)

Questions: [OQ 81](081-two-benjamin-modillion-pitches-against-their-packs-stated.md), [OQ 82](082-repeat-positions-built-and-documented-and-never-called.md), [OQ 83](083-the-sweep-rule-spelled-twice-in-javascript.md)

### From the dormer layer (WP-5.13, 27 Aug 2026)

Questions: [OQ 84](084-cornice-that-is-a-fascia-two-rival-secondaries.md), [OQ 85](085-a-stack-and-a-window-on-one-axis-nothing-comparing.md)

### From the four rulings (WP-5.14, 27 Aug 2026)

Questions: [OQ 86](086-node-s-own-measured-parameter-pack-rule-contradict.md), [OQ 87](087-slot-bound-open-inherits-constraint-style-declined-make.md)

### From the adversarial audit of WP-5.14 (28 Aug 2026)

Questions: [OQ 88](088-sash-light-s-frame-wall-sill-rule-reaches-masonry-nodes.md), [OQ 89](089-three-measurements-still-withheld-work-around-gaps-applies.md)

### From the third collision (28 Aug 2026)

Questions: [OQ 90](090-two-different-work-packages-called-wp-5-reports-only.md)

### From the plan-semantics program (WP-6.1 / WP-6.2, 26 August 2026)

Questions: [OQ 91](091-window-unit-type-field-nothing-fills-because-nobody-ruled.md), [OQ 92](092-furniture-placed-wet-rooms-kitchen-nothing-else.md), [OQ 93](093-every-door-hinged-low-rule-decides-hand.md), [OQ 94](094-reference-plan-cannot-satisfy-own-style-s-hard.md)


*Raised by Lucas's review of two rendered Tidewater sheets: "the Chomsky error of colorless*
*green ideas sleeping furiously is still very much in play." Every entry below is what that*
*review turned up and this program did NOT settle.*

### From geometry truth (WP-6.3, 27 August 2026)

Questions: [OQ 95](095-placement-generator-blind-other-level-score-term-see.md), [OQ 96](096-shared-s-first-match-wins-ordering-report-corner-kiss-sha.md)

### From the level-aware generator (WP-7.1, 27 August 2026)

Questions: [OQ 97](097-search-span-term-whether-placement-clears-own-structural.md)

### From the adversarial audit of WP-7.4 (27 August 2026)

Questions: [OQ 98](098-span-check-credits-bearing-wall-across-whole-floor-plate.md)

### Reissued 28 August 2026 — a FOURTH collision, and this block has now moved twice


*The third collision (below) moved this branch's questions from 72-79 to 78-85. While that was
being written, a second session was independently moving ITS block into 78-89 for the same
reason, and merged first as PR #14. So 78-85 collided a second time, in the same file, over the
same rule, four days running.*

**Main keeps 78-90** — the entablature datum, the eave cornice, the dormer layer, WP-5.14 and
its audit — by the rule this register has now applied four times: whoever merged first keeps the
numbers, and it is never the side still on a branch. **This branch's eight moved again, to
91-98.**

| raised as | became (3rd collision) | is now | subject |
|---|---|---|---|
| 72 | 78 | **91** | where a window's authority lives (grammar decides the role, the kit the sash kind) |
| 73 | 79 | **92** | furniture: sizing refused, arrangement to the rooms' own words |
| 74 | 80 | **93** | every door hinged `low`; no rule decides the hand |
| 75 | 81 | **94** | the reference plan cannot satisfy its own style's hard passage rule |
| 76 | 82 | **95** | declared stacking, and what the generator could not fix |
| 77 | 83 | **96** | `_shared`'s first-match-wins can report a corner kiss as a shared edge |
| 78 | 84 | **97** | the search had no span term |
| 79 | 85 | **98** | `span_check` credits a partial wall across the whole plate; the validator is silent on capacity |

**A commit message, report or code comment written on this branch before 28 August 2026 carries
one of the two older numbers**, and which one depends on whether it was written before or after
the third collision — the reports under `docs/reports/wp-6.*` and `wp-7.*` have been converted
twice and now read 91-98; the commit messages were not and cannot be. **Reading a bare "OQ 78"
in this branch's history is therefore ambiguous by date and the date is the only way to resolve
it**, which is the clearest argument yet that ids must not be issued from the working tree.

**Four collisions in four days. The register has now predicted its own next collision three
times and been right three times.** Nothing in this commit fixes that either.

---

## Reissued 28 August 2026 — the WORK-PACKAGE numbers, settled at last (OQ 90)

*Four id collisions in four days renumbered the open questions every time and the work
packages never once, and that asymmetry was a deferral rather than a decision. It is decided
now. **Main's atlas keeps WP-5.7**; this branch's chain moved, by the same rule applied to the
ids four times over — whoever merged first keeps the numbers.*

| was | is now | package |
|---|---|---|
| WP-5.7 | **WP-5.11** | the geometry layer: moulding constructions, coursing, repetition |
| WP-5.8 | **WP-5.12** | the four rulings from the geometry layer, and a correction that did not land |
| WP-5.9 | **WP-5.13** | the roof layer |
| WP-5.10 | **WP-5.14** | the four rulings from the dormer layer |

**WP-5.7 still means main's atlas and the shell's proportions**, and always did.

Four report files were renamed with them. Two of those reports were called
`wp-5.8-the-four-rulings.md` and `wp-5.10-the-four-rulings.md` — **different packages with
identical slugs**, which is why OQ 90's own proposed fallback ("cite the report, never the
number") could not have worked: the report names did not distinguish them either. Each now says
which four rulings it carries, and `build/check_ids.py` fails the build on two reports sharing a
slug, and on any `docs/reports/…md` path cited in the tree that does not resolve.

**Eight commit subjects carry the old numbers and cannot be changed**: `7beb40a`, `529310c`
(WP-5.7, the geometry layer), `fa4bf90` (WP-5.8), `40fc540`, `92fd7f9`, `bfbc7c1`, `f768c02`
(WP-5.9), `426ed35` (WP-5.10). `958276b` and `2c77499` are main's WP-5.7 and are still correct.

**This is the last conversion table this register should ever need.** The cause was never the
numbering, it was that an id was issued by reading the working tree — and a shared file is
where two sessions' answers to "what is the next number" can both survive a merge. The register
is a directory now. Two sessions issuing id 99 create the same PATH, and git refuses to
auto-resolve an add/add conflict.
