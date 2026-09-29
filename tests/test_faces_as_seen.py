"""test_faces_as_seen.py -- every elevation drawn as seen from outside, on every surface at once.

R2 (ruled 29 Sep 2026, WP-16.3): a drafter draws a north elevation as seen from the north, with
east on the LEFT, and a west one as seen from the west, with north on the left. From WP-13.3 until
WP-16.3 this record drew all four faces with the plan's own axis, and a first attempt to mirror N
and W (WP-13.3's first draft) mirrored the sheet and not the readers beside it: the Round put the
spec Colonial's front door 44.0 ft from where the plan seats it, and a stack refusal compared a
mirrored window against an unmirrored stack. So the flip is ONE SWITCH, `elevation.FACE_MIRRORED`,
and this file holds ONE NAMED OPENING at ONE MODEL POINT on every surface that draws it:

  the record   `elevation.faces[face].placed`: the opening's `u` is its distance from the face's
               own left edge as seen, on the outside of the wall
  the sheet    the SVG's `op` rectangle, read back through the plate's own `data-frame`
  the DXF      the `TDL-ELEV-OPENING` polyline, in inches of the same `u`
  the scene    the `opening-frame` solid, in the model's own x or y
  the Round    `frame.js::modelAt`, fed the direction the server serves (`corpus.plate_direction`)

THE SPECIMEN MUST BE ASYMMETRIC, OR NOTHING HERE CAN FAIL. Every surface that ignored the switch
would draw a symmetric face identically, so each face's specimen is the opening farthest from any
mirror twin, and that distance is asserted before anything else: a drawing reversed end for end
puts the specimen where no opening stands. The expected figures are written out with the
footprint's own numbers and never through `elevation.face_u_ft`, the conversion under test.

Two readers the shipped corpus cannot reach are DRIVEN rather than trusted: every roof profile
the corpus draws is symmetric, so a renderer reading the profile in the plan's direction draws the
same roof -- a lopsided profile is handed to the sheet and the DXF here -- and no plan seats two
equally wide doors on a north or west entrance front, so the tie between them is driven too.
"""
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import modcache as mc  # noqa: E402
import inkread as IR  # noqa: E402

FACES = ("S", "N", "E", "W")
AS_SEEN_AGAINST_THE_PLAN = {"S": False, "E": False, "N": True, "W": True}


def _m(name):
    return mc.load(name, os.path.join(ROOT, "build", name + ".py"))


_BUILT = {}


def _build(pid):
    """One shipped plan placed on the heuristic (deterministic), with its section, roof, elevation
    and scene -- built once per plan for the module."""
    if pid not in _BUILT:
        G, ST, RF, EL, SC = (_m("geometry"), _m("structure"), _m("roof"), _m("elevation"),
                             _m("scene"))
        path = next(q for q in (os.path.join(ROOT, "plans", pid + ".json"),
                                os.path.join(ROOT, "plans", "reference", pid + ".json"))
                    if os.path.exists(q))
        p = G.solve(json.load(open(path)), engine="heuristic")
        sec = ST.build_section(p, None, geometry_result=p)
        rf = RF.build_roof(p, None, section=sec)
        el = EL.build_elevation(p, None, section=sec, roof=rf)
        assert "error" not in el, (pid, el.get("error"))
        sc = SC.build_scene(p, sec, rf, el)
        _BUILT[pid] = (p, sec, rf, el, sc)
    return _BUILT[pid]


@pytest.fixture(scope="module")
def built():
    return _build("tidewater-georgian-careful")


# Every face on a plan whose drawing of it carries an asymmetric window (measured 29 Sep 2026 over
# the sixteen shipped plans: no Tidewater E face draws a window, so the E control is good-05's).
# The two mirrored faces are each held on two plans, so the reading cannot be one plan's luck.
CASES = [("tidewater-georgian-careful", "S"), ("tidewater-georgian-careful", "N"),
         ("tidewater-georgian-careful", "W"), ("good-05-lobby-gallery-mansion", "E"),
         ("good-05-lobby-gallery-mansion", "W"), ("spec-builder-colonial", "N")]


def _dims(sec):
    fp = sec["footprint"]
    t = sec["wall"]["exterior_in"] / 12.0
    return float(fp["clear_width_ft"]), float(fp["clear_depth_ft"]), t


def _drawn_width(face, sec):
    """The face's drawn width: the OUTSIDE figure the section's footprint states, which the wall
    band spans and the roof is laid over."""
    fp = sec["footprint"]
    return float(fp["width_ft"] if face in ("S", "N") else fp["depth_ft"])


def _expected_u(face, along, sec):
    """The face's `u` for a plan coordinate, written out: the outside wall adds `t`, and on a face
    drawn as seen from outside against the plan's axis the distance runs from the far end of the
    face's DRAWN width, so the face is the plan-direction face reversed end for end."""
    _Wc, _Dc, t = _dims(sec)
    return (_drawn_width(face, sec) - (along + t)) if AS_SEEN_AGAINST_THE_PLAN[face] else (along + t)


def _specimen(el, sec, face):
    """The opening on `face` farthest from any opening at its mirror position on the same storey,
    and that distance. An opening on the face's centre line is its own twin and scores 0."""
    EL = _m("elevation")
    Wc, Dc, _t = _dims(sec)
    span = Wc if face in ("S", "N") else Dc
    rects = [r for r in EL.opening_rects(el, face)["rects"] if r["kind"] == "window"]
    best, gap = None, -1.0
    for r in rects:
        mirror = span - r["along_ft"]
        g = min(abs(mirror - o["along_ft"]) for o in rects if o["storey"] == r["storey"])
        if g > gap:
            best, gap = r, g
    return best, gap


@pytest.mark.parametrize("face", FACES)
def test_the_switch_is_the_ruling(face):
    EL = _m("elevation")
    assert EL.FACE_MIRRORED[face] is AS_SEEN_AGAINST_THE_PLAN[face], EL.FACE_MIRRORED


@pytest.mark.parametrize("pid", sorted({pid for pid, _f in CASES}))
def test_the_mirror_axis_is_the_faces_drawn_width_and_not_the_exact_span(pid):
    """A mirrored face is reflected about its own DRAWN width -- the outside figure the footprint
    states, which the wall band spans and the roof is laid over -- so the face seen from outside
    is the plan-direction face reversed and nothing else. The footprint states that figure rounded
    to two places, and every plan here rounds it visibly: the first version of the flip reflected
    the openings about the exact clear span plus two walls, and each stood 0.0033 ft off its wall's
    reflection. This holds the one axis and its premise."""
    EL = _m("elevation")
    p, sec, rf, el, sc = _build(pid)
    fp = sec["footprint"]
    Wc, Dc, t = _dims(sec)
    for face, clear in (("N", Wc), ("W", Dc), ("S", Wc), ("E", Dc)):
        drawn = _drawn_width(face, sec)
        assert EL.face_span_outside_ft(face, fp) == drawn, face
        assert abs((clear + 2.0 * t) - drawn) > 1e-4, (
            "the premise: this plan's stated outside figure is rounded, so the exact span and the "
            "drawn width are two different axes", face)
        assert el["faces"][face]["outside_width_in"] == pytest.approx(drawn * 12.0, abs=1e-9), face
        if AS_SEEN_AGAINST_THE_PLAN[face]:
            assert EL.face_u_outside(face, 0.0, fp) == drawn, face
            assert EL.face_u_ft(face, 3.25, Wc, Dc, t, outside_ft=drawn) == \
                pytest.approx(drawn - 3.25 - t, abs=1e-12), face
        else:
            assert EL.face_u_outside(face, 3.25, fp) == 3.25, face


@pytest.mark.parametrize("pid", ["tidewater-georgian-careful", "spec-builder-colonial"])
def test_a_mirrored_face_is_the_plan_direction_face_reversed_and_nothing_else(pid, monkeypatch):
    """R2's own words: every N and W sheet redraws with the SAME CONTENT REVERSED. So the house is
    built twice, once as ruled and once with the switch off on every face, and on the N and W faces
    each placed opening's `u` and its `u` in the plan's direction sum to the face's drawn width, the
    roof profile is the reflected profile, each stack mark is its reflection, and the wall beside a
    doorcase measures the same two walls at the same lengths, on the other sides. A mirror about
    any other axis, or a reader left in the plan's direction, breaks one of the sums."""
    EL = _m("elevation")
    p, sec, rf, el, sc = _build(pid)
    fp = sec["footprint"]
    monkeypatch.setattr(EL, "FACE_MIRRORED", {f: False for f in FACES})
    plain = EL.build_elevation(p, None, section=sec, roof=rf)
    plain_piers = {f: EL.doorcase_piers(plain, f) for f in ("N", "W")}
    plain_marks = {f: EL.stack_marks(plain, f)["marks"] for f in ("N", "W")}
    plain_prof = {f: EL.face_profile(rf, f, fp) for f in ("N", "W")}
    monkeypatch.undo()
    assert EL.FACE_MIRRORED == AS_SEEN_AGAINST_THE_PLAN
    checked = 0
    for face in ("N", "W"):
        span = _drawn_width(face, sec)
        theirs = {(q["room"], q["storey"], q["kind"], q["along_ft"]): q["u_ft"]
                  for q in plain["faces"][face]["placed"]}
        ours = {(q["room"], q["storey"], q["kind"], q["along_ft"]): q["u_ft"]
                for q in el["faces"][face]["placed"]}
        assert ours.keys() == theirs.keys(), face
        for k, u in ours.items():
            assert u + theirs[k] == pytest.approx(span, abs=2e-4), (face, k, u, theirs[k])
            checked += 1
        prof = EL.face_profile(rf, face, fp)
        assert sorted((round(span - x, 6), round(h, 6)) for x, h in prof) == \
            sorted((round(x, 6), round(h, 6)) for x, h in plain_prof[face]), face
        marks = EL.stack_marks(el, face)["marks"]
        assert len(marks) == len(plain_marks[face]), face
        for mk, pm in zip(sorted(marks, key=lambda m: -max(u for u, _h in m["outline"])),
                          sorted(plain_marks[face], key=lambda m: min(u for u, _h in m["outline"]))):
            assert sorted((round(span - u, 6), round(h, 6)) for u, h in mk["outline"]) == \
                sorted((round(u, 6), round(h, 6)) for u, h in pm["outline"]), face
        a, b = EL.doorcase_piers(el, face), plain_piers[face]
        assert (a is None) == (b is None), face
        if a:
            assert sorted(sd["clear_in"] for sd in a["sides"]) == \
                pytest.approx(sorted(sd["clear_in"] for sd in b["sides"]), abs=1e-3), (a, b)
            assert [sd["side"] for sd in a["sides"]] == ["left", "right"]
            got = {sd["side"]: sd["clear_in"] for sd in a["sides"]}
            was = {sd["side"]: sd["clear_in"] for sd in b["sides"]}
            assert got["left"] == pytest.approx(was["right"], abs=1e-3), (got, was)
    assert checked, "the premise: the N and W faces place something"


@pytest.mark.parametrize("pid,face", CASES)
def test_one_opening_stands_at_one_point_on_every_surface(pid, face, tmp_path):
    EL = _m("elevation")
    p, sec, rf, el, sc = _build(pid)
    r, gap = _specimen(el, sec, face)
    assert r is not None, f"the premise: the {face} face draws a window"
    w_ft = r["width_in"] / 12.0
    # THE PREMISE: a drawing reversed end for end would put this window where no window stands
    assert gap >= w_ft + 0.5, (
        f"the {face} face's best specimen stands {gap:.2f} ft from an opening at its mirror "
        f"position: this face is too symmetric to tell a reversed drawing from a right one. "
        f"Drive an opening off the centre line rather than loosening this.")
    along = r["along_ft"]
    u = _expected_u(face, along, sec)
    wrong_u = along + _dims(sec)[2]      # where a drawing in the plan's direction would put it

    # the record
    pl = next(q for q in el["faces"][face]["placed"]
              if q["room"] == r["room"] and q["storey"] == r["storey"] and q["along_ft"] == along)
    assert pl["u_ft"] == pytest.approx(u, abs=1e-3), (face, pl["u_ft"], u)
    assert r["cx_in"] / 12.0 == pytest.approx(u, abs=1e-6), (face, r["cx_in"] / 12.0, u)

    # the sheet
    out = str(tmp_path / f"e-{face}.svg")
    _m("render_elevation").render_elevation(el, out, face=face)
    ink = IR.Ink(open(out, encoding="utf-8").read())
    plate = next(f for f in ink.frames() if f.get("proj") == "elevation")
    drawn = []
    for it in ink.select(cls="op"):
        b = it.bbox()
        (u0, _v0), (u1, _v1) = IR.to_model(plate, b[0], b[3]), IR.to_model(plate, b[2], b[1])
        drawn.append(((u0 + u1) / 2.0, abs(u1 - u0)))
    hits = [c for c, wd in drawn if abs(c - u) < 0.03 and abs(wd - w_ft) < 0.05]
    assert hits, (f"the {face} sheet draws no {w_ft:.2f} ft opening at u = {u:.3f} ft "
                  f"(openings drawn at {sorted(round(c, 2) for c, _w in drawn)})")
    if AS_SEEN_AGAINST_THE_PLAN[face]:
        assert not [c for c, wd in drawn if abs(c - wrong_u) < 0.03 and abs(wd - w_ft) < 0.05], (
            f"the {face} sheet also draws it at {wrong_u:.3f}, the plan's direction")

    # the scene: the frame of the same opening, in the model's own coordinate along the wall
    frames = [s for s in sc["solids"] if s["class"] == "opening-frame" and s.get("face") == face]
    assert frames, f"the premise: the scene frames the {face} face's openings"
    k = 0  # the outline's first coordinate is x on the N and S faces (plane xz) and y on E and W (yz)
    centres = [(min(v[k] for v in s["geometry"]["outline"]) + max(v[k] for v in s["geometry"]["outline"])) / 2.0
               for s in frames]
    # to a thousandth and a half: the scene writes its outlines to three places, and a mirror
    # taken about any axis but the elevation's own -- the exact span, say -- moves every mirrored
    # solid by 0.0033 ft on this plan, which is exactly what the flip's first version did
    assert any(abs(c - along) < 0.0015 for c in centres), (
        f"the scene frames no {face} opening at the plan's {along:.3f} ft "
        f"(frames at {sorted(round(c, 3) for c in centres)})")

    # the Round: the plate registers where the server says it runs, and lands on the same point
    if not shutil.which("node"):
        pytest.skip("COULD NOT EVALUATE the Round's half: node is not installed")
    sys.path.insert(0, os.path.join(ROOT, "workbench", "server"))
    import corpus  # noqa: E402  (workbench/server/corpus.py; needs no web framework)
    served = corpus.plate_direction(el, face)
    assert served == {"face": face, "mirrored": AS_SEEN_AGAINST_THE_PLAN[face]}, served
    url = "file://" + os.path.join(ROOT, "workbench", "app", "src", "round", "frame.js")
    js = ("import { modelAt } from %s;\n" % json.dumps(url) +
          "const q = JSON.parse(process.argv[1]);\n"
          "process.stdout.write(JSON.stringify(modelAt(q.view, { bounds: { envelope: q.env } }, "
          "q.u, q.v, q.mirrored)));")
    arg = json.dumps({"view": face.lower(), "env": sc["bounds"]["envelope"], "u": u, "v": 5.0,
                      "mirrored": served["mirrored"]})
    got = subprocess.run(["node", "--input-type=module", "-e", js, arg], capture_output=True,
                         text=True, timeout=60)
    assert got.returncode == 0, got.stderr
    pt = json.loads(got.stdout)
    assert pt is not None, f"the Round refuses the {face} plate's direction {served}"
    along_model = pt[0] if face in ("S", "N") else pt[1]
    assert along_model == pytest.approx(along, abs=0.01), (
        f"the Round lays the {face} plate's u = {u:.3f} at {along_model:.3f} ft, not the plan's "
        f"{along:.3f}")


@pytest.mark.parametrize("pid,face", CASES)
def test_the_dxf_draws_the_same_opening_at_the_same_u(pid, face):
    ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE the DXF half: ezdxf is not installed")
    p, sec, rf, el, sc = _build(pid)
    r, gap = _specimen(el, sec, face)
    w_ft = r["width_in"] / 12.0
    assert gap >= w_ft + 0.5
    u = _expected_u(face, r["along_ft"], sec)
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "e.dxf")
        res = _m("export_dxf").export_elevation_dxf(el, path, face=face)
        assert not (isinstance(res, dict) and (res.get("error") or res.get("refusal"))), res
        msp = ezdxf.readfile(path).modelspace()
        drawn = []
        for e in msp.query("LWPOLYLINE"):
            if e.dxf.layer != "TDL-ELEV-OPENING":
                continue
            xs = [pt[0] for pt in e.get_points()]
            drawn.append(((min(xs) + max(xs)) / 24.0, (max(xs) - min(xs)) / 12.0))
    assert [c for c, wd in drawn if abs(c - u) < 0.01 and abs(wd - w_ft) < 0.01], (
        f"the {face} DXF draws no {w_ft:.2f} ft opening at u = {u:.3f} ft "
        f"(openings at {sorted(round(c, 2) for c, _w in drawn)})")


# ------------------------------------------------------------------ driven: a lopsided roof
def _lopsided(el, face):
    """The elevation with `face`'s roof profile replaced by a triangle whose apex stands a quarter
    of the way along the plan's axis -- the one kind of profile the corpus never states."""
    e2 = copy.deepcopy(el)
    fp = e2["footprint"]
    span = fp["width_ft"] if face in ("S", "N") else fp["depth_ft"]
    prof = e2["roof_record"]["elevation_profiles"][face]
    lo, hi = min(h for _x, h in prof), max(h for _x, h in prof)
    e2["roof_record"]["elevation_profiles"][face] = [(0.0, lo), (span, lo), (0.25 * span, hi)]
    return e2, span


@pytest.mark.parametrize("face", FACES)
def test_a_lopsided_roof_is_drawn_from_the_faces_own_left(built, face, tmp_path):
    """The apex a quarter of the way along the plan's axis stands a quarter of the way along the
    face on S and E and three quarters of the way on N and W, where the face runs the other way.
    `elevation.face_profile` is the one reader; this reads the INK."""
    p, sec, rf, el, sc = built
    e2, span = _lopsided(el, face)
    out = str(tmp_path / f"r-{face}.svg")
    _m("render_elevation").render_elevation(e2, out, face=face)
    ink = IR.Ink(open(out, encoding="utf-8").read())
    plate = next(f for f in ink.frames() if f.get("proj") == "elevation")
    (roof,) = ink.select(tag="polygon", cls="rf")
    pts = [IR.to_model(plate, x, y) for x, y in roof.points(n=2, lines=True)]
    apex_u = max(pts, key=lambda q: q[1])[0]
    want = (0.75 if AS_SEEN_AGAINST_THE_PLAN[face] else 0.25) * span
    assert apex_u == pytest.approx(want, abs=0.05), (face, apex_u, want)


@pytest.mark.parametrize("face", FACES)
def test_the_dxf_draws_the_lopsided_roof_the_same_way(built, face):
    ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE the DXF half: ezdxf is not installed")
    p, sec, rf, el, sc = built
    e2, span = _lopsided(el, face)
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "r.dxf")
        _m("export_dxf").export_elevation_dxf(e2, path, face=face)
        msp = ezdxf.readfile(path).modelspace()
        (poly,) = [e for e in msp.query("LWPOLYLINE") if e.dxf.layer == "TDL-ELEV-ROOF"]
        apex = max(poly.get_points(), key=lambda q: q[1])
    want = (0.75 if AS_SEEN_AGAINST_THE_PLAN[face] else 0.25) * span
    assert apex[0] / 12.0 == pytest.approx(want, abs=0.05), (face, apex[0] / 12.0, want)


# ------------------------------------------------------------------ driven: two equal front doors
def test_two_equally_wide_front_doors_tie_to_the_same_door_whichever_way_the_face_reads(built, monkeypatch):
    """`doorcase.entrance_index` takes the widest door and breaks a tie on the lower PLAN
    coordinate, and the placer hands it `position_ft`. The elevation handed it the face's own `u`
    until WP-16.3, which on a face drawn as seen from outside runs the other way: two equally wide
    doors on a north front would have made the placer dress one and the elevation the other. No
    shipped plan seats two, so two are driven onto the N face through the one reader the
    elevation takes its openings from (`render_plan.openings_of_level`)."""
    EL, DC, RP = _m("elevation"), _m("doorcase"), _m("render_plan")
    p, sec, rf, el, sc = built
    _Wc, Dc, _t = _dims(sec)
    pair = [(3.0, 12.25), (3.0, 30.75)]   # equal widths; the lower plan coordinate first
    by_plan = DC.entrance_index(pair)
    by_face = DC.entrance_index([(w, _expected_u("N", a, sec)) for w, a in pair])
    assert (by_plan, by_face) == (0, 1), (
        "the premise: on a face drawn as seen from outside the two readings choose different "
        "doors, so which one the elevation passes is decidable", by_plan, by_face)

    def two_doors_on_the_north_wall(placed, lv, *_):
        if (lv.get("index") or 0) != 0:
            return {"exterior": [], "windows": []}
        return {"exterior": [{"wall": "N", "at_ft": a, "width_ft": w, "room": f"r{i}",
                              "edge_ft": Dc} for i, (w, a) in enumerate(pair)],
                "windows": []}

    monkeypatch.setattr(RP, "openings_of_level", two_doors_on_the_north_wall)
    got = EL.placed_openings(p, sec, "N")
    ent = [d for d in got["faces"]["N"]["placed"] if d["kind"] == "door" and d.get("entrance")]
    assert len(ent) == 1, ent
    assert ent[0]["along_ft"] == pytest.approx(pair[by_plan][1]), (
        f"the elevation dresses the door at {ent[0]['along_ft']} ft; the placer's rule takes the "
        f"lower plan coordinate, {pair[by_plan][1]} ft")


# ------------------------------------------------------------------ driven: a dormer between two
def test_a_dormer_between_two_equally_central_windows_takes_the_one_the_plan_would(built):
    """A dormer is centred on an upper window, taken from the middle outward; with an even count of
    candidates two are equally central and the tie goes to the lower PLAN coordinate (WP-16.3). It
    went to the lower index, which on a face drawn as seen from outside is the other window: the
    flip would have moved a dormer to a different room. The Tidewater N face places two upper
    windows, so one declared dormer there is exactly that tie."""
    EL, ST, RF = _m("elevation"), _m("structure"), _m("roof")
    p, sec, rf, el, sc = built
    ups = [q for q in el["faces"]["N"]["placed"] if q["kind"] == "window" and q["storey"] == "upper"]
    assert len(ups) == 2, ("the premise: two upper windows on the N face make one dormer a tie", ups)
    want = min(ups, key=lambda q: q["along_ft"])
    other = max(ups, key=lambda q: q["along_ft"])
    assert want["u_ft"] > other["u_ft"], "the premise: on N the lower plan coordinate is the later u"
    q = copy.deepcopy(p)
    q.setdefault("declared", {})["dormer"] = {"count": 1, "face": "N"}
    s2 = ST.build_section(q, None, geometry_result=q)
    e2 = EL.build_elevation(q, None, section=s2, roof=RF.build_roof(q, None, section=s2))
    d = e2["dormers"]
    assert d.get("stated") and d.get("count") == 1 and not d.get("refused"), d
    assert d["positions_ft"] == [pytest.approx(want["u_ft"], abs=1e-6)], (
        f"the dormer stands at u = {d['positions_ft']}; the window at the lower plan coordinate "
        f"({want['room']}, {want['along_ft']} ft) is at u = {want['u_ft']}, the other "
        f"({other['room']}) at {other['u_ft']}")


# ------------------------------------------------------------------ driven: the stacks
def test_a_stack_on_a_mirrored_face_stands_where_its_window_would_be_refused(built):
    """`stack_axes_for_face` hands OQ 85's refusal of a window on a stack the stack's position along
    the face. The Tidewater stacks stand at the north end of each gable and no window stands near
    either, so a stack axis read in the plan's direction refuses nothing and says nothing: a stack
    is DRIVEN onto the W face's own upper window here, at the window's plan coordinate, and the
    window must be refused -- which it can be only if the axis and the window are read in one
    frame. The four faces' axes are held to the footprint's own numbers beside it."""
    EL = _m("elevation")
    p, sec, rf, el, sc = built
    fp = sec["footprint"]
    _Wc, _Dc, t = _dims(sec)
    W_out, D_out = _drawn_width("N", sec), _drawn_width("W", sec)
    chim = {"positions": [{"x_ft": 0.0, "y_ft": 10.0}, {"x_ft": fp["width_ft"], "y_ft": 10.0},
                          {"x_ft": 12.0, "y_ft": 0.0}, {"x_ft": 12.0, "y_ft": fp["depth_ft"]}]}
    assert EL.stack_axes_for_face("W", chim, fp) == [pytest.approx(D_out - 10.0, abs=1e-9)]
    assert EL.stack_axes_for_face("E", chim, fp) == [pytest.approx(10.0, abs=1e-9)]
    assert EL.stack_axes_for_face("S", chim, fp) == [pytest.approx(12.0, abs=1e-9)]
    assert EL.stack_axes_for_face("N", chim, fp) == [pytest.approx(W_out - 12.0, abs=1e-9)]

    win = next(r for r in EL.opening_rects(el, "W")["rects"] if r["kind"] == "window")
    e2 = copy.deepcopy(el)
    e2["faces"]["W"]["stack_axes_ft"] = EL.stack_axes_for_face(
        "W", {"positions": [{"x_ft": 0.0, "y_ft": win["along_ft"] + t}]}, fp)
    got = EL.opening_rects(e2, "W")
    assert not [r for r in got["rects"] if r["room"] == win["room"] and r["storey"] == win["storey"]
                and r["along_ft"] == win["along_ft"]], (
        f"a stack stands on the {win['room']} window's own axis and the window is still drawn")
    assert any(x.get("room") == win["room"] and x.get("cause") == "stack" for x in got["refused"]), \
        got["refused"]


def test_the_far_gables_stack_follows_the_rake_at_its_own_depth_on_a_mirrored_face(built):
    """The E gable's stack seen from the west stands behind the whole house and shows above the W
    gable's rake at its own depth (`stack_outline`'s gable-face branch). The Tidewater stacks stand
    north of the ridge, where the rake falls northward; on the W face, drawn as seen from outside,
    north is on the LEFT, so the stack's span is its depth measured from the north end and its
    foot is LOWER on the left. Read in the plan's direction the span and the slope both reverse."""
    EL = _m("elevation")
    p, sec, rf, el, sc = built
    fp = sec["footprint"]
    D_out = _drawn_width("W", sec)
    east = next(c for c in rf["chimneys"]["positions"] if c["x_ft"] > fp["width_ft"] / 2.0)
    x0, y0, x1, y1 = east["plan_rect_ft"]
    assert (y0 + y1) / 2.0 > D_out / 2.0 + 2.0, ("the premise: the stack stands north of the "
                                                 "ridge, off the gable's centre line", y0, y1)
    got = EL.stack_outline("W", east, rf, fp)
    assert got.get("relation") == "behind" and "outline" in got, got
    us = [u for u, _h in got["outline"]]
    assert min(us) == pytest.approx(D_out - y1, abs=1e-6) and max(us) == pytest.approx(D_out - y0, abs=1e-6), \
        (min(us), max(us), D_out - y1, D_out - y0)
    foot = got["outline"][2:]            # right to left, as every outline states it
    assert foot[-1][0] < foot[0][0], foot
    assert foot[-1][1] < foot[0][1], (
        f"the foot is not lower on the left (north) end: {foot}")


def test_the_scene_compares_the_entrance_and_not_the_first_door_on_its_face(built):
    """`scene._entrance_agreement` holds the drawn front door against the placed one. It took the
    FIRST door along the face, which on a face drawn as seen from outside is a different door from
    the plan's first; it takes the door the elevation dresses as the entrance now. On every shipped
    plan the entrance happens to be the first door in the face's own order, so a second door is
    DRIVEN to the face's left end here: the entrance must still be the one compared."""
    SC, EL = _m("scene"), _m("elevation")
    p, sec, rf, el, sc = built
    face = el["entrance_face"]

    def said(s):
        return [n for n in s["not_modelled"] if "axis.door_bay" in n["source"]]

    assert not said(sc), "the premise: the shipped record's two records of the front door agree"
    e2 = copy.deepcopy(el)
    doors = [q for q in e2["faces"][face]["placed"] if q["kind"] == "door" and q["storey"] == "ground"]
    other = next(q for q in doors if not q.get("entrance"))
    other["along_ft"] = 3.0
    other["u_ft"] = _expected_u(face, 3.0, sec)
    other["cx_in"] = other["u_ft"] * 12.0
    e2["faces"][face]["placed"].sort(key=lambda q: (q["storey"] != "ground", q["u_ft"]))
    first = next(r for r in EL.opening_rects(e2, face)["rects"] if r["kind"] == "door")
    assert not first.get("entrance"), "the premise: the first door on the face is not the entrance"
    s2 = SC.build_scene(p, sec, rf, e2)
    assert not said(s2), (
        "the scene compared the first door on the face, not the entrance, with the placed front "
        f"door: {said(s2)[0]['why'][:200]}")
