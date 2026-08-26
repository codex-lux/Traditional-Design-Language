#!/usr/bin/env python3
"""harvest_habs.py — WP-4.4's harvester for the Historic American Buildings Survey.

WHAT THIS IS FOR. `assets/` holds 322 asset records, every one of them `status: wanted` — a
shot spec, alt text, what it depicts, and no file. HABS is the obvious first source: it is
public domain, professionally measured, and its measured drawings and large-format photographs
are exactly what the `measured-drawing` and `photograph` records ask for. This script searches
the Library of Congress's HABS collection for the buildings a record names, and writes back the
provenance a `sourced` record needs.

IT HAS NEVER BEEN RUN AGAINST THE LIVE API, and that is stated here rather than discovered by
whoever runs it first. The environment this was written in denies `www.loc.gov` at the proxy:

    curl: (56) CONNECT tunnel failed, response 403
    gateway answered 403 to CONNECT (policy denial or upstream failure)  host www.loc.gov:443

So the request shape below is written from the loc.gov JSON API's documented behaviour and the
parsing is defensive throughout — every field is fetched with `.get`, every list access is
guarded, and `--dry-run` (the default) prints what it WOULD request and change without touching
the network or the corpus. Run `--dry-run` first, read the URLs, and only then let it out.

    python3 build/harvest_habs.py --dry-run                 # what it would ask for
    python3 build/harvest_habs.py --dry-run --limit 5       # the first five records
    python3 build/harvest_habs.py --live --limit 5          # actually fetch, write nothing
    python3 build/harvest_habs.py --live --write --limit 5  # and update assets/

WHAT IT WILL NOT DO. It never sets `status: approved` — that is a human's word, per the asset
schema's own definition. It never invents a `habs_number` or a `license`: a record whose search
returns nothing is left `wanted`, because a `sourced` record with no provenance is worse than an
absent one. And it does not download image files; it records the URL and the identifiers, so
the corpus stays text and the decision about carrying binaries stays open.
"""
import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets", "manifest.json")

# The loc.gov JSON API. `fo=json` is the documented way to ask any collection page for JSON;
# `c` is the page size. HABS/HAER/HALS live in the `hh` collection under /pictures/.
BASE = "https://www.loc.gov/pictures/collection/hh/"
USER_AGENT = ("Traditional-Design-Language/0.6 (corpus research; contact via the repository) "
              "python-urllib")
PAUSE_S = 1.0          # be a good citizen; the API asks for it and nothing here is urgent


def search_url(query, count=10):
    return BASE + "?" + urllib.parse.urlencode({"q": query, "fo": "json", "c": count})


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT,
                                               "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def query_for(asset):
    """The search string for one asset record.

    Built from what the record already states rather than from anything invented: the building
    if `provenance.building` names one, otherwise the style nodes it depicts and the slot it is
    about. A record that names neither yields None and is skipped rather than searched for
    something arbitrary."""
    prov = asset.get("provenance") or {}
    if prov.get("building"):
        bits = [prov["building"]]
        if prov.get("location"): bits.append(prov["location"])
        return " ".join(bits)
    depicts = asset.get("depicts") or {}
    nodes = depicts.get("nodes") or []
    if not nodes: return None
    return nodes[0].replace("-", " ")


def best_result(payload):
    """One result, or None. Deliberately conservative: the first item that has both a title and
    a stable id, and nothing clever about ranking — a wrong image sourced automatically is worse
    than a record left `wanted`, and the human reviewing `sourced` records is the point."""
    for item in (payload.get("results") or []):
        if not isinstance(item, dict): continue
        if item.get("title") and (item.get("id") or item.get("url")):
            return item
    return None


def provenance_from(item):
    """Only fields the response actually carries. No defaults, no guesses; `license` is set to
    public-domain because that is what the HABS collection IS, and it is the one claim here
    that does not come from the response."""
    out = {"source": "Historic American Buildings Survey, Library of Congress",
           "license": "public-domain"}
    for key, field in (("building", "title"), ("date", "date"), ("author", "creator")):
        v = item.get(field)
        if isinstance(v, list): v = v[0] if v else None
        if v: out[field if False else key] = str(v)
    url = item.get("url") or item.get("id")
    if url: out["url"] = str(url)
    for k in ("number", "call_number", "shelf_id"):
        v = item.get(k)
        if isinstance(v, list): v = v[0] if v else None
        if v and "HABS" in str(v).upper():
            out["habs_number"] = str(v); break
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true", default=True,
                    help="the default: print what it would request and change, touching neither "
                         "the network nor the corpus.")
    ap.add_argument("--live", dest="dry_run", action="store_false",
                    help="actually make requests. Without it nothing touches the network.")
    ap.add_argument("--write", action="store_true",
                    help="update assets/assets.json. Requires --live, and never sets `approved`.")
    ap.add_argument("--limit", type=int, default=0, help="only the first N wanted records")
    ap.add_argument("--kind", default=None,
                    help="only records of this kind, e.g. measured-drawing")
    a = ap.parse_args()
    if a.write and a.dry_run:
        print("--write requires --live: refusing to write provenance nothing fetched.")
        return 2

    doc = json.load(open(ASSETS))
    wanted = [x for x in doc["assets"] if x.get("status") == "wanted"
              and (a.kind is None or x.get("kind") == a.kind)]
    if a.limit: wanted = wanted[:a.limit]
    print("%d wanted record(s) selected of %d in the file" % (len(wanted), len(doc["assets"])))
    if a.dry_run:
        print("DRY RUN — no network, no writes. The requests it would make:\n")

    # A record with no `provenance.building` can only be searched on its style name, and every
    # record about that style then searches for the same thing and gets the same first result.
    # Found by running the dry run: the first four records all produced
    # `?q=english+georgian`. Reported here rather than left for whoever runs it live to notice
    # after 322 records point at one photograph.
    generic = [x for x in wanted if not (x.get("provenance") or {}).get("building")]
    if generic:
        print("\n%d of %d selected records name no building, so they would be searched on their "
              "STYLE alone and would all match the same result. Sourcing those automatically "
              "would produce one image cited by many records, which is worse than none. Give "
              "them a `provenance.building` first, or run with --kind to work through the "
              "records that do name one.\n" % (len(generic), len(wanted)))
        if a.write:
            print("Refusing to --write while %d selected records would search generically." % len(generic))
            return 3

    found = skipped = failed = 0
    for asset in wanted:
        q = query_for(asset)
        if not q:
            skipped += 1
            print("  SKIP  %s — the record names no building and no style to search on"
                  % asset["id"])
            continue
        url = search_url(q)
        if a.dry_run:
            print("  GET   %s\n        for %s" % (url, asset["id"]))
            continue
        try:
            payload = fetch(url)
        except Exception as e:                       # network, HTTP, JSON — all the same here
            failed += 1
            print("  FAIL  %s — %s" % (asset["id"], e))
            time.sleep(PAUSE_S)
            continue
        item = best_result(payload)
        if item is None:
            skipped += 1
            print("  NONE  %s — no usable result; left `wanted`" % asset["id"])
        else:
            found += 1
            prov = provenance_from(item)
            print("  OK    %s -> %s" % (asset["id"], prov.get("url", "?")))
            if a.write:
                asset["provenance"] = {**(asset.get("provenance") or {}), **prov}
                asset["status"] = "sourced"
                asset["review_note"] = (
                    "Sourced automatically by build/harvest_habs.py from the loc.gov HABS "
                    "collection. NOT reviewed: nobody has looked at this image and confirmed it "
                    "shows what the record says it shows. Set `approved` only by hand.")
        time.sleep(PAUSE_S)

    print("\nfound %d, skipped %d, failed %d" % (found, skipped, failed))
    if a.write and found:
        doc["counts"]["by_status"] = {}
        for x in doc["assets"]:
            doc["counts"]["by_status"][x["status"]] = doc["counts"]["by_status"].get(x["status"], 0) + 1
        json.dump(doc, open(ASSETS, "w"), indent=1, ensure_ascii=False)
        open(ASSETS, "a").write("\n")
        print("wrote %s" % os.path.relpath(ASSETS, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
