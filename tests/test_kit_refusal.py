"""WP-16.4: the elevation, the DXF, the scene and the placer refuse what the resolved kit forbids,
naming the node that WROTE the ban, and reading a dated ban against the house's date.

Lucas ruled (29 Sep 2026, R3) that a feature the resolved kit forbids is refused, naming the node
that wrote the ban, and (30 Sep 2026, A3) that a forbidden row's own date range is read against the
house's date: a dated house outside the range draws the feature, and an UNDATED house keeps the
refusal and the sheet says its date is unstated.

Every branch is DRIVEN. The corpus reaches the dated sidelight ban (the Tidewater plan is dated
1765, inside georgian-colonial-american's 1700-1780), the pilaster doorcase (four Italianate styles)
and the modillion band (new-urbanist-traditional, bad-03), but no style the elevation draws forbids
the WATER TABLE or the CORNICE whole, and no kit makes an exterior stack canonical where its cascade
forbids one. A guard that runs only where the bug cannot occur is not a guard, so each of those is
handed the record it answers.
"""
import copy
import json
import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

RK = modcache.load("resolve_kit", os.path.join(ROOT, "build", "resolve_kit.py"))
DC = modcache.load("doorcase", os.path.join(ROOT, "build", "doorcase.py"))
G = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))
ST = modcache.load("structure", os.path.join(ROOT, "build", "structure.py"))
RF = modcache.load("roof", os.path.join(ROOT, "build", "roof.py"))
EL = modcache.load("elevation", os.path.join(ROOT, "build", "elevation.py"))
RE = modcache.load("render_elevation", os.path.join(ROOT, "build", "render_elevation.py"))
TH = modcache.load("threshold", os.path.join(ROOT, "build", "threshold.py"))

TIDEWATER = os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")


def _plan(path=TIDEWATER, date="as-stated", style=None):
    p = json.load(open(path))
    if date != "as-stated":
        ctx = p.setdefault("context", {})
        if date is None:
            ctx.pop("date_of_representation", None)
        else:
            ctx["date_of_representation"] = date
    if style:
        p["style"] = style
    return p


def _elevation(plan, monkeypatch=None):
    """The elevation of a plan placed on the search engine, with a PRIVATE solve cache: the date
    and the style change what the placer reserves, and the cache is keyed on the call's arguments
    (this file's copies would otherwise share a key with the shipped record)."""
    if monkeypatch is not None:
        monkeypatch.setattr(G, "_SOLVE_CACHE", {})
    placed = G.solve(plan, engine="heuristic")
    sec = ST.build_section(placed, None, geometry_result=placed)
    rf = RF.build_roof(placed, None, section=sec)
    return placed, EL.build_elevation(placed, None, section=sec, roof=rf)


def _forbid_through_the_resolved_kit(monkeypatch, slot):
    """No drawn style forbids its water table or its cornice whole, so the ban is driven -- and
    driven where the corpus would put it, in the RESOLVED kit the elevation reads, bound `forbidden`
    by a node called `somebody`. (WP-16.8, auditor E's E20: the first version patched the OUTPUT of
    `envelope_refusals`, so deleting a row of `ENVELOPE_BANS` left both tests green.)"""
    real = EL.RK.resolve_slots

    def forbidding(graph, chain, scope=None):
        slots, rest = real(graph, chain, scope)
        return {**slots, slot: {**(slots.get(slot) or {}), "binding": "forbidden",
                                "_bound_by": "somebody", "variants": []}}, rest
    monkeypatch.setattr(EL.RK, "resolve_slots", forbidding)


def _swept(style, monkeypatch, date="as-stated"):
    """The census's own construction: the Tidewater placement, the style swapped afterwards."""
    monkeypatch.setattr(G, "_SOLVE_CACHE", {})
    placed = G.solve(_plan(date=date), engine="heuristic")
    p = copy.deepcopy(placed)
    p["style"] = style
    sec = ST.build_section(p, None, geometry_result=p)
    rf = RF.build_roof(p, None, section=sec)
    return EL.build_elevation(p, None, section=sec, roof=rf)


def _svg(el, tmp_path, face=None):
    face = face or el["entrance_face"]
    out = str(tmp_path / f"{el['style']}-{face}.svg")
    RE.render_elevation(el, out, face=face)
    return open(out).read()


def _texts(svg):
    return [re.sub(r"\s+", " ", t).strip().upper()
            for t in re.findall(r"<text[^>]*>([^<]*)</text>", svg.replace("&#x27;", "'")
                                .replace("&apos;", "'"))]


# ---------------------------------------------------------------- the one reading of a ban
def _rec(*rows, binding="specified", bound_by="root"):
    return {"binding": binding, "_bound_by": bound_by,
            "variants": [dict(r) for r in rows]}


SIDE_1700 = {"id": "sidelights", "status": "forbidden", "_written_by": "georgian",
             "applies_when": {"date_range": [1700, 1780]}}


class TestTheBanReader:
    def test_a_whole_slot_is_forbidden_at_every_date_by_its_binder(self):
        for date in (None, 1500, 2000):
            b = RK.ban(_rec(binding="forbidden", bound_by="writer"), ("anything",), date)
            assert b["writers"] == ["writer"] and b["whole_slot"] and not b["date_unstated"]

    def test_a_dated_row_is_read_against_the_houses_date(self):
        rec = _rec(SIDE_1700)
        inside = RK.ban(rec, ("sidelight",), 1765)
        assert inside["writers"] == ["georgian"] and inside["dated"] == [[1700, 1780]]
        assert inside["date"] == 1765 and not inside["date_unstated"]
        assert RK.ban(rec, ("sidelight",), 1790) is None, "a dated house outside the range draws it"
        assert RK.ban(rec, ("sidelight",), 1700) and RK.ban(rec, ("sidelight",), 1780), \
            "the range is inclusive at both ends, as `in_period` reads a window surround's"

    def test_an_undated_house_keeps_a_dated_ban_and_says_its_date_is_unstated(self):
        b = RK.ban(_rec(SIDE_1700), ("sidelight",), None)
        assert b["writers"] == ["georgian"] and b["date_unstated"] is True

    def test_a_row_out_of_period_leaves_the_permitted_row_to_decide(self):
        later = {"id": "sidelights", "status": "permitted", "_written_by": "federal",
                 "applies_when": {"date_range": [1781, 1830]}}
        rec = _rec(SIDE_1700, later)
        assert RK.ban(rec, ("sidelight",), 1765)["writers"] == ["georgian"]
        assert RK.ban(rec, ("sidelight",), 1800) is None
        # undated: both rows apply and one is permitted, so the feature is not forbidden
        assert RK.ban(rec, ("sidelight",), None) is None

    def test_forbidden_by_is_the_bans_writers(self):
        rec = _rec(SIDE_1700)
        for date in (None, 1765, 1790):
            b = RK.ban(rec, ("sidelight",), date)
            assert RK.forbidden_by(rec, ("sidelight",), date) == (b["writers"] if b else None)

    def test_the_words_name_the_writer_the_range_and_the_date(self):
        assert RK.ban_words(RK.ban(_rec(SIDE_1700), ("sidelight",), 1765)) == (
            "forbidden by georgian's kit for houses of 1700–1780, and this house is dated 1765")
        assert RK.ban_words(RK.ban(_rec(SIDE_1700), ("sidelight",), None)).endswith(
            "; this record states no date, so the ban is kept")
        two = RK.ban(_rec({"id": "a-x", "status": "forbidden", "_written_by": "p"},
                          {"id": "b-x", "status": "forbidden", "_written_by": "q"}), ("x",), None)
        assert RK.ban_words(two) == "forbidden by p and q's kits"


# ---------------------------------------------------------------- the entrance's one spelling
class TestTheEntrancesRefusals:
    def _slots(self, style):
        return TH.resolved_slots(style)

    def test_the_tidewater_sidelights_are_refused_at_1765_and_drawn_at_1790(self):
        s = self._slots("tidewater-georgian")
        at = DC.refusals(s, 1765)
        assert at["sidelights"]["writers"] == ["georgian-colonial-american"]
        assert at["sidelights"]["dated"] == [[1700, 1780]]
        assert at["transom_sidelight"] is None, "a row ban is not the whole slot"
        assert DC.refusals(s, 1790)["sidelights"] is None
        assert DC.refusals(s, None)["sidelights"]["date_unstated"] is True

    @pytest.mark.parametrize("style", ["italian-renaissance-revival", "italianate-townhouse",
                                       "second-empire", "renaissance-revival-american"])
    def test_the_italianate_family_forbids_the_pilaster_doorcase_in_its_own_words(self, style):
        b = DC.refusals(self._slots(style), None)["doorcase"]
        assert b and b["writers"] == [style], b

    def test_minimal_traditional_forbids_the_whole_door_surround(self):
        b = DC.refusals(self._slots("minimal-traditional"), None)["doorcase"]
        assert b["whole_slot"] and b["writers"] == ["minimal-traditional"]

    def test_a_row_ban_on_the_sidelights_keeps_the_transom_and_a_slot_ban_takes_both(self):
        op, fac = DC.PE.resolve("opening-proportion"), DC.PE.resolve("facade-classical")
        free = DC.composition(op, fac, 147.0)
        row = DC.composition(op, fac, 147.0, refused={"sidelights": {"writers": ["x"]}})
        slot = DC.composition(op, fac, 147.0, forbids={"transom_sidelight"})
        assert free["sidelight_w_in"] and free["transom_h_in"]
        assert row["sidelight_w_in"] is None and row["transom_h_in"] == free["transom_h_in"]
        assert row["sidelights_forbidden"] and not row["transom_forbidden"]
        assert slot["sidelight_w_in"] is None and slot["transom_h_in"] is None
        assert slot["transom_forbidden"]
        assert row["composition_w_in"] == free["without_sidelights_in"]


# ---------------------------------------------------------------- the placer reserves what is drawn
class TestThePlacerReservesWhatTheElevationDraws:
    def test_the_tidewater_run_is_reserved_without_sidelights_and_says_who_refused_them(self, monkeypatch):
        placed, el = _elevation(_plan(), monkeypatch)
        dc = placed["opening_report"]["doorcase"]
        assert dc["reserved"] and dc["sidelights_in"] is None
        assert dc["sidelights_refused"]["writers"] == ["georgian-colonial-american"]
        assert dc["composed_for"] == {"style": "tidewater-georgian", "date": 1765}
        assert el["entrance"]["sidelights_present"] is False
        assert el["entrance"]["sidelights_refused_by"]["date"] == 1765

    def test_a_house_dated_after_the_ban_reserves_and_draws_its_sidelights(self, monkeypatch):
        placed, el = _elevation(_plan(date=1790), monkeypatch)
        dc = placed["opening_report"]["doorcase"]
        assert dc["sidelights_in"] and dc["sidelights_refused"] is None
        assert el["entrance"]["sidelights_present"] is True
        lo, hi = dc["run_ft"]
        placed0, _el0 = _elevation(_plan(), monkeypatch)
        lo0, hi0 = placed0["opening_report"]["doorcase"]["run_ft"]
        assert (hi - lo) > (hi0 - lo0), "the sidelights' run is reserved only where they are drawn"


# ---------------------------------------------------------------- the elevation refuses and says so
class TestTheElevationRefusesAndSaysWho:
    def test_the_tidewater_front_draws_no_sidelights_keeps_its_transom_and_says_why(self, monkeypatch, tmp_path):
        _placed, el = _elevation(_plan(), monkeypatch)
        svg = _svg(el, tmp_path)
        said = _texts(svg)
        assert el["entrance"]["transom"]["drawn"], "the canonical transom stays: the ban is the row's"
        assert any(t.startswith("SIDELIGHTS NOT DRAWN — FORBIDDEN BY GEORGIAN-COLONIAL-AMERICAN'S KIT "
                                "FOR HOUSES OF 1700–1780, AND THIS HOUSE IS DATED 1765") for t in said), said
        m = el["measurements"]
        assert m["count_of_sidelights_drawn_at_the_entrance"] == 0
        assert "sidelight_width_in" not in m, "a sidelight not drawn has no width"

    def test_an_undated_house_keeps_the_refusal_and_says_its_date_is_unstated(self, monkeypatch, tmp_path):
        _placed, el = _elevation(_plan(date=None), monkeypatch)
        said = _texts(_svg(el, tmp_path))
        assert el["entrance"]["sidelights_present"] is False
        assert any("THIS RECORD STATES NO DATE, SO THE BAN IS KEPT" in t for t in said), said

    def test_a_dated_house_outside_the_ban_draws_the_pair_and_counts_it(self, monkeypatch, tmp_path):
        _placed, el = _elevation(_plan(date=1790), monkeypatch)
        m = el["measurements"]
        assert m["count_of_sidelights_drawn_at_the_entrance"] == 2
        assert m["sidelight_width_in"] == el["entrance"]["sidelight_width_in"]
        assert not any("SIDELIGHTS NOT DRAWN" in t for t in _texts(_svg(el, tmp_path)))

    def test_a_refused_doorcase_leaves_the_plain_casing_and_withholds_its_order(self, monkeypatch, tmp_path):
        el = _swept("italian-renaissance-revival", monkeypatch)
        ent = el["entrance"]
        assert ent["doorcase_refused_by"]["writers"] == ["italian-renaissance-revival"]
        # the doorcase's OWN casing, the one figure the measurement publishes, and not the kit's
        # `casing` slot, whose 4.5 in is trim-classical's interior Federal casing (elevation.py)
        assert ent["plain_casing_width_in"] == ent["casing_width_in"]
        assert el["measurements"]["pilaster_or_casing_width_in"] == ent["plain_casing_width_in"]
        assert ent["entablature_members"] == [] and ent["pilaster_width_in"] is None
        svg = _svg(el, tmp_path)
        assert 'class="csp"' in svg and 'class="cs"' not in svg, \
            "the plain casing is drawn in its own class, and no doorcase"
        assert any(t.startswith("DOORCASE NOT DRAWN — FORBIDDEN BY ITALIAN-RENAISSANCE-REVIVAL'S KIT")
                   for t in _texts(svg))
        m = el["measurements"]
        for k in ("pilaster_width_in", "column_height_in", "lower_shaft_diameter_in",
                  "surround_height_above_opening_in", "entablature_bed_height_in",
                  "distinct_mouldings_within_4ft_of_the_entrance"):
            assert k not in m, k

    def test_a_refused_frieze_and_belt_are_not_drawn_and_have_no_figures(self, monkeypatch, tmp_path):
        el = _swept("new-england-colonial", monkeypatch)
        svg = _svg(el, tmp_path)
        said = _texts(svg)
        assert el["eave_cornice"]["frieze_refused_by"]["writers"] == ["new-england-colonial"]
        assert el["water_table_belt"]["belt_refused_by"]["writers"] == ["new-england-colonial"]
        assert 'class="bd fz' not in svg, "the frieze band is not drawn"
        assert 'class="wt w-med"' not in svg, "the belt is not drawn"
        assert 'class="wt w-prof"' in svg, "the water table is its own question and stays"
        for w in ("FRIEZE", "BELT COURSE"):
            assert any(t.startswith(f"{w} NOT DRAWN — FORBIDDEN BY NEW-ENGLAND-COLONIAL'S KIT")
                       for t in said), w
        m = el["measurements"]
        for k in ("frieze_height_in", "entablature_height_in", "belt_height_in",
                  "belt_height_above_first_floor_in"):
            assert k not in m, k
        # the roof stands on what is drawn: the eave band is the cornice alone
        eave = el["roof_record"]["main"]["grade_to_eave_ft"] * 12.0
        assert el["grade_to_true_eave_in"] == pytest.approx(
            eave + el["eave_cornice"]["cornice_height_in"], abs=1e-6)

    def test_a_refused_water_table_is_driven_because_no_drawn_style_forbids_one(self, monkeypatch, tmp_path):
        _forbid_through_the_resolved_kit(monkeypatch, "water_table")
        _placed, el = _elevation(_plan(), monkeypatch)
        svg = _svg(el, tmp_path)
        assert 'class="wt w-prof"' not in svg and 'class="wt w-med"' in svg, \
            "the water table goes and the belt, its own slot, stays"
        assert any(t.startswith("WATER TABLE NOT DRAWN — FORBIDDEN BY SOMEBODY'S KIT") for t in _texts(svg))
        m = el["measurements"]
        assert "water_table_height_above_finished_grade_in" not in m
        assert "wall_height_water_table_to_cornice_in" not in m
        assert "belt_height_in" in m

    def test_a_refused_cornice_is_driven_and_the_roof_stands_on_the_frieze(self, monkeypatch, tmp_path):
        _forbid_through_the_resolved_kit(monkeypatch, "cornice")
        _placed, el = _elevation(_plan(), monkeypatch)
        svg = _svg(el, tmp_path)
        assert 'class="bd w-prof"' not in svg and 'class="bd fz w-med"' in svg
        assert "cm w-fine" not in svg and "SEE INSET FOR PROFILE" not in svg
        said = _texts(svg)
        assert any(t.startswith("CORNICE NOT DRAWN — FORBIDDEN BY SOMEBODY'S KIT") for t in said)
        assert not any(t.startswith("MODILLIONS NOT DRAWN") for t in said), \
            "the modillions go with the cornice and are not said twice"
        assert "modillions" not in el["refused_by_the_kit"]
        eave = el["roof_record"]["main"]["grade_to_eave_ft"] * 12.0
        assert el["grade_to_true_eave_in"] == pytest.approx(
            eave + el["eave_cornice"]["frieze_height_in"], abs=1e-6)
        m = el["measurements"]
        for k in ("cornice_height_in", "count_of_moulded_members_in_the_eave_assembly",
                  "cyma_profiles_at_the_eave", "eave_overhang_in", "entablature_height_in"):
            assert k not in m, k

    def test_a_refused_modillion_band_leaves_the_other_members_at_the_same_height(self, monkeypatch, tmp_path):
        el = _swept("new-urbanist-traditional", monkeypatch)
        free = _swept("colonial-revival", monkeypatch)
        c, c0 = el["eave_cornice"], free["eave_cornice"]
        assert c["refused_members"] == ["corn_modillion", "corn_modillion_cap"]
        assert not any("modillion" in m["id"] for m in c["members"])
        assert c["member_count"] == c0["member_count"] - 2
        assert c["cornice_height_in"] == pytest.approx(c0["cornice_height_in"], abs=0.01), \
            "the envelope fixes the cornice's height; the refusal changes its shape"
        svg = _svg(el, tmp_path)
        assert "MODILLION BAND DRAWN SOLID" not in svg and 'data-member="corn_modillion"' not in svg
        assert any(t.startswith("MODILLIONS NOT DRAWN — FORBIDDEN BY NEW-URBANIST-TRADITIONAL'S KIT")
                   for t in _texts(svg))


# ---------------------------------------------------------------- a house nothing is refused on does not move
GOOD_03 = os.path.join(ROOT, "plans", "reference", "good-03-parlor-drawing-room-house.json")


def test_the_true_eave_is_summed_from_the_eave_as_it_always_was(monkeypatch):
    """`grade_to_true_eave_in` is the eave plus the frieze plus the cornice, added LEFT TO RIGHT.
    Adding the two bands first -- which the refusal's `or 0.0` invited -- is the same number to
    within the last bit, and on good-03, where the kit refuses nothing, that bit carried three of
    the DXF's cornice lines across a rounding tie at the thousandth. Exact equality, because the
    property is the order of an addition and an approximate test cannot see one."""
    _p, el = _elevation(_plan(GOOD_03), monkeypatch)
    c = el["eave_cornice"]
    assert not el["refused_by_the_kit"], "the premise: nothing is refused on this house"
    eave = el["roof_record"]["main"]["grade_to_eave_ft"]
    assert el["grade_to_true_eave_in"] == eave * 12.0 + c["frieze_height_in"] + c["cornice_height_in"]


# ---------------------------------------------------------------- the CAD file and the model refuse the same
EX = modcache.load("export_dxf", os.path.join(ROOT, "build", "export_dxf.py"))
SC = modcache.load("scene", os.path.join(ROOT, "build", "scene.py"))


def _full(plan, monkeypatch, style=None):
    """The placed record, its section and roof, and the elevation -- everything the scene reads.
    With `style`, the census's own construction: placed as the record says, the style swapped."""
    monkeypatch.setattr(G, "_SOLVE_CACHE", {})
    placed = G.solve(plan, engine="heuristic")
    if style:
        placed = copy.deepcopy(placed)
        placed["style"] = style
    sec = ST.build_section(placed, None, geometry_result=placed)
    rf = RF.build_roof(placed, None, section=sec)
    return placed, sec, rf, EL.build_elevation(placed, None, section=sec, roof=rf)


def _dxf(el, tmp_path, name):
    path = str(tmp_path / f"{name}.dxf")
    res = EX.export_elevation_dxf(el, path, el["entrance_face"]) or {}
    assert not (res.get("error") or res.get("refusal")), res
    import ezdxf
    return ezdxf.readfile(path).modelspace()


def _kit_refused(msp):
    """Every `TDL::kit-refused` record in the file, read back as the JSON it was written as."""
    out = []
    for e in msp:
        if e.has_xdata(EX.APPID):
            tags = [v for _c, v in e.get_xdata(EX.APPID)]
            if tags and tags[0] == "TDL::kit-refused":
                out.append(json.loads("".join(tags[1:])))
    return out


def _dxf_texts(msp):
    return [re.sub(r"\s+", " ", e.dxf.text if e.dxftype() == "TEXT" else e.text).strip().upper()
            for e in msp if e.dxftype() in ("TEXT", "MTEXT")]


def _panes(msp, width_in):
    """Closed opening-layer rectangles exactly `width_in` wide: a drawn sidelight, in the DXF."""
    n = 0
    for e in msp:
        if e.dxftype() == "LWPOLYLINE" and "OPENING" in e.dxf.layer.upper() and e.closed:
            xs = [p[0] for p in e.get_points()]
            if abs((max(xs) - min(xs)) - width_in) < 1e-3:
                n += 1
    return n


class TestTheCadFileAndTheModelRefuseWhatTheSheetRefuses:
    def test_the_dxf_draws_no_sidelights_and_carries_who_forbade_them(self, monkeypatch, tmp_path):
        pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
        _p, _s, _r, el = _full(_plan(), monkeypatch)
        _p, _s, _r, el90 = _full(_plan(date=1790), monkeypatch)
        slw = el90["entrance"]["sidelight_width_in"]
        assert slw, "the premise: dated after the ban, the composition holds a pair"
        msp, msp90 = _dxf(el, tmp_path, "1765"), _dxf(el90, tmp_path, "1790")
        assert _panes(msp90, slw) == 2, "the control draws its pair in the CAD file"
        assert _panes(msp, slw) == 0, "a pair the kit forbids is not in the CAD file"
        recs = _kit_refused(msp)
        assert len(recs) == 1 and set(recs[0]) == {"sidelights"}, recs
        side = recs[0]["sidelights"]
        assert side["ban"]["writers"] == ["georgian-colonial-american"] and side["ban"]["date"] == 1765
        assert side["transom_too"] is False, "a row ban leaves the transom its own question"
        assert side["words"] == EL.ban_words(el["entrance"]["sidelights_refused_by"])
        assert any(t.startswith("SIDELIGHTS NOT DRAWN — FORBIDDEN BY GEORGIAN-COLONIAL-AMERICAN'S KIT")
                   for t in _dxf_texts(msp))
        assert _kit_refused(msp90) == [], "the control says no refusal it does not make"

    def test_the_dxf_draws_the_plain_casing_and_carries_who_forbade_the_doorcase(self, monkeypatch, tmp_path):
        pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
        _p, _s, _r, el = _full(_plan(), monkeypatch, style="italian-renaissance-revival")
        msp = _dxf(el, tmp_path, "irr")
        recs = [r for r in _kit_refused(msp) if "doorcase" in r]
        assert len(recs) == 1, _kit_refused(msp)
        assert recs[0]["doorcase"]["ban"]["writers"] == ["italian-renaissance-revival"]
        assert any(t.startswith("DOORCASE NOT DRAWN — FORBIDDEN BY ITALIAN-RENAISSANCE-REVIVAL'S KIT")
                   for t in _dxf_texts(msp))

    def test_the_scene_models_no_sidelights_and_names_the_ban(self, monkeypatch):
        placed, sec, rf, el = _full(_plan(), monkeypatch)
        scene = SC.build_scene(placed, sec, rf, el)
        said = [n for n in scene["not_modelled"] if n["what"] == "the sidelights"]
        assert len(said) == 1, scene["not_modelled"]
        assert "georgian-colonial-american's kit" in said[0]["why"] and "dated 1765" in said[0]["why"]
        assert not [s for s in scene["solids"] if "-sidelight-" in s["id"]], "a refused pair was modelled"
        placed, sec, rf, el = _full(_plan(date=1790), monkeypatch)
        scene = SC.build_scene(placed, sec, rf, el)
        assert [s for s in scene["solids"] if "-sidelight-" in s["id"]], "the control models its pair"
        assert not [n for n in scene["not_modelled"] if n["what"] == "the sidelights"]

    def test_the_scene_models_no_order_over_a_refused_doorcase_and_names_the_ban(self, monkeypatch):
        placed, sec, rf, el = _full(_plan(), monkeypatch, style="italian-renaissance-revival")
        scene = SC.build_scene(placed, sec, rf, el)
        said = [n for n in scene["not_modelled"] if n["what"] == "the doorcase"]
        assert len(said) == 1 and "italian-renaissance-revival's kit" in said[0]["why"], scene["not_modelled"]
        assert not [s for s in scene["solids"] if "-ent_" in s["id"]], "an entablature was modelled"
        placed, sec, rf, el = _full(_plan(), monkeypatch, style="colonial-revival")
        scene = SC.build_scene(placed, sec, rf, el)
        assert [s for s in scene["solids"] if "-ent_" in s["id"]], "the control models its entablature"


# ---------------------------------------------------------------- the stack, refused where it is placed
class TestAForbiddenExteriorStackIsRefusedByThePlacer:
    def test_driven_a_kit_forbidding_the_exterior_end_places_no_stack_and_says_who(self, monkeypatch):
        slots = copy.deepcopy(TH.resolved_slots("tidewater-georgian"))
        hp = slots.setdefault("hearth_position", {"binding": "specified", "variants": []})
        hp["variants"] = [v for v in hp.get("variants") or [] if v.get("id") != "exterior-end"] + [
            {"id": "exterior-end", "status": "forbidden", "_written_by": "new-england-colonial"}]
        monkeypatch.setattr(TH, "resolved_slots", lambda style: slots)
        placed, _el = _elevation(_plan(), monkeypatch)
        he = placed["hearths"]
        assert he["side"] == "exterior" and he["stacks"] == []
        why = [u for u in he["unplaced"] if u.get("what") == "the stacks"]
        assert why and "new-england-colonial's kit" in why[0]["reason"], he["unplaced"]

    def test_control_the_shipped_kit_places_its_exterior_stacks(self, monkeypatch):
        placed, _el = _elevation(_plan(), monkeypatch)
        assert placed["hearths"]["side"] == "exterior" and placed["hearths"]["stacks"]


    def test_the_roof_the_roof_plan_the_scene_and_the_plan_sheet_refuse_the_same_stacks(self, monkeypatch, tmp_path):
        """WP-16.8 (auditor C). `hearth_pass` writes the flues before it refuses the stacks, and
        `roof.chimney_positions` read the flues: the roof plan drew both stacks and the scene drew
        both axes while the elevation, the DXF and the plan drew none, under `hearth_pass`'s own
        comment that none of them draws a stack another does not. Every surface refuses them now,
        and says the ban and its writer."""
        slots = copy.deepcopy(TH.resolved_slots("tidewater-georgian"))
        hp = slots.setdefault("hearth_position", {"binding": "specified", "variants": []})
        hp["variants"] = [v for v in hp.get("variants") or [] if v.get("id") != "exterior-end"] + [
            {"id": "exterior-end", "status": "forbidden", "_written_by": "new-england-colonial"}]
        monkeypatch.setattr(TH, "resolved_slots", lambda style: slots)
        placed, sec, rf, el = _full(_plan(), monkeypatch)
        assert placed["hearths"]["stacks"] == [], "the premise: the placer refused them"
        ch = rf["chimneys"]
        assert ch["positions"] == [] and ch.get("refused_by"), ch
        assert "new-england-colonial's kit" in ch["note"], ch["note"]
        out = str(tmp_path / "roof.svg")
        modcache.load("render_roof", os.path.join(ROOT, "build", "render_roof.py")).render_roof(rf, out)
        assert 'class="ch' not in open(out, encoding="utf-8").read(), "the roof plan drew a stack"
        scene = SC.build_scene(placed, sec, rf, el)
        assert not [x for x in scene["solids"] if x.get("class") == "chimney"]
        said = [n for n in scene["not_modelled"] if n["what"] == "the chimney stacks"]
        assert said and "new-england-colonial's kit" in said[0]["why"], scene["not_modelled"]
        DI = modcache.load("disclosures", os.path.join(ROOT, "build", "disclosures.py"))
        line = DI.fires_not_drawn(placed)
        assert line and "FORBIDDEN BY NEW-ENGLAND-COLONIAL'S KIT" in line["text"], line

    def test_control_on_the_shipped_kit_the_roof_and_the_scene_carry_both_stacks(self, monkeypatch):
        placed, sec, rf, el = _full(_plan(), monkeypatch)
        assert len(rf["chimneys"]["positions"]) == 2
        scene = SC.build_scene(placed, sec, rf, el)
        assert [x for x in scene["solids"] if x.get("class") == "chimney"]

# ---------------------------------------------------------------- the sidelight fault is gated on the drawing
class TestTheSidelightFaultAsksOnlyWhereSidelightsAreDrawn:
    def test_every_test_of_the_fault_is_gated_on_the_drawn_count(self):
        f = json.load(open(os.path.join(ROOT, "faults", "sidelights-as-storefront-glass.json")))
        tests = [f["test"], *f["secondary_tests"],
                 *[e["bounds_test"] for e in f.get("exceptions", []) if e.get("bounds_test")]]
        for t in tests:
            aw = t.get("applies_when") or {}
            assert aw.get("expression") == "count_of_sidelights_drawn_at_the_entrance" \
                and aw.get("direction") == "at-least" and aw.get("threshold") == 1, t["expression"]

    def test_a_front_with_no_sidelights_is_not_applicable_and_one_with_a_pair_is_judged(self, monkeypatch):
        _p, none = _elevation(_plan(), monkeypatch)
        _p, pair = _elevation(_plan(date=1790), monkeypatch)
        assert _verdict(none) == "not_applicable"
        assert _verdict(pair) in ("faults_present", "faults_clear"), "a drawn pair is judged"

    def test_a_pair_the_composition_holds_and_no_face_draws_is_unmeasured_not_zero(self, monkeypatch):
        """THE THIRD STATE. Where the composition holds a pair and no face draws the entrance door
        (good-03 on the search engine seats no front door on its entrance face), the count is not
        a measured zero: the house has sidelights and the drawing is what is missing. So the count
        is withheld and the fault is could-not-evaluate -- not applicable would be a verdict about
        the house on the strength of a gap in the drawing. DRIVEN: the entrance door's rect is
        taken off every face of a house dated after the ban, whose composition keeps its pair."""
        real = EL.opening_rects

        def no_entrance(elev, face):
            out = real(elev, face)
            return {**out, "rects": [r for r in out["rects"]
                                     if not (r["kind"] == "door" and r.get("entrance"))]}
        monkeypatch.setattr(EL, "opening_rects", no_entrance)
        _p, el = _elevation(_plan(date=1790), monkeypatch)
        assert el["entrance"]["sidelights_present"] is True, "the premise: the composition holds a pair"
        m = el["measurements"]
        assert "count_of_sidelights_drawn_at_the_entrance" not in m and "sidelight_width_in" not in m
        assert _verdict(el) == "could_not_judge"

    def test_a_garage_door_marked_the_entrance_draws_no_composition_and_is_unmeasured(self, monkeypatch):
        """bad-02's widest front door is its garage's, so the rect marked `entrance` is a garage
        door, which carries no doorcase and no sidelights (WP-14.3). The composition's pair is
        drawn nowhere, so the count is unmeasured, as where no face draws the entrance door."""
        _p, el = _elevation(_plan(BAD_02), monkeypatch)
        ent = [r for r in EL.opening_rects(el, el["entrance_face"])["rects"]
               if r["kind"] == "door" and r.get("entrance")]
        assert ent and all("garage" in str(r.get("type") or "").lower() for r in ent), \
            "the premise: bad-02's entrance rect is its garage door"
        assert el["entrance"]["sidelights_present"] is True, "the premise: a pair is composed"
        assert "count_of_sidelights_drawn_at_the_entrance" not in el["measurements"]
        assert _verdict(el) == "could_not_judge"


BAD_02 = os.path.join(ROOT, "plans", "reference", "bad-02-flex-room-craftsman.json")


def _verdict(el, fid="sidelights-as-storefront-glass"):
    core = modcache.load("mcp_core", os.path.join(ROOT, "mcp_server", "core.py"))
    got = core.check_measurements(el["measurements"], style=el["style"])
    for state in ("faults_present", "faults_clear", "could_not_judge", "not_applicable"):
        if any((r.get("fault") or r.get("id")) == fid for r in got.get(state) or []):
            return state
    return None
