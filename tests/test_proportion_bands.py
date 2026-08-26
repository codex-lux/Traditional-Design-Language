"""Derived proportion rules against their own declared bands — OQ 68.

WHY THIS FILE EXISTS. 22 rules across `proportions/orders/` and `proportions/overlays/`
evaluated outside the band the same rule declares, and were published to the workbench as
"· out of band" with no checker looking at them: `check_modules.py --eval` and
`check_systems.py` both do this check and neither covers those two directories.

Re-diagnosed, they were three different things and almost none of them was a wrong number:

  * TEN stated a band on the RATIO their coefficient encodes while the expression yielded
    inches — greek-doric's entablature evaluating to 41.976 in against [0.3, 0.34], whose
    authority note reads "The Parthenon's measured ratio, about 0.315". Every one of the ten
    ratios lands INSIDE its own band; the schema had one `range` field doing two jobs. Split.
  * SIX were out of band only because of the engine's default bindings, and four of them say
    so in capitals in their own authority note: BIND storey_height TO THE FULL WALL HEIGHT.
    `calibrated_for` had been in the schema for exactly this since the chair-rail correction
    and nothing read it.
  * FOUR missed by 0.00025 — 7/32 = 0.21875 against a floor of 0.219, which is the
    three-decimal rounding of the very expression the band exists to contain.

TWO remain out of band and are meant to. They are pinned below by name.
"""
import glob
import importlib.util
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _engine():
    spec = importlib.util.spec_from_file_location(
        "pe", os.path.join(ROOT, "build", "proportion_engine.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def _packs():
    return [json.load(open(f)) for f in sorted(glob.glob(os.path.join(ROOT, "proportions", "*", "*.json")))]


class TestTheBandsHold:
    # The ratchet. Both are recorded in OQ 68 as wanting a ruling rather than a patch, and
    # both are the mechanism working: a rule deriving a dimension from a small order and a
    # band that says the result is too small to build.
    KNOWN_OUT = {("vignola-doric", "cornice"), ("chambers-ionic", "balustrade")}

    def test_no_rule_evaluates_outside_its_own_band_except_the_two_recorded_ones(self):
        eng = _engine()
        out = {(p["id"], r["target_slot"]) for p in _packs()
               for r in eng.evaluate(p)["rules"] if r.get("in_range") is False}
        assert out == self.KNOWN_OUT, (
            f"unexpected: {sorted(out - self.KNOWN_OUT)}; "
            f"fixed without re-pinning: {sorted(self.KNOWN_OUT - out)}. This number may go "
            f"DOWN with a ruling and must not go up silently.")

    def test_a_rule_outside_its_calibration_is_unjudged_and_not_failed(self):
        """The direction that matters. Judging a rule against a binding its own note tells
        you not to use is unjudged-reported-as-failed, and it convicted six rules of being
        wrong about a building they were never given."""
        eng = _engine()
        withheld = [(p["id"], r["target_slot"], r["out_of_calibration"])
                    for p in _packs() for r in eng.evaluate(p)["rules"]
                    if r.get("out_of_calibration")]
        assert withheld, "expected some rule to declare a calibration the defaults are outside"
        for pid, slot, why in withheld:
            rule = next(r for r in eng.evaluate(next(p for p in _packs() if p["id"] == pid))["rules"]
                        if r["target_slot"] == slot and r.get("out_of_calibration"))
            assert "in_range" not in rule, f"{pid}/{slot}: judged anyway"
            assert "calibrated for" in why, why

    def test_the_benjamin_cornices_come_into_band_at_the_wall_height_they_ask_for(self):
        """Benjamin's own worked example: "suppose a house to be thirty five feet high,
        divide thirty five feet into thirty parts, and one thirtieth will be fourteen
        inches." 420 in, and all four land inside their bands."""
        eng = _engine()
        for pid in ("benjamin-corinthian", "benjamin-doric", "benjamin-ionic", "benjamin-tuscan"):
            pack = next(p for p in _packs() if p["id"] == pid)
            at_default = next(r for r in eng.evaluate(pack)["rules"]
                              if r["target_slot"] == "cornice" and r.get("calibrated_for"))
            at_real = next(r for r in eng.evaluate(pack, bindings={"storey_height": 420.0})["rules"]
                           if r["target_slot"] == "cornice" and r.get("calibrated_for"))
            assert at_default.get("out_of_calibration"), pid
            assert at_real.get("in_range") is True, (pid, at_real["value"], at_real["range"])


class TestTheRatioSplit:
    QUANTITIES = {"entablature_to_column_ratio", "interior_cornice_to_ceiling_ratio",
                  "arch_return_to_radius_ratio"}

    def test_every_ratio_rule_lands_inside_its_own_band(self):
        eng = _engine()
        seen = 0
        for p in _packs():
            for r in eng.evaluate(p)["rules"]:
                if r.get("quantity") in self.QUANTITIES:
                    seen += 1
                    assert r.get("in_range") is True, (p["id"], r["target_slot"], r["value"], r["range"])
        assert seen == 10, f"expected the ten split rules, found {seen}"

    def test_the_dimension_rule_beside_it_no_longer_claims_a_band(self):
        """The whole point of the split: the band belongs to the ratio, and the rule that
        multiplies it out into inches carries no band at all. If a range comes back onto one
        of these, the incommensurable comparison is back."""
        for p in _packs():
            ratios = [r for r in p.get("derived_rules", []) if r.get("quantity") in self.QUANTITIES]
            for rr in ratios:
                # the sibling is the rule this ratio was split FROM, and only that one:
                # height_ratio -> height, return_ratio -> return. Matching any rule on the
                # slot whose dimension merely ENDS in "height" swept up moorish-arch's arch
                # RISE, which is a legitimate ranged rule in inches about a different thing.
                src = rr["dimension"][: -len("_ratio")]
                sibs = [r for r in p["derived_rules"]
                        if r["target_slot"] == rr["target_slot"] and r.get("dimension") == src]
                assert sibs, f'{p["id"]}/{rr["target_slot"]}: ratio rule with no dimension rule beside it'
                for s in sibs:
                    assert "range" not in s, (
                        f'{p["id"]}/{s["target_slot"]}/{s.get("dimension")} carries a band again; '
                        f'the band belongs to {rr["quantity"]}')

    def test_a_ratio_rule_carries_a_named_dimension_not_the_generic_one(self):
        """`facade-arcade` already writes (arch, ratio) for springing_as_fraction_of_height.
        A generic `ratio` on the same slot is an address collision measuring something else,
        which is what check_addresses.py caught the first time these were written."""
        for p in _packs():
            for r in p.get("derived_rules", []):
                if r.get("quantity") in self.QUANTITIES:
                    assert r["dimension"] != "ratio", (p["id"], r["target_slot"])
                    assert r["dimension"].endswith("_ratio"), (p["id"], r["dimension"])


class TestTheToleranceIsTheAuthorsOwnPrecision:
    def test_it_absorbs_a_rounded_band_edge_and_nothing_wider(self):
        eng = _engine()
        # a floor written 0.219 is the author saying 0.219 to three places; 7/32 is that
        assert 0.219 - eng.stated_precision(0.219) <= 0.21875
        # and it must not forgive a real violation of a coarsely written edge
        assert not (0.3 - eng.stated_precision(0.3) <= 0.26)
        # finer precision earns proportionately less slack
        assert eng.stated_precision(0.2222) < eng.stated_precision(0.219)
        # and it is capped, so an integer edge does not acquire half a unit of slack
        assert eng.stated_precision(10) <= 5e-4 and eng.stated_precision(36.0) <= 5e-4


class TestTheCheckerActuallyLooks:
    def test_check_orders_reports_a_rule_outside_its_band(self, tmp_path):
        """The gap this whole entry came from: check_orders.py validated that a range was not
        inverted and never evaluated a rule against it, so 22 violations sat unreported for as
        long as the file has existed. Exercised by breaking a band in a copy."""
        import subprocess, shutil
        work = tmp_path / "repo"
        shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns(
            ".git", "node_modules", "dist", "__pycache__", "*.png"))
        target = work / "proportions" / "orders" / "greek-doric.json"
        pack = json.loads(target.read_text())
        for r in pack["derived_rules"]:
            if r.get("range"):
                r["range"] = [999.0, 1000.0]        # nothing can satisfy this
                break
        target.write_text(json.dumps(pack, indent=2, ensure_ascii=False) + "\n")
        out = subprocess.run(["python3", "build/check_orders.py"], cwd=work,
                             capture_output=True, text=True).stdout
        assert "outside its own declared range" in out, out[-2000:]
