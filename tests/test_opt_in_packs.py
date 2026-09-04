"""`inherits_packs` — OQ 51's delivery half, staged pack by pack.

Lucas re-ruled OQ 51 on 3 Sep 2026: pack inheritance becomes opt-in. Measuring it first changed
the shape — flipping everything at once would strand 2,899 slots across 124 of 132 nodes, against
the ~223 the ruling was taken on, which counts ROLE GAPS and not deliveries. So the switch is per
PACK (`delivery: opt-in` on the pack) and the admission is per NODE (`inherits_packs`), and one
pack moves at a time.

**NOTHING IS FLIPPED TODAY AND THAT IS THE POINT OF THE FIRST TEST.** A mechanism that changes
nothing on the day it ships is indistinguishable from one that does not work, so the corpus is
pinned unchanged AND the gate is driven directly to prove it bites.

Per-node, not per-edge, and that grain is measured rather than chosen: only about half of all gaps
reach their delivering ancestor through a direct lineage edge at all, and `_cascade` is flattened,
so the delivering edge is not recoverable from the chain. A per-edge deny was designed and refused
in OQ 51 with numbers; do not re-propose it.
"""
import collections
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402


def _rk():
    return modcache.load("resolve_kit", os.path.join(ROOT, "build", "resolve_kit.py"))


def _ci():
    return modcache.load("check_inheritance", os.path.join(ROOT, "build", "check_inheritance.py"))


def _cpb():
    return modcache.load("check_pack_bindings",
                         os.path.join(ROOT, "build", "check_pack_bindings.py"))


@pytest.fixture(scope="module")
def graph():
    return json.load(open(os.path.join(ROOT, "dist", "taxonomy.json"), encoding="utf-8"))


# ---------------------------------------------------------------- inert until flipped

def test_exactly_the_flipped_packs_are_flipped_and_they_are_named_here(graph):
    """WP-8.9 shipped this as "nothing is flipped yet" and WP-8.10 flipped the first pack, which
    is the assertion firing as designed rather than a pin going stale. It is named rather than
    counted: a test that only counts lets one pack be swapped for another silently, and the
    whole discipline is that a flip is a deliberate one-pack edit with its stranding re-pinned in
    the same commit.

    The order was ascending stranded count, which is what Lucas ruled on 3 Sep when he closed
    `oq/a-pack-can-be-the-only-writer-a-node-has`: `trim-classical` 10, then `facade-gable` 32,
    then `sash-light` 70, with the five packs whose `applies_to` arms a live behavioural gate
    last. **THE PROGRAMME IS FINISHED.** Lucas ruled on 4 Sep that the last five go together
    rather than one per package, because the refill had moved entirely onto them -- 3 of 13 new
    gaps at the second flip, 10 of 10 at the third -- so staging them singly would have spread
    over five packages the one decision that mattered. All eight packs the programme ever named
    are flipped and the other 49 are on `cascade` because nothing plans to move them."""
    flipped = sorted(p for p, v in graph["_packs"].items() if v["delivery"] == "opt-in")
    assert flipped == ["facade-classical", "facade-gable", "gibbs-ionic", "opening-proportion",
                       "sash-light", "storey-graduation", "timber-bay", "trim-classical"], (
        flipped, "a pack has been flipped or unflipped — re-pin the stranding counts and say "
                 "which, in the same commit")
    deliveries = collections.Counter(v["delivery"] for v in graph["_packs"].values())
    assert deliveries["cascade"] == 49 and len(graph["_packs"]) == 57, deliveries


def test_the_pack_index_covers_every_pack_so_a_stale_build_is_loud(graph):
    """`resolve_packs` reads `graph["_packs"]`. An ABSENT index and a corpus with nothing flipped
    read identically at the resolver — a stale `dist/taxonomy.json` would silently disable the
    gate rather than fail, which is this repository's commonest defect. So the index is required
    to exist and to name every pack on disk."""
    import glob
    on_disk = set()
    for f in sorted(glob.glob(os.path.join(ROOT, "proportions", "*", "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        if d.get("id"):
            on_disk.add(d["id"])
    assert graph.get("_packs"), "the graph carries no _packs index — the gate cannot fire"
    assert set(graph["_packs"]) == on_disk, (
        sorted(on_disk - set(graph["_packs"])), sorted(set(graph["_packs"]) - on_disk))


# ---------------------------------------------------------------- the gate

@pytest.fixture
def flipped(graph):
    """A scratch graph with a still-unflipped pack flipped. Never written; the corpus is untouched.

    MOVED IN WP-8.11, and the reason generalises: this was `facade-gable`, chosen in WP-8.10
    because the corpus left it on `cascade`. Flipping it for real would have made every assertion
    below a statement about the shipped corpus instead of about the gate -- green, and vacuous.
    A driven fixture must name a pack nobody has flipped; check that before flipping the next."""
    import copy
    g = copy.deepcopy(graph)
    assert g["_packs"][PACK]["delivery"] == "cascade", (
        "%s has been flipped for real -- this fixture no longer drives anything" % PACK)
    g["_packs"][PACK]["delivery"] = "opt-in"
    return g


PACK = "trim-craftsman"               # on `cascade`; reaches NODE from `mission-revival`
NODE = "mediterranean-revival"        # receives it by descent; loses 3 slots without it


def _has(rk, g, nid, pid=PACK):
    return pid in rk.resolve_packs(g, rk.chain_for(g, nid))


def test_the_gate_bites_and_the_opt_in_admits(graph, flipped):
    """Four states, driven rather than asserted from the source."""
    rk = _rk()
    assert _has(rk, graph, NODE), "precondition: the cascade delivers it today"
    assert not _has(rk, flipped, NODE), "flipping the pack must stop the delivery"
    flipped["nodes"][NODE]["inherits_packs"] = [PACK]
    assert _has(rk, flipped, NODE), "the node's opt-in must admit it again"


def test_a_node_that_binds_a_pack_is_never_gated(graph, flipped):
    """`chain[0]` is the node, and a node that BINDS a pack has opted into it by binding it.
    Gating that would delete an authored record — the same reason `declined_packs` carries a
    `nid != chain[0]` guard."""
    rk = _rk()
    binder = next(n for n, v in graph["nodes"].items()
                  if any(e["pack"] == PACK for e in (v.get("proportion_packs") or [])))
    assert _has(rk, flipped, binder), binder


def test_an_opt_in_for_a_pack_that_has_not_flipped_changes_nothing(graph):
    """The staging discipline: the nodes that should keep a pack say so FIRST, the pack flips
    SECOND. So an opt-in written ahead of its flip must be inert and correct, not an error."""
    import copy
    rk = _rk()
    g = copy.deepcopy(graph)
    before = sorted(rk.resolve_packs(g, rk.chain_for(g, NODE)))
    g["nodes"][NODE]["inherits_packs"] = [PACK]
    assert sorted(rk.resolve_packs(g, rk.chain_for(g, NODE))) == before


def test_the_gate_preserves_what_four_callers_read_unconditionally(graph, flipped):
    """`_source` and `_overridden_by_ancestor` are read without a guard by `resolve_kit.main`,
    `eval_packs`, and `check_inheritance.governed`; and `choose_pack` does `next(iter(groups))`,
    so the OrderedDict's nearest-first order decides which quantity wins at a multi-quantity
    address. A filter that dropped either would be silent until a plate came out wrong."""
    rk = _rk()
    flipped["nodes"][NODE]["inherits_packs"] = [PACK]
    got = rk.resolve_packs(flipped, rk.chain_for(flipped, NODE))
    assert all("_source" in v and "_overridden_by_ancestor" in v for v in got.values())
    plain = rk.resolve_packs(graph, rk.chain_for(graph, NODE))
    assert list(got) == list(plain), "insertion order must survive the gate"


def test_the_gate_reports_out_of_band_and_never_as_a_key(graph, flipped):
    """`check_addresses.cobinding` does `sorted(resolve_packs(...).keys())`, so a sentinel key
    would be read as a pack id by a checker. `refusals_for` is the precedent for saying so
    elsewhere."""
    rk = _rk()
    got = rk.resolve_packs(flipped, rk.chain_for(flipped, NODE))
    ids = set(json.load(open(os.path.join(ROOT, "dist", "taxonomy.json"),
                             encoding="utf-8"))["_packs"])
    assert set(got) <= ids, sorted(set(got) - ids)


# ---------------------------------------------------------------- the lie-check

def _errs(node, graph, **over):
    cpb = _cpb()
    n = dict(node); n.update(over)
    out = []
    cpb.check_opt_ins(n, set(graph["_packs"]), graph, out)
    return out


@pytest.fixture(scope="module")
def node():
    return json.load(open(os.path.join(ROOT, "styles", "carpenter-gothic.json"), encoding="utf-8"))


def test_an_opt_in_that_admits_nothing_is_an_error_four_ways(node, graph):
    """An opt-in that admits nothing reads exactly like a considered one — the mirror of the
    decline's own stated failure, in the same words. Every branch entered."""
    assert "does not reach it by descent" in _errs(node, graph, inherits_packs=["moorish-arch"])[0]
    binds = node["proportion_packs"][0]["pack"]
    assert "BINDS it as well" in _errs(node, graph, inherits_packs=[binds])[0]
    declines = node["declined_packs"][0]["pack"]
    assert "DECLINES it" in _errs(node, graph, inherits_packs=[declines])[0]
    assert "is not a pack id" in _errs(node, graph, inherits_packs=["no-such-pack"])[0]


def test_opting_in_twice_is_an_error_because_one_statement_per_pair(node, graph):
    errs = _errs(node, graph, inherits_packs=["chambers-doric", "chambers-doric"])
    assert any("twice" in e for e in errs), errs


def test_a_node_with_no_opt_in_is_not_an_error(node, graph):
    """A check that fires on everything is not a check, and every node in the corpus is this
    case today."""
    assert _errs(node, graph, inherits_packs=[]) == []
    n = dict(node); n.pop("inherits_packs", None)
    assert _errs(n, graph) == []


def test_the_whole_corpus_passes_the_opt_in_check(graph):
    """Vacuous today by construction — nothing carries the field — and pinned so it stops being
    vacuous the moment the first flip authors one."""
    import glob
    cpb = _cpb()
    errs, carrying = [], 0
    for f in sorted(glob.glob(os.path.join(ROOT, "styles", "*.json"))):
        n = json.load(open(f, encoding="utf-8"))
        if n.get("inherits_packs"):
            carrying += 1
        cpb.check_opt_ins(n, set(graph["_packs"]), graph, errs)
    assert errs == [], errs[:5]
    # No longer vacuous (WP-8.10): six nodes opt in to `trim-classical`, so `check_opt_ins` is
    # now exercised against real records rather than against an empty loop. Named, not counted --
    # each is a node the pack's own `applies_to` vouches for AND which receives it by descent,
    # and authoring them is what kept the flip's cost at the measured 10 instead of 15.
    assert carrying == 24, ("%d node(s) opt in — a flip has landed or been withdrawn; re-pin the "
                            "stranding counts in the same commit" % carrying)
    opted = sorted(json.load(open(f, encoding="utf-8"))["id"]
                   for f in sorted(glob.glob(os.path.join(ROOT, "styles", "*.json")))
                   if json.load(open(f, encoding="utf-8")).get("inherits_packs"))
    # 41 ENTRIES OVER 24 NODES. `mid-atlantic-georgian` opts into six packs, `charleston-georgian`
    # and `new-england-georgian` five apiece, `tidewater-georgian` four: the Georgian cluster sits
    # deep in a chain that delivered most of what got flipped. A node's `inherits_packs` is a list
    # and later flips APPEND to it -- WP-8.12's authoring script asserted the key was ABSENT and
    # stopped half way through its seven, having already written one.
    #
    # AN OPT-IN NEEDS BOTH CONDITIONS AND WP-8.13 FIRST WROTE ONLY ONE. The list was derived from
    # each pack's `applies_to` minus the nodes that bind or decline it -- 40 entries -- and
    # `check_opt_ins` refused 14 of them, because `applies_to` says the pack is FOR this style and
    # says nothing about whether the cascade DELIVERS it there. The two are independent. All 14
    # were no-ops: removing them left `dimensioned_before`, `stranded`, `rehoused`, `unreached`
    # and `nodes_touched` byte-identical, which is what proves they admitted nothing -- and is
    # also why nothing but this check would ever have reported them.
    assert len(opted) == 24 and opted[0] == "american-farmhouse-vernacular", opted
    for n in ("mid-atlantic-georgian", "tidewater-georgian", "charleston-georgian",
              "new-england-georgian", "queen-anne-british", "octagon-house"):
        assert n in opted, (n, opted)
    entries = sum(len(json.load(open(f, encoding="utf-8")).get("inherits_packs") or [])
                  for f in sorted(glob.glob(os.path.join(ROOT, "styles", "*.json"))))
    assert entries == 41, entries


def test_the_flip_moved_judged_and_the_code_said_it_could_not():
    """`measure()`'s own comment said the withhold branch MUST NOT MOVE `judged`. WP-8.13 moved
    it, 249 -> 250, with no case adjudicated and no `declined_packs` entry written.

    THE ROUTE IS `endorsed`, NOT `declined`, WHICH IS THE HALF THE COMMENT DID NOT CONSIDER.
    Withholding a pack VACATES the role it filled and the role re-attributes to the next
    ancestor -- the same non-monotonicity that made `unendorsed` a work list rather than a
    score. Where that next pack both ARRIVES (the node opted into it) and VOUCHES (its
    `applies_to` names the node), the re-attributed gap lands in `endorsed`.

    Exactly one instance at this flip, and it is pinned by name because a count could not tell
    this from an adjudication: `american-farmhouse-vernacular` / role `opening`, vacated by
    `opening-proportion` (which that node does not opt into) and landing on `sash-light`, which
    it opted into in WP-8.12 and whose `applies_to` names it.

    THE FLOOR IS NOT VIOLATED -- it forbids only going DOWN -- and the classification is not
    wrong: an author really did vouch for that pack on that node. What died is the READING three
    packages rested on, that `judged` is the one number telling a flip from an adjudication."""
    ci = _ci()
    g = ci.load()
    applies = ci.applies_to_index()
    _build, gaps, _inh, _dec = ci.measure(g)
    endorsed = {(nid, role, pack) for nid, role, _anc, pack in gaps
                if nid in applies.get(pack, ())}
    assert ("american-farmhouse-vernacular", "opening", "sash-light") in endorsed, sorted(
        x for x in endorsed if x[0] == "american-farmhouse-vernacular")
    # The two conditions that put it there, asserted separately so a change to either is named.
    node = g["nodes"]["american-farmhouse-vernacular"]
    assert "sash-light" in (node.get("inherits_packs") or []), node.get("inherits_packs")
    assert g["_packs"]["sash-light"]["delivery"] == "opt-in"
    assert g["_packs"]["opening-proportion"]["delivery"] == "opt-in"
    assert ci.RATCHET_FLOOR["judged"] == 250, (
        "judged moved 249 -> 250 on the five-pack flip with nothing adjudicated; if this floor "
        "moves again, establish whether a case was READ before treating it as progress")
