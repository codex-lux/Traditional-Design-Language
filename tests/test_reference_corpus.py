"""Pins WP-2.1's reference corpus (plans/reference/*.json, docs/reports/wp-2.1-reference-corpus.md).

These are transcriptions of real floor-plan drawings, not authored fixtures, so this suite does
NOT pin exact finding counts the way TestShippedPlans does for the two hand-designed example
plans -- a transcription confidence note in the plan itself already says how much weight its
findings deserve. What IS pinned: every record stays schema-valid and runs cleanly, and the two
concrete room-catalogue gaps the report's own analysis rests on (the entrance-hall/gallery-corridor
alias gap, and the primary-bedroom/primary-bathroom dressing-room via gap) actually reproduce
against the live corpus -- so if a future package fixes either gap, this suite fails and says so,
rather than letting the report's evidence silently go stale.
"""
import glob
import os
import subprocess

import pytest

from conftest import ROOT, load_reference_plan

REFERENCE_DIR = os.path.join(ROOT, "plans", "reference")
REFERENCE_IDS = sorted(
    os.path.splitext(os.path.basename(f))[0] for f in glob.glob(os.path.join(REFERENCE_DIR, "*.json"))
)


class TestReferenceCorpusShape:
    def test_at_least_fourteen_records(self):
        assert len(REFERENCE_IDS) >= 14

    def test_seven_bad_and_at_least_six_good(self):
        bad = [i for i in REFERENCE_IDS if i.startswith("bad-")]
        good = [i for i in REFERENCE_IDS if i.startswith("good-")]
        assert len(bad) == 7, "the eight Bad Examples files collapse to seven records (one two-level house)"
        assert len(good) >= 6

    def test_every_record_validates_against_plan_schema(self):
        """jsonschema lives in the system python3, not in pytest's own tool venv (see
        test_constraints.py's note) -- shells out once for the whole batch rather than
        importing jsonschema directly or spawning 14 subprocesses."""
        proc = subprocess.run(
            ["python3", "-c",
             "import json, jsonschema, glob\n"
             "schema = json.load(open('schema/plan.schema.json'))\n"
             "bad = []\n"
             "for f in sorted(glob.glob('plans/reference/*.json')):\n"
             "    p = json.load(open(f))\n"
             "    try:\n"
             "        jsonschema.validate(p, schema)\n"
             "    except Exception as e:\n"
             "        bad.append((f, str(e)[:200]))\n"
             "print('BAD:', bad) if bad else print('OK')\n"],
            cwd=ROOT, capture_output=True, text=True,
        )
        assert proc.returncode == 0 and proc.stdout.strip() == "OK", proc.stdout + proc.stderr

    @pytest.mark.parametrize("plan_id", REFERENCE_IDS)
    def test_plan_check_runs_without_raising(self, plan_id, plan_check_module, corpus):
        plan = load_reference_plan(plan_id)
        result = plan_check_module.check(plan, corpus)
        assert result["plan"] == plan_id
        assert "findings" in result

    @pytest.mark.parametrize("plan_id", REFERENCE_IDS)
    def test_every_record_carries_a_provenance_note(self, plan_id):
        """schema/plan.schema.json has no structured provenance field (docs/reports/wp-2.1-*.md,
        'what was deliberately not done') -- source_image and transcription_confidence live in
        the free-text note instead. Pin that every record actually has one, since nothing else
        enforces it."""
        plan = load_reference_plan(plan_id)
        assert "source_image" in plan.get("note", "")
        assert "transcription_confidence" in plan.get("note", "")


class TestValidatorGapsTheReportFoundAreReal:
    """These pin the two room-catalogue gaps docs/reports/wp-2.1-reference-corpus.md's 'where the
    validator disagrees' section rests its argument on -- not the reference plans' overall finding
    counts, which are expected to drift as the transcriptions or the catalogue evolve."""

    def test_gallery_corridor_is_not_an_entrance_hall_equivalent(self, plan_check_module, corpus):
        """A porch reaching only a gallery-corridor (never an entrance-hall/vestibule/stair-hall)
        should, per this finding, still fail entry-porch's must_adjoin rule -- because
        gallery-corridor is absent from plan_check.EQUIVALENT. If this ever passes, either the
        alias list was fixed (update docs/reports/wp-2.1-*.md to say so) or something else changed."""
        assert not any("gallery-corridor" in grp for grp in plan_check_module.EQUIVALENT)

    def test_primary_bathroom_via_list_has_no_dressing_room(self, corpus):
        rule = next(r for r in corpus["rooms"]["primary-bedroom"]["adjacency"]["must_adjoin"]
                    if r["room"] == "primary-bathroom")
        assert "dressing-room" not in (rule.get("via") or [])

    def test_good_05_reproduces_the_entrance_hall_gallery_fatal(self, plan_check_module, corpus):
        plan = load_reference_plan("good-05-lobby-gallery-mansion")
        result = plan_check_module.check(plan, corpus)
        fatals = [f["statement"] for f in result["findings"] if f["severity"] == "fatal"]
        assert any("Lobby" in s and "stair hall" in s for s in fatals)

    def test_good_07_reproduces_the_dressing_room_bath_fatal(self, plan_check_module, corpus):
        plan = load_reference_plan("good-07-diamond-plan-house")
        result = plan_check_module.check(plan, corpus)
        fatals = [f["statement"] for f in result["findings"] if f["severity"] == "fatal"]
        assert any("Primary Bathroom" in s and "primary bedroom" in s for s in fatals)


class TestFindingsSkewAsTheReportDescribes:
    """Pins the report's strongest quantitative claim: ROOM and FURNITURE layer fatal+serious
    findings are markedly worse on the bad examples than the good ones, while ADJACENCY is not --
    the numeric skew this session actually observed (45 vs 6 room; 63 vs 23 furniture), loosened
    to a directional assertion so the test survives small future edits to either corpus."""

    def test_room_and_furniture_layers_skew_toward_bad_examples(self, plan_check_module, corpus):
        def bad_serious_or_worse(plan_id, layer):
            plan = load_reference_plan(plan_id)
            result = plan_check_module.check(plan, corpus)
            return sum(1 for f in result["findings"]
                       if f["layer"] == layer and f["severity"] in ("fatal", "serious"))

        bad_ids = [i for i in REFERENCE_IDS if i.startswith("bad-")]
        good_ids = [i for i in REFERENCE_IDS if i.startswith("good-")]
        for layer in ("room", "furniture"):
            bad_total = sum(bad_serious_or_worse(i, layer) for i in bad_ids)
            good_total = sum(bad_serious_or_worse(i, layer) for i in good_ids)
            assert bad_total > good_total, f"{layer}: expected bad examples to skew worse (bad={bad_total}, good={good_total})"
