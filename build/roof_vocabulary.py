#!/usr/bin/env python3
"""roof_vocabulary.py -- which of the roof layer's forms a kit's `roof_form` row is (WP-16.9, B1).

Lucas's answer B1 (30 Sep 2026): a plan record that names no roof form takes, after its own
declaration and before its massing's default, the canonical `roof_form` of its style's resolved kit,
"through a closed table onto the forms the roof layer draws". This is that table.

A CLOSED TABLE, on `build/construction_vocabulary.py`'s precedent. Every `roof_form` variant id the
corpus uses is here, in every status, mapped onto one of the seven forms `build/roof.py` draws or
recorded as unmappable (`None`) WITH A REASON. A form the roof layer does not draw -- a mansard, a
shed, a flat roof, an asymmetric saltbox section -- is said, never guessed into the nearest form it
does draw; and an id naming a gable without saying which way it runs is not given an orientation
nobody stated. Each entry quotes the record it reads, and `build/check_threshold.py` holds every
quote to its file and the table total over the corpus, so `TOTAL_CHECKS` does not move.

Drafted by a reading agent over every row and every style record that uses an id, and checked by a
second, independent one. The answers it executes are recorded in
`oq/the-roof-is-drawn-side-gabled-whatever-the-style-says`, and the table's history in WP-16.9's
report.
"""
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The forms `build/roof.py` draws (`main_roof`), and nothing else.
FORMS = ('gable', 'side-gable', 'front-gable', 'hip', 'gable-on-hip', 'cross-gable', 'gambrel')

# variant id -> (form or None, why, (file, field, verbatim text the entry reads))
TABLE = {
    "brisee-mansard": (None,
        "A brisee (mansard) roof: steep below, shallow above, on every pavilion. roof.py draws no mansard and says so; a gambrel is not a mansard, because a gambrel has gable ends and a mansard runs its double pitch round all four sides.",
        ("kits/french-baroque.kit.json", "slots.roof_form.variants[0].note",
         "The brisee or mansard roof, steep below and shallow above, preserving the habitable attic while cutting the silhouette.' Each pavilion carries its own independently terminated roof mass")),
    "broad-frontal-block-low-or-hidden-roof": (None,
        "The id names a massing (a broad frontal block) and a roof condition (low or hidden), and no roof form. Its row carries no note; the style record says the roof is low or concealed behind a parapet, which roof.py cannot draw.",
        ("styles/elizabethan.json", "constraints[3].statement",
         "Roof pitch is low or concealed behind a balustraded or strapwork parapet; a dominant visible roof slope belongs to Tudor or to the vernacular, not here.")),
    "catslide": (None,
        "A catslide carries one slope down lower than the other, so the section is asymmetric. roof.py draws symmetric sections only.",
        ("kits/shingle-style.kit.json", "slots.roof_form.variants[2].note",
         "The long rear catslide, taken from seventeenth-century New England to bring the roof to the ground.")),
    "catslide-saltbox": (None,
        "The row names the asymmetrical section itself. roof.py draws symmetric sections only.",
        ("kits/georgian-colonial-american.kit.json", "slots.roof_form.variants[7].note",
         "An asymmetrical section under a symmetrical front is a contradiction.")),
    "cross-gable": ("cross-gable",
        "The id is the roof layer's own form name, and its rows describe a gabled roof crossed by one or more gables. roof.py draws the simplest member of that class.",
        ("kits/tudor-revival.kit.json", "slots.roof_form.variants[0].note",
         "one or more prominent front-facing cross-gables of unequal size")),
    "cross-gable-multi-gable": ("cross-gable",
        "The row names the cross-gable-victorian skeleton, a multi-gabled mass; the drawn cross-gable is its simplest case.",
        ("kits/neo-eclectic.kit.json", "slots.roof_form.variants[0].note",
         "The two-storey multi-gabled mass is the style's default skeleton (massing_affinities, cross-gable-victorian, common)")),
    "cross-gable-steep": ("cross-gable",
        "Intersecting cross-gables; 'steep' is a pitch, which roof.py reads from the style's own pitch constraint, not from the form.",
        ("kits/gothic-revival-british.kit.json", "slots.roof_form.variants[0].note",
         "the intersecting gabled block is the workhorse form")),
    "flat": (None,
        "A flat roof behind a parapet. roof.py draws no flat roof, and a flat roof is not a hip.",
        ("styles/pueblo-revival.json", "defining_characteristics[0]",
         "Flat roof drained through projecting canales behind an irregular, gently undulating parapet")),
    "flat-or-low-roof-behind-gable-screen": (None,
        "A flat or low roof behind a gable that is a screen, not a roof end. roof.py draws no flat roof and no screen gable. front-gable would draw the gable as the roof's own end, which the same kit forbids by name (front-gable-roof-end).",
        ("kits/dutch-urban-gable-house.kit.json", "slots.roof_form.variants[0].note",
         "The gable is a SCREEN IN FRONT OF THE ROOF, not the end of it.")),
    "flat-parapet": (None,
        "A flat roof behind a parapet. roof.py draws no flat roof, and a flat roof behind a parapet is not a hip.",
        ("kits/spanish-colonial-american.kit.json", "slots.roof_form.variants[0].note",
         "New Mexico, Texas, Arizona: round beams behind a parapet.")),
    "front-gable": ("front-gable",
        "The rows turn the gable to the road or street. roof.py's front-gable draws the ridge on y with gable ends S and N.",
        ("kits/greek-revival-northern.kit.json", "slots.roof_form.variants[0].note",
         "rotating the gable to the road is this variant's own demographic bulk")),
    "front-gable-roof-end": ("front-gable",
        "Both rows define it as a roof that genuinely ends in a gable turned to the entered face, which is what front-gable draws. Both rows forbid it.",
        ("kits/cape-dutch.kit.json", "slots.roof_form.variants[1].note",
         "'the gable, not the eave, is the composed and entered face' -- a roof genuinely ending in a gable")),
    "front-gable-single-entered-gable-end": ("front-gable",
        "A narrow house whose single gable end is the entered front, which is what front-gable draws. The one row forbids it.",
        ("kits/jacobean.kit.json", "slots.roof_form.variants[1].note",
         "germanic-vernacular's narrow, single-gable-fronted urban house logic")),
    "gable": (None,
        "AMENDED TO NULL. roof.py's bare gable takes ridge_axis y, so it is drawn exactly as a front gable (gable ends S and N): mapping to it assigns the front orientation. Of the id's four canonical nodes, only shotgun-house's record states front. craftsman's row says front- OR side-facing; craftsman-bungalow's own record says both subtypes are the same massing with the ridge rotated, and that the street alternates them; california-bungalow's record states no orientation. So on three of four canonical nodes the drawn orientation is roof.py's convention, not the record's. That is a guess by the rule, and keeping the literal form name gable does not change what is drawn. Cost: shotgun-house loses a front gable its own words support. The honest fix for it is its own kit naming front-gable, or a writer-keyed entry, not this id's mapping. On the composer path its massing (shotgun) already falls back to front-gable. For FORBIDDEN rows (prairie-school), the id bans a gabled principal roof of every orientation. Neither null nor gable expresses that, so a reader of forbidden rows needs {gable, side-gable, front-gable} here, not a single form.",
        ("kits/craftsman.kit.json", "slots.roof_form.variants[0].note",
         "Low-pitched gabled roof, front- or side-facing.")),
    "gable-front": ("front-gable",
        "The id names the orientation: the gable-fronted block. The row carries no note; the style record describes the main block as gable-fronted.",
        ("styles/american-farmhouse-vernacular.json", "description.long",
         "a taller gable-fronted block with a lower side-gabled wing")),
    "gable-front-and-wing": (None,
        "The id names a two-volume L: a gable-fronted block with a side-gabled wing. roof.py draws one rectangle under one roof, and its cross-gable is the opposite hierarchy (a dominant side-gable with a small centred cross gable that no elevation shows).",
        ("kits/minimal-traditional.kit.json", "slots.roof_form.variants[2].note",
         "The single-storey version with a projecting entry or living-room gable, the one compositional move the style allows itself")),
    "gable-on-hip": ("gable-on-hip",
        "The id is the roof layer's own form name. No row makes it canonical, so B1 is not affected.",
        ("kits/french-eclectic.kit.json", "slots.roof_form.variants[1].note",
         "A cross-gable dominant enough to read as a gable-on-hip crosses c01's 25 percent front-elevation-width cap and converts the house to Tudor Revival.")),
    "gable-pedimented-temple-front": ("front-gable",
        "A temple front is the pedimented gable end turned to the front, which is front-gable's geometry. The row derives it from the temple-front-with-wings massing affinity.",
        ("kits/new-classical.kit.json", "slots.roof_form.variants[1].note",
         "Implied by the temple-front-with-wings massing affinity.")),
    "gabled-with-repeated-shaped-gables": (None,
        "The id's content is the set of shaped gables repeated along a broad front, which no roof.py form draws. The two nearest forms each draw something the record refuses: cross-gable draws a single gable on the front, which the style's own hard constraint jacobean.c01 calls a Victorian move, and side-gable drops the repeated gables altogether.",
        ("styles/jacobean.json", "defining_characteristics[0]",
         "Shaped and scrolled gables of Netherlandish derivation, usually capped by a small pediment, ranged symmetrically along a front or crowning end pavilions")),
    "gambrel": ("gambrel",
        "Two pitches per side, steep below and shallow above, rising to a ridge: roof.py's gambrel.",
        ("styles/dutch-colonial-revival.json", "defining_characteristics[0]",
         "Gambrel roof - two pitches per side, steep below and shallow above - as the primary and defining massing element")),
    "hip": ("hip",
        "Hipped on all four sides at one pitch: roof.py's hip.",
        ("kits/french-eclectic.kit.json", "slots.roof_form.variants[0].note",
         "Hipped roof of equal pitch on all four sides with no front gable.")),
    "hip-behind-parapet": ("hip",
        "The form the row names is a hip; the parapet that conceals it stands on the wall and is not a roof form. An orthographic elevation draws the hip's silhouette at its true height; 'not the composed feature' is a statement about what is seen from the street.",
        ("kits/gothic-revival-british.kit.json", "slots.roof_form.variants[1].note",
         "A Palladian hip roof concealed behind a parapet is the opposite of everything this style is built to reject")),
    "hip-behind-parapet-invisible": ("hip",
        "As hip-behind-parapet: the form named is a hip, and the invisibility is the parapet's.",
        ("kits/queen-anne-british.kit.json", "slots.roof_form.variants[2].note",
         "an invisible, parapet-concealed Palladian roof contradicts this style's own steep, visible, chimney-topped tile roof")),
    "hip-roof-classical-composition": ("hip",
        "The row says the classical precedent of the five-part-palladian massing is hipped.",
        ("kits/new-classical.kit.json", "slots.roof_form.variants[0].note",
         "Implied by the canonical five-part-palladian massing, whose classical precedent is characteristically hipped.")),
    "hip-symmetrical-quotation": ("hip",
        "A visible hipped roof, symmetrical, quoting the 1700 house.",
        ("kits/queen-anne-british.kit.json", "slots.roof_form.variants[1].note",
         "symmetrical and hipped, quoting the 1700 house directly")),
    "hipped": ("hip",
        "The row contrasts hipped roofs with gabled ones; the form it forbids is a hip.",
        ("kits/jacobean.kit.json", "slots.roof_form.variants[2].note",
         "Baroque roofs are hipped behind balustrades; Jacobean roofs are gabled.")),
    "hipped-thatch-with-applied-gable-screen": ("hip",
        "The row reads the roof as hipped: a continuous eave round the building, with the gable a screen through the eave and not a roof end. The screen is a wall element and is not drawn.",
        ("kits/cape-dutch.kit.json", "slots.roof_form.variants[0].note",
         "a continuous eave line around the building is a hip-roof condition")),
    "low-gable": ("side-gable",
        "The id says gable without saying which way it runs. The canonical row (ranch-style) carries no note, and its style record supports a ridge parallel to the street: a long unbroken ridge of 40 ft or more, on a house that presents a long low band to the street. 'Low' is a pitch, which roof.py reads from the style's constraint.",
        ("styles/ranch-style.json", "defining_characteristics[1]",
         "Low-pitched hipped or gabled roof, 3:12 to 5:12, with an eave of 18 to 36 in and a long unbroken ridge")),
    "low-hip": ("hip",
        "A hip; 'low' is a pitch.",
        ("kits/gothic-revival-american.kit.json", "slots.roof_form.variants[1].note",
         "Suppresses the gable, which the style's own defining_characteristics make the governing compositional element.")),
    "low-hip-behind-balustrade": ("hip",
        "The style's hard constraint states the form outright: hipped, 5:12 to 8:12, concealed behind a balustrade. The form is a hip; the balustrade is the elevation's, and 'not visible from a normal standing viewpoint' is a statement about a view from the street, not about an orthographic elevation (roof.py's own ruling on the long face of a gable, 27 Aug 2026).",
        ("styles/french-neoclassical.json", "constraints[0].statement",
         "Pitch 5:12 to 8:12, hipped, concealed behind a balustrade or blocking course at least 1/16 the wall height.")),
    "low-hip-long-unbroken-ridge": ("hip",
        "A low hip with a long ridge.",
        ("kits/ranch-style.kit.json", "slots.roof_form.variants[0].note",
         "Roof ridge running unbroken for 40 ft or more at a pitch under 5:12")),
    "low-hip-suppressed": ("hip",
        "A low hip, visually suppressed by the cornice. The row carries no note; the style record names a low hip.",
        ("styles/italianate-american.json", "description.short",
         "a low-hipped, wide-eaved, heavily bracketed villa or townhouse")),
    "low-roof-behind-balustrade": (None,
        "The id names a low roof hidden behind a balustrade, and no form: which roof stands behind the balustrade is not said by the id, whether a record makes it canonical (beaux-arts-american) or forbids it, as beaux-arts-french does for the Neoclassical parent's concealment rather than for a form.",
        ("kits/beaux-arts-french.kit.json", "slots.roof_form.variants[1].note",
         "the invisible roof behind a balustrade is Neoclassical")),
    "mansard": (None,
        "A double-pitched roof running round all elevations. roof.py draws no mansard and says so; a gambrel has two gable ends and is not a mansard.",
        ("styles/second-empire.json", "defining_characteristics[0]",
         "A mansard roof, dual-pitched with a steep lower slope of 65 to 80 degrees, forming a full habitable storey on all elevations")),
    "mansard-block": (None,
        "A mansard crowning a block as an occupiable attic. roof.py draws no mansard.",
        ("kits/beaux-arts-french.kit.json", "slots.roof_form.variants[0].note",
         "the mansard returns as a fully occupiable attic and as the device that gives an otherwise flat-topped block a silhouette")),
    "mansard-neo": (None,
        "The 1965-1980 neo-mansard, a mansard used to conceal bulk. roof.py draws no mansard.",
        ("kits/neo-eclectic.kit.json", "slots.roof_form.variants[1].note",
         "The 1965-1980 neo-mansard subtype, a device for concealing a second storey or apartment bulk")),
    "multi-gable-unequal-width": ("cross-gable",
        "A dominant gable with subordinate gables of unequal width. The row carries no note; the style record states the silhouette hierarchy. roof.py's cross-gable is a dominant ridge with one lower, narrower cross gable.",
        ("styles/gothic-revival-american.json", "proportional_system.governing_logic",
         "a dominant gable, subordinate gables of unequal width, and a chimney group that completes the outline against the sky")),
    "par-y-nudillo": (None,
        "The id names a timber construction (tie-beam, rafters and collar as one assembly, with the ceiling and the roof one object), not the roof's external form. No row states whether its ends are gabled or hipped, or which way the ridge runs.",
        ("kits/mudejar.kit.json", "slots.roof_form.variants[0].note",
         "Tie-beam, rafters and collar as one assembly, boarded and worked into an interlace of small timbers (lazo). The ceiling and the roof are the same object.")),
    "picturesque-roof-intersection": ("cross-gable",
        "The row defines it as two roofs of unequal ridge height meeting on the main block, and that is what roof.py's cross-gable draws (a lower cross ridge meeting the main ridge).",
        ("kits/georgian-colonial-american.kit.json", "slots.roof_form.variants[10].note",
         "Two roofs of unequal ridge height meeting on the main block.")),
    "pyramidal": (None,
        "A pyramidal roof comes to one apex over a square plan; roof.py's hip draws a ridge of length W-D. chateauesque's row is conditioned on conical roofs on round towers, which are not the main roof and are not drawn.",
        ("kits/folk-victorian.kit.json", "slots.roof_form.variants[2].note",
         "The pyramidal-cottage massing affinity.")),
    "saltbox": (None,
        "An asymmetric section: the ridge set forward and one slope carried down over a rear lean-to. roof.py draws symmetric sections only.",
        ("kits/saltbox-colonial.kit.json", "slots.roof_form.variants[0].note",
         "a continuous roof plane over two full front storeys and a one-storey rear lean-to, ridge set forward at 35-45% of plan depth")),
    "shallow-gable": (None,
        "The id says gable without saying which way it runs, and nothing the row or the style record says supports either orientation: 'shallow gabled roof', and the row carries no note. 'Shallow' is a pitch.",
        ("styles/italianate-american.json", "defining_characteristics[0]",
         "Low-pitched hipped or shallow gabled roof, 3:12 to 5:12, with the roof visually suppressed")),
    "shed": (None,
        "A single-pitch roof. roof.py draws none.",
        ("kits/georgian-colonial-american.kit.json", "slots.roof_form.variants[9].note",
         "No period existence on a main block.")),
    "side-gable": ("side-gable",
        "The ridge runs the long dimension and the house presents its long eave to the approach: roof.py's side-gable.",
        ("kits/new-england-colonial.kit.json", "slots.roof_form.variants[0].note",
         "Ridge runs the long dimension; the defining_characteristics record this outright.")),
    "simple-dominant-gable": (None,
        "The id says gable without saying which way it runs, and its row (a direct quote of the defining characteristic) states a hierarchy, not an orientation.",
        ("kits/modern-farmhouse-traditional.kit.json", "slots.roof_form.variants[0].note",
         "Simple dominant gable forms with minimal cross-gabling and a legible single roof hierarchy")),
    "steep-dominant-roofscape": (None,
        "The id names a proportion (a roof as tall as the wall) and a roofscape (towers, lucarnes, chimneys), and no form.",
        ("kits/french-renaissance-chateau.kit.json", "slots.roof_form.variants[0].note",
         "The roof is as tall as the wall")),
    "steep-gable": (None,
        "The id says gable without saying which way it runs, and the row's objection is the PITCH ('steep'), which is not a form.",
        ("kits/italianate-american.kit.json", "slots.roof_form.variants[2].note",
         "Contradicts the defining low-pitched, suppressed roof; that is Gothic Revival's territory (distinguished_from).")),
    "steep-gabled-cross-gable": ("cross-gable",
        "Intersecting gabled volumes (cross-gable-victorian canonical, Bedford Park). 'Steep' is a pitch.",
        ("kits/queen-anne-british.kit.json", "slots.roof_form.variants[0].note",
         "cross-gable-victorian canonical (Bedford Park)")),
    "steep-tower-and-gable-roofscape": (None,
        "A roofscape organised round a dominant tower that must rise a full storey above the main ridge. roof.py draws no tower, and the row names no main-roof form or ridge direction.",
        ("kits/scottish-baronial.kit.json", "slots.roof_form.variants[0].note",
         "The dominant tower must rise at least one full storey above the main ridge (soft constraint c04).")),
    "structural-gable-roof-end": (None,
        "The row says the gable is the real end of the roof (not a screen), and says nothing about which way the ridge runs. The style record puts the canonical farm range's long side to the approach and the town houses' gables to the street, so the words support no single orientation.",
        ("kits/flemish-vernacular.kit.json", "slots.roof_form.variants[0].note",
         "is genuinely the end of a roof rather than a screen in front of one")),
    "suspended-ceiling-below-separate-roof": (None,
        "The id names a construction (a ceiling hung below a separate roof), not a roof form.",
        ("kits/mudejar.kit.json", "slots.roof_form.variants[1].note",
         "a suspended ceiling below a separate roof is a different tradition.")),
}


def form_of(variant_id):
    """The roof layer's form for a `roof_form` row, or None where the table records it as a form
    the roof layer does not draw -- or does not carry the id at all, which `check_table` fails."""
    e = TABLE.get(variant_id)
    return e[0] if e else None


def _at(doc, field):
    """The value at a dotted path with [index] steps, or None."""
    cur = doc
    for part in re.findall(r"[^.\[\]]+|\[\d+\]", field or ""):
        if part.startswith("["):
            i = int(part[1:-1])
            cur = cur[i] if isinstance(cur, list) and i < len(cur) else None
        else:
            cur = cur.get(part) if isinstance(cur, dict) else None
        if cur is None:
            return None
    return cur


def _words(s):
    return " ".join(str(s or "").split())


def corpus_ids(root=ROOT):
    """Every `roof_form` variant id any kit file carries, in any status. Enumerated with
    `git ls-files`, never by walking the directory."""
    files = subprocess.run(["git", "-C", root, "ls-files", "kits/*.kit.json"], capture_output=True,
                           text=True, check=True).stdout.split()
    ids = set()
    for rel in files:
        with open(os.path.join(root, rel), encoding="utf-8") as fh:
            doc = json.load(fh)
        slots = doc.get("slots") if isinstance(doc.get("slots"), dict) else doc
        for v in ((slots.get("roof_form") or {}).get("variants") or []):
            if isinstance(v, dict) and v.get("id"):
                ids.add(v["id"])
    return ids


def check_table(root=ROOT):
    """Errors: an id in use and not in the table, an id in the table nobody uses, a form the roof
    layer does not draw, and a quote not found verbatim at its field."""
    errors = []
    used = corpus_ids(root)
    for vid in sorted(used - set(TABLE)):
        errors.append(f"roof_form row '{vid}' is used by a kit and is not in roof_vocabulary.TABLE")
    for vid in sorted(set(TABLE) - used):
        errors.append(f"roof_vocabulary.TABLE carries '{vid}', which no kit uses")
    for vid, (form, why, (rel, field, text)) in sorted(TABLE.items()):
        if form is not None and form not in FORMS:
            errors.append(f"'{vid}' maps to '{form}', which the roof layer does not draw")
        if not why:
            errors.append(f"'{vid}' carries no reason")
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            errors.append(f"'{vid}' quotes {rel}, which does not exist")
            continue
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        got = _at(doc, field)
        if _words(text) not in _words(got if isinstance(got, str) else json.dumps(got, ensure_ascii=False)):
            errors.append(f"'{vid}' quotes {rel} {field} and the text is not there: {text[:80]!r}")
    return errors
