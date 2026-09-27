"""WP-14.18 (PRD tranche 2 §C.3): an assembly may declare which way it runs (`axis`) and how its
own words divide it (`zones`), and `build/check_orders.py` holds every zone to the members it
divides -- `assembly_declaration_errors`, called from `check_pack` beside the assembly sum check.

The failure this exists to prevent was MEASURED before the field existed
(`oq/casings-are-measured-across-and-drawn-upright` §2): `trim-classical` states its division once,
"Pedestal 4, wall field 12, entablature 3", and that string is true of its Georgian wall and false
of its Federal one, whose pedestal ends at 3.75 parts. A zone string copied from the pack's prose
onto every wall section would dimension two plates wrongly, so the checker must be able to say no
-- and every rule below is DRIVEN on an in-memory or temp-directory copy, never on the repository.

Every expectation is computed from the corpus; nothing names a count.
"""
import copy
import json
import os
import sys

import pytest

from conftest import ROOT

sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

CO = modcache.load("check_orders", os.path.join(ROOT, "build", "check_orders.py"))
TRIM = os.path.join(ROOT, "proportions", "systems", "trim-classical.json")


def _pack(path=TRIM):
    return json.load(open(path, encoding="utf-8"))


def _all_packs():
    import glob
    for f in sorted(glob.glob(os.path.join(ROOT, "proportions", "**", "*.json"), recursive=True)):
        yield json.load(open(f, encoding="utf-8"))


def _boundaries(asm):
    run, out = 0.0, []
    for m in asm["members"]:
        run += m["height_parts"]
        out.append(run)
    return out


# ------------------------------------------------------------------------ the shipped corpus
class TestTheCorpusAsItStands:
    def test_every_pack_passes_the_zone_rules(self):
        bad = [e for p in _all_packs() for e in CO.assembly_declaration_errors(p)]
        assert not bad, bad

    def test_the_rules_have_something_to_hold(self):
        """A checker over a corpus with no zones passes by having nothing to read."""
        zoned = [(p["id"], a) for p in _all_packs()
                 for a, rec in (p.get("assemblies") or {}).items() if rec.get("zones")]
        assert zoned, "no assembly declares zones; every test below would be the only exercise"

    def test_the_georgian_zones_end_on_its_own_member_boundaries(self):
        """The premise of the Federal test below, measured rather than assumed: the Georgian
        wall's running totals really pass through 4 and 16, and the Federal's do not."""
        asms = _pack()["assemblies"]
        geo = _boundaries(asms["wall_section_georgian"])
        fed = _boundaries(asms["wall_section_federal"])
        for b in (4, 16, 19):
            assert any(abs(x - b) < 1e-6 for x in geo), b
        assert not any(abs(x - 4) < 1e-6 for x in fed), "the Federal pedestal now ends at 4"
        assert not any(abs(x - 16) < 1e-6 for x in fed), "the Federal field now ends at 16"


class TestAZoneIsTheWordsOfItsOwnPack:
    """`Declared ONLY where the pack's own text states the division` (the schema's words). A
    reader, not a proof: each declared zone must be NAMED and SIZED in its own pack's prose, as
    `name width` -- "Pedestal 4, wall field 12, entablature 3" -- so a division read back off the
    member heights, which no sentence states, fails here as well as in review. A pack that states
    its division in another form extends this reader; it does not delete the assertion."""

    def _prose(self, p):
        bits = [p["module"].get("note") or "", p.get("notes") if isinstance(p.get("notes"), str)
                else json.dumps(p.get("notes") or ""), (p.get("authority") or {}).get("note") or ""]
        bits += [i["statement"] for i in p.get("invariants", [])]
        return " ".join(bits).lower()

    def test_every_declared_zone_is_named_and_sized_in_its_packs_own_words(self):
        seen = 0
        for p in _all_packs():
            prose = self._prose(p)
            for aid, rec in (p.get("assemblies") or {}).items():
                prev = 0.0
                for z in rec.get("zones") or []:
                    width = z["to_parts"] - prev
                    prev = z["to_parts"]
                    phrase = f"{z['name']} {width:g}".lower()
                    assert phrase in prose, (
                        f"{p['id']}/{aid}: the zone {z['name']!r} of {width:g} parts is stated in "
                        f"no sentence of its pack ({phrase!r} not found)")
                    seen += 1
        assert seen, "no zone to read"

    def test_every_turned_assembly_says_so_in_a_members_own_note(self):
        seen = 0
        for p in _all_packs():
            for aid, rec in (p.get("assemblies") or {}).items():
                if rec.get("axis") == "across-from-the-jamb":
                    notes = " ".join(m.get("note") or "" for m in rec["members"]).lower()
                    assert "measured across" in notes, (
                        f"{p['id']}/{aid} declares across-from-the-jamb and no member note says it "
                        f"is measured across")
                    seen += 1
        assert seen, "no assembly declares an axis"

    def test_every_assembly_a_member_note_says_is_measured_across_declares_it(self):
        """The converse, and the half that holds the DATA: an assembly whose own member note says
        it is measured across, and which declares no axis, is exactly the prose-only state
        `oq/casings-are-measured-across-and-drawn-upright` was raised about. Deleting one casing's
        axis leaves the test above green (the other two still say so); this one goes red."""
        seen = 0
        for p in _all_packs():
            for aid, rec in (p.get("assemblies") or {}).items():
                notes = " ".join(m.get("note") or "" for m in rec["members"]).lower()
                if "measured across" in notes:
                    assert rec.get("axis") == "across-from-the-jamb", (
                        f"{p['id']}/{aid}: a member note says the assembly is measured across and "
                        f"the assembly declares {rec.get('axis')!r}")
                    seen += 1
        assert seen, "no member note says measured across; the rule has no subject"


# ------------------------------------------------------------------------ the four rules, driven
def _with_zones(aid, zones, path=TRIM):
    p = copy.deepcopy(_pack(path))
    p["assemblies"][aid]["zones"] = zones
    return p


GEORGIAN = [{"name": "pedestal", "to_parts": 4}, {"name": "wall field", "to_parts": 16},
            {"name": "entablature", "to_parts": 19}]


class TestEachRuleCanFail:
    def test_a_clean_copy_returns_nothing(self):
        assert CO.assembly_declaration_errors(_with_zones("wall_section_georgian", GEORGIAN)) == []

    def test_the_federal_wall_given_the_georgian_division_is_red(self):
        """The case the checker exists for. The prose's 4 + 12 + 3 laid on the Federal section:
        its pedestal ends at 3.75 parts and its field at 16.25, so 4 and 16 are no boundary."""
        errs = CO.assembly_declaration_errors(_with_zones("wall_section_federal", GEORGIAN))
        assert any("'pedestal'" in e and "wall_section_federal" in e and "trim-classical" in e
                   and "no member boundary" in e for e in errs), errs
        assert any("'wall field'" in e and "no member boundary" in e for e in errs), errs
        assert not any("'entablature'" in e for e in errs), \
            "the Federal wall does end at 19; only the two interior boundaries are false"

    def test_the_georgian_pedestal_moved_to_three_and_three_quarters_is_red(self):
        z = copy.deepcopy(GEORGIAN)
        z[0]["to_parts"] = 3.75
        errs = CO.assembly_declaration_errors(_with_zones("wall_section_georgian", z))
        assert any("'pedestal'" in e and "3.75" in e and "no member boundary" in e
                   for e in errs), errs

    def test_zones_that_do_not_increase_are_red(self):
        z = [GEORGIAN[1], GEORGIAN[0], GEORGIAN[2]]
        errs = CO.assembly_declaration_errors(_with_zones("wall_section_georgian", z))
        assert any("'pedestal'" in e and "strictly increase" in e for e in errs), errs

    def test_zones_that_stop_short_of_the_whole_height_are_red(self):
        errs = CO.assembly_declaration_errors(_with_zones("wall_section_georgian", GEORGIAN[:2]))
        assert any("'wall field'" in e and "is the last" in e and "19" in e for e in errs), errs

    def test_zones_on_a_side_by_side_assembly_are_red(self):
        """`sums_check: false` -- members standing side by side -- has no running total. The
        corpus's own instance is `moorish-arch`, whose arch and alfiz are such assemblies; the
        premise is asserted so the test cannot pass on an assembly that stacks."""
        path = os.path.join(ROOT, "proportions", "orders", "moorish-arch.json")
        p = _pack(path)
        aid = next(a for a, rec in p["assemblies"].items() if rec.get("sums_check") is False)
        tops = _boundaries(p["assemblies"][aid])
        errs = CO.assembly_declaration_errors(_with_zones(aid, [
            {"name": "first", "to_parts": tops[0]}, {"name": "whole", "to_parts": tops[-1]}], path))
        assert any(aid in e and "sums_check" in e and "moorish-arch" in e for e in errs), errs


class TestTheCheckerReachesTheRule:
    """The function is only half; `check_pack` must CALL it -- WP-13.2's four blind mutations were
    every one the wiring. Driven through `check_pack` on a copy in a temporary directory, with the
    module's global error lists saved and restored so the run leaves nothing behind."""

    def _errors_for(self, tmp_path, pack):
        path = tmp_path / f"{pack['id']}.json"
        path.write_text(json.dumps(pack, indent=2), encoding="utf-8")
        saved = (list(CO.errors), list(CO.warnings), list(CO.notes), dict(CO.by_id))
        CO.errors.clear(); CO.warnings.clear(); CO.notes.clear(); CO.by_id.clear()
        try:
            validator = CO.schema_validators.compiled(CO.SCHEMA_PATH)
            CO.check_pack(str(path), validator, set(), set())
            return list(CO.errors)
        finally:
            CO.errors[:] = saved[0]; CO.warnings[:] = saved[1]; CO.notes[:] = saved[2]
            CO.by_id.clear(); CO.by_id.update(saved[3])

    def test_the_unmutated_copy_checks_clean_then_the_mutation_is_red(self, tmp_path):
        clean = self._errors_for(tmp_path, _pack())
        assert clean == [], f"the shipped copy does not check clean alone: {clean}"
        mutated = _with_zones("wall_section_federal", GEORGIAN)
        assert mutated["assemblies"]["wall_section_federal"]["zones"] == GEORGIAN, \
            "the mutation did not land"
        errs = self._errors_for(tmp_path, mutated)
        assert any("wall_section_federal" in e and "no member boundary" in e for e in errs), errs


# ------------------------------------------------------------------------ the schema's half
class TestTheSchemaRefusesWhatTheCheckerNeverSees:
    def _validator(self):
        pytest.importorskip("jsonschema")
        return CO.schema_validators.compiled(CO.SCHEMA_PATH)

    def test_a_single_zone_is_refused(self):
        v = self._validator()
        p = _with_zones("wall_section_georgian", GEORGIAN[-1:])
        assert list(v.iter_errors(p)), "one zone is the assembly itself; minItems 2"

    def test_an_axis_outside_the_two_is_refused(self):
        v = self._validator()
        p = copy.deepcopy(_pack())
        p["assemblies"]["casing_georgian"]["axis"] = "sideways"
        assert list(v.iter_errors(p))

    def test_an_absent_axis_is_admitted_and_means_up_the_wall(self):
        """Every stack in the corpus declares none, and must still validate."""
        v = self._validator()
        p = copy.deepcopy(_pack())
        for rec in p["assemblies"].values():
            rec.pop("axis", None)
        assert not list(v.iter_errors(p))
