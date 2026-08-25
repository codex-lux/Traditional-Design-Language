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
    offenders = []
    for sub in ("build", "mcp_server", "workbench"):
        for path in sorted(glob_module.glob(os.path.join(ROOT, sub, "**", "*.py"),
                                            recursive=True)):
            with open(path) as f:
                for n, line in enumerate(f, 1):
                    if "glob.glob(" in line and "sorted(glob.glob(" not in line:
                        rel = os.path.relpath(path, ROOT)
                        offenders.append(f"{rel}:{n}: {line.strip()}")
    assert not offenders, (
        "unsorted glob.glob — directory order is machine-specific:\n  "
        + "\n  ".join(offenders))


def test_pick_partis_is_totally_ordered(compose_mod):
    """Sorted by fit descending, then by id — no reliance on insertion order."""
    picked = compose_mod.pick_partis(_brief("family-georgian"), limit=99)
    keys = [(-p["fit"], p["parti"]) for p in picked]
    assert keys == sorted(keys), "pick_partis has no deterministic tie-break"


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
