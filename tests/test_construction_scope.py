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
    "unjudged": 57,                    # preconditions the corpus cannot resolve from a style
    "unevaluated_regions": 79,         # the key no gazetteer exists for
    "unevaluated_date_range": 102,     # decidable only where a caller supplies a date
    "bounds_test_unjudged": 47,        # of those, the ones that would replace a primary test
}
CENSUS_FLOOR = {            # may only RISE
    "with_granted_when": 331,
    "construction": 123,
    "granted": 46,
    "refused": 20,
}
UNMAPPABLE_CEILING = 17     # tokens the corpus records nothing for
# (pack, slot, dimension) -> deliveries the OQ 88 scope drops as out of scope. Floors.
# Re-measured 28 Aug 2026 after the vocabulary was ported into `proportion_engine.rule_scope`
# in place of `construction_of`'s substring test over the cladding.
SCOPE_FLOOR = {
    ("sash-light", "window_sill", "projection"): 28,
    ("opening-proportion", "window_surround_wood", "exterior_head_assembly_height"): 60,
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
        """Judged both ways. Where the exception's bounds_test and the general rule agree,
        the unresolved question is immaterial and reporting could-not-evaluate would be a
        fake unjudged -- as dishonest in its own direction as a fake pass. Measured over
        164 styles this is the difference between 26 verdicts moving and 11."""
        src = open(os.path.join(ROOT, "mcp_server", "core.py"), encoding="utf-8").read()
        self.assertIn("under_the_general_rule", src)
        self.assertIn("exception_unjudged_but_immaterial", src)

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
            for sid, rows in by_slot.items():
                for r in rows:
                    key = (r["pack"], sid, r.get("dimension"))
                    if key in SCOPE_FLOOR:
                        cls.delivered[key] += 1
                        if r.get("scope_unjudged"):
                            cls.unjudged[key] += 1

    def test_each_scope_refuses_at_least_what_it_refused_when_it_was_written(self):
        for key, floor in SCOPE_FLOOR.items():
            self.assertGreaterEqual(
                self.refused[key], floor,
                "%s/%s/%s refuses %d deliveries against a floor of %d. A scope that stops "
                "refusing reports success: `applies_when` was dropped inside "
                "proportion_engine.evaluate() and refused 0 of 293 with every check green."
                % (key + (self.refused[key], floor)))

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
        self.assertIn("_construction_vocabulary()", body)

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


if __name__ == "__main__":
    unittest.main()


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
        RKm, el = RK, _mod("elevation", "build/elevation.py")
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
