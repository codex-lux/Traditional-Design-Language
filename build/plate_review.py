#!/usr/bin/env python3
"""plate_review.py -- the internal half of a plate's review (WP-14.5).

WHAT CAN BE SAID WITHOUT THE PLATE. Phase 14's third decision (27 Sep 2026) made the source leg
of the fidelity audit INTERNAL CHECKS, plus a list of the plates a person must fetch
(`Plan Examples/Plates/WANTED.md`), because every host the packs cite refuses a CONNECT from
here. So nothing in this file says a figure agrees with its source. It says what the record can
be held to on its own:

  * a member's figure is the figure its own note states -- STATES, not "quotes from its
    authority": many of these are the transcriber's own arithmetic on the authority's words, and
    a note is not a plate;
  * a measured kit parameter the elevation reads is the figure its own note states;
  * an overlay converts the figures it inherits by the factor its own module note states;
  * the members sum to the assembly, and the pack's invariants hold.

THREE VERDICTS, NEVER TWO: agrees, disagrees (with both figures), could not evaluate (with the
reason). A plate none of these reaches is COULD NOT EVALUATE, never "agrees".

THE TABLE. `build/note_figures.json` holds the figures read out of the notes. Agents read them and
the lead verified them; what makes that admissible is that NOTHING in it is taken on trust except
the reading. Every quote is held here, on every run, to be a verbatim substring of the note it
came from, so an edited note makes its row stale rather than silently wrong; and both sides of
every claim are expressions evaluated here over the record's own numbers, so the arithmetic is
never the table's. What the table asserts, and what a person may dispute, is that the quote is
ABOUT the figure its row names.

THE TOLERANCE is the notes' precision and not a fudge: a note states a figure to a sixteenth or a
fraction of a part, the record carries it to four decimal places, so two figures agree within
0.01 of a part (or of the parameter's unit) or 0.5 per cent, whichever is larger.
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

PE = modcache.load("proportion_engine", os.path.join(ROOT, "build", "proportion_engine.py"))
TABLE = os.path.join(ROOT, "build", "note_figures.json")

# A note that states a number, in digits or in the words the treatises use for their divisions.
NUMBER = re.compile(r"(?:\d|\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
                    r"half|third|quarter|fourth|fifth|sixth|seventh|eighth|ninth|tenth|"
                    r"twelfth)\b)", re.I)
DIGIT = re.compile(r"\d")
ELEVATION_FILES = {"elevation.py", "render_elevation.py"}

_TABLE = None
_MEMO = {}


def table():
    global _TABLE
    if _TABLE is None:
        _TABLE = json.load(open(TABLE, encoding="utf-8"))
    return _TABLE


def reset():
    """Forget the table and every judgment made from it (a test that plants a table calls this)."""
    global _TABLE
    _TABLE = None
    _MEMO.clear()


def _memo(fn):
    def wrapped():
        if fn.__name__ not in _MEMO:
            _MEMO[fn.__name__] = fn()
        return _MEMO[fn.__name__]
    wrapped.__name__ = fn.__name__
    wrapped.__doc__ = fn.__doc__
    return wrapped


def agrees(t, s):
    return abs(t - s) <= max(0.01, 0.005 * abs(s))


# ------------------------------------------------------------------ the members of an order pack
def member_env(pid, aid):
    """The names a member claim may use, over the pack's OWN statement of the assembly."""
    raw = PE.PACKS[pid]
    asms = raw.get("assemblies") or {}
    a = asms[aid]
    env = {"parts": raw["module"]["parts"]}
    if isinstance((raw.get("column") or {}).get("height_modules"), (int, float)):
        env["col"] = raw["column"]["height_modules"]
    if isinstance(a.get("height_modules"), (int, float)):
        env["asm_modules"] = a["height_modules"]
    env["asm_parts"] = sum(m.get("height_parts") or 0 for m in a.get("members", []))
    for m in a.get("members", []):
        for pre, k in (("h_", "height_parts"), ("p_", "projection_parts"), ("w_", "width_parts"),
                       ("s_", "spacing_parts")):
            if isinstance(m.get(k), (int, float)):
                env[pre + m["id"]] = m[k]
    for oid, o in asms.items():
        env["A_" + oid] = sum(m.get("height_parts") or 0 for m in o.get("members", []))
        if isinstance(o.get("height_modules"), (int, float)):
            env["M_" + oid] = o["height_modules"]
    return env


def order_packs():
    return sorted(p for p, r in PE.PACKS.items() if (r.get("kind") or "") == "order-system")


def numeric_member_notes():
    """(pack, assembly, member id) for every stated member whose note states a number."""
    out = []
    for pid in order_packs():
        for aid, a in (PE.PACKS[pid].get("assemblies") or {}).items():
            for m in a.get("members", []):
                if NUMBER.search(m.get("note") or ""):
                    out.append((pid, aid, m["id"]))
    return out


def _member(pid, aid, mid):
    for m in ((PE.PACKS.get(pid) or {}).get("assemblies") or {}).get(aid, {}).get("members", []):
        if m.get("id") == mid:
            return m
    return None


def _judge(claims, note, env):
    """Judge one entry's claims. Returns (rows, stale): a row per claim, and whether any claim no
    longer describes its note (its quote is gone or a name it uses no longer exists).

    A NOTE MAY STATE ANOTHER PACK'S FIGURE, and a claim may then name that pack
    (`target_pack`, `target_assembly`): both sides are evaluated over THAT pack's record, in its
    units, and the quote is still held to the note it was read from. The Palladio reader found
    the case by hand -- palladio-corinthian's base note says what Palladio gives the Doric base,
    and palladio-doric's own notes say nothing about its projection -- and a format that could
    only hold a note to its own member could not have said so."""
    rows, stale = [], []
    for c in claims:
        if c["quote"] not in note:
            stale.append("the quotation is no longer in the note: %r" % c["quote"][:80])
            continue
        where = env
        if c.get("target_pack"):
            try:
                where = member_env(c["target_pack"], c["target_assembly"])
            except Exception as e:       # noqa: BLE001 -- named, and it makes the row stale
                stale.append("%s/%s: %s" % (c.get("target_pack"), c.get("target_assembly"), e))
                continue
        try:
            t = PE.evaluate_expr(c["target"], where)
            s = PE.evaluate_expr(c["states"], where)
        except Exception as e:           # noqa: BLE001 -- named, and it makes the row stale
            stale.append("%s / %s: %s" % (c["target"], c["states"], e))
            continue
        rows.append({"quote": c["quote"], "target": c["target"], "states": c["states"],
                     "target_pack": c.get("target_pack"), "target_assembly": c.get("target_assembly"),
                     "record": t, "note": s, "agrees": agrees(t, s), "reading": c.get("reading")})
    return rows, stale


@_memo
def member_entries():
    """Every numeric member note, judged: {pack, assembly, member, verdict, claims, stale, why}.

    verdict: "agrees" (every claim), "disagrees" (any claim), "no-claim" (the note's figures are
    not about a recorded figure, with the table's reason), "stale" (the table no longer describes
    the note) or "not-read" (no entry at all)."""
    entries = {(e["pack"], e["assembly"], e["member"]): e for e in table().get("members", [])}
    out = []
    for key in numeric_member_notes():
        pid, aid, mid = key
        e = entries.get(key)
        row = {"pack": pid, "assembly": aid, "member": mid}
        if e is None:
            out.append(dict(row, verdict="not-read", claims=[], stale=[]))
            continue
        m = _member(pid, aid, mid)
        rows, stale = _judge(e.get("claims") or [], m.get("note") or "", member_env(pid, aid))
        if stale:
            v = "stale"
        elif not e.get("claims"):
            v = "no-claim"
        else:
            v = "agrees" if all(r["agrees"] for r in rows) else "disagrees"
        out.append(dict(row, verdict=v, claims=rows, stale=stale, why=e.get("why")))
    extra = sorted(set(entries) - set(numeric_member_notes()))
    for pid, aid, mid in extra:
        out.append({"pack": pid, "assembly": aid, "member": mid, "verdict": "stale", "claims": [],
                    "stale": ["the table has an entry for a note that no longer states a number, "
                              "or a member that no longer exists"]})
    return out


# ------------------------------------------------------------------ the kit parameters
def elevation_slots():
    CR = modcache.load("check_research", os.path.join(ROOT, "build", "check_research.py"))
    return {s for s, f in CR.generator_read_slots().items() if f & ELEVATION_FILES}


@_memo
def kit_params():
    """(kit, slot, parameter, record) for every `measured` parameter on a slot the elevation reads
    whose note states a number."""
    slots = elevation_slots()
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "kits", "*.kit.json"))):
        k = json.load(open(f, encoding="utf-8"))
        kid = os.path.basename(f)[:-len(".kit.json")]
        for sid, s in sorted((k.get("slots") or {}).items()):
            if sid not in slots:
                continue
            for pk, pv in sorted((s.get("parameters") or {}).items()):
                # NUMBER, as the member notes are read (WP-14.6, G9): `DIGIT` alone passed over a kit
                # note stating its figure in words -- "one-third", "two feet" -- six of them.
                if isinstance(pv, dict) and pv.get("kind") == "measured" and NUMBER.search(pv.get("note") or ""):
                    out.append((kid, sid, pk, pv))
    return out


def kit_env(pv):
    env = {}
    if isinstance(pv.get("value"), (int, float)):
        env["value"] = pv["value"]
    r = pv.get("range")
    if isinstance(r, list) and len(r) == 2 and all(isinstance(x, (int, float)) for x in r):
        env["lo"], env["hi"] = r
    return env


@_memo
def kit_entries():
    entries = {(e["kit"], e["slot"], e["parameter"]): e for e in table().get("kits", [])}
    out, keys = [], set()
    for kid, sid, pk, pv in kit_params():
        keys.add((kid, sid, pk))
        e = entries.get((kid, sid, pk))
        row = {"kit": kid, "slot": sid, "parameter": pk}
        if e is None:
            out.append(dict(row, verdict="not-read", claims=[], stale=[]))
            continue
        rows, stale = _judge(e.get("claims") or [], pv.get("note") or "", kit_env(pv))
        if stale:
            v = "stale"
        elif not e.get("claims"):
            v = "no-claim"
        else:
            v = "agrees" if all(r["agrees"] for r in rows) else "disagrees"
        out.append(dict(row, verdict=v, claims=rows, stale=stale, why=e.get("why")))
    for kid, sid, pk in sorted(set(entries) - keys):
        out.append({"kit": kid, "slot": sid, "parameter": pk, "verdict": "stale", "claims": [],
                    "stale": ["the table has an entry for a parameter no longer in the population"]})
    return out


# ------------------------------------------------------------------ the module conversions
@_memo
def conversions():
    """For every overlay: the factors its own module note states, against what the engine did.

    What the engine did is READ OFF ITS OUTPUT, never re-derived from its formula: every figure of
    an assembly the overlay inherits whole, against the base's, divided out. A shaft whose body
    was re-sized to the overlay's own column (`_height_from_column`, WP-14.2) is a derivation and
    not a conversion, so its body's height is not read; its other figures still are."""
    stated = table().get("modules", {})
    out = []
    for pid in order_packs():
        raw = PE.PACKS[pid]
        if not raw.get("overlay_of"):
            continue
        row = {"pack": pid, "base": raw["overlay_of"]}
        st = stated.get(pid)
        if st is None:
            out.append(dict(row, verdict="not-read", why="the table states no factor for this overlay"))
            continue
        text = ((raw.get("module") or {}).get("note") or "") + " " + ((raw.get("module") or {}).get("name") or "")
        gone = [q for q in st.get("quotes", []) if q not in text]
        if gone:
            out.append(dict(row, verdict="stale", why="the quotation is no longer in the module note: %r" % gone[0]))
            continue
        pf = PE.evaluate_expr(st["part_factor"], {})
        mf = PE.evaluate_expr(st["module_factor"], {})
        res, base = PE.resolve(pid), PE.resolve(raw["overlay_of"])
        seen, off = 0, []
        for aid, a in (res.get("assemblies") or {}).items():
            if PE.assembly_owner(pid, aid) == pid or aid not in (base.get("assemblies") or {}):
                continue
            b = base["assemblies"][aid]
            derived = a.get("_height_from_column") or {}
            if isinstance(b.get("height_modules"), (int, float)):
                was = derived.get("was_modules", a.get("height_modules"))
                seen += 1
                if abs(was - b["height_modules"] * mf) > 1e-6:
                    off.append("%s: %g M against %g x %g" % (aid, was, b["height_modules"], mf))
            bm = {m["id"]: m for m in b.get("members", [])}
            for m in a.get("members", []):
                bmem = bm.get(m["id"])
                for k in ("height_parts", "projection_parts", "width_parts", "spacing_parts"):
                    if k == "height_parts" and m["id"] == derived.get("body"):
                        continue
                    if isinstance(m.get(k), (int, float)) and isinstance((bmem or {}).get(k), (int, float)):
                        seen += 1
                        if abs(m[k] - bmem[k] * pf) > 1e-6:
                            off.append("%s.%s %s: %g against %g x %g" % (aid, m["id"], k, m[k], bmem[k], pf))
        if not seen:
            out.append(dict(row, verdict="could-not-evaluate", part_factor=st["part_factor"],
                            module_factor=st["module_factor"],
                            why="the overlay inherits no figure whole, so no conversion is drawn"))
            continue
        out.append(dict(row, verdict="agrees" if not off else "disagrees", figures=seen, off=off,
                        part_factor=st["part_factor"], module_factor=st["module_factor"]))
    return out


# ------------------------------------------------------------------ one plate
def _chain(pid):
    out, p = [], pid
    while p and p not in out:
        out.append(p)
        p = PE.PACKS.get(p, {}).get("overlay_of")
    return out


def plate_review(pid, aid):
    """The internal verdict for the plate drawing assembly `aid` of pack `pid`, as resolved.

    Returns {"verdict", "checks": [(name, verdict, detail)]}. The checks that reach a plate:
    the assembly's members sum to its height (where its author asked for that); the figures notes
    state about the record it draws; the conversion of any member drawn from another authority's
    module; and the pack's invariants.

    A CLAIM COUNTS ON THE PLATE WHOSE RECORD IT JUDGES. `palladio-corinthian`'s base note states
    what Palladio gives the DORIC base, so that claim reaches the Doric base plate, which draws
    the figure, and not the Corinthian one, which only carries the sentence. The first version
    counted it where the note sat: the Corinthian plate read DISAGREES over a record nobody
    disputes, and the Doric plate read AGREES over the 20 minutes the claim is about."""
    res = PE.resolve(pid)
    a = (res.get("assemblies") or {}).get(aid) or {}
    parts = res["module"]["parts"]
    checks = []

    if a.get("sums_check", True) and isinstance(a.get("height_modules"), (int, float)):
        total = sum(m.get("height_parts") or 0 for m in a.get("members", []))
        want = a["height_modules"] * parts
        checks.append(("the members sum to the assembly",
                       "agrees" if abs(total - want) <= 1e-6 else "disagrees",
                       "%g of %g parts" % (total, want)))
    else:
        checks.append(("the members sum to the assembly", "could-not-evaluate",
                       "its author's members do not sum to it, and a note says why"))

    chain = _chain(pid)
    allentries = member_entries()
    entries = {(e["pack"], e["assembly"], e["member"]): e for e in allentries}
    ok = bad = 0
    bad_detail = []
    foreign = False
    staters = set()

    def _count(c, stater):
        """An inherited figure is judged over the pack that STATES it, in that pack's parts, so
        the detail names that pack: `benjamin-tuscan`'s capital plate draws Vignola's abacus
        converted, and "the record 5" in Vignola's parts would read as Benjamin's."""
        nonlocal ok, bad
        if c["agrees"]:
            ok += 1
        else:
            bad += 1
            owner = c.get("target_pack") or stater
            where = ("%s/%s " % (owner, c.get("target_assembly") or aid)) if owner != pid else ""
            bad_detail.append("%s%s: the record %g, a note %g (%s)"
                              % (where, c["target"], c["record"], c["note"], _clip(c["quote"])))

    for m in a.get("members", []):
        stater = next((p for p in chain if _member(p, aid, m["id"]) is not None), None)
        if stater is None:
            continue
        staters.add(stater)
        if stater != pid:
            foreign = True
        e = entries.get((stater, aid, m["id"]))
        if not e:
            continue
        for c in e["claims"]:
            if c.get("target_pack") and (c["target_pack"], c.get("target_assembly")) != (stater, aid):
                continue    # it judges another pack's record, and counts on that plate
            _count(c, stater)
        if e["verdict"] == "stale":
            bad_detail.append("%s: the table no longer describes the note" % m["id"])
            bad += 1
        elif e["verdict"] == "not-read":
            bad_detail.append("%s: its note states a figure nobody has read" % m["id"])
            bad += 1
    # ...and what other packs' notes state about the record this plate draws.
    for e in allentries:
        for c in e["claims"]:
            if (c.get("target_pack") and (c["target_pack"], c.get("target_assembly")) != (e["pack"], e["assembly"])
                    and c["target_pack"] in staters and c.get("target_assembly") == aid):
                _count(c, c["target_pack"])
    if ok or bad:
        checks.append(("the figures notes state about its record",
                       "disagrees" if bad else "agrees",
                       ("%d agree" % ok) + (("; " + "; ".join(bad_detail)) if bad_detail else "")))
    else:
        checks.append(("the figures notes state about its record", "could-not-evaluate",
                       "no note states a figure about a figure it records"))

    if foreign:
        conv = next((c for c in conversions() if c["pack"] == pid), None)
        if conv is not None:
            checks.append(("the conversion of what it inherits", conv["verdict"],
                           ("by the %s its module note states" % conv.get("part_factor"))
                           if conv["verdict"] == "agrees" else (conv.get("why") or "; ".join(conv.get("off", [])[:3]))))

    inv = PE.check_invariants(res)
    if inv:
        held = sum(1 for r in inv if r.get("holds") is True)
        broke = sum(1 for r in inv if r.get("holds") is False)
        checks.append(("the pack's invariants",
                       "disagrees" if broke else ("agrees" if held == len(inv) else "could-not-evaluate"),
                       "%d of %d hold" % (held, len(inv))))

    vs = [v for _n, v, _d in checks]
    if "disagrees" in vs:
        verdict = "disagrees"
    elif "agrees" in vs:
        verdict = "agrees"
    else:
        verdict = "could-not-evaluate"
    return {"verdict": verdict, "checks": checks}


def _clip(quote, limit=60):
    """A quote to `limit` characters, cut at a word and the cut marked -- WP-11.5's rule for a
    quoted basis. The first version cut mid-phrase and said nothing."""
    q = " ".join(quote.split())
    if len(q) <= limit:
        return q
    return q[:limit].rsplit(" ", 1)[0] + " …"


def review_note(pid, aid, diameter_words, source, unconstructed=()):
    """The review note a plate's manifest record carries: the internal verdict, the source NOT
    evaluated and why, and that nobody has approved it. Approving a plate is a person's act."""
    r = plate_review(pid, aid)
    word = {"agrees": "AGREES", "disagrees": "DISAGREES",
            "could-not-evaluate": "COULD NOT EVALUATE"}[r["verdict"]]
    # AN AGREEMENT OVER A CHECK THAT COULD NOT RUN SAYS SO IN ITS HEADLINE (WP-14.6, auditor C).
    # The verdict is `agrees` wherever something agreed and nothing disagreed, so four plates read
    # INTERNAL: AGREES with one of their three checks unjudged -- listed after the dash, where a
    # reader of the headline does not look. Unjudged is not passed, and the word that summarises
    # the checks must not be read as saying it is.
    unjudged = sum(1 for _n, v, _d in r["checks"] if v == "could-not-evaluate")
    if r["verdict"] == "agrees" and unjudged:
        word = "AGREES WHERE JUDGED, %d OF %d CHECKS COULD NOT BE EVALUATED" % (unjudged, len(r["checks"]))
    parts = ["%s: %s (%s)" % (n, v.replace("-", " "), d) for n, v, d in r["checks"]]
    note = ("Drawn by build/render_profile.py from %s at a %s column; every dimension comes from "
            "proportion_engine.dimension() and every curve from profiles.py. INTERNAL: %s -- %s. "
            "SOURCE: COULD NOT EVALUATE -- %s was not reachable from here, and the figures it would "
            "settle are listed in Plan Examples/Plates/WANTED.md. NOT approved: approving a plate "
            "is a person's act." % (pid, diameter_words, word, "; ".join(parts), source or "the cited plate"))
    if unconstructed:
        note += (" PARTIAL: %s are named on the plate and not drawn, because this corpus records no "
                 "construction for them." % ", ".join(unconstructed))
    return note
