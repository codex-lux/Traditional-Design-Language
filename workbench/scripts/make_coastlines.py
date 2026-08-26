#!/usr/bin/env python3
"""Generate the map's coastline modules, at three levels of detail.

The workbench's atlas is an SVG plate with no tile server behind it, so the only thing
that can make a zoomed-in coastline sharper is more points. Until now there was one
outline — Natural Earth 110m, simplified at 0.55 degrees, 888 points — and zooming past
about ten degrees of longitude magnified its corners into visible facets. A vector that
does not gain detail as it grows is a raster with extra steps.

So: three tiers, generated from three Natural Earth resolutions, and the map loads the
one its current view can actually show.

    coarse   110m, RDP 0.35 deg   eagerly imported, drawn at every scale first
    medium    50m, RDP 0.06 deg   fetched when the view narrows past MEDIUM_AT
    fine      10m, RDP 0.012 deg  fetched when the view narrows past FINE_AT

The finer two are separate modules so Vite splits them into their own chunks: a reader
who never zooms never pays for them, and a reader who does pays once.

INPUT is world-atlas@2 (https://github.com/topojson/world-atlas), which repackages
Natural Earth's public-domain `land` layer as TopoJSON. Fetch it with

    npm pack world-atlas@2.0.2 && tar xzf world-atlas-2.0.2.tgz

and point --src at the resulting `package/` directory. Nothing here is hand-edited, and
nothing here is corpus data: a coastline is furniture, the same as the gazetteer beside
it, and may not migrate into styles/*.json as a measured fact.

TopoJSON is decoded in the standard library — the arcs are delta-encoded integers with a
scale and a translate, which is two lines of arithmetic, and taking a dependency to do it
would put a build-time package between this repo and a drawing.
"""
import argparse
import json
import math
import os

# Tier name → (source file, RDP tolerance in degrees, coordinate decimals).
TIERS = [
    ('coarse', 'land-110m.json', 0.35, 2),
    ('medium', 'land-50m.json', 0.06, 3),
    ('fine', 'land-10m.json', 0.012, 3),
]

# A ring smaller than this many square degrees is dropped: at the tier's own tolerance it
# would be a speck of three points, and 10m land carries thousands of them. Scaled per
# tier so the fine tier keeps islands the coarse tier never had.
MIN_AREA = {'coarse': 0.5, 'medium': 0.05, 'fine': 0.004}


def decode(topo, obj_name):
    """TopoJSON → list of rings, each a list of (lon, lat)."""
    tr = topo['transform']
    sx, sy = tr['scale']
    tx, ty = tr['translate']
    arcs = []
    for arc in topo['arcs']:
        x = y = 0
        out = []
        for dx, dy in arc:
            x += dx
            y += dy
            out.append((x * sx + tx, y * sy + ty))
        arcs.append(out)

    rings = []

    def ring_for(indexes):
        pts = []
        for i in indexes:
            a = arcs[~i][::-1] if i < 0 else arcs[i]
            pts.extend(a[1:] if pts else a)
        return pts

    def walk(geom):
        t = geom.get('type')
        if t == 'GeometryCollection':
            for g in geom['geometries']:
                walk(g)
        elif t == 'Polygon':
            for r in geom['arcs']:
                rings.append(ring_for(r))
        elif t == 'MultiPolygon':
            for poly in geom['arcs']:
                for r in poly:
                    rings.append(ring_for(r))
    walk(topo['objects'][obj_name])
    return rings


def unwrap(ring):
    """Split a ring at the antimeridian, so nothing is drawn across the whole map.

    A few Natural Earth rings — Eurasia, Antarctica, a handful of Pacific islets — have
    their boundary cut at 180 degrees, which leaves a segment stepping from +180 to -180
    inside an otherwise ordinary ring. Drawn literally that is a hairline ruled straight
    across the plate. Splitting at every such step and closing each run on itself puts
    the seam where the data already put it: along the antimeridian.
    """
    jumps = [i for i in range(len(ring) - 1) if abs(ring[i + 1][0] - ring[i][0]) > 180]
    if not jumps:
        return [ring]
    runs, start = [], 0
    for j in jumps:
        runs.append(ring[start:j + 1])
        start = j + 1
    runs.append(ring[start:])
    # A ring is cyclic, so its tail run continues into its head run.
    if len(runs) > 1:
        runs[0] = runs[-1] + runs[0]
        runs.pop()
    return [r for r in runs if len(r) >= 4]


def is_antarctic(ring):
    """Antarctica, dropped.

    It is a third of the ink in a world outline and there is no Antarctic building
    tradition in this corpus — nor a gazetteer entry south of 42 degrees. Saying so is
    better than drawing a continent to prove the map goes all the way down.
    """
    return max(y for _, y in ring) < -60


def area(ring):
    """Unsigned shoelace area, in square degrees. Only ever compared to a threshold."""
    s = 0.0
    for i in range(len(ring)):
        x1, y1 = ring[i]
        x2, y2 = ring[(i + 1) % len(ring)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2


def rdp(points, eps):
    """Ramer-Douglas-Peucker, iterative — a 10m coastline arc runs to tens of thousands
    of points and the recursive form overflows the stack on the Siberian shore."""
    if len(points) < 3:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        lo, hi = stack.pop()
        if hi <= lo + 1:
            continue
        x1, y1 = points[lo]
        x2, y2 = points[hi]
        dx, dy = x2 - x1, y2 - y1
        norm = math.hypot(dx, dy)
        best, best_d = -1, -1.0
        for i in range(lo + 1, hi):
            px, py = points[i]
            if norm == 0:
                d = math.hypot(px - x1, py - y1)
            else:
                d = abs(dy * px - dx * py + x2 * y1 - y2 * x1) / norm
            if d > best_d:
                best, best_d = i, d
        if best_d > eps:
            keep[best] = True
            stack.append((lo, best))
            stack.append((best, hi))
    return [p for p, k in zip(points, keep) if k]


def path(ring, decimals):
    """One ring as SVG path data, quantised then delta-encoded.

    Absolute coordinates cost about eighteen characters a point at the fine tier and
    compress badly, because every one of them is a different long number. Quantising to
    the tier's grid and emitting relative `l` deltas makes almost every number two or
    three characters, and the ones the coastline repeats — a shore that runs at a steady
    angle for a hundred points — become literally repeated bytes for gzip to find.
    Deltas are taken between the ROUNDED positions, so the drift an accumulating
    round-as-you-go encoder would build up over ten thousand points cannot happen.

    lon, then NEGATED lat: the map projects (lat, lon) -> (lon, -lat), so a path stored
    this way needs no transform at draw time beyond the view box.
    """
    q = 10 ** decimals
    pts = []
    for x, y in ring:
        p = (round(x * q), round(-y * q))
        if not pts or p != pts[-1]:
            pts.append(p)
    if len(pts) < 4:
        return None

    def num(v):
        s = f'{v / q:.{decimals}f}'.rstrip('0').rstrip('.')
        if s in ('', '-0', '0'):
            return '0'
        if s.startswith('0.'):
            return s[1:]
        if s.startswith('-0.'):
            return '-' + s[2:]
        return s

    out = ['M', num(pts[0][0]), ',', num(pts[0][1])]
    px, py = pts[0]
    for x, y in pts[1:]:
        dx, dy = num(x - px), num(y - py)
        out.append('l')
        out.append(dx)
        # The comma is only needed when the second number would otherwise run into the
        # first. A minus sign always separates. A leading decimal point separates only if
        # the first number ALREADY SPENT its point — `l-2.58.36` is two numbers, but
        # `l2.36` is one, and dropping the comma there silently merges a coordinate pair
        # into a single number and shifts every point in the ring after it. Caught by
        # src/coastlines.test.mjs, which parses the deltas back rather than eyeballing
        # the bytes.
        if not (dy.startswith('-') or (dy.startswith('.') and '.' in dx)):
            out.append(',')
        out.append(dy)
        px, py = x, y
    out.append('Z')
    return ''.join(out)


def bbox(ring):
    """Drawn-space bounds, rounded outward to whole degrees.

    The atlas culls by these before it renders: at the fine tier there are two thousand
    rings and a zoomed-in view contains a handful, and asking React to mount the other
    two thousand paths — every one of them clipped away by the viewBox — is how a
    sharper coastline becomes a slower one. A degree of slop is deliberate; the cost of
    drawing one ring too many is nothing and the cost of dropping one that was on screen
    is a hole in the world.
    """
    xs = [x for x, _ in ring]
    ys = [-y for _, y in ring]
    return (math.floor(min(xs)), math.floor(min(ys)),
            math.ceil(max(xs)), math.ceil(max(ys)))


def build(src, out_dir):
    report = []
    for name, filename, eps, decimals in TIERS:
        with open(os.path.join(src, filename)) as fh:
            topo = json.load(fh)
        raw_rings = decode(topo, 'land')
        rings = []
        for r in raw_rings:
            if is_antarctic(r):
                continue
            rings.extend(unwrap(r))
        floor = MIN_AREA[name]
        kept, raw_pts, pts = [], 0, 0
        for r in rings:
            raw_pts += len(r)
            if area(r) < floor:
                continue
            s = rdp(r, eps)
            if len(s) < 4:
                continue
            d = path(s, decimals)
            if not d:
                continue
            kept.append((area(s), d, bbox(s)))
            pts += len(s)
        # Biggest first, so the big landmasses are painted before the islands that sit in
        # their bays, and so a truncated read still shows a recognisable world.
        kept.sort(key=lambda t: t[0], reverse=True)
        text = emit(name, filename, eps, floor, len(kept), pts, raw_pts,
                    [d for _, d, _ in kept], [b for _, _, b in kept])
        target = os.path.join(out_dir, f'coastlines{"" if name == "coarse" else "-" + name}.js')
        with open(target, 'w') as fh:
            fh.write(text)
        report.append((name, len(kept), pts, len(text), target))
    return report


HEADER = """/* Coastlines — the {name} tier. GENERATED; do not hand-edit.

   Written by workbench/scripts/make_coastlines.py from {source} (world-atlas@2, which
   repackages Natural Earth's public-domain land layer). Ramer-Douglas-Peucker at
   {eps} degrees; rings under {floor} square degrees dropped; coordinates quantised to
   {decimals} decimal places and delta-encoded.

   {rings} rings, {pts} points, simplified from {raw} in the source.

   `paths` are raw degrees with the latitude negated, so a path is drawn in lon/-lat and
   the view transform alone decides the scale. `bounds` is four numbers per path in the
   same order — x0, y0, x1, y1 in that same drawn space, rounded outward to whole
   degrees — so the atlas can cull to its viewport before it renders.

   This is interface furniture, not corpus data. A coastline is not a source, and not one
   of these numbers may migrate into styles/*.json as a measured fact.
*/
"""


def emit(name, source, eps, floor, rings, pts, raw, paths, boxes):
    decimals = dict((t[0], t[3]) for t in TIERS)[name]
    body = HEADER.format(name=name, source=source, eps=eps, floor=floor,
                         decimals=decimals, rings=rings, pts=pts, raw=raw)
    const = 'COAST_' + name.upper()
    body += f'\nexport const {const} = {{\n'
    body += f"  name: '{name}',\n"
    body += f"  source: '{source} (Natural Earth via world-atlas@2)',\n"
    body += f'  tolerance: {eps},   // degrees of simplification error, the floor on what it can show\n'
    body += f'  rings: {rings},\n'
    body += f'  points: {pts},\n'
    body += '  paths: [\n'
    body += ''.join(f'    "{p}",\n' for p in paths)
    body += '  ],\n'
    body += '  bounds: [\n'
    for i in range(0, len(boxes), 24):
        body += '    ' + ''.join(f'{v},' for b in boxes[i:i + 24] for v in b) + '\n'
    body += '  ],\n'
    body += '};\n'
    if name == 'coarse':
        body += (
            "\n/* The names the atlas imported before there were tiers. The coarse outline is\n"
            "   the one every view starts from and the only one that is never fetched. */\n"
            "export const COASTLINES = COAST_COARSE.paths;\n"
        )
    return body


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--src', required=True, help="world-atlas package/ directory")
    ap.add_argument('--out', default=os.path.join(os.path.dirname(__file__), '..', 'app', 'src', 'data'))
    a = ap.parse_args()
    for tier, rings, pts, size, target in build(a.src, os.path.abspath(a.out)):
        print(f'{tier:7} {rings:5} rings {pts:7} points {size/1024:8.1f} KB  {target}')
