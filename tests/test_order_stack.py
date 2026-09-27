"""The order stack is the one each pack STATES (WP-14.2, step 7).

Three defects in `proportion_engine`, each found by census E1-E3 drawing a stack the pack does not
state, and each wrong on every surface that draws an order -- the orders page, the Proportions
plate, the profile plates' frames:

* An overlay that states its column height and INHERITS its shaft drew the base authority's shaft
  under its own column: benjamin-corinthian 120 in against a stated 132 at a 6 in module, gibbs-ionic
  110 against 108. Five overlays. The shaft is the column less the base and capital drawn --
  `_synth_shaft`'s own rule -- and where the overlay states its shaft too the two agree exactly.
* An overlay that states its WHOLE entablature and inherited a finer triplet that contradicts it
  drew the triplet: benjamin-corinthian 30 in against 24. Four overlays.
* Benjamin's subplinth, which he offers INSTEAD of a pedestal, was stacked ON it.

The rules are held on the whole corpus and each is DRIVEN where the corpus reaches only one side.
"""
import copy
import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

PE = modcache.load("proportion_engine", os.path.join(ROOT, "build", "proportion_engine.py"))


def _orders():
    return sorted(p for p, r in PE.PACKS.items() if r.get("kind") == "order-system")


def _heights(pid, **kw):
    r = PE.resolve(pid)
    d = PE.dimension(r, 6.0, include=PE.stack_for(r, **kw) if kw else None)
    return r, d, {a["id"]: a["y_top_in"] - a["y_bottom_in"] for a in d["assemblies"]}


# ------------------------------------------------------------------ the column
class TestTheColumnIsTheOneThePackStates:
    def test_every_stated_column_is_drawn_at_its_stated_height(self):
        checked = 0
        for pid in _orders():
            _r, d, H = _heights(pid)
            col = d["totals"].get("column_height_in")
            if not col or "shaft" not in H or "capital" not in H:
                continue
            assert sum(H.get(a, 0.0) for a in ("base", "shaft", "capital")) == pytest.approx(col, abs=1e-6), pid
            checked += 1
        assert checked >= 24, checked

    def test_the_five_overlays_the_rule_moved(self):
        """Measured when the rule landed, at a 6 in module: what each STATES and what it drew."""
        was = {"benjamin-corinthian": 120.0, "benjamin-ionic": 108.0, "benjamin-tuscan": 84.0,
               "gibbs-ionic": 110.0, "palladio-corinthian": 60.0}
        for pid, drew in was.items():
            r, d, H = _heights(pid)
            now = H["base"] + H["shaft"] + H["capital"]
            assert now == pytest.approx(d["totals"]["column_height_in"]) and now != pytest.approx(drew), pid
            assert "_height_from_column" in r["assemblies"]["shaft"], pid
            assert any(n.startswith("shaft: its height is") for n in r["_overlay_notes"]), pid

    def test_where_the_overlay_states_its_shaft_the_derived_one_is_that_shaft(self):
        """The evidence this is the authors' own rule: the three overlays stating both a column and
        a shaft get the shaft they state, to the part."""
        for pid in ("benjamin-corinthian", "benjamin-tuscan", "gibbs-ionic"):
            raw = PE.PACKS[pid]["column"]["shaft_height_modules"]
            assert PE.resolve(pid)["assemblies"]["shaft"]["height_modules"] == pytest.approx(raw), pid

    def test_the_inherited_members_stay_and_only_the_body_takes_the_difference(self):
        base = PE.resolve("vignola-corinthian")["assemblies"]["shaft"]["members"]
        mine = PE.resolve("benjamin-corinthian")["assemblies"]["shaft"]
        body = mine["_height_from_column"]["body"]
        conv = 30 / 18                      # Vignola's Corinthian parts in Benjamin's
        assert [m["id"] for m in mine["members"]] == [m["id"] for m in base]
        for a, b in zip(base, mine["members"]):
            assert a["profile"] == b["profile"]
            if b["id"] != body:
                assert b["height_parts"] == pytest.approx(a["height_parts"] * conv), b["id"]
        assert sum(m["height_parts"] for m in mine["members"]) == pytest.approx(mine["height_modules"] * 30)

    def test_an_overlay_whose_own_column_and_shaft_disagree_is_left_alone_and_noted(self, monkeypatch):
        """Driven: no pack does this. The engine does not choose between two of a pack's own
        statements; the column stays as inherited and census E1 says it is drawn wrong."""
        raw = copy.deepcopy(PE.PACKS["gibbs-ionic"])
        raw["column"]["shaft_height_modules"] = 15.0
        monkeypatch.setitem(PE.PACKS, "gibbs-ionic", raw)
        r = PE.resolve("gibbs-ionic")
        assert "_height_from_column" not in r["assemblies"]["shaft"]
        assert any("two of the pack's own statements disagree" in n for n in r["_overlay_notes"])

    def test_a_pack_that_is_not_an_overlay_is_never_re_derived(self):
        for pid in _orders():
            if not PE.PACKS[pid].get("overlay_of"):
                assert "_height_from_column" not in (PE.resolve(pid)["assemblies"].get("shaft") or {}), pid


# ------------------------------------------------------------------ the entablature
class TestTheEntablatureIsTheOneThePackStates:
    WHOLE = {"benjamin-corinthian", "benjamin-ionic", "palladio-composite", "palladio-corinthian"}

    def test_every_stated_entablature_is_drawn_at_its_stated_height(self):
        for pid in _orders():
            _r, d, H = _heights(pid)
            ent = d["totals"].get("entablature_height_in")
            if ent:
                drawn = sum(H.get(a, 0.0) for a in ("architrave", "frieze", "cornice", "entablature"))
                assert drawn == pytest.approx(ent, abs=1e-6), pid

    def test_exactly_the_contradicted_overlays_draw_their_own_whole(self):
        whole = {pid for pid in _orders() if "entablature" in PE.stack_for(PE.resolve(pid))
                 and all(x in PE.resolve(pid)["assemblies"] for x in PE.ENT_TRIPLET)}
        assert whole == self.WHOLE

    def test_a_triplet_that_divides_the_packs_own_total_is_kept(self):
        """gibbs-doric states a 4-module entablature, and Vignola's architrave and frieze with
        Gibbs's own cornice make 4; benjamin-tuscan states 3.5 and Vignola's whole triplet makes 3.5.
        Both keep their triglyphs, mutules and mouldings. The first version of the rule threw them
        away."""
        for pid in ("gibbs-doric", "benjamin-tuscan"):
            r = PE.resolve(pid)
            assert r["_owner"]["entablature"] == pid, "premise"
            assert any(r["_owner"][x] != pid for x in PE.ENT_TRIPLET), "premise: part is inherited"
            assert PE.stack_for(r)[-3:] == list(PE.ENT_TRIPLET), pid

    def test_the_triplet_can_still_be_asked_for_and_its_plate_still_drawn(self):
        r = PE.resolve("benjamin-corinthian")
        assert PE.stack_for(r, entablature="triplet")[-3:] == list(PE.ENT_TRIPLET)
        RP = modcache.load("render_profile", os.path.join(ROOT, "build", "render_profile.py"))
        svg, rep = RP.render("benjamin-corinthian", "cornice", 6.0)
        assert "INHERITED" in re.sub(r"<[^>]+>", " ", svg).upper()

    def test_the_stack_says_what_it_drew_whole_and_whose_triplet_it_left(self):
        _r, d, _H = _heights("benjamin-corinthian")
        n = next(x for x in d["stack_notes"] if x["kind"] == "entablature-whole")
        assert n["owner"] == "benjamin-corinthian"
        assert set(n["triplet_owners"].values()) == {"vignola-corinthian"}


# ------------------------------------------------------------------ an alternative
class TestAnAlternativeIsNotALayer:
    def test_benjamins_subplinth_is_offered_instead_of_the_pedestal_and_says_so_in_his_words(self):
        for pid in ("benjamin-corinthian", "benjamin-ionic", "benjamin-tuscan"):
            sub = PE.PACKS[pid]["assemblies"]["subplinth"]
            assert sub["alternative_to"] == "pedestal"
            assert "subplinth" in sub["alternative_note"] and "'" in sub["alternative_note"], pid
            r, d, H = _heights(pid)
            assert "pedestal" in H and "subplinth" not in H, pid
            n = next(x for x in d["stack_notes"] if x["kind"] == "alternative")
            assert (n["assembly"], n["instead_of"], n["drawn"]) == ("subplinth", "pedestal", "pedestal")

    def test_the_whole_benjamin_sets_it_out_in_holds_no_pedestal(self):
        """The arithmetic each note quotes, re-derived: column + entablature + subplinth, in
        diameters, is the whole Benjamin divides."""
        whole = {"benjamin-tuscan": 43 / 4, "benjamin-ionic": 51 / 4, "benjamin-corinthian": 28 / 2}
        for pid, w in whole.items():
            r = PE.resolve(pid)
            dpm = PE.diameters_per_module(r)
            got = (r["column"]["height_modules"] + r["assemblies"]["entablature"]["height_modules"]
                   + r["assemblies"]["subplinth"]["height_modules"]) * dpm
            assert got == pytest.approx(w), pid

    def test_without_the_assembly_it_replaces_the_alternative_is_drawn(self):
        """Driven: every pack with an alternative also draws the pedestal it replaces (and an
        overlay deleting its own would inherit Vignola's), so the resolved pack is cut instead."""
        r = PE.resolve("benjamin-tuscan")
        del r["assemblies"]["pedestal"]
        assert "subplinth" in PE.stack_for(r)
        d = PE.dimension(r, 6.0)
        assert not any(n["kind"] == "alternative" for n in d["stack_notes"])


# ------------------------------------------------------------------ the elevation's inset
class TestTheInsetNamesThePackItDraws:
    def test_the_caption_is_the_pack_the_cornice_was_drawn_from(self, tmp_path):
        """The inset's caption read 'GIBBS IONIC' as a literal whatever pack eave_cornice() had
        been handed. It names the pack now, and a cornice that pack inherits says whose it is --
        driven, since the shipped elevation draws gibbs-ionic's own cornice."""
        import json
        EL = modcache.load("elevation", os.path.join(ROOT, "build", "elevation.py"))
        RE = modcache.load("render_elevation", os.path.join(ROOT, "build", "render_elevation.py"))
        plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
        elev = EL.build_elevation(plan)
        ec = elev["eave_cornice"]
        assert (ec["order_pack"], ec["cornice_owner"]) == ("gibbs-ionic", "gibbs-ionic")

        def caption(e):
            out = tmp_path / "e.svg"
            RE.render_elevation(e, str(out))
            return re.sub(r"\s+", " ", " ".join(re.findall(r">([^<]*)</text>", out.read_text())))

        assert "GIBBS-IONIC · %d MEMBERS" % len(ec["members"]) in caption(elev)
        other = copy.deepcopy(elev)
        other["eave_cornice"].update(order_pack="chambers-ionic", cornice_owner="vignola-ionic")
        text = caption(other)
        assert "CHAMBERS-IONIC (THE CORNICE VIGNOLA-IONIC'S)" in text and "GIBBS" not in text
