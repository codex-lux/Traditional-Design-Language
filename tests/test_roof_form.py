"""WP-16.9: a roof the record does not name (Lucas's answer B1, 30 Sep 2026).

"After the plan's own declaration and before the massing's default, the roof takes the canonical
`roof_form` of the style's resolved kit, through a closed table onto the forms the roof layer draws.
Side-gable is kept where it is canonical; a style with no canonical form keeps the fallback, and the
sheet says so." Until B1 the kit was never read: twelve of the sixteen shipped roofs were drawn in a
form their kit does not make canonical, nine by the fallback.

The kit reading and the fallback are driven here, each case asserting its premise, because which
shipped plan reaches which branch moves with the kits (the inherited roof records B1 adjudicates).
"""
import copy
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import modcache as mc  # noqa: E402
import inkread as IR  # noqa: E402


def _m(name):
    return mc.load(name, os.path.join(ROOT, "build", name + ".py"))


TH = _m("threshold")
RV = _m("roof_vocabulary")
RF = _m("roof")
EL = _m("elevation")

TIDEWATER = os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")


def _plan(style=None, massing=None, declared=True):
    p = json.load(open(TIDEWATER, encoding="utf-8"))
    if style:
        p["style"] = style
    if massing is not None:
        p["massing"] = massing
    if not declared:
        p["declared"] = {k: v for k, v in (p.get("declared") or {}).items() if k != "roof_form"}
    return p


def _drive(monkeypatch, rows, style="driven-style", keep=False):
    """A style whose resolved `roof_form` is exactly `rows`, read through `kit_roof`'s own cache.
    `keep` keeps the style's other resolved slots, for a fixture that draws the whole house."""
    rec = {"binding": "specified", "_bound_by": style,
           "variants": [dict(r, _written_by=r.get("_written_by", style)) for r in rows]}
    rest = dict(TH.resolved_slots(style) or {}) if keep else {}
    monkeypatch.setitem(TH._RESOLVED, style, dict(rest, roof_form=rec))
    return style


# ------------------------------------------------------------------ the kit, read through the closed table
class TestTheKitsRoof:
    def test_one_canonical_form_is_drawn(self, monkeypatch):
        s = _drive(monkeypatch, [{"id": "hipped", "status": "canonical"},
                                 {"id": "front-gable", "status": "forbidden"}])
        kr = TH.kit_roof(s)
        assert (kr["state"], kr["form"], kr["canonical"], kr["writers"]) == ("kit", "hip", ["hipped"], [s])

    def test_side_gable_is_kept_where_it_is_one_of_several(self, monkeypatch):
        s = _drive(monkeypatch, [{"id": "hip", "status": "canonical"},
                                 {"id": "side-gable", "status": "canonical"}])
        assert (TH.kit_roof(s)["state"], TH.kit_roof(s)["form"]) == ("kit", "side-gable")

    def test_several_without_side_gable_is_not_chosen(self, monkeypatch):
        s = _drive(monkeypatch, [{"id": "hip", "status": "canonical"},
                                 {"id": "front-gable", "status": "canonical"}])
        kr = TH.kit_roof(s)
        assert (kr["state"], kr["form"]) == ("several", None)
        assert "front-gable or hip" in kr["why"] and "not ruled" in kr["why"]

    def test_two_rows_that_are_one_form_are_one_form(self, monkeypatch):
        s = _drive(monkeypatch, [{"id": "hip", "status": "canonical"},
                                 {"id": "low-hip", "status": "canonical"}])
        assert (TH.kit_roof(s)["state"], TH.kit_roof(s)["form"]) == ("kit", "hip")

    def test_an_undrawable_form_is_said_with_the_tables_reason(self, monkeypatch):
        s = _drive(monkeypatch, [{"id": "mansard", "status": "canonical"}])
        kr = TH.kit_roof(s)
        assert (kr["state"], kr["form"]) == ("undrawable", None)
        assert RV.TABLE["mansard"][0] is None and RV.TABLE["mansard"][1] in kr["why"]

    def test_a_permitted_row_decides_nothing_and_a_dated_one_only_at_its_date(self, monkeypatch):
        s = _drive(monkeypatch, [{"id": "hip", "status": "permitted"}])
        assert TH.kit_roof(s)["state"] == "silent"
        s = _drive(monkeypatch, [{"id": "hip", "status": "canonical",
                                  "applies_when": {"date_range": [1700, 1780]}}], style="dated-style")
        assert TH.kit_roof(s, 1750)["form"] == "hip"
        assert TH.kit_roof(s, 1850)["state"] == "silent"

    def test_a_style_whose_kit_cannot_be_resolved_is_unresolved(self, monkeypatch):
        monkeypatch.setitem(TH._RESOLVED, "no-such-style", None)
        kr = TH.kit_roof("no-such-style")
        assert (kr["state"], kr["form"]) == ("unresolved", None)


# ------------------------------------------------------------------ what the roof is drawn as, and who said so
class TestTheReading:
    def test_the_declaration_governs_and_says_nothing(self):
        r = TH.roof_form_reading(_plan(), RF._massing("four-over-four"))
        assert (r["form"], r["by"], r["words"]) == ("side-gable", "declared", None)

    def test_an_undeclared_roof_takes_the_kits_form(self, monkeypatch):
        s = _drive(monkeypatch, [{"id": "hip", "status": "canonical"}])
        r = TH.roof_form_reading(_plan(style=s, declared=False), RF._massing("four-over-four"))
        assert (r["form"], r["by"], r["words"]) == ("hip", "kit", None)
        assert r["note"] == f"No roof_form declared; {s}'s kit makes hip canonical, drawn as hip (B1)."

    def test_the_massings_default_where_the_kit_decides_nothing_and_the_words_say_so(self, monkeypatch):
        s = _drive(monkeypatch, [{"id": "mansard", "status": "canonical"}])
        ms = RF._massing("four-over-four")
        assert ms.get("roof_default"), "the premise: four-over-four states a roof default"
        r = TH.roof_form_reading(_plan(style=s, declared=False), ms)
        assert (r["form"], r["by"]) == (ms["roof_default"][0], "massing")
        assert r["words"].startswith(f"ROOF: {ms['roof_default'][0].upper()}, MASSING FOUR-OVER-FOUR'S "
                                     f"DEFAULT — THE PLAN DECLARES NO ROOF FORM, AND {s.upper()}'S KIT "
                                     "MAKES MANSARD CANONICAL, WHICH THE ROOF LAYER DOES NOT DRAW")

    def test_no_massing_is_the_roof_layers_default_and_names_no_massing(self, monkeypatch):
        s = _drive(monkeypatch, [])
        r = TH.roof_form_reading(_plan(style=s, massing=None, declared=False), {})
        assert (r["form"], r["by"]) == (TH.DEFAULT_ROOF_FORM, "default")
        assert "massing 'None'" not in r["note"] and "the plan naming no massing" in r["note"]
        assert r["words"] == (f"ROOF: {TH.DEFAULT_ROOF_FORM.upper()}, THE ROOF LAYER'S DEFAULT — THE PLAN "
                              f"DECLARES NO ROOF FORM, AND {s.upper()}'S KIT MAKES NO ROOF FORM CANONICAL")
        # and a declared form on a record naming no massing is not held against a list it has not got
        p = _plan(style=s, massing=None)
        p["declared"]["roof_form"] = "hip"
        assert TH.roof_form_reading(p, {})["note"] is None

    def test_roof_form_for_is_the_readings_pair(self, monkeypatch):
        s = _drive(monkeypatch, [{"id": "gable-front", "status": "canonical"}])
        p, ms = _plan(style=s, declared=False), RF._massing("four-over-four")
        r = TH.roof_form_reading(p, ms)
        assert TH.roof_form_for(p, ms) == (r["form"], r["note"]) == ("front-gable", r["note"])


# ------------------------------------------------------------------ B7 and B8: the fallback, ruled
class TestTheFallbackIsRuled:
    def test_several_forms_without_side_gable_draw_the_fallback_and_say_which_are_canonical(self, monkeypatch):
        """B7 (Lucas, 30 Sep 2026): where several canonical forms remain and none is side-gable,
        neither is chosen; the fallback is drawn, and the sheet names the canonical forms and says
        which is drawn is not ruled."""
        s = _drive(monkeypatch, [{"id": "hip", "status": "canonical"},
                                 {"id": "front-gable", "status": "canonical"}])
        ms = RF._massing("four-over-four")
        assert ms["roof_default"][0] == "side-gable", "the premise: the massing's fallback is side-gable"
        r = TH.roof_form_reading(_plan(style=s, declared=False), ms)
        assert (r["form"], r["by"]) == ("side-gable", "massing")
        assert r["words"] == ("ROOF: SIDE-GABLE, MASSING FOUR-OVER-FOUR'S DEFAULT — THE PLAN DECLARES NO "
                              f"ROOF FORM, AND {s.upper()}'S KIT MAKES HIP, FRONT-GABLE CANONICAL, WHICH THE "
                              "ROOF LAYER DRAWS AS FRONT-GABLE OR HIP, AND WHICH OF THEM IS DRAWN IS NOT RULED")

    @pytest.mark.parametrize("rows", [
        [],
        [{"id": "mansard", "status": "canonical"}],
        [{"id": "hip", "status": "canonical"}, {"id": "front-gable", "status": "canonical"}],
    ], ids=["silent", "undrawable", "several"])
    def test_a_fallback_the_kit_forbids_is_refused_and_said(self, monkeypatch, rows):
        """B8 (Lucas, 30 Sep 2026): R3's reading. Whatever left the roof to the fallback -- a kit that
        says nothing, one whose forms the roof layer does not draw, several forms (B7) -- a fallback
        the style's resolved kit forbids is not drawn, and the words say both halves."""
        s = _drive(monkeypatch, rows + [{"id": "side-gable", "status": "forbidden", "_written_by": "w-writer"}])
        p, ms = _plan(style=s, declared=False), RF._massing("four-over-four")
        r = TH.roof_form_reading(p, ms)
        assert (r["form"], r["by"]) == (None, "refused")
        assert r["words"].startswith("NO ROOF DRAWN — THE PLAN DECLARES NO ROOF FORM, ")
        assert r["words"].endswith("AND SIDE-GABLE, THE FALLBACK, IS FORBIDDEN BY W-WRITER")
        assert "(B8)" in r["note"] and TH.roof_form_for(p, ms) == (None, r["note"])

    def test_a_forbidden_row_that_is_not_the_fallback_refuses_nothing(self, monkeypatch):
        s = _drive(monkeypatch, [{"id": "mansard", "status": "canonical"},
                                 {"id": "hip", "status": "forbidden"}])
        r = TH.roof_form_reading(_plan(style=s, declared=False), RF._massing("four-over-four"))
        assert (r["form"], r["by"]) == ("side-gable", "massing")

    def test_a_dated_ban_on_the_fallback_is_read_at_the_house_date(self, monkeypatch):
        s = _drive(monkeypatch, [{"id": "mansard", "status": "canonical"},
                                 {"id": "side-gable", "status": "forbidden",
                                  "applies_when": {"date_range": [1700, 1780]}}])
        for year, want in ((1750, "refused"), (1850, "massing")):
            p = _plan(style=s, declared=False)
            p.setdefault("context", {})["date_of_representation"] = year
            assert TH.roof_form_reading(p, RF._massing("four-over-four"))["by"] == want, year

    def test_a_declared_form_is_drawn_whatever_the_kit_forbids(self, monkeypatch):
        """B8 refuses a FALLBACK. A record stating a form its kit forbids is drawn as stated -- the
        declaration governs (B1) -- and the disagreement is the style layer's to report."""
        s = _drive(monkeypatch, [{"id": "side-gable", "status": "forbidden"}])
        r = TH.roof_form_reading(_plan(style=s), RF._massing("four-over-four"))
        assert (r["form"], r["by"]) == ("side-gable", "declared")


class TestTheRefusedRoofDrawnEndToEnd:
    @pytest.fixture
    def refused(self, monkeypatch, tmp_path):
        """The Tidewater house with no declared form, its kit patched to make a mansard canonical and
        forbid the fallback: every surface of a refused roof, driven, because no shipped record
        reaches B8 (the three styles that do are drawn by no shipped plan)."""
        s = _drive(monkeypatch, [{"id": "mansard", "status": "canonical"},
                                 {"id": "side-gable", "status": "forbidden", "_written_by": "w-writer"}],
                   style="tidewater-georgian", keep=True)
        assert TH.resolved_slots(s).get("chimney"), "the premise: the style's other slots are kept"
        G, ST = _m("geometry"), _m("structure")
        monkeypatch.setattr(G, "_SOLVE_CACHE", {})
        p = G.solve(_plan(declared=False), engine="heuristic")
        assert TH.roof_form_reading(p, RF._massing(p.get("massing")))["by"] == "refused"
        sec = ST.build_section(p, None, geometry_result=p)
        rf = RF.build_roof(p, None, section=sec)
        return s, p, rf, EL.build_elevation(p, None, section=sec, roof=rf)

    def test_the_roof_record_draws_nothing_above_the_wall_line(self, refused):
        _s, _p, rf, _el = refused
        main = rf["main"]
        assert main["form"] is None and "ridge" not in main and main["refused"]["why"] == main["note"]
        assert {o["kind"] for o in rf["outline"]} == {"eave"}
        eave = main["grade_to_eave_ft"]
        for face, prof in rf["elevation_profiles"].items():
            assert {h for _u, h in prof} == {eave}, face
        assert rf["form_reading"]["by"] == "refused"

    def test_no_gable_end_no_rake_and_no_stack(self, refused):
        _s, p, rf, el = refused
        # unjudged, never "no gable end" (WP-16.8, auditor B): the roof is refused, not a hip
        assert EL.gable_faces(rf) is None and el["measurements"].get("count_of_gable_end_walls") is None
        for face in ("S", "N", "W", "E"):
            assert EL.rake_marks(el, face)["bands"] == [], face
        stacks = [u for u in (p.get("hearths") or {}).get("unplaced") or [] if u.get("what") == "the stacks"]
        assert len(stacks) == 1 and stacks[0]["reason"].startswith("no roof is drawn -- ")
        assert not (p.get("hearths") or {}).get("stacks")

    def test_every_sheet_says_it_and_none_says_a_roof_stands_on_its_frieze(self, refused, tmp_path):
        _s, _p, rf, el = refused
        words = " ".join(rf["form_reading"]["words"].split())
        for face in ("S", "N", "W", "E"):
            out = str(tmp_path / f"e-{face}.svg")
            _m("render_elevation").render_elevation(el, out, face=face)
            said = " ".join(" ".join(t.split()) for t, _a, _i in IR.Ink(open(out, encoding="utf-8").read()).texts() if t)
            assert words in said, face
            assert "ROOF DRAWN ON THIS SHEET" not in said.upper(), face
        out = str(tmp_path / "roof.svg")
        _m("render_roof").render_roof(rf, out)
        said = " ".join(" ".join(t.split()) for t, _a, _i in IR.Ink(open(out, encoding="utf-8").read()).texts() if t)
        assert words in said

    def test_the_section_raises_no_ridge_over_it_and_its_sheet_says_no_roof_is_drawn(self, refused, tmp_path):
        """The audit of WP-16.8's own diff, auditor C (W2): C1 made the section carry the refusal --
        no ridge, the refusal's own words, NO ROOF DRAWN where it printed RIDGE UNJUDGED -- and this
        fixture built that section and nothing read it, so raising a ridge over a refused roof, or
        heading it RIDGE UNJUDGED, left the class green."""
        _s, p, rf, _el = refused
        sec = _m("structure").build_section(p, None, geometry_result=p)
        r = sec["roof"]
        assert r.get("grade_to_ridge_ft") is None and r["refused"]["why"] == rf["main"]["refused"]["why"]
        out = str(tmp_path / "section.svg")
        _m("render_section").render_section(sec, out)
        said = " ".join(" ".join(t.split()) for t, _a, _i in IR.Ink(open(out, encoding="utf-8").read()).texts() if t)
        assert "NO ROOF DRAWN" in said and "RIDGE UNJUDGED" not in said, said[:200]

    def test_the_section_dxf_says_no_roof_is_drawn(self, refused, tmp_path):
        """The same, in the CAD file: the section DXF heads the refusal NO ROOF DRAWN (auditor D,
        D10). SPLIT 3 OCT 2026 from the IFC half below, which had skipped it: this half needs
        ezdxf, which CI installs, and the IFC half ifcopenshell, which CI does not, so while the
        two shared one body CI judged neither."""
        ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
        _s, p, rf, _el = refused
        sec = _m("structure").build_section(p, None, geometry_result=p)
        path = str(tmp_path / "section.dxf")
        assert "error" not in _m("export_dxf").export_section_dxf(sec, path)
        notes = [" ".join(e.plain_text().split()) for e in ezdxf.readfile(path).modelspace().query("MTEXT")]
        assert any(n.startswith("NO ROOF DRAWN - ") for n in notes), notes
        assert not any(n.startswith("RIDGE UNJUDGED") for n in notes), notes

    def test_the_ifc_says_no_roof_is_drawn(self, refused, tmp_path):
        """The IFC's roof says the refusal where it said "form 'None' is not modelled by WP-5.1"
        (auditor D, D10). Judged only where ifcopenshell is installed, which CI's jobs are not."""
        ios = pytest.importorskip("ifcopenshell", reason="COULD NOT EVALUATE: ifcopenshell is not installed")
        import ifcopenshell.util.element as uel
        _s, p, rf, _el = refused
        ifc = str(tmp_path / "out.ifc")
        res = _m("export_ifc").export_ifc(copy.deepcopy(p), ifc, geometry_result=copy.deepcopy(p))
        assert "error" not in res, res
        ps = uel.get_psets(ios.open(ifc).by_type("IfcRoof")[0]).get("TDL") or {}
        assert ps["geometry_note"].startswith("no roof is drawn on this house: " + rf["main"]["refused"]["why"]), \
            ps["geometry_note"][:120]
        assert "form 'None'" not in ps["geometry_note"]


class TestTheStacksSayWhoChoseTheHip:
    def test_a_hip_the_kit_chose_is_not_called_declared(self, monkeypatch):
        """Until B1 every form `hearth_pass` read was the record's, and its refusal of a stack on a
        hipped roof said "the declared roof form is 'hip'". A hip the style's kit chose is said to
        be the kit's, naming whose (WP-16.9)."""
        s = _drive(monkeypatch, [{"id": "hip", "status": "canonical", "_written_by": "georgian-colonial-american"}],
                   style="tidewater-georgian", keep=True)
        G = _m("geometry")
        monkeypatch.setattr(G, "_SOLVE_CACHE", {})
        q = G.solve(_plan(declared=False), engine="heuristic")
        why = [u["reason"] for u in (q.get("hearths") or {}).get("unplaced") or [] if u.get("what") == "the stacks"]
        assert why == ["the roof form georgian-colonial-american's kit makes canonical is 'hip', which has no "
                       "full gable-end wall to run a stack through -- the same refusal build/roof.py makes, "
                       "and for the same reason"], why
        q = G.solve(dict(_plan(), id="declared-hip", declared=dict(_plan()["declared"], roof_form="hip")),
                    engine="heuristic")
        why = [u["reason"] for u in (q.get("hearths") or {}).get("unplaced") or [] if u.get("what") == "the stacks"]
        assert why and why[0].startswith("the declared roof form is 'hip'"), why


class TestTheStacksTheRoofPlacesNoneOfAreSaid:
    """WP-16.9. `roof.chimney_positions` answers `applicable: True` with no position and a note
    where the style calls for chimneys and the roof cannot stand one; no surface printed that note.
    B1 hips every house whose kit makes the hip canonical, so it reached every such house."""

    def test_the_sentence_is_the_roof_records_own_note_and_only_where_a_stack_is_owed(self):
        D = _m("disclosures")
        note = "Placement source calls for gable-end chimneys,   but the roof form here is 'hip'."
        assert D.stacks_the_roof_refuses({"chimneys": {"applicable": True, "positions": [], "note": note}}) == (
            "STACKS NOT DRAWN — PLACEMENT SOURCE CALLS FOR GABLE-END CHIMNEYS, BUT THE ROOF FORM HERE IS 'HIP'.")
        for ch in ({"applicable": False, "positions": [], "note": note},
                   {"applicable": True, "positions": [{"x_ft": 1}], "note": note},
                   {"applicable": True, "positions": [], "note": None}, {}):
            assert D.stacks_the_roof_refuses({"chimneys": ch}) is None, ch
        assert D.stacks_the_roof_refuses(None) is None

    def test_a_hipped_house_says_it_on_every_face_the_dxf_and_the_roof_plan(self, monkeypatch, tmp_path):
        s = _drive(monkeypatch, [{"id": "hip", "status": "canonical", "_written_by": "georgian-colonial-american"}],
                   style="tidewater-georgian", keep=True)
        G, ST = _m("geometry"), _m("structure")
        monkeypatch.setattr(G, "_SOLVE_CACHE", {})
        p = G.solve(_plan(declared=False), engine="heuristic")
        sec = ST.build_section(p, None, geometry_result=p)
        rf = RF.build_roof(p, None, section=sec)
        el = EL.build_elevation(p, None, section=sec, roof=rf)
        assert (rf["main"]["form"], rf["chimneys"]["positions"]) == ("hip", []), "the premise"
        words = _m("disclosures").stacks_the_roof_refuses(rf)
        assert words and "'HIP', WHICH HAS NO FULL GABLE-END WALL" in words, words
        for face in ("S", "N", "W", "E"):
            assert words in EL.face_notes(el, face), face
        out = str(tmp_path / "roof.svg")
        _m("render_roof").render_roof(rf, out)
        said = " ".join(" ".join(t.split()) for t, _a, _i in IR.Ink(open(out, encoding="utf-8").read()).texts() if t)
        assert words in said


# ------------------------------------------------------------------ one ridge axis for every reader
class TestOneRidgeAxis:
    @pytest.mark.parametrize("form,W,D,want", [
        ("side-gable", 50, 30, "x"), ("hip", 50, 30, "x"), ("front-gable", 50, 30, "y"),
        ("gable", 50, 30, "y"), ("cross-gable", 50, 30, "x"),
        ("gambrel", 50, 30, "x"), ("gambrel", 30, 50, "y"), ("gambrel", 40, 40, "x")])
    def test_the_axis(self, form, W, D, want):
        assert TH.ridge_axis(form, W, D) == want

    @pytest.mark.parametrize("form,front,want", [
        ("side-gable", "S", "x"), ("side-gable", "N", "x"), ("side-gable", "W", "y"), ("side-gable", "E", "y"),
        ("cross-gable", "W", "y"), ("front-gable", "S", "y"), ("front-gable", "W", "x"),
        ("gable", "E", "x"), ("hip", "W", "x"), ("gambrel", "W", "x")])
    def test_side_and_front_are_read_from_the_entrance(self, form, front, want):
        """B9 (Lucas, 30 Sep 2026): a side-gable's ridge runs parallel to the entrance wall and a
        front-gable's perpendicular to it. The gambrel keeps its own rule, the longer dimension."""
        assert TH.ridge_axis(form, 50, 30, front) == want

    @pytest.mark.parametrize("form", ["gambrel", "cross-gable", "side-gable", "front-gable"])
    @pytest.mark.parametrize("wide", [True, False])
    @pytest.mark.parametrize("front", ["S", "W"])
    def test_the_roof_and_the_stacks_read_one_axis(self, form, wide, front, monkeypatch):
        """UNTIL WP-16.9 roof.py ran a gambrel's ridge along the longer dimension and a cross-gable's
        along x, and the stacks' reader answered 'y' for both: the gable ends and the stacks stood
        on different walls. The roof record and `hearth_pass`'s axis are one reading now, the
        entrance's included (B9)."""
        ST = _m("structure")
        p = json.load(open(TIDEWATER, encoding="utf-8"))
        p["declared"]["roof_form"] = form
        p.setdefault("context", {})["entrance_faces"] = front
        sec = ST.build_section(p)
        W, D = sec["footprint"]["width_ft"], sec["footprint"]["depth_ft"]
        if not wide:
            sec = copy.deepcopy(sec)
            sec["footprint"]["width_ft"], sec["footprint"]["depth_ft"] = min(W, D), max(W, D)
            W, D = min(W, D), max(W, D)
        main = RF.main_roof(p, sec, p["style"])
        assert main["ridge"]["axis"] == TH.ridge_axis(form, W, D, front), (form, W, D, front)

    def test_a_house_entered_on_the_west_puts_its_gable_ends_and_its_stacks_on_s_and_n(self, monkeypatch):
        """good-03 is entered on the west and its side-gable roof drew a gable end on its entrance
        face until B9. Driven on the Tidewater record, its fires stripped so the stacks stand at the
        gable ends the roof's own axis names rather than on stated flues."""
        G, ST = _m("geometry"), _m("structure")
        monkeypatch.setattr(G, "_SOLVE_CACHE", {})
        p = json.load(open(TIDEWATER, encoding="utf-8"))
        p.setdefault("context", {})["entrance_faces"] = "W"
        for lv in p["levels"]:
            for r in lv["rooms"]:
                r.pop("hearth", None)
        q = G.solve(p, engine="heuristic")
        he = q.get("hearths") or {}
        assert he.get("placed_from") == "centre-line", "the premise: no stated fire decides a stack"
        sec = ST.build_section(q, None, geometry_result=q)
        rf = RF.build_roof(q, None, section=sec)
        assert (rf["main"]["form"], rf["main"]["ridge"]["axis"]) == ("side-gable", "y")
        assert EL.gable_faces(rf) == ("S", "N")
        assert {s["wall"] for s in he.get("stacks") or []} == {"S", "N"}


# ------------------------------------------------------------------ the closed table
class TestTheTable:
    def test_the_table_is_total_and_every_quote_is_where_it_says(self):
        assert RV.check_table(ROOT) == []
        assert set(RV.FORMS) == {"gable", "side-gable", "front-gable", "hip", "gable-on-hip",
                                 "cross-gable", "gambrel"}

    def test_every_form_the_table_names_is_one_the_roof_layer_draws(self):
        src = open(os.path.join(ROOT, "build", "roof.py"), encoding="utf-8").read()
        for f in RV.FORMS:
            assert f'"{f}"' in src, f

    def test_a_row_the_table_does_not_carry_fails_the_check(self, tmp_path, monkeypatch):
        monkeypatch.setitem(RV.TABLE, "a-roof-nobody-uses", ("hip", "why", ("kits/x.kit.json", "f", "t")))
        errs = RV.check_table(ROOT)
        assert any("a-roof-nobody-uses" in e and "no kit uses" in e for e in errs)
        monkeypatch.delitem(RV.TABLE, "a-roof-nobody-uses")
        monkeypatch.delitem(RV.TABLE, "hip")
        assert any("'hip' is used by a kit and is not in" in e for e in RV.check_table(ROOT))

    def test_a_quote_moved_off_its_field_fails_the_check(self, monkeypatch):
        form, why, (rel, field, text) = RV.TABLE["hip"]
        monkeypatch.setitem(RV.TABLE, "hip", (form, why, (rel, field, text + " and some words it never said")))
        assert any("'hip' quotes" in e for e in RV.check_table(ROOT))


# ------------------------------------------------------------------ the sheets say a fallback
class TestTheSheetsSayAFallback:
    def _elev(self, monkeypatch, tmp_path):
        s = _drive(monkeypatch, [{"id": "mansard", "status": "canonical"}], style="tidewater-georgian")
        G, ST = _m("geometry"), _m("structure")
        # A TEST THAT PATCHES WHAT A SOLVE READS GIVES THE SOLVE A PRIVATE CACHE (CLAUDE.md): the
        # placement's stack pass reads the patched kit, and its result must not outlive the patch
        monkeypatch.setattr(G, "_SOLVE_CACHE", {})
        p = G.solve(_plan(declared=False), engine="heuristic")
        assert TH.kit_roof(s)["state"] == "undrawable"
        sec = ST.build_section(p, None, geometry_result=p)
        rf = RF.build_roof(p, None, section=sec)
        return rf, EL.build_elevation(p, None, section=sec, roof=rf)

    def test_the_roof_record_carries_who_decided_beside_its_answer(self, monkeypatch, tmp_path):
        rf, _el = self._elev(monkeypatch, tmp_path)
        assert rf["form_reading"]["by"] in ("massing", "default")
        assert "form_by" not in rf["main"] and "form_words" not in rf["main"]
        assert rf["form_reading"]["words"].startswith("ROOF: ")

    def test_the_elevation_and_the_roof_plan_print_it(self, monkeypatch, tmp_path):
        rf, el = self._elev(monkeypatch, tmp_path)
        words = rf["form_reading"]["words"]
        assert words in EL.face_notes(el, "S")
        out = str(tmp_path / "roof.svg")
        _m("render_roof").render_roof(rf, out)
        said = " ".join(" ".join(t.split()) for t, _a, _i in IR.Ink(open(out, encoding="utf-8").read()).texts() if t)
        assert " ".join(words.split()) in said


# ------------------------------------------------------------------ a roof drawn from a judgment, said (T3)
class TestARoofFromAJudgmentIsSaid:
    """T3 (taken as recommended under Lucas's standing instruction of 1 Oct 2026; the question was
    put at 00:34 UTC and unanswered when the instruction arrived): a roof drawn from a kit record its
    writer flags `judgment: true` says so on the roof plan and on every face -- which the DXF
    writes -- naming the record's writer, in one spelling (`disclosures.roof_form_judgment`). A
    declared form, a fallback and an unflagged record say nothing of it."""

    def _flag(self, monkeypatch, rows, flag, style="driven-style", keep=False):
        s = _drive(monkeypatch, rows, style=style, keep=keep)
        TH._RESOLVED[s]["roof_form"]["judgment"] = flag
        return s

    def test_kit_roof_carries_the_flag_and_who_bound_it(self, monkeypatch):
        s = self._flag(monkeypatch, [{"id": "hip", "status": "canonical"}], True)
        kr = TH.kit_roof(s)
        assert (kr["form"], kr["judgment"], kr["judgment_by"]) == ("hip", True, s)
        s2 = self._flag(monkeypatch, [{"id": "hip", "status": "canonical"}], False, style="another-style")
        assert (TH.kit_roof(s2)["judgment"], TH.kit_roof(s2)["judgment_by"]) == (False, None)

    def test_the_sentence_only_where_the_kit_decided_the_form(self):
        D = _m("disclosures")
        kr = {"judgment": True, "judgment_by": "colonial-revival", "canonical": ["side-gable", "hip"]}
        assert D.roof_form_judgment({"form_reading": {"by": "kit", "kit": kr}}) == (
            "ROOF FORM IS A JUDGMENT — COLONIAL-REVIVAL'S KIT MAKES SIDE-GABLE, HIP CANONICAL AND MARKS "
            "THE CALL A JUDGMENT")
        for fr in ({"by": "declared", "kit": kr}, {"by": "massing", "kit": kr}, {"by": "default", "kit": kr},
                   {"by": "refused", "kit": kr}, {"by": "kit", "kit": dict(kr, judgment=False)},
                   {"by": "kit", "kit": None}, {}):
            assert D.roof_form_judgment({"form_reading": fr}) is None, fr
        assert D.roof_form_judgment(None) is None

    def _house(self, monkeypatch, flag, declared=False):
        self._flag(monkeypatch, [{"id": "side-gable", "status": "canonical"}], flag,
                   style="tidewater-georgian", keep=True)
        G, ST = _m("geometry"), _m("structure")
        monkeypatch.setattr(G, "_SOLVE_CACHE", {})
        p = G.solve(_plan(declared=declared), engine="heuristic")
        sec = ST.build_section(p, None, geometry_result=p)
        rf = RF.build_roof(p, None, section=sec)
        return rf, EL.build_elevation(p, None, section=sec, roof=rf)

    def _said(self, rf, el, tmp_path):
        out = str(tmp_path / "roof.svg")
        _m("render_roof").render_roof(rf, out)
        plate = " ".join(" ".join(t.split()) for t, _a, _i in IR.Ink(open(out, encoding="utf-8").read()).texts() if t)
        return plate, {f: EL.face_notes(el, f) for f in ("S", "N", "W", "E")}

    def test_a_judged_roof_says_it_on_every_face_and_the_roof_plan(self, monkeypatch, tmp_path):
        rf, el = self._house(monkeypatch, True)
        assert rf["form_reading"]["by"] == "kit", "the premise: the kit decided the form"
        words = _m("disclosures").roof_form_judgment(rf)
        assert words and "TIDEWATER-GEORGIAN'S KIT MAKES SIDE-GABLE CANONICAL" in words, words
        plate, faces = self._said(rf, el, tmp_path)
        assert words in plate
        for face, notes in faces.items():
            assert words in notes, face

    @pytest.mark.parametrize("flag,declared", [(False, False), (True, True)])
    def test_an_unflagged_or_declared_roof_says_nothing_of_it(self, monkeypatch, tmp_path, flag, declared):
        rf, el = self._house(monkeypatch, flag, declared=declared)
        assert rf["form_reading"]["by"] == ("declared" if declared else "kit"), "the premise"
        plate, faces = self._said(rf, el, tmp_path)
        assert "ROOF FORM IS A JUDGMENT" not in plate
        for face, notes in faces.items():
            assert not any("ROOF FORM IS A JUDGMENT" in n for n in notes), face


def test_every_nodes_kit_roof_outcome_is_pinned():
    """WP-16.8 (auditor E's E29): `roof_vocabulary`'s mappings were held only to their own quotes
    and to totality, so re-mapping `low-gable` to `hip` hipped ranch-style with the suite green --
    V19 reads `RV.TABLE`, the subject's own table. This pins what every one of the 164 nodes
    DRAWS: (style, state, form), as a digest and as counts. A move here is a roof a style is drawn
    with, and is re-pinned only with each node named."""
    import collections
    import hashlib
    ids = sorted(f[:-5] for f in os.listdir(os.path.join(ROOT, "styles")) if f.endswith(".json"))
    rows = [(s, TH.kit_roof(s)["state"], TH.kit_roof(s).get("form")) for s in ids]
    assert len(rows) == 164
    assert collections.Counter(r[1] for r in rows) == {"kit": 73, "silent": 58, "undrawable": 25,
                                                       "several": 8}
    assert collections.Counter(r[2] for r in rows if r[1] == "kit") == {
        "side-gable": 31, "hip": 26, "cross-gable": 12, "gambrel": 3, "front-gable": 1}
    assert ("ranch-style", "kit", "side-gable") in rows
    assert hashlib.sha256(json.dumps(rows).encode()).hexdigest()[:16] == "1db03aaebc9d81b6"
