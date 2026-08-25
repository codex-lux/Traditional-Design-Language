"""Two rulings, OQ 37 and OQ 38, both about a ranking deciding something it cannot.

OQ 37 — `find_faults` sorted on two coarse enums over 209 faults and then cut at `limit`.
For queen-anne-american the cut fell inside a tie group of 104: one fault kept, 103
dropped, all ranked identically. Ruled 25 Aug 2026: widen the key, and report what the cut
still takes out of a tie so the residue reads as unranked rather than unimportant.

OQ 38 — `resolve_kit.choose_pack` settled two packs at the same precedence by their
position in the JSON array and labelled the result "the author's explicit ruling". Ruled
the same day: equal precedence records that NO ruling was made, so the slot is unresolved.
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (os.path.join(ROOT, "mcp_server"), os.path.join(ROOT, "build")):
    if p not in sys.path:
        sys.path.insert(0, p)


@pytest.fixture(scope="module")
def core_mod():
    import core
    return core


@pytest.fixture(scope="module")
def rk_mod():
    import resolve_kit
    return resolve_kit


# ------------------------------------------------------------------ OQ 37

def test_the_widened_key_breaks_the_worst_tie(core_mod):
    """queen-anne-american was the worst case: 103 faults cut out of a 104-wide tie.

    The number is asserted as a ceiling, not pinned exactly, because the corpus grows —
    but a regression to the coarse key puts it back into three figures.
    """
    r = core_mod.find_faults(style="queen-anne-american", limit=25)
    assert r["truncated_within_tie"] <= 5, (
        f"{r['truncated_within_tie']} faults cut from inside a tie group — the ranking "
        f"key has lost its discriminators again")


def test_the_ranking_is_totally_ordered(core_mod):
    """Ends in the fault id, so the cut is reproducible to the last place rather than
    falling back to whatever order the corpus happened to load in."""
    faults = core_mod.find_faults(style="georgian-colonial-american",
                                  limit=10 ** 6)["faults"]
    ids = [f["id"] for f in faults]
    assert len(ids) == len(set(ids))
    # Any two adjacent faults that rank identically on every axis must be in id order.
    for a, b in zip(faults, faults[1:]):
        same = (a["severity"] == b["severity"]
                and a.get("severity_in_use") == b.get("severity_in_use")
                and a.get("frequency") == b.get("frequency"))
        if same and not ({"EXCEPTION_FOR_THIS_STYLE", "INVERTED_FOR_THIS_STYLE"}
                         & (set(a) ^ set(b))):
            assert a["id"] <= b["id"], f"{a['id']} before {b['id']} with no tie-break"


def test_a_truncated_tie_is_declared(core_mod):
    """The whole point of the ruling: `matches` said truncation happened, but nothing said
    the boundary fell inside a group the ranking cannot order."""
    r = core_mod.find_faults(style="georgian-colonial-american", limit=25)
    assert r["truncated_within_tie"] > 0, "expected this style to still cut inside a tie"
    assert r["truncation_note"] and "not by importance" in r["truncation_note"]


def test_no_truncation_note_when_nothing_was_cut_from_a_tie(core_mod):
    """It must not cry wolf: a clean cut, or no cut at all, says nothing."""
    r = core_mod.find_faults(style="tidewater-georgian", limit=10 ** 6)
    assert r["truncated_within_tie"] == 0
    assert r["truncation_note"] is None


# ------------------------------------------------------------------ OQ 38

def _slot_packs(style, slot):
    with open(os.path.join(ROOT, "kits", f"{style}.kit.json")) as f:
        return (json.load(f)["slots"].get(slot) or {}).get("packs") or []


def test_equal_precedence_is_reported_unresolved(rk_mod):
    """Two packs at precedence 1 is not a ruling, and must not be labelled as one."""
    rec = {"packs": [{"pack": "brick-course", "precedence": 1},
                     {"pack": "opening-proportion", "precedence": 1}]}
    got = rk_mod.choose_pack(rec, [], {})
    assert got["how"] == "unresolved", got["how"]
    assert got["chosen"] is None
    assert "no ruling was made" in got["why_unresolved"]
    assert "brick-course" in got["why_unresolved"]


def test_a_real_precedence_still_resolves(rk_mod):
    """The ruling must not make every multi-pack slot unresolved — a stated order is
    exactly what `how: slot.packs` is for."""
    rec = {"packs": [{"pack": "brick-course", "precedence": 2},
                     {"pack": "opening-proportion", "precedence": 1}]}
    got = rk_mod.choose_pack(rec, [], {})
    assert got["how"] == "slot.packs"
    assert got["chosen"]["pack"] == "opening-proportion"


def test_an_out_of_calibration_pack_does_not_create_a_false_tie(rk_mod):
    """Only LIVE packs can tie. One of the four real cases resolves for exactly this
    reason, and treating it as a tie would invent a question the corpus already answered."""
    rec = {"packs": [{"pack": "brick-course", "precedence": 1, "in_calibration": False},
                     {"pack": "opening-proportion", "precedence": 1}]}
    got = rk_mod.choose_pack(rec, [], {})
    assert got["how"] == "slot.packs"
    assert got["chosen"]["pack"] == "opening-proportion"


def test_the_four_live_cases_are_still_the_reason_this_exists():
    """If an authoring pass ever breaks these ties deliberately, the tests above stop
    describing the corpus and should be re-pointed at whatever replaced them."""
    pairs = [("window_head_masonry", {"brick-course", "opening-proportion"}),
             ("window_head_wood", {"brick-course", "opening-proportion"}),
             ("window_surround_masonry", {"sash-light", "brick-course"}),
             ("window_surround_wood", {"sash-light", "brick-course"})]
    for slot, expected in pairs:
        packs = _slot_packs("georgian-colonial-american", slot)
        at_one = {p.get("pack") for p in packs if p.get("precedence") == 1}
        assert at_one == expected, f"{slot}: {at_one} != {expected}"


def test_ranked_order_does_not_depend_on_authoring_order(rk_mod):
    """`ranked` is reported to the caller, and the sort was stable over JSON array
    position — so two kits declaring the same packs in a different order described the
    same slot differently. Feed both orders and demand one answer."""
    a = {"packs": [{"pack": "brick-course", "precedence": 1},
                   {"pack": "opening-proportion", "precedence": 1}]}
    b = {"packs": list(reversed(a["packs"]))}
    order_a = [p["pack"] for p in rk_mod.choose_pack(a, [], {})["ranked"]]
    order_b = [p["pack"] for p in rk_mod.choose_pack(b, [], {})["ranked"]]
    assert order_a == order_b == ["brick-course", "opening-proportion"], (order_a, order_b)
