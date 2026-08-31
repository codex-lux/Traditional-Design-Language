#!/usr/bin/env python3
"""render_profile.py — the asset records the corpus can draw for itself.

WHY THIS EXISTS. `assets/manifest.json` holds 322 records and zero files. WP-4.4's harvest is
blocked on a network this container does not have, and 150 of the records could never be
harvested anyway: they are `role: incorrect`, and no archive indexes wrongness. But eleven
records already carry a `generated_from` block naming a proportion pack and an assembly --
these are measured detail drawings of a moulding profile, and the corpus has held everything
needed to draw them since WP-5.11. They were waiting on a driver, not on a photograph.

THE DRAWING IS NOT A NEW CONSTRUCTION. Every curve here comes from `build/profiles.py`, which
turns a member's height and projection into real geometry -- a quarter ellipse for an ovolo, two
tangent arcs through the chord's midpoint for a cyma, a half round for a torus -- and from
`proportion_engine.dimension()`, which supplies the heights. This file adds a frame, a scale and
the labels; it invents no member and no dimension. That matters because pack geometry is LINEAR
IN THE MODULE (tests/test_profiles.py proves it), so a profile computed once is a profile at any
size, and a second implementation would be a second thing to keep in step.

WHAT IT REFUSES. A member `profiles.py` reports as `unconstructed` -- a volute's spiral, an
acanthus row -- is NAMED ON THE PLATE and not drawn as something plausible. `gibbs-ionic`'s
capital and `vignola-corinthian`'s capital both carry such members, so two of the eleven plates
are partial and say so on their face. A drawing that quietly substitutes a swelling for a
construction it does not have is the laundering this corpus forbids, in ink instead of in JSON.

    python3 build/render_profile.py                  # draw all eleven, report, write nothing
    python3 build/render_profile.py --write          # and file them against their records
    python3 build/render_profile.py --id <asset-id>  # just one
"""
import argparse
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

PE = modcache.load("proportion_engine", os.path.join(ROOT, "build", "proportion_engine.py"))
PROF = modcache.load("profiles", os.path.join(ROOT, "build", "profiles.py"))

ASSETS = os.path.join(ROOT, "assets", "manifest.json")
OUTDIR = os.path.join(ROOT, "assets", "generated")

# The elevation sheet's palette, so a detail plate and the sheet it details look like one set.
PAL = {"ink": "#1b1a17", "ink3": "#6f6a60", "brass": "#b08d57", "paper": "#faf8f3",
       "rule": "#c9c2b4"}

# THE PLATE TAKES THE DRAWING'S SHAPE, IT IS NOT A FIXED BOX THE DRAWING SITS INSIDE. A cornice
# profile is short and wide; a capital is tall. A fixed 520x660 frame drew the Doric cornice into
# the top third and left 400 px of paper under it, which reads as a drawing that failed rather
# than a drawing that fits. Height is DERIVED from the geometry and from how many members have to
# be named -- the same lesson as the atlas's viewBox, where a stored height letterboxed 27.8
# degrees of latitude.
PAD = 44
LEGEND_W = 330          # wide enough for "Cyma reversa crowning the mutules and band" plus a size
PROFILE_W = 320
W = PAD * 2 + PROFILE_W + LEGEND_W
LINE_H = 11.0
# Measured off the rendered plate, not guessed: 8px ui-monospace advances ~4.95px per character.
# The first version assumed 4.42 and three labels ran off the right edge of the paper -- an
# estimate that is only a little low still overflows, because the longest label is the one that
# matters and it is the one an underestimate hits hardest.
CH_W = 4.95


def _esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def _named(unconstructed):
    """`profiles.py` reports an unconstructed member as {id, profile}, not as a name. Sorted so
    a plate's disclosure line is stable across runs -- a caption that reorders itself makes a
    diff that says something changed when nothing did."""
    out = []
    for u in unconstructed or []:
        if isinstance(u, dict):
            nm = str(u.get("id") or "?").replace("_", " ")
            pf = u.get("profile")
            out.append("%s (%s)" % (nm, pf) if pf else nm)
        else:
            out.append(str(u))
    return sorted(out)


def states_assembly(pack_id, assembly_id):
    """The pack in the overlay chain that actually states this assembly, or None.

    AN OVERLAY INHERITS WHAT IT DOES NOT STATE, AND SOMETIMES IT DOES NOT STATE IT ON PURPOSE.
    `palladio-tuscan` records a base, a shaft, a capital and a pedestal, and deliberately no
    entablature: Palladio does not dimension his Tuscan entablature in the text and the plate
    numerals are illegible in every reachable scan, which is the whole of OQ 7. `resolve()` then
    supplies a cornice from `vignola-tuscan`, correctly -- that is what an overlay is for.

    But a plate titled "Palladio's Tuscan Order — cornice" drawing Vignola's members under
    "AFTER: Palladio, I Quattro Libri, Venice 1570" attributes one authority's figures to
    another's citation, on the exact assembly the corpus has an open question about because
    that authority does not give it. That is the laundering this corpus forbids, produced by a
    drawing rather than by a record. So the plate says whose members these are."""
    seen = set()
    pid = pack_id
    while pid and pid not in seen:
        seen.add(pid)
        raw = PE.PACKS.get(pid) or {}
        if assembly_id in (raw.get("assemblies") or {}):
            return pid
        pid = raw.get("overlay_of")
    return None


def _footer_lines(pack, pack_id, assembly_id, module_in, members, height, relief, unconstructed):
    """What the plate says about itself. One function, because the height calculation and the
    drawing both read it and a second copy would let them disagree about how tall it is."""
    lines = ["GENERATED FROM THE RECORD BY build/render_profile.py — NOT A DRAWING OF A REAL "
             "BUILDING.",
             "%s, assembly %s, at a %.0f\u2033 column. %d member(s), %.2f\u2033 high, %.2f\u2033 "
             "of relief from the naked." % (pack.get("name") or pack_id, assembly_id,
                                            module_in * 2, len(members), height, relief)]
    owner = states_assembly(pack_id, assembly_id)
    if owner and owner != pack_id:
        src = PE.PACKS.get(owner) or {}
        lines.append("INHERITED: %s STATES NO %s OF ITS OWN. These members are %s's, delivered "
                     "by the overlay, and the citation below is THEIRS." % (
                         pack_id, assembly_id.upper(), owner))
        auth = (src.get("authority") or {}).get("source")
        if auth:
            lines.append("AFTER: " + auth)
        return lines + ([] if not unconstructed else [
            "NOT CONSTRUCTED, AND NOT DRAWN AS SOMETHING PLAUSIBLE: " + ", ".join(_named(unconstructed))])
    auth = (pack.get("authority") or {}).get("source")
    if auth:
        lines.append("AFTER: " + auth)
    if unconstructed:
        lines.append("NOT CONSTRUCTED, AND NOT DRAWN AS SOMETHING PLAUSIBLE: "
                     + ", ".join(_named(unconstructed)))
    return lines


def assembly_members(dim, assembly_id):
    for a in dim.get("assemblies", []):
        if a.get("id") == assembly_id:
            return a.get("members") or []
    return []


def render(pack_id, assembly_id, module_in=6.0):
    """One assembly of one pack as a detail plate. Returns (svg, report)."""
    if pack_id not in PE.PACKS:
        raise KeyError("no such pack: %s" % pack_id)
    # RESOLVED, never raw. `gibbs-ionic` is an overlay on Vignola and states no `base` of its
    # own; reading its own file finds no base assembly and the plate simply does not exist.
    # That is the raw-record read this corpus has been caught by on kits, on slots and on the
    # cascade -- the answer lives in the inheritance, not in the file.
    pack = PE.resolve(pack_id)
    dim = PE.dimension(pack, module_in=module_in)
    geo = PROF.pack_geometry(dim, column=(pack.get("column") or {}),
                             projection_datum=pack.get("projection_datum"))
    members = assembly_members(dim, assembly_id)
    if not members:
        raise KeyError("pack %s has no assembly %r" % (pack_id, assembly_id))

    asm = next((a for a in geo["assemblies"] if a["id"] == assembly_id), None)
    naked = (asm or {}).get("naked_in") or 0.0
    # The datum is decided PER ASSEMBLY GROUP by profiles.py::axis_holds_for and never
    # re-derived here -- OQ 78 is what happens when two places answer this question.
    from_axis = geo.get("assembly_datum", {}).get(assembly_id) == "axis"

    y0 = min(m["y_bottom_in"] for m in members)
    y1 = max(m["y_top_in"] for m in members)
    drawn_h = (y1 - y0) or 1.0
    relief = max((PROF.outer_face(naked, m.get("projection_in") or 0.0, from_axis) - naked)
                 for m in members) or 1.0

    pad = PAD
    # Scale to the relief, then let the height follow. Capped so a tall capital cannot run to a
    # plate nobody can read at once.
    k = min(PROFILE_W / max(relief, 1.0), 620.0 / drawn_h)
    ink_h = drawn_h * k
    legend_h = len(members) * LINE_H + 20
    box_h = max(ink_h, legend_h)
    H = int(pad * 2 + box_h + 78)   # provisional; grown below if the footer wraps
    px0, py0 = pad + 26, pad + 30
    sx = lambda x: px0 + (x - naked) * k
    sy = lambda y: py0 + (y1 - y) * k

    sil = PROF.silhouette(members, naked_at=naked, from_axis=from_axis)
    unconstructed = sil.get("unconstructed") or []

    # Wrap the footer BEFORE the plate height is committed: a disclosure that needs three lines
    # on a plate sized for two prints outside the viewBox and is invisible, which is worse than
    # a plate that is slightly tall.
    _foot_budget = int((W - pad * 2) / CH_W)
    _foot_rows = 0
    for _ln in _footer_lines(pack, pack_id, assembly_id, module_in, members, y1 - y0, relief,
                             unconstructed):
        _foot_rows += max(1, -(-len(_ln) // _foot_budget))
    H = int(pad * 2 + box_h + 34 + _foot_rows * 11)

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
         '<style>'
         f'.lb{{font:600 9px/1 ui-sans-serif,system-ui,sans-serif;fill:{PAL["ink"]};letter-spacing:.08em}}'
         f'.dm{{font:8px/1 ui-monospace,SFMono-Regular,Menlo,monospace;fill:{PAL["ink3"]}}}'
         f'.ti{{font:600 13px/1 ui-serif,Georgia,serif;fill:{PAL["ink"]}}}'
         f'.pf{{fill:none;stroke:{PAL["rule"]};stroke-width:.6}}'
         '</style>',
         f'<rect width="{W}" height="{H}" fill="{PAL["paper"]}"/>']

    title = "%s — %s" % (pack.get("name") or pack_id, assembly_id)
    s.append(f'<text class="ti" x="{pad}" y="{pad-14}">{_esc(title)}</text>')
    s.append(f'<rect class="pf" x="{pad-8}" y="{pad-6}" width="{W-pad*2+16}" height="{box_h+26:.0f}"/>')

    # The naked: the plane every projection in this assembly is measured from.
    s.append(f'<line x1="{sx(naked):.1f}" y1="{sy(y0):.1f}" x2="{sx(naked):.1f}" y2="{sy(y1):.1f}" '
             f'stroke="{PAL["ink3"]}" stroke-width=".5" stroke-dasharray="2 2"/>')

    d = PROF.svg_path(sil["segments"], sx, sy, start=sil["start"])
    if d:
        s.append(f'<path d="{d}" fill="{PAL["brass"]}" fill-opacity=".5" '
                 f'stroke="{PAL["ink"]}" stroke-width=".9"/>')

    # Member leaders, decluttered upward. Members arrive bottom-to-top, so screen y decreases as
    # the list advances and each label must clear the one BELOW it; nudging the other way walks
    # the legend off the plate, which only looking at the drawing finds.
    lx = pad + PROFILE_W + 44
    band_top, band_bot = pad + 24, pad + box_h + 4
    gap = min(LINE_H, max(8.0, (band_bot - band_top) / max(len(members), 1)))
    anchors = [sy((m["y_bottom_in"] + m["y_top_in"]) / 2.0) for m in members]
    ys, last = [], None
    for a in anchors:
        y = a if last is None else min(a, last - gap)
        ys.append(y); last = y
    over = ys[0] - band_bot
    if over > 0:
        ys = [y - over for y in ys]
    under = band_top - ys[-1]
    if under > 0:
        span = max(ys[0] - ys[-1], 1e-6)
        ys = [band_bot - (ys[0] - y) * ((band_bot - band_top) / span) for y in ys]

    for m, anchor, my in zip(members, anchors, ys):
        face = sx(PROF.outer_face(naked, m.get("projection_in") or 0.0, from_axis))
        s.append(f'<line x1="{face+1:.1f}" y1="{anchor:.1f}" x2="{lx-4:.1f}" y2="{my:.1f}" '
                 f'stroke="{PAL["ink3"]}" stroke-width=".35"/>')
        nm = (m.get("name") or m.get("id") or "").replace("-", " ")
        pf = (m.get("profile") or "flat").replace("-", " ")
        # The size is the point of a detail plate, so it is never what gets cut: the NAME is
        # elided to fit and the figure always survives. A label that runs off the plate is a
        # dimension the millworker does not have.
        tail = " — %s, %.2f\u2033" % (pf, m["height_in"])
        budget = int((W - 8 - lx) / CH_W)
        room = budget - len(tail)
        if len(nm) > room:
            nm = nm[:max(room - 1, 3)].rstrip() + "\u2026"
        label = nm + tail
        if len(label) > budget:                  # a tail alone can outrun the column
            label = label[:max(budget - 1, 4)].rstrip() + "\u2026"
        s.append(f'<text class="dm" x="{lx:.1f}" y="{my+2.6:.1f}">{_esc(label)}</text>')

    # The plate says what it is and what it is not.
    foot = H - pad + 6
    lines = _footer_lines(pack, pack_id, assembly_id, module_in, members, y1 - y0, relief,
                          unconstructed)
    # The footer is prose and prose is not width-aware. Wrap it rather than let a pack with a
    # long name push its own disclosure off the paper -- the disclosure is the one line on this
    # plate that must never be the thing that gets cut.
    budget = int((W - pad * 2) / CH_W)
    wrapped = []
    for ln in lines:
        while len(ln) > budget:
            cut = ln.rfind(" ", 0, budget)
            cut = cut if cut > budget * 0.5 else budget
            wrapped.append(ln[:cut]); ln = ln[cut:].lstrip()
        wrapped.append(ln)
    for i, ln in enumerate(wrapped):
        s.append(f'<text class="dm" x="{pad}" y="{foot - (len(wrapped)-1-i)*11:.1f}">{_esc(ln)}</text>')
    s.append("</svg>")

    return "\n".join(s), {"members": len(members), "unconstructed": _named(unconstructed),
                          "height_in": round(y1 - y0, 3), "relief_in": round(relief, 3),
                          "plate_w": W, "plate_h": H}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true",
                    help="write the SVGs and file them against their records")
    ap.add_argument("--id", default=None, help="only this asset id")
    a = ap.parse_args()

    doc = json.load(open(ASSETS))
    targets = [x for x in doc["assets"] if x.get("generated_from")
               and (a.id is None or x["id"] == a.id)]
    print("%d record(s) carry a `generated_from` block" % len(targets))
    if a.write:
        os.makedirs(OUTDIR, exist_ok=True)

    drawn = failed = 0
    for asset in targets:
        g = asset["generated_from"]
        try:
            svg, rep = render(g["pack"], (g.get("parameters") or {}).get("assembly"),
                              module_in=g.get("module_in") or 6.0)
        except Exception as e:
            failed += 1
            print("  FAIL  %s — %s" % (asset["id"], e))
            continue
        drawn += 1
        note = ("%d member(s), %.2f in high" % (rep["members"], rep["height_in"]))
        if rep["unconstructed"]:
            note += "; UNCONSTRUCTED: " + ", ".join(rep["unconstructed"])
        print("  DRAW  %-42s %s" % (asset["id"], note))
        if a.write:
            rel = os.path.join("assets", "generated", asset["id"] + ".svg")
            path = os.path.join(ROOT, rel)
            open(path, "w").write(svg + "\n")
            data = open(path, "rb").read()
            asset["file"] = {"path": rel, "format": "svg",
                             "width": rep["plate_w"], "height": rep["plate_h"],
                             "bytes": len(data),
                             "sha256": hashlib.sha256(data).hexdigest()}
            # `sourced` means "file present, unreviewed" -- which is now true, and was not when
            # the harvester set it on records whose `file` stayed null.
            asset["status"] = "sourced"
            asset["review_note"] = (
                "Drawn by build/render_profile.py from %s at a %.0f in column. Every dimension "
                "comes from proportion_engine.dimension() and every curve from profiles.py, so "
                "the drawing and the data cannot silently disagree. NOT reviewed: nobody has "
                "looked at this plate and confirmed it shows what the record says it shows.%s"
                % (g["pack"], (g.get("module_in") or 6.0) * 2,
                   ("" if not rep["unconstructed"] else
                    " PARTIAL: %s are named on the plate and not drawn, because this corpus "
                    "records no construction for them." % ", ".join(rep["unconstructed"]))))

    print("\ndrawn %d, failed %d" % (drawn, failed))
    if a.write and drawn:
        doc["counts"]["by_status"] = {}
        for x in doc["assets"]:
            doc["counts"]["by_status"][x["status"]] = doc["counts"]["by_status"].get(x["status"], 0) + 1
        json.dump(doc, open(ASSETS, "w"), indent=2, ensure_ascii=False)
        open(ASSETS, "a").write("\n")
        print("wrote %s and %d file(s) under assets/generated/"
              % (os.path.relpath(ASSETS, ROOT), drawn))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
