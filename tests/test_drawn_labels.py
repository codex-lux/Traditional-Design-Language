"""The label layer, pinned where a browser is not needed.

Three classes of defect are guarded here, all found by the 26 Aug 2026 audit of the
workbench legibility pass and none of them previously covered by anything:

1. A room's name must fit in the room, must never be truncated, and must never be
   dropped. The e2e walk measures this in a real browser for the React sheet; this pins
   the SAME rule for `build/render_plan.py`, which is the renderer behind the Drawing Set
   and every exported SVG, and which no test touched at all.
2. A computed size or colour written as an SVG PRESENTATION ATTRIBUTE is silently beaten
   by any class rule in the same document's <style> block. That bug shipped for one build
   in `render_plan.py` and was still live in three other places. It is invisible in every
   way except by looking at the drawing, so it is asserted structurally here.
3. The engine's member positions are ABSOLUTE in the stack. `CLAUDE.md` states that all
   26 order packs run contiguously from 0, and the workbench plate is built on that
   statement; nothing checked it. It is cheap to check and it belongs in the suite rather
   than in a sentence.
"""
import importlib.util
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build"))
import modcache  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name):
    return modcache.load(name, os.path.join(ROOT, "build", f"{name}.py"))


def _rendered(rel="plans/tidewater-georgian-careful.json", candidates=120):
    geo, rp = _load("geometry"), _load("render_plan")
    out = geo.solve(json.load(open(os.path.join(ROOT, rel))), candidates=candidates)
    path = os.path.join(ROOT, "dist", "_test_labels.svg")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rp.render(out, path)
    svg = open(path).read()
    os.remove(path)
    return out, svg


# --------------------------------------------------------------- the fitter itself

def test_a_name_is_never_truncated():
    """`nm[:9]` did not shorten a name, it amputated one: 'Butler's Pantry' was drawn
    'Butler's ' and read as the room's actual name."""
    rp = _load("render_plan")
    for name in ("Butler's Pantry", "Kitchen (Dependency)", "Principal Chamber",
                 "Back Hall (Hyphen)", "Entrance Portico"):
        for box in ((60, 40), (30, 20), (14, 9), (6, 6)):
            lines, size = rp._fit_lines(name, box[0], box[1], 9.5, 6.0)
            assert " ".join(lines).split() == name.split(), (name, box, lines)
            assert size >= 6.0


def test_the_fitter_survives_what_a_record_can_carry():
    rp = _load("render_plan")
    assert rp._fit_lines("", 60, 40, 9.5, 6.0) is None
    assert rp._fit_lines("   ", 60, 40, 9.5, 6.0) is None
    one = rp._fit_lines("Library", 60, 40, 9.5, 6.0)
    assert one == (["Library"], 9.5)
    # a single word longer than the box is set at the floor, whole
    long_word = "Supercalifragilisticexpialidocious"
    lines, size = rp._fit_lines(long_word, 20, 20, 9.5, 6.0)
    assert lines == [long_word] and size == 6.0
    # negative geometry cannot raise
    assert rp._fit_lines("Two Words", -5, -5, 9.5, 6.0)[1] == 6.0


def test_the_fitter_is_not_a_cpu_bomb():
    """The exhaustive split is O(W^3) and a plan record arrives over HTTP from anyone who
    can reach /api/drawings. Before the cap, 800 words took 73 seconds of pure CPU."""
    rp = _load("render_plan")
    t = time.time()
    lines, _ = rp._fit_lines(" ".join(["word"] * 4000), 200, 200, 9.5, 6.0)
    spent = time.time() - t
    assert spent < 1.0, f"{spent:.1f}s for 4000 words — the bound is gone"
    assert len(lines) <= 3
    assert " ".join(lines).split() == ["word"] * 4000     # bounded, still whole


def test_balance_really_balances():
    """Brute-forced against every split, because a wrapper that picks a bad break is a
    wrapper that shrinks the type for no reason."""
    import itertools
    rp = _load("render_plan")
    width = lambda s: rp._text_w(s, 1.0)
    for words in (["Back", "Hall", "(Hyphen)"], ["A", "BB", "CCC", "DDDD"],
                  ["Principal", "Chamber"], ["One"], ["Kitchen", "(Dependency)"]):
        for n in (1, 2, 3, 4):
            got = rp._balance(words, n)
            if n > len(words):
                assert got is None
                continue
            best = None
            for cuts in itertools.combinations(range(1, len(words)), n - 1):
                prev, lines = 0, []
                for c in cuts:
                    lines.append(" ".join(words[prev:c])); prev = c
                lines.append(" ".join(words[prev:]))
                w = max(width(x) for x in lines)
                if best is None or w < best:
                    best = w
            assert abs(max(width(x) for x in got) - best) < 1e-9, (words, n, got)


# ------------------------------------------------------- the label on the real sheet

def _texts(svg, cls):
    return re.findall(rf'<text class="{cls}"[^>]*>([^<]*)</text>', svg)


def test_every_room_is_named_on_the_sheet():
    """The spill check can pass vacuously on a sheet with no labels at all. This is the
    other half: a room the renderer placed is a room the renderer names."""
    out, svg = _rendered()
    placed = sum(1 for lv in out["levels"] for r in lv["rooms"] if r.get("geometry"))
    named = _texts(svg, "nm")
    assert placed >= 20
    # names may be broken across lines, so the count of TEXT runs is >= the room count
    assert len(named) >= placed, f"{len(named)} name runs for {placed} placed rooms"
    joined = " ".join(named)
    for want in ("Butler's", "Pantry", "Kitchen", "(Dependency)", "Entrance", "Portico"):
        assert want in joined, want


def test_a_fitted_size_is_written_where_it_wins():
    """A presentation attribute loses to `.nm`/`.dm` in this sheet's own <style>, so a
    correctly computed size written as `font-size="7.2"` is computed, discarded, and the
    label runs through the wall anyway. It shipped that way for one build."""
    _, svg = _rendered()
    assert 'style="font-size:' in svg
    assert not re.search(r'<text class="(nm|dm)"[^>]*\sfont-size="', svg), \
        "a fitted size written as an attribute is a fitted size that does not apply"


def test_no_class_rule_silently_beats_a_presentation_attribute():
    """The general form of the same fault, asserted against the document rather than
    against a list of known sites: for every property a class in the <style> block sets,
    no element carrying that class may also carry it as an attribute."""
    for rel in ("plans/tidewater-georgian-careful.json",):
        _, svg = _rendered(rel)
        block = re.search(r"<style>(.*?)</style>", svg, re.S).group(1)
        for cls, body in re.findall(r"\.(\w+)\{([^}]*)\}", block):
            props = {d.split(":")[0].strip() for d in body.split(";") if ":" in d}
            for el in re.findall(rf'<\w+ class="{cls}"[^>]*>', svg):
                attrs = set(re.findall(r'\s([a-z-]+)="', el))
                clash = props & attrs - {"class", "style"}
                assert not clash, f".{cls} sets {clash} in CSS and the element sets it as an attribute: {el[:120]}"


def test_the_void_disclosure_is_not_carried_by_the_dimension_line():
    """OQ 55's disclosure is a statement about what the room IS. Riding it on the
    dimension string meant it dropped out for every room under ~19 ft wide — which is
    most loggias and every piazza in the catalogue — while the test that guards it passed
    on a fixture that happened to have a 20 ft court."""
    rp = _load("render_plan")
    src = open(os.path.join(ROOT, "build", "render_plan.py")).read()
    assert 'dim = f\'{_fmt(min(w,h))} x {_fmt(max(w,h))} · {g["area_sf"]} sf\'' in src, \
        "the void tail is back on the dimension string"
    # and it is drawn from its own size, with its own floor
    assert "tsize" in src and 'style="font-size:{tsize' in src


# ----------------------------------------------------------------- the order stack

def test_every_order_pack_is_one_contiguous_stack():
    """CLAUDE.md states it and the workbench plate is built on it; nothing checked it.
    A member's y_bottom_in/y_top_in are ABSOLUTE — the cumulative sum has already run —
    so a gap here would mean either the engine or the claim is wrong."""
    pe = _load("proportion_engine")
    packs = [p for p, v in pe.PACKS.items() if v.get("kind") == "order-system"]
    assert len(packs) >= 26
    checked = 0
    for pid in packs:
        pk = pe.resolve(pid)
        d = pe.dimension(pk, 36.0, None)
        if not d["assemblies"]:
            continue                       # moorish-arch publishes no stack at all
        checked += 1
        cursor = 0.0
        for a in d["assemblies"]:
            ms = a["members"]
            assert ms, (pid, a["id"], "assembly in the stack with no members")
            y0 = min(m["y_bottom_in"] for m in ms)
            y1 = max(m["y_top_in"] for m in ms)
            assert abs(y0 - cursor) < 0.02, (pid, a["id"], "gap", y0, cursor)
            assert abs((y1 - y0) - a["height_in_stated"]) < 0.05, \
                (pid, a["id"], "summed members disagree with the stated height")
            cursor = y1
        assert abs(cursor - d["totals"]["stack_height_in"]) < 0.05, (pid, cursor)
    assert checked >= 25


def test_every_pack_that_projects_declares_which_datum_it_projects_from():
    """OQ 65, RULED 26 Aug 2026 — declare the datum on the pack.

    Thirteen packs record `projection_parts` as an offset from the member's own naked and
    twelve as an absolute radius from the axis, split by order across all five
    authorities. Nothing said which, so every consumer derived it, and the one that got it
    wrong drew Vignola's Ionic 2.25x too wide with the shaft narrower than its own
    mouldings. The ruling is that the pack says so and the reader believes it.

    What is pinned here is that the declaration is not merely PRESENT but TRUE — verified
    against each pack's own geometry, which is the only thing that makes a declared field
    better than a derived one. `build/check_orders.py` runs the same check on every build;
    this is the suite's own copy of it, and it also pins that the value survives the
    overlay cascade, which is where nineteen of the twenty-six get theirs."""
    pe = _load("proportion_engine")
    seen = {"naked": 0, "axis": 0}
    inherited = 0
    for pid, v in pe.PACKS.items():
        if v.get("kind") != "order-system":
            continue
        r = pe.resolve(pid)
        d = pe.dimension(r, 36.0, None)
        declared = d["projection_datum"]
        has_proj = any((m.get("projection_in") or 0)
                       for a in d["assemblies"] for m in a.get("members", []))
        if not has_proj:
            continue                        # moorish-arch: no projections, nothing to say
        assert declared in ("naked", "axis"), \
            f"{pid} carries projections and declares no datum — a reader has to guess"
        observed = pe.observed_projection_datum(d)
        assert observed is None or observed == declared, \
            f"{pid} declares '{declared}' and its own geometry reads '{observed}'"
        seen[declared] += 1
        if not v.get("projection_datum"):
            inherited += 1
    assert seen["naked"] and seen["axis"], seen           # both readings are still live
    assert seen["naked"] + seen["axis"] >= 25
    assert inherited >= 15, "the overlay cascade stopped carrying it"


def test_the_datum_is_verified_and_not_merely_trusted():
    """A declared field nobody checks is a comment. Declare the wrong thing and the
    corpus's own checker must say so — including on every overlay that inherits it."""
    import copy
    pe = _load("proportion_engine")
    pack = copy.deepcopy(pe.PACKS["vignola-ionic"])
    assert pack["projection_datum"] == "axis"
    pack["projection_datum"] = "naked"
    saved = pe.PACKS["vignola-ionic"]
    pe.PACKS["vignola-ionic"] = pack
    try:
        d = pe.dimension(pe.resolve("vignola-ionic"), 36.0, None)
        assert d["projection_datum"] == "naked"
        assert pe.observed_projection_datum(d) == "axis", "the observation stopped biting"
        # and the lie travels down the cascade, which is why the checker walks resolved packs
        dg = pe.dimension(pe.resolve("gibbs-ionic"), 36.0, None)
        assert dg["projection_datum"] == "naked"
        assert pe.observed_projection_datum(dg) == "axis"
    finally:
        pe.PACKS["vignola-ionic"] = saved
