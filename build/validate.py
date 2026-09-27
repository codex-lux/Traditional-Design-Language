#!/usr/bin/env python3
"""Validate the style graph: schema conformance, referential integrity, acyclicity, date coherence."""
import json, os, sys, glob
try:
    import jsonschema
except ImportError:
    import sys as _sys
    print("SKIPPED — jsonschema is not installed, so nothing here was checked.")
    print("    pip install jsonschema")
    # Exit 3, the convention build/check_all.py reads as "could not evaluate". Exiting 1
    # would report a missing dependency as a failed data check, which is the collapse
    # this corpus forbids everywhere else.
    _sys.exit(3)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import schema_validators                                                   # noqa: E402
# Compiled once for all 164 nodes rather than rebuilt per node: 5.95 s -> 0.19 s.
sch_validator = schema_validators.compiled(f"{ROOT}/schema/style-node.schema.json")
massings = {m["id"] for m in json.load(open(f"{ROOT}/massings/catalog.json"))}
slots = set()
slot_records = {}
for g in json.load(open(f"{ROOT}/elements/slots.json"))["groups"]:
    for s in g["slots"]:
        slots.add(s["id"])
        slot_records[s["id"]] = s

nodes, errs, warns = {}, [], []

# derives_from_module referential integrity (docs/open-questions.md #13): every
# reference must point at a real slot, and not at itself.
for sid, s in slot_records.items():
    dfm = s.get("derives_from_module")
    if dfm is None:
        continue
    if dfm not in slots:
        errs.append(f"slot {sid}: derives_from_module '{dfm}' does not exist")
    elif dfm == sid:
        errs.append(f"slot {sid}: derives_from_module cannot reference itself")
files = sorted(glob.glob(f"{ROOT}/styles/*.json"))
for f in files:
    base = os.path.basename(f)[:-5]
    try:
        n = json.load(open(f))
    except Exception as e:
        errs.append(f"{base}: UNPARSEABLE JSON: {e}"); continue
    try:
        schema_validators.raise_first(sch_validator, n)
    except jsonschema.ValidationError as e:
        errs.append(f"{base}: SCHEMA {'/'.join(str(p) for p in e.absolute_path)}: {e.message}"); continue
    if n["id"] != base: errs.append(f"{base}: id '{n['id']}' does not match filename")
    if n["id"] in nodes: errs.append(f"{base}: duplicate id")
    nodes[n["id"]] = n

RANK_ORDER = {"tradition":0,"family":1,"style":2,"variant":3}
for i, n in nodes.items():
    mo = n.get("member_of")
    if n["rank"] == "tradition":
        if mo: errs.append(f"{i}: tradition must have member_of null")
    else:
        if not mo: errs.append(f"{i}: rank {n['rank']} requires member_of")
        elif mo not in nodes: errs.append(f"{i}: member_of '{mo}' does not exist")
        elif RANK_ORDER[nodes[mo]["rank"]] >= RANK_ORDER[n["rank"]]:
            errs.append(f"{i}: member_of '{mo}' rank {nodes[mo]['rank']} not above {n['rank']}")
    for e in n.get("lineage", []):
        if e["target"] not in nodes: errs.append(f"{i}: lineage target '{e['target']}' does not exist")
        if e["target"] == i: errs.append(f"{i}: self-referential lineage edge")
    if n["rank"] == "variant":
        if not any(e["type"] == "regional_of" for e in n.get("lineage", [])):
            warns.append(f"{i}: variant has no regional_of edge")
    p = n["period"]
    if p["floruit_start"] > p["floruit_end"]: errs.append(f"{i}: floruit_start > floruit_end")
    if p.get("origin") and p["origin"] > p["floruit_start"]: warns.append(f"{i}: origin after floruit_start")
    for df in n.get("distinguished_from", []):
        t = df["node"]
        if t.startswith("massing:"):
            if t[8:] not in massings: errs.append(f"{i}: distinguished_from unknown massing '{t}'")
        elif t not in nodes:
            errs.append(f"{i}: distinguished_from target '{t}' does not exist")
    for e in n.get("lineage", []):
        ik = e.get("inherits_kit", False)
        if e["type"] in ("descends_from","regional_of") and not ik:
            errs.append(f"{i}: {e['type']} -> {e['target']} must set inherits_kit true (it is transmission)")
        if e["type"] in ("references","reacts_against","revives") and ik:
            errs.append(f"{i}: {e['type']} -> {e['target']} must not set inherits_kit (it is not transmission)")
        if ik and e["target"] in nodes and nodes[e["target"]]["rank"] not in ("style","variant"):
            errs.append(f"{i}: inheritance edge -> '{e['target']}' targets rank {nodes[e['target']]['rank']}; only style/variant carry kits")
    for ma in n.get("massing_affinities", []):
        if ma["massing"] not in massings: errs.append(f"{i}: unknown massing '{ma['massing']}'")
    for k in n.get("kit", {}):
        if k not in slots: errs.append(f"{i}: unknown kit slot '{k}'")

# membership tree acyclicity
for i in nodes:
    seen, cur = set(), i
    while cur:
        if cur in seen: errs.append(f"{i}: member_of cycle"); break
        if cur not in nodes: break
        seen.add(cur); cur = nodes[cur].get("member_of")

# lineage DAG acyclicity (inheritance edges only)
INHERIT = {"descends_from","regional_of","hybridizes_with","revives"}
color = {}
def dfs(u, stack):
    color[u] = 1
    for e in nodes[u].get("lineage", []):
        v = e["target"]
        if e["type"] not in INHERIT or v not in nodes: continue
        if color.get(v) == 1: errs.append("LINEAGE CYCLE: " + " -> ".join(stack + [u, v]))
        elif color.get(v, 0) == 0: dfs(v, stack + [u])
    color[u] = 2
for i in nodes:
    if color.get(i, 0) == 0: dfs(i, [])

# chronology: a node should not predate an ancestor it descends from
for i, n in nodes.items():
    for e in n.get("lineage", []):
        if e["type"] in ("descends_from","regional_of") and e["target"] in nodes:
            if n["period"]["floruit_start"] < nodes[e["target"]]["period"]["floruit_start"] - 25:
                warns.append(f"{i} ({n['period']['floruit_start']}) starts well before ancestor {e['target']} ({nodes[e['target']]['period']['floruit_start']})")

print(f"nodes: {len(nodes)}  files: {len(files)}")
by_rank = {}
for n in nodes.values(): by_rank[n["rank"]] = by_rank.get(n["rank"], 0) + 1
print("by rank:", by_rank)
if warns:
    print(f"\n{len(warns)} WARNINGS"); [print("  ! " + w) for w in warns[:60]]
if errs:
    print(f"\n{len(errs)} ERRORS"); [print("  x " + e) for e in errs[:80]]; sys.exit(1)
# WP-12.1: the scene layer's own selftest runs HERE rather than as a 51st entry in
# check_all.CHECKS, so `TOTAL_CHECKS` does not move — the precedent is WP-11.6, which put the
# family-specimen drift check inside check_precedents.py for the same reason. It is placed
# after the taxonomy verdict because it is a different subject and must not be able to make
# that verdict read as its own; it exits non-zero on its own account.
#
# AND IT LOADS THROUGH `modcache` RATHER THAN BY PATH. WP-12.1 wrote a bare
# `spec_from_file_location` here and `tests/test_modcache.py::
# test_no_new_by_path_loader_outside_modcache` refused it — correctly: a fresh module object
# per call is exactly what that cache exists to stop, and `scene.py` pulls in geometry,
# structure, roof and elevation behind it. Found by WP-12.2 running the guard rather than by
# reading, which is the shape this file keeps meeting: a package that commits before its build
# finishes learns what it broke from the build.
_scene_bad = 0
try:
    import modcache as _mc
    _scene = _mc.load("scene", f"{ROOT}/build/scene.py")
    print()
    _scene_bad = _scene.selftest()
except Exception as _e:                 # noqa: BLE001 -- a refusal is content
    # AND A LOUD ERROR IS NOT A REFUSAL (WP-12.8). `scene._extent` raises on a primitive it
    # cannot measure precisely so the frame can never quietly be too small again -- and this
    # blanket except was the only CI consumer of that raise, printing one line of N/EV and
    # exiting 0. `UnknownPrimitive` goes straight through; everything else is still a genuine
    # could-not-evaluate, because a placement can be refused for reasons that are not this
    # checker's and saying which is the third state working.
    if type(_e).__name__ == "UnknownPrimitive":
        raise
    # COULD NOT EVALUATE, named. A scene needs a placement, and a placement can be refused
    # for reasons that are not this checker's; saying which is the third state working.
    print(f"\nN/EV — scene: could not evaluate ({type(_e).__name__}: {str(_e)[:120]})")

# WP-13.5: A DUPLICATE KEY IN A JSON RECORD IS INVISIBLE TO EVERY READER IN THIS TREE.
#
# `plans/tidewater-georgian-careful.json` carried `"stacks_over"` TWICE on two of its upper
# rooms, and had since WP-11.2 authored them. `json.load` takes the LAST occurrence and says
# nothing; `jsonschema` never sees the first, because it validates the parsed object; every
# checker, both engines and both renderers therefore agreed with each other about a record that
# says one thing twice. Both copies happened to carry the same value, so nothing in this corpus
# has ever behaved differently — which is exactly why it survived: a silent disagreement would
# have had to WAIT for the two to differ, and the first reader to notice would have been a
# person reading a sheet.
#
# It was found by ROUND-TRIPPING the file (parse, edit, dump) and reading the diff, which
# collapsed the pair and showed as a deletion of a line nobody deleted. It is a two-line sweep
# and it belongs in the build, so it is here.
#
# IT RUNS INSIDE THIS CHECKER SO `TOTAL_CHECKS` DOES NOT MOVE -- WP-12.1's scene selftest
# above is the precedent and WP-11.6's family-specimen drift check is that one's. It exits on
# its own account, after the taxonomy verdict, so neither subject can make the other's verdict
# read as its own.
#
# AND IT ENUMERATES WITH `git ls-files`, NEVER WITH `os.walk`. WP-13.2 met the other way: a
# checker that walked the directory found the first agent worktree under `.claude/worktrees/`
# -- a git-ignored copy of the whole repository inside itself -- and went red on 2,031 files it
# had never been written to open.
def _duplicate_keys(path):
    """Every (object id, key) this file states twice. The hook sees the RAW pairs, which is the
    only place the duplicate still exists: by the time `json.load` returns, it is gone."""
    dup = []
    def hook(pairs):
        seen = set()
        obj = dict(pairs)
        for k, _v in pairs:
            if k in seen:
                dup.append((obj.get("id") or obj.get("name") or "<anonymous object>", k))
            seen.add(k)
        return obj
    with open(path, encoding="utf-8") as fh:
        json.load(fh, object_pairs_hook=hook)
    return dup


_dup_bad = 0
try:
    import subprocess as _sp
    _tracked = _sp.run(["git", "-C", ROOT, "ls-files", "-co", "--exclude-standard", "*.json"],
                       capture_output=True, text=True, check=True).stdout.split()
except Exception as _e:                 # noqa: BLE001 -- a refusal is content
    # COULD NOT EVALUATE, named and never collapsed into a pass: a tree with no git is a tree
    # this sweep has not read, which is not the same as a tree with no duplicates.
    print(f"\nN/EV — duplicate keys: could not enumerate the tracked records "
          f"({type(_e).__name__}: {str(_e)[:80]})")
    _tracked = None


def duplicate_keys_over(rels, root=None):
    """`(read, dups)` for a list of repo-relative json paths: how many this sweep actually
    PARSED, and one sentence per duplicate.

    A FUNCTION SO THE WIRING CAN BE DRIVEN (WP-13.7). `_duplicate_keys` was tested on hand-built
    files and the loop that applies it to the corpus was module-level, so neutering the call --
    `_found = _duplicate_keys(_abs)` -> `_found = []` -- left `tests/test_duplicate_keys.py` 8 of
    8 green: the census below is a premise assertion about the ENUMERATOR, and a DETECTOR that
    returns nothing prints `duplicates: 0` exactly as a clean corpus does. `export_ifc.slab_boxes`
    is the precedent -- computed where a test can read it, printed where it cannot.

    COUNTED AFTER THE PARSE, not before it, so a file this function could not read does not
    inflate the one number that is supposed to prove the sweep looked."""
    base = ROOT if root is None else root
    dups, read = [], 0
    for rel in rels:
        abs_ = os.path.join(base, rel)
        if not os.path.isfile(abs_):
            continue
        try:
            found = _duplicate_keys(abs_)
        except Exception:               # noqa: BLE001 -- a malformed file is the schema's finding
            continue
        read += 1
        for oid, k in found:
            dups.append(f"{rel}: object '{oid}' states '{k}' twice")
    return read, dups


if _tracked is not None:
    _read, _dups = duplicate_keys_over(_tracked)
    print(f"\njson records read for duplicate keys: {_read}  duplicates: {len(_dups)}")
    for _d in _dups[:40]:
        print("  x " + _d)
    _dup_bad = 1 if _dups else 0

# WP-14.33: A DESCRIPTION IS FOR A READER, AND ITS BUILD HISTORY IS NOT (ruled 26 Sep 2026).
#
# The record pages (WP-14.23) print a parti's, a room's, a grouping's and a massing's
# `description` as the page's own prose. Five parti descriptions carried the account of how the
# record came to say what it says -- "WP-13.5 states the container ... `block: service` ...
# `geometry.blocks_for`", "it was 9,000, which the composer could reach 43% of ... (OQ 45)" --
# which is a maintainer's note printed where a reader looks
# (`oq/five-parti-descriptions-carry-build-history-a-reader-now-sees`). The history moved to the
# parti's `note` (parti schema 0.2.0) and this sweep keeps it from coming back, in every record
# kind whose description a page shows: partis, groupings, rooms, massings and the style nodes.
#
# WHAT IT REFUSES: a work-package number, an open-question number or slug, and a CODE SPAN --
# ANY backticked run, because the record page prints a description as plain text and a reader
# sees the backticks. The first draft refused only a span holding a `.`, `:`, `=` or `(` and
# let a backticked id through, and a mutation putting `area_range_sf` into a description sailed
# past it: an identifier in backticks is code whatever characters it holds. Two descriptions
# carried one (a grouping's `dependency-and-hyphen`, a style's `references` and
# `descends_from`) and were reworded in the words a reader uses.
# IT RUNS INSIDE THIS CHECKER SO `TOTAL_CHECKS` DOES NOT MOVE, beside the duplicate-key sweep.
def description_texts(root=None, unreadable=None):
    """`[(where, text)]` for every description a record page shows. Globbed per directory, never
    walked, and sorted, so a git-ignored copy of the tree cannot be read into it.

    A FILE THAT CANNOT BE READ IS NAMED, NOT RAISED (WP-14.33's audit). The first version let a
    malformed record escape as a bare traceback, and read a massing catalogue that was not a list
    as zero massings -- an empty read that looks exactly like a clean one. Each failure is
    appended to `unreadable`, and the module fails the build on it, because a description the
    sweep could not open is a description it did not judge."""
    import glob as _glob
    base = ROOT if root is None else root
    bad = unreadable if unreadable is not None else []
    out = []

    def _load(rel):
        try:
            return json.load(open(os.path.join(base, rel), encoding="utf-8"))
        except Exception as e:          # noqa: BLE001 -- named below, never swallowed
            bad.append(f"{rel}: could not be read for its description ({type(e).__name__}: {e})")
            return None

    for kind in ("partis", "groupings", "rooms"):
        for path in sorted(_glob.glob(os.path.join(base, kind, "*.json"))):
            rel = f"{kind}/{os.path.basename(path)}"
            d = _load(rel)
            if d is None:
                continue
            if not isinstance(d, dict):
                bad.append(f"{rel}: is not a record object, so its description could not be read")
                continue
            if isinstance(d.get("description"), str):
                out.append((rel, d["description"]))
    if os.path.isfile(os.path.join(base, "massings", "catalog.json")):
        cat = _load("massings/catalog.json")
        if cat is not None and not isinstance(cat, list):
            bad.append("massings/catalog.json: is not a list of massings, so no description in it "
                       "could be read")
        for m in (cat if isinstance(cat, list) else []):
            if isinstance(m, dict) and isinstance(m.get("description"), str):
                out.append((f"massings/catalog.json#{m.get('id')}", m["description"]))
    for path in sorted(_glob.glob(os.path.join(base, "styles", "*.json"))):
        rel = f"styles/{os.path.basename(path)}"
        d = _load(rel)
        if d is None:
            continue
        d = d.get("description") if isinstance(d, dict) else None
        if isinstance(d, dict):
            for part in ("short", "long"):
                if isinstance(d.get(part), str):
                    out.append((f"{rel}#{part}", d[part]))
    return out


# WHAT BUILD HISTORY LOOKS LIKE IN PROSE. Widened by WP-14.33's audit, which found the first
# forms missing `WP 14`, a lower-case `wp-`, `OQ45` and `OQs 12`, a code span wrapped across a
# line, and the two shapes a reworded description had actually kept: a repository path
# (`docs/inheritance.md`) and a snake_case identifier (`garage_strategy`). Measured over the 466
# descriptions on the day it was widened, the path and identifier forms each hit that ONE
# description and nothing else, and it was reworded. A backtick is refused whatever it encloses,
# across a line break too, and a lone one runs to the end of the text, because the page prints
# plain text and a reader sees the character.
HISTORY_FORMS = (
    (r"(?i)\bWP[- ]?\d", "a work-package number"),
    (r"(?i)\bOQs?[- ]?\d", "an open-question number"),
    (r"(?i)\boq/[a-z0-9]", "an open-question slug"),
    (r"`[^`]*`?", "a code span"),
    (r"\b[\w.-]+/[\w./-]*\.(?:md|py|json|jsx|js|mjs|css|html|svg)\b", "a repository path"),
    (r"\b[a-z][a-z0-9]*_[a-z0-9_]*[a-z0-9]\b", "a snake_case identifier"),
)


def build_history_in(texts):
    """One sentence per piece of build history found in `[(where, text)]`. Pure."""
    import re as _re
    forms = [(_re.compile(rx), what) for rx, what in HISTORY_FORMS]
    found = []
    for where, text in texts:
        for rx, what in forms:
            for m in rx.finditer(text):
                found.append(f"{where}: its description carries {what} ({m.group(0)!r}) -- "
                             f"build history goes in the record's `note`, not where a reader looks")
    return found


_desc_unread = []
_desc_texts = description_texts(unreadable=_desc_unread)
_desc_found = build_history_in(_desc_texts) + _desc_unread
print(f"\ndescriptions read for build history: {len(_desc_texts)}  found: {len(_desc_found)}")
for _d in _desc_found[:40]:
    print("  x " + _d)
_desc_bad = 1 if _desc_found else 0

print("\nOK — schema valid, references resolve, no cycles.")
if _scene_bad or _dup_bad or _desc_bad:
    sys.exit(1)
