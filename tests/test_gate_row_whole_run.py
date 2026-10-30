"""The gate row's whole-run half, driven (the audit of Phase 17, finding 20, 30 Oct 2026).

`tests/test_sheet_coherence.py::test_every_upper_bearing_line_stands_on_a_ground_bearing_line`
read `TF.bearing_extents(out) or {}`, so where the reader returned None (no bay module on the
record) or UNJUDGED, its whole-run half found nothing short and PASSED -- while the positional half
above it ran on a defaulted 10 ft grid. Every sheet the gate builds carries a bay module, so the
branch is unreachable from the gate's own population and is driven here, by calling the gate row
itself on hand-built records through a stub `sheets` fixture. No solve runs.

Deliberately NOT done here: the verifier's second half, making the whole-run reference independent
of `typefacts.bearing_extents` (the reader the refusal itself decides on -- the R4 trap). Changing
the reference can change which gate rows are red, and re-attributing the gate by id needs its CP
sheets, which this batch did not run. It is named for the lead.
"""
import copy
import importlib.util
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("sheet_coherence_driven",
                                               ROOT / "tests" / "test_sheet_coherence.py")
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)
ROW = T.test_every_upper_bearing_line_stands_on_a_ground_bearing_line
ROW = getattr(ROW, "__wrapped__", ROW)


def _room(i, x, y, w, h):
    return {"id": i, "type": "parlor", "geometry": {"x_ft": x, "y_ft": y, "width_ft": w, "depth_ft": h}}


def _record(bay=10.0):
    fp = {"width_ft": 20.0, "depth_ft": 20.0}
    if bay:
        fp["bay_module_ft"] = bay
    return {"id": "drv", "footprint": fp,
            "levels": [{"index": 0, "id": "L0", "rooms": [_room("A", 0, 0, 10, 20),
                                                          _room("B", 10, 0, 10, 20)]},
                       {"index": 1, "id": "L1", "rooms": [_room("D", 0, 0, 10, 20),
                                                          _room("E", 10, 0, 10, 20)]}],
            "geometry_report": {"solver": {"engine": "heuristic"}}}


def _run(out):
    return ROW(lambda kind, engine: (out, "", None), "driven", "heuristic")


def test_a_whole_run_held_on_both_floors_passes_the_row():
    """The control: the same house with its bay module stated passes, so the next test's failure
    is the missing bay and not the house."""
    assert T.TF.bearing_extents(_record())["status"] == T.TF.HELD
    _run(_record())


def test_a_record_with_no_bay_module_could_not_be_evaluated_and_does_not_pass():
    out = _record(bay=None)
    assert T.TF.bearing_extents(out) is None, "the premise: the reader cannot read a bay-less record"
    with pytest.raises(AssertionError, match="COULD NOT EVALUATE"):
        _run(out)


def test_an_unjudged_reader_is_not_a_pass(monkeypatch):
    """The reader answering UNJUDGED (one placed level, in its own words) where the positional half
    holds: the row must fail rather than read an empty `short` as every wall standing."""
    monkeypatch.setattr(T.TF, "bearing_extents", lambda plan: {
        "status": T.TF.UNJUDGED, "lines": [], "detail": "one placed level"})
    with pytest.raises(AssertionError, match="COULD NOT EVALUATE"):
        _run(copy.deepcopy(_record()))
