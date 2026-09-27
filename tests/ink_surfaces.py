"""ink_surfaces.py — per-surface readers for the Phase 14 census (WP-14.1).

Each reader takes what a surface EMITS (an SVG string) and returns the drawn geometry in the
surface's own model units, through the frame the surface states about itself. It reads nothing
the renderer computed on the way: a reader that took a renderer's own scale would be checking the
renderer against itself. Where a reader needs the RECORD to compare against, it reads the record
through the engine the corpus publishes (`proportion_engine`), never through the renderer.
"""
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

import inkread as IR  # noqa: E402


def _mod(name):
    return modcache.load(name, os.path.join(ROOT, "build", name + ".py"))


# ------------------------------------------------------------------ the profile plates
# The profile kinds whose outermost ink at the member's own mid-height IS its recorded face:
# the square steps, and the half rounds (whose crown is at mid-height by construction). A quarter
# or a cyma meets its face at one END, so its mid-height extent says nothing about the record and
# is not asked here.
FACE_AT_MID = frozenset((
    "fillet", "listel", "fascia", "plinth", "corona", "abacus", "flat", "dentil", "modillion",
    "mutule", "triglyph", "metope", "bevel", "other", "torus", "astragal", "bead"))
CURVED = frozenset((
    "ovolo", "quarter-round", "echinus", "cavetto", "apophyge", "congé", "cyma-recta",
    "cyma-reversa", "ogee"))
UNCONSTRUCTED = frozenset(("volute", "acanthus"))


# HOW CLOSE TWO HEIGHTS MUST BE TO BE ONE BOUNDARY. The plate prints its path to a thousandth of
# a pixel, so a vertex read back is off its model value by up to 0.0005 px / px_per_in -- 5.7e-6 in
# on a plate drawn at 87 px/in. The census's first run used 1e-6, which is TIGHTER than the print
# quantum, and so called an ovolo that is drawn as an arc "drawn straight" on thirty plates: the
# instrument reporting its own rounding as a defect in the drawing. 0.001 in is two orders above
# the quantum at every scale these plates are drawn at (`ProfilePlate` asserts that) and two below
# the thinnest member any pack states.
EPS_IN = 0.001


class ProfilePlate:
    """One committed or freshly rendered moulding-profile plate, read back.

    `outline` is the filled silhouette path, `commands` its absolute commands and `model(pt)` the
    frame's own conversion to (inches out from the axis, inches up the stack)."""

    def __init__(self, svg):
        self.svg = svg
        self.ink = IR.Ink(svg)
        self.plate = self.ink.frame(proj="profile")
        fills = [it for it in self.ink.select("path")
                 if (it.style.get("fill") or "none") not in ("none", "transparent")]
        self.outline = fills[0] if len(fills) == 1 else None
        self.n_outlines = len(fills)
        if self.plate:
            # the premise EPS_IN rests on, checked on every plate read rather than assumed
            assert 0.0005 / self.plate["px_per_in"] < EPS_IN / 10.0, self.plate
        self.text = " ".join((t or "") for t, _p, _it in self.ink.texts())
        # footer lines wrap at a word boundary; a figure read across the wrap must still read
        self.flat_text = re.sub(r"\s+", " ", self.text)

    def model(self, pt):
        return IR.to_model(self.plate, pt[0], pt[1])

    def points(self, n=48, lines=True):
        return [self.model(p) for p in self.outline.points(n=n, lines=lines)] if self.outline else []

    def naked(self):
        return self.plate["at_origin_in"][0]

    def segments_in_model(self):
        """The outline's absolute commands with their END POINTS in model inches, in order, each
        paired with its start point: [(kind, (u0, v0), (u1, v1))]."""
        out, cur, start = [], None, None
        for c in self.outline.cmds or []:
            k = c[0]
            if k == "M":
                cur = start = self.model(IR.apply(self.outline.ctm, c[1], c[2]))
                continue
            if k == "Z":
                end = start
            else:
                end = self.model(IR.apply(self.outline.ctm, c[-2], c[-1]))
            out.append((k, cur, end))
            cur = end
        return out

    def segments_within(self, lo, hi, kinds=("A", "C", "Q")):
        """The outline segments of the given kinds lying wholly inside the band [lo, hi] inches up
        the stack, to EPS_IN. A member's own curve starts and ends ON its boundaries, so the band
        has to be closed at both ends and read at the print precision, not at float precision."""
        return [s for s in self.segments_in_model()
                if s[0] in kinds and lo - EPS_IN <= s[1][1] <= hi + EPS_IN
                and lo - EPS_IN <= s[2][1] <= hi + EPS_IN]

    def extent_at(self, v, n=64):
        """The outermost ink at height v (inches up the stack): the largest u where the densified
        silhouette crosses the horizontal line. None where nothing crosses it."""
        best = None
        for sub in self.outline.subpaths(n=n, lines=True):
            pts = [self.model(p) for p in sub]
            for (u0, v0), (u1, v1) in zip(pts, pts[1:]):
                if (v0 - v) * (v1 - v) <= 0 and v0 != v1:
                    u = u0 + (u1 - u0) * (v - v0) / (v1 - v0)
                    best = u if best is None else max(best, u)
        return best


def profile_record(pack_id, assembly_id, module_in):
    """What the record says the plate should show: the resolved pack's members for this
    assembly with their dimensioned heights, and whether the RAW record publishes each member's
    `projection_parts` -- a figure, as against a key that is absent or written null (WP-14.2).
    Read off the record and never off the engine, so the census cannot inherit a defect in how
    the engine carries a missing figure: that is the defect WP-14.2 removed."""
    PE = _mod("proportion_engine")
    pack = PE.resolve(pack_id)
    # The stack that HOLDS the assembly (WP-14.2): an overlay drawn with its own whole entablature
    # has no cornice in its default stack, and its cornice plate draws the inherited triplet's --
    # a plate's frame states the assembly's height in the stack it was drawn in, so read that one.
    include = PE.stack_for(pack)
    if assembly_id not in include and assembly_id in PE.stack_for(pack, entablature="triplet"):
        include = PE.stack_for(pack, entablature="triplet")
    dim = PE.dimension(pack, module_in=module_in, include=include)
    members = next((a["members"] for a in dim["assemblies"] if a["id"] == assembly_id), [])
    raw = {m["id"]: m for m in ((pack.get("assemblies") or {}).get(assembly_id) or {}).get("members", [])}
    side = bool((pack.get("assemblies") or {}).get(assembly_id, {}).get("sums_check") is False)
    return {
        "pack": pack, "dim": dim, "members": members, "raw": raw, "side_by_side": side,
        "lower_diameter_in": dim["totals"]["lower_diameter_in"],
        "owner": PE.assembly_owner(pack_id, assembly_id),
        "published": {mid: (r.get("projection_parts") is not None) for mid, r in raw.items()},
    }
