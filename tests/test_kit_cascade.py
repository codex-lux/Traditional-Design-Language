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
