"""WP-14.26 (tranche 2 PRD §C.7): one kit authority.

`mcp_server/core.py` carried two kit resolvers. `resolve_kit` -- served as `tdl_resolve_kit` and
`GET /api/kit` -- was a hand-merge over each node's own kit file, with its own `extends` merge and
its own idea of when the walk stops; `_resolved_kit` calls `build/resolve_kit.resolve_slots`, which
every checker, the elevation, the composer and the dossier read. Measured on `5aa8041` they
disagreed on 38 of the 15,908 (style, slot) pairs, on the binding, the canonical set or the
forbidden set. `resolve_kit` is the build's resolution now, and these guards hold it there:

- every row of every style is `resolve_slots`' answer, read here from the build module directly;
- the 38 pairs the rebase moved no longer answer what the hand-merge answered;
- `get_slot`'s `specified_by_styles` is the resolved list, so a style that FORBIDS a slot is never
  listed as specifying it (`oq/the-slot-tool-lists-a-style-that-forbids-a-slot-as-specifying-it`).

Each expectation is read off the build or the committed record of the move; no count is typed
here. Every guard was mutation-checked against the change it exists for (the report, §IV).
"""
import importlib.util
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from mcp_server import core  # noqa: E402

FIXTURE = os.path.join(ROOT, "tests", "fixtures", "kit_authority_moved_pairs.json")


@pytest.fixture(scope="module")
def build():
    """The build's resolver, loaded here by path rather than through core, so what the guards
    compare against is not the object under test."""
    spec = importlib.util.spec_from_file_location("rk_one_authority",
                                                  os.path.join(ROOT, "build", "resolve_kit.py"))
    rk = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rk)
    g = rk.load_graph()

    def resolved(style_id):
        return rk.resolve_slots(g, rk.chain_for(g, style_id), rk.scope_for(g, style_id))[0]
    return {"rk": rk, "graph": g, "resolved": resolved}


@pytest.fixture(scope="module")
def moved():
    with open(FIXTURE, encoding="utf-8") as fh:
        return json.load(fh)


def _chain_of(source):
    """The ancestors a served `source` string names, base first -- the string PARSED back, so the
    guard does not restate the expression that spelled it."""
    if source is None:
        return []
    return [p.replace(" (extends)", "").strip() for p in source.split(" + ")]


def _variants(rec, status):
    return [v.get("id") for v in (rec.get("variants") or []) if v.get("status") == status]


def _specifies(rec):
    b = rec.get("binding")
    return b == "specified" or (b == "extends" and bool(rec.get("_dangling_extends")))


# ------------------------------------------------------------------ resolve_kit is the build
def test_every_row_of_every_style_is_the_builds_resolution(build):
    D = core._data()
    styles = sorted(D["styles"])
    assert styles, "the premise: the corpus holds styles"
    checked = 0
    for sid in styles:
        want = build["resolved"](sid)
        got = core.resolve_kit(sid, only_specified=False)
        assert "error" not in got, (sid, got)
        rows = {r["slot"]: r for r in got["slots"]}
        # every slot of the ontology is answered, and nothing else is
        assert set(rows) == set(D["slots"]) == set(want), (
            sid, sorted(set(D["slots"]) ^ set(rows)))
        for slot_id, rec in want.items():
            r = rows[slot_id]
            where = f"{sid}/{slot_id}"
            assert r["binding"] == rec.get("binding"), (where, r["binding"], rec.get("binding"))
            assert r["canonical"] == _variants(rec, "canonical"), where
            assert r["forbidden"] == _variants(rec, "forbidden"), where
            assert r["rule"] == rec.get("rule"), where
            assert _chain_of(r["source"]) == list(rec.get("_source_chain") or []), (
                where, r["source"], rec.get("_source_chain"))
            checked += 1
        # the default payload is the same rows less exactly the open ones
        spec = core.resolve_kit(sid)
        assert [r["slot"] for r in spec["slots"]] == sorted(
            k for k, rec in want.items() if rec.get("binding") != "open"), sid
        assert spec["slots_returned"] == len(spec["slots"])
    assert checked == len(styles) * len(D["slots"]), "a style or a slot was skipped"


def test_an_open_slot_is_served_open_with_no_source(build):
    """A slot nothing in the cascade binds is `open` and names no source. The hand-merge named the
    writer of whichever `open` record it had stopped at, which is a slot the cascade walks PAST."""
    open_rows = [(sid, r) for sid in sorted(core._data()["styles"])
                 for r in core.resolve_kit(sid, only_specified=False)["slots"]
                 if r["binding"] == "open"]
    assert open_rows, "the premise: some style leaves some slot open"
    for sid, r in open_rows:
        assert r["source"] is None, (sid, r["slot"], r["source"])
        assert r["canonical"] == [] and r["forbidden"] == [], (sid, r["slot"])


# ------------------------------------------------------------------ the pairs the rebase moved
def test_the_record_of_the_move_is_a_record_of_movement(moved):
    """The committed fixture's premise, checked before it is leaned on: it holds pairs, each names
    what it differs on, and on each of those fields the hand-merge's answer really differs from the
    resolved one. A fixture whose two columns agreed would guard nothing."""
    pairs = moved["pairs"]
    assert pairs, "the fixture names no moved pair"
    causes = set(moved["causes"])
    for p in pairs:
        where = f"{p['style']}/{p['slot']}"
        assert p["cause"] in causes, (where, p["cause"])
        assert p["differs_on"], where
        for f in p["differs_on"]:
            h, r = p["hand_merge"][f], p["resolved"][f]
            if isinstance(h, list):
                h, r = sorted(h), sorted(r)
            assert h != r, (where, f)


def test_no_moved_pair_answers_what_the_hand_merge_answered(moved):
    """THE MUTATION TARGET: restore the hand-merge and this goes red on the moved pairs, because
    each one is served again as the hand-merge served it. Read as a relation, not a pin -- a later
    kit edit moving one of these slots again does not fail it unless it moves it BACK."""
    back = []
    for p in moved["pairs"]:
        got = core.resolve_kit(p["style"], slot=p["slot"], only_specified=False)["slots"]
        assert len(got) == 1, (p["style"], p["slot"])
        row = got[0]
        same = []
        for f in p["differs_on"]:
            h, r = p["hand_merge"][f], row[f]
            if isinstance(h, list):
                h, r = sorted(h), sorted(r)
            same.append(h == r)
        if all(same):
            back.append(f"{p['style']}/{p['slot']}")
    assert not back, f"{len(back)} moved pair(s) are served as the hand-merge served them: {back[:5]}"


def test_the_moved_pairs_are_served_as_the_build_resolves_them(build, moved):
    for p in moved["pairs"]:
        rec = build["resolved"](p["style"])[p["slot"]]
        row = core.resolve_kit(p["style"], slot=p["slot"], only_specified=False)["slots"][0]
        assert row["binding"] == rec.get("binding"), p["slot"]
        assert sorted(row["canonical"]) == sorted(_variants(rec, "canonical")), p["slot"]
        assert sorted(row["forbidden"]) == sorted(_variants(rec, "forbidden")), p["slot"]


# ------------------------------------------------------------------ get_slot reads the cascade
def test_get_slot_lists_exactly_the_styles_whose_resolved_kit_specifies_the_slot(build):
    D = core._data()
    styles = sorted(D["styles"])
    resolved = {sid: build["resolved"](sid) for sid in styles}
    forbidding_with_an_own_record = inherited = 0
    for slot_id in D["slots"]:
        want = [sid for sid in styles if _specifies(resolved[sid].get(slot_id) or {})]
        forbids = {sid for sid in styles
                   if (resolved[sid].get(slot_id) or {}).get("binding") == "forbidden"}
        got = core.get_slot(slot_id)["specified_by_styles"]
        assert got == want, (slot_id, sorted(set(got) ^ set(want))[:6])
        assert not set(got) & forbids, (slot_id, sorted(set(got) & forbids))
        # the population the own-file reader erred on, so this guard can fail both ways
        for sid in forbids:
            own = ((D["kits"].get(sid) or {}).get("slots") or {}).get(slot_id) or {}
            if own.get("status") not in (None, "empty"):
                forbidding_with_an_own_record += 1
        # a specifier whose OWN record the own-file reader skipped: absent, or status empty
        for sid in want:
            own = ((D["kits"].get(sid) or {}).get("slots") or {}).get(slot_id) or {}
            if own.get("status") in (None, "empty"):
                inherited += 1
    assert forbidding_with_an_own_record, "the premise: some style forbids a slot in its own file"
    assert inherited, "the premise: some style specifies a slot only through its cascade"


def test_get_slots_keys_did_not_move():
    """The freeze on `tdl_get_slot` was lifted for its list and nothing else."""
    sid = next(iter(core._data()["slots"]))
    assert set(core.get_slot(sid)) == {"slot", "specified_by_styles", "faults_on_this_slot", "note"}
