"""The eleven asset records the corpus can draw for itself, and the refusals on the plate.

WP-4.4 has been blocked on a network this container does not have since it was written, and a
large share of the manifest could never be harvested anyway -- those records are `role: incorrect`,
and no archive indexes wrongness. (The figures this paragraph used to carry, "150 of its 322
records", were the manifest's size and shape when the layer was authored; `check_counts.computed()`
owns `image_records` and `image_never_harvestable` and holds four documents to them.)
Eleven records were never blocked on anything: they carry a `generated_from`
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
    assert len(GENERATED) == 73, len(GENERATED)
    drawn = [a["id"] for a, _, _ in _plates()]
    assert len(drawn) == 73


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
    """NOT AN INDEPENDENT CROSS-CHECK, and this docstring used to claim it was.

    The caption is written by `gen_assets.py` from `pe.dimension(pe.resolve(pid))`, and `rep`
    comes from the same call. An auditor made `dimension()` silently drop the top member of
    every assembly -- a corpus-wide geometry regression -- and this went red; then re-ran
    `gen_assets.py`, as anyone would before committing, and it went green with the regression
    still there.

    What it does catch is the caption and the plate drifting APART: a renderer that stops
    reading the same assembly, or a manifest edited by hand. That is worth having and it is
    all it is."""
    checked = 0
    for a, _, rep in _plates():
        m = re.search(r"(\d+) members", a.get("caption") or "")
        if not m:
            continue
        checked += 1
        assert rep["members"] == int(m.group(1)), \
            "%s: caption says %s members, the plate draws %d" % (a["id"], m.group(1), rep["members"])
    assert checked == 73, checked


# ------------------------------------------------------------------ what the records now say

def test_a_generated_record_is_never_kinded_photograph():
    for a in GENERATED:
        assert a["kind"] in ("detail-drawing", "line-diagram", "elevation", "section"), \
            "%s is kinded %r" % (a["id"], a["kind"])


def test_sourced_means_a_file_is_actually_present():
    """The schema defines `sourced` as 'file present, unreviewed'. The harvester used to set it
    on records whose `file` stayed null.

    COUNTED, because the loop body is skipped entirely when nothing is sourced -- and "nothing is
    sourced" is exactly the state a gen_assets carry-forward regression produces. An auditor
    nulled every `file` and reset every `status`, i.e. simulated the data loss this package
    exists to prevent, and this test passed."""
    checked = 0
    for a in MANIFEST["assets"]:
        if a.get("status") == "sourced":
            checked += 1
            f = a.get("file")
            assert f and f.get("path"), "%s is `sourced` with no file" % a["id"]
            assert os.path.exists(os.path.join(ROOT, f["path"])), \
                "%s names %s, which does not exist" % (a["id"], f["path"])
            assert f.get("sha256")
    assert checked == 73, "expected 73 sourced records, found %d" % checked


def test_the_generated_files_match_their_recorded_digest():
    """A record whose sha256 has drifted from its file is a record describing something else."""
    import hashlib
    checked = 0
    for a in MANIFEST["assets"]:
        f = a.get("file")
        if not f or not f.get("sha256"):
            continue
        checked += 1
        data = open(os.path.join(ROOT, f["path"]), "rb").read()
        assert hashlib.sha256(data).hexdigest() == f["sha256"], a["id"]
        assert len(data) == f["bytes"], a["id"]
    assert checked == 73, "no file blocks to check; a carry-forward regression passes this"


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
    assert both == 322, both


def test_the_join_is_recorded_and_idempotent():
    """A derivation that does not match what is in the file is a derivation nobody re-ran."""
    for a in MANIFEST["assets"]:
        want = LAF.links_for(a, FAULTS)
        got = (a.get("depicts") or {}).get("faults") or []
        assert got == want, "%s: recorded %r, derives %r" % (a["id"], got, want)


def test_every_linked_fault_exists():
    ids = {f["id"] for f in FAULTS}
    checked = 0
    for a in MANIFEST["assets"]:
        for fid in (a.get("depicts") or {}).get("faults") or []:
            checked += 1
            assert fid in ids, "%s names fault %r, which does not exist" % (a["id"], fid)
    assert checked == 322, "no links to check; dropping every link passes this"


def test_the_evidence_rail_returns_something():
    """0 of 210 faults returned an asset before this. The Fault Corpus surface queries by fault
    and so printed 'no image records are filed against this fault yet' for every fault in the
    corpus, with 322 records sitting one join away."""
    sys.path.insert(0, ROOT)
    from mcp_server import core
    reached = sum(1 for f in FAULTS if core.find_assets(fault=f["id"], limit=1)["matches"])
    assert reached == 25, reached


# ------------------------------------- the generator must not destroy what it does not own

def test_gen_assets_carries_forward_the_fields_it_does_not_own(tmp_path):
    """`build/gen_assets.py` rebuilds the manifest from scratch. It used to hardcode
    `license: unknown`, `file: None` and `status: wanted` on every record, so a run silently
    discarded WP-4.4's 161 building names, the eleven files, the statuses and the 209 fault
    links -- in a 601 KB diff that reads as a reformat, from a script in neither check_all.py
    nor the Makefile.

    This runs the real generator against the real manifest and asserts the carried fields
    survive, restoring from a backup OUTSIDE the repository in a `finally`.

    THE RESTORE IS NOT UNCONDITIONAL AND THIS DOCSTRING USED TO SAY IT WAS. `finally` runs for
    exceptions and for KeyboardInterrupt; it does not run for SIGKILL, SIGTERM, or a
    pytest-timeout thread kill. In those cases the tree keeps whatever the generator emitted --
    normally byte-identical, since the generator carries everything forward, but not if the
    generator itself had regressed. Two mitigations, both real: the manifest is written
    atomically (build/manifest_io.py), so it can never be left a truncated prefix; and the
    backup is outside the repo, so a killed run leaves nothing that `git add -A` would commit.
    Running two of these concurrently is not safe, and nothing does.
    """
    import shutil
    import subprocess

    # The backup lives OUTSIDE the repository. A sibling `.bak` survives a killed run and
    # `git add -A` would commit it -- one was found untracked in the working tree during the
    # audit of this very package.
    manifest_path = os.path.join(ROOT, "assets", "manifest.json")
    backup = str(tmp_path / "manifest.carrytest.bak")
    shutil.copy(manifest_path, backup)
    try:
        before = {a["id"]: a for a in json.load(open(manifest_path))["assets"]}
        r = subprocess.run([sys.executable, "build/gen_assets.py"], cwd=ROOT,
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr[-800:]
        after = {a["id"]: a for a in json.load(open(manifest_path))["assets"]}

        sourced = [i for i, a in before.items() if a.get("status") == "sourced"]
        assert len(sourced) == 73, len(sourced)
        for i in sourced:
            assert i in after, "%s vanished from the regenerated manifest" % i
            assert after[i].get("status") == "sourced", "%s lost its status" % i
            assert after[i].get("file"), "%s lost its file" % i
            assert after[i]["file"]["sha256"] == before[i]["file"]["sha256"], i

        named = [i for i, a in before.items() if (a.get("provenance") or {}).get("building")]
        # The count is NOT pinned here. It read 845, then 786 when name_asset_buildings.py
        # stopped keying on `role` (which gave a real building to 52 line-diagrams whose own
        # alt_text says there is nothing to photograph, and to 7 code-conflict drawings) and
        # started keying on `kind`, then 858 when WP-11.6's Ruling B gave the last 18
        # exemplar-less nodes something to deal from. `check_counts.computed()` owns
        # `image_building_named` and holds three documents' prose to it; the subject HERE is
        # that the generator CARRIES FORWARD a field it does not own, which the loop below is.
        # The floor exists so a manifest that lost every building name cannot pass in silence.
        assert len(named) > 100, len(named)
        for i in named:
            assert (after[i].get("provenance") or {}).get("building"), \
                "%s lost the building name WP-4.4 gave it" % i

        linked = [i for i, a in before.items() if (a.get("depicts") or {}).get("faults")]
        assert len(linked) == 189, len(linked)
        for i in linked:
            assert (after[i].get("depicts") or {}).get("faults"), "%s lost its fault links" % i
    finally:
        shutil.copy(backup, manifest_path)


def test_the_committed_manifest_is_what_the_generator_emits(tmp_path):
    """This used to assert the OPPOSITE, and the inversion is the point.

    The committed file was a frozen snapshot from when the layer was authored -- 322 records over
    three style nodes -- while the generator, tracking the corpus, emitted 1,788 over 142. Nothing
    compared them, so "322 image records" read corpus-wide in four documents while describing
    `georgian-colonial-american`, `tidewater-georgian` and `english-georgian`. Lucas ruled on
    31 Aug to regenerate.

    The guard that matters now is that they cannot silently drift apart again. This runs the real
    generator against a copy of the real manifest and asserts the ID SET is identical -- not the
    whole file, because provenance, files, statuses and fault links are carried forward and are
    not the generator's to produce.
    """
    import shutil
    import subprocess

    manifest_path = os.path.join(ROOT, "assets", "manifest.json")
    backup = str(tmp_path / "manifest.divergetest.bak")
    shutil.copy(manifest_path, backup)
    try:
        committed_recs = {a["id"]: a for a in json.load(open(manifest_path))["assets"]}
        r = subprocess.run([sys.executable, "build/gen_assets.py"], cwd=ROOT,
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr[-800:]
        emitted_recs = {a["id"]: a for a in json.load(open(manifest_path))["assets"]}
    finally:
        shutil.copy(backup, manifest_path)

    committed, emitted = set(committed_recs), set(emitted_recs)
    missing = emitted - committed
    extra = committed - emitted
    assert not missing, "%d record(s) the generator emits are not committed: %s" % (
        len(missing), sorted(missing)[:5])
    assert not extra, "%d committed record(s) the generator no longer emits: %s" % (
        len(extra), sorted(extra)[:5])
    assert len(committed) == 1850, len(committed)

    # NOT JUST THE IDS. Comparing id sets alone let the generator mangle every caption, every
    # alt_text and every shot_spec with the test green -- the same shape as the divergence this
    # was written to prevent, one field over. The GENERATED fields are compared too; the carried
    # ones (provenance, file, status, review_note, depicts.faults) are not, because they are not
    # the generator's to produce.
    gen_fields = ("kind", "role", "pair_with", "caption", "alt_text", "shot_spec", "priority",
                  "tags", "generated_from")
    drifted = []
    for aid in sorted(committed & emitted):
        for f in gen_fields:
            if committed_recs[aid].get(f) != emitted_recs[aid].get(f):
                drifted.append("%s.%s" % (aid, f))
    assert not drifted, "%d generated field(s) differ from what the generator emits: %s" % (
        len(drifted), drifted[:6])


def test_the_manifest_covers_the_corpus_and_not_a_corner_of_it():
    """142 style nodes, not three. Pinned because the three-node fact was true for months and
    "no count anywhere said" it -- WP-4.4's own report."""
    nodes = set()
    for a in MANIFEST["assets"]:
        nodes.update((a.get("depicts") or {}).get("nodes") or [])
    assert len(nodes) == 142, len(nodes)
    assert len(MANIFEST["assets"]) == 1850, len(MANIFEST["assets"])


# ------------------------------- an inherited assembly may not wear the overlay's citation

def test_an_inherited_assembly_cites_the_pack_that_actually_states_it():
    """The sharpest defect this renderer had, and it landed on OQ 7's own subject.

    `palladio-tuscan` records a base, a shaft, a capital and a pedestal, and deliberately no
    entablature: Palladio does not dimension his Tuscan entablature in the text and the plate
    numerals are illegible in every reachable scan. That is the whole of OQ 7. `resolve()` then
    supplies a cornice from `vignola-tuscan` -- correctly, because that is what an overlay is
    for. But the plate was titled "Palladio's Tuscan Order — cornice", drew Vignola's members,
    and footed them "AFTER: Palladio, I Quattro Libri, Venice 1570".

    One authority's figures under another's citation, on the exact assembly the corpus has an
    open question about BECAUSE that authority does not give it. Laundering produced by a
    drawing rather than by a record, and 34 of the 73 plates were doing it.
    """
    svg, _ = RP.render("palladio-tuscan", "cornice", module_in=12.0)
    assert "INHERITED: palladio-tuscan STATES NO CORNICE" in svg, svg[-700:]
    assert "Vignola" in svg, "the citation is not the pack that states these members"
    assert "I Quattro Libri" not in svg, \
        "Palladio is still cited for members palladio-tuscan does not state"


def test_a_pack_that_states_its_own_assembly_makes_no_inheritance_claim():
    """The disclosure has to be earned or it stops meaning anything."""
    svg, _ = RP.render("vignola-tuscan", "cornice", module_in=12.0)
    assert "INHERITED:" not in svg
    assert "Vignola" in svg


def test_states_assembly_walks_the_overlay_chain():
    assert RP.states_assembly("palladio-tuscan", "cornice") == "vignola-tuscan"
    assert RP.states_assembly("palladio-tuscan", "base") == "palladio-tuscan"
    assert RP.states_assembly("vignola-tuscan", "cornice") == "vignola-tuscan"


def test_every_plate_that_draws_inherited_members_says_so():
    """Measured across all 73: 34 draw an assembly their own pack does not state. Pinned as a
    count so a future overlay cannot quietly join them undisclosed."""
    inherited = 0
    for a, svg, _ in _plates():
        g = a["generated_from"]
        owner = RP.states_assembly(g["pack"], (g.get("parameters") or {}).get("assembly"))
        if owner and owner != g["pack"]:
            inherited += 1
            assert "INHERITED:" in svg, "%s draws %s's members undisclosed" % (a["id"], owner)
        else:
            assert "INHERITED:" not in svg, "%s claims inheritance it does not have" % a["id"]
    assert inherited == 34, inherited


# ---------------------- the RECORD and the PLATE must not contradict each other

def test_the_record_cites_the_same_authority_as_the_plate_it_points_at():
    """THE INK WAS FIXED AND THE CATALOGUE WAS NOT, and that is the whole of this test.

    When `states_assembly` was added, the SVG began disclosing that `palladio-tuscan`'s cornice
    members are Vignola's. `assets/manifest.json` went on filing that same record under
    `provenance.source: "Palladio, I Quattro Libri dell'Architettura, Venice 1570"` -- 34 of the
    73 generated records, across the four works OQ 7 through OQ 11 are about, served through
    `find_assets` to the MCP tool, the workbench API and the app.

    Nothing compared them. `check_assets.py` read the plate; this test reads both. The record's
    own alt_text closes "the drawing and the data cannot silently disagree", which is the claim
    being enforced here rather than asserted."""
    mismatches = []
    for a in GENERATED:
        g = a["generated_from"]
        owner = RP.states_assembly(g["pack"], (g.get("parameters") or {}).get("assembly"))
        src = (a.get("provenance") or {}).get("source") or ""
        inherited = bool(owner and owner != g["pack"])
        if inherited and "INHERITED" not in src:
            mismatches.append("%s: plate says the members are %s's, record cites %r"
                              % (a["id"], owner, src[:60]))
        if not inherited and "INHERITED" in src:
            mismatches.append("%s: record claims inheritance the plate does not" % a["id"])
    assert not mismatches, "\n".join(mismatches)


def test_the_two_overlay_walks_agree():
    """`gen_assets.py::_states_assembly` and `render_profile.py::states_assembly` are the same
    walk in two files, on purpose -- neither script may import the other, because they run at
    different times and one must not need the other present. Two copies of one rule is this
    repository's most-repeated defect (three spellings of the citation grammar, two of the sweep
    flag, two of the door's required wall), so the pair is held against each other here."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "gen_assets_probe", os.path.join(ROOT, "build", "gen_assets.py"))
    # gen_assets.py is a script with side effects; read its function out rather than exec it.
    src = open(os.path.join(ROOT, "build", "gen_assets.py")).read()
    assert "def _states_assembly(" in src, "gen_assets.py lost its overlay walk"

    ns = {"pe": RP.PE}
    start = src.index("def _states_assembly(")
    end = src.index("def _assembly_source(")
    exec(compile(src[start:end], "gen_assets_probe", "exec"), ns)
    theirs = ns["_states_assembly"]

    checked = 0
    for a in GENERATED:
        g = a["generated_from"]
        asm = (g.get("parameters") or {}).get("assembly")
        assert theirs(g["pack"], asm) == RP.states_assembly(g["pack"], asm), \
            "the two overlay walks disagree on %s/%s" % (g["pack"], asm)
        checked += 1
    assert checked == 73, checked


def test_the_carry_forward_is_an_allowlist():
    """Written as a four-name list of fields to KEEP, which denies by default: the next
    top-level field any tool adds would be destroyed on regeneration while the run printed
    "carried forward N field(s)". Same shape as the country denylist fixed in harvest_habs.py
    in the same commit."""
    src = open(os.path.join(ROOT, "build", "gen_assets.py")).read()
    code = "\n".join(l for l in src.splitlines() if not l.strip().startswith("#"))
    assert "CARRIED_FIELDS" not in code, "the carry-forward is a denylist again"
    assert "if k in GENERATED_FIELDS" in code, "the allowlist is not the thing being applied"
