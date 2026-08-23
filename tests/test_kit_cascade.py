"""Pins the kit-of-parts cascade — see docs/inheritance.md.

The central finding: 'the cascade has been proved two levels deep, not
twenty' (open question 20), and specifically that converting Georgian's chain
to a genuine three-level cascade (tidewater-georgian -> georgian-colonial-
american -> english-georgian) only pays off where the middle layer `extends`
rather than restates — a fully-specified child makes its ancestors dead
weight. These tests pin that the three-level chain still resolves with all
three levels actually contributing, and that check_kits.py still catches the
dangling-replace failure mode that exercise found.
"""
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestThreeLevelCascade:
    def test_tidewater_chain_starts_with_all_three_populated_kits(self, resolve_kit_module):
        graph = resolve_kit_module.load_graph()
        chain = resolve_kit_module.chain_for(graph, "tidewater-georgian")
        assert chain[:3] == ["tidewater-georgian", "georgian-colonial-american", "english-georgian"]

    def test_all_three_levels_contribute_bindings(self, resolve_kit_module):
        """This is the '0% from the family kit is dead weight' check inverted:
        every one of the three populated kits in the chain must actually
        contribute at least one binding, or the cascade isn't paying for
        itself at that level."""
        for style_id in ("tidewater-georgian", "georgian-colonial-american", "english-georgian"):
            kit_path = os.path.join(ROOT, "kits", f"{style_id}.kit.json")
            kit = json.load(open(kit_path))
            non_open = sum(1 for s in kit["slots"].values() if s.get("binding") != "open")
            assert non_open > 0, f"{style_id} contributes nothing to the cascade"


class TestRuleAppend:
    """OQ 16: `rule_append` was declared in the kit schema at 0.2.1 and
    already used in data (georgian-colonial-american.kit.json's roof_pitch
    and door_surround slots, against english-georgian) well before
    resolve_kit.py had any code path that read it. WP-1.3 wired the merge in
    -- these tests pin the real roof_pitch case, not a synthetic fixture."""

    def test_roof_pitch_rule_is_own_rule_plus_appended_clause(self, resolve_kit_module):
        """georgian-colonial-american's roof_pitch delta unusually sets both a
        full `rule` replacement AND a `rule_append` on the same delta -- the
        replacement (which discards english-georgian's own rule text
        entirely, per MERGE_REPLACE) happens first, then rule_append joins
        onto that replacement, not onto the discarded ancestor text."""
        graph = resolve_kit_module.load_graph()
        chain = resolve_kit_module.chain_for(graph, "georgian-colonial-american")
        slots, _ = resolve_kit_module.resolve_slots(graph, chain)
        rec = slots["roof_pitch"]
        own_replacement = resolve_kit_module.load_kit(
            "georgian-colonial-american")["roof_pitch"]["rule"]
        english_georgian_rule = resolve_kit_module.load_kit("english-georgian")["roof_pitch"]["rule"]
        assert rec["rule"].startswith(own_replacement)
        assert "Colonial roofs run a course steeper" in rec["rule"]
        assert english_georgian_rule not in rec["rule"]  # fully replaced, not inherited

    def test_roof_pitch_rule_append_is_provenanced(self, resolve_kit_module):
        graph = resolve_kit_module.load_graph()
        chain = resolve_kit_module.chain_for(graph, "georgian-colonial-american")
        slots, _ = resolve_kit_module.resolve_slots(graph, chain)
        rec = slots["roof_pitch"]
        joins = rec.get("_rule_append")
        assert joins and joins[0]["from"] == "georgian-colonial-american"
        assert joins[0]["appended"] == resolve_kit_module.load_kit(
            "georgian-colonial-american")["roof_pitch"]["rule_append"]

    def test_merge_extends_appends_onto_inherited_rule_directly(self, resolve_kit_module):
        """Unit-level check of the merge function itself, independent of which
        real kit files happen to use rule_append today."""
        base = {"binding": "specified", "rule": "The base sentence."}
        delta = {"rule_append": "An additional clause."}
        out, prov = resolve_kit_module.merge_extends(base, delta, "ancestor", "child")
        assert out["rule"] == "The base sentence. An additional clause."
        assert out["_rule_append"] == [
            {"from": "child", "appended": "An additional clause.", "joined_after": "The base sentence."}
        ]
        assert prov["rule_appended_from"] == "child"

    def test_merge_extends_rule_append_with_no_inherited_rule(self, resolve_kit_module):
        """No ancestor ever set a rule at all -- the appended clause becomes
        the whole rule rather than erroring or leaving a leading space."""
        base = {"binding": "specified"}
        delta = {"rule_append": "Only clause."}
        out, _ = resolve_kit_module.merge_extends(base, delta, "ancestor", "child")
        assert out["rule"] == "Only clause."


class TestDateConditionalResolution:
    """OQ 22: applies_when.date_range existed and was populated (49 dated
    variant records corpus-wide) but nothing selected on it -- a resolved
    kit had to present every option at once rather than what applies at a
    stated date. WP-1.3 added resolve_kit.py's --date parameter and the
    in_period()/filter_variants_by_date() functions it's built on."""

    def test_in_period_true_for_undated_variant_regardless_of_date(self, resolve_kit_module):
        assert resolve_kit_module.in_period({"id": "x"}, 1745) is True

    def test_in_period_respects_date_range_inclusive_bounds(self, resolve_kit_module):
        v = {"id": "x", "applies_when": {"date_range": [1700, 1750]}}
        assert resolve_kit_module.in_period(v, 1700) is True   # inclusive lower bound
        assert resolve_kit_module.in_period(v, 1750) is True   # inclusive upper bound
        assert resolve_kit_module.in_period(v, 1699) is False
        assert resolve_kit_module.in_period(v, 1751) is False

    def test_in_period_none_date_means_no_filtering(self, resolve_kit_module):
        v = {"id": "x", "applies_when": {"date_range": [1700, 1750]}}
        assert resolve_kit_module.in_period(v, None) is True

    def test_filter_never_silently_drops_the_excluded_variants(self, resolve_kit_module):
        variants = [
            {"id": "early", "applies_when": {"date_range": [1700, 1750]}},
            {"id": "late", "applies_when": {"date_range": [1750, 1800]}},
            {"id": "undated"},
        ]
        kept, dropped = resolve_kit_module.filter_variants_by_date(variants, 1745)
        assert {v["id"] for v in kept} == {"early", "undated"}
        assert {v["id"] for v in dropped} == {"late"}

    def test_tidewater_window_head_masonry_real_case_flips_across_1750(self, resolve_kit_module):
        """tidewater-georgian.window_head_masonry has segmental-gauged-arch
        (1700-1750) and gauged-flat-arch (1750-1800) -- the corpus's own
        example of the change of arch form around 1750 being a dating tell,
        not a taste choice (kits/tidewater-georgian.kit.json's own note)."""
        graph = resolve_kit_module.load_graph()
        chain = resolve_kit_module.chain_for(graph, "tidewater-georgian")
        slots, _ = resolve_kit_module.resolve_slots(graph, chain)
        variants = slots["window_head_masonry"]["variants"]

        kept_1745, dropped_1745 = resolve_kit_module.filter_variants_by_date(variants, 1745)
        assert "segmental-gauged-arch" in {v["id"] for v in kept_1745}
        assert "gauged-flat-arch" in {v["id"] for v in dropped_1745}

        kept_1780, dropped_1780 = resolve_kit_module.filter_variants_by_date(variants, 1780)
        assert "gauged-flat-arch" in {v["id"] for v in kept_1780}
        assert "segmental-gauged-arch" in {v["id"] for v in dropped_1780}


class TestCheckKitsCatchesDanglingReplace:
    def test_replace_targeting_undefined_id_is_an_error(self):
        """A one-character difference in a variant op's target id turns a
        `replace` into a silent `add` and duplicates a record — check_kits.py
        must error on this, not warn or pass. Round-trips a real kit file
        through a deliberately broken copy and restores it in a `finally`."""
        kit_path = os.path.join(ROOT, "kits", "tidewater-georgian.kit.json")
        backup = kit_path + ".bak-test"
        shutil.copy(kit_path, backup)
        try:
            kit = json.load(open(kit_path))
            found = False
            for slot in kit["slots"].values():
                for variant in slot.get("variants", []):
                    if variant.get("op") == "replace":
                        variant["id"] = variant["id"] + "-NONEXISTENT-TEST-ID"
                        found = True
                        break
                if found:
                    break
            assert found, "fixture assumption broken: no replace-op variant found to corrupt"
            json.dump(kit, open(kit_path, "w"), indent=1)

            proc = subprocess.run(
                ["python3", os.path.join(ROOT, "build", "check_kits.py"), "tidewater-georgian"],
                capture_output=True, text=True, cwd=ROOT,
            )
            assert "no ancestor" in proc.stdout, proc.stdout
            assert "ERROR" in proc.stdout.upper()
        finally:
            shutil.move(backup, kit_path)

        # confirm the restore actually worked and the corpus is clean again
        proc = subprocess.run(
            ["python3", os.path.join(ROOT, "build", "check_kits.py"), "tidewater-georgian"],
            capture_output=True, text=True, cwd=ROOT,
        )
        assert "ERROR" not in proc.stdout.upper()
