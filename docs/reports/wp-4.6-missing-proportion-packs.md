# WP-4.6 — the missing proportion packs

*Started 24 Aug 2026, continued 25 Aug. **Partially delivered: fifteen packs of a list of
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

### `proportions/modules/balcony-gallery.json` — the measurement said cast iron is not the system

WP-4.1 asks for "a cast-iron/ironwork system", named in the plan of action, with PB-6a additionally
flagging wrought iron for the Spanish and Mediterranean revivals. **The measurement disagreed with
the item's name.** Ranked by how much their own records talk about ironwork, the corpus puts
`monterey-revival` (31 mentions), `monterey-colonial` (25) and `regency` (24) at the top — and **the
Monterey balcony is wood.** What those three share with the Creole galerie and the Italianate porch
is not a material: it is a horizontal deck applied to a wall, carried one of three ways, with a rail.
So the pack is named for the deck and iron is one of the materials it is made in.

**The central claim is that depth follows carrying strategy**, which is why the pack has three depth
rules rather than one:

| carried by | depth | who says so |
|---|---|---|
| rods or brackets, nothing beneath | **30–48 in** | `creole-cottage-vernacular`'s abat-vent and `regency`'s cast-iron balconette — the same band, stated independently, neither record aware of the other |
| the floor joists, cantilevered | **5–8 ft** | `monterey-colonial` 5–7 ft, `monterey-revival` 6–8 ft |
| posts to grade | **6–14 ft** | `french-colonial-american` 8–12 ft (14 on the raised house), `creole-cottage-vernacular` 6–10 ft |

The bands barely overlap and the bracket regime does not reach the cantilever one at all. A designer
who wants an eight-foot Monterey balcony has to add posts and has thereby changed the style — which
both Monterey records say, one by insisting on "no posts, no brackets to the ground" and the other by
recording that the revival added them.

**A stylistic proportion that turns out to be a structural rule.** `monterey-colonial` gives the
balcony as "roughly one-fifth to one-quarter of the building depth". The joists run the depth of the
house and project past the wall, so the balcony's backspan *is* the building — and past about a third
of a backspan, a cantilever is an uplift problem at the far support. The corpus's own ratio is that
limit, found by feel and written down as a proportion. The pack states it as a ratio rule with the
structural ceiling as the band's top.

Two more findings: the **galerie roof break** is a position rule of the same class as
`dutch-gambrel`'s — "main roof 40–50 degrees; galerie slope 20–30 degrees; **break at the outer wall
plane**", so the gallery reads as a separate plane pinned to the building. And the **floor-length
window** is stated independently by Regency (a sash to the floor, to walk out onto the iron) and by
French Colonial (full-height casement pairs onto the galerie) — it is what the balcony is *for*, and
a balcony served by a 30 in sill is a thing to look at from the street.

**The guard conflict has two halves needing different answers.** IRC R312 wants 36 in and no 4 in
opening; the historical rail is 30–34 in (Monterey) or 900–1050 mm (Regency, straddling the line).
The square-picket railings already pass the sphere rule at a 4 in pitch — but a cast anthemion, lyre
or trellis panel does not, almost anywhere in its pattern. The pack refuses to redesign the pattern
to pass and says to back it with a secondary screen instead, because the pattern is the thing being
reproduced.

**Half the item is deliberately left open.** Cast iron as an **ornament vocabulary** — the anthemion,
lyre, heart and trellis patterns `regency` names, the New Orleans foundries' foliate panels, and the
wrought grilles and rejas PB-6a flagged — is a pattern repertoire and not a proportional system, and
this pack has no figures for any of it beyond the panel's overall proportion. It stays on the
candidate list with the other ornament items, on the same principle that kept muqarnas out of
`moorish-arch`.

**Two nodes considered and refused.** `greek-revival-southern-plantation`'s two-tier gallery is a
colonnade with entasis, which `benjamin-doric` already governs and which `italianate-american`'s own
diagnostic explicitly excludes ("never classical columns with entasis"). `swiss-chalet`'s Lauben
balcony is a real gallery and a genuinely different system, already its own item on WP-4.1's list.

### `proportions/modules/stone-course.json` — the largest item left, measured

With all six of the plan's named candidates built, the remaining list was measured rather than
worked in order. **Stone coursing was the largest item by a wide margin:**

| candidate item | nodes describing it | of which thinly bound (≤3 packs) |
|---|---|---|
| **stone coursing** | **60** | **34** |
| half-timber infill panel | 31 | 23 |
| gable geometry (crow-step, bell, holbol) | 12 | 10 |
| mansard/dormer module | 17 | 4 |
| turned Queen Anne millwork | 15 | 5 |
| sawn Victorian bracket | 13 | 3 |

**The pack's first observation is about itself: it cannot have `brick-course`'s module.** A brick
wall has a gauge rod and every course in it is the same height. A rubble wall has no gauge at all,
because the stone arrives as the quarry bed gives it. So the module is not a course of the wall but
a course of the **dressing** — the quoin, jamb, lintel, mullion, kneeler and coping, the only stone
in the building with a dimension before it is laid. The pack therefore proportions the dressings and
treats the field as what is left over, which is also how these buildings were priced and built.

**The central rule is stated twice in the corpus, independently, in nearly the same words.**
`cotswold-vernacular`: "dressed ashlar **reserved** for mullions, jambs, lintels, quoins, kneelers
and copings." `norman-romanesque-english`: "coursed rubble field walling with ashlar **reserved** for
quoins, jambs, voussoirs, string courses and shafts." Four centuries and two building types apart,
same word, neither aware of the other. Rubble cannot make a corner, an edge or an opening — so every
corner, edge and opening is dressed stone, and the composition *is* the contrast between the two.

**The reveal is not the wall, which is the opposite of `adobe-module`** — and the two packs then give
opposite energy advice, each explaining why. In adobe the reveal *is* the wall thickness (both stated
with the same expression), so internal lining destroys the building's central diagnostic. Here the
jamb is dressed and rebated, so the reveal is about two-thirds of the wall, an internal lining can be
brought up to the jamb and the external shadow survives intact. Two mass-wall packs disagreeing
without explaining themselves would be worse than one pack; both conflicts name the other.

Other findings: **the opening is capped by what a lintel will span** —
`french-provincial-farmhouse`'s own "sized by the lintel or relieving arch available" — which is why
these elevations have few small openings with wide piers and reach for a mullion rather than a wider
head; an invariant ties the lintel's depth to that span so widening the opening visibly costs
something. And **lime, not cement**, stated in capitals inside a blocking conflict rather than in a
note, because a cement mortar is stronger and less permeable than the stone, so water leaves through
the stone's face and the face spalls — and it is still routinely specified.

**Twelve nodes bound, not thirty-four, and the criterion is stated.** The test is whether the stone
wall *governs* or merely *occurs*. The Iberian and Mexican nodes go to `adobe-module`, which already
holds their mass-wall behaviour with the right module; `greek-classical` and `mid-atlantic-georgian`
stay with their orders, because an ashlar Georgian front is proportioned by the order and the stone
is a material choice below it; `jacobean`, `tudor` and `english-medieval-timber-frame` wait for the
half-timber panel module, because their walls are frames with infill and the stone is a plinth.
Binding all thirty-four would have raised a number and told the corpus something false about eleven
of them.

Three systems declined **with their figures quoted in the notes**, so the next author finds them
rather than rediscovering them: the moulded sections (ovolo and cavetto mullions, the Norman chevron
"cut into the stone's arris rather than applied to its face"); the Scottish crow-step at 300–450 mm
tread and the bartizan at 1.2–2.0 m; and `tuscan-vernacular`'s loggia arcade at "pier width 0.4–0.6
of the clear opening", which is a third missing item.

### `proportions/systems/facade-arcade.json` — a pack the list never named, asked for three times

**WP-4.1's candidate list does not contain this item.** Three packs in this work package asked for
it anyway: `adobe-module`'s binding notes on `spanish-colonial-american` and
`california-mission-colonial` both say "a portal/arcade system is still missing and is still in
WP-4.1's candidate list" — which was *wrong*, it was never on it — and `stone-course` quoted
`tuscan-vernacular`'s loggia ratio in its notes purely so the figure would not be lost. A gap that
three separate pieces of work reach for and the list does not name is a fact about the list.
Measured, it was the largest remaining item: **33 nodes, 24 thinly bound.**

**It is the only pack in this package claiming `confidence: high`, and the reason is agreement
rather than sources.** Nine unrelated records give the pier as one third to one half of the clear
span — Italian Renaissance and its American revival, the Italian villa vernacular, the Tuscan
farmhouse, the Mediterranean Revival, Mission Revival, the Californian mission, Norman Romanesque
and the Mexican patio. Five countries, six centuries, no route by which any could have got it from
the others. Three more give the springing at two-thirds of the opening's height; **four say the
arcade *is* the circulation** ("rooms entered from it, not from corridors"). When the corpus agrees
with itself that strongly the pack is reporting rather than reconstructing.

**The arch's shape is deliberately not in the pack, and that is what makes it composable.** Bay,
pier, springing and rhythm are identical whether the arch above is semicircular, equilateral,
four-centred or horseshoe — so the rise rule says to take its figure from whichever arch pack the
node binds. Three nodes bind this pack *and* `moorish-arch`.

It also **moved the facade-role count for the first time in the package: 67 → 61.** Six earlier
packs closed opening, interior and threshold gaps and left the facade role untouched.

### Two defects this pack's own tests found, both mine

**A silent slot-address collision.** `facade-arcade` and `moorish-arch` were both writing to
`porch_support`/`height` — but one meant the impost *block's* height (about 6 in) and the other the
springing *line* above the floor (84 in), and three nodes bind both packs. Two packs putting
**different quantities into one address** is not a conflict, it is a corruption: whichever resolves
last wins and nothing reports it. Precedence cannot help, because precedence decides which of two
accounts of the *same* quantity to believe. The arcade's rule was renamed to a `springing` dimension,
and a test now asserts the two packs share exactly one address — `arch`/`height`, where they really
do mean the same thing and precedence is the right answer.

**Precedence contradicting role, sixteen times.** A test on the new bindings found `facade-arcade`
sitting at precedence 0 ahead of a `primary` pack. Investigating found sixteen such inversions
across fourteen nodes — **twelve of them introduced by this work package**, because every new
binding was inserted at the first unused precedence and 0 is nearly always free. Nothing caught it:
`check_pack_bindings.py` checked `precedence` for being a total order and never for agreeing with
`role`, so the two fields could say opposite things and the build stayed green.

Fixed in the data, and the checker now errors on it. But **only on the narrow rule**, because that
is the only one the corpus holds to. Measured across all 132 buildable nodes: `secondary` sits ahead
of `facade`, `opening`, `interior`, `room` or `massing` in **253 places across 59 nodes** — which is
not a bug but the corpus's own convention, order packs first and role packs after. And `optional`
sits ahead of a role pack in **40 places across 23 nodes**, untidy and mostly older than this
package. Both are warned about once per node rather than enforced; churning 59 nodes to satisfy a
tidier rule nobody had agreed to would have been the wrong trade.

### `proportions/modules/timber-panel.json` — and what the list's phrase "distinct from" was hiding

WP-4.1 asks for "a half-timber infill/nogging panel module, **distinct from `timber-bay`'s** larger
structural framing bay". That qualifier did more work than it looks. Setting out to write the pack,
**six of sixteen planned rules were already `timber-bay`'s** — the structural bay, the storey height,
the range depth, the storey diminution, the roof pitch and the frame reveal — and that pack is
already bound to seven of the fifteen nodes this one binds. So this pack restates none of them and
holds only what *fills* the frame: the panel, the studding, the timber's own section and projection,
the jetty, the plinth and the infill material. A test asserts the two share no slot address.

**Its central rule is regional rather than universal, which is unusual here and is why no source
states it.** The panel's height-over-width runs 1:1 in a German or Alpine *Gefach*, about 1:1.2 in
the English south-east, and 1:3 to 1:4 in East Anglian and Norman close studding —
`english-medieval-timber-frame` holds two of those in a single sentence. There is no correct value,
only a correct value for a place, and a building with the wrong one is competently detailed and from
nowhere. The reason is economic: close studding uses roughly twice the oak, so it is a display of
timber wealth and clusters in the rich, wood-poor east.

Three more findings:

- **One record measures three walls in one sentence** — `english-cottage-vernacular`'s "450–600 mm
  in cob, 350–500 mm in rubble, **150 mm in a daub-panelled frame**". The framed wall is a quarter
  the thickness. No reveal, no thermal mass, and a wall that can be pierced anywhere between two
  studs without touching structure — which is why framed buildings have more and larger openings
  than their masonry contemporaries and were so readily altered.
- **Two records disagree about the jetty and the band holds both.**
  `english-medieval-timber-frame` puts it at about four-thirds of the joist depth, "**never** the
  exaggerated overhang of revival work"; `tudor-revival` caps it at one, "**never** more than the
  depth of a plausible joist". Both warn against the same thing from opposite directions, and the
  revival's is stricter because a revival jetty usually carries no joist at all.
- **Two refusals the records make themselves.** `jacobethan-revival` is "masonry… with **no**
  half-timbering" and `cotswold-cottage-revival` is stone or stucco "**without** applied
  half-timbering". Both are found by a regex sweep for half-timbering and both are explicit
  negatives — a good reminder that a node mentioning a thing is not a node having it.

And one thing the pack states that its own tradition finds uncomfortable: **the exposed black-and-
white frame is substantially a Victorian taste.** Four records here describe the frame being
*covered* — tile-hung, weatherboarded, stuccoed, limewashed — and the climate conflict says plainly
that covering it is what the buildings did rather than a modern compromise.

**It raised OQ 47.** The ontology has no slot for an exposed structural member on a wall face, so the
stud spacing, the timber's face width, its projection and the brace are all routed through
`corner_board` — a board at a corner — and all four read wrong. Same class as OQ 46, and not only a
half-timbering problem: Stick Style's applied bands, the chalet's purlin ends, `opening-craftsman`'s
rafter tail and Tudor Revival's applied timber are the same member. Four packs in this package have
now routed it through a slot written for something else. The proposal is an `expressed_frame` slot
whose most useful field would be *structural / structural-and-expressed / applied* — the distinction
`stick-style` and `tudor-revival` both turn on, and which no slot records, so the corpus cannot
presently tell a frame from a picture of one.

### `proportions/systems/opening-mullioned.json` — two list items that turned out to be one window

WP-4.1 lists the **four-centred Tudor arch** and a **leaded-casement-and-mullion system** separately,
and **both were raised again from inside this work package**: `opening-pointed` records the
four-centred arch as "a real missing pack rather than a boundary of convenience" and names it as why
`tudor` and `tudor-revival` are absent from its own `applies_to`; `opening-craftsman` refuses
`arts-and-crafts-british` because that node's own logic ("no applied system… no vertical alignment
requirement") denies the head-datum rule outright, and says what it wants instead — almost exactly
this pack, including that it "would also serve the parts of `english-gothic` and `tudor` that
`opening-pointed` deliberately left alone."

They are one system. A Tudor window *is* a four-centred head over a mullioned band of leaded lights,
and separating the head from what hangs under it would have produced two packs neither of which
described a window. The union was also the largest remaining item: **15 thinly-bound nodes** against
10 for gable geometry.

**The central rule is that the window is counted, not measured.** `tudor` states it in five words —
"window width is a whole number of lights" — and it is a different *kind* of statement from anything
in the classical opening systems, which give an opening a proportion. This one gives it a **count**:
you do not widen the window, you add a light, so widths go 41, 64, 87, 110 in and there is nothing
at 75. Eight records converge on the light itself at 400–550 mm, and the module is their middle.

**Three cross-pack echoes, each worth more than the rule it sits in:**

- **The tall unit in a wide band.** The single light is 2.4:1 *tall*; the window overall is 2:1 to
  5:1 *wide*. That is the same inversion `opening-craftsman` found in the Craftsman band four
  centuries later — two unrelated traditions building a horizontal band out of vertical units, both
  got wrong the same way by designers who absorb the band and draw a squat unit.
- **Both traditional opening packs fail IRC R310 on the mullion, not the head.** `opening-pointed`
  found that a pointed head passes comfortably and the mullion is fatal; the same arithmetic holds
  here. Two independent systems four centuries apart failing a modern code on the member *between*
  the lights rather than the shape *above* them is a fact about the code as much as about the windows.
- **The glazing ratio is a history, not a range.** Elizabethan 45–60% "and higher at Hardwick";
  Jacobean explicitly "reduced from Elizabethan extremes" to 30–45%; the revival back at 35–55%
  because glass was cheap by 1910. A designer should pick a decade rather than a number — and should
  know that at the top of the band the mullions have become the structure, which is why Hardwick was
  a stunt.

The four-centred head is also **outside what `opening-pointed` can express**, and measurably so: that
pack's flattest arch, the drop arch, still rises 0.707 of its span, and a four-centred head rises a
quarter to a third. A test asserts the two bands do not overlap.

Coverage moved twice: **opening-role 60 → 50**, and nodes carrying two packs or fewer **36 → 14**
across the four packs since the counts guard landed.

### `proportions/systems/facade-gable.json` — a class the library had none of

WP-4.1 records this gap in the strongest terms it uses anywhere: "no gable geometry system of any
kind currently exists in the library." Two packs in this work package added to it independently —
`dutch-gambrel` says plainly it does *not* reduce the item ("a gable profile is an elevation outline
and a gambrel is a roof section"), and `stone-course` quoted the Scottish crow-step figures into its
own notes purely so they would not be lost.

**It is one pack rather than the two the list asks for, because the useful distinction runs across
the list's division rather than along it.** A gable is one of three different objects, and the corpus
distinguishes them in four records none of which is talking about the others:

| | who says it |
|---|---|
| the **end of a roof** | `flemish-vernacular`: crow-steps sit on "a gable that is genuinely the end of a roof rather than a screen in front of one" |
| a **parapet** carried past it | `jacobethan-revival`: "the wall carries up past the roof plane and is capped with coping stones. Tudor Revival gables end at the rake with a barge" |
| a **screen** standing free of it | `cape-dutch`: a gable "standing free above the eave line of a thatched roof", on the *long* elevation where there is no roof end at all |

Deciding which is being drawn is prior to any dimension in the pack, and the module note says so
before it says anything else. Two more findings: the crow-step is **square in Flanders and broader
than high in Scotland** (1:1 against 1.5:1, two records, neither aware of the other), and the same
gable *count* carries **opposite instructions** — Jacobean ranges them symmetrically, while
`rural-gothic-villa` says equal widths are "a failure" and indicate "a builder's composition".

**A third self-refusal.** `arts-and-crafts-british`: "no classical order, no pointed arch, **no shaped
gable**, no period quotation of any kind: the absence of quotation is itself the tell." After
`jacobethan-revival` and `cotswold-cottage-revival` refused half-timbering in their own words, this is
the third node in the package to refuse a pack itself — and the reason a regex sweep is a starting
point and not an answer.

### The address collision, measured properly — and why no checker shipped

`facade-arcade` found one instance of two packs writing different quantities to one
`(slot, dimension)` address. This pack's tests found four more, so the whole corpus was measured:
**1,922 collision instances, 75 distinct addresses, 622 distinct pack-pairs.**

**The measurement was misleading and reading it changed the question.** The largest entries are packs
colliding with *themselves* — `room-harmonic` writes `room_adjacency_overrides`/`width` **ten times**
and `ceiling_height_rule`/`height` seven times; `storey-graduation` writes `height_proportion`/`ratio`
four times. Those are not defects. They are a **menu** at one address, deliberate and labelled as
such in their own notes: "SHAPE 1 OF 7 — THE ROUND ROOM", "METHOD 1 OF 3 — THE ARITHMETIC MEAN". **A
naive uniqueness check would have flagged 1,710 correct rules.**

So there are three cases and only one is wrong: several rules at one address *within* a pack is a
menu; two packs meaning the *same* quantity is what precedence exists for; two packs meaning
*different* quantities is the corruption. Four of the third kind were found and fixed here —
`porch_support`/`height` meaning both an impost block and a springing line, and
`gable_treatment`/`height` meaning a finial, a parapet and a gable-end silhouette in three packs.

**No checker shipped, and that is the finding.** Distinguishing the cases needs semantics a checker
does not have, and shipping one that cries wolf over 1,710 correct rules would be worse than none.
Raised as **OQ 48** with both concrete proposals: a `quantity` field so the real address is
`(slot, dimension, quantity)`, or accept named dimensions as the convention this package fell into
and require any shared address to be declared. Coverage moved: **facade-role 61 → 58.**

### `proportions/systems/trim-sawn.json` — four list items, one machine

WP-4.1 separately asks for **sawn Gothic ornament**, **sawn-bracket Victorian trim**, **turned
Queen Anne millwork** and **Alpine bracket/carved-timber**. The first three are one family, and the
thing that unifies them is not a period or a country but **two machines** — the scroll saw and the
lathe, steam-powered from the 1840s, which put carved ornament into pine at a fraction of hand
carving. A bargeboard of 1845, a bracket of 1870 and a spindle frieze of 1890 were stocked in the
same catalogue and cut on the same bench. Measured, it was the largest remaining item: **27 nodes,
16 thinly bound.**

**Which members a building has *is* its style, and the corpus says so as a decision procedure:**
`gothic-revival-american` — "bargeboard on the rake with no bracket under the eave: Gothic Revival.
Brackets under a wide eave with no bargeboard: Italianate." That is why the pack's central rule is a
**count of members** rather than a dimension of any of them.

**The fourth item is deliberately not merged.** `swiss-chalet` is bound for its *sawn* balustrades
and bargeboards only; its "carved and inscribed facade band" stays on the list, because carving is a
hand craft with a gouge and this pack is about machines.

**Three records refuse the pack in their own words** — and one gives a decision procedure for the
refusal. `stick-style`: "if the applied woodwork curves, turns, or scrolls, the building has moved
to Queen Anne or Eastlake." `queen-anne-free-classic` is defined by the "absence of turned
spindlework"; `queen-anne-patterned-masonry` by "there is no porch spindlework". Two Queen Anne
subtypes refusing the ornament their own siblings are named for is a sharper distinction than any
dimension could draw.

### The address collision, resolved into a proportion — and a tool instead of a checker

The gable pack's measurement (1,922 instances) had raised an alarm. This pack forced the
adjudication: **all 144 cross-pack pairs involving a WP-4.6 pack were read by hand, and eight were
genuinely two packs meaning different quantities — about five per cent.** The rest is the mechanism
working: two packs both giving a room's ceiling height, a window's proportion or an arch's rise are
alternatives, and precedence is exactly what chooses between them.

The eight include `frieze`/`height` meaning a classical entablature frieze *and* a suspended spindle
valance, and `eave_condition`/`height` meaning an eave's height above ground *and* a verge's overhang
depth — **the latter on ten nodes**, and the one that would most easily have shipped silently.

**A checker was considered and deliberately not built.** Only a human can tell an alternative from a
corruption, because the difference is what the rule *means*, and a build check carrying a 144-entry
allowlist re-adjudicated on every new pack is a great deal of ceremony for a five per cent hit rate.
Instead `build/pack_addresses.py` — an authoring aid that lists the addresses a pack shares with its
neighbours and prints both notes side by side. It was written after this package hand-ran the same
query three times, and it caught six of the eight. `CLAUDE.md` now names it as an authoring step.

### A second checker defect, and a badly misleading diagnostic

Binding `trim-sawn` with role `trim` — a role `check_pack_bindings.py`'s `VALID_ROLES` has always
listed — passed `--strict` and then **failed `validate.py`**, because `schema/style-node.schema.json`'s
own role enum does not contain it. Two validators disagreeing about the legal role set, the same
class as the `check_orders`/`check_modules` expression-language divergence this package found
earlier. The schema is the authority and nothing in the corpus used `trim`, so it comes out of
`VALID_ROLES`; a test now pins the two lists identical.

**The diagnostic was the worse half.** A node that fails schema validation is *dropped* from
`validate.py`'s node set — so every `lineage` and `distinguished_from` reference pointing at it then
reports "target does not exist". Nine nodes with an illegal role produced **47 errors, 38 of which
named entirely innocent nodes**, and not one of which mentioned a role. The first thing I did was
check whether style files had been deleted. The note is now in `check_pack_bindings.py`: if you are
reading a pile of "target does not exist" errors for nodes that plainly exist, look at the top of
the list for a schema error first.

### `proportions/modules/octagon-geometry.json` — and a measurement of mine that was wrong again

WP-4.1 asks for "a polygonal/octagonal plan-geometry module (Octagon House's triangular corner
residues, unaddressed by `room-harmonic`)". A keyword sweep put it at **17 nodes, 11 thinly bound**,
which would have made it the largest remaining item. Reading those seventeen: the octagon *as a
plan* is **one** node, and most of the rest match on an octagonal chimney shaft, an octagonal ceiling
panel or an octagonal window in a list of window shapes. **The fourth time in this work package that
a keyword measurement of mine over-counted its own work list** — after the 24 style-scoped tests that
were 6, the 22 arch bindings that were 8, and the 115 predicted fatals that were 0. A regex proposes
and reading disposes.

Built anyway, and it is two things. **Fowler's octagon** is a whole building: `octagon-house`'s own
record states the entire system in five ratios because the type is *closed-form* — fix the side and
the diameter, area, perimeter, storey, veranda, cupola and roof are all determined. **Jefferson's
octagon** is a *room*, made by cutting a square's corners back by a third of their side, and it
reaches most of the corpus in that form as a canted bay on a building with no octagonal plan at all.

**The finding worth carrying is that Fowler's arithmetic was right and his conclusion was wrong.**
An octagon really does enclose its floor for **nine per cent less wall** than a square — computable
from the geometry, and exactly the argument his 1848 book makes. What he did not count is corners:
eight instead of four, all at 45°, sixteen cornice mitres per storey, a roof with eight hips and no
ridge, and no repeated framing bay anywhere. The labour rises faster than the material falls. That is
why the type is a fad with a date rather than a tradition — and a useful corrective to an assumption
easy to fall into across this whole package, that a traditional form is always the economical answer
to something.

### A third checker defect: a warning path that had never executed

`check_modules.py --eval` warns when a derived rule lands outside its own declared range. That path
read `b['opening_width', 'opening_height']` — a **tuple key**, not a fallback — so it raised
`KeyError` every time it ran. Which means it *never* ran: the branch is only reached when a rule is
out of band, and no module pack had been until this one. So `--eval` has been checking ranges and
been unable to report a violation for as long as it has existed.

It caught a real authoring error the first time it could: `part * 102` with a one-foot part gives
**1,224 inches**, not 102. Three checker defects now in this package, all of the same shape — a
check that looked green because it had never been asked the question it exists to answer.

### One checker defect, found by authoring against it

`check_orders.py`'s `SafeEval` has always addressed a list of dicts by its members' `id`, so an
order pack can write `assemblies.impost.members.impost_block.height_parts`. `check_modules.py`'s
`Ref` did not, so **the same invariant expression was legal in an order pack and a `NameError` in a
module pack.** Two checkers over one schema field disagreeing about the expression language does
not produce an error message — it produces an author who writes the weaker of two true statements,
and the weaker one is the one that does not name the member it is about. `Ref` now resolves lists
by `id` like `SafeEval`, and `tests/test_wp46_packs.py` pins it.

### `proportions/systems/facade-pavilion.json` — three list items that were one system

WP-4.1 asks separately for three things:

- *"a French vertical travée facade system (window-over-window-over-dormer as the structural bay) —
  every current facade/opening pack encodes a horizontal, Anglo/Italian-derived logic; French
  Renaissance Chateau has no fit at all"*;
- *"a mansard/dormer massing module (slope geometry, dormer-to-bay proportion, pavilion projection)
  — Second Empire has no fit among the 5 existing modules"*;
- *"a facade system for Baroque's curved-wall, accelerating bay rhythm"*.

Read together, **the first two are one pack** and the list says so without noticing: the second
item's own parenthesis, "dormer-to-bay proportion", names the first item's unit. A mansard's dormer
is proportioned against the travée; the pavilion is what breaks the travée's repetition. Building
them separately would have produced two packs each needing the other's module, and the second one
would have had to restate the first's arithmetic to be usable.

The module is the **travée**: one vertical bay, centre of window to centre of window, 192 in in 12
parts of 16 in — the middle of the 4.0–6.0 m `styles/french-renaissance-chateau.json` gives for
"travée spacing 4.0 to 6.0 m on centre, uniform along a range".

**The pack's claim is about direction.** `facade-classical` composes in horizontal layers — a base,
a piano nobile, an attic, each with its own storey height and window proportion — and the bays are
what falls between them. This system composes in vertical **strips**, and the strip runs from the
ground storey to the finial of a lucarne that cuts through the cornice on its way up. That is why a
French elevation carries a dormer through its cornice without the dormer reading as an interruption,
and why an English one cannot: there the cornice terminates the wall and here it is one horizontal
in a vertical system.

Two rules are therefore stated **with a single permitted value rather than a band**, which is
unusual in this library and deliberate — `window_grouping_rule`/`alignment` = 1.0 and
`cornice`/`continuity` = 1.0. Neither has a partial version. An elevation whose first-floor windows
sit an inch off its ground-floor ones has not slightly broken the system; it has abandoned it,
because the strip is the only thing holding the composition together. A third,
`dormer`/`count` = exactly 1 per travée, is stated the same way for the same reason, and it is the
corrective for the commonest modern failure: dormers placed by what the attic plan wants rather than
by what the facade requires.

Fourteen derived rules, five conflicts, `confidence: medium`, `strength: documented` — Blondel
taught the travée, the avant-corps and the pavilion as named units in a published curriculum, which
is more than most of what this library reconstructs, but he does not give the arithmetic in the form
a compiler needs, and four corpus records do.

**One distinction the pack insists on, because the corpus does.** An avant-corps projects 1/8 to
1/6 of its own width; an end pavilion projects a quarter to a third of its own width *and rises one
to two metres higher as well*. `styles/french-baroque.json` gives both. A French front commonly has
both, and giving them the same projection flattens the hierarchy the composition depends on — so the
pavilion's extra height is a separate rule (`wing_strategy`/`pavilion_height`) precisely so the two
cannot be conflated. Note also that both projections are measured **against the element itself**,
not against the range: a wide pavilion projects further and stays in proportion. That is the French
way of stating a projection and it is not the classical way.

#### The cross-pack finding: the mansard and the gambrel differ entirely in the break

This pack and `dutch-gambrel` describe the same idea in two countries — a steep lower slope that is
really the wall of the storey inside it, a shallow upper slope whose only job is to close the
section, and a break between them. The difference is **the break, and its datum**.

`dutch-gambrel`'s central finding was that three style records give a gambrel's break three
different ways and **not one of them says from where**, and that pack had to reconcile them into
about a third of the half-span, measured horizontally. Here `styles/french-baroque.json` says
"break point at 0.6 to 0.7 of total roof height" in those words. So a mansard's break is a **height**
fraction, two thirds of the way up, and a gambrel's is a horizontal one about a third of the way
across. That is the whole visible difference between the two roofs — a mansard reads as a storey
wearing a hat, a gambrel reads as a roof — and **the two packs' break rules must never be treated as
interchangeable.** The shallow slope carries the same dimension name, `upper_ratio`, in both packs,
which is what makes them comparable at all.

The bands nearly touch and do not overlap in effect: a gambrel's lower slope is 60–72°, a mansard's
65–75°, which sounds close and is not, because at the top of the mansard band the slope is within
fifteen degrees of vertical and is detailed as a wall with slates on it.

#### The Baroque item, half built and half refused

The third list item is folded in **only partly, and the refusal is stated in the pack**. Reading all
twenty-two Baroque-matching nodes, **not one gives a figure for an undulating or concave elevation**;
the only usable ratios they carry are giant-order figures that `vignola-*` and the overlay packs
already own. So the curved wall is not attempted. What *is* built is the avant-corps and the end
pavilion, which `styles/french-baroque.json` dimensions precisely, and which are the Baroque
facade's other move.

This is the project's own rule — unjudged is not passed, and a plausible number is worse than none —
applied to a whole list item rather than to a parameter. The curve stays on the list, unbuilt, now
with a reason beside it.

#### Two address collisions, both real, both renamed

`build/pack_addresses.py` reported two, and both were genuinely different quantities sharing an
address with a pack that co-binds:

- **`roof_form`/`ratio`** — mine is the mansard's break; `facade-picturesque`'s is *the fraction of
  the elevation's width covered by the dominant roof*. They co-bind on `chateauesque`,
  `french-eclectic` and `french-manoir`. Renamed to **`break_ratio`**.
- **`dormer`/`height`** — mine is the lucarne's height to its finial, the whole masonry structure;
  `storey-graduation`'s is the dormer **window**'s height, following the attic storey. They co-bind
  on `beaux-arts-american`, `beaux-arts-french` and `second-empire`. Renamed to
  **`lucarne_height`** — and both rules are right, because a lucarne has a window in it and that
  window has its own height.

In each case precedence would have resolved the clash silently in favour of whichever pack bound
second, which is not a proportioning decision. Two out of fourteen rules is close to the 5% rate the
tranche measured across all 144 WP-4.6 pairs, and it is why that measurement produced an authoring
aid rather than a build check.

#### Bindings

Eight nodes. It leads the facade role on `french-renaissance-chateau` (which had **no facade pack at
all**, exactly as WP-4.1 said), `chateauesque`, `french-manoir` and `french-eclectic` — displacing
`facade-picturesque` on the last three, which was the wrong instrument: picturesque composition is
about massing irregularity, and this style family's irregularity is disciplined, a uniform travée
broken by pavilions and towers rather than a silhouette assembled freely.

It sits **behind** the existing primary on `second-empire`, `french-baroque`, `beaux-arts-french`
and `beaux-arts-american`, and the reason is worth stating: those elevations really are composed in
classical layers, and what they were missing is not a different wall system but **a storey inside the
roof**, which `facade-classical`'s logic cannot express because that logic terminates the elevation
at the cornice. `second-empire` had `facade-classical` bound as *primary* and nothing in the
facade role at all; it keeps the primary and gains the roof.

**Measured movement: nodes with no facade-role pack 58 → 56** — `french-renaissance-chateau` and
`second-empire`. Nodes with two packs or fewer: unchanged at 12, because all eight of these already
carried three or more. The value here is not coverage arithmetic; it is that the eight most French
nodes in the corpus stop composing their elevations by an Anglo-Italian rule.

### `proportions/modules/jetty-overhang.json` — the fifth gap the corpus wrote down itself

Before anyone went looking, `styles/garrison-colonial.json`'s binding note to `timber-bay` said:

> what this pack does NOT derive is the jetty itself — the 8–20 in cantilever of the second-floor
> girt past the wall below is a real gap in this binding: **no pack in this corpus dimensions a
> framed overhang**, and the 14–20 in framed / 2–6 in hewn figures in this node's own record are not
> recoverable from any of the 36 packs available.

That is the fifth time in this work package that the gap was already written into the corpus by an
author who had no way to fill it (after the four adobe nodes, `prairie-school`'s trim note,
`greek-classical`'s "least-bad available approximation", and `rural-gothic-villa`'s empty opening
role). It is worth saying once more that this keeps happening, because it is the strongest argument
for the practice: a binding note that records what a pack *cannot* do is how a corpus tells the next
author where to work.

#### The module is the joist, not the bay

`timber-bay` genuinely cannot generate a jetty, and the reason is not an oversight — **a jetty is not
a division of a bay.** It is a cantilever, and a cantilever is dimensioned by the member doing the
cantilevering. Every record in the corpus that gives a *rule* rather than a number says so: four of
them state the projection as a multiple of the joist's **depth**, and not one mentions the bay. So
the module is the floor joist, 9 in in 9 parts of 1 in.

#### Four rules of thumb, and they disagree — which is the finding

| record | its rule | multiple |
|---|---|---|
| `garrison-colonial` | "how far a 7–9 in joist can project without a visible sag" | ≈ 2× |
| `garrison-revival` | "one third of the joist depth times its span-to-depth allowance", capping near 18 in | ≈ 2× |
| `english-medieval-timber-frame` | "roughly one third of the floor joist depth times four" | 1.33× |
| `tudor-revival` | "never more than the depth of a plausible joist" | 1.0× |

The pack does not average them. **The three multiples measure three different failures:**

- At **2×** the joist runs the full depth of the house, so the backspan holds the cantilever down
  easily and nothing much lands on the tip. What fails first is the *look* — and the record says so
  in those words, "without a visible sag".
- At **1.33×** the medieval joist is far deeper *and* the jetty carries a whole storey of wall,
  because the upper storey's posts land on the joist ends. What governs is the **load** at the tip,
  not the deflection.
- At **1.0×** the revival jetty carries nothing at all. Its only test is **plausibility** — whether
  the eye believes a joist of that depth could have done it — and the eye is stricter than the
  structure. That is why the revival's ceiling is *lower* than the medieval one, which reads
  backwards until you know why.

`styles/tudor-revival.json`'s own binding note had already noticed the disagreement and left it
standing. The rule is a band of 1.0–2.2 marked `judgment: true`, because what the designer must
decide is which of the three failures is in front of them.

#### The reconciliation settles a second apparent contradiction

**The medieval joist is twice the colonial one.** So the English jetty is *longer* in absolute
inches (350–600 mm against 14–20 in) while being a *smaller* multiple of its joist (1.33× against
2×). Both records are right, about different timber. A compiler handed the multiple and the joist
gets both buildings right; a compiler handed only the inches gets one of them wrong — which is the
argument for dimensioning the pack off the joist, restated as a consequence rather than as a
preference. `tests/test_wp46_packs.py` recomputes the medieval joist depth from the record's own
figures rather than asserting the sentence.

#### Two devices, and one of them is not a cantilever

Same shape as `dutch-gambrel`. The **framed jetty** is a cantilever at 8–24 in with a bressumer, a
soffit and drops that are the cut-off ends of the posts above. The **hewn overhang** is a chamfer at
2–6 in cut out of a single continuous post — no cantilever, no bressumer, and nothing for a drop to
be the bottom of, which is why `styles/garrison-colonial.json` can say that "pendants on a hewn
overhang, or spaced to suit the windows, are decoration without structure." That record also gives
the identification advice that matters and that a checker could never give: *look for the shadow,
then measure.*

Two ceilings and two floors, each stated twice by independent records: 24 in ("never more than 24
in" / "over 24 in. is implausible as joist cantilever") and 6 in against 300 mm — where the two
floors disagree by a factor of two for a reason worth keeping, the revival's being about the
*detail* ceasing to read as a soffit and the medieval one about the *shadow* ceasing to register on
a wall already busy with exposed timber.

#### One rule is the exact inverse of a rule in `facade-pavilion`

Worth reading together, because they are the same slot and the same machinery pointing opposite
ways. There, `window_grouping_rule`/`alignment` = 1.0 says every opening in a travée shares one
vertical axis exactly. Here, `window_grouping_rule`/`post_independence` = 1.0 says the pendant
rhythm and the window rhythm **must not** be reconciled — one is the frame and the other is the
fenestration, and `styles/garrison-colonial.json` states it directly: "the pendants mark the post
lines and therefore do not coincide with the window rhythm." A designer who nudges the drops onto
the window centres has produced an elevation that looks tidier and is telling a lie about how the
building is built.

Both are stated with a single permitted value because neither has a partial version. That is now the
third pack in this package to use that device, and it has settled into a convention worth naming:
**a band says how much latitude there is, and a single value says the rule is categorical.**

#### The dragon beam, stated as a length

`units` has no `deg`, and that turned out to be the right constraint. The angle of a dragon beam is
forced — it bisects a right angle — so stating it tells a compiler nothing. The pack states the
beam's **length** instead, √2 × the projection, which is the member somebody has to cut. The
critic's use of it comes from `styles/english-medieval-timber-frame.json`: it "cannot be faked
convincingly and is absent from all applied half-timbering", so its absence on a building that
jetties two faces is conclusive.

Which leads to a fact that surprised me and is now a rule (`depth_and_pile`/`jetty_faces`): **you
cannot jetty four faces of one storey.** The joists of one floor run one way. A jetty on the two
faces they run towards is free; the other two require the joists to run the other way, which they
cannot also do — so every corner where two jetties meet costs a dragon beam. That is why English
town houses jetty the street front and one flank, why the Wealden jetties its two cross-wings and
not its hall, and why the New England garrison jetties the front and returns onto the gables *at the
attic floor line*, where a separate floor makes the other direction available again.

#### Bindings, and three refusals

Bound to five: `garrison-colonial` (secondary, behind `timber-bay`, which keeps the plan — the bay
generates the rooms and the jetty generates the elevation), `garrison-revival` (**primary**, because
the node says of itself that "remove the overhang and the drops and nothing distinguishes it"),
`english-medieval-timber-frame`, `german-fachwerk` and `tudor-revival`.

Three nodes **refused with stated reasons**:

- `french-normandy-revival` states this pack's `material_change_rule` almost verbatim but has no
  jetty of its own — it names one as a permitted *datum* for a change of material. It is a consumer
  of one rule, not an instance of the type, and binding the pack would make the corpus assert a
  framed overhang on a style that has none. **This is OQ 49**, and the workaround available today is
  worse than the gap: `role: optional` still says the pack applies, and a note scoping it is prose
  no resolver reads.
- `new-england-colonial` carries a jetty in one example record — a two-phase Ipswich house whose
  later block has one — and not in the type.
- `english-cottage-vernacular` refuses itself in its own words: "the cottage uses the same joints
  with a quarter of the timber, no jetty, no display."

One address collision, found and renamed: `belt_course`/`projection` is `facade-classical`'s string
band at 2¼ in — one course of brick, or a 5/4 board — and co-binds on `garrison-revival`. Both are
horizontals at a floor line and they differ by a factor of seven. Renamed to `jetty_projection`.

## What is NOT done, with the measurement

Twenty-eight or so items of WP-4.1's list remain. The ones with the leverage measured above and
still missing: an **octagon/polygonal plan module** (17 nodes, 11 thinly bound), a
**portada/retablo ornament panel** (8/7), a **Mudejar brick corbelling module** (7/7), a
**strapwork/Jacobethan ornament** item (7/7), a **four-centred Tudor arch system** (new, raised by `opening-pointed`'s own boundary), a **leaded-casement-and-mullion
system** (new, raised by `opening-craftsman`'s refusal of `arts-and-crafts-british`, and it would
also serve what `opening-pointed` left alone in `english-gothic` and `tudor`), and a
**medieval/pre-Palladian English facade system** (new only in that two existing list items turn out
to be one pack). One more added by this tranche: **Prairie rectilinear art glass**, a set-out with rules about
asymmetry, colour and the placement of the few coloured pieces that `trim-prairie` has no figures
for and declined to invent. **50 nodes still have no opening-role pack**, down from 68, and **56 no
facade-role pack**, down from 67.

Struck off by the second tranche: the **adobe/rammed-earth module** (5 nodes on the list, and it
reached 9), the **opening half** of the Gothic Revival item (5 nodes, 3 of them previously with no
opening-role pack at all), and **both halves** of the Craftsman item — the opening system for 5 of the 7 nodes that had no
opening-role pack (the other 2 refused for stated reasons), and the Prairie trim family, which
binds one node and corrects a wrong binding rather than filling an empty role. Struck off by the
third: the **Dutch gambrel roof module**, which the list scoped at 3 nodes and reached 6, the
**dimensional half** of the cast-iron item, which reached 7 — its ornament half stays on the list —
and the **stone-coursing equivalent of `brick-course`**, the largest item on the list when measured,
bound to 12 of the 34 thinly-bound stone nodes on a stated criterion. Struck off by the fourth: the
**arcade**, which was never on the list at all and which three packs in this package asked for, the
**half-timber infill panel** (29 nodes, 21 thinly bound), **both** the four-centred Tudor arch and
the leaded-casement-and-mullion items, which turned out to be one window, and the **gable geometry**
item, which the list said the library had none of and which absorbed the crow-step and holbol items
with it, and **four ornament items at once** — sawn Gothic, sawn-bracket Victorian, turned Queen Anne
millwork and the pierced valance — which turned out to be one machine. Struck off by the fifth: the
**octagon/polygonal plan module**, the largest single item left when the tranche began and much the
smallest when measured (17 nodes on the list, 1 in fact); the **French vertical travée facade
system** and the **mansard/dormer massing module**, which were one system and are one pack; and the
**avant-corps half** of the Baroque item — whose curved-wall half is refused above with a reason,
not left silent. Struck off by the sixth: the **jetty module**, which the list scoped at 13 nodes
and which binds 5 — the five that carry figures — with three refused for stated reasons, one of
them raising OQ 49.

Two of the named seven were **not** attempted for a stated reason rather than left silent: the
muqarnas geometry and the tile/plaster/timber stratification that belong with the Moorish system
are absent from `moorish-arch` because the unit-cell proportions vary by regional school and there
is no figure here worth defending. A plausible number would have been worse than none.

## Verification

First tranche: `python3 build/check_all.py` — 22 checks, 461 tests. 38 packs resolve with 0
problems; `check_orders.py` 0 errors; `check_pack_bindings.py --strict` green at **131 of 132 nodes
bound**, up from 129. `tests/test_wp46_packs.py` was new (15 tests).

Later tranches: 23 checks green. **53 packs**, 0 errors from `check_orders.py`,
`check_modules.py --eval` and `check_systems.py` alike; bindings still 131 of 132 (the thirteen new
packs bind 121 nodes but every one of them was already bound, so the count does not move and should
not be read as no progress — the movement is in ROLE coverage, 68 → 60 nodes with no opening-role
pack, plus one wrong interior binding corrected, a roof system six nodes previously had nothing for,
a threshold system seven nodes had nothing for, a walling system twelve nodes had nothing for, and an arcade system sixteen
had nothing for -- of which only the last moves a role count, facade 67 to 61). A test pins that claim from the other direction: every node these
packs bind already had a binding, so none of them can have been used to paper over an unbound node.
Nodes carrying two packs or fewer: 36 → 12 (measured, not estimated — eight of the twelve nodes `stone-course` binds were at two or fewer, and four already had three or more).
`tests/test_wp46_packs.py` is now **198 tests**. The pinned pack count in
`tests/test_proportion_engine.py` is now read off the library instead of hard-coded — a test that
has to be edited every time a pack lands teaches the next author to edit tests rather than read
them.
