"""One named check says whether a deploy can break, apart from the checks that are red by ruling.

Deployment-readiness review, 27 Nov 2026 (DR-03). CI was red on `main` on each of the last five
completed runs, by standing rulings: the Phase 13 gate's rows in the corpus shards, and the
browser walk, which cannot judge six checks (exit 3, ruled 16 Oct) and since Phase 18 also fails
a handful on the plan sheet (exit 1; four on `cc887ea`). Both reds are recorded in CLAUDE.md. The cost was
that a NEW regression in the server, the app or the image looked exactly like them, and the
workbench job, which holds the server suite, was red on every run because the walk was a step
inside it.

These read the workflow file. They hold that the gate exists and names the right jobs, and
that nothing was made green by being removed: the walk and the corpus still run, and still fail
the workflow when they fail.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _jobs():
    with open(os.path.join(ROOT, ".github", "workflows", "ci.yml"), encoding="utf-8") as f:
        text = f.read()
    body = text.split("\njobs:\n", 1)[1]
    starts = [(m.start(), m.group(1)) for m in re.finditer(r"^  ([A-Za-z0-9_-]+):\n", body, re.M)]
    out = {}
    for i, (at, name) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(body)
        out[name] = body[at:end]
    return out


def _live(job):
    """The job's lines that are not comments."""
    return [l.strip() for l in job.splitlines() if l.strip() and not l.strip().startswith("#")]


def _needs(job):
    for line in _live(job):
        if line.startswith("needs:"):
            return sorted(n.strip() for n in line.split(":", 1)[1].strip(" []").split(","))
    return []


def test_the_reader_reads_the_workflow():
    jobs = _jobs()
    assert {"shard", "corpus", "workbench", "image"} <= set(jobs), sorted(jobs)


def test_the_gate_needs_the_jobs_a_deploy_can_break_and_no_others():
    jobs = _jobs()
    gate = jobs["deploy-gate"]
    assert "name: deploy gate" in _live(gate)
    assert _needs(gate) == ["image", "workbench"], _needs(gate)


def test_a_needed_job_that_fails_fails_the_gate_and_does_not_skip_it():
    """`needs` alone skips this job when a needed one fails, and a skipped check is not a failed
    one to a protection rule. The corpus aggregate's own note says so; the same shape here."""
    live = _live(_jobs()["deploy-gate"])
    assert "if: always()" in live
    script = "\n".join(live)
    for needed in ("workbench", "image"):
        assert f'test "${{{{ needs.{needed}.result }}}}" = "success"' in script, needed


def test_the_walk_is_its_own_job_and_still_runs():
    jobs = _jobs()
    runs_walk = [name for name, job in jobs.items()
                 if any(l.startswith("run:") and "workbench/scripts/walk.sh" in l for l in _live(job))]
    assert runs_walk == ["walk"], (
        f"the walk must run in exactly one job, its own; it runs in {runs_walk}")
    assert "walk" not in _needs(jobs["deploy-gate"]), "the walk is red by ruling; it is not in the gate"
    walk = _live(jobs["walk"])
    assert "continue-on-error: true" not in walk, "a red walk must stay red"
    assert not [l for l in walk if l.startswith("if:")], "and must not be skippable"
    assert "run: pip install --require-hashes -r workbench/requirements-dev.lock" in walk


def test_the_workbench_job_still_holds_everything_else_it_held():
    live = _live(_jobs()["workbench"])
    for step in ("run: npm ci", "run: npm run build", "run: npm test",
                 "run: python3 -m pytest workbench/server/tests -q",
                 "run: bash workbench/scripts/smoke.sh"):
        assert step in live, f"the workbench job lost a step: {step}"


def test_the_research_gate_is_untouched_and_nothing_tolerates_a_failure():
    jobs = _jobs()
    assert "name: corpus — check_all.py" in _live(jobs["corpus"]), "the name is load-bearing"
    assert _needs(jobs["corpus"]) == ["shard"]
    for name, job in jobs.items():
        assert "continue-on-error" not in "\n".join(_live(job)), f"{name} tolerates a failure"
