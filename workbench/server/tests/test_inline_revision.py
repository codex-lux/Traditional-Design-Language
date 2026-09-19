"""WP-13.9 -- the corrective rounds run before the plan is surfaced.

Lucas read the bench's Tidewater sheet on 19 Sep 2026: sixty drawn findings, most of them the
`unreachable` fatal, beside a revision panel reporting nothing applied. Solving ran exactly one
`POST /api/plan/evaluate` and the loop was reached only by two chips submitting a job -- whose
record comes back stripped and is re-solved, so the sheet and the loop's key were two different
placements. The ruling: the explicit solve runs one or two rounds, on the engine that placed,
and returns the record the loop ended on with ITS OWN placement and findings.

Each test is named for the defect it forbids. The engine is asked for BY NAME throughout: the
proof path costs a 25 s solve per round and these are route tests, not a measurement of CP.
"""
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _plan(pid="tidewater-georgian-careful"):
    return json.load(open(os.path.join(ROOT, "plans", f"{pid}.json"), encoding="utf-8"))


def _ev(client, **body):
    r = client.post("/api/plan/evaluate", json={"plan": _plan(), "engine": "heuristic", **body})
    assert r.status_code == 200, r.text
    return r.json()


def test_the_default_is_no_rounds_and_the_response_is_what_it_always_was(client):
    """The route's default is 0 and every caller that does not ask -- the CLI parity test, the
    wall drag, a script -- must be byte-identical to before this package. A revision that
    happened by default would be WP-9.3's refused per-edit critique arriving through a
    different door."""
    out = _ev(client)
    assert "revision" not in out
    assert "revised_plan" not in out
    assert "revise" not in out["timing_ms"]


def test_an_explicit_solve_runs_the_rounds_and_says_what_they_did(client):
    out = _ev(client, revise_rounds=2)
    assert "revision" in out, out.keys()
    s = out["revision"]["summary"]
    assert s["rounds"] >= 1
    assert out["revision"]["surfaced"] == "with-its-own-placement"
    assert out["timing_ms"]["revise"] >= 0
    # the package's own subject: this plan's stranded rooms are answerable, so the rounds must
    # actually apply something. A loop that ran and did nothing is the state Lucas reported.
    assert s["moves_applied"] >= 1, out["revision"]["stop_reason"]


def test_the_findings_are_of_the_record_the_loop_ended_on(client):
    """ONE BUILDING (WP-6.4). The whole reason this is inline rather than the job route: the
    fatal count on the response must be the revised record's, not the first pass's."""
    plain = _ev(client)
    revised = _ev(client, revise_rounds=2)
    assert revised["check"]["counts"].get("fatal", 0) < plain["check"]["counts"].get("fatal", 0)
    key_before = revised["revision"]["summary"]["key_before"]
    key_after = revised["revision"]["summary"]["key_after"]
    assert key_after[0] == revised["check"]["counts"].get("fatal", 0), (key_after, revised["check"]["counts"])
    assert key_before[0] == plain["check"]["counts"].get("fatal", 0)


def test_the_revised_record_comes_back_declared_and_carrying_its_report(client):
    """Stripped exactly as `jobs.revised_plan` strips it: a placement travels on `placement`,
    and two copies of one placement on one response is how two readers of one house come to
    disagree. `revision_report` survives the strip -- it IS the panel."""
    out = _ev(client, revise_rounds=2)
    rec = out["revised_plan"]
    assert "revision_report" in rec
    assert not any("geometry" in rm for lv in rec["levels"] for rm in lv["rooms"]), \
        "the revised record carried a second copy of the placement"
    assert "geometry_report" not in rec


def test_the_drawn_findings_name_the_engine_that_placed_the_revised_record(client):
    """A drawn row's engine tag is what the bench prints as 'on the searched placement'. After
    the rounds it must name the engine of the placement those findings were judged against."""
    out = _ev(client, revise_rounds=2)
    drawn = [f for f in out["check"]["findings"] if f["layer"] == "drawn"]
    assert drawn, "premise: this plan draws findings"
    assert {f.get("engine") for f in drawn} == {"heuristic"}


def test_the_rounds_reader_bounds_and_refuses_what_it_cannot_read():
    """DRIVEN ON THE READER, and the reason is a blind guard this package caught in its own
    mutation sweep. The first version of this test posted `revise_rounds: 999` and asserted the
    report came back inside `core.REVISE_MAX_ROUNDS` -- which passes with the route's bound
    DELETED, because `core.revise_plan` bounds `rounds` itself before the loop ever runs. It
    was asserting the inner bound through the outer one, so it could not fail.

    What the route's own reader decides, and nothing else does: that 0 is expressible (a
    caller must be able to say "do not revise"), and that a value we cannot read means none
    rather than the default -- a caller who sent nonsense has not asked for a loop and must
    not be given minutes of one."""
    from mcp_server import core
    from workbench.server import app as A
    assert A._revise_rounds({}) == 0
    assert A._revise_rounds({"revise_rounds": 0}) == 0
    assert A._revise_rounds({"revise_rounds": 2}) == 2
    assert A._revise_rounds({"revise_rounds": 999}) == core.REVISE_MAX_ROUNDS
    assert A._revise_rounds({"revise_rounds": -4}) == 0
    for bad in ("lots", None, [2], {}):
        assert A._revise_rounds({"revise_rounds": bad}) == 0, bad


def test_a_value_the_route_cannot_read_runs_no_rounds(client):
    """The behavioural half of the reader above, through the real route."""
    for bad in ("lots", None, [2]):
        assert "revision" not in _ev(client, revise_rounds=bad)


def test_the_budget_reader_bounds_and_defaults_to_the_interactive_ceiling():
    """`None` means `geometry.BUDGET_REVISE_INLINE_S` -- which is `_revise_inline`'s to
    supply, not the route's, so the reader must say None rather than reaching for a number
    and putting a second spelling of that ceiling in a second file."""
    from mcp_server import core
    from workbench.server import app as A
    assert A._revise_budget({}) is None
    assert A._revise_budget({"revise_budget_s": "nonsense"}) is None
    assert A._revise_budget({"revise_budget_s": 12}) == 12.0
    assert A._revise_budget({"revise_budget_s": 10 ** 6}) == core.REVISE_MAX_BUDGET_S
    assert A._revise_budget({"revise_budget_s": 0}) == 1.0


def test_a_loop_that_fails_still_returns_the_sheet(client, monkeypatch):
    """A loop that raises must not cost the reader the plan. Driven, because no shipped record
    reaches it -- and an untested except branch is a promise rather than a behaviour."""
    from workbench.server import evaluate as EV

    def boom(*_a, **_k):
        raise RuntimeError("the loop fell over")

    monkeypatch.setattr(EV.core, "revise_plan", boom)
    out = _ev(client, revise_rounds=2)
    assert "revision" not in out
    assert out["revision_error"].startswith("RuntimeError"), out["revision_error"]
    assert out["check"]["counts"], "the sheet must still land"
    assert "placement" in out or "placement_refused" in out


def test_the_wall_drags_own_path_is_untouched(client):
    """The drag asks for the hill-climb BY NAME behind a 400 ms debounce and sends no rounds.
    A gesture cannot wait for a loop any more than it can wait for a proof, and this asserts
    the route rather than the client's intention."""
    out = _ev(client)
    assert "revision" not in out and "revised_plan" not in out
    assert out["placement"]["sketch"]["working"] is True
