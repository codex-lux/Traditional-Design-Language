# WP-4.5 — Rooms, groupings and partis to full coverage

*24 August 2026.*

Of 132 buildable nodes, 128 carry a canonical massing and only **39 were named by a parti**.
That is now **129 of 132 named and zero uncovered**: every buildable style with a canonical
massing has at least one diagram of its own.

## The package's premise was wrong, and the truth was worse

`PLAN-OF-ACTION.md`, `CLAUDE.md` and `STATE-OF-THE-PROJECT.md` all said a style with a canonical
massing and no native parti "cannot be composed for at all." It could. `compose.py`'s
`pick_partis` never refuses — nativity is worth `+3.0`, a lineage relative `+1.6`, and otherwise
the candidate survives carrying the string *"NOT native to this style — the composer is borrowing
a diagram."* Measured before any work began: `spanish-colonial-revival`, whose canonical massing
is `courtyard-u`, composed as a **Foursquare**; so did `shingle-style`, whose canonical massing is
`massed-picturesque`. Geometry, structure, roof, elevation and the fault corpus then all worked on
the wrong diagram, and the only thing that said so was a string in the decision log nobody reads.
The hard refusal the docs promised does exist — in `mcp_server/core.py`'s `list_partis`, which
returned nothing for the 93 unnamed styles. A silent wrong answer, not a refusal. Corrected in all
three documents.

## What was built

**`build/check_partis.py`**, wired into `check_all.py` as a 22nd check. `schema/parti.schema.json`
had existed since the layer was built and was referenced by *no code in the repository*: a
malformed parti surfaced only as a `KeyError` inside `compose.py` at the moment a brief reached
it. It now checks the schema plus the referential integrity nothing checked — room types,
groupings, massings, that every `styles[]` entry is a real node **and a buildable rank** (a parti
native to a family is a category error), door-graph closure, unreachable rooms, storeys against
levels used — and reports coverage, which is the number this package exists to move.

**Two rooms.** `rooms/courtyard.json` — the only artifact that genuinely blocked a diagram, since
19 nodes have a courtyard massing as canonical and the void they are built around had no room to
be. `rooms/loggia.json` had carried a hard `must_adjoin: courtyard` since it was written, demoted
to a warning by an allowlist; that reference now resolves. And `rooms/overlook.json`, the one room
from WP-2.1's unmapped list with real evidence behind it — it recurred independently in two source
drawings while overloading `landing`, which is worse than a plain gap because `landing` sits inside
`plan_check`'s `{stair-hall, landing}` alias group, so every mezzanine in the corpus was being read
as a stair hall.

**Nine partis**, covering 50 nodes: `courtyard-and-portal` (18 styles), `living-hall-picturesque`
(13), `great-hall-h-plan` (8), `connected-farmstead` (5), `single-cell-hall` (5), `tower-villa` (2),
`shotgun-linear`, `dogtrot-open-passage`, `octagon-radial`.

**36 style-list extensions**, placed by plan topology rather than by whichever partis a node's
massing set happened to intersect — `english-georgian` alone matched five, and adding a style to
every diagram it could plausibly use would make the nativity bonus meaningless.

**WP-2.1's two validator-data proposals**, and one was only half a fix as proposed — see below.

## What was found

**The validator could not read a gallery-circulation house.** `plan_check` bridges "directly or
across a hall" through rooms whose `function_class` is `circulation` or `threshold`. In the
courtyard types the corridor is a `loggia`, typed `outdoor` because it is roofed and open rather
than enclosed — so every bedroom in a courtyard house was reported as failing to reach a bathroom.
The corridor, which is the correct answer, read as a fault: eleven of the courtyard parti's
seventeen serious findings were that one blind spot. The test is now what the plan *does* with the
room rather than what the room is — an outdoor room with doors to three or more rooms is being used
as circulation; two doors is a porch you pass through, three is a gallery. No existing plan moved,
because until now nothing in the corpus had an outdoor room with three doors on it.
`charleston-single-piazza` has the same shape of room and did not show the damage, because its
piazza is not the only circulation — a stair-hall does the bridging. That is why this went unseen:
the corpus had a gallery house already, and it happened to have a hall too.

**A borrowed diagram outranked a native one, and this package made it visible.** Nativity was worth
`fit * 6` against 8 for a serious finding, so five serious findings outweighed being the right
diagram entirely. Adding nine partis for the composer to borrow from turned that from a latent flaw
into a `tidewater-georgian` brief that came back recommending an **octagon**. `NATIVITY_W` is now
20 — about twelve serious findings — and deliberately still not enough to outrank a fatal at 100,
because a native plan with something wrong in it should lose to a clean borrowed one. A fatal is a
thing that is wrong; foreign is not. This re-ranked the pinned Georgian brief from Side-Hall Town
House to Centre Passage, Double Pile: from a *town house* diagram to what a five-bay Tidewater
plantation house of 3,200 sf actually is.

**Half the kits that state a ceiling height were ignored.** `ceilings_for()` read only
storey-specific keys — `ground`, `first`, `principal`, `second`, `upper`, `chamber`. Thirteen kits
use those; thirteen others say `ceiling_height_min_ft`, `storey_height_range_ft`,
`stube_ceiling_height_max` and silently took the 9.0 ft default. So a shotgun house, whose kit
specifies a 10 ft minimum and 11–12 preferred and whose whole character is a tall room on a small
footprint, was composed at nine feet and then failed its own style's transom-datum constraint at
**fatal**. The style had spoken and nothing was listening.

**A rule declared on two rooms is only half-fixed when you fix one.** WP-2.1 proposed adding
`dressing-room` to the primary-bedroom → primary-bathroom `via` list. Doing so left `good-07` still
failing, from `rooms/primary-bathroom.json`'s own reciprocal `must_adjoin`, which had no `via` of
its own. WP-2.1 could not have seen that from the bedroom's side. Both sides now carry it.

**Every reception room in the catalogue assumes it is on the ground floor.** All thirteen
public/living rooms carry a ground-floor adjacency rule — drawing-room must reach a dining room,
parlor and best-parlor and morning-room an entrance-hall, sitting-room a parlor. An upper-floor
state room can satisfy none of them, so the H-plan's great chamber typed `drawing-room` tripped a
*fatal* for not reaching a dining room a storey below it. Typed `library`, whose rule is `strong`
rather than `hard`, so the same impossibility reports as serious and the diagram stays composable.

**An overlook's defining relationship cannot be stated.** It is open to the hall on the storey
*below*, and a plan record expresses adjacency within a level only — so the rule written for it
could never pass on any correct plan. Held at `preferred` rather than `strong` so a right answer is
not called a defect.

**`compose.py`'s pick order was decided by the filesystem.** It sorted on `-fit` alone, and
`PARTIS` is built by `glob()`, so ties were broken by directory order — and on the Georgian brief
four partis tie at exactly 2.00. Now `(-fit, id)`.

**The 3-bay floor dropped houses rather than inflating them.** `footprint()` floored every diagram
at 3 bays *and* declared a parti lot-infeasible when the lot cleared fewer than its floor — so
`hall-single-cell`, which the massing catalogue gives as 250–500 sf and "1–2" bays, would have been
discarded before scoring. `geometry.py` had always used 2, so the two engines disagreed and neither
said so. `scaling.min_bay_count` added to the parti schema, defaulting to 3.

## What was deliberately not done

- **Eleven of the thirteen rooms first scoped.** `rooms/hall.json` already carries
  `aka: ["great hall", "living hall", "houseplace"]` with `massing_fit` covering
  `hall-single-cell`, `h-plan-manor` and `massed-picturesque`; `cross-passage` is the screens
  passage; `terrace` already has `aka: ["patio"]`; `loggia` already has `["portal", "corredor"]`.
  Nine of eleven partis needed no new room at all. `inglenook` is a hearth treatment rather than a
  room and belongs in `elements/slots.json`. `solar`, `buttery` and `great-chamber` are typed to
  existing rooms with the parti's `name` field, as `charleston-single-piazza` already does.
  `barn`, `woodshed` and `carriage-house` are a **detached outbuilding** problem — the only
  mechanism for one is `garage-and-hyphen`, and three new rooms without it would give
  `geometry.py` three buildings to place inside the house envelope. The connected farmstead's
  chain therefore stops at the shed, and the room says so rather than faking a barn.
- **Six of WP-2.1's unmapped rooms** (`grilling-porch`, `flex-room`, `bonus-room-over-garage`,
  `game-room`, `exercise-room`, `wine-room`). Each is a ~250-line researched file and together
  they unblock **zero** of the 90 nodes. They are contemporary spec-house program and belong in a
  package about that.
- **Three of the package's own named dozen.** `telescope` unblocks nobody — `telescope-house` is
  canonical for no style at all, which is the exact inverse of the gap this package addresses.
  `split-level` unblocks nobody and needs a schema decision (OQ 34). `foursquare side hall`
  unblocks at most one node and `foursquare-quadrant` is *already*
  `circulation_parti: "side-hall"`. Named here rather than quietly dropped.
- **"Complete `style_variation` for every room across every buildable style."** The package text
  asks for this; it is 58 rooms × up to 132 nodes, larger than every other strand combined, and
  `STATE-OF-THE-PROJECT.md` already records all 58 rooms as carrying `style_variation`. Declared
  met at that bar and explicitly out of scope at the literal one.
- **New groupings.** `plan_check` scores a grouping with no `attaches_to` for the plan's massing at
  `info`, weight 0.0, so authoring `courtyard-and-portal-range` and the rest buys tidiness and no
  points. Widening five existing groupings' `circulation_parti` lists — which were narrow enough to
  exclude every centre-hall house from `kitchen-work-core`, though every Georgian has one — was the
  change that actually removed noise.

## Open questions raised

**OQ 33 — the courtyard is a void the geometry engine cannot draw.** `geometry.py` and `solver.py`
both drop every `function_class: outdoor` room before placement, so the courtyard partis compose,
score and render as a *solid* block with no void in it. Pre-existing (the Charleston piazza has the
same problem today) but WP-4.5 makes it the dominant case, for 19 nodes whose canonical massing
*is* the void.

**OQ 34 — no half-storey.** `rooms[].level` is an integer and every consumer reads it as a level
index, so a split-level cannot be expressed. It unblocks zero nodes, so no schema change was spent
on it; the concrete proposal for whoever rules is that `level` stays integer and an optional
`level_offset_ft` is added beside it.

**OQ 35 — no vertical adjacency, and no upper-floor state room.** Two findings with one cause: the
plan record cannot say "open to the room below" (the overlook) and every reception room in the
catalogue carries a ground-floor adjacency rule (the great chamber). Both are currently worked
around by weakening a rule or retyping a room, and both would be answered properly by letting
adjacency span levels.
