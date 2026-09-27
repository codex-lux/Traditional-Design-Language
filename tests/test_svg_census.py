"""The census's own guards (WP-14.1).

`tests/svg_census.py` answers Lucas's question -- does every drawn figure on every surface agree
with the record it was drawn from -- as a table. These tests keep the table honest in the four
ways a table goes wrong: it stops covering the tree (a new surface nobody listed), it stops
matching the corpus (a disagreement nobody pinned, or a fix nobody unpinned), it stops matching
its own document, and it stops being able to say "disagrees" at all.

The last is the one this repository keeps meeting. A check whose disagreeing branch the corpus
never reaches is green whatever the ink does, so a check with no live disagreement is DRIVEN here
where it can be: the defect it exists to catch is planted in a copy of a real plate, in memory,
and the check must report it. Nothing here writes inside the repository.

NOT EVERY ONE, AND THIS SAID EVERY ONE UNTIL WP-14.6 (G6). Counted at WP-14.6: of 68 checks, 64
carry no live disagreement and 17 of those are driven in this file. The other 47 are held by
nothing here. Where one was mutation-checked when it was written -- the defect injected into the
SUBJECT, in an isolated copy, and the check seen to go red -- that is recorded in its package's
report, and it is a proof made once; a drive is a proof made every run. A check among the 47
whose disagreeing branch goes blind later is caught by nothing in this file.
"""
import json
import os
import re
import subprocess
import sys

import pytest

import ink_surfaces as SURF
import svg_census as C

_ROWS = None


def _rows():
    global _ROWS
    if _ROWS is None:
        _ROWS = C.run()
    return _ROWS


# ------------------------------------------------------------------ the registry is the tree
class TestTheRegistryIsTheTree:
    def test_every_file_that_draws_svg_is_registered(self):
        missing = C.unregistered()
        assert not missing, (
            "these files emit SVG and tests/svg_census.py's REGISTRY does not name them: %s. A "
            "surface that draws a building needs census rows; one that does not needs a row with "
            "role 'out-of-scope' and a reason." % missing)

    def test_every_registered_file_exists(self):
        """A row naming a file that is gone is a claim of coverage over nothing."""
        gone = [r["file"] for r in C.REGISTRY if not os.path.exists(os.path.join(C.ROOT, r["file"]))]
        assert not gone, gone

    def test_every_producer_and_carrier_is_found_by_the_scan(self):
        """If the scan cannot see a surface already listed, it could not see a new one either,
        and `test_every_file_that_draws_svg_is_registered` would be green over a blind scan.
        A helper builds path data a producer emits and writes no element of its own, so it is
        the one role the scan is not asked to find."""
        seen = set(C.emitters())
        blind = [r["file"] for r in C.REGISTRY
                 if r["role"] in ("producer", "carrier", "out-of-scope") and r["file"] not in seen]
        assert not blind, blind

    def test_every_out_of_scope_row_says_why(self):
        for r in C.REGISTRY:
            assert r["role"] in ("producer", "carrier", "helper", "out-of-scope"), r
            if r["role"] == "out-of-scope":
                assert len(r.get("reason") or "") > 20, r
            else:
                assert r.get("surface"), r

    def test_the_scan_sees_a_component_that_writes_no_svg_root(self, tmp_path):
        """The first scan matched `<svg` and nothing else, and was blind to a component that
        returns a `<path>` inside its parent's `<svg>` -- which is where a second spelling of a
        mark grows. Driven on a throwaway repository, with the two things that must NOT count:
        a docstring naming `<path>[]` and a route regex's `(?P<path>`."""
        subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
        (tmp_path / "Mark.jsx").write_text("export const Mark = () => <path d='M0 0 L1 1' />;\n")
        (tmp_path / "carrier.jsx").write_text("<div dangerouslySetInnerHTML={{__html: s}} />\n")
        (tmp_path / "prose.py").write_text('"""a list is reported as `<path>[]`"""\n'
                                           'R = r"^/mcp(?P<path>/.*)$"\n')
        assert C.emitters(str(tmp_path)) == ["Mark.jsx", "carrier.jsx"]


# ------------------------------------------------------------------ the known set is the live set
class TestTheKnownDisagreements:
    def test_the_live_disagreements_are_exactly_the_known_ones(self):
        known = json.load(open(C.KNOWN))["disagreements"]
        live = C.disagreements(_rows())
        new, fixed, moved_ids = C.compare(known, live)
        moved = ["%s: %r -> %r" % (k, known[k], live[k]) for k in moved_ids]
        assert not new and not fixed and not moved, (
            "the census moved. NEW disagreements (a drawing now departs from its record; fix it, "
            "or if it is a defect newly MEASURED rather than newly made, add it and say so in the "
            "commit): %s. FIXED (remove from tests/fixtures/ink_known_disagreements.json in the "
            "same commit as the fix): %s. MOVED (a disagreement whose figures changed -- re-pin it "
            "in a commit that says which way and why): %s" % (new, fixed, moved[:12]))

    def test_a_disagreement_whose_figures_changed_is_moved_and_not_passed(self):
        """DRIVEN (WP-14.6, auditor C). The id is the row and the detail is its figures; the pin
        holds both because a row already red for one cause cannot report a second unless its
        figures are held. A change to the DETAIL alone is the case a set comparison on ids would
        call unchanged, so it is driven by hand, beside one of each other kind."""
        known = {"V1:a": "3 marks off", "V1:b": "stays", "V2:c": "gone next run"}
        live = {"V1:a": "5 marks off", "V1:b": "stays", "V9:d": "arrived"}
        assert C.compare(known, live) == (["V9:d"], ["V2:c"], ["V1:a"])
        assert C.compare(known, dict(known)) == ([], [], [])

    def test_the_known_list_is_sorted_and_says_what_it_is(self):
        doc = json.load(open(C.KNOWN))
        assert list(doc["disagreements"]) == sorted(doc["disagreements"]), "keep the ids sorted"
        assert "held by identity" in doc["about"]


# ------------------------------------------------------------------ the doc is the census
class TestTheDocIsTheCensus:
    def test_the_tables_in_docs_fidelity_are_current(self):
        reg, table = C.render_doc_tables(_rows())
        text = open(C.DOC).read()
        assert C.splice(C.splice(text, "registry", reg), "checks", table) == text, (
            "docs/fidelity.md is stale: run `python3 tests/svg_census.py --write-doc`")


# ------------------------------------------------------------------ no check is vacuous
class TestNoCheckIsVacuous:
    def test_every_check_evaluated_something(self):
        s = C.summary(_rows())
        empty = [cid for cid, x in s.items() if not x["rows"]]
        assert not empty, "a check that evaluated nothing reads as a check that found nothing: %s" % empty

    def test_a_check_over_every_plate_reads_every_plate(self):
        n = len(C._profile_assets())
        assert n == 73, n
        for cid, c in C.CHECKS.items():
            if c["population"] == "every committed profile plate":
                assert C.summary(_rows())[cid]["rows"] == n, cid

    def test_every_committed_plate_states_its_frame_and_its_datum(self):
        for a, g, pl, rec in C._profile_assets():
            assert pl.plate is not None, a["id"]
            assert pl.plate["datum"] in ("axis", "naked"), a["id"]
            assert pl.outline is not None, (a["id"], pl.n_outlines)


# ------------------------------------------------------------------ the checks can say "disagrees"
def _planted(asset_id, change):
    """One committed plate, altered in memory by `change(svg) -> svg`, as the census reads it."""
    for a, g, pl, rec in C._profile_assets():
        if a["id"] == asset_id:
            svg = change(pl.svg)
            assert svg != pl.svg, "the planted defect did not land"
            return [(a, g, SURF.ProfilePlate(svg), rec)]
    raise KeyError(asset_id)


def _verdicts(monkeypatch, cid, plates):
    monkeypatch.setattr(C, "_PLATES", plates)
    return [r["verdict"] for r in C.CHECKS[cid]["fn"]()]


class TestTheChecksCanDisagree:
    """P1, P2, P5, P6, P9 and P12 have no live disagreement, so the corpus never reaches the
    branch that says one. Each is driven with the defect it exists for."""

    PLATE = "vignola-doric-capital-profile"

    def _scaled(self, factor):
        def change(svg):
            import re
            return re.sub(r'"px_per_in":([\d.]+)',
                          lambda m: '"px_per_in":%.6f' % (float(m.group(1)) * factor), svg, count=1)
        return change

    def test_the_unplanted_plates_agree_so_each_verdict_below_is_the_plant(self):
        """The control. Without it a 'disagrees' below could be the plate and not the plant."""
        live = {(r["check"], r["subject"]): r["verdict"] for r in _rows()}
        for cid in ("P2", "P5", "P6", "P12"):
            assert live[(cid, self.PLATE)] == "agrees", cid
        assert live[("P9", "palladio-tuscan-cornice-profile")] == "agrees"
        assert live[("P1", "palladio-ionic-base-profile")] == "agrees"
        assert live[("P2", "palladio-doric-capital-profile")] == "agrees"
        assert live[("P13", "vignola-ionic-capital-profile")] == "agrees"
        assert live[("P8", "vignola-corinthian-capital-profile")] == "agrees"
        assert live[("P11", "vignola-doric-capital-profile")] == "agrees"
        assert live[("P10", "palladio-corinthian-cornice-profile")] == "agrees"

    def test_p5_sees_a_plate_drawn_at_a_scale_it_does_not_state(self, monkeypatch):
        got = _verdicts(monkeypatch, "P5", _planted(self.PLATE, self._scaled(1.1)))
        assert got == ["disagrees"], got

    def test_p6_sees_a_face_drawn_off_its_record(self, monkeypatch):
        got = _verdicts(monkeypatch, "P6", _planted(self.PLATE, self._scaled(1.1)))
        assert got == ["disagrees"], got

    def test_p9_sees_an_inherited_plate_that_stops_saying_so(self, monkeypatch):
        inherited = "palladio-tuscan-cornice-profile"      # Palladio states no Tuscan cornice (OQ 7)
        got = _verdicts(monkeypatch, "P9", _planted(inherited, lambda s: s.replace("INHERITED", "OWN")))
        assert got == ["disagrees"], got

    def test_p12_sees_a_committed_plate_nobody_re_rendered(self, monkeypatch):
        got = _verdicts(monkeypatch, "P12", _planted(self.PLATE, lambda s: s.replace("</svg>", "<g/></svg>")))
        assert got == ["disagrees"], got

    def test_p1_sees_a_plate_that_prints_a_column_it_is_not_drawn_at(self, monkeypatch):
        """WP-14.2 fixed the twelve Palladio plates that said "at a 24 in column" over a 12 in
        drawing, so P1 has no live disagreement; this is that defect put back."""
        got = _verdicts(monkeypatch, "P1", _planted(
            "palladio-ionic-base-profile", lambda s: s.replace("at a 12\u2033 column", "at a 24\u2033 column")))
        assert got == ["disagrees"], got

    def test_p2_sees_the_layout_floor_printed_as_relief(self, monkeypatch):
        """The other WP-14.2 defect put back: a plate whose ink draws no relief, printing the
        layout's own 1.00 in floor as if the record stated it."""
        def change(s):
            return s.replace("no relief drawn: no</text>", "1.00\u2033 of relief from the naked.</text>")
        got = _verdicts(monkeypatch, "P2", _planted("palladio-doric-capital-profile", change))
        assert got == ["disagrees"], got

    def test_p2_reads_no_relief_as_a_claim_of_zero_that_ink_can_contradict(self, monkeypatch):
        """"no relief" is read as zero rather than as a plate that printed nothing, so a plate
        saying it over ink that DOES project is a disagreement and not COULD NOT EVALUATE."""
        def change(s):
            return s.replace("2.75\u2033 of relief from the naked.",
                             "no relief: every published face is flush with the naked.")
        got = _verdicts(monkeypatch, "P2", _planted(self.PLATE, change))
        assert got == ["disagrees"], got

    def test_p8_sees_a_curve_inked_for_a_member_it_calls_not_constructed(self, monkeypatch):
        """WP-14.2 draws an unconstructed member as its envelope, so P8 has no live disagreement;
        this puts the swelling's arc back into one acanthus row of the committed plate."""
        import re
        plate = "vignola-corinthian-capital-profile"
        a, g, pl, rec = next(x for x in C._profile_assets() if x[0]["id"] == plate)
        acanthus = next(m for m in rec["members"] if m["id"] == "acanthus_row_1")

        def change(svg):
            def one(m):
                u, v = pl.model((float(m.group(1)), float(m.group(2))))
                if abs(v - acanthus["y_top_in"]) < 0.01 and u > pl.naked() + 0.01:
                    return "A 9 9 0 0 1 %s,%s" % (m.group(1), m.group(2))
                return m.group(0)
            fill = re.search(r'<path d="([^"]+)" fill="#[0-9a-fA-F]+"', svg)
            new_d = re.sub(r"L ([\d.]+),([\d.]+)", one, fill.group(1), count=0)
            return svg.replace(fill.group(1), new_d, 1)
        got = _verdicts(monkeypatch, "P8", _planted(plate, change))
        assert got == ["disagrees"], got

    def test_p10_sees_a_weak_member_left_unmarked_in_words_or_in_ink(self, monkeypatch):
        """WP-14.2 marked all 65 plates, so P10 has no live disagreement; both halves are put back."""
        import re
        plate = "palladio-corinthian-cornice-profile"
        no_words = _planted(plate, lambda s: re.sub(r", (?:low|medium) confidence", "", s))
        assert _verdicts(monkeypatch, "P10", no_words) == ["disagrees"]
        no_ink = _planted(plate, lambda s: re.sub(r'<path class="confidence"[^>]*/>', "", s))
        assert _verdicts(monkeypatch, "P10", no_ink) == ["disagrees"]

    def test_p11_sees_a_curve_drawn_straight_and_not_said(self, monkeypatch):
        """WP-14.2 made the three Doric capitals say their cymatium is drawn straight, so P11 has
        no live disagreement; this is that silence put back."""
        got = _verdicts(monkeypatch, "P11", _planted(
            "vignola-doric-capital-profile",
            lambda s: s.replace("CURVED MEMBER(S) DRAWN STRAIGHT", "CURVED MEMBER(S)")))
        assert got == ["disagrees"], got

    def test_p13_sees_a_section_passed_off_as_the_capital(self, monkeypatch):
        """WP-14.2 made the Ionic capitals say their volute is not recorded, so P13 has no live
        disagreement; this is that silence put back."""
        got = _verdicts(monkeypatch, "P13", _planted(
            "vignola-ionic-capital-profile", lambda s: s.replace("NOT RECORDED: THE VOLUTE", "THE VOLUTE")))
        assert got == ["disagrees"], got

    def test_a_plate_with_no_frame_is_unjudged_and_not_a_crash(self, monkeypatch):
        import re
        stripped = _planted(self.PLATE, lambda s: re.sub(r" data-frame='[^']*'", "", s, count=1))
        for cid in ("P2", "P3", "P5", "P6"):
            assert _verdicts(monkeypatch, cid, stripped) == ["cne"], cid


class TestTheJavaScriptSurfaces:
    """Since WP-14.2 no O or R check has a live disagreement, so each is driven with the defect it
    exists for, and the unplanted control beside it must still agree; and every row that needs
    `node` must say COULD NOT EVALUATE without it, never agree."""

    @staticmethod
    def _orders_planted(monkeypatch, key, svg=None, info=None, reach=None):
        import copy
        run = C._orders_run()
        assert not isinstance(run, str), run
        planted = copy.deepcopy(run)
        if svg:
            planted["out"][key]["svg"] = svg(planted["out"][key]["svg"])
            assert planted["out"][key]["svg"] != run["out"][key]["svg"], "the plant did not land"
        if info:
            planted["out"][key]["info"] = info(planted["out"][key]["info"])
            assert planted["out"][key]["info"] != run["out"][key]["info"], "the plant did not land"
        if reach:
            planted["out"]["__reachable"] = reach(planted["out"]["__reachable"])
        monkeypatch.setattr(C, "_ORDERS", planted)

    @staticmethod
    def _got(cid):
        return {r["subject"]: r["verdict"] for r in C.CHECKS[cid]["fn"]()}

    def test_the_orders_page_carries_no_engine_of_its_own(self):
        """WP-14.2 deleted the page's port of stack_for, _synth_shaft and dimension(), its taper and
        its flute arithmetic. O2 and O3 cannot see a port come back while it agrees with Python --
        which the old one did, 156 of 156 -- so the absence is held here, by name."""
        import re
        tpl = open(os.path.join(C.ROOT, "build", "orders_template.html"), encoding="utf-8").read()
        # ANY WAY OF DEFINING ONE (WP-14.6, G10): the pattern read `function name(` alone, so
        # `const dimension = (pk, d) =>` -- the page's own idiom elsewhere -- would have come back
        # through it. Driven below on each form, so the pattern cannot narrow unseen.
        defines = lambda name: re.compile(  # noqa: E731
            r"(?:\bfunction\s+%(n)s\s*\(|\b(?:const|let|var)\s+%(n)s\s*=|\b%(n)s\s*:\s*(?:function\b|\()"
            r"|^\s*%(n)s\s*\([^)]*\)\s*\{)" % {"n": re.escape(name)}, re.M)
        for form in ("function dimension(pk, d) {", "const dimension = (pk, d) => {",
                     "let dimension = function (pk) {", "var dimension=pk=>pk", "  dimension: (pk) => pk,",
                     "  dimension(pk, d) {"):
            assert defines("dimension").search(form), form
        assert not defines("dimension").search("const g = dimension(pk, d);")
        for name in ("dimension", "synthShaft", "stackFor", "colRadiusFromGeometry", "geomMaxX"):
            assert not defines(name).search(tpl), name
        assert "height_parts" not in re.sub(r"s\.height_parts", "", tpl), \
            "the page multiplies a member's parts again"
        assert "fl/2.4" not in tpl.replace(" ", "")

    def test_o4_sees_an_unjudged_invariant_printed_fail(self, monkeypatch):
        import re
        key = "vignola-ionic@12-unjudged-invariant"
        self._orders_planted(monkeypatch, key, info=lambda s: re.sub(
            r'(<div class="inv"><span class="m )un">N/EV', r'\1no">FAIL', s, count=1))
        assert [r["verdict"] for r in C.CHECKS["O4"]["fn"]()] == ["disagrees"]

    def test_o4_sees_an_unjudged_invariant_printed_as_holding(self, monkeypatch):
        """WP-14.6, G1: the other direction, and the more dangerous one. O4 agreed with anything
        but FAIL, so an unjudged invariant printed "holds" -- a pass nobody measured -- agreed."""
        import re
        key = "vignola-ionic@12-unjudged-invariant"
        self._orders_planted(monkeypatch, key, info=lambda s: re.sub(
            r'(<div class="inv"><span class="m )un">N/EV', r'\1ok">holds', s, count=1))
        got = C.CHECKS["O4"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"] and "'holds'" in got[0]["detail"], got

    def test_o5_sees_a_pack_no_button_reaches(self, monkeypatch):
        self._orders_planted(monkeypatch, "vignola-ionic@12",
                             reach=lambda r: [p for p in r if p != "greek-doric"])
        got = self._got("O5")
        assert got["greek-doric"] == "disagrees" and got["moorish-arch"] == "agrees"

    def test_o6_sees_a_flute_line_dropped(self, monkeypatch):
        import re
        self._orders_planted(monkeypatch, "vignola-ionic@12", svg=lambda s: re.sub(
            r'<g transform="[^"]*"><path class="flute"[^>]*/></g>', "", s, count=1))
        got = self._got("O6")
        assert got["vignola-ionic"] == "disagrees" and got["vignola-corinthian"] == "agrees"

    def test_o7_sees_an_unpublished_member_unbracketed_or_uncounted(self, monkeypatch):
        import re
        self._orders_planted(monkeypatch, "palladio-ionic@12", svg=lambda s: re.sub(
            r'<g transform="[^"]*"><path class="unpub"[^>]*/></g>', "", s, count=1))
        got = self._got("O7")
        assert got["palladio-ionic"] == "disagrees" and got["gibbs-doric"] == "agrees"
        self._orders_planted(monkeypatch, "palladio-ionic@12",
                             info=lambda s: s.replace("14 member(s) drawn as a dashed bracket",
                                                      "13 member(s) drawn as a dashed bracket"))
        assert self._got("O7")["palladio-ionic"] == "disagrees"

    def test_o7_sees_a_complete_stack_that_stops_saying_so(self, monkeypatch):
        import re
        self._orders_planted(monkeypatch, "vignola-ionic@12", info=lambda s: re.sub(
            r"All \d+ member\(s\) publish a projection\.", "", s))
        got = self._got("O7")
        assert got["vignola-ionic"] == "disagrees" and got["vignola-corinthian"] == "agrees"

    def test_o8_sees_an_unconstructed_member_drawn_without_its_envelope(self, monkeypatch):
        import re
        run = C._orders_run()
        pid = next(c["pid"] for c in run["cases"] if c["key"] == c["pid"] + "@12"
                   and 'class="envelope"' in run["out"][c["key"]]["svg"])
        self._orders_planted(monkeypatch, pid + "@12", svg=lambda s: re.sub(
            r'<g transform="[^"]*"><path class="envelope"[^>]*/></g>', "", s, count=1))
        assert self._got("O8")[pid] == "disagrees"

    def test_o9_sees_a_straight_curve_left_unsaid(self, monkeypatch):
        self._orders_planted(monkeypatch, "vignola-ionic@12", info=lambda s: s.replace(
            "CURVED MEMBER(S) DRAWN STRAIGHT", "CURVED MEMBER(S)"))
        assert self._got("O9")["vignola-ionic"] == "disagrees"

    def test_o10_sees_an_assembly_named_under_the_wrong_datum(self, monkeypatch):
        self._orders_planted(monkeypatch, "vignola-ionic@12", info=lambda s: s.replace(
            "from the axis for the pedestal, base, shaft and capital",
            "from the axis for the pedestal, base and shaft").replace(
            "own naked for the architrave", "own naked for the capital, architrave"))
        got = self._got("O10")
        assert got["vignola-ionic"] == "disagrees" and got["vignola-corinthian"] == "agrees"

    @staticmethod
    def _plate_planted(monkeypatch, pid, **change):
        import copy
        run = C._plate_run()
        assert not isinstance(run, str), run
        planted = copy.deepcopy(run)
        for k, fn in change.items():
            planted["plate"][pid][k] = fn(planted["plate"][pid][k])
            assert planted["plate"][pid][k] != run["plate"][pid][k], "the plant did not land"
        monkeypatch.setattr(C, "_PLATEJS", planted)

    def test_r1_sees_a_frame_narrower_than_its_ink(self, monkeypatch):
        self._plate_planted(monkeypatch, "vignola-ionic", maxX=lambda x: x * 0.8)
        got = self._got("R1")
        assert got["vignola-ionic"] == "disagrees" and got["gibbs-doric"] == "agrees"

    def test_r2_sees_an_unpublished_member_left_unsaid_and_a_published_one_called_absent(self, monkeypatch):
        self._plate_planted(monkeypatch, "palladio-ionic", unrecorded=lambda u: u[1:])
        assert self._got("R2")["palladio-ionic"] == "disagrees"
        self._plate_planted(monkeypatch, "gibbs-doric", unrecorded=lambda u: u + ["frieze.metope"])
        got = self._got("R2")
        assert got["gibbs-doric"] == "disagrees" and got["vignola-ionic"] == "agrees"

    def test_r2_does_not_count_the_column_its_own_body(self):
        """palladio-doric and -tuscan leave the shaft body's projection null; the body IS the
        column, so neither the plate nor R2 counts it -- and R2 finds it from the record's own
        heights, not from the geometry's rule."""
        got = self._got("R2")
        assert got["palladio-doric"] == "agrees" and got["palladio-tuscan"] == "agrees"

    def test_o11_sees_an_alternative_left_out_and_unsaid(self, monkeypatch):
        self._orders_planted(monkeypatch, "benjamin-tuscan@12", info=lambda s: s.replace(
            "is not drawn: it is offered instead of the", "is not drawn instead of the"))
        got = self._got("O11")
        assert got["benjamin-tuscan"] == "disagrees" and got["benjamin-ionic"] == "agrees"

    def test_o11_sees_an_entablature_drawn_whole_and_unsaid(self, monkeypatch):
        self._orders_planted(monkeypatch, "palladio-corinthian@12", info=lambda s: s.replace(
            "The entablature is drawn whole, as", "The entablature, as"))
        assert self._got("O11")["palladio-corinthian"] == "disagrees"

    def test_r4_sees_the_plate_stop_saying_what_the_stack_left_out(self, monkeypatch):
        self._plate_planted(monkeypatch, "benjamin-corinthian", stackWords=lambda w: "")
        got = self._got("R4")
        assert got["benjamin-corinthian"] == "disagrees" and got["benjamin-ionic"] == "agrees"

    def test_r3_sees_an_assembly_named_under_the_wrong_datum(self, monkeypatch):
        self._plate_planted(monkeypatch, "vignola-ionic", datumWords=lambda w: w.replace(
            "and from each member’s own naked for the architrave",
            "and from each member’s own naked for the capital, architrave"))
        got = self._got("R3")
        assert got["vignola-ionic"] == "disagrees" and got["gibbs-doric"] == "agrees"

    def test_o1_sees_a_page_committed_without_a_build(self, monkeypatch, tmp_path):
        stale = tmp_path / "orders.html"
        stale.write_text(open(C.ORDERS_PAGE, encoding="utf-8").read() + "<!-- -->", encoding="utf-8")
        monkeypatch.setattr(C, "ORDERS_PAGE", str(stale))
        assert [r["verdict"] for r in C.CHECKS["O1"]["fn"]()] == ["disagrees"]

    def test_o2_and_o3_see_a_section_drawn_at_a_scale_it_does_not_state(self, monkeypatch):
        import copy
        import re
        run = C._orders_run()
        assert not isinstance(run, str), run
        planted = copy.deepcopy(run)
        key = "vignola-ionic@12"
        planted["out"][key]["svg"] = re.sub(
            r'"px_per_in":([\d.]+)', lambda m: '"px_per_in":%r' % (float(m.group(1)) * 1.1),
            planted["out"][key]["svg"], count=1)
        assert planted["out"][key]["svg"] != run["out"][key]["svg"], "the plant did not land"
        monkeypatch.setattr(C, "_ORDERS", planted)
        for cid in ("O2", "O3"):
            got = {r["subject"]: r["verdict"] for r in C.CHECKS[cid]["fn"]()}
            assert got[key] == "disagrees", cid
            assert got["vignola-ionic@24"] == "agrees", cid          # the control, unplanted

    # Every check that runs javascript, spelled out so a reader sees them. The list is HELD to the
    # call graph below: it once named fourteen of these and left out the bench's two (B1, B2) and the
    # tracing canvas (TR1), which WP-14.4 added -- three checks whose unjudged state no test read.
    NODE_CHECKS = ("O2", "O3", "O4", "O5", "O6", "O7", "O8", "O9", "O10", "O11",
                   "R1", "R2", "R3", "R4", "B1", "B2", "TR1")

    def test_the_javascript_list_is_every_check_that_reaches_node(self):
        """A check is javascript-backed if its function -- or anything it calls in the census,
        transitively -- runs `node`. Derived, so a new check cannot be born outside the list."""
        import inspect
        funcs = {n: f for n, f in vars(C).items() if inspect.isfunction(f) and f.__module__ == C.__name__}
        src = {n: inspect.getsource(f) for n, f in funcs.items()}
        backed = {n for n, s in src.items() if 'subprocess.run(["node"' in s}
        assert backed, "no function in the census runs node -- the derivation is reading nothing"
        while True:
            more = {n for n, s in src.items() if n not in backed
                    and any(re.search(r"\b%s\(" % re.escape(h), s) for h in backed)}
            if not more:
                break
            backed |= more
        derived = {cid for cid, c in C.CHECKS.items() if c["fn"].__name__ in backed}
        assert derived == set(self.NODE_CHECKS), (sorted(derived - set(self.NODE_CHECKS)),
                                                  sorted(set(self.NODE_CHECKS) - derived))

    def test_without_node_every_javascript_row_is_unjudged(self, monkeypatch):
        monkeypatch.setattr(C.shutil, "which", lambda name: None)
        monkeypatch.setattr(C, "_ORDERS", None)
        monkeypatch.setattr(C, "_PLATEJS", None)
        monkeypatch.setattr(C, "_BENCH", None)
        for cid in self.NODE_CHECKS:
            got = C.CHECKS[cid]["fn"]()
            assert got and all(r["verdict"] == "cne" for r in got), (cid, got)
            assert "node" in got[0]["detail"], got[0]

    def test_the_plate_fixtures_are_what_the_server_serves(self):
        r = subprocess.run([sys.executable, os.path.join(C.ROOT, "tests", "fixtures", "proportions_plate",
                                                         "generate.py"), "--check"],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr


class TestTheOrderStackCanDisagree:
    """E1-E4 agree on every pack since WP-14.2 step 7, so each is driven with the defect it
    exists for, on the geometry its own reader reads."""

    def test_e4_sees_a_die_drawn_at_a_stand_in(self, monkeypatch):
        """The 1.2 x R stand-in the old E4 assumed and could not see removed, planted back."""
        PROF = C.SURF._mod("profiles")
        real = PROF.pack_geometry

        def planted(dim, column=None, projection_datum=None, **kw):
            g = real(dim, column, projection_datum, **kw)
            if dim.get("pack") == "palladio-ionic":
                for a in g["assemblies"]:
                    if a["id"] == "pedestal":
                        a["naked_in"] = g["lower_radius_in"] * 1.2
            return g
        monkeypatch.setattr(PROF, "pack_geometry", planted)
        got = {r["subject"]: r["verdict"] for r in C.CHECKS["E4"]["fn"]()}
        assert got["palladio-ionic"] == "disagrees" and got["vignola-ionic"] == "agrees"

    def test_e4_sees_a_derived_die_that_does_not_carry_the_plinth(self, monkeypatch):
        PROF = C.SURF._mod("profiles")
        real = PROF.pack_geometry

        def planted(dim, column=None, projection_datum=None, **kw):
            g = real(dim, column, projection_datum, **kw)
            if dim.get("pack") == "benjamin-corinthian":
                for a in g["assemblies"]:
                    if a["id"] == "pedestal":
                        a["naked_in"] -= 1.0
            return g
        monkeypatch.setattr(PROF, "pack_geometry", planted)
        assert {r["subject"]: r["verdict"] for r in C.CHECKS["E4"]["fn"]()}["benjamin-corinthian"] == "disagrees"


class TestTheBuildingSheetsCanDisagree:
    """V7, V9 and V13 agree on every sheet the corpus draws today, so the corpus never reaches the
    branch that says otherwise. Each is driven with the defect it exists for."""

    def _one(self, pid, face=None):
        rec = C._sheets()[pid]
        face = face or rec["elev"]["entrance_face"]
        return rec, face, rec["faces"][face]

    def test_v7_sees_a_head_that_is_not_a_circle(self, monkeypatch):
        import re
        rec, face, svg = self._one("tidewater-georgian-careful")
        # the heads are circular arcs since WP-14.3; plant a parabola 60 px tall in place of one,
        # which is far from any circle
        planted = re.sub(
            r'(<path class="arch w-med" d="M ([\d.]+),([\d.]+)) A [\d.]+,[\d.]+ 0 0 1 ([\d.]+),([\d.]+)',
            lambda m: "%s Q %.2f,%.2f %s,%s" % (m.group(1), (float(m.group(2)) + float(m.group(4))) / 2.0,
                                                float(m.group(3)) - 60.0, m.group(4), m.group(5)),
            svg, count=1)
        assert planted != svg, "the plant did not land"
        monkeypatch.setattr(C, "_elev_and_sweep", lambda: iter([("planted", rec["elev"], planted)]))
        assert [r["verdict"] for r in C.CHECKS["V7"]["fn"]()] == ["disagrees"]

    def test_v6_counts_the_panels_in_the_leaf_and_not_the_shutters_over_it(self, monkeypatch):
        """Corrected at WP-14.3: V6 counted every panel within the garage door's WIDTH, so the
        shutters of the window over bad-03's garage door were read as the door's own panels (10
        against 6). A panel planted over the door is not counted; the same panel planted in the
        leaf is, so the bound is neither missing nor blind."""
        pid = "bad-03-narrow-lot-townhome"
        rec = C._sheets()[pid]
        EL = C.SURF._mod("elevation")
        door = [x for x in EL.opening_rects(rec["elev"], "S")["rects"] if x["kind"] == "door"][0]
        types = {r["id"]: d.get("type") for lv in rec["placed"]["levels"] for r in lv["rooms"]
                 for d in r.get("doors") or [] if d.get("to") == "exterior"}
        assert types.get(door["room"]) == "garage", "the premise: the door on S is the garage's"
        pl = C._face_plate(C.IR.Ink(rec["faces"]["S"]))
        x0 = C.IR.from_model(pl, door["x0_in"] / 12.0, 0)[0]
        head = C.IR.from_model(pl, 0, door["head_in"] / 12.0)[1]

        def count(y):
            svg = rec["faces"]["S"].replace(
                "</svg>", '<rect class="pnl w-fine" x="%.1f" y="%.1f" width="20.0" height="30.0"/>'
                "</svg>" % (x0 + 10.0, y))
            monkeypatch.setitem(rec, "faces", dict(rec["faces"], S=svg))
            row = {r["subject"]: r for r in C.CHECKS["V6"]["fn"]()}[pid + "/S"]
            return int(row["detail"].split()[0]) if row["detail"] else 0

        monkeypatch.setitem(rec, "faces", dict(rec["faces"]))
        before = {r["subject"]: r for r in C.CHECKS["V6"]["fn"]()}[pid + "/S"]
        n = int(before["detail"].split()[0]) if before["detail"] else 0
        assert count(head - 80.0) == n, "a panel over the door was counted as the door's"
        assert count(head + 10.0) == n + 1, "a panel in the leaf was not counted"

    def test_v16_sees_a_surround_neither_drawn_nor_said(self, monkeypatch):
        """No surface draws a window surround, so V16 agrees only on the sheet's words. Take the
        words away from one style and V16 convicts that style and no other."""
        sweep = C._style_sweep()
        sid = "tidewater-georgian"
        el, svg = sweep[sid]
        planted = svg.replace("WINDOW SURROUND NOT DRAWN", "WINDOW NOTE")
        assert planted != svg, "the premise: this sheet says its surround is not drawn"
        monkeypatch.setitem(sweep, sid, (el, planted))
        got = {r["subject"]: r["verdict"] for r in C.CHECKS["V16"]["fn"]()}
        assert got[sid] == "disagrees" and got["colonial-revival"] == "agrees", got

    def test_v9_sees_the_renderers_own_fallbacks_when_the_record_gives_no_figure(self, monkeypatch):
        import copy
        RE = C.SURF._mod("render_elevation")
        rec, face, _svg = self._one("tidewater-georgian-careful", "E")
        el = copy.deepcopy(rec["elev"])
        assert el.get("chimney_stack_plan_in"), "the premise: this record states a stack size"
        el["chimney_stack_plan_in"] = None                   # the renderer falls back to 22 in
        planted = C._render(RE.render_elevation, el, face="E")
        # WP-14.3 refuses the stack and says so: the honest sheet agrees
        monkeypatch.setattr(C, "_elev_and_sweep", lambda: iter([("planted", el, planted)]))
        got = C.CHECKS["V9"]["fn"]()
        assert [r["verdict"] for r in got] == ["agrees"], got
        # the refusal left unsaid, and the old fallback put back: both disagree
        silent = planted.replace("STACKS NOT DRAWN", "STACKS")
        assert silent != planted, "the premise: the sheet says the stacks are not drawn"
        monkeypatch.setattr(C, "_elev_and_sweep", lambda: iter([("planted", el, silent)]))
        got = C.CHECKS["V9"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"] and "neither drawn nor said" in got[0]["detail"], got
        drawn = C._render(RE.render_elevation, copy.deepcopy(rec["elev"]), face="E")
        assert '"ch' in drawn or "class='ch" in drawn or 'class="ch' in drawn, "the premise: a sized stack is drawn"
        monkeypatch.setattr(C, "_elev_and_sweep", lambda: iter([("planted", el, drawn)]))
        got = C.CHECKS["V9"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"] and "no record states" in got[0]["detail"], got

    def test_v9_sees_a_keystone_drawn_or_left_unsaid(self, monkeypatch):
        """WP-14.6, G4. The test above drives V9's stack half only; its keystone half was reached
        by the sweep and driven by nothing. `georgian-revival`'s canonical head is keyed and no
        record gives the keystone a width, so its sheet says KEYSTONE NOT DRAWN. Take the words
        away and V9 convicts; draw a keystone and it convicts on the other clause."""
        sweep = C._style_sweep()
        sid = "georgian-revival"
        el, svg = sweep[sid]
        heads = [sw.get("head_treatment") or {} for sw in el.get("storey_windows") or []]
        assert any(h.get("keystone") and not h.get("keystone_width_in") for h in heads), \
            "the premise: a keyed head with no stated keystone width"
        monkeypatch.setattr(C, "_elev_and_sweep", lambda: iter([("planted", el, svg)]))
        assert [r["verdict"] for r in C.CHECKS["V9"]["fn"]()] == ["agrees"]
        silent = svg.replace("KEYSTONE NOT DRAWN", "KEYSTONE")
        assert silent != svg, "the premise: the sheet says the keystone is not drawn"
        monkeypatch.setattr(C, "_elev_and_sweep", lambda: iter([("planted", el, silent)]))
        got = C.CHECKS["V9"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"] and "keystone with no width" in got[0]["detail"], got
        drawn = svg.replace("</svg>", '<rect class="arch" x="100" y="100" width="6" height="9"/></svg>')
        monkeypatch.setattr(C, "_elev_and_sweep", lambda: iter([("planted", el, drawn)]))
        got = C.CHECKS["V9"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"] and "keystone drawn at a width" in got[0]["detail"], got

    def test_v13_sees_an_inset_drawn_at_a_scale_it_does_not_state(self, monkeypatch):
        import copy
        import re
        rec, face, svg = self._one("tidewater-georgian-careful")
        planted = re.sub(r'("id":"inset","proj":"profile","unit":"in","px_per_in":)([\d.]+)',
                         lambda m: m.group(1) + repr(float(m.group(2)) * 1.1), svg, count=1)
        assert planted != svg, "the plant did not land"
        sheets = copy.copy(C._sheets())
        one = dict(sheets["tidewater-georgian-careful"])
        one["faces"] = {face: planted}
        monkeypatch.setattr(C, "_SHEETS", {"tidewater-georgian-careful": one})
        assert [r["verdict"] for r in C.CHECKS["V13"]["fn"]()] == ["disagrees"]


class TestThePlanSheetsCanDisagree:
    """PL2 and PL3 agree on every sheet once WP-14.4 draws each join once and cuts each opening in
    its own element's wall, so each is driven by putting its defect back into the RENDERER, which is
    stronger than planting ink: the plant is the defect itself, not a picture of it."""

    PID = "tidewater-georgian-careful"

    def _replanted(self, monkeypatch, name, fn):
        """Re-render the one multi-element sheet with one renderer function replaced, and hand the
        census a sheet table holding only it. The CLEAN table is built first, before anything is
        replaced: `_sheets()` caches what it builds, so a test run on its own would otherwise fill
        the cache for the whole session with sheets drawn by the planted renderer."""
        import copy
        RP = C.SURF._mod("render_plan")
        rec = dict(C._sheets()[self.PID])
        monkeypatch.setattr(RP, name, fn)
        rec["plan_svg_working"] = C._render(RP.render, copy.deepcopy(rec["placed"]), register="working")
        monkeypatch.setattr(C, "_SHEETS", {self.PID: rec})
        return rec

    def test_the_premise_both_agree_on_the_one_sheet_with_a_join(self):
        got = {cid: {r["subject"]: r["verdict"] for r in C.CHECKS[cid]["fn"]()}[self.PID] for cid in ("PL2", "PL3")}
        assert got == {"PL2": "agrees", "PL3": "agrees"}, got

    def test_pl2_sees_an_opening_cut_at_the_footprints_face(self, monkeypatch):
        RP = C.SURF._mod("render_plan")

        def old_gaps(op, W, H):
            # the defect WP-14.4 removed: every exterior hole at the FOOTPRINT's face
            gaps = []
            for d in op["interior"]:
                half = d["width_ft"] / 2.0
                gaps.append(("y" if d["horiz"] else "x", d["at_ft"], d["pos_ft"] - half, d["pos_ft"] + half))
            for d in op["exterior"] + op["windows"]:
                axis, pos = RP._wall_axis(d["wall"], W, H)
                half = d["width_ft"] / 2.0
                gaps.append((axis, pos, d["at_ft"] - half, d["at_ft"] + half))
            return gaps
        self._replanted(monkeypatch, "opening_gaps", old_gaps)
        got = C.CHECKS["PL2"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"], got
        assert "drawn through a solid wall" in got[0]["detail"] and "kitchen S" in got[0]["detail"], got

    def test_pl2_sees_a_break_where_the_record_places_no_opening(self, monkeypatch):
        RP = C.SURF._mod("render_plan")
        real = RP.opening_gaps

        def with_a_hole(op, W, H):
            # a 3 ft hole in the main block's south wall at 22 ft, where the record places nothing
            return real(op, W, H) + [("y", 0.0, 21.0, 24.0)]
        self._replanted(monkeypatch, "opening_gaps", with_a_hole)
        got = C.CHECKS["PL2"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"], got
        assert "breaks cut where no opening is placed" in got[0]["detail"], got
        assert "3.0 ft break" in got[0]["detail"], got

    def test_pl3_sees_a_join_drawn_by_both_elements(self, monkeypatch):
        RP = C.SURF._mod("render_plan")
        self._replanted(monkeypatch, "element_joins", lambda blocks, tol=RP.JOIN_TOL_FT: [])
        got = C.CHECKS["PL3"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"], got
        assert "drawn over one another" in got[0]["detail"], got


class TestTheBenchCanDisagree:
    """B1 and B2 agree on every plan once WP-14.4 lands, so each is driven with its defect planted
    in what the bench computes -- the read-back, as the Proportions plate's rows are driven."""

    PID = "tidewater-georgian-careful"

    def test_b1_sees_a_window_on_the_footprints_face(self, monkeypatch):
        import copy
        run = C._bench_run()
        if isinstance(run, str):
            pytest.skip("COULD NOT EVALUATE: " + run)
        planted = copy.deepcopy(run)
        wins = planted["marks"][self.PID + "@0"]["windows"]
        w = next(w for w in wins if w["wall"] == "S" and w["edge_ft"] != 0)
        t = planted["marks"][self.PID + "@0"]["t"]
        w["across"] = [-t, 0.0]            # the defect: an S window drawn on the footprint's face
        monkeypatch.setattr(C, "_BENCH", planted)
        got = {r["subject"]: r for r in C.CHECKS["B1"]["fn"]()}
        assert got[self.PID]["verdict"] == "disagrees" and "drawn across" in got[self.PID]["detail"]
        assert got["spec-builder-colonial"]["verdict"] == "agrees"

    def test_b1_sees_a_window_at_a_fixed_depth(self, monkeypatch):
        import copy
        run = C._bench_run()
        if isinstance(run, str):
            pytest.skip("COULD NOT EVALUATE: " + run)
        planted = copy.deepcopy(run)
        for w in planted["marks"]["spec-builder-colonial@0"]["windows"]:
            lo, hi = w["across"]
            w["across"] = [hi - 0.75, hi] if w["wall"] in "SW" else [lo, lo + 0.75]
        monkeypatch.setattr(C, "_BENCH", planted)
        got = {r["subject"]: r["verdict"] for r in C.CHECKS["B1"]["fn"]()}
        assert got["spec-builder-colonial"] == "disagrees"

    def test_b2_sees_a_placement_served_without_its_walls(self, monkeypatch):
        import copy
        run = C._bench_run()
        if isinstance(run, str):
            pytest.skip("COULD NOT EVALUATE: " + run)
        planted = copy.deepcopy(run)
        planted["served"][self.PID].pop("walls")
        monkeypatch.setattr(C, "_BENCH", planted)
        got = {r["subject"]: r["verdict"] for r in C.CHECKS["B2"]["fn"]()}
        assert got[self.PID] == "disagrees" and got["spec-builder-colonial"] == "agrees"

    def test_tr1_sees_a_traced_room_drawn_unflipped(self, monkeypatch):
        import json as _json
        import subprocess as _sp
        real = _sp.run

        def doctored(cmd, *a, **kw):
            r = real(cmd, *a, **kw)
            if any(str(c).endswith("trace_canvas.mjs") for c in cmd) and r.returncode == 0:
                got = _json.loads(r.stdout)
                room = got[self.PID]["rooms"][0]["rect"]
                room["y"] = -room["y"] - room["height"]          # the defect: y not flipped
                r = _sp.CompletedProcess(r.args, 0, _json.dumps(got), r.stderr)
            return r
        if not C.shutil.which("node"):
            pytest.skip("COULD NOT EVALUATE: node is not installed")
        monkeypatch.setattr(C.subprocess, "run", doctored)
        got = {r["subject"]: r["verdict"] for r in C.CHECKS["TR1"]["fn"]()}
        assert got[self.PID] == "disagrees" and got["spec-builder-colonial"] == "agrees", got


class TestTheRecordCanDisagree:
    """N0 to N3, P14 and P15 read the record against its own notes and a plate's record against
    what it says of itself (WP-14.5). Each is driven here THROUGH THE CENSUS, with its defect
    planted in the table or the asset record the census reads: `test_plate_review.py` drives the
    reviewer, and this is the join -- a census that stopped calling it would be green over any
    table at all."""

    PLATE = "vignola-doric-base-profile"
    NOTE = ("vignola-doric", "base", "base_torus")

    @pytest.fixture
    def table(self, monkeypatch):
        import copy
        PR = C._review()
        PR.reset()
        t = copy.deepcopy(PR.table())
        monkeypatch.setattr(PR, "_TABLE", t)
        PR._MEMO.clear()
        yield t
        PR.reset()

    def _row(self, cid, subject):
        rows = [r for r in C.CHECKS[cid]["fn"]() if r["subject"] == subject]
        assert len(rows) == 1, (cid, subject, rows)
        return rows[0]

    def _entry(self, t, key):
        return next(e for e in t["members"] if (e["pack"], e["assembly"], e["member"]) == key)

    def test_the_premise_the_driven_rows_agree_unplanted(self):
        subj = "/".join(self.NOTE)
        assert self._row("N0", subj)["verdict"] == "agrees"
        assert self._row("N1", subj)["verdict"] == "agrees"
        assert self._row("N2", "chambers-ionic")["verdict"] == "agrees"
        assert self._row("N3", "craftsman/casing/leg_in")["verdict"] == "agrees"

    def test_n0_sees_a_note_nobody_read(self, table):
        table["members"].remove(self._entry(table, self.NOTE))
        got = self._row("N0", "/".join(self.NOTE))
        assert got["verdict"] == "disagrees" and "has not been read" in got["detail"], got

    def test_n0_sees_a_quote_that_has_left_its_note(self, table):
        self._entry(table, self.NOTE)["claims"][0]["quote"] = "words the note never said"
        got = self._row("N0", "/".join(self.NOTE))
        assert got["verdict"] == "disagrees", got

    def test_n1_sees_a_note_that_states_another_figure(self, table):
        c = self._entry(table, self.NOTE)["claims"][0]
        c["states"] = "(%s) * 2" % c["states"]
        got = self._row("N1", "/".join(self.NOTE))
        assert got["verdict"] == "disagrees" and "the record" in got["detail"], got

    def test_n2_sees_a_conversion_stated_wrongly(self, table):
        table["modules"]["chambers-ionic"]["part_factor"] = "2"
        assert self._row("N2", "chambers-ionic")["verdict"] == "disagrees"

    def test_n3_sees_a_kit_note_that_states_another_figure(self, table):
        e = next(k for k in table["kits"] if (k["kit"], k["slot"], k["parameter"]) == ("craftsman", "casing", "leg_in"))
        e["claims"][0]["states"] = "(%s) + 1" % e["claims"][0]["states"]
        assert self._row("N3", "craftsman/casing/leg_in")["verdict"] == "disagrees"

    def _one_plate(self, monkeypatch, change):
        import copy
        a, g, pl, rec = next(x for x in C._profile_assets() if x[0]["id"] == self.PLATE)
        a = copy.deepcopy(a)
        change(a)
        monkeypatch.setattr(C, "_PLATES", [(a, g, pl, rec)])

    def test_p14_and_p15_agree_unplanted(self, monkeypatch):
        self._one_plate(monkeypatch, lambda a: None)
        assert [r["verdict"] for r in C.CHECKS["P14"]["fn"]()] == ["agrees"]
        assert [r["verdict"] for r in C.CHECKS["P15"]["fn"]()] == ["agrees"]

    def test_p14_sees_a_review_note_nobody_rewrote(self, monkeypatch):
        self._one_plate(monkeypatch, lambda a: a.update(
            review_note=a["review_note"].replace("INTERNAL: DISAGREES", "INTERNAL: AGREES")))
        got = C.CHECKS["P14"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"] and "stale" in got[0]["detail"], got

    def test_p14_sees_a_note_that_approves_what_nobody_approved(self, monkeypatch):
        """The second branch, which a current note reaches only when the ONE spelling itself stops
        saying the source was not evaluated: both halves are planted, so the note is current."""
        RP = C.SURF._mod("render_profile")
        monkeypatch.setattr(RP, "review_note", lambda asset, rep: "Approved.")
        self._one_plate(monkeypatch, lambda a: a.update(review_note="Approved."))
        got = C.CHECKS["P14"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"] and "approved" in got[0]["detail"], got

    def test_p15_sees_an_alt_text_that_lists_another_stack(self, monkeypatch):
        self._one_plate(monkeypatch, lambda a: a.update(alt_text=a["alt_text"].replace("(5p)", "(6p)", 1)))
        got = C.CHECKS["P15"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"], got

    def test_p15_says_it_cannot_read_an_alt_text_in_another_form(self, monkeypatch):
        self._one_plate(monkeypatch, lambda a: a.update(alt_text="A drawing of a base."))
        assert [r["verdict"] for r in C.CHECKS["P15"]["fn"]()] == ["cne"]


class TestTheSectionCanDisagree:
    """S1 and S2 agree on every section once WP-14.6 draws each floor structure above its storey's
    ceiling, so each is driven with its defect planted in a real section's ink."""

    PID = "tidewater-georgian-careful"

    def _planted(self, monkeypatch, change):
        import re
        rec = dict(C._sheets()[self.PID])
        rec["sec_svg"] = change(rec["sec_svg"], rec, re)
        assert rec["sec_svg"] != C._sheets()[self.PID]["sec_svg"], "the planted defect did not land"
        monkeypatch.setattr(C, "_SHEETS", {self.PID: rec})

    def test_the_premise_both_agree_unplanted(self):
        got = {cid: {r["subject"]: r["verdict"] for r in C.CHECKS[cid]["fn"]()}[self.PID] for cid in ("S1", "S2")}
        assert got == {"S1": "agrees", "S2": "agrees"}, got

    def test_s2_sees_a_floor_structure_hung_under_its_own_floor(self, monkeypatch):
        """The defect WP-14.6 removed: each body under its storey's floor line, one storey out."""
        import inkread as IR

        def change(svg, rec, re):
            pl = next(p for p in IR.Ink(svg).frames() if p.get("proj") == "section")
            k, oy, av = pl.get("px_per_ft"), pl["origin_px"][1], pl["at_origin_ft"][1]
            floors = {str(st["index"]): st["grade_to_floor_ft"] for st in rec["section"]["storeys"]}
            return re.sub(r'(<rect class="fs" data-storey="(\w+)" x="[^"]*" y=")([^"]*)"',
                          lambda m: '%s%.2f"' % (m.group(1), oy + (av - floors[m.group(2)]) * k), svg)
        self._planted(monkeypatch, change)
        got = C.CHECKS["S2"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"], got
        assert "storey 0" in got[0]["detail"] and "storey 1" in got[0]["detail"], got

    def test_s1_sees_a_wall_drawn_a_fifth_too_thin(self, monkeypatch):
        """The tolerance was a quarter of the wall: 0.78 of every wall agreed on 16 of 16."""
        def change(svg, rec, re):
            return re.sub(r'(<rect class="wb" x="[^"]*" y="[^"]*" width=")([^"]*)"',
                          lambda m: '%s%.2f"' % (m.group(1), float(m.group(2)) * 0.8), svg)
        self._planted(monkeypatch, change)
        got = C.CHECKS["S1"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"], got
