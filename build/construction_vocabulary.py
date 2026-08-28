#!/usr/bin/env python3
"""The controlled vocabulary for `exceptions[].granted_when.construction`
(schema/fault.schema.json), and the resolver that decides whether a token
holds for a style.

WHY THIS EXISTS. 331 of the fault corpus's 846 exceptions carry an
`granted_when` block, 123 of them naming a construction, and until WP-8.4 not
one line of code read any of it. `mcp_server/core.py` selects an exception
with `e["style"] == style` and nothing else, at all three of its selection
sites — so `architrave-that-is-not-there`'s Pueblo Revival licence, written
for an adobe or rammed-earth wall, was excusing a stucco-over-wood-frame
house, and `baluster-too-thin`'s 1870–1910 wood-frame licence was excusing
any date in any construction. An exception is a LICENCE; a licence granted
without reading its own precondition is a fault the corpus has stopped
reporting.

WHAT A TOKEN IS, AND WHAT IT IS NOT. The 78 tokens in use mix five different
kinds of fact — wall assembly (`adobe`, `solid-masonry-two-wythe`,
`balloon-frame`), cladding (`thick-stucco`, `shingle-cladding`), glazing
(`crown-glass`, `casement`), roofing (`slate-roof`) and site condition
(`zero-lot-line`, `street-wall`) — and they were never checked against
anything. This module does NOT invent a construction ontology to hold them.
It is a MAPPING TABLE onto variant ids that already exist in `kits/`, and a
token with no honest target is recorded in UNMAPPABLE with a reason rather
than given one. The ruling of 28 Aug 2026 is explicit: no new corpus ids are
authored on the authority of fault-exception prose.

Like `build/constraint_vocabulary.py`, this table is closed: an agent that
needs a token which is not here REPORTS THE GAP rather than adding one, and
`check_faults.py` errors on a token in neither table.

THE THREE VERDICTS, AND WHY `holds` IS THE HARD ONE. `resolve()` returns
`holds`, `fails` or `undecidable`, never a bare boolean, because the question
"is this house built of adobe?" is usually not answerable from a style id.
`check_measurements` is handed a style and a dict of measurements; the style
resolves to a KIT, which says which constructions the tradition allows, not
which one this house used. So:

  * `fails`      — every variant the token names is absent from the style's
                   resolved record, or present and `forbidden`. The tradition
                   cannot be built this way, so the licence cannot be earned.
  * `holds`      — the token's variants include a `canonical` one AND no
                   canonical variant of that slot lies outside the token's
                   set. The style is built this way and only this way.
  * `undecidable` — anything else: the style permits this construction and
                   others too, and nothing in front of us says which one this
                   house is.

A caller that KNOWS — a plan record declaring `construction_type` — passes
`declared` and gets a straight answer. That is the only path to certainty and
it is the one worth widening.

`strength: "partial"` marks a token carrying a qualifier the corpus does not
record. `thick-stucco` is the type: the kit says the wall is rendered, and
says nothing about how thick the render is. A partial token may return
`fails` (no render anywhere is still a real answer) but NEVER `holds` — its
best case is `undecidable`. Reporting `holds` on the half of the token we can
see would widen a licence its author deliberately narrowed, which is the
error this whole package exists to remove.

Run with --verbose for the table, --coverage for the corpus report.
"""
import collections
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KITS = os.path.join(ROOT, "kits")
FAULTS = os.path.join(ROOT, "faults")

# ---------------------------------------------------------------------------
# Families, spelled once. Every id below is a variant that exists in kits/;
# `check_table()` fails the build if one stops existing.
# ---------------------------------------------------------------------------
_TIMBER_FRAME = ["braced-timber-frame", "box-frame", "cruck-frame",
                 "close-studded-oak-frame-on-stone-soubassement",
                 "colombage-over-stone-base", "low-timber-frame-daub-infill",
                 "timber-frame-on-brick-plinth"]
_LIGHT_FRAME = ["balloon-frame", "balloon-frame-with-masonry-veneer", "platform-frame",
                "light-timber-frame", "light-wood-frame",
                "light-timber-frame-forbidden-in-family-cascade",
                "stucco-over-wood-frame", "wood-frame-wire-lath-portland-cement-stucco"]
_MASONRY_BEARING = ["solid-masonry", "solid-masonry-two-wythe", "solid-masonry-three-wythe",
                    "solid-brick-masonry", "brick-bearing-masonry", "brick-party-wall-masonry",
                    "granite", "rubble", "flint-or-chalk",
                    "limestone-or-roussard-rubble-dressed-openings",
                    "trabeated-dressed-ashlar-no-mortar", "arcuated-concrete-or-brick",
                    "lime-and-gravel-concrete-board-formed",
                    "stucco-over-concrete-block", "stucco-over-hollow-clay-tile"]
_MASONRY_STONE = ["granite", "rubble", "flint-or-chalk",
                  "limestone-or-roussard-rubble-dressed-openings",
                  "trabeated-dressed-ashlar-no-mortar"]
_EARTH = ["adobe", "stucco-over-adobe", "clay-lump", "cob", "rammed-earth",
          "sun-dried-brick-or-rubble-masonry"]
_CLAD_STUCCO = ["stucco", "smooth-stucco", "cement-stucco", "cement-render",
                "earth-toned-stucco", "off-white-warm-earth-stucco", "stucco-scored",
                "regency-ruled-scored-stucco", "stucco-with-wood-banding", "stucco-on-brick",
                "stuccoed-brick", "stucco-over-gravel-concrete",
                "troweled-modelled-plastic-stucco", "rubble-limestone-lime-render",
                "lime-plaster-limewash-white", "limewash"]
_CLAD_SHINGLE = ["shingle", "shingle-continuous-field", "shingle-siding", "wood-shingle"]
_CLAD_BOARD = ["clapboard", "clapboard-horizontal", "beaded-clapboard", "drop-siding",
               "narrow-lap-siding", "board-and-batten", "board-and-batten-vertical",
               "flush-board-rusticated"]
_CLAD_BRICK = ["brick-common-bond", "brick-english-bond", "brick-flemish-bond",
               "brick-flemish-bond-glazed-headers", "brick-flemish-bond-uniform",
               "brick-moulded", "brick-pressed", "pressed-brick", "clinker-brick",
               "roman-brick", "red-brick-diaper-pattern", "red-brick-with-pale-stone-dressings",
               "brick-with-stone-dressings", "brick-with-sandstone-speklagen",
               "banded-brick-and-stone-speklagen", "banded-structural-polychrome-brick"]
_CLAD_STONE = ["ashlar-stone", "ashlar-or-coursed-stone", "plain-ashlar-stone",
               "dressed-ashlar-stone", "dressed-sandstone-ashlar", "coursed-ashlar-stone",
               "continuous-fine-ashlar-whole-elevation", "coursed-limestone",
               "coursed-rubble-field-ashlar-dressings", "rock-faced-ashlar",
               "brownstone-ashlar", "stone-ashlar", "stone-rubble",
               "squared-rubble-granite-ashlar-harled-rubble", "granite-longere",
               "tufa-limestone", "tezontle"]
_STREET_WALL = ["party-wall-continuous-street-wall", "party-walled-urban-row",
                "party-wall-terrace-with-front-area", "jettied-party-walled-street-row",
                "stone-townhouse-in-street-row", "palazzetto-in-continuous-street-wall",
                "urban-zero-lot-line"]

VOCABULARY = {
    # ------------------------------------------------------- wall assembly
    "adobe": {
        "slots": {"construction_type": ["adobe", "stucco-over-adobe", "clay-lump",
                                        "sun-dried-brick-or-rubble-masonry"],
                  "primary_cladding": ["adobe"]},
        "strength": "exact",
        "note": "Sun-dried mud brick laid in mud mortar. `cob` and `rammed-earth` are monolithic "
                "earth and have their own tokens; `stucco-over-adobe` is adobe with a render "
                "coat, which is what nearly every surviving example is."},
    "rammed-earth": {
        "slots": {"construction_type": ["rammed-earth", "cob"]},
        "strength": "exact",
        "note": "Monolithic earth rammed in formwork. `cob` is included because it is the same "
                "wall from the fault corpus's point of view -- a thick monolithic earth wall "
                "with no course lines -- and no exception in the corpus distinguishes them."},
    "tapia": {
        "slots": {"construction_type": ["rammed-earth"]},
        "strength": "exact",
        "note": "The Iberian and Spanish-American name for rammed earth. Recorded here rather "
                "than as a new variant id: it is the same wall under a regional name, and the "
                "corpus does not carry a `tapia` variant."},
    "solid-masonry-two-wythe": {
        "slots": {"construction_type": ["solid-masonry-two-wythe"]},
        "strength": "exact", "note": "The variant id itself."},
    "solid-masonry-three-wythe": {
        "slots": {"construction_type": ["solid-masonry-three-wythe"]},
        "strength": "exact", "note": "The variant id itself."},
    "solid-masonry": {
        "slots": {"construction_type": ["solid-masonry", "solid-masonry-two-wythe",
                                        "solid-masonry-three-wythe", "solid-brick-masonry"]},
        "strength": "exact",
        "note": "Solid masonry of unstated thickness -- the two- and three-wythe variants are "
                "included because both ARE solid masonry, and an exception written for the "
                "general case means the specific ones too."},
    "load-bearing-masonry": {
        "slots": {"construction_type": list(_MASONRY_BEARING)},
        "strength": "exact",
        "note": "Any wall that carries its own floors: brick, stone, concrete or hollow tile. "
                "Excludes every veneer-over-frame variant, which is the distinction the token "
                "exists to draw."},
    "mass-masonry": {
        "slots": {"construction_type": list(_MASONRY_BEARING)},
        "strength": "exact",
        "note": "A second spelling of `load-bearing-masonry` in the same corpus (WP-8.4 finding "
                "-- five spellings of the one idea). Mapped identically rather than merged, "
                "because renaming a token in 846 exception records is a separate change."},
    "masonry": {
        "slots": {"construction_type": list(_MASONRY_BEARING)},
        "strength": "exact",
        "note": "Third spelling. Deliberately does NOT include `masonry-veneer-over-frame`: "
                "every exception using this token is about wall behaviour a veneer does not "
                "have (a Dutch gable parapet built in brick, a real masonry reveal)."},
    "mass-wall": {
        "slots": {"construction_type": list(_MASONRY_BEARING) + list(_EARTH)},
        "strength": "exact",
        "note": "Any thick load-bearing wall, earth or masonry -- the widest of the five "
                "spellings, and the only one that reaches adobe. Used where the licence turns "
                "on wall THICKNESS (a deep reveal, an opening placed by interior need) rather "
                "than on the material."},
    "load-bearing-stone": {
        "slots": {"construction_type": list(_MASONRY_STONE)},
        "strength": "exact", "note": "Load-bearing masonry, stone only."},
    "brick": {
        # CLADDING FIRST, and for this token only: the corpus records brick-versus-stone in the
        # FACE, not in the assembly -- a brick Georgian and a granite baronial house are both
        # `solid-masonry-two-wythe`. Slot order is authority order, so for a MATERIAL question
        # the material-bearing slot has to lead. (The material-neutral tokens -- `mass-wall`,
        # `load-bearing-masonry` -- keep construction_type first, because for them the assembly
        # IS the answer.)
        "slots": {"primary_cladding": list(_CLAD_BRICK),
                  "construction_type": ["solid-brick-masonry", "brick-bearing-masonry",
                                        "brick-party-wall-masonry"]},
        "strength": "exact",
        "note": "Brick as the face or as the wall. DELIBERATELY EXCLUDES "
                "`solid-masonry-two-wythe` and `-three-wythe`, which say how many wythes and "
                "nothing about the material: with them in the list this token returned `holds` "
                "on `scottish-baronial`, whose construction is two-wythe solid masonry and "
                "whose cladding is `squared-rubble-granite-ashlar-harled-rubble` -- a granite "
                "building answering yes to `brick`. The wythe count is a `mass-wall` fact and "
                "belongs to the material-neutral tokens; brick versus stone is recorded in the "
                "CLADDING, which this token reads and which decides it. Found by the WP-8.4 "
                "adversarial audit."},
    "roman-brick": {
        "slots": {"primary_cladding": ["roman-brick"]},
        "strength": "exact", "note": "The long thin brick of the Prairie School."},
    "cut-stone": {
        "slots": {"construction_type": ["trabeated-dressed-ashlar-no-mortar", "granite"],
                  "primary_cladding": ["ashlar-stone", "ashlar-or-coursed-stone",
                                       "plain-ashlar-stone", "dressed-ashlar-stone",
                                       "dressed-sandstone-ashlar", "coursed-ashlar-stone",
                                       "continuous-fine-ashlar-whole-elevation",
                                       "coursed-limestone", "rock-faced-ashlar",
                                       "brownstone-ashlar", "stone-ashlar"]},
        "strength": "exact",
        "note": "Dressed and squared stone, as against rubble. `rock-faced-ashlar` counts: the "
                "face is left rough but the bed and the joint are cut."},
    "stone-rubble": {
        # CLADDING FIRST, for the same reason as `brick` and found on the SAME NODE. Rubble
        # versus ashlar is a MATERIAL-AND-COURSING question and the corpus records it in the
        # face; `solid-masonry-two-wythe` says how many wythes and nothing about the stone.
        # With construction_type leading, `scottish-baronial` -- canonically
        # `squared-rubble-granite-ashlar-harled-rubble` on the face, and named in the `brick`
        # note above as the node that proves this rule -- answered a hard `fails` to
        # `stone-rubble`, and the detail line printed the canonical rubble cladding while
        # refusing. `quoin-by-catalogue`'s Baronial licence, whose own `why` reads "Rubble
        # walling with dressed ashlar corner dressings", was refused on a rubble-walled house.
        # The material-neutral tokens (`mass-wall`, `load-bearing-masonry`) keep
        # construction_type first, because for them the assembly IS the answer; `adobe`, `log`
        # and `wood-frame` keep it too, because they ask what the wall is MADE OF as an
        # assembly and a render can hide any of them. Second instance of one bug; the general
        # form -- a material question decided by a material-NEUTRAL assembly variant -- is
        # raised as `oq/a-material-neutral-assembly-decides-a-material-question`.
        "slots": {"primary_cladding": ["stone-rubble", "coursed-rubble-field-ashlar-dressings",
                                       "squared-rubble-granite-ashlar-harled-rubble",
                                       "rubble-limestone-lime-render"],
                  "construction_type": ["rubble", "limestone-or-roussard-rubble-dressed-openings",
                                        "flint-or-chalk"]},
        "strength": "exact", "note": "Undressed or roughly squared stone."},
    "wood-frame": {
        "slots": {"construction_type": list(_TIMBER_FRAME) + list(_LIGHT_FRAME) +
                                       ["log-under-weatherboard"],
                  "primary_cladding": list(_CLAD_BOARD) + list(_CLAD_SHINGLE)},
        "strength": "exact",
        "note": "Any wall framed in wood, heavy or light. The cladding slot is read because "
                "clapboard and wood shingle are frame surfaces in this corpus -- there is no "
                "variant of either applied to a solid masonry wall."},
    "timber-frame": {
        "slots": {"construction_type": list(_TIMBER_FRAME)},
        "strength": "exact",
        "note": "Heavy frame, hand-cut and pegged, as against the sawn light frames below."},
    "heavy-timber": {
        "slots": {"construction_type": list(_TIMBER_FRAME)},
        "strength": "exact", "note": "A second spelling of `timber-frame`."},
    "braced-timber-frame": {
        "slots": {"construction_type": list(_TIMBER_FRAME)},
        "strength": "exact",
        "note": "The variant id, plus the regional frames that ARE braced frames and differ "
                "only in their plinth (`colombage-over-stone-base`, "
                "`timber-frame-on-brick-plinth`, `close-studded-oak-frame-on-stone-"
                "soubassement`)."},
    "balloon-frame": {
        "slots": {"construction_type": ["balloon-frame", "balloon-frame-with-masonry-veneer"]},
        "strength": "exact", "note": "Continuous studs from sill to plate."},
    "platform-frame": {
        "slots": {"construction_type": ["platform-frame", "light-timber-frame",
                                        "light-wood-frame"]},
        "strength": "exact", "note": "Storey-height studs on a platform."},
    "masonry-veneer-over-frame": {
        "slots": {"construction_type": ["masonry-veneer-over-frame",
                                        "balloon-frame-with-masonry-veneer",
                                        "masonry-or-masonry-veneer-only"]},
        "strength": "exact", "note": "A single wythe hung on a frame wall."},
    "log": {
        "slots": {"construction_type": ["log", "log-under-weatherboard"],
                  "primary_cladding": ["log"]},
        "strength": "exact", "note": "Horizontal notched logs."},
    "half-timbered": {
        "slots": {"primary_cladding": ["half-timber-infill", "half-timber-infill-exposed-frame",
                                       "fachwerk-alsatian", "colombage-brick-plinth-timber-frame",
                                       "brick-nogging-infill",
                                       "brick-nogging-herringbone-or-chequer",
                                       "wattle-and-daub-infill", "lath-and-plaster-infill",
                                       "torchis-clay-and-chopped-straw"],
                  "expressed_frame": ["structural-and-expressed"]},
        "strength": "exact",
        "note": "A frame left visible with its panels infilled. Reads `expressed_frame` as well "
                "-- OQ 47's slot is the corpus's own answer to whether the frame shows."},
    "briquette-entre-poteaux": {
        "slots": {"primary_cladding": ["brick-nogging-infill",
                                       "brick-nogging-herringbone-or-chequer"]},
        "strength": "exact", "note": "Creole brick nogging between the posts of a frame."},
    "stucco-over-frame": {
        "slots": {"construction_type": ["stucco-over-wood-frame",
                                        "wood-frame-wire-lath-portland-cement-stucco"]},
        "strength": "exact", "note": "Render on lath on a wood frame."},
    "stucco": {
        "slots": {"primary_cladding": list(_CLAD_STUCCO)},
        "strength": "exact", "note": "Any render, of any thickness, on any backing."},
    "plaster": {
        "slots": {"primary_cladding": list(_CLAD_STUCCO)},
        "strength": "exact",
        "note": "A second spelling of `stucco` in the same corpus; the one exception using it "
                "pairs the two tokens in a single list, which is the giveaway."},
    "thick-stucco": {
        "slots": {"primary_cladding": list(_CLAD_STUCCO)},
        "strength": "partial",
        "note": "PARTIAL: the corpus records the render and nothing about its thickness. There "
                "is no slot, kit parameter or pack rule anywhere for a render's depth, so the "
                "narrowing this token's author intended cannot be checked. It may refuse a "
                "style with no render at all; it may never confirm one."},
    "cast-iron": {
        "slots": {"primary_cladding": ["cast-iron-front", "cast-iron-elements"]},
        "strength": "exact", "note": "A cast-iron front or applied cast-iron elements."},
    "terracotta": {
        "slots": {"primary_cladding": ["terra-cotta-panel", "terracotta-panel"]},
        "strength": "exact",
        "note": "Both spellings of the variant id exist in kits/ -- a second WP-8.4 finding, and "
                "one the ontology should settle."},
    "shingle-cladding": {
        "slots": {"primary_cladding": list(_CLAD_SHINGLE),
                  "secondary_cladding": ["shingle", "cut-shingle"]},
        "strength": "exact", "note": "Wood shingle as a wall surface."},
    "wood-shingle-clad": {
        "slots": {"primary_cladding": list(_CLAD_SHINGLE),
                  "secondary_cladding": ["shingle", "cut-shingle"]},
        "strength": "exact", "note": "A second spelling of `shingle-cladding`."},
    "wood-shingle-cladding": {
        "slots": {"primary_cladding": list(_CLAD_SHINGLE),
                  "secondary_cladding": ["shingle", "cut-shingle"]},
        "strength": "exact", "note": "A third spelling of `shingle-cladding`."},
    "board-cladding": {
        "slots": {"primary_cladding": list(_CLAD_BOARD)},
        "strength": "exact",
        "note": "Sawn board as a wall surface, horizontal or vertical. The one exception using "
                "it is about the flatness of a trim board on a boarded wall, which is true of "
                "either direction."},

    # ------------------------------------------------------- roof covering
    "slate-roof": {
        "slots": {"roof_material": ["slate", "uniform-course-slate-or-imitation",
                                    "graded-stone-slate-large-to-small"]},
        "strength": "exact", "note": "Slate, or the stone slate of the limestone belt."},
    "stone-slate-roof": {
        "slots": {"roof_material": ["graded-stone-slate-large-to-small"]},
        "strength": "exact", "note": "Graded stone slate, largest at the eave."},
    "standing-seam-metal": {
        "slots": {"roof_material": ["standing-seam-metal",
                                    "corrugated-or-standing-seam-metal"]},
        "strength": "exact", "note": "Mechanically seamed sheet metal."},
    "clay-tile-roof": {
        "slots": {"roof_material": ["clay-tile-barrel", "clay-tile-flat", "flat-clay-tile",
                                    "plain-clay-tile", "flat-tile", "pantile"]},
        "strength": "exact", "note": "Any fired clay tile."},
    "clay-tile-barrel": {
        "slots": {"roof_material": ["clay-tile-barrel"]},
        "strength": "exact", "note": "The half-round pan-and-cover tile."},
    "barrel-tile-roof": {
        "slots": {"roof_material": ["clay-tile-barrel"]},
        "strength": "exact", "note": "A second spelling of `clay-tile-barrel`."},
    "mission-tile-roof": {
        "slots": {"roof_material": ["clay-tile-barrel"]},
        "strength": "exact",
        "note": "A third spelling. Mission tile IS barrel tile; the corpus carries one variant "
                "for it and three tokens naming that variant."},
    "clay-tile-mission": {
        "slots": {"roof_material": ["clay-tile-barrel"]},
        "strength": "exact", "note": "A fourth spelling of `clay-tile-barrel`."},
    "composition-shingle": {
        "slots": {"roof_material": ["composition-shingle", "composition-shingle-plain",
                                    "dimensional-architectural-composition"]},
        "strength": "exact", "note": "Asphalt shingle, plain or laminated."},
    "asphalt-laminate": {
        "slots": {"roof_material": ["dimensional-architectural-composition"]},
        "strength": "exact", "note": "The thick laminated asphalt shingle."},

    # ------------------------------------------------------- openings
    "casement": {
        "slots": {"window_type": ["casement", "casement-leaded", "casement-steel",
                                  "casement-with-hood-mould", "paired-casement",
                                  "small-side-hung-casement",
                                  "small-paned-casement-or-sash-deep-reveal",
                                  "croisee-cross-mullioned"]},
        "strength": "exact", "note": "A side-hung sash of any material."},
    "leaded-casement": {
        "slots": {"window_type": ["casement-leaded", "mullion-transom-flush-grid-leaded"]},
        "strength": "exact", "note": "A casement glazed in lead cames."},
    "steel-sash": {
        "slots": {"window_type": ["casement-steel"]},
        "strength": "exact", "note": "The one steel window variant in the corpus."},
    "stone-lintel": {
        "slots": {"window_head_masonry": ["dressed-stone-lintel",
                                          "stone-lintel-or-relieving-arch-with-hood-mould"]},
        "strength": "exact", "note": "A single stone spanning the head."},

    # ------------------------------------------------------- site and settlement
    "party-wall-row": {
        "slots": {"street_relationship": list(_STREET_WALL),
                  "construction_type": ["brick-party-wall-masonry"]},
        "strength": "exact", "note": "A house sharing its flank walls with its neighbours."},
    "party-wall": {
        "slots": {"street_relationship": list(_STREET_WALL),
                  "construction_type": ["brick-party-wall-masonry"]},
        "strength": "exact", "note": "A second spelling of `party-wall-row`."},
    "terrace": {
        "slots": {"street_relationship": list(_STREET_WALL)},
        "strength": "exact", "note": "The British name for the party-walled row."},
    "street-wall": {
        "slots": {"street_relationship": list(_STREET_WALL) +
                                         ["blank-rusticated-street-face-courtyard-lit"]},
        "strength": "exact",
        "note": "A continuous built frontage on the street line, whether the flanks are shared "
                "or the plan turns inward on a court."},
    "zero-lot-line": {
        "slots": {"street_relationship": list(_STREET_WALL) +
                                         ["blank-rusticated-street-face-courtyard-lit",
                                          "blind-wall-inward-courtyard"]},
        "strength": "exact", "note": "The building standing on its own boundary."},
    "raised-floor": {
        "slots": {"grade_relationship": ["raised-on-piers", "raised-basement",
                                         "raised-on-masonry-service-storey"]},
        "strength": "exact", "note": "A principal floor carried clear of the ground."},
    "raised-basement": {
        "slots": {"grade_relationship": ["raised-basement",
                                         "raised-on-masonry-service-storey"]},
        "strength": "exact", "note": "A service storey half out of the ground."},
    "pier-base": {
        "slots": {"grade_relationship": ["raised-on-piers"]},
        "strength": "exact", "note": "The house standing on piers rather than a wall."},
    "masonry-pier": {
        "slots": {"porch_support": ["masonry-pier", "square-masonry-pier", "arcaded-masonry-pier",
                                    "battered-pier-on-masonry-base", "square-pier"],
                  "grade_relationship": ["raised-on-piers"]},
        "strength": "exact",
        "note": "A masonry pier carrying a porch. `porch_support` is the slot that records it; "
                "`grade_relationship` is read as well for the pier-founded house."},
    "carport": {
        "slots": {"garage_strategy": ["attached-carport"]},
        "strength": "exact", "note": "An open roofed vehicle bay."},
    "detached-outbuilding": {
        "slots": {"garage_strategy": ["detached-outbuilding", "detached-framed-outbuilding",
                                      "detached-matching-outbuilding", "detached-rear-lot",
                                      "detached-rear-of-lot", "detached-outbuilding-off-axis",
                                      "detached-in-the-dependency-position",
                                      "detached-stone-outbuilding-matched-coursing",
                                      "detached-stucco-outbuilding",
                                      "detached-shingled-outbuilding",
                                      "detached-single-purpose-outbuilding",
                                      "detached-low-outbuilding-off-principal-elevation",
                                      "rear-lane-detached", "rear-lane-detached-or-none"]},
        "strength": "exact",
        "note": "Vehicles housed in a separate building, which is the condition under which a "
                "garage-door fault about the principal elevation does not arise."},

    # ------------------------------------------------------- ornament
    "sawn-wood-ornament": {
        "slots": {"ornament_vocabulary": ["sawn-scroll-bracket-vocabulary",
                                          "pierced-cusped-bargeboard-pattern",
                                          "gouged-and-fluted-frieze",
                                          "turned-chamfered-porch-post-sawn-bracket-"
                                          "pierced-valance"]},
        "strength": "exact",
        "note": "Flat jigsawn ornament. NOT a construction at all -- the field is being used "
                "for an ornament fact here, and it is mapped rather than refused because the "
                "slot that answers it exists and the exception is legible. Recorded as a "
                "finding: one token in 78 is in the wrong field."},
}

# A token here is NOT mappable onto anything this corpus records. Its
# preconditions stay UNEVALUABLE and are counted, never quietly passed.
UNMAPPABLE = {
    "crown-glass": "The corpus records no glass-manufacture fact. `glazing_assembly` records "
                   "divided-lite construction and storm/IGU build-up, not how the glass was "
                   "made. Closing this needs a slot, not a mapping.",
    "cylinder-glass": "As crown-glass: the corpus records the divided-lite construction of a "
                      "sash and never the glass in it, and the whole content of this token is "
                      "the glass.",
    "restoration-glass": "As crown-glass -- and this one names a modern product, which the "
                         "corpus has no place for at all.",
    "aluminium-sash": "No window_type variant records an aluminium frame; `casement-steel` is "
                      "the only framing material the slot names.",
    "art-glass-panel": "Leaded art glass is a Prairie School fact the ontology does not carry: "
                       "`special_window` records shapes (oriel, lunette, palladian), not "
                       "glazing treatments.",
    "pressed-metal": "No cladding or ornament variant records pressed metal. `cast-iron-front` "
                     "and the terracotta panels are the nearest, and both are different "
                     "materials with different weathering.",
    "soldered-flat-seam-metal": "The roof_material slot carries `standing-seam-metal` and "
                                "`corrugated-or-standing-seam-metal`; a soldered flat-seam roof "
                                "is a different assembly with a different minimum pitch, which "
                                "is exactly what the exception using it turns on.",
    "moulded-composite-slate": "`uniform-course-slate-or-imitation` records that a roof may be "
                               "an imitation and does not say of what. The exception's whole "
                               "argument is that a full-thickness moulded composite is "
                               "legitimate where a printed fibre-cement sheet is not, and that "
                               "distinction is not in the record.",
    "fibre-cement-slate": "As moulded-composite-slate, and the same exception needs both.",
    "timber-lintel": "No window_head_wood variant states a structural timber lintel; the "
                     "variants there are trim treatments (`flat-casing-head`, `backband-head`) "
                     "and say nothing about what spans the opening.",
    "side-hinged-door": "`garage_strategy` records where the vehicle bay is, never how its door "
                        "opens. Both exceptions using this token are about a garage door leaf.",
    "bi-fold-door": "As side-hinged-door: `garage_strategy` records the bay's position and "
                    "never the leaf's action, and a bi-fold leaf is the second half of the one "
                    "distinction both exceptions using it are drawn to make.",
    "continuous-low-roof": "A massing fact. `roof_form` records the roof's shape per volume and "
                           "nothing records a roof running continuously across house and "
                           "garage, which is the whole content of the token.",
    "narrow-lot-detached": "The corpus has no lot-width fact. `setback_rule` carries no "
                           "variants at all in any kit, and `street_relationship` distinguishes "
                           "party-walled from free-standing without stating a dimension.",
    "jettied-upper-storey": "A jetty is dimensioned by the `jetty-overhang` proportion pack and "
                            "is recorded in no slot, so there is nothing in a resolved kit to "
                            "read. Closing this is a slot question, not a mapping one.",
    "framed-chase": "The `chimney` slot's 39 variants say where a stack stands and what it "
                    "looks like; not one says what it is built of.",
    "brick-veneer-chase": "As framed-chase -- and these two are the pair a licence has to tell "
                          "apart.",
}

VERDICTS = ("holds", "fails", "undecidable", "unmappable")
# Statuses that say the tradition really is built this way.
_LIVE = ("canonical", "permitted", "atypical")


def _slot_record(resolved, sid):
    rec = (resolved or {}).get(sid) or {}
    return rec, [v for v in (rec.get("variants") or []) if v.get("id")]


def resolve(token, resolved_slots, declared=None):
    """Decide whether `token` holds for a style, given its RESOLVED kit.

    Returns (verdict, why). `declared` is an optional {slot: variant_id} the
    caller knows about the actual house -- a plan record's `declared` block --
    and it decides the question FOR ITS OWN SLOT, because the house is the thing
    the exception is about.

    IT DOES NOT SHORT-CIRCUIT THE AUTHORITY ORDER, and the first version did.
    A declared value used to return immediately from whichever of the token's
    slots the caller happened to name, so a plan declaring only
    `primary_cladding: smooth-stucco` on a style whose `construction_type` is
    canonically `braced-timber-frame` got a hard `fails` for `wood-frame` --
    telling the resolver MORE about the house made it answer WRONG, which is the
    worst possible shape for an optional input. A declared value is now folded in
    as that slot's verdict and the same most-decisive-first walk runs over the
    result. Found by the WP-8.4 adversarial audit; the same audit found the
    `partial` rule was skipped on this path too, so `thick-stucco` could return
    `holds` -- the one thing this module says it must never do.
    """
    # A SPEC MAY BE PASSED DIRECTLY, so `resolve_any` need not write its union into the
    # module-level table and pop it again -- that raced on the request path. A dict here is
    # a caller-owned spec and never a lookup; a string is a token as it always was.
    if isinstance(token, dict):
        spec, token = token, token.get("note") or "the union"
    else:
        if token in UNMAPPABLE:
            return "unmappable", UNMAPPABLE[token]
        spec = VOCABULARY.get(token)
        if spec is None:
            return "unmappable", ("%r is in neither VOCABULARY nor UNMAPPABLE; "
                                  "report the gap rather than adding a token" % token)

    # ONE WALK, MOST-DECISIVE SLOT FIRST. A slot the caller has DECLARED is decided by the
    # declaration (the house outranks the tradition for its own slot); every other slot is
    # decided by the resolved kit. Both feed the same authority-ordered walk below.
    per_slot, detail = [], []
    for sid, wanted in spec["slots"].items():
        got = (declared or {}).get(sid)
        got = got.get("variant") if isinstance(got, dict) else got
        if isinstance(got, str) and got:
            if got in wanted:
                per_slot.append("holds")
                detail.append("the record declares %s = %s" % (sid, got))
            else:
                per_slot.append("fails")
                detail.append("the record declares %s = %s, which is not %s" % (sid, got, token))
            continue
        rec, variants = _slot_record(resolved_slots, sid)
        if not variants:
            continue
        live = [v for v in variants if v.get("status") in _LIVE and v["id"] in wanted]
        canon_in = [v for v in variants if v.get("status") == "canonical" and v["id"] in wanted]
        canon_out = [v for v in variants if v.get("status") == "canonical" and v["id"] not in wanted]
        # A CANONICAL OUTRANKS A PERMITTED, and that is the difference between a decision and a
        # shrug. `jeffersonian-classicism` inherits a construction_type where EVERY variant is
        # merely permitted, so that slot cannot decide -- but its own cladding is canonically
        # Flemish-bond brick with clapboard FORBIDDEN, and reading a permitted
        # `beaded-clapboard` as "this might be a frame house" left a brick node undecided and
        # still receiving a sloped timber sill. What a style says CANONICALLY is what it is.
        if not live:
            per_slot.append("fails")
            detail.append("%s names none of %s outside a `forbidden`" % (sid, token))
        elif canon_in and not canon_out:
            per_slot.append("holds")
            detail.append("%s is canonically %s" % (sid, ", ".join(v["id"] for v in canon_in)))
        elif canon_out and not canon_in:
            per_slot.append("fails")
            detail.append("%s is canonically %s, none of which is %s"
                          % (sid, ", ".join(v["id"] for v in canon_out[:3]), token))
        elif canon_in and canon_out:
            # BOTH WAYS, AND THE SLOT MEANS IT. Canonical evidence on each side is a firm
            # answer -- `charleston-georgian` really was built in brick and in clapboard -- so
            # it STOPS the walk. A lower-authority slot must not overturn it: `prairie-school`
            # is canonically `roman-brick` AND `stucco-with-wood-banding`, and letting its
            # `platform-frame` construction_type have the last word returned `fails` for
            # `brick` on a Roman-brick house.
            per_slot.append("undecidable-firm")
            detail.append("%s is canonically both %s and %s"
                          % (sid, ", ".join(v["id"] for v in canon_in[:2]),
                             ", ".join(v["id"] for v in canon_out[:2])))
        else:
            # NO CANONICAL EITHER WAY -- the slot has only permitted or atypical variants, so
            # it has no firm opinion and the walk moves on. `jeffersonian-classicism` inherits
            # a construction_type in which every variant is merely permitted; its own cladding
            # is canonically Flemish-bond brick with clapboard forbidden, and that is the
            # answer.
            per_slot.append("undecidable-soft")
            detail.append("%s permits %s and states no canonical either way"
                          % (sid, ", ".join(v["id"] for v in live[:3])))
    why = "; ".join(detail) or (
        "no slot this token reads carries a variant on this style -- nine nodes state their "
        "construction in a prose `rule` with an empty variant list, and this is what that "
        "looks like from here")
    if not per_slot:
        return "undecidable", why
    # SLOT ORDER IS AUTHORITY ORDER, and the first slot that can answer decides. `slots` is
    # written most-decisive first -- `construction_type` states the wall assembly, where a
    # cladding is only evidence about it. Treating a disagreement between them as a
    # contradiction is what a flat combination does, and it is wrong in a way that matters:
    # `pueblo-revival` is `stucco-over-wood-frame` CANONICAL with `earth-toned-stucco` on the
    # face, so `wood-frame` HOLDS on the assembly and FAILS on the surface, and reading that as
    # "the record points both ways" made a decided question undecidable on 15 nodes. A render
    # is not a wall.
    for verdict in per_slot:
        if verdict == "undecidable-soft":
            continue                       # no firm opinion here; ask the next slot
        if verdict == "undecidable-firm":
            return "undecidable", why
        if verdict == "holds" and spec["strength"] == "partial":
            return "undecidable", ("%s carries a qualifier the corpus does not record, so this "
                                   "is the most that can be said: %s" % (token, why))
        return verdict, why
    return "undecidable", why


# ---------------------------------------------------------------------------
def resolve_any(tokens, resolved_slots, declared=None):
    """A LIST OF TOKENS IS A DISJUNCTION, and it has to be resolved as one.

    `grant_exception` reduces each token to a verdict and then combines, which is right for
    `holds` (any token holding grants the licence) and for `fails` (all failing refuses it),
    and WRONG in the middle: `paint-on-unpainted-brick`'s `english-cottage-vernacular` licence
    names `[solid-masonry-two-wythe, adobe, rammed-earth]` and that style is canonically `cob`
    AND `clay-lump` -- `adobe` covers the clay lump, `rammed-earth` covers the cob, each token
    alone says "canonically both, cannot decide", and the wall is CERTAINLY one of the three
    the licence names. Ten exceptions land in that gap; this resolves the union.

    PARTIAL TOKENS ARE EXCLUDED FROM THE UNION. Nine of the ten reach coverage only through
    `thick-stucco`, whose whole point is that the corpus records the render and not its depth,
    so confirming through it would launder the qualifier the token exists to preserve. The
    union is taken over EXACT tokens only, and a licence that needs a partial token to cover
    its slot stays unjudged -- which is the honest answer.

    Additive by construction: it is consulted only where the per-token pass reached no verdict,
    so it can turn an `undecidable` into a `holds` and can never change a `holds` or a `fails`.
    """
    exact = [t for t in tokens if t in VOCABULARY and VOCABULARY[t]["strength"] == "exact"]
    if len(exact) < 2:
        return None
    merged = {}
    for t in exact:
        for sid, wanted in VOCABULARY[t]["slots"].items():
            merged.setdefault(sid, [])
            merged[sid].extend(w for w in wanted if w not in merged[sid])
    union = {"slots": merged, "strength": "exact",
             "note": "the union of %s" % ", ".join(exact)}
    # RESOLVED DIRECTLY, NOT BY WRITING INTO THE MODULE-LEVEL TABLE. The first version put
    # the union under a sentinel key in `VOCABULARY`, resolved that key, and popped it in a
    # `finally`. This runs on `/api/plan/evaluate`, which FastAPI serves from a threadpool,
    # concurrently with the compose worker's own `plan_check` -- so two requests inside this
    # function at once resolved each other's union, or popped it out from under each other.
    # Both outcomes are silent: a licence GRANTED on another request's tokens, which is an
    # exception excusing a fault the corpus refuses, or the sentinel key leaking into the
    # user-visible `why` ("primary_cladding names none of __union__ ..."). Nothing raises.
    # `resolve()` takes a spec now, so there is no shared mutable state to race on.
    # Found by the WP-8.4 adversarial audit.
    verdict, why = resolve(union, resolved_slots, declared)
    if verdict != "holds":
        return None
    return "holds", ("the wall is one of %s, all of which this licence names: %s"
                     % (" or ".join(exact), why))




def _kit_variant_index():
    """slot id -> set of every variant id authored for it anywhere in kits/."""
    out = collections.defaultdict(set)
    for name in sorted(os.listdir(KITS)):
        if not name.endswith(".kit.json"):
            continue
        with open(os.path.join(KITS, name), encoding="utf-8") as fh:
            kit = json.load(fh)
        for sid, rec in (kit.get("slots") or {}).items():
            for v in (rec.get("variants") or []):
                if v.get("id"):
                    out[sid].add(v["id"])
    return out


def check_table():
    """Every mapped variant id must exist. Errors, never warnings: a token
    mapped onto an id nobody authors resolves `fails` for every style in the
    corpus, which is a licence silently revoked rather than a mapping."""
    errors = []
    index = _kit_variant_index()
    overlap = set(VOCABULARY) & set(UNMAPPABLE)
    if overlap:
        errors.append("token(s) in both VOCABULARY and UNMAPPABLE: %s" % sorted(overlap))
    for token, spec in sorted(VOCABULARY.items()):
        # No sentinel skip any more: `resolve_any` passes its union to `resolve()` as a
        # spec instead of installing it here, so nothing transient can be in this table --
        # which also means this loop can no longer be raced into skipping a real entry.
        if spec.get("strength") not in ("exact", "partial"):
            errors.append("%s: strength must be 'exact' or 'partial'" % token)
        if not (spec.get("note") or "").strip():
            errors.append("%s: every entry states its own reading" % token)
        if not spec.get("slots"):
            errors.append("%s: maps onto no slot -- it belongs in UNMAPPABLE" % token)
        for sid, wanted in (spec.get("slots") or {}).items():
            if sid not in index:
                errors.append("%s: slot %r is not bound in any kit" % (token, sid))
                continue
            for vid in wanted:
                if vid not in index[sid]:
                    errors.append("%s: %s/%s is not a variant any kit authors" % (token, sid, vid))
    for token, reason in sorted(UNMAPPABLE.items()):
        if len((reason or "").strip()) < 40:
            errors.append("%s: an unmappable token states WHY, at length" % token)
    return errors


def corpus_tokens():
    """token -> how many exceptions name it."""
    out = collections.Counter()
    for name in sorted(os.listdir(FAULTS)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(FAULTS, name), encoding="utf-8") as fh:
            rec = json.load(fh)
        for exc in (rec.get("exceptions") or []):
            # THE FIELD IS `granted_when`. WP-8.4 renamed it from `applies_when` on all 331
            # records and this reader was left on the old name, so it returned an EMPTY
            # Counter -- `--coverage` reported nothing and
            # tests/test_construction_scope.py::test_every_token_the_corpus_uses_is_in_the_table
            # computed `used - VOCABULARY - UNMAPPABLE` over an empty set and passed
            # vacuously, which is the guard-that-cannot-fail this corpus polices hardest,
            # inside the suite written to guard the table. Found by the WP-8.4 adversarial
            # audit. The assertion below makes the reader itself refuse to be silent.
            for t in ((exc.get("granted_when") or {}).get("construction") or []):
                out[t] += 1
    if not out:
        raise SystemExit(
            "construction_vocabulary.corpus_tokens() found NO tokens in faults/. Either the "
            "corpus stopped using `granted_when.construction` or this reader is on the wrong "
            "field name again -- it was, once. An empty result here makes every caller pass "
            "vacuously, so it is refused rather than returned.")
    return out


def main():
    errs = check_table()
    if "--verbose" in sys.argv:
        for token, spec in sorted(VOCABULARY.items()):
            print("%-28s %-8s %s" % (token, spec["strength"],
                                     ", ".join("%s(%d)" % (s, len(v))
                                               for s, v in spec["slots"].items())))
        print("\nUNMAPPABLE")
        for token, reason in sorted(UNMAPPABLE.items()):
            print("  %-28s %s" % (token, reason[:96]))
    if "--coverage" in sys.argv:
        used = corpus_tokens()
        unknown = sorted(set(used) - set(VOCABULARY) - set(UNMAPPABLE))
        unused = sorted((set(VOCABULARY) | set(UNMAPPABLE)) - set(used))
        print("tokens in faults/: %d over %d exception uses" % (len(used), sum(used.values())))
        print("  mapped     %d  (%d uses)" % (
            len([t for t in used if t in VOCABULARY]),
            sum(c for t, c in used.items() if t in VOCABULARY)))
        print("  unmappable %d  (%d uses)" % (
            len([t for t in used if t in UNMAPPABLE]),
            sum(c for t, c in used.items() if t in UNMAPPABLE)))
        if unknown:
            print("  UNKNOWN    %s" % unknown)
        if unused:
            print("  in the table but unused in faults/: %s" % unused)
    if errs:
        print("\nFAIL: %d error(s)" % len(errs))
        for e in errs:
            print("  " + e)
        return 1
    print("%d tokens mapped, %d recorded unmappable. Table is consistent with kits/."
          % (len(VOCABULARY), len(UNMAPPABLE)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
