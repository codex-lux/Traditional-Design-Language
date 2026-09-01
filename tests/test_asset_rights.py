"""`asset_rights()` — the licence gate, which had no test at all.

It is the only programmatic route by which an asset's rights reach anyone: the MCP tool
`tdl_find_assets`, the workbench's `/api/assets`, and the app all read `find_assets`, and before
this branch that projection returned a file path with no licence, no attribution and no author.
So the moment a licensed image entered the manifest, compliance was impossible by construction.

A new clearance gate on that route, in a diff about rights and provenance, with nothing
exercising it. These are the cases that matter.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from mcp_server import core  # noqa: E402


def R(license=None, file=None, **prov):
    a = {"id": "x", "kind": "photograph", "role": "correct", "status": "wanted",
         "caption": "c", "alt_text": "a" * 60, "provenance": dict(prov)}
    if license is not None:
        a["provenance"]["license"] = license
    if file is not None:
        a["file"] = file
    return a


F = {"path": "assets/generated/x.svg"}


def test_unknown_is_unjudged_and_never_a_refusal():
    """`unjudged` and `no` are different claims and this corpus never collapses the first into
    the second. A bool could not tell "nobody has looked" (1,716 records) from "a person ruled
    this share-alike"."""
    assert core.asset_rights(R())["publishable"] == "unjudged"
    assert core.asset_rights(R(license="unknown"))["publishable"] == "unjudged"


def test_share_alike_is_refused_not_unjudged():
    for lic in ("cc-by", "cc-by-sa"):
        assert core.asset_rights(R(license=lic, file=F))["publishable"] == "no", lic


def test_attribution_is_required_for_cc_by_even_though_it_is_refused():
    """The object must not simultaneously assume cc-by can occur and say nothing about what it
    would need."""
    r = core.asset_rights(R(license="cc-by", file=F))
    assert r["attribution_required"] is True


def test_a_licence_is_not_a_clearance_for_a_file_that_does_not_exist():
    """61 `owned` records carry `file: null` and came back publishable -- a clearance for
    nothing."""
    assert core.asset_rights(R(license="owned"))["publishable"] == "no-file"
    assert core.asset_rights(R(license="owned", file=F))["publishable"] == "yes"
    assert core.asset_rights(R(license="public-domain"))["publishable"] == "no-file"


def test_rights_evidence_is_carried_and_never_becomes_a_conclusion():
    sentence = ("No known restrictions on images made by the U.S. Government; images copied "
                "from other sources may be restricted.")
    r = core.asset_rights(R(rights_evidence=sentence,
                            rights_evidence_url="https://www.loc.gov/x"))
    assert r["rights_evidence"] == sentence
    assert r["rights_evidence_url"]
    # Evidence a harvester collected is not a licence anybody ruled on.
    assert r["publishable"] == "unjudged"
    assert r["license"] == "unknown"


def test_every_record_in_the_corpus_gets_a_rights_object():
    """No record may reach a consumer without one, whatever its shape."""
    D = core._data()
    seen = set()
    for a in D["assets"]:
        r = core.asset_rights(a)
        assert set(r) >= {"license", "publishable", "attribution_required"}
        seen.add(r["publishable"])
    assert seen <= {"unjudged", "yes", "no", "no-file"}, seen
    assert "yes" in seen and "unjudged" in seen, seen


def test_find_assets_serves_the_rights_object():
    r = core.find_assets(status="sourced", limit=3)
    assert r["matches"] == 73, r["matches"]
    for a in r["assets"]:
        assert a["rights"]["publishable"] == "yes", a["id"]
        assert a["generated_from"], a["id"]


def test_find_assets_can_be_asked_for_a_pack():
    """The 73 records that HAVE a file depict a pack and an assembly -- never a node or a slot --
    so before `pack` existed no filter could reach a single sourced record."""
    assert core.find_assets(pack="vignola-doric")["matches"] == 3
    assert core.find_assets(pack="not-a-pack")["matches"] == 0
