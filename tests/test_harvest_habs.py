"""The four defects WP-4.4's harvester carried, each pinned so it cannot come back.

None of these was found by running the script: `www.loc.gov` answers 403 to CONNECT from this
environment, so the harvester has never once been executed against the live API. They were found
by reading it. That is exactly why they need tests -- the usual way a defect here gets noticed
is that somebody runs the thing, and nobody can.

Every test below was mutation-checked: the fix was reverted and the test was watched to go red.
A test that passes on the broken code is worse than no test, because it reports a guard.
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))

import modcache  # noqa: E402

H = modcache.load("harvest_habs", os.path.join(ROOT, "build", "harvest_habs.py"))
MANIFEST = json.load(open(os.path.join(ROOT, "assets", "manifest.json")))


# ---------------------------------------------------------------- defect 1: the rate limit

def test_the_pause_respects_the_libraries_documented_ceiling():
    """20 requests a minute is the loc.gov JSON API's documented limit, and it blocks for an
    hour above it. PAUSE_S was 1.0 -- 60/min -- so the first live run would have been blocked
    inside the first minute, counted every record as a FAIL, and returned 0."""
    assert H.PAUSE_S >= 3.0, (
        "PAUSE_S of %s is %.0f requests/minute against a documented ceiling of 20"
        % (H.PAUSE_S, 60.0 / H.PAUSE_S))
    assert H.JITTER_S > 0, "no jitter: a retry storm can phase-lock onto a fixed interval"


# ------------------------------------------------------- defect 2: the fabricated licence

def test_the_harvester_never_writes_a_licence():
    """`license` is a conclusion. The Library's sentence is byte-identical on a government
    photograph and on a HABS photograph OF somebody else's copyrighted drawing (Mount Pleasant
    pa0824 index 10), so no machine can read a licence out of it."""
    prov = H.provenance_from({
        "title": "Westover, Charles City County, VA",
        "url": "https://www.loc.gov/pictures/item/va0315/",
        "call_number": "HABS VA,19-WEST,1-",
        "rights_information": "No known restrictions on images made by the U.S. Government; "
                              "images copied from other sources may be restricted.",
    })
    assert "license" not in prov, "a harvester wrote a licence conclusion: %r" % prov.get("license")
    assert prov["rights_evidence"].startswith("No known restrictions"), \
        "the rights sentence must be carried verbatim as evidence"
    assert prov["rights_evidence_url"]


def test_no_rights_sentence_means_no_rights_evidence_invented():
    prov = H.provenance_from({"title": "x", "url": "https://example.invalid/1"})
    assert "rights_evidence" not in prov
    assert "license" not in prov


def test_the_source_file_carries_no_public_domain_literal():
    """The old code wrote `"license": "public-domain"` as a literal, before reading any field.
    Pinned at the source level too, because a future edit could reintroduce it somewhere
    provenance_from does not reach."""
    src = open(os.path.join(ROOT, "build", "harvest_habs.py")).read()
    code = "\n".join(l for l in src.splitlines()
                     if not l.strip().startswith("#") and '"""' not in l)
    assert '"license"' not in code and "'license'" not in code, \
        "harvest_habs.py assigns a licence somewhere"


# --------------------------------------------- defect 3: selecting the record with no pictures

def _hit(ident, brief, call="HABS VA,1-X,1-", title="A House, VA"):
    return {"id": ident, "url": "https://www.loc.gov/pictures/item/%s/" % ident,
            "title": title, "medium_brief": brief, "call_number": call}


def test_a_result_holding_no_pictures_is_refused():
    """Carter's Grove: the old selector took va2290, a HALS record whose entire holding is
    'Data Page(s): 9', because it was first and its title matched the manifest's county."""
    item, why = H.best_result({"results": [_hit("va2290", "Data Page(s): 9", call="HALS VA-1")]})
    assert item is None, "selected a record with no photographs"
    assert "photograph" in why


def test_habs_is_preferred_over_hals_when_both_hold_pictures():
    item, why = H.best_result({"results": [
        _hit("va2290", "Photo(s): 2, Data Page(s): 9", call="HALS VA-1"),
        _hit("va0654", "Photo(s): 82, Measured Drawing(s): 27", call="HABS VA,48-WIL.V,1-"),
    ]})
    assert item is not None and item["id"] == "va0654"
    assert "82" in why


def test_two_qualifying_results_are_refused_rather_than_ranked():
    """The old docstring claimed 'nothing clever about ranking' and then took the first, which
    is not a tie-break -- it is a coin toss with the evidence discarded."""
    item, why = H.best_result({"results": [
        _hit("va0315", "Photo(s): 73", call="HABS VA,19-WEST,1-"),
        _hit("va0316", "Photo(s): 12", call="HABS VA,19-WEST,2-"),
    ]})
    assert item is None, "picked one of two qualifying results instead of refusing"
    assert "choose between them" in why


def test_holding_counts_reads_the_inventory_string():
    assert H.holding_counts({"medium_brief": "Photo(s): 45, Data Page(s): 20"}) == (45, 0)
    assert H.holding_counts({"medium_brief": "Measured Drawing(s): 27"}) == (0, 27)
    assert H.holding_counts({"medium_brief": "Data Page(s): 9"}) == (0, 0)


# --------------------------------------- defect 4: 161 records collapsing onto eleven queries

def _wanted():
    return [x for x in MANIFEST["assets"] if x.get("status") == "wanted"]


def test_records_are_grouped_by_building_so_one_building_is_one_request():
    """161 building-named records name only eleven buildings, so the old code issued 161
    requests to receive eleven distinct answers -- and would have written the same result onto
    all 32 Hammond-Harwood records as though each had its own photograph."""
    queries = [H.query_for(x) for x in _wanted()]
    named = [q for q in queries if q]
    assert len(named) == 845, len(named)
    # 330 distinct queries over 327 distinct building names -- three names sit at two locations.
    # Before build/name_asset_buildings.py dealt each node's records round its own exemplars,
    # 161 records named ELEVEN buildings, and a perfect harvest would have returned eleven
    # photographs for 161 records. That is what the grouping and this number are both about.
    assert len(set(named)) == 330, len(set(named))


def test_the_guard_tests_the_right_condition():
    """The old guard refused to write when a record had NO building, which is the opposite of
    the failure: naming a building is precisely what did not disambiguate anything."""
    assert H.query_for({"provenance": {"building": "Westover", "location": "VA"}}) == "Westover VA"
    assert H.query_for({"provenance": {}, "depicts": {"nodes": ["english-georgian"]}}) is None, \
        "a record with no building must yield no query, never a style-name search"


def test_buildings_outside_the_united_states_are_named_not_searched():
    """HABS is a US survey by charter. Searching a foreign building returns 'no result holds a
    photograph' -- true, and the wrong reason."""
    assert H.outside_the_survey("Bath, England")
    assert H.outside_the_survey("Dublin, Ireland")
    assert "charter" in H.outside_the_survey("Bath, England")
    assert H.outside_the_survey("Charles City County, Virginia") is None
    assert H.outside_the_survey("Washington, District of Columbia") is None


def test_the_jurisdiction_test_is_an_allowlist_and_fails_in_the_cheap_direction():
    """The first version listed england/scotland/wales/ireland, which was right for the three
    style nodes the manifest covered then. At 142 nodes the locations run to Belgium, France,
    Germany, Greece, Italy, Mexico, the Netherlands, Norway, Ontario, South Africa, Spain,
    Sweden, Switzerland and Vatican City. A DENYLIST is wrong by default on the next country
    nobody thought of, and wrong in the expensive direction: it spends a rate-limited request
    and then misreports the cause. An allowlist is wrong only by letting a request through.

    Ontario is the case that makes it concrete -- it is not a country name, so no plausible
    denylist of countries would have caught it."""
    for foreign in ("Antwerp, Belgium", "Paris, France", "Munich, Germany", "Athens, Greece",
                    "Rome, Italy", "Mexico City, Mexico", "Amsterdam, Netherlands",
                    "Oslo, Norway", "Toronto, Ontario", "Cape Town, South Africa",
                    "Seville, Spain", "Stockholm, Sweden", "Bern, Switzerland",
                    "Vatican City"):
        assert H.outside_the_survey(foreign), "%s was treated as searchable" % foreign
    for home in ("Annapolis, Maryland", "Charleston, South Carolina", "Eldon, Iowa",
                 "Schenectady County, New York", "Malibu, California"):
        assert H.outside_the_survey(home) is None, "%s was refused" % home


def test_the_manifest_is_mostly_not_searchable_here_and_says_so():
    """188 of the 330 distinct queries are US buildings. The other 142 are named and skipped
    with jurisdiction as the cause rather than searched and reported as empty."""
    a = [x for x in MANIFEST["assets"] if x.get("status") == "wanted"]
    q = {}
    for x in a:
        s_ = H.query_for(x)
        if s_:
            q.setdefault(s_, (x.get("provenance") or {}).get("location"))
    outside = [k for k, loc in q.items() if H.outside_the_survey(loc)]
    assert len(q) == 330, len(q)
    assert len(outside) == 142, len(outside)


# ------------------------------------------------------------ CAPTCHA served behind a 200

def test_fetch_refuses_html_behind_a_success_status():
    """A datacentre IP -- which is what a CI runner is -- gets CAPTCHA and throttle pages from
    loc.gov with an HTTP 200. A status check cannot see them."""
    src = open(os.path.join(ROOT, "build", "harvest_habs.py")).read()
    assert "doctype html" in src.lower(), "fetch() does not inspect the body for an HTML page"
    assert "captcha" in src.lower()


# ---------------------------------------------------------------- it does not claim `sourced`

def test_nothing_is_marked_sourced_without_a_file():
    """The schema defines `sourced` as 'file present, unreviewed'. This script downloads no
    file, and the old code set `sourced` anyway on a record whose `file` stayed null."""
    src = open(os.path.join(ROOT, "build", "harvest_habs.py")).read()
    code = "\n".join(l for l in src.splitlines()
                     if not l.strip().startswith("#") and '"""' not in l)
    assert '"sourced"' not in code, "harvest_habs.py assigns status 'sourced' with no file"


def test_the_manifest_is_written_at_the_indent_gen_assets_uses():
    """indent=1 against gen_assets.py's indent=2 reformatted all 601 KB on every run."""
    src = open(os.path.join(ROOT, "build", "harvest_habs.py")).read()
    code = "\n".join(l for l in src.splitlines() if not l.strip().startswith("#"))
    assert "indent=2" in code, "the manifest is not written at gen_assets.py's indent"
    assert "indent=1" not in code
