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
NRHP_RE = re.compile(r"^(?:\d{8}|10\d{7})$")                  # 66000701, and the 100-series the
# Register moved to for listings since 2013 -- NPS's own Best Practices Review (April 2023) cites
# "NR Ref. 100005974" and "NR Ref. 100008758" beside legacy 88000403 and 96000614. Widened by
# Tranche 2, which found one: Richmond Heights Pioneer Historic District, listed 2019.
# WP-11.5, for Europe. HISTORIC ENGLAND'S OWN DOCUMENTATION states the shape and it was read
# rather than remembered: "Every List entry has a unique 7-figure reference number"
# (historicengland.org.uk/listing/the-list/understanding-list-entries, 5 Sep 2026), corroborated
# against fifteen sampled numbers -- 1000100, 1004281, 1046598, 1162800, 1188692, 1254925,
# 1256894, 1342941, 1357515, 1359189, 1379911, 1380478, 1401425, 1452906 -- every one 7 digits
# beginning with 1. Written from the register's own statement because the NRHP rule two commits
# ago was written from ONE remembered form and rejected a valid 2019 listing.
HE_LIST_RE = re.compile(r"^1\d{6}$")
ID_SHAPES = {"habs": HABS_RE, "haer": HABS_RE, "loc-item": LOC_ITEM_RE, "nrhp": NRHP_RE,
             "nhl": NRHP_RE, "historic-england": HE_LIST_RE}
# AND THE KINDS WITH NO SHAPE ARE NAMED RATHER THAN LEFT TO A SILENT `.get()` MISS. An id of one
# of these is carried and NOT checked, because no evidence for its format has been read here and
# inventing one is how the NRHP rule went wrong. `check_precedents.py` reports the count on every
# run so the gap is a number rather than a silence; add a shape WITH ITS EVIDENCE when a tranche
# meets the register and can read the register's own statement of it.
UNSHAPED_ID_KINDS = ("cadw", "historic-scotland", "state-register", "niah", "merimee", "bic",
                     "rijksmonument", "denkmalliste", "vincolo", "unesco")
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
#
# `record_kind` IS AUTHORITATIVE AND THE REGEX IS THE FALLBACK, and the order is the point (WP-11.4,
# ruled 5 Sep 2026). This exemption WAS the ruling encoded before the ruling existed: the corpus
# already held thirteen records that are not one building and said so only in each record's `note`,
# so the guard had to infer the class from a regex over a title. The field says it instead. The
# regex stays for a record that predates the field or forgets it -- a district a reader can see and
# the record does not declare must not silently become an identity -- and a record declaring
# `building` is NEVER exempted by the regex, because a real house called "District House" would
# otherwise lose its identity to a word in its name.
NOT_ONE_BUILDING = ("district", "type-model", "group")
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
            declared = rec.get("record_kind")
            if declared in NOT_ONE_BUILDING:
                continue                      # declared: its listing covers more than one building
            if declared is None and kind in ("nrhp", "nhl") and DISTRICT_RE.search(
                    "%s %s" % (r.get("title") or "", r.get("note") or "")):
                continue                      # undeclared: inferred from the listing's own words
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
    # Seeded 3 / 4 / 3 on 4 Sep 2026; re-pinned the same day to Tranche 1 (WP-11.2, 161/171/77) and
    # again on 5 Sep to Tranche 2 (WP-11.3), which finished North America: 86 of 164 nodes covered.
    "precedents": 415,                  # FLOOR -- may only RISE
    "exemplars_with_precedent": 505,    # FLOOR -- may only RISE
    "precedents_with_survey": 155,      # FLOOR -- may only RISE
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
    # WP-11.4, Ruling D. A stated refusal and an unresearched row are counted apart now.
    "no_precedent_beside_a_precedent": 0,
    # WP-11.4, Ruling A. A `measured` figure citing a precedent must cite a MEASUREMENT, and the
    # two numbers must agree. Both at 0 and both hard: a source that contradicts its own figure
    # reads as provenance and is worse than none.
    "measured_cites_a_paragraph": 0,
    "source_contradicts": 0,
    "source_uncomparable": 0,
    # A FLOOR, and it is the half that stops the other three being satisfied by deleting sources.
    # Every ceiling above reads better when a citation is removed; this one reads worse.
    "source_agrees": 6,
    # WP-11.5. A CEILING, and naming the gap turned it into a number on its first run: 58 ids --
    # every one a `state-register` from the American tranches -- were being carried unchecked and
    # nobody knew, because ID_SHAPES.get() misses silently. It may only fall, which happens by
    # adding a shape backed by the register's own statement of its format.
    "ids_with_no_shape_rule": 58,
    "exemplars_unresearched": 185,      # a CEILING -- may only fall, as tranches resolve them.
                                        # Pinned TIGHT at the measured value: 693 exemplars, 505
                                        # resolved, 3 stated refusals, 185 gaps. Pinning it at 188
                                        # -- the count before the refusals were stated -- would have
                                        # left the ceiling slack by exactly the three rows the field
                                        # was built to separate, which is the meter measuring nothing.
}
FLOORS = ("precedents", "exemplars_with_precedent", "precedents_with_survey",
          # WP-11.4 Ruling A. A FLOOR, and it is the half that stops the three ceilings
          # beside it being satisfied by DELETING citations: every one of those reads
          # better when a source is removed, and this one reads worse.
          "source_agrees")


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
    """Every kit `source` that cites a precedent, as (kit, slot, parameter-or-None, source,
    parameter-object-or-None). The parameter object is carried so `kit_source_agrees` can hold its
    number against the measurement's; a pointer that resolves is not a pointer that agrees."""
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, "kits", "*.kit.json"))):
        kit = json.load(open(p, encoding="utf-8"))
        base = os.path.basename(p)[: -len(".kit.json")]
        for sid, s in (kit.get("slots") or {}).items():
            for src in s.get("sources") or []:
                if isinstance(src, str) and src.startswith("precedents/"):
                    out.append((base, sid, None, src, None))
            for pk, pv in (s.get("parameters") or {}).items():
                if isinstance(pv, dict) and isinstance(pv.get("source"), str) and pv["source"].startswith("precedents/"):
                    out.append((base, sid, pk, pv["source"], pv))
    return out


def kit_source_agrees(param, meas):
    """Hold a kit parameter's number against the measurement it cites. Three verdicts, never a
    bool: ("agrees", why) / ("contradicts", why) / (None, why-it-could-not-be-compared).

    WP-11.4, Ruling A. The ruling's own entry says *"a source pointer that resolves is not a source
    that agrees ... that comparison is a reader's"*. It need not be. A `measurements[]` entry carries
    a typed `value` and a `unit` from a closed enum that matches the kit's own units, so the two
    numbers can be held together mechanically -- which is the whole reason a `measured` parameter
    must cite a MEASUREMENT and not a free `survey.<field>`. A number cites a number.

    Could-not-compare is a first-class answer and is never read as agreement: a categorical
    parameter (`value: "gable-end-exterior"`), a measurement nobody parsed a `value` from, and a
    unit mismatch are all genuinely unjudged. Unjudged is not passed.
    """
    mv, mu = meas.get("value"), meas.get("unit")
    if mv is None:
        return None, "the measurement carries no parsed `value` -- only `as_printed` %r" % meas.get("as_printed")
    pu = param.get("unit")
    if pu and mu and pu != mu:
        return None, "the parameter is in %s and the measurement in %s; nothing here converts between them" % (pu, mu)
    lo = hi = None
    if isinstance(param.get("range"), list) and len(param["range"]) == 2:
        lo, hi = param["range"]
    elif isinstance(param.get("value"), (int, float)) and not isinstance(param.get("value"), bool):
        lo = hi = param["value"]
    else:
        return None, "the parameter states no number to compare (value %r)" % (param.get("value"),)
    if lo <= mv <= hi:
        return "agrees", "%s %s is within the parameter's %s" % (mv, mu or "", [lo, hi])
    return "contradicts", ("%s %s is outside the parameter's %s -- the cited building does not "
                           "state what the parameter claims" % (mv, mu or "", [lo, hi]))


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
    # A separate dict, NOT a key of `counts`: `counts` is a Counter, so `counts["refusal_reasons"]`
    # is the integer 0 and `+= 1` on a reason would be a TypeError at the first refusal.
    refusal_reasons = collections.Counter()

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
            if ref.get("kind") in UNSHAPED_ID_KINDS and ref.get("id"):
                counts["ids_with_no_shape_rule"] += 1
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

    # WP-11.4, Ruling D. A STATED REFUSAL IS NOT AN UNRESEARCHED ROW, and until this field existed
    # one number carried both -- after Tranche 3 it would have read ~191 whether that was 191 gaps
    # or 188 gaps and 3 decisions. `no_precedent` says which, in a closed vocabulary, and the two
    # are metered apart below. A `why` is prose and no counter can read it.
    for nid, exs in sorted(EX.items()):
        for e in exs:
            reason = e.get("no_precedent")
            if e.get("precedent"):
                if reason:
                    counts["no_precedent_beside_a_precedent"] += 1
                    rep.err("style:%s" % nid, "exemplar %r carries BOTH precedent=%r and no_precedent=%r; "
                            "the field says why there is no record, so beside a record it is a "
                            "contradiction" % (e.get("name"), e["precedent"], reason))
                continue
            if reason and reason != "not-yet-researched":
                counts["stated_refusals"] += 1
                refusal_reasons[reason] += 1
                if not e.get("why"):
                    rep.warn("style:%s" % nid, "exemplar %r refuses a precedent (%s) and says no `why`; "
                             "a refusal without its reason reads to the next author as a gap"
                             % (e.get("name"), reason))
            else:
                counts["exemplars_unresearched"] += 1

    # Kit figures citing a survey.
    for kit, sid, pk, src, param in kit_pointers():
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
            # WP-11.4, Ruling A. A NUMBER CITES A NUMBER. The `#survey.<field>` form points at a
            # quote and nothing can hold a figure against a paragraph, so it may support a
            # CATEGORICAL call and never a `measured` one. This is the mechanical half of the
            # ruling's own caution that a pointer which resolves is not a pointer that agrees.
            elif param is not None and param.get("kind") == "measured":
                counts["measured_cites_a_paragraph"] += 1
                rep.err(where, "is `kind: measured` and cites %r, a survey FIELD. A quote cannot be "
                               "held against a figure, so a measured parameter must cite a "
                               "measurement -- `precedents/%s#measurements[<n>]` -- whose `value` "
                               "and `unit` this checker compares with the parameter's. Cite the "
                               "measurement, or the parameter is a categorical call and is not "
                               "`measured`." % (src, pid))
        else:
            n = len(rec.get("measurements") or [])
            if not (0 <= int(idx) < n):
                counts["kit_pointers_unresolved"] += 1
                rep.err(where, "source %r: the record has %d measurement(s)" % (src, n))
            elif param is not None:
                verdict, why = kit_source_agrees(param, rec["measurements"][int(idx)])
                if verdict == "contradicts":
                    counts["source_contradicts"] += 1
                    rep.err(where, "cites %r and DISAGREES with it: %s. A source that contradicts "
                                   "the figure it is cited for is worse than no source, because it "
                                   "reads as provenance." % (src, why))
                elif verdict is None:
                    counts["source_uncomparable"] += 1
                    rep.warn(where, "cites %r and the two CANNOT BE COMPARED: %s. Not an "
                                    "agreement -- unjudged is not passed." % (src, why))
                else:
                    counts["source_agrees"] += 1
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
    for (nkey, nstate), ids in sorted(by_name.items()):
        for ra, rb in itertools.combinations(sorted(ids), 2):
            if superseded.get(ra) == rb or superseded.get(rb) == ra:
                continue        # a recorded supersession, which is the id rule working
            ka, kb = keys_of[ra], keys_of[rb]
            shared = {k for k, _ in ka} & {k for k, _ in kb}
            if any({i for k, i in ka if k == d} != {i for k, i in kb if k == d} for d in shared):
                continue        # PROVABLY different: the same kind of id, different numbers
            counts["same_name_records"] += 1
            rep.warn("precedents", "%r in %r is carried by %s and %s, and nothing on either record "
                                   "proves them different buildings. Two houses may share a name -- "
                                   "resolve a locator that separates them, or merge them."
                                   % (nkey, nstate or "no state", ra, rb))

    m = measure(records, EX)
    for k in ("dangling_precedent",):
        m[k] = max(m[k], counts[k])
    for k in ("back_reference_disagreements", "refs_without_locator", "malformed_ids", "license_keys",
              "kit_pointers_unresolved", "kit_pointers", "as_printed_not_in_quote",
              "duplicate_archival_id", "same_name_records",
              # WP-11.4. Ruling D's two, then Ruling A's four.
              "no_precedent_beside_a_precedent", "exemplars_unresearched",
              "measured_cites_a_paragraph", "source_contradicts", "source_uncomparable",
              "source_agrees", "ids_with_no_shape_rule"):
        m[k] = counts[k]

    live_state = None
    if a.live:
        live_state = _live(rep, records)

    print("precedents: %d record(s), %d with a survey, %d reference(s), %d survey quote(s); "
          "%d of %d exemplars carry a `precedent` (%d nodes), %d carry a standing; %d kit figure(s) cite a survey."
          % (m["precedents"], m["precedents_with_survey"], m["refs_total"], m["survey_quotes"],
             m["exemplars_with_precedent"], m["exemplars_total"], m["nodes_with_a_precedent"],
             m["exemplars_with_standing"], m["kit_pointers"]))
    # WP-11.4, Ruling D. PRINTED ON EVERY RUN, not only when a ratchet breaks: the whole point of
    # the field is that a stated refusal and an unresearched row stop being one number, and a
    # distinction nobody can see is a distinction nobody will keep.
    if counts["ids_with_no_shape_rule"]:
        print("  %d archival id(s) carry a kind with NO SHAPE RULE (%s) -- carried, not checked. "
              "Not a pass: add a shape with the register's own statement of its format when a "
              "tranche meets it." % (counts["ids_with_no_shape_rule"], ", ".join(UNSHAPED_ID_KINDS)))
    print("  of the %d exemplars with no `precedent`: %d are a STATED REFUSAL (%s) and %d are "
          "NOT YET RESEARCHED. A refusal is a decision and a gap is work; they are not the same "
          "number." % (counts["stated_refusals"] + counts["exemplars_unresearched"],
                       counts["stated_refusals"],
                       ", ".join("%s %d" % kv for kv in sorted(refusal_reasons.items()))
                       or "none",
                       counts["exemplars_unresearched"]))

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
