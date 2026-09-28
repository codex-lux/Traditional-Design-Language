"""AN OPENING THE ELEVATION DOES NOT DRAW IS SAID WITH ITS OWN CAUSE, AND A SHEET OF THE MAIN BLOCK
SAYS IT IS OF THE MAIN BLOCK (Phase 15, WP-15.5).

The sheet named every opening it could not draw under one reason, "THE PLACER OR A STACK REFUSED
THEM". On the tagged Tidewater front five of the eleven it named stand on the WING's face, and
neither the placer nor a stack refused them: `elevation.placed_openings` refuses them because this
elevation is of the main block. That was a false statement printed on the plate, in the sentence
written to account for what the plate leaves out. Every refusal carries a `cause` from
`elevation.REFUSAL_CAUSES` now, and the sheet says each cause for the openings it is true of.

And the sheet never said that it draws the main block alone, which began to matter when WP-15.5
stood the exterior stacks on the ground: the west stack stands behind the hyphen from the south,
and the sheet drew it to the ground in open air. `elevation.main_block_note` is the sentence, one
spelling for the SVG and the DXF.

Expectations are derived from the record the sheet is drawn from, never written as room names: a
literal list would be one placement's luck.
"""
import copy
import glob
import json
import os
import re
import sys
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402


def _L(n):
    return modcache.load(n, os.path.join(ROOT, "build", n + ".py"))


GEO, ST, RF, EL, RE, ELM = (_L(n) for n in ("geometry", "structure", "roof", "elevation",
                                           "render_elevation", "elements"))
HEAD = "OPENING(S) ON THIS FACE NOT DRAWN"


def _build(path):
    with open(path, encoding="utf-8") as fh:
        plan = json.load(fh)
    saved = GEO._SOLVE_CACHE
    GEO._SOLVE_CACHE = {}
    try:
        placed = GEO.solve(plan, None, 250, engine="heuristic")
    finally:
        GEO._SOLVE_CACHE = saved
    sec = ST.build_section(placed, None, geometry_result=placed)
    if "error" in sec:
        return None
    rf = RF.build_roof(placed, None, section=sec)
    if "error" in rf:
        return None
    el = EL.build_elevation(placed, None, section=sec, roof=rf)
    if "error" in el or not el.get("applicable", True):
        return None
    return el


@pytest.fixture(scope="module")
def corpus():
    paths = (sorted(glob.glob(os.path.join(ROOT, "plans", "*.json")))
             + sorted(glob.glob(os.path.join(ROOT, "plans", "reference", "*.json"))))
    out = {}
    for p in paths:
        el = _build(p)
        if el is not None:
            out[os.path.basename(p)[:-5]] = el
    assert len(out) >= 10, "the premise: most shipped plans build an elevation"
    return out


def _svg(el, face):
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, f"{face}.svg")
        RE.render_elevation(el, out, face=face)
        return open(out, encoding="utf-8").read()


def _said(svg):
    return [" ".join(t.split()) for t in re.findall(r'<text class="dm"[^>]*>([^<]*)</text>', svg)]


def _rooms(xs):
    return {str(x["room"]).upper() for x in xs}


def test_every_refusal_carries_a_cause_from_the_closed_set(corpus):
    seen = {}
    for pid, el in corpus.items():
        for f in EL.FACES:
            for x in EL.opening_rects(el, f)["refused"]:
                assert x.get("cause") in EL.REFUSAL_CAUSES, (pid, f, x.get("why"))
                seen[x["cause"]] = seen.get(x["cause"], 0) + 1
    # the premise: the corpus reaches more than one cause, so a grouping has something to group
    assert seen.get("placer") and seen.get("element"), seen


def test_the_sheet_has_words_for_every_cause_and_in_the_same_order():
    assert tuple(c for c, _w in RE._REFUSED_WORDS) == tuple(EL.REFUSAL_CAUSES)
    assert all(w and w == w.upper() for _c, w in RE._REFUSED_WORDS)


def _face_with(corpus, want_many):
    """A (plan, face) whose named refusals carry more than one cause (want_many) or exactly one."""
    for pid, el in sorted(corpus.items()):
        for f in EL.FACES:
            named = [x for x in EL.opening_rects(el, f)["refused"] if x.get("room")]
            causes = {x["cause"] for x in named}
            if named and ((len(causes) > 1) == want_many):
                return pid, el, f, named
    return None


def test_each_cause_is_said_for_the_openings_it_is_true_of(corpus):
    got = _face_with(corpus, True)
    assert got, "the premise: some face names openings refused for two causes"
    pid, el, face, named = got
    said = _said(_svg(el, face))
    head = [t for t in said if HEAD in t]
    assert len(head) == 1, head
    units = sum(int(x.get("units") or 1) for x in named)
    assert head[0].startswith(f"{units} {HEAD}"), head[0]
    assert head[0].endswith("THE ELEVATION RECORD NAMES EACH:"), head[0]
    words = dict(RE._REFUSED_WORDS)
    lines = [t for t in said if t.startswith("· ")]
    for cause in sorted({x["cause"] for x in named}):
        xs = [x for x in named if x["cause"] == cause]
        n = sum(int(x.get("units") or 1) for x in xs)
        line = [t for t in lines if t.endswith(words[cause])]
        assert len(line) == 1, (pid, face, cause, lines)
        assert line[0].startswith(f"· {n} ("), (line[0], n)
        for room in _rooms(xs):
            assert room in line[0], (room, line[0])
    assert not any("THE PLACER OR A STACK" in t for t in said), "the one reason for every cause"


def test_a_single_cause_is_said_on_the_one_line(corpus):
    got = _face_with(corpus, False)
    assert got, "the premise: some face names openings refused for one cause only"
    _pid, el, face, named = got
    said = _said(_svg(el, face))
    head = [t for t in said if HEAD in t]
    assert len(head) == 1, head
    cause = named[0]["cause"]
    assert f"— {dict(RE._REFUSED_WORDS)[cause]}; THE ELEVATION RECORD NAMES EACH" in head[0], head[0]
    assert not [t for t in said if t.startswith("· ") and any(t.endswith(w) for _c, w in RE._REFUSED_WORDS)]


def test_a_window_a_stack_stands_on_is_said_as_the_stack_refusing_it(corpus):
    """DRIVEN: no shipped plan blinds a window with a stack (WP-12.2), so the stack cause is put on
    a placed window by hand, the way `tests/test_opening_rects.py` drives it."""
    el = copy.deepcopy(corpus["tidewater-georgian-careful"])
    face = el["entrance_face"]
    win = next(p for p in el["faces"][face]["placed"] if p["kind"] == "window")
    el["faces"][face]["stack_axes_ft"] = [win["u_ft"]]
    el["faces"][face]["stack_half_width_ft"] = 0.9167
    stacked = [x for x in EL.opening_rects(el, face)["refused"] if x.get("cause") == "stack"]
    assert stacked, "the drive landed: a stack stands on a placed window"
    assert any(dict(RE._REFUSED_WORDS)["stack"] in t for t in _said(_svg(el, face)))


def test_a_sheet_of_the_main_block_says_so_where_a_wing_stands_beside_it(corpus):
    tagged = corpus["tidewater-georgian-careful"]
    others = [e for e in ELM.elements(tagged["section"]["geometry"]) if e["role"] != "main"]
    assert others, "the premise: the tagged Tidewater placement sets masses beside the main block"
    note = EL.main_block_note(tagged)
    assert note and note.startswith("THIS ELEVATION IS OF THE MAIN BLOCK")
    for e in others:
        assert e["role"].upper() in note, (e["role"], note)
    for f in EL.FACES:
        assert _said(_svg(tagged, f)).count(note) == 1, f
    one = corpus["spec-builder-colonial"]
    assert len(ELM.elements(one["section"]["geometry"])) == 1, "the premise: one rectangle"
    assert EL.main_block_note(one) is None
    for f in EL.FACES:
        assert not any(t.startswith("THIS ELEVATION IS OF THE MAIN BLOCK") for t in _said(_svg(one, f))), f


def test_two_masses_of_one_role_are_counted_in_the_plural_of_that_role(corpus, monkeypatch):
    """DRIVEN (WP-15.8's audit): no shipped plan sets two masses of one role beside its main block,
    and the sentence's first version appended an S -- "THE 2 DEPENDENCYS"."""
    fake = [{"id": "main", "role": "main"}, {"id": "a", "role": "dependency"},
            {"id": "b", "role": "dependency"}, {"id": "h1", "role": "hyphen"},
            {"id": "h2", "role": "hyphen"}]
    monkeypatch.setattr(ELM, "elements", lambda _placed: fake)
    note = EL.main_block_note(corpus["tidewater-georgian-careful"])
    assert "THE 2 DEPENDENCIES AND THE 2 HYPHENS" in note, note
    assert "DEPENDENCYS" not in note, note


def test_the_dxf_elevation_writes_the_same_sentence(corpus):
    ezdxf = pytest.importorskip("ezdxf")
    DX = _L("export_dxf")

    def texts(el):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "e.dxf")
            DX.export_elevation_dxf(el, path, face="S")
            doc = ezdxf.readfile(path)
            return [e.dxf.text for e in doc.modelspace().query("TEXT")]

    tagged = corpus["tidewater-georgian-careful"]
    assert EL.main_block_note(tagged) in texts(tagged)
    assert not any(t.startswith("THIS ELEVATION IS OF THE MAIN BLOCK")
                   for t in texts(corpus["spec-builder-colonial"]))
