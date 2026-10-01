"""The census's own guards (WP-14.1).

`tests/svg_census.py` answers Lucas's question -- does every drawn figure on every surface agree
with the record it was drawn from -- as a table. These tests keep the table honest in the four
ways a table goes wrong: it stops covering the tree (a new surface nobody listed), it stops
matching the corpus (a disagreement nobody pinned, or a fix nobody unpinned), it stops matching
its own document, and it stops being able to say "disagrees" at all.

The last is the one this repository keeps meeting. A check whose disagreeing branch the corpus
never reaches is green whatever the ink does, so a check with no live disagreement is DRIVEN here
where it can be: the defect it exists to catch is planted in a copy of a real plate, in memory,
and the check must report it. Nothing here writes inside the repository.

NOT EVERY ONE, AND THIS SAID EVERY ONE UNTIL WP-14.6 (G6). Counted at WP-14.6: of 68 checks, 64
carry no live disagreement and 17 of those are driven in this file. The other 47 are held by
nothing here. Where one was mutation-checked when it was written -- the defect injected into the
SUBJECT, in an isolated copy, and the check seen to go red -- that is recorded in its package's
report, and it is a proof made once; a drive is a proof made every run. A check among the 47
whose disagreeing branch goes blind later is caught by nothing in this file.

AND THAT COUNT WAS WRONG, IN THE DIRECTION THAT UNDERSTATES THE FILE (re-derived 27 Sep, WP-14.6's
second audit). Read off every test body -- a test that names a check and requires "disagrees" --
the file at WP-14.6 drove 41 of the 64, not 17, and 23 were held by nothing here; seventeen is
`len(NODE_CHECKS)`, the JavaScript-backed checks, which is the likeliest source of the figure.
With V22 the census holds 69 checks, 65 carry no live disagreement, and 42 of those are driven
here. The 23 that are not: E1, E2, E3, F1, P3, P4, P7, PL1, S3, V1, V3, V4, V5, V6, V8, V11, V14,
V17, V18, V20, V21, X1, X2. A count in a docstring is read by no checker: re-derive it, do not
quote it.

AND IT WENT STALE AGAIN, AS IT SAID IT WOULD (WP-15.8's audit, auditor B). Phase 15 added V23,
V24, V25, X3 and X4 with no test that could drive one, and this read 69 and 23 against 74 and 28.
The count is DERIVED now -- `_driven`, at the foot of this file, reads which checks the tests here
require "disagrees" of, following each test into the helpers it hands its check to -- and held
equal to `UNDRIVEN`, which is the list. The five are driven since, so it is the same 23.
"""
import ast
import copy
import json
import os
import re
import subprocess
import sys

import pytest

import ink_surfaces as SURF
import svg_census as C

_ROWS = None


def _rows():
    global _ROWS
    if _ROWS is None:
        _ROWS = C.run()
    return _ROWS


# ------------------------------------------------------------------ which functions run node
# Read off the SYNTAX TREE and not the text (WP-14.6's second audit, M12): a subprocess call whose
# command's first word is the `node` executable, however the call and the command are spelled.
_SUBPROCESS_CALLS = frozenset(("run", "Popen", "call", "check_call", "check_output"))


def _is_node(expr, env, seen=()):
    """Whether one expression names the `node` executable: the word itself or a path to it, a
    `which("node")`, or a name bound to either."""
    if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
        return os.path.basename(expr.value.strip()) == "node"
    if isinstance(expr, ast.Call):
        f = expr.func
        name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
        return (name == "which" and bool(expr.args) and isinstance(expr.args[0], ast.Constant)
                and expr.args[0].value == "node")
    if isinstance(expr, ast.Name) and expr.id in env and expr.id not in seen:
        return _is_node(env[expr.id], env, seen + (expr.id,))
    return False


def _command_runs_node(expr, env, seen=()):
    """Whether a command -- an argv list or tuple, a sum beginning with one, a shell string, or a
    name bound to any of these -- begins with the `node` executable."""
    if isinstance(expr, (ast.List, ast.Tuple)):
        if not expr.elts:
            return False
        first = expr.elts[0]
        if isinstance(first, ast.Starred):
            return _command_runs_node(first.value, env, seen)
        return _is_node(first, env, seen)
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Add):
        return _command_runs_node(expr.left, env, seen)
    if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
        words = expr.value.split()
        return bool(words) and os.path.basename(words[0]) == "node"
    if isinstance(expr, ast.JoinedStr) and expr.values and isinstance(expr.values[0], ast.Constant):
        words = str(expr.values[0].value).split()
        return bool(words) and os.path.basename(words[0]) == "node"
    if isinstance(expr, ast.Name) and expr.id in env and expr.id not in seen:
        return _command_runs_node(env[expr.id], env, seen + (expr.id,))
    return False


def _bindings(nodes):
    """name -> the expression a plain `name = expr` binds it to."""
    env = {}
    for n in nodes:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            env[n.targets[0].id] = n.value
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.value is not None:
            env[n.target.id] = n.value
    return env


def _node_backed(src):
    """The top-level functions of a module that run `node`, directly or through any function of
    the same module they call or refer to, transitively."""
    tree = ast.parse(src)
    mods, bare = set(), set()
    for n in tree.body:
        if isinstance(n, ast.Import):
            mods |= {a.asname or a.name for a in n.names if a.name == "subprocess"}
        elif isinstance(n, ast.ImportFrom) and n.module == "subprocess":
            bare |= {a.asname or a.name for a in n.names if a.name in _SUBPROCESS_CALLS}
    module_env = _bindings(tree.body)
    fns = {n.name: n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}

    def runs(fn):
        env = dict(module_env, **_bindings(ast.walk(fn)))
        for call in (c for c in ast.walk(fn) if isinstance(c, ast.Call)):
            f = call.func
            if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
                if f.value.id == "os":
                    ok = f.attr in ("system", "popen")
                else:
                    ok = f.value.id in mods and f.attr in _SUBPROCESS_CALLS
            else:
                ok = isinstance(f, ast.Name) and f.id in bare
            if not ok:
                continue
            cmd = call.args[0] if call.args else next(
                (k.value for k in call.keywords if k.arg in ("args", "cmd", "command")), None)
            if cmd is not None and _command_runs_node(cmd, env):
                return True
        return False

    refs = {name: {x.id for x in ast.walk(fn) if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load)}
            for name, fn in fns.items()}
    backed = {name for name, fn in fns.items() if runs(fn)}
    while True:
        more = {name for name in fns if name not in backed and refs[name] & backed}
        if not more:
            return backed
        backed |= more


# ------------------------------------------------------------------ the registry is the tree
class TestTheRegistryIsTheTree:
    def test_every_file_that_draws_svg_is_registered(self):
        missing = C.unregistered()
        assert not missing, (
            "these files emit SVG and tests/svg_census.py's REGISTRY does not name them: %s. A "
            "surface that draws a building needs census rows; one that does not needs a row with "
            "role 'out-of-scope' and a reason." % missing)

    def test_every_registered_file_exists(self):
        """A row naming a file that is gone is a claim of coverage over nothing."""
        gone = [r["file"] for r in C.REGISTRY if not os.path.exists(os.path.join(C.ROOT, r["file"]))]
        assert not gone, gone

    def test_every_producer_and_carrier_is_found_by_the_scan(self):
        """If the scan cannot see a surface already listed, it could not see a new one either,
        and `test_every_file_that_draws_svg_is_registered` would be green over a blind scan.
        A helper builds path data a producer emits and writes no element of its own, so it is
        the one role the scan is not asked to find."""
        seen = set(C.emitters())
        blind = [r["file"] for r in C.REGISTRY
                 if r["role"] in ("producer", "carrier", "out-of-scope") and r["file"] not in seen]
        assert not blind, blind

    def test_every_out_of_scope_row_says_why(self):
        for r in C.REGISTRY:
            assert r["role"] in ("producer", "carrier", "helper", "out-of-scope"), r
            if r["role"] == "out-of-scope":
                assert len(r.get("reason") or "") > 20, r
            else:
                assert r.get("surface"), r

    def test_the_scan_sees_a_component_that_writes_no_svg_root(self, tmp_path):
        """The first scan matched `<svg` and nothing else, and was blind to a component that
        returns a `<path>` inside its parent's `<svg>` -- which is where a second spelling of a
        mark grows. Driven on a throwaway repository, with the two things that must NOT count:
        a docstring naming `<path>[]` and a route regex's `(?P<path>`."""
        subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
        (tmp_path / "Mark.jsx").write_text("export const Mark = () => <path d='M0 0 L1 1' />;\n")
        (tmp_path / "carrier.jsx").write_text("<div dangerouslySetInnerHTML={{__html: s}} />\n")
        (tmp_path / "prose.py").write_text('"""a list is reported as `<path>[]`"""\n'
                                           'R = r"^/mcp(?P<path>/.*)$"\n')
        assert C.emitters(str(tmp_path)) == ["Mark.jsx", "carrier.jsx"]


# ------------------------------------------------------------------ the known set is the live set
class TestTheKnownDisagreements:
    def test_the_live_disagreements_are_exactly_the_known_ones(self):
        known = json.load(open(C.KNOWN))["disagreements"]
        live = C.disagreements(_rows())
        new, fixed, moved_ids = C.compare(known, live)
        moved = ["%s: %r -> %r" % (k, known[k], live[k]) for k in moved_ids]
        assert not new and not fixed and not moved, (
            "the census moved. NEW disagreements (a drawing now departs from its record; fix it, "
            "or if it is a defect newly MEASURED rather than newly made, add it and say so in the "
            "commit): %s. FIXED (remove from tests/fixtures/ink_known_disagreements.json in the "
            "same commit as the fix): %s. MOVED (a disagreement whose figures changed -- re-pin it "
            "in a commit that says which way and why): %s" % (new, fixed, moved[:12]))

    def test_a_disagreement_whose_figures_changed_is_moved_and_not_passed(self):
        """DRIVEN (WP-14.6, auditor C). The id is the row and the detail is its figures; the pin
        holds both because a row already red for one cause cannot report a second unless its
        figures are held. A change to the DETAIL alone is the case a set comparison on ids would
        call unchanged, so it is driven by hand, beside one of each other kind."""
        known = {"V1:a": "3 marks off", "V1:b": "stays", "V2:c": "gone next run"}
        live = {"V1:a": "5 marks off", "V1:b": "stays", "V9:d": "arrived"}
        assert C.compare(known, live) == (["V9:d"], ["V2:c"], ["V1:a"])
        assert C.compare(known, dict(known)) == ([], [], [])

    def test_the_known_list_is_sorted_and_says_what_it_is(self):
        doc = json.load(open(C.KNOWN))
        assert list(doc["disagreements"]) == sorted(doc["disagreements"]), "keep the ids sorted"
        assert "held by identity" in doc["about"]


# ------------------------------------------------------------------ the doc is the census
class TestTheDocIsTheCensus:
    def test_the_tables_in_docs_fidelity_are_current(self):
        """Every line of the checks table this environment can compute is held to the doc. A check
        this environment cannot run at all keeps the doc's own line (`unevaluable_here`), and the
        test below names it as could-not-evaluate: CI's corpus shards have no `ezdxf`, and this
        test was red there on every run since the merge while green wherever the doc was written."""
        rows = _rows()
        reg, table = C.render_doc_tables(rows)
        text = open(C.DOC).read()
        table = C.keep_unevaluable_lines(table, text, C.unevaluable_here(rows))
        assert C.splice(C.splice(text, "registry", reg), "checks", table) == text, (
            "docs/fidelity.md is stale: run `python3 tests/svg_census.py --write-doc`")

    def test_the_lines_this_environment_cannot_compute_are_named_and_not_passed(self):
        missing = C.unevaluable_here(_rows())
        if missing:
            pytest.skip("COULD NOT EVALUATE the doc's lines for %s: each check wants a tool this "
                        "environment lacks (%s), so its line was not held" % (
                            ", ".join(sorted(missing)), "; ".join("%s: %s" % kv for kv in sorted(missing.items()))))

    def test_a_check_that_cannot_run_is_told_from_one_that_ran_and_found_nothing(self):
        """DRIVEN: the shape the X rows take where `ezdxf` is absent, beside a check that ran and
        judged nothing (could-not-evaluate for a reason in the record) and one that ran and agreed.
        Only the first is unevaluable here, and only its line is kept from the doc."""
        rows = [C.row("X9", "export_dxf", "cne", "ezdxf is not installed, so the DXF cannot be drawn"),
                C.row("V98", "a", "cne", "the record states no eave"),
                C.row("V99", "b", "agrees", "")]
        assert C.unevaluable_here(rows) == {"X9": "ezdxf"}
        mixed = rows + [C.row("X9", "p/S", "agrees", "")]
        assert C.unevaluable_here(mixed) == {}, "a check that ran somewhere is not unevaluable"
        doc = "| X9 | e | s | p | 2 | 2 | 0 | 0 |\n| V98 | e | s | p | 3 | 0 | 0 | 3 |"
        gen = "| X9 | e | s | p | 1 | 0 | 0 | 1 |\n| V98 | e | s | p | 1 | 0 | 0 | 1 |"
        assert C.keep_unevaluable_lines(gen, doc, {"X9": "ezdxf"}) == (
            "| X9 | e | s | p | 2 | 2 | 0 | 0 |\n| V98 | e | s | p | 1 | 0 | 0 | 1 |")
        assert C.keep_unevaluable_lines(gen, "", {"X9": "ezdxf"}) == gen, (
            "a check the doc does not carry keeps the generated line, so the doc still reads stale")
        # K01 (WP-15.8's audit, auditor M): a check whose every row could not evaluate, one for want
        # of a tool and one for a reason in the record, did not run nowhere -- it ran and judged
        # nothing -- so its line is held; `any` for `all` passed with nothing red
        both = [C.row("X9", "a", "cne", "ezdxf is not installed, so the DXF cannot be drawn"),
                C.row("X9", "b", "cne", "the record states no eave")]
        assert C.unevaluable_here(both) == {}, "a row that ran and judged nothing is not a missing tool"
        # B11 (auditor B): only the COUNTS are the doc's; the statement is the check's own words and
        # is held everywhere, so an X statement edited without regenerating the doc reads stale
        edited = "| X9 | e | s2 | p | 1 | 0 | 0 | 1 |"
        kept = C.keep_unevaluable_lines(edited, doc, {"X9": "ezdxf"})
        assert kept == "| X9 | e | s2 | p | 2 | 2 | 0 | 0 |" and kept not in doc, kept


# ------------------------------------------------------------------ no check is vacuous
class TestNoCheckIsVacuous:
    def test_every_check_evaluated_something(self):
        s = C.summary(_rows())
        empty = [cid for cid, x in s.items() if not x["rows"]]
        assert not empty, "a check that evaluated nothing reads as a check that found nothing: %s" % empty

    def test_a_check_over_every_plate_reads_every_plate(self):
        n = len(C._profile_assets())
        assert n == 73, n
        for cid, c in C.CHECKS.items():
            if c["population"] == "every committed profile plate":
                assert C.summary(_rows())[cid]["rows"] == n, cid

    def test_every_committed_plate_states_its_frame_and_its_datum(self):
        for a, g, pl, rec in C._profile_assets():
            assert pl.plate is not None, a["id"]
            assert pl.plate["datum"] in ("axis", "naked"), a["id"]
            assert pl.outline is not None, (a["id"], pl.n_outlines)


# ------------------------------------------------------------------ the checks can say "disagrees"
def _planted(asset_id, change):
    """One committed plate, altered in memory by `change(svg) -> svg`, as the census reads it."""
    for a, g, pl, rec in C._profile_assets():
        if a["id"] == asset_id:
            svg = change(pl.svg)
            assert svg != pl.svg, "the planted defect did not land"
            return [(a, g, SURF.ProfilePlate(svg), rec)]
    raise KeyError(asset_id)


def _verdicts(monkeypatch, cid, plates):
    monkeypatch.setattr(C, "_PLATES", plates)
    return [r["verdict"] for r in C.CHECKS[cid]["fn"]()]


class TestTheChecksCanDisagree:
    """P1, P2, P5, P6, P9 and P12 have no live disagreement, so the corpus never reaches the
    branch that says one. Each is driven with the defect it exists for."""

    PLATE = "vignola-doric-capital-profile"

    def _scaled(self, factor):
        def change(svg):
            import re
            return re.sub(r'"px_per_in":([\d.]+)',
                          lambda m: '"px_per_in":%.6f' % (float(m.group(1)) * factor), svg, count=1)
        return change

    def test_the_unplanted_plates_agree_so_each_verdict_below_is_the_plant(self):
        """The control. Without it a 'disagrees' below could be the plate and not the plant."""
        live = {(r["check"], r["subject"]): r["verdict"] for r in _rows()}
        for cid in ("P2", "P5", "P6", "P12"):
            assert live[(cid, self.PLATE)] == "agrees", cid
        assert live[("P9", "palladio-tuscan-cornice-profile")] == "agrees"
        assert live[("P1", "palladio-ionic-base-profile")] == "agrees"
        assert live[("P2", "palladio-doric-capital-profile")] == "agrees"
        assert live[("P13", "vignola-ionic-capital-profile")] == "agrees"
        assert live[("P8", "vignola-corinthian-capital-profile")] == "agrees"
        assert live[("P11", "vignola-doric-capital-profile")] == "agrees"
        assert live[("P10", "palladio-corinthian-cornice-profile")] == "agrees"

    def test_p5_sees_a_plate_drawn_at_a_scale_it_does_not_state(self, monkeypatch):
        got = _verdicts(monkeypatch, "P5", _planted(self.PLATE, self._scaled(1.1)))
        assert got == ["disagrees"], got

    def test_p6_sees_a_face_drawn_off_its_record(self, monkeypatch):
        got = _verdicts(monkeypatch, "P6", _planted(self.PLATE, self._scaled(1.1)))
        assert got == ["disagrees"], got

    def test_p9_sees_an_inherited_plate_that_stops_saying_so(self, monkeypatch):
        inherited = "palladio-tuscan-cornice-profile"      # Palladio states no Tuscan cornice (OQ 7)
        got = _verdicts(monkeypatch, "P9", _planted(inherited, lambda s: s.replace("INHERITED", "OWN")))
        assert got == ["disagrees"], got

    def test_p12_sees_a_committed_plate_nobody_re_rendered(self, monkeypatch):
        got = _verdicts(monkeypatch, "P12", _planted(self.PLATE, lambda s: s.replace("</svg>", "<g/></svg>")))
        assert got == ["disagrees"], got

    def test_p1_sees_a_plate_that_prints_a_column_it_is_not_drawn_at(self, monkeypatch):
        """WP-14.2 fixed the twelve Palladio plates that said "at a 24 in column" over a 12 in
        drawing, so P1 has no live disagreement; this is that defect put back."""
        got = _verdicts(monkeypatch, "P1", _planted(
            "palladio-ionic-base-profile", lambda s: s.replace("at a 12\u2033 column", "at a 24\u2033 column")))
        assert got == ["disagrees"], got

    def test_p2_sees_the_layout_floor_printed_as_relief(self, monkeypatch):
        """The other WP-14.2 defect put back: a plate whose ink draws no relief, printing the
        layout's own 1.00 in floor as if the record stated it."""
        def change(s):
            return s.replace("no relief drawn: no</text>", "1.00\u2033 of relief from the naked.</text>")
        got = _verdicts(monkeypatch, "P2", _planted("palladio-doric-capital-profile", change))
        assert got == ["disagrees"], got

    def test_p2_reads_no_relief_as_a_claim_of_zero_that_ink_can_contradict(self, monkeypatch):
        """"no relief" is read as zero rather than as a plate that printed nothing, so a plate
        saying it over ink that DOES project is a disagreement and not COULD NOT EVALUATE."""
        def change(s):
            return s.replace("2.75\u2033 of relief from the naked.",
                             "no relief: every published face is flush with the naked.")
        got = _verdicts(monkeypatch, "P2", _planted(self.PLATE, change))
        assert got == ["disagrees"], got

    def test_p8_sees_a_curve_inked_for_a_member_it_calls_not_constructed(self, monkeypatch):
        """WP-14.2 draws an unconstructed member as its envelope, so P8 has no live disagreement;
        this puts the swelling's arc back into one acanthus row of the committed plate."""
        import re
        plate = "vignola-corinthian-capital-profile"
        a, g, pl, rec = next(x for x in C._profile_assets() if x[0]["id"] == plate)
        acanthus = next(m for m in rec["members"] if m["id"] == "acanthus_row_1")

        def change(svg):
            def one(m):
                u, v = pl.model((float(m.group(1)), float(m.group(2))))
                if abs(v - acanthus["y_top_in"]) < 0.01 and u > pl.naked() + 0.01:
                    return "A 9 9 0 0 1 %s,%s" % (m.group(1), m.group(2))
                return m.group(0)
            fill = re.search(r'<path d="([^"]+)" fill="#[0-9a-fA-F]+"', svg)
            new_d = re.sub(r"L ([\d.]+),([\d.]+)", one, fill.group(1), count=0)
            return svg.replace(fill.group(1), new_d, 1)
        got = _verdicts(monkeypatch, "P8", _planted(plate, change))
        assert got == ["disagrees"], got

    def test_p10_sees_a_weak_member_left_unmarked_in_words_or_in_ink(self, monkeypatch):
        """WP-14.2 marked all 65 plates, so P10 has no live disagreement; both halves are put back."""
        import re
        plate = "palladio-corinthian-cornice-profile"
        no_words = _planted(plate, lambda s: re.sub(r", (?:low|medium) confidence", "", s))
        assert _verdicts(monkeypatch, "P10", no_words) == ["disagrees"]
        no_ink = _planted(plate, lambda s: re.sub(r'<path class="confidence"[^>]*/>', "", s))
        assert _verdicts(monkeypatch, "P10", no_ink) == ["disagrees"]

    def test_p11_sees_a_curve_drawn_straight_and_not_said(self, monkeypatch):
        """WP-14.2 made the three Doric capitals say their cymatium is drawn straight, so P11 has
        no live disagreement; this is that silence put back."""
        got = _verdicts(monkeypatch, "P11", _planted(
            "vignola-doric-capital-profile",
            lambda s: s.replace("CURVED MEMBER(S) DRAWN STRAIGHT", "CURVED MEMBER(S)")))
        assert got == ["disagrees"], got

    # P11's POPULATION IS TWO READERS ORed, AND THE DRIVE ABOVE REACHES ONE (WP-14.6's second audit,
    # M11). Its plate's straight member is a cyma reversa, curved by its profile KIND, so blinding
    # the NAME reader (`_CURVE_NAME` matching nothing) left the drive, the control and every census
    # row green: measured, 58 of the 171 members P11 judges fell out and nothing said so.
    P11_BY_KIND, P11_BY_NAME_ALONE = 113, 58

    def test_p11_judges_every_member_either_reader_calls_a_curve(self):
        """The premise, over the population P11 records it judged (`svg_census.POPULATION`): every
        published member whose profile KIND is a curve, read here from `ink_surfaces.CURVED` itself
        and not through the census's filter, plus the members only their NAME calls one -- pinned
        per reader on N2's precedent, because an agreement over fewer members is still an
        agreement. A count that moves is not a failure of the corpus; it is a change to account
        for in the commit that makes it."""
        C.CHECKS["P11"]["fn"]()
        judged = set(C.POPULATION["P11"])
        by_kind = {(a["id"], m["id"]) for a, g, pl, rec in C._profile_assets() if not rec["side_by_side"]
                   for m in rec["members"]
                   if rec["published"].get(m["id"]) and (m.get("profile") or "") in SURF.CURVED}
        assert len(by_kind) == self.P11_BY_KIND, len(by_kind)
        assert by_kind <= judged, sorted(by_kind - judged)[:5]
        assert len(judged - by_kind) == self.P11_BY_NAME_ALONE, (
            "P11 judged %d members only their name calls a curve, against %d when this was "
            "pinned: %s" % (len(judged - by_kind), self.P11_BY_NAME_ALONE, sorted(judged - by_kind)[:5]))
        assert len(judged) == len(C.POPULATION["P11"]), "a member judged twice"

    @staticmethod
    def _planted_record(asset_id, change):
        """One committed plate with its RECORD altered in memory by `change(rec)`."""
        for a, g, pl, rec in C._profile_assets():
            if a["id"] == asset_id:
                planted = copy.deepcopy(rec)
                change(planted)
                assert planted != rec, "the planted defect did not land"
                return [(a, g, pl, planted)]
        raise KeyError(asset_id)

    def _straight_by_both(self, m):
        assert (m.get("profile") or "") not in SURF.CURVED and not C._CURVE_NAME.search(m.get("name") or ""), (
            "the premise: %s is a straight member by both readers" % m["id"])

    def test_p11_sees_a_member_its_name_calls_a_curve_drawn_straight(self, monkeypatch):
        """A fillet renamed an ovolo -- the shape of WP-14.6's F7, where three members NAMED a
        curve were drawn square -- is judged by its name and convicts the plate, whose words count
        one straight curve and whose ink now holds two."""
        def change(rec):
            m = next(x for x in rec["members"] if x["id"] == "cap_fillet")
            self._straight_by_both(m)
            m["name"] = "Ovolo of the abacus"
        assert _verdicts(monkeypatch, "P11", self._planted_record(self.PLATE, change)) == ["disagrees"]

    def test_p11_sees_a_member_its_kind_calls_a_curve_drawn_straight(self, monkeypatch):
        def change(rec):
            m = next(x for x in rec["members"] if x["id"] == "cap_abacus")
            self._straight_by_both(m)
            m["profile"] = "cavetto"
        assert _verdicts(monkeypatch, "P11", self._planted_record(self.PLATE, change)) == ["disagrees"]

    def test_p13_sees_a_section_passed_off_as_the_capital(self, monkeypatch):
        """WP-14.2 made the Ionic capitals say their volute is not recorded, so P13 has no live
        disagreement; this is that silence put back."""
        got = _verdicts(monkeypatch, "P13", _planted(
            "vignola-ionic-capital-profile", lambda s: s.replace("NOT RECORDED: THE VOLUTE", "THE VOLUTE")))
        assert got == ["disagrees"], got

    def test_a_plate_with_no_frame_is_unjudged_and_not_a_crash(self, monkeypatch):
        import re
        stripped = _planted(self.PLATE, lambda s: re.sub(r" data-frame='[^']*'", "", s, count=1))
        for cid in ("P2", "P3", "P5", "P6"):
            assert _verdicts(monkeypatch, cid, stripped) == ["cne"], cid


class TestTheJavaScriptSurfaces:
    """Since WP-14.2 no O or R check has a live disagreement, so each is driven with the defect it
    exists for, and the unplanted control beside it must still agree; and every row that needs
    `node` must say COULD NOT EVALUATE without it, never agree."""

    @staticmethod
    def _orders_planted(monkeypatch, key, svg=None, info=None, reach=None):
        import copy
        run = C._orders_run()
        assert not isinstance(run, str), run
        planted = copy.deepcopy(run)
        if svg:
            planted["out"][key]["svg"] = svg(planted["out"][key]["svg"])
            assert planted["out"][key]["svg"] != run["out"][key]["svg"], "the plant did not land"
        if info:
            planted["out"][key]["info"] = info(planted["out"][key]["info"])
            assert planted["out"][key]["info"] != run["out"][key]["info"], "the plant did not land"
        if reach:
            planted["out"]["__reachable"] = reach(planted["out"]["__reachable"])
        monkeypatch.setattr(C, "_ORDERS", planted)

    @staticmethod
    def _got(cid):
        return {r["subject"]: r["verdict"] for r in C.CHECKS[cid]["fn"]()}

    def test_the_orders_page_carries_no_engine_of_its_own(self):
        """WP-14.2 deleted the page's port of stack_for, _synth_shaft and dimension(), its taper and
        its flute arithmetic. O2 and O3 cannot see a port come back while it agrees with Python --
        which the old one did, 156 of 156 -- so the absence is held here, by name."""
        import re
        tpl = open(os.path.join(C.ROOT, "build", "orders_template.html"), encoding="utf-8").read()
        # ANY WAY OF DEFINING ONE (WP-14.6, G10): the pattern read `function name(` alone, so
        # `const dimension = (pk, d) =>` -- the page's own idiom elsewhere -- would have come back
        # through it. Driven below on each form, so the pattern cannot narrow unseen.
        defines = lambda name: re.compile(  # noqa: E731
            r"(?:\bfunction\s+%(n)s\s*\(|\b(?:const|let|var)\s+%(n)s\s*=|\b%(n)s\s*:\s*(?:function\b|\()"
            r"|^\s*%(n)s\s*\([^)]*\)\s*\{)" % {"n": re.escape(name)}, re.M)
        for form in ("function dimension(pk, d) {", "const dimension = (pk, d) => {",
                     "let dimension = function (pk) {", "var dimension=pk=>pk", "  dimension: (pk) => pk,",
                     "  dimension(pk, d) {"):
            assert defines("dimension").search(form), form
        assert not defines("dimension").search("const g = dimension(pk, d);")
        for name in ("dimension", "synthShaft", "stackFor", "colRadiusFromGeometry", "geomMaxX"):
            assert not defines(name).search(tpl), name
        assert "height_parts" not in re.sub(r"s\.height_parts", "", tpl), \
            "the page multiplies a member's parts again"
        assert "fl/2.4" not in tpl.replace(" ", "")

    def test_o4_sees_an_unjudged_invariant_printed_fail(self, monkeypatch):
        import re
        key = "vignola-ionic@12-unjudged-invariant"
        self._orders_planted(monkeypatch, key, info=lambda s: re.sub(
            r'(<div class="inv"><span class="m )un">N/EV', r'\1no">FAIL', s, count=1))
        assert [r["verdict"] for r in C.CHECKS["O4"]["fn"]()] == ["disagrees"]

    def test_o4_sees_an_unjudged_invariant_printed_as_holding(self, monkeypatch):
        """WP-14.6, G1: the other direction, and the more dangerous one. O4 agreed with anything
        but FAIL, so an unjudged invariant printed "holds" -- a pass nobody measured -- agreed."""
        import re
        key = "vignola-ionic@12-unjudged-invariant"
        self._orders_planted(monkeypatch, key, info=lambda s: re.sub(
            r'(<div class="inv"><span class="m )un">N/EV', r'\1ok">holds', s, count=1))
        got = C.CHECKS["O4"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"] and "'holds'" in got[0]["detail"], got

    def test_o5_sees_a_pack_no_button_reaches(self, monkeypatch):
        self._orders_planted(monkeypatch, "vignola-ionic@12",
                             reach=lambda r: [p for p in r if p != "greek-doric"])
        got = self._got("O5")
        assert got["greek-doric"] == "disagrees" and got["moorish-arch"] == "agrees"

    def test_o6_sees_a_flute_line_dropped(self, monkeypatch):
        import re
        self._orders_planted(monkeypatch, "vignola-ionic@12", svg=lambda s: re.sub(
            r'<g transform="[^"]*"><path class="flute"[^>]*/></g>', "", s, count=1))
        got = self._got("O6")
        assert got["vignola-ionic"] == "disagrees" and got["vignola-corinthian"] == "agrees"

    def test_o7_sees_an_unpublished_member_unbracketed_or_uncounted(self, monkeypatch):
        import re
        self._orders_planted(monkeypatch, "palladio-ionic@12", svg=lambda s: re.sub(
            r'<g transform="[^"]*"><path class="unpub"[^>]*/></g>', "", s, count=1))
        got = self._got("O7")
        assert got["palladio-ionic"] == "disagrees" and got["gibbs-doric"] == "agrees"
        self._orders_planted(monkeypatch, "palladio-ionic@12",
                             info=lambda s: s.replace("14 member(s) drawn as a dashed bracket",
                                                      "13 member(s) drawn as a dashed bracket"))
        assert self._got("O7")["palladio-ionic"] == "disagrees"

    def test_o7_sees_a_complete_stack_that_stops_saying_so(self, monkeypatch):
        import re
        self._orders_planted(monkeypatch, "vignola-ionic@12", info=lambda s: re.sub(
            r"All \d+ member\(s\) publish a projection\.", "", s))
        got = self._got("O7")
        assert got["vignola-ionic"] == "disagrees" and got["vignola-corinthian"] == "agrees"

    def test_o8_sees_an_unconstructed_member_drawn_without_its_envelope(self, monkeypatch):
        import re
        run = C._orders_run()
        pid = next(c["pid"] for c in run["cases"] if c["key"] == c["pid"] + "@12"
                   and 'class="envelope"' in run["out"][c["key"]]["svg"])
        self._orders_planted(monkeypatch, pid + "@12", svg=lambda s: re.sub(
            r'<g transform="[^"]*"><path class="envelope"[^>]*/></g>', "", s, count=1))
        assert self._got("O8")[pid] == "disagrees"

    def test_o9_sees_a_straight_curve_left_unsaid(self, monkeypatch):
        self._orders_planted(monkeypatch, "vignola-ionic@12", info=lambda s: s.replace(
            "CURVED MEMBER(S) DRAWN STRAIGHT", "CURVED MEMBER(S)"))
        assert self._got("O9")["vignola-ionic"] == "disagrees"

    def test_o10_sees_an_assembly_named_under_the_wrong_datum(self, monkeypatch):
        self._orders_planted(monkeypatch, "vignola-ionic@12", info=lambda s: s.replace(
            "from the axis for the pedestal, base, shaft and capital",
            "from the axis for the pedestal, base and shaft").replace(
            "own naked for the architrave", "own naked for the capital, architrave"))
        got = self._got("O10")
        assert got["vignola-ionic"] == "disagrees" and got["vignola-corinthian"] == "agrees"

    @staticmethod
    def _plate_planted(monkeypatch, pid, **change):
        import copy
        run = C._plate_run()
        assert not isinstance(run, str), run
        planted = copy.deepcopy(run)
        for k, fn in change.items():
            planted["plate"][pid][k] = fn(planted["plate"][pid][k])
            assert planted["plate"][pid][k] != run["plate"][pid][k], "the plant did not land"
        monkeypatch.setattr(C, "_PLATEJS", planted)

    def test_r1_sees_a_frame_narrower_than_its_ink(self, monkeypatch):
        self._plate_planted(monkeypatch, "vignola-ionic", maxX=lambda x: x * 0.8)
        got = self._got("R1")
        assert got["vignola-ionic"] == "disagrees" and got["gibbs-doric"] == "agrees"

    def test_r2_sees_an_unpublished_member_left_unsaid_and_a_published_one_called_absent(self, monkeypatch):
        self._plate_planted(monkeypatch, "palladio-ionic", unrecorded=lambda u: u[1:])
        assert self._got("R2")["palladio-ionic"] == "disagrees"
        self._plate_planted(monkeypatch, "gibbs-doric", unrecorded=lambda u: u + ["frieze.metope"])
        got = self._got("R2")
        assert got["gibbs-doric"] == "disagrees" and got["vignola-ionic"] == "agrees"

    def test_r2_does_not_count_the_column_its_own_body(self):
        """palladio-doric and -tuscan leave the shaft body's projection null; the body IS the
        column, so neither the plate nor R2 counts it -- and R2 finds it from the record's own
        heights, not from the geometry's rule."""
        got = self._got("R2")
        assert got["palladio-doric"] == "agrees" and got["palladio-tuscan"] == "agrees"

    def test_o11_sees_an_alternative_left_out_and_unsaid(self, monkeypatch):
        self._orders_planted(monkeypatch, "benjamin-tuscan@12", info=lambda s: s.replace(
            "is not drawn: it is offered instead of the", "is not drawn instead of the"))
        got = self._got("O11")
        assert got["benjamin-tuscan"] == "disagrees" and got["benjamin-ionic"] == "agrees"

    def test_o11_sees_an_entablature_drawn_whole_and_unsaid(self, monkeypatch):
        self._orders_planted(monkeypatch, "palladio-corinthian@12", info=lambda s: s.replace(
            "The entablature is drawn whole, as", "The entablature, as"))
        assert self._got("O11")["palladio-corinthian"] == "disagrees"

    def test_r4_sees_the_plate_stop_saying_what_the_stack_left_out(self, monkeypatch):
        self._plate_planted(monkeypatch, "benjamin-corinthian", stackWords=lambda w: "")
        got = self._got("R4")
        assert got["benjamin-corinthian"] == "disagrees" and got["benjamin-ionic"] == "agrees"

    def test_r3_sees_an_assembly_named_under_the_wrong_datum(self, monkeypatch):
        self._plate_planted(monkeypatch, "vignola-ionic", datumWords=lambda w: w.replace(
            "and from each member’s own naked for the architrave",
            "and from each member’s own naked for the capital, architrave"))
        got = self._got("R3")
        assert got["vignola-ionic"] == "disagrees" and got["gibbs-doric"] == "agrees"

    # O1 READS THE COMMITTED PAGE, THROUGH GIT (WP-14.6's second audit, C6). It read the working
    # tree's, and `check_all` runs `build.py` first, whose step 6 rewrites that file from the
    # generator -- so in the gating run O1 held the generator to its own output and a page committed
    # without a build agreed. Measured: the generator moved, the page left as committed, the build's
    # own step run, and O1 said AGREES over a HEAD page it did not match. Each state below is a real
    # git repository in a temporary directory, so the reader under test is the one that runs.
    @staticmethod
    def _repo(root, page=None, commit=True):
        """A git repository at `root` whose tree holds `page` as dist/orders.html (or no page at
        all), committed or left on an unborn branch. Outside the repository under test."""
        root.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ, GIT_AUTHOR_NAME="census", GIT_AUTHOR_EMAIL="census@example.invalid",
                   GIT_COMMITTER_NAME="census", GIT_COMMITTER_EMAIL="census@example.invalid")
        for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
            env.pop(k, None)

        def git(*a):
            subprocess.run(["git", *a], cwd=root, env=env, check=True, capture_output=True)

        git("init", "-q")
        if page is not None:
            (root / "dist").mkdir()
            (root / "dist" / "orders.html").write_text(page, encoding="utf-8")
        else:
            (root / "README").write_text("no page here\n", encoding="utf-8")
        if commit:
            git("add", "-A")
            git("commit", "-q", "-m", "fixture")
        return root

    def _o1_at(self, monkeypatch, root):
        monkeypatch.setattr(C, "ROOT", str(root))
        got = C.CHECKS["O1"]["fn"]()
        assert len(got) == 1, got
        return got[0]

    def test_o1_reads_the_page_head_holds_and_agrees_where_it_is_current(self, monkeypatch, tmp_path):
        """The control, through the same instrument as every drive below: a repository whose HEAD
        holds the page the generator builds now agrees -- and the real repository does too."""
        built = C.SURF._mod("render_orders").build_page()
        r = self._o1_at(monkeypatch, self._repo(tmp_path / "current", built))
        assert r["verdict"] == "agrees", r
        monkeypatch.undo()
        state, got = C._committed_orders_page()
        if state == "cne":
            pytest.skip("COULD NOT EVALUATE here, and not a pass: " + got)
        assert state == "page" and got == built, "HEAD's dist/orders.html is stale on this commit"

    def test_o1_sees_a_page_committed_without_a_build(self, monkeypatch, tmp_path):
        """A HEAD page the generator no longer builds disagrees -- even with a CURRENT page in the
        working tree beside it, which is the state `build.py` leaves the gating run in and the one
        the old reading called agreement."""
        built = C.SURF._mod("render_orders").build_page()
        stale = built + "<!-- committed before the generator moved -->"
        root = self._repo(tmp_path / "stale", stale)
        (root / "dist" / "orders.html").write_text(built, encoding="utf-8")      # the build ran
        r = self._o1_at(monkeypatch, root)
        assert r["verdict"] == "disagrees" and "stale" in r["detail"], r
        assert "the working tree's page is current and uncommitted" in r["detail"], r
        # ...and the clause is about THIS root's working tree. The same stale commit with the build
        # NOT run leaves the working-tree page stale too, and the clause must not be said: it was
        # read off the module's own `ORDERS_PAGE`, bound at import to the real checkout, so under
        # a moved `ROOT` it described another tree -- the `root=` seam wired in one place and not
        # its neighbour (WP-13.2), found by writing this half.
        monkeypatch.undo()
        r = self._o1_at(monkeypatch, self._repo(tmp_path / "unbuilt", stale))
        assert r["verdict"] == "disagrees" and "stale" in r["detail"], r
        assert "current and uncommitted" not in r["detail"], r

    def test_o1_sees_a_head_that_holds_no_page(self, monkeypatch, tmp_path):
        r = self._o1_at(monkeypatch, self._repo(tmp_path / "pageless", page=None))
        assert r["verdict"] == "disagrees" and "HEAD holds no dist/orders.html" in r["detail"], r

    def test_o1_cannot_evaluate_where_the_committed_page_cannot_be_read(self, monkeypatch, tmp_path):
        """Four states in which there is no committed page to read, each COULD NOT EVALUATE naming
        which -- never a comparison with the working tree, which is the reading that could not
        fail."""
        built = C.SURF._mod("render_orders").build_page()
        bare = tmp_path / "not-a-repo"
        bare.mkdir()
        r = self._o1_at(monkeypatch, bare)
        assert r["verdict"] == "cne" and "not in a git work tree" in r["detail"], r

        r = self._o1_at(monkeypatch, self._repo(tmp_path / "unborn", built, commit=False))
        assert r["verdict"] == "cne" and "HEAD names no commit" in r["detail"], r

        outer = self._repo(tmp_path / "outer", built)
        inner = outer / "dist"                                   # inside a tree, not its top
        r = self._o1_at(monkeypatch, inner)
        assert r["verdict"] == "cne" and "not the top of its git work tree" in r["detail"], r

        real_which = C.shutil.which
        monkeypatch.setattr(C.shutil, "which", lambda name: None if name == "git" else real_which(name))
        r = self._o1_at(monkeypatch, outer)
        assert r["verdict"] == "cne" and "git is not installed" in r["detail"], r

    def test_o2_and_o3_see_a_section_drawn_at_a_scale_it_does_not_state(self, monkeypatch):
        import copy
        import re
        run = C._orders_run()
        assert not isinstance(run, str), run
        planted = copy.deepcopy(run)
        key = "vignola-ionic@12"
        planted["out"][key]["svg"] = re.sub(
            r'"px_per_in":([\d.]+)', lambda m: '"px_per_in":%r' % (float(m.group(1)) * 1.1),
            planted["out"][key]["svg"], count=1)
        assert planted["out"][key]["svg"] != run["out"][key]["svg"], "the plant did not land"
        monkeypatch.setattr(C, "_ORDERS", planted)
        for cid in ("O2", "O3"):
            got = {r["subject"]: r["verdict"] for r in C.CHECKS[cid]["fn"]()}
            assert got[key] == "disagrees", cid
            assert got["vignola-ionic@24"] == "agrees", cid          # the control, unplanted

    # Every check that runs javascript, spelled out so a reader sees them. The list is HELD to the
    # call graph below: it once named fourteen of these and left out the bench's two (B1, B2) and the
    # tracing canvas (TR1), which WP-14.4 added -- three checks whose unjudged state no test read.
    NODE_CHECKS = ("O2", "O3", "O4", "O5", "O6", "O7", "O8", "O9", "O10", "O11",
                   "R1", "R2", "R3", "R4", "B1", "B2", "TR1")

    def test_the_javascript_list_is_every_check_that_reaches_node(self):
        """A check is javascript-backed if its function -- or anything it calls in the census,
        transitively -- runs `node`. Derived, so a new check cannot be born outside the list.

        READ OFF THE SYNTAX TREE (WP-14.6's second audit, M12). The first version matched the
        TEXT `subprocess.run(["node"`, so the same call spelled `subprocess.run(args=["node", ...])`,
        with the command in a variable, through `shutil.which("node")`, or by `Popen` was a check
        born outside the list: measured, a node call planted in P12 in the keyword spelling left
        this test green, and respelling the bench's real call that way made it convict B1 and B2
        of NOT reaching node. `_node_backed` reads the call, and is driven below on every
        spelling it claims."""
        backed = _node_backed(open(C.__file__, encoding="utf-8").read())
        assert {"_orders_run", "_plate_run", "_bench_run", "tr1"} <= backed, (
            "the four functions that run node today are not all found -- the derivation is "
            "reading nothing: %s" % sorted(backed))
        derived = {cid for cid, c in C.CHECKS.items() if c["fn"].__name__ in backed}
        assert derived == set(self.NODE_CHECKS), (sorted(derived - set(self.NODE_CHECKS)),
                                                  sorted(set(self.NODE_CHECKS) - derived))

    @pytest.mark.parametrize("src", [
        'import subprocess\ndef f():\n    subprocess.run(["node", "x.mjs"])\n',
        'import subprocess\ndef f():\n    subprocess.run(args=["node", "x.mjs"], capture_output=True)\n',
        'import subprocess\ndef f(rest):\n    subprocess.Popen(["node"] + rest)\n',
        'import subprocess, shutil\ndef f():\n    subprocess.check_output([shutil.which("node"), "x"])\n',
        'import subprocess\nNODE = "node"\ndef f():\n    subprocess.run([NODE, "x"])\n',
        'import subprocess\ndef f():\n    cmd = ["node", "x"]\n    subprocess.run(cmd)\n',
        'import subprocess\ndef f():\n    subprocess.run("node x.mjs", shell=True)\n',
        'import subprocess as sp\ndef f():\n    sp.check_call(("/usr/bin/node", "x"))\n',
        'from subprocess import run as go\ndef f():\n    go(["node", "x"])\n',
        'import os\ndef f():\n    os.system("node x.mjs")\n',
        'import subprocess\ndef f():\n    def inner():\n        subprocess.run(["node"])\n    return inner()\n',
    ])
    def test_the_node_reader_finds_every_spelling_of_a_node_call(self, src):
        assert _node_backed(src) == {"f"}, src

    @pytest.mark.parametrize("src", [
        'import subprocess, shutil\ndef f():\n    git = shutil.which("git")\n    subprocess.run([git, "show"])\n',
        'import subprocess\ndef f():\n    subprocess.run(["python3", "node.py"])\n',
        'import shutil\ndef f():\n    return shutil.which("node") is None\n',
        'def f():\n    return "node"\n',
        'import subprocess\ndef f():\n    subprocess.run("nodemon x.js", shell=True)\n',
    ])
    def test_the_node_reader_is_not_fooled_by_a_call_that_runs_something_else(self, src):
        assert _node_backed(src) == set(), src

    def test_the_node_reader_carries_a_call_through_every_caller(self):
        src = ('import subprocess\ndef f():\n    subprocess.run(["node"])\n'
               'def g():\n    return f()\ndef h():\n    return g\ndef k():\n    return 1\n')
        assert _node_backed(src) == {"f", "g", "h"}

    def test_without_node_every_javascript_row_is_unjudged(self, monkeypatch):
        monkeypatch.setattr(C.shutil, "which", lambda name: None)
        monkeypatch.setattr(C, "_ORDERS", None)
        monkeypatch.setattr(C, "_PLATEJS", None)
        monkeypatch.setattr(C, "_BENCH", None)
        for cid in self.NODE_CHECKS:
            got = C.CHECKS[cid]["fn"]()
            assert got and all(r["verdict"] == "cne" for r in got), (cid, got)
            assert "node" in got[0]["detail"], got[0]

    def test_the_plate_fixtures_are_what_the_server_serves(self):
        r = subprocess.run([sys.executable, os.path.join(C.ROOT, "tests", "fixtures", "proportions_plate",
                                                         "generate.py"), "--check"],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr


class TestTheOrderStackCanDisagree:
    """E1-E4 agree on every pack since WP-14.2 step 7, so each is driven with the defect it
    exists for, on the geometry its own reader reads."""

    def test_e4_sees_a_die_drawn_at_a_stand_in(self, monkeypatch):
        """The 1.2 x R stand-in the old E4 assumed and could not see removed, planted back."""
        PROF = C.SURF._mod("profiles")
        real = PROF.pack_geometry

        def planted(dim, column=None, projection_datum=None, **kw):
            g = real(dim, column, projection_datum, **kw)
            if dim.get("pack") == "palladio-ionic":
                for a in g["assemblies"]:
                    if a["id"] == "pedestal":
                        a["naked_in"] = g["lower_radius_in"] * 1.2
            return g
        monkeypatch.setattr(PROF, "pack_geometry", planted)
        got = {r["subject"]: r["verdict"] for r in C.CHECKS["E4"]["fn"]()}
        assert got["palladio-ionic"] == "disagrees" and got["vignola-ionic"] == "agrees"

    def test_e4_sees_a_derived_die_that_does_not_carry_the_plinth(self, monkeypatch):
        PROF = C.SURF._mod("profiles")
        real = PROF.pack_geometry

        def planted(dim, column=None, projection_datum=None, **kw):
            g = real(dim, column, projection_datum, **kw)
            if dim.get("pack") == "benjamin-corinthian":
                for a in g["assemblies"]:
                    if a["id"] == "pedestal":
                        a["naked_in"] -= 1.0
            return g
        monkeypatch.setattr(PROF, "pack_geometry", planted)
        assert {r["subject"]: r["verdict"] for r in C.CHECKS["E4"]["fn"]()}["benjamin-corinthian"] == "disagrees"


class TestTheBuildingSheetsCanDisagree:
    """V7, V9 and V13 agree on every sheet the corpus draws today, so the corpus never reaches the
    branch that says otherwise. Each is driven with the defect it exists for."""

    def _one(self, pid, face=None):
        rec = C._sheets()[pid]
        face = face or rec["elev"]["entrance_face"]
        return rec, face, rec["faces"][face]

    def test_v7_sees_a_head_that_is_not_a_circle(self, monkeypatch):
        import re
        rec, face, svg = self._one("tidewater-georgian-careful")
        # the heads are circular arcs since WP-14.3; plant a parabola 60 px tall in place of one,
        # which is far from any circle
        planted = re.sub(
            r'(<path class="arch w-med" d="M ([\d.]+),([\d.]+)) A [\d.]+,[\d.]+ 0 0 1 ([\d.]+),([\d.]+)',
            lambda m: "%s Q %.2f,%.2f %s,%s" % (m.group(1), (float(m.group(2)) + float(m.group(4))) / 2.0,
                                                float(m.group(3)) - 60.0, m.group(4), m.group(5)),
            svg, count=1)
        assert planted != svg, "the plant did not land"
        monkeypatch.setattr(C, "_elev_and_sweep", lambda: iter([("planted", rec["elev"], planted)]))
        assert [r["verdict"] for r in C.CHECKS["V7"]["fn"]()] == ["disagrees"]

    def test_v6_counts_the_panels_in_the_leaf_and_not_the_shutters_over_it(self, monkeypatch):
        """Corrected at WP-14.3: V6 counted every panel within the garage door's WIDTH, so the
        shutters of the window over bad-03's garage door were read as the door's own panels (10
        against 6). A panel planted over the door is not counted; the same panel planted in the
        leaf is, so the bound is neither missing nor blind."""
        pid = "bad-03-narrow-lot-townhome"
        rec = C._sheets()[pid]
        EL = C.SURF._mod("elevation")
        door = [x for x in EL.opening_rects(rec["elev"], "S")["rects"] if x["kind"] == "door"][0]
        types = {r["id"]: d.get("type") for lv in rec["placed"]["levels"] for r in lv["rooms"]
                 for d in r.get("doors") or [] if d.get("to") == "exterior"}
        assert types.get(door["room"]) == "garage", "the premise: the door on S is the garage's"
        pl = C._face_plate(C.IR.Ink(rec["faces"]["S"]))
        x0 = C.IR.from_model(pl, door["x0_in"] / 12.0, 0)[0]
        head = C.IR.from_model(pl, 0, door["head_in"] / 12.0)[1]

        def count(y):
            svg = rec["faces"]["S"].replace(
                "</svg>", '<rect class="pnl w-fine" x="%.1f" y="%.1f" width="20.0" height="30.0"/>'
                "</svg>" % (x0 + 10.0, y))
            monkeypatch.setitem(rec, "faces", dict(rec["faces"], S=svg))
            row = {r["subject"]: r for r in C.CHECKS["V6"]["fn"]()}[pid + "/S"]
            return int(row["detail"].split()[0]) if row["detail"] else 0

        monkeypatch.setitem(rec, "faces", dict(rec["faces"]))
        before = {r["subject"]: r for r in C.CHECKS["V6"]["fn"]()}[pid + "/S"]
        n = int(before["detail"].split()[0]) if before["detail"] else 0
        assert count(head - 80.0) == n, "a panel over the door was counted as the door's"
        assert count(head + 10.0) == n + 1, "a panel in the leaf was not counted"

    def test_v16_sees_a_surround_neither_drawn_nor_said(self, monkeypatch):
        """No surface draws a window surround, so V16 agrees only on the sheet's words. Take the
        words away from one style and V16 convicts that style and no other."""
        sweep = C._style_sweep()
        sid = "tidewater-georgian"
        el, svg = sweep[sid]
        planted = svg.replace("WINDOW SURROUND NOT DRAWN", "WINDOW NOTE")
        assert planted != svg, "the premise: this sheet says its surround is not drawn"
        monkeypatch.setitem(sweep, sid, (el, planted))
        got = {r["subject"]: r["verdict"] for r in C.CHECKS["V16"]["fn"]()}
        assert got[sid] == "disagrees" and got["colonial-revival"] == "agrees", got

    def test_v9_sees_the_renderers_own_fallbacks_when_the_record_gives_no_figure(self, monkeypatch):
        import copy
        RE = C.SURF._mod("render_elevation")
        rec, face, _svg = self._one("tidewater-georgian-careful", "E")
        el = copy.deepcopy(rec["elev"])
        assert el.get("chimney_stack_plan_in"), "the premise: this record states a stack size"
        el["chimney_stack_plan_in"] = None                   # the renderer falls back to 22 in
        planted = C._render(RE.render_elevation, el, face="E")
        # WP-14.3 refuses the stack and says so: the honest sheet agrees
        monkeypatch.setattr(C, "_elev_and_sweep", lambda: iter([("planted", el, planted)]))
        got = C.CHECKS["V9"]["fn"]()
        assert [r["verdict"] for r in got] == ["agrees"], got
        # the refusal left unsaid, and the old fallback put back: both disagree
        silent = planted.replace("STACKS NOT DRAWN", "STACKS")
        assert silent != planted, "the premise: the sheet says the stacks are not drawn"
        monkeypatch.setattr(C, "_elev_and_sweep", lambda: iter([("planted", el, silent)]))
        got = C.CHECKS["V9"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"] and "neither drawn nor said" in got[0]["detail"], got
        drawn = C._render(RE.render_elevation, copy.deepcopy(rec["elev"]), face="E")
        assert '"ch' in drawn or "class='ch" in drawn or 'class="ch' in drawn, "the premise: a sized stack is drawn"
        monkeypatch.setattr(C, "_elev_and_sweep", lambda: iter([("planted", el, drawn)]))
        got = C.CHECKS["V9"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"] and "no record states" in got[0]["detail"], got

    def test_v9_sees_a_keystone_drawn_or_left_unsaid(self, monkeypatch):
        """WP-14.6, G4. The test above drives V9's stack half only; its keystone half was reached
        by the sweep and driven by nothing. `georgian-revival`'s canonical head is keyed and no
        record gives the keystone a width, so its sheet says KEYSTONE NOT DRAWN. Take the words
        away and V9 convicts; draw a keystone and it convicts on the other clause."""
        sweep = C._style_sweep()
        sid = "georgian-revival"
        el, svg = sweep[sid]
        heads = [sw.get("head_treatment") or {} for sw in el.get("storey_windows") or []]
        assert any(h.get("keystone") and not h.get("keystone_width_in") for h in heads), \
            "the premise: a keyed head with no stated keystone width"
        monkeypatch.setattr(C, "_elev_and_sweep", lambda: iter([("planted", el, svg)]))
        assert [r["verdict"] for r in C.CHECKS["V9"]["fn"]()] == ["agrees"]
        silent = svg.replace("KEYSTONE NOT DRAWN", "KEYSTONE")
        assert silent != svg, "the premise: the sheet says the keystone is not drawn"
        monkeypatch.setattr(C, "_elev_and_sweep", lambda: iter([("planted", el, silent)]))
        got = C.CHECKS["V9"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"] and "keystone with no width" in got[0]["detail"], got
        drawn = svg.replace("</svg>", '<rect class="arch" x="100" y="100" width="6" height="9"/></svg>')
        monkeypatch.setattr(C, "_elev_and_sweep", lambda: iter([("planted", el, drawn)]))
        got = C.CHECKS["V9"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"] and "keystone drawn at a width" in got[0]["detail"], got

    def test_v13_sees_an_inset_drawn_at_a_scale_it_does_not_state(self, monkeypatch):
        import copy
        import re
        rec, face, svg = self._one("tidewater-georgian-careful")
        planted = re.sub(r'("id":"inset","proj":"profile","unit":"in","px_per_in":)([\d.]+)',
                         lambda m: m.group(1) + repr(float(m.group(2)) * 1.1), svg, count=1)
        assert planted != svg, "the plant did not land"
        sheets = copy.copy(C._sheets())
        one = dict(sheets["tidewater-georgian-careful"])
        one["faces"] = {face: planted}
        monkeypatch.setattr(C, "_SHEETS", {"tidewater-georgian-careful": one})
        assert [r["verdict"] for r in C.CHECKS["V13"]["fn"]()] == ["disagrees"]


_TW_AT = {}


def _tidewater_at(date):
    """The Tidewater house placed and drawn as the census draws a shipped plan, its record dated
    `date` (WP-16.4). The kit's dated bans are read at the house's date (ruled 30 Sep 2026, A3), so
    a specimen that needs the sidelights the kit forbids at the record's own 1765 is the same house
    dated outside the ban. Placed afresh, so the placer reserves the run the date's own
    composition asks for."""
    if date not in _TW_AT:
        G, ST, RF, EL = (SURF._mod(n) for n in ("geometry", "structure", "roof", "elevation"))
        plan = json.load(open(os.path.join(C.ROOT, "plans", "tidewater-georgian-careful.json")))
        plan.setdefault("context", {})["date_of_representation"] = date
        placed = G.solve(copy.deepcopy(plan), engine="heuristic")
        sec = ST.build_section(placed, None, geometry_result=placed)
        rf = RF.build_roof(placed, None, section=sec)
        _TW_AT[date] = EL.build_elevation(placed, None, section=sec, roof=rf)
    return _TW_AT[date]


class TestTheRefusalsAreSaid:
    """V22 (WP-14.6's second audit, W3). `_clearances` refuses a sidelight pair or a shutter pair
    that would stand over a neighbour and the legend says so; V20 reads the INK, which an honoured
    refusal leaves blank whether or not it is said, so deleting either sentence -- or printing the
    rooms' count where the windows' belongs -- moved nothing in the census but three of V3's rows
    by coincidence. V22 agrees on every sheet today, so each defect is planted here. The sentences
    are read by their PREFIXES, counts and room ids and never by the explanation after them, so a
    reworded tail cannot turn these red; each plant says what it changed, and lands or fails."""

    SHUTTERED = "good-05-lobby-gallery-mansion/W"    # the face the leaf refusal is DRIVEN on
    SIDELIT = "tidewater-georgian-careful/S"         # the front the sidelight refusal is DRIVEN on
    FOOT_IN = 12.0     # the wall the placer kept between two windows before WP-16.6 (MIN_SOLID_FT)

    @staticmethod
    def _all():
        return {s: (el, svg) for s, el, svg in C._elev_and_sweep()}

    @classmethod
    def _face(cls):
        return cls.SHUTTERED.split("/")[1]

    @classmethod
    def _shuttered(cls):
        """good-05's west face with each room's two sashes driven back a foot apart, where the
        placer seated them before WP-16.6, so in each pier the two windows' leaves lie over one
        another and both rooms' windows are refused their leaves; and that record rendered, so the
        refusal is the record and the ink of one drawing. Each pair moves about its own midpoint,
        and every field the rect is read from moves together: `cx_in` and `u_ft` with the face,
        and `along_ft` against it where the face is drawn as seen (R2, WP-16.3).

        RE-CUT 1 OCT 2026 (WP-16.6). R5 seats two windows at least 1.0 x the wider apart, and a
        wall that wide holds both neighbours' half-width leaves. So over the census's 85
        elevation sheets the windows refused their leaves went 193 -> 1: one window, on good-05's
        east face, over one room. The premise this class was written on, `spec-builder-colonial/S`
        refusing leaves over two rooms, ran out exactly as the control below was written to
        notice, and the refusal is driven now, as the sidelight's was at WP-15.6. Before WP-16.6
        this same face refused five windows over these two rooms."""
        el = copy.deepcopy(cls._all()[cls.SHUTTERED][0])
        front = el["faces"][cls._face()]
        sgn = -1.0 if front.get("mirrored") else 1.0
        rooms = {}
        for p in front["placed"]:
            if p["kind"] == "window":
                rooms.setdefault((p["room"], p["storey"]), []).append(p)
        driven = 0
        for ws in rooms.values():
            if len(ws) != 2:
                continue
            assert ws[0]["width_in"] == ws[1]["width_in"], "the drive assumes a pair of one width"
            ws.sort(key=lambda p: p["cx_in"])
            mid = (ws[0]["cx_in"] + ws[1]["cx_in"]) / 2.0
            half = (ws[0]["width_in"] + cls.FOOT_IN) / 2.0
            for p, want in zip(ws, (mid - half, mid + half)):
                d_in = want - p["cx_in"]
                p["cx_in"] = want
                p["u_ft"] = round(p["u_ft"] + d_in / 12.0, 4)
                p["along_ft"] += sgn * d_in / 12.0
            driven += 1
        assert driven == 2, "the premise: two rooms on this face carry two sashes each"
        return el, C._render(C.SURF._mod("render_elevation").render_elevation, el, face=cls._face())

    @classmethod
    def _sidelit(cls):
        """The Tidewater front with its passage window driven back to where the placer seated it
        before Phase 15's WP-15.6, 12 in from the leaf, so the doorcase refuses its sidelight pair;
        and that record rendered, so the pair is the record and the ink of one drawing. WP-15.6
        reserves the wall beside the doorcase, so no shipped sheet refuses a sidelight pair any
        more: this premise ran out exactly as the control below was written to notice, and the
        refusal is driven now. Every field the rect is read from is shifted together."""
        # RE-CUT 30 SEP 2026 (WP-16.4): the shipped record is dated 1765, and
        # georgian-colonial-american forbids the sidelights for 1700-1780, so at its own date the
        # doorcase composes no pair for the placer to refuse. The specimen is the same house dated
        # 1790, outside the ban, where the pair is composed and the drive can refuse it for want of
        # wall; V22 reads the record the sheet is drawn from, so the date travels with it.
        el = copy.deepcopy(_tidewater_at(1790))
        EL = C.SURF._mod("elevation")
        assert el["entrance"]["sidelights_present"], "the premise: at 1790 the pair is composed"
        ctl = next(r for r in EL.opening_rects(el, "S")["rects"] if r.get("entrance"))
        win = max((p for p in el["faces"]["S"]["placed"] if p["kind"] == "window"
                   and p["storey"] == ctl["storey"] and p["cx_in"] < ctl["cx_in"]),
                  key=lambda p: p["cx_in"])
        d_in = (ctl["x0_in"] - 12.0 - win["width_in"] / 2.0) - win["cx_in"]
        win["cx_in"] += d_in
        win["u_ft"] = round(win["u_ft"] + d_in / 12.0, 4)
        win["along_ft"] += d_in / 12.0
        return el, C._render(C.SURF._mod("render_elevation").render_elevation, el, face="S")

    @staticmethod
    def _v22(monkeypatch, planted):
        monkeypatch.setattr(C, "_elev_and_sweep", lambda: iter(planted))
        return {r["subject"]: r for r in C.CHECKS["V22"]["fn"]()}

    @staticmethod
    def _refused(el, face, key):
        return [r for r in C.SURF._mod("elevation").opening_rects(el, face)["rects"] if r.get(key)]

    def test_the_premise_both_sheets_refuse_something_and_say_so(self, monkeypatch):
        """The control. Without it a 'disagrees' below could be the plate and not the plant."""
        a = self._all()
        el, _svg = a[self.SHUTTERED]
        assert not self._refused(el, self._face(), "shutters_refused"), (
            "the premise: the shipped good-05 west face refuses no leaves -- since WP-16.6 the "
            "pier between its windows holds them -- so the refusal is driven")
        shut_el, shut_svg = self._shuttered()
        wins = self._refused(shut_el, self._face(), "shutters_refused")
        assert len(wins) >= 2 and len({r["room"] for r in wins}) >= 2, (
            "the drive landed: this face refuses leaves over more than one room")
        assert not self._refused(shut_el, self._face(), "sidelights_refused"), (
            "the premise: and no sidelights")
        el, _svg = a[self.SIDELIT]
        assert not self._refused(el, "S", "sidelights_refused"), (
            "the premise: the shipped Tidewater front refuses no pair for want of wall -- since "
            "WP-16.4 its kit forbids the pair at 1765, and before that WP-15.6 reserved its run -- "
            "so the refusal is driven")
        el, svg = self._sidelit()
        assert self._refused(el, "S", "sidelights_refused"), "the drive landed: this face refuses sidelights"
        got = self._v22(monkeypatch, [(self.SHUTTERED, shut_el, shut_svg), (self.SIDELIT, el, svg)])
        assert got[self.SHUTTERED]["verdict"] == "agrees", got[self.SHUTTERED]
        assert got[self.SIDELIT]["verdict"] == "agrees", got[self.SIDELIT]

    def _planted(self, monkeypatch, subject, change):
        el, svg = self._sidelit() if subject == self.SIDELIT else self._shuttered()
        assert subject in (self.SIDELIT, self.SHUTTERED), subject
        planted = change(svg)
        assert planted != svg, "the plant did not land"
        return self._v22(monkeypatch, [(subject, el, planted)])[subject]

    def test_v22_sees_the_shutter_sentence_left_out(self, monkeypatch):
        r = self._planted(monkeypatch, self.SHUTTERED,
                          lambda s: re.sub(r"<text[^>]*>SHUTTERS NOT DRAWN ON[^<]*</text>", "", s))
        assert r["verdict"] == "disagrees" and "prints 0 SHUTTERS NOT DRAWN line(s)" in r["detail"], r

    def test_v22_sees_the_windows_miscounted(self, monkeypatch):
        r = self._planted(monkeypatch, self.SHUTTERED, lambda s: re.sub(
            r"(SHUTTERS NOT DRAWN ON )(\d+)", lambda m: m.group(1) + str(int(m.group(2)) - 1), s, count=1))
        assert r["verdict"] == "disagrees" and "the sheet counts" in r["detail"], r

    def test_v22_sees_a_room_left_unnamed(self, monkeypatch):
        el, _svg = self._shuttered()
        room = sorted({r["room"] for r in self._refused(el, self._face(), "shutters_refused")})[0].upper()

        def change(svg):
            def drop(m):
                return re.sub(r"(?<![A-Z0-9_-])%s(?![A-Z0-9_-])(, )?" % re.escape(room), "", m.group(0))
            return re.sub(r">SHUTTERS NOT DRAWN ON[^<]*<", drop, svg)
        r = self._planted(monkeypatch, self.SHUTTERED, change)
        assert r["verdict"] == "disagrees" and (
            "%s's refused leaves are not named" % room.lower()) in r["detail"].lower(), r

    def test_v22_sees_the_sidelight_sentence_left_out(self, monkeypatch):
        r = self._planted(monkeypatch, self.SIDELIT,
                          lambda s: re.sub(r"<text[^>]*>SIDELIGHTS NOT DRAWN[^<]*</text>", "", s))
        assert r["verdict"] == "disagrees" and "the sheet says 0" in r["detail"], r

    def test_v22_sees_a_refusal_said_that_the_record_does_not_make(self, monkeypatch):
        r = self._planted(monkeypatch, self.SHUTTERED, lambda s: s.replace(
            "</svg>", '<text class="dm" x="0" y="0">SIDELIGHTS NOT DRAWN — PLANTED</text></svg>'))
        assert r["verdict"] == "disagrees" and "refuses 0 doorcase(s)" in r["detail"], r

    def test_v22_owes_a_line_for_every_class_of_refusal(self, monkeypatch):
        """The record may refuse one window's leaves for several CLASSES of reason
        (`shutters_refused_by`), and the legend prints them GROUPED (audit, 27 Sep 2026): one total
        line counting each window once, then a line per reason, "· k (ROOMS): why", counting each
        window under every reason it carries -- and the total says a window refused twice is counted
        under both. Given two classes on every refused window, a legend with no line of reason is
        short by two; the grouped legend agrees; and the same legend without its counted-under-both
        clause disagrees. Written against the RECORD, so it reads the classes whenever the record
        carries them. (This test was first written against one full line per class, before the
        grouped legend existed.)"""
        el, svg = self._shuttered()
        EL = C.SURF._mod("elevation")
        real = EL.opening_rects

        def classed(elev, face):
            got = real(elev, face)
            for r in got["rects"]:
                if r.get("shutters_refused"):
                    r["shutters_refused_by"] = ["corner", "opening"]
            return got

        wins = self._refused(el, self._face(), "shutters_refused")
        monkeypatch.setattr(EL, "opening_rects", classed)
        bare = re.sub(r"<text[^>]*>· [^<]*</text>", "", svg)
        r = self._v22(monkeypatch, [(self.SHUTTERED, el, bare)])[self.SHUTTERED]
        assert r["verdict"] == "disagrees" and "2 class(es)" in r["detail"], r
        rooms = ", ".join(sorted({x["room"].upper() for x in wins}))
        both = " (A WINDOW REFUSED FOR TWO REASONS IS COUNTED UNDER BOTH)"

        def grouped(clause):
            head = ('<text class="dm" x="0" y="0">SHUTTERS NOT DRAWN ON %d WINDOW(S) — %s — A LEAF THAT '
                    'CANNOT SWING ONTO WALL CANNOT BE HUNG%s:</text>' % (len(wins), rooms, clause))
            lines = "".join('<text class="dm" x="0" y="%d">· %d (%s): %s</text>' % (i + 1, len(wins), rooms, why)
                            for i, why in enumerate(("CORNER", "OPENING")))
            return re.sub(r"<text[^>]*>SHUTTERS NOT DRAWN ON[^<]*</text>", "", bare).replace(
                "</svg>", head + lines + "</svg>")
        r = self._v22(monkeypatch, [(self.SHUTTERED, el, grouped(both))])[self.SHUTTERED]
        assert r["verdict"] == "agrees", r
        r = self._v22(monkeypatch, [(self.SHUTTERED, el, grouped(""))])[self.SHUTTERED]
        assert r["verdict"] == "disagrees" and "counted under both" in r["detail"], r


class TestTheKitRefusalIsHeldBothWays:
    """V2 (WP-16.4, R3). Every one of V2's pinned rows left when the refusal landed: the sheets draw
    nothing their kits forbid now, and say each refusal. So no live row could say "disagrees", and
    a V2 that stopped reading the kit would agree everywhere. Each defect is planted in a real
    swept sheet, both ways round, as V24 holds its legend: a refusal left unsaid, a refusal said
    where the kit forbids nothing, and a feature the kit forbids drawn."""

    # its kit forbids the sidelights for 1700-1780 (georgian-colonial-american's row), and the
    # sweep draws every style at the Tidewater record's own 1765
    FORBIDS = "tidewater-georgian"

    @staticmethod
    def _v2(monkeypatch, sweep):
        monkeypatch.setattr(C, "_style_sweep", lambda: sweep)
        return {r["subject"]: r for r in C.CHECKS["V2"]["fn"]()}

    @staticmethod
    def _said(svg):
        return [" ".join(t.split()).upper() for t, _a, _it in C.IR.Ink(svg).texts() if t and t.strip()]

    def test_the_premise_the_forbidding_style_refuses_says_so_and_agrees(self, monkeypatch):
        el, svg = C._style_sweep()[self.FORBIDS]
        assert C._sweep_date() == 1765 and el["entrance"]["sidelights_present"] is False
        assert any(t.startswith("SIDELIGHTS NOT DRAWN — FORBIDDEN BY GEORGIAN-COLONIAL-AMERICAN")
                   for t in self._said(svg)), "the premise: the sheet says the refusal"
        got = self._v2(monkeypatch, {self.FORBIDS: (el, svg)})
        assert got[self.FORBIDS]["verdict"] == "agrees", got[self.FORBIDS]

    def test_v2_sees_a_refusal_left_unsaid(self, monkeypatch):
        el, svg = C._style_sweep()[self.FORBIDS]
        planted = re.sub(r"<text[^>]*>SIDELIGHTS NOT DRAWN — FORBIDDEN BY[^<]*</text>", "", svg)
        assert planted != svg, "the plant did not land"
        r = self._v2(monkeypatch, {self.FORBIDS: (el, planted)})[self.FORBIDS]
        assert r["verdict"] == "disagrees" and \
            "not said naming georgian-colonial-american" in r["detail"], r

    def test_v2_sees_a_refusal_said_that_the_kit_does_not_make(self, monkeypatch):
        el, svg = C._style_sweep()[self.FORBIDS]
        planted = svg.replace("</svg>", '<text class="dm" x="0" y="0">FRIEZE NOT DRAWN — FORBIDDEN '
                              "BY PLANTED'S KIT</text></svg>")
        assert planted != svg, "the plant did not land"
        r = self._v2(monkeypatch, {self.FORBIDS: (el, planted)})[self.FORBIDS]
        assert r["verdict"] == "disagrees" and \
            "the sheet says the frieze is forbidden and the kit does not forbid it" in r["detail"], r

    def test_v2_sees_a_forbidden_feature_drawn(self, monkeypatch):
        """The sheet of a style whose kit permits its pair, held against the kit that forbids it:
        what the Tidewater front drew at 1765 until this package."""
        sweep = C._style_sweep()
        sid = next(s for s, got in sorted(sweep.items()) if got and s != self.FORBIDS
                   and "sidelights" in C._drawn_features(got[1]))
        el, svg = sweep[sid]
        r = self._v2(monkeypatch, {self.FORBIDS: (el, svg)})[self.FORBIDS]
        assert r["verdict"] == "disagrees" and \
            "sidelights (transom_sidelight: inherited from georgian-colonial-american)" in r["detail"], (sid, r)


class TestThePlanSheetsCanDisagree:
    """PL2 and PL3 agree on every sheet once WP-14.4 draws each join once and cuts each opening in
    its own element's wall, so each is driven by putting its defect back into the RENDERER, which is
    stronger than planting ink: the plant is the defect itself, not a picture of it."""

    PID = "tidewater-georgian-careful"

    def _replanted(self, monkeypatch, name, fn):
        """Re-render the one multi-element sheet with one renderer function replaced, and hand the
        census a sheet table holding only it. The CLEAN table is built first, before anything is
        replaced: `_sheets()` caches what it builds, so a test run on its own would otherwise fill
        the cache for the whole session with sheets drawn by the planted renderer."""
        import copy
        RP = C.SURF._mod("render_plan")
        rec = dict(C._sheets()[self.PID])
        monkeypatch.setattr(RP, name, fn)
        rec["plan_svg_working"] = C._render(RP.render, copy.deepcopy(rec["placed"]), register="working")
        monkeypatch.setattr(C, "_SHEETS", {self.PID: rec})
        return rec

    def test_the_premise_both_agree_on_the_one_sheet_with_a_join(self):
        got = {cid: {r["subject"]: r["verdict"] for r in C.CHECKS[cid]["fn"]()}[self.PID] for cid in ("PL2", "PL3")}
        assert got == {"PL2": "agrees", "PL3": "agrees"}, got

    def test_pl2_sees_an_opening_cut_at_the_footprints_face(self, monkeypatch):
        RP = C.SURF._mod("render_plan")

        def old_gaps(op, W, H):
            # the defect WP-14.4 removed: every exterior hole at the FOOTPRINT's face
            gaps = []
            for d in op["interior"]:
                half = d["width_ft"] / 2.0
                gaps.append(("y" if d["horiz"] else "x", d["at_ft"], d["pos_ft"] - half, d["pos_ft"] + half))
            for d in op["exterior"] + op["windows"]:
                axis, pos = RP._wall_axis(d["wall"], W, H)
                half = d["width_ft"] / 2.0
                gaps.append((axis, pos, d["at_ft"] - half, d["at_ft"] + half))
            return gaps
        self._replanted(monkeypatch, "opening_gaps", old_gaps)
        got = C.CHECKS["PL2"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"], got
        assert "drawn through a solid wall" in got[0]["detail"] and "kitchen S" in got[0]["detail"], got

    def test_pl2_sees_a_break_where_the_record_places_no_opening(self, monkeypatch):
        RP = C.SURF._mod("render_plan")
        real = RP.opening_gaps

        def with_a_hole(op, W, H):
            # a 3 ft hole in the main block's south wall at 22 ft, where the record places nothing
            return real(op, W, H) + [("y", 0.0, 21.0, 24.0)]
        self._replanted(monkeypatch, "opening_gaps", with_a_hole)
        got = C.CHECKS["PL2"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"], got
        assert "breaks cut where no opening is placed" in got[0]["detail"], got
        assert "3.0 ft break" in got[0]["detail"], got

    def test_pl3_sees_a_join_drawn_by_both_elements(self, monkeypatch):
        RP = C.SURF._mod("render_plan")
        self._replanted(monkeypatch, "element_joins", lambda blocks, tol=RP.JOIN_TOL_FT: [])
        got = C.CHECKS["PL3"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"], got
        assert "drawn over one another" in got[0]["detail"], got


class TestTheBenchCanDisagree:
    """B1 and B2 agree on every plan once WP-14.4 lands, so each is driven with its defect planted
    in what the bench computes -- the read-back, as the Proportions plate's rows are driven."""

    PID = "tidewater-georgian-careful"

    def test_b1_sees_a_window_on_the_footprints_face(self, monkeypatch):
        import copy
        run = C._bench_run()
        if isinstance(run, str):
            pytest.skip("COULD NOT EVALUATE: " + run)
        planted = copy.deepcopy(run)
        wins = planted["marks"][self.PID + "@0"]["windows"]
        w = next(w for w in wins if w["wall"] == "S" and w["edge_ft"] != 0)
        t = planted["marks"][self.PID + "@0"]["t"]
        w["across"] = [-t, 0.0]            # the defect: an S window drawn on the footprint's face
        monkeypatch.setattr(C, "_BENCH", planted)
        got = {r["subject"]: r for r in C.CHECKS["B1"]["fn"]()}
        assert got[self.PID]["verdict"] == "disagrees" and "drawn across" in got[self.PID]["detail"]
        assert got["spec-builder-colonial"]["verdict"] == "agrees"

    def test_b1_sees_a_window_at_a_fixed_depth(self, monkeypatch):
        import copy
        run = C._bench_run()
        if isinstance(run, str):
            pytest.skip("COULD NOT EVALUATE: " + run)
        planted = copy.deepcopy(run)
        for w in planted["marks"]["spec-builder-colonial@0"]["windows"]:
            lo, hi = w["across"]
            w["across"] = [hi - 0.75, hi] if w["wall"] in "SW" else [lo, lo + 0.75]
        monkeypatch.setattr(C, "_BENCH", planted)
        got = {r["subject"]: r["verdict"] for r in C.CHECKS["B1"]["fn"]()}
        assert got["spec-builder-colonial"] == "disagrees"

    def test_b2_sees_a_placement_served_without_its_walls(self, monkeypatch):
        import copy
        run = C._bench_run()
        if isinstance(run, str):
            pytest.skip("COULD NOT EVALUATE: " + run)
        planted = copy.deepcopy(run)
        planted["served"][self.PID].pop("walls")
        monkeypatch.setattr(C, "_BENCH", planted)
        got = {r["subject"]: r["verdict"] for r in C.CHECKS["B2"]["fn"]()}
        assert got[self.PID] == "disagrees" and got["spec-builder-colonial"] == "agrees"

    def test_tr1_sees_a_traced_room_drawn_unflipped(self, monkeypatch):
        import json as _json
        import subprocess as _sp
        real = _sp.run

        def doctored(cmd, *a, **kw):
            r = real(cmd, *a, **kw)
            if any(str(c).endswith("trace_canvas.mjs") for c in cmd) and r.returncode == 0:
                got = _json.loads(r.stdout)
                room = got[self.PID]["rooms"][0]["rect"]
                room["y"] = -room["y"] - room["height"]          # the defect: y not flipped
                r = _sp.CompletedProcess(r.args, 0, _json.dumps(got), r.stderr)
            return r
        if not C.shutil.which("node"):
            pytest.skip("COULD NOT EVALUATE: node is not installed")
        monkeypatch.setattr(C.subprocess, "run", doctored)
        got = {r["subject"]: r["verdict"] for r in C.CHECKS["TR1"]["fn"]()}
        assert got[self.PID] == "disagrees" and got["spec-builder-colonial"] == "agrees", got


class TestTheRecordCanDisagree:
    """N0 to N3, P14 and P15 read the record against its own notes and a plate's record against
    what it says of itself (WP-14.5). Each is driven here THROUGH THE CENSUS, with its defect
    planted in the table or the asset record the census reads: `test_plate_review.py` drives the
    reviewer, and this is the join -- a census that stopped calling it would be green over any
    table at all."""

    PLATE = "vignola-doric-base-profile"
    NOTE = ("vignola-doric", "base", "base_torus")

    @pytest.fixture
    def table(self, monkeypatch):
        import copy
        PR = C._review()
        PR.reset()
        t = copy.deepcopy(PR.table())
        monkeypatch.setattr(PR, "_TABLE", t)
        PR._MEMO.clear()
        yield t
        PR.reset()

    def _row(self, cid, subject):
        rows = [r for r in C.CHECKS[cid]["fn"]() if r["subject"] == subject]
        assert len(rows) == 1, (cid, subject, rows)
        return rows[0]

    def _entry(self, t, key):
        return next(e for e in t["members"] if (e["pack"], e["assembly"], e["member"]) == key)

    def test_the_premise_the_driven_rows_agree_unplanted(self):
        subj = "/".join(self.NOTE)
        assert self._row("N0", subj)["verdict"] == "agrees"
        assert self._row("N1", subj)["verdict"] == "agrees"
        assert self._row("N2", "chambers-ionic")["verdict"] == "agrees"
        assert self._row("N3", "craftsman/casing/leg_in")["verdict"] == "agrees"

    def test_n0_sees_a_note_nobody_read(self, table):
        table["members"].remove(self._entry(table, self.NOTE))
        got = self._row("N0", "/".join(self.NOTE))
        assert got["verdict"] == "disagrees" and "has not been read" in got["detail"], got

    def test_n0_sees_a_quote_that_has_left_its_note(self, table):
        self._entry(table, self.NOTE)["claims"][0]["quote"] = "words the note never said"
        got = self._row("N0", "/".join(self.NOTE))
        assert got["verdict"] == "disagrees", got

    def test_n1_sees_a_note_that_states_another_figure(self, table):
        c = self._entry(table, self.NOTE)["claims"][0]
        c["states"] = "(%s) * 2" % c["states"]
        got = self._row("N1", "/".join(self.NOTE))
        assert got["verdict"] == "disagrees" and "the record" in got["detail"], got

    def test_n2_sees_a_conversion_stated_wrongly(self, table):
        table["modules"]["chambers-ionic"]["part_factor"] = "2"
        assert self._row("N2", "chambers-ionic")["verdict"] == "disagrees"

    def test_n3_sees_a_kit_note_that_states_another_figure(self, table):
        e = next(k for k in table["kits"] if (k["kit"], k["slot"], k["parameter"]) == ("craftsman", "casing", "leg_in"))
        e["claims"][0]["states"] = "(%s) + 1" % e["claims"][0]["states"]
        assert self._row("N3", "craftsman/casing/leg_in")["verdict"] == "disagrees"

    def _one_plate(self, monkeypatch, change):
        import copy
        a, g, pl, rec = next(x for x in C._profile_assets() if x[0]["id"] == self.PLATE)
        a = copy.deepcopy(a)
        change(a)
        monkeypatch.setattr(C, "_PLATES", [(a, g, pl, rec)])

    def test_p14_and_p15_agree_unplanted(self, monkeypatch):
        self._one_plate(monkeypatch, lambda a: None)
        assert [r["verdict"] for r in C.CHECKS["P14"]["fn"]()] == ["agrees"]
        assert [r["verdict"] for r in C.CHECKS["P15"]["fn"]()] == ["agrees"]

    def test_p14_sees_a_review_note_nobody_rewrote(self, monkeypatch):
        self._one_plate(monkeypatch, lambda a: a.update(
            review_note=a["review_note"].replace("INTERNAL: DISAGREES", "INTERNAL: AGREES")))
        got = C.CHECKS["P14"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"] and "stale" in got[0]["detail"], got

    def test_p14_sees_a_note_that_approves_what_nobody_approved(self, monkeypatch):
        """The second branch, which a current note reaches only when the ONE spelling itself stops
        saying the source was not evaluated: both halves are planted, so the note is current."""
        RP = C.SURF._mod("render_profile")
        monkeypatch.setattr(RP, "review_note", lambda asset, rep: "Approved.")
        self._one_plate(monkeypatch, lambda a: a.update(review_note="Approved."))
        got = C.CHECKS["P14"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"] and "approved" in got[0]["detail"], got

    def test_p15_sees_an_alt_text_that_lists_another_stack(self, monkeypatch):
        self._one_plate(monkeypatch, lambda a: a.update(alt_text=a["alt_text"].replace("(5p)", "(6p)", 1)))
        got = C.CHECKS["P15"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"], got

    def test_p15_says_it_cannot_read_an_alt_text_in_another_form(self, monkeypatch):
        self._one_plate(monkeypatch, lambda a: a.update(alt_text="A drawing of a base."))
        assert [r["verdict"] for r in C.CHECKS["P15"]["fn"]()] == ["cne"]


class TestTheSectionCanDisagree:
    """S1 and S2 agree on every section once WP-14.6 draws each floor structure above its storey's
    ceiling, so each is driven with its defect planted in a real section's ink."""

    PID = "tidewater-georgian-careful"

    def _planted(self, monkeypatch, change):
        import re
        rec = dict(C._sheets()[self.PID])
        rec["sec_svg"] = change(rec["sec_svg"], rec, re)
        assert rec["sec_svg"] != C._sheets()[self.PID]["sec_svg"], "the planted defect did not land"
        monkeypatch.setattr(C, "_SHEETS", {self.PID: rec})

    def test_the_premise_both_agree_unplanted(self):
        got = {cid: {r["subject"]: r["verdict"] for r in C.CHECKS[cid]["fn"]()}[self.PID] for cid in ("S1", "S2")}
        assert got == {"S1": "agrees", "S2": "agrees"}, got

    def test_s2_sees_a_floor_structure_hung_under_its_own_floor(self, monkeypatch):
        """The defect WP-14.6 removed: each body under its storey's floor line, one storey out."""
        import inkread as IR

        def change(svg, rec, re):
            pl = next(p for p in IR.Ink(svg).frames() if p.get("proj") == "section")
            k, oy, av = pl.get("px_per_ft"), pl["origin_px"][1], pl["at_origin_ft"][1]
            floors = {str(st["index"]): st["grade_to_floor_ft"] for st in rec["section"]["storeys"]}
            return re.sub(r'(<rect class="fs" data-storey="(\w+)" x="[^"]*" y=")([^"]*)"',
                          lambda m: '%s%.2f"' % (m.group(1), oy + (av - floors[m.group(2)]) * k), svg)
        self._planted(monkeypatch, change)
        got = C.CHECKS["S2"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"], got
        assert "storey 0" in got[0]["detail"] and "storey 1" in got[0]["detail"], got

    def test_s1_sees_a_wall_drawn_a_fifth_too_thin(self, monkeypatch):
        """The tolerance was a quarter of the wall: 0.78 of every wall agreed on 16 of 16."""
        def change(svg, rec, re):
            return re.sub(r'(<rect class="wb" x="[^"]*" y="[^"]*" width=")([^"]*)"',
                          lambda m: '%s%.2f"' % (m.group(1), float(m.group(2)) * 0.8), svg)
        self._planted(monkeypatch, change)
        got = C.CHECKS["S1"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"], got


# ------------------------------------------------------------------ Phase 15's five, driven
class TestPhaseFifteenChecksCanDisagree:
    """V23, V24, V25, X3 and X4 agree on every row the corpus reaches, so a weakened check agreed
    too and its doc line did not move (WP-15.8's audit, auditors B and M). Each defect is planted
    here: in a real sheet's ink, in the record a sheet is drawn from, or in the DXF writer's
    output, as the check reads each; and several reach branches no shipped plan reaches at all --
    a stack the house hides on a gable, a window on the doorcase's RIGHT, a DXF division line whose
    run is wrong, a sheet drawing no division the record states."""

    PID = "tidewater-georgian-careful"

    @classmethod
    def _rec(cls):
        return C._sheets()[cls.PID]

    @classmethod
    def _one(cls, monkeypatch, cid, el, svg, subject=None):
        # THE SUBJECT NAMES THE PLAN THE PLANTED SHEET STANDS IN FOR (WP-16.4). V25 reads the style
        # and the date off the subject's plan file, never off the record under test, because what
        # the kit forbids depends on both; a bare "planted" names no plan and read as a KeyError.
        subject = subject or "%s/planted" % cls.PID
        monkeypatch.setattr(C, "_elev_and_sweep", lambda: iter([(subject, el, svg)]))
        got = C.CHECKS[cid]["fn"]()
        assert len(got) == 1, got
        return got[0]

    @staticmethod
    def _render(el, face):
        return C._render(C.SURF._mod("render_elevation").render_elevation, el, face=face)

    # ---- V23
    def test_v23_agrees_unplanted_on_the_faces_planted_below(self, monkeypatch):
        rec = self._rec()
        for face in ("S", "E"):
            r = self._one(monkeypatch, "V23", rec["elev"], rec["faces"][face])
            assert r["verdict"] == "agrees", (face, r)

    def test_v23_sees_a_ground_line_that_stops_short_of_a_stack(self, monkeypatch):
        """K04: the "runs a foot past it" clause turned round passed. A line ending half a foot
        past the stack's outer edge -- inside the foot V23 asks for, outside K04's inverted one."""
        rec = self._rec()
        svg = rec["faces"]["S"]
        pl = C._face_plate(C.IR.Ink(svg))
        u0 = min(u for mk in C.SURF._mod("elevation").stack_marks(rec["elev"], "S")["marks"]
                 for u, _h in mk["outline"])
        x_px = C.IR.from_model(pl, u0 - 0.5, 0.0)[0]
        planted = re.sub(r'(<line class="gl[^"]*" x1=")[^"]*"', lambda m: '%s%.1f"' % (m.group(1), x_px),
                         svg, count=1)
        assert planted != svg, "the plant did not land"
        r = self._one(monkeypatch, "V23", rec["elev"], planted)
        assert r["verdict"] == "disagrees" and "stops short of the stack" in r["detail"], r

    def test_v23_sees_a_stack_drawn_over_an_opening(self, monkeypatch):
        """No opening stands within 2 ft of a stack on any row, so the clause never ran."""
        rec = self._rec()
        svg = rec["faces"]["E"]
        pl = C._face_plate(C.IR.Ink(svg))
        (mk,) = C.SURF._mod("elevation").stack_marks(rec["elev"], "E")["marks"]
        u0, u1 = min(u for u, _h in mk["outline"]), max(u for u, _h in mk["outline"])
        (x0, y0), (x1, y1) = C.IR.from_model(pl, u0 + 0.2, 8.0), C.IR.from_model(pl, u1 - 0.2, 3.0)
        planted = svg.replace('<polygon class="ch', '<rect class="op" x="%.1f" y="%.1f" width="%.1f" '
                              'height="%.1f"/><polygon class="ch' % (x0, y0, x1 - x0, y1 - y0), 1)
        assert planted != svg, "the plant did not land"
        r = self._one(monkeypatch, "V23", rec["elev"], planted)
        assert r["verdict"] == "disagrees" and "is drawn over an opening" in r["detail"], r

    def test_v23_sees_a_stack_the_house_hides_standing_off_its_rake(self, monkeypatch):
        """Every row reads 0 stacks above the roof, so the branch holding a hidden stack to the rake
        it rises from has no population. Driven: the west stack alone, seen from the east gable
        (and moved off the east stack's line so the house hides only its foot)."""
        el = copy.deepcopy(self._rec()["elev"])
        pos = el["roof_record"]["chimneys"]["positions"]
        (west,) = [c for c in pos if c["plan_rect_ft"][2] <= 1e-6]
        x0, y0, x1, y1 = west["plan_rect_ft"]
        west["plan_rect_ft"] = [x0, y0 - 8.0, x1, y1 - 8.0]
        el["roof_record"]["chimneys"]["positions"] = [west]
        svg = self._render(el, "E")
        r = self._one(monkeypatch, "V23", el, svg)
        assert r["verdict"] == "agrees" and "1 above the roof" in r["detail"], ("the premise", r)
        poly = re.search(r'<polygon class="ch[^"]*" points="([^"]+)"', svg).group(1)
        pts = [tuple(map(float, p.split(","))) for p in poly.split()]
        top = min(y for _x, y in pts)
        floated = " ".join("%.1f,%.1f" % (x, y if abs(y - top) < 1e-6 else y - 48.0) for x, y in pts)
        r = self._one(monkeypatch, "V23", el, svg.replace(poly, floated))
        assert r["verdict"] == "disagrees" and "the drawn rake there is" in r["detail"], r

    @staticmethod
    def _rear_stack():
        """Auditor D's drive: the Tidewater dining fire moved to its N wall on a flue of its own,
        so the placer seats a stack outboard of the REAR wall -- the case no shipped plan reaches.
        Only that stack is kept on the record, so every V23 row is about it. The premise is read
        off the square here, not through the elevation's own reader."""
        GEO, ST, RF, EL = (C.SURF._mod(n) for n in ("geometry", "structure", "roof", "elevation"))
        with open(os.path.join(C.ROOT, "plans", "tidewater-georgian-careful.json"), encoding="utf-8") as fh:
            plan = json.load(fh)
        moved = 0
        for lv in plan["levels"]:
            for r in lv["rooms"]:
                if r["id"] == "dining":
                    r["hearth"][0]["wall"], r["hearth"][0]["flue"] = "N", "north-stack"
                    moved += 1
        assert moved == 1, "the premise: the shipped record states the dining room's fire"
        saved = GEO._SOLVE_CACHE
        GEO._SOLVE_CACHE = {}
        try:
            placed = GEO.solve(plan, None, 250, engine="heuristic")
        finally:
            GEO._SOLVE_CACHE = saved
        sec = ST.build_section(placed, None, geometry_result=placed)
        rf = RF.build_roof(placed, None, section=sec)
        el = EL.build_elevation(placed, None, section=sec, roof=rf)
        D = el["footprint"]["depth_ft"]
        pos = el["roof_record"]["chimneys"]["positions"]
        north = [c for c in pos if c.get("plan_rect_ft")
                 and (c["plan_rect_ft"][1] + c["plan_rect_ft"][3]) / 2.0 > D]
        assert len(north) == 1, ("the premise: one stack stands outboard of the rear wall",
                                 [c.get("plan_rect_ft") for c in pos])
        el["roof_record"]["chimneys"]["positions"] = north
        return el

    def test_v23_holds_a_rear_stack_to_the_ridge_from_the_front(self, monkeypatch):
        """V23 reads which wall a stack stands at off its square, and holds a stack behind the far
        long wall to the ridge. No shipped plan seats one there, so remapping the wall reading or
        deleting the behind-the-far-wall clause left the whole census suite green (the audit of
        WP-15.8's own diff). The front drawn right agrees; its foot dropped below the ridge does
        not."""
        el = self._rear_stack()
        svg = self._render(el, "S")
        r = self._one(monkeypatch, "V23", el, svg)
        assert r["verdict"] == "agrees" and "0 from grade, 1 above the roof" in r["detail"], (
            "the premise: the front draws the rear stack above the ridge", r)
        pl = C._face_plate(C.IR.Ink(svg))
        drop = C.IR.from_model(pl, 0.0, 0.0)[1] - C.IR.from_model(pl, 0.0, 2.0)[1]
        poly = re.search(r'<polygon class="ch[^"]*" points="([^"]+)"', svg).group(1)
        pts = [tuple(map(float, p.split(","))) for p in poly.split()]
        top = min(y for _x, y in pts)
        sunk = " ".join("%.1f,%.1f" % (x, y if abs(y - top) < 1e-6 else y + drop) for x, y in pts)
        r = self._one(monkeypatch, "V23", el, svg.replace(poly, sunk))
        assert r["verdict"] == "disagrees" and "behind the far wall" in r["detail"], r

    def test_v23_holds_a_rear_stack_to_the_ground_from_its_own_wall(self, monkeypatch):
        """From the rear wall the stack stands in front of the house, so it is drawn from grade;
        the same stack floated up to the ridge is a stack the house does not hide drawn as if it
        did."""
        el = self._rear_stack()
        svg = self._render(el, "N")
        r = self._one(monkeypatch, "V23", el, svg)
        assert r["verdict"] == "agrees" and "1 from grade, 0 above the roof" in r["detail"], (
            "the premise: the rear face draws its own stack from grade", r)
        pl = C._face_plate(C.IR.Ink(svg))
        lift = C.IR.from_model(pl, 0.0, 0.0)[1] - C.IR.from_model(pl, 0.0, 20.0)[1]
        poly = re.search(r'<polygon class="ch[^"]*" points="([^"]+)"', svg).group(1)
        pts = [tuple(map(float, p.split(","))) for p in poly.split()]
        top = min(y for _x, y in pts)
        floated = " ".join("%.1f,%.1f" % (x, y if abs(y - top) < 1e-6 else y - lift) for x, y in pts)
        r = self._one(monkeypatch, "V23", el, svg.replace(poly, floated))
        assert r["verdict"] == "disagrees" and "off the ground line" in r["detail"], r

    # ---- V24
    @staticmethod
    def _front(el, clear_in, right=False):
        """The Tidewater front with its flanking window driven `clear_in` from the casing, on the
        left or round to the right, and the sheet drawn from that record."""
        EL = C.SURF._mod("elevation")
        el = copy.deepcopy(el)
        face = "S"
        (ent,) = [r for r in EL.opening_rects(el, face)["rects"] if r.get("entrance")]
        cas = ent["entrance"]["casing_width_in"]
        p = max((q for q in el["faces"][face]["placed"] if q["kind"] == "window"
                 and q["storey"] == ent["storey"] and q["cx_in"] < ent["cx_in"]), key=lambda q: q["cx_in"])
        target = ((ent["x1_in"] + cas + clear_in + p["width_in"] / 2.0) if right
                  else (ent["x0_in"] - cas - clear_in - p["width_in"] / 2.0))
        d = target - p["cx_in"]
        p["cx_in"] += d
        p["u_ft"] = round(p["u_ft"] + d / 12.0, 4)
        p["along_ft"] += d / 12.0
        return el, C._render(C.SURF._mod("render_elevation").render_elevation, el, face=face)

    def test_v24_agrees_unplanted(self, monkeypatch):
        rec = self._rec()
        assert self._one(monkeypatch, "V24", rec["elev"], rec["faces"]["S"])["verdict"] == "agrees"

    @staticmethod
    def _wall(detail, side):
        m = re.search(r"the %s wall is ([\d.]+) in against ([\d.]+) in" % side, detail)
        return (float(m.group(1)), float(m.group(2))) if m else None

    def test_v24_judges_the_right_side(self, monkeypatch):
        """Every judged doorcase has its window on the left and a door on its right."""
        el, svg = self._front(self._rec()["elev"], 5.0, right=True)
        r = self._one(monkeypatch, "V24", el, svg)
        got = self._wall(r["detail"], "right")
        assert r["verdict"] == "disagrees" and got and abs(got[0] - 5.0) < 0.1 and got[1] == 33.0, r
        assert "legend" not in r["detail"], ("the sheet says the short side it draws, and no other", r)

    def test_v24_takes_the_floor_at_half_the_pier(self, monkeypatch):
        """K03: "about half" transcribed as 0.3 passed. The window driven so the wall beside the
        doorcase, as drawn, is short of half the 66 in ordinary pier and clear of three tenths of
        it. RE-CUT 30 SEP 2026 (WP-16.4): the drive was 40 in with a 14 in sidelight standing in
        it; at the record's 1765 the kit forbids the pair, so the wall as drawn is the drive
        itself, and 26 in is inside the same band."""
        el, svg = self._front(self._rec()["elev"], 26.0)
        (left,) = [s for s in C.SURF._mod("elevation").doorcase_piers(el, "S")["sides"]
                   if s["side"] == "left"]
        assert 0.3 * 66.0 + 1.0 < left["clear_in"] < 0.5 * 66.0 - 1.0, ("the premise", left)
        r = self._one(monkeypatch, "V24", el, svg)
        got = self._wall(r["detail"], "left")
        assert r["verdict"] == "disagrees" and got and abs(got[0] - left["clear_in"]) < 0.1 \
            and got[1] == 33.0, r
        assert "legend" not in r["detail"], ("the sheet says the short side it draws, and no other", r)

    def test_v24_sees_a_window_standing_over_the_casing(self, monkeypatch):
        """A window driven 2 in over the casing. (One EXACTLY meeting the casing with no sidelight
        drawn is read as a sidelight -- glass hard against the casing is what the ink offers V24 to
        tell them by -- and returns no row: auditor B's B7, deferred, because the sheet marks a
        sidelight with the window's own class and telling them apart moves every doorcase sheet.)"""
        el, svg = self._front(self._rec()["elev"], -2.0)
        r = self._one(monkeypatch, "V24", el, svg)
        assert r["verdict"] == "disagrees" and "the doorcase touches the left window" in r["detail"], r

    @pytest.mark.parametrize("sentence,want", [
        ("THE DOORCASE TOUCHES THE PASSAGE WINDOW ON THE LEFT — PLANTED",
         "the left side does not touch its window and the legend says it does"),
        ("THE WALL BESIDE THE DOORCASE IS 5.0″ ON THE RIGHT, TO THE PORCH WINDOW — PLANTED",
         "the right side does not fall short and the legend says it does")])
    def test_v24_holds_the_legend_the_other_way(self, monkeypatch, sentence, want):
        """B8/D14: a false TOUCHES line printed on all 42 fronts agreed; a SHORT line was held only
        where no side fell short. Both are held side by side now."""
        rec = self._rec()
        svg = rec["faces"]["S"]
        planted = svg.replace("</svg>", '<text class="dm" x="0" y="0">%s</text></svg>' % sentence)
        r = self._one(monkeypatch, "V24", rec["elev"], planted)
        assert r["verdict"] == "disagrees" and want in r["detail"], r

    # ---- V25
    def test_v25_agrees_unplanted(self, monkeypatch):
        rec = self._rec()
        assert self._one(monkeypatch, "V25", rec["elev"], rec["faces"]["S"])["verdict"] == "agrees"

    def test_v25_sees_every_division_a_twentieth_of_an_inch_off_its_record(self, monkeypatch):
        """C13, K05 and K07 (G6): every division 0.05 in off, planted where both surfaces draw from
        (`cornice_marks`), passed every guard with V25 re-pointed at that function or its tolerance
        a hundred times looser. V25 reads the record, at the print's tolerance."""
        EL = C.SURF._mod("elevation")
        real = EL.cornice_marks

        def shifted(elev, face):
            got = real(elev, face)
            for m in got.get("members") or []:
                m["h0"] += 0.05 / 12.0
            return got
        monkeypatch.setattr(EL, "cornice_marks", shifted)
        el = self._rec()["elev"]
        r = self._one(monkeypatch, "V25", el, self._render(el, "S"))
        assert r["verdict"] == "disagrees" and "the record puts it at" in r["detail"], r

    def test_v25_sees_a_division_that_does_not_run_across_the_box(self, monkeypatch):
        """C01: division lines spanning the wall and not the cornice passed."""
        rec = self._rec()
        svg = rec["faces"]["S"]
        pl = C._face_plate(C.IR.Ink(svg))
        x0, x1 = C.IR.from_model(pl, 0.0, 0.0)[0], C.IR.from_model(pl, rec["elev"]["footprint"]["width_ft"], 0.0)[0]
        planted = re.sub(r'(<line class="cm[^"]*" data-member="[^"]*" x1=")[^"]*("[^>]* x2=")[^"]*"',
                         lambda m: '%s%.2f%s%.2f"' % (m.group(1), x0, m.group(2), x1), svg)
        assert planted != svg, "the plant did not land"
        r = self._one(monkeypatch, "V25", rec["elev"], planted)
        # "the box it divides" since WP-16.5: a division runs across the eave's box or a return's
        assert r["verdict"] == "disagrees" and "runs" in r["detail"] and "the box it divides" in r["detail"], r

    def test_v25_sees_a_frieze_said_and_unsaid_the_wrong_way(self, monkeypatch):
        """The pack states the frieze flush (0), so the "drawn flush for want of a figure" clause
        had no population in either direction."""
        rec = self._rec()
        el = copy.deepcopy(rec["elev"])
        el["eave_cornice"]["frieze_projection_in"] = None          # the sheet says it is unstated
        r = self._one(monkeypatch, "V25", el, self._render(el, "S"))
        assert r["verdict"] == "disagrees" and "frieze is stated" in r["detail"], r
        monkeypatch.setattr(C, "_frieze_projection_parts", lambda: (None, None))
        r = self._one(monkeypatch, "V25", rec["elev"], rec["faces"]["S"])
        assert r["verdict"] == "disagrees" and "stated by no record" in r["detail"], r

    def test_v25_sees_a_stack_in_front_of_the_face_painted_under_its_cornice(self, monkeypatch):
        """The paint-order clause had no drive (the audit of WP-15.8's own diff, auditor G): it
        could be switched off with the suite green. On the E face the Tidewater stack stands in
        front of the face and is painted over the cornice's return; moved before the cornice's box
        in document order, it is painted under it.

        RE-CUT AT WP-16.5 (30 Sep 2026). That return was the band run straight across the gable
        end. The Tidewater kit makes the full return canonical, so under R8 the gable end draws a
        return 24.6 in long at each corner and the stack, in the middle of the wall, meets neither:
        the clause has no instance on the shipped sheet, which is asserted. It is driven on a kit
        read as settling no return -- the band kept across the gable end, as the spec Colonial's
        is -- planted in the census's own kit reader and in the record the sheet is drawn from."""
        import re
        rec = self._rec()
        shipped = rec["faces"]["E"]
        ink = C.IR.Ink(shipped)
        pl = C._face_plate(ink)
        boxes = [C.IR.to_model(pl, *it.bbox()[:2]) + C.IR.to_model(pl, *it.bbox()[2:])
                 for it in C._rects(ink, "bd", "w-prof")]
        stacks = [C.IR.to_model(pl, *it.bbox()[:2]) + C.IR.to_model(pl, *it.bbox()[2:])
                  for it in C._marks(ink, "ch") if it.tag in ("polygon", "rect", "path")]
        assert len(boxes) == 2 and stacks, "the premise: two returns and a stack on the shipped gable end"
        assert not [1 for b in boxes for c in stacks
                    if min(c[2], b[2]) > max(c[0], b[0]) and min(max(c[1], c[3]), max(b[1], b[3]))
                    > max(min(c[1], c[3]), min(b[1], b[3]))], "a return overlaps the stack"
        EL = C.SURF._mod("elevation")
        unsettled = {"binding": "specified", "_bound_by": "driven",
                     "variants": [{"id": "full-return-carrying-complete-profile", "status": "permitted",
                                   "_written_by": "driven"}]}
        real_kit = C._kit
        monkeypatch.setattr(C, "_kit", lambda style: {**real_kit(style), "cornice_return": unsettled})
        el = copy.deepcopy(rec["elev"])
        el["cornice_return"] = EL.cornice_return(C.SURF._mod("resolve_kit").return_at(unsettled),
                                                 el["eave_cornice"], el["roof_record"])
        assert el["cornice_return"]["draws"] == "band"
        svg = self._render(el, "E")
        assert self._one(monkeypatch, "V25", el, svg)["verdict"] == "agrees"
        stack = re.search(r'<polygon class="ch w-prof"[^>]*/>', svg)
        box = re.search(r'<rect class="bd w-prof"', svg)
        assert stack and box and stack.start() > box.start(), "the premise: the stack is painted last"
        planted = svg[:box.start()] + stack.group(0) + svg[box.start():stack.start()] + svg[stack.end():]
        r = self._one(monkeypatch, "V25", el, planted)
        assert r["verdict"] == "disagrees" and "is painted under its cornice" in r["detail"], r

    # ---- X3 and X4: the DXF against the sheet
    @staticmethod
    def _only(monkeypatch, faces=("S", "E")):
        """The census's sheets narrowed to the Tidewater plan's `faces`."""
        rec = dict(C._sheets()["tidewater-georgian-careful"])
        rec["faces"] = {f: rec["faces"][f] for f in faces}
        monkeypatch.setattr(C, "_SHEETS", {"tidewater-georgian-careful": rec})
        return rec

    @staticmethod
    def _rewrite_xdata(monkeypatch, header, change):
        DX = C.SURF._mod("export_dxf")
        real = DX._xdata

        def planted(entity, head, payload=None, chunk=200):
            if head == header and payload is not None:
                payload = change(dict(payload))
            return real(entity, head, payload, chunk)
        monkeypatch.setattr(DX, "_xdata", planted)

    @staticmethod
    def _rewrite_dxf(monkeypatch, change):
        """Plant a defect in the DXF the census reads: the real export, then `change(msp)` on the
        file it wrote, saved over it."""
        import ezdxf
        DX = C.SURF._mod("export_dxf")
        real = DX.export_elevation_dxf

        def planted(elev, path, *a, **k):
            out = real(elev, path, *a, **k)
            doc = ezdxf.readfile(path)
            change(doc.modelspace())
            doc.saveas(path)
            return out
        monkeypatch.setattr(DX, "export_elevation_dxf", planted)

    # THREE OF X3's CLAUSES WERE DRIVEN BY NOTHING (the audit of WP-15.8's own diff, auditor G):
    # `_driven()` counts a CHECK as driven if any one test plants a defect it sees, and X3's XDATA
    # drives made it count while its grade-line, mask and order clauses could each be switched off
    # with the whole suite green -- and a DXF whose grade line stopped at the wall then passed
    # every file but the known-disagreements pin. Each clause is planted here, with the unplanted
    # control above.
    def test_x3_sees_a_grade_line_that_stops_short_of_a_grounded_stack(self, monkeypatch):
        pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
        self._only(monkeypatch, faces=("S",))

        def at_the_wall(msp):
            wall = [e for e in msp if e.dxftype() == "LWPOLYLINE" and e.dxf.layer == "TDL-ELEV-WALL"]
            xs = [p[0] for e in wall for p in e.get_points()]
            lines = [e for e in msp if e.dxftype() == "LINE" and e.dxf.layer == "TDL-ELEV-GRADE"]
            assert xs and lines, "the plant has nothing to act on"
            for ln in lines:
                ln.dxf.start = (min(xs), ln.dxf.start[1])
                ln.dxf.end = (max(xs), ln.dxf.end[1])
        self._rewrite_dxf(monkeypatch, at_the_wall)
        got = C.CHECKS["X3"]["fn"]()
        assert got and all(r["verdict"] == "disagrees" and "no grade line running a foot past it"
                           in r["detail"] for r in got), got

    def test_x3_sees_a_stack_in_front_of_its_wall_with_no_mask(self, monkeypatch):
        pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
        self._only(monkeypatch, faces=("E",))

        def unmasked(msp):
            wipes = [e for e in msp if e.dxftype() == "WIPEOUT"]
            assert wipes, "the plant has nothing to act on"
            for e in wipes:
                msp.delete_entity(e)
        self._rewrite_dxf(monkeypatch, unmasked)
        got = C.CHECKS["X3"]["fn"]()
        assert got and all(r["verdict"] == "disagrees" and "no mask of its outline" in r["detail"]
                           for r in got), got

    def test_x3_sees_a_stack_drawn_after_the_wall_the_sheet_paints_it_before(self, monkeypatch):
        pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
        self._only(monkeypatch, faces=("S",))

        def last(msp):
            stacks = [e for e in msp if e.dxftype() == "LWPOLYLINE" and e.dxf.layer == "TDL-ELEV-STACK"]
            assert stacks, "the plant has nothing to act on"
            for e in stacks:
                msp.add_entity(e.copy())
                msp.delete_entity(e)
        self._rewrite_dxf(monkeypatch, last)
        got = C.CHECKS["X3"]["fn"]()
        assert got and all(r["verdict"] == "disagrees" and "is drawn after the DXF's" in r["detail"]
                           for r in got), got

    def test_x3_and_x4_agree_unplanted(self, monkeypatch):
        pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
        self._only(monkeypatch)
        for cid in ("X3", "X4"):
            got = C.CHECKS[cid]["fn"]()
            assert got and all(r["verdict"] == "agrees" for r in got), (cid, got)

    @pytest.mark.parametrize("key,value,want", [
        ("plan_judgment", False, "the DXF says plan_judgment False"),
        ("from_grade", False, "says from_grade False in the DXF"),
        ("plan_rect_ft", [0, 0, 1, 1], "is none the roof record seats")])
    def test_x3_reads_what_the_stacks_xdata_says(self, monkeypatch, key, value, want):
        """B5/K06: X3 read that the keys were there, so a DXF calling the judged 22 in square a
        measurement agreed with a sheet saying the opposite."""
        pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
        self._only(monkeypatch)
        self._rewrite_xdata(monkeypatch, "TDL::stack", lambda p: dict(p, **{key: value}))
        got = C.CHECKS["X3"]["fn"]()
        assert got and all(r["verdict"] == "disagrees" and want in r["detail"] for r in got), got

    def test_x3_hears_the_sentences_the_sheet_says_of_its_stacks(self, monkeypatch):
        """M1: the DXF wrote the from-grade sentence and never the judgment line it leaves the size
        to, and nothing read the DXF's words."""
        pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
        self._only(monkeypatch)
        EL = C.SURF._mod("elevation")
        real = EL.face_notes
        monkeypatch.setattr(EL, "face_notes", lambda *a, **k: [
            n for n in real(*a, **k) if "A JUDGMENT, NOT A MEASUREMENT" not in n])
        got = C.CHECKS["X3"]["fn"]()
        assert got and all(r["verdict"] == "disagrees" and "and the DXF does not" in r["detail"]
                           for r in got), got

    def test_x4_reads_each_divisions_profile(self, monkeypatch):
        """C11: a division carrying the profile of the member below it passed."""
        pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
        self._only(monkeypatch)
        self._rewrite_xdata(monkeypatch, "TDL::cornice-member", lambda p: dict(p, profile="fillet"))
        got = C.CHECKS["X4"]["fn"]()
        assert got and all(r["verdict"] == "disagrees" and "another member's profile" in r["detail"]
                           for r in got), got

    def test_x4_reads_each_divisions_run(self, monkeypatch):
        """C02 and C03: a slanted line and a half-length one passed on the first point's height.
        Planted in the sheet here, which X4 holds the DXF to."""
        pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
        rec = self._only(monkeypatch, faces=("S",))
        svg = rec["faces"]["S"]
        planted = re.sub(r'(<line class="cm[^"]*" data-member="[^"]*" x1="[^"]*" y1="[^"]*" x2=")([^"]*)"',
                         lambda m: '%s%.2f"' % (m.group(1), float(m.group(2)) / 2.0), svg)
        assert planted != svg, "the plant did not land"
        rec["faces"] = {"S": planted}
        got = C.CHECKS["X4"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"] and "runs" in got[0]["detail"], got

    def test_x4_cannot_hold_the_dxf_to_a_sheet_that_draws_no_division(self, monkeypatch):
        """Parity of two drawings that draw nothing is not agreement: where the record states
        divisions and the sheet draws none, X4 could not evaluate, and says why."""
        pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
        rec = self._only(monkeypatch, faces=("S",))
        planted = re.sub(r'<line class="cm[^"]*"[^>]*/>', "", rec["faces"]["S"])
        assert planted != rec["faces"]["S"], "the plant did not land"
        rec["faces"] = {"S": planted}
        got = C.CHECKS["X4"]["fn"]()
        assert [r["verdict"] for r in got] == ["cne"] and "draws none" in got[0]["detail"], got



class TestTheGableEndCanDisagree:
    """WP-16.5 (R8, R8a, R9a). V25, X4, V2 and V8 each gained a clause about the gable end, and
    every shipped sheet agrees with each of them, so each clause is driven here with its defect:
    a band across a gable end whose kit states a return, a return drawn where the kit forbids one,
    an end profile missing or off its corner, the legend or the refusal left unsaid, the DXF's wall
    stopped at the eave or its end profiles on another layer, and a ruled judgment published. The
    Tidewater record states the full return and good-05's italian-renaissance-revival forbids it,
    so between them they reach both drawn branches.

    SINCE WP-16.9 (1 Oct 2026) THE SHIPPED good-05 HAS NO GABLE END. B1 hips it by its own kit, so
    its faces carry no end profile, and four of these tests went red on the subject they had lost
    while a fifth (the unplanted one) stayed green on a clause it no longer reached. The forbidden
    branch is DRIVEN now, on good-05's own record declaring a side gable, which B1's first clause
    says governs; every test asserts the face it reads is a gable end."""

    TIDE, G05 = "tidewater-georgian-careful", "good-05-lobby-gallery-mansion"
    FORBIDS = "italian-renaissance-revival"        # a swept style whose own kit forbids the return
    _GABLED = {}

    @classmethod
    def _g05_gabled(cls):
        """good-05, its plan declaring a side gable: the shipped record otherwise, built as `_sheets`
        builds it. Returns the sheet record and one gable face, the premise asserted."""
        if not cls._GABLED:
            plan = copy.deepcopy(C._sheets()[cls.G05]["plan"])
            plan.setdefault("declared", {})["roof_form"] = "side-gable"
            G, ST, RF, EL = (C.SURF._mod(n) for n in ("geometry", "structure", "roof", "elevation"))
            RE = C.SURF._mod("render_elevation")
            placed = G.solve(copy.deepcopy(plan), engine="heuristic")
            sec = ST.build_section(placed, None, geometry_result=placed)
            rf = RF.build_roof(placed, None, section=sec)
            el = EL.build_elevation(placed, None, section=sec, roof=rf)
            gf = EL.gable_faces(rf)
            assert gf and el["cornice_return"]["draws"] == "end-profile", ("the premise", gf)
            rec = {"plan": plan, "placed": placed, "section": sec, "roof": rf, "elev": el,
                   "faces": {f: C._render(RE.render_elevation, el, face=f) for f in ("S", "N", "E", "W")}}
            cls._GABLED.update(rec=rec, face=gf[0])
        return cls._GABLED["rec"], cls._GABLED["face"]

    @staticmethod
    def _is_gable(rec, face):
        return face in (C.SURF._mod("elevation").gable_faces(rec["elev"]["roof_record"]) or ())

    @staticmethod
    def _one(monkeypatch, cid, pid, el, svg):
        monkeypatch.setattr(C, "_elev_and_sweep", lambda: iter([("%s/planted" % pid, el, svg)]))
        got = C.CHECKS[cid]["fn"]()
        assert len(got) == 1, got
        return got[0]

    @staticmethod
    def _render(el, face):
        return C._render(C.SURF._mod("render_elevation").render_elevation, el, face=face)

    @staticmethod
    def _reading(el, state, **kw):
        EL = C.SURF._mod("elevation")
        return EL.cornice_return(dict({"state": state, "writers": ["planted"]}, **kw),
                                 el["eave_cornice"], el["roof_record"])

    # ---- V25
    def test_v25_agrees_on_both_drawn_branches_unplanted(self, monkeypatch):
        g05, gface = self._g05_gabled()
        for pid, want, rec, face in ((self.TIDE, "return", C._sheets()[self.TIDE], "E"),
                                     (self.G05, "end-profile", g05, gface)):
            assert rec["elev"]["cornice_return"]["draws"] == want, "the premise: " + pid
            assert self._is_gable(rec, face), ("the premise: a gable end", pid, face)
            r = self._one(monkeypatch, "V25", pid, rec["elev"], rec["faces"][face])
            assert r["verdict"] == "agrees", (pid, r)

    def test_v25_sees_a_band_across_a_gable_end_whose_kit_states_a_return(self, monkeypatch):
        """What every gable end drew until R8: the band straight across, whatever the kit said."""
        el = copy.deepcopy(C._sheets()[self.TIDE]["elev"])
        el["cornice_return"] = self._reading(el, "unsettled")
        r = self._one(monkeypatch, "V25", self.TIDE, el, self._render(el, "E"))
        assert r["verdict"] == "disagrees" and "the gable end return" in r["detail"], r

    def test_v25_sees_a_return_drawn_where_the_kit_forbids_one(self, monkeypatch):
        g05, face = self._g05_gabled()
        el = copy.deepcopy(g05["elev"])
        el["cornice_return"] = self._reading(el, "stated")
        r = self._one(monkeypatch, "V25", self.G05, el, self._render(el, face))
        assert r["verdict"] == "disagrees" and "0 end profile(s) drawn where the kit asks 2" in r["detail"], r

    def test_v25_sees_an_end_profile_off_its_corner(self, monkeypatch):
        rec, face = self._g05_gabled()
        svg = rec["faces"][face]
        planted = re.sub(r'(<path class="bd w-prof" data-end-profile="left")', r'\1 transform="translate(120,0)"',
                         svg, count=1)
        assert planted != svg, "the plant did not land"
        r = self._one(monkeypatch, "V25", self.G05, rec["elev"], planted)
        assert r["verdict"] == "disagrees" and "the left end profile stands at" in r["detail"], r

    def test_v25_sees_the_gable_legend_left_unsaid(self, monkeypatch):
        rec = C._sheets()[self.TIDE]
        svg = rec["faces"]["E"]
        planted = re.sub(r"<text[^>]*>CORNICE RETURNED[^<]*</text>", "", svg)
        assert planted != svg, "the plant did not land"
        r = self._one(monkeypatch, "V25", self.TIDE, rec["elev"], planted)
        assert r["verdict"] == "disagrees" and "does not say CORNICE RETURNED" in r["detail"], r

    # ---- X4
    def test_x4_sees_a_dxf_wall_that_stops_at_the_eave_under_a_gable(self, monkeypatch):
        pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
        TestPhaseFifteenChecksCanDisagree._only(monkeypatch, faces=("E",))
        TestPhaseFifteenChecksCanDisagree._rewrite_xdata(
            monkeypatch, "TDL::wall", lambda p: dict(p, to_the_rake=False))
        got = C.CHECKS["X4"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"] and "the wall:" in got[0]["detail"], got

    def test_x4_holds_a_gable_end_that_draws_no_division(self, monkeypatch):
        """A gable end showing the end profile draws no division by the rule, and draws the cornice
        all the same: X4 holds its profiles and its wall, where "no division drawn" read it as a
        sheet with nothing to hold the DXF to and went could-not-evaluate."""
        pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
        g05, face = self._g05_gabled()
        rec = dict(g05, faces={face: g05["faces"][face]})
        monkeypatch.setattr(C, "_SHEETS", {self.G05: rec})
        got = C.CHECKS["X4"]["fn"]()
        assert [r["verdict"] for r in got] == ["agrees"], got
        assert got[0]["detail"] == "0 division(s), 2 end profile(s), the wall to the rake", got

    def test_x4_sees_the_end_profiles_missing_from_the_dxf(self, monkeypatch):
        pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
        g05, face = self._g05_gabled()
        rec = dict(g05, faces={face: g05["faces"][face]})
        monkeypatch.setattr(C, "_SHEETS", {self.G05: rec})
        DX = C.SURF._mod("export_dxf")
        real = DX._layer
        monkeypatch.setattr(DX, "_layer", lambda doc, name, color=7, linetype=None: real(
            doc, "TDL-ELEV-PLANTED" if name == "TDL-ELEV-CORNICE-END" else name, color, linetype))
        got = C.CHECKS["X4"]["fn"]()
        assert [r["verdict"] for r in got] == ["disagrees"] and "the end:" in got[0]["detail"], got

    # ---- V2
    _REAL_SWEEP = staticmethod(C._style_sweep)

    def _v2(self, monkeypatch, sid, gable_svg):
        el, svg = self._REAL_SWEEP()[sid]
        monkeypatch.setattr(C, "_style_sweep", lambda: {sid: (el, svg)})
        monkeypatch.setitem(C._GABLE, (sid, id(el)), gable_svg)
        return {r["subject"]: r for r in C.CHECKS["V2"]["fn"]()}[sid]

    def test_v2_holds_the_gable_both_ways_unplanted(self, monkeypatch):
        for sid in (self.FORBIDS, "tidewater-georgian"):
            el, _svg = self._REAL_SWEEP()[sid]
            r = self._v2(monkeypatch, sid, C._gable_sheet(sid, el))
            assert r["verdict"] == "agrees", (sid, r)

    def test_v2_sees_a_return_drawn_on_a_gable_end_the_kit_forbids(self, monkeypatch):
        el, _svg = C._style_sweep()[self.FORBIDS]
        drawn = copy.deepcopy(el)
        drawn["cornice_return"] = self._reading(drawn, "stated")
        r = self._v2(monkeypatch, self.FORBIDS, self._render(drawn, "E"))
        assert r["verdict"] == "disagrees" and "returned on the gable end" in r["detail"], r

    def test_v2_sees_a_return_ban_left_unsaid(self, monkeypatch):
        el, _svg = C._style_sweep()[self.FORBIDS]
        gsvg = C._gable_sheet(self.FORBIDS, el)
        planted = re.sub(r"<text[^>]*>NO CORNICE RETURN — FORBIDDEN BY[^<]*</text>", "", gsvg)
        assert planted != gsvg, "the plant did not land"
        r = self._v2(monkeypatch, self.FORBIDS, planted)
        assert r["verdict"] == "disagrees" and "the return forbidden" in r["detail"], r

    def test_v2_sees_a_return_said_forbidden_where_the_kit_forbids_none(self, monkeypatch):
        el, _svg = C._style_sweep()["tidewater-georgian"]
        gsvg = C._gable_sheet("tidewater-georgian", el)
        planted = gsvg.replace("</svg>", '<text class="dm" x="0" y="0">NO CORNICE RETURN — FORBIDDEN '
                               "BY PLANTED'S KIT</text></svg>")
        r = self._v2(monkeypatch, "tidewater-georgian", planted)
        assert r["verdict"] == "disagrees" and \
            "the sheet says the return is forbidden and the kit does not forbid it" in r["detail"], r

    # ---- V8
    def test_v8_sees_a_ruled_judgment_published(self, monkeypatch):
        """R9a's bed mould and R8a's return are judgments by a ruling, which no pack rule marks."""
        for name in ("bed_mould_projection_in", "return_projection_from_wall_in"):
            rec = copy.deepcopy(C._sheets()[self.TIDE])
            rec["elev"]["measurements"][name] = 2.5
            monkeypatch.setattr(C, "_sheets", lambda rec=rec: {self.TIDE: rec})
            got = C.CHECKS["V8"]["fn"]()
            assert [r["verdict"] for r in got] == ["disagrees"] and name in got[0]["detail"] \
                and "the record marks it a judgment" in got[0]["detail"], (name, got)

# ------------------------------------------------------------------ which checks nothing drives
def _driven():
    """The checks some test in this file names and requires "disagrees" of: read off each test's
    own body and, through `self.`/`cls.` and module-level calls, the helpers it hands the check
    to (`_o1_at`, `_v22`, `_verdicts`), as a string constant equal to a check's id."""
    tree = ast.parse(open(__file__, encoding="utf-8").read())
    module = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}

    def consts(node, scope, seen):
        out = {n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
        for call in (n for n in ast.walk(node) if isinstance(n, ast.Call)):
            f = call.func
            if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id in ("self", "cls"):
                target = scope.get(f.attr)
            else:
                target = module.get(f.id) if isinstance(f, ast.Name) else None
            if target is not None and target.name not in seen:
                out |= consts(target, scope, seen | {target.name})
        return out

    ids, driven = set(C.CHECKS), set()
    scopes = [({}, [n for n in tree.body if isinstance(n, ast.FunctionDef)])]
    scopes += [({m.name: m for m in c.body if isinstance(m, ast.FunctionDef)},
                [m for m in c.body if isinstance(m, ast.FunctionDef)])
               for c in tree.body if isinstance(c, ast.ClassDef)]
    for scope, fns in scopes:
        for fn in fns:
            if fn.name.startswith("test_"):
                # never INTO this reader: its own body holds "disagrees", so a test that merely
                # calls it -- the control below does -- would count as driving every id it names,
                # and the guard would certify itself (WP-15.8's audit of its own diff: renaming all
                # nineteen Phase 15 drivers away left both tests here green)
                got = consts(fn, scope, {fn.name, "_driven"})
                if "disagrees" in got:
                    driven |= got & ids
    return driven


class TestV19ReadsTheRoofsForm:
    """WP-16.9 (Lucas's answers B1, B7 and B8, 30 Sep 2026): V19's `:form` rows hold each roof to
    its record's form, else its style's canonical form, else a fallback said on every sheet -- and
    where the kit forbids that fallback, to no roof, said. No shipped plan reaches the refusal (the
    three styles whose kits forbid their fallback are drawn by none), so it is driven here: the
    Tidewater house undeclared, its kit patched for the roof layer and the census's own reader
    alike to make a mansard canonical and forbid the side gable. Each defect is put back into the
    RENDERER or the record, not painted onto ink."""

    PID = "tidewater-georgian-careful"
    STYLE = "tidewater-georgian"

    def _refused(self, monkeypatch, notes=None):
        TH, RF, EL, G, ST = (SURF._mod(n) for n in ("threshold", "roof", "elevation", "geometry", "structure"))
        RE, RR = SURF._mod("render_elevation"), SURF._mod("render_roof")
        C._sheets()                      # the clean table, cached before anything is patched
        rows = [{"id": "mansard", "status": "canonical", "_written_by": self.STYLE},
                {"id": "side-gable", "status": "forbidden", "_written_by": "w-writer"}]
        kit = dict(TH.resolved_slots(self.STYLE) or {},
                   roof_form={"binding": "specified", "_bound_by": self.STYLE, "variants": rows})
        real_kit = C._kit
        monkeypatch.setitem(TH._RESOLVED, self.STYLE, kit)
        monkeypatch.setattr(C, "_kit", lambda st: kit if st == self.STYLE else real_kit(st))
        monkeypatch.setattr(G, "_SOLVE_CACHE", {})
        plan = json.load(open(os.path.join(C.ROOT, "plans", self.PID + ".json")))
        plan["declared"].pop("roof_form")
        placed = G.solve(copy.deepcopy(plan), engine="heuristic")
        sec = ST.build_section(placed, None, geometry_result=placed)
        rf = RF.build_roof(placed, None, section=sec)
        el = EL.build_elevation(placed, None, section=sec, roof=rf)
        assert rf["form_reading"]["by"] == "refused", "the premise: the fallback is refused"
        if notes:
            real = RE.EL.face_notes
            monkeypatch.setattr(RE.EL, "face_notes", lambda *a, **k: notes(real(*a, **k)))
        rec = {"plan": plan, "placed": placed, "section": sec, "roof": rf, "elev": el,
               "roof_svg": C._render(RR.render_roof, rf),
               "faces": {f: C._render(RE.render_elevation, el, face=f) for f in ("S", "N", "E", "W")}}
        monkeypatch.setattr(C, "_SHEETS", {self.PID: rec})
        return rec

    def _form(self):
        return [r for r in C.CHECKS["V19"]["fn"]() if r["subject"] == self.PID + ":form"]

    def test_the_premise_a_refused_roof_said_everywhere_agrees(self, monkeypatch):
        self._refused(monkeypatch)
        got = self._form()
        assert [r["verdict"] for r in got] == ["agrees"], got
        assert got[0]["detail"] == "None, no roof, the fallback side-gable forbidden, said", got

    def test_v19_sees_a_refused_roof_drawn_anyway(self, monkeypatch):
        rec = self._refused(monkeypatch)
        rec["roof"] = dict(rec["roof"], main=dict(rec["roof"]["main"], form="side-gable"))
        got = self._form()
        assert [r["verdict"] for r in got] == ["disagrees"], got
        assert "the roof is drawn side-gable where the kit's refusal states None" in got[0]["detail"], got

    def test_v19_sees_the_refusal_left_unsaid(self, monkeypatch):
        self._refused(monkeypatch, notes=lambda ns: [n for n in ns if not n.startswith("NO ROOF DRAWN")])
        got = self._form()
        assert [r["verdict"] for r in got] == ["disagrees"], got
        assert "does not say no roof is drawn because side-gable is forbidden" in got[0]["detail"], got

    def test_v19_sees_a_sheet_that_stands_a_refused_roof_on_its_frieze(self, monkeypatch):
        self._refused(monkeypatch, notes=lambda ns: ns + ["ROOF DRAWN ON THIS SHEET’S FRIEZE AND CORNICE"])
        got = self._form()
        assert [r["verdict"] for r in got] == ["disagrees"], got
        assert "says a roof is drawn on its frieze where none is" in got[0]["detail"], got


class TestV23SaysTheStacksTheRoofPlacesNoneOf:
    """WP-16.9: where the style calls for chimneys and the roof record places none (a hip with no
    gable-end wall, a roof with no judged ridge), every face says the record's own reason. The spec
    Colonial reaches it on the shipped corpus -- its kit calls for gable-end chimneys and its roof
    judges no ridge -- and its sheets said nothing until this. Driven by putting the silence back
    into the sentence's one writer and re-rendering the face."""

    PID = "spec-builder-colonial"

    def _faces(self, monkeypatch, writer=None):
        RE = SURF._mod("render_elevation")
        rec = dict(C._sheets()[self.PID])
        ch = (rec["elev"]["roof_record"].get("chimneys") or {})
        assert ch.get("applicable") and not ch.get("positions") and ch.get("note"), (
            "the premise: the spec Colonial's roof places none of the stacks its style calls for")
        if writer:
            DISC = SURF._mod("disclosures")
            monkeypatch.setattr(DISC, "stacks_the_roof_refuses", writer)
        rec["faces"] = {f: C._render(RE.render_elevation, rec["elev"], face=f) for f in ("S", "N", "E", "W")}
        monkeypatch.setattr(C, "_SHEETS", {self.PID: rec})
        monkeypatch.setattr(C, "_style_sweep", lambda: {})
        return [r for r in C.CHECKS["V23"]["fn"]() if r["subject"].endswith(":refused")]

    def test_the_premise_every_face_says_it(self, monkeypatch):
        got = self._faces(monkeypatch)
        assert sorted(r["subject"] for r in got) == ["%s/%s:refused" % (self.PID, f) for f in "ENSW"]
        assert {r["verdict"] for r in got} == {"agrees"}, got

    def test_v23_sees_the_refusal_left_unsaid(self, monkeypatch):
        got = self._faces(monkeypatch, writer=lambda roof: None)
        assert {r["verdict"] for r in got} == {"disagrees"}, got
        assert all("does not say why" in r["detail"] for r in got), got


# EVERY CHECK WITH NO LIVE DISAGREEMENT THAT NO TEST HERE DRIVES, BY NAME (WP-15.8's audit, auditor
# B). This file's docstring counted them by hand -- "69 checks ... 23 undriven" -- and read 74 and
# 28 after Phase 15 with nothing red: V23, V24, V25, X3 and X4 had joined with no test that could
# make one of them say "disagrees". Derived now and held equal to this list, so a new check fails
# here until it is driven or named, and a check driven since must leave it. V8 left on 30 Sep 2026
# (WP-16.5): `test_v8_sees_a_ruled_judgment_published` drives it with the held bed mould published.
UNDRIVEN = ("E1", "E2", "E3", "F1", "P3", "P4", "P7", "PL1", "S3", "V1", "V11", "V14", "V17", "V18",
            "V20", "V21", "V3", "V4", "V5", "V6", "X1", "X2")


class TestTheUndrivenAreNamed:
    def test_the_undriven_checks_are_exactly_the_named_ones(self):
        live = {k.split(":")[0] for k in json.load(open(C.KNOWN))["disagreements"]}
        undriven = sorted(set(C.CHECKS) - live - _driven())
        assert undriven == sorted(UNDRIVEN), (
            "the checks nothing here drives moved: newly undriven %s (drive each with its defect, or "
            "name it in UNDRIVEN and say why), newly driven %s (take it off the list)" % (
                sorted(set(undriven) - set(UNDRIVEN)), sorted(set(UNDRIVEN) - set(undriven))))

    def test_the_reader_follows_a_test_into_the_helper_that_names_its_check(self):
        """The control on the reader: O1 and V22 are driven only through a helper (`_o1_at`,
        `_v22`), and a reader of test bodies alone calls both undriven."""
        assert {"O1", "V22", "V23", "V24", "V25", "X3", "X4"} <= _driven()


class TestV19SaysARoofFromAJudgment:
    """T3 (taken as recommended under Lucas's standing instruction of 1 Oct 2026): V19's `:form` row
    holds the judgment line to the record both ways -- every sheet of a roof the kit decided by a
    record flagged `judgment: true` names it and its writer, and no other sheet says it. Driven on
    the Tidewater house undeclared, its kit patched for the roof layer and the census's own reader
    alike, and each defect put back into the face's one writer, not painted onto ink."""

    PID = "tidewater-georgian-careful"
    STYLE = "tidewater-georgian"

    def _house(self, monkeypatch, flag, notes=None):
        TH, RF, EL, G, ST = (SURF._mod(n) for n in ("threshold", "roof", "elevation", "geometry", "structure"))
        RE, RR = SURF._mod("render_elevation"), SURF._mod("render_roof")
        C._sheets()
        kit = dict(TH.resolved_slots(self.STYLE) or {},
                   roof_form={"binding": "specified", "_bound_by": self.STYLE, "judgment": flag,
                              "variants": [{"id": "side-gable", "status": "canonical", "_written_by": self.STYLE}]})
        real_kit = C._kit
        monkeypatch.setitem(TH._RESOLVED, self.STYLE, kit)
        monkeypatch.setattr(C, "_kit", lambda st: kit if st == self.STYLE else real_kit(st))
        monkeypatch.setattr(G, "_SOLVE_CACHE", {})
        plan = json.load(open(os.path.join(C.ROOT, "plans", self.PID + ".json")))
        plan["declared"].pop("roof_form")
        placed = G.solve(copy.deepcopy(plan), engine="heuristic")
        sec = ST.build_section(placed, None, geometry_result=placed)
        rf = RF.build_roof(placed, None, section=sec)
        el = EL.build_elevation(placed, None, section=sec, roof=rf)
        assert rf["form_reading"]["by"] == "kit", "the premise: the kit decided the form"
        if notes:
            real = RE.EL.face_notes
            monkeypatch.setattr(RE.EL, "face_notes", lambda *a, **k: notes(real(*a, **k)))
        rec = {"plan": plan, "placed": placed, "section": sec, "roof": rf, "elev": el,
               "roof_svg": C._render(RR.render_roof, rf),
               "faces": {f: C._render(RE.render_elevation, el, face=f) for f in ("S", "N", "E", "W")}}
        monkeypatch.setattr(C, "_SHEETS", {self.PID: rec})
        return rec

    def _form(self):
        return [r for r in C.CHECKS["V19"]["fn"]() if r["subject"] == self.PID + ":form"]

    def test_the_premise_a_judged_roof_said_everywhere_agrees(self, monkeypatch):
        self._house(monkeypatch, True)
        got = self._form()
        assert [r["verdict"] for r in got] == ["agrees"], got
        assert got[0]["detail"] == "side-gable, the kit's, a judgment, said", got

    def test_v19_sees_the_judgment_left_unsaid(self, monkeypatch):
        self._house(monkeypatch, True, notes=lambda ns: [n for n in ns if not n.startswith("ROOF FORM IS A JUDGMENT")])
        got = self._form()
        assert [r["verdict"] for r in got] == ["disagrees"], got
        assert "does not say the side-gable is a judgment of tidewater-georgian's kit" in got[0]["detail"], got

    def test_v19_sees_a_judgment_said_of_a_record_that_carries_none(self, monkeypatch):
        self._house(monkeypatch, False, notes=lambda ns: ns + [
            "ROOF FORM IS A JUDGMENT — TIDEWATER-GEORGIAN'S KIT MAKES SIDE-GABLE CANONICAL AND MARKS THE CALL A JUDGMENT"])
        got = self._form()
        assert [r["verdict"] for r in got] == ["disagrees"], got
        assert "calls a roof form a judgment that is not drawn from a judgment-flagged record" in got[0]["detail"], got


class TestTheRakeLegendCanDisagree:
    """WP-16.9 (B29, T11, and a roof that judges no ridge). V25's rake clause holds the gable end's
    legend to the kit: a plain trim the kit states as ONE measured figure is said as MEASURED (B29),
    a kit stating the rake's overhang and no member keeps the edge and says the band (T11, taken as
    recommended under Lucas's standing instruction of 1 Oct 2026, never put), and a roof judging no
    ridge draws no rake and says why, its eave faces not saying the gable ends draw one. No drawn
    shipped plan reaches the first two, and every shipped sheet agrees with the third, so each is
    driven here with its defect: the kit's reading planted through `_kit`, the elevation's own
    reading set from the same record, and each defect put back into the face's words."""

    TIDE, SPEC = "tidewater-georgian-careful", "spec-builder-colonial"

    @staticmethod
    def _one(monkeypatch, pid, el, svg):
        monkeypatch.setattr(C, "_elev_and_sweep", lambda: iter([("%s/planted" % pid, el, svg)]))
        got = C.CHECKS["V25"]["fn"]()
        assert len(got) == 1, got
        return got[0]

    @staticmethod
    def _render(el, face):
        return C._render(C.SURF._mod("render_elevation").render_elevation, el, face=face)

    def _planted(self, monkeypatch, rake_rec, words=None):
        """The Tidewater house (a ridged roof, gable ends W and E) with its style's resolved
        `rake_condition` replaced by `rake_rec` for the census and the elevation alike."""
        RK, EL = C.SURF._mod("resolve_kit"), C.SURF._mod("elevation")
        rec = C._sheets()[self.TIDE]
        el = copy.deepcopy(rec["elev"])
        style = el["style"]
        assert ((el.get("roof_record") or {}).get("main") or {}).get("pitch_rise_per_12") is not None, \
            "the premise: the roof judges a ridge"
        real_kit = C._kit
        kit = dict(real_kit(style), rake_condition=dict(rake_rec, _bound_by=style))
        monkeypatch.setattr(C, "_kit", lambda st: kit if st == style else real_kit(st))
        el["rake"] = EL.rake_for(style, RK.rake_at(kit["rake_condition"], None), el["eave_cornice"])
        if words is not None:
            el["rake"]["words"] = words(el["rake"]["words"])
        return el

    MEASURED = {"binding": "specified",
                "parameters": {"rake_trim_width_in": {"value": 5.5, "unit": "in", "kind": "measured"}}}
    OVERHANG = {"binding": "specified", "rule": "eave and rake overhang between 18 and 36 in",
                "parameters": {"rake_overhang_in": {"range": [18, 36], "unit": "in", "kind": "measured"}}}

    def test_v25_agrees_with_a_measured_trim_said_as_measured(self, monkeypatch):
        el = self._planted(monkeypatch, self.MEASURED)
        assert (el["rake"]["draws"], el["rake"]["judgment"]) == ("plain", False), "the premise"
        r = self._one(monkeypatch, self.TIDE, el, self._render(el, "E"))
        assert r["verdict"] == "agrees", r

    def test_v25_sees_a_measured_trim_said_as_a_judgment(self, monkeypatch):
        el = self._planted(monkeypatch, self.MEASURED, words=lambda w: w.replace(", MEASURED", ", A JUDGMENT"))
        assert el["rake"]["words"].endswith("A JUDGMENT"), "the plant did not land"
        r = self._one(monkeypatch, self.TIDE, el, self._render(el, "E"))
        assert r["verdict"] == "disagrees" and "does not say RAKE: A PLAIN and MEASURED" in r["detail"], r

    def test_v25_agrees_with_an_overhang_kept_as_the_edge_and_said(self, monkeypatch):
        el = self._planted(monkeypatch, self.OVERHANG)
        assert (el["rake"]["state"], el["rake"]["draws"]) == ("overhang", "edge"), "the premise"
        r = self._one(monkeypatch, self.TIDE, el, self._render(el, "E"))
        assert r["verdict"] == "agrees", r

    def test_v25_sees_an_overhang_left_unsaid(self, monkeypatch):
        el = self._planted(monkeypatch, self.OVERHANG,
                           words=lambda w: "RAKE DRAWN AS THE ROOF'S EDGE — THE KIT STATES NO RAKE")
        r = self._one(monkeypatch, self.TIDE, el, self._render(el, "E"))
        assert r["verdict"] == "disagrees" and "STATES A RAKE OVERHANG OF 18–36 IN AND SETTLES NO MEMBER IN A ROW" in r["detail"], r

    def test_v25_sees_a_faults_rake_said_as_measured(self, monkeypatch):
        """The second independent check's case (1 Oct 2026): the grade was held anywhere on the
        sheet, and every shipped sheet says A JUDGMENT of something else, so the fault's rake said
        MEASURED passed. The grade is held in the rake's own note now. The premise asserts the sheet
        still says A JUDGMENT elsewhere, which is what made the old test blind."""
        EL = C.SURF._mod("elevation")
        rec = C._sheets()[self.TIDE]
        el = copy.deepcopy(rec["elev"])
        assert el["rake"]["draws"] == "rake" and "A JUDGMENT" in el["rake"]["words"], "the premise"
        el["rake"]["words"] = el["rake"]["words"].replace("A JUDGMENT", "MEASURED")
        svg = self._render(el, EL.gable_faces(el["roof_record"])[0])
        assert "A JUDGMENT" in svg, "the premise: the sheet says A JUDGMENT of something else"
        r = self._one(monkeypatch, self.TIDE, el, svg)
        assert r["verdict"] == "disagrees" and "does not say RAKE: A  and A JUDGMENT" in r["detail"], r

    def test_v25_agrees_with_every_face_of_a_roof_that_judges_no_ridge(self, monkeypatch):
        rec = C._sheets()[self.SPEC]
        el = rec["elev"]
        assert ((el.get("roof_record") or {}).get("main") or {}).get("pitch_rise_per_12") is None, \
            "the premise: the spec Colonial's roof judges no ridge"
        assert el["rake"]["draws"] in ("rake", "plain"), "the premise: its kit asks a rake"
        for face in ("S", "N", "E", "W"):
            r = self._one(monkeypatch, self.SPEC, el, rec["faces"][face])
            assert r["verdict"] == "agrees", (face, r)

    def test_v25_sees_the_no_ridge_cause_left_unsaid_and_a_rake_claimed_on_an_eave_face(self, monkeypatch):
        EL = C.SURF._mod("elevation")
        rec = C._sheets()[self.SPEC]
        el = rec["elev"]
        real = EL.rake_marks

        def gable_unsaid(elev, face):
            out = dict(real(elev, face))
            if out.get("words") and "NOT DRAWN — THE ROOF JUDGES NO RIDGE" in out["words"]:
                out["words"] = out["words"].split("; NOT DRAWN")[0]
            return out
        monkeypatch.setattr(EL, "rake_marks", gable_unsaid)
        gable = EL.gable_faces(el["roof_record"])[0]
        r = self._one(monkeypatch, self.SPEC, el, self._render(el, gable))
        assert r["verdict"] == "disagrees" and "the roof judges no ridge" in r["detail"], r

        def eave_claims(elev, face):
            out = dict(real(elev, face))
            if not out.get("on_gable"):
                out["words"] = ("THE RAKE IS DRAWN ON THE GABLE ENDS; ITS OVERHANG PAST EACH CORNER IS NOT "
                                "DRAWN ON THIS FACE")
            return out
        monkeypatch.setattr(EL, "rake_marks", eave_claims)
        eave = next(f for f in ("S", "N", "E", "W") if f not in EL.gable_faces(el["roof_record"]))
        r = self._one(monkeypatch, self.SPEC, el, self._render(el, eave))
        assert r["verdict"] == "disagrees" and "the roof judges no ridge for them" in r["detail"], r


# ------------------------------------------------------------------ V26, the wall between two windows
class TestTheWindowPierCanDisagree:
    """WP-16.6. V26 agrees on every row the corpus reaches -- the placer seats to the floor now, so
    no shipped sheet draws a pier under it -- and an agreeing check that nothing drives is the
    shape WP-15.8's audit found nineteen of. Each defect is planted in the record a sheet is drawn
    from and the sheet re-drawn, or in the sheet's own words, as V26 reads each: a pier under the
    floor; a licensed style's narrow pier said and unsaid; the floor's words missing where the
    placed record refused a window for it, and present where it refused none; a door between two
    windows, which breaks the pair; and a fault stating no floor at all."""

    PID = "tidewater-georgian-careful"

    @classmethod
    def _rec(cls):
        return C._sheets()[cls.PID]

    @classmethod
    def _one(cls, monkeypatch, el, svg, face):
        monkeypatch.setattr(C, "_elev_and_sweep", lambda: iter([("%s/%s" % (cls.PID, face), el, svg)]))
        got = C.CHECKS["V26"]["fn"]()
        assert len(got) == 1, got
        return got[0]

    @staticmethod
    def _render(el, face):
        return C._render(C.SURF._mod("render_elevation").render_elevation, el, face=face)

    @staticmethod
    def _narrow(el, gap_over_width):
        """The Tidewater front with the third chamber's right-hand sash driven along the face until
        the wall between its two sashes is `gap_over_width` of the wider. They stand 1.4 apart as
        placed (the aim), so the drive is the only thing that can put one under the floor."""
        el = copy.deepcopy(el)
        a, b = sorted((p for p in el["faces"]["S"]["placed"]
                       if p["storey"] == "upper" and p["room"] == "chamber3" and p["kind"] == "window"),
                      key=lambda p: p["cx_in"])
        w = max(a["width_in"], b["width_in"])
        d = (a["cx_in"] + (a["width_in"] + b["width_in"]) / 2.0 + gap_over_width * w) - b["cx_in"]
        b["cx_in"] += d
        b["u_ft"] = round(b["u_ft"] + d / 12.0, 4)
        b["along_ft"] += d / 12.0
        return el

    def test_v26_agrees_unplanted_on_the_faces_planted_below(self, monkeypatch):
        rec = self._rec()
        for face in ("S", "N"):
            r = self._one(monkeypatch, rec["elev"], rec["faces"][face], face)
            assert r["verdict"] == "agrees", (face, r)
        assert "narrowest 1.400" in self._one(monkeypatch, rec["elev"], rec["faces"]["S"], "S")["detail"]

    def test_v26_sees_a_pier_under_the_floor(self, monkeypatch):
        el = self._narrow(self._rec()["elev"], 0.5)
        r = self._one(monkeypatch, el, self._render(el, "S"), "S")
        assert r["verdict"] == "disagrees" and "(0.500 against 1)" in r["detail"], r

    def test_v26_holds_a_pier_just_over_the_floor(self, monkeypatch):
        """The tolerance is the print and no wider: a wall 1.05 of the wider is over the floor."""
        el = self._narrow(self._rec()["elev"], 1.05)
        r = self._one(monkeypatch, el, self._render(el, "S"), "S")
        assert r["verdict"] == "agrees" and "narrowest 1.050" in r["detail"], r

    @staticmethod
    def _spared(el, style="craftsman"):
        el = copy.deepcopy(el)
        WP = C.SURF._mod("window_pier")
        assert style in WP.spared(), ("the premise: the pier fault licenses %s" % style)
        el["style"] = style
        el["pier_rule"] = dict(el["pier_rule"], style=style, spared=True,
                               spared_source=WP.spared()[style])
        return el

    def test_v26_lets_a_licensed_style_stand_under_the_floor_only_where_the_sheet_says_so(self, monkeypatch):
        el = self._spared(self._narrow(self._rec()["elev"], 0.5))
        svg = self._render(el, "S")
        assert C._PIER_SPARED_SAID in svg, "the premise: the sheet says the pier is not held to it"
        r = self._one(monkeypatch, el, svg, "S")
        assert r["verdict"] == "agrees" and r["detail"].startswith("spared, and said"), r
        unsaid = re.sub(r"<text[^>]*>[^<]*%s[^<]*</text>" % C._PIER_SPARED_SAID, "", svg)
        assert unsaid != svg, "the plant did not land"
        r = self._one(monkeypatch, el, unsaid, "S")
        assert r["verdict"] == "disagrees" and "does not say it is not held to the floor" in r["detail"], r

    def test_v26_refuses_the_licence_to_a_style_the_fault_does_not_name(self, monkeypatch):
        el = self._narrow(self._rec()["elev"], 0.5)
        svg = self._render(el, "S").replace(
            "</svg>", '<text class="dm" x="0" y="0">1 WALL BETWEEN TWO WINDOWS %s — PLANTED</text></svg>'
            % C._PIER_SPARED_SAID)
        r = self._one(monkeypatch, el, svg, "S")
        assert r["verdict"] == "disagrees" and "on a style the fault does not license" in r["detail"], r

    def test_v26_holds_the_legend_to_the_record_both_ways(self, monkeypatch):
        """The S face's record refuses a window for the floor (the back hall's second sash) and its
        legend says so; the N face's refuses none and says nothing. Each is planted the other way."""
        rec = self._rec()
        s = rec["faces"]["S"]
        assert C._PIER_FLOOR_SAID in s, "the premise: the S legend names the floor"
        cut = s.replace(C._PIER_FLOOR_SAID, "WALL")
        r = self._one(monkeypatch, rec["elev"], cut, "S")
        assert r["verdict"] == "disagrees" and "refused 1 window unit(s)" in r["detail"] \
            and "does not say so" in r["detail"], r
        n = rec["faces"]["N"]
        assert C._PIER_FLOOR_SAID not in n, "the premise: the N face refuses nothing for the floor"
        planted = n.replace("</svg>", '<text class="dm" x="0" y="0">THE PIER FLOOR — PLANTED</text></svg>')
        r = self._one(monkeypatch, rec["elev"], planted, "N")
        assert r["verdict"] == "disagrees" and "says it did" in r["detail"], r

    def test_v26_does_not_pair_two_windows_a_door_stands_between(self, monkeypatch):
        """A second passage sash driven onto the ground storey just east of the passage door: the
        door stands between it and the first, so the ground storey has no window pier and the face
        counts the upper storey's two. Pairing across the door would count three."""
        el = copy.deepcopy(self._rec()["elev"])
        pl = el["faces"]["S"]["placed"]
        win = next(p for p in pl if p["storey"] == "ground" and p["kind"] == "window")
        door = next(p for p in pl if p["storey"] == "ground" and p["kind"] == "door" and p["room"] == "passage")
        twin = copy.deepcopy(win)
        d = (door["cx_in"] + door["width_in"] / 2.0 + 6.0 + twin["width_in"] / 2.0) - twin["cx_in"]
        twin["cx_in"] += d
        twin["u_ft"] = round(twin["u_ft"] + d / 12.0, 4)
        twin["along_ft"] += d / 12.0
        pl.append(twin)
        svg = self._render(el, "S")
        assert svg.count('class="op') > self._rec()["faces"]["S"].count('class="op'), "the drive did not land"
        r = self._one(monkeypatch, el, svg, "S")
        assert r["verdict"] == "agrees" and r["detail"].startswith("2 pier(s)"), r

    def test_v26_reads_its_floor_and_its_licences_off_the_fault_file(self, tmp_path):
        """The census reads the floor and the licensed styles off the fault file itself, never
        through `window_pier` and never as a figure written here. Added by WP-16.6's mutation
        pass: a census that wrote 1.0 for the floor went green against every test in this class,
        because the cannot-evaluate test below replaces the reader whole."""
        with open(os.path.join(C.ROOT, "faults", "pier-narrower-than-the-opening.json"),
                  encoding="utf-8") as fh:
            rec = json.load(fh)
        assert C._pier_fault() == (rec["test"]["threshold"],
                                   {e["style"] for e in rec["exceptions"] if e.get("style")})
        rec["test"]["threshold"] = 2.0
        rec["exceptions"] = rec["exceptions"][:1]
        p = tmp_path / "pier.json"
        p.write_text(json.dumps(rec))
        assert C._pier_fault(str(p)) == (2.0, {rec["exceptions"][0]["style"]})
        rec["test"]["direction"] = "at-most"
        p.write_text(json.dumps(rec))
        assert C._pier_fault(str(p))[0] is None

    def test_v26_says_it_cannot_evaluate_where_the_fault_states_no_floor(self, monkeypatch):
        monkeypatch.setattr(C, "_pier_fault", lambda: (None, set()))
        got = C.CHECKS["V26"]["fn"]()
        assert [r["verdict"] for r in got] == ["cne"], got
