"""The eleven asset records the corpus can draw for itself, and the refusals on the plate.

WP-4.4 has been blocked on a network this container does not have since it was written, and 150
of its 322 records could never be harvested anyway -- they are `role: incorrect`, and no archive
indexes wrongness. Eleven records were never blocked on anything: they carry a `generated_from`
block naming a proportion pack and an assembly, and everything needed to draw them has been in
the corpus since WP-5.11. They were waiting on a driver.

A test of the MODEL is not a test of the DRAWING -- this repo shipped 245 arcs drawn as their
own mirror while 34 checks and 970 tests stayed green, because every one of them interrogated
the model and none asked where the ink went. So these read the emitted SVG.
"""
import json
import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

RP = modcache.load("render_profile", os.path.join(ROOT, "build", "render_profile.py"))
MANIFEST = json.load(open(os.path.join(ROOT, "assets", "manifest.json")))
GENERATED = [a for a in MANIFEST["assets"] if a.get("generated_from")]

# 8px ui-monospace advances ~4.95 px/char. Measured off a rendered plate, not guessed: the first
# estimate was 4.42 and three labels ran off the paper.
CH_W = 4.95
_TEXT = re.compile(r'<text[^>]* x="([\d.]+)" y="([\d.]+)"[^>]*>([^<]*)</text>')


def _plates():
    for a in GENERATED:
        g = a["generated_from"]
        svg, rep = RP.render(g["pack"], (g.get("parameters") or {}).get("assembly"),
                             module_in=g.get("module_in") or 6.0)
        yield a, svg, rep


def test_every_generated_record_draws():
    """Three of the eleven failed on the first run and two were the same bug."""
    assert len(GENERATED) == 11, len(GENERATED)
    drawn = [a["id"] for a, _, _ in _plates()]
    assert len(drawn) == 11


def test_an_overlay_pack_is_resolved_not_read_raw():
    """`gibbs-ionic` is an overlay on Vignola and states no `base` assembly of its own. Reading
    its own file finds no base and the plate simply does not exist -- the raw-record read this
    corpus has been caught by on kits, on slots and on the whole cascade. The answer lives in
    the inheritance."""
    import proportion_engine as _pe  # noqa: F401  (loaded by render_profile already)
    raw = RP.PE.PACKS["gibbs-ionic"]
    assert "base" not in (raw.get("assemblies") or {}), \
        "gibbs-ionic now states its own base; this test no longer proves anything"
    svg, rep = RP.render("gibbs-ionic", "base", module_in=6.0)
    assert rep["members"] == 6, rep
    assert "<path" in svg


def test_every_plate_says_it_is_not_a_building():
    """A drawing filed where a record asked for a photograph is a false claim unless the plate
    says otherwise on its own face. Prose beside the image does not travel with it."""
    for a, svg, _ in _plates():
        assert "NOT A DRAWING OF A REAL BUILDING" in svg, a["id"]


def test_an_unconstructed_member_is_named_and_not_invented():
    """`vignola-corinthian`'s capital has two acanthus rows and a caulicoli this corpus records
    no construction for. They draw as the plain bell they are and the plate says so. A drawing
    that quietly substitutes a plausible swelling for a construction it does not have is the
    laundering this corpus forbids, in ink instead of in JSON."""
    svg, rep = RP.render("vignola-corinthian", "capital", module_in=6.0)
    assert len(rep["unconstructed"]) == 3, rep["unconstructed"]
    assert "NOT CONSTRUCTED" in svg
    for name in ("acanthus row 1", "caulicoli"):
        assert name in svg, name


def test_a_fully_constructed_plate_makes_no_such_claim():
    """The disclosure must be earned, not boilerplate: a plate with nothing unconstructed must
    not carry the line, or the line stops meaning anything."""
    svg, rep = RP.render("vignola-doric", "cornice", module_in=6.0)
    assert rep["unconstructed"] == []
    assert "NOT CONSTRUCTED" not in svg


def test_no_text_escapes_the_plate():
    """Labels ran off the right edge and the footer ran off the bottom, both invisibly -- the
    SVG was well-formed and the words were simply not on the paper."""
    bad = []
    for a, svg, _ in _plates():
        W = int(re.search(r'width="(\d+)"', svg).group(1))
        H = int(re.search(r'height="(\d+)"', svg).group(1))
        for x, y, txt in _TEXT.findall(svg):
            if float(x) + len(txt) * CH_W > W - 4:
                bad.append("%s: %r runs past the right edge" % (a["id"], txt[:50]))
            if float(y) > H - 4:
                bad.append("%s: %r is below the plate" % (a["id"], txt[:50]))
    assert not bad, "\n".join(bad)


def test_the_size_survives_when_a_label_has_to_be_cut():
    """Two clamps keep a label on the paper, and they cut different halves. The first elides the
    NAME and keeps the dimension; the second is a blind truncation that would take the figure
    off the end. On a detail plate the size is the whole point -- a millworker can live without
    the full Italian name of a moulding and cannot live without its height -- so the name is what
    gets cut, always. Without this the two clamps are interchangeable and the wrong one wins.

    `vignola-doric`'s cornice carries the longest member names in the corpus."""
    svg, _ = RP.render("vignola-doric", "cornice", module_in=6.0)
    labels = [t for _, _, t in _TEXT.findall(svg) if "\u2033" in t or "\u2026" in t]
    elided = [t for t in labels if "\u2026" in t]
    assert elided, "no label was long enough to be cut; this test proves nothing"
    for t in elided:
        assert t.rstrip().endswith("\u2033"), \
            "a cut label lost its dimension, which is the half that had to survive: %r" % t
        assert "\u2026" in t.split("\u2014")[0], \
            "the ellipsis is not in the name; something other than the name was cut: %r" % t


def test_the_plate_takes_the_drawings_shape():
    """A fixed frame drew the Doric cornice into its top third. Height is derived, and a wide
    profile and a tall one must not come out the same shape."""
    _, cornice = RP.render("vignola-doric", "cornice", module_in=6.0)
    _, capital = RP.render("vignola-corinthian", "capital", module_in=6.0)
    assert capital["plate_h"] > cornice["plate_h"] + 100, (capital, cornice)
    assert capital["plate_w"] == cornice["plate_w"], "width is the legend's, and is fixed"


def test_the_member_count_agrees_with_the_records_own_caption():
    """The captions were authored from the same packs, independently of this renderer. All
    eleven agree, which is a cross-check nothing else in the corpus performs."""
    checked = 0
    for a, _, rep in _plates():
        m = re.search(r"(\d+) members", a.get("caption") or "")
        if not m:
            continue
        checked += 1
        assert rep["members"] == int(m.group(1)), \
            "%s: caption says %s members, the plate draws %d" % (a["id"], m.group(1), rep["members"])
    assert checked == 11, checked


# ------------------------------------------------------------------ what the records now say

def test_a_generated_record_is_never_kinded_photograph():
    for a in GENERATED:
        assert a["kind"] in ("detail-drawing", "line-diagram", "elevation", "section"), \
            "%s is kinded %r" % (a["id"], a["kind"])


def test_sourced_means_a_file_is_actually_present():
    """The schema defines `sourced` as 'file present, unreviewed'. The harvester used to set it
    on records whose `file` stayed null."""
    for a in MANIFEST["assets"]:
        if a.get("status") == "sourced":
            f = a.get("file")
            assert f and f.get("path"), "%s is `sourced` with no file" % a["id"]
            assert os.path.exists(os.path.join(ROOT, f["path"])), \
                "%s names %s, which does not exist" % (a["id"], f["path"])
            assert f.get("sha256")


def test_the_generated_files_match_their_recorded_digest():
    """A record whose sha256 has drifted from its file is a record describing something else."""
    import hashlib
    for a in MANIFEST["assets"]:
        f = a.get("file")
        if not f or not f.get("sha256"):
            continue
        data = open(os.path.join(ROOT, f["path"]), "rb").read()
        assert hashlib.sha256(data).hexdigest() == f["sha256"], a["id"]
        assert len(data) == f["bytes"], a["id"]


# ------------------------------------------------- the join that made the evidence rail work

LAF = modcache.load("link_asset_faults", os.path.join(ROOT, "build", "link_asset_faults.py"))
FAULTS = LAF.load_faults()


def test_the_asset_fault_join_needs_both_halves():
    """Slot alone puts fourteen faults on one porch record -- `porch_support` is named by faults
    about columns, posts, rails and spacing, and an image of a turned post is not evidence about
    all of them. The style test is what makes the link mean something."""
    slot_only = 0
    for a in MANIFEST["assets"]:
        slots = set((a.get("depicts") or {}).get("slots") or [])
        slot_only += sum(1 for f in FAULTS if slots & set(f.get("slots") or []))
    both = sum(len(LAF.links_for(a, FAULTS)) for a in MANIFEST["assets"])
    assert both < slot_only / 5, (both, slot_only)
    assert both == 209, both


def test_the_join_is_recorded_and_idempotent():
    """A derivation that does not match what is in the file is a derivation nobody re-ran."""
    for a in MANIFEST["assets"]:
        want = LAF.links_for(a, FAULTS)
        got = (a.get("depicts") or {}).get("faults") or []
        assert got == want, "%s: recorded %r, derives %r" % (a["id"], got, want)


def test_every_linked_fault_exists():
    ids = {f["id"] for f in FAULTS}
    for a in MANIFEST["assets"]:
        for fid in (a.get("depicts") or {}).get("faults") or []:
            assert fid in ids, "%s names fault %r, which does not exist" % (a["id"], fid)


def test_the_evidence_rail_returns_something():
    """0 of 210 faults returned an asset before this. The Fault Corpus surface queries by fault
    and so printed 'no image records are filed against this fault yet' for every fault in the
    corpus, with 322 records sitting one join away."""
    sys.path.insert(0, ROOT)
    from mcp_server import core
    reached = sum(1 for f in FAULTS if core.find_assets(fault=f["id"], limit=1)["matches"])
    assert reached == 20, reached
