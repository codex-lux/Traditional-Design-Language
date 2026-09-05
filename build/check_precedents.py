#!/usr/bin/env python3
"""check_precedents.py -- the building behind every exemplar, held to a record a checker can resolve.

WP-11.1 (4 Sep 2026). Until this package an exemplar was `{name, location, year, note}` and nothing
else: 482 exemplars across 164 style nodes, 410 distinct buildings, and NOT ONE carried a HABS
number, a register reference or a link. A reader could find Westover; a checker could resolve
nothing. `precedents/<id>.json` is the building's own record -- shared by every node that names
it -- with the archival references that locate it and, where the Historic American Buildings
Survey wrote one, its written data quoted verbatim. An exemplar names its record through
`precedent`; this checker holds the two to each other in BOTH directions, because a record that
lists a node whose exemplars do not name it is a citation nobody made, and an exemplar naming a
record that does not exist is the old state wearing a new key.

What is checked, and what is deliberately not:

  * id == filename; the schema; every `nodes[]` entry is a style id. (Copied from check_rooms.)
  * Every `refs[].id` has the shape its `kind` promises -- a HABS number is `XX-nnn`, a Library
    item id is `xx0000`, a National Register reference is eight digits -- and every ref carries
    either an id or a url. A ref with neither locates nothing.
  * Every ref and every survey carries `retrieved` and `via` (the schema requires both; this
    restates it so the message names the reason): a reference nobody read on a stated day by a
    stated route was typed from memory, which is how a wrong id is laundered as a citation.
  * No record carries a `license` key anywhere, at any depth. A licence is a conclusion a person
    draws from `rights_evidence`; the asset schema says why, and the same rule holds here.
  * Every `measurements[].from_quote` indexes a quote that exists.
  * Every kit parameter or slot `source` of the form `precedents/<id>#survey.<field>` or
    `precedents/<id>#measurements[<n>]` resolves to a record, a quote of that field, or a
    measurement at that index. That is the convention by which a kit figure cites a survey;
    `check_kits.py` reads `source` for a PACK name on an `expr` parameter (line ~516), so a
    precedent pointer must sit on a `value`/`range` parameter and never on an `expr`.
  * NOT the quotes. A survey quote's source is a PDF on `tile.loc.gov`, which this container
    cannot open (`oq/fetching-through-a-tier-the-proxy-denies`); check_openings.py verifies a
    quote against a LOCAL record and there is no local record here. A dry run says how many
    quotes it did not verify. `--live` checks that each URL still ANSWERS, nothing more, and
    returns COULD NOT EVALUATE (3) when the proxy denies the host, never a pass and never a fail.

Ratchets, in the check_grouping_rules.py shape: floors that may only rise (records, exemplars
carrying a `precedent`, records carrying a survey) and ceilings pinned at zero. Deleting a
`precedent` key from an exemplar makes every ceiling look better, which is why the floors exist.
"""
import argparse
import collections
import itertools
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRECEDENTS = os.path.join(ROOT, "precedents")
SCHEMA = os.path.join(ROOT, "schema", "precedent.schema.json")

# The runner reads exit 3 as COULD NOT EVALUATE; tests/test_counts_guard.py holds every checker
# to spelling it this way.
COULD_NOT_EVALUATE = 3

HABS_RE = re.compile(r"^[A-Z]{2}-\d{1,4}(-[A-Z0-9]{1,3})?$")  # VA-141, VA-402-A, and the 1930s district form CA-38-1 (found by Tranche 1E)
LOC_ITEM_RE = re.compile(r"^[a-z]{2}\d{4}$")               # va0433
NRHP_RE = re.compile(r"^\d{8}$")                           # 66000701
ID_SHAPES = {"habs": HABS_RE, "haer": HABS_RE, "loc-item": LOC_ITEM_RE, "nrhp": NRHP_RE, "nhl": NRHP_RE}
KIT_POINTER_RE = re.compile(r"^precedents/([a-z0-9][a-z0-9-]*)#(?:survey\.([a-z_]+)|measurements\[(\d+)\])$")

# ONE BUILDING, ONE RECORD (WP-11.3). Twelve agents researching in parallel can produce the one
# defect the per-record checks cannot see: two records for the same building under two ids. The
# partition makes it unlikely and this makes it visible. Two tests, and they are NOT the same
# strength. A shared archival id is EVIDENCE -- a HABS number, a National Register reference and a
# Library item id each name one building, so two records carrying one is an error. A shared NAME is
# a QUESTION: American house names repeat across states (this corpus holds a Mount Airy, a Mount
# Pleasant and a Mount Vernon, three different houses), so a name match is reported with both
# locations for a reader to judge and is never resolved by merging two real buildings.
UNIQUE_ID_KINDS = ("habs", "haer", "nrhp", "nhl", "loc-item")
# A NATIONAL REGISTER DISTRICT LISTING IS NOT AN IDENTITY. One district reference legitimately
# covers every contributing building in it -- Bungalow Heaven is one record and one listing over a
# whole neighbourhood -- so treating a district number as an identity would merge a district into a
# house. Only an INDIVIDUAL listing names one building.
DISTRICT_RE = re.compile(r"district|thematic|multiple[ -]property|multiple[ -]resource", re.I)
_NAME_ELIDE = re.compile(r"[\u2019']")
_NAME_NOISE = re.compile(r"\(.*?\)|[^a-z0-9 ]")


def normalised_name(name):
    """Case, punctuation, a leading article and a trailing parenthetical alias -- the four ways one
    building gets written two ways. `The Breakers` and `Breakers`; `Steuben House (Zabriskie
    House)` and `Steuben House`.

    The apostrophe is DELETED rather than spaced, and that is not a detail: spacing it makes
    `Carter's Grove` normalise to `carter s grove` and `Carters Grove` to `carters grove`, which do
    not match -- so the guard would have missed a duplicate written the commonest way an American
    house name varies, on a building this corpus already holds. Found by the test below, which is
    why the test names all four normalisations rather than trusting one."""
    n = _NAME_ELIDE.sub("", (name or "").lower())
    n = _NAME_NOISE.sub(" ", n)
    n = " ".join(n.split())
    for article in ("the ", "a "):
        if n.startswith(article):
            n = n[len(article):]
    return n


def identity_keys(rec):
    """Every archival identity a record carries. Read from `refs` AND from the survey block: a
    record may carry its HABS number in `survey.survey_no` and its Library id in `survey.item`
    without repeating either as a ref, and an identity the guard cannot see is an identity that
    cannot catch a duplicate."""
    out = set()
    for r in rec.get("refs") or []:
        kind, rid = r.get("kind"), r.get("id")
        if kind in UNIQUE_ID_KINDS and rid:
            if kind in ("nrhp", "nhl") and DISTRICT_RE.search("%s %s" % (r.get("title") or "", r.get("note") or "")):
                continue
            out.add((kind, rid))
    sv = rec.get("survey") or {}
    if sv.get("survey_no"):
        out.add(("habs", sv["survey_no"]))
    if sv.get("item"):
        out.add(("loc-item", sv["item"]))
    return out


def name_keys(rec):
    """The record's own name and every `aka`, each paired with its state -- because two houses of
    one name in two states are two houses, and the state is what says so."""
    loc = rec.get("location") or {}
    where = normalised_name(loc.get("state") or loc.get("country"))
    return {(normalised_name(n), where) for n in [rec.get("name")] + list(rec.get("aka") or []) if n}

# Measured 4 Sep 2026 on the seeded pilot (Gunston Hall, Westover, Drayton Hall) and thereafter
# may only improve. The floors are the point: a may-only-fall ceiling on dangling references is
# satisfied by deleting the references, and the floors are what stop that reading as progress.
RATCHET = {
    # Seeded 3 / 4 / 3 on 4 Sep 2026; re-pinned the same day to what Tranche 1 landed (WP-11.2).
    "precedents": 161,                  # FLOOR -- may only RISE
    "exemplars_with_precedent": 171,    # FLOOR -- may only RISE
    "precedents_with_survey": 77,       # FLOOR -- may only RISE
    "dangling_precedent": 0,
    "back_reference_disagreements": 0,
    "refs_without_locator": 0,
    "malformed_ids": 0,
    "license_keys": 0,
    "kit_pointers_unresolved": 0,
    "as_printed_not_in_quote": 0,
    # WP-11.3. Both measured 0 before Tranche 2 began, so both start clean. `duplicate_archival_id`
    # is a hard error and stays 0. `same_name_records` counts pairs a reader must look at; it is
    # ratcheted at what the corpus honestly holds, and driving it down by merging two real
    # buildings would be the corruption, not the fix.
    "duplicate_archival_id": 0,
    "same_name_records": 0,
}
FLOORS = ("precedents", "exemplars_with_precedent", "precedents_with_survey")


class Report:
    def __init__(self):
        self.errors, self.warnings, self.notes = [], [], []

    def err(self, where, msg):
        self.errors.append((where, msg))

    def warn(self, where, msg):
        self.warnings.append((where, msg))


def _exemplars():
    """node id -> its `exemplars`, through the module that WRITES asset building names, so this
    reader, check_assets.py and name_asset_buildings.py cannot drift into three answers about
    what an exemplar is."""
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import modcache
    n = modcache.load("name_asset_buildings", os.path.join(ROOT, "build", "name_asset_buildings.py"))
    return n.exemplars_by_node()


def load_records():
    out = {}
    for p in sorted(glob.glob(os.path.join(PRECEDENTS, "*.json"))):
        out[p] = json.load(open(p, encoding="utf-8"))
    return out


def _walk_keys(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield path + "/" + k, k
            yield from _walk_keys(v, path + "/" + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from _walk_keys(v, "%s[%d]" % (path, i))


def kit_pointers():
    """Every kit `source` that cites a precedent, as (kit, slot, parameter-or-None, source)."""
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, "kits", "*.kit.json"))):
        kit = json.load(open(p, encoding="utf-8"))
        base = os.path.basename(p)[: -len(".kit.json")]
        for sid, s in (kit.get("slots") or {}).items():
            for src in s.get("sources") or []:
                if isinstance(src, str) and src.startswith("precedents/"):
                    out.append((base, sid, None, src))
            for pk, pv in (s.get("parameters") or {}).items():
                if isinstance(pv, dict) and isinstance(pv.get("source"), str) and pv["source"].startswith("precedents/"):
                    out.append((base, sid, pk, pv["source"]))
    return out


def measure(records=None, exemplars=None):
    """The counts a ratchet and check_counts.py read. Pure: no printing, no exit."""
    records = load_records() if records is None else records
    exemplars = _exemplars() if exemplars is None else exemplars
    by_id = {r.get("id"): r for r in records.values()}
    m = collections.Counter()
    m["precedents"] = len(records)
    m["precedents_with_survey"] = sum(1 for r in records.values() if r.get("survey"))
    m["refs_total"] = sum(len(r.get("refs") or []) for r in records.values())
    m["survey_quotes"] = sum(len((r.get("survey") or {}).get("quotes") or []) for r in records.values())
    m["exemplars_total"] = sum(len(v) for v in exemplars.values())
    m["exemplars_with_precedent"] = sum(1 for v in exemplars.values() for e in v if e.get("precedent"))
    m["exemplars_with_standing"] = sum(1 for v in exemplars.values() for e in v if e.get("standing"))
    m["dangling_precedent"] = sum(1 for v in exemplars.values() for e in v
                                  if e.get("precedent") and e["precedent"] not in by_id)
    m["nodes_with_a_precedent"] = sum(1 for v in exemplars.values() if any(e.get("precedent") for e in v))
    return m


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--strict", action="store_true", help="warnings are errors; a broken ratchet fails")
    ap.add_argument("--live", action="store_true",
                    help="HEAD every URL on the record. Off by default; from this project's own "
                         "container the archives answer 403 and the run reports COULD NOT EVALUATE.")
    a = ap.parse_args()

    try:
        import jsonschema
    except ImportError:
        print("COULD NOT EVALUATE: jsonschema is not installed, so precedents/ was not validated "
              "against its schema. That is an unjudged state and not a pass.")
        return COULD_NOT_EVALUATE

    rep = Report()
    schema = json.load(open(SCHEMA, encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    styles = {os.path.basename(p)[:-5] for p in sorted(glob.glob(os.path.join(ROOT, "styles", "*.json")))}
    records = load_records()
    EX = _exemplars()
    counts = collections.Counter()

    by_id = {}
    for path, rec in records.items():
        fname = os.path.basename(path)[:-5]
        where = "precedent:%s" % fname
        for e in sorted(validator.iter_errors(rec), key=lambda x: list(x.path)):
            loc = "/".join(str(p) for p in e.path) or "<root>"
            rep.err(where, "schema at %s: %s" % (loc, e.message))
        if rec.get("id") != fname:
            rep.err(where, "id %r does not match filename %r" % (rec.get("id"), fname + ".json"))
        by_id[rec.get("id")] = rec

        for path_, key in _walk_keys(rec):
            if key == "license":
                counts["license_keys"] += 1
                rep.err(where, "carries a `license` at %s. A licence is a conclusion a person draws "
                               "from `rights_evidence`; the record may hold the evidence and never the "
                               "conclusion (schema/asset.schema.json says why)." % path_)

        for i, ref in enumerate(rec.get("refs") or []):
            rw = "%s.refs[%d]" % (where, i)
            if not ref.get("id") and not ref.get("url"):
                counts["refs_without_locator"] += 1
                rep.err(rw, "kind %r carries neither an id nor a url, so it locates nothing" % ref.get("kind"))
            shape = ID_SHAPES.get(ref.get("kind"))
            if shape and ref.get("id") and not shape.match(ref["id"]):
                counts["malformed_ids"] += 1
                rep.err(rw, "id %r is not the shape a %r reference has (%s)" % (ref["id"], ref["kind"], shape.pattern))
            for need in ("retrieved", "via"):
                if not ref.get(need):
                    rep.err(rw, "no `%s`: a reference nobody read on a stated day by a stated route "
                                "was typed from memory" % need)

        sv = rec.get("survey")
        if sv:
            if not LOC_ITEM_RE.match(sv.get("item", "")):
                counts["malformed_ids"] += 1
                rep.err(where + ".survey", "item %r is not a Library item id (xx0000)" % sv.get("item"))
            if sv.get("survey_no") and not HABS_RE.match(sv["survey_no"]):
                counts["malformed_ids"] += 1
                rep.err(where + ".survey", "survey_no %r is not a HABS number (XX-nnn)" % sv.get("survey_no"))
            if not str(sv.get("data_url", "")).startswith("https://tile.loc.gov/"):
                rep.warn(where + ".survey", "data_url is not on tile.loc.gov, the one host that serves "
                                            "the written data as text; say where it came from in `note`")
            counts["survey_quotes"] += len(sv.get("quotes") or [])
            nq = len(sv.get("quotes") or [])
            for j, ms in enumerate(rec.get("measurements") or []):
                if not (0 <= ms.get("from_quote", -1) < nq):
                    rep.err("%s.measurements[%d]" % (where, j),
                            "from_quote %r indexes no quote (the survey has %d)" % (ms.get("from_quote"), nq))
                    continue
                # THE AUDIT'S OWN TEST, MADE PERMANENT. `as_printed` is what was read; it must be
                # a contiguous span of the quote it names. Four Tranche 1 counts were two spans
                # joined with an ellipsis -- an inference wearing a quotation -- and this is what
                # caught them. Whitespace-normalised, because the extract's line breaks are not the
                # page's.
                q = " ".join(str(sv["quotes"][ms["from_quote"]].get("text", "")).split())
                ap = " ".join(str(ms.get("as_printed", "")).split())
                if ap and ap not in q:
                    counts["as_printed_not_in_quote"] += 1
                    rep.err("%s.measurements[%d]" % (where, j),
                            "as_printed %r is not a contiguous span of quote %d -- a figure assembled from the "
                            "prose is a reading, and belongs in `note`, not in as_printed" % (ms.get("as_printed"), ms["from_quote"]))
        elif rec.get("measurements"):
            rep.err(where, "carries measurements with no survey to index into")

        for nid in rec.get("nodes") or []:
            if nid not in styles:
                rep.err(where, "nodes[] names %r, which is not a style node" % nid)
                continue
            names = [e for e in EX.get(nid, []) if e.get("precedent") == rec.get("id")]
            if not names:
                counts["back_reference_disagreements"] += 1
                rep.err(where, "lists node %r, but no exemplar of that node carries precedent=%r -- "
                               "a citation nobody made" % (nid, rec.get("id")))
            else:
                for e in names:
                    if e.get("name") != rec.get("name"):
                        rep.err(where, "node %r names it %r; the record says %r. The exemplar name is the "
                                       "join key check_assets.py reads, so they must agree exactly"
                                       % (nid, e.get("name"), rec.get("name")))
                    loc = rec.get("location") or {}
                    accepted = [loc.get("text")] + list(loc.get("aliases") or [])
                    if e.get("location") and e["location"] not in accepted:
                        rep.err(where, "node %r locates it at %r; the record says %r (aliases %r). The location "
                                       "is half the harvest query and must agree exactly with `text` or an alias"
                                       % (nid, e["location"], loc.get("text"), loc.get("aliases") or []))

    # The other direction: an exemplar naming a record.
    for nid, exs in sorted(EX.items()):
        for e in exs:
            pid = e.get("precedent")
            if not pid:
                continue
            if pid not in by_id:
                counts["dangling_precedent"] += 1
                rep.err("style:%s" % nid, "exemplar %r names precedent %r and precedents/%s.json does not exist"
                        % (e.get("name"), pid, pid))
            elif nid not in (by_id[pid].get("nodes") or []):
                counts["back_reference_disagreements"] += 1
                rep.err("style:%s" % nid, "exemplar %r names precedent %r, whose nodes[] does not list %r"
                        % (e.get("name"), pid, nid))
            if e.get("standing") and not e.get("why"):
                rep.warn("style:%s" % nid, "exemplar %r has a standing and no `why`; a judgment with no "
                                           "reason is a number nobody said anything about" % e.get("name"))

    # Kit figures citing a survey.
    for kit, sid, pk, src in kit_pointers():
        where = "kit:%s.%s%s" % (kit, sid, ("." + pk) if pk else "")
        mt = KIT_POINTER_RE.match(src)
        if not mt:
            counts["kit_pointers_unresolved"] += 1
            rep.err(where, "source %r starts with precedents/ but is not `precedents/<id>#survey.<field>` "
                           "or `precedents/<id>#measurements[<n>]`" % src)
            continue
        pid, field, idx = mt.group(1), mt.group(2), mt.group(3)
        rec = by_id.get(pid)
        if not rec:
            counts["kit_pointers_unresolved"] += 1
            rep.err(where, "source %r names a precedent that does not exist" % src)
            continue
        if field is not None:
            fields = {q.get("field") for q in (rec.get("survey") or {}).get("quotes") or []}
            if field not in fields:
                counts["kit_pointers_unresolved"] += 1
                rep.err(where, "source %r: the survey quotes no %r field (it has %s)" % (src, field, sorted(fields)))
        else:
            n = len(rec.get("measurements") or [])
            if not (0 <= int(idx) < n):
                counts["kit_pointers_unresolved"] += 1
                rep.err(where, "source %r: the record has %d measurement(s)" % (src, n))
        counts["kit_pointers"] += 1

    # One building, one record.
    by_archival = collections.defaultdict(set)
    by_name = collections.defaultdict(set)
    keys_of, superseded = {}, {}
    for rec in records.values():
        rid = rec.get("id")
        keys_of[rid] = identity_keys(rec)
        superseded[rid] = rec.get("deprecated_in_favour_of")
        for k in keys_of[rid]:
            by_archival[k].add(rid)
        for nk in name_keys(rec):
            by_name[nk].add(rid)
    for (kind, aid), ids in sorted(by_archival.items()):
        uniq = sorted(ids)
        if len(uniq) > 1:
            counts["duplicate_archival_id"] += 1
            rep.err("precedents", "%s %s is carried by %s. An archival id names ONE building, so "
                                  "these are one record written twice -- merge them, keeping the id "
                                  "the exemplars already point at." % (kind, aid, ", ".join(uniq)))
    for (norm, where), ids in sorted(by_name.items()):
        for a, b in itertools.combinations(sorted(ids), 2):
            if superseded.get(a) == b or superseded.get(b) == a:
                continue        # a recorded supersession, which is the id rule working
            ka, kb = keys_of[a], keys_of[b]
            shared = {k for k, _ in ka} & {k for k, _ in kb}
            if any({i for k, i in ka if k == d} != {i for k, i in kb if k == d} for d in shared):
                continue        # PROVABLY different: the same kind of id, different numbers
            counts["same_name_records"] += 1
            rep.warn("precedents", "%r in %r is carried by %s and %s, and nothing on either record "
                                   "proves them different buildings. Two houses may share a name -- "
                                   "resolve a locator that separates them, or merge them."
                                   % (norm, where or "no state", a, b))

    m = measure(records, EX)
    for k in ("dangling_precedent",):
        m[k] = max(m[k], counts[k])
    for k in ("back_reference_disagreements", "refs_without_locator", "malformed_ids", "license_keys",
              "kit_pointers_unresolved", "kit_pointers", "as_printed_not_in_quote",
              "duplicate_archival_id", "same_name_records"):
        m[k] = counts[k]

    live_state = None
    if a.live:
        live_state = _live(rep, records)

    print("precedents: %d record(s), %d with a survey, %d reference(s), %d survey quote(s); "
          "%d of %d exemplars carry a `precedent` (%d nodes), %d carry a standing; %d kit figure(s) cite a survey."
          % (m["precedents"], m["precedents_with_survey"], m["refs_total"], m["survey_quotes"],
             m["exemplars_with_precedent"], m["exemplars_total"], m["nodes_with_a_precedent"],
             m["exemplars_with_standing"], m["kit_pointers"]))
    if not a.live:
        print("  %d survey quote(s) NOT VERIFIED against their source: the data pages live on "
              "tile.loc.gov and were read by an extraction tier this container cannot re-run "
              "(`retrieved`/`via` on each record say when and how). Unjudged is not passed."
              % m["survey_quotes"])

    if rep.warnings:
        print("\nWARNINGS (%d)" % len(rep.warnings))
        for w, msg in rep.warnings:
            print("  %s: %s" % (w, msg))
    if rep.errors:
        print("\nERRORS (%d)" % len(rep.errors))
        for w, msg in rep.errors:
            print("  %s: %s" % (w, msg))

    failed = []
    for key, pin in RATCHET.items():
        got = m[key]
        if key in FLOORS:
            if got < pin:
                failed.append("%s FELL: %d -> %d; the checker is holding less, which is not the corpus "
                              "agreeing more" % (key, pin, got))
        elif got > pin:
            failed.append("%s: %d -> %d" % (key, pin, got))
    if failed:
        print("\nRATCHET BROKEN — " + "; ".join(failed))

    bad = len(rep.errors) + (len(rep.warnings) if a.strict else 0) + (len(failed) if a.strict else 0)
    if live_state == COULD_NOT_EVALUATE and not bad:
        return COULD_NOT_EVALUATE
    print("\n%s  errors=%d warnings=%d" % ("FAIL" if bad else "OK", len(rep.errors), len(rep.warnings)))
    return 1 if bad else 0


def _live(rep, records):
    """HEAD every distinct URL. Deliberately NOT harvest_habs.fetch, which is shaped for the
    Library's JSON API and confines its redirects to that host; a reachability probe on an
    arbitrary archive is a different thing and should not inherit that confinement. Honours the
    proxy the environment sets. A denial at the proxy (403 on CONNECT, which urllib surfaces as
    a tunnel error) is COULD NOT EVALUATE, not a dead link."""
    import urllib.request
    import urllib.error
    contact = os.environ.get("HARVEST_CONTACT")
    if not contact:
        print("Refusing --live with no HARVEST_CONTACT set: the archives rate-limit and block by "
              "User-Agent, and this probe would name nobody. Reported as could-not-evaluate.")
        return COULD_NOT_EVALUATE
    ua = "traditional-design-language check_precedents (%s)" % contact
    urls = sorted({r.get("url") for rec in records.values() for r in rec.get("refs") or [] if r.get("url")}
                  | {(rec.get("survey") or {}).get("data_url") for rec in records.values() if rec.get("survey")})
    denied, dead = 0, 0
    for u in urls:
        req = urllib.request.Request(u, method="HEAD", headers={"User-Agent": ua})
        try:
            urllib.request.urlopen(req, timeout=20)
        except urllib.error.HTTPError as e:
            if e.code in (403, 407):
                denied += 1
            else:
                dead += 1
                rep.err("live:%s" % u, "answered %d" % e.code)
        except urllib.error.URLError as e:
            if "403" in str(e.reason) or "tunnel" in str(e.reason).lower():
                denied += 1
            else:
                dead += 1
                rep.err("live:%s" % u, "did not answer: %s" % e.reason)
    print("live: %d url(s) probed, %d denied at the proxy, %d dead" % (len(urls), denied, dead))
    if denied and not dead:
        print("COULD NOT EVALUATE reachability from this tier: the proxy denied %d of %d hosts. "
              "Run from a tier with egress (`oq/fetching-through-a-tier-the-proxy-denies`)." % (denied, len(urls)))
        return COULD_NOT_EVALUATE
    return 0


if __name__ == "__main__":
    sys.exit(main())
