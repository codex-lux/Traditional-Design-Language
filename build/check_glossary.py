#!/usr/bin/env python3
"""check_glossary.py — the glossary records against their contract (WP-14.1).

Every word the workbench shows a reader is defined by a record in glossary/, and the app writes
no definition of its own. That makes this file the only thing standing between a tooltip and an
invented source: a definition is either SOURCED, from a work the corpus already cites, or
EDITORIAL, quoting the file it was read from -- and a quotation nobody can find is a guess
wearing a citation, which is the one thing this corpus must never ship.

The contract is docs/prd/phase-14-the-dossier-and-the-journey.md §A. The rules, in its order:

   1. COULD NOT EVALUATE (exit 3) -- jsonschema is absent, the server's citation validator
      cannot be imported, or the schema cannot be compiled. Never a pass.
   2. SHAPE -- every glossary/*.json validates (build/schema_validators.py, compiled once);
      the filename is the id; ids are unique; a directory with no record is an error. A key
      stated twice in one file is an error too, because json.load keeps the last and says
      nothing (tests/test_duplicate_json_keys.py's finding, met here before it can happen).
   3. SOURCED -- every `sources` string equals, character for character, an item of a
      `sources` list in a record under styles/, faults/, rooms/, proportions/, groupings/ or
      partis/. precedents/ carries archival `refs` and no `sources` key, and is not a
      bibliography; kits/ carries slot-level `sources` that are provenance notes ("Authored,
      not retrieved"), not works, and is not one either.
   4. EDITORIAL -- check_openings.check_basis, CALLED and not copied, with the glossary's own
      pattern of admissible files (check_openings.GLOSSARY_REC_RE), must pass and must report
      at least one verified quotation of twenty-five characters or more. A basis naming the
      generated docs/open-questions.md or any glossary/ file is an error, and a key path the
      verifier cannot walk is an ERROR here rather than an unjudged count: the glossary starts
      with no backlog, so its ceiling is zero.
   5. BINDS -- the fields in FIELDS (the glossary's own `glossary.family` among them since
      WP-14.17), their schemas and pointers checked against the
      schema files as they stand; the value in the enum; the record's family, id and order
      derived from the row; each value bound once; and a field bound at all is bound
      COMPLETELY, every missing value an error.
   6. HOMONYMS -- a term or aka that collides case-insensitively with another record's needs a
      `sense` on both and each naming the other in `confusable_with`, which is symmetric
      everywhere, names only records that exist, and never names its own record.
   7. CITES -- every `see` item and `surface.try` is parsed with the server's own REF_RE (no
      fourth spelling of the grammar): `term:` against this set, `brief:` against briefs/,
      every other kind through the server's own `citations.validate`.
   8. HYGIENE -- no work-package or open-question number, no command-line flag, no snake_case
      identifier and no numeral of any script in the prose a reader sees.
   9. REQUIRED RECORDS -- about-tdl and the four judgment states exist with distinct terms;
      `readers` and `is_not` only on about-tdl, which carries no see, confusable_with, binds or
      surface (it is served to a signed-out visitor and must resolve no other record);
      `surface` only in families surface and section.
  10. LENGTHS -- definition and each readers line at most forty-five words; analogy, the page
      head, each how-to-read line and each is_not at most thirty.
  11. NAMING -- families surface, section, nav-group, layer, judgment, glossary-field, mark and
      family take the id prefix `<family>-`, and an id carrying one of those prefixes is in that
      family.
  12. ASK (0.2.0, WP-14.17) -- every record in family `surface` carries `surface.ask`, the
      assistant's starter questions for that page: one to three, each at most twenty words and
      ending with a question mark, under rule 8's hygiene. A dossier section may carry them.
  13. MARKS (0.2.0, WP-14.17) -- `mark` appears only on families judgment, mark, severity and
      variant-status; each value names a custom property workbench/app/src/theme/tokens.css
      DEFINES (read as text, a declaration and not a use), and each property is named by exactly
      one record. The stylesheet is the only file outside the corpus directories this checker
      reads. Where a record carries a `mark` and the stylesheet cannot be read, the rule is
      COULD NOT EVALUATE, and the run exits 3 unless another rule has already failed it.

Usage:
    python3 build/check_glossary.py                         # the repository's glossary/
    python3 build/check_glossary.py --glossary DIR [...]    # these directories, as ONE set
    python3 build/check_glossary.py --quiet                 # errors and the verdict only
    python3 build/check_glossary.py --tokens FILE           # hold `mark` to this stylesheet

`--glossary` may be repeated; every directory named is read and the union is checked as one set
(an id in two directories is a duplicate). It replaces the default rather than adding to it, so
a batch authored outside this tree is checked on top of the seeds by naming both directories.
The corpus a basis quotes, the bibliography, the schemas and briefs/ are always this repository's.

Exit: 0 pass · 1 any error · 3 COULD NOT EVALUATE.
"""
import argparse
import glob
import json
import os
import re
import sys
import unicodedata
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLOSSARY = os.path.join(ROOT, "glossary")
SCHEMA = os.path.join(ROOT, "schema", "glossary-term.schema.json")
BRIEFS = os.path.join(ROOT, "briefs")
# Rule 13: the one stylesheet a `mark` is held to. `--tokens` points the check at another file,
# which is how tests/test_check_glossary.py drives the rule without writing inside the repository.
TOKENS = os.path.join(ROOT, "workbench", "app", "src", "theme", "tokens.css")

# The runner's protocol (build/check_all.py): 3 is COULD NOT EVALUATE, never a pass.
COULD_NOT_EVALUATE = 3

sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache                                                        # noqa: E402
# The basis verifier and the one spelling of which files a glossary basis may name. CALLED, never
# copied: the corpus has been bitten three times by one rule spelled twice.
CO = modcache.load("check_openings", os.path.join(ROOT, "build", "check_openings.py"))

# Where a `sources` string must already be (rule 3). Top-level `sources` lists of strings, the
# only kind these directories carry.
BIBLIOGRAPHY_GLOBS = ("styles/*.json", "faults/*.json", "rooms/*.json",
                      "proportions/**/*.json", "groupings/*.json", "partis/*.json")

# The bindable fields (rule 5): field -> (schema file, JSON pointer to the enum, family).
# workbench/app/src/glossary/fields.js holds the same keys; tranche 1's §A.4 and tranche 2's §A.1
# are the table both are read from, and `src/lookup.test.mjs` holds the two copies row for row.
# Each row is verified against the schema file on every run, so a pointer that stops resolving is
# an error here rather than a word bound to nothing. The eighth row, `glossary.family` (0.2.0,
# WP-14.17), binds the glossary's own family enum: one `family-*` record per family, whose term is
# the heading the Glossary page groups that family under.
FIELDS = {
    "style.rank": ("schema/style-node.schema.json", "/properties/rank", "rank"),
    "lineage.type": ("schema/style-node.schema.json",
                     "/properties/lineage/items/properties/type", "edge"),
    "kit.binding": ("schema/kit.schema.json",
                    "/properties/slots/additionalProperties/properties/binding", "binding"),
    "kit.variant_status": ("schema/kit.schema.json",
                           "/properties/slots/additionalProperties/properties/variants/items"
                           "/properties/status", "variant-status"),
    "kit.parameter_kind": ("schema/kit.schema.json", "/$defs/parameter/properties/kind",
                           "param-kind"),
    "pack.kind": ("schema/proportion-pack.schema.json", "/properties/kind", "pack-kind"),
    "fault.severity": ("schema/fault.schema.json", "/properties/severity", "severity"),
    "glossary.family": ("schema/glossary-term.schema.json", "/properties/family", "family"),
}

# Rule 9: the five seeds WP-14.1 writes and every other record may lean on.
REQUIRED = ("about-tdl", "judgment-passed", "judgment-failed", "judgment-unjudged",
            "judgment-not-applicable")
ABOUT = "about-tdl"
ABOUT_ONLY = ("readers", "is_not")
ABOUT_FORBIDS = ("see", "confusable_with", "binds", "surface")
SURFACE_FAMILIES = ("surface", "section")

# Rule 11.
PREFIXED_FAMILIES = ("surface", "section", "nav-group", "layer", "judgment",
                     "glossary-field", "mark", "family")

# Rule 12: the starter questions.
ASK_REQUIRED_FAMILY = "surface"
ASK_MIN, ASK_MAX = 1, 3
MAX_WORDS_ASK = 20

# Rule 13: the families a `mark` may sit on, and the shape of a mark's value.
MARK_FAMILIES = ("judgment", "mark", "severity", "variant-status")
_MARK_RE = re.compile(r"^--mark-[a-z0-9-]+$")
# A custom property DECLARED, not used: the name at the start of a declaration -- after `{`, `;`
# or a line start -- followed by a colon. `var(--mark-x)` is a use and defines nothing.
_DECLARED_RE = re.compile(r"(?:^|[{;])\s*(--[A-Za-z0-9_-]+)\s*:", re.M)

# Rule 8. A numeral is caught by its Unicode category rather than by `\d` alone, so a circled
# figure or a fraction -- the build-history shapes the workbench's own copy carried -- cannot pass
# as prose.
HYGIENE = (
    (re.compile(r"WP-\d"), "a work-package number"),
    (re.compile(r"\bOQ\s*\d"), "an open-question number"),
    (re.compile(r"(^|\s)--[a-z]"), "a command-line flag"),
    (re.compile(r"\b[a-z0-9]+_[a-z0-9_]+\b"), "a snake_case identifier"),
)
NUMERAL_CATEGORIES = ("Nd", "No", "Nl")

# Rule 10: (maximum words) for each prose field that has one.
MAX_WORDS_DEFINITION = 45
MAX_WORDS_SHORT = 30
MAX_WORDS_READER = 45
MIN_QUOTE = 25          # the length check_openings._QUOTE_RE sees; restated only in messages

# Rule 4: a glossary/ file named in a basis, which no definition may rest on.
_GLOSSARY_PATH_RE = re.compile(r"(?<![A-Za-z0-9_./-])glossary/[A-Za-z0-9_.\-/]*")
_GENERATED_INDEX = "docs/open-questions.md"


class Report:
    """The interface check_openings.check_basis writes to. An unjudged key path is an ERROR in
    this checker: the glossary starts with no backlog, so the ceiling on unjudged citations is
    zero and there is nothing for a count to ratchet."""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def err(self, where, msg):
        self.errors.append(f"{where}: {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"{where}: {msg}")

    def unjudged(self, where, msg):
        self.errors.append(f"{where}: {msg} -- a glossary basis may not cite what cannot be "
                           f"checked; cite a walkable key or the file alone")


# ------------------------------------------------------------------------------ helpers

def _str(x):
    return x if isinstance(x, str) else None


def _list(x):
    return x if isinstance(x, list) else []


def _strs(x):
    return [s for s in _list(x) if isinstance(s, str)]


def _norm(s):
    """How two strings are compared for a homonym: case-insensitively, trimmed."""
    return s.strip().casefold()


def _pointer(doc, pointer):
    """A JSON pointer over a parsed document, or None where it does not resolve."""
    cur = doc
    for tok in pointer.lstrip("/").split("/"):
        tok = tok.replace("~1", "/").replace("~0", "~")
        if isinstance(cur, dict) and tok in cur:
            cur = cur[tok]
        elif isinstance(cur, list) and tok.isdigit() and int(tok) < len(cur):
            cur = cur[int(tok)]
        else:
            return None
    return cur


def _load_json_no_duplicates(path):
    """Parse a file, refusing a key stated twice in one object. Returns (record, duplicates)."""
    dups = []

    def hook(pairs):
        seen = Counter(k for k, _ in pairs)
        dups.extend(k for k, n in seen.items() if n > 1)
        return dict(pairs)

    with open(path, encoding="utf-8") as fh:
        rec = json.load(fh, object_pairs_hook=hook)
    return rec, dups


def bibliography():
    """Every string in a `sources` list under the six bibliography directories."""
    out = set()
    for pattern in BIBLIOGRAPHY_GLOBS:
        for path in sorted(glob.glob(os.path.join(ROOT, pattern), recursive=True)):
            try:
                with open(path, encoding="utf-8") as fh:
                    rec = json.load(fh)
            except (OSError, ValueError):
                continue
            if isinstance(rec, dict):
                out.update(_strs(rec.get("sources")))
    return out


def prose_fields(rec):
    """(field label, text) for every string rule 8 reads."""
    out = []
    for key in ("term", "sense", "definition", "analogy", "more"):
        if _str(rec.get(key)) is not None:
            out.append((key, rec[key]))
    for i, s in enumerate(_strs(rec.get("aka"))):
        out.append((f"aka[{i}]", s))
    surf = rec.get("surface") if isinstance(rec.get("surface"), dict) else {}
    if _str(surf.get("what")) is not None:
        out.append(("surface.what", surf["what"]))
    for i, s in enumerate(_strs(surf.get("read"))):
        out.append((f"surface.read[{i}]", s))
    for i, s in enumerate(_strs(surf.get("ask"))):
        out.append((f"surface.ask[{i}]", s))
    for i, r in enumerate(_list(rec.get("readers"))):
        if isinstance(r, dict):
            for k in ("who", "line"):
                if _str(r.get(k)) is not None:
                    out.append((f"readers[{i}].{k}", r[k]))
    for i, s in enumerate(_strs(rec.get("is_not"))):
        out.append((f"is_not[{i}]", s))
    return out


def _words(s):
    return len(s.split())


def declared_properties(css):
    """Every custom property a stylesheet DECLARES, read as text with its comments removed."""
    live = re.sub(r"/\*[\s\S]*?\*/", " ", css)
    return set(_DECLARED_RE.findall(live))


# ------------------------------------------------------------------------------ the check

def could_not_evaluate(reason):
    print(f"COULD NOT EVALUATE — check_glossary: {reason}. Unjudged is not passed.")
    return COULD_NOT_EVALUATE


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check the glossary records against their contract.")
    ap.add_argument("--glossary", action="append", metavar="DIR",
                    help="a directory of glossary records; repeat to check several as one set "
                         "(default: this repository's glossary/)")
    ap.add_argument("--quiet", action="store_true", help="print errors and the verdict only")
    ap.add_argument("--tokens", metavar="FILE",
                    help="the stylesheet a record's `mark` is held to (default: the workbench's "
                         "workbench/app/src/theme/tokens.css)")
    args = ap.parse_args(argv)
    dirs = [os.path.abspath(d) for d in (args.glossary or [GLOSSARY])]

    # 1 -- could not evaluate, and say why
    try:
        import jsonschema  # noqa: F401
    except ImportError:
        return could_not_evaluate("jsonschema is not installed, so no record's shape can be judged")
    try:
        import schema_validators
        validator = schema_validators.compiled(SCHEMA)
    except Exception as exc:                                   # noqa: BLE001
        return could_not_evaluate(f"schema/glossary-term.schema.json cannot be compiled "
                                  f"({type(exc).__name__}: {exc})")
    try:
        if ROOT not in sys.path:
            sys.path.insert(0, ROOT)
        import workbench.server.citations as CIT
    except Exception as exc:                                   # noqa: BLE001
        return could_not_evaluate(f"workbench.server.citations cannot be imported "
                                  f"({type(exc).__name__}: {exc}), so no citation can be checked")
    from jsonschema.exceptions import ValidationError

    rep = Report()
    unjudged = []                   # rules that could not be evaluated, each with its reason

    # 2 -- shape
    records = {}                    # id -> record (the last one read, where ids collide)
    where_of = {}                   # id -> the file it came from, for messages
    n_files = 0
    for d in dirs:
        label = os.path.relpath(d, ROOT) if d.startswith(ROOT + os.sep) or d == ROOT else d
        if not os.path.isdir(d):
            rep.err(label, "no such directory -- an absent glossary is an error, not an empty pass")
            continue
        names = sorted(f for f in os.listdir(d) if f.endswith(".json"))
        if not names:
            rep.err(label, "holds no record -- an empty glossary is an error, not an empty pass")
            continue
        for name in names:
            n_files += 1
            path = os.path.join(d, name)
            shown = f"{label}/{name}"
            try:
                rec, dups = _load_json_no_duplicates(path)
            except (OSError, ValueError) as exc:
                rep.err(shown, f"not valid JSON: {exc}")
                continue
            for k in sorted(set(dups)):
                rep.err(shown, f"states the key {k!r} twice in one object; json.load keeps the "
                               f"last and says nothing, so the file says one thing and means another")
            if not isinstance(rec, dict):
                rep.err(shown, "is not a JSON object")
                continue
            try:
                schema_validators.raise_first(validator, rec)
            except ValidationError as exc:
                loc = "/".join(str(p) for p in exc.absolute_path) or "(root)"
                rep.err(shown, f"schema at {loc}: {exc.message}")
            rid = rec.get("id")
            if not isinstance(rid, str) or not rid:
                rep.err(shown, "has no string id")
                continue
            if name != rid + ".json":
                rep.err(shown, f"filename does not match its id {rid!r} (it must be {rid}.json)")
            if rid in records:
                rep.err(shown, f"duplicate id {rid!r}, also in {where_of[rid]}")
            records[rid] = rec
            where_of[rid] = shown

    ids = set(records)

    def at(rid):
        return f"glossary/{rid}.json"

    # 3 -- sourced
    bib = None
    n_sources = 0
    for rid, rec in sorted(records.items()):
        if rec.get("kind") != "sourced":
            continue
        if bib is None:
            bib = bibliography()
            bib_folded = {re.sub(r"\s+", " ", s).strip().casefold(): s for s in bib}
        for s in _strs(rec.get("sources")):
            n_sources += 1
            if s in bib:
                continue
            near = bib_folded.get(re.sub(r"\s+", " ", s).strip().casefold())
            hint = (f" -- the bibliography has {near!r}, which differs only in case or spacing"
                    if near else "")
            rep.err(at(rid), f"source {s!r} is in no `sources` list under styles/, faults/, "
                             f"rooms/, proportions/, groupings/ or partis/. The glossary never "
                             f"introduces a source the corpus does not already cite{hint}")

    # 4 -- editorial
    n_quotes = 0
    for rid, rec in sorted(records.items()):
        if rec.get("kind") != "editorial":
            continue
        basis = _str(rec.get("basis"))
        if basis is None:
            continue                                   # the schema has already said so
        named = CO.GLOSSARY_REC_RE.findall(basis)
        if _GENERATED_INDEX in named:
            rep.err(at(rid), f"basis names {_GENERATED_INDEX}, which is GENERATED -- quote the "
                             f"question's own file, which a glossary basis may not name either")
        for m in _GLOSSARY_PATH_RE.findall(basis):
            rep.err(at(rid), f"basis names {m}: a definition may not rest on another definition")
        verified = CO.check_basis(rep, rec, source=at(rid), rec_re=CO.GLOSSARY_REC_RE)
        n_quotes += verified
        if not verified:
            rep.err(at(rid), f"basis verified no quotation of {MIN_QUOTE} characters or more. It "
                             f"must name the file it read and quote it verbatim in double quotes: "
                             f"a shorter quotation is not checked at all, so it proves nothing")

    # 5 -- binds
    schema_docs = {}
    enums = {}
    for field, (schema, pointer, _fam) in FIELDS.items():
        doc = schema_docs.get(schema)
        if doc is None:
            try:
                with open(os.path.join(ROOT, schema), encoding="utf-8") as fh:
                    doc = schema_docs[schema] = json.load(fh)
            except (OSError, ValueError) as exc:
                rep.err(f"FIELDS[{field}]", f"{schema} cannot be read: {exc}")
                continue
        node = _pointer(doc, pointer)
        enum = node.get("enum") if isinstance(node, dict) else None
        if not isinstance(enum, list) or not enum:
            rep.err(f"FIELDS[{field}]", f"{schema} {pointer} does not reach an enum -- the schema "
                                        f"moved and this table did not")
            continue
        enums[field] = enum
    bound = {}                                           # (field, value) -> [ids]
    for rid, rec in sorted(records.items()):
        for b in _list(rec.get("binds")):
            if not isinstance(b, dict):
                continue
            field, value = b.get("field"), b.get("value")
            if field not in FIELDS:
                rep.err(at(rid), f"binds field {field!r}, which is not one of {sorted(FIELDS)}")
                continue
            schema, pointer, fam = FIELDS[field]
            if b.get("schema") != schema or b.get("pointer") != pointer:
                rep.err(at(rid), f"binds {field} at {b.get('schema')} {b.get('pointer')}; the "
                                 f"field lives at {schema} {pointer}")
            enum = enums.get(field)
            if enum is None:
                continue
            if value not in enum:
                rep.err(at(rid), f"binds {field} = {value!r}, which is not in its enum {enum}")
                continue
            bound.setdefault((field, value), []).append(rid)
            if rec.get("family") != fam:
                rep.err(at(rid), f"binds {field} and is in family {rec.get('family')!r}; a record "
                                 f"binding that field is in family {fam!r}")
            want = f"{fam}-{str(value).replace('_', '-')}"
            if rid != want:
                rep.err(at(rid), f"binds {field} = {value!r} and must be named {want!r}")
            if rec.get("order") != enum.index(value):
                rep.err(at(rid), f"binds {field} = {value!r}, whose index in the enum is "
                                 f"{enum.index(value)}; its `order` is {rec.get('order')!r}")
    for (field, value), who in sorted(bound.items()):
        if len(who) > 1:
            rep.err(f"binds {field} = {value!r}", f"bound by {len(who)} records: {who}. One word "
                                                  f"per value, one value per word")
    fields_bound = sorted({f for f, _v in bound})
    for field in fields_bound:
        for value in enums.get(field) or []:
            if (field, value) not in bound:
                want = f"{FIELDS[field][2]}-{value.replace('_', '-')}"
                rep.err(f"binds {field}", f"{value!r} is bound by no record, while other values "
                                          f"of the field are -- a half-bound field defines some "
                                          f"of a reader's options and leaves the rest bare "
                                          f"(expected {want}.json)")

    # 6 -- homonyms
    by_string = {}
    for rid, rec in records.items():
        for s in [_str(rec.get("term"))] + _strs(rec.get("aka")):
            if s:
                by_string.setdefault(_norm(s), set()).add(rid)
    collisions = 0
    pairs_seen = set()
    for s, who in sorted(by_string.items()):
        if len(who) < 2:
            continue
        who = sorted(who)
        for i, a in enumerate(who):
            for b in who[i + 1:]:
                if (a, b) in pairs_seen:
                    continue
                pairs_seen.add((a, b))
                collisions += 1
                for x, y in ((a, b), (b, a)):
                    if not _str(records[x].get("sense")):
                        rep.err(at(x), f"collides with {y} on {s!r} and states no `sense` -- "
                                       f"both records of a homonym must say which sense they are")
                    if y not in _strs(records[x].get("confusable_with")):
                        rep.err(at(x), f"collides with {y} on {s!r} and does not name it in "
                                       f"`confusable_with`")
    for rid, rec in sorted(records.items()):
        for other in _strs(rec.get("confusable_with")):
            if other == rid:
                rep.err(at(rid), "names itself in `confusable_with`")
            elif other not in records:
                rep.err(at(rid), f"`confusable_with` names {other!r}, which is not a record")
            elif rid not in _strs(records[other].get("confusable_with")):
                rep.err(at(rid), f"names {other} in `confusable_with` and {other} does not name "
                                 f"it back -- the relation is symmetric or it is wrong")

    # 7 -- cites
    n_cites = 0
    for rid, rec in sorted(records.items()):
        cites = [("see", c) for c in _strs(rec.get("see"))]
        surf = rec.get("surface") if isinstance(rec.get("surface"), dict) else {}
        if _str(surf.get("try")) is not None:
            cites.append(("surface.try", surf["try"]))
        for field, cite in cites:
            n_cites += 1
            m = CIT.REF_RE.match(cite)
            if not m:
                rep.err(at(rid), f"{field} {cite!r} is not a citation in the grammar (kind:id)")
                continue
            kind, ident, frag = m.groups()
            if kind == "term":
                if frag:
                    rep.err(at(rid), f"{field} {cite!r}: a term citation carries no fragment")
                elif ident not in ids:
                    rep.err(at(rid), f"{field} {cite!r} names no record in this glossary")
            elif kind == "brief":
                if frag:
                    rep.err(at(rid), f"{field} {cite!r}: a brief citation carries no fragment")
                elif not os.path.isfile(os.path.join(BRIEFS, ident + ".json")):
                    rep.err(at(rid), f"{field} {cite!r} names no file briefs/{ident}.json")
            else:
                ok, reason = CIT.validate(cite)
                if not ok:
                    rep.err(at(rid), f"{field} {cite!r} does not resolve: {reason}")

    # 8 -- hygiene, and 10 -- lengths
    for rid, rec in sorted(records.items()):
        for label, text in prose_fields(rec):
            for rx, what in HYGIENE:
                hit = rx.search(text)
                if hit:
                    rep.err(at(rid), f"{label} carries {what} ({hit.group(0).strip()!r}): the "
                                     f"prose a reader sees states no build history, flag or "
                                     f"identifier")
            num = next((ch for ch in text if unicodedata.category(ch) in NUMERAL_CATEGORIES), None)
            if num is not None:
                rep.err(at(rid), f"{label} carries the numeral {num!r}: no digits, no counts -- "
                                 f"a definition must still be true when every number has changed")
        limits = [("definition", _str(rec.get("definition")), MAX_WORDS_DEFINITION),
                  ("analogy", _str(rec.get("analogy")), MAX_WORDS_SHORT)]
        surf = rec.get("surface") if isinstance(rec.get("surface"), dict) else {}
        limits.append(("surface.what", _str(surf.get("what")), MAX_WORDS_SHORT))
        limits += [(f"surface.read[{i}]", s, MAX_WORDS_SHORT)
                   for i, s in enumerate(_strs(surf.get("read")))]
        limits += [(f"is_not[{i}]", s, MAX_WORDS_SHORT)
                   for i, s in enumerate(_strs(rec.get("is_not")))]
        limits += [(f"readers[{i}].line", _str(r.get("line")), MAX_WORDS_READER)
                   for i, r in enumerate(_list(rec.get("readers"))) if isinstance(r, dict)]
        for label, text, cap in limits:
            if text is not None and _words(text) > cap:
                rep.err(at(rid), f"{label} is {_words(text)} words; the most is {cap}")

    # 9 -- required records and placement
    for rid in REQUIRED:
        if rid not in records:
            rep.err("glossary", f"the required record {rid}.json is missing")
    terms = [(rid, _norm(_str(records[rid].get("term")) or "")) for rid in REQUIRED if rid in records]
    tc = Counter(t for _r, t in terms)
    for rid, t in terms:
        if tc[t] > 1:
            rep.err(at(rid), f"shares its term {t!r} with another required record; the four "
                             f"judgment states and the product must be told apart by their words")
    for rid, rec in sorted(records.items()):
        if rid != ABOUT:
            for key in ABOUT_ONLY:
                if key in rec:
                    rep.err(at(rid), f"carries `{key}`, which only {ABOUT} may carry")
        else:
            for key in ABOUT_FORBIDS:
                if key in rec:
                    rep.err(at(rid), f"carries `{key}`: {ABOUT} is served to a signed-out reader "
                                     f"and must resolve no other record")
        if "surface" in rec and rec.get("family") not in SURFACE_FAMILIES:
            rep.err(at(rid), f"carries `surface` in family {rec.get('family')!r}; only families "
                             f"{' and '.join(SURFACE_FAMILIES)} head a page")

    # 11 -- naming
    for rid, rec in sorted(records.items()):
        fam = rec.get("family")
        for pf in PREFIXED_FAMILIES:
            if fam == pf and not rid.startswith(pf + "-"):
                rep.err(at(rid), f"is in family {pf!r} and its id does not begin {pf + '-'!r}")
            if rid.startswith(pf + "-") and fam != pf:
                rep.err(at(rid), f"its id begins {pf + '-'!r} and it is in family {fam!r}, "
                                 f"not {pf!r}")

    # 12 -- the starter questions
    n_asks = 0
    for rid, rec in sorted(records.items()):
        surf = rec.get("surface") if isinstance(rec.get("surface"), dict) else None
        asks = surf.get("ask") if surf is not None else None
        if rec.get("family") == ASK_REQUIRED_FAMILY and not (isinstance(asks, list) and asks):
            rep.err(at(rid), "is a page (family 'surface') and carries no `surface.ask`: every page "
                             "offers the assistant's starter questions, and a page with none leaves "
                             "a reader nothing to begin from")
            continue
        if asks is None:
            continue
        if not isinstance(asks, list) or not ASK_MIN <= len(asks) <= ASK_MAX:
            n = len(asks) if isinstance(asks, list) else "no list of"
            rep.err(at(rid), f"`surface.ask` holds {n} question(s); a page offers from "
                             f"{ASK_MIN} to {ASK_MAX}")
            continue
        for i, q in enumerate(asks):
            n_asks += 1
            if not isinstance(q, str) or not q.strip():
                rep.err(at(rid), f"surface.ask[{i}] is not a question")
                continue
            if not q.rstrip().endswith("?"):
                rep.err(at(rid), f"surface.ask[{i}] does not end with a question mark: {q!r}")
            if _words(q) > MAX_WORDS_ASK:
                rep.err(at(rid), f"surface.ask[{i}] is {_words(q)} words; the most is {MAX_WORDS_ASK}")

    # 13 -- marks
    marked = [(rid, rec.get("mark")) for rid, rec in sorted(records.items()) if "mark" in rec]
    n_marks = 0
    if marked:
        tokens = os.path.abspath(args.tokens) if args.tokens else TOKENS
        shown_tokens = os.path.relpath(tokens, ROOT) if tokens.startswith(ROOT + os.sep) else tokens
        try:
            with open(tokens, encoding="utf-8") as fh:
                defined = declared_properties(fh.read())
        except OSError as exc:
            defined = None
            unjudged.append(f"{len(marked)} record(s) carry a `mark` and {shown_tokens} cannot be "
                            f"read ({exc.strerror or exc}), so no mark can be held to a property "
                            f"the stylesheet defines")
        named = {}
        for rid, value in marked:
            fam = records[rid].get("family")
            if fam not in MARK_FAMILIES:
                rep.err(at(rid), f"carries `mark` in family {fam!r}; a mark sits only on families "
                                 f"{', '.join(MARK_FAMILIES)}")
            if not isinstance(value, str) or not _MARK_RE.match(value):
                rep.err(at(rid), f"`mark` {value!r} is not a custom property named --mark-<name>")
                continue
            named.setdefault(value, []).append(rid)
            if defined is None:
                continue
            n_marks += 1
            if value not in defined:
                rep.err(at(rid), f"`mark` {value} is a property {shown_tokens} does not define: a "
                                 f"word may not name a mark the stylesheet cannot draw")
        for value, who in sorted(named.items()):
            if len(who) > 1:
                rep.err(f"mark {value}", f"named by {len(who)} records: {who}. One mark, one "
                                         f"meaning -- a property two words share says two things")

    # ---- report
    if not args.quiet:
        print(f"glossary: {n_files} file(s), {len(records)} record(s) in "
              f"{len(dirs)} director{'y' if len(dirs) == 1 else 'ies'}")
        fams = Counter(r.get("family") for r in records.values())
        kinds = Counter(r.get("kind") for r in records.values())
        print("  by kind:   " + ", ".join(f"{k} {n}" for k, n in sorted(kinds.items(), key=str)))
        print("  by family: " + ", ".join(f"{k} {n}" for k, n in sorted(fams.items(), key=str)))
        print(f"  sources checked against the bibliography: {n_sources}; "
              f"basis quotations verified: {n_quotes}; citations checked: {n_cites}")
        print(f"  bound fields: {len(fields_bound)} of {len(FIELDS)}"
              + (f" ({', '.join(fields_bound)})" if fields_bound else "")
              + f"; homonym pairs: {collisions}")
        print(f"  starter questions checked: {n_asks}; marks held to the stylesheet: {n_marks}")
        for w in rep.warnings:
            print(f"  WARN {w}")
    if rep.errors:
        for e in rep.errors:
            print(f"  ERROR {e}")
        print(f"\ncheck_glossary: {len(rep.errors)} error(s) over {len(records)} record(s)")
        return 1
    if unjudged:
        for u in unjudged:
            print(f"  UNJUDGED {u}")
        return could_not_evaluate("; ".join(unjudged))
    print(f"OK — glossary: {len(records)} record(s), {n_quotes} quotation(s) verified, "
          f"{n_sources} source(s) found in the bibliography, {len(fields_bound)} field(s) bound "
          f"completely, {collisions} homonym pair(s) declared")
    return 0


if __name__ == "__main__":
    sys.exit(main())
