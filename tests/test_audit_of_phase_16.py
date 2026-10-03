"""THE AUDIT OF PHASE 16 (WP-16.8): guards for the fixes no other file holds.

Five auditors read Phase 16 at `e604955`. Each test here holds one finding fixed, and each was
mutation-checked against the fix it guards (the WP-16.8 report lists the mutations). The houses are
built on the heuristic engine, which is deterministic, and every solve takes a private cache.

- B1: a count resting on a date the record does not state is withheld, not a zero;
- B5: a hip draws no return, measured;
- A3: a rake the house does not draw says why, per house;
- A4: a light pattern the kit forbids is drawn and said;
- C6: the scene says the envelope bands it does not model;
- C7: the DXF draws the shutter leaves its record describes;
- C8: the section says a gambrel's ridge is the roof record's;
- C9: a roof form drawn from a judgment says so on the scene and the section (T3).
"""
import copy
import json
import os
import sys
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import modcache as mc  # noqa: E402


def _m(name):
    return mc.load(name, os.path.join(ROOT, "build", name + ".py"))


G, ST, RF, EL, SC = (_m("geometry"), _m("structure"), _m("roof"), _m("elevation"), _m("scene"))

SIDELIGHTS = "count_of_sidelights_drawn_at_the_entrance"
RETURNS = "count_of_cornice_returns_drawn_at_the_gable_ends"


def _full(pid, monkeypatch, date="as-stated", style=None):
    path = next(q for q in (os.path.join(ROOT, "plans", pid + ".json"),
                            os.path.join(ROOT, "plans", "reference", pid + ".json")) if os.path.exists(q))
    p = json.load(open(path, encoding="utf-8"))
    if date != "as-stated":
        ctx = p.setdefault("context", {})
        if date is None:
            ctx.pop("date_of_representation", None)
        else:
            ctx["date_of_representation"] = date
    monkeypatch.setattr(G, "_SOLVE_CACHE", {})
    q = G.solve(p, engine="heuristic")
    if style:
        q = copy.deepcopy(q)
        q["style"] = style
    sec = ST.build_section(q, None, geometry_result=q)
    rf = RF.build_roof(q, None, section=sec)
    return q, sec, rf, EL.build_elevation(q, None, section=sec, roof=rf)


# ------------------------------------------------------------------ B1: an undated house
class TestACountRestingOnAnUnstatedDateIsWithheld:
    def test_the_tidewater_sidelights_undated_are_withheld_and_dated_are_a_measured_zero(self, monkeypatch):
        """georgian-colonial-american forbids the sidelights for 1700-1780. Dated 1765 the front
        draws none and the count is a measured 0; undated, A3 keeps the ban in the drawing, and
        the count -- which made `sidelights-as-storefront-glass` not applicable -- is withheld."""
        _q, _s, _r, el = _full("tidewater-georgian-careful", monkeypatch, date=1765)
        assert el["measurements"].get(SIDELIGHTS) == 0
        _q, _s, _r, el = _full("tidewater-georgian-careful", monkeypatch, date=None)
        assert SIDELIGHTS not in el["measurements"]
        why = (el["front"].get("withheld") or {}).get(SIDELIGHTS) or ""
        assert "dated 1700-1780" in why and "states no date" in why, why

    @pytest.mark.parametrize("style", ["new-england-colonial", "saltbox-colonial", "garrison-colonial"])
    def test_a_return_resting_on_a_dated_none_is_withheld_on_an_undated_house(self, style, monkeypatch):
        """Each of the three makes `none` canonical for 1620-1700 alone; an undated house drew the
        end profile and was convicted of `return-that-never-returns` (serious) on that row."""
        _q, _s, _r, el = _full("tidewater-georgian-careful", monkeypatch, date=None, style=style)
        assert el["cornice_return"].get("date_unstated") is True
        assert RETURNS not in el["measurements"]
        assert "dated 1620-1700" in (el["front"].get("withheld") or {}).get(RETURNS, "")


# ------------------------------------------------------------------ B5 and A3: a hip, and the rake
class TestAHipDrawsNoReturnAndNoRake:
    def test_good05s_hip_measures_no_gable_and_no_return_and_says_why_it_has_no_rake(self, monkeypatch):
        _q, _s, rf, el = _full("good-05-lobby-gallery-mansion", monkeypatch)
        assert rf["main"]["form"] == "hip", "the premise: B1 hips good-05"
        m = el["measurements"]
        assert m.get("count_of_gable_end_walls") == 0 and m.get(RETURNS) == 0
        why = el["front"]["withheld"].get("rake_overhang_in", "")
        assert "draws no gable end" in why and "hip" in why, why

    def test_a_hip_whose_kit_is_silent_on_the_return_still_measures_no_return(self, monkeypatch):
        """The case B5 fixed: on a hipped house whose kit says nothing of the return, the band's
        default made the return count unmeasured, so the two shape faults read could-not-evaluate
        beside two gable faults reading not applicable on the same roof. good-05's kit FORBIDS its
        return, which reaches 0 by another route, so the silence is driven."""
        real = EL.RK.return_at
        monkeypatch.setattr(EL.RK, "return_at", lambda rec, date=None: real(None, date))
        _q, _s, rf, el = _full("good-05-lobby-gallery-mansion", monkeypatch)
        assert rf["main"]["form"] == "hip" and el["cornice_return"].get("state") == "silent"
        assert el["measurements"].get(RETURNS) == 0

    def test_an_unridged_gable_says_its_rake_is_not_drawn_and_names_the_style(self, monkeypatch):
        q, _s, rf, el = _full("spec-builder-colonial", monkeypatch)
        assert rf["main"]["ridge"].get("grade_to_ridge_ft") is None, "the premise: no ridge judged"
        why = el["front"]["withheld"].get("rake_overhang_in", "")
        assert "is not drawn: the roof judges no ridge" in why and q["style"] in why, why

    def test_a_drawn_rake_takes_the_standing_reason_alone(self, monkeypatch):
        _q, _s, _r, el = _full("tidewater-georgian-careful", monkeypatch)
        assert "rake_overhang_in" not in (el["front"].get("withheld") or {})
        assert "rake_overhang_in" in EL.NOT_MODELLED


# ------------------------------------------------------------------ A4: the lights
def test_a_light_pattern_the_kit_forbids_is_drawn_and_said(monkeypatch, tmp_path):
    """cape-cod-revival forbids 12/12 and 9/9, and the sash-light arithmetic draws 12/12 at the
    Tidewater's widths. R3 does not reach a pattern (no other pattern is stated for the width), so
    the face draws it and SAYS the ban, naming the writer."""
    _q, _s, _r, el = _full("tidewater-georgian-careful", monkeypatch, style="cape-cod-revival")
    assert set(el["lite_patterns_forbidden"]) >= {"12/12"}
    said = []
    for face in ("S", "N", "E", "W"):
        out = str(tmp_path / f"{face}.svg")
        _m("render_elevation").render_elevation(el, out, face=face)
        said.append(open(out, encoding="utf-8").read())
    assert any("LIGHTS DRAWN 12/12 — FORBIDDEN BY CAPE-COD-REVIVAL" in s for s in said)
    _q, _s, _r, el = _full("tidewater-georgian-careful", monkeypatch)
    for face in ("S", "N"):
        out = str(tmp_path / f"c{face}.svg")
        _m("render_elevation").render_elevation(el, out, face=face)
        assert "LIGHTS DRAWN" not in open(out, encoding="utf-8").read(), "the control's kit forbids none"


# ------------------------------------------------------------------ C6, C9: the scene
def test_the_scene_says_the_envelope_bands_it_does_not_model(monkeypatch):
    q, sec, rf, el = _full("tidewater-georgian-careful", monkeypatch)
    scene = SC.build_scene(q, sec, rf, el)
    said = {n["what"] for n in scene["not_modelled"] if n.get("class") == "envelope"}
    assert "the eave cornice" in said and "the water table" in said, said


def test_a_roof_drawn_from_a_judgment_says_so_on_the_scene_and_the_section(monkeypatch, tmp_path):
    """T3, taken as recommended under Lucas's standing instruction of 1 Oct 2026: a roof B1 draws
    from a kit record flagged `judgment: true` says so on every surface that draws the roof. The
    elevation, the roof plan and the DXF did at WP-16.9; the scene and the section did not. No
    shipped plan draws a ridged roof from a judgment (good-04's and good-06's judge no ridge), so
    the reading is driven onto the Tidewater roof, with the control first."""
    q, sec, rf, el = _full("tidewater-georgian-careful", monkeypatch)
    DI = _m("disclosures")
    assert DI.roof_form_judgment(rf) is None, "the control: a declared form is the record's own"
    scene = SC.build_scene(q, sec, rf, el)
    assert not [s for s in scene["judgment"] if s["what"] == "the roof form"]
    reading = {"by": "kit", "words": None, "kit": {"state": "kit", "form": "side-gable",
               "canonical": ["side-gable"], "judgment": True, "judgment_by": "somebody"}}
    rf, sec = copy.deepcopy(rf), copy.deepcopy(sec)
    rf["form_reading"] = reading
    sec["roof"]["form_reading"] = reading
    words = DI.roof_form_judgment(rf)
    assert words and "SOMEBODY'S KIT" in words
    scene = SC.build_scene(q, sec, rf, el)
    assert [s for s in scene["judgment"] if s["what"] == "the roof form" and s["why"] == words]
    out = str(tmp_path / "s.svg")
    _m("render_section").render_section(sec, out)
    assert "SOMEBODY" in open(out, encoding="utf-8").read().upper()


# ------------------------------------------------------------------ C8: the gambrel
def test_the_section_says_a_gambrels_ridge_is_the_roof_records(monkeypatch):
    _q, sec, rf, _el = _full("good-01-veranda-gallery-estate", monkeypatch)
    assert rf["main"]["form"] == "gambrel", "the premise: B1 draws good-01 as a gambrel"
    assert "gambrel" in sec["roof"]["note"] and "roof record" in sec["roof"]["note"], sec["roof"]["note"]


# ------------------------------------------------------------------ C7: the DXF's shutters
def test_the_dxf_draws_the_shutter_leaves_the_sheet_draws(monkeypatch):
    ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    _q, _s, _r, el = _full("spec-builder-colonial", monkeypatch)
    face = el["entrance_face"] if el.get("entrance_face") in ("S", "N", "E", "W") else "N"
    rects = EL.opening_rects(el, face)["rects"]
    leaved = [r for r in rects if r.get("shutter_leaf_width_in")]
    assert leaved, "the premise: the spec Colonial hangs shutters on this face"
    want = []
    for r in leaved:
        for lf in EL.shutter_leaves(r["x0_in"], r["x1_in"], r["head_in"], r.get("shutter_leaf_width_in"),
                                    r.get("shutter_leaf_height_in"), r.get("shutter_panel_count") or 0):
            want.append((round(lf["x0"], 2), round(lf["x1"], 2)))
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "e.dxf")
        _m("export_dxf").export_elevation_dxf(el, path, face=face)
        msp = ezdxf.readfile(path).modelspace()
        drawn = set()
        for e in msp.query("LWPOLYLINE"):
            xs = [p[0] for p in e.get_points()]
            drawn.add((round(min(xs), 2), round(max(xs), 2)))
    assert want and all(w in drawn for w in want), (sorted(set(want) - drawn)[:6], len(want))


# ------------------------------------------------------------------ the bands, found by attributing the audit's own sheets
class TestTheWaterTableAndTheBeltAreDrawnOnceEverywhere:
    """Found while attributing the audit's own moved sheets (WP-16.8). The scene's new envelope
    entries named a belt course on every one-storey house, where the sheet draws none, because it
    tested the belt's own depth and not the storey it stands on; and the CAD elevation had drawn
    neither band on any face since WP-5.1. `elevation.band_marks` is the one answer now."""

    def test_a_one_storey_house_draws_no_belt_and_the_scene_names_none(self, monkeypatch, tmp_path):
        q, sec, rf, el = _full("bad-01-grilling-porch-ranch", monkeypatch)
        assert len(sec["storeys"]) == 1, "the premise: one storey"
        assert el["water_table_belt"].get("belt_height_in") is not None, \
            "the premise: the record carries a belt depth, which is what the first version read"
        assert EL.band_marks(el)["belt"] is None and EL.band_marks(el)["water_table"]
        said = {n["what"] for n in SC.build_scene(q, sec, rf, el)["not_modelled"]
                if n.get("class") == "envelope"}
        assert "the belt course" not in said and "the water table" in said, said
        out = str(tmp_path / "S.svg")
        _m("render_elevation").render_elevation(el, out, face=el["entrance_face"])
        assert 'class="wt w-med"' not in open(out, encoding="utf-8").read()

    def test_a_two_storey_house_draws_its_belt_and_the_scene_names_it(self, monkeypatch, tmp_path):
        q, sec, rf, el = _full("spec-builder-colonial", monkeypatch)
        bm = EL.band_marks(el)
        assert bm["belt"] and bm["water_table"]
        said = {n["what"] for n in SC.build_scene(q, sec, rf, el)["not_modelled"]
                if n.get("class") == "envelope"}
        assert {"the belt course", "the water table"} <= said, said
        out = str(tmp_path / "S.svg")
        _m("render_elevation").render_elevation(el, out, face="S")
        assert open(out, encoding="utf-8").read().count('class="wt w-med"') == 1

    @pytest.mark.parametrize("pid", ["tidewater-georgian-careful", "spec-builder-colonial"])
    def test_the_dxf_draws_the_bands_the_sheet_draws_and_hides_them_behind_a_door(self, pid,
                                                                                monkeypatch):
        ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
        _q, _s, _r, el = _full(pid, monkeypatch)
        bm = EL.band_marks(el)
        fp = el["footprint"]
        doors_crossing = 0
        with tempfile.TemporaryDirectory() as td:
            for face in ("S", "N", "E", "W"):
                span = (fp["width_ft"] if face in ("S", "N") else fp["depth_ft"]) * 12.0
                want = []
                for key, lo, hi in (("water_table", 0.0, (bm["water_table"] or {}).get("top_in")),
                                    ("belt", (bm["belt"] or {}).get("bottom_in"), None)):
                    b = bm[key]
                    if not b:
                        continue
                    h0 = lo if key == "water_table" else b["bottom_in"]
                    h1 = hi if key == "water_table" else b["bottom_in"] + b["height_in"]
                    want.append((round(-b["projection_in"], 2), round(span + b["projection_in"], 2),
                                 round(h0, 2), round(h1, 2)))
                path = os.path.join(td, f"{face}.dxf")
                _m("export_dxf").export_elevation_dxf(el, path, face=face)
                msp = ezdxf.readfile(path).modelspace()
                drawn = []
                for e in msp.query("LWPOLYLINE"):
                    if e.dxf.layer != "TDL-ELEV-BAND":
                        continue
                    xs, ys = [p[0] for p in e.get_points()], [p[1] for p in e.get_points()]
                    drawn.append((round(min(xs), 2), round(max(xs), 2), round(min(ys), 2),
                                  round(max(ys), 2)))
                assert sorted(drawn) == sorted(want), (face, drawn, want)
                wipes = [[(round(v[0], 2), round(v[1], 2)) for v in w.boundary_path_wcs()]
                         for w in msp.query("WIPEOUT")]
                for r in EL.opening_rects(el, face)["rects"]:
                    crosses = any(min(r["head_in"], w[3]) - max(r["sill_in"], w[2]) > 1e-6
                                  and min(r["x1_in"], w[1]) - max(r["x0_in"], w[0]) > 1e-6
                                  for w in want)
                    if not crosses:
                        continue
                    doors_crossing += 1
                    corners = {(round(r["x0_in"], 2), round(r["sill_in"], 2)),
                               (round(r["x1_in"], 2), round(r["head_in"], 2))}
                    assert any(corners <= set(w) for w in wipes), (face, r.get("id"), "not masked")
        assert doors_crossing >= 2, "the premise: doors on these fronts cross the water table"
