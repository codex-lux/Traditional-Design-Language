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
import sys

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


# THE ELEVATION HALF, TESTED BY RUNNING IT. Both tests above were written for WP-8.3's only
# behavioural change to `build/elevation.py`, and the WP-8.4 adversarial audit deleted that
# change -- `_REFUSED_HERE = ()`, `sidelights_forbidden = False`, the pilaster projection
# computed unconditionally -- and watched this file stay green. One of them never imports
# elevation.py at all (it partitions a corpus measurement against a hardcoded copy of
# `_REFUSED_HERE`, so the split is a CLAIM about the generator, not a reading of it); the
# other calls it on `spec-builder-colonial`, whose style forbids NEITHER slot, so its
# `refused` list is empty and nothing asserts on it.
#
# Neither shipped plan is one of the nine gate styles that forbid a refused slot. That is
# this corpus's own named trap, and it caught its own guard: verifying a corpus-wide change
# on the plans that happen to ship is verifying it on 2 of 164 styles. The fix is to run the
# generator on a style where the refusal BITES -- and doing that immediately found half a
# pilaster still being published on exactly such a style.

FORBIDDING_STYLE = "cape-cod-colonial"      # kit: "The whole classical-apparatus group is
                                            # forbidden at the family"
PERMITTING_STYLE = "colonial-revival"


def _elev_for(style):
    el = _mod("el_" + style.replace("-", "_"), "build/elevation.py")
    plan = json.load(open(os.path.join(ROOT, "plans", "spec-builder-colonial.json"),
                          encoding="utf-8"))
    plan = json.loads(json.dumps(plan))
    plan["style"] = style
    return el.build_elevation(plan)


REFUSED_MEASUREMENTS = ("sidelight_width_in", "transom_width_in", "transom_head_rise_in",
                        "pilaster_projection_in", "pilaster_width_in", "pilaster_width")


def test_a_style_whose_kit_forbids_the_slot_publishes_no_measurement_of_it(rk, graph):
    """DIFFERENTIAL, because an absent key proves nothing on its own.

    The same plan is run under two styles. Under the one whose resolved kit forbids
    `transom_sidelight` and `pilaster`, every measurement of those things must be ABSENT --
    not zero, which is the invented-constant failure `NOT_MODELLED` exists to stop. Under
    the one that permits them, every one of the same keys must be PRESENT, which is what
    stops this passing on a generator that simply stopped producing them.
    """
    kit, _ = rk.resolve_slots(graph, rk.chain_for(graph, FORBIDDING_STYLE),
                              rk.scope_for(graph, FORBIDDING_STYLE))
    forb = {s for s, r in kit.items() if r.get("binding") == "forbidden"}
    assert {"transom_sidelight", "pilaster"} <= forb, (
        f"{FORBIDDING_STYLE} no longer forbids both slots -- this test has gone vacuous; "
        f"re-pin it on one of the nine gate styles that do")

    banned = _elev_for(FORBIDDING_STYLE)["measurements"]
    allowed = _elev_for(PERMITTING_STYLE)["measurements"]
    leaked = {k: banned[k] for k in REFUSED_MEASUREMENTS if k in banned}
    assert leaked == {}, (
        f"{FORBIDDING_STYLE}'s kit forbids these slots and the generator published them "
        f"anyway: {leaked}. A measurement of a thing the record says is not there is what "
        f"the fault corpus then convicts the house on.")
    missing = [k for k in REFUSED_MEASUREMENTS if k not in allowed]
    assert missing == [], (
        f"the control style publishes none of {missing} either, so the assertion above "
        f"passes on a generator that produces nothing -- the test is vacuous")


def test_the_disclosure_names_the_refusal_on_a_style_it_bites_on(rk, graph):
    d = _elev_for(FORBIDDING_STYLE)["forbidden_slots_read_from_packs"]
    assert sorted(d["refused"]) == ["pilaster", "transom_sidelight"], d
    assert not (set(d["read_anyway"]) & {"pilaster", "transom_sidelight"}), d


def test_the_forbidden_meter_is_still_ratcheted_apart_from_the_backlog():
    ci = _mod("ci_f2", "build/check_inheritance.py")
    assert ci.FORBIDDEN_RATCHET == 776
    assert ci.FORBIDDEN_RATCHET not in ci.RATCHET.values()


# ---------------------------------------------------------------------------
# THE CONTRACT, pinned after the WP-8.4 adversarial audit found it broken.
#
# `choose_pack` has five return branches. Four of them return `rejected` and
# `stale_calibration`; WP-8.3's new `kit.forbidden` branch returned neither, and
# `resolve_kit.main()`'s --slot view and its PACK RESOLUTION summary index both
# UNCONDITIONALLY. The result was a KeyError on every one of the 776 (node, slot)
# pairs the package exists to name -- the documented way to read a slot's proven
# resolution, crashing on exactly the population the package created, shipped
# green because no test and no check ever called that CLI path.
# ---------------------------------------------------------------------------

CONTRACT_KEYS = {"how", "chosen", "ranked", "rejected", "stale_calibration"}


def test_every_choose_pack_branch_returns_the_same_keys(resolve_kit_module):
    """Read from a REAL resolution over the whole corpus, not from the source.

    A source-reading test would pass on a branch that builds the dict correctly and
    then returns a different one; and it could not prove the branch is ever reached.
    This asserts every branch the corpus actually exercises, and asserts that more
    than one branch IS exercised so it cannot pass vacuously."""
    rk = resolve_kit_module
    g = rk.load_graph()
    seen, missing = {}, []
    for nid in sorted(g["nodes"]):
        chain = rk.chain_for(g, nid)
        kit, _ = rk.resolve_slots(g, chain, rk.scope_for(g, nid))
        by_slot, _e = rk.eval_packs(rk.resolve_packs(g, chain), CTX, None, kit)
        for sid in set(by_slot) & set(kit):
            ch = rk.choose_pack(kit[sid], by_slot[sid], CTX)
            if ch is None:
                continue
            seen[ch["how"]] = seen.get(ch["how"], 0) + 1
            gap = CONTRACT_KEYS - set(ch)
            if gap:
                missing.append((nid, sid, ch["how"], sorted(gap)))
    assert not missing, (
        f"choose_pack branch(es) omit contract keys: {missing[:5]} "
        f"-- resolve_kit.main() indexes rejected/stale_calibration unconditionally, so an "
        f"omission is a KeyError in the --slot view for every node the branch fires on")
    assert len(seen) >= 3, (
        f"only {sorted(seen)} branches were exercised; this test cannot see an omission in a "
        f"branch the corpus never reaches, so it must not be trusted as full coverage")
    assert seen.get("kit.forbidden"), (
        "no slot resolved `kit.forbidden` -- the branch this test was written for is not "
        "reached, so the assertion above is vacuous for it")


def test_the_slot_view_does_not_crash_on_a_forbidden_slot(resolve_kit_module):
    """The end-to-end form: run the documented CLI on a real refused pair.

    The contract test above would still pass if `main()` grew a new unconditional index
    on a key only some branches return, so this drives the actual command."""
    import subprocess
    import sys
    rk = resolve_kit_module
    g = rk.load_graph()
    target = None
    for nid in sorted(g["nodes"]):
        chain = rk.chain_for(g, nid)
        kit, _ = rk.resolve_slots(g, chain, rk.scope_for(g, nid))
        by_slot, _e = rk.eval_packs(rk.resolve_packs(g, chain), CTX, None, kit)
        for sid in sorted(set(by_slot) & set(kit)):
            ch = rk.choose_pack(kit[sid], by_slot[sid], CTX)
            if ch and ch["how"] == "kit.forbidden":
                target = (nid, sid)
                break
        if target:
            break
    assert target, "no forbidden pair in the corpus -- this test is vacuous, re-pin or delete it"
    nid, sid = target
    p = subprocess.run([sys.executable, os.path.join(ROOT, "build", "resolve_kit.py"), nid,
                        "--slot", sid], cwd=ROOT, capture_output=True, text=True)
    assert p.returncode == 0, f"resolve_kit.py {nid} --slot {sid} exited {p.returncode}:\n{p.stderr}"
    assert "kit.forbidden" in p.stdout
    assert "refused" in p.stdout, (
        "the refusal is not stated in the output -- a refusal printed as an absence is the "
        "silent drop this package exists to remove")


def test_the_pack_resolution_summary_puts_every_slot_in_a_bucket(resolve_kit_module):
    """`kit.forbidden` was counted as neither ruled nor unresolved, so the summary read
    '77 of 97 ... 59 resolved, 0 still unresolved' and left 18 slots named nowhere. A state
    in no bucket reads as absent, which is the one collapse this corpus forbids."""
    import re
    import subprocess
    import sys
    p = subprocess.run([sys.executable, os.path.join(ROOT, "build", "resolve_kit.py"),
                        "american-farmhouse-vernacular"], cwd=ROOT, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    head = re.search(r"PACK RESOLUTION\s+\((\d+) of \d+ slots", p.stdout)
    body = re.search(r"(\d+) resolved by an explicit ruling, (\d+) still unresolved, "
                     r"(\d+) REFUSED", p.stdout)
    assert head and body, f"the summary lines changed shape:\n{p.stdout[:800]}"
    covered = int(head.group(1))
    ruled, unruled, refused = (int(body.group(i)) for i in (1, 2, 3))
    assert refused > 0, "no refused slots on this node -- re-pin this test on one that has some"
    assert ruled + unruled + refused == covered, (
        f"{covered} slots covered but only {ruled + unruled + refused} accounted for")
    assert "! " not in p.stdout.split("PACK RESOLUTION")[1][:400] or "in NO bucket" not in p.stdout


def test_a_sweep_that_finds_nothing_reports_could_not_evaluate_and_not_a_satisfied_ratchet():
    """0 is the most satisfying number a may-only-fall ratchet can read.

    `--forbidden` printed 776 over 118 nodes, then 0 over 0 nodes twice in succession
    during this session's audit, then 776 again for the next twenty runs. The cause was
    never reproduced and is not claimed here. What is not in doubt is the consequence: a
    run reporting 0 pairs exited 0 and SATISFIED a ceiling of 776, because "fewer
    overrides than ever" and "the corpus was not read" are the same integer. They are not
    the same state and may not share an exit code.

    A truncated kit file already raises (verified by hand: a half-written
    `kits/ranch-style.kit.json` gives a traceback, not a zero), so what is left to guard
    is the case where the sweep completes and finds nothing at all. That is what this
    stubs -- `eval_packs` returning no rows for every node -- and the assertion is on the
    EXIT CODE, because that is the only part of the output `check_all.py` reads.
    """
    import io
    import contextlib
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import resolve_kit as rk
    src = open(os.path.join(ROOT, "build", "check_inheritance.py"), encoding="utf-8").read()
    src = src.replace('if __name__ == "__main__":\n    main()', "")
    g = {"__name__": "ci_probe", "__file__": os.path.join(ROOT, "build/check_inheritance.py")}
    exec(compile(src, "build/check_inheritance.py", "exec"), g)
    orig, argv = rk.eval_packs, sys.argv
    rk.eval_packs = lambda *a, **k: ({}, {})
    sys.argv = ["check_inheritance.py", "--forbidden"]
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            g["main"]()
        raise AssertionError("an empty sweep exited 0 -- the ratchet was satisfied by a "
                             "corpus that was never measured")
    except SystemExit as e:
        assert e.code == g["COULD_NOT_EVALUATE"], (
            f"an empty sweep exited {e.code}; COULD NOT EVALUATE is "
            f"{g['COULD_NOT_EVALUATE']}, and 0 would satisfy the ratchet")
        assert "COULD NOT EVALUATE" in buf.getvalue()
    finally:
        rk.eval_packs, sys.argv = orig, argv


# ---------------------------------------------------------- the engine's own refusal
#
# `proportion_engine.evaluate()` sets `out_of_calibration` when the environment is outside
# the band a rule was calibrated in. That is the engine declining to stand behind its own
# number, and BOTH key-by-key row rebuilds downstream dropped it: `eval_packs` (which every
# resolver consumer reads) and `core.RULE_KEYS` (which every MCP caller and the workbench
# Proportions plate read). So `resolve_kit.py adam-style --slot chair_rail` printed
# 1'-10 3/4" with nothing beside it, while the engine row said "ceiling_height is 108,
# calibrated for 142.5-168" -- a number a reader can copy, from a rule that was refused.
#
# The same shape as `error`, whose omission `Proportions.jsx` records as "a refusal rendered
# as a measurement", and the same symptom `build/proportion_engine.py` records as ALREADY
# FIXED. Found by the WP-8.4 adversarial audit.

def test_the_engines_refusal_survives_both_row_rebuilds(rk, graph):
    import sys as _sys
    _sys.path.insert(0, os.path.join(ROOT, "build"))
    import proportion_engine as pe

    CTX = {"ceiling_height": 108.0, "storey_height": 120.0, "opening_width": 36.0,
           "opening_height": 80.0, "span": 540.0, "wall_thickness": 13.5}
    style = "adam-style"
    chain = rk.chain_for(graph, style)
    kit, _ = rk.resolve_slots(graph, chain, rk.scope_for(graph, style))
    by_slot, _ = rk.eval_packs(rk.resolve_packs(graph, chain), CTX, None, kit)

    # The engine really does refuse this rule at this environment -- assert it, or the test
    # below passes on a corpus where nothing is out of calibration.
    ev = pe.evaluate(pe.resolve("trim-classical"), bindings=CTX)
    refused = [r for r in ev["rules"] if r.get("out_of_calibration")]
    assert refused, ("`trim-classical` is in calibration at this env now -- re-pin this test "
                     "on a pack that is not, rather than deleting it")

    rows = [r for r in by_slot.get("chair_rail", []) if r["pack"] == "trim-classical"]
    assert rows, "trim-classical no longer reaches chair_rail on adam-style"
    assert any(r.get("out_of_calibration") for r in rows), (
        "eval_packs delivered the number and dropped the engine's refusal of it")

    from mcp_server import core as _core
    got = _core.get_proportions("benjamin-doric", include_rules=True)
    banded = [r for r in (got.get("derived_rules") or [])
              if r.get("range") and r.get("in_range") is None]
    assert banded, "no rule states a band it could not be judged against -- re-pin"
    assert all(r.get("out_of_calibration") for r in banded), (
        "a rule states a range with `in_range: null` and no reason -- the band cell for an "
        "unjudged rule is byte-identical to the band cell for a passing one: %s"
        % [r["target_slot"] for r in banded if not r.get("out_of_calibration")])


# ------------------------------------------- the critic's own raw-kit blind spot
#
# `plan_check`'s STYLE LAYER read `C["kits"][style]["slots"]` -- the node's own file -- to
# decide whether a declared slot or variant is forbidden. Every forbidden call the LINEAGE
# delivers lives in the resolved record instead, and `resolve_slots` stops its walk only on
# `specified` or `forbidden`, so a slot the node leaves `open` inherits its ancestor's
# prohibition in full and the critic could not see it. Measured over all 132 buildable
# nodes: 879 forbidden BINDINGS and 3,661 forbidden VARIANTS invisible, with every single
# node carrying at least one.
#
# Neither shipped plan gains a finding from the fix, which is exactly why nothing caught it.

def test_the_style_layer_sees_a_prohibition_the_lineage_delivers(rk, graph):
    pc = _mod("plan_check_raw", "build/plan_check.py")
    style, slot = "cape-cod-colonial", "balustrade"

    raw = json.load(open(os.path.join(ROOT, "kits", "%s.kit.json" % style),
                         encoding="utf-8")).get("slots") or {}
    kit, _ = rk.resolve_slots(graph, rk.chain_for(graph, style), rk.scope_for(graph, style))
    assert (raw.get(slot) or {}).get("binding") != "forbidden", (
        "%s now forbids %s in its OWN file, so this witness no longer distinguishes the raw "
        "kit from the cascade -- re-pin it on another" % (style, slot))
    assert (kit.get(slot) or {}).get("binding") == "forbidden", (
        "the cascade no longer forbids %s on %s" % (slot, style))

    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json"),
                          encoding="utf-8"))
    plan = json.loads(json.dumps(plan))
    plan["style"] = style
    plan.setdefault("declared", {})[slot] = "turned-baluster"
    findings = pc.check(plan)["findings"]
    hits = [f for f in findings
            if f.get("layer") == "style" and slot in (f.get("statement") or "")]
    assert hits, ("the style layer did not report a slot the resolved kit forbids -- it is "
                  "reading the node's own kit file again")
    assert any(f["severity"] == "serious" for f in hits), hits

def test_the_chimney_read_is_the_nodes_own_kit_and_that_is_deliberate(rk, graph):
    """THE ONE PLACE THIS AUDIT CHANGED A READER AND CHANGED IT BACK, and the reason is the
    distinction the whole `oq/the-raw-kit-read` question turns on.

    `chimney_positions`' docstring has always claimed "the resolved kit's own canonical
    `chimney` slot variant" and the code read the node's own file. Making the code match the
    docstring is right in principle -- 64 of 164 styles state a canonical chimney only
    through their lineage -- and measurably worse in fact: `colonial-revival` states nothing
    about chimneys, so the cascade hands it `tall-multiple-vertical-accent` from
    `british-picturesque`, a Gothic Revival clustered stack "thin and numerous and well out
    of proportion", seven steps up. That put a Gothic stack on `spec-builder-colonial` and
    took its placed chimney positions from 1 to 0. Its own record carries nothing that would
    let it be bound honestly, so there is no fix at the node either.

    **An inherited `forbidden` is a prohibition an ancestor made and the descendant never
    overturned. An inherited CANONICAL is a positive claim the descendant never made.**
    `plan_check` reads the cascade and keeps it, because it reads only the first kind.

    This pins the behaviour AND the reason, so the next reader who notices the docstring does
    not re-make the change. It asserts the state that made the change wrong, not just the
    output -- if `colonial-revival` ever states a chimney of its own, this test says so.
    """
    rf = _mod("roof_own_kit", "build/roof.py")
    own = (json.load(open(os.path.join(ROOT, "kits", "colonial-revival.kit.json"),
                          encoding="utf-8")).get("slots") or {}).get("chimney") or {}
    assert not [v for v in (own.get("variants") or []) if v.get("status") == "canonical"], (
        "colonial-revival now states a chimney of its own -- the cascade read may be safe "
        "here after all; re-measure `build_roof` on plans/spec-builder-colonial.json before "
        "changing anything")
    kit, _ = rk.resolve_slots(graph, rk.chain_for(graph, "colonial-revival"),
                              rk.scope_for(graph, "colonial-revival"))
    inherited = [v["id"] for v in ((kit.get("chimney") or {}).get("variants") or [])
                 if v.get("status") == "canonical"]
    assert inherited, "the cascade no longer delivers a chimney here; this test is vacuous"

    plan = json.load(open(os.path.join(ROOT, "plans", "spec-builder-colonial.json"),
                          encoding="utf-8"))
    ch = rf.build_roof(plan, None).get("chimneys") or {}
    assert "hearth" in (ch.get("source") or ""), (
        "the roof is sourcing its chimney from the cascade again, which on this style means "
        "%s -- a Gothic Revival stack on a Colonial Revival house" % inherited)



def test_the_mcp_cascade_is_the_build_cascade(rk, graph):
    """core.py carried a SECOND kit cascade and it was truncated.

    `_cascade` walked `lineage` edges with `inherits_kit` and never spliced in a style's
    FAMILY-rank ancestors, which `build/build.py::family_of` has done for every style since
    WP-4.2 -- one day after that function was last touched. Measured before the fix: all 132
    buildable styles got a shorter chain in core than in `resolve_kit.chain_for`, **1,308
    ancestors dropped, 0 added**, and the two disagreed about whether a slot is forbidden on
    **206 (style, slot) records**.

    Served to users twice, through `tdl_resolve_kit` and `GET /api/kit/{style_id}`:
    `resolve_kit('appalachian-log-house', slot='order')` answered `specified` from
    `english-palladian`, canonical `ionic`, quoting Palladio -- on an Appalachian log house --
    because `nordic-alpine-vernacular` binds `order` forbidden and is a family node.

    This asserts the two AGREE rather than pinning either, which is the only form that keeps
    them from drifting apart again.
    """
    from mcp_server import core
    shorter, contradictions = [], []
    for nid in sorted(graph["nodes"]):
        if graph["nodes"][nid].get("rank") not in ("style", "variant"):
            continue
        mcp = core.resolve_kit(nid)
        chain = mcp.get("cascade") or []
        want = [x for x in rk.chain_for(graph, nid) if x != nid]
        missing = [x for x in want if x not in chain]
        if missing:
            shorter.append((nid, missing[:3]))
        cas, _ = rk.resolve_slots(graph, rk.chain_for(graph, nid), rk.scope_for(graph, nid))
        got = {r["slot"]: r for r in (mcp.get("slots") or [])
               if isinstance(r, dict) and "slot" in r}
        for sid, rec in cas.items():
            m = got.get(sid) or {}
            if rec.get("binding") == "forbidden" and m.get("binding") not in (None, "forbidden"):
                contradictions.append((nid, sid, m.get("binding"), m.get("source")))
    assert shorter == [], f"the MCP chain is missing ancestors on {len(shorter)} styles: {shorter[:3]}"
    assert contradictions == [], (
        f"{len(contradictions)} (style, slot) records where the corpus forbids and the MCP "
        f"says otherwise: {contradictions[:3]}")
    # Not vacuous: the population is the whole buildable corpus.
    assert sum(1 for n in graph["nodes"]
               if graph["nodes"][n].get("rank") in ("style", "variant")) >= 130
