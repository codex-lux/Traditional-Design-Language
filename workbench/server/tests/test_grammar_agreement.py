"""The three copies of the citation grammar must agree — checked, not asserted in prose.

There are three regexes for one grammar, in two languages:

  * `workbench/server/citations.py::REF_RE`   validates a ref against the corpus
  * `workbench/server/rail.py::CITE_RE`       EXTRACTS `[[cite:...]]` from model output
  * `workbench/app/src/citations.js::parseCite`  parses it in the browser

WP-5.6 found the client narrower than the server — it rejected the dot in a constraint id like
`tidewater-georgian.c01` — widened the client, and published that as "660 citations un-broken".
It was not: an adversarial audit found `rail.py`'s extractor carried a THIRD copy, also without
the dot, so a constraint citation never reached `validate()` at all and streamed to the reader
as literal bracket text. Widening the parser could not help, because the parser was never
handed anything to parse.

The lesson is not "widen the third one" — it is that a grammar spelled three times will drift
again. The server pair now share `ID_CHARS`/`FRAG_CHARS`, so this pins the remaining seam: the
JavaScript, which cannot import a Python constant.

The previous guard, `router-unit.mjs`, asserted ONE hand-written example against the client
alone and the docs described it as pinning the two against each other. It did not, and could
not: it never read the server at all.
"""
import re

import pytest

from workbench.server import citations, rail

CLIENT = "workbench/app/src/citations.js"


@pytest.fixture(scope="module")
def client_classes():
    """The character classes the browser's parseCite actually uses."""
    import os
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
    src = open(os.path.join(root, CLIENT), encoding="utf-8").read()
    ids = re.search(r"export const ID_CHARS = '([^']+)'", src)
    frags = re.search(r"export const FRAG_CHARS = '([^']+)'", src)
    m = ids and frags
    assert m, ("could not find parseCite's regex in citations.js — if it was reformatted, "
               "update this reader rather than deleting the check: an unread guard is the "
               "state this test exists to prevent")
    return ids.group(1), frags.group(1)


def test_client_and_server_id_classes_are_identical(client_classes):
    ids, frags = client_classes
    assert ids == citations.ID_CHARS, (
        f"the browser accepts [{ids}] in an id and the server accepts "
        f"[{citations.ID_CHARS}]. A ref one half accepts and the other rejects is a citation "
        f"that validates and then renders as dead text, which is how all 660 constraint ids "
        f"were inert.")
    assert frags == citations.FRAG_CHARS, (ids, frags)


def test_the_rail_extractor_accepts_every_id_the_validator_does():
    """The seam that was actually broken. `[[cite:...]]` must reach validate()."""
    cases = [
        "style:craftsman",
        "constraint:tidewater-georgian.c01",     # the dot — the whole finding
        "slot:door-main-entry#head",
        "fault:porch-too-shallow-to-inhabit",
        "pack:gibbs-doric",
    ]
    for ref in cases:
        assert citations.REF_RE.match(ref), f"REF_RE should accept {ref}"
        wrapped = f"[[cite:{ref}]]"
        m = rail.CITE_RE.search(wrapped)
        assert m, (f"rail.CITE_RE does not extract {wrapped}, so validate() never sees it and "
                   f"the reader gets raw bracket syntax instead of a citation")
        assert m.group(1) == ref


def test_a_real_constraint_citation_streams_as_a_citation_not_as_text():
    """End to end, because the regex agreeing is not the same as the reader seeing it."""
    events = rail._emit_text(
        "The rule is [[cite:constraint:tidewater-georgian.c01]].", {})
    kinds = {name for name, _ in events}
    assert "cites" in kinds, f"no cites event was emitted: {events}"
    refs = [d["refs"] for name, d in events if name == "cites"][0]
    assert "constraint:tidewater-georgian.c01" in refs
    text = [d["text"] for name, d in events if name == "text"][0]
    assert "[[cite:" not in text, f"the bracket syntax reached the reader: {text!r}"


def test_trailing_newline_is_rejected_the_same_way_on_both_sides():
    """Python's `$` also matches before a trailing newline; JavaScript's does not. `\\Z`
    closes that, so a ref with a trailing newline is refused by both rather than by one."""
    assert not citations.REF_RE.match("style:craftsman\n")


# ---------------------------------------------------------------- WP-14.3: the dossier's sections
# `DOSSIER_SECTIONS` is a pinned VOCABULARY, not a pattern (PRD phase 14, §D.1): the grammar above
# is untouched by it, and it decides which `style:` fragments name a section. §D.1 allows it
# exactly two spellings -- `citations.py`'s tuple and `citations.js`'s frozen array, which the
# browser needs because it cannot import a Python constant -- and this holds them equal by READING
# the JavaScript, as the id classes above are held.

_DOSSIER_JS = re.compile(r"^export const DOSSIER_SECTIONS = Object\.freeze\(\[([^\]\n]*)\]\);$", re.M)


@pytest.fixture(scope="module")
def client_sections():
    import os
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
    src = open(os.path.join(root, CLIENT), encoding="utf-8").read()
    hits = _DOSSIER_JS.findall(src)
    assert len(hits) == 1, (
        f"found {len(hits)} one-line `export const DOSSIER_SECTIONS = Object.freeze([...]);` in "
        f"citations.js -- §D.1 fixes that exact one-line form so this reader can hold it; if it "
        f"was reformatted, restore the form rather than loosening the reader")
    items = [x.strip() for x in hits[0].split(",") if x.strip()]
    assert all(len(x) > 2 and x[0] == x[-1] == "'" for x in items), items
    return tuple(x[1:-1] for x in items)


def test_client_and_server_dossier_sections_are_identical(client_sections):
    assert client_sections == citations.DOSSIER_SECTIONS, (
        f"the browser routes {client_sections} and the server validates "
        f"{citations.DOSSIER_SECTIONS}: a section one side knows and the other does not is a "
        f"citation that validates and then opens nothing, or opens and then streams as dead text")


def test_the_server_vocabulary_is_a_tuple_led_by_identify_and_names_each_section_once():
    s = citations.DOSSIER_SECTIONS
    assert isinstance(s, tuple), "a list could be widened at run time"
    assert len(set(s)) == len(s), "a section is listed twice"
    assert s[0] == "identify", "identify is the section the bare citation names and leads the order"


def test_no_slot_id_is_a_section_id():
    """What makes `style:<id>#<fragment>` mean ONE thing. A slot named like a section would make
    that citation a slot to the validator and a section to the router, and the fragment rule
    could not tell which the author meant."""
    from workbench.server import corpus
    slots = set(corpus.core._data()["slots"])
    assert slots, "the premise: the ontology is loaded"
    clash = sorted(slots & set(citations.DOSSIER_SECTIONS))
    assert not clash, f"slot ids that are also dossier sections: {clash}"


# ---------------------------------------------------------------- OQ 83: no fifth copy
# The moulding geometry is constructed in build/profiles.py and serialised there. Two JavaScript
# copies of the SVG sweep rule existed until 27 Aug 2026 and BOTH were wrong: each emitted the
# inverse of the correct flag, so every arc in the corpus drew as its own mirror; and the order
# tool's also read only the y-flip on a page that mirrors x on one half, so the two halves of the
# same plate contradicted each other on every arc.
#
# The ruling was to serve the finished path from Python and let SVG's own transform do the
# mirroring. This test holds that line. It reads the JavaScript, in the manner of the citation
# grammar test above, because the thing being guarded is the ABSENCE of code.

_ARC_MATH = ("sweep", "a1 > a0", "a1>a0")

_JS_SURFACES = [
    ("build/orders_template.html", "the order tool"),
    ("workbench/app/src/surfaces/Proportions.jsx", "the workbench Proportions plate"),
    ("workbench/app/src/components/AssemblyPlate.jsx", "the workbench wall-datum plate"),
]


def _strip_comments(src):
    """Comments may DESCRIBE the retired rule -- that history is worth keeping. Only live code
    is searched."""
    out, i, n = [], 0, len(src)
    while i < n:
        if src.startswith("/*", i):
            j = src.find("*/", i + 2)
            i = n if j < 0 else j + 2
        elif src.startswith("//", i):
            j = src.find("\n", i)
            i = n if j < 0 else j
        else:
            out.append(src[i])
            i += 1
    return "".join(out)


def _repo_root():
    import os
    return os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))


def test_no_javascript_surface_re_derives_an_arc_sweep():
    import os
    root = _repo_root()
    offenders = []
    for rel, what in _JS_SURFACES:
        path = os.path.join(root, rel)
        assert os.path.exists(path), f"{rel} moved; this guard must move with it"
        code = _strip_comments(open(path, encoding="utf-8").read())
        for needle in _ARC_MATH:
            if needle in code:
                offenders.append(f"{rel} ({what}) contains {needle!r} in live code")
    assert not offenders, (
        "a JavaScript surface is deriving arc geometry again -- build/profiles.py serves finished "
        "paths in model space precisely so that no consumer has to:\n  " + "\n  ".join(offenders))


def _band_emitters(root):
    """Every shipped app source file whose live code emits a `data-asm` band, as repo-relative
    paths, read with comments stripped so a file that only DESCRIBES a band is not an emitter.
    Enumerated with `git ls-files -co --exclude-standard` and never by walking: WP-13.2 met a test
    that walked into an agent worktree and went red on a copy of the repository, and a symlinked
    `node_modules` beside `src` is one misplaced link from being walked the same way."""
    import os, subprocess
    out = subprocess.run(
        ["git", "-C", root, "ls-files", "-co", "--exclude-standard", "-z", "--", "workbench/app/src"],
        capture_output=True, check=True).stdout.decode("utf-8")
    found = []
    for rel in sorted(p for p in out.split("\0") if p):
        if not rel.endswith((".js", ".jsx", ".mjs")) or rel.endswith(".test.mjs"):
            continue
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            continue
        if "data-asm" in _strip_comments(open(path, encoding="utf-8").read()):
            found.append(rel)
    return found


def test_every_app_file_that_draws_a_band_is_one_this_guard_reads():
    """PRD §I.6 (WP-14.9). A plate band is `<path data-asm data-member>` drawn from a SERVED face
    path, and `_JS_SURFACES` is the list of files held to building no arc. A second plate that
    emitted bands without joining the list would be a surface the arc guard above never opens --
    exactly how a fifth copy of the sweep rule would arrive. So the list is held to the tree:
    every file emitting `data-asm` must be on it."""
    root = _repo_root()
    emitters = _band_emitters(root)
    listed = {rel for rel, _ in _JS_SURFACES}
    assert "workbench/app/src/components/AssemblyPlate.jsx" in emitters \
        and "workbench/app/src/surfaces/Proportions.jsx" in emitters, \
        f"the premise: the walk finds both plates that draw bands ({emitters})"
    unlisted = [e for e in emitters if e not in listed]
    assert not unlisted, (
        "these app files draw plate bands (`data-asm`) and are not in _JS_SURFACES, so nothing "
        "holds them to building no arc -- add each to the list:\n  " + "\n  ".join(unlisted))


def test_the_served_geometry_actually_carries_a_path():
    """The guard above only proves the JS stopped computing. This proves Python started serving,
    so the two cannot both be true and the plate be blank."""
    import importlib.util, os
    root = _repo_root()

    def _load(name):
        spec = importlib.util.spec_from_file_location(name, os.path.join(root, "build", f"{name}.py"))
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        return m

    pe, prof = _load("proportion_engine"), _load("profiles")
    r = pe.resolve("gibbs-doric")
    geo = prof.pack_geometry(pe.dimension(r, 36.0), r.get("column"), r.get("projection_datum"))
    assert geo.get("path", "").startswith("M "), "no silhouette path served"
    assert " A " in geo["path"], "the served path has no arcs at all -- the curves are gone again"
    faces = [f for a in geo["assemblies"] for f in a.get("faces", []) if f.get("path")]
    assert len(faces) > 10, f"only {len(faces)} faces carry a path"
