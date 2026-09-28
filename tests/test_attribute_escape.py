"""A RECORD'S STRING CANNOT LEAVE THE ATTRIBUTE IT IS WRITTEN INTO (audit, 27 Sep 2026).

Each renderer's `_esc` escapes `& < >`, which is all a TEXT node needs, and it was also used
inside `data-key-room="..."`, `data-hearth-refused="..."`, `data-threshold="..."` and five more
attributes -- where the character that closes the value is the one it does not escape -- and
`data-block` took its value with no escape at all. A room id and a level id are free strings in
`plan.schema.json` (the plan's own id carries a pattern; neither of these does), `POST
/api/drawings/{kind}` draws whatever record it is handed, and the Drawing Set and the Round inject
the SVG it returns with `dangerouslySetInnerHTML`. A room id of `bed3" onmouseover="..."` put a
live handler on six elements of `spec-builder-colonial`'s plan, in both registers. Reproduced
before it was fixed; `build/sheet_style.py::attr` is the one spelling now.

THE GUARD IS BEHAVIOURAL, because a source sweep sees only the shapes somebody thought to list:
every room id and every level id of two shipped plans is made hostile, the house is placed and
every sheet the four renderers draw is parsed as XML, and nothing may carry an event handler or an
element the payload smuggled in. A probe that never reached an attribute would pass on any code,
so the payload's arrival IN AN ATTRIBUTE is asserted first, on each plan -- the premise, not a
formality.

A TEXT NODE KEEPS `_esc` AND THAT IS MEASURED, NOT PREFERRED: escaping `"` in text too moved all
32 shipped plan sheets and every elevation (the sheets' own inch marks, `11'-11"`, are text) for
no change in what is drawn. The byte-identity of the shipped sheets across this fix is the
other half of the evidence and is recorded in the audit's report.
"""
import copy
import json
import os
import sys
import xml.etree.ElementTree as ET

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402


def _L(name):
    return modcache.load(name, os.path.join(ROOT, "build", name + ".py"))


GEO, ST, RF, EL = _L("geometry"), _L("structure"), _L("roof"), _L("elevation")
RP, RE, RS, RR = _L("render_plan"), _L("render_elevation"), _L("render_section"), _L("render_roof")
SS = _L("sheet_style")

# TWO PAYLOADS, because they fail differently. The FULL one carries every character that can close
# or open something -- both quotes, both angle brackets, an ampersand -- and a breakout with it
# leaves a `<` loose in an attribute, which no XML parser reads: the guard sees a parse error. The
# QUOTE one closes the attribute and opens a handler and nothing else, so the sheet stays
# well-formed and only the handler assertion can see it. Measured: with the full payload alone,
# every one of ten mutations went red on the parse and not one reached the handler check.
FULL = 'Q" onmouseover="alert(1)" data-q=\'<b>&'
QUOTE = 'Q" onmouseover="alert(1)'
PAYLOADS = {"full": FULL, "quote": QUOTE}
# The spec Colonial (one element, the furniture key), the Tidewater house (three elements, a
# stoop, a refused fire) and good-02 (a terrace drawn as an appendage): between them the payload
# reaches every attribute a record's room or level id is written into -- asserted, not assumed,
# by `test_every_attribute_that_carries_a_record_id_is_reached`.
PLANS = ("plans/spec-builder-colonial.json", "plans/tidewater-georgian-careful.json",
         "plans/reference/good-02-portico-library-house.json")


def _hostile(plan, payload):
    """Every room id and level id made hostile, and every reference to a room id renamed with it
    (a door's `to` and `swing_into`, `stacks_over`, `wet_stack_with`), so the house placed is the
    same house under names nobody should trust."""
    p = copy.deepcopy(plan)
    ren = {r["id"]: f'{r["id"]}{payload}' for lv in p["levels"] for r in lv["rooms"]}
    for lv in p["levels"]:
        lv["id"] = f'{lv.get("id") or "level"}{payload}'
        for r in lv["rooms"]:
            r["id"] = ren[r["id"]]
            for k in ("stacks_over", "wet_stack_with"):
                if r.get(k) in ren:
                    r[k] = ren[r[k]]
            for d in r.get("doors") or []:
                for k in ("to", "swing_into"):
                    if d.get(k) in ren:
                        d[k] = ren[d[k]]
    return p


def _sheets(plan, out):
    """Every sheet the four renderers draw for one placed record: both plan registers, the
    section, the bearing plate, the roof plan and the four elevations, as far as each builds."""
    placed = GEO.solve(plan, engine="heuristic")
    paths = []
    for reg in RP.REGISTERS:
        paths.append(os.path.join(out, f"plan-{reg}.svg"))
        RP.render(placed, paths[-1], register=reg)
    sec = ST.build_section(placed, None, geometry_result=placed)
    if "error" not in sec:
        paths.append(os.path.join(out, "section.svg"))
        RS.render_section(sec, paths[-1])
        paths.append(os.path.join(out, "bearing.svg"))
        RS.render_bearing_diagram(sec, paths[-1])
        roof = RF.build_roof(placed, None, section=sec)
        if "error" not in roof:
            paths.append(os.path.join(out, "roof.svg"))
            RR.render_roof(roof, paths[-1])
        elev = EL.build_elevation(placed, None, section=sec)
        if "error" not in elev:
            for face in "SNEW":
                paths.append(os.path.join(out, f"elev-{face}.svg"))
                RE.render_elevation(elev, paths[-1], face=face)
    return paths


@pytest.fixture(scope="module")
def drawn(tmp_path_factory):
    """Each plan's sheets, drawn on a PRIVATE solve cache: the hostile record's placement must not
    sit in the shared one where a later test could be handed it (WP-14.6's cache poisoning)."""
    out = {}
    saved = GEO._SOLVE_CACHE
    GEO._SOLVE_CACHE = {}
    try:
        for kind, payload in PAYLOADS.items():
            for rel in PLANS:
                with open(os.path.join(ROOT, rel)) as fh:
                    plan = _hostile(json.load(fh), payload)
                d = tmp_path_factory.mktemp(f"{kind}-{os.path.basename(rel)[:-5]}")
                out[kind, rel] = _sheets(plan, str(d))
    finally:
        GEO._SOLVE_CACHE = saved
    return out


def _parse(path):
    with open(path, encoding="utf-8") as fh:
        return ET.fromstring(fh.read())


@pytest.mark.parametrize("kind", sorted(PAYLOADS))
@pytest.mark.parametrize("rel", PLANS)
def test_the_payload_reaches_an_attribute_on_each_plan(drawn, rel, kind):
    """THE PREMISE. Unless the hostile string arrives inside an attribute's VALUE somewhere, the
    no-breakout assertion below is true of any code at all."""
    hits = 0
    for path in drawn[kind, rel]:
        for el in _parse(path).iter():
            hits += sum(1 for v in el.attrib.values() if PAYLOADS[kind] in v)
    assert hits > 0, f"{rel}: no attribute carries the payload, so the guard below guards nothing"


@pytest.mark.parametrize("kind", sorted(PAYLOADS))
@pytest.mark.parametrize("rel", PLANS)
def test_no_sheet_carries_a_handler_or_an_element_the_record_smuggled_in(drawn, rel, kind):
    """Every sheet parses as XML -- a `<` or an `&` loose in an attribute would already fail
    here -- and no element anywhere carries an `on*` attribute or is a `<b>` the payload opened."""
    assert drawn[kind, rel], rel
    for path in drawn[kind, rel]:
        root = _parse(path)
        for el in root.iter():
            tag = el.tag.rsplit("}", 1)[-1]
            assert tag != "b", f"{os.path.basename(path)}: the payload opened an element"
            bad = [k for k in el.attrib if k.lower().startswith("on") or k == "data-q"]
            assert not bad, f"{os.path.basename(path)}: <{tag}> carries {bad} from a record's string"


# The attributes the renderers write a room's or a level's id into. A new one belongs here and in
# the probe's reach, or the guard above says nothing about it.
CARRIERS = {"data-key", "data-key-room", "data-level", "data-plate", "data-threshold",
            "data-hearth-refused", "data-appendage"}


@pytest.mark.parametrize("kind", sorted(PAYLOADS))
def test_every_attribute_that_carries_a_record_id_is_reached(drawn, kind):
    """THE REACH, over all three plans together: each carrier is written with the payload in it
    at least once, so reverting any ONE of them to `_esc` is a breakout the test above sees."""
    seen = set()
    for rel in PLANS:
        for path in drawn[kind, rel]:
            for el in _parse(path).iter():
                seen |= {k for k, v in el.attrib.items() if PAYLOADS[kind] in v}
    assert CARRIERS <= seen, f"never reached: {sorted(CARRIERS - seen)}"


def test_the_attribute_escape_is_one_spelling_and_leaves_text_to_esc():
    """`sheet_style.attr` escapes all four characters and the double quote with them; a renderer's
    `_attr` IS it, not a copy. Text keeps `_esc` (see the module docstring for the measurement)."""
    assert SS.attr('a"b<c>d&e') == "a&quot;b&lt;c&gt;d&amp;e"
    assert SS.attr(None) == "" and SS.attr(3) == "3"
    for mod in (RP, RE, RS, RR):
        assert mod._attr is SS.attr, mod.__name__
        assert mod._esc('"') == '"', f"{mod.__name__}: a text node's quote must not move"


def test_the_frame_attribute_is_well_formed_for_any_level_id():
    """`frame_attr` is single-quoted and escaped only the apostrophe, under a comment saying a level
    id is a slug -- which the schema does not say. A `<` or `&` there made a downloaded sheet
    malformed XML; both are escaped now, and the JSON reads back whole."""
    frames = {"plates": [{"id": FULL, "px_per_ft": 13.0}]}
    el = ET.fromstring(f"<svg data-frame='{SS.frame_attr(frames)}'/>")
    assert json.loads(el.attrib["data-frame"]) == frames
