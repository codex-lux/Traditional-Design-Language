# WP-4.6 — the missing proportion packs

*Started 24 Aug 2026, continued 25 Aug. **Partially delivered: seven packs of a list of
thirty-odd**, chosen by measured leverage. What remains is listed at the end with the
measurement, not left implied.*

## The work list, and how the first two were chosen

WP-4.1 bound 129 of 132 buildable nodes and produced a consolidated list of packs the library
does not have — every "gaps found" section from fifteen batch reports, deduplicated, with which
batches independently confirmed each. Thirty-odd items across orders and ornament, facade
systems, and modules.

`PLAN-OF-ACTION.md` names seven "likely candidates". Rather than work the list in the order it is
written, the two authored here were chosen on two measurements taken first:

| pack | buildable nodes it would serve | unblocks a node with **no** binding? |
|---|---|---|
| Islamic/Moorish arch-and-ornament | **15** | **yes — two of them** |
| adobe / rammed-earth module | 5 | no |
| Greek Doric order | 5 | no, but replaces a **known wrong binding** |
| Gothic Revival facade + opening | 4 | no |
| Dutch gambrel module | 3 | no |
| cast-iron / ironwork | 3 | no |

The Moorish system is OQ 30's item — the single most-corroborated gap WP-4.1 found, reported
independently by three batches working unrelated file lists — and the only one that reaches a node
carrying no binding at all. Greek Doric is the gap whose absence WP-4.1 had already written down
as a *wrong binding* rather than a missing one, which is worse: `greek-classical` was bound to
`benjamin-doric` under a note calling it "the least-bad available approximation."

## `proportions/orders/moorish-arch.json`

The system of support and springing: impost, horseshoe arch, alfiz, and the geometric setting-out
the ornament is struck from. `strength: reconstructed`, from Owen Jones and Goury's measured
Alhambra drawings (1842–45), Creswell on Córdoba, and Bourgoin's plates for the geometry — because
there is no Hispano-Islamic *Regola* and claiming `canonical` would be inventing a treatise.

**It has no `column` block, and that is the finding.** `styles/moorish-andalusian.json`'s own
governing logic reads *"no order and no absolute module… geometric generation from a square,
compass-and-straightedge."* At Córdoba the shafts are spolia — reused Roman and Visigothic columns
of whatever length came to hand — and the arcade is brought to a common springing by the **impost
block**, not by cutting columns to a proportion. So the module is the generating square's side,
divided into eight because eight is what the *khatam* turns on, and the pack asserts nothing about
column height. Every other order pack in the library has a column block, so the absence is spelled
out in the module note rather than left to be noticed.

The number the system turns on is the **return**: how far the arc continues below the springing
line, banded 0.33–0.50 of the radius, Visigothic precedent nearer a third and mature Córdoban work
nearer a half. Below a third it reads as a sagged semicircle; above a half the clear width at the
impost drops below what a person needs — which is a real egress conflict and is recorded as one.

**Bound to 8 nodes**, primary on `moorish-andalusian`, `mudejar` and
`andalusian-courtyard-vernacular`; secondary on `andalusian-spanish-revival` and
`spanish-plateresque`; *optional* on `mission-revival` and `mediterranean-revival`, because those
styles' arcades are round-arched on piers more often than horseshoe and an optional binding is the
honest shape for a vocabulary a style sometimes reaches for.

**`DELIBERATELY_UNBOUND` shrinks from three nodes to one.** `moorish-andalusian` and `mudejar` come
off it because the reason they were on it has gone. `egyptian-revival` stays, its reason untouched.

## `proportions/orders/greek-doric.json`

`strength: reconstructed`, from Stuart and Revett's *Antiquities of Athens* (1762–1816) with
Lafever for the American transmission. WP-4.1's binding note listed four defects in using Benjamin
for `greek-classical`, and this pack corrects all four against the measured Parthenon:

| | Benjamin 1830 | Stuart and Revett |
|---|---|---|
| column height | 7 diameters | **5.5**, inside the style's own stated 4–6.5 |
| entasis begins | at the foot | at the **lower third**, which c04 specifies |
| annulets | "Roman character" | Greek, small and sharply cut |
| mutules | one per triglyph | over **triglyph and metope alike** |

It also states what a Greek Doric has none of: `ornament_vocabulary` count **0, range [0, 0]** —
because absence is this order's most-broken rule and the range is the pack refusing to leave room
for it.

**`benjamin-doric` is demoted, not deprecated.** It is the right pack for American Greek Revival
work, which is most of it — those buildings really were built from those plates. This pack is the
archaeological order they were imitating. Both are true and they are not the same thing, so
`greek-classical` gets this one primary and Benjamin secondary, and the four revival nodes get it
secondary beside Benjamin, so a plan can be checked against both — what was built, and what it was
reaching for. Where they disagree, the disagreement is the finding.

**The Doric corner conflict** is recorded as a `conflict` with no solution, because it has none: a
triglyph must centre on every column, centre on every intercolumniation, and land on the corner,
and those three cannot all hold. The Greeks contracted the corner intercolumniation — a deliberate,
measurable irregularity in the most regular building there is.

## What this raised

**OQ 46 — the ontology has no arch slot.** 95 slots and not one of them is an arch, an arcade, or
an opening head as a structural member. A system whose whole content is arch geometry had to
target a horseshoe's return at `window_head_masonry` and an impost block at `porch_support`, and
both are recorded in the pack as the compromises they are. Not only a Moorish problem: the Gothic
Revival pack, the Romanesque order, Rome's arcuated bay rhythm and the Italianate round-arched
window all want to say something the corpus has no place to put.

## Second tranche, 25 Aug 2026

### `proportions/modules/adobe-module.json` — the gap the corpus had already written down

This one did not have to be found. **Four style nodes name it in their own binding notes**, in so
many words — `spanish-colonial-american`, `new-mexico-adobe`, `california-mission-colonial` and
`monterey-colonial` each say a dedicated mass-wall/adobe module is missing and that their real,
numbered wall constraints have no pack behind any of them. WP-4.1 confirmed it independently from
three batches besides. Until now those nodes carried `room-vernacular` alone, which is a
beam-limited *room* system, genuinely close on the one dimension it shares (span-limited room
width) and silent about walls.

`strength: reconstructed`, from Bunting's measured New Mexico survey (1976), McHenry on the wall
physics (1984), and 14.7.4 NMAC for the ratios. **The code citation is the dangerous one and the
authority note says so**: a code figure looks like a historical measurement and is not — 14.7.4
NMAC stands to adobe practice roughly as Vignola stands to Roman work.

The module is **one adobe laid as a header**, 14 in, part = one inch. That is the pack's one real
idea: a mass wall's thickness comes in whole bricks and cannot come in anything else, which is why
every survey reports 24–36 in and none reports 20. One module is the thinnest bearing wall; two is
a house; three is a church.

Three things it found:

- **The slenderness rule is a ceiling, not a generator, and the band is a disagreement.** 14.7.4
  NMAC says wall height ≤ 10 × thickness; `california-mission-colonial`'s *own record* says 8
  ("buttresses or thickened piers wherever wall height exceeds roughly eight times wall
  thickness"). Both are right — the code assumes a reinforced bond beam the mission builders did
  not have — so the rule carries 8–10 as a range rather than an average. And for a two-adobe house
  wall it never binds at all: nothing about a house's height comes from it. What sets house wall
  height is the viga and the ceiling.
- **The bracing length is what makes the plan a chain**, and it is the exact analogue of the log
  pen's sixteen feet. An unbraced earth wall fails out of plane past ~10 × its thickness, i.e.
  ~24 ft for a two-adobe wall — which is why an adobe building is a chain of ~24 ft ranges whose
  party walls are structure, why there is no large room, and why the placita is what you get from
  adding ranges and turning the corner.
- **The reveal is the one figure that cannot be faked**, so the pack states it with the *same
  expression* as the wall thickness rather than two figures that happen to agree. Stucco on frame
  gives 5½ in against 29, and no other move on the elevation recovers it.

Bound to **9 nodes**: primary on the five where the wall is the only generative system there is,
secondary on `monterey-colonial` (whose *upper* storey is genuinely classical and keeps
`facade-classical` primary) and `andalusian-courtyard-vernacular` (reached through tapia rather
than adobe, where the whole-brick argument does not apply and the pack says so), and secondary or
optional on the two revivals — where the note is explicit that the wall is stucco on frame and the
pack is a statement of what is being imitated, not a claim about construction.

**Five stale sentences retired.** The four nodes' "missing from the corpus" claims, and a fifth on
`monterey-colonial`'s `storey-graduation` binding that said no pack owns the wall-plane step. Each
was superseded *in place* rather than deleted, so what was asked for stays legible beside what was
delivered. The fifth is only half-retired and honestly so: `adobe-module` now derives the 24–30 in
below the step, but the **step itself** is owned by no pack and cannot be — it is not a dimension,
it is the joint between two proportioning systems, and its size is just the difference between what
each says the wall is.

### `proportions/systems/opening-pointed.json` — the opening half, and why only the half

WP-4.1 asks for "a Gothic Revival facade **and** opening system", confirmed by PB-7a and PB-8, with
PB-7a recording that `rural-gothic-villa` came out of WP-4.1 with **no opening-role pack at all**.

**The facade half was measured before it was built, and mostly does not exist.** All four Gothic
Revival nodes already carry `facade-picturesque` in the facade role and it fits them — asymmetry,
incident over rhythm, the gable as the compositional event. A second facade pack for those four
would have been duplication dressed as coverage. So this pack is `kind: opening-system`, and the
narrowing is stated rather than quiet.

**The facade gap is real for exactly one node and for a different reason than the list gives.**
`english-gothic` is not a revival — it is the medieval building, and `facade-picturesque`'s
nineteenth-century picturesque argument is an anachronism against it, which is why that node
carries no facade pack and should not be given this one. What it wants is a *medieval English*
facade system, which is the same missing pack as the pre-Palladian English facade gap the candidate
list already records (Elizabethan, Tudor, Jacobean, falling between `facade-classical` and
`facade-picturesque`). **Those two list items are one pack seen from two sides**, and merging them
is this tranche's contribution to the candidate list.

The system is **the strike ratio**: radius ÷ span, which is Rickman's discrimination of the English
arch families compressed into one number. 0.75 the drop arch, 1.0 the equilateral, 1.5 acute, 2.0 a
true lancet; past 2.0 the opening is ecclesiastical and a house wearing one looks like a chapel.
The module is **the span**, not the height — a pointed opening's height is a *consequence*, and a
designer who fixes the height first lands between the families, which is what builder-Gothic looks
like.

`strength: **documented**`, alone among this package's four packs, and the distinction is worth
keeping: Rickman, Pugin, Downing and Davis wrote this system down without reducing it to a
parametric table. Moorish and adobe were never written down at all. None is `canonical`.

Two things it found:

- **The light zone is a remainder, not a dimension.** A pointed opening is set out head-first —
  span, strike ratio, mouldings — and the vertical light is what is left. 17.108 parts, an untidy
  number the pack refuses to round, held by its own invariant so the next editor finds out
  immediately that it is not theirs to choose.
- **The egress conflict blames the wrong member if you take the obvious answer.** The first draft
  of this pack said the pointed head fails IRC R310. It does not: run the arithmetic on the pack's
  own default and a 36 in equilateral head narrows to 20 in clear at 22½ in above the springing, so
  the top 8½ in of the rise is lost — and the surviving rectangle still measures **about 10 sq ft**
  against a 5.7 requirement. **The mullion is what is fatal.** Two lights in a 36 in span leave
  ~13 in clear each against a 20 in minimum, and no amount of height recovers a rectangle that is
  too narrow. The threshold where the arch alone does bite is a span of about **24 in**. The
  overstated version was caught by computing it rather than by rereading it, and the test now
  recomputes both figures rather than asserting the sentence.

The pack also states what it cannot carry: the **four-centred Tudor arch** is struck from four
centres with two radii, so a single strike ratio cannot express it — which is why `tudor` and
`tudor-revival` are absent from `applies_to` despite being the obvious neighbours, and it is a real
missing pack rather than a boundary of convenience.

### `proportions/systems/opening-craftsman.json` — a datum instead of a proportion

WP-4.1 asks for "a Craftsman opening system **and** a Prairie trim family", confirmed by PB-4,
which recorded the whole cluster as bound with no opening pack available. This is the opening half;
the trim family stays on the list, because whether Prairie's banded oak and art glass is a distinct
family or a dialect of Stickley's wants its own pack rather than a paragraph in this one.

**The measured gap was larger than the list said** — seven nodes with no opening-role pack, not
five. This binds five.

**The pack's central assertion is that there is no proportion.** Every other opening pack in the
library gives an opening a ratio, a strike, a module of its own. This one sets **one horizontal
line** at 6 ft 8 in and every window, door, transom and garage opening on the elevation dies into
it, so an opening's height is not a proportion — it is the datum minus that opening's sill. The
consequence a brief will fight: a taller window means a *lower sill* and never a higher head, which
is exactly what these houses do. `styles/craftsman.json` says why the system can be written this
way at all — "the rules are all absolute lengths, which is why the plan-book trade could transmit
it without transmitting any theory."

The module is **the framing bay**, and two nodes name the same 24 inches from opposite ends:
`craftsman` from the structure ("the exposed rafters declare the framing bay at 16 or 24 inches on
centre") and `prairie-school` from the opening ("the standard casement width of roughly 2 ft, from
which window bands are built in multiples"). They coincide because the mullion lands on a stud,
which is why a Prairie band of five casements is 10 ft and not 9 ft 7.

Three things it found:

- **The porch and the wall come to one plate line.** Both assemblies work out at 4.25 modules —
  8 ft 6 in — which is the structural fact behind the visual one: the porch roof and the house roof
  are one structure at one level and the eave crosses both without a step. A porch beam below the
  wall plate gives a stepped eave, which is a Queen Anne move and reads as one.
- **A disagreement recorded rather than resolved.** `styles/craftsman.json` calls the porch beam
  the *low* datum and the heads the *high* one; a 7 ft clear porch cannot have its beam at 6 ft 8.
  In surviving bungalows the two lines are within a few inches either way and often coincide. The
  invariant therefore asserts only what both accounts agree on — that there are two lines and they
  are close — and declines to say which is on top, because resolving it would mean overruling a
  style record on no evidence.
- **The horizontality is in the grouping, not in the window.** A single unit is 2:1 *tall*; three
  side by side under one head and one sill make the band. Designers who absorb the horizontal
  impression and go looking for a wide window produce a squat 1950s opening and lose the vertical
  counter-rhythm that made the band read as a band.

**Two refusals, both findings rather than omissions.** `mission-revival` shares this cluster's
interior trim and nothing about its openings, which are arched and already reach `moorish-arch`.
`arts-and-crafts-british` looks like the obvious fit and is not: its own governing logic says "no
applied system… there is no repeating bay and no vertical alignment requirement", which is a direct
denial of this pack's central assertion. Binding it to close a count would have meant asserting an
alignment rule against a node's explicit denial of one. What it wants is a **leaded-casement-and-
mullion system**, which is a new candidate item — and one that would also serve the parts of
`english-gothic` and `tudor` that `opening-pointed` deliberately left alone.

### `proportions/systems/trim-prairie.json` — the other half, and a wrong binding corrected

PB-4's line item was two things. `opening-craftsman` was the first; this is the second, and it
closes the item.

**The corpus had written this gap down too — the third time in this package.**
`prairie-school`'s own `trim-craftsman` binding note says that pack "does NOT describe Wright's own
architect-designed interiors, whose bespoke geometric oak trim and art-glass-derived ornament are a
real gap in this pack set: no pack here owns a first-principles, non-catalog Prairie interior
system, **and none should be invented for one**." The last clause is a caution against invention and
it is right. This pack answers it by not inventing: every section is measured off surviving and
restored fabric and checked against the Wasmuth plates.

**The two trim families share a module on purpose, and that is the finding.** Both come out of the
same American mill in the same decade and both are built from the same dressed 1×4 at the same
quarter-inch part, so the packs can be diffed member for member. What differs is entirely what the
board *does*:

| | `trim-craftsman` | `trim-prairie` |
|---|---|---|
| the 1×4 is | a **casing leg**, framing an opening | a **band**, crossing a surface |
| the line is made by | a head casing that **overhangs** | a board **held back** between two proud strips |
| at an opening | the head is one size up the stock series | there is no head — the band runs over and keeps going |
| section widths | 22 and 29 quarter-inches — **exactly** the dressed stock series | 24 — **neither** 1×6 nor 1×8, because it was milled to order |
| authority | `documented` — the mills published the sections | `reconstructed` — Wright published no trim schedule |

That last row is the cleanest statement in this library of what separates **a bought tradition from
a drawn one**, and both packs' invariants assert their own half so the pair can be read side by side.

Two more inversions the pack records: the "wainscot" goes to **6 ft 8**, not waist height, because
the whole field below the lintel band is one surface — a kit reading 36 in would put a line across a
Prairie room at exactly the height the design most wants empty. And the chair rail is **not a chair
rail**: it is the sill band continued across the wall where there is no window, running behind the
bookcase and out through the door head into the next room.

**A code figure chosen over a historical one, deliberately.** The compression zone's historical band
is 6 ft 10 to 7 ft 4; IRC R305.1 requires 7 ft in habitable rooms and hallways alike. Encoding the
historical mean as the default would put a non-compliant number in front of every user, so the
default is **7 ft 0 in** — the lowest compliant height — and the note says why. What must be
preserved is the *ratio*, which lives in `opening-craftsman`, because compression is a relation and
not a dimension.

**The old binding is kept, not struck.** `trim-craftsman` stays bound (optional) and `prairie-school`
stays in its `applies_to`, because the same note identifies something real that it *does* describe:
the plan-book "Prairie box" foursquare, built and trimmed by the same regional lumberyards that
supplied the bungalow next door. Same shape as `greek-doric` beside `benjamin-doric` — one pack for
what the architects drew, one for what the trade built, and where they disagree the disagreement is
the finding.

**Its leverage is the lowest in the package and the report says so.** It binds **one** node and moves
the role-coverage count by **zero**, because `prairie-school` already had an interior-role binding —
the wrong one. It was built because a wrong binding is worse than a missing one, which is the same
argument that justified `greek-doric`, and not because it improves a number. `ranch-style`, which
descends from `prairie-school` at weight 0.35 with `inherits_kit: true`, is deliberately **not**
bound: its own record says its trim is "the same trim" as its Minimal Traditional parent at 0.7, and
draws the distinction in its own words — "Prairie has a centre; the ranch has an extent".

### `proportions/modules/dutch-gambrel.json` — two devices, and a datum nobody stated

WP-4.1's item is "a Dutch gambrel roof geometry system (break point, slope ratio, eave kick)",
confirmed by PB-1a and PB-6c. This is unusual among the packs in this package in one respect: **the
corpus's own style records supply almost every number**, and for this type they are better authority
than anything I could add. The slope bands, the break, the plate heights, the eave projections and
the sweep radii are all quoted from `dutch-colonial-american`, `new-jersey-dutch-gambrel`,
`hudson-valley-dutch` and `dutch-colonial-revival`.

**It carries two devices, not one, because the records show they are independent.**
`hudson-valley-dutch` has a sprung eave — 18–24 in projection on a 5–9 ft sweep radius — over a
*straight* 12:12-to-17:12 gable and no gambrel at all; its own `distinguished_from` entry says so.
Plenty of New England gambrels have the break with no sweep. Calling the pack "the Dutch roof" would
have hidden that, so it names both, every rule says which device it belongs to, and
`hudson-valley-dutch` is bound **for the eave rules only**, with its note saying to leave the
section alone.

**The finding worth carrying forward is the break point's datum.** Three records give the break and
**none of them says from where**:

| record | what it says |
|---|---|
| `dutch-colonial-american` | "break at 55–70% of the half-span" |
| `new-jersey-dutch-gambrel` | "break at 55–70% of the half-span" |
| `dutch-colonial-revival` | "break point at 55–65 percent of the total roof height above the eave" |

Those are two different measurements of one joint. Read naively as *from the eave*, the first is
wrong by nearly a factor of two — it produces a roof whose upper slope is a quarter of what it
should be and whose ridge is half again too high. Reconciled against the slope bands the same three
records give, the colonial figure is consistent **only** as a fraction measured *from the ridge*
(0.55–0.70 from the ridge = 0.30–0.45 from the eave), and the revival's height fraction comes out at
0.34 horizontally on those slopes. Both then agree. The pack states **one canonical datum** —
horizontal, from the outside face of the wall — and writes out the conversion to both of the
corpus's forms. **The style records are not edited:** they quote their sources correctly, the
ambiguity is theirs to keep, and the pack's job is to be the one place it gets resolved.

The test does not assert that reconciliation from the pack's prose — it recomputes it, and fails if
the encoded defaults cannot satisfy the colonial band, the revival band and both slope bands at
once.

Three smaller things:

- **`height_modules` is the roof's own proportion.** Because the module is the half-span, the
  section's height in modules *is* roof-height-over-half-span (0.9375), so nothing else has to be
  stated to know how tall the roof is. On a Dutch house that ratio is very near one, which is why
  `dutch-colonial-american` says "the roof is most of what you see".
- **The colonial has no shed dormer, and the count says zero** — the same move `greek-doric` makes
  with ornament, on the authority of `dutch-colonial-american`'s own sentence that the full-width
  shed dormer is "a combination that almost never occurs in the colonial original". The three rules
  that *do* dimension the revival's dormer each begin "REVIVAL RULE", so the two regimes can never
  be taken for one another.
- **A named dimension rather than a new slot.** A gambrel has two pitches and the ontology has one
  `roof_pitch`; the upper slope is carried as `dimension: "upper_ratio"`, following the precedent
  `moorish-arch` set with `return`. A consumer reading only `ratio` gets the lower slope, which is
  the right default — it is the one that shows.

Two nodes are bound **optional** and narrowly: `new-england-georgian`, where the record lists gambrel
as one of three roof options and the eave rules must *not* apply (it has a boxed modillion cornice, and
a sprung eave would be a Dutch import onto an English house), and `shingle-style`, which takes the
gambrel by publication and then breaks it — its roofs bend and merge, so the two clean slopes are a
starting geometry rather than a rule. The H-bent frame bay is left to `timber-bay`, which stays
primary on both colonial nodes; two packs asserting one number is how a corpus starts disagreeing
with itself.

The **Low Countries gable grammar** — stepped, bell, neck, and the Cape Dutch holbol curve — is *not*
reduced by this pack and the notes say so: a gable profile is an elevation outline and a gambrel is a
roof section, and nothing here helps with a holbol curve or a bell gable's shoulders.

### One checker defect, found by authoring against it

`check_orders.py`'s `SafeEval` has always addressed a list of dicts by its members' `id`, so an
order pack can write `assemblies.impost.members.impost_block.height_parts`. `check_modules.py`'s
`Ref` did not, so **the same invariant expression was legal in an order pack and a `NameError` in a
module pack.** Two checkers over one schema field disagreeing about the expression language does
not produce an error message — it produces an author who writes the weaker of two true statements,
and the weaker one is the one that does not name the member it is about. `Ref` now resolves lists
by `id` like `SafeEval`, and `tests/test_wp46_packs.py` pins it.

## What is NOT done, with the measurement

Twenty-eight or so items of WP-4.1's list remain. The ones with the leverage measured above and
still missing: a **cast-iron system** (3 nodes), a **four-centred Tudor arch system** (new, raised by `opening-pointed`'s own boundary), a **leaded-casement-and-mullion
system** (new, raised by `opening-craftsman`'s refusal of `arts-and-crafts-british`, and it would
also serve what `opening-pointed` left alone in `english-gothic` and `tudor`), and a
**medieval/pre-Palladian English facade system** (new only in that two existing list items turn out
to be one pack). One more added by this tranche: **Prairie rectilinear art glass**, a set-out with rules about
asymmetry, colour and the placement of the few coloured pieces that `trim-prairie` has no figures
for and declined to invent. **60 nodes still have no opening-role pack**, down from 68, and **67 no
facade-role pack**, unchanged — because the facade halves of both two-part items were measured and
found already served.

Struck off by the second tranche: the **adobe/rammed-earth module** (5 nodes on the list, and it
reached 9), the **opening half** of the Gothic Revival item (5 nodes, 3 of them previously with no
opening-role pack at all), and **both halves** of the Craftsman item — the opening system for 5 of the 7 nodes that had no
opening-role pack (the other 2 refused for stated reasons), and the Prairie trim family, which
binds one node and corrects a wrong binding rather than filling an empty role. Struck off by the
third: the **Dutch gambrel roof module**, which the list scoped at 3 nodes and which reached 6.

Two of the named seven were **not** attempted for a stated reason rather than left silent: the
muqarnas geometry and the tile/plaster/timber stratification that belong with the Moorish system
are absent from `moorish-arch` because the unit-cell proportions vary by regional school and there
is no figure here worth defending. A plausible number would have been worse than none.

## Verification

First tranche: `python3 build/check_all.py` — 22 checks, 461 tests. 38 packs resolve with 0
problems; `check_orders.py` 0 errors; `check_pack_bindings.py --strict` green at **131 of 132 nodes
bound**, up from 129. `tests/test_wp46_packs.py` was new (15 tests).

Second and third tranches: 22 checks green again. **43 packs**, 0 errors from `check_orders.py`,
`check_modules.py --eval` and `check_systems.py` alike; bindings still 131 of 132 (the five new
packs bind 26 nodes but every one of them was already bound, so the count does not move and should
not be read as no progress — the movement is in ROLE coverage, 68 → 60 nodes with no opening-role
pack, plus one wrong interior binding corrected and a roof system that six nodes previously had
nothing for, neither of which moves any count).
`tests/test_wp46_packs.py` is now **96 tests**, and the suite as a whole 559. The pinned pack count in
`tests/test_proportion_engine.py` is now read off the library instead of hard-coded — a test that
has to be edited every time a pack lands teaches the next author to edit tests rather than read
them.
