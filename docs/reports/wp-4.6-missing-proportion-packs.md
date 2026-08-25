# WP-4.6 — the missing proportion packs

*Started 24 Aug 2026. **Partially delivered: two packs of a list of thirty-odd**, chosen by
measured leverage. What remains is listed at the end with the measurement, not left implied.*

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

## What is NOT done, with the measurement

Twenty-eight or so items of WP-4.1's list remain. The ones with the leverage measured above and
still missing: an **adobe/rammed-earth module** (5 nodes, named in the plan, independently
confirmed by three batches), a **Gothic Revival facade and opening system** (4 nodes, and PB-7a
left Rural Gothic Villa with no opening-role pack at all as a direct result), a **Craftsman opening
system and Prairie trim family** (5 nodes, named in the plan), a **Dutch gambrel roof module**
(3 nodes), a **cast-iron system** (3 nodes). Sixty-eight nodes still have no opening-role pack and
sixty-seven no facade-role pack.

Two of the named seven were **not** attempted for a stated reason rather than left silent: the
muqarnas geometry and the tile/plaster/timber stratification that belong with the Moorish system
are absent from `moorish-arch` because the unit-cell proportions vary by regional school and there
is no figure here worth defending. A plausible number would have been worse than none.

## Verification

`python3 build/check_all.py` — 22 checks, 461 tests. 38 packs resolve with 0 problems;
`check_orders.py` 0 errors; `check_pack_bindings.py --strict` green at **131 of 132 nodes bound**,
up from 129. `tests/test_wp46_packs.py` is new (15 tests). The pinned pack count in
`tests/test_proportion_engine.py` is now read off the library instead of hard-coded — a test that
has to be edited every time a pack lands teaches the next author to edit tests rather than read
them.
