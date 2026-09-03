"""A stranded slot must say who withheld its pack, or the flip trades one silence for another.

OQ 51's ruling of 3 Sep 2026 requires the opt-in flip to strand LOUDLY. Before WP-8.10 it could
not: `resolve_packs` dropped a gated pack, `eval_packs` therefore built no row for it, and
`choose_pack` returned a bare absence at the address -- indistinguishable from a slot no pack in
the corpus ever wanted. A node reading UNDIMENSIONED where it should read REFUSED is OQ 51's own
silent corruption arriving from the other direction, which is the thing the ruling was about.

The fix is WP-8.3's, one mechanism over and in its own words: THE REFUSED RULE IS MARKED, NOT
DELETED. `withheld_for()` says what the gate stopped, `eval_packs(withheld=...)` builds those
rules and marks them `withheld_by_opt_in`, and `choose_pack` returns `how: "opt-in.withheld"`
naming the pack and the reason.

EVERYTHING HERE IS DRIVEN, NEVER READ OFF THE CORPUS. The fixture flips `facade-gable`, which
this corpus does not flip, so these assertions keep meaning the same thing after a real pack is
flipped and after the last one is.
"""
import collections
import copy
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

CTX = {"ceiling_height": 108.0, "storey_height": 120.0, "opening_width": 36.0,
       "opening_height": 80.0, "span": 540.0, "wall_thickness": 13.5}
NODE = "north-german-hall-house"
PACK = "facade-gable"


def _rk():
    return modcache.load("resolve_kit", os.path.join(ROOT, "build", "resolve_kit.py"))


def _ci():
    return modcache.load("check_inheritance", os.path.join(ROOT, "build", "check_inheritance.py"))


@pytest.fixture(scope="module")
def graph():
    return json.load(open(os.path.join(ROOT, "dist", "taxonomy.json"), encoding="utf-8"))


@pytest.fixture
def flipped(graph):
    g = copy.deepcopy(graph)
    g["_packs"][PACK]["delivery"] = "opt-in"
    return g


def _resolve(g, nid=NODE):
    """(delivered, withheld, kit, by_slot) through the shipped functions, no second walk."""
    rk = _rk()
    chain = rk.chain_for(g, nid)
    packs = rk.resolve_packs(g, chain)
    wh = rk.withheld_for(g, nid)
    kit, _sv = rk.resolve_slots(g, chain, rk.scope_for(g, nid))
    by_slot, _e = rk.eval_packs(packs, CTX, None, kit, withheld=wh)
    return packs, wh, kit, by_slot


def _choice(g, sid, nid=NODE):
    rk = _rk()
    _p, _w, kit, by_slot = _resolve(g, nid)
    return rk.choose_pack(kit.get(sid) or {}, by_slot.get(sid, []), CTX)


# ------------------------------------------------------------------ withheld_for

def test_withheld_for_is_empty_where_nothing_is_flipped(graph):
    """A reporting function that always has something to say is not reporting."""
    rk = _rk()
    assert rk.withheld_for(graph, NODE) == {}


def test_withheld_for_names_the_pack_and_the_ancestor_that_would_have_sent_it(flipped):
    rk = _rk()
    wh = rk.withheld_for(flipped, NODE)
    assert list(wh) == [PACK], wh
    assert wh[PACK]["_would_have_come_from"] == wh[PACK]["_source"] == "flemish-vernacular"
    assert "inherits_packs" in wh[PACK]["_why"], wh[PACK]["_why"]


def test_an_opt_in_removes_it_from_the_withheld_report(flipped):
    """It is not withheld if the node admitted it -- the report must track the mechanism, or a
    reader is told a delivery was stopped that in fact arrived."""
    rk = _rk()
    flipped["nodes"][NODE]["inherits_packs"] = [PACK]
    assert rk.withheld_for(flipped, NODE) == {}
    assert PACK in rk.resolve_packs(flipped, rk.chain_for(flipped, NODE))


def test_a_declined_pack_is_reported_once_and_by_the_decline(flipped):
    """`refusals_for` already carries a decline. Naming the same absence twice under two
    mechanisms would have a reader believe two things happened."""
    rk = _rk()
    flipped["nodes"][NODE]["declined_packs"] = [
        {"pack": PACK, "why": "a fixture, not a corpus decline"}]
    assert rk.withheld_for(flipped, NODE) == {}
    assert [r["pack"] for r in rk.refusals_for(flipped, NODE)] == [PACK]


def test_a_pack_the_node_binds_itself_is_never_withheld(flipped, graph):
    """`chain[0]` is the node and binding IS opting in -- the same guard `declined_packs` and
    `resolve_packs` both carry, and the one whose absence would delete an authored record."""
    rk = _rk()
    binder = next(n for n, v in graph["nodes"].items()
                  if any(e["pack"] == PACK for e in (v.get("proportion_packs") or [])))
    assert rk.withheld_for(flipped, binder) == {}
    assert PACK in rk.resolve_packs(flipped, rk.chain_for(flipped, binder))


# ------------------------------------------------------------------ marked, not deleted

def test_the_rules_are_built_and_marked_rather_than_never_existing(flipped):
    """WP-8.3's rule, applied to WP-8.9's gate. If these rows were dropped the address would go
    quiet and nothing downstream could name what happened -- which is the whole defect."""
    _p, wh, _k, by_slot = _resolve(flipped)
    marked = [r for rows in by_slot.values() for r in rows if r.get("withheld_by_opt_in")]
    assert marked, "the withheld pack contributed no rows at all -- it was dropped, not marked"
    assert {r["pack"] for r in marked} == {PACK}
    assert all(r["withheld_because"] and "opt-in" in r["withheld_because"] for r in marked)


def test_every_row_carries_the_key_whether_or_not_it_is_set(flipped):
    """Always present, True or False -- the same contract `refused_by_kit` keeps. A key only on
    the bad rows makes `r.get(k)` and `r[k]` disagree about a row nobody looked at."""
    _p, _w, _k, by_slot = _resolve(flipped)
    rows = [r for rs in by_slot.values() for r in rs]
    assert rows
    assert all("withheld_by_opt_in" in r and "withheld_because" in r for r in rows)


def test_a_withheld_packs_out_of_scope_rule_does_not_inflate_the_scope_meter(flipped):
    """`scope_dropped` means "scope removed this delivery". A pack the gate already stopped has
    no delivery for scope to remove, and counting it would put OQ 88's meter up with rules that
    were never going to arrive."""
    rk = _rk()
    chain = rk.chain_for(flipped, NODE)
    packs = rk.resolve_packs(flipped, chain)
    kit, _sv = rk.resolve_slots(flipped, chain, rk.scope_for(flipped, NODE))
    a, b = [], []
    rk.eval_packs(packs, CTX, None, kit, a)
    rk.eval_packs(packs, CTX, None, kit, b, withheld=rk.withheld_for(flipped, NODE))
    assert a == b, "the withheld pack's rules reached scope_dropped"


# ------------------------------------------------------------------ choose_pack

WITHHELD_SLOTS = ("gable_treatment", "rake_condition", "cornice_return", "dormer")


@pytest.mark.parametrize("sid", WITHHELD_SLOTS)
def test_the_address_names_the_pack_instead_of_falling_silent(flipped, sid):
    ch = _choice(flipped, sid)
    assert ch["how"] == "opt-in.withheld", ch["how"]
    assert ch["chosen"] is None
    assert [r["pack"] for r in ch["refused"]] == [PACK] * len(ch["refused"])
    assert PACK in ch["why"] and "inherits_packs" in ch["why"], ch["why"]


def test_the_branch_returns_every_key_its_SIBLING_REFUSAL_does(flipped, graph):
    """WP-8.3 shipped the `kit.forbidden` branch with keys missing and no caller to find it --
    a KeyError on 776 pairs, found by an audit two packages later. This is the same branch shape
    one mechanism over, so it is held against that branch as it really runs on this corpus,
    rather than against a list of key names written here and able to go stale with it.

    THE PEER IS THE REFUSAL BRANCH AND NOT A RULED ONE, and the first version of this test got
    that wrong: a ruled branch also returns `other_quantities`, which is OQ 48's report and is
    read with `.get` everywhere precisely because only one branch produces it. Requiring it here
    would have made a refusal claim to have adjudicated competing quantities it never saw."""
    withheld = _choice(flipped, "cornice_return")
    forbidden = _choice(graph, "parapet", nid="tidewater-georgian")
    assert forbidden["how"] == "kit.forbidden", forbidden["how"]
    assert set(withheld) == set(forbidden), (
        sorted(set(forbidden) ^ set(withheld)),
        "the two refusal branches must be interchangeable to every unconditional reader")
    for k in ("how", "chosen", "ranked", "rejected", "stale_calibration", "refused", "why"):
        assert k in withheld, k


def test_the_optional_key_is_optional_at_every_reader(flipped):
    """`other_quantities` is absent from both refusal branches, so any reader that indexes it
    would fail on 776 kit-forbidden pairs and on every withheld address. Source-read, because
    there is no way to enumerate readers at runtime."""
    import glob
    import re
    bad = []
    for f in (sorted(glob.glob(os.path.join(ROOT, "build", "*.py")))
              + sorted(glob.glob(os.path.join(ROOT, "mcp_server", "*.py")))):
        for i, line in enumerate(open(f, encoding="utf-8"), 1):
            if re.search(r'\[\s*"other_quantities"\s*\]', line):
                bad.append("%s:%d" % (os.path.basename(f), i))
    assert not bad, bad


def test_a_marked_row_is_never_chosen_even_as_the_only_candidate(flipped):
    """The mark is made in `eval_packs`, where the binding is in hand; the refusal to choose is
    made here. One judgment, two places, and they agree because only one of them decides."""
    rk = _rk()
    _p, _w, kit, by_slot = _resolve(flipped)
    for sid in WITHHELD_SLOTS:
        rows = by_slot[sid]
        assert rows and all(r["withheld_by_opt_in"] for r in rows), sid
        assert rk.choose_pack(kit.get(sid) or {}, rows, CTX)["chosen"] is None


def test_a_delivered_row_still_wins_at_an_address_a_withheld_one_also_writes(flipped):
    """The gate must not turn a shared address into a refusal. Driven by handing the chooser one
    of each rather than by finding a corpus node that happens to have both."""
    rk = _rk()
    _p, _w, kit, by_slot = _resolve(flipped)
    live = next(r for rows in by_slot.values() for r in rows if not r["withheld_by_opt_in"])
    dead = dict(by_slot["cornice_return"][0])
    got = rk.choose_pack({}, [dead, live], CTX)
    assert got["how"] != "opt-in.withheld", got
    assert got.get("chosen") is None or got["chosen"]["pack"] != PACK


# ------------------------------------------------------------------ the meter did not move

def test_wiring_the_reasons_in_did_not_change_what_is_counted(graph):
    """LOAD-BEARING. The reasons are carried by rows `choose_pack` filters before anything else,
    so a stranding figure measured with them on must equal the same figure measured with them
    off. If this drifts, the meter has started counting the explanation."""
    ci = _ci()
    g = ci.load()
    for nid in ("egyptian-revival", "ranch-style", "tidewater-georgian", NODE):
        plain, _k = ci.governed(g, nid)
        out = {}
        withreasons, _k2 = ci.governed(g, nid, withheld_out=out)
        assert plain == withreasons, nid
        dropped, _k3 = ci.governed(g, nid, drop={"facade-gable"})
        out2 = {}
        dropped2, _k4 = ci.governed(g, nid, drop={"facade-gable"}, withheld_out=out2)
        assert dropped == dropped2, nid


def test_the_counterfactual_drop_is_reported_as_a_withhold(graph):
    """`--stranding` models the flip by dropping packs. Modelling the drop as a DELETION and the
    shipped gate as a MARK would report the same event two ways and the meter would stop
    describing the mechanism it is a meter for."""
    ci = _ci()
    g = ci.load()
    out = {}
    ci.governed(g, NODE, drop={"facade-gable"}, withheld_out=out)
    assert out, "the counterfactual stranded nothing here -- pick another fixture node"
    assert all(p == "facade-gable" for p, _why in out.values()), out
    assert all("withholds" in why for _p, why in out.values()), out


def test_the_sweep_reports_every_stranded_slot_as_named():
    """The measurement the package exists to make. If this falls below the stranded count, some
    address is stranded without an explanation and the residue must be named in the report --
    never left to look like rounding."""
    out = subprocess.run([sys.executable, "build/check_inheritance.py", "--stranding"],
                         cwd=ROOT, capture_output=True, text=True)
    assert out.returncode == 0, out.stdout[-600:]
    import re
    st = int(re.search(r"STRANDED — lose all dimensioning\s+(\d+)", out.stdout).group(1))
    nm = int(re.search(r"NAMED as withheld\s+(\d+)", out.stdout).group(1))
    assert nm == st == 2889, (nm, st)   # 2899 before the first flip took ten of them
    assert "reads UNDIMENSIONED, not refused" not in out.stdout, (
        "the closing paragraph still says the defect is unfixed -- 'until X lands' is a lie the "
        "moment X lands (WP-6.4)")
