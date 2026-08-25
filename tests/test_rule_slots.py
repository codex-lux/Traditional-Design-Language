"""OQ 15 -- rules of four different kinds in one flat set.

`room_adjacency_overrides` on the Georgian kit held six rules as prose strings inside a single
'many'-cardinality parameter: a topological rule about the adjacency graph, a geometric rule
about axes, a rule about where a wall element goes, and a preference about orientation. The
slot's own note said so, twice, and said no engine could act on them as written.

The slot's note ALSO said, since ontology 0.4.0, that the slot holds "only what a style ADDS or
SUPPRESSES" against the universal rules in rooms/ -- and nothing read it. A suppression existed
as prose while the validator went on enforcing the rule the kit said should not apply.
"""
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def kit(style):
    return json.load(open(os.path.join(ROOT, "kits", "%s.kit.json" % style)))


def live(slot):
    """The slot's ACTIVE content -- its rules and parameters, not its note. The note
    deliberately quotes the clauses that were removed and why, which is the record of the
    migration and would otherwise make every 'this is gone' assertion unwritable."""
    return json.dumps({"rules": slot.get("rules"), "parameters": slot.get("parameters"),
                       "rule": slot.get("rule")})


# ---------------------------------------------------------------- the Georgian six


def test_the_flat_prose_set_is_gone():
    s = kit("georgian-colonial-american")["slots"]["room_adjacency_overrides"]
    assert "adjacency_rules" not in (s.get("parameters") or {})
    assert s["rules"], "and something typed took its place"


def test_what_survived_is_two_clauses_of_two_kinds():
    """Two of the six were about the adjacency graph. One of those restated the other."""
    s = kit("georgian-colonial-american")["slots"]["room_adjacency_overrides"]
    assert [r["kind"] for r in s["rules"]] == ["topology", "axis"]
    assert [r["effect"] for r in s["rules"]] == ["restricts", "adds"]
    assert (s.get("parameters") or {}).get("door_alignment_tolerance"), \
        "the axis clause keeps its measured tolerance"


def test_the_clause_that_was_not_about_adjacency_moved_to_the_slot_that_owns_it():
    """Where the chimney breast sits in a room is element placement. It is now on
    hearth_position, beside the regional parameters saying where the STACK goes -- a different
    question with a different answer, and both are needed to draw the room."""
    k = kit("georgian-colonial-american")
    hp = k["slots"]["hearth_position"]["parameters"]["breast_position_in_room"]
    assert "outside wall" in hp["value"]
    assert "chimney breast" not in live(k["slots"]["room_adjacency_overrides"])


@pytest.mark.parametrize("clause,owner,evidence", [
    ("best room is at the front", "public_private_gradient", "Rank falls front to back"),
    ("windows on two walls", "daylight_strategy", "walls_lit_per_principal_room"),
])
def test_the_duplicated_clauses_are_deleted_and_their_owners_still_say_it(clause, owner, evidence):
    """Three of the six duplicated slots that already said the same thing, so they are deleted
    rather than moved. This checks BOTH halves: the duplicate is gone, and the fact survives
    where it belongs -- deleting data because it was said twice must not end with it said
    zero times."""
    k = kit("georgian-colonial-american")
    assert clause not in live(k["slots"]["room_adjacency_overrides"])
    assert evidence in json.dumps(k["slots"][owner])


# ---------------------------------------------------------------- the catalogue


def test_every_populated_override_slot_is_classified():
    """Eight kits state a room_adjacency_overrides rule. All eight now say what KIND of claim
    each clause is, which is the whole of what OQ 15 asked for."""
    import glob
    n = 0
    for p in sorted(glob.glob(os.path.join(ROOT, "kits", "*.kit.json"))):
        s = (json.load(open(p))["slots"].get("room_adjacency_overrides") or {})
        if s.get("status") != "drafted": continue
        n += 1
        assert s.get("rules"), p
        for r in s["rules"]:
            assert r["kind"] and r["effect"] and r["statement"]
            assert r.get("why"), "a rule with no reason is a rule nobody can check"
    # 8 -> 15 on 24 Aug 2026: OQ 43 made the substitution table directional, which surfaced six
    # traditions whose entry sequence or storage habit the universal room rules were never
    # written for, and each declared a suppression rather than being worked around.
    assert n == 15, n


def test_the_suppressions_are_declared_where_the_fact_is_and_say_why():
    """OQ 15 built this mechanism and nothing used it -- the entry said so, and said that
    inventing a suppression to exercise the code would be exactly what this corpus forbids.
    OQ 43 gave it something real to carry: making substitution directional made six traditions'
    universal rules fire, each of them a rule the type structurally cannot satisfy.

    A Charleston single's street door opens onto the PIAZZA; a bungalow's opens into the LIVING
    ROOM, which is the hall the type abolished; a dogtrot's opens into the trot, which is open to
    the weather at both ends; a Creole cabinet is entered from the loggia and never from a
    chamber."""
    import glob
    found = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "kits", "*.kit.json"))):
        d = json.load(open(p))
        for r in ((d["slots"].get("room_adjacency_overrides") or {}).get("rules") or []):
            if r["effect"] != "suppresses": continue
            sup = r["suppresses"]
            found.setdefault(d["style"], []).append((sup["room"], sup["key"], sup["target"]))
            assert r.get("why"), (d["style"], "a suppression with no reason is unreviewable")
            assert len(r["why"]) > 120, (d["style"], "and the reason has to be an argument")
    assert len(found) >= 7, sorted(found)
    # the four shapes, each on the tradition it belongs to
    assert ("entry-porch", "must_adjoin", "entrance-hall") in found["american-arts-and-crafts"]
    assert ("entry-porch", "must_adjoin", "entrance-hall") in found["dogtrot-vernacular"]
    assert ("piazza", "must_adjoin", "entrance-hall") in found["charleston-single-house"]
    assert ("closet", "must_adjoin", "bedroom") in found["creole-cottage-vernacular"]


def test_a_suppression_is_declared_on_every_sibling_because_it_does_not_travel_sideways():
    """The Creole cabinet fact holds for four sibling traditions, and a suppression is inherited
    DOWN a chain. Stating it four times is the honest cost; hoisting it to a shared ancestor
    would claim the cabinet-and-loggia range for traditions that do not have it."""
    import glob
    have = set()
    for p in glob.glob(os.path.join(ROOT, "kits", "*.kit.json")):
        d = json.load(open(p))
        for r in ((d["slots"].get("room_adjacency_overrides") or {}).get("rules") or []):
            if r.get("effect") == "suppresses" and r["suppresses"]["room"] == "closet":
                have.add(d["style"])
    assert {"creole-cottage-vernacular", "french-colonial-american",
            "monterey-colonial", "monterey-revival"} <= have, sorted(have)


# ---------------------------------------------------------------- the executable half


def test_a_declared_suppression_switches_the_universal_rule_off(plan_check_module, corpus):
    """The promise the slot's note has made since ontology 0.4.0 and nothing kept."""
    rooms = [
        {"id": "pr", "type": "parlor", "name": "Parlor",
         "width_ft": 14, "length_ft": 16, "exterior_walls": ["S"],
         "windows": [{"wall": "S", "width_ft": 3, "height_ft": 5, "count": 2}],
         "doors": [{"to": "exterior", "width_ft": 3}]},
    ]
    from test_plan_validator import minimal_plan
    plan = minimal_plan(rooms)
    C = dict(corpus)
    C["kits"] = dict(corpus["kits"])

    def fatals(kits):
        C["kits"] = kits
        return [f for f in plan_check_module.check(plan, C)["findings"]
                if f.get("room") == "pr" and "entrance hall" in f["statement"].lower()]

    style = plan["style"]
    assert fatals(corpus["kits"]), "the universal rule must be firing to begin with"

    patched = dict(corpus["kits"])
    patched[style] = json.loads(json.dumps(corpus["kits"].get(style) or {"style": style, "slots": {}}))
    patched[style].setdefault("slots", {})["room_adjacency_overrides"] = {
        "group": "plan-logic", "binding": "specified", "status": "drafted",
        "rule": "test", "rules": [{
            "kind": "topology", "effect": "suppresses",
            "statement": "test", "why": "test",
            "suppresses": {"room": "parlor", "key": "must_adjoin", "target": "entrance-hall"}}]}
    assert fatals(patched) == []


def test_the_checker_refuses_a_suppression_of_a_rule_that_is_not_there():
    """Suppressing a rule that does not exist switches nothing off and says nothing about it."""
    import sys
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import check_kits
    rooms = {"parlor": json.load(open(os.path.join(ROOT, "rooms", "parlor.json")))}
    rule_slots = {"room_adjacency_overrides": "rule"}

    def run(sup, effect="suppresses"):
        errs, warns = [], []
        k = {"slots": {"room_adjacency_overrides": {"rules": [
            {"kind": "topology", "effect": effect, "statement": "s", "suppresses": sup}]}}}
        if sup is None: k["slots"]["room_adjacency_overrides"]["rules"][0].pop("suppresses")
        check_kits.check_rule_blocks(errs, warns, "t", k, rule_slots, rooms)
        return errs

    assert run({"room": "parlor", "key": "must_adjoin", "target": "entrance-hall"}) == []
    assert any("states no such rule" in e for e in
               run({"room": "parlor", "key": "must_adjoin", "target": "boiler-room"}))
    assert any("not in rooms/" in e for e in
               run({"room": "no-such-room", "key": "must_adjoin", "target": "entrance-hall"}))
    assert any("only as prose" in e for e in run(None))
    assert any("effect is 'adds'" in e for e in
               run({"room": "parlor", "key": "must_adjoin", "target": "entrance-hall"}, effect="adds"))


def test_a_suppression_is_inherited_down_the_style_chain(plan_check_module):
    """A suppression is a fact about a tradition, and a descendant that did not restate it has
    not thereby reinstated the rule."""
    C = {"kits": {"anc": {"slots": {"room_adjacency_overrides": {"rules": [{
        "kind": "topology", "effect": "suppresses", "statement": "s", "why": "w",
        "suppresses": {"room": "parlor", "key": "must_adjoin", "target": "entrance-hall"}}]}}}}}
    assert plan_check_module.kit_suppressions(["child", "anc"], C) == {
        ("parlor", "must_adjoin", "entrance-hall")}
    assert plan_check_module.kit_suppressions(["child"], C) == set()
