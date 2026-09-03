"""WP-4.3. The garage, and the one fatal it exists to make unreachable.

The acceptance line in PLAN-OF-ACTION.md is unusually specific: "The spec
Colonial's garage-beside-primary-bedroom fatal cannot be reproduced by the
composer." That fatal is real and it is in the corpus -- `plans/spec-builder-
colonial.json` puts a two-car garage against the primary bedroom, and
plan_check reports it fatal, because rooms/garage.json forbids the adjacency
outright ("a bedroom over or beside a garage is a noise, fume and fire-
separation problem in one, and the fire separation is code").

The point of this package is not that the validator catches it -- it already
did. The point is that the composer should be structurally incapable of
PRODUCING it. That difference is the whole design: placing a garage by
adjacency asks "what may it touch?", and every locally plausible answer to that
question is how the spec plan ended up as it is. Placing it by the
`garage-and-hyphen` grouping's own `attaches_to` asks "where does a dependency
land on this skeleton?", and the garage ends up with exactly one interior
neighbour -- a threshold room -- so the bedroom question never arises.

These tests pin that property, not the mechanism that happens to deliver it.
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
if BUILD not in sys.path:
    sys.path.insert(0, BUILD)

SLEEPING = ("primary-bedroom", "bedroom", "bedchamber", "nursery", "garret-chamber")


def _garage_neighbours(plan):
    """Every room id the garage shares a door or a declared adjacency with."""
    rooms = {r["id"]: r for lv in plan["levels"] for r in lv["rooms"]}
    garages = [r["id"] for r in rooms.values() if r["type"] == "garage"]
    out = {}
    for gid in garages:
        near = set()
        for d in rooms[gid].get("doors", []):
            if d["to"] != "exterior":
                near.add(d["to"])
        for r in rooms.values():
            if any(d.get("to") == gid for d in r.get("doors", [])):
                near.add(r["id"])
        for a in plan.get("adjacencies", []):
            if a.get("a") == gid:
                near.add(a["b"])
            if a.get("b") == gid:
                near.add(a["a"])
        out[gid] = {rooms[n]["type"] for n in near if n in rooms}
    return out


def test_the_spec_colonial_fatal_is_still_real():
    """The guard on the guard. If this stops being fatal, the test below is
    passing for the wrong reason and proves nothing."""
    import plan_check

    plan = json.load(open(os.path.join(ROOT, "plans", "spec-builder-colonial.json")))
    res = plan_check.check(plan, plan_check.load_corpus())
    fatals = [f for f in res["findings"] if f["severity"] == "fatal"]
    assert any("garage" in f["statement"].lower() and "bedroom" in f["statement"].lower()
               for f in fatals), "the hand-authored spec Colonial no longer trips the garage fatal"


@pytest.mark.parametrize("brief_id", ["family-georgian", "bungalow-small"])
def test_composer_never_puts_a_garage_next_to_a_bedroom(brief_id):
    """THE acceptance criterion. Every candidate, every level, every brief."""
    import compose

    brief = json.load(open(os.path.join(ROOT, "briefs", f"{brief_id}.json")))
    for cand in compose.compose(brief, candidates=4, revise=False)["candidates"]:
        plan = cand.get("plan") or cand
        if "levels" not in plan:
            continue
        for gid, neighbours in _garage_neighbours(plan).items():
            bad = neighbours & set(SLEEPING)
            assert not bad, f"{brief_id}/{cand.get('parti')}: {gid} adjoins {bad}"


def test_composed_garage_has_exactly_one_interior_neighbour():
    """The structural property the acceptance rests on. A garage with one
    interior neighbour cannot touch a bedroom by construction; a garage with
    several is back to being placed by adjacency, and the guarantee is gone
    even if this particular run happens to come out clean."""
    import compose

    brief = json.load(open(os.path.join(ROOT, "briefs", "family-georgian.json")))
    seen = 0
    for cand in compose.compose(brief, candidates=4, revise=False)["candidates"]:
        plan = cand.get("plan") or cand
        if "levels" not in plan:
            continue
        for gid, neighbours in _garage_neighbours(plan).items():
            seen += 1
            assert len(neighbours) == 1, f"{gid} has interior neighbours {neighbours}"
            assert neighbours == {"mudroom"}, (
                f"{gid} lands on {neighbours}; the corpus's own service sequence "
                f"(rooms/back-hall.json: 'garage, mudroom, back hall, kitchen') puts a "
                f"threshold room between the car and the house")
    assert seen, "no candidate carried a garage — the test proved nothing"


def test_garage_is_placed_by_attachment_not_by_adjacency():
    """A garage may only be attached where garage-and-hyphen records an
    attachment for that massing, and never where it records `forbidden`."""
    import compose

    G = json.load(open(os.path.join(ROOT, "groupings", "garage-and-hyphen.json")))
    allowed = {a["massing"] for a in G["attaches_to"] if a.get("fit") != "forbidden"}
    forbidden = {a["massing"] for a in G["attaches_to"] if a.get("fit") == "forbidden"}
    assert forbidden, "the grouping should record at least one massing it refuses"

    brief = json.load(open(os.path.join(ROOT, "briefs", "family-georgian.json")))
    for cand in compose.compose(brief, candidates=4, revise=False)["candidates"]:
        plan = cand.get("plan") or cand
        if "levels" not in plan:
            continue
        has_garage = any(r["type"] == "garage" for lv in plan["levels"] for r in lv["rooms"])
        massing = plan.get("massing")
        if has_garage:
            assert massing in allowed, f"garage placed on {massing}, which the grouping does not receive"
            assert "garage-and-hyphen" in (plan.get("groupings") or []), \
                "a placed garage must record the grouping that placed it"


def test_composer_refuses_rather_than_guesses_when_the_massing_has_no_attachment():
    """The refusal matters as much as the placement -- decision 10's spirit, and
    the reason side-hall-double-pile (a party-walled town house diagram, which
    the grouping deliberately does not receive) gets a stated JUDGMENT rather
    than a garage tucked somewhere plausible."""
    import compose

    brief = json.load(open(os.path.join(ROOT, "briefs", "family-georgian.json")))
    plan, log, _ = compose.instantiate("side-hall-townhouse", brief)
    assert not any(r["type"] == "garage" for lv in plan["levels"] for r in lv["rooms"])
    assert any("garage" in line.lower() and ("JUDGMENT" in line or "REFUSED" in line)
               for line in log), "a refusal must be stated in the decision log, not silent"


def test_every_living_style_specifies_a_garage_strategy():
    """docs/inheritance.md: garage_strategy 'should be `specified` on every
    contemporary buildable variant'. WP-4.3's other half."""
    tax = json.load(open(os.path.join(ROOT, "dist", "taxonomy.json")))
    nodes = tax["nodes"] if "nodes" in tax else tax
    missing = []
    for nid, node in nodes.items():
        if node.get("rank") not in ("style", "variant") or node.get("status") != "living":
            continue
        path = os.path.join(ROOT, "kits", f"{nid}.kit.json")
        if not os.path.exists(path):
            missing.append(nid)
            continue
        slot = json.load(open(path))["slots"].get("garage_strategy", {})
        if slot.get("binding") not in ("specified", "extends", "forbidden"):
            missing.append(nid)
    assert not missing, f"living styles with no garage_strategy of their own: {missing}"


def test_the_garage_grouping_forbids_the_bedroom_adjacency_in_its_own_rules():
    """The rule should live in the data, not only in the composer's code, or a
    second generator written against this corpus inherits none of it."""
    G = json.load(open(os.path.join(ROOT, "groupings", "garage-and-hyphen.json")))
    hard = [r for r in G["internal_rules"] if r.get("severity") == "hard"]
    assert any("bedroom" in r["statement"].lower() for r in hard), \
        "garage-and-hyphen must state the bedroom prohibition as a hard rule of its own"


def test_no_parti_declares_a_garage_room_without_the_grouping_that_governs_it():
    """The invariant one level up from test_garage_is_placed_by_attachment_not_by_adjacency,
    which can only see the partis a brief happens to return.

    WP-4.3 made `garage-and-hyphen` the ONE attachment mechanism. A parti that writes a garage
    room into its own `rooms` list and does not declare the grouping gets a garage that no
    grouping placed and no grouping governs — `attach_garage()` sees the room already there and
    returns before it can record anything. Two partis were in that state (`five-part-palladian`
    and `ranch-tripartite`) and neither was caught, because neither had ever been returned by
    the two shipped briefs. The scoring change of 26 Aug 2026 moved `five-part-palladian` into
    family-georgian's four and the older test fired immediately. Checked against the data here
    so it does not depend on which diagrams a brief happens to rank.
    """
    import glob
    grouping = json.load(open(os.path.join(ROOT, "groupings", "garage-and-hyphen.json")))
    receives = {a["massing"] for a in grouping["attaches_to"] if a.get("fit") != "forbidden"}
    offenders = []
    for path in sorted(glob.glob(os.path.join(ROOT, "partis", "*.json"))):
        parti = json.load(open(path))
        if not any(r["type"] == "garage" for r in parti["rooms"]):
            continue
        if "garage-and-hyphen" not in (parti.get("groupings") or []):
            offenders.append(parti["id"])
            continue
        massings = {parti["massing"]} | set(parti.get("alternate_massings") or [])
        # `<=`, not `&`. The message has always described `<=` — "the grouping layer will
        # report it on every plan" is what happens for EACH massing the grouping has no
        # recorded fit for, not only when it receives none of them. With `&` the assertion
        # could not fail on either parti and never distinguished anything; with `<=` it
        # failed at once on ranch-tripartite's `split-level`, which the grouping omitted while
        # receiving ranch-l and ranch-linear. Found by an independent audit of this test.
        assert massings <= receives, (
            f'{parti["id"]} declares garage-and-hyphen and the grouping records no fit for '
            f'{sorted(massings - receives)} — plan_check.py emits an info finding for each, '
            f'on every plan built from this diagram')
    assert not offenders, (
        f"these partis carry a garage room that no grouping governs: {offenders}. "
        f"Add garage-and-hyphen to their groupings, or remove the room and let "
        f"attach_garage() place it against the massing.")


class TestTheHyphenIsARoom:
    """OQ 40 / oq/the-parti-dissolved-its-own-dependencies, ruled 3 Sep 2026.

    The link between the house and a dependency is a ROOM, and which room is chosen by style.
    Before this it was a property of the attachment whose length lived in a local variable used
    only inside two f-strings -- which is why `hyphen_length_ft`, a strong machine-tested rule in
    BOTH hyphen groupings, had never been evaluated on any plan this composer produced."""

    @staticmethod
    def _brief():
        import json, os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return json.load(open(os.path.join(root, "briefs", "family-georgian.json")))

    def test_the_link_is_a_room_in_the_record(self, compose_module):
        plan, _log, _p = compose_module.instantiate("centre-passage-double-pile", self._brief())
        hy = [r for lv in plan["levels"] for r in lv["rooms"] if r.get("hyphen")]
        assert len(hy) == 1, "exactly one room is the link"
        assert hy[0]["type"] in ("breezeway", "gallery-corridor")
        assert hy[0].get("block"), "the link belongs to the dependency it links to"

    def test_the_links_width_is_hyphen_length_ft_and_is_inside_both_bands(self, compose_module):
        """The figure the rule tests. It must satisfy the GROUPING's 12-20 ft band and the
        ROOM's own width band at once -- a link inside one and outside the other is a rule
        satisfied by breaking a record."""
        import json, os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        plan, _log, _p = compose_module.instantiate("centre-passage-double-pile", self._brief())
        hy = next(r for lv in plan["levels"] for r in lv["rooms"] if r.get("hyphen"))
        w = hy["width_ft"]
        assert 12.0 <= w <= 20.0, "outside garage-and-hyphen's own stated band"
        band = json.load(open(os.path.join(root, "rooms", hy["type"] + ".json")))["dimensions"]["width_ft"]
        assert band[0] <= w <= band[1], f"{w} is outside {hy['type']}'s own {band} ft band"

    def test_which_room_is_the_link_is_read_from_the_records_own_words(self, compose_module):
        """Not an authored table: `breezeway`'s style_variation names it "hyphen" for
        english-palladian and "hyphen or colonnade" for tidewater-georgian, and the Georgian
        chain reaches those. A style the room does not name gets the enclosed gallery."""
        t, why = compose_module.hyphen_room_type("tidewater-georgian")
        assert t == "breezeway" and "breezeway.json" in why
        assert compose_module.hyphen_room_type("craftsman")[0] == "gallery-corridor"

    def test_a_new_mudroom_keeps_its_kitchen_door_where_the_house_has_a_kitchen(self, compose_module):
        """THE REGRESSION THIS PACKAGE CAUSED AND CAUGHT. A first version moved the created
        mudroom into the dependency unconditionally, which cut the door to the kitchen that
        rooms/mudroom.json requires HARD -- so every parti with a kitchen began composing with a
        new fatal, 'Mudroom does not reach a kitchen through a direct door'. The mudroom belongs
        beside the kitchen when there is one; it moves out only when there is none."""
        plan, _log, _p = compose_module.instantiate("centre-passage-single-pile", self._brief())
        rooms = {r["id"]: r for lv in plan["levels"] for r in lv["rooms"]}
        mud = next((r for r in rooms.values() if r["type"] == "mudroom"), None)
        assert mud is not None, "this brief asks for garage bays, so a mudroom is created"
        kitchen = next((r for r in rooms.values() if r["type"] == "kitchen" and not r.get("block")), None)
        assert kitchen is not None, "the single-pile parti still has a kitchen"
        assert not mud.get("block"), "with a kitchen in the house the mudroom stays in the house"
        assert any(d.get("to") == kitchen["id"] for d in (mud.get("doors") or [])), (
            "the mudroom must keep the kitchen door its own hard rule requires")

    def test_no_door_is_authored_across_the_gap_between_two_elements(self, compose_module):
        """A door between rooms in different massing elements would be the drawing lying about
        the record -- there is a hyphen's width of outside air between them. Only the link
        itself may have a door at each end."""
        plan, _log, _p = compose_module.instantiate("centre-passage-double-pile", self._brief())
        rooms = {r["id"]: r for lv in plan["levels"] for r in lv["rooms"]}
        for r in rooms.values():
            if r.get("hyphen"):
                continue
            for d in (r.get("doors") or []):
                other = rooms.get(d.get("to"))
                if other is None or other.get("hyphen"):
                    continue
                assert (r.get("block") or None) == (other.get("block") or None), (
                    f"{r['id']} ({r.get('block') or 'main'}) is doored to {other['id']} "
                    f"({other.get('block') or 'main'}) across a gap, without the hyphen between")


class TestTheServiceProgrammeIsRelocatedNotDeleted:
    """OQ 40's other half. Stripping six service rooms out of centre-passage-double-pile moved a
    programme rather than deleting one -- the ruling says so in as many words -- and until
    `stock_the_dependency` existed the strip was half done: the shipped Georgian brief requires a
    breakfast room, the diagram no longer had a place for one, and the brief simply went unmet.

    The full suite caught it, as a `must_have` the revision loop was accused of dropping. It had
    not dropped it; it was never instantiated. A test whose failure message names the wrong
    culprit is still a test doing its job."""

    @staticmethod
    def _brief():
        import json, os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return json.load(open(os.path.join(root, "briefs", "family-georgian.json")))

    def test_a_must_have_service_room_lands_in_the_dependency(self, compose_module):
        brief = self._brief()
        plan, _log, _p = compose_module.instantiate("centre-passage-double-pile", brief)
        rooms = [r for lv in plan["levels"] for r in lv["rooms"]]
        types = {r["type"] for r in rooms}
        for must in brief["must_have"]:
            assert must in types, f"the brief requires {must} and it is nowhere in the plan"
        bk = next(r for r in rooms if r["type"] == "breakfast-room")
        assert bk.get("block"), (
            "the breakfast room belongs in the dependency -- the main block of this diagram holds "
            "no service programme, which is the arrangement its own exemplars use")

    def test_only_service_side_rooms_are_relocated(self, compose_module):
        """A dependency is where service goes. A brief asking for a drawing room the parti has no
        place for is a different conversation and must still reach the judgment log rather than
        being quietly built out in the wing."""
        brief = dict(self._brief(), must_have=["drawing-room", "music-room"])
        plan, log, _p = compose_module.instantiate("centre-passage-double-pile", brief)
        dep_types = {r["type"] for lv in plan["levels"] for r in lv["rooms"] if r.get("block")}
        assert "music-room" not in dep_types, "a music room is not service and must not be relocated"
        assert any("music room" in l and "no place" in l for l in log), (
            "the composer must still say plainly that it has no place for it")

    def test_nothing_is_relocated_when_there_is_no_dependency(self, compose_module):
        """No garage bays, no dependency, nothing to stock -- and the judgment `instantiate`
        already logs stands. This function refuses rather than inventing a dependency nobody
        asked for."""
        brief = dict(self._brief())
        brief["context"] = dict(brief.get("context") or {}, garage_bays=0)
        plan, log, _p = compose_module.instantiate("centre-passage-double-pile", brief)
        assert not [r for lv in plan["levels"] for r in lv["rooms"] if r.get("block")]
        assert any("breakfast room" in l and "no place" in l for l in log)
