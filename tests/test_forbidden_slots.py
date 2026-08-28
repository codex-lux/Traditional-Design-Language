"""`oq/forbidden-stops-the-pack-cascade` — a pack rule may not write to a slot the resolved kit binds `forbidden`.

`docs/inheritance.md`'s binding table has said `forbidden` means "This node prohibits the slot.
Stops the cascade" since the beginning. It stopped the KIT cascade and never the PACK cascade,
and the gap was 776 (node, slot) pairs across 118 of 132 buildable nodes — **and not one of the
776 was chosen by a human**. Every one resolved by an ancestor's precedence number; no slot
carried a `packs` ruling for any of them.

Ruled: absolute, with a human override — the slot's own `packs` block, which `choose_pack`
already treats as "the only place a human has said which pack wins".

Every assertion here is mutation-checked against the code it guards.
"""
import importlib.util
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CTX = {"ceiling_height": 108.0, "storey_height": 120.0, "opening_width": 36.0,
       "opening_height": 80.0, "span": 540.0, "wall_thickness": 13.5}


def _mod(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def rk():
    return _mod("rk_f", "build/resolve_kit.py")


@pytest.fixture(scope="module")
def graph():
    return json.load(open(os.path.join(ROOT, "dist", "taxonomy.json"), encoding="utf-8"))


def _rows(rk, graph, nid):
    chain = rk.chain_for(graph, nid)
    kit, _ = rk.resolve_slots(graph, chain, rk.scope_for(graph, nid))
    by_slot, _ = rk.eval_packs(rk.resolve_packs(graph, chain), CTX, None, kit)
    return kit, by_slot


def test_the_worked_case_carpenter_gothic_pilaster(rk, graph):
    """The node's own resolved record says "No pilaster order." and `chambers-ionic` dimensioned
    it at 5/6 anyway."""
    kit, by_slot = _rows(rk, graph, "carpenter-gothic")
    assert (kit.get("pilaster") or {}).get("binding") == "forbidden", (
        "carpenter-gothic no longer forbids pilaster — this test's fixture has moved")
    rows = by_slot.get("pilaster") or []
    assert rows, "no pack writes to pilaster here, so this test is vacuous"
    assert all(r.get("refused_by_kit") for r in rows), rows
    ch = rk.choose_pack(kit["pilaster"], rows, CTX)
    assert ch["chosen"] is None and ch["how"] == "kit.forbidden", ch


def test_a_refused_rule_is_MARKED_not_deleted(rk, graph):
    """Deleting would destroy the measurement itself — the 776 count is the marks. And
    `check_addresses` reads these rows without ever calling `choose_pack`, so a refusal placed
    only in the chooser would not reach it. Same discipline as `openings.py` marking an opening
    it cannot realise `unplaced` and never removing it."""
    kit, by_slot = _rows(rk, graph, "carpenter-gothic")
    rows = by_slot["pilaster"]
    assert rows, "the rule was DELETED, not marked — the meter can no longer count it"
    assert all(r.get("refused_because") for r in rows), (
        "a refusal with no reason is an absence wearing a verdict")


def test_the_kit_argument_is_required_and_has_no_default(rk):
    """A `kit=None` default would let every call site keep the old behaviour by saying nothing —
    the exact failure the fault schema describes for a mistyped guard: "omit `expression` and the
    precondition is ignored entirely, the test runs unguarded and convicts"."""
    import inspect
    sig = inspect.signature(rk.eval_packs)
    assert "kit" in sig.parameters, sig
    assert sig.parameters["kit"].default is inspect.Parameter.empty, (
        "eval_packs' `kit` has grown a default; every caller can now skip `oq/forbidden-stops-the-pack-cascade`'s gate silently")


def test_the_human_override_is_the_slots_own_packs_block(rk, graph):
    """The ruling's escape hatch. Zero of the 776 qualify today, so it strands nothing — and
    that is stated rather than claimed as coverage."""
    kit, by_slot = _rows(rk, graph, "carpenter-gothic")
    rec = dict(kit["pilaster"])
    pack = by_slot["pilaster"][0]["pack"]
    rec["packs"] = [{"pack": pack, "expression": "1", "precedence": 1}]
    chain = rk.chain_for(graph, "carpenter-gothic")
    patched = dict(kit)
    patched["pilaster"] = rec
    _, by_slot2 = rk.eval_packs(rk.resolve_packs(graph, chain), CTX, None, patched), None
    by_slot2, _ = rk.eval_packs(rk.resolve_packs(graph, chain), CTX, None, patched)
    named = [r for r in by_slot2["pilaster"] if r["pack"] == pack]
    assert named and not any(r.get("refused_by_kit") for r in named), (
        "a slot naming the pack in its own `packs` block is a person's explicit ruling and must "
        "override the refusal")


def test_no_forbidden_slot_in_the_corpus_carries_a_human_ruling_today(rk, graph):
    """The claim the report makes, held to the data: the override strands nothing because
    nobody has used it. If this ever fails, the report's "zero qualify" line is stale."""
    found = []
    for nid, n in graph["nodes"].items():
        if n.get("rank") not in ("style", "variant"):
            continue
        chain = rk.chain_for(graph, nid)
        kit, _ = rk.resolve_slots(graph, chain, rk.scope_for(graph, nid))
        for sid, rec in kit.items():
            if rec.get("binding") == "forbidden" and (rec.get("packs") or []):
                found.append((nid, sid))
    assert not found, (
        f"{len(found)} forbidden slot(s) now carry a `packs` ruling: {found[:5]}. The override is "
        f"live, so the report's claim that it strands nothing needs re-stating.")


def test_the_elevation_path_is_covered_separately_and_says_which_half(rk, graph):
    """`build/elevation.py` never calls resolve_packs or eval_packs — it reaches packs by
    PE.resolve, so the resolver-side gate reaches NONE of the figures it draws. That second path
    was named in no plan and no open question before WP-8.3.

    Anchored on the CORPUS SWEEP and not on one plan: `spec-builder-colonial`'s own style stopped
    forbidding `transom_sidelight` in this same package (see the `colonial-revival` binding), so
    a test pinned to that one plan would have gone quietly vacuous — which is the shape of the
    negative assertion CLAUDE.md records as inverting into a tautology."""
    pe = _mod("pe_f", "build/proportion_engine.py")
    READ = ("belt_course casing chimney cornice door_surround entry_door frieze pilaster shutter "
            "transom_sidelight water_table window_grouping_rule window_head_masonry "
            "window_head_wood window_lite_pattern window_proportion").split()
    REFUSED_HERE = ("transom_sidelight", "pilaster")
    gate = [n for n in sorted(set(pe.resolve("opening-proportion").get("applies_to") or [])
                              & set(pe.resolve("facade-classical").get("applies_to") or []))
            if (graph["nodes"].get(n) or {}).get("rank") in ("style", "variant")]
    refused = read_anyway = 0
    for nid in gate:
        kit, _ = rk.resolve_slots(graph, rk.chain_for(graph, nid), rk.scope_for(graph, nid))
        forb = {s for s, r in kit.items() if r.get("binding") == "forbidden"} & set(READ)
        refused += len(forb & set(REFUSED_HERE))
        read_anyway += len(forb - set(REFUSED_HERE))
    assert refused + read_anyway == 40, (refused, read_anyway)
    assert (refused, read_anyway) == (16, 24), (
        f"the elevation exposure moved to {refused} refused / {read_anyway} read-anyway. That is "
        f"not automatically wrong — binding one slot on colonial-revival moved it 46 -> 40 — but "
        f"it must be re-measured and re-stated, not re-pinned blind.")


def test_the_generator_discloses_what_it_read_against_a_forbidding_kit():
    """The disclosure itself, on a shipped plan. `read_anyway` is a measured disclosure and not
    a pass: those slots are drawn today against a kit that forbids them."""
    el = _mod("el_f", "build/elevation.py")
    plan = json.load(open(os.path.join(ROOT, "plans", "spec-builder-colonial.json"),
                          encoding="utf-8"))
    e = el.build_elevation(plan)
    d = e["forbidden_slots_read_from_packs"]
    assert set(d) == {"refused", "read_anyway", "note"}, d
    assert d["read_anyway"] == ["belt_course", "frieze", "water_table"], d
    assert "PE.resolve" in d["note"]


def test_the_forbidden_meter_is_still_ratcheted_apart_from_the_backlog():
    ci = _mod("ci_f2", "build/check_inheritance.py")
    assert ci.FORBIDDEN_RATCHET == 776
    assert ci.FORBIDDEN_RATCHET not in ci.RATCHET.values()
