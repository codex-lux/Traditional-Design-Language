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
    "unjudged": 87,                    # preconditions the corpus cannot resolve from a style
    "unevaluated_regions": 79,         # the key no gazetteer exists for
    "unevaluated_date_range": 102,     # decidable only where a caller supplies a date
    "bounds_test_unjudged": 64,        # of those, the ones that would replace a primary test
}
CENSUS_FLOOR = {            # may only RISE
    "with_granted_when": 331,
    "construction": 123,
    "granted": 33,
    "refused": 3,
}
UNMAPPABLE_CEILING = 17     # tokens the corpus records nothing for
# (pack, slot, dimension) -> deliveries the OQ 88 scope refuses. Floors.
SCOPE_FLOOR = {
    ("sash-light", "window_sill", "projection"): 15,
    ("opening-proportion", "window_surround_wood", "exterior_head_assembly_height"): 36,
    ("facade-gable", "gable_treatment", "parapet_height"): 35,
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
        cls.reached = {k: 0 for k in SCOPE_FLOOR}
        for nid in sorted(g["nodes"]):
            chain = RK.chain_for(g, nid)
            kit, _ = RK.resolve_slots(g, chain, RK.scope_for(g, nid))
            by_slot, _e = RK.eval_packs(RK.resolve_packs(g, chain),
                                        {"ceiling_height": 108.0}, None, kit)
            for sid, rows in by_slot.items():
                for r in rows:
                    key = (r["pack"], sid, r.get("dimension"))
                    if key in SCOPE_FLOOR:
                        cls.reached[key] += 1
                        if r.get("refused_by_construction"):
                            cls.refused[key] += 1

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
            self.assertLess(self.refused[key], self.reached[key],
                            "%s/%s/%s refuses every one of its %d deliveries"
                            % (key + (self.reached[key],)))

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
        by_slot, _e = RK.eval_packs(RK.resolve_packs(g, chain),
                                    {"ceiling_height": 108.0}, None, kit)
        rows = [r for r in by_slot.get("window_sill", [])
                if r["pack"] == "sash-light" and r.get("dimension") == "projection"]
        self.assertEqual(1, len(rows))
        self.assertTrue(rows[0]["refused_by_construction"])

    def test_every_scoped_rule_uses_a_token_the_vocabulary_defines(self):
        for d in ("proportions/modules", "proportions/systems"):
            for name in sorted(os.listdir(os.path.join(ROOT, d))):
                if not name.endswith(".json"):
                    continue
                with open(os.path.join(ROOT, d, name), encoding="utf-8") as fh:
                    pack = json.load(fh)
                for r in (pack.get("derived_rules") or []):
                    aw = r.get("applies_when") or {}
                    for key in ("construction", "construction_except"):
                        for token in (aw.get(key) or []):
                            self.assertIn(token, set(CV.VOCABULARY) | set(CV.UNMAPPABLE),
                                          "%s: %s names %r, which the vocabulary does not "
                                          "define" % (pack["id"], key, token))


if __name__ == "__main__":
    unittest.main()
