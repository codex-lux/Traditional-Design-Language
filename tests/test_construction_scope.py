"""WP-8.4 — the construction vocabulary, the exception precondition, and the per-rule scope.

Three mechanisms, one table. `build/construction_vocabulary.py` is a CLOSED mapping from the
78 tokens the fault corpus uses onto variant ids that already exist in `kits/`;
`mcp_server/core.grant_exception` reads it to decide whether an exception's licence is earned;
`build/resolve_kit.eval_packs` reads it to decide whether a pack rule is about this wall.

Every count here is a RATCHET. The unevaluable figures are ceilings that may only fall and the
refusal figures are floors that may only rise, because both directions have a silent failure
mode: a vocabulary that stops resolving refuses nothing and reports success, and a scope whose
key is dropped one layer down refuses nothing and reports success too. That second one is not
hypothetical -- it is what happened to `applies_when` inside `proportion_engine.evaluate()`
while every one of this repository's checks stayed green.
"""
import importlib.util
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _mod(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


CV = _mod("construction_vocabulary", "build/construction_vocabulary.py")
CORE = _mod("core", "mcp_server/core.py")
RK = _mod("resolve_kit", "build/resolve_kit.py")

# --- ratchets, measured 28 Aug 2026 -----------------------------------------
CENSUS_CEILING = {          # may only FALL
    "unjudged": 54,                    # preconditions the corpus cannot resolve from a style
    "unevaluated_regions": 79,         # the key no gazetteer exists for
    "unevaluated_date_range": 102,     # decidable only where a caller supplies a date
    "bounds_test_unjudged": 44,        # of those, the ones that would replace a primary test
    # ADDED 28 AUG 2026 BY THE AUDIT: `slots` was in NO bucket, so 68 of the 331 records were
    # absent from the census entirely and `grant_exception` returned `why: "no precondition"`
    # for records that carry one. `slots_only` is the sharp half -- a licence where nothing
    # whatever about the precondition is read, and 54 of them substitute a `bounds_test` for
    # the fault's primary test on the strength of it. A ceiling because the work is to make
    # these evaluable, or to rule that a slot scope is not a precondition and move it.
    "unevaluated_slots": 104,
    "slots_only": 67,
}
CENSUS_FLOOR = {            # may only RISE
    "with_granted_when": 331,
    "construction": 123,
    "granted": 51,
    # 20 -> 18 ON 28 AUG 2026, AND A FLOOR MAY ONLY RISE, SO THIS NEEDS ITS REASON IN FULL.
    # What the floor protects is the evaluator continuing to refuse at all -- the regression
    # it exists to catch is a change that quietly grants everything, which is what the corpus
    # did for as long as this field went unread. It does NOT protect a wrong refusal. The
    # audit swept every construction precondition against the style in its own `style` key and
    # found 19 refused there; 17 are substantive (a stucco-over-frame `pueblo-revival` really
    # is not adobe) and two were licences refused for being exactly what they describe --
    # `water-table-that-follows-the-grade` on Cotswold and `quoin-by-catalogue` on Scottish
    # Baronial, each naming an exact wythe variant where its own prose says RUBBLE. Correcting
    # the two conditions moved them to `granted`, so `granted` rises 49 -> 51 and `refused`
    # falls 20 -> 18, one pair of movements from one fix.
    # `TestALicenceIsNotRefusedOnTheStyleItWasWrittenFor` is the guard that makes lowering
    # this safe: it fails if any licence is refused on its own style while a broader token
    # containing the one it names holds, so a refusal cannot be dropped for a bad reason.
    "refused": 18,
}
UNMAPPABLE_CEILING = 17     # tokens the corpus records nothing for
# (pack, slot, dimension) -> deliveries the OQ 88 scope drops as out of scope. Floors.
# Re-measured 28 Aug 2026 after the vocabulary was ported into `proportion_engine.rule_scope`
# in place of `construction_of`'s substring test over the cladding, and LOWERED BY ONE EACH
# after the WP-8.4 adversarial audit found the authority walk over-refusing: a lower-authority
# slot was allowed to turn a higher-authority slot's "this style is canonically BOTH" into a
# definite `fails`. Two drops that direction were wrong and are now `undecidable` -- delivered
# with the reason attached, which is the third state doing its job. A floor lowered because the
# reader got MORE CORRECT has to say so, or the next reader reads it as a refusal that was
# quietly weakened.
SCOPE_FLOOR = {
    ("sash-light", "window_sill", "projection"): 27,
    ("opening-proportion", "window_surround_wood", "exterior_head_assembly_height"): 59,
    ("facade-gable", "gable_treatment", "parapet_height"): 14,
}


class TestTheVocabularyIsClosedAndConsistent(unittest.TestCase):
    def test_every_mapped_variant_id_exists_in_kits(self):
        errs = CV.check_table()
        self.assertEqual([], errs, "\n".join(errs))

    def test_every_token_the_corpus_uses_is_in_the_table(self):
        used = set(CV.corpus_tokens())
        unknown = sorted(used - set(CV.VOCABULARY) - set(CV.UNMAPPABLE))
        self.assertEqual([], unknown,
                         "granted_when.construction names %s, which is in neither VOCABULARY "
                         "nor UNMAPPABLE. Report the gap; do not add a token." % unknown)

    def test_unmappable_is_a_ceiling(self):
        self.assertLessEqual(
            len(CV.UNMAPPABLE), UNMAPPABLE_CEILING,
            "a token moved INTO UNMAPPABLE. That is a mechanism going quiet: its "
            "preconditions stop being evaluated. If it is right, re-pin and say why.")

    def test_a_partial_token_can_never_hold(self):
        """`thick-stucco` knows the wall is rendered and nothing about how thick.

        A partial token's best case is `undecidable`. Reporting `holds` on the half we can
        see would widen a licence its author deliberately narrowed."""
        partial = [t for t, v in CV.VOCABULARY.items() if v["strength"] == "partial"]
        self.assertTrue(partial, "no partial tokens left -- re-pin this test or delete it")
        g = RK.load_graph()
        for token in partial:
            for nid in sorted(g["nodes"]):
                kit, _ = RK.resolve_slots(g, RK.chain_for(g, nid), RK.scope_for(g, nid))
                verdict, _why = CV.resolve(token, kit)
                self.assertNotEqual("holds", verdict,
                                    "%s held on %s; a partial token may only fail or be "
                                    "undecidable" % (token, nid))

    def test_an_unknown_token_is_unmappable_and_never_silently_true(self):
        verdict, why = CV.resolve("not-a-real-token", {})
        self.assertEqual("unmappable", verdict)
        self.assertIn("report the gap", why)


class TestTheExceptionPreconditionIsRead(unittest.TestCase):
    def test_a_licence_with_an_unread_precondition_does_not_claim_to_have_none(self):
        """`why: "no precondition"` on a record that carries one is a false statement.

        104 exceptions carry `granted_when.slots` and 67 carry NOTHING ELSE. Those were
        returned `granted / no precondition / unevaluated: []`, and 54 of them substitute a
        `bounds_test` for the fault's primary test whenever the verdict is `granted` -- so a
        fault was judged by the exception's looser rule on the strength of a precondition
        nobody read. That is the defect this whole package removes, one key over, and it
        survived the package. Found by its own adversarial audit.
        """
        D = CORE._data()
        slots_only = [(fid, e) for fid, f in D["faults"].items()
                      for e in f.get("exceptions", [])
                      if (e.get("granted_when") or {}).get("slots")
                      and not (e.get("granted_when") or {}).get("construction")]
        self.assertGreaterEqual(len(slots_only), 60,
                                "the slots-only population has gone; this test is vacuous")
        for fid, exc in slots_only:
            g = CORE.grant_exception(exc, exc.get("style"))
            self.assertIn("slots", g["unevaluated"],
                          "%s/%s does not disclose its unread precondition" % (fid, exc.get("style")))
            self.assertNotEqual("no precondition", g["why"],
                                "%s/%s claims to have no precondition and carries one"
                                % (fid, exc.get("style")))

    def test_the_census_ratchets(self):
        c = CORE.exception_precondition_census()
        for k, ceiling in CENSUS_CEILING.items():
            self.assertLessEqual(c[k], ceiling,
                                 "%s rose to %d against a ceiling of %d -- more of this "
                                 "corpus is unjudged than when the ceiling was set"
                                 % (k, c[k], ceiling))
        for k, floor in CENSUS_FLOOR.items():
            self.assertGreaterEqual(c[k], floor,
                                    "%s fell to %d against a floor of %d -- a precondition "
                                    "stopped being read" % (k, c[k], floor))

    def test_a_licence_written_for_adobe_is_not_granted_to_a_frame_house(self):
        """The flagship. `pueblo-revival` resolves canonically to stucco-over-wood-frame and
        `architrave-that-is-not-there`'s licence is written for adobe or rammed earth."""
        D = CORE._data()
        f = D["faults"]["architrave-that-is-not-there"]
        exc = next(e for e in f["exceptions"] if e["style"] == "pueblo-revival")
        self.assertEqual(["adobe", "rammed-earth"], exc["granted_when"]["construction"])
        g = CORE.grant_exception(exc, "pueblo-revival")
        self.assertNotEqual("granted", g["verdict"])

    def test_a_house_that_declares_its_wall_settles_the_question(self):
        D = CORE._data()
        f = D["faults"]["architrave-that-is-not-there"]
        exc = next(e for e in f["exceptions"] if e["style"] == "pueblo-revival")
        yes = CORE.grant_exception(exc, "pueblo-revival",
                                   {"declared": {"construction_type": "adobe"}})
        self.assertEqual("granted", yes["verdict"])
        no = CORE.grant_exception(exc, "pueblo-revival",
                                  {"declared": {"construction_type": "platform-frame"}})
        self.assertEqual("refused", no["verdict"])

    def test_an_unresolved_precondition_is_unjudged_only_where_it_changes_the_answer(self):
        """Judged both ways, asserted on BEHAVIOUR.

        Where the exception's bounds_test and the general rule agree, the unresolved
        question is immaterial and reporting could-not-evaluate would be a fake unjudged --
        as dishonest in its own direction as a fake pass. Over 164 styles that is the
        difference between 26 verdicts moving and 11.

        THIS TEST USED TO READ core.py's SOURCE for two strings, which the WP-8.4
        adversarial audit correctly called vacuous: replacing `if sa != sb:` with
        `if False:` disables the whole mechanism and a source-reading test stays green.
        It now sweeps the corpus and pins both halves of the behaviour -- the rows where
        the two rules DISAGREE (which must be unjudged, with both verdicts named) and the
        rows where they AGREE (which must be answered, and flagged immaterial). Disabling
        the comparison in either direction moves one of these counts to zero."""
        el = _mod("elevation", "build/elevation.py")
        plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json"),
                              encoding="utf-8"))
        disagree, agree = [], 0
        for style in sorted(CORE._data()["styles"]):
            probe = dict(plan)
            probe["style"] = style
            try:
                meas = el.build_elevation(probe)["measurements"]
            except Exception:
                continue
            r = CORE.check_measurements(meas, style=style, limit=10 ** 6)
            for row in r["could_not_judge"]:
                u = row.get("exception_unjudged")
                if u:
                    disagree.append((style, row["fault"], u))
            for key in ("faults_present", "faults_clear"):
                for row in r[key]:
                    if row.get("exception_unjudged_but_immaterial"):
                        agree += 1

        self.assertGreaterEqual(len(disagree), 3, (
            "no fault is reported could-not-evaluate for an unresolvable exception "
            "precondition. Either the comparison was disabled -- an unresolved precondition "
            "then silently takes one branch -- or the corpus no longer contains a case where "
            "the two rules disagree, in which case re-pin this."))
        self.assertGreaterEqual(agree, 2, (
            "no row is flagged `exception_unjudged_but_immaterial`. Judging both ways has "
            "stopped, and every unresolved precondition is now a could-not-evaluate even "
            "where the two rules reach the SAME verdict -- a fake unjudged."))
        for _style, _fault, u in disagree:
            self.assertIn("under_the_exception", u)
            self.assertIn("under_the_general_rule", u)
            self.assertNotEqual(u["under_the_exception"], u["under_the_general_rule"], (
                "a row was reported could-not-evaluate although the two rules AGREE about "
                "it -- that is the fake unjudged this mechanism exists to avoid"))
            self.assertTrue(u.get("because"), "the unresolved condition is not named")

    def test_the_unevaluated_keys_are_disclosed_on_every_verdict(self):
        D = CORE._data()
        seen = 0
        for f in D["faults"].values():
            for exc in (f.get("exceptions") or []):
                gw = exc.get("granted_when") or {}
                if not gw.get("regions"):
                    continue
                g = CORE.grant_exception(exc, exc.get("style"))
                self.assertIn("regions", g["unevaluated"],
                              "%s: a region precondition was neither evaluated nor "
                              "disclosed" % f["id"])
                seen += 1
        self.assertGreater(seen, 0)

    def test_no_exception_still_carries_the_old_field_name(self):
        D = CORE._data()
        for f in D["faults"].values():
            for exc in (f.get("exceptions") or []):
                self.assertNotIn("applies_when", exc,
                                 "%s: exceptions[].applies_when was renamed `granted_when` "
                                 "(WP-8.4). The surviving `applies_when` is the test-level "
                                 "precondition on MEASUREMENTS and means something else."
                                 % f["id"])


class TestThePerRuleScope(unittest.TestCase):
    """OQ 88: three pack rules stated a scope in prose that their data did not carry."""

    @classmethod
    def setUpClass(cls):
        g = RK.load_graph()
        cls.refused = {k: 0 for k in SCOPE_FLOOR}
        cls.declined_away = {k: 0 for k in SCOPE_FLOOR}
        cls.withheld_away = {k: 0 for k in SCOPE_FLOOR}
        cls.delivered = {k: 0 for k in SCOPE_FLOOR}
        cls.unjudged = {k: 0 for k in SCOPE_FLOOR}
        for nid in sorted(g["nodes"]):
            chain = RK.chain_for(g, nid)
            kit, _ = RK.resolve_slots(g, chain, RK.scope_for(g, nid))
            dropped = []
            by_slot, _e = RK.eval_packs(RK.resolve_packs(g, chain),
                                        {"ceiling_height": 108.0}, None, kit, dropped)
            for d in dropped:
                key = (d["pack"], d["slot"], d.get("dimension"))
                if key in SCOPE_FLOOR:
                    cls.refused[key] += 1

            # A DECLINE IS A REFUSAL THIS COUNTER CANNOT SEE, and that blindness turned the
            # suite red three nodes after the fact. WP-8.7 authored 114 `declined_packs`
            # entries; three of them refuse `opening-proportion`, so its rule no longer
            # ARRIVES at those nodes and the scope never gets the chance to drop it. `refused`
            # fell 59 -> 56 and read exactly like a scope that had stopped working.
            #
            # Measured rather than assumed, by running this same reader over the graph with
            # and without those three declines: 56 against 59, and the difference is exactly
            # `andalusian-courtyard-vernacular`, `french-provincial-farmhouse` and
            # `moorish-andalusian`. The delivery is refused EARLIER and BY A PERSON, quoting
            # the node's own record, which is strictly stronger than an automatic scope test.
            #
            # So the floor is NOT lowered -- lowering is what the note above `SCOPE_FLOOR`
            # warns against, and a floor that drops by one every time somebody declines a pack
            # protects nothing by the end of the backlog. The second mechanism is counted
            # instead, and the sum is held to the original 59. A scope that really stops
            # refusing still fails this, because a decline it never had cannot make up the
            # difference.
            declined = {d["pack"] for d in (g["nodes"][nid].get("declined_packs") or [])}
            for key in SCOPE_FLOOR:
                if key[0] not in declined:
                    continue
                # Would this node have received THIS rule but for the decline? Asked by
                # re-resolving with the decline lifted, rather than assumed. The lift is done
                # IN PLACE and restored in a finally: a `copy.deepcopy` of the graph per probe
                # made this class take minutes, and the graph is only read here.
                original = g["nodes"][nid].get("declined_packs")
                try:
                    g["nodes"][nid]["declined_packs"] = [
                        d for d in (original or []) if d["pack"] != key[0]]
                    p_chain = RK.chain_for(g, nid)
                    p_kit, _ = RK.resolve_slots(g, p_chain, RK.scope_for(g, nid))
                    p_dropped = []
                    RK.eval_packs(RK.resolve_packs(g, p_chain),
                                  {"ceiling_height": 108.0}, None, p_kit, p_dropped)
                finally:
                    if original is None:
                        g["nodes"][nid].pop("declined_packs", None)
                    else:
                        g["nodes"][nid]["declined_packs"] = original
                for d in p_dropped:
                    if (d["pack"], d["slot"], d.get("dimension")) == key:
                        cls.declined_away[key] += 1

            # A THIRD REFUSAL MECHANISM, AND IT ARRIVED EXACTLY AS THE SECOND ONE DID (WP-8.11).
            # OQ 51's opt-in gate stops a flipped pack reaching a node that has not opted in, so
            # the rule never arrives and the scope never gets to drop it. `facade-gable`'s
            # `gable_treatment/parapet_height` fell from 14 refusals to 3 the moment that pack
            # flipped, which reads exactly like a scope that has stopped working -- the same
            # false signal the decline counter was added for, from a mechanism that did not exist
            # when it was added.
            #
            # THE FLOOR IS NOT LOWERED, for the reason the note above `SCOPE_FLOOR` gives and the
            # decline block repeats: a floor that drops every time a pack is flipped protects
            # nothing by the last flip. The third mechanism is counted instead, by the same
            # in-place counterfactual -- lift the gate, re-resolve, see whether the scope would
            # have dropped this rule here.
            own_ids = {e["pack"] for e in (g["nodes"][nid].get("proportion_packs") or [])}
            opted = set(g["nodes"][nid].get("inherits_packs") or [])
            for key in SCOPE_FLOOR:
                pid = key[0]
                if ((g.get("_packs") or {}).get(pid, {}).get("delivery") != "opt-in"
                        or pid in own_ids or pid in opted or pid in declined):
                    continue
                try:
                    g["_packs"][pid]["delivery"] = "cascade"
                    w_chain = RK.chain_for(g, nid)
                    w_kit, _ = RK.resolve_slots(g, w_chain, RK.scope_for(g, nid))
                    w_dropped = []
                    RK.eval_packs(RK.resolve_packs(g, w_chain),
                                  {"ceiling_height": 108.0}, None, w_kit, w_dropped)
                finally:
                    g["_packs"][pid]["delivery"] = "opt-in"
                for d in w_dropped:
                    if (d["pack"], d["slot"], d.get("dimension")) == key:
                        cls.withheld_away[key] += 1

            for sid, rows in by_slot.items():
                for r in rows:
                    key = (r["pack"], sid, r.get("dimension"))
                    if key in SCOPE_FLOOR:
                        cls.delivered[key] += 1
                        if r.get("scope_unjudged"):
                            cls.unjudged[key] += 1

    def test_each_scope_refuses_at_least_what_it_refused_when_it_was_written(self):
        """The floor holds against ALL THREE refusal mechanisms, not just the scope's own.

        A delivery the scope would have dropped, on a node that has since DECLINED the pack or
        that no longer receives it because the pack is now `delivery: opt-in`, is refused earlier
        and for a stated reason. Counting only `refused` made those look like a scope going quiet;
        counting only the sum would let a real regression hide behind a decline or a flip. All
        three numbers are reported in the failure message so the next reader can tell them apart
        at a glance.

        The third was added in WP-8.11 for a defect identical in shape to the one that added the
        second, which is the argument for expecting a fourth: any mechanism that stops a delivery
        BEFORE the scope sees it looks, to this counter, like the scope failing."""
        for key, floor in SCOPE_FLOOR.items():
            total = (self.refused[key] + self.declined_away[key] + self.withheld_away[key])
            self.assertGreaterEqual(
                total, floor,
                "%s/%s/%s refuses %d deliveries by scope + %d refused earlier by a node's own "
                "`declined_packs` + %d never delivered because the pack is `delivery: opt-in` "
                "= %d, against a floor of %d. A scope that stops refusing "
                "reports success: `applies_when` was dropped inside "
                "proportion_engine.evaluate() and refused 0 of 293 with every check green."
                % (key + (self.refused[key], self.declined_away[key], self.withheld_away[key],
                          total, floor)))

    def test_no_scope_refuses_everything_it_reaches(self):
        """A rule refused everywhere is a rule that should be deleted, not scoped."""
        for key in SCOPE_FLOOR:
            self.assertGreater(self.delivered[key], 0,
                               "%s/%s/%s is delivered to NO node -- the scope has become a "
                               "deletion" % key)

    def test_a_style_that_may_be_either_is_delivered_flagged_rather_than_dropped(self):
        """The third state, counted. Undecidable is not refused: withholding a dimension on a
        maybe leaves the slot with nothing, which is worse than a dimension a reader can see
        is scoped."""
        for key in SCOPE_FLOOR:
            self.assertGreater(self.unjudged[key], 0,
                               "%s/%s/%s flags nothing `scope_unjudged`, so either every "
                               "style is decided or the third state has stopped being "
                               "reported" % key)

    def test_a_canonical_statement_outranks_a_permitted_one(self):
        """`jeffersonian-classicism` inherits a construction_type whose every variant is
        merely PERMITTED, so that slot cannot decide -- and its own cladding is canonically
        Flemish-bond brick with clapboard FORBIDDEN. Reading the permitted `beaded-clapboard`
        as "this might be a frame house" left a brick node undecided and still receiving a
        sloped timber sill, which is the very delivery OQ 88 is about."""
        g = RK.load_graph()
        kit, _ = RK.resolve_slots(g, RK.chain_for(g, "jeffersonian-classicism"),
                                  RK.scope_for(g, "jeffersonian-classicism"))
        self.assertEqual("fails", CV.resolve("wood-frame", kit)[0])

    def test_a_dual_construction_style_is_not_refused(self):
        """`charleston-georgian` is canonically BOTH braced timber frame and solid masonry,
        clapboard and Flemish bond. OQ 88 named it as a node wrongly resolving the sloped
        sill; it is not one. Undecidable is not refused, and the Charleston single house
        really is built both ways -- the sill rule is right for its frame half."""
        g = RK.load_graph()
        kit, _ = RK.resolve_slots(g, RK.chain_for(g, "charleston-georgian"),
                                  RK.scope_for(g, "charleston-georgian"))
        verdict, _why = CV.resolve("mass-wall", kit)
        self.assertEqual("undecidable", verdict)

    def test_the_scope_survives_a_child_rebinding_the_pack_unscoped(self):
        """`jeffersonian-classicism` re-binds `sash-light` with no scope, so
        `resolve_packs`' nearest-first rule discards `tidewater-georgian`'s `slots_except`
        and the 2.25 in sloped sill arrived anyway (OQ 88's second delivery path). A scope
        on the RULE cannot be shadowed by a binding."""
        g = RK.load_graph()
        chain = RK.chain_for(g, "jeffersonian-classicism")
        kit, _ = RK.resolve_slots(g, chain, RK.scope_for(g, "jeffersonian-classicism"))
        dropped = []
        by_slot, _e = RK.eval_packs(RK.resolve_packs(g, chain),
                                    {"ceiling_height": 108.0}, None, kit, dropped)
        rows = [r for r in by_slot.get("window_sill", [])
                if r["pack"] == "sash-light" and r.get("dimension") == "projection"]
        self.assertEqual([], rows, "the sloped timber sill reaches this brick node again")
        self.assertTrue([d for d in dropped
                         if d["pack"] == "sash-light" and d["slot"] == "window_sill"],
                        "it was withheld with no reason recorded, which is the silent drop "
                        "this corpus polices hardest")

    def test_the_classifier_the_vocabulary_replaced_is_gone(self):
        """`construction_of()` and `MASONRY_WORDS` classified a node by SUBSTRING MATCH over
        its cladding ids. A substring test over a surface cannot answer a question about an
        assembly: `cape-dutch` is sun-dried brick with timber frame FORBIDDEN and its
        `lime-plaster-limewash-white` face carries no masonry word, so the frame-wall sill
        rule was delivered to a mass masonry wall -- OQ 88's own bug surviving inside OQ 88's
        fix. Source-read on purpose: this asserts the second reading is gone, not that some
        caller happens not to use it."""
        src = open(os.path.join(ROOT, "build", "proportion_engine.py"), encoding="utf-8").read()
        body = src[src.index("def rule_scope("):]
        self.assertNotIn("MASONRY_WORDS", body)
        self.assertNotIn("construction_of(", body)
        # THE POSITIVE HALF USED TO BE SATISFIED BY A DEFINITION. `assertIn(
        # "_construction_vocabulary()", body)` matched the helper's own
        # `def _construction_vocabulary():` line whenever that def sorted after `rule_scope`
        # in the file, so moving the helper below and calling a differently-named classifier
        # from inside `rule_scope` passed all three assertions. Strip every `def` line out of
        # the slice before looking for a CALL.
        calls = "\n".join(ln for ln in body.split("\n") if not ln.lstrip().startswith("def "))
        self.assertIn("_construction_vocabulary()", calls,
                      "rule_scope does not CALL the vocabulary -- the only match was a "
                      "definition, which is what this assertion used to accept")

    def test_every_scoped_rule_uses_a_token_the_vocabulary_defines(self):
        for d in ("proportions/modules", "proportions/systems"):
            for name in sorted(os.listdir(os.path.join(ROOT, d))):
                if not name.endswith(".json"):
                    continue
                with open(os.path.join(ROOT, d, name), encoding="utf-8") as fh:
                    pack = json.load(fh)
                for r in (pack.get("derived_rules") or []):
                    aw = r.get("scope") or {}
                    for key in ("construction",):
                        for token in (aw.get(key) or []):
                            self.assertIn(token, set(CV.VOCABULARY) | set(CV.UNMAPPABLE),
                                          "%s: %s names %r, which the vocabulary does not "
                                          "define" % (pack["id"], key, token))




class TestTheElevationReadsTheCascade(unittest.TestCase):
    """WP-8.4's OQ 89 remainder: two slots in `build/elevation.py` still read the RAW kit.

    The comment above them named the problem and did not reach them -- *"the CASCADED dormer
    slot, not the raw one. `tidewater-georgian` binds this slot EMPTY -- **exactly as it binds
    `shutter`**"* -- and then read `shutter` off `C["kits"]` two lines below. WP-6.4's disease
    in the commit that cured it next door.
    """

    def test_the_shutter_and_head_slots_come_from_the_resolved_kit(self):
        src = open(os.path.join(ROOT, "build", "elevation.py"), encoding="utf-8").read()
        block = src[src.index("_slots, _ = RK.resolve_slots"):src.index("head_variants = ")]
        for slot in ("shutter", "window_head_masonry"):
            self.assertIn('_slots.get("%s")' % slot, block,
                          "%s is read from somewhere other than the resolved kit" % slot)
        self.assertNotIn('C["kits"].get(style) or {}).get("slots", {}) or {}).get("shutter")',
                         src, "the raw-kit read of `shutter` is back")
        # THE SAME NEGATIVE FOR THE HEAD SLOT, which had only the positive half. Overwriting
        # `head_slot` with the raw-kit read on the line AFTER the resolved one satisfied
        # `assertIn` and reverted the behaviour, and the only test that noticed was the
        # SHUTTER one above -- by coupling, because a missing head radius moves a different
        # fault out of `not_applicable`. A guard that fires through a neighbour stops firing
        # the moment the neighbour changes.
        self.assertNotIn(
            'C["kits"].get(style) or {}).get("slots", {}) or {}).get("window_head_masonry")',
            src, "the raw-kit read of `window_head_masonry` is back")

    def test_a_style_whose_cascade_declines_shutters_states_a_measured_zero(self):
        """`jeffersonian-classicism` is the one node where the two records disagree: its own
        kit file says nothing about shutters and its CASCADE makes `none` canonical. Read raw,
        the generator supplied a real 2.0/2.0 and
        `shutter-on-an-unshutterable-opening` came back CLEAR on two shutters the style
        declines -- OQ 89's own defect, surviving on one node because of which record was
        read."""
        el = _mod("elevation", "build/elevation.py")
        plan = json.load(open(os.path.join(ROOT, "plans",
                                           "tidewater-georgian-careful.json"), encoding="utf-8"))
        plan = dict(plan)
        plan["style"] = "jeffersonian-classicism"
        meas = el.build_elevation(plan)["measurements"]
        self.assertEqual(0.0, meas.get("total_shutter_leaves"),
                         "a style whose resolved kit makes `none` canonical is supplying "
                         "shutter leaves again")
        r = CORE.check_measurements(meas, style="jeffersonian-classicism", limit=10 ** 6)
        clear = {x["fault"] for x in r["faults_clear"]}
        na = {x["fault"] for x in r["not_applicable"]}
        self.assertNotIn("shutter-on-an-unshutterable-opening", clear,
                         "the fault is CLEAR on shutters this style declines")
        self.assertIn("shutter-on-an-unshutterable-opening", na)

    def test_the_head_specification_reaches_two_thirds_of_the_corpus(self):
        """`window_head_masonry` is EMPTY in the raw kit and populated by the cascade on 66 of
        164 styles, so `_head_radius_in` was reading no head specification at all on most of
        them. Measured: 8 styles could state a head radius before, 29 after."""
        # A CORPUS RATCHET OVER kits/, and it says so rather than importing a generator it
        # never calls -- this used to bind build/elevation.py to a name it never touched,
        # which reads as "this exercises the generator" and does not.
        RKm = RK
        g = RKm.load_graph()
        raw_empty = cascade_has = 0
        for nid in sorted(g["nodes"]):
            path = os.path.join(ROOT, "kits", "%s.kit.json" % nid)
            if not os.path.exists(path):
                continue
            raw = json.load(open(path, encoding="utf-8")).get("slots") or {}
            cas, _ = RKm.resolve_slots(g, RKm.chain_for(g, nid), RKm.scope_for(g, nid))
            r = (raw.get("window_head_masonry") or {}).get("variants") or []
            c = (cas.get("window_head_masonry") or {}).get("variants") or []
            if not r and c:
                raw_empty += 1
            if c:
                cascade_has += 1
        self.assertGreaterEqual(raw_empty, 60,
                                "the raw kit and the cascade have stopped disagreeing about "
                                "window_head_masonry; re-pin this or delete it")
        self.assertGreater(cascade_has, raw_empty)




class TestTheDivisionGuardReadsWholeDenominators(unittest.TestCase):
    """`check_division_guards` exists to find unguarded divisions. Its first denominator
    reader was `/\\s*([A-Za-z_][A-Za-z0-9_]*)` and could not see a PARENTHESISED denominator --
    an unguarded division invisible to the thing built to find unguarded divisions. Found by
    the WP-8.4 adversarial audit."""

    def setUp(self):
        self.m = _mod("check_division_guards", "build/check_division_guards.py")

    def test_a_parenthesised_denominator_is_read(self):
        got = self.m.denominators("door_leaf_width_in / (storey_height_in / 3.5)")
        self.assertEqual({"storey_height_in"}, got)

    def test_a_literal_denominator_yields_no_name(self):
        """`x / 2` is genuinely safe and must not be reported -- a checker that cries wolf
        gets turned off within a day, which is this codebase's own load.py lesson."""
        self.assertEqual(set(), self.m.denominators("coating_water_vapour_permeance_perms / 10"))
        self.assertEqual(set(), self.m.denominators("exterior_openings_on_the_passage_axis / 2"))

    def test_a_denominator_it_cannot_read_is_named_rather_than_dropped(self):
        """The docstring promised this and `main()` had no such branch.

        A denominator the walker cannot attribute is a test the LIVE meter cannot see, so
        dropping it silently makes an unguarded division invisible forever -- unjudged
        collapsed into a pass, inside the checker written to stop exactly that. Neither form
        occurs in the corpus (0 of 326 dividing expressions), so the reporter is exercised on
        constructed input, which is the only way a prospective guard can be tested at all.
        """
        self.assertEqual({"max"}, self.m.denominators("a / max(b, 1)"),
                         "the walker now reads a call -- if so, delete the reporter rather "
                         "than leaving it as a claim about a case that no longer exists")
        self.assertEqual(set(), self.m.denominators("a / -b"))
        real = self.m.dividing_tests

        def fake():
            return [("a-fake-fault", "test", "x / max(bay_count, 1)", {"max"}),
                    ("another-fake", "secondary_tests[0]", "y / -dormer_count", set())]
        self.m.dividing_tests = fake
        try:
            found = self.m.unattributable_denominators()
        finally:
            self.m.dividing_tests = real
        whys = " ".join(w for _f, _w, _e, w in found)
        self.assertIn("a call", whys)
        self.assertIn("a unary minus", whys)

    def test_the_corpus_has_no_unattributable_denominator_today(self):
        self.assertEqual([], self.m.unattributable_denominators())

    def test_a_compound_denominator_yields_every_name_in_it(self):
        self.assertEqual({"c", "d"}, self.m.denominators("(a+b) / (c*d)"))
        self.assertEqual({"b", "c"}, self.m.denominators("a/b/c"))

    def test_the_corpus_has_a_case_the_old_reader_missed(self):
        """Without a live instance this fix is untested by the corpus itself."""
        import re as _re
        old = _re.compile(r"/\s*([A-Za-z_][A-Za-z0-9_]*)")
        missed = [t for _f, _w, e, _n in self.m.dividing_tests()
                  for t in [e] if "/" in e and not old.search(e) and self.m.denominators(e)]
        self.assertTrue(missed, "no expression in the corpus distinguishes the two readers, so "
                                "this fix is unexercised -- re-pin or delete this test")

    def test_the_live_hazard_is_still_zero(self):
        """The figure that matters. It goes non-zero when a generator starts supplying a new
        zero (which is what WP-5.13 did, convicting two houses) or an unguarded test starts
        dividing by one that already exists.

        THIS USED TO READ `self.m.LIVE_RATCHET` -- the module's own pinned literal -- which
        is a constant only a human edit can move. Adding an unguarded `x / dormer_count`
        secondary to a fault made `check_division_guards.py` print "RATCHET BROKEN — live
        divisions by a supplied zero: 0 -> 1" and return 1, and this class stayed green:
        the test never took the measurement it is named for. That is the defect this whole
        corpus is written against, inside the test that guards it. It measures now.
        """
        live, unguarded, composed, _zeros = self.m.live_hazards()
        self.assertTrue(composed, "no style composed an elevation -- COULD NOT EVALUATE, "
                                  "which this assertion must not read as a pass")
        self.assertTrue(unguarded, "the unguarded population is empty, so an empty `live` "
                                   "proves nothing")
        self.assertEqual([], list(live), (
            "a fault test divides by a name a generator supplies as zero, unguarded: %s"
            % (list(live)[:5],)))
        self.assertEqual(0, self.m.LIVE_RATCHET,
                         "the pin and the measurement have drifted apart")


class TestTheAuthorityWalkAfterTheAudit(unittest.TestCase):
    """Three defects the WP-8.4 adversarial audit found in `resolve()`, each pinned.

    All three shared a shape: a rule that was right for the case it was written against and
    wrong one case over, with no test exercising the second case."""

    @classmethod
    def setUpClass(cls):
        cls.g = RK.load_graph()
        cls.kits = {}

    def kit(self, nid):
        if nid not in self.kits:
            self.kits[nid] = RK.resolve_slots(self.g, RK.chain_for(self.g, nid),
                                              RK.scope_for(self.g, nid))[0]
        return self.kits[nid]

    def test_a_declared_value_does_not_short_circuit_the_authority_order(self):
        """Telling the resolver MORE about the house must never make it answer WRONG.

        The first version returned from whichever of the token's slots the caller happened
        to name, so declaring only a cladding gave a hard `fails` for a token the style's
        own construction_type answers `holds`."""
        kit = self.kit("new-england-colonial")          # canonically braced-timber-frame
        self.assertEqual("holds", CV.resolve("wood-frame", kit)[0])
        self.assertEqual("holds", CV.resolve("wood-frame", kit,
                                             {"primary_cladding": "smooth-stucco"})[0],
                         "a declared LOW-authority slot overturned the decisive one")
        self.assertEqual("fails", CV.resolve("wood-frame", kit,
                                             {"construction_type": "adobe"})[0],
                         "a declared HIGH-authority slot stopped deciding")

    def test_a_partial_token_cannot_hold_on_the_declared_path_either(self):
        """`test_a_partial_token_can_never_hold` swept nodes with no `declared`, so it never
        reached this branch -- and the branch returned `holds`."""
        kit = self.kit("new-england-colonial")
        partial = [t for t, v in CV.VOCABULARY.items() if v["strength"] == "partial"]
        self.assertTrue(partial)
        for token in partial:
            for sid, wanted in CV.VOCABULARY[token]["slots"].items():
                if not wanted:
                    continue
                v, _w = CV.resolve(token, kit, {sid: wanted[0]})
                self.assertNotEqual("holds", v,
                                    "%s held via a declared %s" % (token, sid))

    def test_a_lower_slot_cannot_overturn_a_canonically_both_answer(self):
        """`prairie-school` is canonically `roman-brick` AND `stucco-with-wood-banding`. That
        is a firm answer -- the style is both -- and its `platform-frame` construction_type
        must not turn it into `fails` for `brick` on a Roman-brick house."""
        self.assertEqual("undecidable", CV.resolve("brick", self.kit("prairie-school"))[0])
        self.assertEqual("undecidable", CV.resolve("wood-frame",
                                                   self.kit("charleston-georgian"))[0])

    def test_a_slot_with_no_canonical_still_defers_to_the_next(self):
        """The other half, and the two must not be conflated. `jeffersonian-classicism`
        inherits a construction_type where EVERY variant is merely permitted -- no firm
        opinion -- and its own cladding is canonically Flemish-bond brick with clapboard
        forbidden. That cladding is the answer."""
        self.assertEqual("fails", CV.resolve("wood-frame",
                                             self.kit("jeffersonian-classicism"))[0])

    # TWO FIXES, ONE BUG, AND THE SECOND WAS FOUND BY LOOKING FOR THE FIRST'S SIBLING.
    # `solid-masonry-two-wythe` says how many wythes and nothing about the material, so a
    # material question decided by it is decided by evidence that has no opinion. `brick`
    # answered `holds` on granite `scottish-baronial` until the neutral variants came out of
    # its list AND `primary_cladding` was put first; `stone-rubble` then answered `fails` on
    # THE SAME NODE -- canonically `squared-rubble-granite-ashlar-harled-rubble` on the face,
    # printed in its own refusal detail -- until it got the same ordering. Two tokens now
    # lead with the cladding and four with the assembly, each for a reason in its own entry.
    # The general form is `oq/a-material-neutral-assembly-decides-a-material-question`.
    MATERIAL_TOKENS_READ_THE_FACE_FIRST = ("brick", "stone-rubble")

    def test_a_material_token_reads_the_face_before_the_assembly(self):
        """THE ORDERING IS WHAT DOES THE WORK, and only the ordering is asserted here.

        The first version of this test asserted the two neutral variants were absent from
        `brick`'s list and then checked two verdicts. Putting the variants BACK left both
        verdicts unchanged -- because the cladding now leads and decides first -- so the two
        behavioural lines read as proof and proved nothing about the mechanism. Assert the
        thing that would actually break.
        """
        for token in self.MATERIAL_TOKENS_READ_THE_FACE_FIRST:
            order = list(CV.VOCABULARY[token]["slots"])
            self.assertEqual("primary_cladding", order[0], (
                "%s is a MATERIAL question and the corpus records material in the face; "
                "with the assembly first, a material-neutral canonical decides it" % token))

    def test_the_material_ordering_is_what_produces_the_verdicts(self):
        """The behavioural half, made to depend on the ordering by swapping it here."""
        cases = [("brick", "scottish-baronial", "fails"),
                 ("brick", "tidewater-georgian", "holds"),
                 ("stone-rubble", "scottish-baronial", "holds"),
                 ("stone-rubble", "tidewater-georgian", "fails")]
        for token, style, want in cases:
            self.assertEqual(want, CV.resolve(token, self.kit(style))[0],
                             "%s on %s" % (token, style))
        # Now swap the slot order back and prove at least one verdict depends on it -- an
        # assertion that survives its own mechanism being reversed is not a behavioural test.
        moved = []
        for token in self.MATERIAL_TOKENS_READ_THE_FACE_FIRST:
            slots = CV.VOCABULARY[token]["slots"]
            CV.VOCABULARY[token] = dict(CV.VOCABULARY[token],
                                        slots={k: slots[k] for k in reversed(list(slots))})
        try:
            for token, style, want in cases:
                if CV.resolve(token, self.kit(style))[0] != want:
                    moved.append((token, style))
        finally:
            for token in self.MATERIAL_TOKENS_READ_THE_FACE_FIRST:
                slots = CV.VOCABULARY[token]["slots"]
                CV.VOCABULARY[token] = dict(CV.VOCABULARY[token],
                                            slots={k: slots[k] for k in reversed(list(slots))})
        self.assertTrue(moved, "reversing the slot order changed no verdict, so these cases "
                               "do not exercise the ordering they are written for")
        for token in self.MATERIAL_TOKENS_READ_THE_FACE_FIRST:   # restoration held
            self.assertEqual("primary_cladding", list(CV.VOCABULARY[token]["slots"])[0])

    def test_corpus_tokens_refuses_to_return_nothing(self):
        """It read `exceptions[].applies_when` after WP-8.4 renamed the field, so it returned
        an EMPTY Counter and every caller passed vacuously -- inside the suite written to
        guard the table."""
        used = CV.corpus_tokens()
        self.assertGreater(len(used), 50)
        self.assertGreater(sum(used.values()), 200)

    def test_a_token_list_is_resolved_as_a_disjunction(self):
        """`paint-on-unpainted-brick`'s `english-cottage-vernacular` licence names
        `[solid-masonry-two-wythe, adobe, rammed-earth]`, and that style is canonically `cob`
        AND `clay-lump`: each token alone says "both ways, cannot decide" while the wall is
        CERTAINLY one of the three the licence names. Reducing each token to a verdict and
        then combining is right at the ends and wrong in the middle."""
        g = RK.load_graph()
        kit, _ = RK.resolve_slots(g, RK.chain_for(g, "english-cottage-vernacular"),
                                  RK.scope_for(g, "english-cottage-vernacular"))
        toks = ["solid-masonry-two-wythe", "adobe", "rammed-earth"]
        self.assertEqual(set(), {CV.resolve(t, kit)[0] for t in toks} & {"holds"},
                         "no single token holds -- if one does, this test no longer "
                         "exercises the union and must be re-pinned")
        self.assertEqual("holds", CV.resolve_any(toks, kit)[0])
        D = CORE._data()
        exc = next(e for e in D["faults"]["paint-on-unpainted-brick"]["exceptions"]
                   if e["style"] == "english-cottage-vernacular")
        self.assertEqual("granted", CORE.grant_exception(exc, "english-cottage-vernacular")["verdict"])

    def test_the_union_will_not_confirm_through_a_partial_token(self):
        """The rule stated directly, on a record built to distinguish the two readings.

        THE FIRST VERSION OF THIS TEST PROVED NOTHING, and the audit that found it is worth
        recording. It used `mediterranean-revival`, where `mass-wall` already resolves a
        hard `fails` on `construction_type`, so the union is decided before any cladding is
        consulted and `resolve_any` returns None whether or not the partial was folded in.
        Deleting the exclusion left the whole file green.

        There is no corpus witness. Swept over every licence naming a partial token
        alongside two others: the exclusion changes NO verdict anywhere in the corpus today
        -- measured both ways, byte-identical. So the rule is PROSPECTIVE, and a test of a
        prospective rule has to construct its own case rather than wait for one. This builds
        a resolved-slot record where the exact token cannot decide (a construction_type with
        only permitted variants, which defers) and the partial one would carry it (a
        canonical stucco cladding), and asserts the union still refuses to confirm.

        The corpus inertness is asserted too, in the test below, because "this rule does
        nothing today" is a fact a future author needs and a docstring will not keep.
        """
        record = {
            "construction_type": {"binding": "specified", "variants": [
                {"id": "solid-masonry-two-wythe", "status": "permitted"}]},
            "primary_cladding": {"binding": "specified", "variants": [
                {"id": "smooth-stucco", "status": "canonical"}]},
        }
        # Neither token can decide alone: the exact one because the slot states no canonical,
        # the partial one because a `partial` token may fail but may never confirm.
        self.assertEqual("undecidable", CV.resolve("mass-wall", record)[0])
        self.assertEqual("undecidable", CV.resolve("thick-stucco", record)[0])

        # THE UNION WITH THE PARTIAL FOLDED IN WOULD HOLD. Built here rather than asserted,
        # so the difference the exclusion makes is visible in the test itself -- without
        # this the assertion below passes on any `resolve_any` that returns None.
        merged = {}
        for t in ("mass-wall", "thick-stucco"):
            for sid, wanted in CV.VOCABULARY[t]["slots"].items():
                merged.setdefault(sid, [])
                merged[sid].extend(w for w in wanted if w not in merged[sid])
        CV.VOCABULARY["__audit_union__"] = {"slots": merged, "strength": "exact", "note": "x"}
        try:
            permissive = CV.resolve("__audit_union__", record)
        finally:
            CV.VOCABULARY.pop("__audit_union__", None)
        self.assertEqual("holds", permissive[0],
                         "the witness does not distinguish the two readings any more")

        self.assertIsNone(CV.resolve_any(["mass-wall", "thick-stucco"], record),
                          "the union confirmed through a partial token, laundering the "
                          "qualifier `thick-stucco` exists to preserve")

        # And two EXACT tokens over a record they jointly cover DO combine, so the assertion
        # above is not passing on a `resolve_any` that never returns anything at all.
        both = {"construction_type": {"binding": "specified", "variants": [
            {"id": "cob", "status": "canonical"}, {"id": "clay-lump", "status": "canonical"}]}}
        self.assertIsNotNone(CV.resolve_any(["adobe", "rammed-earth"], both))

    def test_the_partial_exclusion_is_inert_on_todays_corpus_and_says_so(self):
        """Measured, not assumed. If this starts failing, the exclusion has begun to bite:
        re-measure it, say which licences moved, and re-pin -- do not delete the guard."""
        g = RK.load_graph()
        D = CORE._data()
        biting = []
        for fid, fault in D["faults"].items():
            for exc in fault.get("exceptions", []):
                toks = (exc.get("granted_when") or {}).get("construction") or []
                style = exc.get("style")
                if not style or len(toks) < 2:
                    continue
                if not any(CV.VOCABULARY.get(t, {}).get("strength") == "partial"
                           for t in toks):
                    continue
                kit, _ = RK.resolve_slots(g, RK.chain_for(g, style), RK.scope_for(g, style))
                strict = CV.resolve_any(toks, kit)
                loose = CV.resolve_any([t for t in toks
                                        if CV.VOCABULARY.get(t, {}).get("strength")
                                        == "exact"] + ["__forced__"], kit) \
                    if False else None      # placeholder; the real comparison is below
                del loose
                merged = {}
                for t in toks:
                    for sid, wanted in CV.VOCABULARY.get(t, {}).get("slots", {}).items():
                        merged.setdefault(sid, [])
                        merged[sid].extend(w for w in wanted if w not in merged[sid])
                CV.VOCABULARY["__audit_union__"] = {"slots": merged, "strength": "exact",
                                                    "note": "partials folded in"}
                try:
                    permissive = CV.resolve("__audit_union__", kit)[0] == "holds"
                finally:
                    CV.VOCABULARY.pop("__audit_union__", None)
                if permissive != (strict is not None):
                    biting.append((fid, style, tuple(toks)))
        self.assertEqual([], biting, (
            "the partial-token exclusion now changes a verdict; it was inert when written. "
            "Re-measure and re-state rather than deleting it: %s" % (biting,)))


class TestALicenceIsNotRefusedOnTheStyleItWasWrittenFor(unittest.TestCase):
    """An exception names a style. Refusing it on THAT style is at least suspicious.

    Evaluating `granted_when.construction` for the first time convicts houses that were
    previously excused, and the WP-8.4 ruling says to work every new conviction as a
    candidate DATA error before accepting it. This is that check, as a standing one.

    Swept over every exception carrying a construction precondition, evaluated against the
    style in its own `style` key: 19 are refused. Seventeen of those are SUBSTANTIVE and
    correct -- `pueblo-revival` is canonically `stucco-over-wood-frame`, its own diagnostic
    tell reading "the revival often achieves the look in 2 in. of stucco over frame", so an
    adobe licence genuinely does not hold on it. That is the whole package working.

    The two that were NOT substantive are the ones this class exists to keep at zero, and
    they share a shape: the condition names an EXACT variant token as a stand-in for a
    class, and the style is canonically a DIFFERENT MEMBER OF THAT SAME CLASS.
    `water-table-that-follows-the-grade`'s Cotswold licence required
    `solid-masonry-two/three-wythe` on a node canonically `rubble`, while its own bounds read
    "the one place this reads as licence rather than error is where the wall itself is
    RUBBLE"; `quoin-by-catalogue`'s Baronial licence required `solid-masonry-three-wythe` on
    a node canonically two-wythe, while its own why reads "RUBBLE WALLING with dressed ashlar
    corner dressings". Both are licences refused for being exactly the thing they describe.

    The discriminator is mechanical, which is why it can be a test: a refusal is suspect
    when some BROADER vocabulary token -- one whose variant list for that slot contains the
    named token's -- would HOLD on the same style. It is substantive when none does.
    """

    @classmethod
    def setUpClass(cls):
        cls.g = RK.load_graph()
        cls.broad = [t for t, v in CV.VOCABULARY.items()
                     if len(v.get("slots", {}).get("construction_type", [])) >= 3]

    def _suspects(self):
        D = CORE._data()
        out = []
        for fid, fault in sorted(D["faults"].items()):
            for exc in fault.get("exceptions", []):
                named = (exc.get("granted_when") or {}).get("construction")
                style = exc.get("style")
                if not named or not style:
                    continue
                if CORE.grant_exception(exc, style)["verdict"] != "refused":
                    continue
                kit, _ = RK.resolve_slots(self.g, RK.chain_for(self.g, style),
                                          RK.scope_for(self.g, style))
                for b in self.broad:
                    bv = set(CV.VOCABULARY[b]["slots"].get("construction_type", []))
                    # A token with NO construction_type variants is a different axis
                    # entirely -- `casement` is a window, `detached-outbuilding` a garage --
                    # and an empty set is a subset of everything, which made the first
                    # version of this sweep "rescue" both of them vacuously.
                    containing = [n for n in named
                                  if set(CV.VOCABULARY.get(n, {})
                                         .get("slots", {}).get("construction_type", []))
                                  and set(CV.VOCABULARY[n]["slots"]["construction_type"]) <= bv]
                    if containing and CV.resolve(b, kit)[0] == "holds":
                        out.append((fid, style, tuple(named), b))
                        break
        return out

    # ONE KNOWN, NAMED, AND DELIBERATELY NOT FIXED HERE. `porch-ceiling-of-exposed-joists`
    # gates its Craftsman licence on `construction: [timber-frame, heavy-timber]`, and a
    # Craftsman is canonically `platform-frame`, so the licence is refused on the style whose
    # exposed porch structure it exists to permit. But the condition is on the WRONG AXIS
    # rather than under-specified: its own `why` and `bounds` are about the MEMBERS -- "real
    # beams and rafters of full dimension, planed", "exposed 2x framing with joist hangers and
    # OSB is not this exception under any circumstances" -- which is a fact about the porch
    # roof, not about the wall assembly. Widening it to `wood-frame` would grant it to every
    # wood house and throw away the discrimination the licence is made of; the corpus has no
    # slot for a porch member's finish, and `construction_vocabulary`'s own rule is that an
    # agent needing a name the corpus lacks REPORTS the gap rather than inventing one.
    # Raised as `oq/a-licence-conditioned-on-the-wrong-axis`. Listed here so it cannot be
    # mistaken for a passing case and so nothing NEW may join it.
    KNOWN_WRONG_AXIS = {("porch-ceiling-of-exposed-joists", "craftsman")}

    def test_no_licence_is_refused_while_a_broader_token_containing_its_own_holds(self):
        suspects = [x for x in self._suspects() if (x[0], x[1]) not in self.KNOWN_WRONG_AXIS]
        still = {(x[0], x[1]) for x in self._suspects()} & self.KNOWN_WRONG_AXIS
        self.assertEqual(self.KNOWN_WRONG_AXIS, still, (
            "a named exemption stopped being reproducible -- if it was fixed, delete it from "
            "KNOWN_WRONG_AXIS in the same commit rather than leaving a permanent hole"))
        self.assertEqual([], suspects, (
            "these licences are refused on the style they name, and a broader token "
            "containing the one they name HOLDS on that style -- the condition is "
            "under-specified, not the style wrong: %s" % (suspects,)))

    def test_the_sweep_is_not_vacuous(self):
        """The assertion above is `== []`, which an empty population also satisfies.

        A selector matching nothing passes; this corpus has been caught by that form
        before. So pin the population it walks and the substantive refusals it must NOT
        rescue -- if either goes to zero the test above has stopped meaning anything.
        """
        D = CORE._data()
        with_construction = [
            (fid, e) for fid, f in D["faults"].items() for e in f.get("exceptions", [])
            if (e.get("granted_when") or {}).get("construction") and e.get("style")]
        self.assertGreaterEqual(len(with_construction), 100,
                                "the construction preconditions have gone; nothing is swept")
        refused = [(fid, e["style"]) for fid, e in with_construction
                   if CORE.grant_exception(e, e["style"])["verdict"] == "refused"]
        self.assertGreaterEqual(len(refused), 10, (
            "no licence is refused on its own style any more -- either the corpus was "
            "fixed (re-pin this) or the evaluator stopped refusing (a defect)"))
        self.assertIn(("architrave-that-is-not-there", "pueblo-revival"), refused,
                      "the flagship substantive refusal is gone; the evaluator has changed")



if __name__ == "__main__":
    unittest.main()
