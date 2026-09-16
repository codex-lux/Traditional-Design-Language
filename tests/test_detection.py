"""WP-13.1 — the 139,070 characters of `detection` prose nothing read, and the refusals
the unjudged verdict never quoted.

Four things are guarded and they fail on different mutations, which is why all four exist:

  * the READER over the whole corpus (210 records, no text lost by the split);
  * the LIVENESS of the refusal tables -- `refusals()` must read the authorities rather than
    carry a copy, and the test proves it by moving one at runtime;
  * the JOIN into `plan_check`, which must be strictly additive: a row with no refused name
    is returned byte-identical, and no row loses a field;
  * the CONTRADICTION ratchet -- a name a table refuses that a layer supplies anyway. Two are
    known and both are named here, so a third cannot arrive quietly.

Driven, not read off the corpus, wherever a fixture would otherwise be a statement about this
tree rather than about the rule (WP-8.11).
"""
import copy
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name, path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


DET = _load("detection", f"{ROOT}/build/detection.py")
PC = _load("plan_check", f"{ROOT}/build/plan_check.py")

# The corpus-side figures, ratcheted. They are DERIVED from the records on every run; the
# literals are here so that a fall is accounted for rather than accepted, which is what a
# ratchet is for. Re-measure before moving one.
FAULTS = 210
IDENTIFIERS_READ = 825
REFUSALS = 36

# The two live contradictions, BY NAME. A count alone would let one be fixed and another
# arrive on the same commit -- WP-11.7's "a removed serious and an added duplicate cancelled
# and 63 stayed 63". Each is documented in build/arrangement.py beside its entry.
KNOWN_CONTRADICTIONS = {"net_clear_opening_height_in", "wall_thickness_in"}


class TestTheReader:
    def test_every_fault_record_carries_prose_the_reader_can_read(self):
        faults = DET._load_faults()
        assert len(faults) == FAULTS, "re-measure the corpus before moving this figure"
        for fid, rec in faults.items():
            assert isinstance(rec.get("detection"), str) and rec["detection"].strip(), fid
            assert DET.checks(rec), f"{fid}: checks() returned nothing"

    def test_the_split_loses_no_text(self):
        """checks() is a READING AID, so its one real contract is that it drops nothing.

        A count taken from it may not be published (the prose numbers its checks at least
        four ways and this reader knows two), but a reader handed check [2] of 3 must be
        reading the record's own words. Mutation: any split that consumes its delimiter, or
        a `.split()` in place of the lookahead, loses characters here.
        """
        for fid, rec in DET._load_faults().items():
            joined = " ".join(DET.checks(rec))
            assert "".join(joined.split()) == "".join(rec["detection"].split()), fid

    def test_measurement_names_reads_all_three_test_locations(self):
        """A fault's tests live in `test`, `secondary_tests` and `exceptions[].bounds_test`,
        and the third SUBSTITUTES for the primary. Driven, so it cannot pass by the corpus
        happening to put everything in one place."""
        rec = {
            "id": "driven", "detection": "x.",
            "test": {"expression": "alpha / beta"},
            "secondary_tests": [{"expression": "gamma",
                                 "applies_when": {"expression": "delta"}}],
            "exceptions": [{"style": "s", "bounds_test": {"expression": "epsilon"}}],
        }
        assert DET.measurement_names(rec) == {"alpha", "beta", "gamma", "delta", "epsilon"}

    def test_surfaces_is_three_states_and_an_empty_list_is_not_a_photograph(self):
        assert DET.surfaces({"test": {"measurable_from": "plan"}}) == ["plan"]
        assert DET.surfaces({"test": {"expression": "x"}}) == []
        assert DET.surfaces({"test": {"measurable_from": "plan"},
                             "secondary_tests": [{"measurable_from": "photograph"}]}) == \
            ["photograph", "plan"]

    def test_surface_words_refuses_the_word_elevation(self):
        """The documented exclusion, pinned with its reason.

        In this prose `elevation` means the FACE of the building -- "count exterior doors on
        the rear elevation of the main block" -- not the drawing. A naive vocabulary that
        includes it reports a surface disagreement on records that have none, which is why
        the function may not be ratcheted and why no check convicts on it. Mutation: adding
        `elevation` to the vocabulary turns this red.
        """
        rec = {"detection": "Count exterior doors on the rear elevation of the main block."}
        assert DET.surface_words(rec) == []
        rec2 = {"detection": "On a plan, draw the centreline; in a photograph, look for it."}
        assert DET.surface_words(rec2) == ["photograph", "plan"]


class TestTheRefusalsAreLive:
    def test_refusals_read_the_authorities_and_do_not_carry_a_copy(self):
        """Move a table at runtime and the reader must move with it.

        This is the guard that matters most about this module: a refusal's whole value is its
        reason, and a second spelling of one is two refusals that can disagree. Mutation: a
        literal dict of names pasted into detection.py passes every other test here and fails
        this one.
        """
        AR = DET._mod("arrangement", f"{ROOT}/build/arrangement.py")
        sentinel = "zz_driven_quantity_that_does_not_exist_in"
        assert sentinel not in DET.refusals()
        AR.NOT_DERIVABLE[sentinel] = "a reason invented by this test"
        try:
            live = DET.refusals()
            assert sentinel in live
            assert live[sentinel]["why"] == "a reason invented by this test"
            assert live[sentinel]["by"] == "arrangement.NOT_DERIVABLE"
        finally:
            del AR.NOT_DERIVABLE[sentinel]
        assert sentinel not in DET.refusals()

    def test_the_reason_is_verbatim_and_never_paraphrased(self):
        AR = DET._mod("arrangement", f"{ROOT}/build/arrangement.py")
        refs = DET.refusals()
        for name, why in AR.NOT_DERIVABLE.items():
            assert refs[name]["why"] == why, name

    def test_two_tables_refusing_one_name_lose_neither_reason(self):
        """Driven: no name is in both tables today, so this branch is unreachable from the
        corpus and a mutation deleting it would leave the suite green (WP-8.11's rule).

        First-wins would silently pick one reason, and a refusal's whole value is its reason.
        """
        AR = DET._mod("arrangement", f"{ROOT}/build/arrangement.py")
        EL = DET._mod("elevation", f"{ROOT}/build/elevation.py")
        name = "zz_driven_name_two_tables_both_refuse"
        AR.NOT_DERIVABLE[name] = "the arrangement layer's reason"
        EL.NOT_MODELLED[name] = "the elevation layer's reason"
        try:
            row = DET.refusals()[name]
            assert "arrangement.NOT_DERIVABLE" in row["by"]
            assert "elevation.NOT_MODELLED" in row["by"]
            assert {row["why"], row["also"]} == {"the arrangement layer's reason",
                                                 "the elevation layer's reason"}
        finally:
            del AR.NOT_DERIVABLE[name]
            del EL.NOT_MODELLED[name]

    def test_no_refusal_names_a_quantity_nothing_reads(self):
        """A refusal that cannot fire reads exactly like a decision taken.

        This is the corpus's most-repeated defect wearing the other face: a guard that cannot
        fire is invisible, and so is a refusal nothing can reach. All 36 are live today.
        """
        refs = DET.refusals()
        read = set()
        for rec in DET._load_faults().values():
            read |= DET.measurement_names(rec)
        assert len(read) == IDENTIFIERS_READ, "re-measure before moving this figure"
        assert len(refs) == REFUSALS, "re-measure before moving this figure"
        dead = sorted(n for n in refs if n not in read)
        assert dead == [], f"refusals naming nothing any fault test reads: {dead}"

    def test_disposition_has_exactly_two_verdicts_and_unsupplied_is_not_a_gap(self):
        refs = DET.refusals()
        name = sorted(refs)[0]
        d = DET.disposition(name, refs)
        assert d["verdict"] == "refused" and d["why"] == refs[name]["why"]
        d2 = DET.disposition("zz_nothing_named_this", refs)
        assert d2["verdict"] == "unsupplied"
        assert "why" not in d2, ("an unsupplied name has no reason; inventing one is exactly "
                                 "what this module exists to stop")


class TestTheJoinIntoPlanCheck:
    """The annotation must be additive. It may add a field; it may never remove or change one,
    and it may never turn an unjudged into anything else."""

    @staticmethod
    def _rows():
        return [
            {"fault": "a", "name": "A", "needs": ["wholly_unsupplied_name"],
             "measurable_from": "photograph"},
            {"fault": "b", "name": "B",
             "needs": ["dedicated_plant_room_area_sqft"], "measurable_from": "plan"},
            {"fault": "c", "name": "C",
             "needs": ["dedicated_plant_room_area_sqft", "wholly_unsupplied_name"],
             "measurable_from": "plan"},
        ]

    def test_a_row_with_nothing_refused_is_returned_unchanged(self):
        rows = self._rows()
        out = PC._with_dispositions(copy.deepcopy(rows))
        assert out[0] == rows[0], "a row the corpus has said nothing about must not be touched"

    def test_a_refused_row_gains_the_reason_and_loses_no_field(self):
        rows = self._rows()
        out = PC._with_dispositions(copy.deepcopy(rows))
        for before, after in zip(rows, out):
            for k, v in before.items():
                assert after[k] == v, f"{before['fault']}: {k} changed"
        assert out[1]["refused"][0]["name"] == "dedicated_plant_room_area_sqft"
        assert out[1]["refused_all"] is True
        assert out[2]["refused_all"] is False, ("a row with one refused name and one "
                                                "unsupplied one is not wholly accounted for")

    def test_a_failure_in_the_annotation_degrades_to_the_rows_as_they_were(self, monkeypatch):
        """It may not take the validator down, and it may not make an unjudged look judged.

        Patched through PC._load, which is what plan_check is actually holding: a harness that
        loads the module with raw importlib gets a SECOND module object and patches nothing,
        which this repository has already believed once (audit, 7 Sep 2026).
        """
        DET_AS_PC_HOLDS_IT = PC._load("detection", f"{ROOT}/build/detection.py")
        rows = self._rows()

        def boom():
            raise RuntimeError("driven")
        monkeypatch.setattr(DET_AS_PC_HOLDS_IT, "refusals", boom)
        out = PC._with_dispositions(copy.deepcopy(rows))
        assert out == rows

    def test_the_shipped_plan_is_annotated_and_the_result_does_not_balloon(self):
        plan = json.load(open(f"{ROOT}/plans/tidewater-georgian-careful.json"))
        res = PC.check(plan)
        rows = res["fault_unjudged"]
        assert rows, "the Tidewater plan has unjudged faults; if it does not, re-read this"
        annotated = [r for r in rows if r.get("refused")]
        assert annotated, "no unjudged row carried a refusal: the join is not firing"
        # Every annotated row's reasons are the tables' own words.
        refs = DET.refusals()
        for r in annotated:
            for d in r["refused"]:
                assert d["why"] == refs[d["name"]]["why"]
                assert d["name"] in r["needs"]
        # The prose itself must NOT be attached -- 120 rows at a median 639 characters is
        # 77 KB on a 110 KB result, on the route measured as the whole server's bound.
        blob = json.dumps(res)
        assert "detection" not in {k for row in rows for k in row}
        assert len(blob) < 160_000, ("the plan_check result has grown past the budget this "
                                     "annotation was sized against; re-measure")


class TestTheSurfaceCensusTheReportPublishes:
    """The figures WP-13.1's report and CLAUDE.md state about `surface_words`, DERIVED.

    They are published in two markdown files and `check_counts.py`'s CLAIMS list reads only
    corpus-derived counts over a fixed set of files -- neither this census nor the naive one
    is among them. WP-8.14's rule: when a layer publishes figures and no checker derives them,
    name the ones it does not. These are those, and this is where they are named.

    The first version of the report said "all 21 apparent disagreements are the same false
    positive". It survived three readings and died the first time the shipped function was run
    over the corpus: eleven of the twenty-one are the word sense, ten are real.
    """

    # Under the SHIPPED vocabulary (no `elevation`, no `section`).
    CENSUS = {"agrees": 118, "subset": 35, "none": 32, "overlap": 15, "disjoint": 10}
    # The ten, by name. Not one of them is an error: a fault may reach one defect by two
    # routes, and `stair-at-the-front-door` writes a photograph procedure for a `plan` test.
    DISJOINT = {
        "interior-transom-removed", "one-colour-temperature-for-the-house",
        "passage-that-is-a-corridor", "plan-flipped-without-the-sun",
        "porch-without-the-height-to-pay-for-it", "setback-out-of-step-with-the-street",
        "stack-with-nowhere-to-land", "stair-at-the-code-minimum",
        "stair-at-the-front-door", "thresholds-uncrossed",
    }

    def _census(self):
        got = {k: 0 for k in self.CENSUS}
        disjoint = set()
        for fid, rec in DET._load_faults().items():
            prose, tests = set(DET.surface_words(rec)), set(DET.surfaces(rec))
            if not prose:
                got["none"] += 1
            elif prose == tests:
                got["agrees"] += 1
            elif prose <= tests:
                got["subset"] += 1
            elif prose & tests:
                got["overlap"] += 1
            else:
                got["disjoint"] += 1
                disjoint.add(fid)
        return got, disjoint

    def test_the_census_is_what_the_report_says(self):
        got, disjoint = self._census()
        assert got == self.CENSUS, "re-measure, and correct the report and CLAUDE.md with it"
        assert disjoint == self.DISJOINT
        assert sum(got.values()) == FAULTS

    def test_what_the_exclusion_buys_against_a_pinned_naive_vocabulary(self):
        """Driven against a NAIVE vocabulary pinned here, because the naive figure is a
        property of the vocabulary and not of the corpus.

        The first draft of this test asserted 21 and measured 22: the vocabulary this session
        first wrote by hand had a wider `site-visit` arm (`walk`, `tap`, `touch`, `by hand`)
        than the one that shipped, so "21 disjoint" described a regex nobody kept. That is
        `check_grouping_rules.prose_meter`'s own discipline arriving in the test rather than
        in the checker -- a crude match's count is a fact about the match. The vocabulary is
        therefore pinned IN FULL here, and the number means nothing without it."""
        import re as _re
        naive = {
            "photograph": r"\bphotograph\b|\bphoto\b|\bimage\b|\blisting shot\b",
            "plan": r"\bon a plan\b|\bon the plan\b|\bin plan\b|\bin the plan\b|\bfrom a plan\b|\bplan overlay\b",
            "site-visit": r"\bon site\b|\bin person\b|\bwith a tape\b|\bstand in\b",
            "elevation": r"\belevation\b",
            "section": r"\bsection\b",
        }
        naive_disjoint = set()
        for fid, rec in DET._load_faults().items():
            prose = {k for k, pat in naive.items() if _re.search(pat, rec["detection"], _re.I)}
            tests = set(DET.surfaces(rec))
            if prose and not (prose & tests):
                naive_disjoint.add(fid)
        assert len(naive_disjoint) == 22
        _, shipped = self._census()
        assert shipped <= naive_disjoint, (
            "excluding a word may only REMOVE a disjoint record; one appearing is a different "
            "defect wearing this one's clothes")
        assert len(naive_disjoint - shipped) == 12


class TestTheContradictions:
    def test_the_two_known_contradictions_and_no_third(self):
        """A name a refusal table refuses that the measurement layer supplies anyway.

        Both live instances are the same shape and neither is a bug in the code: a refusal
        whose REASON was a claim about what this corpus cannot do, which a different layer
        had since falsified. `wall_thickness_in` said "the plan record states no wall
        thickness" after `footprint.wall` landed; `net_clear_opening_height_in` said the plan
        states no sash operation while the elevation layer supplied the lower sash's travel.
        Both reasons are corrected and both entries KEPT, so one quantity keeps one spelling.

        A third arriving is a third reason that has quietly stopped being true.
        """
        EL = DET._mod("elevation", f"{ROOT}/build/elevation.py")
        AR = DET._mod("arrangement", f"{ROOT}/build/arrangement.py")
        supplied = set()
        for pid in ("tidewater-georgian-careful", "spec-builder-colonial"):
            plan = json.load(open(f"{ROOT}/plans/{pid}.json"))
            el = EL.build_elevation(plan)
            supplied |= {k for k, v in (el.get("measurements") or {}).items() if v is not None}
            supplied |= {k for k, v in AR.declared(plan).items() if v is not None}
        assert supplied, "no measurements were supplied at all; the harness is not running"
        assert set(DET.contradictions(supplied)) == KNOWN_CONTRADICTIONS

    def test_both_corrected_reasons_say_who_supplies_the_quantity(self):
        """The correction is the deliverable, not the entry's presence.

        Mutation: reverting either reason to its old wording -- which asserted the corpus
        could not state the quantity -- turns this red, because neither old reason names a
        supplier.
        """
        refs = DET.refusals()
        for name in KNOWN_CONTRADICTIONS:
            why = refs[name]["why"]
            assert "supplied by elevation.py" in why, name
            assert "one spelling" in why, name


class TestTheCensus:
    def test_the_corpus_side_census_is_derived_and_ratcheted(self):
        c = DET.census()
        assert c["faults"] == FAULTS
        assert c["identifiers_read_by_fault_tests"] == IDENTIFIERS_READ
        assert c["refusals"] == REFUSALS
        assert c["refusals_naming_nothing_any_test_reads"] == []

    def test_the_plan_side_census_adds_up(self):
        plan = json.load(open(f"{ROOT}/plans/tidewater-georgian-careful.json"))
        c = DET.census(PC.check(plan))
        assert c["missing_refused"] + c["missing_unsupplied"] == c["distinct_missing_names"]
        assert sum(c["by_fault"].values()) == c["unjudged_faults"]
        assert c["by_fault"]["refused"] > 0, (
            "faults unjudged entirely for reasons this corpus has already written down are "
            "the finding this package exists for; zero of them means the join is inert")


class TestTheClearVerdictCarriesWhatTheCorpusKnows:
    """The same question as the unjudged annotation, asked of the other bucket.

    A pass earned on a measurement OF THE HOUSE and a pass earned on the generator asserting
    its own output are both `clear`, and until WP-13.1 nothing in the tree could tell them
    apart -- `critique.classify` iterates findings and a fault that passes emits none, so the
    critic-suspect machinery has never seen a single one of these.

    Ratcheted BY NAME as well as by count, because a removed row and an added row cancel
    (WP-11.7: "a removed serious and an added duplicate cancelled and 63 stayed 63").
    """

    # Measured 15 Sep 2026 on both shipped plans. Re-measure before moving either.
    SUSPECT_CLEAR = {"tidewater-georgian-careful": 26, "spec-builder-colonial": 27}
    # The sharpest four, which are cleared on the generator asserting its own output.
    TAUTOLOGIES = {
        "one-bay-symmetry-break",                 # ...without_a_mirror_twin... = 0, on a
                                                  # generator that draws a symmetric facade
        "broken-head-datum",                      # distinct_head_datums... = 1
        "condenser-on-the-entrance-elevation",    # equipment_units_visible... = 0.0
        "brick-front-vinyl-return",               # faces_of_volume_clad_in_primary... = 4
    }

    @pytest.mark.parametrize("pid", sorted(SUSPECT_CLEAR))
    def test_the_count_and_the_four_named_rows(self, pid):
        res = PC.check(json.load(open(f"{ROOT}/plans/{pid}.json")))
        rows = res["fault_clear_on_a_generator_constant"]
        assert rows is not None, "the instrument failed; an absent key is not zero"
        assert len(rows) == self.SUSPECT_CLEAR[pid], "re-measure before moving this figure"
        ids = {r["fault"] for r in rows}
        assert self.TAUTOLOGIES <= ids, sorted(self.TAUTOLOGIES - ids)
        for r in rows:
            assert r["reads"], "a row with no suspect name has no business being here"

    def test_it_is_a_list_and_not_a_count(self):
        """A count cannot be argued with. Every row names the fault AND the measurements that
        made it a suspect, which is what `critic_suspects.why_suspect` insists on for the
        failing half: evidence names the instrument and the measurement, never just the word.
        """
        res = PC.check(json.load(open(f"{ROOT}/plans/spec-builder-colonial.json")))
        CS = PC._load("critic_suspects", f"{ROOT}/build/critic_suspects.py")
        names = CS.suspect_names()
        for r in res["fault_clear_on_a_generator_constant"]:
            assert set(r["reads"]) <= names
            assert r["name"], "the row carries the fault's human name for a reader"

    def test_the_instrument_failing_is_None_and_never_an_empty_list(self, monkeypatch):
        """An empty list is the claim "no pass is suspect". A failure must not make it."""
        CS = PC._load("critic_suspects", f"{ROOT}/build/critic_suspects.py")

        def boom():
            raise RuntimeError("driven")
        monkeypatch.setattr(CS, "suspect_names", boom)
        assert PC._clear_on_a_constant({"faults_clear": [{"fault": "x", "results": []}]}) is None

    def test_a_truncated_clear_list_is_could_not_evaluate_and_never_a_smaller_count(self):
        """`core.check_measurements` cuts `faults_clear` at `limit`. `plan_check` passes 10**6
        so it never does -- which is exactly why this branch needs driving: unreachable from
        the corpus, and a mutation deleting it would leave the suite green (WP-8.11)."""
        out = PC._clear_on_a_constant({
            "faults_clear": [{"fault": "x", "name": "X", "results": [
                {"expression": "equipment_units_visible_on_the_entrance_elevation"}]}],
            "faults_clear_truncated": 7,
        })
        assert isinstance(out, dict) and "could_not_evaluate" in out
        assert "7" in out["could_not_evaluate"]

    def test_a_clear_row_reading_no_suspect_name_is_not_reported(self):
        """Driven, so it cannot pass by the corpus happening to have no clean passes."""
        fr = {"faults_clear": [
            {"fault": "clean", "name": "Clean", "results": [{"expression": "a_real_measurement / another"}]},
            {"fault": "suspect", "name": "Suspect",
             "results": [{"expression": "equipment_units_visible_on_the_entrance_elevation"}]},
        ]}
        out = PC._clear_on_a_constant(fr)
        assert [r["fault"] for r in out] == ["suspect"]
