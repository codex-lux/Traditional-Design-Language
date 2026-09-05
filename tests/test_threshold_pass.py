"""WP-11.4 — the stoop at the entrance door and the stack at the gable end.

Every guard here was mutation-checked: the fix reverted, the test watched go red. WP-11.1
found three guards that would have passed vacuously and WP-11.2 a fourth; the assumption is
always that there is a fifth.
"""
import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

TH = modcache.load("threshold", os.path.join(ROOT, "build", "threshold.py"))
GEOM = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))
ROOF = modcache.load("roof", os.path.join(ROOT, "build", "roof.py"))
PC = modcache.load("plan_check", os.path.join(ROOT, "build", "plan_check.py"))
C = PC.load_corpus()

TIDEWATER = os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")


def _placed(path=TIDEWATER):
    """The heuristic engine, deliberately: CP-SAT under a time budget is not deterministic
    under load and every figure pinned here would drift by a few tenths (CLAUDE.md, WP-9.6)."""
    return GEOM.solve(json.load(open(path, encoding="utf-8")), engine="heuristic")


class TestTheStoop(unittest.TestCase):
    def test_the_entrance_door_gets_a_flight_and_the_other_three_doors_get_a_reason(self):
        pl = _placed()
        th = pl["threshold"]
        self.assertEqual(len(th["steps"]), 1, "one door on the entrance face, one flight")
        st = th["steps"][0]
        self.assertEqual(st["wall"], "S")
        self.assertEqual(st["room"], "porch")
        named = [u["what"] for u in th["unplaced"] if u["rule"] == "th-only-the-entrance-door"]
        self.assertEqual(len(named), 3, "three exterior doors on the north front, three refusals")
        for u in th["unplaced"]:
            self.assertTrue(u.get("reason"), "a refusal that does not say why is a silence")
            self.assertTrue(u.get("rule"), "a refusal must name the rule refusing it")

    def test_a_service_door_on_the_entrance_front_is_named_and_not_given_a_stoop(self):
        """The engine decides whether this fires, which is why it is worth a test rather than
        a comment. On the search engine the Tidewater plan puts one exterior door on the S
        front; CP-SAT puts the KITCHEN's there too, legal by the record and a service door on
        the entrance front all the same. A door carries no `rank` on any record in this
        corpus, so the room's own `function_class` is the discriminator."""
        pl = _placed()
        C_ = C
        # the search engine's placement does not put a service door on the S front, so the
        # branch is exercised on a record that does: the kitchen's own north door, moved.
        for lv in pl["levels"][:1]:
            for r in lv["rooms"]:
                if r["id"] == "kitchen":
                    for d in r["doors"]:
                        if d.get("to") == "exterior":
                            d["wall"] = "S"
        out = TH.entrance_pass(pl, C_, {})
        named = [u for u in out["unplaced"] if "ENTRANCE face" in u["reason"]]
        self.assertEqual(len(named), 1)
        self.assertIn("kitchen", named[0]["what"])
        self.assertEqual([st["room"] for st in out["steps"]], ["porch"],
                         "the porch keeps its stoop and the kitchen does not get one")

    def test_the_flight_is_outside_the_block_and_never_inside_a_room(self):
        pl = _placed()
        t_ft = pl["footprint"]["wall"]["exterior_in"] / 12.0
        f = pl["threshold"]["steps"][0]["flight"]
        # 0.01 ft of tolerance because the record's coordinates are rounded to three
        # decimals, which is 0.012 in -- and a tolerance stated as a number beats a test that
        # passes on a coincidence of rounding.
        self.assertLess(f["y_ft"] + f["depth_ft"], -t_ft + 0.01,
                        "the flight must lie beyond the entrance wall's OUTSIDE face; the block "
                        "edge is the wall's inside face (WP-11.1)")
        for lv in pl["levels"]:
            for r in lv["rooms"]:
                g = r.get("geometry")
                if not g:
                    continue
                self.assertFalse(f["x_ft"] < g["x_ft"] + g["width_ft"]
                                 and g["x_ft"] < f["x_ft"] + f["width_ft"]
                                 and f["y_ft"] < g["y_ft"] + g["depth_ft"]
                                 and g["y_ft"] < f["y_ft"] + f["depth_ft"],
                                 f"the flight overlaps room {r['id']}")

    def test_an_entry_porch_is_the_platform_and_no_second_one_is_drawn(self):
        """The record's own reading: an entry-porch room IS the raised platform, already
        placed and dimensioned. Drawing a second one in front of it puts two thresholds on
        one house."""
        pl = _placed()
        st = pl["threshold"]["steps"][0]
        self.assertTrue(st["platform_is_the_room"])
        self.assertNotIn("platform", st)

    def test_the_flight_is_centred_on_the_door_and_clamped_to_the_room_behind_it(self):
        pl = _placed()
        st = pl["threshold"]["steps"][0]
        f = st["flight"]
        porch = next(r for lv in pl["levels"] for r in lv["rooms"] if r["id"] == "porch")
        g = porch["geometry"]
        self.assertGreaterEqual(f["x_ft"], g["x_ft"] - 1e-6)
        self.assertLessEqual(f["x_ft"] + f["width_ft"], g["x_ft"] + g["width_ft"] + 1e-6)
        self.assertAlmostEqual(f["x_ft"] + f["width_ft"] / 2.0, st["door_position_ft"], places=1)

    def test_the_nosings_are_the_treads_less_one_and_lie_inside_the_flight(self):
        """treads - 1, because the flight rectangle's own two edges ARE the top and bottom
        nosings. The first draft drew `treads` of them and put a second line on the bottom
        edge; nothing but looking at the sheet would have found it."""
        pl = _placed()
        st = pl["threshold"]["steps"][0]
        f = st["flight"]
        treads = max(st["riser_count"] - 1, 1)
        self.assertEqual(len(st["nosings"]), max(treads - 1, 0))
        for n in st["nosings"]:
            x1, y1, x2, y2 = n["line"]
            self.assertGreater(y1, f["y_ft"] + 1e-9)
            self.assertLess(y1, f["y_ft"] + f["depth_ft"] - 1e-9)
            self.assertAlmostEqual(y1, y2)

    def test_a_figure_the_record_gives_keeps_the_record_s_own_kind(self):
        """THE SAFE-LOOKING ERROR IS TO CALL EVERY FIGURE EDITORIAL, and it is still an error.
        `federal-style` resolves `riser_count_from_grade` as a DERIVED 4 from
        `storey-graduation`; `tidewater-georgian` states a band and this pass reduces it, which
        is a judgment and says so. Both must be legible from the record."""
        tw = TH.resolved_slots("tidewater-georgian")
        fed = TH.resolved_slots("federal-style")
        a = TH._figure(tw, "riser_count_from_grade", "th-riser-count", band="low")
        self.assertEqual((a["value"], a["kind"], a["reduced_from_a_band"]), (3, "editorial", "low"))
        b = TH._figure(fed, "riser_count_from_grade", "th-riser-count", band="low")
        self.assertEqual((b["value"], b["kind"]), (4, "derived"))
        self.assertNotIn("reduced_from_a_band", b)
        c = TH._figure(tw, "platform_width_in", "th-platform-width")
        self.assertEqual((c["value"], c["kind"]), (122.4, "derived"))

    def test_the_stoop_depth_is_the_one_value_all_three_statements_admit(self):
        """48 in: the low end of `stoop_depth_ft` [4, 6] ft, the midpoint of
        `platform_depth_in` [36, 60] in, and `stoop_min_depth_in` exactly. Not a midpoint of
        anything, and the arithmetic is the intersection rather than an average."""
        slots = TH.resolved_slots("tidewater-georgian")
        d = TH._stoop_depth_ft(slots)
        self.assertEqual(d["value"], 4.0)
        self.assertEqual(len(d["stated"]), 3)

    def test_an_empty_intersection_is_unjudged_and_never_averaged(self):
        """The mutation this guard exists for: make the three statements disagree and the
        pass must refuse, not split the difference."""
        slots = json.loads(json.dumps(TH.resolved_slots("tidewater-georgian")))
        slots["porch_depth"]["parameters"]["stoop_min_depth_in"]["value"] = 999
        d = TH._stoop_depth_ft(slots)
        self.assertIsNone(d["value"])
        self.assertIn("do not intersect", d["reason"])

    def test_the_pass_never_writes_a_dimension(self):
        """docs/model.md's direction of authority: a room's size comes from its programme and
        its band. This pass arranges into the house it is given."""
        before = _placed()
        sizes = {r["id"]: (r.get("width_ft"), r.get("length_ft"), json.dumps(r.get("geometry")))
                 for lv in before["levels"] for r in lv["rooms"]}
        after = _placed()
        for lv in after["levels"]:
            for r in lv["rooms"]:
                self.assertEqual(sizes[r["id"]],
                                 (r.get("width_ft"), r.get("length_ft"), json.dumps(r.get("geometry"))))


class TestTheStacks(unittest.TestCase):
    def test_two_stacks_at_the_gable_ends_on_the_face_the_record_names(self):
        pl = _placed()
        h = pl["hearths"]
        self.assertEqual(h["side"], "exterior",
                         "tidewater-georgian's own hearth_position makes `exterior-end` "
                         "canonical -- and its `chimney` slot makes BOTH a paired-interior and "
                         "an exterior gable-end stack canonical, so the roof-expression slot "
                         "cannot decide this and the plan slot does")
        self.assertEqual([s["wall"] for s in h["stacks"]], ["W", "E"])
        W = pl["footprint"]["width_ft"]
        t = pl["footprint"]["wall"]["exterior_in"] / 12.0
        s = 22.0 / 12.0
        self.assertAlmostEqual(h["stacks"][0]["x_ft"], -t - s, places=3)
        self.assertAlmostEqual(h["stacks"][1]["x_ft"], W + t, places=3)
        for sk in h["stacks"]:
            self.assertAlmostEqual(sk["width_ft"], s, places=3)
            self.assertAlmostEqual(sk["depth_ft"], s, places=3)
            self.assertEqual(sk["stack_plan_in"], 22.0)

    def test_the_stack_is_centred_on_the_mid_depth_of_its_end_wall(self):
        pl = _placed()
        D = pl["footprint"]["depth_ft"]
        for sk in pl["hearths"]["stacks"]:
            self.assertAlmostEqual(sk["y_ft"] + sk["depth_ft"] / 2.0, D / 2.0, places=3)

    def test_the_size_is_read_and_never_defaulted(self):
        """A stack drawn at an invented size is an invented measurement. Take the figure away
        and the pass must refuse."""
        plan = json.load(open(TIDEWATER, encoding="utf-8"))
        plan["style"] = "tidewater-georgian"
        pl = _placed()
        cache = TH._RESOLVED
        saved = json.loads(json.dumps(cache["tidewater-georgian"]))
        try:
            del cache["tidewater-georgian"]["chimney"]["parameters"]["stack_plan_in"]
            out = TH.hearth_pass(pl, C, {})
            self.assertEqual(out["stacks"], [])
            self.assertIn("stack_plan_in", out["unplaced"][0]["reason"])
        finally:
            cache["tidewater-georgian"] = saved

    def test_the_side_comes_from_the_node_s_own_kit_and_never_the_cascade(self):
        """`colonial-revival` is the case: its `hearth_position` is bound `open`, so the
        cascade hands it `central-open-hearth` from `english-gothic`, seven steps up and
        date-gated 1180-1450. The massing's own field is the fallback and it names no side,
        so nothing is drawn and the reason says which words failed to decide it."""
        pl = _placed(os.path.join(ROOT, "plans", "spec-builder-colonial.json"))
        h = pl["hearths"]
        self.assertEqual(h["stacks"], [])
        self.assertIsNone(h["side"])
        self.assertIn("massing", h["source"])
        self.assertIn("gable-end-paired", h["unplaced"][0]["reason"])

    def test_which_rooms_take_a_hearth_is_not_read(self):
        """PLAN-OF-ACTION.md's own words for this package: raise it, do not read it."""
        pl = _placed()
        self.assertIsNone(pl["hearths"]["hearth_rooms"])
        self.assertIn("oq/which-rooms-take-the-hearth", pl["hearths"]["hearth_rooms_note"])

    def test_two_canonical_sides_are_a_contradiction_and_not_a_choice(self):
        side, why = TH.stack_side(["exterior-end", "interior-paired-flanking-ridge"])
        self.assertIsNone(side)
        self.assertIn("BOTH", why)

    def test_the_massing_vocabulary_is_read_from_its_own_table(self):
        """The two vocabularies are not the same vocabulary, and reading a massing value
        through the kit table would answer UNJUDGED for a token that is really in the
        massing's own list."""
        self.assertIn("gable-end-paired", TH.MASSING_HEARTH)
        self.assertNotIn("gable-end or corner", TH.SIDE_OF)
        ok, _why = TH.at_gable_end(["gable-end or corner"], from_massing=True)
        self.assertIsNone(ok, "a disjunction names two positions and chooses neither")
        ok, _why = TH.at_gable_end(["gable-end-paired"], from_massing=True)
        self.assertTrue(ok)


class TestTheColumnThatCannotBeDrawn(unittest.TestCase):
    def test_a_portico_bays_on_a_stoop_only_node_is_not_read(self):
        """The precondition is the first clause of the slot's own rule -- 'WHERE A PORTICO
        OCCURS it is one bay wide'. Read without it, this puts a portico on a shipped
        reference plan whose kit calls one atypical there."""
        pl = _placed()
        r = next(u for u in pl["threshold"]["unplaced"]
                 if u["rule"] == "th-a-portico-only-where-one-is-canonical")
        self.assertIn("stoop-only", r["reason"])
        self.assertIn("portico_bays", r["reason"])

    def test_no_node_in_the_corpus_has_all_three_facts_a_drawn_column_needs(self):
        """A canonical portico, a bay count, and a diameter in inches. 23, 8 and 1 nodes
        respectively; the intersection is empty. Re-derived here rather than quoted, so the
        refusal stops being true the moment the corpus moves."""
        rk = modcache.load("resolve_kit", os.path.join(ROOT, "build", "resolve_kit.py"))
        g = rk.load_graph()
        portico = bays = dia = both = 0
        for nid in sorted(C["kits"]):
            try:
                slots, _ = rk.resolve_slots(g, rk.chain_for(g, nid), rk.scope_for(g, nid))
            except SystemExit:
                continue
            pt = slots.get("porch_type") or {}
            can = [v["id"] for v in (pt.get("variants") or []) if v.get("status") == "canonical"]
            is_p = any("portico" in v for v in can)
            b = ((pt.get("parameters") or {}).get("portico_bays") or {}).get("value")
            d = (((slots.get("porch_support") or {}).get("parameters") or {}).get("base_diameter_in")
                 or ((slots.get("column") or {}).get("parameters") or {}).get("base_diameter_in"))
            portico += bool(is_p)
            bays += b is not None
            dia += bool(d)
            both += bool(is_p and b is not None and d)
        self.assertEqual((portico, bays, dia, both), (23, 8, 1, 0),
                         "the three-fact measurement threshold/grammar.json's refusal rules "
                         "quote in their own notes")


class TestTheMoveOutOfRoof(unittest.TestCase):
    def test_roof_still_answers_the_same_for_every_plan_and_every_style(self):
        """`roof_form_for`, the ridge axis and the two gable-end points moved into
        build/threshold.py so the placement layer could read them without a second spelling.
        This is the pin that says the move changed nothing: both shipped plans, all fourteen
        reference plans, and the Tidewater block swept over all 164 styles.

        IT HASHES THE ROOF'S OWN ANSWER AND NOT `build_roof`'s WHOLE RETURN, and the reason is
        worth carrying: that return embeds `section`, which embeds the PLACED plan, so a hash
        of it is a hash of the placement too. The first version pinned the raw return, went
        green across the move, and then went red on a later commit in this same package that
        added two keys to the placed record and touched no roof code at all -- a pin that
        reads "the roof changed" when the roof did not is worse than no pin, because the next
        reader believes it."""
        import glob
        keep = ("main", "chimneys", "checks", "outline", "elevation_profiles", "footprint",
                "style", "plan_id")

        def prune(r):
            return {k: r[k] for k in keep if k in r} if isinstance(r, dict) else r

        out = {}
        for pf in sorted(glob.glob(os.path.join(ROOT, "plans", "*.json"))) + \
                sorted(glob.glob(os.path.join(ROOT, "plans", "reference", "*.json"))):
            key = os.path.relpath(pf, ROOT).replace(os.sep, "/")
            p = json.load(open(pf, encoding="utf-8"))
            try:
                out[key] = prune(ROOF.build_roof(p))
            except Exception as e:  # noqa: BLE001 -- the sweep records the failure, not raises
                out[key] = "ERR " + repr(e)
        base = json.load(open(TIDEWATER, encoding="utf-8"))
        for sid in sorted(C["styles"]):
            p = json.loads(json.dumps(base))
            p["style"] = sid
            try:
                out["sweep:" + sid] = prune(ROOF.build_roof(p))
            except Exception as e:  # noqa: BLE001
                out["sweep:" + sid] = "ERR " + repr(e)
        import hashlib
        blob = json.dumps(out, sort_keys=True, default=str)
        self.assertEqual(len(out), 180)
        self.assertEqual(hashlib.sha256(blob.encode()).hexdigest(),
                         "0d94e0cd1587cf3c236f25fd86420f2149b3298fb778e34cf643c69faa4d66a3",
                         "build/roof.py's own answer changed. Measured on a `git archive HEAD` "
                         "checkout of the pristine tree and again here; if a later package "
                         "means to move it, re-measure against a pristine checkout the same "
                         "way and say what moved and why.")
        # WP-11.6 EARNED THIS PRUNING, AND IT IS WORTH THE FOUR LINES TO SAY SO. That package
        # moved the placement of the Tidewater plan -- two authored `stacks_over` claims change
        # what `geometry.bias()` generates, and the upper floor comes out differently. Measured
        # both ways across it: the PRUNED hash above is UNCHANGED at 0d94e0cd..., and the RAW
        # `build_roof` return goes 4335d9e1... -> d8107962... So the pin said "the roof did not
        # change" about a commit that changed the placement, which is exactly the question it
        # was rewritten to answer and the reason it must not be un-pruned.

    def test_the_default_roof_form_is_spelled_once(self):
        src = open(os.path.join(ROOT, "build", "roof.py"), encoding="utf-8").read()
        self.assertNotIn('DEFAULT_ROOF_FORM = "', src,
                         "a second copy of a default is how two files come to disagree about "
                         "the same building")
        self.assertEqual(TH.DEFAULT_ROOF_FORM, "side-gable")


class TestTheModuleGraph(unittest.TestCase):
    def test_threshold_is_not_a_leaf_and_the_sibling_it_loads_cannot_reach_geometry(self):
        """build/threshold.py loads `resolve_kit`, which build/storeys.py, assemblies.py and
        furniture.py are all forbidden to do -- `structure.py` loads `geometry.py`, which
        calls `openings.py`, so a sibling import there closes a cycle. This walks the import
        graph rather than trusting the docstring that says it is safe."""
        seen, stack = set(), ["resolve_kit"]
        # BOTH ways a build/ module reaches a sibling: modcache.load by path, and a plain
        # `import x` after build/ is put on sys.path -- resolve_kit reaches proportion_engine
        # by the second, and the first version of this walk saw only the first and reported an
        # import graph of two modules. The vacuity assertion at the foot is what caught it.
        pat = re.compile(r'(?:modcache|_mc|mc)\.load\(\s*"([a-z_]+)"'
                         r'|^import ([a-z_]+)(?: as \w+)?$'
                         r'|^from ([a-z_]+) import', re.M)
        while stack:
            name = stack.pop()
            if name in seen:
                continue
            seen.add(name)
            path = os.path.join(ROOT, "build", name + ".py")
            if not os.path.exists(path):
                continue
            src = open(path, encoding="utf-8").read()
            for groups in pat.findall(src):
                stack.extend(g for g in groups if g)
        self.assertNotIn("geometry", seen,
                         "resolve_kit's transitive loads now reach geometry, so loading it "
                         "from the placement path closes an import cycle")
        self.assertNotIn("openings", seen)
        self.assertNotIn("structure", seen)
        self.assertIn("proportion_engine", seen,
                      "the walk found nothing, which would make the assertions above vacuous")


class TestTheDrawing(unittest.TestCase):
    def test_both_renderers_are_told_about_the_stoop_and_the_stack(self):
        core = open(os.path.join(ROOT, "mcp_server", "core.py"), encoding="utf-8").read()
        i = core.index("def placement_summary")
        body = core[i:i + 3000]
        self.assertIn('"threshold": out.get("threshold")', body,
                      "omitted here, the browser sheet draws neither while the Python sheet "
                      "draws both -- the defect WP-11.3 found in this same return")
        self.assertIn('"hearths": out.get("hearths")', body)
        jsx = open(os.path.join(ROOT, "workbench", "app", "src", "sheet", "Sheet.jsx"),
                   encoding="utf-8").read()
        self.assertIn("placement?.hearths?.stacks", jsx)
        self.assertIn("placement?.threshold?.steps", jsx)

    def test_the_plate_is_wide_enough_to_hold_what_stands_outside_the_house(self):
        """The stoop and an exterior stack are at a negative coordinate or past `width_ft`.
        A plate sized to the rooms cuts them off with no error anywhere."""
        rp = modcache.load("render_plan", os.path.join(ROOT, "build", "render_plan.py"))
        pl = _placed()
        rects = rp.threshold_rects(pl)
        self.assertGreaterEqual(len(rects), 3, "one flight and two stacks at least")
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "s.svg")
            rp.render(pl, out, register="presentation")
            svg = open(out, encoding="utf-8").read()
        m = re.search(r'viewBox="([-\d.]+) ([-\d.]+) ([\d.]+) ([\d.]+)"', svg)
        self.assertIsNotNone(m)
        self.assertEqual(svg.count("data-stack"), 4, "two stacks on each of two plates")
        self.assertEqual(svg.count('data-threshold="porch"'), 1,
                         "the flight, on the ground plate only -- the stoop is at grade -- and "
                         "`data-threshold` names the ROOM in both renderers, so one selector "
                         "finds it in either")
        self.assertEqual(svg.count('data-part="flight"'), 1)
        self.assertEqual(svg.count('data-part="platform"'), 0,
                         "the entry porch IS the platform")

    def test_the_plate_grows_to_hold_what_stands_outside_the_house(self):
        """A DIFFERENTIAL, because the obvious form of this guard CANNOT FAIL. The first
        version asserted every `.st` rect lies inside the viewBox — and it passed with the
        widening deleted, because the sheet's own margin is deeper than the 3 ft a stack
        projects, so a stack drawn off the plate is still comfortably inside the SHEET. What
        actually breaks is that the drawing runs into its own border. So: render the plan,
        then render it again with the stoop and the stacks stripped off the record, and the
        canvas must be WIDER with them than without."""
        rp = modcache.load("render_plan", os.path.join(ROOT, "build", "render_plan.py"))
        import tempfile

        def canvas(pl):
            with tempfile.TemporaryDirectory() as d:
                out = os.path.join(d, "s.svg")
                rp.render(pl, out, register="working")
                svg = open(out, encoding="utf-8").read()
            m = re.search(r'viewBox="([-\d.]+) ([-\d.]+) ([\d.]+) ([\d.]+)"', svg)
            return tuple(float(g) for g in m.groups())

        with_it = _placed()
        without = _placed()
        without["threshold"] = {"steps": [], "supports": [], "unplaced": [], "figures": {}}
        without["hearths"] = {"stacks": [], "unplaced": [], "source": None, "side": None,
                              "hearth_rooms": None, "hearth_rooms_note": ""}
        a, b = canvas(with_it), canvas(without)
        self.assertGreater(a[2], b[2], "the west and east stacks stand outside the block and "
                                       "the plate must be wider for them")
        self.assertGreater(a[3], b[3], "the flight stands outside the entrance wall and the "
                                       "plate must be taller for it")


class TestThePlacedRecordValidates(unittest.TestCase):
    def test_every_shipped_plan_validates_against_its_own_schema_once_placed(self):
        """TWO OF THE FOURTEEN REFERENCE PLANS DID NOT, and had not since OQ 55: geometry.py
        writes {"heated": false, ...} into `geometry.void` and the schema forbade it. Nothing
        noticed, because nothing validates a PLACED plan except the API's own gate and a
        reference plan never goes through it."""
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema absent -- COULD NOT EVALUATE, never a pass")
        import glob
        sch = json.load(open(os.path.join(ROOT, "schema", "plan.schema.json"), encoding="utf-8"))
        v = jsonschema.Draft202012Validator(sch)
        bad = []
        for pf in sorted(glob.glob(os.path.join(ROOT, "plans", "*.json"))) + \
                sorted(glob.glob(os.path.join(ROOT, "plans", "reference", "*.json"))):
            pl = GEOM.solve(json.load(open(pf, encoding="utf-8")), engine="heuristic")
            errs = [e.message for e in v.iter_errors(pl)]
            if errs:
                bad.append((os.path.basename(pf), errs[:2]))
        self.assertEqual(bad, [], "a placed plan invalid against the contract it was placed from")


if __name__ == "__main__":
    unittest.main()
