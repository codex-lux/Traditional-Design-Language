"""Milestone 3: the drawing pipeline over HTTP, re-tokenized to the Drawn Language.
Same generators the CLI drives; the SVG must carry none of the dark palette."""
import json
import os

from workbench.server import svg_theme

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

DARK = ["#0B1B29", "#0F2536", "#EDE7DA", "#24455E", "#D8B26A", "#C4553A"]


def _plan():
    return json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))


def test_all_five_kinds(client):
    for kind in ("plan", "elevation", "section", "bearing", "roof"):
        r = client.post(f"/api/drawings/{kind}", json={"plan": _plan()})
        assert r.status_code == 200, (kind, r.text[:200])
        svg = r.json()["svg"]
        assert svg.startswith("<svg")
        for hexval in DARK:  # re-rendered, never left in the dark system
            assert hexval.lower() not in svg.lower(), (kind, hexval)


def test_the_plan_sheet_has_two_registers_and_says_which(client):
    """Ruled 4 Sep 2026: a presentation sheet carries the drawing and the names, a working
    sheet adds the dimension strings, the divergence marks and the relaxation triangles on the
    field. Both come from one renderer, and the plate SAYS which -- a printed plate leaves its
    page prose behind, so a reader who cannot tell the two apart on the sheet itself cannot
    tell them apart at all. Nothing is DELETED by the presentation register: every disclosure
    the working sheet carries is set in the title block below the border on both."""
    p = _plan()
    pres = client.post("/api/drawings/plan", json={"plan": p, "register": "presentation"}).json()
    work = client.post("/api/drawings/plan", json={"plan": p, "register": "working"}).json()
    assert pres["register"] == "presentation" and work["register"] == "working"
    assert "PRESENTATION REGISTER" in pres["svg"] and "WORKING REGISTER" in work["svg"]
    # the marks are the difference, and the difference is on the FIELD
    assert "ft off the bay line" in work["svg"], "the working sheet draws no relaxation marks"
    assert "ft off the bay line" not in pres["svg"], (
        "the presentation sheet still carries the diagnostic marks on the drawing")
    # and the disclosure survives in the margin on BOTH -- this is P7, not decoration
    for reg, r in (("presentation", pres), ("working", work)):
        assert "CUT(S) OFF THE BAY LINE" in r["svg"], (
            f"the {reg} sheet has dropped the relaxation count from its schedule")
        assert "DECLARED DOOR(S) WITHOUT A DRAWABLE OPENING" in r["svg"], (
            f"the {reg} sheet has dropped the undrawable-door disclosure")
    assert len(work["svg"]) > len(pres["svg"]), "the working sheet carries strictly more"


def test_an_unknown_register_is_refused_rather_than_guessed(client):
    r = client.post("/api/drawings/plan", json={"plan": _plan(), "register": "sketch"})
    assert r.status_code == 422
    assert "register" in json.dumps(r.json())


def test_plan_kind_reports_relaxations(client):
    r = client.post("/api/drawings/plan", json={"plan": _plan()}).json()
    assert "relaxations" in r and "count" in r["relaxations"]


def test_unknown_kind_names_the_kinds(client):
    r = client.post("/api/drawings/axonometric", json={"plan": _plan()})
    assert r.status_code == 422
    assert "kinds" in r.json()["detail"]


def _sheet_style():
    """build/sheet_style.py, by path -- the one place a sheet's colours are written down."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "sheet_style_for_test", os.path.join(ROOT, "build", "sheet_style.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_retokenize_is_total_over_renderer_palettes():
    """Every hex a sheet can emit must have a Drawn Language duty.

    WIDENED WHEN build/sheet_style.py WAS ADDED, AND THE WIDENING IS THE POINT. This test
    used to read the four `render_*.py` sources; the moment their `PAL` dicts moved into
    `sheet_style.py` it would have scanned four files containing no hex at all and passed
    over an empty set -- a guard that cannot fire, which is the failure this repository has
    met more often than any other. It scans the style module too, and asserts the population
    is non-empty before judging it.

    Two duties count as discharged: a DARK value, which `retokenize` translates on the way
    out; and a value already in the Drawn Language (`sheet_style.LIGHT`, or a value of the
    map), which passes through untouched because it is already what the map produces.
    """
    import re
    SS = _sheet_style()
    hexes = set()
    sources = ("render_plan.py", "render_elevation.py", "render_section.py", "render_roof.py",
               "sheet_style.py")
    for f in sources:
        src = open(os.path.join(ROOT, "build", f)).read()
        hexes.update(h.upper() for h in re.findall(r"#[0-9A-Fa-f]{6}", src))
    assert len(hexes) >= 30, (
        f"only {len(hexes)} colours found across {sources} -- the palette has moved again and "
        "this test is judging an empty set")
    already_light = {v.upper() for v in SS.LIGHT.values()} | {v.upper() for v in svg_theme.HEX_MAP.values()}
    unmapped = hexes - {k.upper() for k in svg_theme.HEX_MAP} - already_light
    assert not unmapped, f"sheet colours with no Drawn Language duty: {sorted(unmapped)}"


def test_the_light_register_quotes_the_standard_and_does_not_invent_it():
    """`sheet_style.LIGHT` says it is Graphic Standard No. 1 lifted verbatim. This checks it.

    WITHOUT THIS, THE TOTALITY TEST ABOVE HAS A HOLE AND A MUTATION FOUND IT. That test
    discharges a colour's duty if it is "already in the Drawn Language", and it decides
    membership by reading `LIGHT` -- so a colour smuggled into `LIGHT` vouches for itself and
    passes. Measured: adding `"smuggled": "#123456"` to `LIGHT` left the totality test GREEN.
    The standard is `workbench/app/src/theme/tokens.css`, which is the artefact tokens.css's
    own header says the values were lifted from, so that file is the thing a light value has
    to be found in. A new ink is then a change to the standard, which is a ruling, not a
    literal in a renderer.
    """
    import re
    SS = _sheet_style()
    css = open(os.path.join(ROOT, "workbench", "app", "src", "theme", "tokens.css")).read()
    declared = {h.upper() for h in re.findall(r"#[0-9A-Fa-f]{6}", css)}
    assert len(declared) >= 20, "tokens.css has moved -- this test is judging an empty standard"
    stray = {k: v for k, v in SS.LIGHT.items() if v.upper() not in declared}
    assert not stray, (
        "sheet_style.LIGHT claims to quote Graphic Standard No. 1 and these values are in no "
        f"token of it: {stray}")


def test_every_dark_value_is_translated():
    """The other direction, and it is not implied by the test above.

    A dark value that is ALSO a Drawn Language token would pass that test through the
    `already_light` branch while reaching the browser untranslated. None is today; this
    asserts it rather than assuming it."""
    SS = _sheet_style()
    keys = {k.upper() for k in svg_theme.HEX_MAP}
    for name, dark in {**SS.DARK, **SS.DARK_ELEVATION, **SS.DARK_FILL,
                       "void_roofed": SS.DARK_VOID_ROOFED,
                       "fill_default": SS.DARK_FILL_DEFAULT}.items():
        assert dark.upper() in keys, f"the dark register's {name} ({dark}) is not translated"
        assert dark.upper() not in {v.upper() for v in SS.LIGHT.values()}, (
            f"{name} ({dark}) is in both registers, so it would reach the browser as itself")
