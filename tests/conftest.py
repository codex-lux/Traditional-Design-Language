"""Shared fixtures for the behaviour-test suite.

These tests exist to pin *behaviour* the review of 23 Aug 2026 found undefended:
excellent data checkers, but nothing that would catch the single-pile Georgian
dropping from first to fourth place again if a scoring change regressed it.
Every test here protects one specific finding recorded in the docs — the test's
name says which one, and the docstring quotes or points at where the finding
lives, so a failure here is diagnostic, not just red.
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
MCP = os.path.join(ROOT, "mcp_server")
for p in (BUILD, MCP):
    if p not in sys.path:
        sys.path.insert(0, p)


@pytest.fixture(scope="session")
def plan_check_module():
    import plan_check
    return plan_check


@pytest.fixture(scope="session")
def corpus(plan_check_module):
    return plan_check_module.load_corpus()


@pytest.fixture(scope="session")
def core_module():
    import core
    return core


@pytest.fixture(scope="session")
def geometry_module():
    import geometry
    return geometry


@pytest.fixture(scope="session")
def compose_module():
    import compose
    return compose


@pytest.fixture(scope="session")
def solver_module():
    import solver
    return solver


@pytest.fixture(scope="session")
def resolve_kit_module():
    import resolve_kit
    return resolve_kit


@pytest.fixture(scope="session")
def check_constraints_module():
    import check_constraints
    return check_constraints


@pytest.fixture(scope="session")
def constraint_vocabulary_module():
    import constraint_vocabulary
    return constraint_vocabulary


@pytest.fixture(scope="session")
def structure_module():
    import structure
    return structure


@pytest.fixture(scope="session")
def render_section_module():
    import render_section
    return render_section


@pytest.fixture(scope="session")
def roof_module():
    import roof
    return roof


@pytest.fixture(scope="session")
def render_roof_module():
    import render_roof
    return render_roof


@pytest.fixture(scope="session")
def elevation_module():
    import elevation
    return elevation


@pytest.fixture(scope="session")
def render_elevation_module():
    import render_elevation
    return render_elevation


def load_style(style_id):
    with open(os.path.join(ROOT, "styles", f"{style_id}.json")) as f:
        return json.load(f)


def load_plan(name):
    with open(os.path.join(ROOT, "plans", f"{name}.json")) as f:
        return json.load(f)


def load_reference_plan(name):
    with open(os.path.join(ROOT, "plans", "reference", f"{name}.json")) as f:
        return json.load(f)


def minimal_plan(rooms, style="georgian-colonial-american", massing="centre-passage-single-pile"):
    """A minimal, schema-shaped plan record with a single ground level.

    `rooms` is the list to place directly under levels[0]['rooms']; every test
    fixture in this suite is built from this so the plan-record shape stays in
    one place rather than fifteen slightly-different hand-authored dicts.
    """
    return {
        "id": "test-plan",
        "name": "Test",
        "style": style,
        "massing": massing,
        "groupings": [],
        "context": {},
        "levels": [
            {"id": "ground", "index": 0, "floor_to_ceiling_ft": 9, "rooms": rooms}
        ],
        "adjacencies": [],
        "declared": {},
    }


# ---------------------------------------------------------------------- WP-13.5, the container
def untagged_reference_plan(name="tidewater-georgian-careful"):
    """A shipped plan record with its own massing container REMOVED, for a fixture that means
    to state its own.

    **WHY THIS EXISTS, AND IT IS ONE SPELLING BECAUSE EIGHT FIXTURES NEED IT.** Until WP-13.5 no
    plan in this corpus carried a `block` tag, so every hand-tagged fixture could open
    `plans/tidewater-georgian-careful.json`, add two or three tags and know exactly what house it
    had built. WP-13.5 moved the service programme into the dependency the plan declares, so that
    record now carries five `block: service` tags and a `hyphen: true` of its own — and a fixture
    that adds `west-dependency` on top of them builds a FOUR-element house where it meant to build
    a two-element one. That is not a wrong answer from the code under test; it is the fixture no
    longer reaching it, which is WP-8.11's rule met from the other side: a fixture must state the
    case it exists for rather than inherit whatever the corpus happens to carry.

    Stripping is the right repair rather than renaming the shipped tags to match, because the
    property each of these fixtures pins is *what the placer does with N elements*, and N is the
    fixture's business. `tests/test_check_plans.py` keeps the other half — that the shipped record
    and its parti agree about the container they DO carry.
    """
    p = json.load(open(os.path.join(ROOT, "plans", name + ".json")))
    return p, as_one_element(p)


def as_one_element(plan):
    """Strip a plan's massing container IN PLACE and return how many tags went.

    The second spelling, for the guards that sweep `plans/**/*.json` by glob and so have the
    record in hand rather than a name. One function does the stripping so the two cannot drift
    about what a container is."""
    stripped = 0
    for lv in plan.get("levels", []):
        for r in lv.get("rooms", []):
            stripped += r.pop("block", None) is not None
            r.pop("hyphen", None)
    return stripped
