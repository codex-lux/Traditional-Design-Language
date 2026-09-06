#!/usr/bin/env python3
"""compass.py — the aspect a room is lit from, and which way the plan's north points (WP-11.9).

WHAT THIS IS FOR. `docs/reports/tidewater-layout-diagnosis-2026-09-04.md` Part VI is a table of
twenty statements the corpus already makes and can execute none of. Four of them are compass
rules on room records — the library's north, the kitchen's east, the drawing room's south and
west, the closet's north or east — and the finding behind them is larger than four: ALL SIXTY room
records state an aspect in `daylight.orientation`, in words, and until this file nothing in the
tree read one. Sixty sentences, no readers.

THE READING IS AUTHORED, NOT PARSED. `daylight.aspect` carries the compass tokens beside the
prose and quotes the sentence it read; `check_rooms.py` holds that quotation against the record.
A regex over the prose was refused for the reason `build/hearths.py` records one layer over: four
different jobs share one syntax there. `larder` states a governing aspect ("NORTH, and it is not a
preference"); `terrace` states one CONDITIONED on a climate axis this checker does not have, and
its two branches point opposite ways; `breezeway` and `cross-passage` state an axis of DOORS
across the summer breeze, which is not an aspect for glass; and `garage` says "Any", which is an
answer and not a silence. A pattern cannot tell those apart. Twenty-five of the sixty answer with
something that is not a compass, and each says which in its own `note`.

PLAN NORTH. Ruled by Lucas, 5 September 2026: **plan-N IS true-N unless a bearing says otherwise**
— the convention `render_plan.py` has printed on the plate as "NORTH IS UP" since WP-2.4, made a
rule here. The ruling's cost was stated when it was taken and is honoured in `assumption()`: the
checker must STATE the assumption in every finding it makes, not merely hold it. A reader who is
told a library faces south deserves to know whether the record said so or whether this file
assumed it.

`site.street_bearing_deg` is the bearing that says otherwise. It states the compass bearing the
principal front faces; `context.entrance_faces` states which plan face is the front; the rotation
is the difference, and every plan face turns with it. Where a bearing is stated and the front is
NOT, the rotation is unknowable and every reading here is COULD NOT EVALUATE — taking the S
default in that one case would be an assumption stacked on an assumption, and it would silently
rotate a real house by whatever the difference happened to be.
"""
from __future__ import annotations

# Nominal bearings of the eight points, clockwise from north.
POINTS = {"N": 0.0, "NE": 45.0, "E": 90.0, "SE": 135.0,
          "S": 180.0, "SW": 225.0, "W": 270.0, "NW": 315.0}

# A face satisfies a token when its true bearing lies inside that token's own 45-degree sector.
# EDITORIAL. No source states a tolerance, and none is needed on an unrotated plan: with plan-N
# true-N every face lands exactly on a cardinal and this number never decides anything. It decides
# only under a stated bearing, where it is the coarseness of the eight-point compass the records
# themselves are written in, and nothing finer would be honest about a sentence that says "east".
SECTOR_TOL_DEG = 22.5

FACES = ("N", "E", "S", "W")


def _delta(a, b):
    """Smallest angle between two bearings, 0-180."""
    d = abs((a - b) % 360.0)
    return min(d, 360.0 - d)


def plan_north(plan):
    """Which way plan-up points on the ground, and whether the record said so.

    Returns a dict, always -- never None, because every caller has to print the assumption:
      bearing_deg   the true bearing of plan +y, or None where it cannot be known
      stated        True only where the record's own site data fixed it
      why           the sentence a finding quotes
    """
    site = plan.get("site") or {}
    ctx = plan.get("context") or {}
    b = site.get("street_bearing_deg")
    if b is None:
        return {"bearing_deg": 0.0, "stated": False,
                "why": "plan-N is read as true-N: this record states no site.street_bearing_deg, "
                       "and north is up on every plate this tree draws"}
    front = (ctx.get("entrance_faces") or "").upper()
    if front not in POINTS:
        return {"bearing_deg": None, "stated": True,
                "why": f"site.street_bearing_deg is {float(b):.0f} deg and context.entrance_faces "
                       f"is {ctx.get('entrance_faces')!r}: the bearing says which way the FRONT "
                       f"faces and nothing says which plan face the front is, so the rotation "
                       f"cannot be computed. Not a pass -- every aspect on this plan is unjudged"}
    rot = (float(b) - POINTS[front]) % 360.0
    return {"bearing_deg": rot, "stated": True,
            "why": f"plan-N bears {rot:.0f} deg true: the record states its front on plan-{front} "
                   f"and site.street_bearing_deg {float(b):.0f} deg, so the plan is turned "
                   f"{rot:.0f} deg from north"}


def assumption(north):
    """The one sentence every finding this file causes must carry. Ruled 5 Sep 2026: the
    convention is only honest if the reader is told it was applied."""
    return north["why"] + "."


def face_bearing(face, north):
    """The true bearing of a plan face, or None where plan north is unknown."""
    if north.get("bearing_deg") is None or face not in POINTS:
        return None
    return (POINTS[face] + north["bearing_deg"]) % 360.0


def face_token(face, north):
    """The eight-point token a plan face lands on, or None where plan north is unknown."""
    b = face_bearing(face, north)
    if b is None:
        return None
    return min(POINTS, key=lambda t: _delta(b, POINTS[t]))


def matches(face, token, north):
    """Does a plan face lie in `token`'s sector? Unrotated, this is plain equality."""
    b = face_bearing(face, north)
    return b is not None and _delta(b, POINTS[token]) <= SECTOR_TOL_DEG


def lit_faces(room):
    """The plan faces this room's DECLARED windows sit on.

    Declared, not drawn, and the layer follows from it: a window's `wall` is AUTHORED (a door's is
    solver output -- CLAUDE.md records the round-trip failure that established the difference), so
    this reads the record and belongs beside the other record-reading layers. WP-11.4's rule: ask
    what a check READS before choosing its layer. Whether the placement could seat those windows
    where the record put them is a DIFFERENT question and `plan_check`'s drawn layer already
    answers it (`drawn-window-off-the-placed-wall`).
    """
    out = []
    for w in (room.get("windows") or []):
        f = (w.get("wall") or "").upper()
        if f in FACES and f not in out:
            out.append(f)
    return out


def read(aspect, faces, north):
    """Hold a room's declared window walls against its type's authored aspect.

    Returns {"verdict": ..., "reason": str, ...}. FIVE verdicts, and four of them are not a pass:

      not_applicable  the record answered the orientation question with something that is not a
                      compass. A judged state, carrying the record's own note -- never a silence.
      unstated        the type record carries no `aspect` at all. Unjudged.
      unjudged        this plan cannot supply the reading: no declared window wall, or a stated
                      bearing whose rotation could not be resolved.
      avoided         a window sits on an aspect the record names as wrong.
      unwanted        no window sits on any aspect the record names as wanted.
      satisfied       evaluated and clear.
    """
    if not aspect:
        return {"verdict": "unstated",
                "reason": "this room type's record states no daylight.aspect, so its prose has "
                          "not been read into tokens. Unjudged, not passed"}
    if not aspect.get("applies"):
        return {"verdict": "not_applicable",
                "reason": aspect.get("note") or f"the record answers with \"{aspect['basis']}\"",
                "basis": aspect.get("basis")}
    if north.get("bearing_deg") is None:
        return {"verdict": "unjudged", "reason": north["why"]}
    if not faces:
        return {"verdict": "unjudged",
                "reason": "this room declares no window on any exterior wall, so it states no "
                          "aspect to be held to"}
    tokens = {f: face_token(f, north) for f in faces}
    avoid = [f for f in faces if any(matches(f, t, north) for t in (aspect.get("avoid") or []))]
    prefer = aspect.get("prefer") or []
    wanted = [f for f in faces if any(matches(f, t, north) for t in prefer)]
    if avoid:
        return {"verdict": "avoided", "faces": avoid, "tokens": tokens,
                "avoid": aspect.get("avoid"), "basis": aspect["basis"],
                "strength": aspect.get("strength") or "preferred"}
    if prefer and not wanted:
        return {"verdict": "unwanted", "faces": faces, "tokens": tokens,
                "prefer": prefer, "basis": aspect["basis"],
                "strength": aspect.get("strength") or "preferred"}
    return {"verdict": "satisfied", "faces": faces, "tokens": tokens,
            "basis": aspect["basis"], "strength": aspect.get("strength") or "preferred"}
