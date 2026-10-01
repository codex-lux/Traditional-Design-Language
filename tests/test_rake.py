"""WP-16.9: the rake the gable end draws, the gable end two faults are gated on, and a cornice
deepened to its kit's own minimum. Lucas's answers of 30 Sep 2026, put as direct questions.

B3: The Cardboard Gable's own rake -- "a raking cornice board 6-8 in deep carrying a reduced version
of the eave profile, bed mould and crown without the corona and modillions, at roughly 0.5-0.7 of
the eave cornice's members", standing 1 1/4 in proud of the wall and 4-8 in beyond it -- drawn at
the middles, labelled a judgment and withheld from the fault. The styles the fault excepts keep the
roof's edge, and a pediment keeps its own rule.

B5 (the question behind B3 said no record dimensions a raking member, and `rake_condition` does):
the kit first. The fault's rake where the resolved kit states it or says nothing; a kit that states
another rake draws its own; a forbidden slot is refused (R3).

B6: `flush-rake` is not applicable where the elevation draws no gable end. B2: `return-that-never-
returns` the same, and it gains no exception.

B4: where a kit states a minimum cornice for its return, the cornice is drawn at least that deep.

Every figure here is read off the fault or the kit, never copied from `elevation`'s constants,
which are the subject. What the corpus cannot reach is driven, each case asserting its premise.
"""
import copy
import json
import math
import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import modcache as mc  # noqa: E402
import inkread as IR  # noqa: E402


def _m(name):
    return mc.load(name, os.path.join(ROOT, "build", name + ".py"))


RK = _m("resolve_kit")
EL = _m("elevation")
CORE = mc.load("tdlcore", os.path.join(ROOT, "mcp_server", "core.py"))

FAULT = os.path.join(ROOT, "faults", "flush-rake.json")
PLANS = ([os.path.join("plans", f) for f in sorted(os.listdir(os.path.join(ROOT, "plans")))
          if f.endswith(".json")] +
         [os.path.join("plans", "reference", f)
          for f in sorted(os.listdir(os.path.join(ROOT, "plans", "reference"))) if f.endswith(".json")])


def _fault():
    with open(FAULT, encoding="utf-8") as fh:
        return json.load(fh)


def _words(s):
    return " ".join(str(s or "").split())


def _build(rel):
    G, ST, RF = _m("geometry"), _m("structure"), _m("roof")
    p = G.solve(json.load(open(os.path.join(ROOT, rel))), engine="heuristic")
    sec = ST.build_section(p, None, geometry_result=p)
    rf = RF.build_roof(p, None, section=sec)
    return EL.build_elevation(p, None, section=sec, roof=rf)


_BUILT = {}


def _elev(rel):
    if rel not in _BUILT:
        _BUILT[rel] = _build(rel)
    return _BUILT[rel]


def _ridged(el):
    """Whether the roof judges a ridge: roof.py leaves the ridge height unjudged where its record
    states no pitch, rather than compute it off an invented one, and a gable end with no ridge has
    no slope for a rake to run along. Read off the roof record."""
    return ((el.get("roof_record") or {}).get("main") or {}).get("pitch_rise_per_12") is not None


@pytest.fixture(scope="module")
def raked():
    """Every shipped plan whose elevation draws a rake on a gable end whose roof judges a ridge,
    found by reading rather than named: which plans do is a property of their kits and their roofs,
    and both move (B5, B1). A plan whose kit asks a rake under a roof with no ridge draws none, and
    `TestTheUnridgedGable` holds what it says instead."""
    out = []
    for rel in PLANS:
        el = _elev(rel)
        if ((el.get("rake") or {}).get("draws") in ("rake", "plain") and EL.gable_faces(el["roof_record"])
                and _ridged(el)):
            out.append((rel, el))
    assert out, "no shipped plan draws a rake on a gable end, so nothing here reaches the marks"
    return out


def _slots(style):
    g = RK.load_graph()
    return RK.resolve_slots(g, RK.chain_for(g, style), RK.scope_for(g, style))[0]


# ------------------------------------------------------------------ B3: the fault's own figures
class TestTheFiguresAreTheFaultsOwn:
    def test_the_board_and_the_member_scale_are_the_middles_of_the_faults_words(self):
        cp = _words(_fault()["correct_practice"])
        b = re.search(r"a raking cornice board (\d+)-(\d+) in deep", cp)
        k = re.search(r"at roughly (\d*\.\d+)-(\d*\.\d+) of the eave cornice's members", cp)
        assert b and k, cp
        assert EL.RAKE_BOARD_IN == (float(b.group(1)) + float(b.group(2))) / 2.0
        assert EL.RAKE_MEMBER_SCALE == pytest.approx((float(k.group(1)) + float(k.group(2))) / 2.0)

    def test_the_proud_figure_is_the_governing_tests_threshold_and_its_words(self):
        f = _fault()
        assert f["test"]["expression"] == "rake_member_projection_from_siding_face_in"
        assert (f["test"]["direction"], f["test"]["threshold"]) == ("at-least", EL.RAKE_PROUD_IN)
        assert "A rake board 1 1/4 in proud of the siding" in _words(f["correct_practice"])

    def test_the_overhang_is_the_middle_of_the_faults_own_band(self):
        t = next(t for t in _fault()["secondary_tests"] if t["expression"] == "rake_overhang_in")
        assert t["direction"] == "between"
        assert EL.RAKE_OVERHANG_IN == (t["threshold"] + t["upper"]) / 2.0

    def test_the_basis_quotes_the_fault_verbatim(self):
        path, field, quote = EL.RAKE_BASIS
        with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
            assert _words(quote) in _words(json.load(fh)[field])

    def test_the_excepted_styles_are_read_off_the_fault_and_not_copied(self, tmp_path, monkeypatch):
        assert set(EL.rake_excepted_styles()) == {e["style"] for e in _fault()["exceptions"]}
        # a copy of the fault excepting one more style, read in its place, excepts it too
        f = _fault()
        f["exceptions"].append({"style": "tidewater-georgian"})
        (tmp_path / "faults").mkdir()
        (tmp_path / "faults" / "flush-rake.json").write_text(json.dumps(f), encoding="utf-8")
        monkeypatch.setattr(EL, "ROOT", str(tmp_path))
        assert "tidewater-georgian" in EL.rake_excepted_styles()
        rk = EL.rake_for("tidewater-georgian", {"state": "fault", "writers": ["x"]}, {})
        assert rk["draws"] == "edge" and "THE CARDBOARD GABLE EXCEPTS TIDEWATER-GEORGIAN" in rk["words"]


# ------------------------------------------------------------------ B5: the kit, read first
class TestTheKitsReading:
    def test_nothing_bound_is_silent(self):
        for rec in (None, {}, {"binding": "open"}, {"binding": "open", "_bound_by": "x"}):
            r = RK.rake_at(rec)
            assert (r["state"], r["writers"]) == ("silent", []), rec

    def test_a_forbidden_slot_is_refused_by_its_writer(self):
        r = RK.rake_at({"binding": "forbidden", "_bound_by": "italianate-american"})
        assert (r["state"], r["writers"]) == ("forbidden", ["italianate-american"])

    @pytest.mark.parametrize("vid,state", [("boxed-rake-with-return", "fault"),
                                           ("kneelers-and-raised-coping", "undrawn"),
                                           ("bargeboard-full-rake-pierced", "undrawn"),
                                           ("a-rake-nobody-has-named", "unjudged")])
    def test_a_canonical_row_decides_and_names_its_writer(self, vid, state):
        rec = {"binding": "specified", "_bound_by": "b",
               "variants": [{"id": vid, "status": "canonical", "_written_by": "w"}]}
        r = RK.rake_at(rec)
        assert (r["state"], r["variant"], r["writers"]) == (state, vid, ["w"])

    def test_the_faults_row_wins_over_another_canonical_one(self):
        rec = {"binding": "specified", "_bound_by": "b", "variants": [
            {"id": "timber-barge-board", "status": "canonical", "_written_by": "w1"},
            {"id": "boxed-rake-with-return", "status": "canonical", "_written_by": "w2"}]}
        assert (RK.rake_at(rec)["state"], RK.rake_at(rec)["writers"]) == ("fault", ["w2"])

    def test_a_dated_row_is_read_at_the_house_date(self):
        rec = {"binding": "specified", "_bound_by": "b", "variants": [
            {"id": "boxed-rake-with-return", "status": "canonical", "_written_by": "w",
             "applies_when": {"date_range": [1700, 1780]}}]}
        assert RK.rake_at(rec, 1750)["state"] == "fault"
        assert RK.rake_at(rec, 1850)["state"] != "fault"

    def test_a_plain_trim_is_read_at_its_middle_or_its_maximum_and_never_in_another_unit(self):
        band = {"binding": "specified", "_bound_by": "b", "_param_writers": {"rake_trim_width_in": "w"},
                "parameters": {"rake_trim_width_in": {"range": [6, 8], "unit": "in", "kind": "measured"}}}
        r = RK.rake_at(band)
        assert (r["state"], r["trim_in"], r["trim_by"]) == ("plain", 7.0, "w")
        assert r["trim_basis"] == "the middle of rake_trim_width_in, 6-8 in"
        mx = {"binding": "specified", "_bound_by": "b",
              "parameters": {"rake_width_max": {"value": 6, "unit": "in", "kind": "measured"}}}
        r = RK.rake_at(mx)
        assert (r["state"], r["trim_in"], r["trim_by"]) == ("plain", 6.0, "b")
        assert r["trim_basis"] == "rake_width_max, 6 in, a maximum drawn at its figure"
        ft = copy.deepcopy(mx)
        ft["parameters"]["rake_width_max"]["unit"] = "ft"
        assert RK.rake_at(ft)["state"] != "plain"

    def test_one_measured_figure_is_a_measurement_and_a_band_or_a_maximum_is_not_B29(self):
        """B29 (1 Oct 2026): minimal-traditional's 5 1/2 in board 'is a measurement rather than a
        judgment'. One measured figure is drawn as it stands; a band's middle, a maximum drawn at its
        figure and an unmeasured figure are a choice of where in what the kit allows."""
        def one(k, v, kind):
            return {"binding": "specified", "_bound_by": "b",
                    "parameters": {k: dict(v, unit="in", kind=kind)}}
        assert RK.rake_at(one("rake_trim_width_in", {"value": 5.5}, "measured"))["trim_measured"] is True
        for rec in (one("rake_trim_width_in", {"value": 5.5}, "editorial"),
                    one("rake_trim_width_in", {"range": [4, 6]}, "measured"),
                    one("rake_width_max", {"value": 6}, "measured")):
            r = RK.rake_at(rec)
            assert (r["state"], r["trim_measured"]) == ("plain", False), rec

    def test_an_overhang_with_no_member_is_its_own_state_and_never_silent_T11(self):
        """T11 (1 Oct 2026, taken as recommended under Lucas's standing instruction, never put): a
        record stating the rake's own overhang and no canonical row and no trim has said something,
        so it is not read as silence, and the fault's rake is not drawn over it."""
        rec = {"binding": "specified", "_bound_by": "b", "_param_writers": {"rake_overhang_in": "w"},
               "rule": "eave and rake overhang between 18 and 36 in",
               "parameters": {"rake_overhang_in": {"range": [18, 36], "unit": "in", "kind": "measured"}}}
        r = RK.rake_at(rec)
        assert (r["state"], r["writers"], r["bands"]["rake_overhang_in"]["range"]) == (
            "overhang", ["w"], [18.0, 36.0])
        # permitted rows beside it are named, as a silence's are, and still settle nothing
        withp = dict(rec, variants=[{"id": "close-verge-with-rake-mould", "status": "permitted"}])
        assert (RK.rake_at(withp)["state"], RK.rake_at(withp)["permitted"]) == (
            "overhang", ["close-verge-with-rake-mould"])
        # a canonical row still decides: the fault's rake with its own band is the fault's
        canon = dict(rec, variants=[{"id": "boxed-rake-with-return", "status": "canonical",
                                     "_written_by": "w"}])
        assert RK.rake_at(canon)["state"] == "fault"
        # and a record PERMITTING the fault's own rake beside its band has permitted that member:
        # it reads as a silence does, and the fault's rake is drawn (the second independent check,
        # 1 Oct 2026: as first written this kept the flush edge the fault names)
        permf = dict(rec, variants=[{"id": "boxed-rake-with-return", "status": "permitted"}])
        assert (RK.rake_at(permf)["state"], RK.rake_at(permf)["permitted"]) == (
            "silent", ["boxed-rake-with-return"])

    def test_a_record_forbidding_the_faults_rake_and_settling_nothing_else_refuses_it(self):
        """R3, in `rake_at`'s own terms: a record that forbids `boxed-rake-with-return` and makes no
        row canonical and states no trim read as a silence, and a silence draws the fault's rake --
        the very variant it forbids. Unreached by any record today (1 Oct 2026), so driven: it is
        refused by the row's writer, and a trim the record states still decides first."""
        rec = {"binding": "specified", "_bound_by": "b", "variants": [
            {"id": "boxed-rake-with-return", "status": "forbidden", "_written_by": "w"},
            {"id": "close-verge-with-rake-mould", "status": "permitted"}]}
        r = RK.rake_at(rec)
        assert (r["state"], r["variant"], r["writers"]) == ("forbidden", "boxed-rake-with-return", ["w"])
        banded = dict(rec, parameters={"rake_overhang_in": {"range": [6, 12], "unit": "in"}})
        assert RK.rake_at(banded)["state"] == "forbidden"
        trim = dict(rec, parameters={"rake_trim_width_in": {"value": 5.5, "unit": "in", "kind": "measured"}})
        assert RK.rake_at(trim)["state"] == "plain"
        live = dict(rec, variants=rec["variants"] + [{"id": "boxed-rake-with-return", "status": "permitted",
                                                      "applies_when": {"date_range": [1700, 1780]}}])
        assert RK.rake_at(live, 1750)["state"] == "silent", "a row of it still permitted is not refused"

    def test_a_rake_stated_only_in_words_is_quoted_and_never_parsed(self):
        rec = {"binding": "specified", "_bound_by": "elizabethan",
               "rule": "Coped parapet gables with kneelers; the rake is 6 in, say."}
        r = RK.rake_at(rec)
        assert (r["state"], r["writers"], r["rule"]) == ("unread", ["elizabethan"], rec["rule"])
        assert r["trim_in"] is None

    def test_permitted_rows_settle_nothing_and_are_named(self):
        rec = {"binding": "specified", "_bound_by": "b", "variants": [
            {"id": "boxed-rake-with-return", "status": "permitted", "_written_by": "b"},
            {"id": "close-verge-with-rake-mould", "status": "permitted", "_written_by": "b"}]}
        r = RK.rake_at(rec)
        assert (r["state"], r["permitted"]) == ("silent", ["boxed-rake-with-return",
                                                           "close-verge-with-rake-mould"])

    def test_the_tables_are_disjoint_and_total_over_the_rows_the_corpus_uses(self):
        """Every canonical row any node's RESOLVED `rake_condition` carries is one the reader knows
        (the fault's, or one it does not draw), and every id in the two tables is a row somebody
        wrote: a canonical id in neither would read as unjudged on a real house, and an id in a
        table that no record carries is a branch nobody reaches."""
        fault, undrawn = set(RK.RAKE_FAULT_VARIANTS), set(RK.RAKE_UNDRAWN_VARIANTS)
        assert not fault & undrawn
        g = RK.load_graph()
        canonical, used = set(), set()
        for nid in g["nodes"]:
            try:
                slots = RK.resolve_slots(g, RK.chain_for(g, nid), RK.scope_for(g, nid))[0]
            except SystemExit:
                continue
            for v in (slots.get("rake_condition") or {}).get("variants") or []:
                if isinstance(v, dict):
                    used.add(v.get("id"))
                    if v.get("status") == "canonical":
                        canonical.add(v.get("id"))
        assert canonical, "no node makes a rake canonical: the premise of this test is gone"
        assert canonical <= fault | undrawn, sorted(canonical - fault - undrawn)
        assert fault | undrawn <= used, sorted((fault | undrawn) - used)

    def _readings(self):
        g = RK.load_graph()
        out = {}
        for nid in g["nodes"]:
            try:
                slots = RK.resolve_slots(g, RK.chain_for(g, nid), RK.scope_for(g, nid))[0]
            except SystemExit:
                continue
            out[nid] = RK.rake_at(slots.get("rake_condition"))
        return out

    def test_every_fault_reading_carries_the_faults_own_figures_or_none(self):
        """The fault's rake is drawn at the fault's own middles. That is the kit's own figure only
        while every record making the fault's row canonical states the fault's own band or none:
        measured 1 Oct 2026, eleven drawn and three undrawn nodes read georgian-colonial-american's
        record, whose 4 to 8 in and 0.5 to 0.7 are the fault's, and modern-farmhouse-traditional
        (undrawn) reads its own (T1), which states no band in this slot. (Its `eave_condition` states
        a rake overhang of at least 8 in, against the 6 in the fault's rake would print: latent, and
        named in WP-16.9's report.) A record stating that row with another band fails here, so the
        drawing cannot quietly ignore the kit's figure (B5)."""
        f = _fault()
        ov = next(t for t in f["secondary_tests"] if t["expression"] == "rake_overhang_in")
        want = {"rake_overhang_in": [float(ov["threshold"]), float(ov["upper"])]}
        k = re.search(r"at roughly (\d*\.\d+)-(\d*\.\d+) of the eave cornice's members",
                      _words(f["correct_practice"]))
        want["rake_to_cornice_ratio"] = [float(k.group(1)), float(k.group(2))]
        seen = 0
        for nid, r in self._readings().items():
            if r["state"] != "fault":
                continue
            seen += 1
            for key, b in r["bands"].items():
                assert b["range"] == want[key], (nid, key, b["range"], want[key])
        assert seen, "no node reads the fault's rake: the premise of this guard is gone"

    def test_the_corpus_reaches_the_measured_trim_and_the_overhang_state(self):
        """Premise for the two driven tests above: after WP-16.9's records, minimal-traditional states
        one measured board (B29), the plain trims stated as a band or a maximum are judgments, and
        ranch-style (T1) and neo-eclectic (T7) state an overhang and no member (T11), each its own."""
        r = self._readings()
        assert (r["minimal-traditional"]["state"], r["minimal-traditional"]["trim_in"],
                r["minimal-traditional"]["trim_measured"]) == ("plain", 5.5, True)
        for nid in ("cape-cod-colonial", "cape-cod-revival", "american-farmhouse-vernacular"):
            assert (r[nid]["state"], r[nid]["trim_measured"]) == ("plain", False), nid
        assert (r["ranch-style"]["state"], r["ranch-style"]["writers"],
                r["ranch-style"]["bands"]["rake_overhang_in"]["range"]) == ("overhang", ["ranch-style"], [18.0, 36.0])
        assert (r["neo-eclectic"]["state"], r["neo-eclectic"]["writers"],
                r["neo-eclectic"]["bands"]["rake_overhang_in"]["range"]) == ("overhang", ["neo-eclectic"], [6.0, 12.0])
        # every reading with an overhang band and nothing canonical is the overhang state, never silence
        assert not [n for n, x in r.items() if x["state"] == "silent" and x["bands"]]


# ------------------------------------------------------------------ the rake's members
CORNICE = {"members": [
    {"id": "corn_bed_fillet", "profile": "fillet", "height_in": 0.5, "y_bottom_in": 0.0, "y_top_in": 0.5},
    {"id": "corn_bed_ovolo", "profile": "ovolo", "height_in": 1.5, "y_bottom_in": 0.5, "y_top_in": 2.0},
    {"id": "corn_modillion", "profile": "modillion", "height_in": 3.0, "y_bottom_in": 2.0, "y_top_in": 5.0},
    {"id": "corn_corona", "profile": "corona", "height_in": 4.0, "y_bottom_in": 5.0, "y_top_in": 9.0},
    {"id": "corn_cyma", "profile": "cyma-recta", "height_in": 3.0, "y_bottom_in": 9.0, "y_top_in": 12.0},
    {"id": "corn_cyma_fillet", "profile": "fillet", "height_in": 0.5, "y_bottom_in": 12.0, "y_top_in": 12.5}]}


class TestTheMembers:
    def test_crown_then_board_then_bed_mould_each_at_the_scale_from_the_edge_inward(self):
        ms, why = EL.rake_members(CORNICE)
        k = EL.RAKE_MEMBER_SCALE
        assert why is None
        assert [(m["id"], m["kind"], m["depth_in"]) for m in ms] == [
            ("rake_corn_cyma_fillet", "crown", round(0.5 * k, 4)),
            ("rake_corn_cyma", "crown", round(3.0 * k, 4)),
            ("rake_board", "board", EL.RAKE_BOARD_IN),
            ("rake_corn_bed_ovolo", "bed", round(1.5 * k, 4)),
            ("rake_corn_bed_fillet", "bed", round(0.5 * k, 4))]
        # the corona and the modillion band are left out, as the fault says
        assert not {"rake_corn_corona", "rake_corn_modillion"} & {m["id"] for m in ms}

    def test_no_members_or_no_corona_is_the_board_alone_and_says_why(self):
        for cornice, says in (({}, "draws no members"),
                              ({"members": [m for m in CORNICE["members"] if m["profile"] != "corona"]},
                               "no corona")):
            ms, why = EL.rake_members(cornice)
            assert [m["id"] for m in ms] == ["rake_board"] and says in why

    def test_the_shipped_eave_is_read_by_its_own_member_ids(self):
        el = _elev("plans/tidewater-georgian-careful.json")
        ms, why = EL.rake_members(el["eave_cornice"])
        ids = {m["id"] for m in el["eave_cornice"]["members"]}
        kinds = [m["kind"] for m in ms]
        assert why is None and "crown" in kinds and "bed" in kinds, (why, kinds)
        assert all(m["of"] in ids for m in ms if m["kind"] != "board")
        # every crown member stands above the corona, every bed member names `bed`
        top = max(m["y_top_in"] for m in el["eave_cornice"]["members"] if m.get("profile") == "corona")
        by_id = {m["id"]: m for m in el["eave_cornice"]["members"]}
        assert all(by_id[m["of"]]["y_bottom_in"] >= top - 1e-9 for m in ms if m["kind"] == "crown")
        assert all("bed" in m["of"] for m in ms if m["kind"] == "bed")


# ------------------------------------------------------------------ what the gable end draws
class TestTheRake:
    def test_a_forbidden_rake_is_refused_by_its_writer(self):
        rk = EL.rake_for("second-empire", {"state": "forbidden", "writers": ["italianate-american"]}, CORNICE)
        assert (rk["draws"], rk["members"], rk["judgment"]) == ("edge", [], False)
        assert rk["words"].startswith("RAKE NOT DRAWN — FORBIDDEN BY ITALIANATE-AMERICAN")

    def test_the_faults_rake_is_a_judgment_on_its_own_figures(self):
        rk = EL.rake_for("tidewater-georgian", {"state": "fault", "writers": ["georgian-colonial-american"],
                                                "variant": "boxed-rake-with-return"}, CORNICE)
        assert (rk["draws"], rk["judgment"], rk["basis"]) == ("rake", True, list(EL.RAKE_BASIS))
        assert (rk["board_in"], rk["proud_in"], rk["overhang_in"], rk["scale"]) == (
            EL.RAKE_BOARD_IN, EL.RAKE_PROUD_IN, EL.RAKE_OVERHANG_IN, EL.RAKE_MEMBER_SCALE)
        assert [m["id"] for m in rk["members"]] == [m["id"] for m in EL.rake_members(CORNICE)[0]]
        assert rk["words"] == ("RAKE: A 7 IN BOARD CARRYING THE EAVE'S BED MOULD AND CROWN AT 0.6, "
                               "1.25 IN PROUD OF THE WALL AND 6 IN BEYOND IT — THE CARDBOARD GABLE'S OWN "
                               "FIGURES AT THEIR MIDDLES, A JUDGMENT (GEORGIAN-COLONIAL-AMERICAN'S KIT "
                               "STATES THIS RAKE)")

    def test_silence_draws_the_faults_rake_and_says_the_kit_states_none_or_settles_none(self):
        rk = EL.rake_for("x-style", {"state": "silent", "writers": []}, CORNICE)
        assert rk["draws"] == "rake" and rk["words"].endswith("(THE KIT STATES NO RAKE)")
        rk = EL.rake_for("x-style", {"state": "silent", "writers": ["b"],
                                     "permitted": ["boxed-rake-with-return", "close-verge-with-rake-mould"]},
                         CORNICE)
        assert rk["draws"] == "rake" and rk["words"].endswith(
            "(B'S KIT PERMITS BOXED-RAKE-WITH-RETURN, CLOSE-VERGE-WITH-RAKE-MOULD AND SETTLES NONE)")

    def test_a_style_the_fault_excepts_keeps_the_edge_where_its_kit_states_the_faults_rake_or_none(self):
        for style in EL.rake_excepted_styles():
            for state in ("fault", "silent"):
                rk = EL.rake_for(style, {"state": state, "writers": ["w"], "trim_in": 6.0}, CORNICE)
                assert (rk["draws"], rk["members"]) == ("edge", []), (style, state)
                assert f"THE CARDBOARD GABLE EXCEPTS {style.upper()}" in rk["words"]

    def test_an_excepted_style_whose_own_kit_states_its_rake_draws_its_own_B10(self):
        """B10 (30 Sep 2026): B5's kit-first governs an excepted style whose own kit states its rake,
        so minimal-traditional's gable end draws its own plain board, a judgment -- and the edge is
        not what the words say."""
        for style in EL.rake_excepted_styles():
            rk = EL.rake_for(style, {"state": "plain", "writers": [style], "trim_in": 6.0,
                                     "trim_by": style, "trim_basis": "its own 1x6 board"}, CORNICE)
            assert (rk["draws"], rk["judgment"]) == ("plain", True), style
            assert [(m["id"], m["depth_in"]) for m in rk["members"]] == [("rake_trim", 6.0)], style
            assert "EXCEPTS" not in rk["words"] and rk["words"].startswith("RAKE: A PLAIN 6 IN TRIM"), style

    def test_a_plain_trim_is_one_band_at_the_kits_figure_a_judgment(self):
        rk = EL.rake_for("cape-cod-colonial", {"state": "plain", "writers": ["cape-cod-colonial"],
                                               "trim_in": 6.0, "trim_by": "cape-cod-colonial",
                                               "trim_basis": "rake_width_max, 6 in, a maximum drawn at its figure"},
                         CORNICE)
        assert (rk["draws"], rk["judgment"]) == ("plain", True)
        assert [(m["id"], m["kind"], m["depth_in"]) for m in rk["members"]] == [("rake_trim", "trim", 6.0)]
        assert rk["words"] == ("RAKE: A PLAIN 6 IN TRIM, NO MOULDINGS — CAPE-COD-COLONIAL'S OWN KIT "
                               "(RAKE_WIDTH_MAX, 6 IN, A MAXIMUM DRAWN AT ITS FIGURE), A JUDGMENT")

    def test_one_measured_figure_is_drawn_and_said_as_a_measurement_B29(self):
        rk = EL.rake_for("minimal-traditional", {"state": "plain", "writers": ["minimal-traditional"],
                                                 "trim_in": 5.5, "trim_by": "minimal-traditional",
                                                 "trim_basis": "rake_trim_width_in, 5.5 in",
                                                 "trim_measured": True}, CORNICE)
        assert (rk["draws"], rk["judgment"]) == ("plain", False)
        assert [(m["id"], m["depth_in"]) for m in rk["members"]] == [("rake_trim", 5.5)]
        assert rk["words"] == ("RAKE: A PLAIN 5.5 IN TRIM, NO MOULDINGS — MINIMAL-TRADITIONAL'S OWN "
                               "KIT (RAKE_TRIM_WIDTH_IN, 5.5 IN), MEASURED")
        assert "JUDGMENT" not in rk["words"]

    def test_an_overhang_with_no_member_keeps_the_edge_and_says_the_band_T11(self):
        """SETTLES NO MEMBER IN A ROW, and not "NO MEMBER" (the second independent check, 1 Oct 2026):
        a record may name its member in words this reader does not parse, or permit one, and the
        words claim only what the rows say."""
        for style in ("x-style",) + tuple(EL.rake_excepted_styles())[:1]:
            rk = EL.rake_for(style, {"state": "overhang", "writers": ["ranch-style"],
                                     "bands": {"rake_overhang_in": {"range": [18.0, 36.0]}}}, CORNICE)
            assert (rk["draws"], rk["members"], rk["judgment"]) == ("edge", [], False), style
            assert rk["words"] == ("RAKE DRAWN AS THE ROOF'S EDGE — RANCH-STYLE'S KIT STATES A RAKE "
                                   "OVERHANG OF 18–36 IN AND SETTLES NO MEMBER IN A ROW; THE OVERHANG "
                                   "STANDS SQUARE TO THIS FACE, AND NO MEMBER THE KIT DOES NOT SETTLE IS "
                                   "DRAWN"), style
        rk = EL.rake_for("x-style", {"state": "overhang", "writers": ["w"],
                                     "permitted": ["close-verge-with-rake-mould"],
                                     "bands": {"rake_overhang_in": {"range": [6.0, 12.0]}}}, CORNICE)
        assert "SETTLES NO MEMBER IN A ROW, PERMITTING CLOSE-VERGE-WITH-RAKE-MOULD;" in rk["words"]

    def test_a_forbidden_row_is_named_with_its_writer(self):
        rk = EL.rake_for("x-style", {"state": "forbidden", "writers": ["w"],
                                     "variant": "boxed-rake-with-return"}, CORNICE)
        assert (rk["draws"], rk["members"]) == ("edge", [])
        assert rk["words"] == ("RAKE NOT DRAWN — BOXED-RAKE-WITH-RETURN FORBIDDEN BY W'S KIT; THE "
                               "ROOF'S EDGE IS DRAWN")
        whole = EL.rake_for("x-style", {"state": "forbidden", "writers": ["w"]}, CORNICE)
        assert whole["words"] == "RAKE NOT DRAWN — FORBIDDEN BY W'S KIT; THE ROOF'S EDGE IS DRAWN"

    def test_a_rake_this_generator_does_not_draw_or_read_keeps_the_edge_and_says_which(self):
        cases = {"undrawn": ({"variant": "kneelers-and-raised-coping"}, "MAKES KNEELERS-AND-RAISED-COPING "
                                                                        "CANONICAL, WHICH THIS GENERATOR DOES NOT DRAW"),
                 "unjudged": ({"variant": "a-new-rake"}, "RAKE UNJUDGED — W'S KIT MAKES A-NEW-RAKE CANONICAL"),
                 "unread": ({"rule": "Coped   parapet\ngables."}, "STATES ITS RAKE ONLY IN WORDS, WHICH ARE "
                                                                 "NOT READ: “COPED PARAPET GABLES.”")}
        for state, (extra, says) in cases.items():
            rk = EL.rake_for("x-style", dict({"state": state, "writers": ["w"]}, **extra), CORNICE)
            assert (rk["draws"], rk["judgment"]) == ("edge", False), state
            assert says in rk["words"], (state, rk["words"])

    def test_no_eave_members_is_the_board_alone_and_the_words_say_why(self):
        rk = EL.rake_for("x-style", {"state": "silent"}, {})
        assert [m["id"] for m in rk["members"]] == ["rake_board"]
        assert "ALONE: THE EAVE CORNICE DRAWS NO MEMBERS" in rk["words"]


# ------------------------------------------------------------------ the marks the sheet and the DXF draw
def _poly_ok(el, face, rm):
    """The bands of one gable end, re-derived here from the edge the face draws and the members'
    depths: from the edge inward, each band's outer line the last one's inner line, square to the
    slope at its member's depth, dying into the cornice's top, meeting the other slope plumb."""
    roof = el["roof_record"]
    lift = el["grade_to_true_eave_in"] / 12.0 - roof["main"]["grade_to_eave_ft"]
    prof = [(u, h + lift) for u, h in EL.face_profile(roof, face, el["footprint"])]
    assert len(prof) == 3
    apex, members = prof[1], el["rake"]["members"]
    for slope, eave in (("left", prof[0]), ("right", prof[2])):
        bands = [b for b in rm["bands"] if b["slope"] == slope]
        du, dh = apex[0] - eave[0], apex[1] - eave[1]
        vert = math.hypot(du, dh) / abs(du)
        assert [b["member"] for b in bands] == [m["id"] for m in members][:len(bands)]
        d = 0.0
        for b, m in zip(bands, members):
            (u0, h0), (ua, ha), (ub, hb), (u1, h1) = b["poly"]
            assert h0 == pytest.approx(eave[1], abs=1e-3) and h1 == pytest.approx(eave[1], abs=1e-3)
            assert ua == pytest.approx(apex[0], abs=1e-3) and ub == pytest.approx(apex[0], abs=1e-3)
            assert apex[1] - ha == pytest.approx(d * vert, abs=1e-3)
            d += m["depth_in"] / 12.0
            assert apex[1] - hb == pytest.approx(d * vert, abs=1e-3)
            # the outer line is the roof's edge moved plumb, so it keeps the edge's slope
            assert (ha - h0) / (ua - u0) == pytest.approx(dh / du, rel=1e-3)
        # every member is drawn whose inner line clears the cornice's top
        assert len(bands) == sum(1 for i in range(len(members))
                                 if sum(x["depth_in"] for x in members[:i + 1]) / 12.0 * vert < dh)


class TestTheUnridgedGable:
    """A ROOF THAT JUDGES NO RIDGE GIVES THE GABLE END NO SLOPE. Measured 1 Oct 2026, with WP-16.9's
    records: the kit asks a rake on the gable ends of eight of the ten drawn shipped plans whose
    roof judges none (colonial-revival's five, good-02, good-07 and bad-03), because no roof-pitch
    constraint is migrated for their styles. Each draws no band, its gable ends say why, and its
    eave faces do not say the gable ends draw a rake. Found by reading, not named.

    THE CAUSE WAS FIRST WORDED "NO PITCH IS STATED", AND THAT WAS FALSE OF ALL FOUR STYLES (the
    second independent check, 1 Oct 2026): each resolved kit states a pitch in its `roof_pitch`
    slot (colonial-revival and georgian-revival queen-anne-american's 9:12 and over, new-urbanist-
    traditional folk-victorian's 6:12 to 12:12, new-classical greek-classical's 12 to 17 degrees),
    which roof.py does not read. The words say what roof.py lacks, and name the style."""

    @staticmethod
    def NO_RIDGE(style):
        return ("; NOT DRAWN — THE ROOF JUDGES NO RIDGE (NO ROOF-PITCH CONSTRAINT IS MIGRATED FOR %s), "
                "SO THE GABLE END HAS NO SLOPE TO CARRY IT" % style.upper())

    def test_every_gable_end_under_no_ridge_draws_no_rake_and_says_why(self):
        seen = 0
        for rel in PLANS:
            el = _elev(rel)
            if "eave_cornice" not in el:
                continue                   # the elevation refuses the style outright (its gate)
            gf = EL.gable_faces(el["roof_record"])
            if (el.get("rake") or {}).get("draws") not in ("rake", "plain") or not gf or _ridged(el):
                continue
            seen += 1
            for face in ("S", "N", "E", "W"):
                rm = EL.rake_marks(el, face)
                assert rm["bands"] == [], (rel, face)
                if face in gf:
                    assert rm["words"] == el["rake"]["words"] + self.NO_RIDGE(el["roof_record"]["style"]), (rel, face)
                else:
                    assert rm["words"] is None, (rel, face)
        assert seen, "no shipped plan asks a rake under a roof with no ridge: the premise is gone"

    def test_the_cause_is_the_roofs_and_a_ridged_outline_that_is_no_triangle_says_the_other(
            self, raked, monkeypatch):
        el = copy.deepcopy(raked[0][1])
        face = EL.gable_faces(el["roof_record"])[0]
        el["roof_record"]["main"]["pitch_rise_per_12"] = None
        monkeypatch.setattr(EL, "face_profile", lambda roof, f, fp: [(0.0, 0.0), (1.0, 0.0)])
        assert EL.rake_marks(el, face)["words"].endswith(self.NO_RIDGE(el["roof_record"]["style"]))
        eave = next(f for f in ("S", "N", "E", "W") if f not in EL.gable_faces(el["roof_record"]))
        assert EL.rake_marks(el, eave)["words"] is None


class TestTheMarks:
    def test_each_member_is_a_band_along_each_slope_square_to_it_from_the_edge_inward(self, raked):
        for rel, el in raked:
            for face in EL.gable_faces(el["roof_record"]):
                rm = EL.rake_marks(el, face)
                assert rm["on_gable"] and rm["bands"], (rel, face)
                _poly_ok(el, face, rm)
                assert rm["words"] == el["rake"]["words"]

    def test_a_face_that_is_not_a_gable_end_draws_none_and_says_its_overhang_is_not_drawn(self, raked):
        rel, el = raked[0]
        eaves = [f for f in ("S", "N", "E", "W") if f not in EL.gable_faces(el["roof_record"])]
        assert eaves
        for face in eaves:
            rm = EL.rake_marks(el, face)
            assert (rm["on_gable"], rm["bands"]) == (False, [])
            assert "ITS OVERHANG PAST EACH CORNER IS NOT DRAWN ON THIS FACE" in rm["words"]

    def test_a_hipped_roof_has_no_rake_on_any_face(self, raked):
        el = copy.deepcopy(raked[0][1])
        el["roof_record"]["main"]["form"] = "hip"
        for face in ("S", "N", "E", "W"):
            assert EL.rake_marks(el, face) == {"face": face, "on_gable": False, "draws": None,
                                               "bands": [], "words": None}

    def test_the_edge_draws_no_band_and_says_why(self, raked):
        el = copy.deepcopy(raked[0][1])
        el["rake"] = EL.rake_for(el["style"], {"state": "forbidden", "writers": ["w"]}, el["eave_cornice"])
        face = EL.gable_faces(el["roof_record"])[0]
        rm = EL.rake_marks(el, face)
        assert rm["bands"] == [] and rm["words"].startswith("RAKE NOT DRAWN — FORBIDDEN BY W")

    def test_a_band_that_never_clears_the_cornice_is_not_drawn(self, raked):
        el = copy.deepcopy(raked[0][1])
        face = EL.gable_faces(el["roof_record"])[0]
        # a member deeper than the gable rises: the ones beyond it cannot clear the cornice's top
        el["rake"]["members"] = [{"id": "a", "kind": "board", "depth_in": 6.0},
                                 {"id": "deep", "kind": "board", "depth_in": 12.0 * 60},
                                 {"id": "beyond", "kind": "bed", "depth_in": 1.0}]
        rm = EL.rake_marks(el, face)
        assert {b["member"] for b in rm["bands"]} == {"a"}
        _poly_ok(el, face, rm)

    def test_a_gable_whose_outline_is_not_a_triangle_is_not_drawn_and_says_so(self, raked, monkeypatch):
        el = raked[0][1]
        face = EL.gable_faces(el["roof_record"])[0]
        monkeypatch.setattr(EL, "face_profile", lambda roof, f, fp: [(0.0, 0.0), (1.0, 1.0)])
        rm = EL.rake_marks(el, face)
        assert rm["bands"] == [] and rm["words"].endswith("NOT DRAWN — THE GABLE'S OUTLINE IS NOT A TRIANGLE")


class TestTheSurfaces:
    def test_the_sheet_draws_the_bands_where_the_marks_put_them_and_says_the_rake(self, raked, tmp_path):
        R = _m("render_elevation")
        rel, el = raked[0]
        for face in ("S", "N", "E", "W"):
            out = str(tmp_path / f"{face}.svg")
            R.render_elevation(el, out, face=face)
            svg = open(out, encoding="utf-8").read()
            ink = IR.Ink(svg)
            pl = next(p for p in ink.frames() if p.get("face") == face)
            want = EL.rake_marks(el, face)["bands"]
            got = [it for it in ink.items if it.attrs.get("data-rake")]
            assert len(got) == len(want), (rel, face)
            for it, b in zip(got, want):
                assert (it.attrs["data-rake"], it.attrs["data-rake-kind"]) == (b["member"], b["kind"])
                pts = [IR.to_model(pl, x, y) for x, y in it.points(n=1)][:4]
                for (u, h), (bu, bh) in zip(pts, b["poly"]):
                    assert abs(u - bu) < 0.01 and abs(h - bh) < 0.01
            said = _words(" ".join(t for t, _a, _it in ink.texts() if t)).upper()
            words = EL.rake_marks(el, face)["words"]
            assert words and _words(words) in said, (face, words)

    def test_the_dxf_draws_the_same_bands_each_naming_its_member(self, raked, tmp_path):
        ezdxf = pytest.importorskip("ezdxf")
        DX = _m("export_dxf")
        rel, el = raked[0]
        face = EL.gable_faces(el["roof_record"])[0]
        path = str(tmp_path / "e.dxf")
        DX.export_elevation_dxf(el, path, face=face)
        got = []
        for e in ezdxf.readfile(path).modelspace().query("LWPOLYLINE"):
            try:
                x = "".join(str(v) for _c, v in e.get_xdata("TDL"))
            except Exception:  # noqa: BLE001 -- an entity with no XDATA is not a rake band
                continue
            if "TDL::rake-member" in x:
                assert e.closed and e.dxf.layer == "TDL-ELEV-ROOF"
                got.append((re.search(r'"member":\s*"([^"]+)"', x).group(1),
                            [(round(p[0], 2), round(p[1], 2)) for p in e.get_points()]))
        want = [(b["member"], [(round(u * 12.0, 2), round(h * 12.0, 2)) for u, h in b["poly"]])
                for b in EL.rake_marks(el, face)["bands"]]
        assert got == want


_PARTS = {}


def _parts(rel):
    """The placed plan, the section, the roof and the elevation, built as `_build` builds them."""
    if rel not in _PARTS:
        G, ST, RF = _m("geometry"), _m("structure"), _m("roof")
        p = G.solve(json.load(open(os.path.join(ROOT, rel))), engine="heuristic")
        sec = ST.build_section(p, None, geometry_result=p)
        rf = RF.build_roof(p, None, section=sec)
        _PARTS[rel] = (p, sec, rf, EL.build_elevation(p, None, section=sec, roof=rf))
    return _PARTS[rel]


class TestTheRoofPlanAndTheModelSayWhereTheRoofStops:
    """The elevation's gable faces draw the rake past the wall; the roof plan and the model draw the
    roof record, which stops at the gable wall (WP-16.9, on V19's precedent: one roof, two extents,
    said on each surface). The roof plan says what it DRAWS, and claims no rake; the model names the
    rake as not modelled only where the elevation really draws a member, because a refusal about a
    rake that is not there would be a refusal about nothing."""

    def test_a_gabled_roof_plan_says_it_is_drawn_to_the_gable_wall(self, raked, tmp_path):
        RR, DISC = _m("render_roof"), _m("disclosures")
        rel, _el = raked[0]
        _p, _s, rf, _e = _parts(rel)
        line = DISC.roof_stops_at_the_gable_wall(EL.gable_faces(rf))
        assert line, rel
        out = str(tmp_path / "r.svg")
        RR.render_roof(rf, out)
        said = _words(" ".join(t for t, _a, _it in IR.Ink(open(out, encoding="utf-8").read()).texts() if t))
        assert _words(line) in said, rel

    def test_a_roof_with_no_gable_end_says_nothing_of_one(self, tmp_path):
        RR, DISC = _m("render_roof"), _m("disclosures")
        assert DISC.roof_stops_at_the_gable_wall(()) is None
        assert DISC.roof_stops_at_the_gable_wall(None) is None
        hipped = [rel for rel in PLANS if (_parts(rel)[2].get("main") or {}).get("form") == "hip"]
        assert hipped, "no shipped plan is hipped, so nothing here reaches the empty case"
        out = str(tmp_path / "h.svg")
        RR.render_roof(_parts(hipped[0])[2], out)
        assert "GABLE WALL" not in open(out, encoding="utf-8").read(), hipped[0]

    def test_the_model_names_the_rake_the_elevation_draws_and_says_why(self, raked):
        SC = _m("scene")
        rel, _el = raked[0]
        p, sec, rf, el = _parts(rel)
        said = [n for n in SC.build_scene(p, sec, rf, el)["not_modelled"]
                if n["what"] == "the rake at each gable end"]
        assert len(said) == 1 and said[0]["class"] == "roof", rel
        assert _words(el["rake"]["words"]).lower() in said[0]["why"]
        assert "stops at the gable wall" in said[0]["why"]

    def test_the_model_names_nothing_where_the_elevation_draws_no_member(self, raked):
        SC = _m("scene")
        rel, _el = raked[0]
        p, sec, rf, el = _parts(rel)
        flush = dict(el, rake=dict(el["rake"], draws="edge", members=[]))
        for e in (flush, None):
            assert not [n for n in SC.build_scene(p, sec, rf, e)["not_modelled"]
                        if n["what"] == "the rake at each gable end"], (rel, e is None)


# ------------------------------------------------------------------ B6 and B2: the gable end the faults need
def _state(el, fid):
    r = CORE.check_measurements(el["measurements"], style=el["style"], limit=10**6)
    for state, key in (("present", "faults_present"), ("clear", "faults_clear"),
                       ("needed", "could_not_judge"), ("not_applicable", "not_applicable")):
        if any(x["fault"] == fid for x in r[key]):
            return state
    return None


def _all_tests(fid):
    with open(os.path.join(ROOT, "faults", fid + ".json"), encoding="utf-8") as fh:
        d = json.load(fh)
    return [d["test"]] + list(d.get("secondary_tests") or []) + \
        [e["bounds_test"] for e in d.get("exceptions") or [] if e.get("bounds_test")]


def _with_roof(el, form):
    """The same elevation with its roof record's form replaced, the gable reading re-derived, and
    its measurements re-taken."""
    el = copy.deepcopy(el)
    el["roof_record"]["main"]["form"] = form
    cr = el.get("cornice_return") or {}
    reading = {k: cr.get(k) for k in ("state", "writers", "variant", "band_in", "dated", "date",
                                      "date_unstated", "min_cornice_in", "min_cornice_by")}
    el["cornice_return"] = EL.cornice_return(reading, el["eave_cornice"], el["roof_record"])
    el["measurements"] = EL._derive_measurements(el)
    return el


class TestTheGates:
    GATE = {"expression": "count_of_gable_end_walls", "direction": "at-least", "threshold": 1}

    @pytest.mark.parametrize("fid", ["flush-rake", "return-that-never-returns"])
    def test_every_test_is_gated_on_a_drawn_gable_end(self, fid):
        tests = _all_tests(fid)
        assert len(tests) >= 3
        for t in tests:
            aw = t.get("applies_when") or {}
            assert {k: aw.get(k) for k in self.GATE} == self.GATE, (fid, t["expression"])
            assert "B6" in aw.get("note", "") if fid == "flush-rake" else "B2" in aw.get("note", "")

    def test_the_count_is_the_roofs_own_gable_ends(self):
        el = _elev("plans/tidewater-georgian-careful.json")
        assert el["measurements"]["count_of_gable_end_walls"] == len(EL.gable_faces(el["roof_record"]))
        assert _with_roof(el, "hip")["measurements"]["count_of_gable_end_walls"] == 0
        # a form the generator does not model is unmeasured, which is not published at all
        assert "count_of_gable_end_walls" not in _with_roof(el, "mansard")["measurements"]

    def test_a_hipped_house_is_not_asked_either_question_and_an_unmodelled_roof_is_not_judged(self):
        el = _elev("plans/tidewater-georgian-careful.json")
        hip, mansard = _with_roof(el, "hip"), _with_roof(el, "mansard")
        for fid in ("flush-rake", "return-that-never-returns"):
            assert _state(hip, fid) == "not_applicable", fid
            assert _state(mansard, fid) == "needed", fid

    def test_a_drawn_rake_is_withheld_from_its_fault(self, raked):
        for name in ("rake_overhang_in", "rake_member_projection_from_siding_face_in",
                     "raking_cornice_member_count"):
            assert name in EL.NOT_MODELLED
        for rel, el in raked:
            assert not {"rake_overhang_in", "rake_member_projection_from_siding_face_in"} & set(el["measurements"])
            # the governing test cannot run on a figure withheld, so the fault is not judged: never
            # a clear on the fault's own rule handed back to it
            assert _state(el, "flush-rake") in ("needed", "not_applicable"), rel


# ------------------------------------------------------------------ B4: a cornice deepened to its kit's minimum
class TestTheDeepenedCornice:
    def _packs(self):
        PE = _m("proportion_engine")
        return PE.resolve("facade-classical"), PE.resolve("gibbs-ionic")

    def test_the_minimum_is_taken_only_where_the_kit_permits_the_return_it_conditions(self):
        base = {"min_cornice_in": 10.0, "min_cornice_by": "colonial-revival"}
        for state in ("unsettled", "stated", "plain"):
            assert EL.cornice_minimum(dict(base, state=state)) == {"in": 10.0, "by": "colonial-revival"}
        for state in ("forbidden", "none", "silent", "unjudged"):
            assert EL.cornice_minimum(dict(base, state=state)) is None, state
        assert EL.cornice_minimum({"state": "unsettled", "min_cornice_in": None}) is None
        assert EL.cornice_minimum(None) is None

    def test_a_deeper_minimum_deepens_the_projection_and_keeps_the_heights(self):
        fc, gi = self._packs()
        plain = EL.eave_cornice(fc, gi, module_in=120.0)
        env = plain["envelope_projection_in"]
        deep = EL.eave_cornice(fc, gi, module_in=120.0, minimum={"in": env + 1.4, "by": "k"})
        assert deep["envelope_projection_in"] == pytest.approx(env + 1.4, abs=1e-3)
        assert (deep["facade_envelope_projection_in"], deep["projection_minimum"]) == (
            env, {"in": env + 1.4, "by": "k", "deepened": True})
        assert [(m["id"], m["height_in"]) for m in deep["members"]] == [
            (m["id"], m["height_in"]) for m in plain["members"]]
        assert deep["cornice_height_in"] == plain["cornice_height_in"]
        assert deep["bed_mould_projection_in"] == plain["bed_mould_projection_in"]
        assert deep["projection_ruling"].startswith("B4, ruled 30 Sep 2026")
        assert EL.cornice_depth_words(deep) == (
            f"{env + 1.4:.1f} IN, K'S MINIMUM FOR A CORNICE UNDER ITS RETURN, DEEPER THAN THE "
            f"ENVELOPE'S {env:.1f} IN")

    def test_a_shallower_minimum_or_a_refused_cornice_deepens_nothing(self):
        fc, gi = self._packs()
        plain = EL.eave_cornice(fc, gi, module_in=120.0)
        env = plain["envelope_projection_in"]
        shallow = EL.eave_cornice(fc, gi, module_in=120.0, minimum={"in": env - 1.0, "by": "k"})
        assert shallow["envelope_projection_in"] == env
        assert shallow["projection_minimum"] == {"in": env - 1.0, "by": "k", "deepened": False}
        assert {k: v for k, v in shallow.items() if k != "projection_minimum"} == {
            k: v for k, v in plain.items() if k != "projection_minimum"}
        assert EL.cornice_depth_words(shallow) is None and EL.cornice_depth_words(plain) is None
        refused = EL.eave_cornice(fc, gi, module_in=120.0, minimum={"in": env + 5, "by": "k"},
                                  refused={"cornice": {"writers": ["x"]}})
        assert (refused["envelope_projection_in"], refused["projection_minimum"]) == (None, None)

    def test_the_six_shipped_records_carrying_colonial_revivals_minimum_are_drawn_that_deep(self):
        """Measured 30 Sep 2026: the spec Colonial, bad-01, bad-02, bad-05, bad-07 and good-02 carry
        colonial-revival's 10 in through the cascade and drew 8.6 or 9.6 in; good-07's 11.5 in
        already met it. Found by reading each plan's own kit, not by naming them."""
        seen = 0
        for rel in PLANS:
            el = _elev(rel)
            if "eave_cornice" not in el:
                continue                   # the elevation refuses the style outright (its gate)
            rr = RK.return_at(_slots(el["style"]).get("cornice_return"))
            cor = el["eave_cornice"]
            if rr.get("min_cornice_in") is None or not cor.get("members"):
                assert (cor.get("projection_minimum") or {}).get("deepened") in (None, False), rel
                continue
            seen += 1
            assert cor["envelope_projection_in"] >= rr["min_cornice_in"] - 1e-9, rel
            assert cor["projection_minimum"]["deepened"] == (
                cor["facade_envelope_projection_in"] < rr["min_cornice_in"] - 1e-9), rel
        assert seen >= 6

    def test_the_inset_and_the_dxf_name_both_figures_and_who_wrote_the_minimum(self, tmp_path):
        el = _elev("plans/spec-builder-colonial.json")
        words = EL.cornice_depth_words(el["eave_cornice"], "″")
        assert words and "COLONIAL-REVIVAL'S MINIMUM" in words
        out = str(tmp_path / "S.svg")
        _m("render_elevation").render_elevation(el, out, face="S")
        said = _words(" ".join(t for t, _a, _it in IR.Ink(open(out, encoding="utf-8").read()).texts() if t))
        assert f"PROJECTIONS SCALED INTO {words}, IN THE ORDER'S SHAPE" in said
        ezdxf = pytest.importorskip("ezdxf")
        path = str(tmp_path / "e.dxf")
        _m("export_dxf").export_elevation_dxf(el, path, face="S")
        texts = " ".join(_words(e.dxf.text) for e in ezdxf.readfile(path).modelspace().query("TEXT MTEXT")
                         if hasattr(e.dxf, "text"))
        assert EL.cornice_depth_words(el["eave_cornice"], " IN") in texts
