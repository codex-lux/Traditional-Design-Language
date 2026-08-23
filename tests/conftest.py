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
