"""A record's description is for a reader, and its build history is not (WP-14.33).

Ruled 26 Sep 2026 on `oq/five-parti-descriptions-carry-build-history-a-reader-now-sees`: the
record pages print a description as the page's own prose, so a work-package number, an
open-question number or slug, and a code span belong in the record's `note` instead. Five parti
descriptions carried one; their history moved to `note` (parti schema 0.2.0), and the sweep in
`build/validate.py` keeps it from coming back in any record kind a page shows.

The functions are LIFTED out of `build/validate.py` by AST, on `tests/test_duplicate_keys.py`'s
precedent: that file is a script, importing it runs the whole taxonomy check, and a second copy
of the rule here would be free to drift from the shipped one.

WP-14.33's audit found five holes and each has a guard below: the exit wiring read only that the
flag was NAMED (so `or` -> `and` and `sys.exit(0)` both passed), a flag re-assigned to 0 before
the exit passed, the premise checked which kinds were read and not how much of each (so reading a
style's `short` alone passed), a malformed record escaped as a traceback, and the forms missed the
two shapes a reworded description had kept -- a repository path and a snake_case identifier.
"""
import ast
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VALIDATE = os.path.join(ROOT, "build", "validate.py")
MOVED = ("centre-passage-double-pile", "courtyard-and-portal", "great-hall-h-plan",
         "living-hall-picturesque", "tower-villa")
# A distinctive run of each moved history, so a note truncated to its marker cannot pass for one
# that carries the history (the audit's `"WP-13.5."` mutation).
HISTORY = {
    "centre-passage-double-pile": "Until then every room of this diagram was laid into one rectangle",
    "courtyard-and-portal": "reported as a 41% miss nobody could act on",
    "great-hall-h-plan": "it was 12,000, of which the composer could reach 82%",
    "living-hall-picturesque": "a near miss, corrected for the same reason as the others",
    "tower-villa": "it was 5,500, of which 97% was reachable",
}


def _tree():
    return ast.parse(open(VALIDATE, encoding="utf-8").read())


def _lifted(name):
    tree = _tree()
    fn = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name), None)
    assert fn is not None, f"build/validate.py no longer defines {name}"
    consts = [n for n in tree.body if isinstance(n, ast.Assign) and len(n.targets) == 1
              and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "HISTORY_FORMS"]
    ns = {"json": json, "os": os, "ROOT": ROOT}
    exec(compile(ast.Module(body=consts + [fn], type_ignores=[]), VALIDATE, "exec"), ns)
    return ns[name]


def _where(found):
    return [f.split(":")[0] for f in found]


def test_each_form_of_build_history_is_found_and_named():
    found = _lifted("build_history_in")([
        ("a", "WP-13.5 states the container the description always implied."),
        ("b", "it was 9,000, of which the composer could reach 43% (OQ 45)."),
        ("c", "see oq/the-raw-kit-read for why"),
        ("d", "the back hall carries `hyphen: true`, so `geometry.blocks_for` lays it out"),
    ])
    assert _where(found) == ["a", "b", "c", "d", "d", "d"], found
    assert "a work-package number" in found[0] and "an open-question number" in found[1]
    assert "an open-question slug" in found[2] and "a code span" in found[3]
    # the third on "d" is `blocks_for` inside the second span, which is also a snake_case name
    assert "a code span" in found[4] and "a snake_case identifier ('blocks_for')" in found[5]


def test_the_spellings_the_first_forms_missed():
    """Each of these passed the first sweep (WP-14.33's audit)."""
    bh = _lifted("build_history_in")
    for text in ("as WP 14 settled", "per wp-14.2", "ruled at OQ45", "see OQs 12 and 13",
                 "a span `wrapped\nacross a line`", "a lone ` backtick"):
        assert len(bh([("x", text)])) == 1, text
    path = bh([("x", "in the sense docs/inheritance.md means")])
    snake = bh([("x", "when it says garage_strategy is the slot")])
    assert len(path) == 1 and "a repository path" in path[0], path
    assert len(snake) == 1 and "a snake_case identifier" in snake[0], snake


def test_a_backticked_identifier_is_a_code_span_whatever_it_holds():
    """The first draft refused only a span holding `.`, `:`, `=` or `(`, and a mutation putting
    `area-range` into a parti description passed it: the page prints plain text, so the reader
    sees the backticks around an identifier exactly as around a call."""
    found = _lifted("build_history_in")([
        ("a", "Its stated area range, `area-range`, is what these rooms reach."),
        ("b", "It is a narrowing of `dependency-and-hyphen` to the one modern function."),
    ])
    assert _where(found) == ["a", "b"], found


def test_a_reader_s_figure_and_the_letters_alone_are_not_build_history():
    """The other direction: the type's true size is a reader's fact, and the letters WP and OQ
    with no number after them are words; so are `and/or` and a hyphenated compound."""
    found = _lifted("build_history_in")([
        ("a", "An English H-plan manor of the first rank runs to 12,000 sf and past it."),
        ("b", "the reason the taxonomy needs separate references and descends-from edges."),
        ("c", "Four-over-four, with the WP of a window and OQ as letters alone."),
        ("d", "a porch and/or a stoop, one-and-a-half storeys, 3/4 in of reveal"),
    ])
    assert found == []


def test_a_record_the_sweep_cannot_read_is_named_rather_than_raised(tmp_path):
    """The first version raised a bare `JSONDecodeError` on a malformed record and read a
    massing catalogue that was not a list as zero massings -- an empty read that looks exactly
    like a clean one. Each is a named line now, and the module fails the build on it."""
    for kind in ("partis", "groupings", "rooms", "massings", "styles"):
        (tmp_path / kind).mkdir()
    (tmp_path / "partis" / "broken.json").write_text("{ not json")
    (tmp_path / "rooms" / "listy.json").write_text("[1, 2]")
    (tmp_path / "massings" / "catalog.json").write_text('{"id": "x"}')
    (tmp_path / "groupings" / "fine.json").write_text('{"description": "A room."}')
    bad = []
    texts = _lifted("description_texts")(root=str(tmp_path), unreadable=bad)
    assert texts == [("groupings/fine.json", "A room.")]
    assert len(bad) == 3, bad
    assert any(b.startswith("partis/broken.json: could not be read") for b in bad)
    assert any(b.startswith("rooms/listy.json: is not a record object") for b in bad)
    assert any(b.startswith("massings/catalog.json: is not a list") for b in bad)


def _expected_places():
    """Every description a page shows, enumerated here INDEPENDENTLY of the sweep, so a sweep
    narrowed to a style's `short` or to one kind cannot also narrow its own premise."""
    want = set()
    for kind in ("partis", "groupings", "rooms"):
        for f in sorted(os.listdir(os.path.join(ROOT, kind))):
            if f.endswith(".json"):
                d = json.load(open(os.path.join(ROOT, kind, f), encoding="utf-8"))
                if isinstance(d.get("description"), str):
                    want.add(f"{kind}/{f}")
    for m in json.load(open(os.path.join(ROOT, "massings", "catalog.json"), encoding="utf-8")):
        if isinstance(m.get("description"), str):
            want.add(f"massings/catalog.json#{m['id']}")
    for f in sorted(os.listdir(os.path.join(ROOT, "styles"))):
        if f.endswith(".json"):
            d = json.load(open(os.path.join(ROOT, "styles", f), encoding="utf-8")).get("description")
            for part in ("short", "long"):
                if isinstance(d, dict) and isinstance(d.get(part), str):
                    want.add(f"styles/{f}#{part}")
    return want


def test_the_premise_the_sweep_reads_every_description_a_page_shows():
    """An empty result from a reader that read nothing looks exactly like a clean corpus. Held
    place for place against an independent enumeration, with a count per kind so a kind that
    has quietly emptied cannot pass on both sides at once."""
    bad = []
    texts = _lifted("description_texts")(unreadable=bad)
    got = [w for w, _ in texts]
    assert len(got) == len(set(got)), "a description was read twice"
    want = _expected_places()
    assert set(got) == want, (sorted(want - set(got))[:5], sorted(set(got) - want)[:5])
    per = {}
    for w in got:
        per[w.split("/")[0]] = per.get(w.split("/")[0], 0) + 1
    assert per["partis"] >= 21 and per["groupings"] >= 17 and per["rooms"] >= 60, per
    assert per["massings"] >= 40 and per["styles"] >= 2 * 164, per
    assert bad == []
    assert _lifted("build_history_in")(texts) == []


def test_the_history_moved_to_note_and_left_the_description():
    """The history was MOVED and not deleted: each of the five carries it in `note`, with the
    citation it made -- so `check_citations.py` still reads OQ 45 -- and none of it is left in
    the description a reader sees. Four notes had one word re-anchored after the move ("The
    range above" pointed at the description it had left), so the run held is a distinctive
    phrase of each history rather than the whole text."""
    for pid in MOVED:
        d = json.load(open(os.path.join(ROOT, "partis", f"{pid}.json"), encoding="utf-8"))
        assert isinstance(d.get("note"), str) and d["note"], pid
        assert d["note"] not in d["description"], pid
        marker = "WP-13.5" if pid == "centre-passage-double-pile" else "(OQ 45)"
        assert marker in d["note"] and marker not in d["description"], pid
        assert HISTORY[pid] in d["note"] and HISTORY[pid] not in d["description"], pid
        assert "The range above" not in d["note"], pid


def _assigns(tree):
    """Every assignment ANYWHERE in the module (nested ones too), in source order."""
    out = []
    for n in ast.walk(tree):
        if isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            targets = n.targets if isinstance(n, ast.Assign) else [n.target]
            for t in targets:
                if isinstance(t, ast.Name):
                    out.append((n.lineno, t.id, n))
    return sorted(out, key=lambda x: x[0])


def exit_condition(tree):
    """The module's final `if`: its flags, and whether it is an `or` of names ending the run
    with a non-zero exit. Shared with `tests/test_duplicate_keys.py`."""
    last_if = [n for n in tree.body if isinstance(n, ast.If)][-1]
    t = last_if.test
    assert isinstance(t, ast.BoolOp) and isinstance(t.op, ast.Or), \
        "the final exit must fire on ANY flag: an `or` of the flags"
    assert all(isinstance(v, ast.Name) for v in t.values), "the exit condition must be bare flags"
    body = last_if.body
    assert len(body) == 1 and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Call)
    call = body[0].value
    assert ast.unparse(call.func) == "sys.exit", "the final `if` must end the run"
    assert len(call.args) == 1 and isinstance(call.args[0], ast.Constant) \
        and call.args[0].value not in (0, None, False), "the exit status must be non-zero"
    return {v.id for v in t.values}, last_if.lineno


def test_the_verdict_is_wired_to_the_sweep_and_to_the_exit():
    """THE JOIN, WHICH NO LIFTED FUNCTION CAN SEE. The lines that apply the sweep to the corpus
    and turn a finding into a failing exit are module-level. This reads them: each of the four
    names is assigned EXACTLY ONCE in the whole module (so nothing can reset the flag or empty
    the list on its way to the exit), the reader is handed the unreadable list, the findings
    are the sweep over what it read PLUS what it could not read, the flag is their truthiness,
    and the final `if` is an `or` of flags naming this one and ending in a non-zero exit."""
    tree = _tree()
    by = {}
    for line, name, node in _assigns(tree):
        by.setdefault(name, []).append((line, node))
    for name in ("_desc_unread", "_desc_texts", "_desc_found", "_desc_bad"):
        assert len(by.get(name, [])) == 1, f"{name} is assigned {len(by.get(name, []))} times"
    texts = by["_desc_texts"][0][1].value
    assert isinstance(texts, ast.Call) and ast.unparse(texts.func) == "description_texts"
    assert [(k.arg, ast.unparse(k.value)) for k in texts.keywords] == [("unreadable", "_desc_unread")]
    found = ast.unparse(by["_desc_found"][0][1].value)
    assert found == "build_history_in(_desc_texts) + _desc_unread", found
    flag = by["_desc_bad"][0][1].value
    assert ast.unparse(flag) == "1 if _desc_found else 0", ast.unparse(flag)
    flags, if_line = exit_condition(tree)
    assert "_desc_bad" in flags
    assert by["_desc_bad"][0][0] < if_line
