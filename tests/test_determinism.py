"""The corpus must load in the same order on every machine.

The finding these pin, from the first CI run this project ever had (PR #2, 25 Aug 2026):
two composer tests passed on the authoring machine and failed on the runner. Neither the
composer nor the geometry solver is random — `geometry.solve` is seeded at 7 and
`compose.py` imports no RNG — but the corpus was loaded through unsorted `glob.glob`,
which returns directory order, and `pick_partis` then sorted on `fit` alone.

Python's sort is stable, so a tie fell back to insertion order, and `out[:limit]` cut
through the middle of it. For `briefs/family-georgian.json` four diagrams tie at fit 2.00
and only three survived the cut — so *which* diagram the composer never even scored was
decided by readdir. On this machine `side-hall-townhouse` survived and won; on the runner
it did not, and the assertion that it ranks first failed.

The tests below defend the two halves of the fix independently, because either one alone
leaves the other failure mode live.
"""
import glob as glob_module
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def compose_mod():
    import compose
    return compose


def _brief(name):
    with open(os.path.join(ROOT, "briefs", f"{name}.json")) as f:
        return json.load(f)


def test_corpus_globs_are_sorted():
    """Every corpus-loading glob in the toolchain is wrapped in sorted().

    Greps rather than introspects, because the failure is a *missing* wrapper — there is
    nothing to call once it is absent, and the next unsorted glob someone adds is exactly
    the regression this file exists to catch.
    """
    # Every way this codebase can read a directory. The first version of this test
    # matched only the literal "glob.glob(", which would have missed the next unsorted
    # read spelled any other way — and two really did survive it, in tests/ itself,
    # which is where the original cross-machine failure actually surfaced.
    readers = ("glob.glob(", "iglob(", "os.listdir(", "os.scandir(", "os.walk(",
               ".iterdir(", ".rglob(")
    offenders = []
    for sub in ("build", "mcp_server", "workbench", "tests"):
        for path in sorted(glob_module.glob(os.path.join(ROOT, sub, "**", "*.py"),
                                            recursive=True)):
            if os.path.basename(path) == os.path.basename(__file__):
                continue          # this file names the readers in order to look for them
            with open(path) as f:
                for n, line in enumerate(f, 1):
                    for r in readers:
                        i = line.find(r)
                        if i == -1:
                            continue
                        # Guarded when a sorted( opens before the read — which covers
                        # sorted(os.listdir(x)) and also sorted(f for f in os.listdir(x)),
                        # the comprehension form a literal "sorted(os.listdir(" match
                        # flagged as an offender when it was already correct.
                        s = line.find("sorted(")
                        if s != -1 and s < i:
                            continue
                        rel = os.path.relpath(path, ROOT)
                        offenders.append(f"{rel}:{n}: {line.strip()}")
    assert not offenders, (
        "unsorted directory read — the order is machine-specific:\n  "
        + "\n  ".join(offenders))


def test_pick_partis_expansion_is_bounded(compose_mod):
    """A narrow tie is kept whole; a wide one is not, because expanding it costs compose
    time proportional to the pool and adds nothing the fit function actually knows.

    adam-style has no native parti and no massing affinity — the majority case in this
    corpus — so ten diagrams tie at the cut. Before the bound, limit=6 returned all 12
    and doubled the composer's work."""
    wide = compose_mod.pick_partis(
        {"style": "adam-style", "target_area_sf": 6000, "bedrooms": 3}, limit=6)
    assert len(wide) == 6, f"wide tie must take the deterministic cut, got {len(wide)}"

    narrow = compose_mod.pick_partis(_brief("family-georgian"), limit=6)
    assert 6 < len(narrow) <= 6 + compose_mod.MAX_TIE_EXPANSION


def test_pick_partis_rejects_a_nonpositive_limit(compose_mod):
    """out[limit-1] with limit=0 indexes from the END and returned the whole corpus."""
    assert compose_mod.pick_partis(_brief("family-georgian"), limit=0) == []
    assert compose_mod.pick_partis(_brief("family-georgian"), limit=-3) == []


def test_pick_partis_is_totally_ordered(compose_mod):
    """Sorted by fit descending, then by id — with NO reliance on insertion order.

    The first version of this test asserted the output was sorted by (-fit, id) and was
    theatre: every file in partis/ is named <id>.json, so sorted(glob(...)) already gives
    id order, Python's sort is stable, and the output is id-ordered whether or not the
    tie-break key exists. Reverting the key alone left the whole file green.

    So the premise is attacked instead: PARTIS is reordered to the WORST case — reverse id
    order — and the result must still come back in id order. That can only hold if the key
    is really in the sort.
    """
    original = dict(compose_mod.PARTIS)
    hostile = dict(reversed(list(original.items())))
    compose_mod.PARTIS.clear()
    compose_mod.PARTIS.update(hostile)
    try:
        picked = compose_mod.pick_partis(_brief("family-georgian"), limit=99)
    finally:
        compose_mod.PARTIS.clear()
        compose_mod.PARTIS.update(original)

    keys = [(-p["fit"], p["parti"]) for p in picked]
    assert keys == sorted(keys), (
        "pick_partis fell back to insertion order — the tie-break key is missing")


def test_pick_partis_never_cuts_through_a_tie(compose_mod):
    """Diagrams that fit equally well are indistinguishable to this function, so the
    slice must not be what decides between them. Take the whole tie group; let the
    validator rank it."""
    brief = _brief("family-georgian")
    full = compose_mod.pick_partis(brief, limit=99)
    picked = compose_mod.pick_partis(brief, limit=6)

    assert len(picked) > 6, (
        "family-georgian ties four diagrams at the limit — if this returns exactly 6, "
        "the cut is again falling inside a tie group")

    edge = picked[-1]["fit"]
    dropped_at_edge = [p["parti"] for p in full
                       if p["fit"] == edge and p not in picked]
    assert not dropped_at_edge, (
        f"dropped {dropped_at_edge} while keeping others at the same fit {edge}")


def test_the_four_way_tie_is_still_there(compose_mod):
    """The tie is the reason the other two tests exist. If a scoring change ever breaks
    it apart, they stop testing anything and should be re-pointed at a live tie."""
    full = compose_mod.pick_partis(_brief("family-georgian"), limit=99)
    at_two = sorted(p["parti"] for p in full if p["fit"] == 2.0)
    assert at_two == ["charleston-single-piazza", "foursquare-quadrant",
                      "ranch-tripartite", "side-hall-townhouse"], at_two
