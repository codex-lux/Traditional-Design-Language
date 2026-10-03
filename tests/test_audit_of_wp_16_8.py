"""THE AUDIT OF WP-16.8'S OWN DIFF (`e604955..6873f91`, 3 Oct 2026): guards for what it found.

WP-16.8 audited Phase 16; five more auditors then took WP-16.8's own diff, on WP-15.8's precedent
(that audit's §X). Each test here holds one finding fixed, and each was mutation-checked against
the fix it guards (the WP-16.8 report's §X lists the mutations). Houses are built on the heuristic
engine, which is deterministic, and every solve takes a private cache.

- B2: the section's roof-judgment line (T3) is wrapped to the sheet and reads back whole;
- B6: every note beneath every elevation fits its sheet, and reads back whole;
- B3 and B10: the DXF masks what the sheet paints over a band -- the sidelights, the transom and
  every opening -- and masks each band before its outline, as the sheet's fill hides the wall;
- B5: the roof plan's DXF says what the roof plan says (`render_roof.plan_notes`, one list);
- A-F4: the belt's figures reach the critic only where a belt is drawn, and only as stated;
- B11: a belt is refused only where an upper floor would carry one;
- A-F1: an undated hip draws no return, measured -- U15's date gate is a gable end's;
- A-F2: whether the rake is drawn is asked of the drawn marks (`rake_drawn`), and why it is not of
  the roof's ridge and form (`rake_not_drawn_cause`), never of the pitch; A-F6, the gambrel's outline;
- D1: a return said drawn only where one is; where none is, the house's own reason (`return_withheld`);
- U16 (auditor D's D3): the lights an undated house is drawn with are the default's, withheld from
  the critic -- a reading taken as recommended under Lucas's standing instruction of 1 Oct 2026,
  never put;
- auditor C's W2, W3: each stack a face draws stands at its own plan extent on either ridge, and the
  near wall's is drawn last; the section is cut across the span its ridge was raised over;
- auditor C's W1 and D's D10: every shipped section carries its roof record's judgment (T3), the
  section DXF and the IFC say it, and the IFC says why it places no planes;
- D6: a banned stack is refused for its ban on every roof; D11: an unstated band projection is
  written as unstated; D7 (= B's B8): the scene says a forbidden light pattern; D9c (= B's B9): a
  gambrel's section raises no single-pitch ridge; D-S2: a windowless room's advice follows the rule
  that refused its window;
- B's B12, A's F5: a hip rises at its stated pitch on every face, whatever its footprint;
- C's M1: no standing reason says a rake or a return is drawn on every house, and each of
  `rake_withheld`'s branches is driven; C's M3: the scene names every band the elevation draws and
  no other; C's M4: the DXF draws the bands and the member lines the SHEET draws, read off its ink;
  C's M7: a refused roof has no judged gable end on either reader.
"""
import copy
import glob
import json
import os
import sys
import tempfile
import xml.etree.ElementTree as ET

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import modcache as mc  # noqa: E402
import inkread as IR  # noqa: E402


def _m(name):
    return mc.load(name, os.path.join(ROOT, "build", name + ".py"))


G, ST, RF, EL, RE, RS, DI = (_m(n) for n in ("geometry", "structure", "roof", "elevation",
                                             "render_elevation", "render_section", "disclosures"))
SVG = "{http://www.w3.org/2000/svg}"
FACES = ("S", "N", "E", "W")
# The advance of a character in each monospaced class the sheets set, in px: `.dm` is 7.5 px
# (0.6 em a character), `.lb` 8.5 px with .14 em of letter-spacing.
ADVANCE = {"dm": 7.5 * 0.6, "lb": 8.5 * (0.6 + 0.14)}


def _plans():
    return (sorted(glob.glob(os.path.join(ROOT, "plans", "*.json")))
            + sorted(glob.glob(os.path.join(ROOT, "plans", "reference", "*.json"))))


def _built(plan):
    saved = G._SOLVE_CACHE
    G._SOLVE_CACHE = {}
    try:
        q = G.solve(copy.deepcopy(plan), None, 250, engine="heuristic")
    finally:
        G._SOLVE_CACHE = saved
    sec = ST.build_section(q, None, geometry_result=q)
    if "error" in sec:
        return q, None, None, None
    rf = RF.build_roof(q, None, section=sec)
    return q, sec, rf, EL.build_elevation(q, None, section=sec, roof=rf)


@pytest.fixture(scope="module")
def corpus():
    out = {}
    for f in _plans():
        with open(f, encoding="utf-8") as fh:
            out[os.path.basename(f)[:-5]] = _built(json.load(fh))
    return out


def _svg(fn, obj, **kw):
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "s.svg")
        fn(obj, path, **kw)
        with open(path, encoding="utf-8") as fh:
            return fh.read()


def _lines(text_el):
    """A <text>'s lines as set: one per <tspan> where it carries spans, else its own text --
    each with the x it is set at."""
    spans = text_el.findall(SVG + "tspan")
    if spans:
        return [(float(sp.get("x")), sp.text or "") for sp in spans]
    return [(float(text_el.get("x")), text_el.text or "")]


def _overruns(svg, cls, below_y=None):
    root = ET.fromstring(svg)
    width = float(root.get("width"))
    bad, wrapped = [], 0
    for t in root.iter(SVG + "text"):
        if cls not in (t.get("class") or "").split():
            continue
        if below_y is not None and float(t.get("y")) <= below_y:
            continue
        lines = _lines(t)
        wrapped += len(lines) > 1
        for x, ln in lines:
            if x + len(ln.rstrip()) * ADVANCE[cls] > width + 0.5:
                bad.append((round(x + len(ln.rstrip()) * ADVANCE[cls] - width), ln[:50]))
    return bad, wrapped


def _ground_y(svg):
    root = ET.fromstring(svg)
    ys = [float(t.get("y")) for t in root.iter(SVG + "text")
          if "dm" in (t.get("class") or "").split() and (t.text or "").startswith("GROUND ")]
    assert len(ys) == 1, ys
    return ys[0]


# ------------------------------------------------------------------ B6: the elevation's notes
def test_every_note_beneath_every_elevation_fits_its_sheet(corpus):
    """Auditor B: the rake's note ran 310 to 688 px off the sheet on sixteen gable faces, and on
    four "NOT DRAWN" itself was never visible. Every note is wrapped to the sheet now. The premise
    -- some note in the corpus is long enough to wrap -- is asserted, or this would pass over a
    renderer that never wraps on a corpus that never needs it."""
    faces, wrapped, bad = 0, 0, []
    for pid, (_q, _sec, _rf, el) in sorted(corpus.items()):
        if el is None or not el.get("applicable", True) or "error" in el:
            continue
        for face in FACES:
            svg = _svg(RE.render_elevation, el, face=face)
            over, w = _overruns(svg, "dm", below_y=_ground_y(svg))
            bad += [(pid, face) + o for o in over]
            wrapped += w
            faces += 1
    assert faces >= 40, ("the premise: the corpus draws its elevations", faces)
    assert wrapped >= 1, "the premise: no note in the corpus wraps, so the wrap was not tested"
    assert not bad, bad[:5]


def test_a_wrapped_note_reads_back_as_the_sentence_face_notes_wrote(corpus):
    """The tspans of a wrapped note are one <text>, every line but the last ending in its space,
    so the ink returns the sentence whole -- which is what holds the sheet to the DXF's list. Every
    note that wraps is looked for, whole, among the sheet's texts."""
    checked = 0
    for pid, (_q, _sec, _rf, el) in sorted(corpus.items()):
        if el is None or not el.get("applicable", True) or "error" in el:
            continue
        for face in FACES:
            svg = _svg(RE.render_elevation, el, face=face)
            inked = {" ".join((t or "").split()) for t, _a, it in IR.Ink(svg).texts() if "dm" in it.classes}
            for t in ET.fromstring(svg).iter(SVG + "text"):
                if t.findall(SVG + "tspan") and "dm" in (t.get("class") or "").split():
                    whole = " ".join("".join(t.itertext()).split())
                    assert whole in {" ".join(n.split()) for n in EL.face_notes(el, face)}, (pid, face, whole[:80])
                    assert whole in inked
                    checked += 1
    assert checked >= 1, "the premise: some note wraps and was read back"


# ------------------------------------------------------------------ B2: the section's T3 line
def test_the_sections_roof_judgment_line_is_wrapped_to_the_sheet_and_reads_back_whole(corpus):
    """Auditor B: the line T3 added was one <text> and ran 124 to 299 px off all seven sections
    that print it, cutting "MARKS THE CALL A JUDGMENT". Driven onto the Tidewater section, whose
    canvas is narrower than the sentence, with the shipped (unflagged) record as the control."""
    _q, sec, rf, _el = corpus["tidewater-georgian-careful"]
    assert DI.roof_form_judgment(sec["roof"]) is None, "the control: a declared form says nothing"
    sec = copy.deepcopy(sec)
    sec["roof"]["form_reading"] = {"by": "kit", "words": None, "kit": {
        "state": "kit", "form": "side-gable", "canonical": ["side-gable"], "judgment": True,
        "judgment_by": "a-node-with-a-long-name-for-the-purpose"}}
    words = DI.roof_form_judgment(sec["roof"])
    assert words and words.endswith("JUDGMENT"), words
    svg = _svg(RS.render_section, sec)
    root = ET.fromstring(svg)
    t3 = [t for t in root.iter(SVG + "text") if "lb" in (t.get("class") or "").split()
          and "JUDGMENT" in "".join(t.itertext())]
    assert len(t3) == 1, len(t3)
    assert len(_lines(t3[0])) >= 2, "the premise: the sentence is wider than this canvas"
    assert " ".join("".join(t3[0].itertext()).split()) == " ".join(words.split())
    over, _w = _overruns(svg, "lb")
    assert not over, over


# ------------------------------------------------------------------ B3, B10: the DXF's masks
def _bbox(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), max(xs), min(ys), max(ys)


def _covers(w, b, tol=0.01):
    return w[0] <= b[0] + tol and w[1] >= b[1] - tol and w[2] <= b[2] + tol and w[3] >= b[3] - tol


def test_the_dxf_masks_every_filled_opening_and_every_band_the_sheet_paints_over(corpus, tmp_path):
    """Auditor B: the DXF masked a band only behind the rects `opening_rects` returns, so the water
    table ran through the spec Colonial's two sidelights -- glass the sheet paints over it -- and
    no wipeout stood behind a band, so the wall's corner lines ran through both to grade. Read in
    the file's own order: every closed outline on the opening layer that crosses a band has a
    wipeout covering it drawn before it, and every band box is masked before it is drawn. The
    premise -- some crossing outline is not an `opening_rects` rect, i.e. a sidelight or a transom
    -- is asserted, because the defect lived exactly there."""
    ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    DX = _m("export_dxf")
    crossing, beside_rects, bands_seen = 0, 0, 0
    for pid, (_q, _sec, _rf, el) in sorted(corpus.items()):
        if el is None or not el.get("applicable", True) or "error" in el:
            continue
        for face in FACES:
            path = str(tmp_path / f"{pid}-{face}.dxf")
            res = DX.export_elevation_dxf(el, path, face=face)
            assert "error" not in res, res
            ents = list(ezdxf.readfile(path).modelspace())
            wipes = []                                   # (entity index, bbox)
            for i, e in enumerate(ents):
                if e.dxftype() == "WIPEOUT":
                    wipes.append((i, _bbox([(v[0], v[1]) for v in e.boundary_path_wcs()])))
            bands = [(i, _bbox(e.get_points())) for i, e in enumerate(ents)
                     if e.dxftype() == "LWPOLYLINE" and e.dxf.layer == "TDL-ELEV-BAND"]
            for i, b in bands:
                bands_seen += 1
                assert any(j < i and _covers(w, b) for j, w in wipes), (pid, face, "band unmasked", b)
            rects = {(round(r["x0_in"], 2), round(r["x1_in"], 2), round(r["sill_in"], 2), round(r["head_in"], 2))
                     for r in EL.opening_rects(el, face)["rects"]}
            for i, e in enumerate(ents):
                if e.dxftype() != "LWPOLYLINE" or e.dxf.layer != "TDL-ELEV-OPENING" or not e.closed:
                    continue
                o = _bbox(e.get_points())
                if not any(min(o[1], b[1]) - max(o[0], b[0]) > 1e-6 and min(o[3], b[3]) - max(o[2], b[2]) > 1e-6
                           for _j, b in bands):
                    continue
                crossing += 1
                beside_rects += tuple(round(v, 2) for v in o) not in rects
                assert any(j < i and _covers(w, o) for j, w in wipes), (pid, face, "glass unmasked", o)
    assert bands_seen >= 10, ("the premise: the corpus draws bands", bands_seen)
    assert crossing >= 1 and beside_rects >= 1, (
        "the premise: a sidelight or transom crosses a band somewhere in the corpus", crossing, beside_rects)


# ------------------------------------------------------------------ B5: the roof plan's DXF
def test_the_roof_plans_dxf_says_every_note_the_roof_plan_says(corpus, tmp_path):
    """Auditor B: the roof plan's DXF wrote its title and nothing else, so C3's refused stacks
    vanished from it unexplained and T3 was said on every roof surface but this one. Both surfaces
    write `render_roof.plan_notes` now: the DXF's notes ARE that list, in order, and the sheet's
    note lines read back as the same sentences. The premise -- some shipped roof says something --
    is asserted."""
    ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    DX, RR = _m("export_dxf"), _m("render_roof")
    said = 0
    for pid, (_q, _sec, rf, _el) in sorted(corpus.items()):
        if rf is None or "error" in rf:
            continue
        notes = [" ".join(n.split()) for n in RR.plan_notes(rf)]
        path = str(tmp_path / f"{pid}.dxf")
        res = DX.export_roof_dxf(rf, path)
        assert "error" not in res, res
        mt = sorted(ezdxf.readfile(path).modelspace().query("MTEXT"), key=lambda e: -e.dxf.insert[1])
        assert [" ".join(e.plain_text().split()) for e in mt] == notes, (pid, notes)
        svg = _svg(RR.render_roof, rf)
        inked = " ".join(" ".join((t or "").split()) for t, _a, it in IR.Ink(svg).texts() if "dm" in it.classes)
        assert " ".join(notes) in inked, (pid, notes)
        said += len(notes)
    assert said >= 3, ("the premise: the shipped roofs say something", said)


# ------------------------------------------------------------------ A-F4, B11: the belt
BELT = ("belt_height_in", "belt_course_projection_in", "belt_height_above_first_floor_in")


def test_the_belts_figures_reach_the_critic_only_where_a_belt_is_drawn_and_as_stated(corpus):
    """Auditor A: `band_marks` (F1) draws no belt on a one-storey house, and the measurements went
    on publishing a 9.0 in belt and its 2.25 in projection to the fault corpus on six shipped plans;
    and since WP-3.2 a belt whose record states no projection -- a masonry house's, on purpose --
    was published at an invented 1.0 in. The measurements are held to `band_marks` on every plan,
    and a published projection to the record's own figure. Both premises are asserted: some
    one-storey plan carries an unrefused belt record, and some drawn belt states no projection."""
    one_storey, unstated, drawn = 0, 0, 0
    for pid, (_q, _sec, _rf, el) in sorted(corpus.items()):
        if el is None or "error" in el or not el.get("applicable", True):
            continue
        m, wtb, belt = el.get("measurements") or {}, el.get("water_table_belt") or {}, EL.band_marks(el)["belt"]
        if not belt:
            assert not [k for k in BELT if k in m], (pid, "belt figures for a belt nothing draws",
                                                    {k: m[k] for k in BELT if k in m})
            one_storey += wtb.get("belt_height_in") is not None and wtb.get("belt_datum_grade_to_floor_ft") is None
            continue
        drawn += 1
        assert m.get("belt_height_in") == wtb["belt_height_in"], pid
        if wtb.get("belt_course_projection_in") is None:
            unstated += 1
            assert "belt_course_projection_in" not in m, (pid, "an unstated projection published",
                                                          m.get("belt_course_projection_in"))
        else:
            assert m["belt_course_projection_in"] == wtb["belt_course_projection_in"], pid
    assert one_storey >= 1, "the premise: a one-storey plan carries a belt record nothing draws"
    assert drawn >= 1 and unstated >= 1, ("the premise: a drawn belt states no projection", drawn, unstated)


def _restyled(corpus, pid, style, undated=False, roof_form=None):
    q, _sec, _rf, _el = corpus[pid]
    q = copy.deepcopy(q)
    q["style"] = style
    if undated:
        (q.get("context") or {}).pop("date_of_representation", None)
    if roof_form:
        q.setdefault("declared", {})["roof_form"] = roof_form
    sec = ST.build_section(q, None, geometry_result=q)
    rf = RF.build_roof(q, None, section=sec)
    return EL.build_elevation(q, None, section=sec, roof=rf)


def test_a_belt_is_refused_only_where_an_upper_floor_would_carry_one(corpus):
    """Auditor B: "BELT COURSE NOT DRAWN -- FORBIDDEN BY ..." was printed on one-storey houses, a
    refusal about a band the house has no floor to carry. Driven: a one-storey shipped house and
    the two-storey Tidewater, each restyled to a kit that forbids the belt; the two-storey house is
    the control that the refusal is still said where a belt would stand."""
    style = "cape-cod-revival"
    one = _restyled(corpus, "bad-01-grilling-porch-ranch", style)
    two = _restyled(corpus, "tidewater-georgian-careful", style)
    assert (one.get("water_table_belt") or {}).get("belt_refused_by"), "the premise: the kit forbids the belt"
    assert (two.get("water_table_belt") or {}).get("belt_refused_by"), "the premise, on the control"
    assert (one["water_table_belt"].get("belt_datum_grade_to_floor_ft") is None
            and two["water_table_belt"].get("belt_datum_grade_to_floor_ft") is not None), "the premise: storeys"
    said = lambda el: [n for f in FACES if f in (el.get("faces") or {}) for n in EL.face_notes(el, f)
                       if n.startswith("BELT COURSE NOT DRAWN")]
    assert not said(one), said(one)[:1]
    assert said(two), "the control: a two-storey house still says the refused belt"


# ------------------------------------------------------------------ A-F1: an undated hip
RETURNS = "count_of_cornice_returns_drawn_at_the_gable_ends"


@pytest.mark.parametrize("style", ["new-england-colonial", "saltbox-colonial", "garrison-colonial"])
def test_an_undated_hip_measures_no_return_whatever_its_return_rows_date(corpus, style):
    """Auditor A: U15's date gate was AND-ed onto B5's hip branch, so an undated HIPPED house of
    a style whose `none` return is dated 1620-1700 withheld its zero -- no gable end, so no row
    decides anything -- and the two shape faults went back to could-not-evaluate. Driven onto the
    Tidewater declared hipped; the side-gabled house is the control that U15 still withholds."""
    hip = _restyled(corpus, "tidewater-georgian-careful", style, undated=True, roof_form="hip")
    gab = _restyled(corpus, "tidewater-georgian-careful", style, undated=True)
    assert hip["cornice_return"].get("date_unstated") and gab["cornice_return"].get("date_unstated"), \
        "the premise: both readings rest on a dated row"
    assert hip["cornice_return"].get("gable_faces") == [] and gab["cornice_return"].get("gable_faces"), \
        "the premise: one is a hip and one has gable ends"
    assert hip["measurements"].get(RETURNS) == 0, hip["measurements"].get(RETURNS)
    assert RETURNS not in (hip["front"].get("withheld") or {})
    assert RETURNS not in gab["measurements"] and "dated 1620-1700" in gab["front"]["withheld"][RETURNS]


# ------------------------------------------------------------------ A-F2 and A-F6: the gambrel's rake
def test_a_gambrels_rake_is_not_said_to_want_a_ridge_its_roof_states(corpus):
    """Auditor A (F2): A3's reasons decided "is not drawn: the roof judges no ridge" by a missing
    PITCH, and a gambrel states no single pitch while its roof record states its ridge. When this
    test was first written the gambrel's gable end was drawn as a single-pitch triangle and the rake
    was drawn on it; auditor A's F6 found that triangle is not a gambrel's gable end -- the two
    profiles were swapped -- and the gable end is its two-slope outline now (`roof.elevation_profile`),
    which the rake, drawn along one slope a side, does not follow. RE-CUT 3 OCT 2026 to the property
    that survives: why the rake is not drawn is read off the roof's own ridge and form
    (`rake_not_drawn_cause`), never off the pitch -- so the gambrel's reason names its outline and
    not a ridge it has. Driven: the Tidewater declared a gambrel under colonial-revival, a style with
    no migrated pitch. The spec Colonial, whose roof really judges no ridge, is the control."""
    el = _restyled(corpus, "tidewater-georgian-careful", "colonial-revival", roof_form="gambrel")
    m = el["roof_record"]["main"]
    assert m["form"] == "gambrel" and m.get("pitch_rise_per_12") is None, "the premise: no single pitch"
    assert m["ridge"]["grade_to_ridge_ft"], "the premise: the gambrel's ridge is judged"
    gf = EL.gable_faces(el["roof_record"])
    assert gf and EL.rake_drawn(el) is False
    for f in gf:
        assert len(EL.face_profile(el["roof_record"], f, el["footprint"])) == 5, "the premise: two slopes"
        assert "TWO-SLOPE OUTLINE" in (EL.rake_marks(el, f)["words"] or ""), f
    for why in EL.rake_withheld(el).values():
        assert "two-slope outline" in why and "judges no ridge" not in why, why
    _q, _s, _r, ctl = corpus["spec-builder-colonial"]
    assert EL.rake_drawn(ctl) is False
    assert any("the roof judges no ridge" in why for why in EL.rake_withheld(ctl).values())


# ------------------------------------------------------------------ D1: the return's reasons
def test_a_house_drawing_no_return_says_why_and_the_standing_reason_claims_none(corpus):
    """Auditor D: the standing reasons for the return's two figures said "a return is drawn as far
    as the cornice is tall", and eight of the sixteen shipped plans draw the band and no return --
    the only evidence on their unjudged `return-that-never-returns` row (serious) described a
    drawing that does not exist. A3 corrected the rake's two entries and not these. The standing
    reasons are worded to hold everywhere; a house that draws no return carries its own cause in
    `front.withheld`, quoting the sheet, and a house that draws one carries none. Both kinds are
    asserted present."""
    for n in EL.RETURN_NAMES:
        assert not EL.NOT_MODELLED[n].lower().startswith("a return is drawn"), EL.NOT_MODELLED[n]
    kinds = {"drawn": 0, "none": 0}
    for pid, (_q, _sec, _rf, el) in sorted(corpus.items()):
        if el is None or "error" in el or not el.get("applicable", True):
            continue
        cr, held = el.get("cornice_return") or {}, el["front"].get("withheld") or {}
        if cr.get("draws") in ("return", "plain-return"):
            kinds["drawn"] += 1
            assert not [k for k in EL.RETURN_NAMES if k in held], (pid, held)
            continue
        kinds["none"] += 1
        for k in EL.RETURN_NAMES:
            assert k in held, (pid, k)
            # the sheet's words are quoted where a gable end says them (`cornice_marks` prints them
            # only on a gable face); a hip's reason is its own
            if cr.get("words") and cr.get("gable_faces"):
                assert cr["words"] in held[k], (pid, held[k][:80])
            elif not cr.get("gable_faces"):
                assert "no gable end" in held[k], (pid, held[k][:80])
    assert kinds["drawn"] >= 1 and kinds["none"] >= 1, kinds


# ------------------------------------------------------------------ U16 (D3): an undated house's lights
def _verdicts(el, style):
    CORE = mc.load("tdlcore", os.path.join(ROOT, "mcp_server", "core.py"))
    r = CORE.check_measurements(el["measurements"], style=style, limit=10**6)
    out = {}
    for key, st in (("faults_present", "present"), ("faults_clear", "clear"),
                    ("could_not_judge", "unjudged"), ("not_applicable", "not applicable")):
        for row in r.get(key) or []:
            out[row["fault"]] = st
    return out


def test_an_undated_houses_lights_are_withheld_and_a_dated_houses_reach_the_critic(corpus):
    """Auditor D: an undated house is drawn at sash-light's 1700-1760 band, a period-neutral
    default, and the figures measured off it went to the critic as the house's own --
    `muntin-wider-than-its-date` (serious), a fault whose subject is the date, convicted good-03
    and bad-03 on the default. U16 (taken as recommended under Lucas's standing instruction of
    1 Oct 2026, never put) withholds them, quoting the module's own sentence, and only those this
    house would have published: a house with no shutters has no panel count to say anything about.
    Held on every shipped elevation, then DRIVEN on one house: the Tidewater (dated 1765) with and
    without its date, so nothing differs but the date -- the dated reading publishes and judges,
    the undated withholds and does not."""
    undated, dated, panels = 0, 0, 0
    for pid, (_q, _sec, _rf, el) in sorted(corpus.items()):
        if el is None or "error" in el or not el.get("applicable", True):
            continue
        m, held = el["measurements"], el["front"].get("withheld") or {}
        if el.get("date_of_representation") is None:
            undated += 1
            assert not [k for k in EL.DATED_LIGHT_FIGURES if k in m], (pid, "a default's light published")
            for k in EL.DATED_LIGHT_FIGURES:
                if k in held:
                    assert "(U16)" in held[k] and el["glass_module_source"] in held[k], (pid, k)
            assert "individual_light_width_in" in held, (pid, "the light width is withheld unsaid")
            panels += "shutter_panel_count_per_leaf" in held
        else:
            dated += 1
            assert not [k for k in EL.DATED_LIGHT_FIGURES if "(U16)" in held.get(k, "")], pid
    assert undated >= 5 and dated >= 1, ("the premise: both kinds of house are shipped", undated, dated)
    assert panels >= 1, "the premise: an undated shipped house carries shutters, so a panel count is withheld"

    pid = "tidewater-georgian-careful"
    style = corpus[pid][0]["style"]
    with_date = corpus[pid][3]
    without = _restyled(corpus, pid, style, undated=True)
    assert with_date["date_of_representation"] == 1765 and without["date_of_representation"] is None
    for k in ("individual_light_width_in", "individual_light_height_in", "window_sash_light_count_across"):
        assert k in with_date["measurements"] and k not in without["measurements"], k
        assert "(U16)" in without["front"]["withheld"][k] and k not in (with_date["front"].get("withheld") or {})
    # the house carries no shutters, so no panel count is withheld in its name
    assert with_date["measurements"].get("shutter_panel_count_per_leaf") is None
    assert "shutter_panel_count_per_leaf" not in without["front"]["withheld"]
    v_with, v_without = _verdicts(with_date, style), _verdicts(without, style)
    for f in ("muntin-wider-than-its-date", "lite-count-wrong-for-the-date"):
        assert v_with.get(f) in ("present", "clear"), (f, v_with.get(f), "the premise: judged on a stated date")
        assert v_without.get(f) == "unjudged", (f, v_without.get(f))


# ------------------------------------------------------------------ auditor C's W3: where a stack stands
@pytest.fixture(scope="module")
def west():
    """The Tidewater record entered on the west: B9 runs its ridge along y (the C2 drive)."""
    with open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json"), encoding="utf-8") as fh:
        plan = json.load(fh)
    plan["context"]["entrance_faces"] = "W"
    return _built(plan)[3]


def test_every_stack_a_face_draws_stands_at_its_own_plan_extent_on_either_ridge(corpus, west):
    """Auditor C (W3): C2's guard asserted that the marks exist and that the sheet draws as many as
    the record, never WHERE -- swapping the coordinates across and along the ridge in the y branch,
    the confusion C2's own docstring describes, left it green while the E and W faces each drew the
    far stack off the face, 41 ft up. An elevation is orthographic: a stack's width on a face is its
    plan extent along that face -- x on S and N, y on E and W -- through the face's own `u`. Held
    on both ridge axes, the shipped Tidewater (along x) and the same record entered on the west
    (along y), on every mark of every face; the far stack each long face hides is asserted hidden."""
    for axis, el in (("x", corpus["tidewater-georgian-careful"][3]), ("y", west)):
        assert el["roof_record"]["main"]["ridge"]["axis"] == axis, "the premise: both ridge axes"
        fp, drawn, hidden = el["footprint"], 0, 0
        for face in FACES:
            sm = EL.stack_marks(el, face)
            hidden += sm["hidden"]
            for mk in sm["marks"]:
                x0, y0, x1, y1 = mk["stack"]["plan_rect_ft"]
                a, b = (x0, x1) if face in ("S", "N") else (y0, y1)
                want = sorted((EL.face_u_outside(face, a, fp), EL.face_u_outside(face, b, fp)))
                us = [u for u, _h in mk["outline"]]
                assert abs(min(us) - want[0]) < 1e-6 and abs(max(us) - want[1]) < 1e-6, \
                    (axis, face, mk["relation"], [round(u, 2) for u in us], [round(w, 2) for w in want])
                drawn += 1
        assert drawn >= 6 and hidden >= 2, ("the premise: stacks drawn and hidden", axis, drawn, hidden)


def test_the_stack_at_a_faces_own_wall_is_drawn_last_on_a_ridge_along_y(west):
    """Auditor C (W3, C2b): `near_end_last` ordered the E and W faces alone, and since B9 a ridge
    along y stands its gable ends on S and N. No shipped record puts a stack at an S or N wall, so
    the order is DRIVEN: two stacks at the S and N walls, their squares overlapping across the face
    so the far one is not hidden, the near one listed first. The near stack must be drawn last, over
    the far, on each gable face."""
    el = copy.deepcopy(west)
    fp = el["footprint"]
    W, D = fp["width_ft"], fp["depth_ft"]
    base = el["roof_record"]["chimneys"]["positions"][0]
    side = base["plan_rect_ft"][2] - base["plan_rect_ft"][0]
    south = dict(base, x_ft=10.0 + side / 2, y_ft=0.0, plan_rect_ft=[10.0, -side, 10.0 + side, 0.0])
    north = dict(base, x_ft=11.0 + side / 2, y_ft=D, plan_rect_ft=[11.0, D, 11.0 + side, D + side])
    for face, near, far in (("S", south, north), ("N", north, south)):
        el["roof_record"]["chimneys"]["positions"] = [copy.deepcopy(near), copy.deepcopy(far)]
        marks = EL.stack_marks(el, face)["marks"]
        assert len(marks) == 2, ("the premise: the far stack is not hidden", face, len(marks))
        assert marks[-1]["stack"]["y_ft"] == near["y_ft"] and marks[-1]["relation"] == "front", \
            (face, [(m["relation"], m["stack"]["y_ft"]) for m in marks])


@pytest.mark.parametrize("side", ["west-of-the-ridge", "east-of-the-ridge"])
def test_an_interior_stack_under_a_ridge_along_y_stands_at_its_extent_and_shows_more_on_its_side(west, side):
    """Auditor E (C2e, C2g): on a ridge along y the long faces are E and W, and an INTERIOR stack's
    outline was guarded by nothing -- reading its extent off x, or taking E for the low face, so
    that each long face measured the roof in front of the stack from the other's eave, left every
    test green. No shipped record has an interior stack, so one is DRIVEN into the west-entered
    Tidewater, a stack's width off the ridge on either side. On each long face it is drawn across
    its own plan extent along the face (y), and it shows lower on its own side of the ridge, where
    only the slope up to it stands in front, than across the ridge, where the ridge does -- or it
    is hidden there."""
    el = copy.deepcopy(west)
    assert el["roof_record"]["main"]["ridge"]["axis"] == "y", "the premise: a ridge along y"
    fp = el["footprint"]
    W, D = fp["width_ft"], fp["depth_ft"]
    proto = el["roof_record"]["chimneys"]["positions"][0]
    w = proto["plan_rect_ft"][2] - proto["plan_rect_ft"][0]
    x0 = 8.0 if side == "west-of-the-ridge" else W - 8.0 - w
    rect = (x0, D / 2 - w / 2, x0 + w, D / 2 + w / 2)
    assert rect[2] < W / 2 or rect[0] > W / 2, "the premise: the square stands off the ridge"
    el["roof_record"]["chimneys"]["positions"] = [
        dict(copy.deepcopy(proto), plan_rect_ft=list(rect), x_ft=x0 + w / 2, y_ft=D / 2, side="interior")]
    feet = {}
    for face in ("E", "W"):
        sm = EL.stack_marks(el, face)
        if not sm["marks"]:
            assert sm["hidden"] == 1, (face, sm)
            feet[face] = None
            continue
        (mk,) = sm["marks"]
        assert mk["relation"] == "interior", (face, mk["relation"])
        us = [u for u, _h in mk["outline"]]
        want = sorted(EL.face_u_outside(face, a, fp) for a in (rect[1], rect[3]))
        assert abs(min(us) - want[0]) < 1e-6 and abs(max(us) - want[1]) < 1e-6, (face, us, want)
        feet[face] = min(h for _u, h in mk["outline"])
    own, far = ("W", "E") if side == "west-of-the-ridge" else ("E", "W")
    assert feet[own] is not None and (feet[far] is None or feet[own] < feet[far] - 1e-6), feet


# ------------------------------------------------------------------ auditor C's W1 and W2, auditor D's D10
T3_PLANS = ("bad-01-grilling-porch-ranch", "bad-02-flex-room-craftsman", "bad-05-two-story-spec-colonial",
            "bad-07-octagon-dinette-colonial", "good-02-portico-library-house",
            "good-04-rambling-porch-farmhouse", "good-06-dogtrot-farmhouse-sketch")


def test_every_shipped_section_carries_its_roof_records_judgment_and_says_it(corpus):
    """Auditor C (W1): the test C9 was guarded by wrote the judgment reading into the very section
    record it then read, so deleting its producer -- `structure.roof_heights`' `form_reading` -- left
    it green while the seven shipped sections that print T3 off it would all have stopped. Read here
    off the shipped sections, unpatched: each section's reading is its roof record's, and every one
    whose roof is drawn from a judgment prints the sentence whole. The premise is the seven."""
    said = []
    for pid, (_q, sec, rf, _el) in sorted(corpus.items()):
        if sec is None or rf is None or "error" in rf:
            continue
        assert sec["roof"].get("form_reading") == rf.get("form_reading"), pid
        words = DI.roof_form_judgment(rf)
        assert DI.roof_form_judgment(sec["roof"]) == words, pid
        if words:
            inked = " ".join(" ".join((t or "").split()) for t, _a, _it in IR.Ink(_svg(RS.render_section, sec)).texts())
            assert " ".join(words.split()) in inked, pid
            said.append(pid)
    assert tuple(said) == tuple(sorted(T3_PLANS)), said


def test_the_section_dxf_says_t3(corpus, tmp_path):
    """Auditor C (W1): the section DXF's T3 note was deletable with every test green. SPLIT 3 OCT
    2026 from the IFC half below, which had skipped it: this half needs ezdxf, which CI installs,
    and the IFC half ifcopenshell, which CI does not, so while the two shared one body CI judged
    neither."""
    ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    DX = _m("export_dxf")
    checked = 0
    for pid in T3_PLANS:
        _q, sec, rf, _el = corpus[pid]
        words = " ".join(DI.roof_form_judgment(rf).split())
        path = str(tmp_path / f"{pid}.dxf")
        assert "error" not in DX.export_section_dxf(sec, path)
        assert words in [" ".join(e.plain_text().split()) for e in ezdxf.readfile(path).modelspace().query("MTEXT")], pid
        checked += 1
    assert checked == len(T3_PLANS) >= 3


def test_the_ifc_says_t3_and_why_it_places_no_planes(corpus, tmp_path):
    """Auditor C (W1): the IFC's `form_judgment` was deletable with every test green. Auditor D
    (D10), and its second occurrence found sweeping for it: the IFC's roof said "form 'X' is not
    modelled by WP-5.1 (gable planes only)" of every roof that drew no planes -- of a side gable
    whose ridge is merely unjudged, a form it does model, and of a roof B8 refuses as "form 'None'".
    The unjudged case is the shipped one: each IFC says the ridge. Judged only where ifcopenshell
    is installed, which CI's jobs are not."""
    ios = pytest.importorskip("ifcopenshell", reason="COULD NOT EVALUATE: ifcopenshell is not installed")
    import ifcopenshell.util.element as uel
    EI = _m("export_ifc")
    checked = 0
    for pid in T3_PLANS:
        q, _sec, rf, _el = corpus[pid]
        words = " ".join(DI.roof_form_judgment(rf).split())
        ifc = str(tmp_path / f"{pid}.ifc")
        res = EI.export_ifc(copy.deepcopy(q), ifc, geometry_result=copy.deepcopy(q))
        if "error" in res:
            continue
        roofs = ios.open(ifc).by_type("IfcRoof")
        assert len(roofs) == 1, pid
        ps = uel.get_psets(roofs[0]).get("TDL") or {}
        assert " ".join((ps.get("form_judgment") or "").split()) == words, pid
        if (rf["main"].get("ridge") or {}).get("grade_to_ridge_ft") is None:
            assert ps["geometry_note"].startswith(f"the {rf['main']['form']} roof's planes are not placed "
                                                  f"because its ridge is not judged"), (pid, ps["geometry_note"][:90])
        checked += 1
    assert checked >= 3, ("the premise: the IFC exports these houses", checked)


def test_every_ifc_placement_goes_through_the_one_helper_that_states_the_unit():
    """X1's source half: one call of `geometry.edit_object_placement`, passing `is_si=False`. Three
    helpers each spelling the call is how the audit of Phase 14's fix reached `_placement` and not
    the two rotated placements the roof planes go through. MOVED 3 OCT 2026 out of
    `tests/test_ifc_openings_are_the_sheets.py`, which skips whole where ifcopenshell is not
    installed -- every CI job -- so this test, which reads the source and needs no library, was
    judged nowhere CI runs."""
    import ast
    src = open(os.path.join(ROOT, "build", "export_ifc.py"), encoding="utf-8").read()
    calls = []
    for node in ast.walk(ast.parse(src)):
        if (isinstance(node, ast.Call) and node.args and isinstance(node.args[0], ast.Constant)
                and node.args[0].value == "geometry.edit_object_placement"):
            calls.append({k.arg: k.value for k in node.keywords})
    assert len(calls) == 1, f"{len(calls)} calls of the placement API; route them through _place_matrix"
    flag = calls[0].get("is_si")
    assert isinstance(flag, ast.Constant) and flag.value is False, "the one call must state is_si=False"


def test_the_section_is_cut_across_the_span_its_ridge_was_raised_over_on_every_surface(corpus, tmp_path):
    """Auditor C (W2): C1 made the section span `threshold.ridge_span`'s, stated on the record as
    `span_ft`, and the guard held the RECORD; the sheet and the DXF could each go back to the
    footprint's shorter side with every test green. good-03 is the house where the two differ -- a
    side gable entered on its narrow front, its ridge raised over the long dimension -- and the
    sheet's own SPAN figure and the DXF's walls are held to the record there."""
    ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    _q, sec, _rf, _el = corpus["good-03-parlor-drawing-room-house"]
    fp, span = sec["footprint"], sec["roof"]["span_ft"]
    assert abs(span - min(fp["width_ft"], fp["depth_ft"])) > 1.0, "the premise: the span is not the shorter side"
    svg = _svg(RS.render_section, sec)
    assert f"SPAN {RS._fmt(span)}" in svg and f"SPAN {RS._fmt(min(fp['width_ft'], fp['depth_ft']))}" not in svg
    DX = _m("export_dxf")
    path = str(tmp_path / "g03.dxf")
    assert "error" not in DX.export_section_dxf(sec, path)
    xs = [x for e in ezdxf.readfile(path).modelspace().query("LINE") if e.dxf.layer == "TDL-SECT-WALL"
          for x in (e.dxf.start[0], e.dxf.end[0])]
    assert xs and abs(max(xs) - min(xs) - span * 12.0) < 0.01, (min(xs), max(xs), span * 12.0)


# ------------------------------------------------------------------ auditor D's D6: a banned stack on any roof
@pytest.mark.parametrize("roof", ["hip", "unjudged", "side-gable"])
def test_a_banned_stack_is_refused_for_its_ban_on_every_roof(roof, monkeypatch):
    """Auditor D (D6): the roof read the placement's ban AFTER its unjudged-ridge and hip returns,
    so on those roofs the plan sheet said the kit forbids the stacks and the roof plan, the scene
    and the elevation said the roof is a hip, or judges no ridge. Driven as C3's test drives the
    ban (new-england-colonial forbidding the exterior stack), on a hip, on a side gable whose ridge
    is unjudged, and on the judged side gable that is the control: one reason, the ban, on the
    roof record every one of those surfaces prints."""
    TH = _m("threshold")
    slots = copy.deepcopy(TH.resolved_slots("tidewater-georgian"))
    hp = slots.setdefault("hearth_position", {"binding": "specified", "variants": []})
    hp["variants"] = [v for v in hp.get("variants") or [] if v.get("id") != "exterior-end"] + [
        {"id": "exterior-end", "status": "forbidden", "_written_by": "new-england-colonial"}]
    monkeypatch.setattr(TH, "resolved_slots", lambda style: slots)
    if roof == "unjudged":
        monkeypatch.setattr(ST, "_style_roof_pitch", lambda style: (None, None, None))
        monkeypatch.setattr(RF, "_style_roof_pitch", lambda style: (None, None, None))
    with open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json"), encoding="utf-8") as fh:
        plan = json.load(fh)
    if roof == "hip":
        plan.setdefault("declared", {})["roof_form"] = "hip"
    monkeypatch.setattr(G, "_SOLVE_CACHE", {})
    q = G.solve(plan, None, 250, engine="heuristic")
    assert q["hearths"]["stacks"] == [], "the premise: the placer refused the stacks"
    sec = ST.build_section(q, None, geometry_result=q)
    rf = RF.build_roof(q, None, section=sec)
    main = rf["main"]
    assert (main["form"] == "hip") == (roof == "hip"), "the premise: the roof drawn"
    assert (main["ridge"].get("grade_to_ridge_ft") is None) == (roof == "unjudged"), "the premise: the ridge"
    ch = rf["chimneys"]
    assert ch["positions"] == [] and ch.get("refused_by"), ch
    assert "new-england-colonial's kit" in ch["note"], ch["note"]
    assert "the roof form here is" not in ch["note"] and "no judged ridge" not in ch["note"], ch["note"]
    el = EL.build_elevation(q, None, section=sec, roof=rf)
    SC = _m("scene")
    said = [n for n in SC.build_scene(q, sec, rf, el)["not_modelled"] if n["what"] == "the chimney stacks"]
    assert said and "new-england-colonial's kit" in said[0]["why"], said


# ------------------------------------------------------------------ auditor D's D11: an unstated projection
def test_the_dxf_says_a_bands_unstated_projection_is_unstated(corpus, tmp_path):
    """Auditor D (D11): `band_marks` draws a band whose record states no projection flush, at 0.0,
    and the DXF wrote that 0.0 into the band's XDATA as though the record had stated it -- the
    Tidewater belt, whose record states none. The data says unstated now; a stated projection is
    written as stated (the water table, the control)."""
    ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    _q, _s, _r, el = corpus["tidewater-georgian-careful"]
    wtb = el["water_table_belt"]
    assert wtb["belt_course_projection_in"] is None and wtb["water_table_projection_in"] is not None, \
        "the premise: the belt states no projection and the water table states one"
    path = str(tmp_path / "e.dxf")
    assert "error" not in _m("export_dxf").export_elevation_dxf(el, path, face="S")
    got = {}
    for e in ezdxf.readfile(path).modelspace().query("LWPOLYLINE"):
        if e.dxf.layer == "TDL-ELEV-BAND" and e.has_xdata("TDL"):
            tags = [v for _c, v in e.get_xdata("TDL")]
            if tags and tags[0] == "TDL::band":
                rec = json.loads("".join(tags[1:]))
                got[rec["band"]] = rec
    assert set(got) == {"water table", "belt course"}, sorted(got)
    assert got["belt course"]["projection_in"] is None and "states no projection" in got["belt course"]["projection_note"]
    assert got["water table"]["projection_in"] == pytest.approx(wtb["water_table_projection_in"])
    assert "projection_note" not in got["water table"]


# ------------------------------------------------------------------ auditor D's D7 (= B's B8): the scene's lights
def test_the_scene_says_a_forbidden_light_pattern_as_the_sheet_says_it(corpus):
    """Auditor D (D7): the sheet and the DXF say a sash light pattern the kit forbids (A4), and
    the scene drew the bars of the same pattern -- 140 of them on the Tidewater restyled
    cape-cod-revival, whose kit forbids 12/12 -- and said nothing. One reader now
    (`elevation.forbidden_lights`): the scene's judgment carries the face note's own sentence. The
    shipped kit is the control, and a ban on the whole slot (`"*"`, which no style writes today)
    is driven: it reaches every pattern drawn."""
    SC = _m("scene")
    q, sec, rf, _el = corpus["tidewater-georgian-careful"]
    el = _restyled(corpus, "tidewater-georgian-careful", "cape-cod-revival")
    assert "12/12" in el["lite_patterns_forbidden"], "the premise: the kit forbids 12/12"
    notes = {n for f in FACES for n in EL.face_notes(el, f) if n.startswith("LIGHTS DRAWN 12/12")}
    assert len(notes) == 1, notes
    q2 = dict(q, style="cape-cod-revival")
    said = [j for j in SC.build_scene(q2, sec, rf, el)["judgment"] if j["what"] == "the 12/12 sash lights"]
    assert said and said[0]["why"] in notes, said
    ctl = SC.build_scene(q, sec, rf, corpus["tidewater-georgian-careful"][3])
    assert not [j for j in ctl["judgment"] if j["what"].endswith("sash lights")], "the control's kit forbids none"
    whole = copy.deepcopy(corpus["tidewater-georgian-careful"][3])
    whole["lite_patterns_forbidden"] = {"*": el["lite_patterns_forbidden"]["12/12"]}
    drawn = {r["sash_pattern"] for f in FACES for r in EL.opening_rects(whole, f)["rects"]
             if r.get("kind") == "window" and r.get("sash_pattern")}
    got = {pt for f in FACES for pt, _w in EL.forbidden_lights(whole, EL.opening_rects(whole, f)["rects"])}
    assert drawn and got == drawn, (drawn, got)


# ------------------------------------------------------------------ auditor B's B9 (= D's D9c): a pitched gambrel's section
def test_a_gambrels_section_raises_no_single_pitch_ridge_and_quotes_true_on_the_scene(corpus):
    """Auditors B (B9) and D (D9c): C8 made the section say a gambrel's ridge is the roof record's,
    for the gambrel with no migrated pitch it was written for; on a style that migrates one, the
    section still raised a gable ridge at it -- 38.72 ft, labelled 8.0:12 -- under that sentence,
    while the roof record put the gambrel's ridge at 56.71. And the scene quotes the section's note,
    so its datum entry said "this section does not draw it" of a model. Driven: the Tidewater
    declared a gambrel. The section states no ridge and says whose it is, in words true wherever
    they are quoted; good-01's unpitched gambrel is the control."""
    SC = _m("scene")
    q, _sec, _rf, _el = corpus["tidewater-georgian-careful"]
    q = copy.deepcopy(q)
    q.setdefault("declared", {})["roof_form"] = "gambrel"
    sec = ST.build_section(q, None, geometry_result=q)
    rf = RF.build_roof(q, None, section=sec)
    assert rf["main"]["form"] == "gambrel" and rf["main"]["ridge"]["grade_to_ridge_ft"], "the premise"
    assert ST._style_roof_pitch(q["style"])[0] is not None, "the premise: the style migrates a pitch"
    r = sec["roof"]
    assert r["grade_to_ridge_ft"] is None and "roof record" in r["note"], r
    svg = _svg(RS.render_section, sec)
    assert "RIDGE 38" not in svg and "8.0:12" not in svg
    el = EL.build_elevation(q, None, section=sec, roof=rf)
    said = [n for n in SC.build_scene(q, sec, rf, el)["not_modelled"] if n["what"] == "ridge datum"]
    assert said and "this section" not in said[0]["why"].lower(), said
    _q1, sec1, rf1, _el1 = corpus["good-01-veranda-gallery-estate"]
    assert rf1["main"]["form"] == "gambrel" and sec1["roof"]["grade_to_ridge_ft"] is None
    assert "roof record" in sec1["roof"]["note"] and "this section" not in sec1["roof"]["note"]


# ------------------------------------------------------------------ auditor D's suspect S2: a windowless room's advice
@pytest.mark.parametrize("rule, says, not_says", [
    ("pier", "(R5)", "Free that run"),
    ("alignment", "(R6)", "or narrow the window"),
    (None, "the run there is taken by what the refusal names. Free that run, or narrow the window.", "(R5)")])
def test_a_windowless_rooms_advice_follows_the_rule_that_refused_its_window(corpus, rule, says, not_says):
    """Auditor D (suspect S2): a room whose windows are all refused on a wall it stands on was told
    "the run there is taken by what the refusal names. Free that run, or narrow the window." For a
    unit refused for the pier between windows (R5) nothing takes the run, and for one refused for
    the axis below (R6) narrowing does not move an axis. Every windowless room on the shipped plans
    is a run refusal, so the other two are driven: the spec Colonial's dining room, its W windows
    all refused by each rule in turn, and the run refusal the control, its sentence unchanged."""
    q = copy.deepcopy(corpus["spec-builder-colonial"][0])
    room = next(r for lv in q["levels"] for r in lv["rooms"] if r["id"] == "dining")
    assert room["windows"] and all(w.get("wall") == "W" for w in room["windows"]), "the premise"
    for w in room["windows"]:
        w.pop("positions_ft", None)
        w["unplaced"] = dict({"reason": "driven"}, **({"rule": rule} if rule else {}))
    found = [x for x in _m("plan_check").check(q)["findings"]
             if x.get("kind") == "drawn-window-off-the-placed-wall" and x.get("room") == "dining"]
    assert len(found) == 1 and "W" in found[0]["lit_walls"], found
    assert says in found[0]["fix"] and not_says not in found[0]["fix"], found[0]["fix"]


# ------------------------------------------------------------------ auditor B's B12, A's F5 (= D's D9a): the hips
def _slopes(prof):
    """Every sloping segment's rise over run, of a face profile."""
    return [round((h1 - h0) / (u1 - u0), 4) for (u0, h0), (u1, h1) in zip(prof, prof[1:])
            if abs(u1 - u0) > 1e-6 and abs(h1 - h0) > 1e-6]


@pytest.mark.parametrize("pid, style, form", [
    ("bad-04-log-cabin", "french-neoclassical", "hip"),
    ("tidewater-georgian-careful", "tidewater-georgian", "gable-on-hip")])
def test_a_hipped_roof_rises_at_its_stated_pitch_on_every_face_whatever_its_footprint(corpus, pid, style, form):
    """Auditor B (B12): a hip on a house deeper than it is wide had its ridge read along x, left no
    length between the hips, and collapsed it to a point -- a vertical edge at the west corner of the
    S face, the E and W faces rising at 0.311 under a 0.542 label -- and B1 hips the composer's
    Georgian candidates, three of whose 110 roofs are deeper than wide. Auditors A and D (F5, D9a):
    a gable-on-hip's ridge ran along y whatever the footprint, so the Tidewater declared one drew its
    S and N faces at 6.70:12 under 8.0:12. Driven on both: the ridge runs along the longer dimension,
    stops half the span short of each end, and every sloping segment of every face rises at the
    stated pitch."""
    q, _s, _r, _el = corpus[pid]
    q = copy.deepcopy(q)
    q["style"] = style
    q.setdefault("declared", {})["roof_form"] = form
    sec = ST.build_section(q, None, geometry_result=q)
    rf = RF.build_roof(q, None, section=sec)
    m = rf["main"]
    W, D = sec["footprint"]["width_ft"], sec["footprint"]["depth_ft"]
    assert m["form"] == form and m.get("pitch_rise_per_12"), "the premise: a pitched hip"
    assert (W < D) == (form == "hip"), "the premise: the deep footprint and the wide one"
    r = m["ridge"]
    long_, short = max(W, D), min(W, D)
    assert r["axis"] == ("x" if W >= D else "y")
    assert r["from_ft"] == pytest.approx(short / 2, abs=0.01) and r["to_ft"] == pytest.approx(long_ - short / 2, abs=0.01)
    want = round(m["pitch_rise_per_12"] / 12.0, 4)
    for face, prof in rf["elevation_profiles"].items():
        sl = _slopes(prof)
        assert sl and all(abs(abs(x) - want) < 0.002 for x in sl), (face, sl, want)


# ------------------------------------------------------------------ auditor C's M1: the rake's reasons
_DRAWN = __import__("re").compile(r"\bdraw(?:n|s)?\b")
_OF = __import__("re").compile(r"\b(?:rake|return)s?\b")
_HELD = __import__("re").compile(r"\b(?:where|no|not|none)\b")


def test_no_standing_reason_says_a_rake_or_a_return_is_drawn_on_every_house():
    """Auditor C (M1): A3 rewrote the rake's standing reasons because "the rake is drawn to The
    Cardboard Gable's own figures" was false on eight of the ten shipped gable-end plans, and the
    test it left asserted only that the key exists -- restoring the false sentence stayed green. A
    standing reason is read on every house, so each clause of it that says a rake or a return is
    drawn says where (or says none is): the rake's three and the return's two, D1's class one
    reading wider than its first guard."""
    import re
    names = EL.RAKE_NAMES + EL.RETURN_NAMES
    clauses = 0
    for n in names:
        for clause in re.split(r";|, and |\bas \w+ --", EL.NOT_MODELLED[n]):
            if _OF.search(clause) and _DRAWN.search(clause):
                clauses += 1
                assert _HELD.search(clause), (n, clause.strip())
    assert clauses >= len(names), ("the premise: every reason speaks of what is drawn", clauses)


def _rake_house(monkeypatch, reading=None, roof_form="as-stated", kit_roof=None):
    """The Tidewater house built whole, with the rake's reading driven where `reading` is given, its
    declared roof form replaced (None drops it), and its kit's `roof_form` driven where `kit_roof` is
    given -- through each reader's own seam, so the reason reaches `front.withheld` the way the
    corpus's do."""
    TH = _m("threshold")
    with open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json"), encoding="utf-8") as fh:
        plan = json.load(fh)
    if roof_form != "as-stated":
        plan.setdefault("declared", {}).pop("roof_form", None)
        if roof_form:
            plan["declared"]["roof_form"] = roof_form
    if kit_roof is not None:
        rec = {"binding": "specified", "_bound_by": plan["style"], "variants": kit_roof}
        monkeypatch.setitem(TH._RESOLVED, plan["style"],
                            dict(TH.resolved_slots(plan["style"]) or {}, roof_form=rec))
    if reading is not None:
        monkeypatch.setattr(EL.RK, "rake_at", lambda rec, date=None: dict(reading))
    _q, _sec, rf, el = _built(plan)
    return rf, el


def _bands(el):
    return [b for f in FACES if f in (el.get("faces") or {}) for b in EL.rake_marks(el, f)["bands"]]


@pytest.mark.parametrize("case", ["undrawn-form", "refused"])
def test_a_house_drawing_no_roof_says_its_rake_is_not_drawn_for_that_reason(monkeypatch, case):
    """Auditor C (M1): `rake_withheld`'s first branch -- no gable end because the roof is a form
    this generator does not draw, or is refused (B8) -- was reached by no shipped plan, and silencing
    it stayed green. Driven both ways: a declared mansard, and B8's refusal of a fallback the kit
    forbids (test_roof_form's own drive). Each says its own cause on all three figures."""
    if case == "undrawn-form":
        rf, el = _rake_house(monkeypatch, roof_form="mansard")
        cause = "roof form (mansard) is one this generator does not draw"
    else:
        rf, el = _rake_house(monkeypatch, roof_form=None, kit_roof=[
            {"id": "mansard", "status": "canonical", "_written_by": "tidewater-georgian"},
            {"id": "side-gable", "status": "forbidden", "_written_by": "w-writer"}])
        cause = "no roof is drawn on this house (B8)"
    assert EL.gable_faces(rf) is None and bool(rf["main"].get("refused")) == (case == "refused"), \
        "the premise: no gable end, for the reason the case names"
    assert not _bands(el)
    held = el["front"].get("withheld") or {}
    for n in EL.RAKE_NAMES:
        assert cause in held.get(n, "") and "no rake with it" in held[n], (n, held.get(n, "")[:120])
    # and the return's two figures say the same cause (`return_withheld`'s first branch, reached by
    # no shipped plan either: the audit of WP-16.8's own diff, a mutation silencing it stayed green)
    for n in EL.RETURN_NAMES:
        assert cause in held.get(n, "") and "no return with it" in held[n], (n, held.get(n, "")[:120])


def test_a_house_whose_kit_refuses_its_cornice_says_its_gable_ends_have_no_return(monkeypatch):
    """`return_withheld`'s third branch -- no eave cornice drawn, so no return to draw -- was reached
    by no shipped plan, and silencing it stayed green (the audit of WP-16.8's own diff). Driven on
    the Tidewater, its cornice forbidden whole in the resolved kit (WP-16.4's refusal, in private
    caches): its gable ends stand, and both return figures say why they are not drawn."""
    for mod, name in ((_m("threshold"), "_RESOLVED"), (_m("window_pier"), "_CACHE"),
                      (_m("plan_check"), "_RESOLVED_SLOTS")):
        monkeypatch.setattr(mod, name, {})
    real = EL.RK.resolve_slots

    def forbidding(graph, chain, scope=None):
        slots, rest = real(graph, chain, scope)
        return {**slots, "cornice": {**(slots.get("cornice") or {}), "binding": "forbidden",
                                     "_bound_by": "w-writer", "variants": []}}, rest
    monkeypatch.setattr(EL.RK, "resolve_slots", forbidding)
    _rf, el = _rake_house(monkeypatch)
    cr = el["cornice_return"]
    assert el["eave_cornice"].get("cornice_refused_by") and cr["draws"] == "nothing" and cr["gable_faces"], \
        "the premise: the cornice is refused and the gable ends stand"
    held = el["front"].get("withheld") or {}
    for n in EL.RETURN_NAMES:
        assert held.get(n) == "no eave cornice is drawn on this house, so its gable ends have no return to draw", \
            (n, held.get(n))


def test_a_gable_end_drawing_the_roofs_edge_quotes_the_sheet_on_every_figure(monkeypatch):
    """Auditor C (M1): the edge branch -- a kit that forbids the rake, or states one this generator
    does not draw -- was reached by no shipped plan. Driven: the Tidewater's own gable ends, under a
    ban on the rake. The reason quotes the sentence the gable face prints, on all three figures."""
    rf, el = _rake_house(monkeypatch, reading={"state": "forbidden", "writers": ["w-writer"],
                                               "variant": "boxed-rake-with-return"})
    gf = EL.gable_faces(rf)
    assert gf and el["rake"]["draws"] == "edge" and not _bands(el), "the premise: gable ends, no member"
    words = el["rake"]["words"]
    assert words and all(words in EL.face_notes(el, f) for f in gf), "the sheet says it on each gable end"
    held = el["front"].get("withheld") or {}
    for n in EL.RAKE_NAMES:
        assert "draws the roof's edge and no rake member" in held.get(n, "") and words in held[n], n


def test_a_plain_trim_withholds_only_its_projection_and_names_whose_trim_it_is(monkeypatch):
    """Auditor C (M1): the plain branch -- a kit's own plain trim, drawn, states no projection from
    the wall -- was reached by no shipped plan. Driven on the Tidewater, whose roof judges a ridge,
    so the trim is drawn: the projection is withheld naming the kit, and the overhang and the member
    count keep their standing reasons alone, as a drawn rake's do."""
    rf, el = _rake_house(monkeypatch, reading={
        "state": "plain", "writers": ["w-writer"], "trim_in": 5.5, "trim_by": "w-writer",
        "trim_basis": "a driven trim", "trim_measured": True})
    assert el["rake"]["draws"] == "plain" and _bands(el), "the premise: the plain trim is drawn"
    held = el["front"].get("withheld") or {}
    proj = "rake_member_projection_from_siding_face_in"
    assert "w-writer's own plain trim" in held.get(proj, "") and "states no projection" in held[proj]
    assert not [n for n in EL.RAKE_NAMES if n != proj and n in held], held


# ------------------------------------------------------------------ auditor C's M3: the scene's bands
def _envelope_lines(el, scene):
    """The envelope lines the scene states, and the lines the elevation's own marks call for --
    `cornice_marks` and `band_marks`, the spellings the sheet and the DXF draw from."""
    said = {n["what"] for n in scene["not_modelled"] if n.get("class") == "envelope"}
    marks = [EL.cornice_marks(el, f) for f in el["faces"]]
    bm = EL.band_marks(el)
    want = {name for name, drawn in (
        ("the eave cornice", any(cm.get("cornice") for cm in marks)),
        ("the frieze under the eave cornice", any(cm.get("frieze") for cm in marks)),
        ("the cornice returns at the gable ends",
         any(r.get("cornice") or r.get("frieze") for cm in marks for r in cm.get("returns") or [])),
        ("the cornice's end profiles at the gable corners", any(cm.get("end_profiles") for cm in marks)),
        ("the water table", bool(bm["water_table"])),
        ("the belt course", bool(bm["belt"]))) if drawn}
    return said, want


def test_the_scene_names_every_band_the_elevation_draws_and_no_other(corpus):
    """Auditor C (M3): C6's test read two of the six lines `_envelope_bands` states, and deleting the
    frieze's line (eleven shipped scenes) or the returns' (the Tidewater and good-03) stayed green.
    Every shipped plan's scene, each line in both directions against the elevation's own marks, and
    each of the four reached lines asserted to occur."""
    SC = _m("scene")
    seen = {}
    for pid, (q, sec, rf, el) in sorted(corpus.items()):
        if el is None or "error" in el or not el.get("applicable", True):
            continue
        said, want = _envelope_lines(el, SC.build_scene(q, sec, rf, el))
        assert said == want, (pid, sorted(said ^ want))
        for w in want:
            seen[w] = seen.get(w, 0) + 1
    for line in ("the eave cornice", "the frieze under the eave cornice",
                 "the cornice returns at the gable ends", "the water table"):
        assert seen.get(line), ("the premise: a shipped scene states", line, seen)


@pytest.mark.parametrize("case", ["end-profiles", "no-water-table"])
def test_the_scene_follows_the_drawing_where_no_shipped_plan_reaches(corpus, monkeypatch, case):
    """Auditor C (M3): no shipped plan draws the cornice's end profiles (a kit that forbids its
    return or makes none canonical), and every shipped plan draws a water table, so deleting the
    end profiles' line, or stating the water table on every house, stayed green. Driven on the
    Tidewater: its gable ends under a ban on the return, and its water table forbidden whole in the
    resolved kit (test_kit_refusal's drive, in private caches)."""
    SC = _m("scene")
    q, sec, rf, _el = corpus["tidewater-georgian-careful"]
    if case == "end-profiles":
        monkeypatch.setattr(EL.RK, "return_at", lambda rec, date=None: {
            "state": "forbidden", "writers": ["w-writer"], "variant": None, "band_in": None,
            "dated": [], "date": date, "date_unstated": False})
    else:
        for mod, name in ((_m("threshold"), "_RESOLVED"), (_m("window_pier"), "_CACHE"),
                          (_m("plan_check"), "_RESOLVED_SLOTS")):
            monkeypatch.setattr(mod, name, {})
        real = EL.RK.resolve_slots

        def forbidding(graph, chain, scope=None):
            slots, rest = real(graph, chain, scope)
            return {**slots, "water_table": {**(slots.get("water_table") or {}), "binding": "forbidden",
                                             "_bound_by": "somebody", "variants": []}}, rest
        monkeypatch.setattr(EL.RK, "resolve_slots", forbidding)
    el = EL.build_elevation(q, None, section=sec, roof=rf)
    said, want = _envelope_lines(el, SC.build_scene(q, sec, rf, el))
    if case == "end-profiles":
        assert el["cornice_return"]["draws"] == "end-profile", "the premise: the gable ends draw end profiles"
        assert "the cornice's end profiles at the gable corners" in want, "the premise, from the marks"
    else:
        assert el["water_table_belt"].get("water_table_refused_by"), "the premise: the drive landed"
        assert "the water table" not in want, "the premise: no water table is drawn"
    assert said == want, sorted(said ^ want)


# ------------------------------------------------------------------ auditor C's M4: the bands, sheet to DXF
def test_the_dxf_draws_the_bands_and_the_member_lines_the_sheet_draws(corpus, tmp_path):
    """Auditor C (M4): the DXF's band test built what it wanted from `band_marks`, the function the
    DXF draws from, while the sheet reads `band_marks` only for WHETHER a band is drawn and computes
    WHERE itself -- and deleting the water table's member lines from the DXF stayed green. Here the
    sheet's own ink is the reference, read back to the face's inches through its plate's frame
    (census X4's method): every band rectangle and every member line, on every face of every
    shipped plan, against the DXF's band layer."""
    ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    DX = _m("export_dxf")
    seen = {"faces": 0, "boxes": 0, "lines": 0}

    def close(a, b):
        return len(a) == len(b) and all(max(abs(x - y) for x, y in zip(p, q)) <= 0.15
                                        for p, q in zip(sorted(a), sorted(b)))
    for pid, (_q, _sec, _rf, el) in sorted(corpus.items()):
        if el is None or "error" in el or not el.get("applicable", True):
            continue
        for face in FACES:
            if face not in (el.get("faces") or {}):
                continue
            ink = IR.Ink(_svg(RE.render_elevation, el, face=face))
            pl = next((p for p in ink.frames() if p.get("proj") == "elevation"), None)
            assert pl, (pid, face, "the plate states no frame")

            def inch(x, y):
                u, v = IR.to_model(pl, x, y)
                return u * 12.0, v * 12.0
            want_boxes, want_lines = [], []
            for it in ink.items:
                if it.tag == "rect" and "wt" in it.classes:
                    b = it.bbox()
                    (u0, v0), (u1, v1) = inch(b[0], b[3]), inch(b[2], b[1])
                    want_boxes.append((min(u0, u1), min(v0, v1), max(u0, u1), max(v0, v1)))
            # `wtm` styles two kinds of line on the sheet: a band's member divisions, and the
            # frieze's top where the cornice springs (`render_elevation`); a band's are the ones
            # standing inside a band the sheet draws
            for it in ink.items:
                if "wtm" in it.classes:
                    (a0, h0), (a1, h1) = inch(*it.points(n=1)[0]), inch(*it.points(n=1)[-1])
                    if any(b[1] - 0.15 <= h0 <= b[3] + 0.15 for b in want_boxes):
                        want_lines.append((h0, h1, min(a0, a1), max(a0, a1)))
            path = str(tmp_path / f"{pid}-{face}.dxf")
            DX.export_elevation_dxf(el, path, face=face)
            msp = ezdxf.readfile(path).modelspace()
            got_boxes, got_lines = [], []
            for e in msp.query("LWPOLYLINE"):
                if e.dxf.layer == "TDL-ELEV-BAND":
                    xs, ys = [p[0] for p in e.get_points()], [p[1] for p in e.get_points()]
                    got_boxes.append((min(xs), min(ys), max(xs), max(ys)))
            for e in msp.query("LINE"):
                if e.dxf.layer == "TDL-ELEV-BAND":
                    (a0, h0), (a1, h1) = (e.dxf.start[0], e.dxf.start[1]), (e.dxf.end[0], e.dxf.end[1])
                    got_lines.append((h0, h1, min(a0, a1), max(a0, a1)))
            assert close(want_boxes, got_boxes), (pid, face, sorted(want_boxes), sorted(got_boxes))
            assert close(want_lines, got_lines), (pid, face, len(want_lines), len(got_lines))
            seen["faces"] += 1
            seen["boxes"] += len(want_boxes)
            seen["lines"] += len(want_lines)
    assert seen["boxes"] > seen["faces"] >= 16 and seen["lines"] >= 1, \
        ("the premise: bands on every face, a belt somewhere, member lines somewhere", seen)



# ------------------------------------------------------------------ auditor E's C7c: the panels each leaf carries
def _leaves_of(r):
    """The two leaves the RECORD hangs beside a window, from the rect's own fields and not from
    `elevation.shutter_leaves`, which is the subject: each a leaf's width outboard of its jamb,
    hung from the head down its own height."""
    w, h, head = r["shutter_leaf_width_in"], r["shutter_leaf_height_in"], r["head_in"]
    return [(r["x0_in"] - w, head - h, r["x0_in"], head), (r["x1_in"], head - h, r["x1_in"] + w, head)]


def _inside(b, box, tol=0.05):
    return (box[0] - tol <= b[0] and b[2] <= box[2] + tol
            and box[1] - tol <= b[1] and b[3] <= box[3] + tol)


def test_every_leaf_on_the_sheet_and_in_the_dxf_carries_the_panels_its_record_states(corpus, tmp_path):
    """Auditor E (C7c): WP-16.8 put the leaves and their fielded panels into one spelling,
    `elevation.shutter_leaves`, which the sheet and the DXF both draw -- and making it draw ONE
    panel a leaf whatever the record says left every test green, because the DXF test reads the
    leaves' outlines and nothing read a panel. Here the record's own `shutter_panel_count` is the
    reference, against what each surface draws inside each leaf the record hangs: the sheet's `pnl`
    rects read back to the face's inches through the plate's frame, and the DXF's closed outlines
    on the sash layer. A leaf is placed from the rect's own fields, so the subject's arithmetic is
    in neither the reference nor the matching. The corpus states both counts the panel rule gives
    (2 and 3), so a constant of either would fail somewhere."""
    ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    DX = _m("export_dxf")
    counts, leaves = set(), 0
    for pid, (_q, _sec, _rf, el) in sorted(corpus.items()):
        if el is None or "error" in el or not el.get("applicable", True):
            continue
        for face in FACES:
            if face not in (el.get("faces") or {}):
                continue
            hung = [r for r in EL.opening_rects(el, face)["rects"]
                    if r["kind"] == "window" and r.get("shutter_leaf_width_in")
                    and r.get("shutter_leaf_height_in")]
            if not hung:
                continue
            want = [(box, r["shutter_panel_count"]) for r in hung for box in _leaves_of(r)]
            ink = IR.Ink(_svg(RE.render_elevation, el, face=face))
            pl = next((p for p in ink.frames() if p.get("proj") == "elevation"), None)
            assert pl, (pid, face, "the plate states no frame")

            def inch(it):
                b = it.bbox()
                (u0, v0), (u1, v1) = IR.to_model(pl, b[0], b[3]), IR.to_model(pl, b[2], b[1])
                return (min(u0, u1) * 12.0, min(v0, v1) * 12.0, max(u0, u1) * 12.0, max(v0, v1) * 12.0)
            sheet_leaves = [inch(it) for it in ink.items if it.tag == "rect" and "sh" in it.classes]
            sheet_panels = [inch(it) for it in ink.items if it.tag == "rect" and "pnl" in it.classes]
            path = str(tmp_path / f"{pid}-{face}.dxf")
            DX.export_elevation_dxf(el, path, face=face)
            dxf_boxes = []
            for e in ezdxf.readfile(path).modelspace().query("LWPOLYLINE"):
                if e.dxf.layer == "TDL-ELEV-SASH":
                    xs, ys = [p[0] for p in e.get_points()], [p[1] for p in e.get_points()]
                    dxf_boxes.append((min(xs), min(ys), max(xs), max(ys)))
            assert len(sheet_leaves) == len(want), (pid, face, "leaves drawn", len(sheet_leaves), len(want))
            for box, n in want:
                # the sheet rounds to a tenth of a pixel, so its leaf is matched within half an inch
                drawn = [b for b in sheet_leaves if max(abs(x - y) for x, y in zip(b, box)) <= 0.5]
                assert len(drawn) == 1, (pid, face, box, "the sheet draws no leaf where the record hangs one")
                assert (box[3] - box[1]) / n > 8.0, (pid, face, box, n, "premise: no panel near the sheet's 2 px floor")
                on_sheet = sum(_inside(p, drawn[0], tol=0.5) for p in sheet_panels)
                assert on_sheet == n, (pid, face, box, "panels on the sheet", on_sheet, "the record", n)
                own = [b for b in dxf_boxes if max(abs(x - y) for x, y in zip(b, box)) <= 0.01]
                assert len(own) == 1, (pid, face, box, "the DXF draws no leaf where the record hangs one")
                in_dxf = sum(b != own[0] and _inside(b, box) for b in dxf_boxes)
                assert in_dxf == n, (pid, face, box, "panels in the DXF", in_dxf, "the record", n)
                counts.add(n)
                leaves += 1
    assert counts >= {2, 3} and leaves >= 16, ("the premise: both panel counts drawn, on many leaves", counts, leaves)



# ------------------------------------------------------------------ auditor E's A4b, A4c, A4d: the light bans
def test_a_light_ban_on_the_whole_slot_or_on_one_id_is_read_as_written():
    """Auditor E (A4b, A4d): `lite_patterns_forbidden`'s two other readings had no test. A slot
    forbidden whole bans every pattern and names its writer (A4b: returning nothing there stayed
    green). A row is read by its EXACT id, because `resolve_kit.ban` reads words as substrings and
    asks that every row they match be forbidden, so "1/1" also matches a permitted "11/11" and the
    ban would read as none (A4d: equivalent on the corpus, whose sixteen ids hold no such pair, and
    the docstring's own example of it, "2/2" inside "12/12", was false). Both driven."""
    whole = EL.lite_patterns_forbidden({"binding": "forbidden", "_bound_by": "w-writer", "variants": []})
    assert list(whole) == ["*"] and whole["*"]["writers"] == ["w-writer"] and whole["*"]["whole_slot"]
    rows = [{"id": "1/1", "status": "forbidden", "_written_by": "w-writer"},
            {"id": "11/11", "status": "permitted", "_written_by": "x-writer"}]
    slot = {"binding": "specified", "variants": rows}
    exact = EL.lite_patterns_forbidden(slot)
    assert list(exact) == ["1/1"] and exact["1/1"]["rows"] == ["1/1"], exact
    assert EL.RK.ban(slot, ["1/1"]) is None, "the premise: the substring reading misses the ban"


@pytest.mark.parametrize("case,dated,says", [
    ("whole", True, "LIGHTS DRAWN 12/12 \u2014 FORBIDDEN BY W-WRITER'S KIT;"),
    ("outside", True, None),
    ("inside", True, "FOR HOUSES OF 1700\u20131780, AND THIS HOUSE IS DATED 1765;"),
    ("inside", False, "FOR HOUSES OF 1700\u20131780; THIS RECORD STATES NO DATE, SO THE BAN IS KEPT;")],
    ids=["whole-slot", "dated-outside", "dated-inside", "undated"])
def test_a_light_ban_is_read_at_the_houses_own_date_and_said_on_the_face(corpus, monkeypatch, case,
                                                                         dated, says):
    """Auditor E (A4c): the elevation read the light bans at the house's date, and dropping the
    date at that one call stayed green, because no kit dates a light ban. Driven on the Tidewater
    (dated 1765), which draws 12/12: a ban on the whole slot is said on the face; a 12/12 ban dated
    1800-1850 is no ban at 1765 and nothing is said; one dated 1700-1780 is said with the house's
    date; and the same house undated keeps it and says why (A3). Dropping the date at the call
    turns the second into a ban kept for want of a date the record states."""
    q = copy.deepcopy(corpus["tidewater-georgian-careful"][0])
    assert q["context"]["date_of_representation"] == 1765, "the premise: the house is dated 1765"
    if not dated:
        q["context"].pop("date_of_representation")
    for mod, name in ((_m("threshold"), "_RESOLVED"), (_m("window_pier"), "_CACHE"),
                      (_m("plan_check"), "_RESOLVED_SLOTS")):
        monkeypatch.setattr(mod, name, {})
    real = EL.RK.resolve_slots

    def banning(graph, chain, scope=None):
        slots, rest = real(graph, chain, scope)
        lp = dict(slots.get("window_lite_pattern") or {})
        if case == "whole":
            lp.update({"binding": "forbidden", "_bound_by": "w-writer", "variants": []})
        else:
            lp["binding"] = "specified"
            lp["variants"] = [v for v in lp.get("variants") or [] if v.get("id") != "12/12"] + [
                {"id": "12/12", "status": "forbidden", "_written_by": "w-writer",
                 "applies_when": {"date_range": [1700, 1780] if case == "inside" else [1800, 1850]}}]
        return {**slots, "window_lite_pattern": lp}, rest
    monkeypatch.setattr(EL.RK, "resolve_slots", banning)
    sec = ST.build_section(q, None, geometry_result=q)
    el = EL.build_elevation(q, None, section=sec, roof=RF.build_roof(q, None, section=sec))
    faces = [f for f in FACES if f in (el.get("faces") or {})]
    assert "12/12" in {r.get("sash_pattern") for f in faces for r in EL.opening_rects(el, f)["rects"]
                       if r.get("kind") == "window"}, "the premise: the house draws 12/12"
    said = [str(n) for f in faces for n in EL.face_notes(el, f) if str(n).startswith("LIGHTS DRAWN 12/12")]
    if says is None:
        # the house's own kit forbids other patterns, undated (1/1, 6/1 ...), which it does not draw
        assert not said and "12/12" not in el["lite_patterns_forbidden"], (said, el["lite_patterns_forbidden"])
    else:
        assert said and all(says in n for n in said), said



# ------------------------------------------------------------------ auditor E's C5b: a stack refusal said where fires are stated
def test_a_wholesale_stack_refusal_is_said_only_on_a_plan_that_states_its_fires(corpus):
    """Auditor E (C5b): `disclosures.fires_not_drawn` says a wholesale stack refusal only where the
    plan states its fires (`placed_from` is `stated-hearths`), and dropping that gate was held by
    nothing but the corpus sheet digest -- a figure a re-pin loses. As a property: on every shipped
    plan that states no fire the line is silent whatever its stack refusal says (15 of 16 carry
    one, for want of a stated hearth); and on the one that states its fires, a wholesale refusal
    is printed whole. The second is driven, because the shipped Tidewater is refused no stack
    wholesale."""
    quiet = 0
    for pid, (q, _sec, _rf, _el) in sorted(corpus.items()):
        h = q.get("hearths") or {}
        whole = [u for u in h.get("unplaced") or []
                 if u.get("what") == "the stacks" and not u.get("room") and not u.get("flue")]
        if h.get("placed_from") != "stated-hearths":
            assert DI.fires_not_drawn(q) is None, (pid, DI.fires_not_drawn(q))
            quiet += bool(whole)
    assert quiet >= 10, ("the premise: plans stating no fire carry a wholesale refusal", quiet)
    q = copy.deepcopy(corpus["tidewater-georgian-careful"][0])
    assert q["hearths"]["placed_from"] == "stated-hearths", "the premise: the Tidewater states its fires"
    q["hearths"].setdefault("unplaced", []).append(
        {"what": "the stacks", "reason": "a driven refusal: no stack rises through this roof"})
    said = DI.fires_not_drawn(q)
    assert said and "STACKS NOT DRAWN \u2014 A DRIVEN REFUSAL: NO STACK RISES THROUGH THIS ROOF" in said["text"], said


# ------------------------------------------------------------------ auditor C's M7: U9 on the census's reader
@pytest.mark.parametrize("main", [
    {"refused": {"why": "B8"}, "form": None},
    {"refused": {"why": "B8"}, "form": "side-gable", "ridge": {"axis": "x"}},
    {"refused": {"why": "B8"}, "form": "hip", "ridge": {"axis": "x"}}], ids=["as-written", "stale-gable", "stale-hip"])
def test_a_refused_roof_has_no_judged_gable_end_on_either_reader(main):
    """Auditor C (M7): U9 reads a refused roof's gable faces as unjudged, never as "no gable end",
    in `elevation.gable_faces` and in the census's own reader (`svg_census._gable_faces_of`, written
    apart from the subject on purpose) -- and deleting the census's refused branch stayed green,
    because roof.py writes a refused roof with no form, which both readers' last line also answers
    None. The branch is what keeps the answer when a refused record carries a stale form, so it is
    driven so: both readers say unjudged, and the same record unrefused is the control."""
    import svg_census as C
    rec = {"main": main}
    assert EL.gable_faces(rec) is None and C._gable_faces_of(rec) is None
    plain = {"main": {k: v for k, v in main.items() if k != "refused"}}
    want = {None: None, "side-gable": ("W", "E"), "hip": ()}[main["form"]]
    assert C._gable_faces_of(plain) == want and (EL.gable_faces(plain) == want or (
        want and sorted(EL.gable_faces(plain)) == sorted(want))), (EL.gable_faces(plain), want)
