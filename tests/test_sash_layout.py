"""The sash as the members that make it (WP-14.3, step 3).

No surface drew a sash. The elevation plate divided the WHOLE opening into equal rectangles with
lines of no stated width and drew the meeting rail as a line; the DXF drew the same lines; the
scene laid bars across the full opening. sash-light states every member -- "about 1 1/2 in of
jamb, pulley stile and parting-bead clearance", 2 in stiles, a 2 in top rail, a 3 in bottom rail,
a 1 1/4 in meeting rail, a 7/8 in muntin -- and its own light rule divides the glass those members
leave. `elevation.sash_layout` lays them out once, for all three surfaces.

The figures here are read from the PACK'S OWN TEXT (census `_sash_figures`), never from
`elevation.SASH_FRAME`, which is the subject's transcription of the same sentence.
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import modcache as mc  # noqa: E402
import svg_census as C  # noqa: E402

EL = mc.load("elevation", os.path.join(ROOT, "build", "elevation.py"))
PE = mc.load("proportion_engine", os.path.join(ROOT, "build", "proportion_engine.py"))
STILE, RAILS, JAMB, MUNTIN = C._sash_figures()
TOP, BOTTOM, MEETING = RAILS


def _area(b):
    return (b["x1"] - b["x0"]) * (b["y1"] - b["y0"])


def test_the_pack_states_every_member_this_file_reads():
    """The premise: if the pack's wording moves, every assertion below would read None."""
    assert (STILE, TOP, BOTTOM, MEETING, JAMB, MUNTIN) == (2.0, 2.0, 3.0, 1.25, 0.75, 0.875)


@pytest.mark.parametrize("width", [24.0, 30.0, 34.5, 38.6, 42.0, 48.0])
@pytest.mark.parametrize("module", [8.0, 10.0, 12.0])
def test_each_light_is_the_packs_own_light_width(width, module):
    pack = PE.resolve("sash-light")
    sash = EL.sash_at(pack, width, module, height_in=width * 2.1)
    lay = EL.sash_layout(0.0, width, 30.0, 30.0 + width * 2.1, sash["lights_across"],
                         sash["lights_high_per_sash"], MUNTIN)
    want, _r = EL._val(pack, "window_lite_pattern", {"opening_width": width, "module": module},
                       note_substr="RESULTING LIGHT WIDTH", dimension="width")
    assert lay["light_width_in"] == pytest.approx(want, abs=1e-9)
    for p in lay["panes"]:
        assert p["x1"] - p["x0"] == pytest.approx(want, abs=1e-9)


def test_the_members_are_the_widths_the_pack_states():
    lay = EL.sash_layout(10.0, 48.6, 30.0, 110.0, 3, 4, MUNTIN)
    by = {}
    for m in lay["members"]:
        by.setdefault(m["kind"], []).append(m)
    assert [round(m["x1"] - m["x0"], 9) for m in by["jamb"]] == [JAMB, JAMB]
    assert [round(m["x1"] - m["x0"], 9) for m in by["stile"]] == [STILE, STILE]
    assert [round(m["y1"] - m["y0"], 9) for m in by["top-rail"]] == [TOP]
    assert [round(m["y1"] - m["y0"], 9) for m in by["bottom-rail"]] == [BOTTOM]
    assert sorted(round(m["y1"] - m["y0"], 9) for m in by["meeting-rail"]) == [MEETING, MEETING]
    assert all(m.get("approximate") for m in by["jamb"]) and not any(
        m.get("approximate") for k in ("stile", "top-rail", "bottom-rail", "meeting-rail") for m in by[k])
    assert all(round(m["x1"] - m["x0"], 9) == MUNTIN for m in lay["muntins"] if m["dir"] == "v")
    assert all(round(m["y1"] - m["y0"], 9) == MUNTIN for m in lay["muntins"] if m["dir"] == "h")


@pytest.mark.parametrize("n,h", [(1, 1), (2, 3), (3, 4), (4, 2)])
def test_the_members_the_muntins_and_the_glass_tile_the_opening(n, h):
    """Nothing is drawn twice and nothing is left undrawn: the members, the muntins and the panes
    cover the opening exactly, the only overlap being where a vertical muntin crosses a
    horizontal one."""
    x0, x1, sill, head = 5.0, 45.0, 28.0, 118.0
    lay = EL.sash_layout(x0, x1, sill, head, n, h, MUNTIN)
    crossings = 2 * (n - 1) * (h - 1) * MUNTIN * MUNTIN
    covered = (sum(_area(b) for b in lay["members"]) + sum(_area(b) for b in lay["muntins"])
               + sum(_area(b) for b in lay["panes"]) - crossings)
    assert covered == pytest.approx((x1 - x0) * (head - sill), abs=1e-9)
    assert len(lay["panes"]) == 2 * n * h
    for b in lay["members"] + lay["muntins"] + lay["panes"]:
        assert x0 - 1e-9 <= b["x0"] < b["x1"] <= x1 + 1e-9 and sill - 1e-9 <= b["y0"] < b["y1"] <= head + 1e-9


def test_the_two_sashes_meet_at_mid_height_on_their_own_meeting_rails():
    lay = EL.sash_layout(0.0, 40.0, 30.0, 110.0, 3, 4, MUNTIN)
    mid = (30.0 + 110.0) / 2.0
    upper, lower = [(m["y0"], m["y1"]) for m in lay["members"] if m["kind"] == "meeting-rail"]
    assert upper == pytest.approx((mid, mid + MEETING)) and lower == pytest.approx((mid - MEETING, mid))
    assert lay["meeting_in"] == mid


def test_no_light_count_no_muntin_or_no_room_for_glass_is_refused_with_a_reason():
    assert "light count" in EL.sash_layout(0, 40, 30, 110, None, 4, MUNTIN)["refused"]
    assert "muntin" in EL.sash_layout(0, 40, 30, 110, 3, 4, None)["refused"]
    # a 6 in opening: the jambs and stiles take 5.5 of it and leave no room for three lights
    assert "no glass" in EL.sash_layout(0, 6, 30, 110, 3, 4, MUNTIN)["refused"]
