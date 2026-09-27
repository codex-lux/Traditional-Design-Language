"""A projection nobody published is not a projection of 0 (WP-14.2, Phase 14 decision 2).

`proportion_engine.dimension()` read a member's projection as `m.get("projection_parts", 0)`, so
the 94 resolved order-pack members whose authority gives no projection -- every torus, scotia and
plinth among them -- reached every surface as faces MEASURED flush with their naked. Three things
followed, and each was a different surface telling a different lie about one missing figure:

  * a torus built from a crown of 0 springs half its height INSIDE the naked, so fourteen tori and
    scotias were drawn bitten into the shaft they stand on (census P3, six plates), two of them
    running off the plate (P4);
  * OQ 78's datum detection read those zeros as EVIDENCE, so nine assemblies with no figure at all
    were confidently called "naked" on the strength of their own silence; and
  * the pedestal's die, derived from the base's plinth, fell back to R x 1.2 wherever the plinth
    had no figure -- a number no record states -- and where it had one, was read on the PACK's
    datum rather than the base's, so an axis-declared pack whose base reads as relief drew its die
    narrower than the plinth standing on it.

The ruling (27 Sep 2026): mark it, draw it as a ghost at its naked, and count it on every plate.
This file holds each half of that, and pins the 46 written zeros that remain against the reason
each one is a real zero rather than a placeholder -- on `TestTheTranscribedWidths...`'s precedent,
because a zero is a transcription too, and nothing else in the tree says which of the two it is.

Nothing here writes inside the repository: every case that needs a defect puts it on a copy.
"""
import copy
import glob
import json
import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import modcache  # noqa: E402
import inkread as IR  # noqa: E402

PE = modcache.load("proportion_engine", os.path.join(ROOT, "build", "proportion_engine.py"))
PROF = modcache.load("profiles", os.path.join(ROOT, "build", "profiles.py"))


def _order_ids():
    return sorted(pid for pid, p in PE.PACKS.items() if p.get("kind") == "order-system")


def _raw_files():
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "proportions", "**", "*.json"), recursive=True)):
        d = json.load(open(f))
        out[d["id"]] = (f, d)
    return out


def _geometry(pid, module_in=36.0, pedestal=True):
    r = PE.resolve(pid)
    asms = PE.stack_for(r)
    if not pedestal:
        asms = [a for a in asms if a not in ("pedestal", "subplinth")]
    d = PE.dimension(r, module_in, include=asms)
    return r, d, PROF.pack_geometry(d, r.get("column"), r.get("projection_datum"))


# ------------------------------------------------------------------ the engine
class TestTheEngineCarriesAMissingFigureAsNone:
    def test_absent_written_zero_and_written_null_are_three_different_answers(self):
        def member(pid, aid, mid):
            d = PE.dimension(PE.resolve(pid), 36.0)
            a = next(a for a in d["assemblies"] if a["id"] == aid)
            return next(m for m in a["members"] if m["id"] == mid)
        # absent in the record: Palladio restates his Ionic base and publishes no projection
        assert member("palladio-ionic", "base", "base_plinth")["projection_in"] is None
        # written 0: the die IS the pedestal's naked
        assert member("vignola-doric", "pedestal", "ped_die")["projection_in"] == 0.0
        # written null: reclassified in WP-14.2 (below)
        assert member("vignola-tuscan", "shaft", "shaft_apophyge")["projection_in"] is None
        assert member("vignola-tuscan", "shaft", "shaft_apophyge")["projection_parts"] is None

    def test_every_resolved_member_is_none_exactly_where_its_record_publishes_nothing(self):
        """Over the whole population, not three examples: 934 resolved members at the time of
        writing, every one held to its own resolved record."""
        n = 0
        for pid in _order_ids():
            r = PE.resolve(pid)
            d = PE.dimension(r, 36.0, include=list((r.get("assemblies") or {}).keys()))
            for a in d["assemblies"]:
                if a["id"] not in r["assemblies"]:
                    continue         # the engine's own derived shaft: no record to hold it to
                raw = {m["id"]: m for m in r["assemblies"][a["id"]].get("members", [])}
                for m in a["members"]:
                    n += 1
                    want_none = raw[m["id"]].get("projection_parts") is None
                    assert (m["projection_in"] is None) == want_none, (pid, a["id"], m["id"])
        assert n > 900, n

    def test_an_unpublished_shaft_is_no_evidence_for_the_observed_datum(self):
        """`observed_projection_datum` read `or 0.0`, so a shaft body nobody transcribed read as
        "naked" -- the reading a missing figure happens to resemble. It is no evidence now, and
        the capital answers instead; with nothing else to read, the verdict is None."""
        d = PE.dimension(PE.resolve("vignola-tuscan"), 36.0)
        assert PE.observed_projection_datum(d) == "naked"
        shaft = next(a for a in d["assemblies"] if a["id"] == "shaft")
        body = next(m for m in shaft["members"] if m["id"] == "shaft_body")
        body["projection_in"] = 50.0                 # a real, wrong, radius-sized figure ...
        assert PE.observed_projection_datum(d) is None   # ... is read, and fits neither
        body["projection_in"] = None                 # unpublished: skipped, the capital answers
        assert PE.observed_projection_datum(d) == "naked"
        d["assemblies"] = [a for a in d["assemblies"] if a["id"] == "shaft"]
        assert PE.observed_projection_datum(d) is None   # nothing left to read


# ------------------------------------------------------------------ the written zeros
class TestTheWrittenZerosAreClassified:
    """Every `projection_parts: 0` still in the corpus, and why it is a real zero.

    Three kinds of reason, and the test checks each against the record rather than trusting it:

      datum    the member IS the plane its assembly's figures are measured from -- a pedestal's
               die, a shaft's body, a frieze or metope (the entablature's naked, by
               `pack_geometry`'s own datum rule), a capital's necking. Its 0 is a definition.
      origin   the lowest face of an architrave whose every later member states a positive
               offset from it. The 0 is the origin the author counted the sequence from.
      stated   the member's own note says the face is in the plane, and the quotation is held
               to the note.

    The two rows that were NOT real zeros are RECLASSIFIED below, null in the record since
    WP-14.2. Classified by reading each note, 27 Sep 2026; zero rows were left COULD NOT
    CLASSIFY. A written zero added without a row here fails, which is the point: a 0 is a
    transcription and has to say which kind it is."""

    WRITTEN_ZEROS = [
        ("greek-doric", "entablature", "architrave", "origin", ""),
        ("vignola-composite", "architrave", "fascia_1", "origin", ""),
        ("vignola-composite", "frieze", "frieze", "datum", ""),
        ("vignola-corinthian", "architrave", "fascia_1", "origin", ""),
        ("vignola-corinthian", "frieze", "frieze", "datum", ""),
        ("vignola-doric", "pedestal", "ped_die", "datum", ""),
        ("vignola-doric", "shaft", "shaft_body", "datum", ""),
        ("vignola-doric", "capital", "cap_necking", "datum", ""),
        ("vignola-doric", "architrave", "arch_lower_fascia", "origin", ""),
        ("vignola-doric", "frieze", "metope", "datum", ""),
        ("vignola-ionic", "architrave", "fascia_1", "origin", ""),
        ("vignola-ionic", "frieze", "frieze", "datum", ""),
        ("vignola-ionic", "entablature", "frieze", "datum", ""),
        ("vignola-tuscan", "pedestal", "ped_die", "datum", ""),
        ("vignola-tuscan", "shaft", "shaft_body", "datum", ""),
        ("vignola-tuscan", "capital", "cap_necking", "datum", ""),
        ("vignola-tuscan", "architrave", "arch_face", "stated",
         "its lower edge is set in line with the top of the shaft"),
        ("vignola-tuscan", "frieze", "frieze_face", "datum", ""),
        ("vignola-tuscan", "entablature", "ent_frieze", "datum", ""),
        ("benjamin-corinthian", "pedestal", "ped_die", "datum", ""),
        ("benjamin-corinthian", "entablature", "ent_frieze", "datum", ""),
        ("benjamin-corinthian", "entablature_plain_frieze", "entpf_frieze", "datum", ""),
        ("benjamin-doric", "capital", "cap_necking", "datum", ""),
        ("benjamin-doric", "frieze", "metope", "datum", ""),
        ("benjamin-doric", "frieze", "frieze_plane_note", "stated",
         "the faces of the frize and architrave are both in the same plane"),
        ("benjamin-ionic", "pedestal", "ped_die", "datum", ""),
        ("benjamin-ionic", "entablature", "ent_frieze", "datum", ""),
        ("benjamin-tuscan", "pedestal", "ped_die", "datum", ""),
        ("benjamin-tuscan", "entablature", "ent_frieze", "datum", ""),
        ("gibbs-composite", "pedestal", "ped_die", "datum", ""),
        ("gibbs-composite", "architrave", "arch_fascia_1", "origin", ""),
        ("gibbs-composite", "frieze", "frieze_face", "datum", ""),
        ("gibbs-composite", "entablature", "ent_frieze", "datum", ""),
        ("gibbs-corinthian", "pedestal", "ped_die", "datum", ""),
        ("gibbs-corinthian", "architrave", "arch_fascia_1", "origin", ""),
        ("gibbs-corinthian", "frieze", "frieze_face", "datum", ""),
        ("gibbs-corinthian", "entablature", "ent_frieze", "datum", ""),
        ("gibbs-doric", "pedestal", "ped_die", "datum", ""),
        ("gibbs-ionic", "pedestal", "ped_die", "datum", ""),
        ("gibbs-ionic", "architrave", "arch_fascia_1", "origin", ""),
        ("gibbs-ionic", "frieze", "frieze_face", "datum", ""),
        ("gibbs-ionic", "entablature", "ent_frieze", "datum", ""),
        ("gibbs-tuscan", "pedestal", "ped_die", "datum", ""),
        ("gibbs-tuscan", "architrave", "arch_lower_fascia", "origin", ""),
        ("gibbs-tuscan", "frieze", "frieze_face", "datum", ""),
        ("gibbs-tuscan", "entablature", "ent_frieze", "datum", ""),
    ]

    # Written 0 until WP-14.2 and null since, each with the words that showed the 0 was a
    # placeholder: an apophyge whose face is 0 never flares to the fillet it exists to meet.
    RECLASSIFIED = [
        ("vignola-doric", "shaft", "shaft_apophyge", "Height apportioned"),
        ("vignola-tuscan", "shaft", "shaft_apophyge", "Vignola gives it graphically only"),
    ]

    # Which assemblies and member ids a `datum` row may name: the planes pack_geometry measures
    # each assembly's figures from.
    DATUM_ROLES = {
        "pedestal": ("die", "dye"),
        "shaft": ("shaft_body",),
        "capital": ("necking",),
        "frieze": ("frieze", "metope"),
        "entablature": ("frieze",),
        "entablature_plain_frieze": ("frieze",),
    }

    def _written_zeros(self):
        live = {}
        for pid, (_f, d) in _raw_files().items():
            if d.get("kind") != "order-system":
                continue
            for aid, a in (d.get("assemblies") or {}).items():
                for i, m in enumerate(a.get("members", [])):
                    if "projection_parts" in m and m["projection_parts"] == 0:
                        live[(pid, aid, m["id"])] = (i, a["members"], m)
        return live

    def test_the_table_is_every_written_zero_in_the_corpus(self):
        live = set(self._written_zeros())
        pinned = {(p, a, m) for p, a, m, _k, _q in self.WRITTEN_ZEROS}
        assert len(pinned) == len(self.WRITTEN_ZEROS), "a row is pinned twice"
        assert live == pinned, (
            "a written zero with no reason recorded, or a row whose zero has gone -- classify it "
            f"or remove it: unpinned {sorted(live - pinned)}; stale {sorted(pinned - live)}")

    def test_each_reason_is_true_of_the_record(self):
        live = self._written_zeros()
        bad = []
        for pid, aid, mid, kind, quote in self.WRITTEN_ZEROS:
            i, members, m = live[(pid, aid, mid)]
            if kind == "datum":
                roles = self.DATUM_ROLES.get(aid, ())
                if not any(r in mid for r in roles):
                    bad.append(f"{pid}/{aid}.{mid}: not a datum plane of its assembly")
            elif kind == "origin":
                later = [x.get("projection_parts") for x in members[i + 1:]]
                if i != 0 or not later or not all(isinstance(v, (int, float)) and v > 0
                                                  for v in later):
                    bad.append(f"{pid}/{aid}.{mid}: not the origin of a positive relief sequence")
            elif kind == "stated":
                if not quote or quote not in (m.get("note") or ""):
                    bad.append(f"{pid}/{aid}.{mid}: the quotation is not in the member's note")
            else:
                bad.append(f"{pid}/{aid}.{mid}: unknown kind {kind!r}")
        assert not bad, "\n  ".join(bad)

    def test_the_reclassified_rows_are_null_and_say_why(self):
        files = _raw_files()
        for pid, aid, mid, quote in self.RECLASSIFIED:
            _f, d = files[pid]
            m = next(x for x in d["assemblies"][aid]["members"] if x["id"] == mid)
            assert "projection_parts" in m and m["projection_parts"] is None, (pid, mid)
            assert quote in m["note"] and "PROJECTION NOT PUBLISHED" in m["note"], (pid, mid)


# ------------------------------------------------------------------ the ghost
class TestAnUnpublishedMemberIsAGhostAtItsNaked:
    def test_no_ghost_is_constructed_and_every_one_stands_at_its_naked(self):
        n = 0
        for pid in _order_ids():
            for ped in (True, False):
                _r, _d, g = _geometry(pid, pedestal=ped)
                ghosts = {(u["assembly"], u["id"]): u for u in g["unpublished"]}
                for a in g["assemblies"]:
                    for f in a["faces"]:
                        if f.get("projection") != "unpublished":
                            continue
                        n += 1
                        u = ghosts[(a["id"], f["id"])]
                        assert all(s["kind"] == "line" and s.get("ghost") == f["id"]
                                   for s in f["segments"]), (pid, f["id"], f["segments"])
                        # to the 5 places `unpublished` is stated to; the segments carry 6
                        assert all(abs(s["to"][0] - u["x"]) < 1e-5 for s in f["segments"][-1:])
                        assert f["x"] == u["x"]
                assert len(ghosts) == len(g["unpublished"]), pid
        assert n > 100, f"only {n} ghosts: the population this guards has gone"

    def test_the_ink_draws_no_edge_across_a_ghost_and_the_fill_does(self):
        """`path` is the body -- one closed fill through every member -- and `outline_path` the
        ink. A stroke up a ghost's naked is a face drawn as though somebody measured it."""
        checked = 0
        for pid in _order_ids():
            _r, _d, g = _geometry(pid)
            if not g["unpublished"]:
                continue
            ink = _drawn_edges(g["outline_path"])
            fill = _drawn_edges(g["path"])
            for u in g["unpublished"]:
                if u["y1"] - u["y0"] < 1e-6:
                    continue
                edge = ((round(u["x"], 3), round(u["y0"], 3)), (round(u["x"], 3), round(u["y1"], 3)))
                assert edge not in ink, (pid, u["id"])
                assert edge in fill, (pid, u["id"])
                checked += 1
        assert checked > 50, checked

    def test_every_ghost_has_its_bracket_and_the_bracket_points_out(self):
        for pid in _order_ids():
            _r, _d, g = _geometry(pid)
            tall = [u for u in g["unpublished"] if u["y1"] - u["y0"] > 1e-6]
            subs = [s for s in IR.sample_commands(IR.parse_path(g["ghost_path"]), n=2, lines=True)
                    if s] if g["ghost_path"] else []
            assert len(subs) == len(tall), (pid, len(subs), len(tall))
            for sub, u in zip(subs, tall):
                xs = [x for x, _y in sub]
                assert min(xs) == pytest.approx(u["x"], abs=1e-3), pid       # on the naked
                assert max(xs) > u["x"], pid                                   # ticks point out

    def test_the_stated_extent_holds_all_the_ink_and_no_more(self):
        """`bbox_in` is what a plate sizes its frame from (the workbench frame that came out
        narrower than its own ink on twelve axis packs). Containing and TIGHT, both."""
        for pid in _order_ids():
            _r, _d, g = _geometry(pid)
            b = g["bbox_in"]
            if not g["path"]:
                assert b is None, pid        # nothing drawn, no extent claimed (moorish-arch)
                continue
            pts = [p for sub in IR.sample_commands(IR.parse_path(g["path"]), n=48, lines=True)
                   for p in sub]
            if g["ghost_path"]:
                pts += [p for sub in IR.sample_commands(IR.parse_path(g["ghost_path"]), n=2,
                                                        lines=True) for p in sub]
            xs, ys = [x for x, _ in pts], [y for _, y in pts]
            assert min(xs) >= b["x0"] - 1e-3 and max(xs) <= b["x1"] + 1e-3, pid
            assert min(ys) >= b["y0"] - 1e-3 and max(ys) <= b["y1"] + 1e-3, pid
            assert max(xs) == pytest.approx(b["x1"], abs=0.02), (pid, max(xs), b["x1"])

    def test_the_new_outputs_are_linear_in_the_module(self):
        """tests/test_profiles.py proves the geometry scales with the module; the ghost's bracket
        and the stated extent must too, or a consumer that scales the served geometry (which is
        what the orders page does) draws them at the wrong size."""
        for pid in ("palladio-ionic", "vignola-tuscan", "chambers-corinthian"):
            _r, _d, a = _geometry(pid, 12.0)
            _r, _d, b = _geometry(pid, 36.0)
            for k in ("x1", "y1"):
                assert b["bbox_in"][k] == pytest.approx(a["bbox_in"][k] * 3.0, rel=1e-4), pid
            pa = [p for s in IR.sample_commands(IR.parse_path(a["ghost_path"]), n=2, lines=True) for p in s]
            pb = [p for s in IR.sample_commands(IR.parse_path(b["ghost_path"]), n=2, lines=True) for p in s]
            assert len(pa) == len(pb) and pa, pid
            for (xa, ya), (xb, yb) in zip(pa, pb):
                assert xb == pytest.approx(xa * 3.0, abs=2e-3) and yb == pytest.approx(ya * 3.0, abs=2e-3)


def _drawn_edges(d):
    """The straight edges a path DRAWS (L commands), rounded; moves are not edges."""
    out = set()
    cur = None
    for c in IR.parse_path(d):
        k = c[0]
        if k == "M":
            cur = (c[1], c[2])
        elif k == "L":
            a, b = (round(cur[0], 3), round(cur[1], 3)), (round(c[1], 3), round(c[2], 3))
            out.add((a, b)); out.add((b, a))
            cur = (c[1], c[2])
        elif k in ("A", "C", "Q"):
            cur = (c[-2], c[-1])
    return out


# ------------------------------------------------------------------ the datum
class TestADatumWithNoEvidenceIsUnjudged:
    UNJUDGED = {
        ("palladio-ionic", "base"), ("palladio-ionic", "architrave"),
        ("palladio-ionic", "frieze"), ("palladio-ionic", "cornice"),
        ("palladio-corinthian", "pedestal"), ("palladio-composite", "pedestal"),
        ("chambers-ionic", "pedestal"), ("chambers-corinthian", "pedestal"),
        ("chambers-composite", "pedestal"),
    }

    def test_the_unjudged_assemblies_are_exactly_the_nine(self):
        """Measured when the rule changed: nine assemblies went "naked" -> "unjudged", none of
        them holding a figure, and no group moved between "axis" and "naked"."""
        live = set()
        for pid in _order_ids():
            _r, _d, g = _geometry(pid)
            live |= {(pid, a) for a, v in g["assembly_datum"].items() if v == "unjudged"}
        assert live == self.UNJUDGED, (sorted(live - self.UNJUDGED), sorted(self.UNJUDGED - live))

    def test_an_unjudged_group_publishes_nothing_and_a_naked_pack_is_taken_at_its_word(self):
        for pid in _order_ids():
            r, d, g = _geometry(pid)
            for a in d["assemblies"]:
                pub = [m for m in a["members"] if m.get("projection_in") is not None]
                if g["assembly_datum"][a["id"]] == "unjudged":
                    assert r.get("projection_datum") == "axis" and not pub, (pid, a["id"])
        # palladio-tuscan publishes nothing in its capital and declares naked: declaration holds
        _r, _d, g = _geometry("palladio-tuscan")
        assert g["assembly_datum"]["capital"] == "naked"


# ------------------------------------------------------------------ the die
class TestTheDieCarriesThePlinth:
    def test_the_die_is_the_plinths_drawn_face_read_on_the_bases_own_datum(self):
        checked = 0
        for pid in _order_ids():
            r, d, g = _geometry(pid)
            if "pedestal" not in g["assembly_datum"]:
                continue
            base = next(a for a in d["assemblies"] if a["id"] == "base")
            pub = [m["projection_in"] for m in base["members"] if m.get("projection_in") is not None]
            R = g["lower_radius_in"]
            ped = next(a for a in g["assemblies"] if a["id"] == "pedestal")
            if not pub:
                assert g["die_naked"] == "unjudged" and g["die_naked_in"] is None, pid
                assert "base" in g["die_naked_reason"], pid
                assert ped["naked_in"] == pytest.approx(R), pid
                continue
            face = PROF.outer_face(R, max(pub), g["assembly_datum"]["base"] == "axis")
            assert g["die_naked"] == "derived", pid
            assert g["die_naked_in"] == pytest.approx(face, abs=1e-4), pid
            assert ped["naked_in"] == pytest.approx(face, abs=1e-4), pid
            checked += 1
        assert checked >= 20, checked

    def test_benjamins_corinthian_die_stands_under_its_plinth_and_not_inside_it(self):
        """The case that found it: axis-declared, base read as relief, and the die placed at
        max(R, plinth) = R while the plinth it carries projected to R + plinth."""
        _r, d, g = _geometry("benjamin-corinthian")
        base = next(a for a in g["assemblies"] if a["id"] == "base")
        plinth_face = max(f["x"] for f in base["faces"])
        assert g["die_naked_in"] == pytest.approx(plinth_face, abs=1e-4)
        assert g["die_naked_in"] > g["lower_radius_in"] + 1.0

    def test_no_die_is_invented(self):
        """R x 1.2 was the old fallback. Where the base publishes nothing, the die is None and the
        pedestal stands on the column's own radius, which is a placement, not a figure."""
        _r, _d, g = _geometry("palladio-ionic")
        assert g["die_naked_in"] is None and g["die_naked"] == "unjudged"


# ------------------------------------------------------------------ the surfaces
class TestTheSurfacesSayIt:
    def test_the_agents_tool_is_told_what_the_plate_is_told(self):
        """`tdl_get_proportions` served every member's null projection and nothing else: an agent
        could not tell which datum an assembly was read on, or that a null is a ghost at the naked
        rather than a face. Served since WP-14.2, and judged on the FULL stack even when one
        assembly is asked for -- the datum is a property of the assembly's group, and the cornice
        read alone could come out differently from the entablature it belongs to."""
        import sys as _s
        _s.path.insert(0, os.path.join(ROOT, "mcp_server"))
        import core
        for pid, asm in (("palladio-ionic", None), ("vignola-ionic", "cornice"),
                         ("chambers-corinthian", "pedestal")):
            got = core.get_proportions(pid, column_diameter=12, include_rules=False, assembly=asm)
            r = PE.resolve(pid)
            full = PE.dimension(r, got["module_in"])
            g = PROF.pack_geometry(full, r.get("column"), r.get("projection_datum"))
            assert got["projection_datum"] == r.get("projection_datum"), pid
            assert got["assembly_datum"] == g["assembly_datum"], pid
            assert got["unpublished"] == [{"assembly": u["assembly"], "id": u["id"]}
                                          for u in g["unpublished"]], pid
            assert got["bbox_in"] == g["bbox_in"], pid
        # the premise: one of the three really carries unpublished members and an unjudged group
        got = core.get_proportions("palladio-ionic", column_diameter=12, include_rules=False)
        assert len(got["unpublished"]) == 14 and "unjudged" in got["assembly_datum"].values()

    def test_a_plate_of_ghosts_says_how_many_and_draws_them_dashed(self):
        RP = modcache.load("render_profile", os.path.join(ROOT, "build", "render_profile.py"))
        svg, rep = RP.render("palladio-ionic", "base", 12.0)
        assert len(rep["unpublished"]) == 6
        text = re.sub(r"\s+", " ", " ".join(re.findall(r">([^<]*)</text>", svg)))
        assert "6 member(s) drawn as a dashed bracket at the naked: no projection published" in text
        assert "no relief drawn: no member publishes a projection" in text
        ghost = re.search(r'<path class="ghost" d="([^"]+)"[^>]*stroke-dasharray', svg)
        assert ghost and len(IR.sample_commands(IR.parse_path(ghost.group(1)), n=2, lines=True)) == 6

    def test_the_plates_ink_runs_up_no_ghosts_naked(self):
        """FOUND BY LOOKING, and this is the guard for it: the first plates rendered with ghosts
        still stroked the silhouette's CLOSING edge, which runs back down the naked -- where every
        ghost stands -- so a solid line crossed the three members the brackets called unknown.
        Read back through the plate's own frame: no stroked edge on the naked overlaps a ghost."""
        import ink_surfaces as SURF
        RP = modcache.load("render_profile", os.path.join(ROOT, "build", "render_profile.py"))
        svg, rep = RP.render("palladio-doric", "base", 12.0)
        assert len(rep["unpublished"]) == 3, "premise: the plate carries ghosts"
        pl = SURF.ProfilePlate(svg)
        naked = pl.naked()
        rec = SURF.profile_record("palladio-doric", "base", 12.0)
        spans = [(m["y_bottom_in"], m["y_top_in"]) for m in rec["members"]
                 if m["id"] in rep["unpublished"]]
        inks = [it for it in pl.ink.select("path")
                if (it.style.get("fill") or "none") in ("none", "transparent")
                and (it.style.get("stroke") or "none") != "none"
                and not ({"ghost", "confidence", "envelope"} & set(it.classes))]
        assert inks, "no stroked outline found"
        crossing = []
        for it in inks:
            for sub in it.subpaths(n=2, lines=True):
                pts = [pl.model(p) for p in sub]
                for (u0, v0), (u1, v1) in zip(pts, pts[1:]):
                    if abs(u0 - naked) < 1e-3 and abs(u1 - naked) < 1e-3:
                        lo, hi = sorted((v0, v1))
                        for a, b in spans:
                            if min(hi, b) - max(lo, a) > 1e-3:
                                crossing.append((round(lo, 3), round(hi, 3), a, b))
        assert not crossing, f"solid ink up the naked across a ghost: {crossing}"

    def test_a_complete_plate_says_it_is_complete(self):
        RP = modcache.load("render_profile", os.path.join(ROOT, "build", "render_profile.py"))
        svg, rep = RP.render("vignola-doric", "capital", 6.0)
        assert rep["unpublished"] == []
        text = re.sub(r"\s+", " ", " ".join(re.findall(r">([^<]*)</text>", svg)))
        assert "All %d member(s) publish a projection." % rep["members"] in text
        assert 'class="ghost"' not in svg

    def test_the_elevation_inset_draws_and_says_a_ghost_DRIVEN(self, tmp_path):
        """No building sheet reaches an unpublished cornice member today (measured over all
        sixteen plans), so this branch is driven with one and its premise asserted."""
        EL = modcache.load("elevation", os.path.join(ROOT, "build", "elevation.py"))
        RE = modcache.load("render_elevation", os.path.join(ROOT, "build", "render_elevation.py"))
        plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
        elev = EL.build_elevation(plan)
        members = elev["eave_cornice"]["members"]
        assert all(m.get("projection_in") is not None for m in members), "premise: all published"
        out = str(tmp_path / "control.svg")
        RE.render_elevation(elev, out)
        assert 'class="ghost"' not in open(out).read()
        driven = copy.deepcopy(elev)
        driven["eave_cornice"]["members"][1]["projection_in"] = None
        out = str(tmp_path / "driven.svg")
        RE.render_elevation(driven, out)
        svg = open(out).read()
        assert 'class="ghost"' in svg
        assert "1 MEMBER(S) DRAWN AS A DASHED BRACKET AT THE NAKED" in svg

    def test_the_scene_does_not_call_an_unpublished_member_a_projection_of_0_DRIVEN(self):
        SC = modcache.load("scene", os.path.join(ROOT, "build", "scene.py"))
        G = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))
        ST = modcache.load("structure", os.path.join(ROOT, "build", "structure.py"))
        RF = modcache.load("roof", os.path.join(ROOT, "build", "roof.py"))
        EL = modcache.load("elevation", os.path.join(ROOT, "build", "elevation.py"))
        plan = json.load(open(os.path.join(ROOT, "plans", "spec-builder-colonial.json")))
        sol = G.solve(json.loads(json.dumps(plan)), engine="heuristic")
        sec = ST.build_section(sol, None, geometry_result=sol)
        rf = RF.build_roof(sol, None, section=sec)
        ev = EL.build_elevation(sol, None, section=sec, roof=rf)
        mem = (ev.get("entrance") or {}).get("entablature_members") or []
        assert mem and all(m.get("projection_in") is not None for m in mem), "premise"
        ev = copy.deepcopy(ev)
        ev["entrance"]["entablature_members"][0]["projection_in"] = None
        mid = ev["entrance"]["entablature_members"][0]["id"]
        sc = SC.build_scene(sol, sec, rf, ev)
        hit = [s for s in sc["solids"] if s["id"].endswith("-" + mid) and s["class"] == "entablature"]
        assert hit and hit[0]["geometry"]["type"] == "plane"
        assert "publishes no projection" in hit[0]["note"]
        assert "projection of 0 states" not in hit[0]["note"]
