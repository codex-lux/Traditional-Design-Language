"""A record's description is for a reader, and its build history is not (WP-14.33).

Ruled 26 Sep 2026 on `oq/five-parti-descriptions-carry-build-history-a-reader-now-sees`: the
record pages print a description as the page's own prose, so a work-package number, an
open-question number or slug, and a code span belong in the record's `note` instead. Five parti
descriptions carried one; their history moved to `note` (parti schema 0.2.0), and the sweep in
`build/validate.py` keeps it from coming back in any record kind a page shows.

The two functions are LIFTED out of `build/validate.py` by AST, on `tests/test_duplicate_keys.py`'s
precedent: that file is a script, importing it runs the whole taxonomy check, and a second copy
of the rule here would be free to drift from the shipped one.
"""
import ast
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VALIDATE = os.path.join(ROOT, "build", "validate.py")
MOVED = ("centre-passage-double-pile", "courtyard-and-portal", "great-hall-h-plan",
         "living-hall-picturesque", "tower-villa")


def _lifted(name):
    tree = ast.parse(open(VALIDATE, encoding="utf-8").read())
    fn = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name), None)
    assert fn is not None, f"build/validate.py no longer defines {name}"
    ns = {"json": json, "os": os, "ROOT": ROOT}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), VALIDATE, "exec"), ns)
    return ns[name]


def test_each_form_of_build_history_is_found_and_named():
    found = _lifted("build_history_in")([
        ("a", "WP-13.5 states the container the description always implied."),
        ("b", "it was 9,000, of which the composer could reach 43% (OQ 45)."),
        ("c", "see oq/the-raw-kit-read for why"),
        ("d", "the back hall carries `hyphen: true`, so `geometry.blocks_for` lays it out"),
    ])
    assert [f.split(":")[0] for f in found] == ["a", "b", "c", "d", "d"], found
    assert "a work-package number" in found[0] and "an open-question number" in found[1]
    assert "an open-question slug" in found[2] and "a code span" in found[3]


def test_a_backticked_identifier_is_a_code_span_whatever_it_holds():
    """The first draft refused only a span holding `.`, `:`, `=` or `(`, and a mutation putting
    `area_range_sf` into a parti description passed it: the page prints plain text, so the reader
    sees the backticks around an identifier exactly as around a call."""
    found = _lifted("build_history_in")([
        ("a", "Its stated area range, `area_range_sf`, is what these rooms reach."),
        ("b", "It is a narrowing of `dependency-and-hyphen` to the one modern function."),
    ])
    assert [f.split(":")[0] for f in found] == ["a", "b"], found


def test_a_reader_s_figure_and_the_letters_alone_are_not_build_history():
    """The other direction: the type's true size is a reader's fact, and the letters WP and OQ
    with no number after them are words."""
    found = _lifted("build_history_in")([
        ("a", "An English H-plan manor of the first rank runs to 12,000 sf and past it."),
        ("b", "the reason the taxonomy needs separate references and descends-from edges."),
        ("c", "Four-over-four, with the WP of a window and OQ as letters alone."),
    ])
    assert found == []


def test_the_premise_the_sweep_reads_every_kind_a_page_shows():
    """An empty result from a reader that read nothing looks exactly like a clean corpus."""
    texts = _lifted("description_texts")()
    kinds = {w.split("/")[0] for w, _ in texts}
    assert kinds == {"partis", "groupings", "rooms", "massings", "styles"}, kinds
    partis = [w for w, _ in texts if w.startswith("partis/")]
    assert len(partis) == len([f for f in sorted(os.listdir(os.path.join(ROOT, "partis")))
                               if f.endswith(".json")])
    assert _lifted("build_history_in")(texts) == []


def test_the_history_moved_to_note_verbatim_and_left_the_description():
    """The history was MOVED and not deleted: each of the five carries it in `note`, word for
    word, with the citation it made -- so `check_citations.py` still reads OQ 45 -- and none of
    it is left in the description a reader sees."""
    for pid in MOVED:
        d = json.load(open(os.path.join(ROOT, "partis", f"{pid}.json"), encoding="utf-8"))
        assert isinstance(d.get("note"), str) and d["note"], pid
        assert d["note"] not in d["description"], pid
        marker = "WP-13.5" if pid == "centre-passage-double-pile" else "(OQ 45)"
        assert marker in d["note"] and marker not in d["description"], pid


def test_the_verdict_is_wired_to_the_sweep_and_to_the_exit():
    """THE JOIN, WHICH NO LIFTED FUNCTION CAN SEE. The two functions above are driven; the lines
    that apply them to the corpus and turn a finding into a failing exit are module-level, and
    `_desc_bad = 0` -- a mutation run on the day this was written -- left every other test here
    green while the sweep printed its findings and exited 0. This reads the module's own
    statements: the finding list is the sweep's result over `description_texts()`, the flag is
    that list's truthiness, and the final exit condition names the flag. It is a structural
    guard, and a copy that spelled the join differently would need it re-cut rather than pass."""
    tree = ast.parse(open(VALIDATE, encoding="utf-8").read())
    assigns = {}
    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            assigns.setdefault(n.targets[0].id, []).append(n.value)

    def calls(v, name):
        return isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id == name

    texts = [k for k, vs in assigns.items() if any(calls(v, "description_texts") for v in vs)]
    found = [k for k, vs in assigns.items() if any(
        calls(v, "build_history_in") and v.args and isinstance(v.args[0], ast.Name)
        and v.args[0].id in texts for v in vs)]
    assert len(found) == 1, "the sweep's result is not assigned from description_texts()"
    flags = [k for k, vs in assigns.items() if any(
        isinstance(v, ast.IfExp) and isinstance(v.test, ast.Name) and v.test.id == found[0]
        and isinstance(v.body, ast.Constant) and v.body.value == 1 for v in vs)]
    assert len(flags) == 1, "no flag is set from the sweep's findings"
    last_if = [n for n in tree.body if isinstance(n, ast.If)][-1]
    named = {x.id for x in ast.walk(last_if.test) if isinstance(x, ast.Name)}
    assert flags[0] in named, "the final exit does not read the description flag"
