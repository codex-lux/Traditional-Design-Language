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


def test_plan_kind_reports_relaxations(client):
    r = client.post("/api/drawings/plan", json={"plan": _plan()}).json()
    assert "relaxations" in r and "count" in r["relaxations"]


def test_unknown_kind_names_the_kinds(client):
    r = client.post("/api/drawings/axonometric", json={"plan": _plan()})
    assert r.status_code == 422
    assert "kinds" in r.json()["detail"]


def test_retokenize_is_total_over_renderer_palettes():
    # every hex the four renderers emit must have a mapping — a new renderer colour
    # showing up unmapped should fail here, not ship half-dark
    import re
    hexes = set()
    for f in ("render_plan.py", "render_elevation.py", "render_section.py", "render_roof.py"):
        src = open(os.path.join(ROOT, "build", f)).read()
        hexes.update(h.upper() for h in re.findall(r"#[0-9A-Fa-f]{6}", src))
    unmapped = hexes - {k.upper() for k in svg_theme.HEX_MAP}
    assert not unmapped, f"renderer colours with no Drawn Language duty: {unmapped}"
