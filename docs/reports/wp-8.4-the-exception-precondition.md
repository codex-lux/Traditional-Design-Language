# WP-8.4 — an exception is a licence, and nothing had ever read its condition

*28 August 2026. Branch `claude/planning-items-e6c13s`. Closes the exception half of the
fault corpus's precondition layer, closes OQ 86, reconciles OQ 88 against main's own answer
to it, and raises two named questions. The package also collided with `main` head-on, which
is the second half of this report.*

---

## I — What was wrong

`mcp_server/core.py` selects a fault exception with `e["style"] == style`, at three sites, and
nothing else. **331 of the corpus's 846 exceptions carry a precondition** — 123 naming a
construction, 102 a date range, 79 a region — and not one line of code read any of it.

An exception is a **licence**: it says the general rule does not convict this style, and where
it carries a `bounds_test` it *replaces* the fault's primary test outright. So a precondition
nobody reads is not a harmless omission. `architrave-that-is-not-there`'s Pueblo Revival
licence is written for `construction: [adobe, rammed-earth]`, and `pueblo-revival` resolves
canonically to **stucco-over-wood-frame**. The corpus was excusing a framed house under an
adobe rule, and had been for as long as the field existed.

### Why nobody had read it

`schema/fault.schema.json` carried **two fields called `applies_when` meaning different
things**: one a precondition on MEASUREMENTS (evaluated since WP-5.13), one a precondition on
CONTEXT (evaluated by nothing). `check_faults.py` validated the `slots` key of the second and
stopped. Two mechanisms under one name is the condition under which *"the guard exists"* and
*"the guard runs"* stop being distinguishable to a reader, and this pair spent a year in
exactly that state.

The unread one is renamed **`granted_when`** on all 331 records. `check_faults.py` now errors
on the old name, and the schema's `additionalProperties: false` catches it a second way.

---

## II — The construction vocabulary

78 distinct construction tokens were in use, mixing five kinds of fact — wall assembly
(`adobe`, `solid-masonry-two-wythe`), cladding (`thick-stucco`, `shingle-cladding`), glazing
(`crown-glass`), roofing (`slate-roof`) and site condition (`zero-lot-line`) — and spelling one
idea five ways (`masonry` / `solid-masonry` / `load-bearing-masonry` / `mass-masonry` /
`mass-wall`), barrel tile four ways and wood shingle three.

`build/construction_vocabulary.py` is a **mapping table, not an ontology**. It maps 61 tokens
onto variant ids that ALREADY EXIST in `kits/`, and records the other 17 as **UNMAPPABLE with
a reason apiece** — no new corpus ids are authored on the authority of fault-exception prose,
per the ruling. `check_table()` fails the build if a mapped id stops existing: a token pointing
at nothing resolves `fails` for every style in the corpus and revokes a licence in silence.

Three design rules earned their place by being wrong first:

**Slot order is authority order.** A token's slots are read most-decisive first, and the first
that can answer decides. `construction_type` states the wall assembly; a cladding is only
evidence about it. Treating a disagreement between them as a contradiction is what a flat
combination does, and it left `pueblo-revival` — `stucco-over-wood-frame` canonical with
`earth-toned-stucco` on the face — reading *"the record points both ways"* on 15 nodes. **A
render is not a wall.**

**A canonical outranks a permitted.** `jeffersonian-classicism` inherits a `construction_type`
in which every variant is merely *permitted*, so that slot cannot decide; its own cladding is
canonically Flemish-bond brick with clapboard FORBIDDEN. Reading the permitted
`beaded-clapboard` as *"this might be a frame house"* left a brick node undecided and still
receiving a sloped timber sill — the very delivery OQ 88 exists to stop. What a style says
CANONICALLY is what it is.

**A `partial` token may fail but never hold.** `thick-stucco` is the type: the kit records the
render and says nothing about its depth, and no slot, kit parameter or pack rule anywhere
carries a render thickness. Its best case is `undecidable`. Confirming on the half we can see
would widen a licence its author deliberately narrowed.

---

## III — Three verdicts, and judging both ways

`grant_exception()` returns `granted` / `refused` / `unjudged`, never a bool, because *"is this
house adobe"* is usually unanswerable from a style id — most styles permit several
constructions.

Where an exception carries a `bounds_test`, an unresolved precondition means nobody can say
which of two rules governs. **So both are run and compared.** Where they agree, the question is
immaterial and the fault is answered; where they disagree, it is could-not-evaluate, naming the
condition it could not resolve. Measured over 164 styles that is the difference between **26
verdicts moving and 11**. A fake unjudged is as dishonest in its own direction as a fake pass.

### The census, ratcheted

| | |
|---|---|
| exceptions | 846 |
| carrying `granted_when` | 331 |
| naming a construction | 123 |
| **granted** | **46** |
| **refused** | **20** |
| **unjudged** | **57** |
| carrying a substituting `bounds_test` | 89 |
| of those, unjudged | 47 |
| `regions` populated, not evaluated | 79 |
| `date_range` populated, evaluated only with a caller's date | 102 |

### What is counted instead of evaluated, and why — measured, not assumed

**`regions` is not evaluated.** 78 of its 79 uses name a region that CONTAINS the style's own
regions or hearth: *"New England"* over a style whose regions are Massachusetts, Connecticut
and Rhode Island; *"british-isles"* over England, Scotland, Ireland; *"South Carolina low
country"* over Charleston peninsula. The key restates the style match at a coarser grain. The
one that does not is **`lever-on-a-period-door` on `french-eclectic`** — regions France and
Continental Europe against a style whose own region is the United States — and it is named
rather than left to be found again. Closing this properly needs a gazetteer with containment,
not a mapping: the 45 tokens in use are free text under two spelling conventions
(`gulf-coast` and `Gulf Coast`, `chesapeake` and `Chesapeake`) and the style corpus's own 219
region names are free text too.

**`date_range` is evaluated only where a caller supplies a date.** Of its 102 uses, 23 contain
their style's whole floruit and 79 overlap it, and **not one is disjoint from it**. A date test
against a style's floruit can therefore never refuse a licence, and would convert 79 decidable
questions into unjudged ones on the strength of our own missing input rather than anything
about the building.

**`plan_check` now passes the house's own record** — `plan.declared` and
`context.date_of_representation` — which is what makes this real rather than deferred. Both
reference plans already declare `construction_type` and a date.

**An unevaluated key does not block a grant, and that is stated rather than slipped in.** Before
this package every one of these preconditions was ignored; reading the ones we can read and
refusing where they refuse is a strict improvement. Treating the ones we cannot read as
blockers would turn a licence into an unjudged fault on the strength of a missing evaluator
rather than a fact about the building.

---

## IV — The verdict diff, and the convictions read as suspects

Eleven (fault, style) pairs move across 164 styles: 8 present → unjudged, 1 clear → unjudged,
1 present → clear, 1 clear → present. Per the ruling, every new conviction was read before
being accepted.

**`pueblo-revival` / `house-without-a-base`, clear → present, is correct and the exception's
own prose says so.** Its `bounds` read, before this package and after: *"Requires the batter
and requires a genuinely thick wall reading. **A thin stuccoed frame box sitting on the ground
is not this.**"* Pueblo Revival resolves to `stucco-over-wood-frame`. The corpus wrote the
condition down, nothing read it, and the first thing reading it enforced the record's own
words.

**`pueblo-revival` / `architrave-that-is-not-there`, present → clear**, is the same mechanism
in the other direction: the adobe licence is refused, the general rule runs instead, and the
general rule passes. A refusal that makes a fault go away is as much a finding as one that
makes a fault appear.

### Two data errors, both OQ 87, found by the refusal biting

- **`spanish-colonial-revival`** binds `roof_material` **`open`**, so `resolve_slots` walked
  past it to `french-baroque` — nine steps along a 59-node chain — and the corpus was stating
  that a Spanish Colonial Revival house is roofed in **slate**, with a note quoting
  Vaux-le-Vicomte. Its own record says *"low-pitched, 3:12 to 5:12, in red clay barrel or
  mission tile"* in a defining characteristic AND a hard constraint.
- **`cotswold-vernacular`** binds `construction_type` `open` and resolved it from
  `roman-classical`, giving a Cotswold limestone house `arcuated-concrete-or-brick` CANONICAL
  under a rule about Greek and Roman antiquity. Its own record: *"Walls of coursed or random
  oolitic limestone rubble, 500-700 mm thick, in lime mortar."*

Both are bound now on their own nodes' evidence. The Spanish one surfaced as an **acquittal**
rather than a conviction, which is worth remembering the next time a refusal makes a number
improve.

---

## V — The guard that did not reach its own function

The per-rule construction scope refused **0 of 293 deliveries on its first run, with every
check green.** `proportion_engine.evaluate()` rebuilds each rule row key-by-key and dropped the
new field — the exact failure its own comment describes, **in the comment that claims a test
prevents it**:

> *calibrated_for and diagnostic … were dropped here … a row rebuilt key-by-key from a richer
> source drops whatever nobody re-listed. tests/test_wp46_packs.py compares this dict against
> the schema so it cannot recur.*

No such test existed. The one that does is `test_score.py`'s
`test_rule_keys_publishes_every_key_the_pack_schema_defines`, and it reads
`mcp_server/core.py`'s `RULE_KEYS` — a **different** key-by-key rebuild, one layer further out.
So the function whose own comment tells this story was the one function nothing checked. This
is the third instance of WP-6.4's *"a comment claiming a check that was never written"*.

Both rebuilds are pinned now. The engine's guard reads a **real emitted row** rather than the
source, because a key present in the dict literal and overwritten below would still pass a
source-reading test.

---

## VI — OQ 86 closed: `kit_vs_pack` was a per-file check wearing a per-node name

`check_addresses.kit_vs_pack` read `load_kit(nid)` — the node's **own file** — while comparing
against rules `eval_packs` had assembled from the whole cascade. The one case it could never
see was a node inheriting its parameter from one ancestor and its pack from another, which is
most of the corpus.

Reading the cascade takes the published **62 to 1,231**, at **37 distinct (slot, dimension,
pack) addresses**. The 62 was a floor wearing a measurement's clothes. The distinct-address
count is the number that can be worked: one ancestor's parameter meeting one pack is re-counted
at every descendant, exactly as OQ 51's 3,356 inherited packs are.

A rule marked `refused_by_kit` or dropped out of scope no longer counts as a contradiction —
it writes nothing, so it cannot contradict anything.

---

## VII — The collision with main, and the reconciliation

**While this package was being written, `main` shipped its own answer to OQ 88, its own OQ 99
and its own WP-8.1.** The fifth collision in four days, and the first to hit a *mechanism*
rather than an id.

Main's answer: a `scope` field on a `derived_rule`, decided in `proportion_engine.rule_scope()`,
with `construction: [masonry|frame]` and `slot_variant: {any_of, none_of}`, dropped by
`eval_packs` with its reason and flagged `scope_unjudged` where undecidable. This package's
answer had the same shape under a different name, decided in a different function, reading a
61-token vocabulary instead of a two-value enum.

**Lucas ruled: main's field survives, this vocabulary is ported into it.** That is what
shipped. `applies_when` on `derived_rules` is gone; `scope` is the one spelling; `rule_scope()`
is the one decision point.

### The port is not cosmetic, and the number says why

Main's `construction_of()` classified a node masonry / frame / mixed by **substring match** over
its canonical `primary_cladding` ids — `"brick"`, `"stone"`, `"stucco"`, `"tile"` and eight
more. A substring test over a **surface** cannot answer a question about an **assembly**, and
measured against each node's own `construction_type` it disagreed on **13 of 164 styles, in
both directions**:

| node | its wall | its face | the substring test said | and so |
|---|---|---|---|---|
| `cape-dutch` | `sun-dried-brick-or-rubble-masonry`, timber frame FORBIDDEN | `lime-plaster-limewash-white` | **frame** — no masonry word | the frame-wall sill rule went to a mass masonry wall |
| `prairie-school` | `platform-frame` canonical, solid masonry FORBIDDEN | `roman-brick` | **masonry** | the frame rule was dropped from a framed house |
| `storybook-style` | `wood-frame-wire-lath-portland-cement-stucco` | `troweled-modelled-plastic-stucco` | **masonry** | same drop |
| `beaux-arts-american` | `masonry-veneer-over-frame` canonical | `stone-ashlar` | **masonry** | right, by accident |

`cape-dutch` is the one to remember: **OQ 88's own bug, surviving inside OQ 88's fix.**

After the port, with slot-authority and canonical-outranks-permitted: `sash-light`'s sill rule
is dropped on **28** nodes and delivered flagged on 17; `opening-proportion`'s head assembly
dropped on **60**, flagged on 17; `facade-gable`'s parapet dropped on 14, flagged on 61. Main's
`mixed` has not been lost — it is what `undecidable` means, and it is still delivered rather
than dropped.

### The register: a directory AND a slug

Main's OQ 99 froze the numbers at 99 and named every later question `oq/<slug>`. This branch's
WP-8.1 had made the register a **directory**, one file per question. **Both survive, because
they are complementary**: the directory turns a duplicate id into an add/add conflict git
REFUSES instead of a text conflict it merges by juxtaposition; the slug makes the id
underivable from the working tree in the first place. `check_ids.py` now refuses a numbered
file above 99 and reads both forms; `check_citations.py` reads the directory through
`check_ids` rather than parsing the generated index, which it had been doing — it failed
loudly the moment the shape changed, which is why that reconciliation was five lines and not a
silent outage.

This branch's OQ 99 became **`oq/forbidden-stops-the-pack-cascade`** under main's own ruling.
A bare "OQ 99" in this branch's history before 28 Aug means the forbidden slot; on main it
means the id scheme. That ambiguity is the entire argument the ruling makes, arriving one
collision after it was written down.

**OQ 90 is closed by the same reasoning, at its third option: a work-package number is a LABEL,
not an identifier — cite the report.** Renumbering this branch's chain a second time
(5.11–5.14 → 5.15–5.18, plus 8.1) touches 199 references, 64 of which are WP-5.11 citations
that now belong to two packages and would each have to be read. And commit messages carry these
numbers and cannot be rewritten, so renumbering makes the reports disagree with the history
rather than agreeing with it — which is the argument main's OQ 99 makes for not migrating the
numbered questions, unchanged. What actually protects a citation is already built:
`check_ids.py` fails the build when two reports share a filename slug.

---

## VII½ — OQ 89's remainder, and a tie the cascade created

Main closed OQ 89 while this branch was working. Auditing its fix against this package's plan
left two things, both the same shape as everything else here.

**`build/elevation.py` read `shutter` and `window_head_masonry` off the RAW kit**, three lines
below a comment that says *"the CASCADED dormer slot, not the raw one. `tidewater-georgian`
binds this slot EMPTY — **exactly as it binds `shutter`**"*. The comment named the slot and did
not reach it. Measured:

- **`jeffersonian-classicism`** is the one node where the two records disagree about shutters:
  its own file says nothing and its cascade makes `none` canonical. OQ 89's conditional pair
  therefore supplied a real 2.0/2.0 there and `shutter-on-an-unshutterable-opening` came back
  **CLEAR on two shutters the style declines** — OQ 89's own defect, surviving on one node
  because of which record was read. Now 39 styles clear and 2 not-applicable, against main's
  40 and 1.
- **`window_head_masonry` is EMPTY in the raw kit on 66 of 164 styles** and populated by the
  cascade, so `_head_radius_in` was reading no head specification at all on two thirds of the
  corpus. Styles that can state a head radius: **8 → 29**.

**And the fix created a tie worth recording.** A resolved record is a MERGE, so
`mid-atlantic-georgian` comes back with three canonical masonry heads where its own file names
one, and the date rule then picked the first flat arch in list order — the ancestor's
`gauged-flat-arch`, not the `keystoned-flat-arch` the style is distinguished by. A test caught
it. The tie is broken by the node's own word, which is the same principle the construction
vocabulary needed one section earlier: **what a node says itself outranks what it inherits.**

## VIII — What was found and not fixed

**A pack value baked into a kit file is a second delivery path that no scope reaches.**
3,176 `kind: derived` parameters carrying a `source: <pack>` resolve corpus-wide, and **20 now
deliver a figure the live rule refuses**, across fourteen nodes. Deleting the baked parameter on
an ancestor removes it from every descendant, and most of the nodes resolving it are ones the
rule is right for. Counted, ratcheted, and raised as
`oq/a-baked-pack-value-is-a-second-delivery-path` rather than patched.

**The measurement itself had to be fixed to see them**, and that is the part to carry forward:
the two refusals are reported two different ways — WP-8.3's kit refusal MARKS the row, OQ 88's
scope DROPS it and records the drop separately — so reading only the marked rows made the count
report **0** the moment the scope started biting. The number went to zero because the evidence
had been removed, not because the collision had.

**`applies_when` still means two things across the corpus.** After the rename,
`fault.schema.json` has one (measurements, 13 records) and `kit.schema.json` has one (context,
155 records) — and the kit one is itself **half-read**: `resolve_kit` evaluates its `date_range`
and ignores its `regions`, `construction` and `climate_zones`. That is the same shape as the
exception precondition this package just closed, one schema over, found while closing it.
Raised as `oq/applies-when-means-two-things`.

**Eight exceptions are unreachable.** `check_faults.py` permits a `construction:` or `region:`
pseudo-id in `exceptions[].style` and eight records use one — but every selection site matches
`e["style"] == style` against a real style id, so none of them can ever be selected. A designed
mechanism nothing implements; named here rather than removed, because the intent is legible and
the fix is a scope, not a deletion.

**Nine nodes state their construction in prose and cannot be read for it.**
`construction_type` resolves `specified` with an empty variant list on
`log-vernacular-american`, `appalachian-log-house`, `swiss-chalet`, `dogtrot-vernacular`,
`german-fachwerk`, `germanic-vernacular`, `nordic-alpine-vernacular`,
`north-german-hall-house`, `scandinavian-log-vernacular` — every one of them a family whose
whole identity is its construction, each stating it in a `rule` string no machine reads. (The
same shape is 3,316 (node, slot) pairs corpus-wide, but most are dimensional slots where a
prose rule is the right record.)

---

## IX — Verification

- `python3 build/check_all.py` green: **41 checks** (38 in the loop plus three appended
  suites), **1,154 tests**, with the two CAD selftests and the fastapi suite reporting
  COULD NOT EVALUATE for want of optional dependencies — a named unjudged state, never a pass.
- **`build/check_division_guards.py` is new**, and it is the reproducible form of a number
  OQ 89 left as prose. Every dividing test — primary, secondary, or an exception's substituting
  `bounds_test` — against every measurement a generator supplies as ZERO, swept over all 164
  styles rather than guessed from a name (which is how OQ 88's irreproducible "27" happened).
  **306 unguarded dividing tests, of which 0 divide by a name that can actually be zero.**
  That second figure is pinned at zero and goes non-zero in exactly two ways, both the same
  bug from opposite directions: a generator starts supplying a new zero — which is precisely
  what WP-5.13 did, convicting two houses — or an unguarded test starts dividing by one that
  already exists. Mutation-checked by unguarding `dormer-off-the-bay`'s parity test, which the
  checker named along with the 41 styles that supply `dormer_count` as 0.
- **Swept all 164 styles**, never the two reference plans. Worth stating plainly: **the two
  shipping plans show none of this.** Neither `tidewater-georgian` nor `colonial-revival` has an
  exception whose precondition is undecidable AND whose two branches disagree, so a
  before/after on them is byte-identical. CLAUDE.md's own rule — verifying on the plans that
  happen to ship is verifying on 2 of 164 — is what found the 11.
- Every ratchet moved is re-pinned in this commit: `kit_vs_pack` 62 → **1,231**,
  `baked_vs_refused` new at **20**, and the exception census pinned as four ceilings (unjudged
  57, regions 79, date_range 102, bounds_test_unjudged 47) and four floors (`granted_when` 331,
  construction 123, granted 46, refused 20).
- Every new assertion mutation-checked, with `rm -rf __pycache__` between mutating and
  re-running. The engine-row guard was checked by deleting the key it guards and confirming the
  failure.
