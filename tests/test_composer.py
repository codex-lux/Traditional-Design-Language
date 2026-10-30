"""Pins the composer's ranking — see docs/compose.md and the 23 Aug review's
finding that a fix to the `via` adjacency rule 'moved the single-pile Georgian
to first place.' A scoring regression that silently drops it back to fourth is
exactly what this test protects against.

UPDATED for WP-3.2 (the elevation generator): build/plan_check.py's own ELEVATION LAYER now
folds build/elevation.py's measurements into every plan_check.check() call, including the ones
build/compose.py runs internally to score candidates -- so a candidate's elevation (bay count,
cornice proportion, window composition) can now change its ranking where before only its room
plan could. Traced directly (not assumed): for family-georgian's own brief, the single-pile
Centre Passage candidate is a very wide, shallow massing (about 82.5 ft wide, 23 ft clear depth)
-- WP-3.2's own bay-grouping formula gives it a genuine 9-bay front, which faults/even-bay-
front.json's own secondary test calls out by name ("Nine-bay fronts are institutional, not
domestic"), and the same shallow depth against a tall Tidewater wall gives a real
roof-height-to-wall-height ratio under faults/truss-flattened-pitch.json's own 0.45 floor. Both
are genuine, previously-invisible proportion problems this parti actually has at this brief's
scale -- not a scoring bug, and not the same silent regression this file was originally written
to catch. See docs/reports/wp-3.2-elevation-generator.md's own 'What was found' for the full trace.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _brief(name):
    with open(os.path.join(ROOT, "briefs", f"{name}.json")) as f:
        return json.load(f)


class TestFamilyGeorgianBrief:
    def test_single_pile_centre_passage_now_carries_two_real_elevation_fatals(self, compose_module):
        """Confirms the two fatals traced in this file's own module docstring are still exactly
        even-bay-front and truss-flattened-pitch -- if this ever changes, the ranking test below
        needs re-tracing, not just re-pinning to whatever the new number happens to be.

        WP-4.5 widened compose()'s pick window from 6 partis to 12, which found four candidates
        with zero fatal on this brief -- so this two-fatal candidate correctly no longer appears
        in the returned top four. That is the window working, not a regression. The finding this
        test exists to pin is about the PARTI, not its rank, so it is now scored directly rather
        than fished out of a truncated list: the old `next(...)` raised StopIteration the moment
        the candidate placed fifth, which reads as a crash rather than as the pin it is."""
        brief = _brief("family-georgian")
        plan, _log, _parti = compose_module.instantiate("centre-passage-single-pile", brief)
        # RE-TRACED 29 Oct 2026 (Phase 17, WP-17.2), AS THIS DOCSTRING ASKS. The two fatals were a
        # property of the house the default placer built and not of the parti: with no `parti` on
        # the plan record the single pile was placed on the placer's 10 ft module, 90 x 25 ft over
        # nine bays, where its ridge is 0.39 of its wall and its upper front has no centre. A
        # composed plan names its parti and its entrance front now, and the house is built on the
        # diagram's own footprint -- 70 x 32 ft over seven bays -- where both clear on measured
        # figures (not unjudged). The two fatals are held here as what they are: a finding about
        # the default-module house, reproduced by taking the parti and the front back off.
        res = compose_module.PC.check(plan)
        assert res["counts"].get("fatal", 0) == 0, [f["statement"] for f in res["findings"]
                                                    if f["severity"] == "fatal"]
        # "CLEAR ON MEASURED FIGURES (NOT UNJUDGED)" IS FOUR STATEMENTS, AND THIS HELD ONE (the
        # audit of Phase 17, finding 32). Fault-layer findings are the PRESENT faults; a fault the
        # house could not be judged on goes to `fault_unjudged`, one whose preconditions decline
        # to `fault_not_applicable`, and neither emits a finding -- and `counts["fatal"]` counts
        # no unjudged fatal. So absence from the findings passed whether the two faults cleared,
        # went unjudged or did not apply. Each state is now ruled out by name, and under R4 a
        # fault in none of the three is clear on its governing (primary) test.
        two = {"even-bay-front", "truss-flattened-pitch"}
        present = {f.get("fault") or f["id"] for f in res["findings"] if f.get("layer") == "fault"}
        assert not present & two, present & two
        unjudged = {r["fault"] for r in res["fault_unjudged"]}
        assert not unjudged & two, [r for r in res["fault_unjudged"] if r["fault"] in two]
        not_applicable = {r["fault"] for r in res["fault_not_applicable"]}
        assert not not_applicable & two, [r for r in res["fault_not_applicable"]
                                          if r["fault"] in two]
        # And the governing test reads a measurement OF THE HOUSE, not the generator's own
        # constant. `fault_clear_on_a_generator_constant` lists a cleared fault if ANY of its
        # tests reads a critic-suspect name, and truss-flattened-pitch is on it: its secondary
        # `count_of_distinct_roof_slope_angles_on_the_building` is one (measured on 33652ac). So
        # the assertion is on the PRIMARY: the suspect names a row reads are disjoint from the
        # identifiers of that fault's own `test.expression`. A list is required first -- the
        # reader returns None or a could-not-evaluate dict when it cannot look, and absence from
        # either would be vacuous.
        DET = compose_module.PC._load("detection", os.path.join(ROOT, "build", "detection.py"))
        constant = res["fault_clear_on_a_generator_constant"]
        assert isinstance(constant, list), constant
        for row in constant:
            if row["fault"] in two:
                with open(os.path.join(ROOT, "faults", row["fault"] + ".json")) as f:
                    primary = DET.identifiers(json.load(f)["test"]["expression"])
                assert primary and not primary & set(row["reads"]), (row, primary)
        default = dict(plan)
        default.pop("parti")
        default["context"] = {k: v for k, v in plan["context"].items() if k != "entrance_faces"}
        res0 = compose_module.PC.check(default)
        single_pile = {"counts": res0["counts"], "worst": res0["findings"]}
        assert single_pile["counts"].get("fatal", 0) == 2
        rules = {w["statement"].split(":")[0] for w in single_pile["worst"] if w["severity"] == "fatal"}
        assert any("Front With No Centre" in r for r in rules)
        assert any("Truss Default" in r for r in rules)

    def test_centre_passage_double_pile_ranks_first(self, compose_module):
        """RE-PINNED by WP-4.5, and the move is the fix rather than a regression.

        This asserted Side-Hall Town House. That was the answer a nativity weight of 6 gave:
        fit ran 0-7 and a serious finding cost 8, so five serious findings outweighed being the
        right diagram, and the composer ranked a TOWN HOUSE diagram first for a Tidewater
        Georgian plantation house. WP-4.5 raised the weight to 20 (compose.py's NATIVITY_W,
        which carries the argument), and the brief now returns the centre-passage double pile --
        which is what a five-bay Tidewater Georgian of 3,200 sf actually is, and what
        styles/tidewater-georgian.json marks canonical.

        The failure this file was originally written to catch is unchanged and still guarded:
        a scoring regression that drops the right Georgian diagram down the list still fails
        here. It is now pinned to a better right answer."""
        result = compose_module.compose(_brief("family-georgian"), revise=False)
        # RE-TRACED 29 Oct 2026 (Phase 17, WP-17.2): the single pile's two fatals were the
        # default-module house's (the test above), and with them gone both native centre passages
        # are fatal-free and the score decides -- 68.2 against 66.9 when this was re-cut. What this
        # test guards is that a scoring regression does not drop the RIGHT GEORGIAN DIAGRAM down
        # the list; both are native and canonical for the style, so either leads, and the double
        # pile must be among the first two.
        # RE-TRACED AGAIN 30 Oct 2026 (the audit of Phase 17): `compose.repair` ran the declared
        # loop under a 6 s wall clock, so the house ranked here depended on what had run before it
        # in the process -- cold, the five-part took 14 moves and scored 65.1; warm, 21 and 69.0.
        # Bounded by its work now, it is 69.0 every time, and it leads: R13 composed its passage to
        # the floor its own fault convicts at, which is the lead Lucas ruled R13 knowing (report
        # §X, ruling 13). All three are the style's own diagrams on canonical massings, so the
        # guard is that one of THEM leads and the double pile stays among the first three -- a
        # scoring regression that drops the Georgian diagrams down the list still fails here.
        natives = ("Centre Passage, Double Pile", "Centre Passage, Single Pile", "Five-Part Palladian")
        first_three = [c["parti_name"] for c in result["candidates"][:3]]
        assert result["candidates"][0]["parti_name"] in natives, first_three
        assert "Centre Passage, Double Pile" in first_three, first_three

    def test_the_winning_diagram_is_native_to_the_brief_s_style(self, compose_module):
        """The structural claim behind the pin above, which never needs re-pinning.

        A composer that recommends a diagram no style in the brief's own lineage ever built has
        failed at the thing WP-4.5 exists to fix, whatever it scores. Stated separately from the
        identity pin so that when a future package moves the winner, this test says whether the
        move was legitimate."""
        import json as _json, os as _os
        brief = _brief("family-georgian")
        result = compose_module.compose(brief, revise=False)
        winner = result["candidates"][0]
        parti = compose_module.PARTIS[winner["parti"]]
        chain = compose_module.PC.style_chain(brief["style"], compose_module.C)
        assert set(parti["styles"]) & (chain | {brief["style"]}), (
            f'{winner["parti_name"]} is native to no style in {brief["style"]}\'s lineage')

    def test_top_candidate_has_zero_fatal(self, compose_module):
        result = compose_module.compose(_brief("family-georgian"), revise=False)
        top = result["candidates"][0]
        assert top["counts"].get("fatal", 0) == 0

    def test_returns_four_contrasting_candidates_never_one(self, compose_module):
        """Decision not to undo #10: the composer returns N contrasting
        candidates and never calls a plan 'good.'"""
        result = compose_module.compose(_brief("family-georgian"), revise=False)
        assert len(result["candidates"]) == 4
        partis = {c["parti_name"] for c in result["candidates"]}
        assert len(partis) == 4, "candidates must be genuinely different partis, not near-duplicates"

    def test_every_candidate_states_what_it_trades_away(self, compose_module):
        """The honest part, per docs/compose.md: 'every diagram gives something
        up.'"""
        result = compose_module.compose(_brief("family-georgian"), revise=False)
        for c in result["candidates"]:
            assert c.get("trades_away"), f"{c['parti_name']} has no trades_away statement"


class TestBungalowBrief:
    def test_open_linear_bungalow_ranks_first_with_zero_fatal(self, compose_module):
        result = compose_module.compose(_brief("bungalow-small"), revise=False)
        top = result["candidates"][0]
        assert top["parti_name"] == "Bungalow, Open and Linear"
        assert top["counts"].get("fatal", 0) == 0


# ------------------------------------------------------------------ WP-14.19: a brief may name a parti
# Ruled 25 Sep 2026 (`oq/a-brief-cannot-name-a-parti`, answer 1): a brief may name a parti, and the
# composer guarantees it a place among the contrasting candidates -- scored by the same arithmetic,
# appended after the set if the composer's own ranking does not return it, displacing nothing. A
# parti not native to the style is borrowed and says so. A named parti the brief's own massing
# contradicts is refused by name before a job starts.
#
# THE FIXTURE BRIEF IS THE GEORGIAN ONE NARROWED TO ITS OWN CANONICAL MASSING, and that is for speed
# and nothing else: `four-over-four` admits three partis, so a compose considers three diagrams
# rather than thirteen, and every premise below is ASSERTED rather than assumed -- which diagram the
# composer returns at one candidate is a property of the tree, and a premise that stops holding must
# say so rather than let an assertion go vacuous.
import pytest as _pytest


def _narrow():
    b = _brief("family-georgian")
    b["massing"] = "four-over-four"
    return b


def _named(parti, **context):
    b = _narrow()
    b["parti"] = parti
    b["context"] = dict(b["context"], **context)
    return b


def _key(c):
    # what makes a candidate THIS candidate: the diagram, its verdict and its score
    return (c["parti"], c["counts"].get("fatal", 0), c["counts"].get("serious", 0), c["score"])


@_pytest.fixture(scope="module")
def unnamed_set(compose_module):
    return compose_module.compose(_narrow(), 1, revise=False)


@_pytest.fixture(scope="module")
def below_the_cut(compose_module, unnamed_set):
    """A NATIVE parti the composer considers and does not return at one candidate."""
    picks = compose_module.pick_partis(_narrow(), limit=12)
    returned = {c["parti"] for c in unnamed_set["candidates"]}
    native = [p["parti"] for p in picks if p["nativity"] == "native" and p["parti"] not in returned]
    assert native, ("premise: at one candidate every native diagram of the narrowed Georgian brief "
                    "is returned, so no native parti falls below the cut -- re-pick the brief rather "
                    "than let the guarantee's test pass without an append to test")
    return native[0]


@_pytest.fixture(scope="module")
def named_set(compose_module, below_the_cut):
    return compose_module.compose(_named(below_the_cut), 1, revise=False)


class TestABriefMayNameAParti:
    def test_a_native_parti_below_the_cut_is_returned(self, unnamed_set, named_set, below_the_cut):
        """The guarantee: the named diagram is among the candidates, as candidate N+1."""
        got = [c["parti"] for c in named_set["candidates"]]
        assert below_the_cut in got, f"{below_the_cut} was named and not returned: {got}"
        n1 = len(unnamed_set["candidates"]) + 1
        np_ = named_set["named_parti"]
        assert np_ == {"parti": below_the_cut, "nativity": "native", "returned": True,
                       "appended": True, "rank": n1}, np_
        c = named_set["candidates"][-1]
        assert c["parti"] == below_the_cut and c["named_by_brief"] is True and c["nativity"] == "native"
        assert "named by the brief" in c["why_this_diagram"][0]
        assert any(f"appended as candidate {n1}" in line for line in named_set["how_to_read_this"])

    def test_the_composers_own_set_is_unchanged_by_a_name(self, unnamed_set, named_set):
        """Displaces nothing: the first N candidates are the set the composer returns with no name,
        in the same order and with the same verdicts, and only then the named one."""
        n = len(unnamed_set["candidates"])
        assert n == 1, "premise: the fixture asks for one candidate"
        assert len(named_set["candidates"]) == n + 1
        assert [_key(c) for c in named_set["candidates"][:n]] == [_key(c) for c in unnamed_set["candidates"]]
        assert all(c["named_by_brief"] is False for c in named_set["candidates"][:n])
        assert unnamed_set["named_parti"] is None
        assert all(c["named_by_brief"] is False for c in unnamed_set["candidates"])

    def test_a_parti_the_composer_returns_anyway_is_not_appended(self, compose_module, unnamed_set):
        """Naming the composer's own choice changes nothing but the labels: no second copy."""
        leader = unnamed_set["candidates"][0]["parti"]
        got = compose_module.compose(_named(leader), 1, revise=False)
        assert [_key(c) for c in got["candidates"]] == [_key(c) for c in unnamed_set["candidates"]]
        assert got["named_parti"] == {"parti": leader, "nativity": "native", "returned": True,
                                      "appended": False, "rank": 1}
        assert got["candidates"][0]["named_by_brief"] is True

    def test_a_borrowed_parti_carries_nativity_borrowed_and_says_so(self, compose_module, unnamed_set):
        picks = {p["parti"]: p for p in compose_module.pick_partis(_narrow(), limit=12)}
        borrowed = [p for p, r in picks.items() if r["nativity"] == "borrowed"
                    and p not in {c["parti"] for c in unnamed_set["candidates"]}]
        assert borrowed, "premise: the narrowed brief considers a borrowed diagram it does not return"
        got = compose_module.compose(_named(borrowed[0]), 1, revise=False)
        assert got["named_parti"]["nativity"] == "borrowed" and got["named_parti"]["returned"]
        c = got["candidates"][-1]
        assert c["parti"] == borrowed[0] and c["nativity"] == "borrowed" and c["named_by_brief"]
        assert any("borrowing" in w and w.startswith("NOT native") for w in c["why_this_diagram"]), \
            c["why_this_diagram"]
        assert any("It is borrowed" in line for line in got["how_to_read_this"])

    def test_a_parti_the_lot_drops_is_said_to_be_dropped(self, compose_module):
        """If the lot drops it there is nothing to append, and the result says so by name."""
        brief = _named("foursquare-quadrant", lot_width_ft=30)
        got = compose_module.compose(brief, 1, revise=False)
        dropped = {d["parti"] for d in got.get("dropped_lot_infeasible") or []}
        assert "foursquare-quadrant" in dropped, "premise: a 30 ft lot drops the thirteen-foot-bay foursquare"
        assert "foursquare-quadrant" not in {c["parti"] for c in got["candidates"]}
        np_ = got["named_parti"]
        assert np_["returned"] is False and np_["why"].startswith("the lot drops it: ")
        assert "rank" not in np_
        assert any("not among the candidates" in line for line in got["how_to_read_this"])


class TestTheNamedPartiIsPickedByTheSameArithmetic:
    def test_pick_partis_keeps_the_named_parti_past_the_cut_at_its_own_fit(self, compose_module):
        brief = _brief("family-georgian")
        full = {p["parti"]: p for p in compose_module.pick_partis(brief, limit=99)}
        cut = compose_module.pick_partis(brief, limit=1)
        outside = sorted(set(full) - {p["parti"] for p in cut})
        assert outside, "premise: a limit of one cuts some diagram off"
        named = outside[-1]
        got = compose_module.pick_partis(dict(brief, parti=named), limit=1)
        assert got[-1]["parti"] == named and got[-1]["named_by_brief"] is True, \
            f"{named} was named and not kept past the cut: {[p['parti'] for p in got]}"
        assert [p["parti"] for p in got[:-1]] == [p["parti"] for p in cut], "the cut itself moved"
        assert got[-1]["fit"] == full[named]["fit"], "being named bought the diagram points"

    def test_a_limit_of_nothing_asks_for_nothing_even_with_a_name(self, compose_module):
        brief = dict(_brief("family-georgian"), parti="tower-villa")
        assert compose_module.pick_partis(brief, limit=0) == []


class TestTheBriefIsCheckedBeforeAnythingIsComposed:
    def test_both_shipped_briefs_validate_under_the_new_schema_and_carry_no_parti(self, compose_module):
        import jsonschema
        with open(os.path.join(ROOT, "schema", "brief.schema.json")) as f:
            schema = json.load(f)
        assert schema["version"] == "0.2.0"
        assert schema["properties"]["parti"]["pattern"] == "^[a-z0-9]+(-[a-z0-9]+)*$"
        names = sorted(n for n in os.listdir(os.path.join(ROOT, "briefs")) if n.endswith(".json"))
        assert names, "premise: the repository ships example briefs"
        for n in names:
            brief = _brief(n[:-len(".json")])
            jsonschema.validate(brief, schema)
            assert "parti" not in brief, n
            assert compose_module.check_brief_refs(brief) is None, n
        named = dict(_brief("family-georgian"), parti="centre-passage-double-pile")
        jsonschema.validate(named, schema)
        with _pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(dict(named, parti="../plans/x"), schema)

    def test_an_unknown_parti_is_refused_by_name(self, compose_module):
        ref = compose_module.check_brief_refs(dict(_brief("family-georgian"), parti="no-such-parti"))
        assert ref and "'no-such-parti'" in ref and "no parti has that id" in ref

    def test_a_parti_the_briefs_massing_contradicts_is_refused_naming_both(self, compose_module):
        brief = dict(_narrow(), parti="octagon-radial")
        ref = compose_module.check_brief_refs(brief)
        assert ref and "'octagon-radial'" in ref and "'four-over-four'" in ref
        with _pytest.raises(ValueError, match="octagon-radial"):
            compose_module.compose(brief, 1, revise=False)   # never silently re-picked

    def test_a_parti_built_on_an_alternate_massing_is_not_a_contradiction(self, compose_module):
        # five-part-palladian names four-over-four among its alternates; the filter admits it,
        # so the refusal must too -- the two read one predicate
        p = compose_module.PARTIS["five-part-palladian"]
        assert "four-over-four" in (p.get("alternate_massings") or []), "premise"
        assert compose_module.check_brief_refs(dict(_narrow(), parti="five-part-palladian")) is None


class TestOneSpellingOfNativity:
    def test_list_partis_and_pick_partis_agree_for_every_style_and_parti(self, compose_module, core_module):
        """`core.list_partis` and `compose.pick_partis` are the two readers, and they read one
        function. Held over every (style, parti) pair in the corpus, in both directions: every
        parti the style's list carries is picked with the same nativity, every non-borrowed pick
        is listed, and a pick's own words agree with its nativity."""
        words = {"lineage": "native to an ancestor or relative",
                 "borrowed": "NOT native to this style"}
        styles = sorted(core_module._data()["styles"])
        # premise: both readers see the same corpus, every style of it and not a sample
        assert styles and set(styles) == set(compose_module.C["styles"])
        checked = 0
        for sid in styles:
            listed = {p["id"]: p["nativity"] for p in
                      core_module.list_partis(style=sid, include_borrowed=True)["partis"]}
            default = {p["id"] for p in core_module.list_partis(style=sid)["partis"]}
            picks = {p["parti"]: p for p in compose_module.pick_partis(
                {"style": sid, "target_area_sf": 2000}, limit=99)}
            assert set(listed) == set(picks) == set(compose_module.PARTIS), sid
            for pid, pick in picks.items():
                assert listed[pid] == pick["nativity"] == compose_module.nativity(pid, sid), (sid, pid)
                word = f"native to {sid}" if pick["nativity"] == "native" else words[pick["nativity"]]
                assert any(w.startswith(word) for w in pick["why"]), (sid, pid, pick["why"])
                checked += 1
            assert default == {p for p, n in listed.items() if n != "borrowed"}, sid
        assert checked == len(styles) * len(compose_module.PARTIS)

    def test_nativity_has_three_answers_and_each_occurs(self, compose_module, core_module):
        seen = {compose_module.nativity(p, s) for p in compose_module.PARTIS
                for s in core_module._data()["styles"]}
        assert seen == set(compose_module.NATIVITY)
