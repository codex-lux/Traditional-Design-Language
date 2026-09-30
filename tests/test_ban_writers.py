"""Who wrote each ban (WP-16.2, R3 of 29 Sep 2026, stage 1).

Lucas ruled that the elevation refuses what a style's resolved kit forbids, AND NAMES THE NODE
EACH BAN COMES FROM. Every reader of "where does this ban come from" read the resolved slot's
`_source`, and `_source` is the NEAREST node to touch the slot: where the style itself `extends`
a slot an ancestor wrote a ban in, the ban read as the style's own. colonial-revival's doorcase was
the case. gothic-revival-british wrote `pilasters-and-entablature` forbidden, colonial-revival
extended the slot to add rows of its own, and census V2 said "doorcase (door_surround: own)".
(Stage 2 bound that slot in colonial-revival's own kit on 30 Sep 2026, so the corpus no longer
carries this case; the synthetic kits below still do.)

`resolve_slots` now records `_bound_by` on every slot, the node whose record set the binding, and
`_written_by` on every variant row, the node whose record or delta wrote it. `forbidden_by` is
the one spelling of who forbids a feature.

The mechanism is driven on SYNTHETIC kits, because WP-16.2's own adjudication moves the corpus
cases (the ruling's own example is colonial-revival binding its own doorcase), and a guard pinned
to a case the package is about to fix goes quiet the day it is fixed. The corpus is held by a
census that is true whatever the adjudication decides: every forbidden row's writer states that
row, forbidden, in its own kit file.
"""
import glob
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import modcache  # noqa: E402

RK = modcache.load("resolve_kit", os.path.join(ROOT, "build", "resolve_kit.py"))

SLOT = "door_surround"


def _graph(chain):
    return {"nodes": {n: {} for n in chain},
            "slots": [{"id": SLOT, "group": "openings", "name": "Door surround"}]}


def _resolve(monkeypatch, kits, chain):
    """Resolve one slot for chain[0] over synthetic kit files, nearest first."""
    monkeypatch.setattr(RK, "load_kit", lambda nid: kits.get(nid, {}))
    slots, _ = RK.resolve_slots(_graph(chain), chain)
    return slots[SLOT]


def _rows(rec):
    return [(v["id"], v.get("status"), v.get("_written_by")) for v in rec.get("variants") or []]


class TestTheResolverRecordsTheWriter:
    CHAIN = ["child", "parent", "root"]

    def _kits(self):
        return {
            "root": {SLOT: {"binding": "specified", "variants": [
                {"id": "pilasters-and-entablature", "status": "forbidden"},
                {"id": "plain-casing", "status": "canonical"},
                {"id": "gibbs-surround", "status": "permitted"}]}},
            "parent": {SLOT: {"binding": "extends", "variants": [
                {"op": "replace", "id": "plain-casing", "status": "permitted"},
                {"op": "add", "id": "fanlight-over-door", "status": "forbidden"}]}},
            "child": {SLOT: {"binding": "extends", "parameters": {"x": {"value": 1}},
                             "variants": [{"op": "remove", "id": "gibbs-surround"}]}},
        }

    def test_each_row_carries_the_node_that_wrote_it(self, monkeypatch):
        rec = _resolve(monkeypatch, self._kits(), self.CHAIN)
        assert _rows(rec) == [
            ("pilasters-and-entablature", "forbidden", "root"),
            ("plain-casing", "permitted", "parent"),
            ("fanlight-over-door", "forbidden", "parent"),
        ], rec["variants"]

    def test_the_binding_is_credited_to_the_base_and_source_is_unchanged(self, monkeypatch):
        """`_source` still names the nearest node to touch the slot, which is what it has
        always answered; `_bound_by` is the base the deltas merged onto."""
        rec = _resolve(monkeypatch, self._kits(), self.CHAIN)
        assert rec["_source"] == "child"
        assert rec["_source_chain"] == ["root", "parent", "child"]
        assert rec["_bound_by"] == "root"

    def test_forbidden_by_names_the_writer_and_not_the_nearest_node(self, monkeypatch):
        rec = _resolve(monkeypatch, self._kits(), self.CHAIN)
        assert RK.forbidden_by(rec, ("pilasters-and-entablature",)) == ["root"]
        assert RK.forbidden_by(rec, ("fanlight",)) == ["parent"]
        assert RK.forbidden_by(rec, ("pilasters", "fanlight")) == ["parent", "root"]
        # a feature one of whose matching rows is not forbidden is not forbidden
        assert RK.forbidden_by(rec, ("casing", "fanlight")) is None
        # no words: the question is the slot's alone, and the slot is not forbidden
        assert RK.forbidden_by(rec) is None
        # words that match nothing forbid nothing
        assert RK.forbidden_by(rec, ("keystone",)) is None

    def test_a_restated_ban_is_credited_to_the_node_that_restated_it(self, monkeypatch):
        kits = self._kits()
        kits["child"][SLOT]["variants"].append(
            {"op": "replace", "id": "pilasters-and-entablature", "status": "forbidden",
             "note": "restated with the child's own reason"})
        rec = _resolve(monkeypatch, kits, self.CHAIN)
        assert RK.forbidden_by(rec, ("pilasters-and-entablature",)) == ["child"]

    def test_a_forbidden_binding_extended_by_a_child_is_the_bases(self, monkeypatch):
        """colonial-revival's `cornice_return` was this shape until stage 2 bound the slot in its
        own kit (30 Sep 2026): gothic-revival-american binds the slot forbidden and colonial-revival
        extended it with a rule that PERMITS a return, which a delta cannot do -- a delta cannot
        change a binding."""
        kits = {"root": {SLOT: {"binding": "forbidden", "note": "bargeboards"}},
                "child": {SLOT: {"binding": "extends", "rule_append": "a return is permitted"}}}
        rec = _resolve(monkeypatch, kits, ["child", "root"])
        assert rec["binding"] == "forbidden"
        assert rec["_source"] == "child"
        assert rec["_bound_by"] == "root"
        assert RK.forbidden_by(rec) == ["root"]
        assert RK.forbidden_by(rec, ("anything",)) == ["root"]

    def test_an_open_slot_is_bound_by_nobody(self, monkeypatch):
        rec = _resolve(monkeypatch, {}, ["child", "root"])
        assert rec["binding"] == "open"
        assert rec["_bound_by"] is None
        assert RK.forbidden_by(rec) is None

    def test_a_record_the_resolver_did_not_produce_names_no_writer(self):
        """A raw record carries no writer, and the answer says so rather than guessing one."""
        assert RK.forbidden_by({"binding": "forbidden", "_source": "someone"}) == ["?"]
        raw = {"binding": "specified", "variants": [{"id": "x", "status": "forbidden"}]}
        assert RK.forbidden_by(raw, ("x",)) == ["?"]
        assert RK.forbidden_by(None) is None


class TestTheCensusNamesTheWriter:
    def test_v2_reads_the_writer_not_the_nearest_node(self):
        C = pytest.importorskip("svg_census")
        slots = {SLOT: {"binding": "specified", "_source": "colonial-revival",
                        "_bound_by": "gothic-revival-british",
                        "variants": [{"id": "pilasters-and-entablature", "status": "forbidden",
                                      "_written_by": "gothic-revival-british"}]}}
        assert C._forbidden(slots, SLOT, ("pilasters-and-entablature",)) == ["gothic-revival-british"]
        assert C._ban_label("colonial-revival", ["gothic-revival-british"]) == \
            "inherited from gothic-revival-british"

    def test_the_three_labels(self):
        C = pytest.importorskip("svg_census")
        assert C._ban_label("a", ["a"]) == "own"
        assert C._ban_label("a", ["b", "c"]) == "inherited from b, c"
        assert C._ban_label("a", ["a", "b"]) == "own and inherited from b"


def _kit_file(nid):
    p = os.path.join(ROOT, "kits", nid + ".kit.json")
    return json.load(open(p, encoding="utf-8")).get("slots", {}) if os.path.exists(p) else {}


@pytest.fixture(scope="module")
def resolved():
    g = RK.load_graph()
    out = {}
    for nid in sorted(n for n in g["nodes"] if RK.load_kit(n)):
        chain = RK.chain_for(g, nid)
        slots, _ = RK.resolve_slots(g, chain, RK.scope_for(g, nid))
        out[nid] = (chain, slots)
    return out


class TestTheCorpus:
    """Over every node's resolved kit, the writers are real: each is a node in the chain, and
    each forbidden row's writer states that row, forbidden, in its own kit file."""

    def test_every_slot_and_row_carries_a_writer_in_its_own_chain(self, resolved):
        n_rows = 0
        for nid, (chain, slots) in resolved.items():
            for sid, rec in slots.items():
                assert "_bound_by" in rec, (nid, sid)
                if rec["binding"] == "open" and not rec.get("_source_chain"):
                    assert rec["_bound_by"] is None, (nid, sid)
                    continue
                assert rec["_bound_by"] in chain, (nid, sid, rec["_bound_by"])
                for v in rec.get("variants") or []:
                    assert v.get("_written_by") in chain, (nid, sid, v)
                    n_rows += 1
        assert n_rows > 1000, "the census read almost no variant rows; its premise has moved"

    def test_every_ban_is_stated_by_the_node_it_is_credited_to(self, resolved):
        """The writer's own kit file carries the row, forbidden -- as a specified record's row
        or as a delta's add or replace. A writer that cannot be found in its own file is an
        attribution the resolver invented."""
        checked = 0
        for nid, (chain, slots) in resolved.items():
            for sid, rec in slots.items():
                if rec.get("binding") == "forbidden":
                    own = _kit_file(rec["_bound_by"]).get(sid) or {}
                    assert own.get("binding") == "forbidden", (nid, sid, rec["_bound_by"])
                    checked += 1
                for v in rec.get("variants") or []:
                    if v.get("status") != "forbidden":
                        continue
                    own = _kit_file(v["_written_by"]).get(sid) or {}
                    stated = [r for r in own.get("variants") or []
                              if r.get("id") == v["id"] and r.get("status") == "forbidden"
                              and r.get("op", "add") in ("add", "replace")]
                    assert stated, (nid, sid, v["id"], v["_written_by"])
                    checked += 1
        assert checked > 500, "the census judged almost no bans; its premise has moved"

    def test_the_nearest_node_is_not_always_the_writer(self, resolved):
        """The premise of the whole package, asserted rather than assumed: somewhere in the
        corpus a forbidden row sits in a slot whose `_source` is the style itself and whose writer
        is an ancestor. If this ever fails, `_source` and the writer have become the same thing
        and the attribution census below says nothing."""
        differ = [(nid, sid, v["id"]) for nid, (_c, slots) in resolved.items()
                  for sid, rec in slots.items() if rec.get("_source") == nid
                  for v in rec.get("variants") or []
                  if v.get("status") == "forbidden" and v.get("_written_by") != nid]
        assert differ, "no ban is misattributed by `_source` any more"


class TestTheAdjudicationOf30September:
    """WP-16.2 stage 2: each wrong inherited ban corrected in the style's own kit (R3), on the
    records' own words and Lucas's answers of 30 Sep 2026 (A1-A10, recorded in
    `oq/an-inherited-ban-decides-what-the-elevation-may-draw`).

    Pinned as OUTCOMES -- who, if anyone, forbids each ruled feature now -- read through
    `forbidden_by`, the one reader the census and the refusal share. These are rulings, not
    measurements, so a later edit that moves one fails here and must read the ruling first. The
    mechanism itself stays driven on synthetic kits above; this class holds the corpus to what was
    decided."""

    # (style, slot, words, the writers forbidden_by must name, or None where nothing forbids it)
    CASES = [
        # the nine adjudicated edits, and the four companions the independent check wrote
        ("colonial-revival", "door_surround", ("pilasters-and-entablature",), None),
        ("colonial-revival", "cornice_return", None, None),
        ("colonial-revival", "cornice", ("modillion",), None),
        ("minimal-traditional", "cornice", ("modillion",), ["minimal-traditional"]),
        ("minimal-traditional", "cornice_return", None, ["minimal-traditional"]),
        ("cape-cod-revival", "water_table", None, None),
        ("new-classical", "water_table", None, None),
        ("georgian-revival", "water_table", None, None),
        ("garrison-revival", "cornice", ("modillion",), ["garrison-revival"]),
        ("garrison-revival", "door_surround", ("engaged-columns",), ["garrison-revival"]),
        ("neo-eclectic", "cornice", ("dentil",), None),
        ("minimal-traditional", "frieze", None, None),
        ("modern-farmhouse-traditional", "cornice_return", None, None),
        # A1: colonial-revival's own trim, and the descendants the ruling says inherit it
        ("colonial-revival", "water_table", None, None),
        ("colonial-revival", "belt_course", None, None),
        ("colonial-revival", "frieze", None, None),
        ("georgian-revival", "frieze", None, None),
        ("neoclassical-revival", "water_table", None, None),
        # A2: the silence, permitted and unsettled
        ("second-empire", "transom_sidelight", ("sidelight",), None),
        ("italian-renaissance-revival", "transom_sidelight", ("sidelight",), None),
        ("italianate-townhouse", "transom_sidelight", ("sidelight",), None),
        # A4: the Italianate family's own bans
        ("italian-renaissance-revival", "door_surround", ("pilasters-and-entablature",),
         ["italian-renaissance-revival"]),
        ("italianate-townhouse", "door_surround", ("pilasters-and-entablature",),
         ["italianate-townhouse"]),
        ("second-empire", "door_surround", ("pilasters-and-entablature",), ["second-empire"]),
        ("renaissance-revival-american", "door_surround", ("pilasters-and-entablature",),
         ["renaissance-revival-american"]),
        ("italian-renaissance-revival", "cornice_return", None, ["italian-renaissance-revival"]),
        ("italianate-townhouse", "cornice_return", None, ["italianate-townhouse"]),
        ("second-empire", "cornice_return", None, ["second-empire"]),
        ("renaissance-revival-american", "cornice_return", None, ["renaissance-revival-american"]),
        ("renaissance-revival-american", "transom_sidelight", ("sidelight",),
         ["renaissance-revival-american"]),
        ("renaissance-revival-american", "transom_sidelight", ("fanlight",),
         ["renaissance-revival-american"]),
        # A5: the Cape and the saltbox keep a transom and refuse sidelights, in their own words
        ("cape-cod-colonial", "transom_sidelight", ("sidelight",), ["cape-cod-colonial"]),
        ("cape-cod-colonial", "transom_sidelight", ("transom",), None),
        ("saltbox-colonial", "transom_sidelight", ("sidelight",), ["saltbox-colonial"]),
        ("saltbox-colonial", "transom_sidelight", ("transom",), None),
        # A6: the Jeffersonian keystone keeps tidewater-georgian's ban, named as its writer
        ("jeffersonian-classicism", "window_head_masonry", ("keyed", "keystone"),
         ["tidewater-georgian"]),
        # A7 and A8: new-urbanist-traditional's cornice, frieze and return
        ("new-urbanist-traditional", "cornice", None, None),
        ("new-urbanist-traditional", "cornice", ("modillion",), ["new-urbanist-traditional"]),
        ("new-urbanist-traditional", "frieze", None, None),
        ("new-urbanist-traditional", "cornice_return", None, None),
        # A9: minimal-traditional's water table inherits A1's permitted record; nothing forbids it
        ("minimal-traditional", "water_table", None, None),
        # the four companions the second check wrote, where a descendant's own words contradict
        # what the twenty would hand it
        ("cape-cod-revival", "frieze", None, ["cape-cod-revival"]),
        ("cape-cod-revival", "belt_course", None, ["cape-cod-revival"]),
        ("mediterranean-revival", "door_surround", ("pilasters-and-entablature",), None),
        ("minimal-traditional", "belt_course", None, ["minimal-traditional"]),
        # ...and where minimal-traditional's belt ban reaches, the two descendants whose own words
        # the check found support it, weakly
        ("ranch-style", "belt_course", None, ["minimal-traditional"]),
        ("modern-farmhouse-traditional", "belt_course", None, ["minimal-traditional"]),
        # A10: neo-eclectic binds its own belt course, so that ban does not reach it
        ("neo-eclectic", "belt_course", None, None),
    ]

    @pytest.mark.parametrize("style,slot,words,writers", CASES,
                             ids=["%s:%s:%s" % (c[0], c[1], "+".join(c[2] or ("slot",)))
                                  for c in CASES])
    def test_the_ruled_outcome_holds(self, resolved, style, slot, words, writers):
        rec = resolved[style][1][slot]
        assert RK.forbidden_by(rec, words) == writers, (
            f"{style}.{slot} {words or ''}: forbidden_by reads {RK.forbidden_by(rec, words)}, the "
            f"ruling says {writers}. The binding is {rec.get('binding')} (bound by "
            f"{rec.get('_bound_by')}); read the ruling before moving either.")

    # Every slot the adjudication bound at the style itself: the nine edits, the three the check
    # amended among them, the four companions, the twenty records of Lucas's answers, the four
    # companions the second check wrote, and neo-eclectic's belt course (A10).
    # garrison-revival's `door_surround` is the one delta, held by its row in CASES.
    SELF_BOUND = [
        ("cape-cod-revival", "water_table"), ("colonial-revival", "cornice"),
        ("colonial-revival", "cornice_return"), ("colonial-revival", "door_surround"),
        ("garrison-revival", "cornice"), ("georgian-revival", "water_table"),
        ("minimal-traditional", "cornice"), ("minimal-traditional", "cornice_return"),
        ("minimal-traditional", "frieze"), ("modern-farmhouse-traditional", "cornice_return"),
        ("neo-eclectic", "cornice"), ("new-classical", "water_table"),
        ("cape-cod-colonial", "transom_sidelight"), ("colonial-revival", "belt_course"),
        ("colonial-revival", "frieze"), ("colonial-revival", "water_table"),
        ("italian-renaissance-revival", "cornice_return"),
        ("italian-renaissance-revival", "door_surround"),
        ("italian-renaissance-revival", "transom_sidelight"),
        ("italianate-townhouse", "cornice_return"), ("italianate-townhouse", "door_surround"),
        ("italianate-townhouse", "transom_sidelight"),
        ("new-urbanist-traditional", "cornice"), ("new-urbanist-traditional", "cornice_return"),
        ("new-urbanist-traditional", "frieze"),
        ("renaissance-revival-american", "cornice_return"),
        ("renaissance-revival-american", "door_surround"),
        ("renaissance-revival-american", "transom_sidelight"),
        ("saltbox-colonial", "transom_sidelight"), ("second-empire", "cornice_return"),
        ("second-empire", "door_surround"), ("second-empire", "transom_sidelight"),
        # the second check's four companions, and neo-eclectic's belt course (A10)
        ("cape-cod-revival", "belt_course"), ("cape-cod-revival", "frieze"),
        ("mediterranean-revival", "door_surround"), ("minimal-traditional", "belt_course"),
        ("neo-eclectic", "belt_course"),
    ]

    def test_no_ruled_slot_is_left_to_a_writer_the_ruling_replaced(self, resolved):
        """Binding a slot at the style replaces the whole inherited record, not only the row the
        ruling was about. The four Italianate-family door surrounds resolved gothic-revival-british's
        WHOLE record, a pointed-arch buttressed porch canonical; neo-eclectic's cornice would have
        inherited colonial-revival's modillions canonical, which `forbidden_by` cannot see because
        a canonical row forbids nothing. So every slot is held to its own style: the binding, and
        every row, written there and nowhere else."""
        assert len(self.SELF_BOUND) == 37
        for sid, slot in self.SELF_BOUND:
            rec = resolved[sid][1][slot]
            assert rec["_bound_by"] == sid, (sid, slot, rec["_bound_by"])
            rows = {v["_written_by"] for v in rec.get("variants") or []}
            assert rows <= {sid}, (sid, slot, rec["variants"])


def _elevation(plan_path, dormer):
    """The elevation of a shipped plan with its dormers declared, on the search (deterministic)."""
    L = lambda n: modcache.load(n, os.path.join(ROOT, "build", n + ".py"))  # noqa: E731
    G, ST, RF, EL = (L(n) for n in ("geometry", "structure", "roof", "elevation"))
    p = json.load(open(os.path.join(ROOT, plan_path), encoding="utf-8"))
    p.setdefault("declared", {})["dormer"] = dormer
    placed = G.solve(p, engine="heuristic")
    sec = ST.build_section(placed, None, geometry_result=placed)
    rf = RF.build_roof(placed, None, section=sec)
    el = EL.build_elevation(placed, None, section=sec, roof=rf)
    assert "error" not in el and el.get("applicable", True), el.get("error")
    return EL, el


class TestTheDormerLineNamesTheWriter:
    """The elevation's dormer line said where the variant came from by reading the slot's
    `_source`, so a style that extends its dormer slot and inherits the variant was said to have
    written it, and the line stayed silent. No shipped plan declares dormers, so both branches
    are driven by declaring three on a shipped plan."""

    def test_a_style_that_extends_the_slot_is_told_the_variant_is_inherited(self, resolved):
        chain, slots = resolved["greek-revival-american"]
        rec = slots["dormer"]
        # the premise: the style touches the slot, so `_source` names it and the old line was silent
        assert rec["_source"] == "greek-revival-american", rec["_source_chain"]
        gabled = [v for v in rec["variants"] if v["id"] == "gabled"]
        assert gabled and gabled[0]["_written_by"] != "greek-revival-american"
        EL, el = _elevation("plans/reference/good-03-parlor-drawing-room-house.json",
                            {"count": 3, "variant": "gabled"})
        d = el["dormers"]
        assert d["variant_source_node"] == gabled[0]["_written_by"]
        assert d["slot_extended_here"] is True
        lines = [n for n in EL.face_notes(el, el["entrance_face"]) if n.startswith("DORMER VARIANT")]
        assert lines == [f'DORMER VARIANT “GABLED” IS INHERITED FROM '
                         f'{gabled[0]["_written_by"].replace("-", " ").upper()} — THIS STYLE '
                         f'EXTENDS THE SLOT AND DOES NOT RESTATE IT'], lines

    def test_a_style_that_binds_the_slot_nothing_is_told_so(self, resolved):
        chain, slots = resolved["tidewater-georgian"]
        rec = slots["dormer"]
        assert "tidewater-georgian" not in rec["_source_chain"], rec["_source_chain"]
        EL, el = _elevation("plans/tidewater-georgian-careful.json",
                            {"count": 3, "variant": "gabled"})
        assert el["dormers"]["slot_extended_here"] is False
        lines = [n for n in EL.face_notes(el, el["entrance_face"]) if n.startswith("DORMER VARIANT")]
        assert len(lines) == 1 and lines[0].endswith("THIS STYLE BINDS THE SLOT NOTHING (OQ 51)"), lines

    def test_a_declared_variant_the_kit_does_not_list_is_credited_to_nobody(self):
        EL, el = _elevation("plans/reference/good-03-parlor-drawing-room-house.json",
                            {"count": 3, "variant": "not-a-listed-dormer"})
        assert el["dormers"].get("variant_source_node") is None
        assert not [n for n in EL.face_notes(el, el["entrance_face"])
                    if n.startswith("DORMER VARIANT “NOT")]
