"""Pins the kit-of-parts cascade — see docs/inheritance.md.

The central finding: 'the cascade has been proved two levels deep, not
twenty' (open question 20), and specifically that converting Georgian's chain
to a genuine three-level cascade (tidewater-georgian -> georgian-colonial-
american -> english-georgian) only pays off where the middle layer `extends`
rather than restates — a fully-specified child makes its ancestors dead
weight. These tests pin that the three-level chain still resolves with all
three levels actually contributing, and that check_kits.py still catches the
dangling-replace failure mode that exercise found.

UPDATED 23 Aug 2026 (WP-4.2, opening the kit-fill work): `build/build.py`'s
cascade computation now splices a style-rank ancestor's own family in
immediately after that ancestor, before its further lineage ancestors — the
mechanism OQ 20 named as unbuilt ('the full three-level test... has not run
yet because Phase 4's kit-fill is deliberately deferred'). Families carry no
lineage edges of their own (member_of is organisational, not descent), so
they could not previously appear in any `_cascade` at all; WP-4.2's own task
text ('27 family nodes... then 90 styles using extends against the family')
requires that they do. Concretely, tidewater-georgian's chain is now FOUR
populated levels, not three: its own kit, its parent style's kit
(georgian-colonial-american), that style's own family kit (american-
colonial), then english-georgian (a real lineage/descent ancestor from a
DIFFERENT family, english-classical, reached because georgian-colonial-
american descends from it directly — the two mechanisms, member_of family
and lineage descent, are independent and both real). This is additive, not a
regression: every previously-resolved slot value on all three pre-existing
populated kits is unchanged (diffed directly against a resolve_kit.py --json
snapshot taken immediately before this change landed) — the family entries
are new fallback candidates, currently empty until WP-4.2 authors them, that
do not preempt any binding a real ancestor already supplied.
"""
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestThreeLevelCascade:
    def test_tidewater_chain_starts_with_all_three_populated_kits(self, resolve_kit_module):
        """Chain order as of WP-4.2's family-cascade mechanism: own kit, parent
        style, that style's own family (american-colonial, currently empty
        but real and present), then english-georgian — a genuine lineage/
        descent ancestor from a different family, reached because
        georgian-colonial-american itself descends_from english-georgian
        directly. See this file's module docstring for the full mechanism."""
        graph = resolve_kit_module.load_graph()
        chain = resolve_kit_module.chain_for(graph, "tidewater-georgian")
        assert chain[:4] == ["tidewater-georgian", "georgian-colonial-american",
                              "american-colonial", "english-georgian"]

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


class TestFamilyCascade:
    """WP-4.2 (23 Aug 2026): family nodes now get a kit file, and participate
    in every member's cascade as the nearest, most-shared ancestor a style
    can `extends` against — the mechanism this whole work package depends
    on. See build/build.py's cascade_chain()/family_of() and this file's
    module docstring for the design."""

    def test_every_family_node_has_a_kit_file(self, resolve_kit_module):
        graph = resolve_kit_module.load_graph()
        families = [i for i, n in graph["nodes"].items() if n["rank"] == "family"]
        assert len(families) == 27
        for fam in families:
            path = os.path.join(ROOT, "kits", f"{fam}.kit.json")
            assert os.path.exists(path), f"{fam} has no kit file"

    def test_a_styles_own_family_is_the_first_cascade_entry(self, resolve_kit_module):
        """A style with no real lineage/descent ancestors of its own still
        reaches its family — family participation does not depend on the
        style also having a documented descends_from edge."""
        graph = resolve_kit_module.load_graph()
        chain = resolve_kit_module.chain_for(graph, "georgian-colonial-american")
        assert chain[1] == "american-colonial"

    def test_a_variants_cascade_reaches_its_family_through_its_parent_style(self, resolve_kit_module):
        """A variant's member_of points at its parent STYLE, not directly at
        the family — family_of() must walk through that style rather than
        stopping there, and the variant reaches the same family its parent
        style would (american-colonial), not the style itself a second time."""
        graph = resolve_kit_module.load_graph()
        chain = resolve_kit_module.chain_for(graph, "tidewater-georgian")
        assert chain.count("american-colonial") == 1
        assert chain.count("georgian-colonial-american") == 1

    def test_family_kit_regenerates_without_dropping_authored_content(self, resolve_kit_module):
        """build.py's kit-directory step preserves any already-authored slot
        content on a family kit exactly the way it always has for style/
        variant kits (the existing-content merge in build.py's step 1) —
        this just confirms family kits went through the same code path,
        not a separate, easier-to-drift one."""
        path = os.path.join(ROOT, "kits", "american-colonial.kit.json")
        kit = json.load(open(path))
        assert kit["style"] == "american-colonial"
        assert kit["ontology_version"] and kit["kit_version"]
        # 95 -> 96 on 24 Aug 2026 (OQ 46): `arch` joined the openings group at ontology 0.6.0.
        # 96 -> 97 on 25 Aug 2026 (OQ 47): `expressed_frame` joined the envelope group at 0.7.0.
        assert len(kit["slots"]) == 97


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


class TestScopedLineageEdges:
    """OQ 58, ruled 24 Aug 2026. A `hybridizes_with` edge drawn to carry one narrow aspect of a
    donor's practice transmitted that donor's ENTIRE kit, because the cascade could not partition
    a donor's bindings by which aspect the edge was drawn for. An edge may now name the slots it
    carries; an edge that names none carries everything, as it always did."""

    def test_an_unscoped_edge_still_carries_everything(self, resolve_kit_module):
        """The default must not change, or every kit in the corpus moves at once."""
        import json, os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        graph = json.load(open(os.path.join(root, "dist", "taxonomy.json")))
        scoped = [nid for nid, n in graph["nodes"].items() if n.get("_cascade_scope")]
        # Pinned at 2, not `< 10`. Seven units of slack in a number that is deliberately small.
        assert len(scoped) == 2, "scoping is deliberately incremental; most edges carry everything"

    def test_the_octagon_no_longer_takes_its_roof_from_italianate_dress(self, resolve_kit_module):
        """The worked case. `octagon-house hybridizes_with italianate-american` says in its own
        note that the octagon is a plan thesis with no ornamental vocabulary of its own and so
        wears Italianate dress. Unscoped, that edge also handed it roof_form, roof_pitch and
        height_proportion — and an octagon's roof is eight hips meeting at a point because its
        plan is eight-sided, not because Italianate builders did it that way."""
        import json, os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        graph = json.load(open(os.path.join(root, "dist", "taxonomy.json")))
        chain = resolve_kit_module.chain_for(graph, "octagon-house")
        scope = resolve_kit_module.scope_for(graph, "octagon-house")
        assert "italianate-american" in scope
        slots, _ = resolve_kit_module.resolve_slots(graph, chain, scope)
        for sid in ("roof_form", "roof_pitch", "height_proportion"):
            v = slots.get(sid)
            if v:
                assert v.get("_source") != "italianate-american", (
                    f"{sid} should no longer come from the dress edge")

    def test_a_scoped_edge_still_carries_what_it_was_drawn_for(self, resolve_kit_module):
        import json, os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        graph = json.load(open(os.path.join(root, "dist", "taxonomy.json")))
        chain = resolve_kit_module.chain_for(graph, "octagon-house")
        scope = resolve_kit_module.scope_for(graph, "octagon-house")
        slots, _ = resolve_kit_module.resolve_slots(graph, chain, scope)
        still = [s for s, v in slots.items() if v and v.get("_source") == "italianate-american"]
        assert len(still) >= 10, "the dress itself must still come through the edge"

class TestASlotAStyleDeclinedToConstrainIsNotConstrainedForIt:
    """OQ 85's sibling, closed 27 Aug 2026 (WP-5.14), and found by drawing rather than by testing.

    `colonial-revival` bound `dormer` as `binding: "open"`, `status: "empty"` — the style
    explicitly declining to constrain the slot. `resolve_slots` only stops its walk on `specified`
    or `forbidden`; `open` is skipped entirely, so the walk continued to
    `english-cottage-vernacular` and returned its whole slot: `eyebrow-swept-dormer-within-thatch`
    canonical, `catslide-over-rear-outshot` permitted, and **`boxed-dormer` forbidden** — the only
    dormer a production Colonial Revival is ever built with, refused on a `c01, hard.`

    That a style saying `open` inherits a constraint it declined to make is a question about the
    semantics of `open` across all 97 slots, and it is raised separately rather than answered
    here. This pins the instance."""

    def test_colonial_revival_owns_its_dormer_slot(self, resolve_kit_module):
        rk = resolve_kit_module
        g = rk.load_graph()
        chain = rk.chain_for(g, "colonial-revival")
        slots, _ = rk.resolve_slots(g, chain, rk.scope_for(g, "colonial-revival"))
        d = slots["dormer"]
        assert d["_source"] == "colonial-revival", (
            f"the dormer slot resolves from {d['_source']} — the cascade is answering for a style "
            "that has its own binding")
        st = {v["id"]: v.get("status") for v in d["variants"]}
        assert st.get("boxed-dormer") == "canonical", st
        assert "eyebrow-swept-dormer-within-thatch" not in st, (
            "a thatched cottage's dormer is canonical on a production Colonial Revival again")

    def test_the_style_can_now_state_the_dormer_it_is_built_with(self, resolve_kit_module):
        """The behaviour the binding exists for: a record declaring a boxed dormer must not be
        refused. Before this, it was — by an inherited `forbidden`."""
        import copy
        import json as _j
        import os as _os
        e = __import__("elevation")
        root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
        plan = _j.load(open(_os.path.join(root, "plans", "spec-builder-colonial.json")))
        plan = copy.deepcopy(plan)
        plan["declared"]["dormer"] = {"count": 3, "variant": "boxed-dormer"}
        d = e.build_elevation(plan)["dormers"]
        assert d.get("refused") is not True
        assert d["variant"] == "boxed-dormer"

    def test_the_sash_pattern_no_longer_has_to_be_drawn_as_bare_glass(self, resolve_kit_module):
        """The slot states one now. WP-5.13 had to draw this style's dormer sash with no glazing
        bars at all, and say so on the sheet, because nothing in the cascade stated a pattern."""
        import copy
        import json as _j
        import os as _os
        e = __import__("elevation")
        root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
        plan = copy.deepcopy(_j.load(open(_os.path.join(root, "plans", "spec-builder-colonial.json"))))
        plan["declared"]["dormer"] = {"count": 3}
        d = e.build_elevation(plan)["dormers"]
        assert d["sash_pattern"] == "6/6"
        assert d["lights_across"] == 2 and d["lights_high_per_sash"] == 3

class TestTheSillNoLongerForbidsWhatItSpecifies:
    """The window sill, ruled 27 Aug 2026: the forbidden variant wins.

    `kits/tidewater-georgian.kit.json` forbids `wood-sill-sloped` with a reason — "the parent's
    2 1/4 in projecting sloped sill throws a shadow under every window and the brick sill does
    not, so the elevation is flatter" — and two inherited things contradicted it. The parent's
    `rule` sentence ended "...it projects past the wall face with a drip and is sloped 1 in 6",
    which describes the forbidden variant. And `sash-light`'s `window_sill/projection` rule
    delivered 2.25 in under the name `projection_in`, beside the node's own authored `projection`
    of 0–1 in: two names for one quantity, differing by more than twice, with nothing comparing
    them.

    The pack's own note had the answer in it all along — "In a frame wall this is a real sill
    member; in a masonry wall it is a rowlock or a stone and belongs to the brick-course pack, not
    this one" — and the fix is that sentence written into the data."""

    def _sill(self, rk, style):
        g = rk.load_graph()
        chain = rk.chain_for(g, style)
        slots, _ = rk.resolve_slots(g, chain, rk.scope_for(g, style))
        return slots["window_sill"]

    def test_the_rule_no_longer_describes_the_variant_it_forbids(self, resolve_kit_module):
        ws = self._sill(resolve_kit_module, "tidewater-georgian")
        rule = ws["rule"].lower()
        assert "sloped 1 in 6" not in rule and "projects past the wall face" not in rule, ws["rule"]
        assert "one course of brick" in rule
        st = {v["id"]: v.get("status") for v in ws["variants"]}
        assert st["wood-sill-sloped"] == "forbidden", "the forbidding is the premise of this test"

    def test_one_name_for_the_projection_and_it_is_the_nodes_own_figure(self, resolve_kit_module):
        ws = self._sill(resolve_kit_module, "tidewater-georgian")
        prm = ws["parameters"]
        assert "projection" not in prm, (
            "`projection` and `projection_in` are two names for one quantity; that is how a 0–1 in "
            "measured figure and a 2.25 in pack figure sat in one slot without meeting")
        assert prm["projection_in"]["range"] == [0, 1]
        assert prm["projection_in"]["kind"] == "measured"

    def test_a_frame_tradition_still_gets_the_packs_figure(self, resolve_kit_module):
        """The scope must be a scope, not a deletion. `sash-light`'s sloped sill is right on a
        frame wall and the parent keeps it."""
        prm = self._sill(resolve_kit_module, "georgian-colonial-american")["parameters"]
        assert prm["projection_in"]["computed_at"]["value"] == 2.25

    def test_the_pack_still_delivers_its_other_thirteen_addresses(self, resolve_kit_module):
        """`slots_except` refuses one rule. An allowlist would have meant naming the other
        thirteen by hand, and would silently stop delivering any rule the pack gained later —
        which is why the denylist form exists."""
        rk = resolve_kit_module
        g = rk.load_graph()
        chain = rk.chain_for(g, "tidewater-georgian")
        packs = rk.resolve_packs(g, chain)
        assert packs["sash-light"]["_source"] == "tidewater-georgian"
        assert packs["sash-light"]["slots_except"] == ["window_sill/projection"]
        ctx = {"ceiling_height": 108.0, "storey_height": 120.0, "opening_height": 80.0,
               "opening_width": 36.0, "span": 16.0}
        pack_slots, _ = rk.eval_packs(packs, ctx, None)
        sill = [r for r in (pack_slots.get("window_sill") or []) if r["pack"] == "sash-light"]
        assert not sill, "the refused rule is back"
        elsewhere = [sid for sid, rows in pack_slots.items()
                     if any(r["pack"] == "sash-light" for r in rows)]
        assert len(elsewhere) >= 5, (
            f"sash-light now reaches only {elsewhere} — the exclusion has become a deletion")

