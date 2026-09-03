#!/usr/bin/env python3
"""harvest_habs.py — WP-4.4's harvester for the Historic American Buildings Survey.

WHAT THIS IS FOR. `assets/` holds 1,850 asset records, 1,777 of them `status: wanted` — a
shot spec, alt text, what it depicts, and no file. (It held 322 over three style nodes when this
was written; the manifest was a frozen snapshot of a generator that had been tracking the whole
corpus, which is `oq/regenerating-the-asset-manifest-discards-what-was-added-to-it`.) HABS is the obvious first source: it is a
US Government survey, professionally measured, and its drawings and large-format photographs
are exactly what the `measured-drawing` and `photograph` records ask for. This script finds the
Library of Congress SURVEY RECORD for each building a record names and writes back what the
response actually says about it.

IT HAS NEVER BEEN RUN AGAINST THE LIVE API. The environment this was written in denies
`www.loc.gov` at the proxy:

    curl: (56) CONNECT tunnel failed, response 403
    gateway answered 403 to CONNECT (policy denial or upstream failure)  host www.loc.gov:443

So the request shape is written from the loc.gov JSON API's documented behaviour and the parsing
is defensive throughout. `--dry-run` is the default.

    python3 build/harvest_habs.py --dry-run                 # what it would ask for
    python3 build/harvest_habs.py --live --limit 5          # actually fetch, write nothing
    python3 build/harvest_habs.py --live --write --limit 5  # and update assets/manifest.json

FOUR THINGS IT USED TO DO WRONG, ALL FIXED HERE, ALL FOUND BY READING RATHER THAN BY RUNNING —
because it cannot be run from here, which is exactly why they survived so long.

1. IT WAS THREE TIMES TOO FAST. `PAUSE_S` was 1.0, i.e. 60 requests a minute against a
   documented ceiling of 20 for the JSON API; loc.gov blocks for an hour above it. The first
   live run would have earned the block inside the first minute, counted every subsequent
   record as a `FAIL`, and then RETURNED 0. A harvester that reports success while fetching
   nothing is the "unjudged reported as passed" failure in a new place.

2. IT ASSERTED A LICENCE THE SOURCE DOES NOT STATE. `provenance_from` wrote
   `license: "public-domain"` unconditionally, before reading a single field, and its own
   docstring conceded this was "the one claim here that does not come from the response". LoC's
   actual sentence is collection-level boilerplate — "No known restrictions on images made by
   the U.S. Government; images copied from other sources may be restricted" — and it is
   byte-identical on a government photograph and on Mount Pleasant `pa0824` index 10, which is
   a HABS photograph OF a third party's 1897 drawing held by the Free Library of Philadelphia.
   THIS SCRIPT NO LONGER WRITES `license` AT ALL. It records the sentence verbatim in
   `rights_evidence` with the URL it was read from, and a person draws the conclusion. Laundering
   a guess as `measured` is this corpus's cardinal sin; asserting a licence off boilerplate is
   the same sin wearing a lawyer's coat.

3. IT PICKED THE RECORD WITH NO PICTURES IN IT. `best_result` took "the first item that has both
   a title and a stable id". For Carter's Grove that is `va2290`, a HALS record whose entire
   holding is "Data Page(s): 9" — no images — and whose title matches the manifest's stated
   county exactly, while `va0654`, which holds 82 photographs and 27 measured drawings, says
   "Williamsburg" and does not match. Selection now REQUIRES a non-zero photograph or measured
   drawing count, prefers HABS over HALS/HAER, and REFUSES rather than ranks when two candidates
   still qualify — which is what the old docstring said it did and did not do.

4. 161 RECORDS COLLAPSED ONTO ELEVEN QUERIES, AND THE GUARD AGAINST IT TESTED THE WRONG THING.
   `query_for` keys on `provenance.building`, and the 161 building-named records name only
   eleven buildings — Westover 38, Hammond-Harwood 32, Drayton Hall 32, Mount Pleasant 32, and
   seven more. All 32 Hammond-Harwood records issued the identical query and would have taken
   the identical result. The existing guard tested `not provenance.building`, which is the
   opposite condition: naming a building does not disambiguate anything. The fix is to stop
   pretending each record gets its own picture. Records are GROUPED BY BUILDING and each
   building is fetched ONCE — eleven requests, not 161, which also puts the run comfortably
   inside the rate limit — and every record naming that building gets the SURVEY's provenance,
   which is true of all of them. Choosing which of Westover's 73 photographs shows the water
   table is human work and is not attempted here.

WHAT IT WILL NOT DO. It never sets `approved` — a human's word, per the schema. It never sets
`sourced` either, and that is a change: the schema defines `sourced` as "file present,
unreviewed", this script downloads no file, and the old code set `sourced` anyway on a record
whose `file` stayed `null`. A record it has enriched is still `wanted`, now with a real survey
to go and look at.
"""
import argparse
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets", "manifest.json")

sys.path.insert(0, os.path.join(ROOT, "build"))
import manifest_io  # noqa: E402  -- the one atomic writer for this file

# The loc.gov JSON API. `fo=json` is the documented way to ask any collection page for JSON;
# `c` is the page size. HABS/HAER/HALS live in the `hh` collection under /pictures/.
BASE = "https://www.loc.gov/pictures/collection/hh/"
# The Library blocks by User-Agent, and "contact via the repository" is not a contact when the
# repository is private. HARVEST_CONTACT must be set to a reachable address before a live run;
# main() refuses --live without it rather than presenting an unreachable string to an operator
# who may need to reach us.
CONTACT = os.environ.get("HARVEST_CONTACT", "")
USER_AGENT = ("Traditional-Design-Language/0.6 (corpus research; %s) python-urllib"
              % (CONTACT or "NO CONTACT SET"))

# 20 requests per minute is the Library's documented ceiling for the JSON API, and it blocks for
# an hour above it. 3.5s is 17/min, with jitter so a retry storm cannot phase-lock onto it.
PAUSE_S = 3.5
JITTER_S = 0.75

# What the Library says about every item in this collection, and the only rights text there is.
RIGHTS_URL = "https://www.loc.gov/research-centers/prints-and-photographs/about-this-research-center/rights-and-restrictions/"


def search_url(query, count=25):
    return BASE + "?" + urllib.parse.urlencode({"q": query, "fo": "json", "c": count})


def pause():
    time.sleep(PAUSE_S + random.uniform(0, JITTER_S))


# The largest legitimate response here is a 25-item search page; 8 MB is four orders of
# magnitude of headroom and still bounded. `r.read()` with no argument is not: `timeout` bounds
# per-socket inactivity, not total transfer, so a slow-drip or hostile body streams until the
# process dies. This runs on a one-core container with no swap, and `json.loads` would then
# double whatever was read.
MAX_BODY = 8 * 1024 * 1024


class _ConfinedRedirects(urllib.request.HTTPRedirectHandler):
    """Follow a redirect only while it stays on the host we asked for.

    urllib follows up to ten hops to any host by default. The base URL is a constant here, so
    this needs loc.gov or an intervening proxy to redirect — but the script runs with the
    operator's network position, and "the destination is whatever the remote says" is a
    server-side request forgery primitive whichever way it is reached."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urllib.parse.urlsplit(newurl).hostname != urllib.parse.urlsplit(req.full_url).hostname:
            raise urllib.error.HTTPError(
                req.full_url, code,
                "refusing a redirect off %s to %s" % (
                    urllib.parse.urlsplit(req.full_url).hostname, newurl), headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_OPENER = urllib.request.build_opener(_ConfinedRedirects)


def fetch(url, timeout=30):
    """Fetch and parse, refusing anything that is not actually JSON.

    A datacentre IP — which is what a CI runner is — gets served CAPTCHA and throttle pages by
    loc.gov with an HTTP 200, so a status check cannot see them. The body is inspected before it
    is trusted."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT,
                                               "Accept": "application/json"})
    with _OPENER.open(req, timeout=timeout) as r:
        ctype = (r.headers.get("Content-Type") or "").lower()
        body = r.read(MAX_BODY + 1)
        if len(body) > MAX_BODY:
            raise ValueError("response exceeds %d bytes; refusing to buffer it" % MAX_BODY)
    head = body[:512].lstrip().lower()
    if head.startswith(b"<!doctype html") or head.startswith(b"<html"):
        raise ValueError("served HTML, not JSON — a CAPTCHA or throttle page behind a 200")
    for marker in (b"captcha", b"rate limit", b"too many requests"):
        if marker in head:
            raise ValueError("body carries %r behind a 200" % marker.decode())
    if "json" not in ctype and not head.startswith((b"{", b"[")):
        raise ValueError("content-type %r and the body is not JSON" % ctype)
    return json.loads(body.decode("utf-8"))


def query_for(asset):
    """The search string for one asset record, or None.

    Built from what the record already states rather than from anything invented. A record that
    names no building yields None: searching it on its style name alone is what made every
    English Georgian record ask for `?q=english+georgian` and take the same answer."""
    prov = asset.get("provenance") or {}
    if not prov.get("building"):
        return None
    bits = [prov["building"]]
    if prov.get("location"):
        bits.append(prov["location"])
    return " ".join(bits)


# HABS IS A UNITED STATES SURVEY, BY CHARTER, and the manifest is not a United States shot list.
# Searching a foreign building anyway spends a request to report "no result holds a photograph",
# which is true and says the wrong thing: the reason is jurisdiction, not holdings.
#
# THIS IS AN ALLOWLIST OF US STATES, NOT A DENYLIST OF COUNTRIES, and that direction is the whole
# of it. The first version listed england/scotland/wales/ireland, which was right for the three
# style nodes the manifest covered then. At 142 nodes the locations run to Belgium, France,
# Germany, Greece, Italy, Mexico, the Netherlands, Norway, Ontario, South Africa, Spain, Sweden,
# Switzerland and Vatican City -- and a denylist is wrong by DEFAULT on the next country nobody
# thought of, in the direction that wastes the request and misreports the cause. An allowlist is
# wrong in the direction that spends a request on a building HABS might actually hold, which is
# merely a wasted request and a truthful "no result".
US_STATES = frozenset("""
alabama alaska arizona arkansas california colorado connecticut delaware florida georgia hawaii
idaho illinois indiana iowa kansas kentucky louisiana maine maryland massachusetts michigan
minnesota mississippi missouri montana nebraska nevada ohio oklahoma oregon pennsylvania
tennessee texas utah vermont virginia washington wisconsin wyoming
""".split()) | frozenset([
    "new hampshire", "new jersey", "new mexico", "new york", "north carolina", "north dakota",
    "rhode island", "south carolina", "south dakota", "west virginia",
    "district of columbia", "d.c.", "dc", "puerto rico", "guam", "virgin islands",
])


def outside_the_survey(location):
    """Why HABS cannot hold this building, or None if it might.

    Reads the LAST comma-separated part of the location, which is where the corpus's exemplar
    records put the state or the country."""
    if not location:
        return None                      # nothing to judge on; let the query run and report
    tail = location.split(",")[-1].strip().lower()
    if not tail or tail in US_STATES:
        return None
    if any(tail.endswith(" " + s) or tail == s for s in US_STATES):
        return None
    return ("HABS is a United States survey by charter and this building's location ends in %r, "
            "which is not a US state; no query here will find it. Those records need a different "
            "source, and every English photograph checked so far is share-alike, which is a "
            # The slug is kept on ONE line deliberately: check_citations.py reads line by
            # line, so a slug split across a string-literal break reads to it as a truncated
            # id and is reported dangling. Third instance of that same line-by-line gotcha --
            # see CLAUDE.md on the WP-8.5 commit subject and on a code span straddling a
            # newline. Do not re-wrap this string.
            "ruling rather than a fetch"
            " (oq/a-share-alike-photograph-has-no-home-in-the-asset-schema)."
            % location.split(",")[-1].strip())


_COUNT_RE = re.compile(r"(photo|measured drawing|drawing)\(s\)\s*:\s*(\d+)", re.I)


def holding_counts(item):
    """How many pictures a survey record actually holds, read from its own inventory string.

    `medium_brief` looks like "Photo(s): 45, Color Transparencies: 1, Data Page(s): 20". A
    record whose whole holding is data pages is a bibliographic stub, not a source of images,
    and it is the one the old selector kept choosing."""
    text = " ".join(str(item.get(k) or "") for k in ("medium_brief", "medium", "description"))
    if isinstance(item.get("medium"), list):
        text += " " + " ".join(str(x) for x in item["medium"])
    photos = drawings = 0
    for kind, n in _COUNT_RE.findall(text):
        if kind.lower() == "photo":
            photos += int(n)
        else:
            drawings += int(n)
    return photos, drawings


def survey_prefix(item):
    """HABS / HAER / HALS, from whichever identifier carries it."""
    for k in ("call_number", "number", "shelf_id", "title"):
        v = item.get(k)
        if isinstance(v, list):
            v = v[0] if v else None
        if not v:
            continue
        m = re.search(r"\b(HABS|HAER|HALS)\b", str(v).upper())
        if m:
            return m.group(1)
    return None


def best_result(payload):
    """One survey record, or None — and it REFUSES rather than ranks when the choice is not clear.

    Three conditions, in order. It must hold pictures: a record whose inventory shows no
    Photo(s) and no Measured Drawing(s) is dropped, which is what keeps Carter's Grove off
    `va2290`. HABS is preferred over HAER and HALS, because these records are buildings. And if
    more than one candidate still stands, this returns None with a reason: a wrong building
    sourced automatically is worse than a record left alone, and picking the first is not a
    tie-break, it is a coin toss with the evidence thrown away."""
    candidates = []
    for item in (payload.get("results") or []):
        if not isinstance(item, dict):
            continue
        if not (item.get("title") and (item.get("id") or item.get("url"))):
            continue
        photos, drawings = holding_counts(item)
        if photos == 0 and drawings == 0:
            continue
        candidates.append((item, photos, drawings, survey_prefix(item)))
    if not candidates:
        return None, "no result holds a photograph or a measured drawing"
    habs = [c for c in candidates if c[3] == "HABS"]
    if habs:
        candidates = habs
    if len(candidates) > 1:
        names = ", ".join(str((c[0].get("id") or c[0].get("url"))) for c in candidates[:4])
        return None, "%d results qualify and nothing here can choose between them (%s)" % (
            len(candidates), names)
    item, photos, drawings, _ = candidates[0]
    return item, "photo(s): %d, measured drawing(s): %d" % (photos, drawings)


def provenance_from(item):
    """Only fields the response actually carries, plus the rights sentence VERBATIM.

    No `license`. That is a conclusion and this is a machine; see the module docstring."""
    out = {"source": "Historic American Buildings Survey, Library of Congress"}
    # `building` IS NOT WRITTEN. It used to map from the response's `title`, and `--write` merges
    # this over the record -- so the first live run would have replaced all 786 curated names
    # ("Westover") with LoC titles ("Westover, State Route 5, Charles City, Charles City County,
    # VA"), while `location` stayed as it was. `query_for` concatenates both, so the NEXT run's
    # query would have been worse than the first, and `gen_assets` carries provenance forward, so
    # it would have been permanent. The curated name is what this script searches ON; overwriting
    # it with what it found is the class 32b7c9e exists to stop, one file over. The response's
    # title goes to `found_title` instead, where a reviewer can compare the two.
    for key, field in (("found_title", "title"), ("date", "date"), ("author", "creator")):
        v = item.get(field)
        if isinstance(v, list):
            v = v[0] if v else None
        if v:
            out[key] = str(v)
    url = item.get("url") or item.get("id")
    if url:
        out["url"] = str(url)
    for k in ("number", "call_number", "shelf_id"):
        v = item.get(k)
        if isinstance(v, list):
            v = v[0] if v else None
        if v and "HABS" in str(v).upper():
            out["habs_number"] = str(v)
            break
    rights = item.get("rights_information") or item.get("rights_advisory") or item.get("rights")
    if isinstance(rights, list):
        rights = rights[0] if rights else None
    if rights:
        out["rights_evidence"] = str(rights)
        out["rights_evidence_url"] = str(url or RIGHTS_URL)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true", default=True,
                    help="the default: print what it would request and change, touching neither "
                         "the network nor the corpus.")
    ap.add_argument("--live", dest="dry_run", action="store_false",
                    help="actually make requests. Without it nothing touches the network.")
    ap.add_argument("--write", action="store_true",
                    help="update assets/manifest.json. Requires --live. Never sets `sourced` or "
                         "`approved`, and never writes a licence.")
    ap.add_argument("--limit", type=int, default=0, help="only the first N buildings")
    ap.add_argument("--kind", default=None,
                    help="only records of this kind, e.g. measured-drawing")
    a = ap.parse_args()
    if not a.dry_run and not CONTACT:
        print("Refusing --live with no HARVEST_CONTACT set. The Library rate-limits and blocks "
              "by User-Agent, and this one would name a private repository as its contact. "
              "Set HARVEST_CONTACT to an address somebody actually reads.")
        return 5
    if a.write and a.dry_run:
        print("--write requires --live: refusing to write provenance nothing fetched.")
        return 2

    doc = json.load(open(ASSETS))
    wanted = [x for x in doc["assets"] if x.get("status") == "wanted"
              and (a.kind is None or x.get("kind") == a.kind)]

    # GROUPED BY BUILDING, which is the whole of fix 4. Eleven requests, not 161.
    groups, generic = {}, []
    for x in wanted:
        q = query_for(x)
        if q is None:
            generic.append(x)
        else:
            groups.setdefault(q, []).append(x)
    outside = {}
    for q in list(groups):
        why = outside_the_survey((groups[q][0].get("provenance") or {}).get("location"))
        if why:
            outside[q] = why
            del groups[q]
    order = sorted(groups)
    if a.limit:
        order = order[:a.limit]

    print("%d wanted record(s) of %d in the file, naming %d distinct building(s)"
          % (len(wanted), len(doc["assets"]), len(groups)))
    if generic:
        n_wrong = sum(1 for x in generic if x.get("role") == "incorrect")
        print("%d name no building at all. %d of those are `role: incorrect`, and the corpus "
              "names buildings that exemplify a style and never ones that exemplify a fault, so "
              "they are not an omission and no archive will ever hold them. They are skipped, "
              "not searched." % (len(generic), n_wrong))
    for q in sorted(outside):
        print("  OUTSIDE %s — %s" % (q, outside[q]))
    if a.dry_run:
        print("\nDRY RUN — no network, no writes. One request per building:\n")

    found = skipped = failed = enriched = 0
    consecutive_failures = 0
    for q in order:
        members = groups[q]
        url = search_url(q)
        if a.dry_run:
            print("  GET   %s\n        for %d record(s): %s%s"
                  % (url, len(members), ", ".join(m["id"] for m in members[:2]),
                     " …" if len(members) > 2 else ""))
            continue
        try:
            payload = fetch(url)
        except Exception as e:                       # network, HTTP, JSON, CAPTCHA — all one here
            failed += 1
            consecutive_failures += 1
            print("  FAIL  %s — %s" % (q, e))
            # Fix 1 of this file is about not earning an hour-long block. Once blocked, the old
            # loop spent the remaining twelve minutes proving it, one 3.5 s pause at a time, and
            # then exited 0 with a tally. Three in a row is a wall, not a coincidence.
            if consecutive_failures >= 3:
                print("\n  STOP  three consecutive failures. This is a wall (a block, a CAPTCHA "
                      "or an outage), not a run with some bad records in it. %d building(s) were "
                      "not attempted. Nothing was written." % (len(order) - order.index(q) - 1))
                return 4
            pause()
            continue
        consecutive_failures = 0
        item, why = best_result(payload)
        if item is None:
            skipped += 1
            print("  NONE  %s — %s; %d record(s) left untouched" % (q, why, len(members)))
        else:
            found += 1
            prov = provenance_from(item)
            print("  OK    %s -> %s (%s)" % (q, prov.get("url", "?"), why))
            if "rights_evidence" not in prov:
                print("        no rights statement in the response; none invented")
            if a.write:
                for m in members:
                    m["provenance"] = {**(m.get("provenance") or {}), **prov}
                    m["review_note"] = (
                        "Survey located automatically by build/harvest_habs.py in the loc.gov "
                        "HABS collection (%s). NOT sourced: no file has been downloaded and no "
                        "individual photograph has been chosen — this names the survey, which "
                        "holds %s. NOT licensed: `rights_evidence` is what the Library says, "
                        "verbatim; drawing a `license` from it is a person's judgment, because "
                        "the same sentence sits on a government photograph and on a HABS "
                        "photograph of somebody else's copyrighted drawing."
                        % (prov.get("url", "?"), why))
                    enriched += 1
        pause()

    print("\nbuildings: found %d, refused %d, failed %d — records enriched %d"
          % (found, skipped, failed, enriched))
    # AND THE EXIT CODE SAYS SO. This file's own docstring names "counted every subsequent record
    # as a FAIL, and then RETURNED 0" as a defect it fixed, and only the rate limit had actually
    # changed: a run where every request failed still exited 0, which is the harvester reporting
    # success while fetching nothing. Any failure is a non-zero exit now; the three-in-a-row
    # circuit breaker above is the separate case of stopping early.
    if a.write and enriched:
        doc["counts"]["by_status"] = {}
        for x in doc["assets"]:
            doc["counts"]["by_status"][x["status"]] = doc["counts"]["by_status"].get(x["status"], 0) + 1
        # indent=2 matches gen_assets.py. Writing indent=1 here reformatted all 601 KB on every
        # run, so the real change drowned in a whole-file diff.
        manifest_io.write_manifest(doc, ASSETS)
        print("wrote %s" % os.path.relpath(ASSETS, ROOT))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
