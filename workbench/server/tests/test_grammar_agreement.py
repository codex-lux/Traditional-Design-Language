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


# ---------------------------------------------------------------- OQ 77: no fifth copy
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
