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

EVERYTHING HERE IS DRIVEN, NEVER READ OFF THE CORPUS. The fixture flips a pack the corpus does
NOT flip, so these assertions keep meaning the same thing after a real pack is flipped and after
the last one is.

**THE FIXTURE MOVED IN WP-8.11 AND THAT IS THE POINT OF THIS PARAGRAPH.** It was `facade-gable`
on `north-german-hall-house` — chosen in WP-8.10 precisely because the corpus left that pack on
`cascade`. WP-8.11 flipped `facade-gable` for real, which would have turned every driven assertion
below into an assertion about the shipped corpus: green, and vacuous, since the "counterfactual"
would have been the status quo. A driven fixture has to name a pack nobody has flipped, so **check
that before flipping the next one** — `sash-light` is next by size and is not used here.
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
NODE = "mediterranean-revival"
PACK = "trim-craftsman"        # on `cascade`; reaches NODE from `mission-revival` and governs 3 slots


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

def test_withheld_for_names_exactly_the_shipped_FLIPS_that_reach_this_node(graph):
    """WP-8.10 wrote this as "empty where nothing is flipped" and WP-8.11 made it say something:
    two packs are flipped now, both reach this node, and the report names both and nothing else.
    That is strictly better than the empty assertion it replaces — a reporting function that
    always has nothing to say is as unfalsifiable as one that always has something."""
    rk = _rk()
    got = set(_rk().withheld_for(graph, NODE))
    # SIX of the eight shipped flips reach this node -- `opening-proportion` and `timber-bay`
    # do not, which is why the set is asserted rather than a count: a count would have been
    # satisfied by any six and this names which.
    assert got == {"trim-classical", "facade-gable", "sash-light", "facade-classical",
                   "storey-graduation", "gibbs-ionic"}, sorted(got)
    assert PACK not in got, (
        "the driven fixture's pack has been flipped for real — every assertion in this file is "
        "now about the shipped corpus rather than about the gate; move the fixture")


def test_withheld_for_names_the_pack_and_the_ancestor_that_would_have_sent_it(flipped):
    rk = _rk()
    wh = rk.withheld_for(flipped, NODE)
    assert PACK in wh, sorted(wh)
    assert wh[PACK]["_would_have_come_from"] == wh[PACK]["_source"] == "mission-revival"
    assert "inherits_packs" in wh[PACK]["_why"], wh[PACK]["_why"]


def test_an_opt_in_removes_it_from_the_withheld_report(flipped):
    """It is not withheld if the node admitted it -- the report must track the mechanism, or a
    reader is told a delivery was stopped that in fact arrived."""
    rk = _rk()
    flipped["nodes"][NODE]["inherits_packs"] = [PACK]
    assert PACK not in rk.withheld_for(flipped, NODE)
    assert PACK in rk.resolve_packs(flipped, rk.chain_for(flipped, NODE))


def test_a_declined_pack_is_reported_once_and_by_the_decline(flipped):
    """`refusals_for` already carries a decline. Naming the same absence twice under two
    mechanisms would have a reader believe two things happened."""
    rk = _rk()
    flipped["nodes"][NODE]["declined_packs"] = [
        {"pack": PACK, "why": "a fixture, not a corpus decline"}]
    assert PACK not in rk.withheld_for(flipped, NODE)
    assert [r["pack"] for r in rk.refusals_for(flipped, NODE)] == [PACK]


def test_a_pack_the_node_binds_itself_is_never_withheld(flipped, graph):
    """`chain[0]` is the node and binding IS opting in -- the same guard `declined_packs` and
    `resolve_packs` both carry, and the one whose absence would delete an authored record."""
    rk = _rk()
    binder = next(n for n, v in graph["nodes"].items()
                  if any(e["pack"] == PACK for e in (v.get("proportion_packs") or [])))
    assert PACK not in rk.withheld_for(flipped, binder)
    assert PACK in rk.resolve_packs(flipped, rk.chain_for(flipped, binder))


# ------------------------------------------------------------------ marked, not deleted

def test_the_rules_are_built_and_marked_rather_than_never_existing(flipped):
    """WP-8.3's rule, applied to WP-8.9's gate. If these rows were dropped the address would go
    quiet and nothing downstream could name what happened -- which is the whole defect."""
    _p, wh, _k, by_slot = _resolve(flipped)
    marked = [r for rows in by_slot.values() for r in rows if r.get("withheld_by_opt_in")]
    assert marked, "the withheld pack contributed no rows at all -- it was dropped, not marked"
    # PACK is the driven one; the other two are the corpus's own shipped flips reaching this node.
    # Asserting the SET equals {PACK} would have been a coincidence of WP-8.10's fixture node, and
    # it broke the moment a real flip touched the same node.
    assert PACK in {r["pack"] for r in marked}
    assert {r["pack"] for r in marked} <= {PACK, "trim-classical", "facade-gable", "sash-light",
                                           "facade-classical", "storey-graduation",
                                           "gibbs-ionic"}
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

WITHHELD_SLOTS = ("trim_family", "built_ins", "newel_balustrade")


@pytest.mark.parametrize("sid", WITHHELD_SLOTS)
def test_the_address_names_the_pack_instead_of_falling_silent(flipped, sid):
    ch = _choice(flipped, sid)
    assert ch["how"] == "opt-in.withheld", ch["how"]
    assert ch["chosen"] is None
    # Every refused row is a withheld one, and the driven pack is among them. The address may be
    # written by more than one withheld pack once the corpus has real flips -- what must hold is
    # that NONE of them was delivered, not that exactly one wanted to write here.
    assert ch["refused"] and all(r["withheld_by_opt_in"] for r in ch["refused"])
    assert PACK in {r["pack"] for r in ch["refused"]}
    assert "inherits_packs" in ch["why"], ch["why"]


def test_the_branch_returns_every_key_its_SIBLING_REFUSAL_does(flipped, graph):
    """WP-8.3 shipped the `kit.forbidden` branch with keys missing and no caller to find it --
    a KeyError on 776 pairs, found by an audit two packages later. This is the same branch shape
    one mechanism over, so it is held against that branch as it really runs on this corpus,
    rather than against a list of key names written here and able to go stale with it.

    THE PEER IS THE REFUSAL BRANCH AND NOT A RULED ONE, and the first version of this test got
    that wrong: a ruled branch also returns `other_quantities`, which is OQ 48's report and is
    read with `.get` everywhere precisely because only one branch produces it. Requiring it here
    would have made a refusal claim to have adjudicated competing quantities it never saw."""
    withheld = _choice(flipped, WITHHELD_SLOTS[0])
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
    dead = dict(by_slot[WITHHELD_SLOTS[0]][0])
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
    for nid in ("egyptian-revival", "ranch-style", "tidewater-georgian", NODE):  # noqa: E501
        plain, _k = ci.governed(g, nid)
        out = {}
        withreasons, _k2 = ci.governed(g, nid, withheld_out=out)
        assert plain == withreasons, nid
        # A pack still on `cascade`: dropping an already-flipped one is a no-op drop and would
        # make this test pass without exercising the counterfactual at all.
        dropped, _k3 = ci.governed(g, nid, drop={PACK})
        out2 = {}
        dropped2, _k4 = ci.governed(g, nid, drop={PACK}, withheld_out=out2)
        assert dropped == dropped2, nid


def test_the_counterfactual_drop_is_reported_as_a_withhold(graph):
    """`--stranding` models the flip by dropping packs. Modelling the drop as a DELETION and the
    shipped gate as a MARK would report the same event two ways and the meter would stop
    describing the mechanism it is a meter for."""
    ci = _ci()
    g = ci.load()
    out = {}
    ci.governed(g, NODE, drop={PACK}, withheld_out=out)
    assert out, "the counterfactual stranded nothing here -- pick another fixture node"
    # The node also carries the corpus's REAL flips, so this filters to the counterfactual's own
    # entries rather than asserting over all of them -- the two mechanisms report side by side
    # and each says which it is, which is the property worth holding.
    mine = {sid: why for sid, (pk, why) in out.items() if pk == PACK}
    assert mine, sorted((sid, pk) for sid, (pk, _w) in out.items())
    assert all("withholds" in why for why in mine.values()), mine
    shipped = {pk for pk, _w in out.values()} - {PACK}
    assert shipped <= {"trim-classical", "facade-gable", "sash-light"}, shipped
    assert all("delivery: opt-in" in why
               for pk, why in out.values() if pk in shipped), out


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
    # 2899 -> 2889 at the trim-classical flip -> 2857 at facade-gable's: a flipped pack's slots
    # leave the counterfactual because they are already withheld, and the ALREADY WITHHELD block
    # above the sweep is where they are now counted (42 over 36 nodes).
    # 2899 -> 2889 -> 2857 -> 2787 -> 2585 across the four flips.
    assert nm == st == 2585, (nm, st)
    assert "reads UNDIMENSIONED, not refused" not in out.stdout, (
        "the closing paragraph still says the defect is unfixed -- 'until X lands' is a lie the "
        "moment X lands (WP-6.4)")
